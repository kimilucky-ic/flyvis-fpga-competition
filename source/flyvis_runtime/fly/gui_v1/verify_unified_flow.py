"""Actual saved-data/HTTP/software-player checks. No new neural arrays or devices."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from io import BytesIO
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from data_store import DataStore, ROOT, read_json, sha256
from phase3_adapter import Phase3Adapter
from unified_flow import UnifiedFlow
from workbench import Workbench


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8773')
    parser.add_argument('--output',default=str(ROOT/'gui_v1/evidence/phase4_unified_20261011/software_acceptance.json'))
    args=parser.parse_args();store=DataStore();p3=Phase3Adapter(store);wb=Workbench(store,p3)
    cid=next(iter(p3.packages));f=p3.packages[cid].frozen
    def http(path,body=None):
        request=Request(args.url+path,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json'})
        try:
            with urlopen(request,timeout=60) as r:return r.status,r.read(),dict(r.headers)
        except HTTPError as e:return e.code,e.read(),dict(e.headers)
    def obj(path,body=None):
        code,body,headers=http(path,body);return code,json.loads(body),headers
    result={'schema':'flyvis-unified-GUI-software-acceptance-v1','utc':datetime.now(timezone.utc).isoformat(),
        'status':'PASS_SOFTWARE_STRUCTURE_ONLY','camera_opened':False,'new_neural_inference':False,'board_operations':False,
        'actual_new_phone_input_positive':'NOT_RUN: producer capture pending',
        'new_task_service_positive':'NOT_RUN: formal service absent','negative_checks':[]}
    def rejected(name,fn):
        try:fn()
        except (ValueError,KeyError,OSError):result['negative_checks'].append(name);return
        raise AssertionError(name+' was accepted')
    with tempfile.TemporaryDirectory(prefix='gui_flow_') as temp:
        flow=UnifiedFlow(store,wb,runtime=temp);assert flow.presenter and not flow.presenter_error
        s=flow.create();sid=s['session_id']
        rejected('submit_without_input',lambda:flow.action(sid,'submit',{'revision':0,'mode':'Full_GPU'}))
        rejected('wrong_source',lambda:flow.action(sid,'select',{'revision':0,'source_kind':'pretend_camera'}))
        rejected('stale_revision',lambda:flow.action(sid,'select',{'revision':5,'source_kind':'phone_camera'}))
        rejected('boolean_revision',lambda:flow.action(sid,'select',{'revision':False,'source_kind':'phone_camera'}))
        rejected('wrong_comparison',lambda:flow.action(sid,'freeze',{'revision':0,'comparison_id':'camera_old'}))
        code,s=flow.action(sid,'freeze',{'revision':0,'comparison_id':cid});assert code==200
        ref=s['input_reference'];assert ref['identity_fingerprint']==f.fingerprint and ref['input_shape']==[1,800,1,721]
        assert ref['source_is_camera'] is ref['new_capture'] is ref['new_inference'] is False
        assert ref['input_time_s']==[0,3.995] and ref['activity_time_s']==[.005,4]
        saved=read_json(ref['reference_path']);assert 'reference_sha256' not in saved and sha256(ref['reference_path'])==ref['reference_sha256']
        rejected('wrong_reference',lambda:flow.action(sid,'submit',{'revision':1,'reference_id':'wrong','mode':'Full_GPU'}))
        rejected('wrong_mode',lambda:flow.action(sid,'submit',{'revision':1,'reference_id':ref['reference_id'],'mode':'fake_fpga'}))
        for mode in ('Full_GPU','Sham_Ablation','Python_Replacement','FPGA_Replacement'):
            code,s=flow.action(sid,'submit',{'revision':1,'reference_id':ref['reference_id'],'mode':mode})
            assert code==503 and s['state']=='WAITING_COMPUTE' and s['job_id'] is s['run_id'] is s['result'] is None
        Path(ref['reference_path']).write_text('{}',encoding='utf-8')
        rejected('modified_frozen_reference',lambda:flow.action(sid,'submit',{'revision':1,'reference_id':ref['reference_id'],'mode':'Full_GPU'}))
        for source in ('interactive_digital','phone_camera'):
            code,s=flow.action(sid,'select',{'revision':s['revision'],'source_kind':source})
            assert s['state']=='PREVIEW_ONLY' and s['input_reference'] is s['result'] is s['run_id'] is None
            code,s=flow.action(sid,'freeze',{'revision':s['revision'],'comparison_id':cid})
            assert code==503 and s['input_reference'] is None;result['negative_checks'].append(source+'_cannot_relabel_P0')
            for action in ('preview','capture','stop_capture'):
                code,response=flow.action(sid,action,{'revision':s['revision']});assert code==503 and not response['camera_capture']
        absent=UnifiedFlow(store,wb,runtime=temp,presentation_root=Path(temp)/'missing')
        assert absent.capabilities()['presentation']['status']=='NOT_AVAILABLE' and len(absent.capabilities()['verified_p0'])==1
        result['negative_checks'].append('missing_optional_presenter_isolated')
        # Invoke original sealed producer arm/events logger, not a rewritten renderer.
        bridge=flow.presenter
        def phone(path,body,token=None):
            raw=json.dumps(body).encode();out=[]
            request=SimpleNamespace(path=path,headers={'X-Stimulus-Token':token or bridge.state.token,'Content-Length':str(len(raw))},rfile=BytesIO(raw))
            bridge.post(request,lambda code,value:out.append((code,value)));return out[0]
        code,value=phone('/api/arm',{'settings':{'direction_deg':90,'polarity':'ON'},'client':{'scope':'GUI software test'}})
        assert code==200 and value['validation_only'] is True
        presentation=read_json(value['presentation_path']);assert not presentation['camera_capture'] and not presentation['neural_inference'] and presentation['comparison_id'] is None
        code,events=phone('/api/events',{'session_id':value['session_id'],'events':[{'kind':'start','client_performance_ms':1},{'kind':'complete','client_performance_ms':4001}]})
        assert code==200 and events['state']=='complete';assert flow.snapshot(sid)['input_reference'] is None
        for path,body,token in [('/api/arm',{'settings':{'bogus':1}},None),('/api/arm',{'settings':{}},'wrong'),('/api/events',{'session_id':value['session_id'],'events':[{'kind':'complete','client_performance_ms':-1}]},None)]:
            assert phone(path,body,token)[0] in (400,403)
        result['negative_checks']+=['bad_presentation_parameters','bad_presentation_token','bad_presentation_clock']
    assert 'torch' not in sys.modules and 'cv2' not in sys.modules
    catalog=obj('/api/catalog')[1];assert len(catalog['datasets'])==7 and sum(len(d['conditions']) for d in catalog['datasets'])==55
    code,caps,_=obj('/api/flow');assert code==200 and caps['camera']['capture_open'] is False and caps['board']['status']=='NOT_CONNECTED'
    assert caps['direct_interactive_export']['status']=='NOT_AVAILABLE' and caps['execution']['job_id'] is None
    for name in ('phone.html','player.js','style.css'):
        code,raw,headers=http('/input-player/'+name)
        assert code==200 and raw==(ROOT/'camera_pipeline/phase4_phone_camera_20261010_r1/web'/name).read_bytes()
        assert headers['X-Source-SHA256']==sha256(ROOT/'camera_pipeline/phase4_phone_camera_20261010_r1/web'/name)
        assert ("frame-ancestors 'self'" if name=='phone.html' else "frame-ancestors 'none'") in headers['Content-Security-Policy']
    assert "frame-ancestors 'none'" in http('/')[2]['Content-Security-Policy']
    _,s,_=obj('/api/flow/sessions',{});sid=s['session_id']
    code,s,_=obj(f'/api/flow/sessions/{sid}/freeze',{'revision':0,'comparison_id':cid});assert code==200
    code,s,_=obj(f'/api/flow/sessions/{sid}/submit',{'revision':1,'reference_id':s['input_reference']['reference_id'],'mode':'FPGA_Replacement'})
    assert code==503 and s['run_id'] is s['job_id'] is s['result'] is None
    _,s,_=obj(f'/api/flow/sessions/{sid}/select',{'revision':1,'source_kind':'phone_camera'})
    assert s['input_reference'] is None and s['state']=='PREVIEW_ONLY'
    code,s,_=obj(f'/api/flow/sessions/{sid}/freeze',{'revision':2,'comparison_id':cid});assert code==503 and s['input_reference'] is None
    for body in ({'revision':1,'source_kind':'phone_camera'},[],{'revision':2,'source_kind':'fake'}):
        assert obj(f'/api/flow/sessions/{sid}/select',body)[0]==409
    result.update(actual_preserved_conditions=55,pinned_original_player_assets=3,
        freeze_matches_real_P0_input=True,all_modes_no_job_on_missing_service=True,
        input_change_clears_previous_binding=True,original_producer_software_logging=True)
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':result['status'],'negative_checks':len(result['negative_checks']),'output':str(path)}))


if __name__=='__main__':main()

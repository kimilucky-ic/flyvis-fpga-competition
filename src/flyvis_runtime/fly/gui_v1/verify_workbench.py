"""Real P0/55-condition HTTP checks; faults mutate metadata only, never activity."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request,urlopen

import numpy as np
from data_store import DataStore,ROOT,read_json,sha256
from phase3_adapter import Phase3Adapter,VerifiedFiles
from server import handler_factory
from workbench import Workbench,RecordedPackage,validate_events,verify_package_header,inside


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8771');parser.add_argument('--output',default=str(ROOT/'gui_v1/evidence/phase4/workbench_acceptance.json'));args=parser.parse_args()
    store=DataStore();adapter=Phase3Adapter(store);assert len(adapter.packages)==1 and not adapter.errors
    wb=Workbench(store,adapter);assert not wb.import_errors
    pkg=next(iter(adapter.packages.values()));f=pkg.frozen;cid=f.comparison_id
    def get(path,base=args.url,body=None):
        req=Request(base+path,data=body,headers={'Content-Type':'application/json'})
        try:
            with urlopen(req,timeout=45) as r:return r.status,r.read(),dict(r.headers)
        except HTTPError as r:return r.code,r.read(),dict(r.headers)
    def obj(path,base=args.url):
        code,body,_=get(path,base);assert code==200,(path,code,body[:200]);return json.loads(body)
    result={'schema':'flyvis-phase4-GUI-acceptance-v1','status':'PASS','utc':datetime.now(timezone.utc).isoformat(),'display_kind':'offline_replay','neural_inference_executed':False,'board_executed':False,'new_live_backend_connected':False,'negative_tests':[],'real_board_positive_import':'NOT_RUN: actual producer handoff absent; admission locked'}
    catalog=obj('/api/catalog');assert len(catalog['datasets'])==7 and sum(len(d['conditions']) for d in catalog['datasets'])==55
    status=obj('/api/workbench');assert status['status']=='READY_FOR_EVIDENCE' and len(status['comparisons'])==1
    assert status['execution_backend']['status']=='NOT_AVAILABLE' and status['execution_backend']['run_id'] is status['execution_backend']['job_id'] is None
    info=obj('/api/workbench/comparisons/'+cid);expected=wb.info(cid)
    # DataStore records its own verification wall time for each process.
    expected['preview']['dataset']['verification']=info['preview']['dataset']['verification']
    assert info==expected
    assert info['modes']['Sham_Ablation']['status']==info['modes']['FPGA_Replacement']['status']=='NOT_AVAILABLE'
    assert info['current_board_connection']['board_id'] is None and info['current_backend_connection']['status']=='NOT_AVAILABLE'
    assert not info['formal_functional_reports'] and info['official_DSI']['status']=='NOT_AVAILABLE'
    assert np.array_equal(info['input_time_s'],f.time) and np.array_equal(info['activity_time_s'],f.activity_time)
    assert obj('/api/workbench/camera')['capture_open'] is False
    for run in info['runs']:
        rid=run['run_id'];mode=run['mode'];code,body,headers=get(run['activity_url']);assert code==200
        assert body==np.ascontiguousarray(pkg.arrays[mode][:,f.central_ids],dtype='<f4').tobytes()
        for key,value in {'X-Run-ID':rid,'X-Comparison-ID':cid,'X-Source-SHA256':run['source_activity_sha256'],'X-Display-Kind':'offline_replay'}.items():assert headers[key]==value
        assert run['board_connected_now'] is None and run['board_used'] is False and all(v is None for v in run['hardware_metrics'].values())
        events=obj(run['evidence_url']);path=pkg.roles[run['step_status_role']]
        original=[json.loads(line) for line in path.read_text('utf-8').splitlines() if line.strip()]
        assert events['events']==original and events['source_sha256']==sha256(path) and events['event_schema']=='producer_original_P0'
        assert len(original)==(800 if mode=='Full_GPU' else 1600)
        for k in [0,199,400,799]:
            step=wb.step(rid,k)
            assert step['input_time_s']==f.time[k] and step['activity_time_s']==f.activity_time[k]
            assert step['pl_status']=='NOT_APPLICABLE' and step['candidate'] is None and step['candidate_status']=='NOT_RECORDED'
            assert step['validation_status']=='PASS_SOURCE_CHAIN' and not step['selected_step_is_execution_progress']
            if mode=='Full_GPU':assert step['unified_commit'] is None and step['commit_status']=='REFERENCE_RECORDED'
            else:assert step['unified_commit']['state_token']==k+1 and step['commit_status']=='COMMITTED_RECORDED'
            assert obj(f'/api/workbench/runs/{rid}/steps/{k}')==step
        assert get(f'/api/workbench/runs/{rid}/steps/800')[0]==400
        assert get(f'/api/workbench/runs/{rid}/functional-report')[0]==400
    assert info['errors']==pkg.errors and max(info['errors']['full']['max_abs'])==9.5367431640625e-7
    for path in ['/api/workbench/runs/no_such_run/activity.bin','/api/workbench/comparisons/'+'0'*64]:
        code,body,_=get(path);assert code==404 and json.loads(body)['status']=='NOT_AVAILABLE'
    for mode in info['modes']:
        code,body,_=get('/api/workbench/jobs',body=json.dumps({'comparison_id':cid,'mode':mode}).encode());reply=json.loads(body)
        assert code==503 and reply['status']=='NOT_AVAILABLE' and reply['backend_status']=='not_connected'
        assert all(reply[k] is None for k in ['run_id','job_id','execution_kind','result'])
    assert get('/api/inference',body=b'{}')[0]==503
    # Header/state faults use identities from actual accepted sources, no neuron fixtures.
    base_run=dict(info['runs'][0],comparison_id=cid,identity_fingerprint=f.fingerprint,origin_execution_kind='reused_verified_actual_computation')
    desc=dict(schema='flyvis-workbench-evidence-v1',comparison_id=cid,display_kind='offline_replay',identity_fingerprint=f.fingerprint,runs=[base_run])
    acceptance=dict(status='PASS',comparison_id=cid,evidence_scope='actual_computation',production_data_unchanged=True,accepted_run_ids=[base_run['run_id']])
    verify_package_header(desc,acceptance)
    original_full=wb.events(base_run['run_id'])['events']
    reference_projection=[{'seq':k,'run_id':base_run['run_id'],'comparison_id':cid,'step_id':k,'type':'REFERENCE_RECORDED','before_digest':e['before_digest'],'input_digest':e['input_digest'],'after_digest':e['after_digest']} for k,e in enumerate(original_full)]
    ref_progress=validate_events(reference_projection,dict(base_run,comparison_id=cid),800)
    assert ref_progress['reference_steps']==800 and ref_progress['committed_steps']==0
    def reject(name,fn):
        try:fn()
        except (ValueError,KeyError,TypeError,OSError) as error:result['negative_tests'].append({'test':name,'status':'PASS_REJECTED','error':str(error)})
        else:raise AssertionError('Fault accepted: '+name)
    header_faults=[('replay_as_live',lambda d:d.update(display_kind='live')),('wrong_cohort',lambda d:d.update(comparison_id='0'*64)),('missing_initial_identity',lambda d:d['identity_fingerprint'].pop('initial')),('cross_mode_state',lambda d:d['runs'][0].update(identity_fingerprint=dict(f.fingerprint,initial='0'*64))),('simulation_origin',lambda d:d['runs'][0].update(origin_execution_kind='simulation')),('simulation_as_board',lambda d:d['runs'][0].update(mode='FPGA_Replacement',evidence_level='RTL_SIMULATION',board={})),('formal_spec_as_ablation',lambda d:d['runs'][0].update(mode='Sham_Ablation',variant='Ablation'))]
    for name,change in header_faults:
        altered=deepcopy(desc);change(altered);reject(name,lambda:verify_package_header(altered,acceptance))
    for name,change in [('unaccepted',lambda a:a.update(status='NOT_RUN')),('uncovered_run',lambda a:a.update(accepted_run_ids=[])),('software_simulation',lambda a:a.update(evidence_scope='software_simulation'))]:
        altered=deepcopy(acceptance);change(altered);reject(name,lambda:verify_package_header(desc,altered))
    br=next(r for r in info['runs'] if r['mode']=='Python_Replacement');original=wb.events(br['run_id'])['events'];real=next(e for e in original if e['status']=='PREPARED')
    # Pure protocol fault fixtures, not newly observed execution events.
    prepared={'seq':0,'run_id':br['run_id'],'comparison_id':cid,'step_id':0,'type':'PREPARED','request_digest':real['request_digest'],'input_digest':real['input_digest'],'old_state_digest':real['old_full_digest']}
    validate_events([prepared],dict(br,comparison_id=cid),800)
    for name,change in [('wrong_run',lambda e:e.update(run_id='missing')),('wrong_request',lambda e:e.update(request_digest='bad')),('out_of_range',lambda e:e.update(step_id=800)),('out_of_order',lambda e:e.update(seq=7))]:
        altered=deepcopy(prepared);change(altered);reject(name,lambda:validate_events([altered],dict(br,comparison_id=cid),800))
    for typ in ['UNIFIED_COMMITTED','VALIDATION_ACCEPTED','PL_STARTED','PL_SUBMITTED']:
        e=dict(prepared,seq=1,type=typ);reject('premature_'+typ,lambda:validate_events([prepared,e],dict(br,comparison_id=cid),800))
    reject('path_escape',lambda:inside(ROOT/'gui_v1','../outside'))
    with tempfile.TemporaryDirectory(dir=ROOT/'gui_v1/evidence/phase4',prefix='fault_') as temp:
        tmp=Path(temp);bad=tmp/'invalid_config.json';bad.write_text(json.dumps({'schema':'wrong','evidence_packages':[]}),encoding='utf-8')
        # Self-declared board PASS is explicitly rejected before reading any arrays.
        board_desc=deepcopy(desc);board_desc['runs'][0].update(mode='FPGA_Replacement',evidence_level='ACTUAL_BOARD_CLOSED_LOOP',board={'board_id':'METADATA_FAULT_FIXTURE_NOT_EXECUTED','device':'NOT_A_BOARD','bit_sha256':f.fingerprint['model'],'hwh_sha256':f.fingerprint['model']})
        board_accept=dict(acceptance,physical_board_execution=True,live_feedback_closed_loop=True)
        for name,value in [('descriptor.json',board_desc),('manifest.json',{'files':[]}),('acceptance.json',board_accept)]:
            (tmp/name).write_text(json.dumps(value),encoding='utf-8')
        pins={name:sha256(tmp/name) for name in ['descriptor.json','manifest.json','acceptance.json']}
        reject('self_declared_board_PASS_stays_locked',lambda:RecordedPackage({'root':str(tmp),'pins':pins},store))
        assert Workbench(store,adapter,bad).import_errors and len(store.datasets)==7
        with patch('phase3_adapter.Phase3Adapter',return_value=adapter):handler=handler_factory(store,workbench_config_path=bad)
        server=ThreadingHTTPServer(('127.0.0.1',0),handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            url=f'http://127.0.0.1:{server.server_port}';assert obj('/api/health',url)['status']=='ok' and len(obj('/api/catalog',url)['datasets'])==7
            assert obj('/api/workbench',url)['import_errors'] and obj('/api/workbench',url)['comparisons'][0]['comparison_id']==cid
            assert get('/api/datasets/edge24/samples/0/activity.bin',url)[0]==200
        finally:server.shutdown();server.server_close();thread.join(3);assert not thread.is_alive()
        copied=tmp/'workbench.json';copied.write_bytes((ROOT/'gui_v1/workbench.json').read_bytes());checked=VerifiedFiles();checked.check(copied,sha256(copied));copied.write_bytes(copied.read_bytes()+b' ');reject('changed_source',checked.assert_unchanged)
        config=tmp/'missing_evidence.json';config.write_text(json.dumps({'schema':'flyvis-workbench-config-v1','execution_backend':None,'camera_backend':None,'evidence_packages':[{'root':str(tmp),'pins':{'descriptor.json':'0'*64,'manifest.json':'0'*64,'acceptance.json':'0'*64}}]}),encoding='utf-8')
        invalid=Workbench(store,adapter,config);assert invalid.import_errors and len(invalid.comparisons())==1 and len(store.datasets)==7
        with patch('workbench.RecordedPackage',side_effect=EOFError('TEST_ONLY: malformed optional array')):truncated=Workbench(store,adapter,config)
        assert truncated.import_errors and len(truncated.comparisons())==1 and len(store.datasets)==7
        result['negative_tests'].append({'test':'optional_truncated_array_preserves_legacy_and_P0','status':'PASS_ISOLATED'})
    assert all(sha256(path)==value for path,value in pkg.checked.items()) and all(sha256(path)==value for path,value in f.checked.items())
    result.update(comparison_id=cid,legacy_conditions=55,activity_values_bitwise_verified=104000,input_values_time_grid=800*721,original_events_unchanged=2400,step_semantics_checked=8,step_ids_per_mode=[0,199,400,799],original_800_state_chains_reused_from_independent_phase3_verifier=True,error_full_max_abs=max(info['errors']['full']['max_abs']),source_files_unchanged=True,optional_fault_preserves_legacy_and_P0=True)
    Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'status':'PASS','negative_tests':len(result['negative_tests']),'output':args.output}))


if __name__=='__main__':main()

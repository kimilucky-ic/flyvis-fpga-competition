"""Bounded CPU/hash/HTTP acceptance of already executed science B. No inference."""
import argparse
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import numpy as np

from data_store import ROOT, DataStore, read_json
from scientific_pilot import ScientificPilot, MODES
from scientific_sparse import ScientificSparse, COUNTS, CONDITIONS, METRICS, validate_partition
from server import handler_factory


def measured(flow,reference,roi):
    """Independent CPU check of sealed metric values; never produces neural/flow data."""
    ref=np.asarray(reference,dtype=np.float64);val=np.asarray(flow,dtype=np.float64)
    baseline=ref[160:200].mean(axis=0)
    ref=(ref-baseline)[200:286][:,:,roi];val=(val-baseline)[200:286][:,:,roi]
    energy=np.sum(ref*ref);q=float(np.sum(ref*val)/energy);m=float(np.sqrt(np.sum(val*val)/energy))
    return {'Q':q,'magnitude_ratio':m,'field_error_E':float(np.sqrt(np.sum((val-ref)**2)/energy)),
        'angle_deg':float(np.degrees(np.arccos(np.clip(q/m,-1,1))))}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8773')
    parser.add_argument('--output',default=str(ROOT/'gui_v1/evidence/scientific_sparse_20261012/software_acceptance.json'));args=parser.parse_args()
    def get(path):
        with urlopen(args.url+path,timeout=60) as response:return response.read(),dict(response.headers)
    def js(path):return json.loads(get(path)[0])
    store=DataStore();pilot=ScientificPilot(store);reader=ScientificSparse(store,pilot)
    status=js('/api/scientific-sparse');assert status==reader.status()
    transports=[];metric_errors=[];endpoint_values=0;pre_state_values=0;clamped_values=0
    for condition in CONDITIONS:
        info=js('/api/scientific-sparse/conditions/'+condition);assert info==reader.info(condition)
        body,headers=get(f'/api/scientific-sparse/conditions/{condition}/input.bin');assert body==reader.binary(condition)
        assert headers['X-Source-SHA256']==pilot.conditions[condition]['stimulus_sha256']
        old_full=pilot.array(f'artifacts/pilot_gpu_r1/{condition}/Full/activities_full.npy')[0]
        for mode in ['Full',*['KEEP_'+str(c) for c in COUNTS]]:
            body,headers=get(f'/api/scientific-sparse/conditions/{condition}/{mode}/flow.bin');assert body==reader.binary(condition,mode)
            assert headers['X-Source-SHA256']==reader.flow_identity(condition,mode)['sha256']
            assert headers['X-Source-Run-ID']==reader.flow_identity(condition,mode)['run_id']
            assert headers['X-Evidence-Level']=='SOFTWARE_SPARSE_RETAIN' and headers['X-Display-Kind']=='OFFLINE_REPLAY' and headers['X-PL-Execution']=='false'
            transports.append({'condition':condition,'mode':mode,'values':485*2*721,'bitwise_original':True,'source_run_id':headers['X-Source-Run-ID']})
            if mode=='Full':continue
            values=measured(reader.flows[condition][mode],pilot.flows[condition]['Sham'],reader.roi)
            for key in METRICS:
                error=abs(values[key]-reader.metrics[condition][mode][key]);assert error<1e-10
                metric_errors.append(error)
            count=int(mode.split('_')[1]);activity=reader.array(f'artifacts/gpu_r1/{condition}/{mode}/activities_full.npy')[0]
            assert activity.shape==(485,45669) and activity.dtype==np.float32
            inactive=reader.array(f'inactive_{count}.npy')
            for start in range(0,200,32):
                end=min(200,start+32);assert np.array_equal(activity[start:end],old_full[start:end]);pre_state_values+=(end-start)*45669
            for start in range(200,485,32):
                end=min(485,start+32);assert np.all(activity[start:end,inactive]==0);clamped_values+=(end-start)*len(inactive)
            if count in (0,5768):
                reference=old_full if count==5768 else pilot.array(f'artifacts/pilot_gpu_r1/{condition}/CLAMP_T4T5/activities_full.npy')[0]
                for start in range(0,485,32):
                    end=min(485,start+32);assert np.array_equal(activity[start:end],reference[start:end]);endpoint_values+=(end-start)*45669
    set_values=0
    for count in COUNTS:
        actual=js(f'/api/scientific-sparse/sets/{count}');assert actual==reader.node_set(count)
        assert len(actual['global_ids'])==len(actual['nodes'])==count;set_values+=count
        for prefix in ('keep','inactive'):
            name=f'{prefix}_{count}.npy';assert get('/api/scientific-sparse/files/'+name)[0]==reader.files[name].read_bytes()
    for name in ('SPARSE_REPORT.md','sparsity_curve.csv','FINAL_HANDOFF.json','DELIVERY_MANIFEST.json'):
        assert get('/api/scientific-sparse/files/'+name)[0]==(reader.root/name).read_bytes()
    old_samples=0
    assert len(js('/api/catalog')['datasets'])==7
    for dataset in store.datasets.values():
        for i in range(len(dataset.conditions)):
            assert js(f'/api/datasets/{dataset.id}/samples/{i}')['execution_kind']=='offline_replay';old_samples+=1
        assert get(dataset.sample(0)['activity']['url'])[0]==np.asarray(dataset.activity[0],dtype='<f4').tobytes()
    assert old_samples==55
    assert js('/api/datasets/edge24/directions?cell=T4c&intensity=1')['official_metric']['official_dsi']==0.627361980585308
    assert js('/api/phase3')['comparisons'] and js('/api/workbench')['comparisons'] and js('/api/flow')['schema']
    assert js('/api/autorunner')['records'][0]['summary']['results']['FullGPU']['actual_new_computation'] is False
    for condition in CONDITIONS:
        assert js('/api/scientific-pilot/conditions/'+condition)==pilot.info(condition)
        for mode in MODES:assert get(f'/api/scientific-pilot/conditions/{condition}/{mode}/flow.bin')[0]==pilot.binary(condition,mode)
    negatives=[]
    for path in ('/api/scientific-sparse/conditions/ON0','/api/scientific-sparse/sets/1000','/api/scientific-sparse/conditions/ON60/FPGA/flow.bin','/api/scientific-sparse/files/../../server.py','/api/scientific-sparse/files/USER_AUTHORIZATION_IMMEDIATE.json','/api/scientific-sparse/files/artifacts/gpu_r1/ON60/KEEP_488/activities_full.npy'):
        try:get(path);raise AssertionError('Unexpected source/mode admitted')
        except HTTPError as error:assert error.code==404;negatives.append(path)
    for path in ('/api/scientific-sparse/submit','/api/inference','/api/workbench/submit'):
        try:urlopen(Request(args.url+path,data=b'{}',headers={'Content-Type':'application/json'}),timeout=10);raise AssertionError('Execution admitted')
        except HTTPError as error:assert error.code==503 and json.load(error)['result'] is None;negatives.append(path)
    keep=reader.array('keep_488.npy');inactive=reader.array('inactive_488.npy')
    for bad_keep,bad_inactive,radius,label in ((keep[::-1],inactive,4,'unsorted IDs'),(np.concatenate((keep,keep[:1])),inactive,4,'duplicate IDs'),(keep,inactive[1:],4,'incomplete partition'),(keep,inactive,6,'incorrect radius'),(keep.astype(np.float32),inactive,4,'non-int64 IDs')):
        try:validate_partition(bad_keep,bad_inactive,reader.nodes,radius);raise AssertionError('Bad set admitted')
        except ValueError:negatives.append(label)
    with tempfile.TemporaryDirectory(prefix='flyvis_gui_sparse_') as tmp:
        bad=Path(tmp)/'bad.json';config=dict(reader.config,manifest_sha256='0'*64);bad.write_text(json.dumps(config),encoding='utf-8')
        try:ScientificSparse(store,pilot,bad);raise AssertionError('Bad hash admitted')
        except ValueError:negatives.append('bad manifest hash rejected')
        isolated=ThreadingHTTPServer(('127.0.0.1',0),handler_factory(store,sparse_config_path=bad));thread=Thread(target=isolated.serve_forever,daemon=True);thread.start()
        try:
            base=f'http://127.0.0.1:{isolated.server_port}'
            with urlopen(base+'/api/scientific-sparse',timeout=30) as response:assert json.load(response)['status']=='NOT_AVAILABLE'
            with urlopen(base+'/api/catalog',timeout=30) as response:assert len(json.load(response)['datasets'])==7
            with urlopen(base+'/api/scientific-pilot',timeout=30) as response:assert json.load(response)['status']=='VERIFIED'
            negatives.append('optional B failure leaves old55 and pilot available')
        finally:isolated.shutdown();isolated.server_close();thread.join()
    path=reader.files['sparsity_curve.csv'];stamp=reader.stamps[path];reader.stamps[path]=(0,0,0)
    try:reader.info('ON60');raise AssertionError('Changed source displayed')
    except ValueError:negatives.append('changed source invalidates B before display')
    finally:reader.stamps[path]=stamp
    report={'status':'PASS_READ_ONLY_SCIENTIFIC_SPARSE','utc':datetime.now(timezone.utc).isoformat(),'run_id':reader.config['run_id'],
        'evidence_level':'SOFTWARE_SPARSE_RETAIN','display_kind':'OFFLINE_REPLAY','FPGA_status':'NOT_CONNECTED','PL_execution':False,
        'sealed_files_verified':len(reader.manifest['files']),'manifest_sha256':reader.config['manifest_sha256'],
        'flow_transports':transports,'B_flow_values':14*485*2*721,'Full_reference_flow_values':2*485*2*721,
        'input_values':2*485*721,'actual_retained_global_ids':set_values,'primary_metric_values':56,
        'metric_recomputation_max_error':max(metric_errors),'endpoint_activity_bitwise_values':endpoint_values,
        'pre_clamp_activity_bitwise_values':pre_state_values,'post_clamp_zero_values':clamped_values,
        'negative_checks':negatives,'legacy55_metadata':old_samples,'legacy_activity_exact_spotchecks':7,
        'legacy_official_DSI_P0_flow_and_pilot_preserved':True,'new_GPU_runs':0,'new_decoder_calls':0,'camera_operations':0,'board_operations':0,
        'sources_SHA256':{str(path):digest for path,digest in reader.checked.items()}}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({key:report[key] for key in ('status','B_flow_values','primary_metric_values','metric_recomputation_max_error','legacy55_metadata')}))


if __name__=='__main__':main()

"""Actual frozen input HTTP checks; rejection tests use metadata only.

Never generates or relabels activity as a successful Replacement computation.
Positive Full/Python import remains NOT_RUN until B delivers the actual package.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
from threading import Thread
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import numpy as np

from data_store import DataStore, ROOT, read_json, sha256
from phase3_adapter import Phase3Adapter, VerifiedFiles, FrozenVideoInput
from server import handler_factory


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default=str(ROOT/'gui_v1/evidence/phase3/input_preparation_regression.json'))
    args=parser.parse_args()
    store=DataStore()
    input_test_dir=tempfile.TemporaryDirectory(dir=ROOT/'gui_v1/evidence/phase3')
    input_test_config=Path(input_test_dir.name)/'input_only.json'
    config=read_json(ROOT/'gui_v1/phase3.json');config['comparison_packages']=[]
    input_test_config.write_text(json.dumps(config),encoding='utf-8')
    adapter=Phase3Adapter(store,input_test_config)
    status=adapter.status()
    assert status['status']=='waiting_for_accepted_comparison' and not status['errors']
    frozen=adapter.input
    assert frozen is not None and not adapter.packages
    checked_before={str(p):digest for p,digest in frozen.checked.items()}
    report={'schema':'flyvis-gui-phase3-preparation-acceptance-v1','utc':datetime.now(timezone.utc).isoformat(),
            'status':'PASS_GUI_PREPARATION','comparison_id':frozen.comparison_id,'input_files_sha256':checked_before,
            'positive_Full_Python_import':'NOT_RUN_NO_ACCEPTED_B_PACKAGE','FPGA_execution':'NOT_RUN',
            'new_GPU_inference':'NOT_RUN','tests':[]}
    tests=report['tests']

    def get(url,path):
        with urlopen(url+path,timeout=20) as r:return r.read(),dict(r.headers)

    class Quiet(handler_factory(store,phase3_config_path=input_test_config)):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Quiet)
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    url=f'http://127.0.0.1:{server.server_port}'
    try:
        catalog=json.loads(get(url,'/api/catalog')[0])
        assert len(catalog['datasets'])==7 and sum(len(d['conditions']) for d in catalog['datasets'])==55
        result=json.loads(get(url,'/api/phase3')[0]); assert result['status']==status['status']
        assert not any(result[m]['available'] for m in ['Full_GPU','Python_Replacement','FPGA_Replacement'])
        assert result['FPGA_Replacement']['pl_cycles'] is None and result['online_GPU_service']=='not_connected'
        input_info=json.loads(get(url,'/api/phase3/input')[0])
        data,headers=get(url,input_info['stimulus']['url'])
        assert data==frozen.stimulus[0,:,0].tobytes() and len(data)==800*721*4
        assert headers['X-Source-SHA256']==frozen.fingerprint['stimulus'] and headers['X-Comparison-ID']==frozen.comparison_id
        assert np.array_equal(np.frombuffer(data,dtype='<f4').reshape(800,721),store.datasets['controlled6'].stimulus[1,:,0])
        assert np.array_equal(input_info['input_time_s'],np.arange(800)*.005) and np.array_equal(input_info['activity_time_s'],np.arange(800)*.005+.005)
        for i in range(240):
            image,h=get(url,f'/api/phase3/input/frames/{i}.png')
            original=store.datasets['controlled6'].frame_path(i,1)
            assert image==original.read_bytes() and h['X-Source-SHA256']==sha256(original)
        for k,source in enumerate(input_info['input_source_indices']):
            assert source==np.searchsorted(np.arange(240)/60.,k*.005,side='right')-1
        tests.append({'test':'frozen_input_HTTP','status':'PASS','float32_values_bitwise_equal':800*721,'steps':800,'source_PNGs_exact':240,'source_ZOH_time_rows':800})
        rejected=[(f'/api/phase3/comparisons/{frozen.comparison_id}',409),
                  (f'/api/phase3/comparisons/{frozen.comparison_id}/Python_Replacement/activity.bin',409),
                  (f'/api/phase3/comparisons/{frozen.comparison_id}/FPGA_Replacement/activity.bin',404),
                  ('/api/phase3/input/frames/240.png',404),('/api/phase3/input/frames/../video_manifest.json',404)]
        for path,code in rejected:
            try:get(url,path);raise AssertionError('Unexpected open mode/path')
            except HTTPError as e:assert e.code==code,(path,e.code)
        req=Request(url+'/api/inference',data=b'{}',headers={'Content-Type':'application/json'},method='POST')
        try:urlopen(req);raise AssertionError('GPU unexpectedly connected')
        except HTTPError as e:
            payload=json.loads(e.read());assert e.code==503 and payload['result'] is None and payload['execution_kind'] is None
        tests.append({'test':'unadmitted_results_paths_and_GPU_rejected','status':'PASS','HTTP_cases':len(rejected)+1})
    finally:
        server.shutdown();server.server_close();thread.join(3)
    assert not thread.is_alive()

    # Mutate metadata in memory only. Original files/arrays remain untouched.
    probes=[('wrong_condition','video_manifest.json',lambda d:d.update(condition_id='MovingEdge')),
            ('wrong_sample','video_manifest.json',lambda d:d.update(original_sample=0)),
            ('485_steps','video_manifest.json',lambda d:d.update(steps=485)),
            ('wrong_dt','video_manifest.json',lambda d:d.update(dt_s=.01)),
            ('wrong_shape','video_manifest.json',lambda d:d.update(shape=[6,800,1,721])),
            ('camera_claim','video_manifest.json',lambda d:d.update(source_is_camera=True)),
            ('extra_warmup','video_manifest.json',lambda d:d.update(no_additional_warmup=False)),
            ('not_frozen','video_manifest.json',lambda d:d.update(status='NOT_RUN')),
            ('wrong_comparison','video_manifest.json',lambda d:d.update(comparison_id='0'*64)),
            ('different_stimulus','video_manifest.json',lambda d:d['identity_fingerprint'].update(stimulus='0'*64)),
            ('wrong_parent','video_manifest.json',lambda d:d.update(parent_stimulus_sha256='0'*64)),
            ('wrong_video','video_manifest.json',lambda d:d.update(source_mp4_sha256='0'*64)),
            ('G2_initial','identity_manifest.json',lambda d:d.update(initial_state_sha256='0'*64)),
            ('different_model','identity_manifest.json',lambda d:d.update(model_id='different')),
            ('different_parameters','identity_manifest.json',lambda d:d.update(expanded_parameters_sha256='0'*64)),
            ('relaxed_tolerance','metric_profile.json',lambda d:d.update(atol=.001)),
            ('post_hoc_tolerance','metric_profile.json',lambda d:d.update(registered_before_execution=False))]
    input_config=read_json(input_test_config)
    for name,filename,mutate in probes:
        def altered(path):
            value=read_json(path)
            if Path(path).name==filename:value=deepcopy(value);mutate(value)
            return value
        try:
            with patch('phase3_adapter.read_json',side_effect=altered):FrozenVideoInput(input_config,store.root,store.datasets['controlled6'])
            raise AssertionError(f'Bad input accepted: {name}')
        except ValueError as e:tests.append({'test':name,'status':'PASS_REJECTED_METADATA','error':str(e)})
    with tempfile.TemporaryDirectory(dir=ROOT/'gui_v1/evidence/phase3') as temp:
        temp=Path(temp)
        marker=temp/'metadata.txt';marker.write_text('identity probe',encoding='utf-8')
        verified=VerifiedFiles();verified.check(marker,sha256(marker));marker.write_text('changed identity',encoding='utf-8')
        try:verified.assert_unchanged();raise AssertionError('Changed source accepted')
        except ValueError:tests.append({'test':'changed_verified_file','status':'PASS_REJECTED_METADATA'})
        broken=temp/'broken.json';broken.write_text('{broken',encoding='utf-8')
        bad=Phase3Adapter(store,broken)
        assert bad.status()['status']=='input_unavailable' and bad.errors
        missing=temp/'missing.json'
        assert Phase3Adapter(store,missing).status()['status']=='input_unavailable'
        config=read_json(ROOT/'gui_v1/phase3.json');config['input_pins']['video_manifest.json']='0'*64
        wrong=temp/'wrong.json';wrong.write_text(json.dumps(config),encoding='utf-8')
        assert Phase3Adapter(store,wrong).status()['status']=='input_unavailable'
        class BadOptional(handler_factory(store,phase3_config_path=broken)):
            def log_message(self,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),BadOptional)
        thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            url=f'http://127.0.0.1:{server.server_port}'
            assert json.loads(get(url,'/api/phase3')[0])['input'] is None
            catalog=json.loads(get(url,'/api/catalog')[0])
            assert sum(len(d['conditions']) for d in catalog['datasets'])==55
            original=get(url,'/api/datasets/edge24/samples/0/activity.bin')[0]
            assert original==store.datasets['edge24'].activity[0].astype('<f4').tobytes()
            tests.append({'test':'optional_bad_handoff_does_not_block_55_conditions','status':'PASS','missing_config_rejected':True,'malformed_config_rejected':True,'wrong_SHA_rejected':True,'legacy_activity_bitwise_equal':True})
        finally:
            server.shutdown();server.server_close();thread.join(3)
    assert all(sha256(Path(p))==digest for p,digest in checked_before.items())
    report['original_input_files_unchanged']=True
    report['conditions_preserved']=55
    input_test_dir.cleanup()
    Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps({'status':report['status'],'tests':len(tests),'output':args.output}))


if __name__=='__main__':main()

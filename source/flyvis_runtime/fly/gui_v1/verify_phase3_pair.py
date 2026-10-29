"""Verify actual accepted A/B outputs and HTTP, without executing inference."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import json
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import urlopen

import numpy as np

from data_store import DataStore,ROOT,read_json,sha256
from phase3_adapter import Phase3Adapter
from native_comparison import NativeAnimationComparison


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8771');parser.add_argument('--output',default=str(ROOT/'gui_v1/evidence/phase3/pair_http_acceptance.json'));args=parser.parse_args()
    store=DataStore();adapter=Phase3Adapter(store)
    assert not adapter.errors and len(adapter.packages)==1
    p=next(iter(adapter.packages.values()));f=p.frozen
    def get(path):
        with urlopen(args.url+path,timeout=30) as response:return response.read(),dict(response.headers)
    status=json.loads(get('/api/phase3')[0]);assert status['status']=='ready' and status['display_kind']=='offline_replay' and status['Full_GPU']['available'] and status['Python_Replacement']['available'] and not status['FPGA_Replacement']['available']
    base='/api/phase3/comparisons/'+f.comparison_id
    info=json.loads(get(base)[0]);assert info['comparison_id']==f.comparison_id and info['errors']==p.errors
    for mode in ['Full_GPU','Python_Replacement']:
        data,headers=get(base+'/'+mode+'/activity.bin')
        assert data==np.ascontiguousarray(p.arrays[mode][:,f.central_ids],dtype='<f4').tobytes()
        assert len(data)==800*65*4 and headers['X-Run-ID']==p.descriptor['modes'][mode]['run_id'] and headers['X-Comparison-ID']==f.comparison_id and headers['X-Source-SHA256']==p.descriptor['modes'][mode]['source_activity_sha256'] and headers['X-Display-Kind']=='offline_replay'
    data,h=get('/api/phase3/input/stimulus.bin');assert data==f.stimulus[0,:,0].tobytes() and h['X-Comparison-ID']==f.comparison_id
    error=np.max(np.abs(p.arrays['Python_Replacement'][:,f.central_ids].astype(np.float64)-p.arrays['Full_GPU'][:,f.central_ids].astype(np.float64)),axis=1)
    assert np.array_equal(error,p.errors['central65']['max_abs'])
    report=dict(schema='flyvis-gui-phase3-real-pair-HTTP-acceptance-v1',status='PASS',utc=datetime.now(timezone.utc).isoformat(),comparison_id=f.comparison_id,display_kind='offline_replay',steps=800,activity_values_bitwise_verified=2*800*65,input_values_bitwise_verified=800*721,run_ids={m:p.descriptor['modes'][m]['run_id'] for m in p.arrays},max_abs={k:max(v['max_abs']) for k,v in p.errors.items()},violations={k:sum(v['violations']) for k,v in p.errors.items()},state_chain_800_verified_per_mode=True,source_files_verified=len(p.checked),neural_inference_executed_by_GUI=False,FPGA_executed=False,negative_tests=[])
    # Faults mutate metadata in memory only, after verifying original hashes.
    # No recorded activity, upstream descriptor or upstream report is changed.
    spec=read_json(ROOT/'gui_v1/phase3.json')['comparison_packages'][0]
    original_read=read_json
    mutations=[('schema',lambda d:d.update(schema='wrong')),('unaccepted_handoff',lambda d:d.update(status='NOT_RUN')),
               ('wrong_comparison',lambda d:d.update(comparison_id='0'*64)),('old_condition',lambda d:d.update(condition_id='MovingEdge')),
               ('485_steps',lambda d:d.update(steps=485)),('wrong_dt',lambda d:d.update(dt_s=.01)),
               ('wrong_video',lambda d:d.update(video_sha256='0'*64)),('FPGA_claim',lambda d:d.update(FPGA_execution=True)),
               ('FPGA_available',lambda d:d['mode_status']['FPGAReplacement'].update(available=True)),
               ('replay_as_new_origin',lambda d:d['mode_status']['PythonReplacement'].update(execution_kind='offline_replay')),
               ('recorded_as_live',lambda d:d['mode_status']['PythonReplacement'].update(display_mode='live')),
               ('wrong_full_path',lambda d:d['mode_status']['FullGPU'].update(source_all_nodes_path=str(ROOT/'not_a_result.npy'))),
               ('wrong_activity_hash',lambda d:d['mode_status']['FullGPU'].update(source_all_nodes_sha256='0'*64))]
    for name,mutate in mutations:
        def altered(path):
            value=original_read(path)
            if Path(path).name=='GUI_READONLY_HANDOFF.json':value=deepcopy(value);mutate(value)
            return value
        try:
            with patch('native_comparison.read_json',side_effect=altered):NativeAnimationComparison(spec,f)
            raise AssertionError('Fault not rejected: '+name)
        except ValueError as e:report['negative_tests'].append(dict(test=name,status='PASS_REJECTED',error=str(e)))
    assert all(sha256(path)==digest for path,digest in p.checked.items()) and all(sha256(path)==digest for path,digest in f.checked.items())
    report['source_files_unchanged']=True
    Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps(dict(status='PASS',activity_values=report['activity_values_bitwise_verified'],negative_tests=len(report['negative_tests']),output=args.output)))


if __name__=='__main__':main()

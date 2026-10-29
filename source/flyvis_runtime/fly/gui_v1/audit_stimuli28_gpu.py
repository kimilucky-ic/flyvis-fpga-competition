"""Independent bounded CPU audit of saved GPU results, not new experiments."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import numpy as np

HERE=Path(__file__).resolve().parent
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def main(root):
    started=time.perf_counter();pack_root=HERE.parent.parent/'fpga/flyvis-circuit-selection/controlled_stimuli_20261019_v1'
    pack=read(pack_root/'PACK.json');result=read(root/'RESULT.json');manifest=read(root/'RESULT_MANIFEST.json')
    assert result['total_neural_steps']==result['total_decoder_frames']==13580
    assert result['PACK_sha256']==sha(pack_root/'PACK.json')=='7291e37f21a94244b81fb916dca0296d310ce354ac32fc4c8e9077d6aeac3500'
    assert result['GPU'] is True and result['PL_execution'] is False
    for f in manifest['files']:
        p=(root/f['path']).resolve();assert p.is_relative_to(root.resolve())
        assert p.stat().st_size==f['bytes'] and sha(p)==f['sha256'],f['path']
    from line11_live_cpu import reference_engine
    engine=reference_engine();initial=np.load(root/'initial_state.npy',allow_pickle=False)
    assert np.array_equal(engine.activity,initial)
    ids=np.load(root/'T4T5_global_ids.npy',allow_pickle=False).reshape(-1)
    audit=[];selected_states=[];selected_flows=[];decoder_rows=[]
    for c,run in zip(pack['conditions'],result['conditions']):
        cid=c['condition_id'];assert cid==run['condition_id']
        folder=root/'conditions'/cid
        load=lambda n:np.load(folder/(n+'.npy'),mmap_mode='r',allow_pickle=False)
        x=load('input');full=load('states');spatial=load('spatial');means=load('means');flow=load('flow')
        assert np.array_equal(x,np.load(pack_root/c['paths']['input']['path'],allow_pickle=False))
        assert full.shape==(485,45669) and full.dtype==np.float32 and np.isfinite(full).all()
        assert flow.shape==(485,2,721) and flow.dtype==np.float32 and np.isfinite(flow).all()
        assert np.array_equal(spatial,full[:,ids])
        actual_means=spatial.reshape(485,8,721).mean(axis=2,dtype=np.float64)
        assert np.allclose(means,actual_means,atol=1e-12,rtol=0)
        assert run['initial_raw_sha256']==result['common_initial_raw_sha256']
        checks=[]
        for k in (0,199,200,300,400,484):
            engine.activity[:]=initial if k==0 else full[k-1]
            expected=engine.advance(np.array(x[k],copy=True))
            delta=full[k].astype(np.float64)-expected.astype(np.float64)
            passed=bool(np.allclose(full[k],expected,atol=1e-5,rtol=1e-5))
            checks.append(dict(step_id=k,allclose=passed,max_abs=float(np.abs(delta).max()),
                               bitwise_equal=bool(np.array_equal(full[k].view('<u4'),expected.view('<u4')))))
            assert passed,(cid,k,checks[-1])
        if cid in ('BAR_BRIGHT_RIGHT','EDGE_ON_RIGHT','EDGE_OFF_RIGHT','DOT_CCW'):
            for k in (200,300,484):
                selected_states.append(np.array(full[k],copy=True));selected_flows.append(np.array(flow[k],copy=True))
                decoder_rows.append(dict(condition_id=cid,step_id=k))
        audit.append(dict(condition_id=cid,all_485_full_states_finite=True,all_spatial_exact=True,
                          all_485_flow_finite=True,all_means_match=True,same_old_CPU_step_checks=checks))
    from line11_ddr_flow import CPUDecoder
    decoder=CPUDecoder(root/'independent_cpu_decoder_cache')
    cpu_flow=decoder.decode(np.array(selected_states,dtype=np.float32))
    for row,cpu,gpu in zip(decoder_rows,cpu_flow,selected_flows):
        row.update(max_abs=float(np.max(np.abs(cpu-gpu))),allclose=bool(np.allclose(cpu,gpu,atol=1e-5,rtol=1e-5)))
        assert row['allclose'],row
    assert not decoder.torch.cuda.is_initialized()
    acceptance=dict(schema='flyvis-stimuli28-gpu-acceptance/v1',
        status='PASS_ACTUAL_GPU_DATA_AND_TARGETED_NUMERICAL_AUDIT',
        PACK_sha256=result['PACK_sha256'],manifest_sha256=sha(root/'RESULT_MANIFEST.json'),
        actual_GPU_conditions=28,actual_GPU_neural_steps=13580,actual_GPU_decoded_frames=13580,
        complete_state_values_saved=28*485*45669,complete_state_finite_and_spatial_checks=28,
        numerical_audit_scope='168 independent strictFP32 CPU same-old-state one-step checks;12 saved-state CPU official-decoder comparisons. Not full sequential CPU replay or hardware equivalence.',
        atol=1e-5,rtol=1e-5,independent_CPU_one_step_checks=168,independent_CPU_decoder_frames=12,
        runs=audit,decoder_checks=decoder_rows,CPU_decoder_identity=decoder.identity,
        raw_input_unchanged=True,full_initial_state='original_bias_fp32',
        PL_execution=False,FPGA_status='NOT_CONNECTED',functional_acceptance='NOT_EVALUATED',
        display_kind='OFFLINE_REPLAY',elapsed_s=time.perf_counter()-started)
    with (root/'ACCEPTANCE.json').open('x',encoding='utf-8') as f:json.dump(acceptance,f,ensure_ascii=False,indent=2)
    print('PASS_ACTUAL_GPU_DATA_AND_TARGETED_NUMERICAL_AUDIT',round(acceptance['elapsed_s'],3),'seconds',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);main(p.parse_args().root)

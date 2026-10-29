"""Actual native GPU parameter, Full/R-only/H single-step identity confirmation."""
import sys, time, uuid
import numpy as np
from common import *


def main():
    out=HERE/'artifacts/preflight_r1'
    if out.exists():raise SystemExit('Preflight preserved; choose new namespace before repeat')
    out.mkdir(parents=True)
    torch=configure_gpu()
    from full_oracle import FullNetworkOracle
    from r_only import RStepService
    from gpu_adapter import GPUAdapter
    from coordinator import Coordinator
    meta,model,h,inputs,stimulus,initial,_,_,entries=read_input()
    start=time.monotonic()
    oracle=FullNetworkOracle(BUNDLE/'identity_manifest.json',device='cuda')
    # Oracle initialization checks every actual expanded official array digest.
    expected=oracle.step(torch.tensor(initial.copy(),device='cuda'),torch.tensor(stimulus[0,0,0].copy(),device='cuda'))
    expected=expected.cpu().numpy().copy()
    service=RStepService(*parameters_paths(),device='cuda')
    adapter=GPUAdapter(service,inputs)
    with np.load(BUNDLE/'expanded_parameters.npz',allow_pickle=False) as p:
        assert not np.isin(p['target_global'][service.original_edge_ids],h.h_ids).any()
    c=Coordinator(h,adapter,initial,str(uuid.uuid4()),meta['comparison_id'],'01_off_right')
    with native_full_forbidden() as guard:
        actual=c.step(0,make_input(stimulus[0,0,0],inputs))
    delta=np.abs(actual.astype(np.float64)-expected.astype(np.float64))
    assert not (delta>1e-5+1e-5*np.abs(expected.astype(np.float64))).any()
    assert c.next_step_id==h.step_count==adapter.calls==1 and guard['forbidden_native_call_count']==0
    oracle.assert_weights_unchanged();assert unchanged(entries)
    np.save(out/'Full_after_step0.npy',expected);np.save(out/'Python_after_step0.npy',actual)
    dump(out/'result.json',dict(status='PASS_ACTUAL_GPU_VIDEO_PREFLIGHT',evidence_level='SOFTWARE_ACTUAL_GPU_SINGLE_STEP',
        comparison_id=meta['comparison_id'],checkpoint_sha256=model['checkpoint_sha256'],
        expanded_parameters_sha256=model['expanded_parameters_sha256'],initial_state_sha256=model['initial_state_sha256'],
        stimulus_sha256=file_hash(BUNDLE/'stimulus.npy'),candidate_sha256=file_hash(parameters_paths()[2]),
        official_Full_expanded_arrays_checked_exact=True,R_target_H_edges=0,R_edge_count=service.n_r_edges,
        partition_counts=service.partition_counts,actual_R_calls=adapter.calls,actual_independent_H_steps=h.step_count,
        single_step_full_max_abs=float(delta.max()),nonfinite=0,violations=0,production_guard=guard,
        A_callable_provenance=load(HERE/'dependencies/provenance.json')['A_callable_reused_unchanged'],
        environment=dict(torch=torch.__version__,numpy=np.__version__,gpu=torch.cuda.get_device_name(0)),
        input_bundle_unchanged=True,wall_s=time.monotonic()-start,command=[sys.executable,*sys.argv],
        scope='actual A callable and official GPU native profile identity; single-step only, not800-step acceptance'))
    seal(out)
    print('PREFLIGHT_RESULT',load(out/'result.json')['status'],float(delta.max()),flush=True)


if __name__=='__main__':main()

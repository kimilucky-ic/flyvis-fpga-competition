"""Fresh-process, fresh-service replay of 32 LIVE closed-loop steps."""
from pathlib import Path
import os, sys, json, uuid, argparse
import numpy as np
from h_step import HUpdater, file_hash, array_hash
from coordinator import Coordinator
from run_closed_loop import native_full_forbidden, validate_parameters, manifest_verify
HERE=Path(__file__).resolve().parent
BUNDLE=HERE.parents[2]/'fly/gpu_phase2/artifacts/reference_bundle_v1'
STATIC=HERE.parent/'round1_20261010/artifacts/B_T5c/static_boundary.npz'
OUT=HERE/'artifacts/reproduce_prefix_r1'

def main():
    global BUNDLE,STATIC,OUT
    parser=argparse.ArgumentParser()
    parser.add_argument('--bundle',type=Path,default=BUNDLE)
    parser.add_argument('--static-path',type=Path,default=STATIC)
    parser.add_argument('--source-run',type=Path,default=HERE/'artifacts/source_gpu_r1')
    parser.add_argument('--run',default='reproduce_prefix_r1')
    args=parser.parse_args()
    BUNDLE,STATIC,OUT=args.bundle,args.static_path,HERE/'artifacts'/args.run
    if OUT.exists():raise SystemExit('Existing reproduction preserved')
    OUT.mkdir(parents=True)
    os.environ.update(CUDA_VISIBLE_DEVICES='0',FLYVIS_ROOT_DIR='/tmp/flyvis-circuit-selection-phase2-20261010',
        MPLCONFIGDIR=str(HERE/'runtime/matplotlib'),MPLBACKEND='Agg',NUMBA_CACHE_DIR=str(HERE/'runtime/numba'),
        CUBLAS_WORKSPACE_CONFIG=':4096:8',TIMEZONE='Asia/Shanghai',PYTHONDONTWRITEBYTECODE='1')
    sys.dont_write_bytecode=True
    import torch
    torch.set_num_threads(1);torch.set_num_interop_threads(1);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    sys.path.insert(0,str(HERE/'dependencies/a_snapshot'))
    from r_only import RStepService
    from gpu_adapter import GPUAdapter
    entries=manifest_verify(BUNDLE)
    u=HUpdater(STATIC)
    inputs=validate_parameters(u,BUNDLE/'expanded_parameters.npz')
    svc=RStepService(BUNDLE/'expanded_parameters.npz',BUNDLE/'identity_manifest.json',BUNDLE/'candidates/B_T5c/candidate_manifest.json',device='cuda')
    adapter=GPUAdapter(svc,inputs)
    a0=np.load(BUNDLE/'initial_state_full.npy',allow_pickle=False)
    stimulus=np.load(BUNDLE/'stimulus.npy',mmap_mode='r',allow_pickle=False)
    expected=np.load(args.source_run/'activities_full.npy',mmap_mode='r',allow_pickle=False)
    c=Coordinator(u,adapter,a0,str(uuid.uuid4()),'FRESH_PROCESS_REPRODUCTION','OFF_0_prefix')
    values=[]
    with native_full_forbidden() as audit:
        for k in range(32):
            x=np.zeros(45669,dtype=np.float32);x[inputs.reshape(-1)]=np.tile(stimulus[0,k,0],8)
            values.append(c.step(k,x))
    values=np.stack(values)
    assert np.array_equal(values,expected[0,:32]) and audit['forbidden_native_call_count']==0
    np.save(OUT/'activities_full.npy',values)
    record=dict(status='PASS_BITWISE_LIVE_PREFIX_REPRODUCTION',steps=32,all_nodes=45669,
        fresh_python_process=True,fresh_R_service=True,shared_initial_sha256=file_hash(BUNDLE/'initial_state_full.npy'),
        reproduction_array_digest=array_hash(values),original_prefix_array_digest=array_hash(np.array(expected[0,:32])),
        R_evaluations=adapter.calls,H_steps=u.step_count,production_guard=audit,
        command=[sys.executable,*sys.argv],circuit_sha256=u.circuit_digest,
        expanded_parameters_sha256=file_hash(BUNDLE/'expanded_parameters.npz'),stimulus_sha256=file_hash(BUNDLE/'stimulus.npy'),
        expected_run=str(args.source_run),expected_trajectory_sha256=file_hash(args.source_run/'activities_full.npy'),
        code_sha256={name:file_hash(HERE/name) for name in ['reproduce_live_prefix.py','h_step.py','coordinator.py','gpu_adapter.py']},
        input_bundle_unchanged=all(file_hash(BUNDLE/e['path'])==e['sha256'] for e in entries),
        limitation='Independent repetition covers OFF0 first32 steps; not a second complete four-condition acceptance run.')
    assert record['input_bundle_unchanged']
    (OUT/'result.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    (OUT/'trace.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in c.logs),encoding='utf-8')
    print(json.dumps(record),flush=True)

if __name__=='__main__':main()

"""Minimal actual consumer of stateless R-only API. Full comparison is optional debug."""
import argparse, json, os
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--device',choices=['cpu','cuda'],default='cpu')
p.add_argument('--candidate',default='B_T5c')
p.add_argument('--compare-full',action='store_true');p.add_argument('--bundle')
p.add_argument('--output',required=True)
args=p.parse_args()
BASE=Path(__file__).resolve().parent;bundle=BASE/'artifacts'/(args.bundle or ('reference_bundle_gpu_native_v1' if args.device=='cuda' else 'reference_bundle_v1'))
out=Path(args.output)
if out.exists():raise SystemExit('Existing consumer output preserved')
os.environ.update(CUDA_VISIBLE_DEVICES='0' if args.device=='cuda' else '-1',
 FLYVIS_ROOT_DIR='/opt/flyvis-phase2-data',MPLBACKEND='Agg',MPLCONFIGDIR='/opt/flyvis-phase2-data/matplotlib',
 NUMBA_CACHE_DIR='/opt/flyvis-phase2-data/numba',TIMEZONE='Asia/Shanghai',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import numpy as np,torch
torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
from r_only import RStepService,file_sha
identity=json.loads((bundle/'identity_manifest.json').read_text())
assert file_sha(bundle/'initial_state_full.npy')==identity['initial_state_sha256']
service=RStepService(bundle/'expanded_parameters.npz',bundle/'identity_manifest.json',
 bundle/'candidates'/args.candidate/'candidate_manifest.json',device=args.device)
# Load the identical complete a0 and the exact frozen first frame.
old_full=torch.from_numpy(np.load(bundle/'initial_state_full.npy')).to(service.device)
hex_frame=torch.from_numpy(np.load(bundle/'stimulus.npy')[0,0,0].copy()).to(service.device)
old_copy=old_full.clone()
candidate=service.step(old_full,hex_frame,step_id=0,run_id='consumer-example',condition_id='0')
assert torch.equal(old_full,old_copy)
info=dict(status='PASS_R_ONLY_CONSUMER_CALL',candidate_status=candidate.status,step_id=candidate.step_id,
 r_nodes=candidate.activity.numel(),global_ids=candidate.global_node_indices.numel(),h_nodes=len(service.h_indices),
 device=str(candidate.activity.device),dtype=str(candidate.activity.dtype),dt_s=service.dt,
 expanded_parameters_sha256=identity['expanded_parameters_sha256'],parameter_bundle=bundle.name,full_dependency_imported=False,checkpoint_sha256=candidate.checkpoint_sha256,
 candidate_manifest_sha256=candidate.candidate_sha256,state_advanced=False,
 next_action='B computes independent H from this same old_full, validates both results, and atomically merges into a new full state')
if args.compare_full:
 from full_oracle import FullNetworkOracle
 full=FullNetworkOracle(bundle/'identity_manifest.json',device=args.device)
 reference=full.step(old_full,hex_frame).index_select(0,candidate.global_node_indices)
 info.update(optional_debug_full_max_abs=float(torch.max(torch.abs(candidate.activity-reference))),
  optional_debug_full_allclose=bool(torch.allclose(candidate.activity,reference,atol=1e-5,rtol=1e-5)))
 assert info['optional_debug_full_allclose']
else:
 import sys
 assert 'flyvis' not in sys.modules and 'full_oracle' not in sys.modules
 info['full_and_flyvis_modules_absent']=True
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
print('CONSUMER_PASS',json.dumps(info),flush=True)

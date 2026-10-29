"""Preserve CPU bundle; create original native-GPU parameters sharing CPU a0."""
import json,shutil
from pathlib import Path
import numpy as np
from r_only import file_sha
BASE=Path(__file__).resolve().parent;CPU=BASE/'artifacts/reference_bundle_v1';GPU=BASE/'artifacts/init_gpu_r1';OUT=BASE/'artifacts/reference_bundle_gpu_native_v1'
if OUT.exists():raise SystemExit('Native GPU bundle exists; preserved')
shutil.copytree(CPU,OUT)
identity=json.loads((CPU/'identity_manifest.json').read_text());native=json.loads((GPU/'identity_manifest.json').read_text())
assert native['checkpoint_sha256']==identity['checkpoint_sha256'] and native['source_commit']==identity['source_commit']
assert native['nodes_full_sha256']==identity['nodes_full_sha256']
with np.load(CPU/'expanded_parameters.npz') as ca,np.load(GPU/'expanded_parameters.npz') as ga:
 for name in ca.files:
  if name not in ['syn_count','effective_weight']:assert np.array_equal(ca[name],ga[name])
identity.update(expanded_parameters_sha256=native['expanded_parameters_sha256'],expanded_parameter_digests=native['expanded_parameter_digests'],
 parameter_expansion_device='cuda',parameter_expansion_torch=native['torch'],parameter_profile='OFFICIAL_NATIVE_GPU_EXPANDED',
 parameter_profile_note='Official lognormal raw syn_count.exp() differs across CPU/CUDA float32 kernels. H and R must load this same profile.',
 official_native_gpu_adaptation_state_sha256=native['initial_state_sha256'],canonical_initial_state_device='cpu',
 initial_state_sha256=file_sha(CPU/'initial_state_full.npy'))
def dump(f,v):Path(f).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
shutil.copy2(GPU/'expanded_parameters.npz',OUT/'expanded_parameters.npz');dump(OUT/'identity_manifest.json',identity)
for path in (OUT/'candidates').glob('*/candidate_manifest.json'):
 m=json.loads(path.read_text());m.update(expanded_parameters_sha256=identity['expanded_parameters_sha256'],
 parameter_profile='OFFICIAL_NATIVE_GPU_EXPANDED',parameter_expansion_device='cuda',source_B_node_edge_order_verified=True,source_B_numeric_parameters_are_not_used=True)
 dump(path,m)
accept=json.loads((CPU/'bundle_acceptance.json').read_text())
accept.update(status='PASS_NATIVE_GPU_EXPANDED_PARAMETERS_COMMON_CPU_A0',parameter_profile='OFFICIAL_NATIVE_GPU_EXPANDED',
 common_initial_and_stimulus_bytes_exact=True,CPU_bundle_unchanged=True,native_initial_state_not_used_for_shared_comparison=True)
dump(OUT/'bundle_acceptance.json',accept)
dump(OUT/'artifact_manifest.json',dict(files=[dict(path=str(f.relative_to(OUT)),bytes=f.stat().st_size,sha256=file_sha(f))
 for f in sorted(OUT.rglob('*')) if f.is_file() and f.name!='artifact_manifest.json']))
print('GPU_NATIVE_BUNDLE_READY',identity['expanded_parameters_sha256'])

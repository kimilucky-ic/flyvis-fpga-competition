"""Final owned-stage seal; omit runtime caches, preserve accepted runs."""
from common import *

source=HERE/'artifacts/python_source_raw_800_r2'
result=load(source/'result.json');ack=load(HERE/'A_B_STRICT_IDENTITY_CONFIRMATION.json')
checks={}
for name,digest in result['run_identity']['code_sha256'].items():checks['production:'+name]=file_hash(HERE/name)==digest
for name,digest in ack['A_existing_callables_exact'].items():
    checks['A_current:'+name]=file_hash(HERE.parents[1].parent/'fly/gpu_phase2'/name)==digest
checks['A_backend_unchanged']=file_hash(host_path(ack['A_backend_path']))==ack['A_backend_sha256']
checks['phase2_original_manifest_unchanged']=file_hash(HERE.parent/'phase2_20261010/artifact_manifest.json')=='3f0dc9c8a2158f9430fba9f7eb4d747efecf89575e734c10f43d7deac0104279'
for folder in [BUNDLE,source,HERE/'c_reference',HERE/'gui_bundle',HERE/'artifacts/audit_800_r1',HERE/'artifacts/consumer_audit_r2',HERE/'artifacts/fpga_unavailable_r1']:
    manifest_verify(folder);checks['manifest:'+folder.relative_to(HERE).as_posix()]=True
# Legacy accepted probe harness emits a list manifest; verify its actual files.
probe=HERE/'artifacts/live_feedback_r1'
for entry in load(probe/'artifact_manifest.json'):
    assert file_hash(probe/entry['path'])==entry['sha256'] and (probe/entry['path']).stat().st_size==entry['bytes']
checks['manifest:live_feedback_r1']=True
assert all(checks.values())
dump(HERE/'FINAL_VERIFICATION.json',dict(status='PASS_FINAL_IDENTITY_AND_ACCEPTED_ARTIFACT_SEAL',checks=checks,
    stage='Gate S1 SOFTWARE ONLY',C_manifest_sha256=file_hash(HERE/'c_reference/artifact_manifest.json'),
    GUI_manifest_sha256=file_hash(HERE/'gui_bundle/artifact_manifest.json'),RTL_execution=False,board_access=False))
files=[]
for path in sorted(HERE.rglob('*')):
    rel=path.relative_to(HERE)
    if not path.is_file() or path==HERE/'artifact_manifest.json' or '__pycache__' in rel.parts or rel.parts[0]=='runtime' or path.suffix=='.pyc':continue
    files.append(dict(path=rel.as_posix(),bytes=path.stat().st_size,sha256=file_hash(path)))
dump(HERE/'artifact_manifest.json',dict(scope='B phase3 deliverable and evidence; runtime/__pycache__ excluded',files=files))
manifest_verify(HERE)
print('FINAL_SEAL_PASS',len(files),sum(item['bytes'] for item in files),file_hash(HERE/'artifact_manifest.json'))

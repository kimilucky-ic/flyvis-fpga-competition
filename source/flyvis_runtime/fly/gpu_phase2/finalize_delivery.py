"""Final delivery integrity and owned-lane paths; no simulation."""
import hashlib,json,re
from pathlib import Path
from r_only import file_sha
BASE=Path(__file__).resolve().parent
H=json.loads((BASE/'handoff.json').read_text())
assert H['status']=='PASS_A_FULL_A0_AND_REAL_R_ONLY_CPU_GPU'
for key in ['canonical_initial_state','consumer_example','api_documentation','report']:
 assert (BASE/H[key]).is_file(),key
for key in ['R_api','full_debug_oracle']:
 assert (BASE/H[key].split(':')[0]).is_file()
for profile in H['parameter_profiles'].values():
 bundle=BASE/profile['bundle']
 identity=json.loads((bundle/'identity_manifest.json').read_text())
 assert file_sha(bundle/'expanded_parameters.npz')==profile['parameter_sha256']==identity['expanded_parameters_sha256']
 assert file_sha(bundle/'candidates/B_T5c/candidate_manifest.json')==profile['candidate_sha256']
 for name in H['bundle_files'].values():assert (bundle/name).is_file(),name
 manifest=json.loads((bundle/'artifact_manifest.json').read_text())
 for v in manifest['files']:assert file_sha(bundle/v['path'])==v['sha256']
for path in H['accepted_runs'].values():
 assert (BASE/path).is_file()
for key,path in H['timeseries'].items():
 if isinstance(path,str):assert (BASE/path).is_file(),key
for path in [BASE/'PHASE2_REPORT.md',BASE.parent/'.agents/skills/flyvis-r-only-reference/SKILL.md',
 BASE.parent/'docs/workstreams/flyvis-visual-workline.md']:
 for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
  if target.startswith(('https:','http:')):continue
  assert (path.parent/target).exists(),(str(path),target)
# Correct the retained diagnosis link; no numerical record changed.
path=BASE/'artifacts/r_only_cpu_r1/failure.json'
failure=json.loads(path.read_text());failure['verified_diagnosis_path']='../trace_instrumentation_diagnosis.json'
path.write_text(json.dumps(failure,indent=2),encoding='utf-8')
files=[]
for path in sorted(BASE.rglob('*')):
 if not path.is_file() or '__pycache__' in path.parts or path.name=='delivery_manifest.json':continue
 files.append(dict(path=str(path.relative_to(BASE)),bytes=path.stat().st_size,sha256=file_sha(path)))
external=[BASE.parent/'.agents/skills/flyvis-r-only-reference/SKILL.md',BASE.parent/'docs/workstreams/flyvis-visual-workline.md']
for path in external:files.append(dict(path=str(path),bytes=path.stat().st_size,sha256=file_sha(path),scope='same FlyVis lane'))
manifest=dict(status='PASS_FINAL_DELIVERY_FILES_HASHED',root=str(BASE),files=files,
 total_bytes=sum(x['bytes'] for x in files),excludes='generated __pycache__ only',personal_memory_modified=False,
 other_workline_files_modified_by_this_task=False)
target=BASE/'delivery_manifest.json'
if target.exists():raise SystemExit('Existing final inventory preserved')
target.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(status=manifest['status'],files=len(files),total_bytes=manifest['total_bytes']),indent=2))

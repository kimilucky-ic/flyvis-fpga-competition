"""Static protection/snapshot only, no device or subprocess calls."""
import ast,difflib,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;G=P.parents[1]
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def save(n,v):(P/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
b=load(P/'BEFORE.json');prior=G/'evidence/joint_step_latency_20261017/DELIVERY_MANIFEST.json'
assert sha(prior)==b['prior_delivery_sha256']
for n,v in b['source_sha256'].items():assert sha(P/'before_sources'/n)==v,n
old=G/'evidence/camera_joint32_20261016';manifest=load(old/'DELIVERY_MANIFEST.json')
for n,v in manifest['files'].items():assert sha(old/n)==v,n
registry=load(G/'live_registry.json');models={}
for n in ('full','r_only','decoder','parameters','initial','identity','nodes'):
    pin=registry['pins'][n];assert sha(pin['path'])==pin['sha256'];models[n]=pin['sha256']
h=load(G/'runtime/joint/7f111da4437843539eeffef2c6c2546e/hardware_handoff.json')
for n,v in h['software_sha256'].items():assert sha(Path(h['software_package'])/n)==v,n
for n in ('joint_camera_engine.py','joint_camera_io.py'):
    assert sha(G/n)==load(prior)['source_sha256'][n],n
scope=load(G/'runtime/joint/34e96b4d227f488bb3214190089569d1/scope.json')
for n in ('hybrid_gpu.py','hybrid_a3.py','hybrid_v2.py','hybrid_full485.py'):
    assert sha(G/n)==scope['source_sha256'][n],n
active=load(G/'runtime/joint_active.json');assert active['state']=='STOPPED' and active['run_id']=='815a7069e02e42fb8dc0cf9477e97926'
result=load(P/'CPU_RESULT.json');compare=load(P/'CPU_COMPARISON.json')
assert result['tests']==23 and result['failures']==result['errors']==0
assert compare['all_original_validation_results_and_saved_file_bytes_equal']
for row in compare['log_admission_rows']:assert sha(P/row['captured_file'])==row['capture_sha256']
names=('ps_commit_evidence.py','test_ps_hotpath.py');out=P/'delivered_sources';out.mkdir(exist_ok=True);pins={};diff=[]
for n in names:
    raw=(G/n).read_bytes();ast.parse(raw,filename=n)
    if n=='ps_commit_evidence.py':ast.parse(raw,filename=n,feature_version=(3,8))
    (out/n).write_bytes(raw);pins[n]=sha(G/n)
    if n in b['source_sha256']:
        diff.extend(difflib.unified_diff((P/'before_sources'/n).read_text(encoding='utf8').splitlines(True),raw.decode('utf8').splitlines(True),fromfile='before/'+n,tofile='after/'+n))
(P/'SOURCE_DIFF.patch').write_text(''.join(diff),encoding='utf8')
save('VERIFICATION.json',dict(status='PASS_CPU_ORIGINAL_RUN_HELPERS_ONLY',historical_files_verified=len(manifest['files']),
    original_model_pins=models,frozen_hardware_source_files_verified=len(h['software_sha256']),
    original_PC_engine_IO_GPU_Coordinator_unchanged=True,board_Python38_AST=True,source_sha256=pins,CPU_tests=23,
    CPU_native_closed_comparison_sha256={r['captured_file']:r['capture_sha256'] for r in compare['log_admission_rows']},
    CPU_saved_protocol_closed_sha256={f.relative_to(P).as_posix():sha(f) for f in sorted((P/'cpu_cases').glob('*/ps/evidence.fvej'))},
    active_state=active['state'],active_run=active['run_id'],board_connections=0,real_MMIO=0,GPU_runs=0,
    camera_starts=0,GUI_starts=0,new_scopes=0,actual_PS_ms='NOT_MEASURED'))
files={}
for f in sorted(P.iterdir()):
    if f.is_file() and f.name!='DELIVERY_MANIFEST.json' and f.suffix in ('.py','.json','.log','.md','.patch'):files[f.name]=sha(f)
for folder in ('before_sources','delivered_sources'):
    for f in sorted((P/folder).glob('*.py')):files[f.relative_to(P).as_posix()]=sha(f)
save('DELIVERY_MANIFEST.json',dict(schema='flyvis-line2-software-delivery/v1',evidence_level='CPU_SOFTWARE_ONLY',files=files,
    source_sha256=pins,gui_documents={n:sha(G/n) for n in ('API_CONTRACT.md','JOINT_STREAM_RUNTIME_CONTRACT.md')},
    actual_PS_ms='NOT_MEASURED',excluded=['cpu_cases and native_closed_comparison bulk fixtures: SHA in VERIFICATION.json']))
print(json.dumps(dict(status='SEALED_CPU_SOFTWARE_ONLY',files=len(files),source_files=len(names),
    historical_files=len(manifest['files']),model_pins=len(models),frozen_PS_sources=len(h['software_sha256']),CPU_tests=23,
    manifest_sha256=sha(P/'DELIVERY_MANIFEST.json')),indent=2))

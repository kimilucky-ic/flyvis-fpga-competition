"""Read-only protection checks, then seal this local CPU-only delivery."""
import ast,difflib,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;G=P.parents[1]
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(n,v):(P/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
b=load(P/'BEFORE.json')
for n,v in b['source_sha256'].items():assert sha(P/'before_sources'/n)==v,n
prior=G/'evidence/joint_streamline_20261017/DELIVERY_MANIFEST.json'
assert sha(prior)==b['previous_delivery_sha256']
old=G/'evidence/camera_joint32_20261016';m=load(old/'DELIVERY_MANIFEST.json')
for n,v in m['files'].items():assert sha(old/n)==v,n
r=load(G/'live_registry.json');models={}
for n in ('full','r_only','decoder','parameters','initial','identity','nodes'):
    pin=r['pins'][n];assert sha(pin['path'])==pin['sha256'];models[n]=pin['sha256']
h=load(G/'runtime/joint/7f111da4437843539eeffef2c6c2546e/hardware_handoff.json')
for n,v in h['software_sha256'].items():assert sha(Path(h['software_package'])/n)==v,n
a=load(G/'runtime/joint_active.json');assert a['state']=='STOPPED' and a['run_id']=='815a7069e02e42fb8dc0cf9477e97926'
windows=load(P/'WINDOWS_OFFLINE_CATALOG.json');assert windows['condition_count']==55 and not windows['errors']
cpu=load(P/'CPU_FINAL_V2_TESTS.json');assert cpu['status']=='PASS_CPU_PROTOCOL_ONLY' and cpu['tests']==49
assert 'Ran 2 tests' in (P/'CPU_IDENTITY_FIX_CHECKS.log').read_text() and (P/'CPU_IDENTITY_FIX_CHECKS.log').read_text().rstrip().endswith('OK')
src=tuple(b['source_sha256'])+('joint_camera_io.py','test_joint_io.py')
d=P/'delivered_sources';d.mkdir(exist_ok=True);pins={};patch=[]
for n in src:
    raw=(G/n).read_bytes();ast.parse(raw,filename=n);(d/n).write_bytes(raw);pins[n]=sha(G/n)
    if n in b['source_sha256']:
        patch.extend(difflib.unified_diff((P/'before_sources'/n).read_text(encoding='utf8').splitlines(True),raw.decode('utf8').splitlines(True),fromfile='before/'+n,tofile='after/'+n))
(P/'SOURCE_DIFF.patch').write_text(''.join(patch),encoding='utf8')
save('CATALOG_PLATFORM_DIAGNOSIS.json',dict(WSL_initial_count=54,
    cause='Windows absolute recording_directory in pinned historical handoff was interpreted as a Linux relative path',
    actual_rejected_path='/mnt/c/Users/hzy72/Documents/ChatGPT/fly/camera_pipeline/C:/Users/hzy72/Documents/ChatGPT/fly/camera_pipeline/recordings/real_camera_20261010_r1/recording.json',
    Windows_native_count=55,Windows_errors=[],original_data_or_pins_modified=False,
    supersedes='Early CPU_FINAL_TESTS.json excluded field was a provisional, incorrect contract-mismatch guess'))
save('VERIFICATION.json',dict(status='PASS_CPU_SOFTWARE_DELIVERY_NOT_PHYSICAL_SPEEDUP',
    historical_files_verified=len(m['files']),historical_manifest_sha256=sha(old/'DELIVERY_MANIFEST.json'),
    original_model_pins=models,frozen_hardware_sources_verified=len(h['software_sha256']),
    production_and_test_sha256=pins,syntax_checked=len(src),CPU_tests=49,identity_followup_tests=2,
    original_Windows_conditions=55,active_state=a['state'],active_run=a['run_id'],
    new_GPU_runs=0,new_camera_captures=0,new_GUI_launches=0,board_connections=0,new_neural_steps=0,
    PC_normal_sync_checkpoints=dict(old=5,new=4),PS_checkpoints_unchanged=4,
    storage_default='DIRECT_SESSION/v1',native_storage_speedup='NOT_PROVEN_DEFAULT_DISABLED',
    actual_joint_performance='NOT_MEASURED'))
files={}
for p in sorted(P.iterdir()):
    if p.is_file() and p.name!='DELIVERY_MANIFEST.json' and p.suffix in ('.py','.json','.log','.md','.patch'):
        files[p.name]=sha(p)
for folder in ('before_sources','delivered_sources'):
    for p in sorted((P/folder).glob('*.py')):files[p.relative_to(P).as_posix()]=sha(p)
save('DELIVERY_MANIFEST.json',dict(schema='flyvis-line2-software-delivery/v1',evidence_level='CPU_SOFTWARE_ONLY',
    files=files,gui_documents={n:sha(G/n) for n in ('API_CONTRACT.md','JOINT_STREAM_RUNTIME_CONTRACT.md')},
    source_sha256=pins,excluded=['large replay byte copies and temporary native-disk candidate source; SHA identity recorded in CPU_STORAGE_COMPARE.json'],
    actual_joint_performance='NOT_MEASURED_NO_REALTIME_OR_BOARD_PASS'))
print(json.dumps(dict(status='SEALED_CPU_SOFTWARE_ONLY',files=len(files),sources=len(src),
    baseline_files=len(m['files']),protected_models=len(models),hardware_sources=len(h['software_sha256']),
    Windows_conditions=55,new_device_runs=0),indent=2))

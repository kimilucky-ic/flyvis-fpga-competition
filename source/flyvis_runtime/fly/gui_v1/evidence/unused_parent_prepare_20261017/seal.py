"""Read-only source protection plus local software-delivery snapshots."""
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
b=load(P/'BEFORE.json');prior=G/'evidence/ps_hotpath_20261017/DELIVERY_MANIFEST.json'
assert sha(prior)==b['prior_delivery_sha256']
for n,v in b['source_sha256'].items():assert sha(P/'before_sources'/n)==v,n
old=G/'evidence/camera_joint32_20261016';historical=load(old/'DELIVERY_MANIFEST.json')
for n,v in historical['files'].items():assert sha(old/n)==v,n
registry=load(G/'live_registry.json');models={}
for n in ('full','r_only','decoder','parameters','initial','identity','nodes'):
    pin=registry['pins'][n];assert sha(pin['path'])==pin['sha256'];models[n]=pin['sha256']
h=load(G/'runtime/joint/7f111da4437843539eeffef2c6c2546e/hardware_handoff.json')
for n,v in h['software_sha256'].items():assert sha(Path(h['software_package'])/n)==v,n
assert sha(G/'ps_commit_evidence.py')==load(prior)['source_sha256']['ps_commit_evidence.py']
engine_prior=load(G/'evidence/joint_step_latency_20261017/DELIVERY_MANIFEST.json')
for n in ('joint_camera_engine.py','joint_camera_io.py'):assert sha(G/n)==engine_prior['source_sha256'][n],n
scope=load(G/'runtime/joint/34e96b4d227f488bb3214190089569d1/scope.json')
for n in ('hybrid_gpu.py','hybrid_a3.py','hybrid_v2.py','hybrid_full485.py'):
    assert sha(G/n)==scope['source_sha256'][n],n
launch_prior=load(G/'evidence/ps_commit_journal_20261017/DELIVERY_MANIFEST.json')
for n in ('joint_camera_worker.py','joint_camera_controller.py'):assert sha(G/n)==launch_prior['source_sha256'][n],n
import sys
sys.path.insert(0,str(G))
from joint_camera_bundle import unused_parent,UNUSED_RUNTIME_PINS,UNUSED_BUNDLE_PINS
selected=unused_parent()
active=load(G/'runtime/joint_active.json');assert active['state']=='STOPPED' and active['run_id']==selected['run_id']
result=load(P/'CPU_RESULT.json');assert result['tests']==42 and result['failures']==result['errors']==0
names=tuple(b['source_sha256'])+('test_joint_camera_unused.py',);out=P/'delivered_sources';out.mkdir(exist_ok=True);pins={};diff=[]
for n in names:
    raw=(G/n).read_bytes();ast.parse(raw,filename=n)
    if n in ('joint_camera_retained.py','joint_camera_board_entry.py'):ast.parse(raw,filename=n,feature_version=(3,8))
    (out/n).write_bytes(raw);pins[n]=sha(G/n)
    if n in b['source_sha256']:
        diff.extend(difflib.unified_diff((P/'before_sources'/n).read_text(encoding='utf8').splitlines(True),raw.decode('utf8').splitlines(True),fromfile='before/'+n,tofile='after/'+n))
from joint_camera_manual import board_cell
ast.parse(board_cell('42'*32,unused=selected),feature_version=(3,8))
(P/'SOURCE_DIFF.patch').write_text(''.join(diff),encoding='utf8')
cpu_files={}
for folder in ('cpu_cases','cpu_archives','legacy_checks','fixture'):
    for f in sorted((P/folder).rglob('*')):
        if f.is_file():cpu_files[f.relative_to(P).as_posix()]=sha(f)
save('VERIFICATION.json',dict(status='PASS_CPU_SOFTWARE_ONLY_NOT_BOARD_PREPARED',CPU_tests=result['tests'],
    historical_files_verified=len(historical['files']),pinned_PC_failed_files_verified=len(UNUSED_RUNTIME_PINS)+len(UNUSED_BUNDLE_PINS),
    original_model_pins=models,frozen_hardware_source_files_verified=len(h['software_sha256']),
    PC_engine_IO_GPU_Coordinator_worker_controller_and_PS_adapter_unchanged=True,
    board_Python38_AST=True,source_sha256=pins,CPU_fixture_files_sha256=cpu_files,
    active_state=active['state'],active_run=active['run_id'],board_connections=0,real_MMIO=0,GPU_runs=0,
    camera_starts=0,GUI_starts=0,new_executable_scopes=0,CPU_ONLY_archives=1,
    actual_board_preparation='NOT_PERFORMED',actual_joint_speed='NOT_MEASURED',
    GUI_interpretation_files='USER_ASSIGNED_OTHER_WORKSTREAM_NOT_EDITED_HERE'))
files={}
for f in sorted(P.iterdir()):
    if f.is_file() and f.name!='DELIVERY_MANIFEST.json' and f.suffix in ('.py','.json','.log','.md','.patch'):files[f.name]=sha(f)
for folder in ('before_sources','delivered_sources'):
    for f in sorted((P/folder).glob('*.py')):files[f.relative_to(P).as_posix()]=sha(f)
save('DELIVERY_MANIFEST.json',dict(schema='flyvis-line2-software-delivery/v1',evidence_level='CPU_SOFTWARE_ONLY',
    files=files,source_sha256=pins,prior_delivery_sha256=b['prior_delivery_sha256'],
    actual_board_preparation='NOT_PERFORMED',excluded=['CPU bulk cases and private CPU archives: per-file SHA in VERIFICATION.json']))
print(json.dumps(dict(status='SEALED_CPU_SOFTWARE_ONLY',files=len(files),source_files=len(names),CPU_tests=result['tests'],
    historical_files=len(historical['files']),pinned_failed_files=9,model_pins=len(models),frozen_PS_sources=len(h['software_sha256']),
    manifest_sha256=sha(P/'DELIVERY_MANIFEST.json')),indent=2))

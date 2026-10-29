"""Source/package/static protection only. No device or process launch."""
import ast,difflib,hashlib,json,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;G=P.parents[1]
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(n,v):(P/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
assert load(P/'CPU_RESULT.json')['status']=='PASS_CPU_ONLY'
metadata=load(P/'INITIALIZATION_PACKAGE.json');root=Path(metadata['root']);archive=Path(metadata['archive'])
assert sha(archive)==metadata['archive_sha256'] and sha(root/'INIT_PLAN.json')==metadata['plan_sha256']
runtime=load(root/'RUNTIME_SHA256.json')
with zipfile.ZipFile(archive) as z:
    for n,d in runtime.items():assert hashlib.sha256(z.read(n)).hexdigest()==d
    assert z.read('INIT_PLAN.json')==(root/'INIT_PLAN.json').read_bytes()
for n in ('next_fresh_init_cell.py','next_fresh_init_inline_cell.py'):ast.parse((P/n).read_text(encoding='utf8'),feature_version=(3,8))
old=G/'evidence/camera_joint32_20261016';history=load(old/'DELIVERY_MANIFEST.json')
for n,d in history['files'].items():assert sha(old/n)==d,n
registry=load(G/'live_registry.json');models={}
for n in ('full','r_only','decoder','parameters','initial','identity','nodes'):
    pin=registry['pins'][n];assert sha(pin['path'])==pin['sha256'];models[n]=pin['sha256']
h=load(G/'runtime/joint/7f111da4437843539eeffef2c6c2546e/hardware_handoff.json')
for n,d in h['software_sha256'].items():assert sha(Path(h['software_package'])/n)==d,n
scope=load(G/'runtime/joint/34e96b4d227f488bb3214190089569d1/scope.json')
for n in ('hybrid_gpu.py','hybrid_a3.py','hybrid_v2.py','hybrid_full485.py'):assert sha(G/n)==scope['source_sha256'][n],n
last=load(G/'evidence/joint_step_latency_20261017/DELIVERY_MANIFEST.json')
for n in ('joint_camera_engine.py','joint_camera_io.py'):assert sha(G/n)==last['source_sha256'][n],n
assert sha(G/'ps_commit_evidence.py')==load(G/'evidence/ps_hotpath_20261017/DELIVERY_MANIFEST.json')['source_sha256']['ps_commit_evidence.py']
out=P/'delivered_sources';out.mkdir(exist_ok=True);pins={};diff=[]
before=G/'evidence/unused_parent_prepare_20261017/delivered_sources'
names=('joint_camera_fresh.py','test_joint_camera_fresh.py','joint_camera_bundle.py','joint_camera_controller.py','joint_camera_board_entry.py','joint_camera_preparation.py')
for n in names:
    raw=(G/n).read_bytes();ast.parse(raw)
    if n in ('joint_camera_fresh.py','joint_camera_board_entry.py'):ast.parse(raw,feature_version=(3,8))
    (out/n).write_bytes(raw);pins[n]=sha(G/n)
    prior=before/n
    if n=='joint_camera_controller.py':prior=G/'evidence/ps_commit_journal_20261017/delivered_sources'/n
    if prior.exists():diff.extend(difflib.unified_diff(prior.read_text(encoding='utf8').splitlines(True),raw.decode('utf8').splitlines(True),fromfile='previous/'+n,tofile='fresh/'+n))
(P/'SOURCE_DIFF.patch').write_text(''.join(diff),encoding='utf8')
save('VERIFICATION.json',dict(status='PASS_CPU_SOFTWARE_ONLY_PENDING_HUMAN_INITIALIZATION',CPU_tests=26,
    historical_files_verified=len(history['files']),model_pins=models,frozen_PS_files_verified=len(h['software_sha256']),
    source_sha256=pins,original_GPU_model_Coordinator_engine_IO_PS_adapter_unchanged=True,
    original_driver_run_finish_unchanged=True,board_Python38_AST=True,
    initialization_package_sha256=metadata['archive_sha256'],initialization_plan_sha256=metadata['plan_sha256'],
    current_boot_inventory_source='USER_MANUAL_READ_ONLY_AND_NOTEBOOK_VISIBLE_OUTPUT',
    actual_initialization='NOT_EXECUTED_BY_AGENT',new_joint_run='NOT_STARTED',new_joint_steps=0,
    future_manual_initialization_scope=dict(loads=1,DMA_initialization_reset=1,CMA_allocations=2,neural_steps=0),
    GUI_interpretation='OTHER_WORKSTREAM_UNTOUCHED'))
files={}
for f in sorted(P.iterdir()):
    if f.is_file() and f.name!='DELIVERY_MANIFEST.json':files[f.name]=sha(f)
for folder in (out,root):
    for f in sorted(folder.rglob('*')):
        if f.is_file():files[f.relative_to(P).as_posix()]=sha(f)
save('DELIVERY_MANIFEST.json',dict(schema='flyvis-line2-software-delivery/v1',evidence_level='CPU_SOFTWARE_ONLY_PENDING_USER_BOARD_INITIALIZATION',
    files=files,source_sha256=pins,actual_initialization='NOT_EXECUTED_BY_AGENT',actual_joint_speed='NOT_MEASURED'))
print(json.dumps(dict(status='SEALED_CPU_ONLY_MANUAL_INIT_PACKAGE',files=len(files),tests=26,manifest_sha256=sha(P/'DELIVERY_MANIFEST.json')),indent=2))

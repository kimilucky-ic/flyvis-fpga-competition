"""Static protection and identity sealing, no subprocess/socket/device calls."""
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
b=load(P/'BEFORE.json');prior=G/'evidence/joint_io_20261017/DELIVERY_MANIFEST.json'
assert sha(prior)==b['prior_delivery_sha256']
for n,v in b['source_sha256'].items():assert sha(P/'before_sources'/n)==v,n
baseline=G/'evidence/camera_joint32_20261016';manifest=load(baseline/'DELIVERY_MANIFEST.json')
for n,v in manifest['files'].items():assert sha(baseline/n)==v,n
reg=load(G/'live_registry.json');models={}
for n in ('full','r_only','decoder','parameters','initial','identity','nodes'):
    pin=reg['pins'][n];assert sha(pin['path'])==pin['sha256'];models[n]=pin['sha256']
handoff=load(G/'runtime/joint/7f111da4437843539eeffef2c6c2546e/hardware_handoff.json')
for n,v in handoff['software_sha256'].items():assert sha(Path(handoff['software_package'])/n)==v,n
assert sha(G/'joint_camera_engine.py')==load(prior)['source_sha256']['joint_camera_engine.py']
oldscope=load(G/'runtime/joint/34e96b4d227f488bb3214190089569d1/scope.json')
for n in ('hybrid_gpu.py','hybrid_a3.py','hybrid_v2.py','hybrid_full485.py'):
    assert sha(G/n)==oldscope['source_sha256'][n],n
active=load(G/'runtime/joint_active.json');assert active['state']=='STOPPED' and active['run_id']=='815a7069e02e42fb8dc0cf9477e97926'
result=load(P/'CPU_RESULT_FINAL2.json');admission=load(P/'CPU_ADMISSION.json')
assert result['tests']==32 and result['failures']==result['errors']==0
assert admission['tests']==1 and admission['failures']==admission['errors']==0
names=tuple(b['source_sha256'])+('ps_commit_evidence.py','test_ps_commit_evidence.py')
out=P/'delivered_sources';out.mkdir(exist_ok=True);pins={};diff=[]
for n in names:
    raw=(G/n).read_bytes();ast.parse(raw,filename=n)
    if n in ('ps_commit_evidence.py','joint_camera_board_entry.py'):ast.parse(raw,filename=n,feature_version=(3,8))
    (out/n).write_bytes(raw);pins[n]=sha(G/n)
    if n in b['source_sha256']:
        diff.extend(difflib.unified_diff((P/'before_sources'/n).read_text(encoding='utf8').splitlines(True),raw.decode('utf8').splitlines(True),fromfile='before/'+n,tofile='after/'+n))
(P/'SOURCE_DIFF.patch').write_text(''.join(diff),encoding='utf8')
captures={}
for row in load(P/'CPU_COMPARISON.json')['rows']:
    f=Path(row['capture_path'].replace('/mnt/c/','C:/'));captures[str(f)]=sha(f)
save('VERIFICATION.json',dict(status='PASS_CPU_PS_POLICY_SOFTWARE_ONLY',historical_files_verified=len(manifest['files']),
    original_model_pins=models,frozen_hardware_source_files_verified=len(handoff['software_sha256']),
    original_Coordinator_GPU_and_PC_engine_unchanged=True,syntax_checked=len(names),board_Python38_AST_checked=True,
    source_sha256=pins,CPU_tests=33,CPU_comparison_captures=captures,
    normal32_fsync_count=dict(old=128,new=64),active_state=active['state'],active_run=active['run_id'],
    real_MMIO=0,board_connections=0,new_GPU_runs=0,new_camera_captures=0,new_GUI_launches=0,new_neural_computations=0,
    live_authorization_scopes_generated=0,physical_power_loss_tests=0,actual_joint_speed='NOT_MEASURED'))
files={}
for f in sorted(P.iterdir()):
    if f.is_file() and f.name!='DELIVERY_MANIFEST.json' and f.suffix in ('.py','.json','.log','.md','.patch'):files[f.name]=sha(f)
for folder in ('before_sources','delivered_sources'):
    for f in sorted((P/folder).glob('*.py')):files[f.relative_to(P).as_posix()]=sha(f)
save('DELIVERY_MANIFEST.json',dict(schema='flyvis-line2-software-delivery/v1',evidence_level='CPU_SOFTWARE_ONLY',files=files,
    source_sha256=pins,gui_documents={n:sha(G/n) for n in ('API_CONTRACT.md','JOINT_STREAM_RUNTIME_CONTRACT.md')},
    scope='PS_TWO_DURABLE_COMMIT_ACK_BARRIERS_UNCOMMITTED_DIAGNOSTICS_VOLATILE',
    actual_joint_speed='NOT_MEASURED',excluded=['cpu_cases: hashes of closed comparison captures are in VERIFICATION.json']))
print(json.dumps(dict(status='SEALED_CPU_SOFTWARE_ONLY',files=len(files),source_files=len(names),
    protected_historical_files=len(manifest['files']),protected_model_pins=len(models),frozen_hardware_sources=len(handoff['software_sha256']),
    CPU_tests=33,devices_started=0),indent=2))

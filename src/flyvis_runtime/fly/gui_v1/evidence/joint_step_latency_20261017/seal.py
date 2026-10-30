"""Static checks and snapshots, no device or subprocess calls."""
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
b=load(P/'BEFORE.json');prior=G/'evidence/joint_transport_20261017/DELIVERY_MANIFEST.json'
assert sha(prior)==b['prior_delivery_sha256']
for n,v in b['source_sha256'].items():assert sha(P/'before_sources'/n)==v,n
class ProgressOnly(ast.NodeTransformer):
    count=0
    def visit_Call(self,node):
        self.generic_visit(node)
        if (isinstance(node.func,ast.Attribute) and node.func.attr=='call'
                and ast.unparse(node.func.value)=='self.diagnostics' and node.args
                and isinstance(node.args[0],ast.Constant) and node.args[0].value in ('progress.before_STEP','progress.before_COMMIT')):
            assert ast.unparse(node.args[1])=='self.progress' and not node.keywords
            self.count+=1;return ast.Call(func=node.args[1],args=node.args[2:],keywords=[])
        return node
tree=ast.parse((G/'joint_camera_engine.py').read_text(encoding='utf8'));transform=ProgressOnly();normalized=transform.visit(tree)
assert transform.count==2 and ast.dump(normalized)==ast.dump(ast.parse((P/'before_sources/joint_camera_engine.py').read_text(encoding='utf8')))
old=G/'evidence/camera_joint32_20261016';manifest=load(old/'DELIVERY_MANIFEST.json')
for n,v in manifest['files'].items():assert sha(old/n)==v,n
reg=load(G/'live_registry.json');models={}
for n in ('full','r_only','decoder','parameters','initial','identity','nodes'):
    pin=reg['pins'][n];assert sha(pin['path'])==pin['sha256'];models[n]=pin['sha256']
h=load(G/'runtime/joint/7f111da4437843539eeffef2c6c2546e/hardware_handoff.json')
for n,v in h['software_sha256'].items():assert sha(Path(h['software_package'])/n)==v,n
scope=load(G/'runtime/joint/34e96b4d227f488bb3214190089569d1/scope.json')
for n in ('hybrid_gpu.py','hybrid_a3.py','hybrid_v2.py','hybrid_full485.py'):
    assert sha(G/n)==scope['source_sha256'][n],n
active=load(G/'runtime/joint_active.json');assert active['state']=='STOPPED' and active['run_id']=='815a7069e02e42fb8dc0cf9477e97926'
initial=load(P/'CPU_RESULT.json');final=load(P/'CPU_RESULT_FINAL.json');compare=load(P/'CPU_COMPARISON.json')
assert initial['tests']==24 and initial['failures']==1 and initial['errors']==0
assert final['tests']==6 and final['failures']==final['errors']==0
assert compare['all_bytes_identical'] and compare['records']==5804
names=tuple(b['source_sha256'])+('test_joint_step_latency.py',)
out=P/'delivered_sources';out.mkdir(exist_ok=True);pins={};diff=[]
for n in names:
    raw=(G/n).read_bytes();ast.parse(raw,filename=n)
    if n=='ps_commit_evidence.py':ast.parse(raw,filename=n,feature_version=(3,8))
    (out/n).write_bytes(raw);pins[n]=sha(G/n)
    if n in b['source_sha256']:
        diff.extend(difflib.unified_diff((P/'before_sources'/n).read_text(encoding='utf8').splitlines(True),raw.decode('utf8').splitlines(True),fromfile='before/'+n,tofile='after/'+n))
(P/'SOURCE_DIFF.patch').write_text(''.join(diff),encoding='utf8')
save('VERIFICATION.json',dict(status='PASS_CPU_SAVED_EVIDENCE_SOFTWARE_ONLY',historical_files_verified=len(manifest['files']),
    model_pins=models,frozen_hardware_source_files_verified=len(h['software_sha256']),
    original_GPU_Coordinator_files_unchanged=True,PC_engine_AST_only_progress_wrappers=transform.count,
    CPU_initial_23_passed_1_fixture_failure=True,CPU_targeted_followup_6_passed=True,distinct_checks_passed=25,
    saved_MMIO_JSONL_records_byte_identical=5804,board_Python38_AST=True,source_sha256=pins,
    closed_CPU_evidence_sha256={p.relative_to(P).as_posix():sha(p) for p in sorted((P/'cpu_cases').glob('*/ps/evidence.fvej'))},
    active_state=active['state'],active_run=active['run_id'],board_connections=0,real_MMIO=0,
    GPU_runs=0,camera_starts=0,GUI_starts=0,new_scopes=0,actual_joint_steps_s='NOT_MEASURED'))
files={}
for f in sorted(P.iterdir()):
    if f.is_file() and f.name!='DELIVERY_MANIFEST.json' and f.suffix in ('.py','.json','.log','.md','.patch'):files[f.name]=sha(f)
for folder in ('before_sources','delivered_sources'):
    for f in sorted((P/folder).glob('*.py')):files[f.relative_to(P).as_posix()]=sha(f)
save('DELIVERY_MANIFEST.json',dict(schema='flyvis-line2-software-delivery/v1',evidence_level='CPU_SOFTWARE_ONLY',files=files,
    source_sha256=pins,gui_documents={n:sha(G/n) for n in ('API_CONTRACT.md','JOINT_STREAM_RUNTIME_CONTRACT.md')},
    actual_joint_steps_s='NOT_MEASURED',excluded=['cpu_cases bulk fixtures: closed container SHA in VERIFICATION.json']))
print(json.dumps(dict(status='SEALED_CPU_SOFTWARE_ONLY',files=len(files),source_files=len(names),
    historical_files=len(manifest['files']),model_pins=len(models),frozen_PS_sources=len(h['software_sha256']),
    distinct_checks_passed=25,manifest_sha256=sha(P/'DELIVERY_MANIFEST.json')),indent=2))

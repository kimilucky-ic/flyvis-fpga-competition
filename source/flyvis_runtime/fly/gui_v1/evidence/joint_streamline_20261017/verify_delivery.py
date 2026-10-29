"""Standard-library, read-only protection checks and local delivery sealing.

No sockets, subprocesses, neural computations, GUI/device imports or new scopes.
Writes only this explicitly named CPU evidence directory.
"""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
GUI=HERE.parents[1]
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def save(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf8')

before=load(HERE/'BEFORE.json')
for name,digest in before['source_sha256'].items():
    assert sha(HERE/'before_sources'/name)==digest, 'BEFORE_SOURCE '+name

base=GUI/'evidence/camera_joint32_20261016'
assert sha(base/'DELIVERY_MANIFEST.json')==before['historical_manifest_sha256']
old=load(base/'DELIVERY_MANIFEST.json')
for name,digest in old['files'].items():assert sha(base/name)==digest, 'OLD_EVIDENCE '+name
reg=load(GUI/'live_registry.json')
models={}
for key in ('full','r_only','decoder','parameters','initial','identity','nodes'):
    p=reg['pins'][key]
    assert sha(p['path'])==p['sha256'], 'MODEL_PIN '+key
    models[key]=dict(path=p['path'],sha256=p['sha256'])

hardware=load(GUI/'runtime/joint/7f111da4437843539eeffef2c6c2546e/hardware_handoff.json')
package=Path(hardware['software_package'])
for name,digest in hardware['software_sha256'].items():
    assert sha(package/name)==digest, 'FROZEN_HARDWARE_SOFTWARE '+name

active=load(GUI/'runtime/joint_active.json')
assert active['state']=='STOPPED' and active['run_id']=='815a7069e02e42fb8dc0cf9477e97926'
production=tuple(before['source_sha256'])+('joint_runtime_audit.py',)
snapshot=HERE/'delivered_sources'
snapshot.mkdir(exist_ok=True)
all_sources=production+('test_joint_streamline.py',)
source_sha={}
for name in all_sources:
    raw=(GUI/name).read_bytes()
    ast.parse(raw,filename=name)
    (snapshot/name).write_bytes(raw)
    source_sha[name]=sha(GUI/name)

diff=[]
for name in before['source_sha256']:
    oldtext=(HERE/'before_sources'/name).read_text(encoding='utf8').splitlines(True)
    newtext=(GUI/name).read_text(encoding='utf8').splitlines(True)
    diff.extend(difflib.unified_diff(oldtext,newtext,fromfile='before/'+name,tofile='after/'+name))
(HERE/'SOURCE_DIFF.patch').write_text(''.join(diff),encoding='utf8')

verification=dict(status='PASS_DELIVERY_STATIC_SOFTWARE_ONLY',historical_files_verified=len(old['files']),
    historical_manifest_sha256=sha(base/'DELIVERY_MANIFEST.json'),model_pins=models,
    frozen_hardware_software_files_verified=len(hardware['software_sha256']),
    unchanged_pinned_BIT_SHA=hardware['bit_sha256'],unchanged_pinned_HWH_SHA=hardware['hwh_sha256'],
    firmware_note='Pinned identity only; no board identity read or physical revalidation in this task',
    runtime_marker=dict(state=active['state'],run_id=active['run_id']),production_source_sha256=source_sha,
    syntax_checked=len(all_sources),new_GPU_runs=0,new_camera_captures=0,new_GUI_launches=0,
    board_connections=0,new_neural_steps=0,new_hardware_authorization_scopes=0,
    CPU_checks=dict(core=37,heartbeat=3,failures=0,errors=0),
    CPU_file_compare=load(HERE/'CPU_FILE_COMPARE.json')['summary'],
    CPU_HTTP_compare={name:value['summary'] for name,value in load(HERE/'CPU_HTTP_COMPARE.json')['variants'].items()},
    acceptance='NO_NEW_JOINT_PERFORMANCE_OR_REALTIME_PASS')
save('VERIFICATION.json',verification)

names=('BEFORE.json','REPORT.md','CPU_CHECKS.log','CPU_CHECKS_FINAL.log','CPU_HEARTBEAT_CHECKS.log',
    'cpu_compare.py','CPU_FILE_COMPARE.json','CPU_FILE_COMPARE_INTERMEDIATE.json','CPU_HTTP_COMPARE.json',
    'CPU_CLOCK_PHASES.json','CPU_HTTP_SERVER_CLOSED.json','CPU_HTTP_DONE.json','CPU_HTTP_REVOKE.json',
    'CPU_HTTP_REVOKED.json','cpu_idle_check.py','cpu_idle_check.json','verify_delivery.py',
    'VERIFICATION.json','SOURCE_DIFF.patch')
files={name:sha(HERE/name) for name in names}
for folder in ('before_sources','delivered_sources'):
    for p in sorted((HERE/folder).glob('*.py')):files[p.relative_to(HERE).as_posix()]=sha(p)
docs={name:sha(GUI/name) for name in ('JOINT_STREAM_RUNTIME_CONTRACT.md','API_CONTRACT.md')}
save('DELIVERY_MANIFEST.json',dict(schema='flyvis-line2-software-delivery/v1',evidence_level='CPU_SOFTWARE_ONLY',
    files=files,gui_documents=docs,production_source_sha256=source_sha,
    excluded=['CPU_HTTP_CONFIG_PRIVATE.json','temporary CPU fixture directories'],
    new_device_runs=0,whole_run_acceptance='NOT_A_NEW_EXPERIMENT'))
print(json.dumps(dict(status=verification['status'],historical_files_verified=len(old['files']),
    frozen_model_pins=len(models),hardware_source_files=len(hardware['software_sha256']),
    delivery_files=len(files),source_files=len(source_sha),devices_started=0),indent=2))

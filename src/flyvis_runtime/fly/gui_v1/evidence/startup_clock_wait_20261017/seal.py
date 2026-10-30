"""Local file evidence only; never contacts or operates a device."""
import ast,difflib,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
P=Path(__file__).resolve().parent;G=P.parent.parent
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(n,v):(P/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
old=G/'runtime/joint/af817b9ba8e8438b806c2f860f533b39'
bundle=G/'evidence/fresh_camera_start_20261017/actual_camera32/prepared_bundles/b3ab3d3be1e24ee9b69cf676f3ec4326'
launch=load(G/'evidence/fresh_camera_start_20261017/actual_camera32/PC_LAUNCH.json')
started=datetime.fromisoformat(launch['started_utc'].replace('Z','+00:00'))
events=[]
for label,path in [('PREPARED_PACKET',bundle/'PREPARED_PACKET.json'),('GPU_READY',old/'GPU_READY.json'),('FIRST_SAVED_RESULT',old/'result.json'),('WORKER_FAILURE',old/'worker_start_failure.json')]:
    stamp=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc)
    events.append(dict(event=label,Windows_file_mtime_utc=stamp.isoformat(),elapsed_from_launcher_s=(stamp-started).total_seconds(),path=str(path),sha256=sha(path)))
save('FAILURE_TIMELINE.json',dict(run_id=launch['run_id'],launcher_started_utc=launch['started_utc'],
    timing_basis='Windows file mtimes; first original clock error was not saved',events=events,
    result=load(old/'result.json'),worker_exit=load(old/'worker_exit.json'),
    conclusion='Eager 300-second lifetime defect reproduced on CPU; actual quarantine timing agrees, but original first clock cause unavailable'))
registry=load(G/'live_registry.json');models={}
for n in ('full','r_only','decoder','parameters','initial','identity','nodes'):
    pin=registry['pins'][n];assert sha(pin['path'])==pin['sha256'],n;models[n]=pin['sha256']
hardware=load(G/'runtime/joint/7f111da4437843539eeffef2c6c2546e/hardware_handoff.json')
for n,d in hardware['software_sha256'].items():assert sha(Path(hardware['software_package'])/n)==d,n
clock=Path(hardware['software_package'])/'a3ready/clock.py'
assert sha(clock)=='039bb5cb3c2688512bcf737c970d8364e773166763e67485f63454583993f7c1'
sources={};delivered=P/'delivered_sources';delivered.mkdir(exist_ok=True)
for n in ('joint_camera_preparation.py','joint_camera_fresh.py','joint_camera_bundle.py','joint_camera_manual.py','joint_camera_board_entry.py',
          'test_joint_camera_preparation.py','test_joint_preparation_clock_lifecycle.py','test_joint_fresh_unused.py'):
    raw=(G/n).read_bytes();ast.parse(raw);(delivered/n).write_bytes(raw);sources[n]=sha(G/n)
for n in ('joint_camera_fresh.py','joint_camera_board_entry.py'):ast.parse((G/n).read_text(encoding='utf8'),feature_version=(3,8))
before=(P/'before_sources/joint_camera_preparation.py').read_text(encoding='utf8').splitlines(True)
after=(G/'joint_camera_preparation.py').read_text(encoding='utf8').splitlines(True)
(P/'CLOCK_SOURCE_DIFF.patch').write_text(''.join(difflib.unified_diff(before,after,fromfile='before/joint_camera_preparation.py',tofile='after/joint_camera_preparation.py')),encoding='utf8')
save('VERIFICATION.json',dict(evidence_level='CPU_SOFTWARE_CHECKS_AND_ACTUAL_USER_PREPARATION',
    clock_tests=load(P/'CPU_RESULT.json'),handover_tests=load(P/'HANDOVER_CPU_RESULT.json'),
    model_pins=models,frozen_PS_source_files_verified=len(hardware['software_sha256']),original_clock_sha256=sha(clock),
    unchanged_clock_limits=dict(max_age_s=300,jump_guard_ms=200),source_sha256=sources,
    original_failed_run_committed_steps=0,actual_current_run=load(G/'runtime/joint_active.json'),
    no_claim_of_new_32step_PASS=True))
files={}
for f in sorted(P.iterdir()):
    if f.is_file() and f.name not in ('DELIVERY_MANIFEST.json','PC_CONTROLLER_r2.log','PC_CONTROLLER_r2.stderr.log','USER_PREPARE_READY.png'):
        files[f.name]=sha(f)
for f in sorted(delivered.iterdir()):files[f.relative_to(P).as_posix()]=sha(f)
save('DELIVERY_MANIFEST.json',dict(schema='flyvis-line2-startup-clock-fix/v1',files=files,source_sha256=sources,
    live_logs_unsealed_until_run_end=['PC_CONTROLLER_r2.log','PC_CONTROLLER_r2.stderr.log'],
    Notebook_screenshot_with_private_one_use_token_excluded=True))
print(json.dumps(dict(status='SEALED_LOCAL_SOFTWARE_EVIDENCE',model_pins=len(models),PS_sources=len(hardware['software_sha256']),tests=29)))

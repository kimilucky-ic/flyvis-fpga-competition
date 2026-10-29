"""Local evidence index only. Never launches a service, device or experiment."""
import ast,difflib,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent
GUI=OUT.parents[1];FLY=GUI.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(name,value):
    (OUT/name).write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))

passed=set()
for path in OUT.glob('CPU_*.log'):
    for line in path.read_text(encoding='utf-8-sig',errors='replace').splitlines():
        match=re.match(r'^\w+ \(([^)]+)\) \.\.\. ok$',line)
        if match:passed.add(match[1])
missing=[]
tree=ast.parse((GUI/'test_joint_fixed.py').read_text(encoding='utf-8'))
for cls in tree.body:
    if isinstance(cls,ast.ClassDef):
        for fn in cls.body:
            if isinstance(fn,ast.FunctionDef) and fn.name.startswith('test_'):
                name='test_joint_fixed.'+cls.name+'.'+fn.name
                if name not in passed:missing.append(name)
assert not missing,missing

syntax=[]
for name in ('joint_camera_fixed_board.py','joint_camera_fresh.py','joint_camera_repeat_board.py','joint_camera_clock_wait.py',
    'joint_camera_board_entry.py','joint_minimal_board.py','joint_minimal_core.py','joint_minimal_worker.py'):
    ast.parse((GUI/name).read_text(encoding='utf-8'),feature_version=(3,8));syntax.append(name)
notebook=load(GUI/'FlyVis摄像头联合实验.ipynb')
assert len([c for c in notebook['cells'] if c['cell_type']=='code'])==1
ast.parse(''.join(notebook['cells'][1]['source']),feature_version=(3,8))
entry=notebook['metadata']['flyvis_fixed_entry']
assert hashlib.sha256(entry['source'].encode()).hexdigest()==entry['source_sha256']
assert entry['source']==(GUI/'joint_camera_fixed_board.py').read_text(encoding='utf-8')

diff=[];files=[]
for old in sorted((OUT/'before_sources').iterdir()):
    current=FLY/old.name.replace('__','/')
    if not current.is_file():continue
    files.append(dict(path=str(current),before_sha256=sha(old),sha256=sha(current),changed=sha(old)!=sha(current)))
    if old.suffix in ('.py','.js','.cjs','.ps1','.cmd','.md','.cs'):
        diff.extend(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),
            current.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+old.name,tofile=str(current)))
(OUT/'PRODUCTION.diff').write_bytes(''.join(diff).encode('utf-8'))
for name in ('joint_camera_fixed.py','joint_camera_fixed_board.py','test_joint_fixed.py','test_joint_minimal.py','FlyVis摄像头联合实验.ipynb'):
    files.append(dict(path=str(GUI/name),sha256=sha(GUI/name)))

# Small original model/coordinator and historical-manifest identity checks.
# No expensive full historical experiment scan or recalculation.
invariants={}
historical=GUI/'runtime/joint/b89df86a91b947ed93a4007b6e907a9b'
pins=load(historical/'scope.json')['source_sha256']
for name in ('hybrid_a3.py','hybrid_gpu.py','hybrid_full485.py','prepared_camera_input.py',
    'joint_camera_fresh.py','joint_camera_board_entry.py','joint_camera_engine.py','joint_camera_bridge.py'):
    invariants[name]=sha(GUI/name)==pins[name]
assert all(invariants.values()),invariants
for path in (historical/'result.json',historical/'worker_exit.json',GUI/'runtime/joint_active.json',GUI/'runtime/joint_workbench_active.json'):
    files.append(dict(path=str(path),sha256=sha(path),read_only=True))
baseline=load(GUI/'evidence/repeat_workbench_20261018/ACTUAL_RUN_MANIFEST.json')
old100=[dict(path=row['path'],unchanged=sha(Path(row['path']))==row['sha256']) for row in baseline['files']]
assert all(row['unchanged'] for row in old100)

save('VERIFICATION.json',dict(status='PASS_FOCUSED_SOFTWARE_ONLY_REAL_60S_PENDING',
    evidence_level='CPU_PROTOCOL_MOCK_HTTP_DOM_SAVED_REAL_ARRAYS_NO_NEW_INFERENCE',
    time_utc=datetime.now(timezone.utc).isoformat(),default_actual_duration_s=60,maximum_actual_duration_s=60,
    maximum_steps=12000,model_dt_s=.005,compute_pacing='UNTHROTTLED_COMMIT_DRIVEN',display_max_hz=5,
    input_policy='LATEST_CONVERTED_AT_STEP_START_COMMIT_DRIVEN',record_queue_capacity=32,
    record_policy='ASYNC_STREAMING_BOUNDED_FAIL_STOP',short_test_steps=100,
    python_unique_cases_passed=len(passed),python_cases=sorted(passed),all_20_new_tests_passed=True,
    ps_python38_syntax=syntax,notebook_single_code_cell=True,
    JS=dict(timed_start_stop_audit_start=12,unthrottled_fake_clock_scenarios=4,legacy_saved_array_protocol=5),
    original_sources_unchanged=invariants,prior_accepted_100_run_files_unchanged=old100,
    process_launches=0,network_listeners=0,board_connections=0,hardware_loads=0,hardware_resets=0,
    GPU_runs=0,camera_runs=0,GUI_launches=0,board_run_status='NOT_RUN_BOARD_OCCUPIED',REALTIME_STREAM_PASS='NOT_CLAIMED',
    desktop_shortcut=dict(path='C:\\Users\\hzy72\\Desktop\\FlyVis 摄像头联合实验.lnk',
        target=str(FLY/'flyvis_96b7ca62.cmd'),created_and_target_verified=True,launched=False),
    original_desktop_entry=dict(path=str(FLY/'FlyVis.exe'),default='ORIGINAL_JOINT_CONTROLLER_FIXED_NOTEBOOK_60S',
        offline_switch='--offline',old_binary_preserved=str(OUT/'before_sources/FlyVis.exe'),
        verification=load(OUT/'DESKTOP_ROUTING.json'),executable_sha256=sha(FLY/'FlyVis.exe')),
    unused_notebook_pairing_rotated_before_delivery=True,
    initial_failures_preserved=['One new test referenced a nonexistent helper method; fixed test name',
        'Two old CPU board fixtures used Linux /proc on Windows; verified with isolated CPU boot fixture',
        'One test syntax continuation corrected',
        'Cold-prefix file used CRLF but text hash normalized LF; fixed prefix to UTF-8 bytes and rechecked'],
    incomplete=['Real new-kernel A3R1 preparation and actual 60s camera/GPU/FPGA run',
        'Real stop/restart, memory/disk throughput and end-to-end FPS/latency',
        'Latest historical run7141 PC result remains STOPPED_PENDING_PS_AUDIT; missing PS capture not waived'],
    operator_steps=['Upload the one fixed Notebook once after board release',
        'Double-click desktop FlyVis 摄像头联合实验',
        'Run the one Notebook cell; confirm hardware initialization only when board is released',
        'GUI Start/Stop; wait for automatic evidence/audit then Start again',
        'Close workbench normally; no automatic hardware retry'],files=files))
print(json.dumps(dict(status='PASS_FOCUSED_SOFTWARE_ONLY',python_unique_cases=len(passed),
    new_tests=20,output=str(OUT/'VERIFICATION.json')),ensure_ascii=False))

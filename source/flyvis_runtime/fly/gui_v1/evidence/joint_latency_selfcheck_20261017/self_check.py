"""Read-only comparison of saved physical run and unused-start host diagnostics.

Standard library only. No socket, torch, camera, GPU or FPGA execution.
"""
import ast,collections,hashlib,importlib.util,json,statistics,time
from pathlib import Path

HERE=Path(__file__).resolve().parent;GUI=HERE.parents[1]
BASE=GUI/'evidence/camera_joint32_20261016'
OLD=GUI/'runtime/joint/7f111da4437843539eeffef2c6c2546e'
UNUSED=GUI/'runtime/joint/34e96b4d227f488bb3214190089569d1'
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def stats(values):
    a=sorted(values)
    return dict(count=len(a),sum=sum(a),p50=statistics.median(a),p95=a[int(.95*(len(a)-1))],max=a[-1])

manifest=load(BASE/'DELIVERY_MANIFEST.json')
for name,digest in manifest['files'].items():assert sha(BASE/name)==digest, 'BASELINE_FILE_CHANGED '+name
scope=load(UNUSED/'scope.json')
for name,digest in scope['source_sha256'].items():assert sha(GUI/name)==digest, 'CURRENT_SOURCE_CHANGED '+name
reg=load(GUI/'live_registry.json');protected={}
for key in ('full','r_only','decoder','parameters','initial','identity','nodes'):
    p=reg['pins'][key];assert sha(p['path'])==p['sha256'], 'MODEL_PIN_CHANGED '+key;protected[key]=p['sha256']

accepted=load(BASE/'actual_32step/FINAL_AUDIT.json');snaps=accepted['snapshots']
assert sha(OLD/'pc/evidence.fvej')==accepted['PC_capture_sha256']
assert sha(OLD/'ps_retrieved_authorized/evidence.fvej')==accepted['PS_capture_sha256']
h=load(OLD/'hardware_handoff.json');member='a3latency485/evidence_journal.py';reader_file=Path(h['software_package'])/member
assert sha(reader_file)==h['software_sha256'][member]
spec=importlib.util.spec_from_file_location('saved_journal_readonly_20261017',reader_file)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
pc,ps=mod.JournalReader(OLD/'pc/evidence.fvej'),mod.JournalReader(OLD/'ps_retrieved_authorized/evidence.fvej')
events=[json.loads(s) for s in ps.read('events.jsonl').splitlines()]
event_counts=collections.Counter(e['event'] for e in events)
profiles=[json.loads(ps.read('ps_profile_%d.json'%k)) for k in range(32)]
ps_timings=[json.loads(ps.read('timing_%d.json'%k)) for k in range(32)]
intervals=[]
for before,after in zip(snaps,snaps[1:]):
    interval=(after['wall_elapsed_s']-before['wall_elapsed_s'])*1000
    wire=after['STEP_roundtrip_ms']+after['COMMIT_roundtrip_ms']
    intervals.append(dict(step=after['step'],interval_ms=interval,STEP_COMMIT_inclusive_ms=wire,
        outside_STEP_COMMIT_ms=interval-wire))

d=load(UNUSED/'host_diagnostics.json');assert d['run_id']==scope['run_id'] and d['diagnostic_complete'] and not d['dropped_spans']
groups=collections.defaultdict(list)
for row in d['spans']:groups[row['name']].append(row)
diagnostic_summary={}
for name,rows in groups.items():
    diagnostic_summary[name]=dict(wall_ms=stats([s['duration_ns']/1e6 for s in rows]),
        thread_cpu_ms=sum(s['thread_cpu_ns'] for s in rows)/1e6,failed=sum(s['failed'] for s in rows))
clock=groups['gate.PC_clock_HTTP']
long=[dict(ordinal=i,start_s=r['start_ns']/1e9,wall_ms=r['duration_ns']/1e6,thread_cpu_ms=r['thread_cpu_ns']/1e6)
    for i,r in enumerate(clock,1) if r['duration_ns']>100_000_000]
engine_ast=ast.parse((BASE/'executed_sources/joint_camera_engine.py').read_text())
engine_step=next(n for n in ast.walk(engine_ast) if isinstance(n,ast.FunctionDef) and n.name=='step')
calls=sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name)
    and n.func.value.id=='self' and n.func.attr=='gate' for n in ast.walk(engine_step))

result=dict(status='READ_ONLY_LATENCY_SELF_CHECK_NOT_NEW_DEVICE_ACCEPTANCE',date='2026-10-17',
    protected=dict(baseline_manifest_sha256=sha(BASE/'DELIVERY_MANIFEST.json'),baseline_files_verified=len(manifest['files']),
        current_source_pins_verified=len(scope['source_sha256']),model_pins=protected),
    physical_run=dict(run_id=accepted['run_id'],steps=32,PC_bytes=(OLD/'pc/evidence.fvej').stat().st_size,
        PC_barrier_counts=dict(collections.Counter(b['barrier'] for b in pc.batches)),
        PS_event_counts=dict(event_counts),PS_profiles=profiles,PS_timings=ps_timings,
        PS_step_fsync_ms=stats([p['phase_ns']['fsync']/1e6 for p in profiles]),
        PS_step_fsync_calls=sum(p['fsync_calls'] for p in profiles),
        PS_before_final_close_profile=json.loads(ps.read('PS_PROFILE_TOTAL.json')),
        performance=load(BASE/'PERFORMANCE.json'),intervals=intervals),
    unused_run=dict(run_id=d['run_id'],neural_steps=load(UNUSED/'result.json')['committed_steps'],
        evidence_scope='HOST_PRESTART_DIAGNOSTICS_NOT_PHASE_TIMING_OF_THE_32STEP_RUN',
        diagnostic_complete=True,diagnostic_span_count=len(d['spans']),phase_summary=diagnostic_summary,
        long_clock_checks=long,long_clock_wall_s=sum(r['wall_ms'] for r in long)/1000,
        long_clock_thread_cpu_ms=sum(r['thread_cpu_ms'] for r in long)),
    code_paths=dict(engine_gates_per_step=calls,outer_worker_gate_per_step=1,decoder_gates_per_one_frame_chunk=2,
        total_authenticated_clock_checks_per_ordinary_step=calls+3,
        STEP_roundtrip_includes_PC_BEFORE_SEND_fsync=True,COMMIT_roundtrip_includes_PC_BEFORE_SEND_fsync=True,
        CPU_same_old_reference_runs_before_PL_STEP=True,official_decoder_weights_checked_before_and_after_each_decode=True),
    CPU_path_probe=load(HERE/'CPU_PATH_RESULT.json'),CPU_HTTP_probe=load(HERE/'CPU_HTTP_RESULT.json'),
    unresolved=['No phase timings exist for physical step15/30; causal attribution is not proven.',
        'The virtual-adapter CPU HTTP test did not reproduce the old physical-address one-second waits.',
        'No actual end-to-end speedup has been measured; necessary checks and persistent barriers are unchanged.'],
    execution=dict(new_GPU_runs=0,new_camera_captures=0,board_connections=0,new_neural_steps=0,
        production_source_modifications=0,CPU_diagnostic_guard_requests=640))
(HERE/'READ_ONLY_FINDINGS.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps(dict(status=result['status'],protected=result['protected'],code_paths=result['code_paths'],
    PS_step_fsync_ms=result['physical_run']['PS_step_fsync_ms'],long_clock_checks=len(long),
    long_clock_wall_s=result['unused_run']['long_clock_wall_s']),indent=2))

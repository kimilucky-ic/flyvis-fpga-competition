"""②'s ONE managed launch owner. Default is read-only check; execute is explicit."""
import argparse
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import uuid

from live_protocol import HERE, Registry, canonical, host_path, load, require, sha, utc, write
from joint_camera_protocol import PROFILE, POLICY, validate_scope
from joint_camera_control import require_camera_service

ACTIVE = HERE/'runtime/joint_active.json'
SOURCES = ('joint_camera_controller.py','joint_camera_protocol.py','joint_camera_engine.py','joint_camera_worker.py',
    'joint_camera_control.py','joint_camera_runtime.py','joint_camera_converter.py','joint_camera_bridge.py','joint_camera_finish.py',
    'joint_camera_preparation.py','joint_camera_board_entry.py',
    'joint_camera_retained.py','joint_camera_bundle.py','joint_camera_manual.py',
    'joint_camera_fresh.py','joint_camera_clock_wait.py','hybrid_gpu.py','hybrid_a3.py','hybrid_v2.py','hybrid_full485.py','live_protocol.py','prepared_camera_input.py',
    'stream_transport.py','spatial_state.py','projection_startup.py','cached_skeleton.py','server.py','joint_diagnostics.py','joint_runtime_audit.py','joint_camera_io.py','ps_commit_evidence.py',
    'joint_minimal_core.py','joint_minimal_board.py','joint_minimal_worker.py')

def controller_heartbeat(root,session_id,pc_clock=None,*,neural_active=True):
    # A completed/failed worker must not acquire a new clock failure while the
    # user inspects its saved final frame. Cleanup also cannot depend on expiry.
    if pc_clock and neural_active:
        try:pc_clock.check()
        except BaseException as error:
            path=root/'ERROR_REQUEST.json'
            if not path.exists():write(path,dict(error='PC_CLOCK_AUTHORITY: '+str(error),session_id=session_id))
            raise
    write(root/'controller.json',dict(session_id=session_id,unix_time=time.time(),pid=os.getpid()))


def source_pins():
    return {name: sha(HERE/name) for name in SOURCES}


def draft(path):
    from hybrid_full485 import Full485Contract
    from hybrid_a3 import module
    c = Full485Contract()
    initial, words, _ = c.initial()
    hmod = module('camera_draft_initial', c.paths['h_step'])
    run, sid, ps = (uuid.uuid4().hex for _ in range(3))
    value = dict(schema='flyvis-camera-joint-scope/v1', status='DRAFT_NOT_AUTHORIZED', execution_authority='NONE',
        human_authorization_reference=None, run_id=run, session_id=sid, server_session=ps, gpu_lease_id=uuid.uuid4().hex,
        comparison_id='CAMERA_'+run, boot_id=None, source_kind='real_windows_camera', condition_id='CURRENT_CAMERA', camera_id=0,
        dt_s=.005, numerical_profile=PROFILE, input_policy=POLICY, model=c.registry['model'], mapping_sha256=c.mapping_sha,
        initial_full_digest=hmod.array_hash(initial), initial_H_sha256=sha_bytes(words),
        tolerance=c.tolerance, bit_sha256=c.wire.BIT_SHA, hwh_sha256=c.wire.HWH_SHA,
        max_steps=32, capture_duration_s=30, max_worker_s=180, start_utc=None, end_utc=None,
        new_loads=0, new_resets=0, new_allocations=0, native_H_GPU_updates=0, automatic_retry=False,
        validation_policy='SAME_OLD_CPU_POST_RUN',runtime_audit_policy='LOADED_STATIC_START_END_HASH/v1',
        neural_transport_policy='TCP_NODELAY_QUICKACK_WHEN_SUPPORTED/v1',journal_storage_policy='DIRECT_SESSION/v1',
        pc_commit_journal_policy='MERGED_INTENT_BEFORE_SEND/v1',
        ps_durability_policy='PS_COMMIT_ACK_DURABLE_TWO_BARRIERS/v1',ps_evidence_adapter_sha256=sha(HERE/'ps_commit_evidence.py'),
        hardware_handoff_sha256=None, source_sha256=source_pins())
    p = host_path(path)
    require(not p.exists(), 'DRAFT_FILE_ALREADY_EXISTS')
    p.parent.mkdir(parents=True, exist_ok=True)
    write(p, value)
    return dict(status='DRAFT_ONLY', path=str(p), execution_authority='NONE', run_id=run)


def sha_bytes(raw):
    import hashlib
    return hashlib.sha256(raw).hexdigest()


def check(scope_path, hardware_path):
    s, h = load(scope_path), load(hardware_path)
    validate_scope(s)
    if s.get('hardware_declaration_sha256'):
        from joint_camera_preparation import verify_prepared_handoff
        verify_prepared_handoff(h,s,host_path(hardware_path).parent)
    else:
        require(sha(hardware_path) == s['hardware_handoff_sha256'], 'HARDWARE_HANDOFF_SHA')
    require_camera_service(h, s)
    require(s['source_sha256'] == source_pins(), 'JOINT_CONTROLLER_SOURCE_CHANGED')
    from hybrid_full485 import Full485Contract
    validate_scope(s, Full485Contract())
    return s, h


def linux(path):
    path = str(Path(path).resolve())
    require(len(path) > 3 and path[1] == ':', 'ABSOLUTE_WINDOWS_PATH_REQUIRED')
    return '/mnt/'+path[0].lower()+'/'+path[3:].replace('\\','/')


def execute(scope_path, hardware_path, pc_clock=None):
    from launch_recovery import launch_guard, gui_port_available
    # No GPU, camera, board, GUI or socket starts before all local admission checks.
    scope, hardware = check(scope_path, hardware_path)
    reg = Registry()
    with launch_guard():
        if ACTIVE.exists():
            require(load(ACTIVE).get('state')=='STOPPED', 'PREVIOUS_JOINT_STOP_NOT_CONFIRMED')
        original=HERE/'runtime/demo_active.json'
        if original.exists():
            require(load(original).get('state')=='STOPPED', 'ORIGINAL_GUI_OR_FULL_WORKER_NOT_STOPPED')
        gui_port_available()
        root = HERE/'runtime/joint'/scope['session_id']
        root.mkdir(parents=True, exist_ok=False)  # Never resurrect an old run.
        for src, name in ((scope_path,'scope.json'),(hardware_path,'hardware_handoff.json')):
            (root/name).write_bytes(host_path(src).read_bytes())
        require(sha(root/'scope.json') == sha(scope_path), 'SCOPE_COPY_IDENTITY')
        port = None
        for candidate in range(18781,18789):
            try:
                with socket.socket() as probe: probe.bind(('127.0.0.1',candidate))
                port = candidate; break
            except OSError: continue
        require(port is not None, 'JOINT_RPC_PORT_UNAVAILABLE')
        from camera_stream_protocol import dependencies
        session = dict(schema='flyvis-camera-joint-session/v1', session_id=scope['session_id'], run_id=scope['run_id'],
            scope_sha256=sha(root/'scope.json'), hardware_handoff_sha256=sha(hardware_path), rpc_port=port,
            end_unix=datetime.fromisoformat(scope['end_utc']).timestamp(), camera_dependencies_sha256=canonical(dependencies()))
        write(root/'session.json', session)
        if pc_clock and getattr(pc_clock,'clock_started_utc',None):
            # Display metadata only; the original clock helper still enforces
            # its bounded lifetime. Do not create/refresh a clock here.
            clock_end=min(datetime.fromisoformat(scope['end_utc']),
                datetime.fromisoformat(pc_clock.clock_started_utc)+timedelta(seconds=pc_clock.clock_wait_s))
            write(root/'START_WINDOW.json',dict(run_id=scope['run_id'],session_id=scope['session_id'],
                pc_clock_id=hardware['pc_clock_id'],deadline_unix=clock_end.timestamp()))
        children, logs = [], []
        state = dict(state='STARTING', session_id=scope['session_id'], run_id=scope['run_id'], root=str(root),
            owner='LINE2_CAMERA_JOINT_SINGLE_CONTROLLER', pid=os.getpid(), children=[])
        def beat(neural_active=None):
            if neural_active is None:neural_active=not any(name=='joint_worker' and p.poll() is not None for name,p in children)
            controller_heartbeat(root,scope['session_id'],pc_clock,neural_active=neural_active)
        def spawn(name, command):
            f = (root/(name+'.log')).open('ab'); logs.append(f)
            flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            p = subprocess.Popen(command, stdout=f, stderr=subprocess.STDOUT, cwd=str(HERE), creationflags=flags)
            children.append((name,p)); state['children'].append(dict(name=name,pid=p.pid)); write(ACTIVE,state)
        try:
            beat(); write(ACTIVE,state)
            spawn('gui', [sys.executable,'-B',str(HERE/'server.py'),'--no-open','--port','8771',
                '--joint-session',str(root/'session.json'),'--stop-file',str(root/'GUI_STOP.json'),'--controller-file',str(root/'controller.json')])
            spawn('joint_worker', ['wsl.exe','-d','FlyVisCPU','--exec',reg.data['runtime']['python'],'-B',
                linux(HERE/'joint_camera_worker.py'),'--root',linux(root)])
            state['state']='RUNNING'; write(ACTIVE,state)
            print('http://127.0.0.1:8771/#competition · 摄像头联合入口；页面明确开始才采集。',flush=True)
            while not (root/'STOP_REQUEST.json').exists():
                beat()
                if any(name=='gui' and p.poll() is not None for name,p in children): break
                if any(name=='joint_worker' and p.poll() is not None for name,p in children):
                    # GUI survives for recording/inspection and old offline data.
                    state['worker_exit_code']=next(p.poll() for name,p in children if name=='joint_worker')
                    write(ACTIVE,state)
                if time.time() >= session['end_unix']: break
                time.sleep(.5)
        finally:
            write(root/'STOP_REQUEST.json', dict(reason='CONTROLLER_STOP', session_id=scope['session_id']))
            state['state']='STOPPING'; write(ACTIVE,state)
            worker = next((p for name,p in children if name=='joint_worker'),None)
            if worker:
                until=time.monotonic()+20
                while worker.poll() is None and time.monotonic()<until:
                    beat(neural_active=False); time.sleep(.1)
                if worker.poll() is None:
                    state['state']='GPU_STOP_UNCONFIRMED_NO_FORCED_KILL'
            write(root/'GUI_STOP.json', dict(reason='CONTROLLER_STOP'))
            for name,p in children:
                if name=='gui':
                    try:p.wait(5)
                    except subprocess.TimeoutExpired:pass
            state['exit_codes']={name:p.poll() for name,p in children}
            if all(code is not None for code in state['exit_codes'].values()): state['state']='STOPPED'
            write(ACTIVE,state)
            for f in logs:f.close()


def stop():
    state=load(ACTIVE); root=host_path(state['root'])
    require(root.resolve().parent==(HERE/'runtime/joint').resolve() and root.name==state['session_id'], 'JOINT_STOP_OWNER')
    write(root/'STOP_REQUEST.json',dict(reason='USER_STOP',session_id=state['session_id']))
    return dict(status='STOP_REQUESTED_NOT_YET_CONFIRMED')


def main():
    p=argparse.ArgumentParser(description='Single camera GPU-FPGA controller; no implicit device launch')
    p.add_argument('--scope');p.add_argument('--hardware-handoff');p.add_argument('--draft')
    p.add_argument('--execute',action='store_true');p.add_argument('--stop',action='store_true')
    p.add_argument('--prepared-bundle')
    p.add_argument('--manual-prepare',action='store_true')
    p.add_argument('--minimal-compute',action='store_true')
    a=p.parse_args()
    if a.manual_prepare:
        require(a.execute,'MANUAL_PREPARATION_EXECUTE_REQUIRED')
        from joint_camera_manual import manual_prepare
        manual_prepare(execute,minimal_compute=a.minimal_compute);return
    if a.prepared_bundle:
        require(a.execute, 'PREPARATION_EXECUTE_REQUIRED')
        from joint_camera_preparation import prepare_and_execute
        prepare_and_execute(a.prepared_bundle, execute);return
    if a.draft: result=draft(a.draft)
    elif a.stop: result=stop()
    elif a.scope and a.hardware_handoff:
        if a.execute: execute(a.scope,a.hardware_handoff);return
        check(a.scope,a.hardware_handoff);result=dict(status='LOCAL_ADMISSION_ONLY_NO_EXECUTION')
    else: result=dict(status='NOT_CONNECTED',reason='Explicit new camera scope and matching hardware handoff required',execution_authority='NONE')
    import json
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

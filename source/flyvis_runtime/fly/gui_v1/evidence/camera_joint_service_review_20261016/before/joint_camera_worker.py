"""Explicitly scoped camera -> original CUDA chemical/R -> prepared A3 service.

This is the sole neural worker of the new controller. There is NO Full step,
ON60 fallback, board initialization, automatic retry or historical output source.
"""
import argparse
from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from live_protocol import HERE, Registry, canonical, host_path, load, require, sha, utc, write
from live_worker import import_file
from joint_camera_protocol import LIVE, validate_scope


def current_reference(reg, c, torch):
    R = import_file('camera_joint_original_cpu_R', reg.path_for('r_only')).RStepService
    reference = R(reg.path_for('parameters'), reg.path_for('identity'), c.paths['R5768_manifest'], device='cpu')
    with np.load(reg.path_for('parameters'), allow_pickle=False) as z:
        mask = np.isin(z['target_global'], c.h)
        local = np.full(45669, -1, dtype=np.int64)
        local[c.h] = np.arange(5768)
        src, dst, weight = z['source_global'][mask].copy(), local[z['target_global'][mask]], z['effective_weight'][mask].copy()
        input_ids = z['input_node_index'].copy()
    def check(old, frame, out, step):
        rr = reference.step(torch.from_numpy(old.copy()), torch.from_numpy(frame.copy()),
            run_id='INDEPENDENT_CURRENT_INPUT_REFERENCE', step_id=step, condition_id='CURRENT_CAMERA')
        chem = np.zeros(5768, dtype=np.float32)
        np.add.at(chem, dst, weight * np.maximum(old[src], np.float32(0)))
        x = np.zeros(45669, dtype=np.float32)
        x[input_ids] = frame
        require(np.array_equal(out['r_ids'], c.r) and np.array_equal(out['x_full'], x), 'JOINT_REFERENCE_MAP')
        require(np.allclose(rr.activity.numpy(), out['new_R'], atol=1e-5, rtol=1e-5), 'JOINT_R_REFERENCE')
        require(np.allclose(chem, out['chemical_H'], atol=1e-5, rtol=1e-5), 'JOINT_CHEMICAL_REFERENCE')
        return dict(status='PASS_CURRENT_INPUT_SAME_OLD_REFERENCE', R_max_abs=float(np.max(np.abs(rr.activity.numpy()-out['new_R']))),
            chemical_max_abs=float(np.max(np.abs(chem-out['chemical_H']))), atol=1e-5, rtol=1e-5,
            production_source=False)
    return check


def run(root):
    root = host_path(root).resolve()
    session = load(root/'session.json')
    scope = load(root/'scope.json')
    require(root.parent == (HERE/'runtime/joint').resolve(), 'JOINT_WORKER_ROOT')
    require(sha(root/'scope.json') == session['scope_sha256'], 'JOINT_SCOPE_FILE')
    validate_scope(scope)
    from hybrid_full485 import Full485Contract
    from hybrid_gpu import GPUCandidates
    from joint_camera_engine import CameraJointEngine, JointCameraEvidence
    from joint_camera_runtime import JointCameraHub
    from stream_transport import LocalRPC, AuditMonitor
    from realtime_timing import Timings
    from joint_camera_control import require_camera_service, board_client, CameraHardwareControl
    c, reg = Full485Contract(), Registry()
    validate_scope(scope, c)
    hardware = load(root/'hardware_handoff.json')
    require(sha(root/'hardware_handoff.json') == scope['hardware_handoff_sha256'], 'JOINT_HARDWARE_HANDOFF_CHANGED')
    require_camera_service(hardware, scope)
    control = CameraHardwareControl(board_client(hardware), hardware, scope, session['scope_sha256'])
    # Authenticated readiness/capabilities BEFORE acquiring or importing CUDA.
    # Old fixed485 services are deliberately incompatible and fail here.
    control.prepared()
    package = host_path(hardware['software_package'])
    for relative, expected in hardware['software_sha256'].items():
        p = (package/relative).resolve()
        require(p.is_relative_to(package.resolve()) and sha(p) == expected, 'JOINT_HARDWARE_SOFTWARE_SOURCE')
    # Same accepted ⑦ vector checker and append-only writer, imported by exact pin.
    require({'fast_validation.py', 'a3latency485/evidence_journal.py'} <= hardware['software_sha256'].keys(), 'JOINT_REQUIRED_REUSED_MODULES')
    import_file('camera_joint_reused_vector', package/'fast_validation.py').install(c)
    Journal = import_file('camera_joint_reused_journal', package/'a3latency485/evidence_journal.py').JournalWriter
    runner = import_file('camera_joint_shared_lease', reg.path_for('runner_lease'))
    began = time.monotonic()
    hub = JointCameraHub(scope, c.spatial)
    scope_sha = sha(root/'scope.json')
    monitor = None
    converter = engine = client = handle = rpc = torch = log = evidence = None
    reason = 'FAILED_BEFORE_START'
    inflight = False
    def audit():
        validate_scope(scope, c)
        require(sha(root/'scope.json') == scope_sha and load(root/'session.json') == session, 'JOINT_SESSION_CHANGED')
        require(sha(root/'hardware_handoff.json') == scope['hardware_handoff_sha256'], 'JOINT_HANDOFF_CHANGED')
        for name, expected in scope['source_sha256'].items():
            path = (HERE/name).resolve()
            require(path.is_relative_to(HERE) and sha(path) == expected, 'JOINT_GUI_SOURCE_CHANGED '+name)
        c.unchanged(); reg.unchanged()
        ctrl = load(root/'controller.json')
        require(ctrl['session_id'] == scope['session_id'] and time.time()-ctrl['unix_time'] < 10, 'JOINT_CONTROLLER_LOST')
        require(not runner.own_path('runtime','RESOURCE_QUARANTINE.json').exists(), 'RESOURCE_QUARANTINE')
    def gate():
        validate_scope(scope)
        require(time.monotonic()-began < scope['max_worker_s'], 'JOINT_WORKER_DEADLINE')
        if (root/'ERROR_REQUEST.json').exists():
            raise ValueError('JOINT_INPUT_OR_DISPLAY_ERROR')
        if monitor: monitor.check()
        # Normal STOP defers to a transaction boundary. Errors/deadlines do not.
        hub.check(allow_stop=inflight)
    class Lease(runner.Lease):
        def init__(self):
            self.job = root
            self.config = dict(campaign_id=scope['gpu_lease_id'], stage='CAMERA_GPU_FPGA_JOINT', queue_s=10)
            self.ticket = dict(config=self.config, identity_key=canonical(scope), job_dir=str(root), scope='current camera chemical/R only, no native H')
        def check(self, phase='check'): gate()
    try:
        audit()
        monitor = AuditMonitor(audit)
        handle, queue_s = Lease().acquire()
        scratch = Path('/tmp')/('camera-joint-'+scope['run_id'])
        scratch.mkdir()
        os.environ.update(CUBLAS_WORKSPACE_CONFIG=':4096:8', CUDA_VISIBLE_DEVICES='0', FLYVIS_ROOT_DIR=str(scratch/'flyvis'), MPLBACKEND='Agg', MPLCONFIGDIR=str(scratch/'mpl'))
        rpc = LocalRPC(scope['session_id'], hub.dispatch, port=session['rpc_port'])
        write(root/'joint_endpoint.json', rpc.endpoint)
        log = (root/'converter.log').open('ab')
        converter = subprocess.Popen([sys.executable, '-B', str(HERE/'joint_camera_converter.py'), '--root', str(root)],
            env=dict(os.environ, CUDA_VISIBLE_DEVICES='-1'), stdout=log, stderr=subprocess.STDOUT)
        import torch as t
        torch = t
        torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = torch.backends.cudnn.allow_tf32 = False
        require(torch.cuda.is_available(), 'CUDA_REQUIRED_NO_FALLBACK')
        Full = import_file('camera_joint_original_Full', reg.path_for('full')).FullNetworkOracle
        oracle = Full(reg.path_for('identity'), model_path=reg.data['runtime']['model_path'], device='cuda')
        Decode = import_file('camera_joint_official_Decoder', reg.path_for('decoder')).OfficialDecoderService
        decoder = Decode(reg.data['runtime']['model_path'], reg.path_for('decoder_contract'), device='cuda', check_scope=lambda *args: gate())
        producer = GPUCandidates(reg, c, oracle, torch, Timings())
        check = current_reference(reg, c, torch)
        hub.gpu_ready = True; hub.state = 'WAITING_CAMERA_SELECTION'
        gpu_ready = dict(status='GPU_READY', run_id=scope['run_id'], session_id=scope['session_id'], server_session=scope['server_session'],
            scope_sha256=scope_sha, native_H_updates=0, device=torch.cuda.get_device_name(),
            board_connected=False, waiting_for='BOARD_READY.json')
        write(root/'GPU_READY.json', gpu_ready)
        while hub.control is None:
            gate(); require(converter.poll() is None, 'JOINT_CONVERTER_EXITED'); time.sleep(.02)
        control.prepared()
        evidence = JointCameraEvidence(Journal(root/'pc', dict(role='PC', run_id=scope['run_id'], admission='PENDING_PS_AUDIT')), scope['max_steps'])
        # One authenticated START, followed immediately by ONE neural connection.
        armed = control.start(gpu_ready, min(1500, datetime.fromisoformat(scope['end_utc']).timestamp()-time.time()))
        evidence.json('ARMED.json', armed)
        endpoint = hardware['endpoint']
        client = c.wire.Client(endpoint['host'], endpoint['port'], observer=evidence.observe)
        att = client.attestation
        require(att['boot_id'] == hardware['boot_id'] and att['server_session'] == hardware['server_session']
                and att['bit_sha256'] == c.wire.BIT_SHA and att['hwh_sha256'] == c.wire.HWH_SHA, 'JOINT_ATTESTATION_CHANGED')
        identity = dict(run_id=scope['run_id'], session_id=scope['session_id'], comparison_id=scope['comparison_id'],
            condition_id='CURRENT_CAMERA', max_steps=scope['max_steps'], model=scope['model'], mapping_sha256=c.mapping_sha,
            hardware=dict(ASID=client.asid.hex(), boot_id=att['boot_id'], server_session=att['server_session'],
                bit_sha256=c.wire.BIT_SHA, hwh_sha256=c.wire.HWH_SHA))
        def publication(full):
            tensor = torch.as_tensor(full.copy(), device='cuda', dtype=torch.float32)
            torch.cuda.synchronize()
            require(np.array_equal(tensor.detach().cpu().numpy(), full), 'JOINT_GPU_STAGING_COPY')
            return tensor
        engine = CameraJointEngine(c, client,
            lambda old, frame, k: producer.produce(old, torch.as_tensor(frame.copy(), device='cuda'), run_id=scope['run_id'], step_id=k, condition_id='CURRENT_CAMERA'),
            lambda full: decoder.decode(full[None,None], chunk_frames=1)[0,0], evidence, identity, gate,
            publication, lambda tensor: tensor.detach().cpu().numpy(), check, execution_kind=LIVE)
        hub.identity = identity
        engine.progress = hub.update_progress
        first_input = None
        while hub.committed < scope['max_steps']:
            if hub.stopping or (root/'STOP_REQUEST.json').exists():
                reason = 'USER_STOP'; break
            gate(); require(converter.poll() is None, 'JOINT_CONVERTER_EXITED')
            item = hub.inputs.freeze_for_step()
            if item is None:
                require(time.monotonic()-began < scope['max_worker_s'], 'JOINT_FIRST_INPUT_TIMEOUT'); time.sleep(.01); continue
            if first_input is None: first_input = time.monotonic()
            if time.monotonic()-first_input >= scope['capture_duration_s']:
                reason = 'CAPTURE_WINDOW_COMPLETE'; break
            require(item['conversion']['dependencies_sha256'] == session['camera_dependencies_sha256'], 'JOINT_CONVERTER_DEPENDENCIES')
            inflight = True
            try: packet = engine.step(item)
            finally: inflight = False
            if hub.stopping:
                hub.committed = engine.barrier.state_token
                reason = 'USER_STOP'; break
            hub.publish(packet)
        else:
            reason = 'STEP_LIMIT_COMPLETE'
        require(producer.calls == hub.committed and producer.native_H_update_count == 0, 'JOINT_GPU_PRODUCTION_COUNTS')
        producer.check_unchanged(); decoder.assert_weights_unchanged()
        # Stop new acquisition before authenticated bounded-window finish.
        hub.stopping = True
        hub.state = 'STOPPING'
        closed_path=root/'camera_capture.json'
        wait_until=time.monotonic()+5
        while not closed_path.exists() and time.monotonic()<wait_until:time.sleep(.02)
        require(closed_path.exists(), 'JOINT_SOURCE_CLOSE_NOT_CONFIRMED')
        closed=load(closed_path)
        require(closed['run_id']==scope['run_id'] and closed['closed'] is True and not closed['error'], 'JOINT_SOURCE_CLOSE_FAILED')
        evidence.json('source_closed.json', closed)
        require(engine.barrier.phase == 'READY' and engine.barrier.pending is None, 'JOINT_FINISH_INFLIGHT')
        ending = control.finish(hub.committed, engine.barrier._visible[2].hex(), engine.barrier._visible[3].hex(), reason)
        evidence.json('PS_FINISH.json', ending)
        write(root/'PS_FINISH.json', ending)
        write(root/'result.json', dict(status='STOPPED_PENDING_PS_AUDIT', reason=reason, run_id=scope['run_id'],
            committed_steps=hub.committed, input_policy=hub.inputs.status(), numerical_profile=scope['numerical_profile'],
            native_H_GPU_updates=producer.native_H_update_count, whole_run_acceptance='PENDING', REALTIME_STREAM_PASS='NOT_CLAIMED'))
    except BaseException as error:
        reason = str(error); hub.revoke(error)
        write(root/'result.json', dict(status='FAILED_OR_IN_DOUBT', error=reason, committed_steps=hub.committed,
            coordinator_state_token=engine.barrier.state_token if engine else 0,
            phase=engine.barrier.phase if engine else None, PL_proven_global_ids=[], automatic_retry=False))
        raise
    finally:
        hub.stopping = True; hub.packet = None
        write(root/'CONVERTER_STOP_REQUEST.json', dict(reason=reason))
        errors = []
        cuda_synchronized = lease_closed = False
        try:
            if engine: engine.close(reason)
            elif client: client.close()
        except Exception as error: errors.append(str(error))
        if converter:
            try: converter.wait(4)
            except subprocess.TimeoutExpired:
                converter.terminate(); converter.wait(3)  # Exact owned CPU-only converter.
        if log: log.close()
        if torch:
            try: torch.cuda.synchronize(); cuda_synchronized=True
            except Exception as error: errors.append(str(error))
        if handle:
            try: handle.close(); lease_closed=True
            except Exception as error: errors.append(str(error))
        if monitor: monitor.close()
        hub.stopped = True; hub.state = 'STOPPED_PENDING_PS_AUDIT' if hub.error is None else 'FAILED'
        if rpc: rpc.close()
        write(root/'worker_exit.json', dict(run_id=scope['run_id'], GPU_inflight_waited=cuda_synchronized, lease_closed=lease_closed,
            cleanup_errors=errors, committed_steps=hub.committed, reason=reason, whole_run_acceptance='PENDING'))
        files = ('scope.json','session.json','GPU_READY.json','PS_FINISH.json','result.json','worker_exit.json','pc/evidence.fvej')
        write(root/'manifest.json', dict(run_id=scope['run_id'], files={n:sha(root/n) for n in files if (root/n).exists()},
            evidence_level='PC_CAPTURE_REQUIRES_NEW_CAMERA_PS_AUDIT', whole_run_acceptance='PENDING'))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', required=True)
    args=p.parse_args()
    try:run(args.root)
    except BaseException as error:
        failed_root=host_path(args.root).resolve()
        if failed_root.parent==(HERE/'runtime/joint').resolve() and failed_root.exists():
            write(failed_root/'worker_start_failure.json',dict(status='FAILED',error=str(error),utc=utc(),whole_run_acceptance='NOT_AVAILABLE'))
        raise

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
from joint_diagnostics import JointDiagnostics,TimedJournal,measured_sync


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
    require(scope.get('runtime_audit_policy')=='LOADED_STATIC_START_END_HASH/v1',
            'NEW_CAMERA_SCOPE_REQUIRED_FOR_STREAMLINED_WORKER')
    reference_policy=scope.get('validation_policy','SAME_OLD_CPU_INLINE')
    diagnostics=JointDiagnostics('WSL_joint_worker')
    from hybrid_full485 import Full485Contract
    from hybrid_gpu import GPUCandidates
    from joint_camera_engine import CameraJointEngine, JointCameraEvidence
    from joint_camera_runtime import JointCameraHub
    from stream_transport import LocalRPC, AuditMonitor
    from joint_camera_control import require_camera_service, board_client, CameraHardwareControl
    from joint_camera_finish import FinishWindowBudget, finish_camera_window
    c, reg = Full485Contract(), Registry()
    validate_scope(scope, c)
    hardware = load(root/'hardware_handoff.json')
    hardware_sha=session.get('hardware_handoff_sha256',scope.get('hardware_handoff_sha256'))
    require(hardware_sha and sha(root/'hardware_handoff.json') == hardware_sha, 'JOINT_HARDWARE_HANDOFF_CHANGED')
    require_camera_service(hardware, scope)
    control = CameraHardwareControl(board_client(hardware), hardware, scope, session['scope_sha256'])
    pc_guard=None
    if hardware.get('clock_policy'):
        from joint_camera_preparation import PCClockClient
        pc_guard=PCClockClient(hardware,scope,session['scope_sha256'],diagnostics=diagnostics)
        diagnostics.call('startup.PC_clock_HTTP',pc_guard.check)
    # Authenticated readiness/capabilities BEFORE acquiring or importing CUDA.
    # Old fixed485 services are deliberately incompatible and fail here.
    diagnostics.call('startup.prepared_status',control.prepared)
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
    native_journal = tuned_socket = None
    reason = 'FAILED_BEFORE_START'
    finish_budget = FinishWindowBudget()
    inflight = False
    from joint_runtime_audit import prepare_runtime_files
    file_guard=prepare_runtime_files(root,scope,scope_sha,session,hardware_sha,c,reg,diagnostics=diagnostics)
    quarantine=runner.own_path('runtime','RESOURCE_QUARANTINE.json')
    def audit_checks():
        # Remote clock liveness is bounded by the existing 2s monitor freshness;
        # it is no longer seven blocking HTTP transactions per neural step.
        if pc_guard:diagnostics.call('audit.PC_clock_HTTP',pc_guard.check)
        validate_scope(scope)
        file_guard.check()
        ctrl = load(root/'controller.json')
        require(ctrl['session_id'] == scope['session_id'] and time.time()-ctrl['unix_time'] < 10, 'JOINT_CONTROLLER_LOST')
        require(not quarantine.exists(), 'RESOURCE_QUARANTINE')
    def audit():diagnostics.call('audit.total_inclusive',audit_checks)
    def gate():
        diagnostics.call('gate.scope_time',validate_scope,scope)
        require(time.monotonic()-began < scope['max_worker_s'], 'JOINT_WORKER_DEADLINE')
        if diagnostics.call('gate.error_file_exists',(root/'ERROR_REQUEST.json').exists):
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
        producer = GPUCandidates(reg, c, oracle, torch, diagnostics)
        check = current_reference(reg,c,torch) if reference_policy=='SAME_OLD_CPU_INLINE' else None
        hub.gpu_ready = True; hub.state = 'WAITING_CAMERA_SELECTION'
        gpu_ready = dict(status='GPU_READY', run_id=scope['run_id'], session_id=scope['session_id'], server_session=scope['server_session'],
            scope_sha256=scope_sha, native_H_updates=0, device=torch.cuda.get_device_name(),
            validation_policy=reference_policy,runtime_audit_policy=scope['runtime_audit_policy'],
            neural_transport_policy=scope.get('neural_transport_policy','PINNED_CLIENT_DEFAULT'),
            journal_storage_policy=scope.get('journal_storage_policy','DIRECT_SESSION/v1'),
            pc_commit_journal_policy=scope.get('pc_commit_journal_policy','IMMEDIATE/v1'),
            board_connected=False, waiting_for='BOARD_READY.json')
        write(root/'GPU_READY.json', gpu_ready)
        while hub.control is None:
            gate(); require(converter.poll() is None, 'JOINT_CONVERTER_EXITED'); time.sleep(.02)
        # Camera opening/first official conversion can take several seconds.
        # Do not consume the board's 5s neural-idle window during that work.
        while hub.inputs.freeze_for_step() is None:
            gate();require(converter.poll() is None,'JOINT_CONVERTER_EXITED');time.sleep(.01)
        control.prepared()
        journal_directory=root/'pc'
        if scope.get('journal_storage_policy')=='WSL_NATIVE_DURABLE_EXPORT/v1':
            from joint_camera_io import NativePCJournal
            native_journal=NativePCJournal(root,scope['run_id'],scope['session_id'],diagnostics=diagnostics)
            journal_directory=native_journal.directory
        writer=Journal(journal_directory,dict(role='PC',run_id=scope['run_id'],admission='PENDING_PS_AUDIT'),sync=measured_sync(diagnostics))
        if native_journal:native_journal.attach(writer)
        evidence=JointCameraEvidence(TimedJournal(writer,diagnostics),scope['max_steps'],diagnostics,
            commit_policy=scope.get('pc_commit_journal_policy','IMMEDIATE/v1'),wire=c.wire)
        # One authenticated START, followed immediately by ONE neural connection.
        armed = control.start(gpu_ready, min(1500, datetime.fromisoformat(scope['end_utc']).timestamp()-time.time()))
        evidence.json('ARMED.json', armed)
        endpoint = hardware['endpoint']
        finish_budget.exchange_started()
        client = c.wire.Client(endpoint['host'], endpoint['port'], observer=evidence.observe)
        if scope.get('neural_transport_policy')=='TCP_NODELAY_QUICKACK_WHEN_SUPPORTED/v1':
            from joint_camera_io import tune_client
            tuned_socket=tune_client(client,diagnostics)
        att = client.attestation
        require(att['boot_id'] == hardware['boot_id'] and att['server_session'] == hardware['server_session']
                and att['bit_sha256'] == c.wire.BIT_SHA and att['hwh_sha256'] == c.wire.HWH_SHA, 'JOINT_ATTESTATION_CHANGED')
        identity = dict(run_id=scope['run_id'], session_id=scope['session_id'], comparison_id=scope['comparison_id'],
            condition_id='CURRENT_CAMERA', max_steps=scope['max_steps'], model=scope['model'], mapping_sha256=c.mapping_sha,
            validation_policy=reference_policy,
            hardware=dict(ASID=client.asid.hex(), boot_id=att['boot_id'], server_session=att['server_session'],
                bit_sha256=c.wire.BIT_SHA, hwh_sha256=c.wire.HWH_SHA))
        def publication(full):
            tensor=diagnostics.call('state.stage_H2D',torch.as_tensor,full.copy(),device='cuda',dtype=torch.float32)
            diagnostics.call('CUDA_wait_after_full_stage',torch.cuda.synchronize)
            checked=diagnostics.call('state.stage_D2H_check',lambda:tensor.detach().cpu().numpy())
            require(np.array_equal(checked, full), 'JOINT_GPU_STAGING_COPY')
            return tensor
        engine = CameraJointEngine(c, client,
            lambda old, frame, k: producer.produce(old, torch.as_tensor(frame.copy(), device='cuda'), run_id=scope['run_id'], step_id=k, condition_id='CURRENT_CAMERA'),
            lambda full: decoder.decode(full[None,None], chunk_frames=1)[0,0], evidence, identity, gate,
            publication, lambda tensor: tensor.detach().cpu().numpy(), check, execution_kind=LIVE,diagnostics=diagnostics)
        hub.identity = identity
        engine.progress = hub.update_progress
        engine.exchange_started = finish_budget.exchange_started
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
            diagnostics.call('display.mailbox_publish',hub.publish,packet)
        else:
            reason = 'STEP_LIMIT_COMPLETE'
        require(producer.calls == hub.committed and producer.native_H_update_count == 0, 'JOINT_GPU_PRODUCTION_COUNTS')
        # The owned CPU converter may have a completed frame in flight when
        # input admission closes; make that expected shutdown explicit first.
        write(root/'CONVERTER_STOP_REQUEST.json', dict(reason=reason))
        ending = finish_camera_window(finish_budget, root/'camera_capture.json', hub, engine.barrier, evidence, control, reason)
        evidence.json('PS_FINISH.json', ending)
        write(root/'PS_FINISH.json', ending)
        # Preserve final checks, after the idle-sensitive authenticated close.
        # A failure still prevents a successful PC result.
        producer.check_unchanged(); decoder.assert_weights_unchanged()
        # The board's normal finish is already confirmed before this full hash.
        # Pause the background auditor to avoid overlapping the final file pass.
        monitor.close();monitor.check();monitor=None
        write(root/'runtime_validation.json',dict(run_id=scope['run_id'],validation_policy=reference_policy,
            independent_CPU_reference='PENDING_OFFLINE_AUDIT' if check is None else 'CHECKED_INLINE',
            file_audit=file_guard.final(),clock_liveness_max_age_s=2,whole_run_acceptance='PENDING'))
        if engine.barrier.state_token:
            write(root/'final_snapshot.json', packet)
        write(root/'result.json', dict(status='STOPPED_PENDING_PS_AUDIT', reason=reason, run_id=scope['run_id'],
            committed_steps=hub.committed, input_policy=hub.inputs.status(), numerical_profile=scope['numerical_profile'],
            validation_policy=reference_policy,independent_CPU_reference='PENDING_OFFLINE_AUDIT' if check is None else 'CHECKED_INLINE',
            native_H_GPU_updates=producer.native_H_update_count, whole_run_acceptance='PENDING', REALTIME_STREAM_PASS='NOT_CLAIMED'))
    except BaseException as error:
        reason = str(error); hub.revoke(error)
        if evidence:evidence.failed=True
        write(root/'result.json', dict(status='FAILED_OR_IN_DOUBT', error=reason, committed_steps=hub.committed,
            coordinator_state_token=engine.barrier.state_token if engine else 0,
            phase=engine.barrier.phase if engine else None, PL_proven_global_ids=[], automatic_retry=False))
        raise
    finally:
        hub.stopping = True; hub.packet = None
        write(root/'CONVERTER_STOP_REQUEST.json', dict(reason=reason))
        errors = []
        try: write(root/'finish_budget.json', finish_budget.summary())
        except Exception as error: errors.append('FINISH_BUDGET_RECORD: '+str(error))
        cuda_synchronized = lease_closed = False
        try:
            if engine: engine.close(reason)
            else:
                try:
                    if client:client.close()
                finally:
                    if evidence:evidence.close(reason)
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
        if pc_guard:
            try:diagnostics.call('clock.close',pc_guard.close)
            except Exception as error:errors.append('PC_CLOCK_CLOSE: '+str(error))
        # Board close and GPU synchronization/release precede cross-filesystem
        # export. The native journal remains the durable source at every step.
        if native_journal and native_journal.writer is not None:
            try:write(root/'PC_JOURNAL_EXPORT.json',native_journal.export_closed())
            except Exception as error:
                errors.append('PC_JOURNAL_EXPORT: '+str(error))
                write(root/'PC_JOURNAL_EXPORT_ERROR.json',dict(error=str(error),**native_journal.identity))
        if tuned_socket:
            try:write(root/'transport_profile.json',tuned_socket.summary())
            except Exception as error:errors.append('TRANSPORT_PROFILE: '+str(error))
        hub.stopped = True; hub.state = 'STOPPED_PENDING_PS_AUDIT' if hub.error is None else 'FAILED'
        if rpc: rpc.close()
        diagnostic_error=None
        try:diagnostics.save(root/'host_diagnostics.json',scope['session_id'],scope['run_id'])
        except Exception as error:diagnostic_error=str(error)
        write(root/'worker_exit.json', dict(run_id=scope['run_id'], GPU_inflight_waited=cuda_synchronized, lease_closed=lease_closed,
            cleanup_errors=errors,committed_steps=hub.committed,reason=reason,whole_run_acceptance='PENDING',diagnostic_error=diagnostic_error))
        files = ('scope.json','session.json','GPU_READY.json','PS_FINISH.json','result.json','worker_exit.json','finish_budget.json','pc/evidence.fvej','final_snapshot.json','host_diagnostics.json','runtime_validation.json','PC_JOURNAL_LOCATION.json','PC_JOURNAL_EXPORT.json','PC_JOURNAL_EXPORT_ERROR.json','transport_profile.json')
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

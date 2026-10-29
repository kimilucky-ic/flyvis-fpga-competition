"""Authenticated input/snapshot hub for ONE camera joint worker; no device imports."""
import copy
import threading
import time

from live_protocol import require
from joint_camera_protocol import LatestCameraInput, validate_snapshot


class JointCameraHub:
    def init__(self, scope, spatial):
        self.scope, self.spatial = scope, spatial
        self.inputs = LatestCameraInput(scope['run_id'])
        self.lock = threading.RLock()
        self.changed = threading.Condition(self.lock)
        self.control = None
        self.identity = None
        self.packet = None
        self.error = None
        self.state = 'PREPARING_GPU_AND_CONVERTER'
        self.converter_ready = self.gpu_ready = self.stopping = self.stopped = False
        self.bridge_at = self.renderer_at = time.monotonic()
        self.committed = 0
        self.progress = None
        self.capture_close_requested = False

    def update_progress(self, phase, step):
        with self.changed:
            self.progress = dict(phase=phase, step_id=step, evidence='HOST_CONTROL_MILESTONE_NOT_PL_BUSY_REGISTER')

    def check(self, allow_stop=False):
        require(allow_stop or not self.stopping, 'JOINT_STOP_REQUESTED')
        require(self.error is None, 'JOINT_REVOKED ' + str(self.error))
        if self.control and not self.stopping:
            require(time.monotonic() - self.bridge_at < 5, 'JOINT_GUI_DISCONNECTED')
            require(self.scope.get('scientific_input') or time.monotonic() - self.renderer_at < 5, 'JOINT_CONVERTER_DISCONNECTED')

    def revoke(self, error):
        with self.changed:
            self.error, self.packet, self.state, self.stopping = str(error), None, 'FAILED', True
            self.changed.notify_all()

    def begin_stop(self):
        with self.changed:
            self.stopping, self.packet, self.state = True, None, 'STOPPING'
            self.changed.notify_all()

    def publish(self, packet):
        with self.changed:
            self.check()
            require(self.identity is not None, 'JOINT_NOT_ATTESTED')
            validate_snapshot(packet, self.identity, self.spatial)
            require(packet['step_id'] == self.committed, 'JOINT_PUBLICATION_ORDER')
            if self.packet:
                require(packet['transaction']['old_full_sha256'] == self.packet['transaction']['full_after_sha256'], 'JOINT_FEEDBACK_CHAIN')
            self.packet = copy.deepcopy(packet)
            self.committed += 1
            self.state = 'RUNNING_ACK_DURABLE_PENDING_AUDIT'
            self.changed.notify_all()

    def status(self):
        return dict(status=self.state, session_id=self.scope['session_id'], run_id=self.scope['run_id'],
            result_valid=bool(self.packet) and self.error is None and not self.stopping,
            ready_for_camera=self.gpu_ready and self.converter_ready and not self.stopping and self.error is None,
            renderer_ready=self.converter_ready, stop_acknowledged=self.stopped, error=self.error,
            stopping=self.stopping,
            identity=self.identity, committed_steps=self.committed, capture=self.inputs.status(),
            whole_run_acceptance='PENDING', FPGA_status='ATTESTED_SESSION' if self.identity and not self.stopped else 'NOT_CONNECTED',
            progress=self.progress,
            runtime_policy=self.scope.get('runtime_policy'),
            live_response_hz=self.scope.get('live_response_hz'),
            recording_required_before_camera=self.scope.get('recording_required_before_camera',False),
            capture_close_requested=self.capture_close_requested,
            REALTIME_STREAM_PASS='NOT_CLAIMED')

    def dispatch(self, role, op, body):
        with self.changed:
            if role == 'bridge':
                self.bridge_at = time.monotonic()
            elif role == 'renderer':
                self.renderer_at = time.monotonic()
            else:
                raise ValueError('JOINT_RPC_ROLE')
            if op == 'status':
                return self.status()
            if op == 'stop':
                require(role == 'bridge', 'JOINT_STOP_ROLE')
                self.begin_stop()
                return self.status()
            if op == 'latest' and self.stopping:
                return dict(status=self.status(), packet=None)
            self.check()
            if op == 'ready':
                require(role == 'renderer', 'JOINT_CONVERTER_ROLE')
                self.converter_ready = True
                return self.status()
            if op == 'start':
                require(role == 'bridge' and self.control is None and self.gpu_ready and self.converter_ready, 'JOINT_NOT_READY_OR_ALREADY_STARTED')
                require(set(body) == {'run_id', 'session_id', 'camera_id'} and body['run_id'] == self.scope['run_id']
                        and body['session_id'] == self.scope['session_id'] and body['camera_id'] == self.scope['camera_id'], 'JOINT_START_IDENTITY')
                self.control = copy.deepcopy(body)
                self.state = 'CONNECTING_PREPARED_HARDWARE'
                return self.status()
            if op == 'input':
                require(role == 'bridge' and self.control is not None, 'JOINT_INPUT_BEFORE_START')
                self.inputs.receive(body)
                self.changed.notify_all()
                return dict(accepted_sequence=body['source']['sequence'])
            if op == 'raw':
                require(role == 'renderer', 'JOINT_CONVERTER_ROLE')
                self.changed.wait_for(lambda: self.stopping or self.error or self.inputs.raw is not None, .1)
                self.check()
                return self.inputs.take_raw()
            if op == 'converted':
                require(role == 'renderer', 'JOINT_CONVERTER_ROLE')
                self.inputs.accept_conversion(body)
                self.changed.notify_all()
                return True
            if op == 'latest':
                require(role == 'bridge', 'JOINT_DISPLAY_ROLE')
                after = (body or {}).get('after_serial', 0)
                require(type(after) is int and after >= 0, 'JOINT_LATEST_BOUND')
                self.changed.wait_for(lambda: self.stopping or self.error or (self.packet and self.packet['serial'] > after), .1)
                return dict(status=self.status(), packet=self.packet if self.packet and self.packet['serial'] > after else None)
            raise ValueError('JOINT_UNKNOWN_OPERATION')

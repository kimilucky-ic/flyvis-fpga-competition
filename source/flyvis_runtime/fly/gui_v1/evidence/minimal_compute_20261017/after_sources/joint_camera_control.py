"""Thin authenticated-control adapter. Reuses ⑦ BoardClient; never initializes PL."""
import importlib.util
from pathlib import Path
import sys

from live_protocol import canonical, host_path, require, sha


def require_camera_service(handoff, scope):
    require(handoff.get('schema') == 'flyvis-camera-hardware-handoff/v1'
            and handoff.get('status') == 'PREPARED_FOR_THIS_CAMERA_RUN', 'CAMERA_HARDWARE_HANDOFF_NOT_AVAILABLE')
    cap = handoff.get('capabilities', {})
    require(handoff.get('ps_durability_policy','PS_FOUR_WIRE_BARRIERS/v1')==scope.get('ps_durability_policy','PS_FOUR_WIRE_BARRIERS/v1'),
            'CAMERA_PS_DURABILITY_POLICY_MISMATCH')
    if scope.get('ps_durability_policy')=='PS_COMMIT_ACK_DURABLE_TWO_BARRIERS/v1':
        require(handoff.get('ps_evidence_adapter_sha256')==scope.get('ps_evidence_adapter_sha256'),'CAMERA_PS_ADAPTER_MISMATCH')
    require(cap.get('camera_joint_contract') == 'flyvis-camera-joint/v1'
            and cap.get('normal_finish') == 'finish_window/v1'
            and cap.get('max_steps') == scope['max_steps'], 'CAMERA_NORMAL_FINISH_NOT_IMPLEMENTED')
    require(all(handoff.get(k) == scope.get(k) for k in ('run_id', 'server_session', 'boot_id')), 'CAMERA_HARDWARE_SCOPE')
    require(handoff['bit_sha256'] == scope['bit_sha256'] and handoff['hwh_sha256'] == scope['hwh_sha256'], 'CAMERA_HARDWARE_IMAGE')
    require(handoff['initial_full_digest'] == scope['initial_full_digest'] and handoff['initial_H_sha256'] == scope['initial_H_sha256']
            and handoff['mapping_sha256'] == scope['mapping_sha256'], 'CAMERA_HARDWARE_INITIAL_MAP')
    for endpoint in ('endpoint', 'control_endpoint'):
        e = handoff[endpoint]
        require(isinstance(e['host'], str) and e['host'] and type(e['port']) is int and 1 <= e['port'] <= 65535, 'CAMERA_HARDWARE_ENDPOINT')
    config = handoff['control_config']
    require(all(config[k] == handoff[k] for k in ('run_id', 'server_session', 'plan_sha256'))
            and len(bytes.fromhex(config['control_key'])) == 32, 'CAMERA_CONTROL_BINDING')
    return handoff


def hardware_module(handoff, member):
    """Load the complete explicitly pinned helper package without string patches."""
    package = host_path(handoff['software_package']).resolve()
    package_dir = package / handoff['control_package']
    required = {handoff['control_package'] + '/' + n for n in ('init__.py','control_client.py','control2.py')}
    require(required <= handoff['software_sha256'].keys(), 'CAMERA_CONTROL_SOURCE_PINS')
    for relative, expected in handoff['software_sha256'].items():
        path = (package / relative).resolve()
        require(path.is_relative_to(package) and sha(path) == expected, 'CAMERA_HARDWARE_SOURCE_CHANGED')
    # Only approved helper files are package members reachable by these imports.
    name = '_flyvis_camera_hardware_' + canonical([str(package),handoff['software_sha256']])[:16]
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, package_dir/'init__.py', submodule_search_locations=[str(package_dir)])
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    require(handoff['control_package']+'/'+member+'.py' in handoff['software_sha256'], 'CAMERA_HELPER_NOT_PINNED')
    sub = name + '.' + member
    if sub not in sys.modules:
        spec = importlib.util.spec_from_file_location(sub, package_dir/(member+'.py'))
        module = importlib.util.module_from_spec(spec)
        sys.modules[sub] = module
        spec.loader.exec_module(module)
    return sys.modules[sub]


def board_client(handoff):
    ep = handoff['control_endpoint']
    return hardware_module(handoff,'control_client').BoardClient(ep['host'], ep['port'], handoff['control_config'])


class CameraHardwareControl:
    def init__(self, client, handoff, scope, scope_sha):
        self.client, self.handoff, self.scope, self.scope_sha = client, handoff, scope, scope_sha
        self.armed = self.finished = self.start_attempted = False
        self.identity = dict(run_id=scope['run_id'], server_session=scope['server_session'], boot_id=scope['boot_id'],
            scope_sha256=scope_sha, listener_id=handoff['listener_id'])

    def check_status(self, status, *, clean=False):
        require(all(status[k] == self.handoff[k] for k in ('run_id','server_session','boot_id','plan_sha256','bit_sha256','hwh_sha256')), 'CAMERA_CONTROL_STATUS_IDENTITY')
        require(status['boot_id'] == self.scope['boot_id'] and not status.get('error')
                and not status.get('poisoned') and status.get('service_alive') is True, 'CAMERA_SERVICE_NOT_READY')
        require(status.get('camera_joint_contract') == 'flyvis-camera-joint/v1'
                and status.get('normal_finish') == 'finish_window/v1', 'CAMERA_SERVICE_CAPABILITY')
        if clean:
            require(status['state'] == 'BOARD_PREPARED' and status['requests'] == status['commits'] == 0
                    and status['pending'] is False and status['neural_connections'] == 0, 'CAMERA_SERVICE_ALREADY_USED')
        return status

    def prepared(self):
        return self.check_status(self.client.request('/status'), clean=True)

    def start(self, gpu_ready, remaining_s):
        require(not self.start_attempted and not self.finished, 'CAMERA_CONTROL_START_CONSUMED')
        self.start_attempted = True
        require(0 < remaining_s <= 1500, 'CAMERA_CONTROL_DEADLINE')
        require(gpu_ready.get('status')=='GPU_READY' and gpu_ready.get('board_connected') is False
                and gpu_ready.get('waiting_for')=='BOARD_READY.json'
                and all(gpu_ready.get(k)==self.identity[k] for k in ('run_id','server_session','scope_sha256')), 'CAMERA_CONTROL_GPU_READY')
        response = self.client.request('/start', dict(identity=self.identity, gpu_ready=gpu_ready, scope_remaining_s=remaining_s))
        self.check_status(response)
        require(response['state'] == 'ARMED' and response['identity'] == self.identity, 'CAMERA_CONTROL_NOT_ARMED')
        self.armed = True
        return response

    def finish(self, completed, commit_sha, txn, reason):
        require(self.armed and not self.finished and reason in ('STEP_LIMIT_COMPLETE','CAPTURE_WINDOW_COMPLETE','USER_STOP'), 'CAMERA_FINISH_PHASE')
        require(type(completed) is int and 0 <= completed <= self.scope['max_steps']
                and (completed>0 or self.scope.get('allow_zero_step_cancel') is True), 'CAMERA_FINISH_COUNT')
        self.finished = True  # Ambiguous control failure must never cause a retry.
        response = self.client.request('/finish_window', dict(identity=self.identity, completed_steps=completed,
            last_unified_commit_sha256=commit_sha, last_txn=txn, reason=reason, source_closed=True))
        require(response['state'] == 'FINISHED_PENDING_AUDIT' and response['identity'] == self.identity
                and response['completed_steps'] == completed and response['last_unified_commit_sha256'] == commit_sha
                and response['last_txn'] == txn and response['capture_closed'] is True and response.get('error') is None
                and response['requests']==response['commits']==completed and response['pending'] is False
                and len(response['PS_capture_sha256']) == 64, 'CAMERA_FINISH_ACK_MISMATCH')
        return response

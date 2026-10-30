"""Camera joint identity/time contract. Import never acquires a device or socket."""
import base64
import copy
import hashlib
import re
import threading
import time
from datetime import datetime, timezone

import numpy as np
from live_protocol import canonical, require

DT = .005
PROFILE = 'H_A3R1_Q24_R_ORIGINAL_FP32'
LIVE = 'LIVE_CAMERA_GPU_FPGA_PENDING_AUDIT'
TEST = 'CPU_PROTOCOL_REPLAY'
POLICY = 'LATEST_CONVERTED_AT_STEP_START_COMMIT_DRIVEN'
CONVERSION_RECEIPT = 'flyvis-camera-conversion-receipt/v1'


def conversion_receipt(frame):
    """Return receptors and source identity; the hub already owns the PNG."""
    return dict(schema=CONVERSION_RECEIPT,source=frame['source'],values=frame['values'],conversion=frame['conversion'])


def digest(data):
    return hashlib.sha256(data).hexdigest()


def frame_check(item, run_id, source_kind):
    s = item['source']
    require(s['run_id'] == run_id and s['source_kind'] == source_kind, 'JOINT_SOURCE_RUN')
    require(type(s['sequence']) is int and s['sequence'] >= 0, 'JOINT_SOURCE_SEQUENCE')
    require(type(s['received_monotonic_ns']) is int and s['received_monotonic_ns'] > 0, 'JOINT_SOURCE_CLOCK')
    require(np.isfinite(s['relative_s']) and s['relative_s'] >= 0, 'JOINT_SOURCE_TIME')
    require(s['timestamp_kind'] == 'Windows_receipt_not_sensor', 'JOINT_CLOCK_DOMAIN')
    png = base64.b64decode(item['png'], validate=True)
    require(0 < len(png) <= 2_500_000 and digest(png) == s['png_sha256'], 'JOINT_SOURCE_PIXELS')
    if 'values' in item:
        x = np.asarray(item['values'], dtype='<f4')
        require(x.shape == (721,) and np.isfinite(x).all() and np.all((x >= 0) & (x <= 1)), 'JOINT_BOXEYE_VALUES')
        require(digest(x.tobytes()) == s['hex_values_sha256'], 'JOINT_BOXEYE_SHA')
        require(item['conversion']['backend'] == 'ORIGINAL_PREPARED_CAMERA_INPUT_BOXEYE_CPU', 'JOINT_OFFICIAL_CONVERTER')
    return s


def validate_scope(scope, contract=None, now=None):
    require(scope.get('schema') == 'flyvis-camera-joint-scope/v1', 'JOINT_SCOPE_SCHEMA')
    require(scope.get('status') == 'APPROVED_BY_HUMAN' and scope.get('human_authorization_reference'), 'JOINT_NOT_AUTHORIZED')
    for key in ('run_id', 'session_id', 'gpu_lease_id'):
        require(isinstance(scope.get(key), str) and re.fullmatch('[a-f0-9]{32}', scope[key]), 'JOINT_RUN_ID')
    require(scope.get('source_kind') == 'real_windows_camera' and scope.get('condition_id') == 'CURRENT_CAMERA', 'JOINT_CAMERA_SCOPE')
    require(type(scope.get('camera_id')) is int and 0 <= scope['camera_id'] <= 15, 'JOINT_CAMERA_ID')
    require(scope.get('numerical_profile') == PROFILE and scope.get('dt_s') == DT and scope.get('input_policy') == POLICY, 'JOINT_NUMERIC_TIME_PROFILE')
    require(type(scope.get('max_steps')) is int and 1 <= scope['max_steps'] <= 60000, 'JOINT_STEP_BOUND')
    require(type(scope.get('capture_duration_s')) is int and 1 <= scope['capture_duration_s'] <= 300, 'JOINT_CAPTURE_BOUND')
    require(type(scope.get('max_worker_s')) is int and 30 <= scope['max_worker_s'] <= 1800, 'JOINT_WORKER_BOUND')
    if scope.get('clock_wait_profile'):
        from joint_camera_clock_wait import PROFILE as WAIT_PROFILE,WAIT_S
        require(scope['clock_wait_profile']==WAIT_PROFILE and scope.get('clock_wait_s')==WAIT_S
            and scope['max_worker_s']==300 and scope['max_steps']<=(100 if scope.get('live_response_hz')==5 else 32)
            and isinstance(scope.get('clock_wait_adapter_sha256'),str)
            and re.fullmatch('[a-f0-9]{64}',scope['clock_wait_adapter_sha256'])
            and scope.get('clock_wait_adapter_sha256')==scope.get('source_sha256',{}).get('joint_camera_clock_wait.py'),
            'JOINT_CLOCK_WAIT_PROFILE')
    require(scope.get('automatic_retry') is False and scope.get('native_H_GPU_updates') == 0, 'JOINT_NO_RETRY_OR_NATIVE_H')
    require(scope.get('validation_policy','SAME_OLD_CPU_INLINE') in ('SAME_OLD_CPU_INLINE','SAME_OLD_CPU_POST_RUN'),'JOINT_REFERENCE_POLICY')
    require(scope.get('runtime_audit_policy','LEGACY_FULL_SHA') in
            ('LEGACY_FULL_SHA','LOADED_STATIC_START_END_HASH/v1'),'JOINT_AUDIT_POLICY')
    require(scope.get('neural_transport_policy','PINNED_CLIENT_DEFAULT') in
            ('PINNED_CLIENT_DEFAULT','TCP_NODELAY_QUICKACK_WHEN_SUPPORTED/v1'),'JOINT_TRANSPORT_POLICY')
    require(scope.get('journal_storage_policy','DIRECT_SESSION/v1') in
            ('DIRECT_SESSION/v1','WSL_NATIVE_DURABLE_EXPORT/v1'),'JOINT_STORAGE_POLICY')
    require(scope.get('pc_commit_journal_policy','IMMEDIATE/v1') in
            ('IMMEDIATE/v1','MERGED_INTENT_BEFORE_SEND/v1','ASYNC_AFTER_ACK/v1'),'JOINT_COMMIT_JOURNAL_POLICY')
    require(scope.get('ps_durability_policy','PS_FOUR_WIRE_BARRIERS/v1') in
            ('PS_FOUR_WIRE_BARRIERS/v1','PS_COMMIT_ACK_DURABLE_TWO_BARRIERS/v1','ASYNC_AFTER_ACK_NO_CRASH_DURABILITY/v1'),'JOINT_PS_DURABILITY_POLICY')
    if scope.get('runtime_policy')=='MINIMAL_COMPUTE_ASYNC_V1':
        if scope.get('live_response_hz') is not None:
            require(type(scope['live_response_hz']) is int and scope['live_response_hz']==5
                and scope.get('display_policy')=='LIVE_LATEST_COMMITTED_STATE_5HZ','JOINT_LIVE5_SCOPE')
        require(scope.get('ps_durability_policy')=='ASYNC_AFTER_ACK_NO_CRASH_DURABILITY/v1'
            and scope.get('recording_required_before_camera') is False
            and scope.get('pc_commit_journal_policy')=='ASYNC_AFTER_ACK/v1','MINIMAL_SYNC_OBSERVER_NOT_ALLOWED')
        for name,field in [('joint_minimal_core.py','minimal_core_sha256'),('joint_minimal_board.py','minimal_board_sha256')]:
            require(scope.get(field)==scope.get('source_sha256',{}).get(name) and isinstance(scope.get(field),str),'MINIMAL_SOURCE_PIN')
    else:
        require(scope.get('live_response_hz') is None,'LIVE5_REQUIRES_MINIMAL_RUNTIME')
        require(scope.get('ps_durability_policy')!='ASYNC_AFTER_ACK_NO_CRASH_DURABILITY/v1'
            and scope.get('pc_commit_journal_policy')!='ASYNC_AFTER_ACK/v1','ASYNC_POLICY_REQUIRES_EXPLICIT_MINIMAL_RUNTIME')
    if scope.get('ps_durability_policy')=='PS_COMMIT_ACK_DURABLE_TWO_BARRIERS/v1':
        require(scope.get('ps_evidence_adapter_sha256')==scope.get('source_sha256',{}).get('ps_commit_evidence.py')
            and isinstance(scope.get('ps_evidence_adapter_sha256'),str)
            and re.fullmatch('[a-f0-9]{64}',scope['ps_evidence_adapter_sha256']),'JOINT_PS_ADAPTER_SOURCE')
    require(scope.get('new_loads') == scope.get('new_resets') == scope.get('new_allocations') == 0, 'JOINT_PREPARED_SERVICE_ONLY')
    begin, end = (datetime.fromisoformat(scope[k]) for k in ('start_utc', 'end_utc'))
    now = now or datetime.now(timezone.utc)
    require(begin.tzinfo and end.tzinfo and begin <= now < end and 0 < (end - begin).total_seconds() <= 1800, 'JOINT_SCOPE_EXPIRED')
    require(bool(scope.get('hardware_handoff_sha256')) != bool(scope.get('hardware_declaration_sha256'))
            and scope.get('source_sha256'), 'JOINT_HANDOFF_PINS')
    if contract is not None:
        require(scope['model'] == contract.registry['model'] and scope['mapping_sha256'] == contract.mapping_sha, 'JOINT_MODEL_MAP')
        require(scope['bit_sha256'] == contract.wire.BIT_SHA and scope['hwh_sha256'] == contract.wire.HWH_SHA, 'JOINT_IMAGE')
        require(scope['tolerance'] == contract.tolerance, 'JOINT_TOLERANCE')
        from hybrid_a3 import module
        hmod = module('camera_joint_initial_identity', contract.paths['h_step'])
        initial, words, _ = contract.initial()
        require(scope['initial_full_digest'] == hmod.array_hash(initial)
                and scope['initial_H_sha256'] == digest(words), 'JOINT_INITIAL_IDENTITY')
    return scope


class LatestCameraInput:
    """Two bounded mailboxes; acquisition/conversion never queue model steps."""
    def init__(self, run_id, source_kind='real_windows_camera'):
        self.run_id, self.kind = run_id, source_kind
        self.lock = threading.RLock()
        self.raw = self.converted = self.inflight = None
        self.last_received = self.last_converted = self.last_selected = -1
        self.last_time = -1.
        self.last_received_ns = 0
        self.dropped_raw = self.coalesced_converted = self.held = 0
        self.compact_receipts = self.elided_png_characters = 0

    def receive(self, item):
        s = frame_check(item, self.run_id, self.kind)
        with self.lock:
            require(s['sequence'] == self.last_received + 1, 'JOINT_CAPTURE_ORDER')
            require(s['relative_s'] > self.last_time and s['received_monotonic_ns'] > self.last_received_ns, 'JOINT_CAPTURE_CLOCK_REVERSED')
            if self.raw is not None:
                self.dropped_raw += 1
            self.raw = copy.deepcopy(item)
            self.last_received = s['sequence']
            self.last_time, self.last_received_ns = s['relative_s'], s['received_monotonic_ns']

    def take_raw(self):
        with self.lock:
            if self.inflight is not None or self.raw is None:
                return None
            self.inflight, self.raw = self.raw, None
            return copy.deepcopy(self.inflight)

    def accept_conversion(self, item):
        with self.lock:
            require(self.inflight is not None, 'JOINT_UNSOLICITED_CONVERSION')
            compact='schema' in item
            if compact:
                require(item.get('schema')==CONVERSION_RECEIPT and set(item)=={'schema','source','values','conversion'},'JOINT_CONVERSION_RECEIPT_SCHEMA')
                item=dict(source=item['source'],values=item['values'],conversion=item['conversion'],png=self.inflight['png'])
            s = frame_check(item, self.run_id, self.kind)
            original = self.inflight['source']
            require(all(s.get(k) == v for k, v in original.items()) and item['png'] == self.inflight['png'], 'JOINT_CONVERTER_SOURCE_CHANGED')
            require(s['sequence'] > self.last_converted, 'JOINT_CONVERSION_ORDER')
            if self.converted is not None and self.converted['source']['sequence'] > self.last_selected:
                self.coalesced_converted += 1
            self.converted = copy.deepcopy(item)
            if compact:
                self.compact_receipts+=1
                self.elided_png_characters+=len(self.inflight['png'])
            self.last_converted = s['sequence']
            self.inflight = None

    def freeze_for_step(self):
        with self.lock:
            if self.converted is None:
                return None
            item = copy.deepcopy(self.converted)
            seq = item['source']['sequence']
            require(seq >= self.last_selected, 'JOINT_INPUT_REVERSED')
            if seq == self.last_selected:
                self.held += 1
            self.last_selected = seq
            return item

    def status(self):
        with self.lock:
            return dict(raw_pending=int(self.raw is not None), conversion_inflight=int(self.inflight is not None),
                        converted_history=int(self.converted is not None), captured=self.last_received + 1,
                        dropped_before_conversion=self.dropped_raw, coalesced_before_selection=self.coalesced_converted,
                        held_steps=self.held, compact_conversion_receipts=self.compact_receipts,
                        elided_return_png_characters=self.elided_png_characters, policy=POLICY)


def validate_snapshot(p, identity, spatial, *, allow_test=False):
    require(p['schema'] == 'flyvis-camera-joint-output/v1', 'JOINT_OUTPUT_SCHEMA')
    require(all(p[k] == identity[k] for k in ('run_id', 'session_id', 'model', 'mapping_sha256', 'hardware')), 'JOINT_OUTPUT_IDENTITY')
    k = p['step_id']
    require(type(k) is int and k >= 0 and p['serial'] == p['state_token'] == k + 1, 'JOINT_OUTPUT_STEP')
    require(p['input_time_s'] == k * DT and p['activity_time_s'] == k * DT + DT, 'JOINT_OUTPUT_TIME')
    require(p['numerical_profile'] == PROFILE and p['temporal_mapping']['policy'] == POLICY, 'JOINT_OUTPUT_PROFILE')
    is_test = p['execution_kind'] == TEST
    require((allow_test and is_test) or p['execution_kind'] == LIVE, 'JOINT_NOT_LIVE_CAMERA')
    require(p['source_kind'] == ('recorded_protocol_fixture' if is_test else 'real_windows_camera'), 'JOINT_SOURCE_KIND')
    item = dict(source=p['source'], png=p['preview_png'], values=p['input_hex'], conversion=p['conversion'])
    frame_check(item, p['run_id'], p['source_kind'])
    s = p['spatial']
    require(s['run_id'] == p['run_id'] and s['step_id'] == k and s['state_token'] == k + 1 and s['map_sha256'] == spatial.digest, 'JOINT_SPATIAL_IDENTITY')
    values = np.asarray(s['values'], dtype='<f4')
    flow = np.asarray(p['flow'], dtype='<f4')
    require(values.shape == (5768,) and flow.shape == (2, 721) and np.isfinite(values).all() and np.isfinite(flow).all(), 'JOINT_ARRAY_SCHEMA')
    require(digest(values.tobytes()) == s['values_sha256'] and digest(flow.tobytes()) == p['flow_sha256'], 'JOINT_ARRAY_SHA')
    ids = spatial.ids.tolist()
    require(p['PL_proven_global_ids'] == [] and p['PL_participating_global_ids'] == ([] if is_test else ids), 'JOINT_EVIDENCE_LEVEL')
    minimal=p.get('runtime_policy')=='MINIMAL_COMPUTE_ASYNC_V1'
    require(not minimal or identity.get('runtime_policy')==p['runtime_policy'],'JOINT_RUNTIME_POLICY_IDENTITY')
    require(p['evidence_level'] == ('ACK_MATCHED_RAM_ONLY_ASYNC_RECORDING' if minimal else 'CPU_PROTOCOL_REPLAY_ONLY' if is_test else 'ACK_MATCHED_DURABLE_PENDING_PS_AUDIT'), 'JOINT_PENDING_AUDIT')
    tx, durable = p['transaction'], p['durable']
    require(tx['status'] == 'ACK_MATCHED_AND_PUBLISHED' and tx['step_id'] == k and
            (tx['integer_error'] is None and tx.get('numerical_check')=='DEFERRED_OFFLINE' if minimal else tx['integer_error']==0), 'JOINT_COMMIT_STATUS')
    for key in ('old_full_sha256', 'full_after_sha256', 'unified_commit_sha256', 'request_sha256', 'candidate_sha256', 'ACK_sha256', 'old_H_sha256'):
        require(isinstance(tx[key], str) and re.fullmatch('[a-f0-9]{64}', tx[key]), 'JOINT_TRANSACTION_SHA')
    require(tx['ASID'] == p['hardware']['ASID'] and re.fullmatch('[a-f0-9]{32}', tx['txn']), 'JOINT_TXN_IDENTITY')
    require(tx['core_cycles'] == 57681 and tx['adapter_cycles'] >= tx['core_cycles'], 'JOINT_CYCLES')
    if minimal:
        live5=identity.get('live_response_hz')==5
        expected='LIVE_LOW_RATE_LATEST_COMMITTED_STATE' if live5 else 'POST_COMPUTE_SAME_RUN_NOT_REALTIME'
        require(p.get('live_response_hz')==identity.get('live_response_hz')
            and durable['barrier']=='NOT_SYNCHRONOUS' and p.get('display_kind')==expected,'JOINT_MINIMAL_NOT_DURABLE_OR_REALTIME')
    else:
        require(durable['barrier'] == 'STEP_PUBLISHED' and type(durable['end_offset']) is int and durable['end_offset'] > 0
                and type(durable['sequence']) is int and durable['sequence'] >= 0 and re.fullmatch('[a-f0-9]{64}', durable['batch_sha256']), 'JOINT_NOT_DURABLE')
    require(p['REALTIME_STREAM_PASS'] == 'NOT_CLAIMED' and p['whole_run_acceptance'] == 'PENDING', 'JOINT_FALSE_FINAL_PASS')
    return values.reshape(8, 721).mean(axis=1, dtype=np.float64)

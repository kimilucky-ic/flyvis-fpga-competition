"""Bounded full-PL display ingress in the ORIGINAL GUI; no board/GPU control.

An accepted first-step ZIP anchors run/boot and retained complete state. Neural
steps arrive in order. Display keeps only the latest complete immutable packet;
neither browser drawing, decoder completion nor disk writes gate reception.
"""
from collections import OrderedDict
import hmac
import json
import math
import secrets
import struct
import threading
import time
import uuid

import numpy as np
from line11_result import digest
from live_protocol import HERE, load, require

MAX_FRAME_BYTES = 200_000


def decode_frame(blob):
    require(4 <= len(blob) <= MAX_FRAME_BYTES, 'FULL_PL_FRAME_BOUND')
    size = struct.unpack_from('<I', blob)[0]
    require(0 < size <= 8192 and len(blob) == 4+size+2884+182676, 'FULL_PL_FRAME_LENGTH')
    meta = json.loads(blob[4:4+size])
    start = 4+size
    return meta, bytes(blob[start:start+2884]), bytes(blob[start+2884:])


class FullPLStream:
    def init__(self, seed, enabled=False, max_frames=32, idle_timeout_s=30., clock=time.perf_counter_ns, *, protocol_test=False):
        require(type(max_frames) is int and 1 <= max_frames <= 10000, 'FULL_PL_WINDOW_BOUND')
        self.seed, self.enabled, self.limit = seed, enabled, max_frames
        self.protocol_test=protocol_test
        self.clock, self.timeout_ns = clock, int(idle_timeout_s*1e9)
        self.lock = threading.RLock()
        self.state = 'DISABLED' if not enabled else 'WAITING_FIRST_STEP'
        self.error = None
        self.session_id = self.token = None
        self.count = self.revision = self.drawn = 0
        self.latest_frame = None
        self.receipts = OrderedDict()
        self.last_drawn_step = 0
        self.display_skipped_steps = 0

    def prepare(self):
        with self.lock:
            require(self.enabled, 'FULL_PL_STREAM_DISABLED')
            if self.session_id is None:
                self.anchor = self.seed.frame()  # full all-word acceptance once
                self.profile=self.anchor.get('transport_profile','LINE11_MMIO_FP32_ABI_00110002')
                require(self.profile in ('LINE11_MMIO_FP32_ABI_00110002','LINE11_DDR_FP32_ABI_00110004'),'FULL_PL_UNKNOWN_PROFILE')
                if self.profile=='LINE11_DDR_FP32_ABI_00110004':
                    from line11_ddr_bridge import BIT_SHA,HWH_SHA,CORE_CYCLES,INITIAL_BOUNDARY
                    h=self.anchor['hardware']
                    require(h['bit_sha256']==BIT_SHA and h['hwh_sha256']==HWH_SHA
                            and h['compute_cycles']==CORE_CYCLES,'DDR_FIRST_STEP_CANDIDATE')
                    require(self.anchor['initial_state_readback']==INITIAL_BOUNDARY,'DDR_INITIAL_READBACK_UNAVAILABLE')
                    require(self.protocol_test or self.anchor.get('operator_context_pc_verified') is True,'DDR_PHYSICAL_OPERATOR_CONTEXT_NOT_ACCEPTED')
                    self.audit_chain=self.anchor['audit_chain'];self.audit_cookie=self.anchor['audit_cookie']
                    from line11_ddr_bridge import COUNTER_DEFINITION
                    self.counter_definition=COUNTER_DEFINITION
                else:self.counter_definition='OLD_MMIO_ACCEPTED_COUNTER_BOUNDARY'
                self.decoder_pin = load(HERE/'live_registry.json')['pins']['decoder']
                self.session_id, self.token = uuid.uuid4().hex, secrets.token_hex(32)
                self.last_sha = self.anchor['full_state_sha256']
                self.state = 'READY_WAITING_PRODUCER'
            return self.anchor

    def _expired(self):
        if self.state == 'RECEIVING' and self.clock()-self.received_ns > self.timeout_ns:
            self._fail('FULL_PL_RECEIVE_TIMEOUT')

    def _fail(self, message):
        self.error, self.state, self.latest_frame = message, 'FAILED', None
        raise ValueError(message)

    def connection(self, base_url):
        self.prepare()
        return dict(schema='flyvis-line11-gui-connection/v1', url=base_url.rstrip('/'), token=self.token,
                    session_id=self.session_id, run_id=self.anchor['run_id'], boot_id=self.anchor['hardware']['boot_id'],
                    seed_state_sha256=self.anchor['full_state_sha256'], first_frame_id=1, retained_completed_steps=1,
                    max_new_frames=self.limit, model_dt_s=.005, clock_hz=self.anchor['hardware']['clock_hz'],
                    transport_profile=self.profile,protocol_test=self.protocol_test,
                    initial_state_readback=self.anchor.get('initial_state_readback','OLD_MMIO_ALL_INITIAL_WORDS_VERIFIED'),
                    meaning='DISPLAY_RECEIPT_ONLY_NOT_NEURAL_COMMIT; producer must verify retained state before continuing')

    def authenticate(self, authorization):
        self.prepare()
        require(isinstance(authorization,str) and hmac.compare_digest(authorization,'Bearer '+self.token), 'FULL_PL_UNAUTHORIZED')

    def accept(self, blob, authorization):
        self.authenticate(authorization)
        received_at = self.clock()  # complete body received, BEFORE array validation
        with self.lock:
            self._expired()
            require(self.state in ('READY_WAITING_PRODUCER','RECEIVING'), 'FULL_PL_STREAM_CLOSED')
            try:
                m, input_bits, state_bits = decode_frame(blob)
                require(m['schema']=='flyvis-line11-state-stream/v1', 'FULL_PL_STREAM_SCHEMA')
                require(m['session_id']==self.session_id and m['run_id']==self.anchor['run_id']
                        and m['boot_id']==self.anchor['hardware']['boot_id'], 'FULL_PL_STREAM_IDENTITY')
                k = m['frame_id']
                require(type(k) is int and k==self.count+1 and m['completed_steps']==k+1, 'FULL_PL_STREAM_ORDER')
                require(self.count < self.limit, 'FULL_PL_WINDOW_EXCEEDED')
                require(m['previous_state_sha256']==self.last_sha, 'FULL_PL_OLD_STATE_CHAIN')
                require(m['input_sha256']==digest(input_bits) and m['state_sha256']==digest(state_bits), 'FULL_PL_FRAME_SHA')
                require(m['faults']==0 and m['compute_cycles']==self.anchor['hardware']['compute_cycles']
                        and m['clock_hz']==self.anchor['hardware']['clock_hz'], 'FULL_PL_STREAM_HARDWARE')
                if self.profile=='LINE11_DDR_FP32_ABI_00110004':
                    from line11_ddr_bridge import PROFILE,check_receipt
                    row=m['source_audit']
                    require(m['transport_profile']==PROFILE and row['evidence']==('CPU_MOCK_ONLY' if self.protocol_test else 'OPERATOR_PHYSICAL_READS_UNATTESTED'),'DDR_SOURCE_EVIDENCE')
                    check_receipt(row,k,m['run_id'],self.audit_cookie,self.audit_chain,m['input_sha256'],m['state_sha256'])
                elapsed = m['elapsed_seconds']
                require(type(elapsed) in (int,float) and math.isfinite(elapsed) and elapsed >= 0, 'FULL_PL_STREAM_TIMING')
                for raw in (input_bits,state_bits):
                    require(np.isfinite(np.frombuffer(raw,dtype='<f4')).all(), 'FULL_PL_STREAM_NONFINITE')
                self.received_ns = received_at
                self.count += 1
                self.revision += 1
                self.last_sha = m['state_sha256']
                if self.profile=='LINE11_DDR_FP32_ABI_00110004':self.audit_chain=m['source_audit']['chain']
                self.latest_frame = (m,input_bits,state_bits,self.received_ns,None)
                self.receipts[k] = (self.last_sha,self.received_ns)
                while len(self.receipts)>64:self.receipts.popitem(last=False)
                self.state = 'RECEIVING'
                return dict(status='RECEIVED_FOR_DISPLAY',run_id=m['run_id'],session_id=self.session_id,
                            frame_id=k,full_state_sha256=self.last_sha,neural_commit=False)
            except (ValueError,KeyError,TypeError,OverflowError) as error:
                self._fail(str(error))

    def status(self):
        with self.lock:
            if self.enabled:
                try:self.prepare();self._expired()
                except (OSError,ValueError,KeyError,TypeError) as error:
                    self.error=str(error)
            return dict(status=self.state,configured=self.enabled,session_id=self.session_id,
                        run_id=self.anchor['run_id'] if self.session_id else None,
                        boot_id=self.anchor['hardware']['boot_id'] if self.session_id else None,
                        first_step_accepted=self.session_id is not None,error=self.error,
                        received_steps=self.count,max_new_steps=self.limit,revision=self.revision,
                        browser_receipts=self.drawn,display_skipped_steps=self.display_skipped_steps,
                        result_valid=self.latest_frame is not None and self.state in ('RECEIVING','FINISHED'),
                        board_connection='PRODUCER_POSTING_REPORTED_BOARD_STATE' if self.state=='RECEIVING' else 'NOT_CONNECTED',
                        evidence_level='CPU_PROTOCOL_ONLY_NO_PHYSICAL_RUN' if self.protocol_test else 'FIRST_STEP_VERIFIED_SUBSEQUENT_TRAJECTORY_AUDIT_PENDING',
                        REALTIME_STREAM_PASS='NOT_CLAIMED',all_steps_persisted=False,
                        storage_policy='LATEST_STATE_IN_RAM_ONLY_NO_FULL_TRAJECTORY_ARCHIVE')

    def latest(self, after=-1):
        with self.lock:
            s = self.status()
            if not s['result_valid'] or self.revision==after:return dict(status=s,frame=None)
            m, raw_input, raw_state, received_ns, flow = self.latest_frame
            revision = self.revision
        full = np.frombuffer(raw_state,dtype='<f4')
        values = self.seed.spatial.extract(full)
        k = m['frame_id']
        packet = dict(schema='flyvis-full-pl-stream-display/v1',run_id=m['run_id'],session_id=self.session_id,
            step_id=k,serial=k+1,state_token=k+1,revision=revision,backend='FULL_NETWORK_FPGA',
            display_kind='CPU_PROTOCOL_TEST_ONLY' if self.protocol_test else 'CURRENT_FULL_PL_STATE_PENDING_AUDIT' if s['status']=='RECEIVING' else 'FINISHED_FULL_PL_LAST_STATE',
            evidence_level=s['evidence_level'],input_time_s=k*.005,activity_time_s=(k+1)*.005,
            full_state_sha256=m['state_sha256'],previous_state_sha256=m['previous_state_sha256'],
            input_sha256=m['input_sha256'],input_hex=np.frombuffer(raw_input,dtype='<f4').tolist(),
            spatial=dict(values=values.tolist(),values_sha256=digest(values.tobytes()),map_sha256=self.seed.spatial.digest),
            signed_means=values.reshape(8,721).mean(axis=1,dtype=np.float64).tolist(),
            source=dict(sequence=k,kind='line11_frame_input'),hardware=dict(self.anchor['hardware'],completed_steps=k+1),
            transport_profile=self.profile,source_audit=m.get('source_audit'),
            cycle_definition=self.counter_definition,
            initial_state_readback=self.anchor.get('initial_state_readback','OLD_MMIO_ALL_INITIAL_WORDS_VERIFIED'),
            model=self.anchor['model'],anchor_archive_sha256=self.seed.archive_sha,
            received_pc_ns=received_ns,elapsed_seconds=m['elapsed_seconds'],
            flow=flow['values'] if flow else None,flow_sha256=flow['sha256'] if flow else None,
            flow_binding=flow['binding'] if flow else None,flow_status='OFFICIAL_DECODER_SAME_STATE' if flow else 'NOT_AVAILABLE_NOT_DECODED')
        return dict(status=s,frame=packet,response_pc_ns=self.clock())

    def complete_state_for_decoder(self):
        """Existing official decoder can consume this; no GPU job is started here."""
        with self.lock:
            require(self.status()['result_valid'], 'FULL_PL_NO_CURRENT_STATE')
            m, _, bits, _, _ = self.latest_frame
            return dict(run_id=m['run_id'],session_id=self.session_id,frame_id=m['frame_id'],
                        full_state_sha256=m['state_sha256'],state_bits=bits)

    def attach_flow(self, binding, values):
        with self.lock:
            require(self.status()['result_valid'], 'FULL_PL_NO_CURRENT_STATE')
            m, inp, state, received, _ = self.latest_frame
            require(binding['run_id']==m['run_id'] and binding['session_id']==self.session_id
                    and binding['frame_id']==m['frame_id'] and binding['full_state_sha256']==m['state_sha256'], 'FULL_PL_FLOW_STATE_BINDING')
            require(binding['decoder']=='DecoderGAVP' and binding['decoder_source_sha256']==self.decoder_pin['sha256']
                    and binding['checkpoint_sha256']==self.anchor['model']['checkpoint_sha256']
                    and binding['recursive_eval'] is True, 'FULL_PL_OFFICIAL_DECODER_BINDING')
            a = np.asarray(values,dtype='<f4')
            require(a.shape==(2,721) and np.isfinite(a).all(), 'FULL_PL_FLOW_ARRAY')
            self.latest_frame=(m,inp,state,received,dict(values=a.tolist(),sha256=digest(a.tobytes()),binding=dict(binding)))
            self.revision+=1
            return dict(status='FLOW_ATTACHED_TO_EXACT_STATE',revision=self.revision)

    def paint(self, receipt):
        """Browser-reported callback evidence only; never a neural/PL ACK."""
        with self.lock:
            require(self.status()['result_valid'], 'FULL_PL_NO_CURRENT_STATE')
            k = receipt['frame_id']
            require(receipt['session_id']==self.session_id and receipt['run_id']==self.anchor['run_id']
                    and k in self.receipts and receipt['full_state_sha256']==self.receipts[k][0], 'FULL_PL_PAINT_IDENTITY')
            require(k>=self.last_drawn_step, 'FULL_PL_PAINT_ORDER')
            lo, hi = receipt['receive_to_draw_lower_ms'],receipt['receive_to_draw_upper_ms']
            require(all(type(v) in (float,int) and math.isfinite(v) for v in (lo,hi)) and 0<=lo<=hi, 'FULL_PL_PAINT_CLOCK')
            if k>self.last_drawn_step:
                self.display_skipped_steps+=max(0,k-self.last_drawn_step-1)
                self.last_drawn_step=k
                self.drawn+=1
            self.last_paint=dict(receipt,evidence='BROWSER_REPORTED_CALLBACK_NOT_PHOTON_MEASUREMENT')
            return dict(status='BROWSER_RECEIPT_RECORDED',neural_commit=False)

    def finish(self, body, authorization):
        self.authenticate(authorization)
        with self.lock:
            self._expired()
            require(self.state=='RECEIVING' and body['session_id']==self.session_id
                    and body['run_id']==self.anchor['run_id'] and body['received_steps']==self.count
                    and body['last_frame_id']==self.count and body['full_state_sha256']==self.last_sha, 'FULL_PL_FINISH_BINDING')
            self.state='FINISHED'
            self.revision+=1
            return dict(status='FINISHED_PRODUCER_REPORTED',received_steps=self.count,whole_run_acceptance='PENDING')

    def close(self):
        with self.lock:
            if self.state!='FINISHED':self.state='STOPPED';self.latest_frame=None

    def abort(self, message):
        with self.lock:
            self.error, self.state, self.latest_frame = message, 'FAILED', None


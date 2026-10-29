"""Bounded OV5640 saved-result admission in the original GUI. No board APIs.

The sealed line11 producer is one frame / one step, NOT a continuous camera.
Only its existing CPU oracle and official complete-state decoder are reused.
"""
import hashlib
import hmac
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import uuid
import zipfile
from types import SimpleNamespace

import numpy as np
from line11_result import FullPLResult
from live_protocol import HERE

RELEASE = HERE.parents[1]/'flyvis-lossless-study/ov5640_release_20261023'
# fly may resolve through flyvis_runtime; derive the repository explicitly.
if not RELEASE.exists():
    RELEASE = next(p for p in HERE.parents if (p/'flyvis-lossless-study').is_dir())/'flyvis-lossless-study/ov5640_release_20261023'
# Separate GUI-owned conditional admission revision; original release unchanged.
BUNDLE = HERE/'handoff/ov5640_conditional_r1_20261023/bundle'
PACKAGE = BUNDLE.parent/'GUI_OV5640_CONDITIONAL_R1.zip'
PACKAGE_SHA = 'b65fb680d6277dc900f5e14d4e5344ea3ec5057919b6aad7cbf0ba78972649bd'
BIT_SHA = '781981526e8cc9916c096ff46b92046d90021d56c9438718fe5566cfdf1df7d7'
HWH_SHA = '61465634adaa0e421a5b07c77b38e0739fdcfdf8e68e977f25bf2d803b9097ae'
MAX_ZIP = 16_000_000


def sha(data): return hashlib.sha256(data).hexdigest()
def require(ok, message):
    if not ok: raise ValueError(message)
def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))


def checked_files(blob):
    require(0 < len(blob) <= MAX_ZIP, 'OV5640_ZIP_SIZE')
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        rows = z.infolist()
        require(len(rows) <= 150 and len({r.filename for r in rows}) == len(rows), 'OV5640_ZIP_ENTRIES')
        require(sum(r.file_size for r in rows) <= 64_000_000, 'OV5640_UNPACKED_SIZE')
        for r in rows:
            parts = r.filename.split('/')
            require(not r.filename.startswith('/') and '\\' not in r.filename and ':' not in r.filename
                    and not any(p in ('.', '..') for p in parts), 'OV5640_UNSAFE_PATH')
            require(not r.flag_bits & 1 and (r.external_attr >> 16) & 0o170000 != 0o120000, 'OV5640_ZIP_MODE')
        return {r.filename: z.read(r) for r in rows if not r.is_dir()}


def verify_package():
    blob = PACKAGE.read_bytes()
    require(sha(blob) == PACKAGE_SHA, 'OV5640_RELEASE_SHA')
    # Verify the executable oracle sources against the actual sealed ZIP too.
    for name, data in checked_files(blob).items():
        require((BUNDLE/name).read_bytes() == data, 'OV5640_BUNDLE_CHANGED '+name)
    return blob


def cpu_process(argv, log, timeout=150):
    env = dict(os.environ, CUDA_VISIBLE_DEVICES='-1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
    with Path(log).open('xb') as f:
        cwd = HERE.parent if Path(argv[0]).name == 'ov5640_adapter.py' else BUNDLE
        subprocess.run([sys.executable, '-X', 'utf8', '-B']+list(map(str, argv)), cwd=str(cwd),
                       env=env, stdout=f, stderr=subprocess.STDOUT, timeout=timeout, check=True,
                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))


class OV5640Session(FullPLResult):
    source_kind = 'board_ov5640'
    camera_live = False

    def init__(self, root=None):
        super().init__(None)
        self.session_id = uuid.uuid4().hex
        self.output = Path(root or HERE/'runtime/ov5640')/self.session_id
        self.output.mkdir(parents=True, exist_ok=False)
        self.seed = SimpleNamespace(status=self.seed_status,frame=self.frame,projection=self.projection,cache=self.cache)
        self.claimed = False
        self.import_attempted = False
        self.packet = None
        self.phase = 'WAITING_FIRST_STEP'
        self.claim_lock = threading.Lock()
        from line11_ddr_notebook import installation
        self.pairing = installation()
        verify_package()

    def authenticated(self, auth):
        return isinstance(auth, str) and hmac.compare_digest(auth, 'Bearer '+self.pairing['pairing_key'])

    def notebook_bundle(self, body, auth):
        require(self.authenticated(auth), 'OV5640_PAIRING')
        require(body.get('kind') in ('manifest', 'package', 'capture-intent') and body.get('installation_id') == self.pairing['installation_id'], 'OV5640_NOTEBOOK_ID')
        if body['kind'] == 'capture-intent':
            require(body.get('session_id') == self.session_id, 'OV5640_SESSION_CHANGED')
            with self.lock:
                require(not self.claimed and self.phase == 'WAITING_FIRST_STEP', 'OV5640_NO_AUTOMATIC_RETRY')
                self.claimed = True
                self.phase = 'WAITING_CAPTURE'
                (self.output/'CAPTURE_INTENT.json').write_text(json.dumps(dict(session_id=self.session_id,
                    meaning='OPERATOR_ABOUT_TO_CALL_SEALED_BOARD_ENTRY; NOT_HARDWARE_SUCCESS')),encoding='utf-8')
            return dict(session_id=self.session_id,status='CAPTURE_INTENT_RESERVED',board_operations=0)
        if body['kind'] == 'package':
            require(body.get('session_id') == self.session_id, 'OV5640_SESSION_CHANGED')
            return verify_package()
        return dict(session_id=self.session_id, package_sha256=PACKAGE_SHA, package_bytes=PACKAGE.stat().st_size,
                    input_kind=self.source_kind, steps=1, continuous_60s=False,
                    test_profile='GUI_OV5640_CONDITIONAL_ONE_FRAME_R1',electrical_timing_acceptance=False)

    def status(self):
        return dict(configured=True, source_kind=self.source_kind, status=self.phase,
                    first_step_accepted=self.packet is not None, result_valid=self.packet is not None,
                    display_complete=self.packet is not None, session_id=self.session_id,
                    run_id=self.packet['run_id'] if self.packet else None,
                    error=self.error, board_connection='NOT_CONNECTED', received_steps=int(self.packet is not None),
                    continuous_60s=False, actual_execution=False,
                    evidence=self.packet['evidence_level'] if self.packet else 'NOT_AVAILABLE')

    def seed_status(self):
        return dict(self.status(), status='VERIFIED_SAVED_FIRST_STEP' if self.packet else
                    ('NOT_AVAILABLE' if self.error else 'WAITING_FIRST_STEP'))

    def _load(self):
        require(self.packet is not None, self.error or 'OV5640_WAITING_RESULT')
        return self.packet

    def frame(self): return self._load()
    def close(self): pass
    def clock(self): return time.perf_counter_ns()
    def latest(self, after=-1):
        return dict(status=self.status(), frame=self.packet if self.packet and after < 1 else None,
                    response_pc_ns=self.clock())

    def ingest(self, blob, auth, session):
        require(self.authenticated(auth), 'OV5640_PAIRING')
        require(session == self.session_id, 'OV5640_SESSION_CHANGED')
        require(self.claim_lock.acquire(blocking=False), 'OV5640_IMPORT_IN_PROGRESS')
        try:
            require(not self.import_attempted, 'OV5640_NO_AUTOMATIC_RETRY')
            self.import_attempted = True
            self.claimed = True
            self.phase = 'AUDITING'
            files = checked_files(blob)
            require('IN_DOUBT.json' not in files, 'OV5640_IN_DOUBT')
            require({'RUN_CONTEXT.json', 'RESULT.json', 'bound/000000/actual_state.bin'} <= set(files), 'OV5640_REQUIRED_FILES')
            archive = self.output/'RESULT.zip';archive.write_bytes(blob)
            cpu_process([BUNDLE/'verify_run.py', archive, self.output/'audit'], self.output/'audit.log')
            a = load(self.output/'audit/ACCEPTANCE.json')
            require(a['status'] == 'PASS_SAVED_ONE_STEP_ALL_STATES' and a['mismatch_words'] == 0
                    and a['state_words_compared'] == 45669 and a['completed_steps'] == 1, 'OV5640_FULL_STATE_AUDIT')
            require(a['evidence'] in ('CPU_MOCK_ONLY', 'OFFLINE_CPU_AUDIT_OF_OPERATOR_REPORTED_BOARD_CAPTURE'), 'OV5640_EVIDENCE')
            c, r = json.loads(files['RUN_CONTEXT.json']), json.loads(files['RESULT.json'])
            require(a.get('test_profile')=='GUI_OV5640_CONDITIONAL_ONE_FRAME_R1' and a.get('electrical_timing_acceptance') is False,
                    'OV5640_CONDITIONAL_SCOPE')
            require(c['identity']['bit_sha256'] == BIT_SHA and c['identity']['hwh_sha256'] == HWH_SHA, 'OV5640_IMAGE')
            d = 'bound/000000/'
            state, inp, source = (files[d+n] for n in ('actual_state.bin', 'actual_input.bin', 'source_frame.bin'))
            require(sha(state) == a['state_sha256'] and sha(inp) == a['input_sha256']
                    and sha(source) == a['source_frame_sha256'], 'OV5640_AUDIT_BINDING')
            self.full = np.frombuffer(state, dtype='<f4').copy()
            self.input = np.frombuffer(inp, dtype='<f4').copy()
            require(self.full.shape == (45669,) and np.isfinite(self.full).all(), 'OV5640_STATE')
            from spatial_state import SpatialRegistry
            self.spatial = SpatialRegistry()
            values = self.spatial.extract(self.full)
            statefile = self.output/'state.bin';statefile.write_bytes(state)
            cpu_process([Path(__file__).resolve(), '--decode', statefile, self.output/'flow'], self.output/'decode.log')
            flow = np.frombuffer((self.output/'flow/flow.bin').read_bytes(), dtype='<f4').reshape(2,721)
            identity = load(self.output/'flow/identity.json')
            require(identity['recursive_eval'] is True and identity['device'] == 'cpu' and np.isfinite(flow).all(), 'OV5640_DECODER')
            model = load(BUNDLE/'original_model_provenance.json')
            require(identity['checkpoint_sha256'] == model['checkpoint_sha256'] and model['neurons'] == 45669
                    and model['synapses'] == 1513231 and model['dt_seconds'] == .005, 'OV5640_MODEL_DECODER_BINDING')
            from PIL import Image
            image = np.frombuffer(source, dtype=np.uint8).reshape(480,640,3)
            require(r['channel_order'] in ('BGR','RGB','GBR'), 'OV5640_CHANNEL_ORDER')
            image = image[:,:,[r['channel_order'].index(c) for c in 'RGB']]
            png = io.BytesIO();Image.fromarray(image).save(png, format='PNG');self.png = png.getvalue()
            run = self.session_id
            prepared = json.loads(files[d+'PREPARED.json'])
            self.packet = dict(schema='flyvis-full-pl-stream-display/v1', backend='FULL_NETWORK_FPGA',
                display_kind='OFFLINE_OV5640_ONE_STEP', evidence_level=a['evidence'],
                board_connection='NOT_CONNECTED', session_id=self.session_id, run_id=run,
                step_id=0, serial=1, revision=1, state_token=1, input_time_s=0., activity_time_s=.005,
                elapsed_seconds=None, input_hex=self.input.tolist(), input_sha256=sha(inp), full_state_sha256=sha(state),
                archive_sha256=sha(blob), original_run_context=c, acceptance=a,
                source=dict(kind=self.source_kind, sequence=0, source_frame=0, raw_sha256=sha(source),
                    pixel_png_sha256=sha(self.png), channel_order=r['channel_order'], color_order_verified=a['color_order_verified'],
                    timestamp_ns=prepared['source_timestamp_ns'], timestamp_definition='PS monotonic capture request; NOT exposure timestamp'),
                spatial=dict(values=values.tolist(), values_sha256=sha(values.tobytes()), map_sha256=self.spatial.digest),
                signed_means=values.reshape(8,721).mean(axis=1,dtype=np.float64).tolist(),
                hardware=dict(bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,boot_id=c.get('boot_id'),
                    compute_cycles=r['cycles'],clock_hz=100_000_000,clock_evidence='REGISTER_DERIVED_NOMINAL_NOT_MEASURED',
                    faults=0,completed_steps=1), model=model,
                flow=flow.tolist(),flow_sha256=sha(flow.tobytes()),flow_status='OFFICIAL_DECODER_SAME_STATE',
                flow_binding=dict(identity,run_id=run,session_id=self.session_id,frame_id=0,full_state_sha256=sha(state)),
                plan_metadata=dict(steps=1,input_kind=self.source_kind,input_time_offset_s=0.))
            (self.output/'DISPLAY.json').write_text(json.dumps(self.packet),encoding='utf-8')
            self.phase = 'FINISHED'
            return self.status()
        except BaseException as error:
            # One authenticated attempt: preserve evidence; never leave old pixels valid.
            self.packet = None;self.phase = 'FAILED';self.error = str(error)
            (self.output/'FAILED.json').write_text(json.dumps(dict(error=str(error),automatic_retry=False)),encoding='utf-8')
            raise
        finally: self.claim_lock.release()

    def source_frame(self, step, run, state):
        p = self._load()
        require(step == 0 and run == p['run_id'] and state == p['full_state_sha256'], 'OV5640_SOURCE_IDENTITY')
        return self.png


def decode_cli(state, output):
    from line11_ddr_flow import CPUDecoder
    root = Path(output);root.mkdir(exist_ok=False)
    decoder = CPUDecoder(root/'scratch')
    values = np.fromfile(state,dtype='<f4').reshape(1,45669)
    flow = np.asarray(decoder.decode(values),dtype='<f4').reshape(2,721)
    (root/'flow.bin').write_bytes(flow.tobytes())
    (root/'identity.json').write_text(json.dumps(decoder.identity),encoding='utf-8')


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--decode':decode_cli(sys.argv[2],sys.argv[3])
    else:raise SystemExit('Saved-state CPU decoder only')

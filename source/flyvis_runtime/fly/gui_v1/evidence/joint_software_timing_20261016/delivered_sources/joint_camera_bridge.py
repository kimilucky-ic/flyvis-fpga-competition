"""Original GUI camera owner and validated joint display consumer. No GPU worker."""
import base64
from collections import OrderedDict
import copy
import hashlib
import json
import os
from pathlib import Path
import threading
import time
from types import SimpleNamespace
import uuid

import numpy as np
from live_protocol import HERE, Registry, host_path, load, require, sha, utc, write
from joint_camera_protocol import LIVE, validate_snapshot, validate_scope, digest
from spatial_state import SpatialRegistry
from stream_transport import RPC
from realtime_timing import latency_sample
from joint_diagnostics import JointDiagnostics,NONE


class JointCameraBridge:
    def init__(self, session_path=None):
        self.path = host_path(session_path) if session_path else None
        self.root = self.path.parent if self.path else None
        self.session = self.scope = self.spatial = self.registry = None
        self.client = self.input_client = None
        self.thread = self.capture_thread = None
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.packet = self.error = None
        self.packets = OrderedDict()
        self.last_status = {}
        self.control = None
        self.sequence = 0
        self.origin = None
        self.capture_closed = True
        self.drawn = set()
        self.last_poll = time.monotonic()
        self.geometry = self.cached = None
        self.identity = None
        self.final_held = False
        self.draw_pending=set();self.draw_io_lock=threading.Lock()
        self.diagnostics=JointDiagnostics('Windows_GUI') if self.path else NONE
        self.diagnostics_saved=False
        if self.path:
            self.session = load(self.path)
            require(self.root.resolve().parent == (HERE/'runtime/joint').resolve(), 'JOINT_GUI_ROOT')
            self.scope = load(self.root/'scope.json')
            require(sha(self.root/'scope.json') == self.session['scope_sha256'] and self.scope['session_id'] == self.session['session_id'], 'JOINT_GUI_SCOPE')
            self.spatial, self.registry = SpatialRegistry(), Registry()

    def touch(self):
        self.last_poll = time.monotonic()

    def clock(self):
        return dict(clock='Windows_perf_counter_ns', server_monotonic_ns=time.perf_counter_ns(), valid_for_s=5)

    def connect(self):
        require(self.path is not None, 'CAMERA_JOINT_NOT_CONNECTED')
        validate_scope(self.scope)
        require(sha(self.root/'scope.json') == self.session['scope_sha256'], 'JOINT_GUI_SCOPE_CHANGED')
        if self.client is None:
            endpoint = load(self.root/'joint_endpoint.json')
            require(endpoint['session_id'] == self.session['session_id'], 'JOINT_GUI_ENDPOINT')
            self.client, self.input_client = RPC(endpoint), RPC(endpoint)

    def status(self):
        self.touch()
        if self.path is None:
            return dict(status='NOT_CONNECTED', ready_for_camera=False, result_valid=False, FPGA_status='NOT_CONNECTED',
                error='New camera hardware scope and normal-finish service are not connected', whole_run_acceptance='NOT_AVAILABLE')
        if (self.root/'worker_start_failure.json').exists():
            self.error=load(self.root/'worker_start_failure.json')['error']
        if not self.control and self.error is None:
            try:
                self.connect()
                self.last_status = self.client.call('status')
            except FileNotFoundError:
                self.last_status = dict(status='PREPARING', ready_for_camera=False)
            except (OSError,ValueError,KeyError) as error:
                self.error = str(error)
        if self.stop_event.is_set() and self.error is None and (self.root/'worker_exit.json').exists():
            result = load(self.root/'result.json')
            exit_state = load(self.root/'worker_exit.json')
            if result.get('status') == 'STOPPED_PENDING_PS_AUDIT' and not exit_state.get('cleanup_errors'):
                self.last_status = dict(self.last_status, status='STOPPED_PENDING_PS_AUDIT', stop_acknowledged=True)
            else:
                self.error = result.get('error') or 'JOINT_CLEANUP_FAILED'
        return dict(self.last_status, run_id=self.scope['run_id'], session_id=self.scope['session_id'],
            ready_for_camera=bool(self.last_status.get('ready_for_camera')) and not self.error and self.control is None,
            result_valid=bool(self.packet) and not self.error and (not self.stop_event.is_set() or self.final_held),
            display_kind='STOPPED_LAST_COMMITTED_FRAME_PENDING_AUDIT' if self.final_held else 'CURRENT_JOINT_RUN',
            error=self.error or self.last_status.get('error'), capture_closed=self.capture_closed,
            source_kind='real_windows_camera', whole_run_acceptance='PENDING', REALTIME_STREAM_PASS='NOT_CLAIMED')

    def prepare(self):
        require(self.path is not None, 'CAMERA_JOINT_NOT_CONNECTED')
        if self.geometry is None:
            from projection_startup import load_static_projection
            result = load_static_projection(SimpleNamespace(adapter=SimpleNamespace(registry=self.registry), spatial=self.spatial))
            require(result is not None, 'JOINT_FIXED_GEOMETRY_NOT_AVAILABLE')
            self.geometry, self.cached = result
            self.geometry['projection_cache']['url'] = '/api/joint-camera/cache'
            self.geometry['consumer_kind'] = 'JOINT_CAMERA_PENDING_AUDIT'
            self.geometry['coordinates_uv'] = self.registry.uv.tolist()
            self.geometry['joint_spatial_global_ids'] = self.spatial.ids.tolist()
        return self.geometry

    def cache(self):
        self.prepare()
        return self.cached.blob

    def start(self, body):
        with self.lock:
            require(self.control is None and not self.stop_event.is_set(), 'JOINT_GUI_START_CONSUMED')
            self.connect()
            require(self.geometry is not None, 'JOINT_PREPARE_DISPLAY_FIRST')
            require(set(body) == {'run_id','session_id'} and all(body[k] == self.scope[k] for k in body), 'JOINT_GUI_START_IDENTITY')
            self.control = dict(body, camera_id=self.scope['camera_id'])
            self.last_status = self.client.call('start', self.control)
            self.capture_closed = False
            self.thread = threading.Thread(target=self.loop, daemon=True)
            self.capture_thread = threading.Thread(target=self.capture, daemon=True)
            self.thread.start(); self.capture_thread.start()
            return dict(self.last_status, source_kind='real_windows_camera')

    def validate(self, packet):
        require(packet['execution_kind'] == LIVE and packet['actual_new_computation'] is True, 'JOINT_REPLAY_NOT_LIVE')
        identity = self.identity
        require(identity is not None, 'JOINT_GUI_NO_ATTESTATION')
        require(identity['model'] == self.scope['model'] and identity['mapping_sha256'] == self.scope['mapping_sha256'], 'JOINT_GUI_MODEL')
        hw = identity['hardware']
        require(all(hw[k] == self.scope[k] for k in ('boot_id','server_session','bit_sha256','hwh_sha256')), 'JOINT_GUI_HARDWARE')
        return validate_snapshot(packet, identity, self.spatial)

    def loop(self):
        try:
            while not self.stop_event.is_set():
                require(time.monotonic()-self.last_poll < 5, 'JOINT_BROWSER_DISCONNECTED')
                result = self.client.call('latest', dict(after_serial=self.packet['serial'] if self.packet else 0))
                with self.lock:
                    self.last_status = result['status']
                    ident = self.last_status.get('identity')
                    if ident:
                        require(self.identity is None or self.identity == ident, 'JOINT_GUI_ATTESTATION_CHANGED')
                        self.identity = copy.deepcopy(ident)
                    require(not self.last_status.get('error'), 'JOINT_WORKER_FAILED '+str(self.last_status.get('error')))
                    if self.last_status.get('stopping'):
                        self.stop_event.set()
                        break
                    p = result['packet']
                    if p:
                        self.validate(p)
                        if self.packet:
                            require(p['serial'] > self.packet['serial'], 'JOINT_GUI_STALE_PACKET')
                        self.packet = copy.deepcopy(p)
                        self.packets[p['serial']] = self.packet
                        while len(self.packets) > 32: self.packets.popitem(last=False)
        except (OSError,ValueError,KeyError,ConnectionError) as error:
            # A normal closed worker is reported only from its saved final state.
            exit_path = self.root/'worker_exit.json'
            result_path = self.root/'result.json'
            until = time.monotonic()+2
            while not exit_path.exists() and time.monotonic() < until:
                time.sleep(.02)
            if exit_path.exists() and result_path.exists() and load(result_path).get('status') == 'STOPPED_PENDING_PS_AUDIT' and not load(exit_path).get('cleanup_errors'):
                self.last_status = dict(status='STOPPED_PENDING_PS_AUDIT', stop_acknowledged=True, result_valid=False)
            else:
                self.error = str(error)
        finally:
            with self.lock:
                if not self.error:
                    try:self.hold_final_snapshot()
                    except (OSError,ValueError,KeyError) as error:self.error=str(error)
                if self.error:self.packet = None
                self.stop_event.set()
            if self.error:
                write(self.root/'ERROR_REQUEST.json',dict(run_id=self.scope['run_id'],error=self.error))

    def hold_final_snapshot(self):
        """Normal end retains only this run's saved, hash-bound committed frame."""
        until=time.monotonic()+3
        while not (self.root/'manifest.json').exists() and time.monotonic()<until:
            time.sleep(.02)
        result=load(self.root/'result.json');exit_state=load(self.root/'worker_exit.json')
        require(result['status']=='STOPPED_PENDING_PS_AUDIT' and result['committed_steps']>0
            and not exit_state['cleanup_errors'] and exit_state['GPU_inflight_waited'] and exit_state['lease_closed'],'JOINT_FINAL_NOT_CLEAN')
        manifest=load(self.root/'manifest.json')
        require(manifest['run_id']==self.scope['run_id'] and sha(self.root/'final_snapshot.json')==manifest['files']['final_snapshot.json'],'JOINT_FINAL_SNAPSHOT_SHA')
        p=load(self.root/'final_snapshot.json');self.validate(p)
        require(p['state_token']==result['committed_steps']==exit_state['committed_steps'],'JOINT_FINAL_STATE_TOKEN')
        self.packet=copy.deepcopy(p);self.packets[p['serial']]=self.packet;self.final_held=True
        self.last_status=dict(status='STOPPED_PENDING_PS_AUDIT',stop_acknowledged=True,identity=self.identity,committed_steps=p['state_token'])

    def capture(self):
        camera = None
        try:
            import sys
            sys.path.insert(0, str(HERE.parent))
            from camera_pipeline.capture import open_camera, read_frame
            camera = open_camera(self.scope['camera_id'], backend='dshow', width=640, height=480, fps=15)
            next_read = time.monotonic()
            while not self.stop_event.is_set():
                if self.stop_event.wait(max(0, next_read-time.monotonic())): break
                frame = self.diagnostics.call('camera.read_frame',read_frame,camera)
                ok,png=self.diagnostics.call('camera.PNG_encode',camera.cv2.imencode,'.png',frame.bgr)
                require(ok, 'JOINT_CAMERA_PNG')
                if self.origin is None: self.origin = frame.received_monotonic_ns
                raw = png.tobytes()
                source = dict(run_id=self.scope['run_id'], source_kind='real_windows_camera', sequence=self.sequence,
                    received_monotonic_ns=frame.received_monotonic_ns, received_utc=frame.received_utc,
                    relative_s=(frame.received_monotonic_ns-self.origin)/1e9, png_sha256=digest(raw),
                    timestamp_kind='Windows_receipt_not_sensor', camera_id=self.scope['camera_id'], camera_sequence=frame.sequence,
                    camera_resolution=[frame.bgr.shape[1],frame.bgr.shape[0]], camera_backend='DSHOW')
                self.diagnostics.call('camera.input_RPC',self.input_client.call,'input',dict(source=source,png=base64.b64encode(raw).decode()))
                self.sequence += 1
                next_read = time.monotonic()+1/15
        except BaseException as error:
            if not self.stop_event.is_set():
                self.error = str(error); self.stop_event.set()
        finally:
            if camera: camera.close()
            self.capture_closed = camera is None or camera.closed
            write(self.root/'camera_capture.json', dict(run_id=self.scope['run_id'], frames_delivered=self.sequence,
                closed=self.capture_closed, error=self.error, sensor_exposure_time_available=False,
                semantics='Windows capture receipt times; selected source frames are preserved in PC joint journal'))
            if self.error:
                write(self.root/'ERROR_REQUEST.json', dict(error=self.error, run_id=self.scope['run_id']))

    def latest(self):
        status = self.status()
        with self.lock:
            return dict(status=status, packet=copy.deepcopy(self.packet) if status['result_valid'] else None)

    def record_draw(self, body):
        return self.diagnostics.call('draw.total_inclusive',self._record_draw,body)

    def _record_draw(self,body):
        self.touch()
        require(self.path and not self.error, 'JOINT_DRAW_REVOKED')
        serial=body['serial']
        with self.diagnostics.measure('draw.reserve_state_lock'):
            with self.lock:
                p=self.packets.get(serial)
                require(p is not None and serial not in self.drawn and serial not in self.draw_pending,'JOINT_DRAW_EXPIRED_OR_DUPLICATE')
                self.draw_pending.add(serial)
        try:
            self.diagnostics.call('draw.snapshot_recheck',self.validate,p)
            for key in ('run_id','session_id','step_id','state_token'):
                require(body[key] == p[key], 'JOINT_DRAW_IDENTITY')
            require(body['unified_commit_sha256'] == p['transaction']['unified_commit_sha256']
                    and body['source_png_sha256'] == p['source']['png_sha256']
                    and body['spatial_values_sha256'] == p['spatial']['values_sha256']
                    and body['flow_sha256'] == p['flow_sha256'], 'JOINT_DRAW_COMMIT')
            require(body['projection_cache_sha256'] == self.cached.sha256 and 0 <= body['clock_age_s'] <= 5
                    and abs(time.perf_counter_ns()-body['draw_server_monotonic_ns']) < 2e9, 'JOINT_DRAW_CLOCK_OR_GEOMETRY')
            means = np.asarray(p['spatial']['values'], dtype='<f4').reshape(8,721).mean(axis=1,dtype=np.float64)
            rgba,_=self.diagnostics.call('draw.CPU_pixel_reference',self.cached.render,means,self.geometry)
            require(digest(rgba.tobytes()) == body['skeleton_raw_sha256'], 'JOINT_DRAW_BRIGHTNESS_PIXELS')
            sample = latency_sample(p['source'], body['draw_server_monotonic_ns'], body['clock_uncertainty_ms'])
            row = dict(body, **sample, received_utc=utc(), evidence='BROWSER_RAF_SUBMISSION_NOT_PHYSICAL_SCANOUT',
                       whole_run_acceptance='PENDING')
            if 'browser_stage_timings' in body:
                fields=body['browser_stage_timings']
                require(set(fields)=={'validate_ms','skeleton_render_ms','bitmap_ms','prepare_ms','raf_wait_ms','canvas_draw_ms'}
                    and all(type(v) in (int,float) and np.isfinite(v) and 0<=v<=60000 for v in fields.values()),'JOINT_DRAW_BROWSER_DIAGNOSTICS')
            # This lock serializes append+fsync only. It does not block the
            # receive thread from accepting the next committed snapshot.
            with self.diagnostics.measure('draw.receipt_IO_lock'):
                with self.draw_io_lock:
                    with self.lock:require(not self.error,'JOINT_DRAW_REVOKED')
                    with (self.root/'display_receipts.jsonl').open('a',encoding='utf-8') as f:
                        self.diagnostics.call('draw.receipt_write',f.write,json.dumps(row,allow_nan=False)+'\n')
                        self.diagnostics.call('draw.receipt_flush',f.flush)
                        self.diagnostics.call('draw.receipt_fsync',os.fsync,f.fileno())
            with self.lock:
                require(not self.error,'JOINT_DRAW_REVOKED')
                self.drawn.add(serial)
            return dict(status='DRAW_IDENTITY_AND_PIXELS_VERIFIED', latency=sample, whole_run_acceptance='PENDING')
        finally:
            with self.lock:self.draw_pending.discard(serial)

    def stop(self, body=None):
        if not self.path: return self.status()
        if body and body.get('error'):
            self.error=str(body['error'])
            write(self.root/'ERROR_REQUEST.json',dict(run_id=self.scope['run_id'],error=self.error))
        self.stop_event.set()
        if self.client:
            try: self.last_status = self.client.call('stop')
            except (OSError,ValueError): pass
        return dict(status='STOP_REQUESTED_WAIT_INFLIGHT_ACK', stop_acknowledged=False)

    def recording(self, raw):
        require(self.path and self.control and len(raw) <= 300_000_000 and raw[:4] == bytes.fromhex('1a45dfa3'), 'JOINT_RECORDING_FORMAT')
        out = self.root/'recordings'; out.mkdir(exist_ok=True)
        path = out/(self.scope['run_id']+'_'+uuid.uuid4().hex+'.webm')
        with path.open('xb') as f: f.write(raw); f.flush(); os.fsync(f.fileno())
        receipt = dict(run_id=self.scope['run_id'], session_id=self.scope['session_id'], path=str(path), sha256=sha(path),
            evidence='GUI_CANVAS_RECORDING_PENDING_RUN_AUDIT', whole_run_acceptance='PENDING')
        write(path.with_suffix('.json'), receipt)
        return receipt

    def close(self):
        if self.control: self.stop()
        for thread in (self.capture_thread,self.thread):
            if thread: thread.join(2)
        for client in (self.client,self.input_client):
            if client: client.close()
        if self.path and not self.diagnostics_saved:
            self.diagnostics_saved=True
            try:self.diagnostics.save(self.root/'gui_host_diagnostics.json',self.scope['session_id'],self.scope['run_id'])
            except Exception as error:write(self.root/'gui_diagnostic_error.json',dict(error=str(error)))

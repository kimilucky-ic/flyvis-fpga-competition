"""Only this module owns VideoCapture. No FlyVis imports or WSL USB access."""
from __future__ import annotations
import csv
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from .common import ROOT, cv2_module, new_directory, sha256, utc_now, write_json

class CameraError(RuntimeError):
    pass

@dataclass(frozen=True)
class FramePacket:
    bgr: np.ndarray
    sequence: int
    received_monotonic_ns: int
    received_utc: str
    read_duration_s: float

class CameraSession:
    def init__(self, device_id=0, *, backend='dshow', width=640, height=480, fps=30):
        self.cv2 = cv2_module()
        self.device_id, self.sequence, self.timestamps = device_id, 0, []
        self.lock = ROOT / 'runtime' / 'camera.lock'
        self.lock.parent.mkdir(parents=True, exist_ok=True)
        self.cap = None
        self.closed = False
        self.owns_lock = False
        try:
            fd = os.open(self.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as error:
            raise CameraError(f'CAMERA_BUSY: camera owner lock exists: {self.lock}. Close its owner first; inspect PID if stale.') from error
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump({'pid': os.getpid(), 'device_id': device_id, 'created_utc': utc_now()}, handle)
        self.owns_lock = True
        try:
            flag = {'dshow': self.cv2.CAP_DSHOW, 'msmf': self.cv2.CAP_MSMF,
                    'any': self.cv2.CAP_ANY}[backend]
            self.cap = self.cv2.VideoCapture(int(device_id), flag)
            if not self.cap.isOpened():
                raise CameraError(f'CAMERA_UNAVAILABLE: device {device_id} ({backend}) cannot open. Check connection, Windows camera permissions and other camera apps.')
            self.cap.set(self.cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(self.cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(self.cv2.CAP_PROP_FPS, fps)
            self.cap.set(self.cv2.CAP_PROP_BUFFERSIZE, 1)  # backend may ignore this request
            self.info = {'device_id': device_id, 'backend': self.cap.getBackendName(),
                         'requested_resolution': [width, height], 'requested_fps': fps,
                         'reported_resolution': [int(self.cap.get(3)), int(self.cap.get(4))],
                         'reported_fps': float(self.cap.get(self.cv2.CAP_PROP_FPS)),
                         'buffer_size_reported': float(self.cap.get(self.cv2.CAP_PROP_BUFFERSIZE)),
                         'exposure_reported': float(self.cap.get(self.cv2.CAP_PROP_EXPOSURE)),
                         'opencv': self.cv2.__version__, 'pid': os.getpid()}
        except BaseException:
            self.close()
            raise

    def read_frame(self):
        if self.closed:
            raise CameraError('CAMERA_CLOSED: session already released')
        start = time.perf_counter_ns()
        ok, image = self.cap.read()
        received = time.perf_counter_ns()
        if not ok or image is None or image.size == 0:
            raise CameraError(f'CAMERA_READ_FAILED: no frame from device {self.device_id}')
        packet = FramePacket(image, self.sequence, received, utc_now(), (received-start)/1e9)
        self.sequence += 1
        self.timestamps.append(received)
        self.info['actual_resolution'] = [image.shape[1], image.shape[0]]
        return packet

    def status(self):
        fps = ((len(self.timestamps)-1)*1e9/(self.timestamps[-1]-self.timestamps[0])
               if len(self.timestamps)>1 else None)
        return {**self.info, 'schema': 'flyvis-camera-status-v1',
                'state': 'closed' if self.closed else 'open', 'frames_read': self.sequence,
                'measured_delivery_fps': fps, 'exposure_timestamp_available': False,
                'sensor_drop_count': None, 'capture_queue_length': None}

    def close(self):
        if self.cap is not None:
            self.cap.release()
        self.closed = True
        if self.owns_lock:
            self.lock.unlink(missing_ok=True)
            self.owns_lock = False

    def __enter__(self): return self
    def __exit__(self, *args): self.close()

def open_camera(device_id=0, **kwargs):
    return CameraSession(device_id, **kwargs)

def read_frame(camera):
    return camera.read_frame()

def probe_device(device_id, backend):
    cv2 = cv2_module()
    cap = cv2.VideoCapture(device_id, {'dshow': cv2.CAP_DSHOW, 'msmf': cv2.CAP_MSMF}[backend])
    try:
        if not cap.isOpened(): return {'device_id': device_id, 'backend': backend, 'available': False}
        start = time.perf_counter()
        ok, image = cap.read()
        return {'device_id': device_id, 'backend': backend, 'available': bool(ok and image is not None),
                'resolution': [image.shape[1], image.shape[0]] if ok else None,
                'reported_fps': cap.get(cv2.CAP_PROP_FPS), 'first_read_s': time.perf_counter()-start}
    finally: cap.release()

def scan_cameras(max_devices=4, timeout_s=8):
    # Probe serially in owned child processes: bound driver hangs, always release process resources.
    if not 1 <= max_devices <= 16: raise ValueError('max_devices must be in [1,16]')
    ROOT.joinpath('runtime').mkdir(exist_ok=True)
    lock = ROOT / 'runtime/camera.lock'
    try: fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error: raise CameraError('CAMERA_BUSY: cannot scan while another camera_pipeline session owns camera') from error
    with os.fdopen(fd, 'w') as handle: json.dump({'pid': os.getpid(), 'operation': 'scan'}, handle)
    results = []
    try:
        for device_id in range(max_devices):
            for backend in ('dshow','msmf'):
                command = [sys.executable, str(ROOT/'camera_test.py'), '_probe', '--device', str(device_id), '--backend', backend]
                try:
                    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout_s)
                    found = json.loads(result.stdout)
                    found['stderr'] = result.stderr[-1500:]
                    found['exit_code'] = result.returncode
                except (subprocess.TimeoutExpired, ValueError, IndexError) as error:
                    found = {'device_id': device_id, 'backend': backend, 'available': False, 'error': str(error)}
                results.append(found)
                if found.get('available'): break
    finally: lock.unlink(missing_ok=True)
    return results

def record_clip(camera, output, duration_s=6, *, preview=False):
    if not 0 < duration_s <= 30: raise ValueError('Recording duration must be in (0,30] seconds')
    output = new_directory(output)
    cv2 = camera.cv2
    raw = output/'raw_frames'
    raw.mkdir()
    records = []
    first = None
    deadline = None
    state = 'recording'
    write_json(output/'job_status.json', {'schema':'flyvis-camera-job-v1','job_id':output.name,'state':state,'created_utc':utc_now()})
    try:
        while first is None or time.perf_counter_ns() < deadline:
            packet = read_frame(camera)
            if first is None:
                first = packet.received_monotonic_ns
                deadline = first + int(duration_s*1e9)
            relative = (packet.received_monotonic_ns-first)/1e9
            name = f'frame_{len(records):06d}.png'
            before = time.perf_counter()
            if not cv2.imwrite(str(raw/name), packet.bgr, [cv2.IMWRITE_PNG_COMPRESSION,1]):
                raise CameraError('FRAME_SAVE_FAILED')
            records.append({'frame':len(records), 'camera_sequence':packet.sequence,
                            'relative_time_s':relative, 'received_monotonic_ns':packet.received_monotonic_ns,
                            'received_utc':packet.received_utc, 'read_duration_s':packet.read_duration_s,
                            'save_duration_s':time.perf_counter()-before, 'path':f'raw_frames/{name}'})
            if preview:
                view = packet.bgr.copy()
                cv2.putText(view, f"{relative:.2f}s | {camera.status()['measured_delivery_fps'] or 0:.1f} FPS | Q: stop", (10,25), cv2.FONT_HERSHEY_SIMPLEX,.6,(0,255,0),1)
                cv2.imshow('FlyVis camera_pipeline - raw capture', view)
                if cv2.waitKey(1)&0xff in (ord('q'),27): break
        if len(records)<2: raise CameraError('INSUFFICIENT_FRAMES: need at least two frames')
        times = np.array([r['relative_time_s'] for r in records], dtype=np.float64)
        fps = (len(times)-1)/(times[-1]-times[0])
        first_image = cv2.imread(str(raw/Path(records[0]['path']).name))
        shape = (len(records), *first_image.shape)
        frames = np.lib.format.open_memmap(output/'frames.npy', mode='w+', dtype=np.uint8, shape=shape)
        writer = cv2.VideoWriter(str(output/'clip.avi'), cv2.VideoWriter_fourcc(*'MJPG'), fps, (shape[2],shape[1]))
        if not writer.isOpened(): raise CameraError('VIDEO_WRITER_FAILED: MJPG codec unavailable')
        try:
            for i, row in enumerate(records):
                image = cv2.imread(str(output/row['path']), cv2.IMREAD_COLOR)
                if image.shape != shape[1:]: raise CameraError('FRAME_RESOLUTION_CHANGED')
                frames[i] = image
                writer.write(image)
        finally: writer.release()
        frames.flush()
        del frames
        np.save(output/'frame_times.npy', times, allow_pickle=False)
        with (output/'frame_timestamps.csv').open('w', newline='', encoding='utf-8') as handle:
            writer_csv = csv.DictWriter(handle, fieldnames=list(records[0])); writer_csv.writeheader();writer_csv.writerows(records)
        gaps = np.diff(times)
        metadata = {'schema':'flyvis-camera-recording-v1','source_kind':'real_windows_camera',
                    'created_utc':utc_now(),'capture':camera.status(),'frames_shape':list(shape),
                    'frames_dtype':'uint8 BGR','requested_duration_s':duration_s,'recorded_span_s':float(times[-1]),
                    'measured_delivery_fps':float(fps),'frame_interval_median_s':float(np.median(gaps)),
                    'frame_interval_max_s':float(gaps.max()),'large_gaps_gt_1_5_median':int((gaps>1.5*np.median(gaps)).sum()),
                    'timestamp_semantics':'host perf_counter_ns immediately after VideoCapture.read; not sensor exposure time',
                    'camera_sensor_drops':None,'actual_capture_queue_length':None,
                    'replay_video':'MJPG AVI, nominal constant FPS from measured frame delivery; timing authority is frame_times.npy',
                    'authoritative_pixels':'frames.npy and lossless PNG; AVI is lossy replay only',
                    'data_sha256':{name:sha256(output/name) for name in ('frames.npy','frame_times.npy','clip.avi','frame_timestamps.csv')}}
        write_json(output/'recording.json', metadata)
        state = 'complete'
        write_json(output/'job_status.json', {'schema':'flyvis-camera-job-v1','job_id':output.name,'state':state,'result':str(output),'frames':len(records)})
        return metadata
    except BaseException as error:
        write_json(output/'job_status.json', {'schema':'flyvis-camera-job-v1','job_id':output.name,'state':'failed','error':str(error),'saved_raw_frames':len(records)})
        raise
    finally:
        if preview: cv2.destroyAllWindows()

def preview_camera(camera, duration_s=10):
    cv2 = camera.cv2
    start = time.perf_counter()
    try:
        while time.perf_counter()-start < duration_s:
            packet = read_frame(camera)
            view = packet.bgr.copy()
            cv2.putText(view, f"device {camera.device_id} | {camera.status()['measured_delivery_fps'] or 0:.1f} FPS | Q: stop", (10,25),cv2.FONT_HERSHEY_SIMPLEX,.6,(0,255,0),1)
            cv2.imshow('FlyVis camera_pipeline - preview', view)
            if cv2.waitKey(1)&0xff in (ord('q'),27): break
        return camera.status()
    finally: cv2.destroyAllWindows()

"""Keep the existing camera open for placement, then record until phone completion.

No second collector or player. Original capture.record_clip writes every formal
pixel/timestamp. Readiness is emitted after first raw PNG, never on process launch.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import time
import uuid
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from camera_pipeline import capture
from camera_pipeline.common import sha256, utc_now, write_json
from camera_pipeline.phase4_phone_camera_20261010_r1 import camera_session as api
from camera_pipeline.phase4_phone_camera_20261010_r1.config import ROOT, write_new
from camera_pipeline.phase4_phone_camera_20261010_r1.geometry import native_geometry, overlay, screen_coverage


class CompletionGate:
    def init__(self, phone_path, session_id, post_s=1.):
        self.phone_path=Path(phone_path); self.session_id=session_id
        self.events_path=self.phone_path.parent/'events.jsonl'; self.last_poll_ns=None
        self.post_s=post_s; self.complete_observed_ns=None; self.reason=None

    def poll(self, now_ns):
        # Watch the append-only, session-specific server log rather than opening
        # presentation.json while Windows may be atomically replacing it.
        # An incomplete trailing JSON line is ignored until its newline arrives.
        if self.last_poll_ns is None or now_ns-self.last_poll_ns>=200_000_000:
            self.last_poll_ns=now_ns
            if self.events_path.exists():
                data=self.events_path.read_text(encoding='utf-8')
                lines=data.splitlines(keepends=True)
                for line in lines:
                    if not line.endswith('\n'): continue
                    event=json.loads(line)['client_event']['kind']
                    if event=='stop': self.reason='phone_stopped'; return True
                    if event=='complete' and self.complete_observed_ns is None:
                        self.complete_observed_ns=now_ns
        if self.complete_observed_ns is not None and now_ns-self.complete_observed_ns>=int(self.post_s*1e9):
            self.reason='phone_complete_plus_post_receipt_hold'; return True
        return False


class CoordinatedCV:
    def init__(self, delegate, relay, recording, control, gate):
        self.delegate=delegate; self.relay=relay; self.recording=recording
        self.control=control; self.gate=gate; self.ready=False
    def __getattr__(self, name): return getattr(self.delegate,name)
    def imshow(self, name, image):
        self.delegate.imshow(name,image)
        if not self.ready:
            first=self.recording/'raw_frames/frame_000000.png'
            if not first.is_file(): raise RuntimeError('READY requires saved raw frame')
            write_new(self.control/'recording_ready.json',{
                'schema':'phone-camera-recording-ready-v1','created_utc':utc_now(),
                'recording_path':str(self.recording),'first_raw_png_sha256':sha256(first),
                'first_recorded_receipt_monotonic_ns':self.relay.measurements[-1]['received_monotonic_ns'],
                'phone_session_id':self.gate.session_id,'raw_recording_has_started':True,
                'message':'READY: tap phone now; completion controls stop, not window startup'})
            self.ready=True
            print('RAW_RECORDING_READY: first PNG saved; tap phone now.',flush=True)
    def waitKey(self, delay):
        key=self.delegate.waitKey(delay)
        if key & 255 in (ord('q'),27):
            self.gate.reason='operator_stop'; return key
        if self.gate.poll(time.perf_counter_ns()):
            write_new(self.control/'capture_stopped.json',{
                'reason':self.gate.reason,'created_utc':utc_now(),
                'complete_observed_monotonic_ns':self.gate.complete_observed_ns,
                'last_recorded_receipt_monotonic_ns':self.relay.measurements[-1]['received_monotonic_ns'],
                'clock_semantics':'server completion observed, not optical alignment'})
            return ord('q')
        return key


def run(args):
    # Explicit user confirmation is recorded by operator; CLI cannot manufacture it.
    if not args.user_authorized: raise ValueError('Camera not opened: user authorization required')
    if not 6 <= args.max_record_s <= 30 or not 1 <= args.setup_timeout_s <= 120:
        raise ValueError('Bounded setup and capture required')
    phone_path,spec=api.read_presentation(args.phone_session)
    if spec['state']!='armed': raise ValueError('Prepare a fresh phone session and standby first')
    control=Path(args.control).resolve(); control.mkdir(parents=True,exist_ok=False)
    capture_id='camera_'+uuid.uuid4().hex
    recording=ROOT/'recordings'/capture_id
    gate=CompletionGate(phone_path,spec['phone_stimulus_session_id'],1.)
    write_new(control/'request.json',{'phone_path':str(phone_path),'phone_at_request':spec,
        'user_authorized':True,'recording_path':str(recording),'max_record_s':args.max_record_s,
        'setup_timeout_s':args.setup_timeout_s,'created_utc':utc_now()})
    with capture.open_camera(0,backend='dshow',width=640,height=480,fps=30) as camera:
        before=api.property_snapshot(camera); first=camera.read_frame()
        h,w=first.bgr.shape[:2]; centers,mask,geometry=native_geometry(w,h)
        window='FlyVis camera_pipeline - raw capture'; deadline=time.perf_counter()+args.setup_timeout_s
        packet=first; count=0; last_snapshot=0.; command=None
        while time.perf_counter()<deadline:
            camera.cv2.imshow(window,overlay(packet.bgr,camera.cv2,centers,mask))
            if time.perf_counter()-last_snapshot>=.5:
                # Mutable placement snapshots only. These are never neural pixels.
                temporary=control/'latest_setup_raw.tmp.png'
                if not camera.cv2.imwrite(str(temporary),packet.bgr): raise capture.CameraError('SETUP_SAVE_FAILED')
                temporary.replace(control/'latest_setup_raw.png')
                write_json(control/'camera_ready.json',{'created_utc':utc_now(),
                    'camera_state':'open_setup_only','sequence':packet.sequence,
                    'received_monotonic_ns':packet.received_monotonic_ns,'resolution_wh':[w,h],
                    'formal_recording_started':False,'phone_session_id':spec['phone_stimulus_session_id']})
                last_snapshot=time.perf_counter()
            key=camera.cv2.waitKey(1)&255
            if key in (ord('q'),27): raise ValueError('Setup cancelled; no formal capture')
            if (control/'GO.json').is_file():
                command=json.loads((control/'GO.json').read_text(encoding='utf-8'))
                if command.get('phone_session_id')!=spec['phone_stimulus_session_id'] or command.get('screen_reviewed') is not True:
                    raise ValueError('GO requires exact phone identity and current placement review')
                break
            packet=camera.read_frame(); count+=1
        if command is None: raise TimeoutError('Setup timeout; no formal capture')
        _,fresh=api.read_presentation(phone_path)
        if fresh['state']!='armed' or fresh['settings_sha256']!=spec['settings_sha256']:
            raise ValueError('Phone started or parameters changed before actual recording')
        polygon=np.asarray(command['screen_polygon_raw_xy'],dtype=float).reshape(4,2).tolist()
        coverage=screen_coverage(mask,polygon)
        if not coverage['all_footprints_inside_active_screen']: raise ValueError('Coverage not accepted')
        write_new(control/'setup_review_at_go.json',{'command':command,'coverage':coverage,
            'last_setup_sequence':packet.sequence,'last_setup_receipt_monotonic_ns':packet.received_monotonic_ns,
            'setup_frames_not_used_as_model_input':True})
        relay=api.CaptureRelay(camera,centers,mask,polygon)
        relay.cv2=CoordinatedCV(relay.cv2,relay,recording,control,gate)
        metadata=capture.record_clip(relay,recording,duration_s=args.max_record_s,preview=True)
        if gate.reason is None: gate.reason='bounded_capture_timeout'
        write_new(recording/'phone_at_capture_start.json',fresh)
        write_new(recording/'roi_measurements.json',relay.measurements)
        write_new(recording/'property_samples.json',relay.properties)
        binding={'schema':'flyvis-real-screen-capture-binding-v1','capture_id':capture_id,
            'comparison_id':capture_id,'phone_stimulus_session_id':spec['phone_stimulus_session_id'],
            'phone_presentation_path':str(phone_path),'phone_settings_sha256':spec['settings_sha256'],
            'source_kind':'real_camera_recapture_of_phone','created_utc':utc_now(),
            'phone_placement_confirmed_by_operator':True,'screen_coverage_reviewed_by_operator':True,
            'operator_notes':command.get('notes',''),'geometry':geometry,'coverage':coverage,
            'property_before':before,'property_requests':[],'property_after':api.property_snapshot(camera),
            'physical_exposure_mode_verified':False,'physical_screen_refresh_hz':None,
            'phone_to_sensor_optical_alignment_s':None,'recording_json_sha256':sha256(recording/'recording.json'),
            'raw_png_sha256':{p.name:sha256(p) for p in sorted((recording/'raw_frames').glob('*.png'))},
            'camera_raw_receipt_clock':metadata['timestamp_semantics'],'neural_inference':False,'board_used':False,
            'coordination_control_path':str(control),'stop_reason':gate.reason}
        write_new(recording/'capture_binding.json',binding)
        result={'recording_path':str(recording),'comparison_id':capture_id,'stop_reason':gate.reason,
            'recorded_span_s':metadata['recorded_span_s'],'frames':metadata['frames_shape'][0],
            'needs_raw_sequence_review':True,'neural_inference':False}
    write_new(control/'result.json',result)
    print(json.dumps(result,ensure_ascii=False),flush=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phone-session',type=Path,required=True)
    p.add_argument('--control',type=Path,required=True)
    p.add_argument('--user-authorized',action='store_true')
    p.add_argument('--max-record-s',type=float,default=20)
    p.add_argument('--setup-timeout-s',type=float,default=90)
    a=p.parse_args()
    try: run(a)
    except BaseException as error:
        target=Path(a.control)
        if target.is_dir(): write_json(target/'error.json',{'error':str(error),'created_utc':utc_now(),'neural_inference':False})
        raise
    finally:
        # Sole owner closes/releases camera through context, even on abort.
        from camera_pipeline.common import cv2_module
        cv2_module().destroyAllWindows()

"""Operator-started recording using the one existing Windows camera owner.

R starts saving after preview is already visible. The green RECORDING cue is
shown only after an actual PNG exists. No 403px placement requirement here.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys
import time
import uuid

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from camera_pipeline import capture
from camera_pipeline.common import cv2_module, sha256, utc_now, write_json
from camera_pipeline.phase4_phone_camera_20261010_r1.camera_session import property_snapshot, read_presentation
from camera_pipeline.phone_screen_rectification_20261011_r1.screen_import import HERE

PHONE_SESSIONS=HERE.parent/'phase4_real_phone_20261011_r1'/'phone_sessions'


def armed_phone():
    for path in sorted(PHONE_SESSIONS.glob('*/presentation.json'),key=lambda p:p.stat().st_mtime,reverse=True):
        try:
            _,doc=read_presentation(path)
            events=path.parent/'events.jsonl'
            if doc['state']=='armed' and events.is_file() and '"standby"' in events.read_text(encoding='utf-8'):
                return path,doc
        except (ValueError,OSError,json.JSONDecodeError):
            continue
    return None,None


class RecordingDisplay:
    def init__(self,cv,output): self.cv=cv;self.output=output;self.ready=False
    def __getattr__(self,name): return getattr(self.cv,name)
    def imshow(self,name,image):
        first=self.output/'raw_frames'/'frame_000000.png'
        if not first.is_file(): raise RuntimeError('Cannot display ready before saving actual original')
        if not self.ready:
            write_json(self.output/'recording_ready.json',{'created_utc':utc_now(),
                'first_raw_png_sha256':sha256(first),'raw_recording_has_started':True})
            print('RECORDING: first raw PNG saved. Tap phone NOW.',flush=True);self.ready=True
        view=image.copy()
        self.cv.rectangle(view,(0,40),(view.shape[1]-1,86),(0,80,0),-1)
        self.cv.putText(view,'RECORDING - TAP PHONE NOW | Q after final hold',(8,68),self.cv.FONT_HERSHEY_SIMPLEX,.55,(255,255,255),1)
        self.cv.imshow(name,view)


class CameraRelay:
    def init__(self,camera,output):
        self.camera=camera;self.cv2=RecordingDisplay(camera.cv2,output);self.properties=[];self.count=0
    def status(self): return self.camera.status()
    def read_frame(self):
        packet=self.camera.read_frame()
        if self.count%5==0:
            self.properties.append({'sequence':packet.sequence,'received_monotonic_ns':packet.received_monotonic_ns,
                'received_utc':packet.received_utc,'properties':property_snapshot(self.camera)})
        self.count+=1
        return packet


def record(args):
    if not args.user_authorized or not 6<=args.duration_s<=30 or not 10<=args.preview_timeout_s<=180:
        raise ValueError('Camera not opened: authorization and bounded preview/recording are required')
    output=HERE/'recordings'/('camera_'+uuid.uuid4().hex)
    cv=cv2_module(); window='Phone recording - R starts; Q quits'
    with capture.open_camera(0,backend='dshow',width=640,height=480,fps=30) as camera:
        deadline=time.monotonic()+args.preview_timeout_s
        while time.monotonic()<deadline:
            packet=camera.read_frame();view=packet.bgr.copy()
            cv.putText(view,'PREVIEW ONLY | R: record | Q: quit',(8,24),cv.FONT_HERSHEY_SIMPLEX,.6,(0,255,255),1)
            cv.putText(view,'Keep the WHOLE white square visible; no distance gate',(8,48),cv.FONT_HERSHEY_SIMPLEX,.47,(0,255,255),1)
            cv.imshow(window,view);key=cv.waitKey(1)&255
            if key in (ord('q'),27): return {'status':'cancelled_no_formal_recording'}
            if key==ord('r'):
                phone_path,phone=armed_phone()
                before=property_snapshot(camera)
                cv.destroyWindow(window)
                relay=CameraRelay(camera,output)
                metadata=capture.record_clip(relay,output,duration_s=args.duration_s,preview=True)
                write_json(output/'property_samples.json',relay.properties)
                after=property_snapshot(camera)
                context={'schema':'screen-B-selfserve-camera-v1','created_utc':utc_now(),
                    'source_kind':'real_windows_camera','operator_start':'R in already open preview',
                    'phone_original_is_neural_input':False,'property_before':before,'property_after':after,
                    'physical_property_modes_verified':False,'screen_calibration':'offline fixed homography; not yet accepted',
                    'phone_session_path':str(phone_path) if phone_path else None,
                    'phone_stimulus_session_id':phone['phone_stimulus_session_id'] if phone else None,
                    'phone_settings_sha256':phone['settings_sha256'] if phone else None,
                    'phone_complete_log_verified':False,'raw_clock':metadata['timestamp_semantics'],
                    'neural_inference':False,'board_used':False}
                if phone_path:
                    write_json(output/'phone_at_capture_start.json',phone)
                    shutil.copyfile(phone_path,output/'phone_presentation_after_capture.json')
                    shutil.copyfile(phone_path.parent/'events.jsonl',output/'phone_events.jsonl')
                    entries=[json.loads(line) for line in (output/'phone_events.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
                    kinds=[e['client_event']['kind'] for e in entries]
                    context['phone_complete_log_verified']=kinds.count('start')==1 and 'complete' in kinds
                context['retained_extra_files_sha256']={p.name:sha256(p) for p in output.iterdir()
                    if p.is_file() and p.name not in ('selfserve_context.json',)}
                write_json(output/'selfserve_context.json',context)
                return {'status':'raw_recording_complete_pending_screen_review','recording_path':str(output),
                    'frames':metadata['frames_shape'][0],'span_s':metadata['recorded_span_s'],
                    'phone_playback_complete_logged':context['phone_complete_log_verified'],'neural_inference':False}
    raise TimeoutError('Preview timed out; no formal recording')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--user-authorized',action='store_true')
    p.add_argument('--duration-s',type=float,default=12);p.add_argument('--preview-timeout-s',type=float,default=180)
    args=p.parse_args()
    try: print(json.dumps(record(args),ensure_ascii=False,indent=2),flush=True)
    finally: cv2_module().destroyAllWindows()

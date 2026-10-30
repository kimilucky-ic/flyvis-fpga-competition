"""Gated preview/recording wrapper. Only existing capture.CameraSession opens USB."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
import time
import uuid
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from camera_pipeline import capture
from camera_pipeline.common import sha256,utc_now,write_json
from camera_pipeline.phase4_phone_camera_20261010_r1.config import ROOT,settings_sha,write_new
from camera_pipeline.phase4_phone_camera_20261010_r1.geometry import native_geometry,overlay,roi_statistics,screen_coverage

PROPERTIES=('EXPOSURE','AUTO_EXPOSURE','GAIN','BRIGHTNESS','CONTRAST','GAMMA','AUTO_WB',
            'WB_TEMPERATURE','FOCUS','AUTOFOCUS','FPS','BUFFERSIZE','FRAME_WIDTH','FRAME_HEIGHT')

def property_snapshot(camera):
    result={}
    for name in PROPERTIES:
        key='CAP_PROP_'+name;code=getattr(camera.cv2,key,None)
        try: value=float(camera.cap.get(code)) if code is not None else None
        except Exception: value=None
        if value is not None and not math.isfinite(value): value=None
        result[name]={'reported_value':value,'support_confirmed':False,
                      'meaning':'backend-specific; zero may mean unsupported; not sensor exposure time'}
    return result

def apply_requests(camera,args):
    results=[]
    for name,value in [('AUTO_EXPOSURE',args.auto_exposure_value),('EXPOSURE',args.exposure_value)]:
        if value is None: continue
        if not math.isfinite(value): raise ValueError('Camera property request must be finite')
        key=getattr(camera.cv2,'CAP_PROP_'+name)
        accepted=bool(camera.cap.set(key,value));readback=float(camera.cap.get(key))
        results.append({'property':name,'requested':value,'set_return_bool':accepted,
                        'readback':readback if math.isfinite(readback) else None,'physical_mode_verified':False})
    return results

def read_presentation(path,*,finished=False):
    path=Path(path).resolve();spec=json.loads(path.read_text(encoding='utf-8'))
    if spec.get('schema')!='flyvis-phone-presentation-session-v1' or spec.get('validation_only') is not False:
        raise ValueError('Formal camera input rejects software validation sessions')
    if spec.get('settings_sha256')!=settings_sha(spec['settings']): raise ValueError('Phone parameter identity mismatch')
    if spec['settings']['family']=='calibration': raise ValueError('Calibration is setup only; choose a formal stimulus family')
    if spec.get('state') not in (('complete','stop') if finished else ('armed','playing')):
        raise ValueError('Phone must be freshly armed/playing for capture, then finished before freezing input')
    session=spec.get('phone_stimulus_session_id','')
    if len(session)!=32 or any(c not in '0123456789abcdef' for c in session): raise ValueError('Invalid phone session ID')
    return path,spec

def guard(args):
    if not args.phone_ready_confirmed:
        raise ValueError('CAMERA_NOT_OPENED: user phone placement confirmation required (--phone-ready-confirmed)')
    if args.command=='record':
        if not args.screen_coverage_confirmed or not args.phone_session or args.screen_corners is None:
            raise ValueError('CAMERA_NOT_OPENED: recording requires reviewed screen coverage, four corners and armed phone session')
        _,spec=read_presentation(args.phone_session)
        if spec['state']!='armed':raise ValueError('CAMERA_NOT_OPENED: prepare a new phone session and enter standby before recording')
        required=spec['settings']['pre_s']+spec['settings']['active_s']+spec['settings']['post_s']+2
        if args.seconds<required:raise ValueError(f'CAMERA_NOT_OPENED: need >= {required:g}s for this trial plus startup margin')
    if not 0<args.seconds<=30: raise ValueError('Bounded session requires seconds in (0,30]')
    if args.width<403 or args.height<403 or not math.isfinite(args.fps) or args.fps<=0:
        raise ValueError('CAMERA_NOT_OPENED: request a raw frame with complete footprints and positive finite FPS')

class OverlayCV2:
    def init__(self,real,relay):self.real=real;self.relay=relay
    def __getattr__(self,name):return getattr(self.real,name)
    def imshow(self,name,image):
        self.real.imshow(name,overlay(image,self.real,self.relay.centers,self.relay.mask,self.relay.polygon))

class CaptureRelay:
    def init__(self,camera,centers,mask,polygon):
        self.camera=camera;self.centers=centers;self.mask=mask;self.polygon=polygon
        self.cv2=OverlayCV2(camera.cv2,self);self.measurements=[];self.properties=[]
    def status(self):return self.camera.status()
    def read_frame(self):
        packet=self.camera.read_frame()
        if packet.bgr.shape[:2]!=self.mask.shape: raise ValueError('Resolution changed during capture')
        self.measurements.append({'camera_sequence':packet.sequence,'received_monotonic_ns':packet.received_monotonic_ns,
                                  **roi_statistics(packet.bgr,self.mask)})
        if len(self.measurements)%30==1:
            self.properties.append({'camera_sequence':packet.sequence,'reported':property_snapshot(self.camera)})
        return packet

def run(args):
    guard(args) # Always before open_camera; even bad/missing session cannot touch camera.
    presentation_path,spec=read_presentation(args.phone_session) if args.command=='record' else (None,None)
    run_id=uuid.uuid4().hex
    output=ROOT/('recordings' if args.command=='record' else 'preview_checks')/('camera_'+run_id)
    output.parent.mkdir(parents=True,exist_ok=True)
    polygon=np.asarray(args.screen_corners,dtype=float).reshape(4,2).tolist() if args.screen_corners is not None else []
    with capture.open_camera(args.device,backend=args.backend,width=args.width,height=args.height,fps=args.fps) as camera:
        before=property_snapshot(camera);requests=apply_requests(camera,args)
        first=camera.read_frame();h,w=first.bgr.shape[:2];centers,mask,geometry=native_geometry(w,h)
        coverage=screen_coverage(mask,polygon) if polygon else None
        if args.command=='record' and not coverage['all_footprints_inside_active_screen']:
            raise ValueError('SCREEN_COVERAGE_FAILED: reposition phone; no geometric correction is performed')
        if args.command=='preview':
            output.mkdir(exist_ok=False);window='Phase4 phone placement - raw coordinates'
            camera.cv2.namedWindow(window,camera.cv2.WINDOW_AUTOSIZE)
            def mouse(event,x,y,flags,param):
                if event==camera.cv2.EVENT_LBUTTONDOWN and len(polygon)<4: polygon.append([x,y])
            camera.cv2.setMouseCallback(window,mouse)
            start=time.perf_counter();packet=first;measurements=[]
            try:
                while time.perf_counter()-start<args.seconds:
                    measurements.append({'sequence':packet.sequence,'received_monotonic_ns':packet.received_monotonic_ns,
                                         'received_utc':packet.received_utc,**roi_statistics(packet.bgr,mask)})
                    camera.cv2.imshow(window,overlay(packet.bgr,camera.cv2,centers,mask,polygon))
                    key=camera.cv2.waitKey(1)&255
                    if key in (ord('q'),27):break
                    if key==ord('c'):polygon.clear()
                    packet=camera.read_frame()
                coverage=screen_coverage(mask,polygon) if len(polygon)==4 else None
                camera.cv2.imwrite(str(output/'last_raw_frame.png'),packet.bgr)
                camera.cv2.imwrite(str(output/'last_overlay.png'),overlay(packet.bgr,camera.cv2,centers,mask,polygon))
            finally:camera.cv2.destroyAllWindows()
            report={'schema':'phone-camera-placement-check-v1','created_utc':utc_now(),'camera':camera.status(),
                    'geometry':geometry,'coverage':coverage,'property_before':before,'property_requests':requests,
                    'property_after':property_snapshot(camera),'measurements':measurements,
                    'preview_frames_not_used_as_model_input':True,'all_preview_frames_archived':False,
                    'manual_grayscale_focus_flicker_check_required':True}
            write_new(output/'placement_check.json',report)
            print(json.dumps({'placement_check':str(output/'placement_check.json'),'coverage':coverage},ensure_ascii=False))
            return report
        relay=CaptureRelay(camera,centers,mask,polygon)
        write_new(ROOT/'capture_requests'/('camera_'+run_id+'.json'),{
            'schema':'phone-camera-recording-request-v1','capture_id':'camera_'+run_id,'recording_path':str(output),
            'requested_utc':utc_now(),'requested_duration_s':args.seconds,'phone_at_start':spec,
            'phone_presentation_path':str(presentation_path),'geometry':geometry,'coverage':coverage,
            'property_before':before,'property_requests':requests,'operator_notes':args.notes,
            'status':'request_only; recording/job_status.json is execution authority'})
        # First frame is a setup/resolution check; recorded frames/timestamps remain root recorder's actual receipts.
        print('Recording now. Press START on phone; keep screen and camera fixed.',flush=True)
        metadata=capture.record_clip(relay,output,duration_s=args.seconds,preview=True)
        write_new(output/'phone_at_capture_start.json',spec)
        write_new(output/'roi_measurements.json',relay.measurements)
        write_new(output/'property_samples.json',relay.properties)
        binding={'schema':'flyvis-real-screen-capture-binding-v1','capture_id':'camera_'+run_id,
                 'comparison_id':'camera_'+run_id,'phone_stimulus_session_id':spec['phone_stimulus_session_id'],
                 'phone_presentation_path':str(presentation_path),'phone_settings_sha256':spec['settings_sha256'],
                 'source_kind':'real_camera_recapture_of_phone','created_utc':utc_now(),
                 'phone_placement_confirmed_by_operator':True,'screen_coverage_reviewed_by_operator':True,
                 'operator_notes':args.notes,'geometry':geometry,'coverage':coverage,'property_before':before,
                 'property_requests':requests,'property_after':property_snapshot(camera),
                 'physical_exposure_mode_verified':False,'physical_screen_refresh_hz':None,
                 'phone_to_sensor_optical_alignment_s':None,'recording_json_sha256':sha256(output/'recording.json'),
                 'raw_png_sha256':{p.name:sha256(p) for p in sorted((output/'raw_frames').glob('*.png'))},
                 'camera_raw_receipt_clock':metadata['timestamp_semantics'],'neural_inference':False,'board_used':False}
        write_new(output/'capture_binding.json',binding)
        print(json.dumps({'recording':str(output),'capture_id':binding['capture_id'],'comparison_id':binding['comparison_id'],
                          'measured_camera_fps':metadata['measured_delivery_fps'],'neural_inference':False},ensure_ascii=False))
        return binding

def parser():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=('preview','record'))
    p.add_argument('--phone-ready-confirmed',action='store_true');p.add_argument('--screen-coverage-confirmed',action='store_true')
    p.add_argument('--phone-session',type=Path);p.add_argument('--screen-corners',type=float,nargs=8)
    p.add_argument('--device',type=int,default=0);p.add_argument('--backend',choices=('dshow','msmf'),default='dshow')
    p.add_argument('--width',type=int,default=640);p.add_argument('--height',type=int,default=480);p.add_argument('--fps',type=float,default=30)
    p.add_argument('--seconds',type=float,default=8);p.add_argument('--auto-exposure-value',type=float);p.add_argument('--exposure-value',type=float)
    p.add_argument('--notes',default='');return p

if __name__=='__main__':
    try:run(parser().parse_args())
    except (ValueError,capture.CameraError) as error:raise SystemExit(str(error))

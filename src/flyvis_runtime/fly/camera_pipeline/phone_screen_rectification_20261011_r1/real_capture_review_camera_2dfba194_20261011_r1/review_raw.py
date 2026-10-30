"""Read-only real capture QC. Feature motion is DIAGNOSTIC ONLY, never rectification.

Neural input would use the one initial homography unchanged. No neural inference.
"""
from pathlib import Path
import csv
import json
import sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from camera_pipeline.common import cv2_module, sha256, write_json, utc_now
from camera_pipeline.phase4_phone_camera_20261010_r1.geometry import native_geometry

ROOT=Path(__file__).resolve().parent
source=ROOT/'source'
source=json.loads((source/'source.json').read_text(encoding='utf-8'))
recording=Path(source['source_path'])
cv=cv2_module()
frames=np.load(source['frames_path'],mmap_mode='r',allow_pickle=False)
times=np.load(source/'source_time.npy',allow_pickle=False)
with (recording/'frame_timestamps.csv').open(encoding='utf-8',newline='') as handle: stamps=list(csv.DictReader(handle))
context=json.loads((recording/'selfserve_context.json').read_text(encoding='utf-8'))
for name,digest in context['retained_extra_files_sha256'].items():
    if sha256(recording/name)!=digest: raise ValueError('Recording changed '+name)
pngs=sorted((recording/'raw_frames').glob('*.png'))
if len(pngs)!=len(frames) or len(stamps)!=len(frames): raise ValueError('Count mismatch')
for i,path in enumerate(pngs):
    if not np.array_equal(cv.imread(str(path)),frames[i]): raise ValueError('Lossless PNG/npy mismatch '+str(i))
ns=np.array([int(row['received_monotonic_ns']) for row in stamps],dtype=np.int64)
if not np.allclose(times,(ns-ns[0])/1e9,rtol=0,atol=1e-12): raise ValueError('Source clocks differ')
cal=json.loads((ROOT/'calibration_proposal'/'calibration.json').read_text(encoding='utf-8'))
quad=np.array(cal['selected_corners'],dtype=np.float32)
matrix=np.array(cal['transform']['raw_to_render_homography'])
inverse=np.array(cal['transform']['render_to_raw_homography'])
centers,mask,_=native_geometry(640,640)
ys,xs=np.nonzero(mask)
pixels=cv.perspectiveTransform(np.column_stack([xs,ys]).astype(np.float32)[None],inverse)[0]
raw_centers=cv.perspectiveTransform(centers.astype(np.float32)[None],inverse)[0]
# Features come from the static phone title/header, border and lower control area.
# The moving black/white canvas is EXCLUDED. Motion estimates only flag quality;
# they are never applied to pixels that enter the neural input.
feature_mask=np.zeros((480,640),np.uint8)
cv.fillConvexPoly(feature_mask,np.array([[315,64],[486,71],[484,440],[302,442]],np.int32),255)
cv.fillConvexPoly(feature_mask,np.round(quad).astype(np.int32),0)
gray0=cv.cvtColor(np.asarray(frames[0]),cv.COLOR_BGR2GRAY)
anchor=cv.goodFeaturesToTrack(gray0,maxCorners=140,qualityLevel=.005,minDistance=3,blockSize=5,mask=feature_mask)
if anchor is None or len(anchor)<12: raise ValueError('Too few phone-body QC features')
anchor=anchor[:,0];tracked=anchor.copy();alive=np.ones(len(anchor),bool);previous=gray0
trajectory=[];quads=[];metrics=[]
for i,image in enumerate(frames):
    gray=cv.cvtColor(np.asarray(image),cv.COLOR_BGR2GRAY)
    if i:
        now,status,_=cv.calcOpticalFlowPyrLK(previous,gray,tracked.astype(np.float32)[:,None],None,
            winSize=(21,21),maxLevel=3,criteria=(cv.TERM_CRITERIA_EPS|cv.TERM_CRITERIA_COUNT,30,.01))
        back,backstatus,_=cv.calcOpticalFlowPyrLK(gray,previous,now,None,winSize=(21,21),maxLevel=3,
            criteria=(cv.TERM_CRITERIA_EPS|cv.TERM_CRITERIA_COUNT,30,.01))
        fb=np.linalg.norm(back[:,0]-tracked,axis=1)
        alive &= (status[:,0]==1)&(backstatus[:,0]==1)&(fb<1.2)
        tracked=now[:,0]
    previous=gray
    valid=alive & np.isfinite(tracked).all(axis=1)
    if valid.sum()>=12:
        motion,inlier=cv.findHomography(anchor[valid],tracked[valid],cv.RANSAC,2.0)
    else: motion=None;inlier=None
    if i==0: motion=np.eye(3);inlier=np.ones((len(anchor),1),np.uint8)
    if motion is not None and inlier.sum()>=10:
        current_quad=cv.perspectiveTransform(quad[None],motion)[0]
        edges=np.roll(current_quad,-1,axis=0)-current_quad
        cross=edges[:,0,None]*(pixels[None,:,1]-current_quad[:,1,None])-edges[:,1,None]*(pixels[None,:,0]-current_quad[:,0,None])
        inside=(cross>=0).all(axis=0)|(cross<=0).all(axis=0)
        outside=int((~inside).sum())
        displacement=current_quad.mean(axis=0)-quad.mean(axis=0)
    else: current_quad=None;outside=None;displacement=[None,None]
    quads.append(current_quad)
    rectified=cv.warpPerspective(np.asarray(image),matrix,(640,640),flags=cv.INTER_LINEAR,borderMode=cv.BORDER_CONSTANT,borderValue=0)
    luminance=np.asarray(Image.fromarray(rectified[:,:,::-1]).convert('L'),dtype=np.float32)
    values=luminance[mask]
    trajectory.append({'frame':i,'source_time_s':float(times[i]),'received_utc':stamps[i]['received_utc'],
        'valid_feature_tracks':int(valid.sum()),'ransac_inliers':int(inlier.sum()) if inlier is not None else 0,
        'tracked_screen_dx_px':float(displacement[0]) if displacement[0] is not None else None,
        'tracked_screen_dy_px':float(displacement[1]) if displacement[1] is not None else None,
        'outside_fixed_sampling_pixels':outside,'outside_fraction':outside/len(pixels) if outside is not None else None,
        'tracked_screen_quad':current_quad.tolist() if current_quad is not None else None,
        'diagnostic_motion_matrix':motion.tolist() if motion is not None else None,
        'fixed_sampling_gray_mean_0_255':float(values.mean()),'fixed_sampling_fraction_gt_180':float((values>180).mean()),
        'fixed_sampling_fraction_lt_60':float((values<60).mean()),'dynamic_matrix_used_for_neural_pixels':False})

write_json(ROOT/'frame_quality.json',trajectory)
fieldnames=[key for key in trajectory[0] if key not in ('tracked_screen_quad','diagnostic_motion_matrix')]
with (ROOT/'frame_quality.csv').open('x',encoding='utf-8',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=fieldnames);writer.writeheader();writer.writerows([{key:r[key] for key in fieldnames} for r in trajectory])

indices=[0,80,110,130,150,170,200,260,350]
sheet=Image.new('RGB',(960,780),'#202020');draw=ImageDraw.Draw(sheet)
for tile,index in enumerate(indices):
    view=np.asarray(frames[index]).copy()
    for x,y in raw_centers: cv.circle(view,(int(round(x)),int(round(y))),1,(0,255,0),-1)
    cv.polylines(view,[np.round(quad).astype(np.int32)],True,(0,200,255),1)
    if quads[index] is not None: cv.polylines(view,[np.round(quads[index]).astype(np.int32)],True,(255,255,0),1)
    cv.imwrite(str(ROOT/f'qc_frame_{index:06d}.png'),view)
    tile_image=Image.fromarray(view[:,:,::-1]).crop((170,45,520,480)).resize((320,230))
    x0=(tile%3)*320;y0=(tile//3)*260
    sheet.paste(tile_image,(x0,y0))
    row=trajectory[index]
    draw.text((x0+5,y0+232),f"frame {index} | {times[index]:.3f}s | outside {row['outside_fraction']:.1%}" if row['outside_fraction'] is not None else f'frame {index}: QC UNKNOWN',fill='white')
sheet.save(ROOT/'screen_motion_review.png')

events=[json.loads(line) for line in (recording/'phone_events.jsonl').read_text(encoding='utf-8').splitlines()]
markers=[{'kind':r['client_event']['kind'],'server_received_utc':r['server_received_utc'],
    'server_receipt_relative_to_first_camera_receipt_s':(int(r['server_received_monotonic_ns'])-int(ns[0]))/1e9,
    'not_optical_alignment':True,'client_event':r['client_event']}
    for r in events if r['client_event']['kind'] in ('start','complete','stop')]
first_outside=next((r for r in trajectory if r['outside_fixed_sampling_pixels'] not in (None,0)),None)
known=[r for r in trajectory if r['outside_fraction'] is not None]
report={'schema':'real-phone-capture-quality-v1','created_utc':utc_now(),'capture_id':recording.name,
    'source_is_camera':True,'raw_file_and_all_351_PNG_vs_npy_identity':'PASS','source_receipt_clock_alignment':'PASS',
    'recording_complete':True,'frames':len(frames),'resolution_wh':[640,480],'span_s':float(times[-1]),
    'measured_delivery_fps':float((len(times)-1)/times[-1]),'phone_playback_complete_logged':True,
    'phone_session_id':context['phone_stimulus_session_id'],'phone_settings_sha256':context['phone_settings_sha256'],
    'phone_event_markers':markers,'initial_screen_quad_raw_xy':quad.tolist(),
    'QC_motion_model':'Phone-body LK forward/backward + RANSAC anchored homography; active moving canvas excluded; diagnostic only, not precise optical calibration',
    'QC_frames_with_pose_estimate':len(known),'first_estimated_sample_outside':first_outside,
    'last_estimated_screen_shift_xy_px':[trajectory[-1]['tracked_screen_dx_px'],trajectory[-1]['tracked_screen_dy_px']],
    'max_estimated_outside_fraction':max(r['outside_fraction'] for r in known),
    'physical_exposure_mode_verified':False,'physical_screen_refresh_hz':None,
    'neural_inference':False,'frozen_stimulus':False,'board_used':False,
    'control_quality_status':'PENDING_MANUAL_QC_REVIEW','phone_motion_is_confounded_with_stimulus_motion':True}
write_json(ROOT/'raw_quality_report.json',report)
print(json.dumps({'report':str(ROOT/'raw_quality_report.json'),'frames':len(frames),
    'pose_frames':len(known),'first_outside_frame':first_outside['frame'] if first_outside else None,
    'first_outside_time_s':first_outside['source_time_s'] if first_outside else None,
    'last_dx_dy_px':report['last_estimated_screen_shift_xy_px'],
    'max_outside_fraction':report['max_estimated_outside_fraction'],'neural_inference':False},indent=2))

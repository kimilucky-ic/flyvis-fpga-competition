"""Synthetic SOFTWARE validation only: no camera, neural network or board execution."""
from __future__ import annotations
import csv
import json
from pathlib import Path
import sys
import uuid
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from camera_pipeline.common import cv2_module, sha256, write_json, utc_now
from camera_pipeline.adapter import render_bgr_frames, resample_hex
from camera_pipeline.phone_screen_rectification_20261011_r1.screen_import import (
    HERE, ingest, calibrate, freeze, load_input, fixed_transform, validate_times, bright_screen_candidates)


def run():
    cv=cv2_module();output=HERE/'validation'/('software_'+uuid.uuid4().hex);output.mkdir(parents=True)
    quad=np.array([[200,110],[440,90],[460,350],[180,370]],dtype=np.float32)
    matrix,inverse,centers,mask,transform=fixed_transform(quad,640,480)
    checks=[]
    def checked(name,value):
        if not value: raise AssertionError(name)
        checks.append({'check':name,'passed':True})
    checked('screen quad can be smaller than original 403 pixel sampling span',np.ptp(quad[:,0])<403 and np.ptp(quad[:,1])<403)
    reprojection=cv.perspectiveTransform(cv.perspectiveTransform(centers.astype(np.float32)[None],inverse),matrix)[0]
    checked('721 centers inverse and forward geometry match',np.max(np.abs(reprojection-centers))<.001)
    for bad in (quad[::-1],[[100,100],[101,100],[101,101],[100,101]],[[0,0],[500,400],[500,0],[0,400]]):
        try: fixed_transform(bad,640,480)
        except ValueError: pass
        else: raise AssertionError('Bad winding/degenerate quad accepted')
    checked('mirrored crossing and tiny geometry rejected',True)
    for times in ([0,0,.1],[0,.1,.09],[0,float('nan'),.1]):
        try: validate_times(times)
        except ValueError: pass
        else: raise AssertionError('Bad source time accepted')
    checked('duplicate backwards and nonfinite timestamps rejected',True)
    metrics=[];first_raw=None;last_frames=None
    x=np.arange(640)[None,:];y=np.arange(640)[:,None]
    for direction,coordinate,increasing in [('right',x,True),('left',x,False),('down',y,True),('up',y,False)]:
        canvas=[];raw=[];rectified=[]
        for i,edge in enumerate(np.linspace(0,640,17)):
            white=(coordinate>=edge) if increasing else (coordinate<640-edge)
            gray=np.broadcast_to(white,(640,640)).astype(np.uint8)*255
            frame=np.repeat(gray[:,:,None],3,axis=2)
            canvas.append(frame)
            phone=cv.warpPerspective(frame,inverse,(640,480),flags=cv.INTER_LINEAR,borderMode=cv.BORDER_CONSTANT,borderValue=0)
            raw.append(phone)
            rectified.append(cv.warpPerspective(phone,matrix,(640,640),flags=cv.INTER_LINEAR,borderMode=cv.BORDER_CONSTANT,borderValue=0))
        hexes,coords,_=render_bgr_frames(np.stack(rectified),spatial_policy='native')
        expected_centers=np.array([[r['render_column'],r['render_row']] for r in coords])
        checked(direction+' official centers preserved',np.array_equal(expected_centers,centers))
        crossing=np.argmax(hexes<.5,axis=0)
        spatial=centers[:,0] if direction in ('left','right') else centers[:,1]
        corr=float(np.corrcoef(crossing,spatial)[0,1])
        checked(direction+' OFF crossing direction preserved',corr>.98 if increasing else corr<-.98)
        checked(direction+' endpoint luminance retained',np.max(hexes[0]-1)<1e-6 and np.min(hexes[0])>.99 and np.max(hexes[-1])<.01)
        irregular=np.arange(17,dtype=np.float64)/30;irregular[8:]+=.012
        stimulus,grid,alignment=resample_hex(hexes,irregular,dt_s=.005,method='zoh')
        index=np.searchsorted(irregular,grid,side='right')-1
        checked(direction+' causal ZOH actually resamples values',np.array_equal(stimulus[0,:,0],hexes[index]) and all(not a['uses_future_frame'] for a in alignment) and grid[-1]<=irregular[-1])
        metrics.append({'direction':direction,'crossing_space_correlation':corr,'frames':17,'model_steps':len(grid)})
        if direction=='right': first_raw=raw[0];last_frames=raw
    candidates=bright_screen_candidates(first_raw)
    checked('automatic white-screen proposal finds synthetic phone quad',bool(candidates) and np.max(np.abs(np.asarray(candidates[0]['corners'])-quad))<=4)
    movie=output/'synthetic_phone_fixture.avi'
    writer=cv.VideoWriter(str(movie),cv.VideoWriter_fourcc(*'MJPG'),30,(640,480))
    if not writer.isOpened(): raise RuntimeError('Fixture codec unavailable')
    try:
        for image in last_frames: writer.write(image)
    finally: writer.release()
    source_dir=output/'source';source=ingest(movie,source_dir,'digital_stimulus',provenance_note='Explicit synthetic software fixture, not camera capture')
    checked('file decoder timestamps match known 30fps fixture',np.allclose(np.load(source_dir/'source_time.npy'),np.arange(17)/30,atol=1e-9,rtol=0))
    calibration_dir=output/'calibration';calibrate(source_dir,calibration_dir,corners=quad)
    try: freeze(source_dir,calibration_dir/'calibration.json',output/'unreviewed',reviewed=False)
    except ValueError: pass
    else: raise AssertionError('Unreviewed source accepted')
    checked('unreviewed calibration freeze rejected',True)
    identity,input_dir=freeze(source_dir,calibration_dir/'calibration.json',output/'frozen',reviewed=True,
        review_note='Synthetic known-geometry software fixture only; no real recording or activity acceptance')
    loaded,replay,t,activity=load_input(input_dir)
    checked('frozen [1,N,1,721] float32 in [0,1]',replay.shape==(1,len(t),1,721) and replay.dtype==np.float32 and np.isfinite(replay).all() and replay.min()>=0 and replay.max()<=1)
    checked('source/input/post-update clocks stay distinct',np.array_equal(activity,t+.005) and t[-1]<=source['source_span_s'])
    checked('synthetic input cannot claim actual camera or neural mode',not identity['source_is_camera'] and identity['comparison_id'].startswith('digital_rectB_') and all(m['status']=='not_run' for m in identity['modes'].values()))
    checked('fixed rectified pixels reproducible for every frame',np.array_equal(np.load(identity['rectified_frames_path'],mmap_mode='r'),np.stack([
        cv.warpPerspective(f,matrix,(640,640),flags=cv.INTER_LINEAR,borderMode=cv.BORDER_CONSTANT,borderValue=0)
        for f in np.load(source['frames_path'],mmap_mode='r')])))
    again=load_input(input_dir)
    checked('independent sealed readback identical and read-only',np.array_equal(replay,again[1]) and not replay.flags.writeable)
    with (input_dir/'three_clock_alignment.csv').open(encoding='utf-8',newline='') as handle: rows=list(csv.DictReader(handle))
    checked('video file does not fabricate camera UTC or receipt ns',all(r['source_received_utc']=='' and r['source_received_monotonic_ns']=='' for r in rows))
    with (input_dir/'raw_sampling_coordinates.csv').open(encoding='utf-8',newline='') as handle: coordinates=list(csv.DictReader(handle))
    checked('raw inverse mapping documents 721 centers and kernel quadrilaterals',len(coordinates)==721 and len(coordinates[0])==13)
    result={'schema':'screen-B-software-validation-v1','created_utc':utc_now(),'status':'PASS',
        'scope':'SYNTHETIC_SOFTWARE_ONLY','camera_opened':False,'real_phone_video_imported':False,
        'neural_inference':False,'board_used':False,'checks':checks,'direction_metrics':metrics,
        'fixture_path':str(movie),'fixture_sha256':sha256(movie),'input_path':str(input_dir),
        'comparison_id':identity['comparison_id'],'shape':identity['shape'],'opencv':cv.__version__,
        'real_recorded_screen_review_pending':True,'selfserve_hardware_recording_tested':False}
    write_json(output/'result.json',result);print(json.dumps({'result':str(output/'result.json'),'checks':len(checks),'status':'PASS','scope':result['scope']},ensure_ascii=False),flush=True)


if __name__=='__main__': run()

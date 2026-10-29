"""Freeze a reviewed NEW camera recapture using the accepted BoxEye/ZOH implementation."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import shutil
import sys
import uuid
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from camera_pipeline.adapter import video_to_flyvis_stimulus,save_stimulus,load_stimulus
from camera_pipeline.common import sha256,utc_now
from camera_pipeline.phase4_phone_camera_20261010_r1.config import ROOT,write_new
from camera_pipeline.phase4_phone_camera_20261010_r1.camera_session import read_presentation

def verify_capture(recording):
    recording=Path(recording).resolve();binding=json.loads((recording/'capture_binding.json').read_text(encoding='utf-8'))
    if binding.get('schema')!='flyvis-real-screen-capture-binding-v1' or binding.get('source_kind')!='real_camera_recapture_of_phone':
        raise ValueError('Require new phone-camera capture binding, not an animation or historical clip')
    if not binding['coverage']['all_footprints_inside_active_screen'] or not binding['screen_coverage_reviewed_by_operator']:
        raise ValueError('Screen placement/coverage not accepted')
    if not binding['comparison_id'].startswith('camera_') or binding['comparison_id']!=binding['capture_id']:
        raise ValueError('Require separate new recapture identity')
    if sha256(recording/'recording.json')!=binding['recording_json_sha256']:raise ValueError('Recording metadata changed')
    metadata=json.loads((recording/'recording.json').read_text(encoding='utf-8'))
    if metadata['source_kind']!='real_windows_camera':raise ValueError('Not a real camera recording')
    for name,digest in metadata['data_sha256'].items():
        if sha256(recording/name)!=digest:raise ValueError('Recording data checksum mismatch: '+name)
    actual_pngs={p.name:sha256(p) for p in sorted((recording/'raw_frames').glob('*.png'))}
    if actual_pngs!=binding['raw_png_sha256']:raise ValueError('Lossless raw frame identity mismatch')
    presentation_path,spec=read_presentation(binding['phone_presentation_path'],finished=True)
    if spec['phone_stimulus_session_id']!=binding['phone_stimulus_session_id'] or spec['settings_sha256']!=binding['phone_settings_sha256']:
        raise ValueError('Phone session changed or mismatched')
    events=presentation_path.parent/'events.jsonl'
    entries=[json.loads(line) for line in events.read_text(encoding='utf-8').splitlines()]
    kinds=[row['client_event']['kind'] for row in entries]
    if kinds.count('start')!=1 or not any(k in ('complete','stop') for k in kinds):raise ValueError('Incomplete phone playback log')
    with (recording/'frame_timestamps.csv').open(encoding='utf-8',newline='') as stream: timestamps=list(csv.DictReader(stream))
    times=np.load(recording/'frame_times.npy',allow_pickle=False)
    ns=np.array([int(r['received_monotonic_ns']) for r in timestamps],dtype=np.int64)
    if len(times)<2 or len(times)!=len(timestamps) or len(times)!=len(actual_pngs):raise ValueError('Raw-frame/timestamp counts differ')
    if not np.allclose(times,(ns-ns[0])/1e9,rtol=0,atol=1e-12):raise ValueError('Receipt time/sequence alignment mismatch')
    return recording,binding,metadata,presentation_path,spec,entries,timestamps

def freeze(recording,*,capture_reviewed=False):
    if not capture_reviewed:raise ValueError('Review actual raw replay, exposure, direction and phone visibility first (--capture-reviewed)')
    recording,binding,source,presentation_path,spec,entries,timestamps=verify_capture(recording)
    folder=ROOT/'inputs'/('input_'+uuid.uuid4().hex)
    bundle=video_to_flyvis_stimulus(recording,spatial_policy='native',method='zoh',dt_s=.005)
    coords=np.array([[row['render_column'],row['render_row']] for row in bundle.coordinates])
    from camera_pipeline.phase4_phone_camera_20261010_r1.geometry import native_geometry
    expected,mask,geometry=native_geometry(source['frames_shape'][2],source['frames_shape'][1])
    if not np.array_equal(coords,expected):raise ValueError('Official mapping disagrees with reviewed footprint geometry')
    save_stimulus(bundle,folder)
    loaded,grid,_,_=load_stimulus(folder)
    if not np.array_equal(loaded,bundle.stimulus) or not np.array_equal(grid,bundle.time):raise ValueError('Frozen input readback differs')
    activity_time=bundle.time+.005;np.save(folder/'activity_time.npy',activity_time,allow_pickle=False)
    rows=[]
    for alignment in bundle.alignment:
        index=alignment['source_left_frame'];stamp=timestamps[index]
        rows.append({'model_step':alignment['model_frame'],'source_frame':index,
                     'source_received_utc':stamp['received_utc'],'source_received_monotonic_ns':stamp['received_monotonic_ns'],
                     'source_relative_time_s':alignment['source_left_time_s'],'input_time_s':alignment['model_time_s'],
                     'activity_after_update_time_s':float(activity_time[alignment['model_frame']]),
                     'source_frame_age_at_input_s':alignment['model_time_s']-alignment['source_left_time_s'],
                     'uses_future_frame':False,'activity_is_initial_state':False})
    with (folder/'three_clock_alignment.csv').open('x',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    provenance=folder/'provenance';provenance.mkdir()
    for name in ('capture_binding.json','recording.json','phone_at_capture_start.json','roi_measurements.json','property_samples.json'):
        shutil.copyfile(recording/name,provenance/name)
    shutil.copyfile(presentation_path,provenance/'phone_presentation_final.json')
    shutil.copyfile(presentation_path.parent/'events.jsonl',provenance/'phone_events.jsonl')
    frame_events=[row['client_event'] for row in entries if row['client_event']['kind']=='frame']
    intervals=np.diff([r['client_performance_ms'] for r in frame_events])/1000 if len(frame_events)>1 else np.array([])
    artifacts={str(p.relative_to(folder)):sha256(p) for p in folder.rglob('*') if p.is_file()}
    descriptor={'schema':'flyvis-real-screen-input-v1','input_id':folder.name,'comparison_id':binding['comparison_id'],
                'capture_id':binding['capture_id'],'phone_stimulus_session_id':spec['phone_stimulus_session_id'],
                'created_utc':utc_now(),'source_kind':'real_camera_recapture_of_phone','source_is_camera':True,
                'operator_capture_reviewed':True,'phone_original_is_neural_input':False,
                'recording_path':str(recording),'raw_recording_hashes':source['data_sha256'],
                'raw_png_hashes':binding['raw_png_sha256'],'phone_settings':spec['settings'],
                'phone_settings_sha256':spec['settings_sha256'],'phone_presentation_final_sha256':sha256(presentation_path),
                'stimulus_file':'stimulus.npy','shape':list(bundle.stimulus.shape),'dtype':'float32','range':[0,1],
                'spatial_policy':'native','boxeye':[15,13],'mapping':geometry,'dt_s':.005,'temporal_method':'causal_zoh',
                'source_camera_delivery_fps':source['measured_delivery_fps'],'simulation_steps_per_second':200,
                'actual_compute_steps_per_second':None,'phone_browser_frame_callback_fps':float(1/intervals.mean()) if len(intervals) else None,
                'phone_physical_refresh_hz':None,'phone_to_camera_optical_alignment':None,
                'source_clock':'measured host receipt, not sensor exposure','input_clock':'relative to first recorded receipt; grid <= last actual receipt',
                'activity_clock':'after-update Euler state at input_time+dt; a0 is separate',
                'requested_phone_condition_may_not_fill_entire_camera_clip':True,
                'status':'input_frozen_neural_not_run','files_sha256':artifacts,
                'original_model':'flow/0000/000','source_commit':bundle.metadata['source_commit'],
                'modes':{name:{'status':'not_run','activity_path':None} for name in ('full_gpu','python_replacement','fpga_replacement')},
                'initial_state_identity':None,'expanded_parameter_identity':None,
                'backend_handoff':'A/B establish one new shared a0 and parameter/node map/numerical identity for this comparison; use exact frozen stimulus bytes',
                'gui_handoff':'Display input with no activity yet; accept activity only for this comparison_id plus stimulus/time/a0/model hashes',
                'board_used':False,'processing_mode':'offline_preprocessing'}
    write_new(folder/'INPUT_IDENTITY.json',descriptor)
    write_new(folder/'manifest.json',{'schema':'phase4-frozen-input-seal-v1','files':{
        str(p.relative_to(folder)):sha256(p) for p in folder.rglob('*') if p.is_file()}})
    return folder,descriptor

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('recording',type=Path);p.add_argument('--capture-reviewed',action='store_true')
    args=p.parse_args()
    try:
        folder,descriptor=freeze(args.recording,capture_reviewed=args.capture_reviewed)
        print(json.dumps({'input':str(folder),'comparison_id':descriptor['comparison_id'],'shape':descriptor['shape'],
                          'neural_inference':False,'board_used':False},ensure_ascii=False))
    except (ValueError,FileNotFoundError) as error:raise SystemExit(str(error))

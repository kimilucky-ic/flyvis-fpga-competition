"""Create an explicitly authorized lossless source view, then reuse scheme B freeze.

The full camera recording is retained unchanged. This is a NEW independent
experiment start, not a resumed hidden network state from the original video.
"""
from pathlib import Path
import csv
import json
import shutil
import sys
import uuid
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from camera_pipeline.common import sha256,write_json,utc_now
from camera_pipeline.phone_screen_rectification_20261011_r1.screen_import import seal,verify_seal,calibrate,freeze

ROOT=Path(__file__).resolve().parent
PARENT=ROOT/'source'
FIRST,LAST=100,190
verify_seal(PARENT)
parent=json.loads((PARENT/'source.json').read_text(encoding='utf-8'))
full=np.load(parent['frames_path'],mmap_mode='r',allow_pickle=False)
full_time=np.load(PARENT/'source_time.npy',allow_pickle=False)
selected=ROOT/'selected_source_100_190'
selected.mkdir(exist_ok=False)
np.save(selected/'frames.npy',np.asarray(full[FIRST:LAST+1]),allow_pickle=False)
original_time=full_time[FIRST:LAST+1]
relative_time=original_time-original_time[0]
np.save(selected/'source_time.npy',relative_time,allow_pickle=False)
np.save(selected/'source_times_original.npy',original_time,allow_pickle=False)
np.save(selected/'original_source_frame_indices.npy',np.arange(FIRST,LAST+1,dtype=np.int64),allow_pickle=False)
with (PARENT/'source_times.csv').open(encoding='utf-8',newline='') as handle:
    parent_rows=list(csv.DictReader(handle))
rows=[]
for local,original in enumerate(range(FIRST,LAST+1)):
    row=dict(parent_rows[original]);row['source_frame']=local;row['original_source_frame']=original
    row['source_relative_time_s']=float(relative_time[local]);row['parent_relative_time_s']=float(full_time[original])
    rows.append(row)
with (selected/'source_times.csv').open('x',encoding='utf-8',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
with (PARENT/'frame_timestamps.csv').open(encoding='utf-8',newline='') as handle:
    original_stamps=list(csv.DictReader(handle))[FIRST:LAST+1]
with (selected/'frame_timestamps.csv').open('x',encoding='utf-8',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(original_stamps[0]));writer.writeheader();writer.writerows(original_stamps)
for name in ('source_recording.json','selfserve_context.json'):
    if (PARENT/name).is_file():shutil.copyfile(PARENT/name,selected/name)
if (PARENT/'provenance').is_dir():shutil.copytree(PARENT/'provenance',selected/'provenance')
authorization={'schema':'real-camera-window-authorization-v1','recorded_utc':utc_now(),
    'basis':'Direct user answer to input range question',
    'answer':'截取3.43–6.47秒较稳定片段，先做真实输入闭环（推荐）',
    'first_original_frame':FIRST,'last_original_frame':LAST,'parent_capture_id':Path(parent['source_path']).name,
    'preserve_entire_original_recording':True,'same_initial_screen_homography_for_all_frames':True,
    'new_simulation_start_not_mid_run_state_restore':True}
write_json(selected/'selection_authorization.json',authorization)
doc={**parent,'source_bundle_id':selected.name,'created_utc':utc_now(),'frames_path':str(selected/'frames.npy'),
    'frames_sha256':sha256(selected/'frames.npy'),'shape':[LAST-FIRST+1,*full.shape[1:]],
    'origin_evidence':'existing_real_windows_camera_recorder_selected_lossless_frames',
    'source_timestamp_origin_s':float(original_time[0]),'source_span_s':float(relative_time[-1]),
    'average_presentation_or_delivery_fps':float((len(relative_time)-1)/relative_time[-1]),
    'original_recording_delivery_fps':parent['average_presentation_or_delivery_fps'],
    'phone_log_binding':{'phone_stimulus_session_id':'d602eadfa3c74a38987a932355106ae3',
        'settings_sha256':'be29aa80006a2225340aa54817f7f44de7b7d2d49e901cfa5e6028c034192e38',
        'association':'Actual recorder selected the armed phone session before first recorded PNG; saved start/final snapshots and event log retained; optical alignment unknown'},
    'source_frame_selection':{'parent_source_bundle':str(PARENT),'parent_manifest_sha256':sha256(PARENT/'manifest.json'),
        'parent_capture_id':Path(parent['source_path']).name,'parent_frames':len(full),'first_original_frame':FIRST,
        'last_original_frame':LAST,'original_start_time_s':float(original_time[0]),'original_end_time_s':float(original_time[-1]),
        'new_capture_performed':False,'lossless_source_frame_slice':True,
        'parent_contains_complete_4_second_phone_playback':True,'selected_window_is_full_phone_animation':False,
        'selected_window_covers_white_to_black_passage_over_721_sampling_field':True},
    'quality':{'status':'ACCEPTED_FOR_FIRST_REAL_INPUT_PIPELINE_EXPERIMENT_WITH_LIMITATIONS',
        'not_clean_controlled_direction_benchmark':True,'phone_hand_motion_remains':True,
        'estimated_sampling_outside_screen_fraction_in_selected_window':0.0,
        'geometry_QC_is_diagnostic_not_precise_optical_calibration':True,
        'physical_exposure_mode_verified':False,'no_inference_claim':True},
    'operator_provenance_note':'User explicitly selected recorded frames100..190; initial camera frame0 calibration reused unchanged; no brightness enhancement, image tracking or temporal interpolation'}
write_json(selected/'source.json',doc)
external={str(PARENT/'manifest.json'):sha256(PARENT/'manifest.json')}
parent_seal=json.loads((PARENT/'manifest.json').read_text())
external.update(parent_seal['external_files'])
external.update({str(PARENT/name):digest for name,digest in parent_seal['files'].items()})
seal(selected,external=external)
# Keep initial camera frame0's EXACT reviewed matrix, even though selected frame0
# is original frame100. Do not compute a new moving/stabilizing homography.
cal_source=ROOT/'calibration_proposal'
verify_seal(cal_source)
cal=json.loads((cal_source/'calibration.json').read_text(encoding='utf-8'))
cal_output=ROOT/'selected_calibration_initial_frame0';cal_output.mkdir(exist_ok=False)
for name in ('calibration_raw.png','rectified_calibration.png','sampling_overlay_raw.png','raw_sampling_coordinates.csv'):
    shutil.copyfile(cal_source/name,cal_output/name)
cal={**cal,'source_bundle_path':str(selected),'source_bundle_id':selected.name,
    'source_manifest_sha256':sha256(selected/'manifest.json'),'calibration_frame_index':-FIRST,
    'selection':'Explicitly reviewed parent original frame0; fixed matrix retained for selected view',
    'calibration_frame_is_parent_reference':True,'parent_calibration_original_frame':0,
    'parent_calibration_source_manifest_sha256':sha256(PARENT/'manifest.json')}
# Existing freeze requires a calibration frame IN its source array. To satisfy
# this invariant without changing geometry, regenerate ONLY the diagnostic
# calibration image from selected frame0 using the same original frame0 corners.
# Its actual selected-frame pixels are reviewed independently; transform stays
# byte/numerically identical to the initial full-record calibration.
for path in cal_output.iterdir():
    # Do not delete copied artifacts: this directory is an explicit historical
    # reference, sealed below and separate from the executable calibration.
    pass
write_json(cal_output/'parent_calibration_reference.json',cal)
seal(cal_output)
exec_cal=ROOT/'selected_calibration'
selected_cal=calibrate(selected,exec_cal,frame_index=0,corners=cal['selected_corners'])
if selected_cal['transform']!=cal['transform']:raise ValueError('Fixed initial transform changed')
identity,input_dir=freeze(selected,exec_cal/'calibration.json',ROOT/'frozen_selected_100_190',reviewed=True,
    review_note='User approved frames100..190 (3.4294444..6.4699407s of original recording). Actual complete parent351-frame phone capture retained. Selected91 lossless frames show rightward OFF passage through the sampled region and final dark hold; original frame0 homography remains identical. Phone wobble/exposure/reflections remain; not a clean direction benchmark. New simulation begins from shareda0, not restored middle-of-video state. No neural run yet.')
# Frozen files are not changed. Supplement original-frame mapping as a separately
# sealed handoff addition so consumers cannot confuse local vs original frame IDs.
handoff=ROOT/'handoff_selected_100_190';handoff.mkdir(exist_ok=False)
with (input_dir/'three_clock_alignment.csv').open(encoding='utf-8',newline='') as handle:
    alignment=list(csv.DictReader(handle))
mapped=[]
for a in alignment:
    local=int(a['source_frame']);original=FIRST+local
    mapped.append({**a,'source_local_frame':local,'source_original_frame':original,
        'original_recording_relative_time_s':float(full_time[original]),
        'original_recording_grid_time_s':float(original_time[0]+float(a['input_time_s'])),
        'original_recording_activity_grid_time_s':float(original_time[0]+float(a['activity_after_update_time_s']))})
with (handoff/'original_frame_alignment.csv').open('x',encoding='utf-8',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(mapped[0]));writer.writeheader();writer.writerows(mapped)
experiment={'schema':'real-camera-selected-experiment-v1','comparison_id':identity['comparison_id'],
    'input_id':identity['input_id'],'input_directory':str(input_dir),'input_manifest_sha256':sha256(input_dir/'manifest.json'),
    'stimulus_npy_sha256':sha256(input_dir/'stimulus.npy'),'input_time_npy_sha256':sha256(input_dir/'time.npy'),
    'activity_time_npy_sha256':sha256(input_dir/'activity_time.npy'),'shape':identity['shape'],
    'parent_capture_id':Path(parent['source_path']).name,'recording_path':parent['source_path'],
    'source_selection':doc['source_frame_selection'],'quality':doc['quality'],'scheme':identity['scheme'],
    'same_initial_homography_for_whole_selected_sequence':True,
    'parent_calibration_reference':str(cal_output/'parent_calibration_reference.json'),
    'model_start':'one new shareda0 for selected segment; no prior 12s model activity exists',
    'backend_required_steps':identity['shape'][1],'backend_modes':identity['modes'],
    'activity_after_update_time_semantics':'local input_time+0.005, original grid origin3.4294444s; this is not continuously resumed original-video neural state',
    'source_is_camera':True,'phone_original_is_neural_input':False,'neural_inference':False,'board_used':False}
write_json(handoff/'experiment.json',experiment);seal(handoff)
write_json(ROOT/'selection_result.json',{'input':str(input_dir),'handoff':str(handoff),'comparison_id':identity['comparison_id'],
    'shape':identity['shape'],'neural_inference':False,'board_used':False})
print(json.dumps({'input':str(input_dir),'handoff':str(handoff),'comparison_id':identity['comparison_id'],
    'shape':identity['shape'],'neural_inference':False},indent=2),flush=True)

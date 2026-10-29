"""Offline scheme B: one reviewed screen homography, original BoxEye and causal ZOH.

No USB device is opened here. File presentation timestamps are not camera receipt
or exposure timestamps. Automatic white-screen proposals require visual review.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import shutil
import sys
import uuid
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from camera_pipeline.common import cv2_module, new_directory, sha256, utc_now, write_json
from camera_pipeline.adapter import (StimulusBundle, SOURCE_COMMIT, load_video_source,
    render_bgr_frames, resample_hex, save_stimulus, load_stimulus)
from camera_pipeline.phase4_phone_camera_20261010_r1.geometry import native_geometry

HERE = Path(__file__).resolve().parent
KINDS = ('camera_recapture', 'digital_stimulus')


def seal(folder, name='manifest.json', external=None):
    folder = Path(folder)
    write_json(folder/name, {'schema': 'screen-B-seal-v1', 'files': {
        str(p.relative_to(folder)): sha256(p) for p in sorted(folder.rglob('*'))
        if p.is_file() and p != folder/name}, 'external_files': external or {}})


def verify_seal(folder, name='manifest.json'):
    folder = Path(folder).resolve()
    doc = json.loads((folder/name).read_text(encoding='utf-8'))
    if doc['schema'] != 'screen-B-seal-v1':
        raise ValueError('Unknown input seal')
    for relative, digest in doc['files'].items():
        path = (folder/relative).resolve()
        if not path.is_relative_to(folder) or sha256(path) != digest:
            raise ValueError('Changed sealed file: '+relative)
    for path, digest in doc['external_files'].items():
        if sha256(path) != digest:
            raise ValueError('Changed referenced original: '+path)
    return doc


def validate_times(times):
    times = np.asarray(times, dtype=np.float64)
    if times.ndim != 1 or len(times) < 2 or not np.isfinite(times).all() or (np.diff(times) <= 0).any():
        raise ValueError('Need strictly increasing measured receipt or decoded presentation times; no automatic FPS fallback')
    return times


def ingest(source, output, source_kind, *, provenance_note='', phone_presentation=None):
    if source_kind not in KINDS:
        raise ValueError('Declare camera_recapture or digital_stimulus explicitly')
    source = Path(source).resolve()
    output = new_directory(output)
    external = {}
    cv = cv2_module()
    if source.is_dir():
        frames, times, recording = load_video_source(source)
        if recording.get('source_kind') != 'real_windows_camera' or source_kind != 'camera_recapture':
            raise ValueError('Directory entry requires actual existing Windows recorder evidence')
        for name, digest in recording['data_sha256'].items():
            if sha256(source/name) != digest:
                raise ValueError('Source recording checksum mismatch: '+name)
            external[str(source/name)] = digest
        external[str(source/'recording.json')] = sha256(source/'recording.json')
        shutil.copyfile(source/'recording.json', output/'source_recording.json')
        shutil.copyfile(source/'frame_timestamps.csv', output/'frame_timestamps.csv')
        if (source/'selfserve_context.json').is_file():
            external[str(source/'selfserve_context.json')] = sha256(source/'selfserve_context.json')
            shutil.copyfile(source/'selfserve_context.json', output/'selfserve_context.json')
        provenance = output/'provenance'; provenance.mkdir()
        for name in ('property_samples.json','recording_ready.json','phone_at_capture_start.json',
                     'phone_presentation_after_capture.json','phone_events.jsonl'):
            if (source/name).is_file():
                external[str(source/name)] = sha256(source/name)
                shutil.copyfile(source/name,provenance/name)
        for path in sorted((source/'raw_frames').glob('*.png')):
            external[str(path)] = sha256(path)
        frames_path = source/'frames.npy'
        timing_kind = 'measured_host_frame_receipt'
        origin_evidence = 'existing_real_windows_camera_recorder'
        nominal_fps = recording['capture']['reported_fps']
        source_clock = recording['timestamp_semantics']
        decode = None
    else:
        if not source.is_file():
            raise FileNotFoundError(source)
        original_digest = sha256(source)
        original = output/('original'+source.suffix.lower())
        shutil.copyfile(source, original)
        if sha256(original) != original_digest or sha256(source) != original_digest:
            raise ValueError('Original changed while copying')
        cap = cv.VideoCapture(str(original))  # FILE only, never a camera index
        if not cap.isOpened():
            raise ValueError('Cannot decode supplied video')
        raw = output/'decoded_frames'; raw.mkdir()
        times = []; shape = None
        try:
            orientation_request = cap.set(cv.CAP_PROP_ORIENTATION_AUTO, 0)
            orientation_auto = cap.get(cv.CAP_PROP_ORIENTATION_AUTO)
            if orientation_auto != 0:
                raise ValueError('Cannot disable hidden decoder autorotation')
            nominal_fps = float(cap.get(cv.CAP_PROP_FPS))
            decode = {'opencv': cv.__version__, 'backend': cap.getBackendName(),
                'orientation_auto_set_return': bool(orientation_request),
                'orientation_auto_reported': float(orientation_auto),
                'orientation_metadata_degrees': float(cap.get(cv.CAP_PROP_ORIENTATION_META)),
                'auto_rotation_applied': False, 'decoded_pixels': 'BGR uint8; original compressed file retained',
                'timestamp_api': 'CAP_PROP_POS_MSEC immediately after each successful decoded read'}
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                if shape is None:
                    shape = frame.shape
                if frame.shape != shape:
                    raise ValueError('Video dimensions changed')
                stamp = float(cap.get(cv.CAP_PROP_POS_MSEC))/1000
                if not np.isfinite(stamp):
                    raise ValueError('Nonfinite video presentation timestamp')
                name = raw/f'frame_{len(times):06d}.png'
                if not cv.imwrite(str(name), frame, [cv.IMWRITE_PNG_COMPRESSION, 1]):
                    raise ValueError('Failed saving decoded original')
                times.append(stamp)
                if len(times) > 3600:
                    raise ValueError('Use a short first experiment (at most 3600 decoded frames)')
        finally:
            cap.release()
        times = validate_times(times)
        frames_path = output/'frames.npy'
        frames = np.lib.format.open_memmap(frames_path, mode='w+', dtype=np.uint8, shape=(len(times), *shape))
        for i, path in enumerate(sorted(raw.glob('*.png'))):
            frames[i] = cv.imread(str(path), cv.IMREAD_COLOR)
        frames.flush(); del frames
        frames = np.load(frames_path, mmap_mode='r', allow_pickle=False)
        timing_kind = 'decoder_reported_video_presentation_time'
        origin_evidence = 'operator_declared_camera_file' if source_kind == 'camera_recapture' else 'operator_declared_digital_video'
        source_clock = 'Media presentation times reported by file decoder; no host camera receipt, sensor exposure or UTC inferred'
        recording = {'source_kind': 'imported_video', 'source_sha256': original_digest, 'source_path': str(original)}
    phone_binding = None
    if phone_presentation is not None:
        from camera_pipeline.phase4_phone_camera_20261010_r1.camera_session import read_presentation
        path,spec = read_presentation(phone_presentation,finished=True)
        provenance=output/'provenance';provenance.mkdir(exist_ok=True)
        shutil.copyfile(path,provenance/'phone_presentation_after_capture.json')
        shutil.copyfile(path.parent/'events.jsonl',provenance/'phone_events.jsonl')
        phone_binding={'phone_stimulus_session_id':spec['phone_stimulus_session_id'],
            'settings_sha256':spec['settings_sha256'],'association':'operator-declared association; no optical clock alignment inferred'}
    times = validate_times(times)
    np.save(output/'source_times_original.npy', times, allow_pickle=False)
    np.save(output/'source_time.npy', times-times[0], allow_pickle=False)
    if not cv.imwrite(str(output/'first_raw_frame.png'), np.asarray(frames[0])):
        raise ValueError('Cannot save calibration frame')
    rows = []
    receipts = None
    if (output/'frame_timestamps.csv').is_file():
        with (output/'frame_timestamps.csv').open(encoding='utf-8', newline='') as handle:
            receipts = list(csv.DictReader(handle))
        if len(receipts) != len(times):
            raise ValueError('Receipt rows and frame count differ')
        ns = np.array([int(r['received_monotonic_ns']) for r in receipts], dtype=np.int64)
        if not np.allclose(times-times[0], (ns-ns[0])/1e9, rtol=0, atol=1e-12):
            raise ValueError('Receipt clock mismatch')
    for i, stamp in enumerate(times):
        rows.append({'source_frame': i, 'source_relative_time_s': float(stamp-times[0]),
            'source_original_time_s': float(stamp),
            'source_received_utc': receipts[i]['received_utc'] if receipts else '',
            'source_received_monotonic_ns': receipts[i]['received_monotonic_ns'] if receipts else ''})
    with (output/'source_times.csv').open('x', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    doc = {'schema': 'screen-B-source-v1', 'source_bundle_id': output.name, 'created_utc': utc_now(),
        'source_kind': source_kind, 'source_is_camera': source_kind == 'camera_recapture',
        'origin_evidence': origin_evidence, 'operator_provenance_note': provenance_note,
        'frames_path': str(frames_path), 'frames_sha256': sha256(frames_path), 'shape': list(frames.shape),
        'source_path': str(source), 'source_metadata': recording, 'decoder': decode,
        'timestamp_kind': timing_kind, 'source_clock': source_clock,
        'source_timestamp_origin_s': float(times[0]), 'source_span_s': float(times[-1]-times[0]),
        'nominal_fps_reported': nominal_fps if np.isfinite(nominal_fps) else None,
        'average_presentation_or_delivery_fps': float((len(times)-1)/(times[-1]-times[0])),
        'sensor_exposure_timestamps_available': False, 'camera_properties_verified': False,
        'phone_playback_log_available': (output/'provenance'/'phone_events.jsonl').is_file(),
        'phone_log_binding':phone_binding,
        'calibration_status': 'not_reviewed', 'neural_inference': False, 'board_used': False}
    write_json(output/'source.json', doc)
    seal(output, external=external)
    return doc


def bright_screen_candidates(frame):
    """Propose bright convex quads; never declare a phone or accept them automatically."""
    cv = cv2_module(); gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    h, w = gray.shape; result = []
    for threshold in (60, 100, 140, 180, 220):
        contours, _ = cv.findContours((gray >= threshold).astype(np.uint8)*255, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv.contourArea(contour)
            if not .015*h*w < area < .8*h*w:
                continue
            polygon = cv.approxPolyDP(contour, .018*cv.arcLength(contour, True), True)
            if len(polygon) != 4 or not cv.isContourConvex(polygon):
                continue
            points = polygon[:, 0].astype(float)
            center = points.mean(axis=0)
            points = points[np.argsort(np.arctan2(points[:,1]-center[1], points[:,0]-center[0]))]
            points = np.roll(points, -int(np.argmin(points.sum(axis=1))), axis=0)
            edges = np.linalg.norm(np.roll(points, -1, axis=0)-points, axis=1)
            if edges.min() < 40 or edges.max()/edges.min() > 2.5:
                continue
            if any(np.max(np.abs(points-np.array(old['corners']))) < 8 for old in result):
                continue
            centrality = np.linalg.norm((center-[w/2,h/2])/[w,h])
            score = float(area/(h*w)/(1+4*centrality)/(edges.max()/edges.min()))
            result.append({'corners': points.tolist(), 'threshold': threshold, 'score': score,
                'automatic_proposal_only': True, 'logical_corner_orientation_verified': False})
    return sorted(result, key=lambda row: row['score'], reverse=True)[:8]


def fixed_transform(corners, width, height):
    cv = cv2_module(); points = np.asarray(corners, dtype=np.float64).reshape(4,2)
    if not np.isfinite(points).all() or (points < 0).any() or (points[:,0] >= width).any() or (points[:,1] >= height).any():
        raise ValueError('Four finite screen points must lie in the original image')
    edges = np.roll(points, -1, axis=0)-points
    turns = edges[:,0]*np.roll(edges,-1,axis=0)[:,1]-edges[:,1]*np.roll(edges,-1,axis=0)[:,0]
    if not (turns > 0).all() or np.linalg.norm(edges,axis=1).min() < 40:
        raise ValueError('Require convex clockwise TL/TR/BR/BL screen polygon; mirrored, tiny or crossing corners rejected')
    target = np.array([[0,0],[639,0],[639,639],[0,639]], dtype=np.float32)
    matrix = cv.getPerspectiveTransform(points.astype(np.float32), target)
    if not np.isfinite(matrix).all() or abs(np.linalg.det(matrix)) < 1e-12:
        raise ValueError('Degenerate homography')
    inverse = np.linalg.inv(matrix)
    mapped = cv.perspectiveTransform(points.astype(np.float32)[None], matrix)[0]
    if np.max(np.abs(mapped-target)) > .001:
        raise ValueError('Corner mapping residual too high')
    centers, mask, geometry = native_geometry(640,640)
    valid = cv.warpPerspective(np.ones((height,width),np.float32), matrix, (640,640),
        flags=cv.INTER_LINEAR, borderMode=cv.BORDER_CONSTANT, borderValue=0)
    if (valid[mask] < .99999).any():
        raise ValueError('Official sampling would use outside-frame border pixels')
    doc = {'policy': 'B_fixed_screen_homography_640', 'source_resolution_wh': [width,height],
        'render_resolution_wh': [640,640], 'corners_logical_TL_TR_BR_BL_raw_xy': points.tolist(),
        'destination_corners_xy': target.tolist(), 'raw_to_render_homography': matrix.tolist(),
        'render_to_raw_homography': inverse.tolist(), 'interpolation': 'OpenCV INTER_LINEAR BGR uint8 before official Pillow luminance',
        'border_mode': 'constant 0; independently verified no border contribution to official 13x13 footprints',
        'explicit_crop_and_perspective_resampling': True, 'per_frame_transform_updates': False,
        'temporal_stabilization_or_optical_flow': False, 'lens_undistortion': False,
        'brightness_normalization': False, 'rendered_sampling_bounds_xy': geometry['footprint_bounds_xy_inclusive'],
        'sampling_union_pixels': int(mask.sum()), 'sampling_bounding_fraction_of_logical_screen': 403/640,
        'camera_FOV_degrees': None, 'physical_speed_calibrated': False,
        'orientation': 'Logical corners explicitly define orientation; clockwise winding prevents reflection',
        'boxeye': [15,13], 'boxeye_after_rectification_policy': 'native; no additional resize'}
    return matrix, inverse, centers, mask, doc


def calibrate(source_bundle, destination, *, frame_index=0, corners=None):
    source_bundle = Path(source_bundle).resolve(); verify_seal(source_bundle)
    source = json.loads((source_bundle/'source.json').read_text(encoding='utf-8'))
    frames = np.load(source['frames_path'], mmap_mode='r', allow_pickle=False)
    if sha256(source['frames_path']) != source['frames_sha256']:
        raise ValueError('Original pixel identity changed')
    if not 0 <= frame_index < len(frames):
        raise IndexError(frame_index)
    output = new_directory(destination); cv = cv2_module(); frame = np.asarray(frames[frame_index])
    cv.imwrite(str(output/'calibration_raw.png'), frame)
    candidates = bright_screen_candidates(frame)
    selected = np.asarray(corners).reshape(4,2).tolist() if corners is not None else (candidates[0]['corners'] if candidates else None)
    doc = {'schema': 'screen-B-calibration-v1', 'created_utc': utc_now(), 'source_bundle_path': str(source_bundle),
        'source_manifest_sha256': sha256(source_bundle/'manifest.json'), 'source_bundle_id': source['source_bundle_id'],
        'calibration_frame_index': frame_index, 'calibration_raw_sha256': sha256(output/'calibration_raw.png'),
        'selection': 'explicit_points' if corners is not None else 'automatic_bright_quad_proposal',
        'candidates': candidates, 'selected_corners': selected, 'visual_and_logical_direction_review_required': True}
    if selected is not None:
        matrix, inverse, centers, mask, transform = fixed_transform(selected, frame.shape[1], frame.shape[0])
        doc['transform'] = transform
        rectified = cv.warpPerspective(frame, matrix, (640,640), flags=cv.INTER_LINEAR, borderMode=cv.BORDER_CONSTANT, borderValue=0)
        cv.imwrite(str(output/'rectified_calibration.png'), rectified)
        view = frame.copy(); cv.polylines(view,[np.round(selected).astype(np.int32)],True,(0,200,255),2)
        projected = cv.perspectiveTransform(centers.astype(np.float32)[None], inverse)[0]
        for x,y in projected:
            cv.circle(view,(int(round(x)),int(round(y))),1,(0,255,0),-1)
        # All 13x13 boundaries, not just center points; visualization uses rounded drawing only.
        rows=[]
        for i,(x,y) in enumerate(centers):
            quad=np.array([[x-6,y-6],[x+6,y-6],[x+6,y+6],[x-6,y+6]],np.float32)
            raw_quad=cv.perspectiveTransform(quad[None],inverse)[0]
            cv.polylines(view,[np.round(raw_quad).astype(np.int32)],True,(0,110,0),1)
            rows.append({'hex_pixel':i,'render_column':int(x),'render_row':int(y),
                'raw_center_x':float(projected[i,0]),'raw_center_y':float(projected[i,1]),
                **{f'raw_kernel_corner_{k}_{axis}':float(raw_quad[k,j]) for k in range(4) for j,axis in enumerate(('x','y'))}})
        cv.imwrite(str(output/'sampling_overlay_raw.png'), view)
        with (output/'raw_sampling_coordinates.csv').open('x', encoding='utf-8', newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    write_json(output/'calibration.json', doc); seal(output)
    return doc


def freeze(source_bundle, calibration, output, *, reviewed=False, review_note=''):
    if not reviewed or not review_note.strip():
        raise ValueError('Review complete actual replay, fixed placement and logical corner orientation before --reviewed --review-note')
    source_bundle = Path(source_bundle).resolve(); verify_seal(source_bundle)
    calibration = Path(calibration).resolve(); verify_seal(calibration.parent)
    cal = json.loads(calibration.read_text(encoding='utf-8'))
    if cal['source_bundle_path'] != str(source_bundle) or cal['source_manifest_sha256'] != sha256(source_bundle/'manifest.json'):
        raise ValueError('Calibration belongs to another source')
    source = json.loads((source_bundle/'source.json').read_text(encoding='utf-8'))
    frames = np.load(source['frames_path'], mmap_mode='r', allow_pickle=False)
    if sha256(source['frames_path']) != source['frames_sha256']:
        raise ValueError('Original frames changed')
    cv = cv2_module(); matrix, inverse, centers, mask, transform = fixed_transform(cal['selected_corners'],frames.shape[2],frames.shape[1])
    if transform != cal['transform']:
        raise ValueError('Reviewed transform does not reproduce')
    expected_frame = np.asarray(frames[cal['calibration_frame_index']])
    if not np.array_equal(cv.imread(str(calibration.parent/'calibration_raw.png')),expected_frame):
        raise ValueError('Calibration image identity mismatch')
    output = new_directory(output)
    derived = output/'rectified_frames.npy'
    rectified = np.lib.format.open_memmap(derived,mode='w+',dtype=np.uint8,shape=(len(frames),640,640,3))
    for i,frame in enumerate(frames):
        # One matrix reused for every frame; no tracking or motion-dependent recropping.
        rectified[i] = cv.warpPerspective(np.asarray(frame),matrix,(640,640),flags=cv.INTER_LINEAR,borderMode=cv.BORDER_CONSTANT,borderValue=0)
    rectified.flush()
    source_hex, coords, official = render_bgr_frames(rectified,spatial_policy='native')
    del rectified
    times = np.load(source_bundle/'source_time.npy',allow_pickle=False)
    stimulus, grid, alignment = resample_hex(source_hex,times,dt_s=.005,method='zoh')
    meta={'schema':'flyvis-camera-stimulus-v1','created_utc':utc_now(),'source':{**source,'source_path':str(source_bundle)},
        'source_commit':SOURCE_COMMIT,'target_model':'flow/0000/000','model_weights_modified':False,
        'stimulus_shape':list(stimulus.shape),'stimulus_axes':['sample','frame','channel','hex_pixel'],'stimulus_dtype':'float32',
        'pre_boxeye_screen_transform':transform,'spatial_transform':official,'dt_s':.005,'simulation_fps':200,
        'temporal_method':'zoh','causal':True,'source_frame_count':len(times),'source_frame_span_s':float(times[-1]),
        'model_last_input_time_s':float(grid[-1]),'neural_inference_executed':False,'simulation_compute_fps':None,
        'time_semantics':'source receipt or file presentation -> causal input grid -> after-update input+dt; no padding beyond last source frame',
        'evidence_level':'offline input preprocessing; camera-file provenance may be operator declared'}
    input_dir = output/'input'
    save_stimulus(StimulusBundle(stimulus,grid,source_hex,times,coords,alignment,meta),input_dir)
    np.save(input_dir/'activity_time.npy',grid+.005,allow_pickle=False)
    for name in ('calibration.json','sampling_overlay_raw.png','raw_sampling_coordinates.csv'):
        shutil.copyfile(calibration.parent/name,input_dir/name)
    shutil.copyfile(source_bundle/'source.json',input_dir/'source.json')
    shutil.copyfile(source_bundle/'source_times.csv',input_dir/'source_times.csv')
    if (source_bundle/'provenance').is_dir():
        shutil.copytree(source_bundle/'provenance',input_dir/'provenance')
    with (source_bundle/'source_times.csv').open(encoding='utf-8',newline='') as handle:
        source_rows=list(csv.DictReader(handle))
    rows=[]
    for a in alignment:
        s=source_rows[a['source_left_frame']]
        rows.append({'model_step':a['model_frame'],'source_frame':a['source_left_frame'],
            'source_relative_time_s':a['source_left_time_s'],'source_received_utc':s['source_received_utc'],
            'source_received_monotonic_ns':s['source_received_monotonic_ns'],'input_time_s':a['model_time_s'],
            'activity_after_update_time_s':float(grid[a['model_frame']]+.005),'uses_future_frame':False})
    with (input_dir/'three_clock_alignment.csv').open('x',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    prefix='camera_rectB_' if source['source_is_camera'] else 'digital_rectB_'
    identity={'schema':'flyvis-screen-rectified-input-v1','input_id':output.name,'comparison_id':prefix+uuid.uuid4().hex,
        'created_utc':utc_now(),'source_kind':source['source_kind'],'source_is_camera':source['source_is_camera'],
        'origin_evidence':source['origin_evidence'],'source_bundle_path':str(source_bundle),
        'phone_playback_log_available':source['phone_playback_log_available'],'phone_log_binding':source['phone_log_binding'],
        'source_manifest_sha256':sha256(source_bundle/'manifest.json'),'source_clock':source['source_clock'],
        'scheme':'B_fixed_screen_homography_640','standard_A_comparison':False,
        'calibration_sha256':sha256(calibration),'transform':transform,'review_note':review_note,
        'rectified_frames_path':str(derived),'rectified_frames_sha256':sha256(derived),
        'shape':list(stimulus.shape),'dtype':'float32','range':[0,1],'dt_s':.005,'temporal_method':'causal_zoh',
        'source_span_s':float(times[-1]),'source_camera_delivery_fps':source['average_presentation_or_delivery_fps'] if source['timestamp_kind']=='measured_host_frame_receipt' else None,
        'source_video_presentation_fps':source['average_presentation_or_delivery_fps'] if source['timestamp_kind']!='measured_host_frame_receipt' else None,
        'simulation_steps_per_second':200,'actual_compute_steps_per_second':None,
        'source_commit':SOURCE_COMMIT,'original_model':'flow/0000/000','phone_original_is_neural_input':source['source_kind']=='digital_stimulus',
        'initial_state_identity':None,'expanded_parameter_identity':None,
        'status':'input_frozen_neural_not_run','board_used':False,
        'modes':{key:{'status':'not_run','activity_path':None} for key in ('full_gpu','python_replacement','fpga_replacement')},
        'files_sha256':{name:sha256(input_dir/name) for name in ('stimulus.npy','time.npy','activity_time.npy','input_hex_coordinates.csv','calibration.json')}}
    write_json(input_dir/'INPUT_IDENTITY.json',identity)
    loaded, actual_grid, _, _ = load_stimulus(input_dir)
    if not np.array_equal(loaded,stimulus) or not np.array_equal(actual_grid,grid):
        raise ValueError('Frozen input readback differs')
    seal(input_dir)
    seal(output)
    return identity, input_dir


def load_input(folder):
    folder=Path(folder).resolve();verify_seal(folder)
    identity=json.loads((folder/'INPUT_IDENTITY.json').read_text(encoding='utf-8'))
    if identity['schema']!='flyvis-screen-rectified-input-v1' or identity['scheme']!='B_fixed_screen_homography_640':
        raise ValueError('Wrong explicit preprocessing scheme')
    source=Path(identity['source_bundle_path']);verify_seal(source)
    if sha256(source/'manifest.json')!=identity['source_manifest_sha256'] or sha256(identity['rectified_frames_path'])!=identity['rectified_frames_sha256']:
        raise ValueError('Source or derived-frame identity changed')
    x,t,_,_=load_stimulus(folder);activity=np.load(folder/'activity_time.npy',allow_pickle=False)
    if x.dtype!=np.float32 or x.shape!=(1,len(t),1,721) or not np.array_equal(activity,t+.005):
        raise ValueError('After-update activity timeline mismatch')
    x.flags.writeable=False
    return identity,x,t,activity


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('ingest');a.add_argument('source',type=Path);a.add_argument('output',type=Path)
    a.add_argument('--source-kind',choices=KINDS,required=True);a.add_argument('--provenance-note',default='')
    a.add_argument('--phone-session',type=Path)
    a=sub.add_parser('calibrate');a.add_argument('source_bundle',type=Path);a.add_argument('output',type=Path)
    a.add_argument('--frame-index',type=int,default=0);a.add_argument('--corners',type=float,nargs=8)
    a=sub.add_parser('freeze');a.add_argument('source_bundle',type=Path);a.add_argument('calibration',type=Path);a.add_argument('output',type=Path)
    a.add_argument('--reviewed',action='store_true');a.add_argument('--review-note',default='')
    a=p.parse_args()
    if a.command=='ingest': result=ingest(a.source,a.output,a.source_kind,provenance_note=a.provenance_note,phone_presentation=a.phone_session)
    elif a.command=='calibrate': result=calibrate(a.source_bundle,a.output,frame_index=a.frame_index,corners=a.corners)
    else:
        identity, folder=freeze(a.source_bundle,a.calibration,a.output,reviewed=a.reviewed,review_note=a.review_note)
        result={'input':str(folder),'comparison_id':identity['comparison_id'],'shape':identity['shape'],'neural_inference':False,'board_used':False}
    print(json.dumps(result,ensure_ascii=False,indent=2))

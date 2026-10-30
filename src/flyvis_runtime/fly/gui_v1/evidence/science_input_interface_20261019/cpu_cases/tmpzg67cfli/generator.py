"""Verify/decode each MP4 once, freeze exact pixels and original native BoxEye inputs."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import shutil
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
from PIL import Image
from camera_pipeline.adapter import StimulusBundle, render_bgr_frames, resample_hex, save_stimulus, load_stimulus
from camera_pipeline.common import ROOT, cv2_module, new_directory, sha256, utc_now, write_json

TASK = Path(__file__).resolve().parent
ORIGINAL = ROOT.parent/'artifacts/controlled_visual_animation_20261010_142528'


def cfr_zoh(source_hex, timestamps, duration_s=4., dt_s=.005):
    """Known CFR presentation interval, including last-frame hold; not camera extrapolation."""
    if (len(timestamps) != 240 or not np.allclose(timestamps, np.arange(240)/60, atol=1e-9, rtol=0)
            or duration_s != 4. or dt_s != .005):
        raise ValueError('This frozen experiment requires verified 240-frame/60Hz/4s CFR clips')
    # Add a support endpoint for the declared presentation interval, then EXCLUDE that endpoint.
    stimulus, grid, rows = resample_hex(np.concatenate((source_hex, source_hex[-1:])),
                                       np.append(timestamps, duration_s), dt_s=dt_s, method='zoh')
    keep = grid < duration_s
    stimulus, grid, rows = stimulus[:, keep], grid[keep], rows[:int(keep.sum())]
    assert stimulus.shape == (1, 800, 1, 721)
    assert max(row['source_left_frame'] for row in rows) == 239
    return stimulus, grid, rows


def write_csv(path, rows):
    with Path(path).open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)


def main(resume=False):
    def directory(path):
        if resume and path.is_dir(): return path
        return new_directory(path)
    sources = directory(TASK/'sources')
    pixels = directory(TASK/'decoded_frames')
    inputs = directory(TASK/'inputs')
    cv2 = cv2_module()
    manifest_path = ORIGINAL/'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['schema'] == 'flyvis-controlled-display-stimuli/v1'
    assert manifest['resolution'] == [640, 640] and manifest['video_fps'] == 60
    assert len(manifest['conditions']) == 6
    original_hashes = {}
    for item in manifest['files']:
        path = (ORIGINAL/item['path'].replace('\\', '/')).resolve()
        assert path.is_relative_to(ORIGINAL.resolve())
        assert path.stat().st_size == item['bytes'] and sha256(path) == item['sha256'], path
        original_hashes[item['path']] = item['sha256']
    shutil.copyfile(manifest_path, sources/'original_manifest.json')
    shutil.copyfile(ORIGINAL/'black_white_stimuli_24s.mp4', sources/'black_white_stimuli_24s.mp4')
    samples, audits, values, hex_values, combined_alignment = [], [], [], [], []
    coordinates = None
    for sample, condition in enumerate(manifest['conditions']):
        condition_id = condition['condition_id']
        assert condition_id in ('00_static_edge', '01_off_right', '02_off_left', '03_on_right', '04_on_left', '05_brightness')
        source = sources/f'{condition_id}.mp4'
        shutil.copyfile(ORIGINAL/condition['path'].replace('\\', '/'), source)
        output_pixels = directory(pixels/condition_id)
        cached = resume and all((output_pixels/f'frame_{i:04d}.png').is_file() for i in range(240))
        previous_audit = output_pixels/'validation.json'
        # Completed decoded PNGs are the authoritative pixel cache. A failed audit cache
        # without its receipt is independently decoded once to verify all existing pixels.
        use_cache = cached and previous_audit.exists()
        video = None if use_cache else cv2.VideoCapture(str(source))
        if video is not None:
            assert video.isOpened()
            assert video.get(cv2.CAP_PROP_FPS) == 60. and video.get(cv2.CAP_PROP_FRAME_COUNT) == 240
        frames, pts, frame_inventory = [], [], []
        try:
            while len(frames) < 240:
                if use_cache:
                    frame = cv2.imread(str(output_pixels/f'frame_{len(frames):04d}.png'))
                else:
                    ok, frame = video.read()
                    if not ok: break
                assert frame.shape == (640, 640, 3) and frame.dtype == np.uint8
                index = len(frames)
                path = output_pixels/f'frame_{index:04d}.png'
                if path.exists(): assert np.array_equal(frame, cv2.imread(str(path)))
                else: assert cv2.imwrite(str(path), frame, [cv2.IMWRITE_PNG_COMPRESSION, 3])
                assert np.array_equal(frame, cv2.imread(str(path))), 'PNG did not preserve decoded pixels'
                pts.append(index/60. if use_cache else video.get(cv2.CAP_PROP_POS_MSEC)/1000.)
                frames.append(frame)
                frame_inventory.append({'frame': index, 'time_s': index/60.,
                                        'path': path.relative_to(TASK).as_posix(), 'sha256': sha256(path)})
        finally:
            if video is not None:
                assert not video.read()[0], 'More than 240 decoded frames'
                video.release()
        assert len(frames) == 240
        timestamps = np.arange(240, dtype=np.float64)/60.
        assert np.allclose(pts, timestamps, atol=1e-6, rtol=0), 'Decoder PTS not consistent with CFR manifest'
        frames = np.stack(frames)
        gray = np.stack([np.asarray(Image.fromarray(frame[:, :, ::-1]).convert('L')) for frame in frames])
        profile = gray[:, 119:522].mean(axis=1)
        gradients = np.diff(profile, axis=1)
        position = np.argmax(np.abs(gradients), axis=1)+.5
        visible = np.max(np.abs(gradients), axis=1) > 100.
        position[~visible] = np.nan
        mean_luminance = gray.mean(axis=(1, 2))/255.
        measured = []
        for frame in range(240):
            measured.append({'frame': frame, 'source_time_s': timestamps[frame],
                             'edge_x_px': float(position[frame]) if visible[frame] else None,
                             'edge_visible': bool(visible[frame]), 'mean_gray_01': float(mean_luminance[frame])})
        audit = {'condition_id': condition_id, 'kind': condition['kind'],
                 'claimed_direction': condition['direction_in_video_coordinates'],
                 'resolution': [640, 640], 'decoded_frames': len(frames), 'fps': 60.,
                 'decoded_pts_max_error_s': float(np.max(np.abs(np.array(pts)-timestamps))),
                 'source_mp4_sha256': sha256(source), 'source_is_camera': False,
                 'pixel_values': [int(gray.min()), int(gray.max())],
                 'position_detection': 'row-averaged source image; boundary exists only if adjacent gray jump >100/255',
                 'decoded_pixel_cache_reused': bool(use_cache)}
        moving = (timestamps >= 1.) & (timestamps < 3.)
        if condition['kind'] in ('on', 'off'):
            usable = moving & visible
            assert usable.sum() >= 100
            slope = float(np.polyfit(timestamps[usable], position[usable], 1)[0])
            correlation = float(np.corrcoef(timestamps[usable], position[usable])[0, 1])
            expected = 1 if condition['direction_in_video_coordinates'] == 'right' else -1
            assert slope*expected > 0 and abs(correlation) > .999
            assert np.ptp(mean_luminance[timestamps < 1.]) < 1e-5 and np.ptp(mean_luminance[timestamps >= 3.]) < 1e-5
            change = float(mean_luminance[180]-mean_luminance[59])
            assert change < -.4 if condition['kind'] == 'off' else change > .4
            audit.update(measured_edge_velocity_px_s=slope, motion_position_time_correlation=correlation,
                         motion_luminance_change=change, static_before_and_after=True,
                         visible_edge_frame_count=int(visible.sum()),
                         visible_edge_first_time_s=float(timestamps[visible][0]),
                         visible_edge_last_time_s=float(timestamps[visible][-1]),
                         edge_first_visible_x_px=float(position[visible][0]),
                         edge_last_visible_x_px=float(position[visible][-1]))
        elif condition['kind'] == 'static':
            assert np.array_equal(frames, np.broadcast_to(frames[0], frames.shape))
            audit.update(decoded_static_bitwise=True, edge_x_px=float(position[0]))
        else:
            levels = np.round(mean_luminance, 2)
            assert len(np.unique(levels)) == 2 and levels.min() < .03 and levels.max() > .95
            transitions = np.flatnonzero(levels[1:] != levels[:-1])+1
            audit.update(brightness_transition_times_s=timestamps[transitions].tolist(),
                         decoded_gray_levels=np.unique(levels).tolist())
        existing_input = inputs/condition_id
        if resume and existing_input.exists():
            old_stimulus, old_grid, old_coords, old_metadata = load_stimulus(existing_input)
            receptor = np.load(existing_input/'source_hex.npy', allow_pickle=False)
            coords = [{key: (int(value) if key in ('hex_pixel', 'u', 'v', 'render_row', 'render_column')
                             else value == 'True' if key == 'center_in_camera_image' else float(value))
                       for key, value in row.items()} for row in old_coords]
            transform = old_metadata['spatial_transform']
        else:
            receptor, coords, transform = render_bgr_frames(frames, spatial_policy='native')
        assert transform['resize'] == 'none' and not transform['actual_boxeye_internal_resize']
        assert transform['input_hw'] == transform['render_hw'] == [640, 640]
        if coordinates is None: coordinates = coords
        else: assert coords == coordinates
        input_values, grid, alignment = cfr_zoh(receptor, timestamps)
        source_info = {'source_kind': 'synthetic_controlled_video', 'source_path': str(source),
                       'source_sha256': sha256(source), 'source_is_camera': False,
                       'timestamp_source': 'decoded_PTS_verified_against_60Hz_CFR', 'video_nominal_fps': 60.,
                       'declared_presentation_duration_s': 4., 'last_frame_presentation_valid_until_s': 4.,
                       'measured_delivery_fps': None, 'sensor_exposure_timestamps_available': False,
                       'decoded_pixel_records': str(output_pixels), 'condition_id': condition_id}
        metadata = {'schema': 'flyvis-camera-stimulus-v1', 'created_utc': utc_now(), 'source': source_info,
                    'source_commit': '92b3845cc426dd309a1a0e1b3890156c42e14021', 'target_model': 'flow/0000/000',
                    'stimulus_shape': [1, 800, 1, 721], 'stimulus_axes': ['sample', 'frame', 'channel', 'hex_pixel'],
                    'stimulus_dtype': 'float32', 'spatial_transform': transform, 'dt_s': .005, 'simulation_fps': 200.,
                    'temporal_method': 'zoh', 'causal': True, 'source_frame_count': 240,
                    'source_frame_span_s': float(timestamps[-1]), 'model_last_input_time_s': float(grid[-1]),
                    'duration_policy': 'known CFR last-frame hold on [239/60,4); 4s excluded from input, included as final activity time',
                    'time_semantics': 'file presentation time, not wall-clock camera receipt; activity after update=input+dt',
                    'model_weights_modified': False, 'neural_inference_executed': False,
                    'evidence_level': 'controlled synthetic MP4 decoded pixels -> official native BoxEye input'}
        bundle = StimulusBundle(input_values, grid, receptor, timestamps, coords, alignment, metadata)
        if resume and existing_input.exists():
            assert np.array_equal(input_values, old_stimulus) and np.array_equal(grid, old_grid)
        else:
            save_stimulus(bundle, existing_input)
        write_csv(output_pixels/'frames.csv', frame_inventory)
        write_csv(output_pixels/'measured_motion.csv', measured)
        write_json(output_pixels/'validation.json', audit)
        samples.append({'sample': sample, 'condition_id': condition_id, 'title': condition['title'],
                        'kind': condition['kind'], 'direction': condition['direction_in_video_coordinates'],
                        'motion_start_s': 1. if condition['kind'] in ('on', 'off') else None,
                        'motion_stop_s': 3. if condition['kind'] in ('on', 'off') else None,
                        'duration_s': 4., 'source': source.relative_to(TASK).as_posix()})
        values.append(input_values); hex_values.append(receptor); audits.append(audit)
        combined_alignment.extend([{'sample': sample, **row} for row in alignment])
        print(json.dumps({'condition': condition_id, 'status': 'PASS', 'shape': list(input_values.shape),
                          'motion': audit.get('measured_edge_velocity_px_s')}, ensure_ascii=False), flush=True)
        del frames, gray
    aggregate = new_directory(TASK/'input')
    np.save(aggregate/'stimulus.npy', np.concatenate(values, axis=0), allow_pickle=False)
    np.save(aggregate/'source_hex.npy', np.stack(hex_values), allow_pickle=False)
    np.save(aggregate/'time.npy', grid, allow_pickle=False)
    np.save(aggregate/'source_time.npy', timestamps, allow_pickle=False)
    write_csv(aggregate/'samples.csv', samples)
    write_csv(aggregate/'time_alignment.csv', combined_alignment)
    write_csv(aggregate/'input_hex_coordinates.csv', coordinates)
    aggregate_meta = {'schema': 'flyvis-controlled-video-input-v1', 'created_utc': utc_now(),
                      'source_kind': 'synthetic_controlled_video', 'source_is_camera': False, 'samples': samples,
                      'stimulus_shape': [6, 800, 1, 721], 'stimulus_dtype': 'float32', 'dt_s': .005,
                      'video_fps': 60., 'simulation_fps': 200., 'spatial_transform': transform,
                      'temporal_method': 'zoh', 'duration_policy': metadata['duration_policy'],
                      'time_semantics': metadata['time_semantics'],
                      'preprocessing_count_per_clip': 1, 'frozen_shared_input_for_comparison_modes': True,
                      'data_sha256': {p.name: sha256(p) for p in aggregate.iterdir() if p.is_file()}}
    write_json(aggregate/'metadata.json', aggregate_meta)
    write_json(TASK/'source_validation.json', {'status': 'PASS', 'created_utc': utc_now(),
               'original_manifest_sha256': sha256(manifest_path), 'original_file_hashes': original_hashes,
               'condition_audits': audits, 'decoded_frames_saved_losslessly': 1440,
               'standard_policy': 'native official BoxEye(15,13), no crop/resize/mirror/rotation',
               'input_shape': [6, 800, 1, 721], 'source_is_camera': False,
               'combined_video_use': 'continuous media demo only; six independent network experiments use separate clips'})
    write_json(TASK/'job_status.json', {'state': 'input_ready', 'job_id': TASK.name})


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--resume', action='store_true'); a = p.parse_args()
    try:
        main(resume=a.resume)
    except BaseException as error:
        write_json(TASK/'job_status.json', {'state': 'failed', 'stage': 'prepare', 'error': str(error), 'job_id': TASK.name})
        raise

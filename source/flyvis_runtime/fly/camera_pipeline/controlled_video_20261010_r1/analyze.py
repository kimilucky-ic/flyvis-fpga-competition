"""Independent pixel/input checks and measured original-model responses; no formal DSI."""
from __future__ import annotations
import csv
import json
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
from PIL import Image
from camera_pipeline.common import ROOT, sha256, utc_now, write_json
from camera_pipeline.controlled_video_20261010_r1.prepare import TASK, ORIGINAL, write_csv


def main():
    output = TASK/'analysis'
    output.mkdir(exist_ok=False)
    meta = json.loads((TASK/'input/metadata.json').read_text(encoding='utf-8'))
    for name, digest in meta['data_sha256'].items(): assert sha256(TASK/'input'/name) == digest
    source_validation = json.loads((TASK/'source_validation.json').read_text(encoding='utf-8'))
    assert sha256(ORIGINAL/'manifest.json') == source_validation['original_manifest_sha256']
    for name, digest in source_validation['original_file_hashes'].items():
        assert sha256(ORIGINAL/name.replace('\\', '/')) == digest
    stimulus = np.load(TASK/'input/stimulus.npy', allow_pickle=False)
    receptors = np.load(TASK/'input/source_hex.npy', allow_pickle=False)
    grid = np.load(TASK/'input/time.npy', allow_pickle=False)
    source_time = np.load(TASK/'input/source_time.npy', allow_pickle=False)
    with (TASK/'input/input_hex_coordinates.csv').open(encoding='utf-8') as file:
        coords = list(csv.DictReader(file))
    row = np.array([int(c['render_row']) for c in coords]); col = np.array([int(c['render_column']) for c in coords])
    x = np.array([float(c['source_center_x']) for c in coords])
    bound = 169*(np.finfo(np.float32).eps/2)/(1-169*(np.finfo(np.float32).eps/2))+3*np.finfo(np.float32).eps/2
    # Bound covers summing 169 nonnegative float32 values, normalization and division.
    max_error, transitions = 0., []
    source_indices = np.searchsorted(source_time, grid, side='right')-1
    assert stimulus.shape == (6, 800, 1, 721) and stimulus.dtype == np.float32
    assert np.isfinite(stimulus).all() and stimulus.min() >= 0 and stimulus.max() <= 1
    with (TASK/'input/time_alignment.csv').open(encoding='utf-8') as file:
        alignment = list(csv.DictReader(file))
    assert len(alignment) == 4800
    for sample, condition in enumerate(meta['samples']):
        condition_id = condition['condition_id']
        folder = TASK/'decoded_frames'/condition_id
        with (folder/'frames.csv').open(encoding='utf-8') as file: frames = list(csv.DictReader(file))
        assert len(frames) == 240
        for frame, entry in enumerate(frames):
            path = TASK/entry['path']
            assert sha256(path) == entry['sha256'] and float(entry['time_s']) == source_time[frame]
            # Independent float64 summed-area means, directly from saved decoded pixels.
            gray = np.asarray(Image.open(path).convert('L'), dtype=np.float64)/255.
            integral = np.pad(gray.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
            expected = (integral[row+7, col+7]-integral[row-6, col+7]
                        -integral[row+7, col-6]+integral[row-6, col-6])/169.
            error = float(np.max(np.abs(expected-receptors[sample, frame])))
            max_error = max(max_error, error)
            assert error <= bound, (sample, frame, error, bound)
        assert np.array_equal(stimulus[sample, :, 0], receptors[sample, source_indices])
        assert np.array_equal(stimulus[sample:sample+1], np.load(TASK/'inputs'/condition_id/'stimulus.npy', allow_pickle=False))
        for step in range(800):
            entry = alignment[sample*800+step]
            assert int(entry['sample']) == sample and int(entry['model_frame']) == step
            assert int(entry['source_left_frame']) == int(entry['source_right_frame']) == source_indices[step]
            assert float(entry['model_time_s']) == grid[step] and float(entry['right_weight']) == 0
            assert entry['uses_future_frame'] == 'False'
        if condition['kind'] in ('on', 'off'):
            crossed = receptors[sample] > .5 if condition['kind'] == 'on' else receptors[sample] < .5
            assert crossed[-1].all() and not crossed[0].any()
            crossing = source_time[np.argmax(crossed, axis=0)]
            sign = 1 if condition['direction'] == 'right' else -1
            correlation = float(np.corrcoef(x, crossing)[0, 1])
            assert correlation*sign > .999
            transitions.append({'condition_id': condition_id, 'source_x_crossing_time_correlation': correlation,
                                'crossing_time_first_s': float(crossing.min()), 'crossing_time_last_s': float(crossing.max())})
            write_csv(output/f'{condition_id}_hex_crossings.csv', [{'hex_pixel': i, 'u': int(coords[i]['u']),
                      'v': int(coords[i]['v']), 'source_x_px': x[i], 'crossing_time_s': crossing[i]}
                      for i in range(721)])
    records = [json.loads((TASK/name/'result.json').read_text(encoding='utf-8')) for name in ('gpu_full_r1', 'gpu_full_r2')]
    for directory, record in zip(('gpu_full_r1', 'gpu_full_r2'), records):
        assert record['status'] == 'PASS' and record['weights_exact_before_and_after']
        assert record['input_sha256'] == sha256(TASK/'input/stimulus.npy')
        for name, digest in record['data_sha256'].items(): assert sha256(TASK/directory/name) == digest
        assert len(set(t['same_initial_state_value_sha256'] for t in record['condition_timings'])) == 1
        assert all(t['warmup_in_condition'] == 0 for t in record['condition_timings'])
    for name in ('activity_central', 'activity_T4_T5', 'initial_state_full', 'final_state_full', 'time', 'activity_time'):
        assert np.array_equal(np.load(TASK/f'gpu_full_r1/{name}.npy', allow_pickle=False),
                              np.load(TASK/f'gpu_full_r2/{name}.npy', allow_pickle=False)), name
    activity = np.load(TASK/'gpu_full_r1/activity_central.npy', allow_pickle=False)
    cells = np.load(TASK/'gpu_full_r1/cell_types.npy', allow_pickle=False).tolist()
    activity_time = np.load(TASK/'gpu_full_r1/activity_time.npy', allow_pickle=False)
    assert np.array_equal(activity_time, grid+.005) and activity_time[-1] == 4.
    targets = records[0]['target_types']; indices = [cells.index(c) for c in targets]
    target_activity = activity[:, :, indices].astype(np.float64)
    baseline = (grid >= .5) & (grid < 1.)
    comparison = (grid >= 1.) & (grid < 3.)
    metrics = []
    for sample, condition in enumerate(meta['samples']):
        for index, cell in enumerate(targets):
            curve = target_activity[sample, :, index]
            base = float(curve[baseline].mean())
            delta = curve[comparison]-base
            peak_frame = np.flatnonzero(comparison)[np.argmax(np.abs(delta))]
            metrics.append({'sample': sample, 'condition_id': condition['condition_id'], 'cell_type': cell,
                            'baseline_input_window_start_s': .5, 'baseline_input_window_stop_exclusive_s': 1.,
                            'comparison_input_window_start_s': 1., 'comparison_input_window_stop_exclusive_s': 3.,
                            'baseline_mean_activity': base, 'raw_peak_in_window': float(curve[comparison].max()),
                            'raw_min_in_window': float(curve[comparison].min()),
                            'delta_positive_peak': float(delta.max()), 'delta_negative_peak': float(delta.min()),
                            'delta_absolute_peak': float(np.abs(delta).max()),
                            'delta_rms': float(np.sqrt(np.mean(delta*delta))), 'delta_mean': float(delta.mean()),
                            'peak_input_time_s': float(grid[peak_frame]), 'peak_activity_time_s': float(activity_time[peak_frame]),
                            'static_window_std': float(curve[comparison].std()) if sample == 0 else None})
    write_csv(output/'T4_T5_condition_metrics.csv', metrics)
    differences = []
    for kind, right, left in [('off', 1, 2), ('on', 3, 4)]:
        for index, cell in enumerate(targets):
            curve = target_activity[right, comparison, index]-target_activity[left, comparison, index]
            differences.append({'polarity': kind, 'cell_type': cell, 'window_input_start_s': 1.,
                                'window_input_stop_exclusive_s': 3., 'right_minus_left_mean': float(curve.mean()),
                                'right_left_rms_difference': float(np.sqrt(np.mean(curve*curve))),
                                'right_left_max_absolute_difference': float(np.abs(curve).max())})
    write_csv(output/'opposite_direction_differences.csv', differences)
    os.environ.update(MPLBACKEND='Agg', MPLCONFIGDIR=str(ROOT/'runtime/matplotlib'))
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(6, 2, figsize=(13, 17), sharex=True)
    for sample, condition in enumerate(meta['samples']):
        for group in range(2):
            ax = axes[sample, group]
            for index in range(group*4, (group+1)*4):
                ax.plot(activity_time, target_activity[sample, :, index], label=targets[index], lw=.9)
            ax.axvspan(1.005, 3., alpha=.08, color='black')
            ax.set_title(f"{condition['condition_id']} | {'T4' if group == 0 else 'T5'}")
            ax.set_ylabel('central activity (model units)'); ax.legend(ncol=4, fontsize=8); ax.grid(alpha=.2)
    for ax in axes[-1]: ax.set_xlabel('Post-Euler-update time (s)')
    fig.suptitle('Original Full FlyVis | six independent synthetic-file conditions | same frozen full initial state')
    fig.tight_layout(); fig.savefig(output/'all_conditions_T4_T5.png', dpi=130); plt.close(fig)
    fig, axes = plt.subplots(2, 4, figsize=(15, 7), sharex=True)
    for index, ax in enumerate(axes.flat):
        for sample in (1, 2, 3, 4):
            ax.plot(activity_time, target_activity[sample, :, index], label=meta['samples'][sample]['condition_id'][3:], lw=1)
        ax.axvspan(1.005, 3., color='black', alpha=.08); ax.set_title(targets[index]); ax.grid(alpha=.2)
        ax.legend(fontsize=7); ax.set_xlabel('post-update time (s)')
    fig.suptitle('Actual opposite-direction/polarity responses; no official DSI or camera claim')
    fig.tight_layout(); fig.savefig(output/'direction_comparison.png', dpi=140); plt.close(fig)
    footprint = np.zeros((640, 640), bool)
    for y, xcol in zip(row, col): footprint[y-6:y+7, xcol-6:xcol+7] = True
    fig, ax = plt.subplots(figsize=(7, 7))
    frame = np.asarray(Image.open(TASK/'decoded_frames/00_static_edge/frame_0000.png'))
    ax.imshow(frame); overlay = np.zeros((640, 640, 4)); overlay[footprint] = [0, 1, 1, .15]; ax.imshow(overlay)
    ax.scatter(col, row, s=3, color='lime'); ax.set_title('Actual decoded 640x640 frame: 721 centers + true 13x13 footprint')
    ax.set_xlabel('source column (px)'); ax.set_ylabel('source row (px; downward)')
    fig.tight_layout(); fig.savefig(output/'sampling_overlay.png', dpi=140); plt.close(fig)
    static_std = max(m['static_window_std'] for m in metrics if m['sample'] == 0)
    result = {'schema': 'flyvis-controlled-video-analysis-v1', 'status': 'PASS', 'checked_utc': utc_now(),
              'input_shape': [6, 800, 1, 721], 'input_sha256': sha256(TASK/'input/stimulus.npy'),
              'decoded_PNG_frames_independently_checked': 1440, 'receptor_means_checked': 6*240*721,
              'independent_receptor_mean_max_abs_error': max_error, 'declared_float32_rounding_bound': float(bound),
              'rounding_bound_scope': 'input convolution/gray arithmetic only, not relaxed neural equivalence tolerance',
              'source_direction_crossings': transitions, 'all_4800_ZOH_values_and_indices_exact': True,
              'last_input_s': float(grid[-1]), 'last_post_update_activity_s': float(activity_time[-1]),
              'independent_GPU_replay_bitwise_equal': True, 'complete_final_states_bitwise_equal': True,
              'same_frozen_initial_state_bitwise_equal': True, 'weights_exact_before_and_after': True,
              'maximum_static_T4_T5_std_in_1_3s_window': static_std,
              'condition_metrics': metrics, 'opposite_direction_differences': differences,
              'sampling': {'image_hw': [640, 640], 'covered_pixels': int(footprint.sum()),
                           'coverage_fraction': float(footprint.mean()), 'bounds_inclusive_xyxy': [119, 119, 521, 521]},
              'source_is_camera': False, 'formal_DSI_computed': False, 'physical_speed_calibration': False,
              'evidence_scope': 'single fixed six-condition synthetic-file test; descriptive differences only, no biological/population statistics',
              'data_sha256': {p.name: sha256(p) for p in output.iterdir() if p.is_file()}}
    write_json(output/'analysis.json', result)
    print(json.dumps({key: result[key] for key in ('status', 'input_sha256', 'independent_GPU_replay_bitwise_equal',
                                                 'independent_receptor_mean_max_abs_error', 'maximum_static_T4_T5_std_in_1_3s_window')}), flush=True)


if __name__ == '__main__':
    main()

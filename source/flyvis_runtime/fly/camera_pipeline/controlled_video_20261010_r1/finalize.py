"""Finalize this controlled-file experiment and a compact evidence report."""
from __future__ import annotations
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
from camera_pipeline.common import ROOT, sha256, utc_now, write_json
from camera_pipeline.controlled_video_20261010_r1.prepare import TASK, ORIGINAL
from camera_pipeline.controlled_video_20261010_r1.gui_handoff import load_experiment


def main():
    analysis = json.loads((TASK/'analysis/analysis.json').read_text(encoding='utf-8'))
    source = json.loads((TASK/'source_validation.json').read_text(encoding='utf-8'))
    result = json.loads((TASK/'gpu_full_r1/result.json').read_text(encoding='utf-8'))
    replay = json.loads((TASK/'gpu_full_r2/result.json').read_text(encoding='utf-8'))
    experiment = load_experiment(TASK/'gui/experiment.json')
    assert analysis['status'] == source['status'] == result['status'] == replay['status'] == 'PASS'
    assert replay['initializer']['warmup_count'] == 0 and result['initializer']['warmup_count'] == 1
    assert np.array_equal(np.load(TASK/'gpu_full_r1/initial_state_full.npy', allow_pickle=False),
                          np.load(TASK/'gpu_full_r2/initial_state_full.npy', allow_pickle=False))
    for package, manifest_file in [(ROOT, ROOT/'results/validation/manifest.json'),
                                   (ROOT, ROOT/'phase2/results/manifest.json')]:
        manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
        entries = manifest['files'].items() if isinstance(manifest['files'], dict) else (
            (row['path'], row['sha256']) for row in manifest['files'])
        assert all(sha256(package/name) == digest for name, digest in entries)
    protected = json.loads((TASK/'logs/protected_after.json').read_text(encoding='utf-8'))
    assert protected['protected_hashes_unchanged'] and not protected['tracked_upstream_status']
    assert sha256(ORIGINAL/'manifest.json') == source['original_manifest_sha256']
    for name, digest in source['original_file_hashes'].items(): assert sha256(ORIGINAL/name.replace('\\', '/')) == digest
    tests = (TASK/'logs/protocol_tests.log').read_text(encoding='utf-8')
    assert 'Ran 5 tests' in tests and tests.rstrip().endswith('OK')
    def metric(sample, cell):
        return next(row for row in analysis['condition_metrics'] if row['sample'] == sample and row['cell_type'] == cell)
    comparisons = [{'cell_type': cell, 'polarity': polarity, 'right_raw_peak': metric(right, cell)['raw_peak_in_window'],
                    'left_raw_peak': metric(left, cell)['raw_peak_in_window']}
                   for cell, polarity, right, left in [('T4a', 'ON', 3, 4), ('T4b', 'ON', 3, 4),
                                                       ('T5a', 'OFF', 1, 2), ('T5b', 'OFF', 1, 2)]]
    acceptance = {'schema': 'flyvis-controlled-video-acceptance-v1', 'status': 'PASS', 'checked_utc': utc_now(),
                  'scope': 'six controlled synthetic file conditions through original Full GPU network',
                  'source_is_camera': False, 'source_frames_per_condition': 240, 'video_fps': 60.,
                  'input_shape': [6, 800, 1, 721], 'activity_shape': [6, 800, 65], 'dt_s': .005,
                  'simulation_fps': 200., 'same_frozen_initial_state_for_all_conditions': True,
                  'initial_state_shape': [1, 45669], 'initial_state_sha256': sha256(TASK/'gpu_full_r1/initial_state_full.npy'),
                  'input_sha256': sha256(TASK/'input/stimulus.npy'), 'output_sha256': sha256(TASK/'gpu_full_r1/activity_central.npy'),
                  'model_identity': result['model_identity'], 'device': result['environment'],
                  'weights_exact_before_and_after': True, 'independent_GPU_replay_bitwise_equal': True,
                  'complete_final_states_replay_bitwise_equal': True, 'all_4800_ZOH_values_and_indices_checked': True,
                  'source_PNG_frames_checked': 1440, 'all_1038240_receptor_means_checked': True,
                  'independent_receptor_mean_max_error': analysis['independent_receptor_mean_max_abs_error'],
                  'source_motion_and_hex_direction_checks': 'PASS', 'known_CFR_endpoint_policy': '800 inputs on [0,4), final activity4s',
                  'protocol_tests_passed': 5, 'GUI_local_descriptor_and_reader': 'PASS',
                  'gui_descriptor_sha256': sha256(TASK/'gui/experiment.json'), 'gui_loaded': False,
                  'first_stage_files_unchanged': 324, 'previous_state_stage_files_unchanged': 68,
                  'protected_reference_files_unchanged': 84, 'source_material_manifest_files_unchanged': 9,
                  'representative_raw_peak_comparisons': comparisons,
                  'statistics_scope': 'descriptive single-file responses, 1<=input_time<3s; no formal DSI or p-values',
                  'activity_units': 'original model node activity; signed values allowed, not a firing-rate Hz measurement',
                  'neural_computation_s': result['total_inference_s'],
                  'compute_steps_per_s_excluding_io': 4800/result['total_inference_s'],
                  'processing_mode': 'offline', 'real_time_claim': False,
                  'new_camera_capture': False, 'combined_24s_continuous_network_inference': False,
                  'modes_verified': ['Full'], 'gui_source_modified': False, 'fpga_execution': False}
    write_json(TASK/'acceptance.json', acceptance)
    details = '\n'.join(f"- {row['cell_type']} / {row['polarity']}: right peak {row['right_raw_peak']:.7f}, left peak {row['left_raw_peak']:.7f}."
                        for row in comparisons)
    report = f'''# Controlled synthetic-video Full experiment

2026-10-10, PASS. Evidence: controlled local MP4 file input, original complete FlyVis GPU inference and independent replay.
This is not real-camera or FPGA evidence. Original supplied media, both earlier sealed packages and protected references retain their hashes.

## Fixed input and initialization

Six separate 640x640/60Hz/240-frame clips. Original native BoxEye(15,13,mean), official Pillow RGB->L /255,
no crop, resize, letterbox, mirror or rotation. MP4 compression is preserved in decoded input: the frozen receptor range is
{float(experiment.stimulus.min()):.8f}..{float(experiment.stimulus.max()):.8f}; it is not forced back to ideal binary values.
Source decoded PTS match the declared 60Hz CFR grid. Known last-frame presentation is [239/60,4), unlike unknown camera exposure/delivery.
800 actual causal ZOH inputs on [0,4), step3.995s -> after-update state4.000s. Six samples remain independent.
The 24s combined file is media for demonstration, not an inferred continuous trajectory here.

One original full-network 1s grey0.5 initialization is frozen as [1,45669]. Every condition uses those exact values.
The independent replay restores the same file and performs zero new warmup. Original source/checkpoint/topology identities
and weights/buffers are checked. {result['model_identity']['nodes']} nodes, {result['model_identity']['edges']} edges.
Device: {result['environment']['gpu']}, torch {result['environment']['torch']}, FlyVis {result['environment']['flyvis']}.

## Observed responses

All curves and metrics come from saved computed float32 activities, not procedural response generation.
Raw peaks below use the declared comparison interval 1 <= input_time < 3s; the corresponding output times are input+dt.
They are original signed model-state units, not neuronal firing rates in Hz.

{details}

These paired conditions share the same initial state and the same starting full-field polarity within each ON/OFF pair.
Opposite directions have different computed responses in this fixed pixel-space experiment. This does not establish a general
direction-tuning curve, biological preferred angle, accurate physical speed or complete optical flow.
The static condition has maximum T4/T5 standard deviation {analysis['maximum_static_T4_T5_std_in_1_3s_window']:.9g}
in the 1..3s input window; its absolute activity is not assumed zero. A small residual offset relative to the0.5..1s baseline is retained.
The full-field brightness condition changes at1/2/3s and also produces T4/T5 transients; therefore an activity peak alone is not evidence of object motion.
Both positive/negative changes and all eight types are retained in metrics rather than selecting only positive peaks.

## Reproducibility and GUI

Both GPU runs have bitwise equal65-type activities,8-type T4/T5 activities,full initial state and all45669-node final states.
All1440 saved decoded PNGs and1,038,240 independent float64 receptor means checked; max input arithmetic difference
{analysis['independent_receptor_mean_max_abs_error']:.9g} within the predeclared nonnegative-float32-sum bound.
All4800 ZOH source selections and values exactly checked. No neural tolerance was relaxed.
Five endpoint/causality tests passed, plus independent GUI descriptor loading and60 event/boundary payload checks.

GUI: [descriptor](gui/experiment.json), [reader](gui_handoff.py), [handoff verification](gui/handoff_validation.json).
Local references only, source_kind=synthetic_controlled_video, source_is_camera=false, source receipt UTC/monotonic are null.
Only Full is available. Future modes must consume the exact frozen input and common initial state; do not preprocess per mode.
Camera collector remains the existing unique owner and was not opened. GUI source was not modified by this lane.

## Timing and remaining evidence

4800 synchronized GPU neural steps took {result['total_inference_s']:.6f}s, {4800/result['total_inference_s']:.3f} steps/s,
excluding initialization, file decoding, CPU BoxEye, uploads/downloads and result/plot writing. This is offline throughput.
Physical screen recapture, camera/ISP controls, capture-to-output latency and stable live throughput remain untested.
Future screen capture must create a new recording and frozen input with actual measured timestamps and sampled screen coverage.

## Corrected input audit

The first audit assumed an edge always existed in the full frame. The left-moving clip starts uniformly white while the edge is outside the frame.
An argmax on a zero gradient falsely returned column0.5 and failed direction checking. Detection now requires a real adjacent grey jump>100/255;
only visible boundary frames are used for the velocity fit, with first/last visible times recorded. Measured image slopes are approximately
+/-320.998 pixels/s, not calibrated visual angles or physical velocities. All721 crossing times confirm the mapped direction.
Original clips and already frozen inputs were preserved. The failure log and corrected audit are retained.

Artifacts: [all six actual curves](analysis/all_conditions_T4_T5.png), [opposite direction curves](analysis/direction_comparison.png),
[sampling footprint](analysis/sampling_overlay.png), [metrics](analysis/T4_T5_condition_metrics.csv),
[differences](analysis/opposite_direction_differences.csv), [source audit](source_validation.json),
[analysis](analysis/analysis.json), [acceptance](acceptance.json), [commands](README.md).
'''
    (TASK/'REPORT.md').write_text(report, encoding='utf-8')
    write_json(TASK/'job_status.json', {'state': 'complete', 'job_id': TASK.name, 'result': 'acceptance.json'})
    print(json.dumps({'status': 'PASS', 'input_sha256': acceptance['input_sha256'],
                      'output_sha256': acceptance['output_sha256'], 'source_is_camera': False}), flush=True)


if __name__ == '__main__': main()

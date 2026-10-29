"""Local-only, verified synthetic-video GUI API. No camera capture or GUI modifications."""
from __future__ import annotations
import argparse
import csv
from dataclasses import dataclass
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
from PIL import Image
from camera_pipeline.common import ROOT, sha256, utc_now, write_json
from camera_pipeline.controlled_video_20261010_r1.prepare import TASK


def csv_rows(path):
    with Path(path).open(encoding='utf-8', newline='') as file: return list(csv.DictReader(file))


@dataclass
class ControlledVideoExperiment:
    descriptor: dict
    stimulus: np.ndarray
    activity: np.ndarray
    source_time: np.ndarray
    input_time: np.ndarray
    activity_time: np.ndarray
    cell_types: list
    coordinates: list
    neurons: list
    frames: list
    source_indices: np.ndarray
    signatures: dict

    def describe(self):
        return {key: self.descriptor[key] for key in ('experiment_id', 'dataset_type', 'source_kind', 'source_is_camera',
                'condition_execution', 'samples', 'model', 'axes', 'timing', 'modes', 'limitations', 'processing_mode')}

    def read_step(self, sample, step):
        if not 0 <= sample < 6 or not 0 <= step < 800: raise IndexError('Sample/step out of range')
        for path, expected in self.signatures.items():
            stat = path.stat()
            if (stat.st_size, stat.st_mtime_ns) != expected: raise ValueError('Verified experiment changed; reload and verify')
        source = int(self.source_indices[step]); entry = self.frames[sample][source]
        path = (TASK/entry['path']).resolve()
        if not path.is_relative_to(TASK.resolve()) or sha256(path) != entry['sha256']:
            raise ValueError('Decoded frame path/hash mismatch')
        bgr = np.asarray(Image.open(path).convert('RGB'))[:, :, ::-1].copy()
        return {'experiment_id': self.descriptor['experiment_id'], 'sample': sample, 'step': step,
                'condition_id': self.descriptor['samples'][sample]['condition_id'],
                'source_frame': source, 'source_time_s': float(self.source_time[source]),
                'input_time_s': float(self.input_time[step]), 'activity_time_s': float(self.activity_time[step]),
                'source_received_utc': None, 'source_received_monotonic_ns': None,
                'held_frame_age_s': float(self.input_time[step]-self.source_time[source]),
                'bgr': bgr, 'hex_input': self.stimulus[sample, step, 0],
                'activity_central': self.activity[sample, step], 'cell_types': self.cell_types,
                'source_kind': 'synthetic_controlled_video', 'live_camera': False,
                'display_kind': 'verified_offline_replay'}


def load_experiment(path):
    descriptor = json.loads(Path(path).read_text(encoding='utf-8'))
    if descriptor.get('schema') != 'flyvis-controlled-video-experiment-v1' or descriptor.get('status') != 'PASS':
        raise ValueError('Unknown or unaccepted controlled-video descriptor')
    if descriptor['source_kind'] != 'synthetic_controlled_video' or descriptor['source_is_camera']:
        raise ValueError('Synthetic-file provenance must not claim camera capture')
    paths, signatures = {}, {}
    for entry in descriptor['files']:
        target = (ROOT/entry['path']).resolve()
        if not target.is_relative_to(TASK.resolve()): raise ValueError('Reference escapes isolated experiment')
        if target.stat().st_size != entry['bytes'] or sha256(target) != entry['sha256']:
            raise ValueError(f"Hash/size mismatch: {entry['role']}")
        if entry['role'] in paths: raise ValueError('Duplicate role')
        paths[entry['role']] = target
        stat = target.stat(); signatures[target] = (stat.st_size, stat.st_mtime_ns)
    def array(role): return np.load(paths[role], allow_pickle=False, mmap_mode='r')
    stimulus, activity = array('stimulus'), array('activity')
    source_time, input_time, activity_time = array('source_time'), array('input_time'), array('activity_time')
    source_hex = array('source_hex')
    if (stimulus.shape != (6, 800, 1, 721) or activity.shape != (6, 800, 65)
            or stimulus.dtype != np.float32 or activity.dtype != np.float32
            or not np.isfinite(stimulus).all() or not np.isfinite(activity).all()
            or stimulus.min() < 0 or stimulus.max() > 1): raise ValueError('Invalid shape/dtype/range')
    if not (np.array_equal(source_time, np.arange(240)/60.)
            and np.array_equal(input_time, np.arange(800)*.005)
            and np.array_equal(activity_time, input_time+.005)): raise ValueError('Incorrect file/input/post-update clocks')
    indices = np.searchsorted(source_time, input_time, side='right')-1
    if not np.array_equal(stimulus[:, :, 0], source_hex[:, indices]): raise ValueError('Inputs are not actual causal ZOH values')
    if descriptor['timing']['last_frame_valid_until_s'] != 4. or descriptor['timing']['input_stop_exclusive_s'] != 4.:
        raise ValueError('Incorrect known-CFR presentation endpoint')
    coords, neurons = csv_rows(paths['coordinates']), csv_rows(paths['neurons'])
    cells = array('cell_types').tolist()
    if ([int(row['hex_pixel']) for row in coords] != list(range(721)) or len(cells) != 65
            or [row['cell_type'] for row in neurons] != cells): raise ValueError('Coordinate/cell order mismatch')
    analysis = json.loads(paths['analysis'].read_text(encoding='utf-8'))
    result = json.loads(paths['result'].read_text(encoding='utf-8'))
    metadata = json.loads(paths['input_metadata'].read_text(encoding='utf-8'))
    if not (analysis['status'] == result['status'] == 'PASS' and analysis['independent_GPU_replay_bitwise_equal']
            and result['weights_exact_before_and_after'] and result['same_initial_state_for_all_conditions']
            and result['input_sha256'] == analysis['input_sha256'] == sha256(paths['stimulus'])
            and descriptor['model'] == result['model_identity'] and descriptor['samples'] == metadata['samples']):
        raise ValueError('Input/result/acceptance/model identity mismatch')
    geometry = metadata['spatial_transform']
    if (geometry['policy'] != 'native' or geometry['resize'] != 'none' or geometry['crop'] is not None
            or geometry['mirror_horizontal'] or geometry['mirror_vertical'] or geometry['rotation_degrees'] != 0
            or geometry['actual_boxeye_internal_resize']): raise ValueError('Unaccepted geometry')
    frames = [csv_rows(paths[f'frames_{sample}']) for sample in range(6)]
    if any(len(rows) != 240 for rows in frames): raise ValueError('Incomplete decoded frames')
    return ControlledVideoExperiment(descriptor, stimulus, activity, source_time, input_time, activity_time,
                                     cells, coords, neurons, frames, indices, signatures)


def build():
    output = TASK/'gui'; output.mkdir(exist_ok=False)
    data, result = TASK/'input', TASK/'gpu_full_r1'
    record = json.loads((result/'result.json').read_text(encoding='utf-8'))
    meta = json.loads((data/'metadata.json').read_text(encoding='utf-8'))
    files = {'stimulus': data/'stimulus.npy', 'source_hex': data/'source_hex.npy', 'source_time': data/'source_time.npy',
             'input_time': data/'time.npy', 'input_metadata': data/'metadata.json', 'coordinates': data/'input_hex_coordinates.csv',
             'samples': data/'samples.csv', 'alignment': data/'time_alignment.csv', 'activity': result/'activity_central.npy',
             'activity_T4_T5': result/'activity_T4_T5.npy', 'activity_time': result/'activity_time.npy',
             'cell_types': result/'cell_types.npy', 'neurons': result/'neurons.csv', 'result': result/'result.json',
             'initial_state_full': result/'initial_state_full.npy', 'initial_state_checkpoint': result/'initial_state.pt',
             'analysis': TASK/'analysis/analysis.json', 'source_validation': TASK/'source_validation.json'}
    for sample, condition in enumerate(meta['samples']):
        files[f'frames_{sample}'] = TASK/'decoded_frames'/condition['condition_id']/'frames.csv'
        files[f'source_video_{sample}'] = TASK/condition['source']
    descriptor = {'schema': 'flyvis-controlled-video-experiment-v1', 'status': 'PASS', 'created_utc': utc_now(),
                  'experiment_id': 'controlled_synthetic_video_6_full_native_zoh_20261010_r1',
                  'dataset_type': 'controlled_video_flyvis', 'access': 'local_reference_only',
                  'source_kind': 'synthetic_controlled_video', 'source_is_camera': False,
                  'processing_mode': 'offline', 'origin_execution_kind': 'new_inference', 'display_kind': 'verified_offline_replay',
                  'condition_execution': 'six independent 4s clips, same frozen 45669-node initial state',
                  'samples': meta['samples'], 'model': record['model_identity'], 'device': record['environment'],
                  'axes': {'stimulus': ['sample', 'frame', 'channel', 'hex_pixel'], 'activity': ['sample', 'frame', 'central_cell_type'],
                           'stimulus_shape': [6, 800, 1, 721], 'activity_shape': [6, 800, 65]},
                  'timing': {'source_clock': 'verified_60Hz_file_presentation', 'sensor_or_capture_utc_available': False,
                             'dt_s': .005, 'input_clock': 'clip-relative 5ms input grid',
                             'activity_clock': 'same-index post-Euler state=input+dt', 'last_frame_valid_until_s': 4.,
                             'input_stop_exclusive_s': 4., 'last_input_s': 3.995, 'last_activity_s': 4., 'legacy_offset_s': 0},
                  'frozen_comparison_input_sha256': record['input_sha256'],
                  'frozen_common_initial_state_sha256': sha256(result/'initial_state_full.npy'),
                  'modes': {'Full': 'PASS', 'Ablation': 'unavailable', 'Python Replacement': 'unavailable', 'FPGA Replacement': 'unavailable'},
                  'four_mode_contract': 'all modes must use the same frozen input and initial-state bytes; preprocessing is not repeated per mode',
                  'collector_owner': 'camera_pipeline.capture.CameraSession; not used for this file-input experiment',
                  'gui_source_modified': False, 'gui_loaded': False,
                  'limitations': ['synthetic pixel-space file, not screen-recorded camera evidence',
                                  'not official angular-space MovingEdge/12-direction DSI',
                                  '24s media is a demo; independent activities are not a continuous 24s network trajectory',
                                  'screen recapture must be a separate measured/timestamped input'],
                  'files': [{'role': role, 'path': path.relative_to(ROOT).as_posix(), 'sha256': sha256(path), 'bytes': path.stat().st_size}
                            for role, path in files.items()]}
    path = output/'experiment.json'; write_json(path, descriptor)
    experiment = load_experiment(path)
    for sample in range(6):
        for step in (0, 199, 200, 400, 599, 600, 796, 797, 798, 799):
            payload = experiment.read_step(sample, step)
            assert payload['source_time_s'] <= payload['input_time_s'] < 4.
            assert payload['activity_time_s'] == payload['input_time_s']+.005
            assert np.array_equal(payload['activity_central'], experiment.activity[sample, step])
    write_json(output/'handoff_validation.json', {'status': 'PASS', 'descriptor_sha256': sha256(path),
               'all_4800_zoh_values_checked': True, '60_boundary_and_event_display_payloads_checked': True,
               'file_input_not_camera': True, 'gui_source_modified': False, 'gui_loaded': False})
    print(json.dumps({'status': 'PASS', 'descriptor': str(path), 'sha256': sha256(path)}), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--verify', type=Path); a = p.parse_args()
    if a.verify:
        experiment = load_experiment(a.verify)
        print(json.dumps({'status': 'PASS', 'samples': 6, 'frames_per_sample': 800, 'source_is_camera': False}))
    else: build()

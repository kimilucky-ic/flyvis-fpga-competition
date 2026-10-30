"""A verified local-reference experiment descriptor and read-only GUI consumer API.

No VideoCapture, GUI source changes, HTTP server, uploads or embedded raw media.
The camera family has source/input/post-update clocks, never the legacy -1s axis.
"""
from __future__ import annotations
import argparse
import csv
from dataclasses import dataclass
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
from camera_pipeline.common import ROOT, new_directory, sha256, utc_now, write_json

SCHEMA = 'flyvis-camera-experiment-v2'
TARGETS = [f'T{n}{s}' for n in (4, 5) for s in 'abcd']


def read_csv(path):
    with Path(path).open(encoding='utf-8', newline='') as file:
        return list(csv.DictReader(file))


def validate_alignment(source_time, input_time, activity_time, rows, source_hex, stimulus, dt):
    if dt != .005 or not np.array_equal(input_time, np.arange(len(input_time))*dt):
        raise ValueError('Camera input time must start at zero on the exact 5ms grid')
    if not np.array_equal(activity_time, input_time+dt):
        raise ValueError('Activity time must be AFTER the same-index Euler update (input+dt)')
    if source_time[0] != 0 or not np.all(np.diff(source_time) > 0):
        raise ValueError('Invalid measured source frame time')
    if input_time[-1] > source_time[-1] or len(rows) != len(input_time):
        raise ValueError('Input extends past the last measured frame or alignment length mismatch')
    indices = np.searchsorted(source_time, input_time, side='right')-1
    for i, (row, source) in enumerate(zip(rows, indices)):
        if (int(row['model_frame']) != i or float(row['model_time_s']) != input_time[i]
                or int(row['source_left_frame']) != source or int(row['source_right_frame']) != source
                or float(row['source_left_time_s']) != source_time[source]
                or float(row['source_right_time_s']) != source_time[source]
                or float(row['right_weight']) != 0 or row['uses_future_frame'] != 'False'):
            raise ValueError(f'Noncausal or shifted frame alignment at step {i}')
    if not np.array_equal(stimulus[0, :, 0], source_hex[indices]):
        raise ValueError('721 input values do not match the actual source frame selected by ZOH')
    return indices


@dataclass
class CameraExperiment:
    descriptor: dict
    paths: dict
    frames: np.ndarray
    source_time: np.ndarray
    source_timestamps: list
    input_time: np.ndarray
    activity_time: np.ndarray
    stimulus: np.ndarray
    activity: np.ndarray
    cell_types: list
    coordinates: list
    neurons: list
    source_indices: np.ndarray

    def describe(self):
        """Metadata only: safe for GUI status/experiment selection without pixel transmission."""
        return {key: self.descriptor[key] for key in
                ('experiment_id', 'title', 'condition', 'execution_kind', 'display_kind',
                 'status', 'axes', 'timing', 'capture', 'model', 'integration', 'limitations')}

    def read_step(self, step):
        """Local-only payload. source/frame/activity all refer to this SAME input index."""
        if not 0 <= step < len(self.input_time):
            raise IndexError('Simulation step out of range')
        source = int(self.source_indices[step])
        timestamp = self.source_timestamps[source]
        return {'experiment_id': self.descriptor['experiment_id'], 'sample': 0, 'step': step,
                'source_frame': source, 'source_time_s': float(self.source_time[source]),
                'source_received_utc': timestamp['received_utc'],
                'source_received_monotonic_ns': int(timestamp['received_monotonic_ns']),
                'input_time_s': float(self.input_time[step]),
                'activity_time_s': float(self.activity_time[step]),
                'held_frame_age_s': float(self.input_time[step]-self.source_time[source]),
                'bgr': self.frames[source], 'hex_input': self.stimulus[0, step, 0],
                'activity_central': self.activity[0, step], 'cell_types': self.cell_types,
                'playback_kind': 'verified_offline_replay', 'live_camera': False}


def load_experiment(descriptor_path):
    descriptor = json.loads(Path(descriptor_path).read_text(encoding='utf-8'))
    if descriptor.get('schema') != SCHEMA or descriptor.get('status') != 'PASS':
        raise ValueError('Unaccepted camera descriptor')
    if descriptor.get('data_root') != 'camera_pipeline' or descriptor.get('access') != 'local_reference_only':
        raise ValueError('Unexpected access contract')
    paths = {}
    for entry in descriptor['files']:
        relative = Path(entry['path'])
        path = (ROOT/relative).resolve()
        if relative.is_absolute() or not path.is_relative_to(ROOT.resolve()):
            raise ValueError('Descriptor reference escapes camera lane')
        if entry['role'] in paths:
            raise ValueError('Duplicate file role')
        if path.stat().st_size != entry['bytes'] or sha256(path) != entry['sha256']:
            raise ValueError(f"Experiment checksum mismatch: {entry['role']}")
        paths[entry['role']] = path
    required = {'source_frames', 'source_time', 'source_timestamps', 'recording_metadata',
                'stimulus', 'input_time', 'source_hex', 'coordinates', 'alignment', 'input_metadata',
                'activity', 'activity_T4_T5', 'activity_time', 'cell_types', 'neurons',
                'result_metadata', 'result_input_time', 'phase1_acceptance', 'state_validation'}
    if not required.issubset(paths):
        raise ValueError(f'Missing roles: {required-set(paths)}')
    metadata = json.loads(paths['input_metadata'].read_text(encoding='utf-8'))
    result = json.loads(paths['result_metadata'].read_text(encoding='utf-8'))
    recording = json.loads(paths['recording_metadata'].read_text(encoding='utf-8'))
    state_validation = json.loads(paths['state_validation'].read_text(encoding='utf-8'))
    acceptance = json.loads(paths['phase1_acceptance'].read_text(encoding='utf-8'))
    if result['status'] != 'PASS' or state_validation['status'] != 'PASS' or acceptance['status'] != 'PASS':
        raise ValueError('Linked verification is not PASS')
    if recording['source_kind'] != 'real_windows_camera':
        raise ValueError('Require actual camera recording')
    transform = metadata['spatial_transform']
    if (transform['policy'] != 'native' or transform['resize'] != 'none'
            or transform['actual_boxeye_internal_resize'] or transform['crop'] is not None
            or transform['mirror_horizontal'] or transform['mirror_vertical']
            or transform['rotation_degrees'] != 0 or metadata['temporal_method'] != 'zoh'
            or not metadata['causal'] or (transform['boxeye_extent'], transform['boxeye_kernel_size']) != (15, 13)):
        raise ValueError('Only the accepted standard A geometry and causal ZOH are allowed')
    for role, name, owner in [('source_frames', 'frames.npy', recording),
                              ('stimulus', 'stimulus.npy', metadata),
                              ('activity', 'activity_central.npy', result)]:
        if sha256(paths[role]) != owner['data_sha256'][name]:
            raise ValueError('Descriptor and original metadata identity differ')
    if result['input_sha256'] != sha256(paths['stimulus']):
        raise ValueError('Activity is from a different input')
    model_keys = ('model', 'checkpoint_sha256', 'source_commit', 'neurons', 'edges', 'device', 'gpu', 'torch', 'flyvis')
    if descriptor['model'] != {key: result[key] for key in model_keys}:
        raise ValueError('Descriptor model/device identity differs from result')
    for key in ('model', 'checkpoint_sha256', 'source_commit'):
        if not (result[key] == acceptance['GPU_record'][key] == state_validation['identity'][key]):
            raise ValueError('Accepted model and state-validation candidate differ')
    if (state_validation['input_sha256'] != sha256(paths['stimulus'])
            or state_validation['coordinates_sha256'] != sha256(paths['coordinates'])
            or acceptance['GPU_record']['data_sha256'] != result['data_sha256']):
        raise ValueError('Descriptor input/output/state evidence are from different experiments')
    if descriptor['execution_kind'] != 'new_inference' or descriptor['display_kind'] != 'verified_offline_replay':
        raise ValueError('This descriptor identifies saved original inference and offline display')
    def array(role):
        return np.load(paths[role], allow_pickle=False, mmap_mode='r')
    frames, source_time, source_hex = array('source_frames'), array('source_time'), array('source_hex')
    stimulus, input_time = array('stimulus'), array('input_time')
    activity, activity_time = array('activity'), array('activity_time')
    cells = array('cell_types').tolist()
    coordinates, neurons = read_csv(paths['coordinates']), read_csv(paths['neurons'])
    timestamps = read_csv(paths['source_timestamps'])
    if (stimulus.dtype != np.float32 or activity.dtype != np.float32
            or stimulus.shape != (1, len(input_time), 1, 721) or activity.shape != (1, len(input_time), 65)
            or not np.isfinite(stimulus).all() or not np.isfinite(activity).all()
            or stimulus.min() < 0 or stimulus.max() > 1 or len(cells) != 65 or len(set(cells)) != 65
            or len(coordinates) != 721 or len(neurons) != 65 or len(timestamps) != len(source_time)
            or frames.shape != tuple(recording['frames_shape']) or frames.dtype != np.uint8
            or source_hex.shape != (len(source_time), 721)):
        raise ValueError('Invalid array shapes/ranges/identities')
    if descriptor['axes'] != {'stimulus': ['sample', 'frame', 'channel', 'hex_pixel'],
                              'activity': ['sample', 'frame', 'central_cell_type'],
                              'stimulus_shape': list(stimulus.shape), 'activity_shape': list(activity.shape)}:
        raise ValueError('Descriptor axes differ from arrays')
    if ([int(c['hex_pixel']) for c in coordinates] != list(range(721))
            or [c['cell_type'] for c in neurons] != cells
            or [int(c['cell_type_axis']) for c in neurons] != list(range(65))):
        raise ValueError('Spatial/cell axis identity mismatch')
    for i, row in enumerate(timestamps):
        if int(row['frame']) != i or float(row['relative_time_s']) != source_time[i]:
            raise ValueError('Source frame timestamp mismatch')
    if not np.array_equal(input_time, array('result_input_time')):
        raise ValueError('Result and input grids differ')
    if not np.array_equal(array('activity_T4_T5'), activity[:, :, [cells.index(c) for c in TARGETS]]):
        raise ValueError('T4/T5 ordering or activity differs from central array')
    if descriptor['timing'] != {'source_clock': 'measured_host_frame_receipt', 'source_time_file_role': 'source_time',
                                'input_clock': 'first_source_frame_relative_5ms_grid', 'input_time_file_role': 'input_time',
                                'activity_clock': 'post_Euler_update_same_index_input_plus_dt',
                                'activity_time_file_role': 'activity_time', 'dt_s': .005, 'legacy_offset_s': 0}:
        raise ValueError('Unsupported or shifted clock semantics')
    indices = validate_alignment(source_time, input_time, activity_time, read_csv(paths['alignment']),
                                 source_hex, stimulus, .005)
    return CameraExperiment(descriptor, paths, frames, source_time, timestamps, input_time,
                            activity_time, stimulus, activity, cells, coordinates, neurons, indices)


def build(destination, state_directory):
    destination = new_directory(destination)
    raw = ROOT/'recordings/real_camera_20261010_r1'
    data = ROOT/'results/real_camera_native_zoh_r1'
    result_dir = ROOT/'results/real_camera_gpu_zoh_r1'
    files = {'source_frames': raw/'frames.npy', 'source_time': raw/'frame_times.npy',
             'source_timestamps': raw/'frame_timestamps.csv', 'recording_metadata': raw/'recording.json',
             'replay_video': raw/'clip.avi', 'stimulus': data/'stimulus.npy', 'input_time': data/'time.npy',
             'source_hex': data/'source_hex.npy', 'coordinates': data/'input_hex_coordinates.csv',
             'alignment': data/'time_alignment.csv', 'input_metadata': data/'metadata.json',
             'activity': result_dir/'activity_central.npy', 'activity_T4_T5': result_dir/'activity_T4_T5.npy',
             'activity_time': result_dir/'activity_time.npy', 'cell_types': result_dir/'cell_types.npy',
             'neurons': result_dir/'neurons.csv', 'result_metadata': result_dir/'result.json',
             'result_input_time': result_dir/'time.npy', 'phase1_acceptance': ROOT/'results/validation/acceptance.json',
             'previous_handoff': ROOT/'results/validation/gui_handoff.json',
             'state_validation': state_directory/'state_validation.json'}
    result = json.loads(files['result_metadata'].read_text(encoding='utf-8'))
    recording = json.loads(files['recording_metadata'].read_text(encoding='utf-8'))
    descriptor = {'schema': SCHEMA, 'created_utc': utc_now(), 'experiment_id': 'camera_real_native_zoh_r1',
                  'title': '真实摄像头普通场景 / 标准A / 原始FlyVis / 离线回放',
                  'data_root': 'camera_pipeline', 'access': 'local_reference_only', 'status': 'PASS',
                  'condition': {'kind': 'ordinary_real_scene', 'controlled_motion': False,
                                'requested_controlled_conditions_status': 'PENDING_PHYSICAL_SETUP_USER_UNAVAILABLE'},
                  'execution_kind': 'new_inference', 'display_kind': 'verified_offline_replay',
                  'axes': {'stimulus': ['sample', 'frame', 'channel', 'hex_pixel'],
                           'activity': ['sample', 'frame', 'central_cell_type'],
                           'stimulus_shape': [1, 1202, 1, 721], 'activity_shape': [1, 1202, 65]},
                  'timing': {'source_clock': 'measured_host_frame_receipt', 'source_time_file_role': 'source_time',
                             'input_clock': 'first_source_frame_relative_5ms_grid', 'input_time_file_role': 'input_time',
                             'activity_clock': 'post_Euler_update_same_index_input_plus_dt',
                             'activity_time_file_role': 'activity_time', 'dt_s': .005, 'legacy_offset_s': 0},
                  'capture': recording['capture'],
                  'model': {key: result[key] for key in ('model', 'checkpoint_sha256', 'source_commit', 'neurons',
                                                        'edges', 'device', 'gpu', 'torch', 'flyvis')},
                  'integration': {'collector_owner': 'camera_pipeline.capture.CameraSession',
                                  'gui_creates_capture': False, 'consumer': 'camera_pipeline.phase2.gui_handoff.load_experiment',
                                  'gui_source_modified_by_this_lane': False, 'gui_loaded': False,
                                  'required_gui_family': 'recorded_camera_flyvis',
                                  'legacy_reader_compatibility': 'Requires camera family loader; current official stimulus reader assumes frame*dt-1s'},
                  'limitations': ['ordinary scene is not a controlled direction-tuning experiment',
                                  'camera exposure/ISP auto-control states were not recorded in phase1; exposure reported -6 only',
                                  'source receipt times are not sensor exposure times',
                                  'no angular/physical speed calibration; no object-recognition/accurate-flow claim',
                                  'full state equivalence does not prove live end-to-end performance'],
                  'files': [{'role': role, 'path': path.relative_to(ROOT).as_posix(),
                             'sha256': sha256(path), 'bytes': path.stat().st_size}
                            for role, path in files.items()]}
    path = destination/'experiment.json'
    write_json(path, descriptor)
    experiment = load_experiment(path)
    for step in range(len(experiment.input_time)):
        payload = experiment.read_step(step)
        assert payload['source_time_s'] <= payload['input_time_s']
        assert payload['activity_time_s'] == payload['input_time_s']+.005
        assert np.array_equal(payload['hex_input'], experiment.stimulus[0, step, 0])
        assert np.array_equal(payload['activity_central'], experiment.activity[0, step])
    validation = {'schema': 'flyvis-camera-gui-handoff-validation-v2', 'status': 'PASS',
                  'descriptor_sha256': sha256(path), 'files_verified': len(files),
                  'steps_checked': len(experiment.input_time), 'source_frames': len(experiment.source_time),
                  'all_zoh_indices_and_values_checked': True, 'all_post_update_times_checked': True,
                  'all_display_payloads_same_index_as_npy': True,
                  'T4_T5_activity_order_verified': True, 'gui_source_modified': False,
                  'gui_loaded': False, 'no_raw_media_transmitted': True}
    write_json(destination/'handoff_validation.json', validation)
    print(json.dumps(validation), flush=True)
    return path


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action', required=True)
    b = sub.add_parser('build'); b.add_argument('destination', type=Path); b.add_argument('state_directory', type=Path)
    v = sub.add_parser('verify'); v.add_argument('descriptor', type=Path)
    a = p.parse_args()
    if a.action == 'build':
        build(a.destination.resolve(), a.state_directory.resolve())
    else:
        experiment = load_experiment(a.descriptor)
        print(json.dumps({'status': 'PASS', 'experiment_id': experiment.descriptor['experiment_id'],
                          'frames': len(experiment.input_time), 'last_input_s': float(experiment.input_time[-1]),
                          'last_activity_s': float(experiment.activity_time[-1]), 'gui_loaded': False}), flush=True)

"""Verify existing sample 1 bytes and publish identity without preprocessing again."""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PureWindowsPath
import platform
import sys
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
CAMERA = HERE.parent
source = CAMERA / 'controlled_video_20261010_r1'
CONDITION = '01_off_right'
PINNED = {
    'source_mp4': '0ce06450d5c59da25157780197dd64f7080969331301371027406fcb6c69d880',
    'aggregate_stimulus': '4a55fa37d3a4f1064270b258f314047f059af2880a9ed95689ed438793b654e6',
    'single_stimulus': '5b83e2514e1d4f2e3d83b480d04371592bac6ee29d8a9dd014ebc5efd4a4e023',
    'initial_state': '4e09f6eb57dbc84b68294d486fa8684764b2081f1c942ca25ec57228fbd39c0e',
    'input_time': '344dd2dab3b270742a2f334dcf691575e02d95475bee3bbe5762db5f93ea395e',
    'activity_time': '042d1367f7f7b7ff36285a85062e1a247cbef23afb0d11be47a29c5ebef882d9',
    'coordinates': 'a6b889afb932c6efd081c9e287801e6a2abc3144e767a157ebcd5828a3ded743',
}
PATHS = {
    'source_mp4': source / f'sources/{CONDITION}.mp4',
    'aggregate_stimulus': source / 'input/stimulus.npy',
    'single_stimulus': source / f'inputs/{CONDITION}/stimulus.npy',
    'initial_state': source / 'gpu_full_r1/initial_state_full.npy',
    'full_state_checkpoint': source / 'gpu_full_r1/initial_state.pt',
    'input_time': source / 'input/time.npy',
    'activity_time': source / 'gpu_full_r1/activity_time.npy',
    'source_time': source / 'input/source_time.npy',
    'source_hex': source / f'inputs/{CONDITION}/source_hex.npy',
    'coordinates': source / 'input/input_hex_coordinates.csv',
    'single_metadata': source / f'inputs/{CONDITION}/metadata.json',
    'aggregate_metadata': source / 'input/metadata.json',
    'original_alignment': source / f'inputs/{CONDITION}/time_alignment.csv',
    'decoded_frames_index': source / f'decoded_frames/{CONDITION}/frames.csv',
    'source_audit': source / 'source_validation.json',
    'historical_full_result': source / 'gpu_full_r1/result.json',
    'historical_full_central': source / 'gpu_full_r1/activity_central.npy',
    'historical_full_final_states': source / 'gpu_full_r1/final_state_full.npy',
    'historical_cell_types': source / 'gpu_full_r1/cell_types.npy',
    'historical_central_node_indices': source / 'gpu_full_r1/central_node_indices.npy',
    'historical_acceptance': source / 'acceptance.json',
    'historical_manifest': source / 'manifest.json',
}

def check(condition, message):
    if not condition:
        raise ValueError(message)

def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def reference_matches(recorded_path, expected_path):
    # The identity records Windows paths. Resolve references relative to this module
    # so the exact same files can be verified when imported under WSL /mnt/c.
    root = PureWindowsPath(r'C:\Users\hzy72\Documents\ChatGPT\fly\camera_pipeline')
    try:
        relative = PureWindowsPath(recorded_path).relative_to(root).as_posix()
        return relative == expected_path.resolve().relative_to(CAMERA.resolve()).as_posix()
    except ValueError:
        return False

def rows(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

def payload_sha(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes(order='C')).hexdigest()

def tensor_identity(array):
    # Same formula as the accepted OriginalModel.tensor_sha; shape is part of identity.
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode('utf-8'))
    digest.update(str(array.shape).encode('utf-8'))
    digest.update(np.ascontiguousarray(array).tobytes(order='C'))
    return {'dtype': str(array.dtype), 'shape': list(array.shape),
            'c_order_payload_sha256': payload_sha(array), 'tensor_sha256': digest.hexdigest()}

def array(path):
    return np.load(path, allow_pickle=False, mmap_mode='r')

def verify_historical_seal():
    manifest = read_json(source / 'manifest.json')
    for entry in manifest['files']:
        path = (source / entry['path']).resolve()
        check(path.is_relative_to(source.resolve()), 'Historical manifest escapes its directory')
        check(path.stat().st_size == entry['bytes'] and sha(path) == entry['sha256'], f'Historical file changed: {path}')
    return len(manifest['files'])

def verify_frozen():
    for key, expected in PINNED.items():
        check(sha(PATHS[key]) == expected, f'Pinned identity mismatch: {key}')
    stimulus = array(PATHS['single_stimulus'])
    aggregate = array(PATHS['aggregate_stimulus'])
    initial = array(PATHS['initial_state'])
    grid = array(PATHS['input_time'])
    output_time = array(PATHS['activity_time'])
    source_time = array(PATHS['source_time'])
    receptors = array(PATHS['source_hex'])
    check(stimulus.dtype == np.dtype('<f4') and stimulus.shape == (1, 800, 1, 721), 'Single stimulus protocol changed')
    check(aggregate.dtype == stimulus.dtype and aggregate.shape == (6, 800, 1, 721), 'Aggregate protocol changed')
    check(stimulus.tobytes() == aggregate[1:2].tobytes(), 'Single file differs from aggregate sample=1 bytes')
    check(np.isfinite(stimulus).all() and stimulus.min() >= 0 and stimulus.max() <= 1, 'Invalid stimulus values')
    check(initial.shape == (1, 45669) and initial.dtype == stimulus.dtype and np.isfinite(initial).all(), 'Invalid full initial state')
    check(np.array_equal(grid, np.arange(800) * .005), 'Input time is not the frozen 5ms grid')
    check(np.array_equal(output_time, grid + .005) and output_time[-1] == 4., 'Post-update clock mismatch')
    check(np.array_equal(source_time, np.arange(240) / 60), 'Source presentation clock mismatch')
    check(receptors.shape == (240, 721) and receptors.dtype == stimulus.dtype, 'Source receptor protocol changed')
    index = np.searchsorted(source_time, grid, side='right') - 1
    check(index.min() == 0 and index.max() == 239, 'Invalid source frame selection')
    check(np.all(source_time[index] <= grid) and grid[-1] < 4, 'Noncausal or out-of-duration input')
    check(stimulus[0, :, 0].tobytes() == receptors[index].tobytes(), 'ZOH actual values mismatch')
    alignment = rows(PATHS['original_alignment'])
    check(len(alignment) == 800, 'Missing original alignment steps')
    for k, entry in enumerate(alignment):
        check(int(entry['model_frame']) == k and float(entry['model_time_s']) == grid[k], 'Original step alignment mismatch')
        check(int(entry['source_left_frame']) == int(index[k]) == int(entry['source_right_frame']), 'Original source alignment mismatch')
        check(float(entry['source_left_time_s']) == source_time[index[k]] == float(entry['source_right_time_s']), 'Original source times mismatch')
        check(float(entry['right_weight']) == 0 and entry['uses_future_frame'] == 'False', 'Original non-ZOH record')
    meta = read_json(PATHS['aggregate_metadata'])
    check(meta['samples'][1]['condition_id'] == CONDITION and meta['samples'][1]['direction'] == 'right', 'Wrong sample identity')
    spatial = meta['spatial_transform']
    check((spatial['boxeye_extent'], spatial['boxeye_kernel_size'], spatial['boxeye_filter']) == (15, 13, 'mean'), 'Wrong BoxEye configuration')
    check(spatial['policy'] == 'native' and spatial['resize'] == 'none' and spatial['crop'] is None, 'Unexpected geometry')
    check(not spatial['mirror_horizontal'] and not spatial['mirror_vertical'] and spatial['rotation_degrees'] == 0 and not spatial['actual_boxeye_internal_resize'], 'Unexpected orientation/resize')
    record = read_json(PATHS['historical_full_result'])
    check(record['input_sha256'] == PINNED['aggregate_stimulus'] and record['initial_state_value_sha256'] == tensor_identity(initial)['tensor_sha256'], 'Historical Full input/initial identity mismatch')
    check(record['dt_s'] == .005 and record['same_initial_state_for_all_conditions'] and record['weights_exact_before_and_after'], 'Historical Full metadata mismatch')
    return stimulus, initial, grid, output_time, source_time, receptors, index, spatial, record

def verify_visual_direction(source_time, receptors):
    coordinates = rows(PATHS['coordinates'])
    check(len(coordinates) == 721 and [int(c['hex_pixel']) for c in coordinates] == list(range(721)), 'Coordinate order mismatch')
    for c in coordinates:
        u, v = int(c['u']), int(c['v'])
        check(int(c['render_row']) == int(13*(u+v/2))+320 and int(c['render_column']) == 13*v+320, 'BoxEye coordinate formula mismatch')
    crossed = receptors < .5
    check(not crossed[0].any() and crossed[-1].all(), 'Input is not white-to-black for every receptor')
    crossing = source_time[np.argmax(crossed, axis=0)]
    correlation = float(np.corrcoef([float(c['source_center_x']) for c in coordinates], crossing)[0, 1])
    check(correlation > .999, 'Mapped input does not move right')
    frames = rows(PATHS['decoded_frames_index'])
    check(len(frames) == 240, 'Missing decoded source frames')
    visible_time, visible_x = [], []
    for k, frame in enumerate(frames):
        path = (source / frame['path']).resolve()
        check(path.is_relative_to((source / f'decoded_frames/{CONDITION}').resolve()), 'Source PNG path escapes condition')
        check(int(frame['frame']) == k and float(frame['time_s']) == source_time[k] and sha(path) == frame['sha256'], 'Decoded PNG identity/time changed')
        with Image.open(path) as image:
            check(image.size == (640, 640), 'PNG resolution mismatch')
            gray = np.asarray(image.convert('L'), dtype=np.float64)/255
        column = gray.mean(axis=0)
        difference = np.abs(np.diff(column))
        if 1 <= source_time[k] < 3 and difference.max() > 100/255:
            visible_time.append(source_time[k]); visible_x.append(int(difference.argmax()) + .5)
    check(len(visible_time) >= 100, 'Insufficient visible edge frames')
    slope = float(np.polyfit(visible_time, visible_x, 1)[0])
    position_correlation = float(np.corrcoef(visible_time, visible_x)[0, 1])
    check(slope > 0 and position_correlation > .999, 'Source PNG motion is not rightward')
    return {'status': 'PASS', 'source_PNG_frames_sha_checked': 240, 'visible_edge_frames': len(visible_time),
            'source_edge_velocity_px_s': slope, 'source_position_time_correlation': position_correlation,
            'hex_crossing_time_source_x_correlation': correlation, 'crossed_receptors': 721,
            'physical_speed_calibrated': False}

def write_json(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')

def build():
    target = HERE / 'INPUT_SINGLE_VIDEO_IDENTITY.json'
    check(not target.exists(), 'Refusing to overwrite identity; use --verify')
    old_files = verify_historical_seal()
    stimulus, initial, grid, output_time, source_time, receptors, index, spatial, record = verify_frozen()
    visual = verify_visual_direction(source_time, receptors)
    alignment_path = HERE / 'source_model_activity_alignment.csv'
    with alignment_path.open('x', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['step_id', 'condition_id', 'aggregate_sample', 'source_frame_id', 'source_presentation_time_s', 'input_time_s', 'activity_time_s', 'source_received_utc', 'source_received_monotonic_ns', 'uses_future_frame'])
        writer.writeheader()
        for k in range(800):
            writer.writerow({'step_id': k, 'condition_id': CONDITION, 'aggregate_sample': 1, 'source_frame_id': int(index[k]),
                             'source_presentation_time_s': float(source_time[index[k]]), 'input_time_s': float(grid[k]),
                             'activity_time_s': float(output_time[k]), 'source_received_utc': '',
                             'source_received_monotonic_ns': '', 'uses_future_frame': False})
    identity = {
        'schema': 'flyvis-phase3-fixed-input-identity-v1', 'status': 'PASS', 'created_utc': datetime.now(timezone.utc).isoformat(),
        'artifact_id': 'INPUT_SINGLE_VIDEO_IDENTITY_20261010_r1', 'condition_id': CONDITION, 'aggregate_sample': 1,
        'source_kind': 'synthetic_controlled_video', 'source_is_camera': False,
        'execution_evidence_level': 'new read-only identity and visual-direction verification of frozen historical input',
        'new_preprocessing': False, 'new_GPU_inference': False, 'new_camera_capture': False, 'RTL_simulation': False, 'live_PL_execution': False,
        'comparison_id': None, 'comparison_id_owner': 'A/B after GPU-native parameter and a0 identity confirmation',
        'target_from_task_assignment': {'H': 'T5c 67-node set', 'boundary_mode': 'SOURCE_RAW', 'verified_by_input_lane': False},
        'input': {'canonical_npy_shape': [1, 800, 1, 721], 'producer_selection': 'aggregate[1:2]',
                  'x_view': 'single_stimulus[0,:,0,:]', 'x_shape': [800, 721],
                  'canonical_tensor': tensor_identity(stimulus), 'x_tensor': tensor_identity(stimulus[0, :, 0]),
                  'same_C_order_payload_across_views': True, 'range': [float(stimulus.min()), float(stimulus.max())]},
        'initial_state': {'file_shape': [1, 45669], 'full_state_view': 'initial_state_full[0,:]',
                          'file_tensor': tensor_identity(initial), 'flat_tensor': tensor_identity(initial[0]),
                          'same_C_order_payload_across_views': True, 'new_warmup_permitted': False,
                          'quantization': 'none; a quantized common a0 requires a new comparison_id and all-mode reruns'},
        'hash_semantics': {'file_sha256': 'entire file including NPY header', 'c_order_payload_sha256': 'SHA256 of C-order numeric bytes only',
                           'tensor_sha256': 'SHA256(UTF8(str(numpy.dtype)) || UTF8(str(numpy.shape)) || C-order bytes), accepted OriginalModel.tensor_sha algorithm'},
        'time': {'source_fps': 60., 'source_frames': 240, 'simulation_steps': 800, 'dt_s': .005, 'simulation_fps': 200.,
                 'input_domain': '[0,4)', 'input_first_s': 0., 'input_last_s': float(grid[-1]),
                 'activity_first_s': float(output_time[0]), 'activity_last_s': float(output_time[-1]),
                 'activity_semantics': 'state a[k+1] after x[k] update, at input_time[k]+dt',
                 'method': 'causal ZOH; searchsorted(source_time,input_time,side=right)-1',
                 'endpoint_policy': 'known CFR frame239 held from239/60 until4s exclusive',
                 'receipt_UTC': None, 'receipt_monotonic_ns': None, 'actual_computation_throughput': 'not measured in this input verification'},
        'spatial_transform': spatial, 'model_from_historical_full': record['model_identity'],
        'GPU_native_expanded_parameter_profile_sha256': None, 'node_map_identity': 'A/B must confirm input hex order -> original R1 indices and full global order',
        'historical_full_scope': 'actual earlier Full GPU result; 65 central nodes at all800 steps and complete final state, not a complete per-step45669-node trajectory',
        'strict_Full_vs_Replacement_approved': False,
        'files': {key: {'path': str(path.resolve()), 'sha256': sha(path), 'bytes': path.stat().st_size} for key, path in PATHS.items()},
        'alignment': {'path': str(alignment_path.resolve()), 'sha256': sha(alignment_path), 'bytes': alignment_path.stat().st_size},
        'checks': {'historical_sealed_files_unchanged': old_files, 'single_slice_payload_bitwise_equal': True,
                   'all_800_ZOH_values_and_indices_exact': True, 'actual_direction': visual},
        'handoff_requirements': {
            'A': ['confirm GPU-native expanded parameters/profile hash, node_map and R1 input assignment', 'confirm checkpoint/source identity and exact animation a0; provide A_SINGLE_VIDEO_HANDOFF', 'provide matched full-state trajectory or regenerate Full under new comparison_id if required'],
            'B': ['independently hash x[800,721] actual slice bytes and declare hash semantics', 'use this animation a0 rather than G2 MovingEdge a0', 'after A/B identity agreement create comparison_id and run800 SOURCE_RAW H/R steps with state-chain/threshold evidence'],
            'C': ['continue independent numeric/RTL feasibility; input identity is ready and does not block C', 'consume B animation-specific old_H/x_H/source_raw/new_H vectors rather than using video pixels directly'],
            'GUI': ['use source/frame/input/post-update clocks without a one-frame offset', 'show Python or FPGA only after matching computation/board evidence is delivered by its owner']}
    }
    write_json(target, identity)
    write_json(HERE / 'verification.json', {'status': 'PASS', 'identity_file_sha256': sha(target), 'checks': identity['checks'],
        'environment': {'python': sys.version, 'numpy': np.__version__, 'platform': platform.platform()},
        'scope': 'input identity; no new neural calculation or hardware execution'})
    print(json.dumps({'status': 'PASS', 'identity': str(target), 'x_payload_sha256': identity['input']['x_tensor']['c_order_payload_sha256'],
                      'a0_payload_sha256': identity['initial_state']['flat_tensor']['c_order_payload_sha256'], 'checks': identity['checks']}, ensure_ascii=False))

def load_bundle(identity_path=HERE / 'INPUT_SINGLE_VIDEO_IDENTITY.json', expected_identity_sha256=None):
    """Return verified read-only x[800,721], a0[45669], input and post-update clocks."""
    identity_path = Path(identity_path)
    if expected_identity_sha256 is not None:
        check(sha(identity_path) == expected_identity_sha256, 'Identity JSON hash mismatch')
    identity = read_json(identity_path)
    check(identity['schema'] == 'flyvis-phase3-fixed-input-identity-v1' and identity['condition_id'] == CONDITION and identity['aggregate_sample'] == 1, 'Wrong experiment identity')
    check(identity['source_kind'] == 'synthetic_controlled_video' and identity['source_is_camera'] is False, 'Wrong input provenance')
    check(identity['time']['dt_s'] == .005 and identity['time']['simulation_steps'] == 800 and identity['time']['source_fps'] == 60., 'Wrong time contract')
    check(identity['input']['canonical_npy_shape'] == [1, 800, 1, 721] and identity['input']['x_shape'] == [800, 721], 'Wrong input axes')
    for key, ref in identity['files'].items():
        check(key in PATHS and reference_matches(ref['path'], PATHS[key]), f'Unexpected artifact path: {key}')
        check(PATHS[key].stat().st_size == ref['bytes'] and sha(PATHS[key]) == ref['sha256'], f'Artifact changed: {key}')
    check(set(identity['files']) == set(PATHS), 'Missing required identity references')
    stimulus, initial, grid, output_time, source_time, receptors, index, spatial, record = verify_frozen()
    check(identity['input']['canonical_tensor'] == tensor_identity(stimulus) and identity['initial_state']['file_tensor'] == tensor_identity(initial), 'Canonical tensor identity mismatch')
    check(identity['input']['x_tensor'] == tensor_identity(stimulus[0, :, 0]) and identity['initial_state']['flat_tensor'] == tensor_identity(initial[0]), 'Actual input/a0 tensor fingerprint mismatch')
    ref = identity['alignment']; path = HERE / 'source_model_activity_alignment.csv'
    check(reference_matches(ref['path'], path) and path.stat().st_size == ref['bytes'] and sha(path) == ref['sha256'], 'Alignment identity changed')
    alignment = rows(path); check(len(alignment) == 800, 'Wrong alignment length')
    for k, entry in enumerate(alignment):
        check(int(entry['step_id']) == k and int(entry['aggregate_sample']) == 1 and entry['condition_id'] == CONDITION and int(entry['source_frame_id']) == int(index[k]), 'New source alignment mismatch')
        check(float(entry['source_presentation_time_s']) == source_time[index[k]] and float(entry['input_time_s']) == grid[k] and float(entry['activity_time_s']) == output_time[k], 'New clock alignment mismatch')
        check(entry['source_received_utc'] == entry['source_received_monotonic_ns'] == '' and entry['uses_future_frame'] == 'False', 'Fabricated receipt or future frame')
    return {'x': stimulus[0, :, 0], 'a0': initial[0], 'input_time': grid, 'activity_time': output_time, 'identity': identity}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--build', action='store_true'); group.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.build:
        build()
    else:
        bundle = load_bundle()
        print(json.dumps({'status': 'PASS', 'x_shape': list(bundle['x'].shape), 'a0_shape': list(bundle['a0'].shape),
                          'simulation_steps': 800, 'source_is_camera': False, 'new_GPU_inference': False}))

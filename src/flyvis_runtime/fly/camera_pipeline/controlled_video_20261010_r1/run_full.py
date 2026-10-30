"""Original Full GPU network, six independent conditions from one frozen full initial state."""
from __future__ import annotations
import argparse
import gc
import json
from pathlib import Path
import shutil
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
from camera_pipeline.adapter import load_stimulus
from camera_pipeline.common import new_directory, sha256, utc_now, write_json
from camera_pipeline.phase2.model_runtime import OriginalModel
from camera_pipeline.phase2.network_state import load_state, save_state, simulate_block

TASK = Path(__file__).resolve().parent


def run(destination, initial_path=None):
    destination = new_directory(destination)
    status = destination/'job_status.json'
    write_json(status, {'state': 'running', 'job_id': destination.name, 'stage': 'model_load'})
    runtime = OriginalModel()
    torch = runtime.torch
    stimulus, grid, coordinates, metadata = load_stimulus(TASK/'input')
    assert stimulus.shape == (6, 800, 1, 721) and metadata['source_kind'] == 'synthetic_controlled_video'
    assert metadata['spatial_transform']['policy'] == 'native' and metadata['temporal_method'] == 'zoh'
    assert np.array_equal(grid, np.arange(800)*.005)
    runtime.validate_coordinates(coordinates)
    identity = {'input_sha256': sha256(TASK/'input/stimulus.npy'),
                'coordinates_sha256': sha256(TASK/'input/input_hex_coordinates.csv')}
    movie, transfer_s = runtime.timed(lambda: torch.tensor(np.array(stimulus), dtype=torch.float32, device='cuda'))
    if initial_path is None:
        from flyvis.utils.nn_utils import simulation
        with simulation(runtime.network):
            initial, initial_s = runtime.timed(lambda: runtime.network.steady_state(1., .005, 1, value=.5))
        save_state(destination/'initial_state.pt', initial, runtime, next_step=0, **identity)
        initializer = {'kind': 'one 1s grey 0.5 full-network steady_state once', 'warmup_count': 1,
                       'elapsed_s': initial_s, 'checkpoint': str(destination/'initial_state.pt')}
    else:
        initial, initial_s = runtime.timed(lambda: load_state(initial_path, runtime, next_step=0, **identity))
        shutil.copyfile(initial_path, destination/'initial_state.pt')
        initializer = {'kind': 'restore exact frozen full initial state', 'warmup_count': 0,
                       'elapsed_s': initial_s, 'checkpoint': str(initial_path)}
    frozen_initial = initial.nodes.activity.detach().clone()
    np.save(destination/'initial_state_full.npy', frozen_initial.cpu().numpy(), allow_pickle=False)
    initial_value_sha = runtime.tensor_sha(frozen_initial)
    central = runtime.network.connectome.central_cells_index[:]
    cell_types = runtime.network.connectome.unique_cell_types[:].astype(str)
    central_values, final_values, timings = [], [], []
    for sample in range(6):
        write_json(status, {'state': 'running', 'job_id': destination.name, 'stage': 'inference', 'sample': sample})
        # Original dynamics allocates each next state; it does not mutate the initial namespace.
        assert torch.equal(initial.nodes.activity, frozen_initial)
        torch.cuda.reset_peak_memory_stats()
        pair, elapsed_s = runtime.timed(lambda: simulate_block(runtime, movie[sample:sample+1], initial))
        activity, final = pair
        central_value, download_s = runtime.timed(lambda: activity[:, :, central].cpu().numpy())
        assert torch.isfinite(activity).all() and torch.equal(initial.nodes.activity, frozen_initial)
        central_values.append(central_value)
        final_values.append(final.nodes.activity.cpu().numpy())
        save_state(destination/f'final_state_condition_{sample:02d}.pt', final, runtime, next_step=800, **identity)
        timings.append({'sample': sample, 'condition_id': metadata['samples'][sample]['condition_id'],
                        'inference_s': elapsed_s, 'steps': 800, 'compute_steps_per_s': 800/elapsed_s,
                        'central_device_to_host_s': download_s, 'same_initial_state_value_sha256': initial_value_sha,
                        'warmup_in_condition': 0, 'peak_allocated_MiB': torch.cuda.max_memory_allocated()/2**20,
                        'peak_reserved_MiB': torch.cuda.max_memory_reserved()/2**20})
        del activity, final; gc.collect()
        print(json.dumps({'sample': sample, 'condition': timings[-1]['condition_id'], 'inference_s': elapsed_s}), flush=True)
    runtime.assert_unchanged()
    central_values = np.concatenate(central_values, axis=0)
    final_values = np.concatenate(final_values, axis=0)
    targets = [f'T{n}{suffix}' for n in (4, 5) for suffix in 'abcd']
    target_values = central_values[:, :, [list(cell_types).index(c) for c in targets]]
    for name, value in [('activity_central', central_values), ('activity_T4_T5', target_values),
                        ('final_state_full', final_values), ('cell_types', cell_types),
                        ('central_node_indices', central), ('time', grid), ('activity_time', grid+.005)]:
        np.save(destination/f'{name}.npy', value, allow_pickle=False)
    from camera_pipeline.controlled_video_20261010_r1.prepare import write_csv
    neurons = [{'cell_type_axis': i, 'cell_type': cell, 'original_node_index': int(index), 'u': 0, 'v': 0}
               for i, (cell, index) in enumerate(zip(cell_types, central))]
    write_csv(destination/'neurons.csv', neurons)
    write_csv(destination/'activity_T4_T5.csv', [{'sample': sample, 'input_time_s': float(t),
               'activity_after_update_time_s': float(t+.005), **dict(zip(targets, target_values[sample, frame].tolist()))}
              for sample in range(6) for frame, t in enumerate(grid)])
    record = {'schema': 'flyvis-controlled-video-full-result-v1', 'status': 'PASS', 'created_utc': utc_now(),
              'job_id': destination.name, 'execution_kind': 'new_inference', 'processing_mode': 'offline',
              'model_identity': runtime.identity, 'environment': runtime.environment, **identity,
              'source_kind': 'synthetic_controlled_video', 'source_is_camera': False, 'source_video_fps': 60.,
              'dt_s': .005, 'simulation_fps': 200., 'initializer': initializer,
              'same_initial_state_for_all_conditions': True, 'initial_state_value_sha256': initial_value_sha,
              'initial_state_shape': [1, 45669], 'network_mode': 'six independent 4s conditions, common initial state',
              'condition_timings': timings, 'host_to_device_s': transfer_s,
              'total_inference_s': sum(t['inference_s'] for t in timings),
              'activity_shape': list(central_values.shape), 'activity_axes': ['sample', 'frame', 'central_cell_type'],
              'activity_spatial_scope': 'one actual central node per type, 65 types', 'target_types': targets,
              'time_semantics': 'time.npy=input presentation; activity_time.npy=input+dt, post-Euler same frame index',
              'weights_exact_before_and_after': True, 'decoder_executed': False, 'real_time_claim': False,
              'combined_24s_continuous_network_inference': False,
              'limitations': ['pixel-space file conditions, not official angular-space MovingEdge equivalence',
                              'not physical camera capture', 'no official 12-direction DSI or calibrated speed/flow claim'],
              'data_sha256': {p.name: sha256(p) for p in destination.iterdir() if p.suffix in ('.npy', '.csv', '.pt')}}
    write_json(destination/'result.json', record)
    write_json(status, {'state': 'complete', 'job_id': destination.name, 'result': 'result.json'})
    return record


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('destination', type=Path); p.add_argument('--initial', type=Path)
    a = p.parse_args()
    try:
        run(a.destination.resolve(), a.initial.resolve() if a.initial else None)
    except BaseException as error:
        if a.destination.exists():
            write_json(a.destination/'job_status.json', {'state': 'failed', 'job_id': a.destination.name, 'error': str(error)})
        raise

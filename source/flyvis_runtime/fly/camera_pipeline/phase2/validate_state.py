"""Full-node monolithic vs disk-resumed chunks, including a fresh WSL process."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
from camera_pipeline.common import ROOT, new_directory, sha256, utc_now, write_json
from camera_pipeline.phase2.model_runtime import OriginalModel
from camera_pipeline.phase2.network_state import audit_state, load_state, save_state, simulate_block


def rows_comparison(actual, expected, start):
    difference = np.abs(actual.astype(np.float64)-expected.astype(np.float64))
    return [{'step': start+i, 'input_time_s': (start+i)*.005,
             'activity_after_update_time_s': (start+i+1)*.005,
             'max_abs_all_45669_nodes': float(d.max()),
             'rmse_all_45669_nodes': float(np.sqrt(np.mean(d*d))),
             'bitwise_equal': bool(np.array_equal(actual[0, i], expected[0, i]))}
            for i, d in enumerate(difference[0])]


def run(dataset, destination, *, resume=False):
    from camera_pipeline.adapter import load_stimulus
    if not resume:
        destination = new_directory(destination)
        write_json(destination/'job_status.json', {'job_id': destination.name, 'state': 'running',
                                                    'kind': 'continuous_state_validation'})
    runtime = OriginalModel()
    torch = runtime.torch
    stimulus, grid, coordinates, metadata = load_stimulus(dataset)
    assert stimulus.shape[0] == 1 and metadata['temporal_method'] == 'zoh'
    assert metadata['spatial_transform']['policy'] == 'native' and metadata['dt_s'] == .005
    runtime.validate_coordinates(coordinates)
    identity = {'input_sha256': sha256(dataset/'stimulus.npy'),
                'coordinates_sha256': sha256(dataset/'input_hex_coordinates.csv')}
    movie = torch.tensor(np.array(stimulus), dtype=torch.float32, device='cuda')
    n = len(grid)
    if resume:
        # Cold model load. No steady_state/warmup in this process.
        start = 1
        initial = load_state(destination/'state_after_000001.pt', runtime, next_step=start, **identity)
        expected = np.load(destination/'activity_all_nodes_monolithic.npy', mmap_mode='r')
        comparisons = []
        elapsed = 0.
        for left in range(start, n, 127):
            right = min(left+127, n)
            pair, timing = runtime.timed(lambda: simulate_block(runtime, movie[:, left:right], initial))
            activity, initial = pair
            elapsed += timing
            comparisons.extend(rows_comparison(activity.cpu().numpy(), expected[:, left:right], left))
            del activity
        runtime.assert_unchanged()
        save_state(destination/'state_final_fresh_process.pt', initial, runtime, next_step=n, **identity)
        result = {'status': 'PASS' if all(r['bitwise_equal'] for r in comparisons) else 'FAIL',
                  'pid': __import__('os').getpid(), 'warmup_in_this_process': 0,
                  'resumed_from_next_step': start, 'steps_compared': len(comparisons),
                  'max_abs_error': max(r['max_abs_all_45669_nodes'] for r in comparisons),
                  'elapsed_simulation_s': elapsed, 'environment': runtime.environment,
                  'weights_exact_after': True}
        write_json(destination/'fresh_process_result.json', result)
        with (destination/'fresh_process_step_comparison.csv').open('w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=list(comparisons[0]))
            writer.writeheader(); writer.writerows(comparisons)
        assert result['status'] == 'PASS', result
        return result

    from flyvis.utils.nn_utils import simulation
    with simulation(runtime.network):
        initial, warmup_s = runtime.timed(lambda: runtime.network.steady_state(1., .005, 1, value=.5))
    audit_state(initial, runtime)
    save_state(destination/'state_initial.pt', initial, runtime, next_step=0, **identity)
    pair, monolithic_s = runtime.timed(lambda: simulate_block(runtime, movie, initial))
    all_activity, final = pair
    all_cpu = all_activity.cpu().numpy()
    np.save(destination/'activity_all_nodes_monolithic.npy', all_cpu, allow_pickle=False)
    save_state(destination/'state_final_monolithic.pt', final, runtime, next_step=n, **identity)
    del all_activity, final
    central = runtime.network.connectome.central_cells_index[:]
    accepted = np.load(ROOT/'results/real_camera_gpu_zoh_r1/activity_central.npy', allow_pickle=False)
    baseline_identical = np.array_equal(all_cpu[:, :, central], accepted)
    assert baseline_identical, 'Monolithic run differs from accepted first-stage GPU activity'
    # Awkward boundaries include a single step and a camera-hold boundary; no time reset.
    cuts = sorted(set([0, 1, 37, 128, 329, 512, 777, 1024, n]))
    cuts = [c for c in cuts if c <= n]
    state = load_state(destination/'state_initial.pt', runtime, next_step=0, **identity)
    comparisons, blocks = [], []
    for left, right in zip(cuts[:-1], cuts[1:]):
        pair, elapsed = runtime.timed(lambda: simulate_block(runtime, movie[:, left:right], state))
        activity, state = pair
        comparisons.extend(rows_comparison(activity.cpu().numpy(), all_cpu[:, left:right], left))
        checkpoint = destination/f'state_after_{right:06d}.pt'
        save_state(checkpoint, state, runtime, next_step=right, **identity)
        state, restore_s = runtime.timed(lambda: load_state(checkpoint, runtime, next_step=right, **identity))
        blocks.append({'first_step': left, 'stop_step_exclusive': right, 'steps': right-left,
                       'simulation_s': elapsed, 'restore_s': restore_s,
                       'checkpoint': checkpoint.name, 'checkpoint_sha256': sha256(checkpoint),
                       'warmup_in_block': 0})
        del activity
    assert all(row['bitwise_equal'] for row in comparisons), 'Chunk trajectory differs'
    final_equal = np.array_equal(state.nodes.activity.cpu().numpy(), all_cpu[:, -1])
    assert final_equal
    runtime.assert_unchanged()
    with (destination/'step_comparison.csv').open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(comparisons[0]))
        writer.writeheader(); writer.writerows(comparisons)
    np.save(destination/'activity_central.npy', all_cpu[:, :, central], allow_pickle=False)
    np.save(destination/'cell_types.npy', runtime.network.connectome.unique_cell_types[:].astype(str), allow_pickle=False)
    np.save(destination/'time.npy', grid, allow_pickle=False)
    np.save(destination/'activity_time.npy', grid+.005, allow_pickle=False)
    del initial, state, movie, all_cpu
    runtime.torch.cuda.empty_cache()
    child = subprocess.run([sys.executable, str(Path(__file__).resolve()), str(dataset), str(destination), '--resume'],
                           capture_output=True, text=True, timeout=120)
    (destination/'fresh_process.log').write_text(child.stdout+'\n'+child.stderr)
    assert child.returncode == 0, child.stderr[-4000:]
    fresh = json.loads((destination/'fresh_process_result.json').read_text(encoding='utf-8'))
    result = {'schema': 'flyvis-camera-continuous-state-validation-v1', 'created_utc': utc_now(),
              'status': 'PASS', 'identity': runtime.identity, 'environment': runtime.environment,
              **identity, 'input_directory': str(dataset), 'dt_s': .005, 'steps': n,
              'all_node_trajectory_shape': [1, n, 45669], 'independent_state_fields': {'nodes': ['activity'], 'edges': []},
              'derived_state': 'sources/targets RefTensor gathers reconstructed and checked for all 1513231 edges',
              'warmup_count': 1, 'warmup_s': warmup_s, 'warmup_per_chunk': 0,
              'monolithic_simulation_s': monolithic_s, 'blocks': blocks,
              'per_step_max_abs_error': max(r['max_abs_all_45669_nodes'] for r in comparisons),
              'all_steps_bitwise_equal': True, 'final_state_bitwise_equal': final_equal,
              'accepted_phase1_central_bitwise_equal': baseline_identical, 'fresh_process_resume': fresh,
              'weights_exact_before_and_after': True, 'real_time_claim': False,
              'scope': 'current pinned original PPNeuronIGRSynapses, full 45669-node batch=1 state; not a universal dynamics serializer',
              'timing_scope': 'GPU-synchronized simulation with read-only finite-state audit hooks; disk save/load and comparisons are separate overhead',
              'data_sha256': {p.name: sha256(p) for p in destination.iterdir()
                              if p.suffix in ('.pt', '.npy', '.csv', '.log')}}
    write_json(destination/'state_validation.json', result)
    write_json(destination/'job_status.json', {'job_id': destination.name, 'state': 'complete', 'result': 'state_validation.json'})
    print(json.dumps({'status': 'PASS', 'steps': n, 'nodes': 45669,
                      'per_step_max_abs_error': result['per_step_max_abs_error'], 'fresh_process': fresh['status']}), flush=True)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('dataset', type=Path); p.add_argument('destination', type=Path)
    p.add_argument('--resume', action='store_true'); a = p.parse_args()
    try:
        run(a.dataset.resolve(), a.destination.resolve(), resume=a.resume)
    except BaseException as error:
        if a.destination.exists() and not a.resume:
            write_json(a.destination/'job_status.json', {'job_id': a.destination.name, 'state': 'failed', 'error': str(error)})
        raise

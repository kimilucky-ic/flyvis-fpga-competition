"""Full CPU oracle or live GPU-R / independent NumPy-H replacement.

Runs are separate; replacements consume only their own live committed full state.
Full arrays are read ONLY after a step to compute errors, never by Coordinator.
"""
from pathlib import Path
from contextlib import contextmanager
import argparse
import csv
import hashlib
import json
import os
import platform
import sys
import time
import uuid
import numpy as np
from h_step import HUpdater, StepError, array_hash, file_hash, frozen
from coordinator import Coordinator

HERE = Path(__file__).resolve().parent
FLY = HERE.parents[2] / 'fly'
DEFAULT_BUNDLE = FLY / 'gpu_phase2/artifacts/reference_bundle_v1'
STATIC = HERE.parent / 'round1_20261010/artifacts/B_T5c/static_boundary.npz'


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def manifest_verify(bundle):
    entries = json.loads((bundle / 'artifact_manifest.json').read_text(encoding='utf-8'))['files']
    for entry in entries:
        path = bundle / entry['path']
        if not path.exists() or path.stat().st_size != entry['bytes'] or file_hash(path) != entry['sha256']:
            raise StepError('MODEL_MISMATCH', 'bundle artifact failed: ' + entry['path'])
    return entries


def validate_parameters(updater, parameter_path):
    with np.load(parameter_path, allow_pickle=False) as p, np.load(STATIC, allow_pickle=False) as h:
        assert np.array_equal(updater.bias, p['bias'][updater.h_ids])
        assert np.array_equal(h['time_const_s'], p['time_const'][updater.h_ids])
        for route in ['internal', 'incoming', 'outgoing']:
            ids = h[route + '_edge_id']
            assert np.array_equal(h[route + '_weight'], p['effective_weight'][ids])
            assert np.array_equal(h[route + '_source_index'], p['source_global'][ids])
            assert np.array_equal(h[route + '_target_index'], p['target_global'][ids])
        return p['input_node_index'].copy()


@contextmanager
def native_full_forbidden():
    from flyvis.network.network import Network
    from flyvis.network.dynamics import PPNeuronIGRSynapses
    saved = [(Network, '_next_state', Network._next_state), (Network, 'forward', Network.forward),
        (PPNeuronIGRSynapses, 'write_state_velocity', PPNeuronIGRSynapses.write_state_velocity)]
    audit = {'forbidden_native_call_count': 0, 'guard_entry_points': [name for _, name, _ in saved]}
    def forbidden(*args, **kwargs):
        audit['forbidden_native_call_count'] += 1
        raise StepError('NATIVE_FULL_UPDATE_FORBIDDEN', 'native Full/H update disabled during replacement')
    for cls, name, _ in saved:
        setattr(cls, name, forbidden)
    try:
        yield audit
    finally:
        for cls, name, method in saved:
            setattr(cls, name, method)


def errors(actual, expected, ids):
    delta = actual[ids].astype(np.float64) - expected[ids].astype(np.float64)
    absolute = np.abs(delta)
    tolerance = 1e-5 + 1e-5 * np.abs(expected[ids].astype(np.float64))
    return dict(max_abs=float(absolute.max()), mae=float(absolute.mean()), rmse=float(np.sqrt((delta * delta).mean())),
        violations=int((absolute > tolerance).sum()), worst_global_node=int(ids[absolute.argmax()]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bundle', type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument('--run', required=True)
    parser.add_argument('--mode', choices=['Full', 'SOURCE_RAW', 'CURRENT_AGG'], required=True)
    parser.add_argument('--device', choices=['cpu', 'cuda'], required=True)
    parser.add_argument('--reference', type=Path)
    args = parser.parse_args()
    out = HERE / 'artifacts' / args.run
    if out.exists():
        raise SystemExit('Run exists; preserve it and choose a new --run')
    out.mkdir(parents=True)
    os.environ.update(CUDA_VISIBLE_DEVICES='0' if args.device == 'cuda' else '-1',
        FLYVIS_ROOT_DIR='/tmp/flyvis-circuit-selection-phase2-20261010' if sys.platform == 'linux' else str(HERE / 'runtime/flyvis'), MPLBACKEND='Agg',
        MPLCONFIGDIR=str(HERE / 'runtime/matplotlib'), NUMBA_CACHE_DIR=str(HERE / 'runtime/numba'),
        TIMEZONE='Asia/Shanghai', CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONDONTWRITEBYTECODE='1')
    sys.dont_write_bytecode = True
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.manual_seed(0)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    dependency = HERE / 'dependencies/a_snapshot'
    sys.path.insert(0, str(dependency))
    from r_only import RStepService
    from gpu_adapter import GPUAdapter
    bundle = args.bundle.resolve()
    start = time.monotonic()
    entries = manifest_verify(bundle)
    before = {entry['path']: entry['sha256'] for entry in entries}
    identity = json.loads((bundle / 'identity_manifest.json').read_text(encoding='utf-8'))
    stimulus_meta = json.loads((bundle / 'stimulus_manifest.json').read_text(encoding='utf-8'))
    candidate_path = bundle / 'candidates/B_T5c/candidate_manifest.json'
    candidate = json.loads(candidate_path.read_text(encoding='utf-8'))
    stimulus = np.load(bundle / 'stimulus.npy', allow_pickle=False)
    initial = np.load(bundle / 'initial_state_full.npy', allow_pickle=False)
    clock = np.load(bundle / 'time.npy', allow_pickle=False)
    assert stimulus.shape == (4, 485, 1, 721) and stimulus.dtype == np.float32 and stimulus.flags.c_contiguous
    assert np.isfinite(stimulus).all() and ((stimulus >= 0) & (stimulus <= 1)).all()
    assert initial.shape == (45669,) and initial.dtype == np.float32 and np.isfinite(initial).all()
    assert np.array_equal(clock, np.arange(485) * .005 - 1.0)
    assert file_hash(bundle / 'initial_state_full.npy') == identity['initial_state_sha256']
    assert file_hash(bundle / 'stimulus.npy') == stimulus_meta['stimulus_sha256']
    assert file_hash(bundle / 'time.npy') == stimulus_meta['time_sha256']
    conditions = list(csv.DictReader((bundle / 'conditions.csv').open(encoding='utf-8')))
    assert [int(row['original_sample']) for row in conditions] == [0, 1, 12, 13]
    updater = HUpdater(STATIC)
    assert np.array_equal(candidate['h_global_node_indices'], updater.h_ids)
    inputs = validate_parameters(updater, bundle / 'expanded_parameters.npz')
    h_ids = updater.h_ids
    r_ids = np.setdiff1d(np.arange(45669, dtype=np.int64), h_ids)
    central = np.load(bundle / 'central_node_indices.npy', allow_pickle=False)
    types = np.load(bundle / 'cell_types.npy', allow_pickle=False)
    t4t5 = central[np.isin(types, ['T4'+s for s in 'abcd'] + ['T5'+s for s in 'abcd'])]
    comparison = hashlib.sha256(json.dumps(dict(checkpoint=identity['checkpoint_sha256'],
        expanded=identity['expanded_parameters_sha256'], candidate=file_hash(candidate_path),
        initial=file_hash(bundle / 'initial_state_full.npy'), stimulus=file_hash(bundle / 'stimulus.npy'),
        time=file_hash(bundle / 'time.npy'), metrics='atol=rtol=1e-5;all_H_R_full_central_T4T5'), sort_keys=True).encode()).hexdigest()
    run_id = str(uuid.uuid4())
    code_files = ['h_step.py', 'coordinator.py', 'gpu_adapter.py', 'run_closed_loop.py']
    source_hashes = {name: file_hash(HERE / name) for name in code_files}
    dependency_hashes = {name: file_hash(dependency / name) for name in ['r_only.py', 'full_oracle.py']}
    spec = dict(run_id=run_id, comparison_id=comparison, mode=args.mode, device=args.device,
        checkpoint_sha256=identity['checkpoint_sha256'], source_commit=identity['source_commit'],
        expanded_parameters_sha256=identity['expanded_parameters_sha256'], initial_state_sha256=identity['initial_state_sha256'],
        stimulus_sha256=stimulus_meta['stimulus_sha256'], time_axis_sha256=stimulus_meta['time_sha256'],
        conditions_sha256=stimulus_meta['conditions_sha256'], H_ids_hash=updater.h_order_digest,
        node_map_sha256=file_hash(bundle / 'candidates/B_T5c/node_map.csv'),
        edge_partition_sha256=file_hash(bundle / 'candidates/B_T5c/edge_partition_ids.npz'),
        candidate_sha256=file_hash(candidate_path), circuit_sha256=updater.circuit_digest,
        dt_s=.005, atol=1e-5, rtol=1e-5, code_sha256=source_hashes, A_snapshot_sha256=dependency_hashes,
        command=[sys.executable, *sys.argv], python=platform.python_version(), torch=torch.__version__, numpy=np.__version__,
        canonical_initial_device=identity['canonical_initial_state_device'], numeric_profile='FP32 software; no hardware format selected',
        CURRENT_AGG_reduction='NumPy host-side live RH, then HH+RH; no claim of GPU RH reduction parity',
        execution_evidence_level='SOFTWARE_FULL_REFERENCE' if args.mode == 'Full' else 'SOFTWARE_CLOSED_LOOP',
        acceptance_profile='Reference gate atol=rtol=1e-5 fixed before this run; hardware acceptance separate')
    dump(out / 'run_identity.json', spec)
    if args.mode != 'Full':
        if args.reference is None:
            raise StepError('NO_REFERENCE', 'new same-initial Full run required')
        ref_meta = json.loads((args.reference / 'run_identity.json').read_text(encoding='utf-8'))
        assert ref_meta['comparison_id'] == comparison and ref_meta['mode'] == 'Full'
        reference = np.load(args.reference / 'activities_full.npy', mmap_mode='r', allow_pickle=False)
        assert reference.shape == (4, 485, 45669)
        service = RStepService(bundle / 'expanded_parameters.npz', bundle / 'identity_manifest.json', candidate_path, device=args.device)
        adapter = GPUAdapter(service, inputs)
        assert service.partition_counts == dict(HH=970, RH=5567, HR=8159, RR=1498535)
        with np.load(bundle / 'expanded_parameters.npz', allow_pickle=False) as all_params:
            assert not np.isin(all_params['target_global'][service.original_edge_ids], h_ids).any()
        assert service.n_r == 45602 and service.n_r_edges == 1506694
    else:
        from full_oracle import FullNetworkOracle
        oracle = FullNetworkOracle(bundle / 'identity_manifest.json', device=args.device)
    trace = np.lib.format.open_memmap(out / 'activities_full.npy', mode='w+', dtype='<f4', shape=(4, 485, 45669))
    np.save(out / 'H_global_ids.npy', h_ids)
    np.save(out / 'R_global_ids.npy', r_ids)
    np.save(out / 'central_global_ids.npy', central)
    np.save(out / 'T4T5_global_ids.npy', t4t5)
    records = []
    status_log = (out / 'step_status.jsonl').open('w', encoding='utf-8')
    guards = []
    for c, condition in enumerate(conditions):
        case = out / f'condition_{c:02d}'
        case.mkdir()
        local_start = time.monotonic()
        rows = []
        per_node = np.zeros(45669, dtype=np.float64)
        H_both = np.empty((485, 2, 67), dtype=np.float32)
        if args.mode == 'Full':
            old = torch.tensor(initial.copy(), device=args.device, dtype=torch.float32)
            for k in range(485):
                old_np = old.detach().cpu().numpy().copy()
                H_both[k, 0] = old_np[h_ids]
                old = oracle.step(old, torch.tensor(stimulus[c, k, 0].copy(), device=args.device, dtype=torch.float32))
                result = old.detach().cpu().numpy().copy()
                trace[c, k] = result
                H_both[k, 1] = result[h_ids]
                status_log.write(json.dumps(dict(status='FULL_REFERENCE_ONLY', condition=c, step_id=k,
                    input_digest=array_hash(stimulus[c, k, 0]), before_digest=array_hash(old_np), after_digest=array_hash(result))) + '\n')
            oracle.assert_weights_unchanged()
            records.append(dict(condition=condition, steps=485, wall_s=time.monotonic()-local_start))
        else:
            updater = HUpdater(STATIC)
            coordinator = Coordinator(updater, adapter, initial, run_id, comparison, str(condition['original_sample']))
            with native_full_forbidden() as audit:
                for k in range(485):
                    old_np = coordinator.state
                    H_both[k, 0] = old_np[h_ids]
                    x = np.zeros(45669, dtype=np.float32)
                    x[inputs.reshape(-1)] = np.tile(stimulus[c, k, 0], 8)
                    result = coordinator.step(k, x, args.mode)
                    trace[c, k] = result
                    H_both[k, 1] = result[h_ids]
                    row = dict(step_id=k, time_after_label=float(clock[k]))
                    for label, ids in [('H', h_ids), ('R', r_ids), ('full', np.arange(45669)), ('central', central), ('T4T5', t4t5)]:
                        row.update({label + '_' + key: value for key, value in errors(result, reference[c, k], ids).items()})
                    rows.append(row)
                    per_node = np.maximum(per_node, np.abs(result.astype(np.float64)-reference[c, k].astype(np.float64)))
                    for event in coordinator.logs[-2:]:
                        status_log.write(json.dumps(dict(condition=c, **event)) + '\n')
                assert updater.step_count == 485 and coordinator.next_step_id == 485
                guards.append(dict(condition=c, **audit, independent_H_steps=updater.step_count, committed_steps=coordinator.next_step_id))
            with (case / 'step_errors.csv').open('w', newline='', encoding='utf-8') as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            np.save(case / 'per_node_max_abs.npy', per_node)
            np.save(case / 'final_full_error.npy', trace[c, -1].astype(np.float64)-reference[c, -1].astype(np.float64))
            records.append(dict(condition=condition, steps=485, wall_s=time.monotonic()-local_start,
                max_abs={label:max(row[label+'_max_abs'] for row in rows) for label in ['H','R','full','central','T4T5']},
                violations={label:sum(row[label+'_violations'] for row in rows) for label in ['H','R','full','central','T4T5']},
                final={label:errors(trace[c, -1], reference[c, -1], ids) for label, ids in [('H',h_ids),('R',r_ids),('full',np.arange(45669)),('central',central),('T4T5',t4t5)]}))
        np.save(case / 'H_before_after.npy', H_both)
        np.save(case / 'activity_central.npy', trace[c, :, central].T)
        np.save(case / 'activity_T4T5.npy', trace[c, :, t4t5].T)
        trace.flush()
        print('CONDITION_COMPLETE', json.dumps(dict(mode=args.mode, original_sample=condition['original_sample'], seconds=time.monotonic()-local_start)), flush=True)
    status_log.close()
    trace.flush()
    unchanged = all(file_hash(bundle / path) == digest for path, digest in before.items())
    assert unchanged
    assert all(file_hash(HERE / name) == digest for name, digest in source_hashes.items())
    assert all(file_hash(dependency / name) == digest for name, digest in dependency_hashes.items())
    numerical_pass = args.mode == 'Full' or all(sum(row['violations'].values()) == 0 for row in records)
    info = dict(status='PASS_FULL_REFERENCE' if args.mode=='Full' else ('PASS_CLOSED_LOOP_NUMERICAL' if numerical_pass else 'FAIL_CLOSED_LOOP_NUMERICAL'),
        phase2_status='PENDING_FEEDBACK_AND_REAL_SERVICE_NEGATIVE_TESTS', evidence_level=spec['execution_evidence_level'],
        run_identity=spec, conditions=records, production_guards=guards, input_bundle_unchanged=unchanged,
        input_bundle_manifest_entries_verified=len(entries), wall_s=time.monotonic()-start,
        peak_cuda_bytes=torch.cuda.max_memory_allocated() if args.device=='cuda' else 0,
        gpu=torch.cuda.get_device_name(0) if args.device=='cuda' else None,
        no_recorded_R_as_production_input=True, native_H_production_updates=0 if args.mode!='Full' else 'FULL_REFERENCE_ONLY',
        limitations=['No FPGA/RTL or fixed-point evidence', 'Host/GPU snapshot transfer and whole-state validation are not a 200Hz performance claim'])
    dump(out / 'result.json', info)
    dump(out / 'artifact_manifest.json', [dict(path=str(path.relative_to(out)), bytes=path.stat().st_size, sha256=file_hash(path))
        for path in sorted(out.rglob('*')) if path.is_file() and path.name!='artifact_manifest.json'])
    print('RUN_RESULT', json.dumps(dict(status=info['status'], wall_s=info['wall_s'], max_full=None if args.mode=='Full' else max(row['max_abs']['full'] for row in records))), flush=True)


if __name__ == '__main__':
    main()

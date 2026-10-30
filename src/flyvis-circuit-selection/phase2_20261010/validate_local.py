"""Historical-boundary replay only. Explicitly NOT full-network replacement."""
from pathlib import Path
import csv
import argparse
import json
import platform
import time
import uuid
import numpy as np
from h_step import HUpdater, HRequest, StepTag, array_hash, file_hash, frozen

HERE = Path(__file__).resolve().parent
FPGA = HERE.parents[1]
STATIC = HERE.parent / 'round1_20261010/artifacts/B_T5c/static_boundary.npz'
BOUNDARY = FPGA / 'flyvis-visual-experiments/artifacts/boundary_cuda_r1/T5c'
GOLDEN = FPGA / 'flyvis-visual-experiments/artifacts/golden_reference_v2'
OUT = HERE / 'artifacts/local_replay_r2'


def error_metrics(actual, expected):
    delta = actual.astype(np.float64) - expected.astype(np.float64)
    absolute = np.abs(delta)
    tolerance = 1e-5 + 1e-5 * np.abs(expected.astype(np.float64))
    return dict(max_abs=float(absolute.max()), mae=float(absolute.mean()), rmse=float(np.sqrt((delta * delta).mean())),
        violations=int((absolute > tolerance).sum()), argmax_flat=int(absolute.argmax()), bitwise_equal=bool(np.array_equal(actual, expected)))


def main():
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=OUT)
    OUT = parser.parse_args().output.resolve()
    if OUT.exists():
        raise SystemExit('Existing run preserved; use a fresh output namespace.')
    OUT.mkdir(parents=True)
    samples = {int(row['sample']): row for row in csv.DictReader((GOLDEN / 'samples.csv').open(encoding='utf-8'))}
    records, inputs = [], {}
    run_id = str(uuid.uuid4())
    start = time.monotonic()
    updater = HUpdater(STATIC)
    np.save(OUT / 'H_global_ids.npy', updater.h_ids)
    np.save(OUT / 'incoming_source_global_ids.npy', updater.source_ids)
    log = (OUT / 'step_status.jsonl').open('w', encoding='utf-8')
    for sample in [0, 1, 12, 13]:
        folder = BOUNDARY / f'sample_{sample:02d}'
        paths = {name: folder / name for name in ['initial_internal.npy', 'boundary_incoming_activity_before.npy',
            'internal_activity_after.npy', 'external_node_input.npy']}
        inputs.update({str(path): file_hash(path) for path in paths.values()})
        init = np.load(paths['initial_internal.npy'], allow_pickle=False)
        boundary = np.load(paths['boundary_incoming_activity_before.npy'], allow_pickle=False)
        golden = np.load(paths['internal_activity_after.npy'], allow_pickle=False)
        direct_x = np.load(paths['external_node_input.npy'], allow_pickle=False)
        assert init.shape == (67,) and boundary.shape == (485, 1364) and golden.shape == direct_x.shape == (485, 67)
        case = OUT / f'sample_{sample:02d}'
        case.mkdir()
        arrays = {key: np.empty_like(golden) for key in ['source_raw_teacher', 'source_raw_recursive', 'current_agg_teacher', 'current_agg_recursive']}
        step_rows = []
        for layout in ['SOURCE_RAW', 'CURRENT_AGG']:
            recursive = init.copy()
            for k in range(485):
                old_teacher = init if k == 0 else golden[k - 1]
                incoming = frozen(boundary[k]) if layout == 'SOURCE_RAW' else updater.aggregate_sources(frozen(boundary[k]))
                source_ids = updater.source_ids if layout == 'SOURCE_RAW' else None
                results = {}
                for kind, old in [('teacher', old_teacher), ('recursive', recursive)]:
                    tag = StepTag(run_id, 'LOCAL_REPLAY_ONLY', str(sample), 0, k, 'FULL_STATE_NOT_AVAILABLE')
                    request = HRequest(tag, layout, frozen(old), frozen(direct_x[k]), frozen(incoming),
                        updater.h_ids, source_ids, updater.circuit_digest)
                    result = updater.step(request)
                    arrays[layout.lower() + '_' + kind][k] = result.new_h
                    results[kind] = error_metrics(result.new_h, golden[k])
                    step_rows.append(dict(sample=sample, layout=layout, kind=kind, step_id=k,
                        **results[kind], request_digest=result.request_digest))
                    log.write(json.dumps(dict(evidence_level='SOFTWARE_REPLAY', sample=sample, layout=layout,
                        kind=kind, step_id=k, request_digest=result.request_digest, new_H_digest=array_hash(result.new_h))) + '\n')
                    if kind == 'recursive':
                        recursive = result.new_h
        for name, values in arrays.items():
            np.save(case / (name + '.npy'), values)
            np.save(case / (name + '_error.npy'), values.astype(np.float64) - golden.astype(np.float64))
        with (case / 'step_errors.csv').open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(step_rows[0]))
            writer.writeheader()
            writer.writerows(step_rows)
        aggregate_difference = error_metrics(arrays['current_agg_recursive'], arrays['source_raw_recursive'])
        measures = {key: dict(all_steps=error_metrics(values, golden), final=error_metrics(values[-1], golden[-1]),
            per_node_max_abs=np.abs(values.astype(np.float64) - golden.astype(np.float64)).max(axis=0).tolist()) for key, values in arrays.items()}
        records.append(dict(sample=sample, angle=float(samples[sample]['angle']), intensity=float(samples[sample]['intensity']),
            polarity='ON' if float(samples[sample]['intensity']) == 1 else 'OFF', steps=485,
            local_initial_sha256=file_hash(paths['initial_internal.npy']), metrics=measures,
            current_agg_vs_source_raw=aggregate_difference))
    log.close()
    assert all(file_hash(Path(path)) == digest for path, digest in inputs.items())
    all_pass = all(item['all_steps']['violations'] == 0 for record in records for item in record['metrics'].values())
    result = dict(status='PASS_LOCAL_REPLAY' if all_pass else 'FAIL_LOCAL_REPLAY', evidence_level='SOFTWARE_REPLAY',
        phase2_status='PARTIAL_NOT_CLOSED_LOOP', candidate='T5c_67_SOFTWARE_PROVISIONAL',
        run_id=run_id, dt_s=0.005, atol=1e-5, rtol=1e-5, full_initial_state='NOT_AVAILABLE',
        live_R_only_service='NOT_USED', native_H_update_exclusion='NOT_PROVEN_IN_FULL_NETWORK',
        circuit_sha256=file_hash(STATIC), H_ids_hash=updater.h_order_digest, source_ids_hash=updater.source_order_digest,
        input_file_hashes=inputs, inputs_unchanged=True,
        code_hashes={str(HERE / name): file_hash(HERE / name) for name in ['h_step.py', 'validate_local.py']},
        runtime=dict(python=platform.python_version(), numpy=np.__version__, platform=platform.platform()),
        conditions=records, wall_seconds=time.monotonic() - start,
        limitation='Recorded R_before drives this experiment; no live R trajectory, whole-state error or closed-loop feedback proof.')
    (OUT / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(dict(status=result['status'], seconds=result['wall_seconds'],
        cases=[dict(sample=r['sample'], source_max=r['metrics']['source_raw_recursive']['all_steps']['max_abs'],
            aggregate_max=r['metrics']['current_agg_recursive']['all_steps']['max_abs'],
            aggregate_vs_source=r['current_agg_vs_source_raw']['max_abs']) for r in records]), ensure_ascii=False))


if __name__ == '__main__':
    main()

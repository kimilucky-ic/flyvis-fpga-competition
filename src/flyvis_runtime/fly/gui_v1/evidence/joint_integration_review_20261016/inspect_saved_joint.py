"""Bounded read-only review of an existing joint run; never runs neural compute."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import time

import numpy as np

FLY = Path(r'C:\Users\hzy72\Documents\ChatGPT\fly')
BASE = FLY.parent / 'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/joint_latency485_20261016'
RUN = 'c708f1c9bac14c07ac8f56d59678b95a'
WORKER = BASE / 'workers' / RUN
RESULTS = BASE / 'runs' / RUN
OUT = Path(__file__).resolve().parent


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def require(value, label):
    if not value:
        raise ValueError(label)


def main():
    began = time.perf_counter()
    final = load(RESULTS / 'FINAL_RESULT.json')
    metrics = load(RESULTS / 'AUDIT_METRICS.json')
    manifest = load(WORKER / 'manifest.json')
    stamps = {}
    checked = {}
    for name, expected in manifest['files'].items():
        p = (WORKER / name).resolve()
        require(p.is_relative_to(WORKER.resolve()), 'MANIFEST_PATH_ESCAPE')
        stamps[p] = (p.stat().st_size, p.stat().st_mtime_ns)
        actual = digest(p)
        require(actual == expected, 'PC_MANIFEST_CHANGED: ' + name)
        checked[name] = actual
    pc_path, ps_path = WORKER / 'pc/evidence.fvej', RESULTS / 'board.fvej'
    stamps[ps_path] = (ps_path.stat().st_size, ps_path.stat().st_mtime_ns)
    require(checked['pc/evidence.fvej'] == metrics['pc_sha256'], 'PC_AUDIT_CAPTURE')
    ps_sha = digest(ps_path)
    require(ps_sha == metrics['ps_sha256'], 'PS_AUDIT_CAPTURE')
    require(digest(WORKER / 'manifest.json') == final['pc_manifest_sha256'], 'FINAL_MANIFEST_PIN')
    require(final['status'] == 'PASS_ACTUAL_485_STEP_GPU_FPGA_CLOSED_LOOP', 'NOT_ACCEPTED')
    require(final['run_id'] == RUN and final['model_steps'] == list(range(485)), 'RUN_STEPS')
    require(final['PL_outputs_checked'] == 485 * 5768 and final['PL_feedback_words_checked'] == 484 * 5768, 'PL_COUNTS')
    require(final['native_H_GPU_updates'] == 0 and len(set(final['PL_proven_global_ids'])) == 5768, 'PL_OWNERSHIP')
    require(final['extra_raw_checks'] == dict(wire_frames=1942, raw_MMIO_identity_steps=485, recomputed_unified_COMMITs=485), 'RAW_AUDIT_COUNTS')

    # Import only the delivered standard-library file reader, never a worker/service.
    reader_path = BASE / 'a3latency485/evidence_journal.py'
    spec = importlib.util.spec_from_file_location('saved_joint_reader_only', reader_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pc, ps = module.JournalReader(pc_path), module.JournalReader(ps_path)
    require(pc.terminal['status'] == ps.terminal['status'] == 'CAPTURE_COMPLETE_NOT_HARDWARE_ADMISSION', 'CAPTURE_TERMINAL')
    require(pc.terminal['completed'] == ps.terminal['requests'] == ps.terminal['acks'] == 485, 'TERMINAL_COUNTS')

    def array(name):
        return np.load(io.BytesIO(pc.read(name)), allow_pickle=False)

    previous = None
    means = []
    for k, audit_row in enumerate(final['rows']):
        row = json.loads(pc.read(f'committed_step_{k}.json'))
        require(row['run_id'] == RUN and row['model_step'] == k and row['state_token'] == k + 1, 'ROW_IDENTITY')
        require(row['full_after_sha'] == audit_row['new_full_sha'] and row['unified_commit_sha'] == audit_row['commit_sha'], 'ROW_COMMIT_IDENTITY')
        require(row['commit'] == 'ACK_MATCHED_AND_PUBLISHED' and audit_row['PL_integer_error'] == 0, 'ROW_COMMIT_OR_INTEGER')
        require(previous is None or row['old_full_sha'] == previous, 'FEEDBACK_CHAIN')
        require(row['input_time_s'] == k * .005 - 1 and row['activity_time_s'] == k * .005 - 1 + .005, 'DUAL_MODEL_TIME')
        previous = row['full_after_sha']
        x, spatial, flow = (array(f'{name}_{k}.npy') for name in ('input_721', 'spatial', 'flow'))
        for a, shape in ((x, (721,)), (spatial, (5768,)), (flow, (2, 721))):
            require(a.dtype == np.dtype('<f4') and a.shape == shape and np.isfinite(a).all(), 'GUI_ARRAY_SCHEMA')
        means.append(spatial.reshape(8, 721).mean(axis=1, dtype=np.float64))
    signed_means = np.stack(means)
    exit_state = load(WORKER / 'exit.json')
    require(exit_state['GPU_inflight_waited'] and exit_state['lease_closed'] and not exit_state['cleanup_errors'], 'GPU_CLEANUP')
    for p, stamp in stamps.items():
        require((p.stat().st_size, p.stat().st_mtime_ns) == stamp, 'SOURCE_CHANGED_DURING_REVIEW')

    time_data = final['post_run_timing']
    exclusive = final['host_optimization']['totals']['exclusive_s']
    denom = final['host_optimization']['totals']['inclusive_s']['complete_step']
    out = dict(
        status='PASS_SAVED_JOINT_INTEGRATION_REVIEW', run_id=RUN,
        evidence_level='READONLY_REVIEW_OF_EXISTING_ACTUAL_JOINT_RUN_NOT_NEW_EXECUTION',
        final_result_sha256=digest(RESULTS / 'FINAL_RESULT.json'),
        saved_audit_metrics_sha256=digest(RESULTS / 'AUDIT_METRICS.json'),
        pc_manifest_sha256=digest(WORKER / 'manifest.json'),
        pc_capture_sha256=checked['pc/evidence.fvej'], ps_capture_sha256=ps_sha,
        manifest_files_checked=len(checked), logical_files_pc=len(pc.files), logical_files_ps=len(ps.files),
        saved_committed_steps_checked=485, gui_spatial_values_checked=485 * 5768,
        gui_official_flow_values_checked=485 * 2 * 721, signed_type_means_checked=485 * 8,
        means_min=signed_means.min(axis=0).tolist(), means_max=signed_means.max(axis=0).tolist(),
        numeric_profile='H_A3R1_Q24_R_ORIGINAL_FP32',
        mixed_flow_reference='NOT_INDEPENDENTLY_RECOMPUTED_IN_THIS_485_RUN',
        steps_per_wall_second=485 / time_data['formal_step_loop_s'],
        step_loop_s=time_data['formal_step_loop_s'], step_body_sum_s=time_data['formal_step_sum_s'],
        model_duration_s=485 * .005, formal_execution_s=time_data['formal_execution_s'],
        preparation_s=time_data['preparation_s'], ready_to_verified_s=time_data['LOCAL_READY_to_verified_s'],
        mean_step_body_ms=time_data['formal_step_sum_s'] / 485 * 1000,
        exclusive_host_phase_s=exclusive,
        exclusive_phase_share_of_instrumented_total={k: v / denom for k, v in exclusive.items()},
        note='PS fsync is nested inside PC exchange; CUDA host-with-sync timings are not kernel-only.',
        GPU_operations=0, camera_operations=0, GUI_launches=0, board_operations=0,
        runtime_or_registry_changes=0, historical_neural_recomputations=0,
        elapsed_review_s=time.perf_counter() - began,
    )
    path = OUT / 'review.json'
    with path.open('x', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2, allow_nan=False)
    print(json.dumps({k: out[k] for k in ('status', 'run_id', 'manifest_files_checked', 'saved_committed_steps_checked', 'steps_per_wall_second', 'elapsed_review_s')}, indent=2))


if __name__ == '__main__':
    main()

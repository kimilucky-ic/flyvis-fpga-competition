"""Actual GPU-R faults and bidirectional live-state causal probes.

Probe branches have explicit different initial-state hashes; they are isolated
from the normal Full/Replacement equality comparison. No recorded R drives them.
"""
from pathlib import Path
from dataclasses import replace
import json
import os
import sys
import uuid
import argparse
import numpy as np
from h_step import HUpdater, HRequest, StepTag, StepError, array_hash, file_hash, frozen
from coordinator import Coordinator
from run_closed_loop import native_full_forbidden, manifest_verify, validate_parameters
from run_negative_tests import FaultH

HERE = Path(__file__).resolve().parent
STATIC = HERE.parent / 'round1_20261010/artifacts/B_T5c/static_boundary.npz'
BUNDLE = HERE.parents[2] / 'fly/gpu_phase2/artifacts/reference_bundle_v1'
OUT = HERE / 'artifacts/live_feedback_r1'


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


class FaultR:
    state_semantics = 'STATELESS_CANDIDATE_ONLY'
    def init__(self, adapter, fault):
        self.adapter, self.fault = adapter, fault

    def evaluate(self, old, x, tag):
        if self.fault == 'future_H_in_R_same_step':
            u = HUpdater(STATIC)
            request = HRequest(tag, 'SOURCE_RAW', frozen(old[u.h_ids]), frozen(x[u.h_ids]),
                frozen(old[u.source_ids]), u.h_ids, u.source_ids, u.circuit_digest)
            future = old.copy()
            future[u.h_ids] = u.step(request).new_h
            return self.adapter.evaluate(future, x, tag)
        result = self.adapter.evaluate(old, x, tag)
        if self.fault == 'nan_R':
            data = result.new_r.copy()
            data[0] = np.nan
            return replace(result, new_r=frozen(data))
        if self.fault == 'swapped_R_ids':
            ids = result.r_global_ids.copy()
            ids[[0, 1]] = ids[[1, 0]]
            return replace(result, r_global_ids=frozen(ids))
        return result


def main():
    global STATIC, BUNDLE, OUT
    parser=argparse.ArgumentParser()
    parser.add_argument('--bundle',type=Path,default=BUNDLE)
    parser.add_argument('--static-path',type=Path,default=STATIC)
    parser.add_argument('--source-run',type=Path,default=HERE/'artifacts/source_gpu_r1')
    parser.add_argument('--run',default='live_feedback_r1')
    args=parser.parse_args()
    BUNDLE,STATIC,OUT=args.bundle,args.static_path,HERE/'artifacts'/args.run
    if OUT.exists():
        raise SystemExit('Existing live probe preserved; use a new namespace.')
    OUT.mkdir(parents=True)
    os.environ.update(CUDA_VISIBLE_DEVICES='0', FLYVIS_ROOT_DIR='/tmp/flyvis-circuit-selection-phase2-20261010',
        MPLBACKEND='Agg', MPLCONFIGDIR=str(HERE/'runtime/matplotlib'), NUMBA_CACHE_DIR=str(HERE/'runtime/numba'),
        CUBLAS_WORKSPACE_CONFIG=':4096:8', TIMEZONE='Asia/Shanghai', PYTHONDONTWRITEBYTECODE='1')
    sys.dont_write_bytecode = True
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    sys.path.insert(0, str(HERE/'dependencies/a_snapshot'))
    from r_only import RStepService
    from gpu_adapter import GPUAdapter
    entries = manifest_verify(BUNDLE)
    inputs_before = {entry['path']: entry['sha256'] for entry in entries}
    updater = HUpdater(STATIC)
    input_ids = validate_parameters(updater, BUNDLE/'expanded_parameters.npz')
    service = RStepService(BUNDLE/'expanded_parameters.npz', BUNDLE/'identity_manifest.json',
        BUNDLE/'candidates/B_T5c/candidate_manifest.json', device='cuda')
    adapter = GPUAdapter(service, input_ids)
    stimulus = np.load(BUNDLE/'stimulus.npy', allow_pickle=False)
    initial = np.load(BUNDLE/'initial_state_full.npy', allow_pickle=False)
    x = np.zeros(45669, dtype=np.float32)
    x[input_ids.reshape(-1)] = np.tile(stimulus[0, 0, 0], 8)
    tests, events = [], []
    with native_full_forbidden() as fault_guard:
        for fault, expected in [('wrong_request_step','OUT_OF_ORDER'), ('nan_H','NONFINITE'), ('nan_R','NONFINITE'),
            ('failure','CORE_ERROR'), ('worker_exit','CORE_ERROR'), ('timeout','CORE_ERROR'), ('swapped_H_ids','LAYOUT_MISMATCH'),
            ('swapped_source_ids','LAYOUT_MISMATCH'), ('swapped_R_ids','LAYOUT_MISMATCH'),
            ('wrong_result_step','OUT_OF_ORDER'), ('wrong_epoch','OUT_OF_ORDER'), ('stale_request','STATE_MISMATCH'),
            ('future_H_in_R_same_step','STATE_MISMATCH')]:
            coordinator = Coordinator(updater, FaultR(adapter, fault), initial, str(uuid.uuid4()), 'GPU_FAULT_ONLY', fault)
            digest = array_hash(coordinator.state)
            calls = adapter.calls
            caught = None
            try:
                prepared = coordinator.prepare(1 if fault=='wrong_request_step' else 0, x, h_backend=FaultH(updater, fault))
                coordinator.commit(prepared)
            except StepError as error:
                caught = error.code
            assert caught == expected, (fault, caught, expected)
            assert array_hash(coordinator.state)==digest and coordinator.next_step_id==0 and coordinator.status=='FAILED'
            assert not any(row['status']=='COMMITTED' for row in coordinator.logs)
            tests.append(dict(test=fault, status='PASS', error=caught, actual_GPU_R_evaluations=adapter.calls-calls,
                R_candidate_not_committed=True, full_state_unchanged=True, fallback_count=0))
            events.extend(dict(test=fault, **row) for row in coordinator.logs)
        coordinator = Coordinator(updater, adapter, initial, str(uuid.uuid4()), 'GPU_FAULT_ONLY', 'duplicate_commit')
        prepared = coordinator.prepare(0, x)
        assert array_hash(coordinator.state)==array_hash(initial)
        coordinator.commit(prepared)
        digest = array_hash(coordinator.state)
        try:
            coordinator.commit(prepared)
            raise AssertionError('duplicate accepted')
        except StepError as error:
            assert error.code=='ALREADY_COMMITTED'
        assert coordinator.next_step_id==1 and array_hash(coordinator.state)==digest
        tests.append(dict(test='duplicate_commit', status='PASS', committed_steps=1, no_second_commit=True))
        events.extend(dict(test='duplicate_commit', **row) for row in coordinator.logs)
    assert fault_guard['forbidden_native_call_count']==0
    # A deliberate positive control proves the production guard really rejects.
    with native_full_forbidden() as positive_guard:
        from flyvis.network.network import Network
        try:
            Network._next_state(None, None, None, None, None)
            raise AssertionError('native guard not active')
        except StepError as error:
            assert error.code=='NATIVE_FULL_UPDATE_FORBIDDEN'
    assert positive_guard['forbidden_native_call_count']==1
    tests.append(dict(test='native_full_guard_positive_control', status='PASS', forbidden_attempts=1,
        note='deliberate separate negative experiment, not a production native update'))

    # Fork a verified own Replacement checkpoint, then calculate every subsequent R live.
    main_source = args.source_run
    info = json.loads((main_source/'result.json').read_text(encoding='utf-8'))
    assert info['status']=='PASS_CLOSED_LOOP_NUMERICAL'
    assert info['run_identity']['expanded_parameters_sha256']==file_hash(BUNDLE/'expanded_parameters.npz')
    assert info['run_identity']['circuit_sha256']==updater.circuit_digest
    main_trajectory = np.load(main_source/'activities_full.npy', mmap_mode='r', allow_pickle=False)
    branch_step = 220
    common = np.array(main_trajectory[0, branch_step-1], copy=True)
    with np.load(STATIC, allow_pickle=False) as static:
        z = {key: static[key] for key in static.files}
    incoming_by_source = {}
    for i, (src, weight) in enumerate(zip(z['incoming_source_index'], z['incoming_weight'])):
        if abs(weight) > .01:
            incoming_by_source.setdefault(int(src), []).append(i)
    pairs = []
    for i, (src, dst, weight) in enumerate(zip(z['outgoing_source_index'], z['outgoing_target_index'], z['outgoing_weight'])):
        if abs(weight) > .01 and common[src] > 0 and common[dst] > 0:
            for j in incoming_by_source.get(int(dst), []):
                pairs.append((float(abs(weight*z['incoming_weight'][j])), i, j))
    assert pairs
    _, hr, rh = max(pairs)
    h_source = int(z['outgoing_source_index'][hr])
    r_source = int(z['outgoing_target_index'][hr])
    return_target = int(z['incoming_target_index'][rh])
    starts = {'control': common.copy(), 'H_perturbed': common.copy(), 'R_perturbed': common.copy()}
    starts['H_perturbed'][h_source] += np.float32(.25)
    starts['R_perturbed'][r_source] += np.float32(.25)
    coordinators = {name: Coordinator(HUpdater(STATIC), adapter, state, str(uuid.uuid4()), 'ISOLATED_CAUSAL_PROBE', name)
        for name, state in starts.items()}
    traces = {name:[state.copy()] for name, state in starts.items()}
    probe_guard = {}
    with native_full_forbidden() as probe_guard:
        for k in range(8):
            x = np.zeros(45669, dtype=np.float32)
            x[input_ids.reshape(-1)] = np.tile(stimulus[0, branch_step+k, 0], 8)
            for name, coordinator in coordinators.items():
                traces[name].append(coordinator.step(k, x).copy())
                events.extend(dict(probe=name, main_frame=branch_step+k, **event) for event in coordinator.logs[-2:])
    traces = {name: np.stack(values) for name, values in traces.items()}
    delta_r_first = float(traces['H_perturbed'][1,r_source]-traces['control'][1,r_source])
    delta_h_first = float(traces['R_perturbed'][1,return_target]-traces['control'][1,return_target])
    assert abs(delta_r_first)>1e-8 and abs(delta_h_first)>1e-8
    # Same perturbed H old-state; change ONLY the returned R source in a diagnostic H step.
    after_one = traces['H_perturbed'][1]
    live_boundary = frozen(after_one[updater.source_ids])
    counterfactual_boundary = live_boundary.copy()
    source_local = int(np.searchsorted(updater.source_ids, r_source))
    counterfactual_boundary[source_local] = traces['control'][1,r_source]
    x_h = np.zeros(67, dtype=np.float32)
    tag = StepTag(str(uuid.uuid4()), 'DIAGNOSTIC_RETURN_EDGE_ONLY', 'source_clamp', 0, 1, array_hash(after_one))
    diagnostic_updater = HUpdater(STATIC)
    request = HRequest(tag, 'SOURCE_RAW', frozen(after_one[updater.h_ids]), x_h, live_boundary,
        updater.h_ids, updater.source_ids, updater.circuit_digest)
    live_h = diagnostic_updater.step(request).new_h
    without_selected_return = diagnostic_updater.step(replace(request, boundary=frozen(counterfactual_boundary))).new_h
    return_local = int(np.searchsorted(updater.h_ids, return_target))
    return_delta = float(live_h[return_local]-without_selected_return[return_local])
    assert abs(return_delta)>1e-8
    assert np.array_equal(live_h,traces['H_perturbed'][2,updater.h_ids])
    for name, values in traces.items():
        np.save(OUT/(name+'_full.npy'),values)
    unchanged = all(file_hash(BUNDLE/path)==digest for path,digest in inputs_before.items())
    assert unchanged and probe_guard['forbidden_native_call_count']==0
    result = dict(status='PASS_LIVE_FEEDBACK_AND_GPU_NEGATIVE_TESTS', evidence_level='SOFTWARE_CLOSED_LOOP_CAUSAL_AND_FAULT_TEST',
        actual_GPU_service_tested=True, actual_GPU_R_calls=adapter.calls, negative_tests=tests,
        fault_production_guard=fault_guard, positive_guard_control=positive_guard, causal_production_guard=probe_guard,
        source_checkpoint=dict(path=str(main_source/'activities_full.npy'),sha256=file_hash(main_source/'activities_full.npy'),
            before_main_step=branch_step, branch_step_ids='0..7 in independent probe epoch; stimulus frames220..227'),
        initial_probe_hashes={name:array_hash(state) for name,state in starts.items()},
        feedback=dict(H_source_global=h_source,R_intermediate_global=r_source,H_return_target_global=return_target,
            HR_original_edge_id=int(z['outgoing_edge_id'][hr]),RH_original_edge_id=int(z['incoming_edge_id'][rh]),
            HR_weight=float(z['outgoing_weight'][hr]),RH_weight=float(z['incoming_weight'][rh]),
            H_perturbation=.25,R_perturbation=.25,H_to_R_next_delta=delta_r_first,R_to_H_next_delta=delta_h_first,
            returned_R_causal_contribution_to_H_after_second_step=return_delta,
            final_full_H_branch_max_abs=float(np.abs(traces['H_perturbed'][-1]-traces['control'][-1]).max()),
            final_full_R_branch_max_abs=float(np.abs(traces['R_perturbed'][-1]-traces['control'][-1]).max()),
            diagnostic_live_H_matches_production_next_H_bitwise=True),
        input_bundle_unchanged=unchanged, code_sha256=file_hash(Path(__file__)),
        command=[sys.executable,*sys.argv],circuit_sha256=updater.circuit_digest,
        expanded_parameters_sha256=file_hash(BUNDLE/'expanded_parameters.npz'),
        initial_state_sha256=file_hash(BUNDLE/'initial_state_full.npy'),stimulus_sha256=file_hash(BUNDLE/'stimulus.npy'),
        comparison_id=info['run_identity']['comparison_id'],
        dependency_sha256={name:file_hash(HERE/name) for name in ['h_step.py','coordinator.py','gpu_adapter.py','run_negative_tests.py']},
        A_r_only_sha256=file_hash(HERE/'dependencies/a_snapshot/r_only.py'),
        limitation='Probe interventions are not normal equality conditions and do not freeze an ablation standard.')
    dump(OUT/'result.json',result)
    (OUT/'trace.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in events),encoding='utf-8')
    dump(OUT/'artifact_manifest.json',[dict(path=path.name,sha256=file_hash(path),bytes=path.stat().st_size)
        for path in sorted(OUT.iterdir()) if path.is_file() and path.name!='artifact_manifest.json'])
    print(json.dumps(dict(status=result['status'], negative_tests=len(tests), feedback=result['feedback'])),flush=True)


if __name__=='__main__':
    main()

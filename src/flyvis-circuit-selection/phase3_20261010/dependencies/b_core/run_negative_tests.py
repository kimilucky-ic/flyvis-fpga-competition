"""Fault-injection tests with an explicitly synthetic R stub, not a FlyVis service."""
from pathlib import Path
from dataclasses import replace
import json
import uuid
import subprocess
import sys
import numpy as np
from h_step import HUpdater, HResult, StepError, array_hash, frozen
from coordinator import Coordinator, RResult

HERE = Path(__file__).resolve().parent
OUT = HERE / 'artifacts/negative_tests'
STATIC = HERE.parent / 'round1_20261010/artifacts/B_T5c/static_boundary.npz'


class SyntheticR:
    state_semantics = 'STATELESS_CANDIDATE_ONLY'
    def init__(self, h_ids, fault=None):
        self.r_ids = frozen(np.setdiff1d(np.arange(45669, dtype=np.int64), h_ids))
        self.fault = fault
        self.calls = 0

    def evaluate(self, old, x, tag):
        self.calls += 1
        new = old[self.r_ids] + np.float32(.125)
        ids, count = self.r_ids, 0
        if self.fault == 'nan_R':
            new[0] = np.nan
        if self.fault == 'swapped_R_ids':
            ids = ids.copy()
            ids[[0, 1]] = ids[[1, 0]]
        if self.fault == 'native_H':
            count = 1
        if self.fault == 'mutated_old':
            old.flags.writeable = True
            old[0] += np.float32(1)
        return RResult(tag, frozen(new), frozen(ids), count, {'kind': 'SYNTHETIC_PROTOCOL_STUB'})


class FaultH:
    def init__(self, updater, fault):
        self.updater, self.fault = updater, fault

    def step(self, request):
        if self.fault == 'worker_exit':
            child = subprocess.run([sys.executable, '-c', 'raise SystemExit(23)'], capture_output=True, timeout=5)
            if child.returncode != 23:
                raise AssertionError('worker exit injection did not execute')
            raise StepError('CORE_ERROR', 'owned H worker exited with code23 before returning a candidate')
        if self.fault in ['failure', 'timeout']:
            raise RuntimeError('injected child failure') if self.fault == 'failure' else TimeoutError('injected timeout')
        if self.fault == 'swapped_H_ids':
            ids = request.h_global_ids.copy()
            ids[[0, 1]] = ids[[1, 0]]
            return self.updater.step(replace(request, h_global_ids=ids))
        if self.fault == 'swapped_source_ids':
            ids = request.source_global_ids.copy()
            ids[[0, 1]] = ids[[1, 0]]
            return self.updater.step(replace(request, source_global_ids=ids))
        result = self.updater.step(request)
        if self.fault == 'nan_H':
            new = result.new_h.copy()
            new[0] = np.nan
            return replace(result, new_h=frozen(new))
        if self.fault == 'wrong_result_step':
            return replace(result, tag=replace(result.tag, step_id=result.tag.step_id + 1))
        if self.fault == 'wrong_epoch':
            return replace(result, tag=replace(result.tag, epoch=result.tag.epoch + 1))
        if self.fault == 'stale_request':
            return replace(result, request_digest='not-the-prepared-request')
        return result


def main():
    if OUT.exists():
        raise SystemExit('Existing tests preserved; use a fresh output namespace.')
    OUT.mkdir(parents=True)
    records, trace = [], []
    updater = HUpdater(STATIC)
    x = np.zeros(45669, dtype=np.float32)
    initial = np.ones(45669, dtype=np.float32)  # Deliberately synthetic, not canonical a0.
    for fault, code in [('wrong_request_step', 'OUT_OF_ORDER'), ('nan_H', 'NONFINITE'), ('nan_R', 'NONFINITE'),
        ('failure', 'CORE_ERROR'), ('timeout', 'CORE_ERROR'), ('swapped_H_ids', 'LAYOUT_MISMATCH'),
        ('swapped_source_ids', 'LAYOUT_MISMATCH'), ('swapped_R_ids', 'LAYOUT_MISMATCH'),
        ('wrong_result_step', 'OUT_OF_ORDER'), ('wrong_epoch', 'OUT_OF_ORDER'),
        ('stale_request', 'STATE_MISMATCH'), ('native_H', 'NATIVE_H_EXECUTED'), ('mutated_old', 'STATE_MISMATCH')]:
        r = SyntheticR(updater.h_ids, fault)
        coordinator = Coordinator(updater, r, initial, str(uuid.uuid4()), 'SYNTHETIC_TEST_ONLY', fault)
        before = array_hash(coordinator.state)
        caught = None
        try:
            transaction = coordinator.prepare(1 if fault == 'wrong_request_step' else 0, x,
                h_backend=FaultH(updater, fault))
            coordinator.commit(transaction)
        except StepError as error:
            caught = error.code
        assert caught == code, (fault, caught, code)
        assert array_hash(coordinator.state) == before and coordinator.next_step_id == 0
        assert not any(row['status'] == 'COMMITTED' for row in coordinator.logs)
        assert coordinator.status == 'FAILED'
        records.append(dict(test=fault, expected_error=code, observed_error=caught, status='PASS',
            R_evaluations=r.calls, committed_steps=0, full_state_unchanged=True, no_fallback=True))
        trace.extend(dict(test=fault, **row) for row in coordinator.logs)

    coordinator = Coordinator(updater, SyntheticR(updater.h_ids), initial, str(uuid.uuid4()), 'SYNTHETIC_TEST_ONLY', 'duplicate')
    transaction = coordinator.prepare(0, x)
    assert np.array_equal(coordinator.state, initial) and coordinator.next_step_id == 0
    coordinator.commit(transaction)
    digest = array_hash(coordinator.state)
    try:
        coordinator.commit(transaction)
        raise AssertionError('duplicate accepted')
    except StepError as error:
        assert error.code == 'ALREADY_COMMITTED'
    assert coordinator.next_step_id == 1 and array_hash(coordinator.state) == digest
    records.append(dict(test='duplicate_commit', status='PASS', observed_error='ALREADY_COMMITTED',
        committed_steps=1, no_second_commit=True))
    trace.extend(dict(test='duplicate_commit', **row) for row in coordinator.logs)

    coordinator = Coordinator(updater, SyntheticR(updater.h_ids), initial, str(uuid.uuid4()), 'SYNTHETIC_TEST_ONLY', 'pending')
    coordinator.prepare(0, x)
    try:
        coordinator.prepare(0, x)
        raise AssertionError('second pending accepted')
    except StepError as error:
        assert error.code == 'NOT_READY'
    assert coordinator.next_step_id == 0 and np.array_equal(coordinator.state, initial)
    records.append(dict(test='second_pending_request', status='PASS', observed_error='NOT_READY', committed_steps=0))
    trace.extend(dict(test='second_pending_request', **row) for row in coordinator.logs)
    result = dict(status='PASS_COMPONENT_NEGATIVE_TESTS', evidence_level='SYNTHETIC_PROTOCOL_TEST',
        phase2_status='PARTIAL_NOT_CLOSED_LOOP', actual_GPU_service_tested=False,
        canonical_initial_state_used=False, tests=records,
        limitation='Must repeat faults against the supplied A GPU service before G2 acceptance.')
    (OUT / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / 'trace.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in trace), encoding='utf-8')
    print(json.dumps(dict(status=result['status'], tests=len(records), actual_GPU_service_tested=False)))


if __name__ == '__main__':
    main()

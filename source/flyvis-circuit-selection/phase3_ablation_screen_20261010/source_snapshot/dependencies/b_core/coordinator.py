"""Software old-state snapshot / prepare / atomic logical commit.

No FlyVis import, Full evaluation, recorded-R lookup or fallback exists here.
R service must be stateless: evaluate returns only an uncommitted R candidate.
This semantic adapter is a proposal, not a frozen PS/PL or transport ABI.
"""
from dataclasses import dataclass
import time
import numpy as np
from h_step import HRequest, StepTag, StepError, array_hash, frozen, request_hash, vector


@dataclass(frozen=True)
class RResult:
    tag: StepTag
    new_r: np.ndarray
    r_global_ids: np.ndarray
    native_h_update_count: int
    evidence: dict


@dataclass(frozen=True)
class PreparedStep:
    tag: StepTag
    h_request: HRequest
    h_result: object
    r_result: RResult
    input_digest: str
    expected_h_request_digest: str


class Coordinator:
    def init__(self, updater, r_service, initial_full, run_id, comparison_id, condition_id, epoch=0):
        self.updater = updater
        self.r_service = r_service
        if getattr(r_service, 'state_semantics', None) != 'STATELESS_CANDIDATE_ONLY':
            raise StepError('SERVICE_NOT_READY', 'R evaluator must not advance backend-owned state')
        self.h_ids = updater.h_ids
        self.r_ids = frozen(np.setdiff1d(np.arange(45669, dtype=np.int64), self.h_ids))
        self._state = frozen(vector(initial_full, 45669, 'initial_full'))
        self.run_id, self.comparison_id, self.condition_id = run_id, comparison_id, condition_id
        self.epoch = epoch
        self.next_step_id = 0
        self.pending = None
        self.status = 'READY'
        self.logs = []

    @property
    def state(self):
        # A defensive copy prevents a consumer from re-enabling writes on owned state.
        return frozen(self._state)

    def _fail(self, error, phase):
        self.pending = None
        self.status = 'FAILED'
        self.logs.append(dict(status='FAILED', phase=phase, error=error.code,
            next_step_id=self.next_step_id, committed_digest=array_hash(self._state)))

    def prepare(self, step_id, x_full, layout='SOURCE_RAW', h_backend=None):
        start = time.monotonic()
        try:
            if self.status == 'FAILED':
                raise StepError('NOT_READY', 'explicit recovery epoch required after failure')
            if self.pending is not None:
                raise StepError('NOT_READY', 'one uncommitted step is already pending')
            if type(step_id) is not int or step_id != self.next_step_id:
                raise StepError('OUT_OF_ORDER', 'unexpected step_id')
            x = frozen(vector(x_full, 45669, 'x_full'))
            # Both evaluators receive copies of the same committed snapshot.
            old = frozen(self._state)
            input_digest = array_hash(x)
            tag = StepTag(self.run_id, self.comparison_id, self.condition_id, self.epoch,
                step_id, array_hash(old))
            r_result = self.r_service.evaluate(old, x, tag)
            if array_hash(old) != tag.old_full_digest or array_hash(x) != input_digest:
                raise StepError('STATE_MISMATCH', 'R evaluator mutated its old-state/input snapshot')
            source = frozen(old[self.updater.source_ids])
            if layout == 'SOURCE_RAW':
                boundary, source_ids = source, self.updater.source_ids
            elif layout == 'CURRENT_AGG':
                boundary, source_ids = self.updater.aggregate_sources(source), None
            else:
                raise StepError('LAYOUT_MISMATCH', 'unknown H layout')
            request = HRequest(tag, layout, frozen(old[self.h_ids]), frozen(x[self.h_ids]),
                boundary, self.h_ids, source_ids, self.updater.circuit_digest)
            expected_h_digest = request_hash(request)
            result = (h_backend or self.updater).step(request)
            transaction = PreparedStep(tag, request, result, r_result, input_digest, expected_h_digest)
            self.pending = transaction
            self.status = 'PREPARED'
            self.logs.append(dict(status='PREPARED', step_id=step_id, epoch=self.epoch,
                old_full_digest=tag.old_full_digest, live_R_source_digest=array_hash(source),
                old_H_digest=array_hash(request.old_h), input_digest=array_hash(x),
                request_digest=request_hash(request), wall_prepare_ms=(time.monotonic()-start)*1000))
            return transaction
        except Exception as error:
            converted = error if isinstance(error, StepError) else StepError('CORE_ERROR', str(error))
            self._fail(converted, 'prepare')
            raise converted

    def commit(self, transaction):
        try:
            if transaction.tag.step_id < self.next_step_id:
                raise StepError('ALREADY_COMMITTED', 'duplicate commit cannot advance state')
            if self.status != 'PREPARED' or self.pending is not transaction:
                raise StepError('NOT_READY', 'transaction is not the active prepared step')
            if transaction.tag.old_full_digest != array_hash(self._state):
                raise StepError('STATE_MISMATCH', 'committed state changed after prepare')
            h, r, request = transaction.h_result, transaction.r_result, transaction.h_request
            if h.tag != transaction.tag or r.tag != transaction.tag:
                raise StepError('OUT_OF_ORDER', 'H/R result identity differs from request')
            if h.layout != request.layout or h.request_digest != transaction.expected_h_request_digest or request_hash(request) != transaction.expected_h_request_digest:
                raise StepError('STATE_MISMATCH', 'H result is not bound to this request')
            if h.h_order_digest != self.updater.h_order_digest or h.circuit_digest != self.updater.circuit_digest:
                raise StepError('LAYOUT_MISMATCH', 'H result mapping/model mismatch')
            if not np.array_equal(r.r_global_ids, self.r_ids):
                raise StepError('LAYOUT_MISMATCH', 'R result node order')
            if type(r.native_h_update_count) is not int or r.native_h_update_count != 0:
                raise StepError('NATIVE_H_EXECUTED', 'service reports native H production update')
            new_h = vector(h.new_h, len(self.h_ids), 'new_H')
            new_r = vector(r.new_r, len(self.r_ids), 'new_R')
            # No assignment to committed state occurs before every validation passes.
            new = np.empty(45669, dtype=np.float32)
            new[self.h_ids], new[self.r_ids] = new_h, new_r
            vector(new, 45669, 'merged_next_state')
            new = frozen(new)
            row = dict(status='COMMITTED', step_id=self.next_step_id, epoch=self.epoch,
                state_token=self.next_step_id + 1, full_after_digest=array_hash(new),
                H_after_digest=array_hash(new_h), R_after_digest=array_hash(new_r),
                native_H_update_count=r.native_h_update_count, H_request_digest=h.request_digest,
                input_digest=transaction.input_digest)
            self._state = new
            self.next_step_id += 1
            self.pending = None
            self.status = 'READY'
            self.logs.append(row)
            return self.state
        except Exception as error:
            converted = error if isinstance(error, StepError) else StepError('CORE_ERROR', str(error))
            self._fail(converted, 'commit')
            raise converted

    def step(self, step_id, x_full, layout='SOURCE_RAW'):
        return self.commit(self.prepare(step_id, x_full, layout))

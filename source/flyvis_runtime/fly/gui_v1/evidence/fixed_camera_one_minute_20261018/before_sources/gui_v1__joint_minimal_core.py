"""Computation-only camera loop; original Coordinator and numerical producers.

No filesystem, decoder, rendering, independent oracle or durable journal in
step(). Diagnostics are best-effort asynchronous observations, never admission.
"""
import dataclasses
import queue
import threading
import time

POLICY = 'MINIMAL_COMPUTE_ASYNC_V1'
EVIDENCE = 'ACK_MATCHED_RAM_ONLY_ASYNC_RECORDING'


class AsyncRecords:
    def init__(self, consume, capacity=32):
        self.queue = queue.Queue(maxsize=capacity)
        self.consume = consume
        self.submitted = self.saved = self.dropped = self.errors = 0
        self.error = None
        self.stopping = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def submit(self, record):
        if self.stopping.is_set():
            self.dropped += 1
            return False
        try:
            self.queue.put_nowait(record)
            self.submitted += 1
            return True
        except queue.Full:
            self.dropped += 1
            return False

    def _run(self):
        while not self.stopping.is_set() or not self.queue.empty():
            try:
                item = self.queue.get(timeout=.02)
            except queue.Empty:
                continue
            try:
                self.consume(item)
                self.saved += 1
            except BaseException as error:
                self.errors += 1
                if self.error is None:
                    self.error = str(error)
            finally:
                self.queue.task_done()

    def close(self, timeout=3):
        self.stopping.set()
        self.thread.join(timeout)
        return self.status()

    def status(self):
        return dict(policy='BEST_EFFORT_NONBLOCKING_DROP_ON_FULL', submitted=self.submitted,
                    saved=self.saved, dropped=self.dropped, errors=self.errors,
                    error=self.error, closed=not self.thread.is_alive(),
                    complete=not self.thread.is_alive() and not self.dropped and not self.errors
                    and self.saved == self.submitted)


class MinimalEngine:
    """One original state owner; no second implementation of neural equations."""
    def init__(self, contract, client, produce, publication, identity, recorder,
                 *, clock=time.perf_counter_ns, txn=None):
        import uuid
        from hybrid_a3 import _CoordinatorBarrier
        from joint_camera_protocol import LIVE
        self.c, self.client, self.produce = contract, client, produce
        self.identity, self.recorder, self.clock = identity, recorder, clock
        self.txn = txn or (lambda: uuid.uuid4().bytes)
        self.events, self.samples = [], []
        self.original_unchanged = contract.unchanged
        # Static source identity was checked during admission. End-of-run
        # verification is outside this computation loop, not silently skipped.
        self.original_unchanged()
        contract.unchanged = lambda: None
        self.failed = False
        self.started_ns = clock()
        initial, words, _ = contract.initial()
        self.initial, self.initial_words = initial, words
        try:
            self.barrier = _CoordinatorBarrier(contract, initial, words, identity['run_id'],
                identity['comparison_id'], identity['condition_id'], client.asid,
                self.events.append, execution_kind=LIVE, publication_factory=publication)
        except BaseException:
            contract.unchanged = self.original_unchanged
            raise

    def step(self, item):
        import numpy as np
        b, c, w = self.barrier, self.c, self.c.wire
        if self.failed or b.state_token >= self.identity['max_steps']:
            raise ValueError('MINIMAL_STOPPED_OR_STEP_LIMIT')
        k = b.state_token
        began = self.clock()
        self.events.clear()
        try:
            old = b.state
            frame = np.asarray(item['values'], dtype='<f4')
            at = self.clock()
            output = self.produce(b.publication, frame, k)
            gpu_ns = self.clock() - at
            x, chemical, rr, ids = (output[n] for n in ('x_full', 'chemical_H', 'new_R', 'r_ids'))
            cb = dict(b.binding(x), chemical_digest=b.hmod.array_hash(chemical))
            rb = dict(b.binding(x), r_candidate_digest=b.hmod.array_hash(rr),
                      r_ids_digest=b.hmod.array_hash(ids))
            header_raw, payload = b.prepare(self.txn(), x, chemical, cb)
            h = w.Header.unpack(header_raw)
            at = self.clock()
            names = ('asid', 'txn', 'step', 'old_sha', 'epoch', 'config', 'parent_commit', 'previous_txn')
            n = w.WORD_BYTES
            candidate, receipt = self.client.step(payload[:n], payload[n:2*n], payload[2*n:],
                                                 {name:getattr(h, name) for name in names})
            step_ns = self.clock() - at
            # Keep the original in-memory H/R binding and atomic publication.
            # The independent Q24/CPU oracle is not run here.
            staged = b.accept_candidates(receipt.pack(), candidate, rr, ids, rb)
            commit = b.commit_frame()
            at = self.clock()
            ack = self.client.commit(bytes.fromhex(staged['unified_commit_sha256']))
            commit_ns = self.clock() - at
            if ack != dataclasses.replace(w.Header.unpack(commit), op=w.ACK):
                raise ValueError('MINIMAL_COMMIT_ACK_MISMATCH')
            full = b.acknowledge(ack.pack())
            finished = self.clock()
            record = dict(step_id=k, item=item, old=old, frame=frame, output=output, full=full,
                header=header_raw, payload=payload, candidate=candidate, receipt=receipt.pack(),
                commit=commit, ack=ack.pack(), events=list(self.events),
                decision=staged['unified_commit_sha256'], GPU_produce_wall_ns=gpu_ns,
                STEP_socket_roundtrip_ns=step_ns, COMMIT_socket_roundtrip_ns=commit_ns,
                compute_step_wall_ns=finished-began, compute_elapsed_ns=finished-self.started_ns,
                core_cycles=receipt.compute_cycles, adapter_cycles=receipt.transfer_cycles)
            self.samples.append(record)  # Bounded by this run's 32-step scope.
            record['record_enqueued'] = self.recorder.submit(record)
            return record
        except BaseException:
            self.failed = True
            raise  # No resend, fallback, rollback or next-step publication.

    def close(self, reason=None):
        self.c.unchanged = self.original_unchanged
        close = getattr(self.client, 'close', None)
        if close:
            close()


def transport_residual(pc_roundtrip_ns, ps_residence_ns):
    """Paired-clock duration subtraction, never subtract clock epochs.

    This is transport/protocol/scheduling residual, NOT a PHY-only measurement
    or an identified one-way GPU-to-PL time. Negative observations are invalid.
    """
    value = pc_roundtrip_ns - ps_residence_ns
    return dict(pc_socket_roundtrip_ns=pc_roundtrip_ns, ps_residence_ns=ps_residence_ns,
                transport_residual_ns=value if value >= 0 else None,
                valid=value >= 0, measurement='ROUNDTRIP_MINUS_PS_RESIDENCE',
                includes='TCP/network stack, receive parsing and scheduling outside PS timed residence',
                one_way_time='NOT_IDENTIFIABLE_WITHOUT_CLOCK_ALIGNMENT')

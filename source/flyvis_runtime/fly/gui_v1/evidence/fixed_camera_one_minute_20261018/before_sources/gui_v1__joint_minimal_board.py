"""Python 3.8 PS hot path over the existing service, buffers and DMA driver.

Installed only by the human's new, SHA-bound preparation. No load/reset/allocate.
No filesystem or evidence observer on STEP/COMMIT; same original run/finish
bytecode, MMIO operations, Q24 profile, hardware error checks and RELEASE.
"""
import dataclasses
import json
import socket
import threading
import time
import types

POLICY = 'MINIMAL_COMPUTE_ASYNC_V1'


def install(service, wire, scope, recorder_class):
    d, base = service.driver, service.evidence
    if scope.get('runtime_policy') != POLICY or service.config.get('runtime_policy') != POLICY:
        raise ValueError('MINIMAL_BOARD_SCOPE_REQUIRED')
    if d.requests or d.commits or d.pending is not None or d.poisoned:
        raise ValueError('MINIMAL_BOARD_NOT_UNUSED')
    if getattr(service, '_minimal_runtime', None):
        raise ValueError('MINIMAL_BOARD_ALREADY_INSTALLED')
    limit = scope['max_steps']
    rows, probes, current = [], [], {}
    probe_marker=wire.digest(b'MINIMAL_TRANSPORT_ONLY_PROBE_V1')
    recording_window_closed = threading.Event()

    def save(record):
        recording_window_closed.wait()
        k = record['step_id']
        base.journal.add('minimal_timing_%d.json' % k, json.dumps(record['timing']).encode())
        base.journal.checkpoint('ASYNC_AFTER_ACK')

    recorder = recorder_class(save, capacity=limit)
    service._minimal_runtime = dict(rows=rows, probes=probes, recorder=recorder)

    def alive(self):
        now = time.monotonic()
        if self.poisoned or now >= self.session_deadline or (
                self.compute_deadline is not None and now >= self.compute_deadline):
            raise RuntimeError('MINIMAL_BOARD_STOPPED_OR_DEADLINE')

    def bounds(self, h, payload):
        alive(self)
        if self.requests != self.commits or self.pending is not None or self.requests >= limit:
            raise ValueError('MINIMAL_PREVIOUS_COMMIT_REQUIRED')
        if h.step != self.commits or h.epoch != 0 or h.asid.hex() != self.bound_asid or h.config != wire.CONFIG:
            raise ValueError('MINIMAL_BOARD_STEP_IDENTITY')
        if self.requests == 0 and (h.old_sha.hex() != self.plan['initial_full_sha256']
                or wire.digest(payload[:wire.WORD_BYTES]).hex() != self.plan['initial_H_sha256']):
            raise ValueError('MINIMAL_FROZEN_INITIAL_STATE_MISMATCH')

    d.check_deadline = types.MethodType(alive, d)
    d.runtime_check = types.MethodType(alive, d)
    d.check_bounds = types.MethodType(bounds, d)
    d._event = types.MethodType(lambda self, *a, **kw: None, d)
    d._read = types.MethodType(lambda self, bank, offset: int(getattr(self, bank).read(offset)), d)
    d._write = types.MethodType(lambda self, bank, offset, value: getattr(self, bank).write(offset, value), d)
    # No hot-path evidence callbacks. Preparation/final metadata use base below.
    d.evidence = None
    original_run = d.run.__func__
    namespace = dict(original_run.__globals__)
    def words(raw):
        if len(raw) % 4:
            raise ValueError('unaligned Q24 words')
        values = d.np.frombuffer(raw, dtype='<i4')
        if d.np.any(values < -(1 << 30)) or d.np.any(values >= (1 << 30)):
            raise ValueError('signed31 Q24 range')
    namespace['validate_words'] = words
    adapted = types.FunctionType(original_run.__code__, namespace, original_run.__name__,
                                 original_run.__defaults__, original_run.__closure__)
    d.run = types.MethodType(adapted, d)

    def serve(self, conn, *unused):
        first = True
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        idle = time.monotonic() + 5
        while True:
            if self.finish_requested.is_set():
                return
            if self.state != 'RUNNING':
                raise RuntimeError('MINIMAL_NEURAL_SESSION_STOPPED')
            alive(d)
            if time.monotonic() >= idle:
                raise TimeoutError('MINIMAL_NEURAL_IDLE_TIMEOUT')
            if not self.waiter(conn, .02):
                continue
            self.inflight = True
            try:
                deadline = min(time.monotonic()+5, d.session_deadline)
                h, payload = wire.recv_frame(conn, deadline=deadline)
                received = time.monotonic_ns()
                if hasattr(socket, 'TCP_QUICKACK'):
                    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
                if first:
                    if h.op != wire.HELLO:
                        raise ValueError('MINIMAL_HELLO_REQUIRED')
                    raw = json.dumps(d.attest(h), sort_keys=True).encode()
                    d.bound_asid = h.asid.hex()
                    wire.send_frame(conn, dataclasses.replace(h, op=wire.ATTEST,
                        payload_bytes=len(raw), payload_sha=wire.digest(raw)), raw)
                    first = False
                elif h.op==wire.STEP and h.epoch==1 and h.old_sha==probe_marker:
                    if d.requests or len(probes)>=scope.get('transport_probe_count',0) or len(payload)!=wire.INPUT_BYTES:
                        raise ValueError('MINIMAL_TRANSPORT_PROBE_SCOPE')
                    echo=payload[:wire.WORD_BYTES]
                    reply=dataclasses.replace(h,op=wire.RESULT,payload_bytes=len(echo),payload_sha=wire.digest(echo))
                    ready=time.monotonic_ns()
                    probes.append(dict(index=len(probes),ps_residence_ns=ready-received,
                        input_bytes=len(payload),output_bytes=len(echo),PL_calls=0,GPU_calls=0))
                    wire.send_frame(conn,reply,echo)
                elif h.op == wire.STEP:
                    if d.compute_deadline is None:
                        d.compute_deadline = min(d.session_deadline, time.monotonic()+scope['max_worker_s'])
                    receipt, candidate, timing = d.run(h, payload)
                    ready = time.monotonic_ns()
                    current.clear()
                    current.update(step_id=h.step, request=h.pack()+payload, candidate=candidate,
                        result=receipt.pack(), timing=dict(timing, STEP_ps_residence_ns=ready-received))
                    wire.send_frame(conn, receipt, candidate)
                elif h.op == wire.COMMIT:
                    with self.lock:
                        if self.state != 'RUNNING' or h.step != current.get('step_id'):
                            raise ValueError('MINIMAL_COMMIT_STEP')
                        ack = d.finish(h, True)
                        ready = time.monotonic_ns()
                        current.update(commit=h.pack(), ack=ack.pack())
                        current['timing']['COMMIT_ps_residence_ns'] = ready-received
                        rows.append(dict(step_id=h.step, **current['timing']))
                        wire.send_frame(conn, ack)
                        recorder.submit(dict(current))
                        self.inflight = False
                else:
                    raise ValueError('MINIMAL_ONLY_STEP_COMMIT')
                idle = time.monotonic()+5
            finally:
                self.inflight = False

    service.serve_connection = types.MethodType(serve, service)
    summary={}
    def finish_capture(self, record):
        n=record['completed_steps']
        if d.pending is not None or d.poisoned or d.requests!=d.commits or d.commits!=n or len(rows)!=n:
            raise ValueError('MINIMAL_FINISH_NOT_COMMITTED')
        logging=recorder.close(timeout=2)
        if not logging['closed']:
            raise RuntimeError('MINIMAL_POST_RUN_RECORDER_NOT_CLOSED')
        summary.update(runtime_policy=POLICY,evidence_level='ASYNC_DIAGNOSTICS_NOT_DURABLE_BEFORE_ACK',
            timing_rows=rows,transport_probes=probes,recording=logging,new_loads=0,new_resets=0,new_allocations=0)
        if self.journal.poisoned:
            self.journal.abandon()
        else:
            self.journal.add('MINIMAL_SUMMARY.json',json.dumps(summary).encode())
            self.journal.close('MINIMAL_ASYNC_CAPTURE_NOT_CRASH_DURABLE',requests=n,acks=n,
                completed_steps=n,reason=record['reason'],runtime_policy=POLICY,
                whole_run_acceptance='PENDING')
    base.finish_window=types.MethodType(finish_capture,base)
    original_finish = service._finish
    def finish(self, body):
        # Source is closed and all computation is over before any drain/write.
        recording_window_closed.set()
        d.evidence = base
        result = original_finish(body)
        result['minimal_compute'] = dict(summary)
        return result
    service._finish = types.MethodType(finish, service)
    original_failed_close = getattr(service, '_close_failed_evidence', None)
    if original_failed_close is not None:
        def failed_close(self):
            recording_window_closed.set()
            logging = recorder.close(timeout=2)
            if not logging['closed']:
                self.secondary_errors.append('MINIMAL_ASYNC_RECORDER_CLOSE_PENDING')
                return  # Never close a journal while its recorder is using it.
            original_failed_close()
        service._close_failed_evidence = types.MethodType(failed_close, service)
    service.config['minimal_compute_installed'] = True
    return service._minimal_runtime

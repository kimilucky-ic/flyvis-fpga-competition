"""Instrumented single-request API; importing never accesses a board.

This module does not provide a load/program command. The first load needs a
separately reviewed one-step launcher and exact-operation user authorization.
No host numerical computation or state COMMIT is implemented here.
"""
import json
import math
import os
from pathlib import Path
import time

import numpy as np
from flyvis_v1_driver import (
    FlyVisBoardFault, STATE_WORDS, OUTPUT_WORDS, CTRL, AP_RETURN,
    REQUEST_LO, REQUEST_HI, RESULT_LO, RESULT_HI, AP_START, AP_DONE,
    buffer_address, sha_bytes, sync_from_device, sync_to_device,
    validate_q22_sign_extension,
)

AP_IDLE = 1 << 2
AUTO_RESTART = 1 << 7
REGISTERS = {'CTRL': 0, 'GIER': 4, 'IP_IER': 8, 'IP_ISR': 12,
             'ap_return': 16, 'request_low': 24, 'request_high': 28,
             'result_low': 36, 'result_high': 40}
# Module ownership keeps buffers alive even after a notebook drops its driver.
# Do not clear this list until an explicitly authorized recovery confirms that
# the PL master is stopped. A process exit can also release these allocations.
PINNED_UNCERTAIN_BUFFERS = []


class EvidenceStepDriver:
    def init__(self, overlay, mmio, allocate_fn, evidence_dir,
                 timeout_seconds=30.0, memory_limit=0x40000000):
        if not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 30:
            raise FlyVisBoardFault('Timeout must be finite and within 0..30 seconds')
        self.overlay = overlay
        self.mmio = mmio
        self.allocate = allocate_fn
        self.directory = Path(evidence_dir)
        self.directory.mkdir(parents=True, exist_ok=False)
        self.timeout_seconds = timeout_seconds
        self.memory_limit = memory_limit
        self.failed = False
        self.used = False
        self.trace = (self.directory / 'register_trace.jsonl').open('x', encoding='utf-8')
        self.started_at = time.monotonic()

    def event(self, action, **fields):
        row = {'elapsed_s': time.monotonic() - self.started_at,
               'action': action, **fields}
        self.trace.write(json.dumps(row, sort_keys=True) + '\n')
        self.trace.flush()
        os.fsync(self.trace.fileno())

    def read(self, offset):
        value = int(self.mmio.read(offset))
        self.event('mmio_read', offset=offset, value=value, hex='0x{:08x}'.format(value))
        return value

    def write(self, offset, value):
        # Persist intent before a write: a bus exception cannot prove that the
        # slave did not receive the command.
        self.event('mmio_write_intent', offset=offset, value=value)
        self.mmio.write(offset, value)
        self.event('mmio_write_returned', offset=offset, value=value)

    def snapshot(self, label):
        registers = {name: self.read(offset) for name, offset in REGISTERS.items()}
        self.event('register_snapshot', label=label, registers=registers,
                   ctrl_done_clear_on_read=True)
        return registers

    def save_report(self, report):
        with (self.directory / 'step_report.json').open('x', encoding='utf-8') as stream:
            json.dump(report, stream, indent=2)
            stream.write('\n')

    def step(self, request_q22_i32):
        if self.used or self.failed:
            raise FlyVisBoardFault('This first-step driver permits exactly one attempt; no retry')
        self.used = True
        raw = np.asarray(request_q22_i32)
        if raw.dtype.kind not in ('i', 'u') or raw.shape != (STATE_WORDS,):
            raise FlyVisBoardFault('Request must be an integer array of exactly 1498 words')
        if np.any(raw < -(1 << 28)) or np.any(raw > (1 << 28) - 1):
            raise FlyVisBoardFault('Request exceeds signed 29-bit Q22 state range')
        request = raw.astype('<i4', copy=True)
        validate_q22_sign_extension(request)
        request_bytes = request.tobytes()
        (self.directory / 'request_i32le.bin').write_bytes(request_bytes)
        report = {'status': 'FAIL_CLOSED', 'compute_owner': 'FPGA_PL_HLS',
                  'evidence_level': 'DRIVER_TRACE_EXECUTION_ENVIRONMENT_REQUIRES_INDEPENDENT_ATTESTATION',
                  'python_fallback': False, 'committed': False,
                  'state_semantics': 'stateless STEP; explicit old_H; candidate only',
                  'request_sha256': sha_bytes(request_bytes),
                  'completed': False, 'buffers_pinned': False,
                  'board_evidence': 'Not a PASS until run on the physical board and independently compared'}
        buffers = []
        may_be_running = False
        completion_safe = False
        launch_time = None
        try:
            if not self.overlay.is_loaded():
                raise FlyVisBoardFault('PYNQ overlay bookkeeping does not match this object')
            report['registers_before'] = self.snapshot('before')
            before = report['registers_before']['CTRL']
            if not before & AP_IDLE or before & (AP_START | AUTO_RESTART):
                raise FlyVisBoardFault('HLS is not idle, or start/auto-restart is active')
            # Snapshot consumes any stale DONE. Verify it stays clear before
            # exposing a new request to the core.
            cleared = self.read(CTRL)
            if cleared & (AP_DONE | AP_START | AUTO_RESTART) or not cleared & AP_IDLE:
                raise FlyVisBoardFault('Unexpected HLS state after stale-DONE read')
            inp = self.allocate(shape=(STATE_WORDS,), dtype=np.dtype('<i4'))
            buffers.append(inp)
            out = self.allocate(shape=(OUTPUT_WORDS,), dtype=np.dtype('<i4'))
            buffers.append(out)
            inp[:] = request
            out[:] = 0x5A5A5A5A
            in_addr, out_addr = buffer_address(inp), buffer_address(out)
            for address, size in ((in_addr, STATE_WORDS * 4), (out_addr, OUTPUT_WORDS * 4)):
                if address < 0x100000 or address % 4 or address + size > self.memory_limit:
                    raise FlyVisBoardFault('Allocated buffer lies outside reviewed HP0 DDR range')
            if max(in_addr, out_addr) < min(in_addr + STATE_WORDS * 4, out_addr + OUTPUT_WORDS * 4):
                raise FlyVisBoardFault('Input and output allocations overlap')
            sync_to_device(inp)
            sync_to_device(out)
            report['buffers'] = {'input_address': in_addr, 'input_bytes': STATE_WORDS * 4,
                                 'output_address': out_addr, 'output_bytes': OUTPUT_WORDS * 4}
            self.event('cache_flushed', **report['buffers'])
            for offset, value in ((REQUEST_LO, in_addr), (REQUEST_HI, 0),
                                  (RESULT_LO, out_addr), (RESULT_HI, 0)):
                self.write(offset, value)
                if self.read(offset) != value:
                    raise FlyVisBoardFault('HLS pointer register did not read back exactly')
            may_be_running = True
            launch_time = time.monotonic()
            self.write(CTRL, AP_START)
            polls = 0
            while True:
                control = self.read(CTRL)
                polls += 1
                if control & AUTO_RESTART:
                    raise FlyVisBoardFault('Auto-restart unexpectedly active')
                if control & AP_DONE:
                    report['completion_ctrl'] = control
                    break
                if time.monotonic() - launch_time >= self.timeout_seconds:
                    raise FlyVisBoardFault('AP_DONE timeout; master completion is uncertain')
                time.sleep(0.0005)
            report['host_completion_elapsed_s'] = time.monotonic() - launch_time
            report['poll_count'] = polls
            report['timing_scope'] = 'Host start/write and DONE polling, including evidence I/O; not cycle latency'
            report['registers_after'] = self.snapshot('after_done')
            final_ctrl = report['registers_after']['CTRL']
            if not final_ctrl & AP_IDLE or final_ctrl & (AP_START | AUTO_RESTART):
                raise FlyVisBoardFault('DONE observed but core did not return to idle')
            completion_safe = True
            sync_from_device(out)
            candidate = np.asarray(out, dtype='<i4').copy()
            candidate_bytes = candidate.tobytes()
            (self.directory / 'PL_candidate_i32le.bin').write_bytes(candidate_bytes)
            report['pl_output_sha256'] = sha_bytes(candidate_bytes)
            report['hls_status'] = report['registers_after']['ap_return']
            if report['hls_status'] != 0:
                raise FlyVisBoardFault('HLS numeric/input status is nonzero: {}'.format(report['hls_status']))
            validate_q22_sign_extension(candidate)
            if np.any(candidate == 0x5A5A5A5A):
                raise FlyVisBoardFault('PL output sentinel remained untouched')
            report['completed'] = True
            report['status'] = 'PL_STEP_COMPLETED_ORACLE_COMPARISON_PENDING'
            self.event('step_completed', output_sha256=report['pl_output_sha256'])
            self.save_report(report)
            return {'candidate_h_q22_i32': candidate, 'report': report}
        except BaseException as exc:
            self.failed = True
            report['error'] = '{}: {}'.format(type(exc).__name__, exc)
            if launch_time is not None:
                report['host_attempt_elapsed_s'] = time.monotonic() - launch_time
            if may_be_running and not completion_safe:
                PINNED_UNCERTAIN_BUFFERS.extend(buffers)
                report['buffers_pinned'] = True
                report['recovery'] = 'Keep this process/kernel alive. No retry/free/reset/reload; obtain exact recovery authorization.'
            self.event('fail_closed', error=report['error'], buffers_pinned=report['buffers_pinned'])
            self.save_report(report)
            raise
        finally:
            if not may_be_running or completion_safe:
                for buffer in buffers:
                    free = getattr(buffer, 'freebuffer', None)
                    if callable(free):
                        free()
                    else:
                        close = getattr(buffer, 'close', None)
                        if callable(close):
                            close()
                self.event('buffers_released_after_safe_completion_or_before_start')
            self.trace.close()

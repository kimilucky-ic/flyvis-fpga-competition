"""Bounded source-close/finish sequence. No device, socket or neural computation.

The board's existing 5s idle deadline stays unchanged. The anchor is the
Windows/WSL worker's last neural request START, conservatively earlier than the
board's reply and next idle window; it is never compared to another host clock.
"""
import math
import time

from live_protocol import load, require

BOARD_IDLE_S = 5.0
SOURCE_CLOSE_WITHIN_S = 2.0
FINISH_SEND_WITHIN_S = 3.0


class FinishWindowBudget:
    def init__(self, *, clock=time.monotonic, sleep=time.sleep):
        self.clock, self.sleep = clock, sleep
        self.exchange_at = None
        self.source_closed_at = self.finish_started_at = self.finish_returned_at = None

    def exchange_started(self):
        self.exchange_at = self.clock()

    def elapsed(self):
        require(self.exchange_at is not None, 'JOINT_FINISH_NO_NEURAL_EXCHANGE_ANCHOR')
        elapsed = self.clock() - self.exchange_at
        require(math.isfinite(elapsed) and elapsed >= 0, 'JOINT_FINISH_CLOCK')
        return elapsed

    def wait_source_closed(self, path, run_id):
        while True:
            remaining = SOURCE_CLOSE_WITHIN_S - self.elapsed()
            require(remaining > 0, 'JOINT_SOURCE_CLOSE_IDLE_BUDGET_EXCEEDED')
            if path.exists():
                closed = load(path)
                require(closed.get('run_id') == run_id and closed.get('closed') is True
                        and 'error' in closed and not closed['error'], 'JOINT_SOURCE_CLOSE_FAILED')
                require(self.elapsed() < SOURCE_CLOSE_WITHIN_S, 'JOINT_SOURCE_CLOSE_IDLE_BUDGET_EXCEEDED')
                self.source_closed_at = self.clock()
                return closed
            self.sleep(min(.02, remaining))

    def require_send_margin(self):
        require(self.elapsed() < FINISH_SEND_WITHIN_S, 'JOINT_FINISH_SEND_IDLE_BUDGET_EXCEEDED')

    def summary(self):
        return dict(clock='worker_monotonic_only', anchor_kind='LAST_NEURAL_REQUEST_START_BEFORE_REPLY',
            board_idle_s=BOARD_IDLE_S, source_close_within_s=SOURCE_CLOSE_WITHIN_S,
            finish_send_within_s=FINISH_SEND_WITHIN_S, minimum_send_margin_s=BOARD_IDLE_S-FINISH_SEND_WITHIN_S,
            exchange_started_at=self.exchange_at, source_closed_at=self.source_closed_at,
            finish_started_at=self.finish_started_at, finish_returned_at=self.finish_returned_at,
            scope='HOST_ADMISSION_BUDGET_NOT_PROOF_OF_LAN_OR_BOARD_TIMING')


def finish_camera_window(budget, closed_path, hub, barrier, evidence, control, reason):
    """No retry. Delayed close/persistence may fail; they cannot extend idle time."""
    require(barrier.phase == 'READY' and barrier.pending is None, 'JOINT_FINISH_INFLIGHT')
    require(hub.error is None, 'JOINT_FINISH_REVOKED')
    hub.begin_stop()
    closed = budget.wait_source_closed(closed_path, hub.scope['run_id'])
    evidence.json('source_closed.json', closed)
    # Includes everything since COMMIT request start: ACK wait, decode, saved
    # snapshot, bridge polling, camera close and persistence above.
    budget.require_send_margin()
    budget.finish_started_at = budget.clock()
    result = control.finish(hub.committed, barrier._visible[2].hex(), barrier._visible[3].hex(), reason)
    budget.finish_returned_at = budget.clock()
    return result

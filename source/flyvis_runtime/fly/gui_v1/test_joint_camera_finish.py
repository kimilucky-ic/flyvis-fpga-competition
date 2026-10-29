"""Virtual-clock finish deadlines + delivered Line 7 in-memory service. No devices."""
import importlib.util
import json
from pathlib import Path
import socket
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import uuid

from live_protocol import HERE
from joint_camera_finish import FinishWindowBudget, finish_camera_window
from joint_camera_runtime import JointCameraHub

OUT = HERE / 'evidence/camera_joint_service_review_20261016'
LINE7 = HERE.parent.parent / 'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/camera_joint_service_20261016'


class Clock:
    def init__(self): self.now = 100.0
    def read(self): return self.now
    def sleep(self, seconds): self.now += seconds


class DelayedFile:
    def init__(self, path, clock, visible_at): self.path, self.clock, self.visible_at = path, clock, visible_at
    def exists(self): return self.path.exists() and self.clock.now >= self.visible_at
    def __fspath__(self): return str(self.path)


class FinishBudgetTests(unittest.TestCase):
    def setUp(self):
        self.root = OUT / 'finish_cases' / uuid.uuid4().hex
        self.root.mkdir(parents=True)
        self.clock = Clock()
        self.budget = FinishWindowBudget(clock=self.clock.read, sleep=self.clock.sleep)
        self.budget.exchange_started()
        self.hub = JointCameraHub(dict(run_id='CPU_CURRENT_RUN', session_id='CPU_SESSION'), SimpleNamespace())
        self.hub.committed = 1
        self.barrier = SimpleNamespace(phase='READY', pending=None, _visible=(None, None, b'c'*32, b't'*16))
        self.evidence = SimpleNamespace(json=Mock())
        self.control = SimpleNamespace(finish=Mock(return_value=dict(state='FINISHED_PENDING_AUDIT')))
        self.closed_path = self.root / 'camera_capture.json'
        self.proof()

    def proof(self, **overrides):
        value = dict(run_id='CPU_CURRENT_RUN', closed=True, error=None)
        value.update(overrides)
        self.closed_path.write_text(json.dumps(value), encoding='utf-8')

    def finish(self, path=None):
        return finish_camera_window(self.budget, path or self.closed_path, self.hub, self.barrier,
                                    self.evidence, self.control, 'CAPTURE_WINDOW_COMPLETE')

    def test_closed_source_finishes_once_with_two_second_send_margin(self):
        self.clock.now += .4
        self.assertEqual(self.finish()['state'], 'FINISHED_PENDING_AUDIT')
        self.control.finish.assert_called_once_with(1, (b'c'*32).hex(), (b't'*16).hex(), 'CAPTURE_WINDOW_COMPLETE')
        self.assertTrue(self.hub.stopping)
        self.assertEqual(self.budget.summary()['minimum_send_margin_s'], 2.0)

    def test_close_confirmation_at_1_9_seconds_is_accepted(self):
        self.finish(DelayedFile(self.closed_path, self.clock, 101.9))
        self.assertLess(self.budget.source_closed_at - self.budget.exchange_at, 2)
        self.control.finish.assert_called_once()

    def test_two_second_close_boundary_fails_without_network_request(self):
        self.clock.now = 102
        with self.assertRaisesRegex(ValueError, 'SOURCE_CLOSE_IDLE_BUDGET'):
            self.finish()
        self.control.finish.assert_not_called()

    def test_missing_confirmation_does_not_wait_the_old_five_seconds(self):
        with self.assertRaisesRegex(ValueError, 'SOURCE_CLOSE_IDLE_BUDGET'):
            self.finish(DelayedFile(self.closed_path, self.clock, 105))
        self.assertAlmostEqual(self.clock.now, 102)
        self.control.finish.assert_not_called()

    def test_decode_and_saved_snapshot_time_is_already_in_budget(self):
        self.clock.now += 2.1
        with self.assertRaisesRegex(ValueError, 'SOURCE_CLOSE_IDLE_BUDGET'):
            self.finish()
        self.control.finish.assert_not_called()

    def test_slow_source_proof_persistence_cannot_start_late_finish(self):
        self.evidence.json.side_effect = lambda *args: self.clock.sleep(3)
        with self.assertRaisesRegex(ValueError, 'FINISH_SEND_IDLE_BUDGET'):
            self.finish()
        self.control.finish.assert_not_called()

    def test_exact_three_second_send_boundary_is_rejected(self):
        self.clock.now += 3
        with self.assertRaisesRegex(ValueError, 'FINISH_SEND_IDLE_BUDGET'):
            self.budget.require_send_margin()

    def test_old_run_false_closed_or_capture_error_never_finish(self):
        for update in (dict(run_id='OLD_RUN'), dict(closed=False), dict(error='CPU_CAPTURE_FAILED')):
            with self.subTest(update=update):
                value = dict(run_id='CPU_CURRENT_RUN', closed=True, error=None)
                value.update(update)
                self.closed_path.write_text(json.dumps(value), encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'SOURCE_CLOSE_FAILED'): self.finish()
                self.control.finish.assert_not_called()

    def test_pending_transaction_and_revoked_run_are_not_normal_finish(self):
        self.barrier.pending = object()
        with self.assertRaisesRegex(ValueError, 'FINISH_INFLIGHT'): self.finish()
        self.barrier.pending = None
        self.hub.revoke('CPU_WRONG_ACK')
        with self.assertRaisesRegex(ValueError, 'FINISH_REVOKED'): self.finish()
        self.control.finish.assert_not_called()

    def test_new_exchange_reanchors_and_summary_uses_one_host_clock(self):
        self.clock.now += 4
        self.budget.exchange_started()
        self.clock.now += .1
        self.finish()
        self.assertEqual(self.budget.summary()['exchange_started_at'], 104)
        self.assertEqual(self.budget.summary()['clock'], 'worker_monotonic_only')

    def test_missing_exchange_anchor_or_reversed_clock_is_rejected(self):
        self.budget.exchange_at = None
        with self.assertRaisesRegex(ValueError, 'NO_NEURAL_EXCHANGE_ANCHOR'): self.finish()
        self.budget.exchange_at = self.clock.now + 1
        with self.assertRaisesRegex(ValueError, 'FINISH_CLOCK'): self.finish()
        self.control.finish.assert_not_called()


class DeliveredServiceFinishTests(FinishBudgetTests):
    # Deliberately select only this class's two integration methods in the runner;
    # inherited virtual-clock checks above are not counted twice.
    def harness(self):
        import sys
        sys.path.insert(0, str(LINE7))
        spec = importlib.util.spec_from_file_location('line2_finish_line7_fixture', LINE7 / 'test_camera_service.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.stack = __import__('contextlib').ExitStack()
        self.stack.enter_context(patch.object(socket, 'socket', side_effect=AssertionError('NO_REAL_SOCKET')))
        self.stack.enter_context(patch.object(socket, 'create_connection', side_effect=AssertionError('NO_REAL_CONNECTION')))
        self.addCleanup(self.stack.close)
        h = module.Harness(self.root / 'line7')
        self.addCleanup(h.close)
        h.start(); h.step()
        self.hub = JointCameraHub(dict(run_id=h.c['run_id'], session_id='CPU_SESSION'), SimpleNamespace())
        self.hub.committed = h.d.commits
        self.barrier._visible = (None, None, h.parent, h.txn)
        self.closed_path.write_text(json.dumps(dict(run_id=h.c['run_id'], closed=True, error=None)), encoding='utf-8')
        self.control = h.control
        return h

    def test_real_control_adapter_and_delivered_service_finish_within_budget(self):
        h = self.harness()
        result = self.finish()
        self.assertEqual(result['state'], 'FINISHED_PENDING_AUDIT')
        self.assertEqual(result['requests'], 1)
        self.assertEqual(h.d.writes, [('reg', 0x10, 2)])
        self.assertEqual(sum(path == '/finish_window' for _, path in h.calls), 1)

    def test_late_close_is_rejected_before_delivered_service_receives_finish(self):
        h = self.harness()
        self.clock.now += 2.01
        with self.assertRaisesRegex(ValueError, 'SOURCE_CLOSE_IDLE_BUDGET'): self.finish()
        self.assertEqual(sum(path == '/finish_window' for _, path in h.calls), 0)


def suite():
    cases = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(FinishBudgetTests))
    cases.addTests(DeliveredServiceFinishTests(name) for name in DeliveredServiceFinishTests.__dict__ if name.startswith('test_'))
    return cases


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(suite())
    raise SystemExit(not result.wasSuccessful())

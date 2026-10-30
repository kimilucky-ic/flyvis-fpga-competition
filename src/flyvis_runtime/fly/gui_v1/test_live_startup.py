"""Bounded startup reporting tests; no camera, GPU, renderer, or neural calls."""
import json
import sys
import time
import types
import unittest
from unittest.mock import patch

from test_live_protocol import Protocol
from live_protocol import HERE, load, write
from live_worker import run


class Startup(unittest.TestCase):
    setUp=Protocol.setUp
    tearDown=Protocol.tearDown
    heartbeat=Protocol.heartbeat

    def update(self,**fields):
        p=self.root/'heartbeat.json';value=load(p);value.update(fields);write(p,value)

    def test_busy_timeout_is_terminal_and_not_connected(self):
        self.update(state='FAILED',device=None,error={'code':'GPU_BUSY_TIMEOUT','message':'No other process interrupted'})
        c=self.a.capabilities()
        self.assertEqual(c['status'],'NOT_CONNECTED')
        self.assertEqual(c['service']['state'],'FAILED')
        self.assertTrue(c['service']['terminal'])
        self.assertIn('超时',c['service']['message'])

    def test_waiting_and_preload_are_distinct(self):
        self.update(state='PRELOADING',device=None,phase='WAITING_FOR_SHARED_GPU')
        self.assertEqual(self.a.capabilities()['service']['state'],'WAITING_FOR_GPU')
        self.update(phase='PRELOADING_ORIGINAL_MODEL')
        self.assertEqual(self.a.capabilities()['service']['state'],'PRELOADING')

    def test_old_stopped_is_not_a_startup_spinner(self):
        p=self.root/'heartbeat.json';beat=load(p);beat.update(state='STOPPED',device=None);del beat['evidence_scope'];write(p,beat)
        self.assertEqual(self.a.capabilities()['service']['state'],'STOPPED')

    def test_cross_session_and_stale_ready_are_rejected(self):
        self.update(session_id='other')
        self.assertEqual(self.a.capabilities()['service']['state'],'DISCONNECTED')
        self.heartbeat(age=20)
        self.assertEqual(self.a.capabilities()['service']['state'],'DISCONNECTED')

    def test_exit_record_overrides_alive_but_not_ready_heartbeat(self):
        self.update(state='PRELOADING',device=None)
        write(self.root/'worker_exit.json',{'session_id':self.session['session_id'],'exit_code':1})
        self.assertEqual(self.a.capabilities()['service']['state'],'FAILED')

    def test_ready_and_offline_still_work(self):
        self.assertEqual(self.a.capabilities()['service']['state'],'READY')
        from live_jobs import LiveGPUAdapter
        self.assertEqual(LiveGPUAdapter(registry=self.registry).capabilities()['service']['state'],'NOT_STARTED')

    def test_worker_failure_preserves_error_and_scope(self):
        class BusyError(RuntimeError):code='GPU_BUSY_TIMEOUT'
        class Lease:
            def acquire(self):raise BusyError('No other process interrupted')
        runner=types.SimpleNamespace(Lease=Lease,own_path=lambda *parts:self.root.joinpath(*parts))
        with patch('live_worker.Registry',return_value=self.registry),patch('live_worker.import_file',return_value=runner),patch('live_worker.validate_scope'):
            with self.assertRaises(BusyError):run(self.root/'session.json')
        beat=load(self.root/'heartbeat.json')
        self.assertEqual(beat['state'],'FAILED')
        self.assertEqual(beat['error']['code'],'GPU_BUSY_TIMEOUT')
        self.assertEqual(beat['evidence_scope'],'CPU_PROTOCOL_TEST_ONLY')
        self.assertFalse(load(self.root/'worker_shutdown.json')['CUDA_synchronized'])


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Startup))
    report=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),
                status='PASS_CPU_STARTUP_REPORTING' if result.wasSuccessful() else 'FAIL',
                device_imports=[name for name in ('torch','flyvis','cv2') if name in sys.modules],
                new_neural_steps=0,camera_operations=0,board_operations=0)
    write(HERE/'evidence/startup_status_20261015/tests.json',report)
    print(json.dumps(report));sys.exit(0 if result.wasSuccessful() and not report['device_imports'] else 1)

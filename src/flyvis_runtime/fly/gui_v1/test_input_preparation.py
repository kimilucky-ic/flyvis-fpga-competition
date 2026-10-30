"""CPU lifecycle/identity fixtures, no actual child, camera or neural execution."""
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock,patch
from types import SimpleNamespace
from input_preparation import PreparedConverter,wait_for_stream_endpoint
from live_protocol import HERE,load,write


class Preparation(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=HERE/'runtime');self.root=Path(self.temp.name)
        self.session=dict(session_id='CPU_PREPARATION_TEST',stream_enabled=True)
        write(self.root/'session.json',self.session)
        write(self.root/'controller.json',dict(session_id=self.session['session_id'],unix_time=time.time()))
        self.process=Mock(pid=12345);self.process.poll.return_value=None;self.process.wait.return_value=0
    def tearDown(self):
        self.assertTrue(self.root.resolve().is_relative_to((HERE/'runtime').resolve()));self.temp.cleanup()
    def test_child_is_CPU_only_and_has_no_endpoint_or_input(self):
        with patch('input_preparation.validate_scope'),patch('input_preparation.subprocess.Popen',return_value=self.process) as spawn:
            owner=PreparedConverter(self.root,self.session).start()
            try:
                self.assertEqual(spawn.call_args.kwargs['env']['CUDA_VISIBLE_DEVICES'],'-1')
                self.assertFalse((self.root/'stream_endpoint.json').exists())
                owner.attach()
                with self.assertRaisesRegex(ValueError,'ALREADY_ATTACHED'):owner.attach()
            finally:owner.close();owner.close()
        self.process.wait.assert_called_once();self.assertTrue(load(self.root/'converter_shutdown.json')['exit_code']==0)
        self.assertFalse(load(self.root/'converter_preparation.json')['camera_opened'])
    def test_early_exit_cannot_be_adopted(self):
        with patch('input_preparation.validate_scope'),patch('input_preparation.subprocess.Popen',return_value=self.process):
            owner=PreparedConverter(self.root,self.session).start();self.process.poll.return_value=1
            try:
                with self.assertRaisesRegex(ValueError,'EXITED'):owner.attach()
            finally:owner.close()
    def test_missing_auth_prevents_child_start(self):
        with patch('input_preparation.subprocess.Popen') as spawn:
            with self.assertRaises(ValueError):PreparedConverter(self.root,self.session).start()
            spawn.assert_not_called()
    def test_same_session_endpoint_can_be_attached(self):
        write(self.root/'stream_endpoint.json',dict(session_id=self.session['session_id'],token='CPU_FIXTURE',port=1))
        with patch('input_preparation.validate_scope'):
            self.assertEqual(wait_for_stream_endpoint(self.root,self.session)['session_id'],self.session['session_id'])
    def test_wrong_session_endpoint_is_rejected(self):
        write(self.root/'stream_endpoint.json',dict(session_id='other'))
        with patch('input_preparation.validate_scope'):
            with self.assertRaisesRegex(ValueError,'ENDPOINT_SESSION'):wait_for_stream_endpoint(self.root,self.session)
    def test_stop_while_model_is_loading_does_not_wait_for_endpoint(self):
        write(self.root/'CONVERTER_STOP_REQUEST.json',{})
        with patch('input_preparation.validate_scope'):
            with self.assertRaisesRegex(ValueError,'STOP_REQUESTED'):wait_for_stream_endpoint(self.root,self.session)
    def test_lost_controller_or_changed_session_cannot_publish_readiness(self):
        with patch('input_preparation.validate_scope'):
            write(self.root/'controller.json',dict(session_id=self.session['session_id'],unix_time=time.time()-20))
            with self.assertRaisesRegex(ValueError,'CONTROLLER_LOST'):wait_for_stream_endpoint(self.root,self.session)
            write(self.root/'session.json',dict(session_id='other'))
            with self.assertRaisesRegex(ValueError,'SESSION_CHANGED'):wait_for_stream_endpoint(self.root,self.session)
    def test_endpoint_timeout_is_bounded(self):
        with patch('input_preparation.validate_scope'):
            with self.assertRaisesRegex(ValueError,'ENDPOINT_TIMEOUT'):wait_for_stream_endpoint(self.root,self.session,timeout_s=0)
    def test_device_libraries_not_imported(self):
        self.assertFalse(set(('torch','flyvis','cv2'))&set(sys.modules))


class WorkerFailure(unittest.TestCase):
    def test_model_construction_failure_closes_parallel_child_after_fake_cuda_ack(self):
        from contextlib import ExitStack
        import live_worker
        from test_live_protocol import Protocol
        p=Protocol();p.setUp();events=[]
        try:
            p.session['stream_enabled']=True;write(p.root/'session.json',p.session)
            write(p.root/'controller.json',dict(session_id=p.session['session_id'],unix_time=time.time()))
            class Lease:
                def acquire(self):return SimpleNamespace(close=lambda:None),0
            runner=SimpleNamespace(Lease=Lease,own_path=lambda *parts:p.root.joinpath(*parts))
            class Owner:
                def init__(self,*a):pass
                def start(self):events.append('CPU_PREPARE_START');return self
                def close(self):events.append('CPU_PREPARE_CLOSE')
            class Full:
                def init__(self,*a,**k):
                    events.append('CPU_FAKE_MODEL_CONSTRUCT');raise ValueError('CPU_MODEL_CONSTRUCT_FAILED')
            fake_torch=SimpleNamespace(set_num_threads=lambda *a:None,use_deterministic_algorithms=lambda *a:None,
                cuda=SimpleNamespace(is_available=lambda:True,synchronize=lambda:events.append('CPU_FAKE_CUDA_ACK')),
                backends=SimpleNamespace(cuda=SimpleNamespace(matmul=SimpleNamespace()),cudnn=SimpleNamespace()))
            def scoped_path(value,*args):
                text=str(value)
                return p.root/'tmp'/text[5:] if text.startswith('/tmp/') else p.root/'tmp' if text=='/tmp' else Path(value,*args)
            with ExitStack() as stack:
                stack.enter_context(patch.dict(sys.modules,{'torch':fake_torch}))
                stack.enter_context(patch.dict(live_worker.os.environ,{},clear=False))
                stack.enter_context(patch('live_worker.Path',side_effect=scoped_path))
                stack.enter_context(patch('live_worker.validate_scope'))
                stack.enter_context(patch('live_worker.Registry',return_value=p.registry))
                stack.enter_context(patch('live_worker.import_file',side_effect=lambda name,path:runner if 'runner_lease' in name else SimpleNamespace(FullNetworkOracle=Full)))
                stack.enter_context(patch('input_preparation.PreparedConverter',Owner))
                stack.enter_context(patch('static_connectome.prepare_static_connectome',return_value={}))
                stack.enter_context(patch('live_worker.importlib.import_module',return_value=None))
                with self.assertRaisesRegex(ValueError,'CPU_MODEL_CONSTRUCT_FAILED'):live_worker.run(p.root/'session.json')
            self.assertEqual(events,['CPU_PREPARE_START','CPU_FAKE_MODEL_CONSTRUCT','CPU_FAKE_CUDA_ACK','CPU_PREPARE_CLOSE'])
            self.assertEqual(load(p.root/'heartbeat.json')['state'],'FAILED')
            self.assertEqual(load(p.root/'worker_error.json')['message'],'CPU_MODEL_CONSTRUCT_FAILED')
            self.assertNotIn('torch',sys.modules)
        finally:p.tearDown()

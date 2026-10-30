"""CPU-only recording gate checks. No camera, GPU, board, socket, or GUI launch."""
import contextlib, json, unittest, uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from joint_camera_bridge import JointCameraBridge

class RecordingGateTests(unittest.TestCase):
    @contextlib.contextmanager
    def case(self):
        root=Path(__file__).parent/'evidence/joint32_profile_20261016/cpu_cases'/uuid.uuid4().hex
        root.mkdir(parents=True,exist_ok=False)
        yield root
    def fixture(self, root):
        b=JointCameraBridge();b.root=Path(root);b.path=b.root/'session.json'
        b.scope=dict(run_id='cpu_run',session_id='CPU_SESSION',camera_id=0,recording_required_before_camera=True)
        b.geometry={};b.connect=Mock();b.client=Mock();b.client.call.return_value={}
        return b,dict(run_id='cpu_run',session_id='CPU_SESSION')

    def test_missing_recorder_blocks_before_camera_rpc(self):
        with self.case() as root:
            b,body=self.fixture(root)
            with self.assertRaisesRegex(ValueError,'RECORDING_MUST_START_FIRST'):b.start(body)
            b.client.call.assert_not_called();self.assertIsNone(b.control)
            self.assertFalse((b.root/'CAMERA_START_REQUEST.json').exists())

    def test_ready_receipt_is_persisted_before_start_rpc(self):
        with self.case() as root:
            b,body=self.fixture(root)
            body['recording_ready']=dict(schema='flyvis-joint-recorder-ready/v1',recorder_id=str(uuid.uuid4()),
                mime_type='video/webm;codecs=vp8',width=1920,height=1080,capture_fps=15,
                browser_started_ms=10.,prestart_frame_requested=True)
            def rpc(method, identity):
                self.assertEqual(method,'start');self.assertEqual(set(identity),{'run_id','session_id','camera_id'})
                ready=json.loads((b.root/'RECORDING_READY.json').read_text(encoding='utf8'))
                start=json.loads((b.root/'CAMERA_START_REQUEST.json').read_text(encoding='utf8'))
                self.assertEqual(ready['run_id'],'cpu_run')
                self.assertLess(ready['received_windows_monotonic_ns'],start['windows_monotonic_ns'])
                self.assertEqual(len(start['recording_ready_sha256']),64)
                return {}
            b.client.call.side_effect=rpc
            with patch('joint_camera_bridge.threading.Thread',return_value=SimpleNamespace(start=lambda:None)):
                b.start(body)
            b.client.call.assert_called_once()
            with self.assertRaisesRegex(ValueError,'START_CONSUMED'):b.start(body)

if __name__=='__main__':unittest.main()

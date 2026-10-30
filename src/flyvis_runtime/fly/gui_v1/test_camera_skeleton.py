"""Small capture lifecycle checks; fake camera is confined to this CPU test."""
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
from live_protocol import load
from stream_bridge import StreamBridge
from camera_pipeline import capture


class CameraConsumerTests(unittest.TestCase):
    def exercise(self, failure=None):
        with tempfile.TemporaryDirectory() as directory:
            b=StreamBridge.__new__(StreamBridge)
            b.root=Path(directory);b.control=dict(camera_id=0,session_id='CPU_TEST',run_id='CPU_CAPTURE_TEST')
            b.stop_event=threading.Event();b.error=None;b.sequence=0;b.camera_info=None;b.capture_closed=False
            b.status=lambda:dict(renderer_ready=True)
            camera=SimpleNamespace(closed=False,cv2=SimpleNamespace(imencode=lambda *a:(True,np.array([1,2],dtype=np.uint8))))
            camera.close=lambda:setattr(camera,'closed',True)
            camera.status=lambda:dict(backend='TEST_ONLY',state='closed' if camera.closed else 'open')
            frame=SimpleNamespace(bgr=np.zeros((480,640,3),dtype=np.uint8),sequence=0,
                                  received_monotonic_ns=12345,received_utc='CPU_TEST_TIMESTAMP',read_duration_s=.02)
            accepted=[]
            def push(png,metadata,stamp):
                if failure=='input':raise ValueError('TEST_INPUT_REJECTED')
                accepted.append((png,metadata,stamp));b.sequence+=1;b.stop_event.set()
            b.push=push
            with patch.object(capture,'open_camera',side_effect=ValueError('TEST_CAMERA_UNAVAILABLE') if failure=='open' else None,return_value=camera),patch.object(capture,'read_frame',return_value=frame):
                b.capture()
            evidence=load(b.root/'camera_capture.json')
            self.assertTrue(b.capture_closed);self.assertEqual(evidence['source_kind'],'real_windows_camera')
            self.assertFalse(evidence['PL_execution'])
            if failure:
                self.assertEqual(accepted,[]);self.assertIn('TEST_',evidence['error'])
            else:
                self.assertTrue(camera.closed);self.assertEqual(accepted[0][2],12345)
                self.assertEqual(accepted[0][1]['camera_received_utc'],'CPU_TEST_TIMESTAMP')
                self.assertEqual(accepted[0][1]['camera_resolution'],[640,480])
                self.assertEqual(evidence['accepted_source_frames'],1)
            if failure=='input':self.assertTrue(camera.closed)

    def test_original_timestamp_and_release(self):self.exercise()
    def test_input_failure_releases_camera(self):self.exercise('input')
    def test_unavailable_does_not_substitute_recording(self):self.exercise('open')


if __name__=='__main__':unittest.main()

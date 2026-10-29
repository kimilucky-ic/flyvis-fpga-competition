"""CPU protocol tests only: prewarming never becomes camera/neural evidence."""
import base64
import hashlib
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

from live_protocol import HERE,load,write
from realtime_timing import StartupTimings
from stream_runtime import StreamHub
from test_live_protocol import Protocol


class Prewarm(unittest.TestCase):
    def setUp(self):
        self.h=StreamHub('CPU_PROTOCOL_SESSION')
        self.control=dict(session_id='CPU_PROTOCOL_SESSION',run_id='a'*32,
            source_kind='digital_direct',mode='Full',PL_execution=False)

    def frame(self):
        raw=b'CPU_PROTOCOL_ONLY_NOT_VIDEO'
        return dict(png=base64.b64encode(raw).decode(),source=dict(run_id='a'*32,
            source_kind='digital_direct',sequence=0,relative_s=0,
            png_sha256=hashlib.sha256(raw).hexdigest()))

    def test_prewarm_has_no_input_run_packet_or_neural_progress(self):
        self.h.dispatch('renderer','ready',None)
        s=self.h.status()
        self.assertEqual(s['status'],'WAITING_INPUT_SELECTION')
        self.assertIsNone(s['run_id']);self.assertIsNone(self.h.packet)
        self.assertEqual((s['computed_steps'],s['input_frames'],s['converted_frames']),(0,0,0))
        self.assertIsNone(self.h.dispatch('renderer','raw',{'wait_ms':1}))

    def test_prepared_converter_is_preserved_at_input_selection(self):
        self.h.dispatch('renderer','ready',None)
        s=self.h.dispatch('bridge','start',self.control)
        self.assertEqual(s['status'],'WAITING_SOURCE');self.assertTrue(s['renderer_ready'])

    def test_selection_before_warmup_still_waits_and_rejects_input(self):
        s=self.h.dispatch('bridge','start',self.control)
        self.assertEqual(s['status'],'WAITING_CONVERTER')
        with self.assertRaisesRegex(ValueError,'BEFORE_READY'):
            self.h.dispatch('bridge','input',self.frame())
        self.h.dispatch('renderer','ready',None)
        self.assertEqual(self.h.status()['status'],'WAITING_SOURCE')

    def test_prewarm_cannot_publish_converted_or_raw_source(self):
        self.h.dispatch('renderer','ready',None)
        with self.assertRaisesRegex(ValueError,'BEFORE_INPUT_SELECTION'):
            self.h.dispatch('renderer','converted',{})
        with self.assertRaisesRegex(ValueError,'BEFORE_READY'):
            self.h.dispatch('bridge','input',self.frame())

    def test_raw_wait_bound_and_role(self):
        for value in (-1,101,True,1.5):
            with self.assertRaisesRegex(ValueError,'WAIT_BOUND'):
                self.h.dispatch('renderer','raw',{'wait_ms':value})
        with self.assertRaisesRegex(ValueError,'ROLE'):
            self.h.dispatch('bridge','raw',{'wait_ms':1})

    def test_waiting_converter_wakes_on_actual_input_without_poll_delay(self):
        self.h.dispatch('renderer','ready',None);self.h.dispatch('bridge','start',self.control)
        ready=threading.Event();out=[]
        def consume():
            with self.h.updated:
                ready.set();out.append(self.h.dispatch('renderer','raw',{'wait_ms':100}))
        thread=threading.Thread(target=consume);thread.start()
        self.assertTrue(ready.wait(1));self.h.dispatch('bridge','input',self.frame());thread.join(1)
        self.assertFalse(thread.is_alive());self.assertEqual(out[0],self.frame())
        self.assertEqual(self.h.status()['computed_steps'],0)

    def test_stop_wakes_idle_converter_and_revokes(self):
        ready=threading.Event();out=[]
        def consume():
            with self.h.updated:
                ready.set()
                try:self.h.dispatch('renderer','raw',{'wait_ms':100})
                except ValueError as error:out.append(str(error))
        thread=threading.Thread(target=consume);thread.start()
        self.assertTrue(ready.wait(1));self.h.dispatch('bridge','stop',None);thread.join(1)
        self.assertFalse(thread.is_alive());self.assertIn('STREAM_STOP_REQUESTED',out)
        self.assertFalse(self.h.status()['result_valid'])


class StartupDetails(unittest.TestCase):
    def test_nested_stage_restores_parent_without_double_count_claim(self):
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as d:
            timing=StartupTimings(Path(d),'CPU_PROTOCOL_SESSION')
            with timing.measure('original_full_model_load'):
                with timing.measure('original_full_module_import'):
                    self.assertEqual(timing.snapshot()['stage'],'original_full_module_import')
                self.assertEqual(timing.snapshot()['stage'],'original_full_model_load')
            self.assertIsNone(timing.snapshot()['stage'])
            data=load(Path(d)/'startup_timings.json')
            self.assertEqual([s['name'] for s in data['stages']],['original_full_module_import','original_full_model_load'])
            self.assertTrue(all(s['success'] for s in data['stages']))

    def test_stage_failure_is_saved_and_active_stage_is_cleared(self):
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as d:
            timing=StartupTimings(Path(d),'CPU_PROTOCOL_SESSION')
            with self.assertRaisesRegex(ValueError,'CPU_TEST_FAILURE'):
                with timing.measure('original_full_model_construct'):raise ValueError('CPU_TEST_FAILURE')
            self.assertIsNone(timing.snapshot()['stage'])
            self.assertEqual(load(Path(d)/'startup_timings.json')['status'],'FAILED')

    def test_current_session_stage_is_explained_without_admitting_cuda(self):
        p=Protocol();p.setUp()
        try:
            target=p.root/'heartbeat.json';beat=load(target)
            beat.update(state='PRELOADING',device=None,phase='PRELOADING_ORIGINAL_MODEL',
                startup=dict(stage='original_full_model_construct',stage_elapsed_s=12,elapsed_s=16))
            write(target,beat);caps=p.a.capabilities()
            self.assertEqual(caps['status'],'NOT_CONNECTED')
            self.assertIn('构建原始完整网络',caps['service']['message'])
            self.assertEqual(caps['service']['startup']['stage_elapsed_s'],12)
            beat['session_id']='other';write(target,beat)
            self.assertEqual(p.a.capabilities()['service']['state'],'DISCONNECTED')
        finally:p.tearDown()

    def test_test_process_imports_no_device_libraries(self):
        self.assertFalse(set(('torch','flyvis','cv2'))&set(sys.modules))


if __name__=='__main__':unittest.main()

"""Read-only diagnostic accounting and protocol clock tests; no devices."""
import copy
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from live_protocol import HERE,load,write
from stream_manual_summary import startup_summary
from stream_runtime import StreamHub


class Accounting(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=HERE/'runtime')
        self.session=Path(self.temp.name);self.root=self.session/'stream';self.root.mkdir()
        self.control=dict(session_id='CPU_PROTOCOL_SESSION',run_id='a'*32)

    def tearDown(self):self.temp.cleanup()

    def worker(self):
        stages=[dict(name=n,wall_s=t,success=True) for n,t in
            [('original_full_module_import',1),('official_flyvis_import',12),
             ('original_full_model_construct',7),('original_full_model_load',20)]]
        return dict(schema='flyvis-startup-timing/v1',session_id=self.control['session_id'],
            status='READY',elapsed_s=30,stages=stages)

    def converter(self):
        return dict(schema='flyvis-input-converter-startup/v1',session_id=self.control['session_id'],
            elapsed_s=.1,process_elapsed_s=5.7,helper_import_s=.05,official_converter_construct_s=5,
            published_source_frames=0,neural_updates=0)

    def summary(self):return startup_summary(self.root,self.control,{})

    def test_missing_diagnostics_are_unknown_without_neural_result_claim(self):
        s=self.summary();self.assertEqual(s['status'],'NOT_RECORDED')
        self.assertIsNone(s['worker']);self.assertIsNone(s['converter'])
        self.assertNotIn('REALTIME_STREAM_PASS',s)

    def test_nested_original_timings_are_reported_without_total_sum(self):
        write(self.session/'startup_timings.json',self.worker());s=self.summary()
        self.assertEqual(s['worker']['elapsed_s'],30)
        self.assertEqual(s['worker']['stage_wall_s']['original_full_model_load'],20)
        self.assertIn('official_flyvis_import',s['worker']['hierarchy']['original_full_model_load'])
        self.assertNotIn('sum_of_stages',s['worker'])

    def test_diagnostics_are_read_only(self):
        target=self.session/'startup_timings.json';write(target,self.worker());before=target.read_bytes()
        self.summary();self.assertEqual(target.read_bytes(),before)

    def test_wrong_session_cannot_supply_startup_times(self):
        data=self.worker();data['session_id']='OTHER_SESSION';write(self.session/'startup_timings.json',data)
        s=self.summary();self.assertEqual(s['status'],'INVALID_DIAGNOSTICS');self.assertIsNone(s['worker'])
        self.assertIn('IDENTITY',s['errors']['worker'])

    def test_duplicate_or_failed_stages_are_not_performance_results(self):
        for change in ('duplicate','failed'):
            data=self.worker()
            if change=='duplicate':data['stages'].append(copy.deepcopy(data['stages'][0]))
            else:data['stages'][0]['success']=False
            write(self.session/'startup_timings.json',data);self.assertIsNone(self.summary()['worker'])

    def test_legacy_unbound_converter_does_not_inherit_old_measurements(self):
        write(self.session/'converter_warmup.json',dict(elapsed_s=.1))
        self.assertEqual(self.summary()['converter'],dict(status='LEGACY_UNBOUND_NOT_USED'))

    def test_converter_records_zero_published_warmup_and_same_session(self):
        write(self.session/'converter_warmup.json',self.converter());s=self.summary()
        self.assertEqual(s['converter']['process_elapsed_s'],5.7)
        for field,value in [('session_id','OTHER'),('published_source_frames',1),('neural_updates',1),('elapsed_s',-1)]:
            data=self.converter();data[field]=value;write(self.session/'converter_warmup.json',data)
            self.assertIsNone(self.summary()['converter'])

    def test_invalid_auxiliary_json_is_reported_without_throwing(self):
        target=self.session/'startup_timings.json'
        for text in ('[1,2]','{broken'):
            target.write_text(text,encoding='utf-8')
            self.assertEqual(self.summary()['status'],'INVALID_DIAGNOSTICS')


class PreparationClocks(unittest.TestCase):
    def hub(self):
        return StreamHub('CPU_PROTOCOL_SESSION'),dict(session_id='CPU_PROTOCOL_SESSION',run_id='a'*32,
            source_kind='digital_direct',mode='Full',PL_execution=False)

    def test_prepared_before_selection_reports_zero_remaining_wait(self):
        hub,control=self.hub()
        with patch('stream_runtime.time.monotonic',return_value=100):hub.dispatch('renderer','ready',None)
        with patch('stream_runtime.time.monotonic',return_value=101):s=hub.dispatch('bridge','start',control)
        d=s['input_preparation'];self.assertTrue(d['prewarmed_before_selection'])
        self.assertEqual(d['remaining_converter_wait_after_selection_s'],0)
        self.assertEqual(d['ready_lead_before_selection_s'],1)
        self.assertIsNone(d['selection_to_first_converted_s'])
        self.assertEqual(s['computed_steps'],0)

    def test_immediate_selection_reports_real_remaining_preparation(self):
        hub,control=self.hub()
        with patch('stream_runtime.time.monotonic',return_value=100):hub.dispatch('bridge','start',control)
        with patch('stream_runtime.time.monotonic',return_value=102):hub.dispatch('renderer','ready',None)
        d=hub.input_preparation();self.assertFalse(d['prewarmed_before_selection'])
        self.assertEqual(d['remaining_converter_wait_after_selection_s'],2)
        self.assertEqual(d['ready_lead_before_selection_s'],0)

    def test_before_selection_and_before_converter_are_not_zero_measurements(self):
        hub,_=self.hub();d=hub.input_preparation()
        self.assertIsNone(d['prewarmed_before_selection'])
        self.assertIsNone(d['remaining_converter_wait_after_selection_s'])

    def test_diagnostic_tests_do_not_import_device_libraries(self):
        self.assertFalse(set(('torch','flyvis','cv2'))&set(sys.modules))


if __name__=='__main__':unittest.main()

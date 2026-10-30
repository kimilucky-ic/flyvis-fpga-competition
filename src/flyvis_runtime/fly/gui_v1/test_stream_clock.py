"""Bounded CPU clock/causality tests, no camera or model execution."""
import unittest
from stream_clock import clock_spec,control_clock,model_source_time,schedule
from camera_stream_protocol import PreparedCausalSelector,CausalSelector
from test_stream_durability import ManualSummary
from live_protocol import load,write

class ClockTests(unittest.TestCase):
    def test_all_rates_keep_steps_and_physical_capture_times(self):
        original=[dict(sequence=i,relative_s=i*.1) for i in range(101)]
        for rate in (50,100,200):
            clock=clock_spec(rate);selector=PreparedCausalSelector()
            mapped=[dict(f,relative_s=model_source_time(f,clock)) for f in original]
            selector.prepare(mapped)
            for k in range(rate*10):
                chosen,index=selector.select(k)
                self.assertLessEqual(chosen['relative_s'],k*.005)
                if index+1<len(mapped):self.assertGreater(mapped[index+1]['relative_s'],k*.005)
                selector.commit(original[index],k)
            self.assertEqual(selector.next_step,rate*10)
            self.assertEqual(original[-1]['relative_s'],10)
            self.assertEqual(rate*10*.005,10*clock['model_seconds_per_wall_second'])
    def test_schedule_lag_is_wall_time_and_never_advances_steps(self):
        for rate in (50,100,200):
            c=clock_spec(rate)
            self.assertEqual(schedule(rate,0,c),(1,0))
            self.assertEqual(schedule(rate,1.75,c),(0,.75))
    def test_rate_mapping_and_identity_rejections(self):
        for bad in (0,99,True,100.0,'100',201):
            with self.assertRaises(ValueError):clock_spec(bad)
        c=clock_spec(100)
        with self.assertRaises(ValueError):control_clock(dict(clock=c,binding=dict(clock=clock_spec(50))))
        with self.assertRaises(ValueError):model_source_time(dict(relative_s=2,model_relative_s=2),c)
        with self.assertRaises(ValueError):model_source_time(dict(relative_s=float('nan')),c)
    def test_old_records_and_original_clock_remain_original(self):
        c=control_clock({});self.assertEqual(c,clock_spec(200))
        old=CausalSelector();new=PreparedCausalSelector()
        frames=[dict(sequence=i,relative_s=i*.07) for i in range(10)]
        new.prepare([dict(f,relative_s=model_source_time(f,c)) for f in frames])
        for k in range(140):
            a=old.choose(frames,k);b,_=new.select(k);self.assertEqual(a,b)
            old.commit(a,k);new.commit(b,k)

class SlowSummaryTests(unittest.TestCase):
    setUp=ManualSummary.setUp
    tearDown=ManualSummary.tearDown
    row=ManualSummary.row
    fixture=ManualSummary.fixture
    def test_slow_success_is_not_realtime_or_manual_early_stop(self):
        from stream_manual_summary import manual_summary
        c=self.fixture();c['clock']=clock_spec(100);c['binding']=dict(clock=c['clock'])
        r=load(self.root/'result.json');r.update(reason='STREAM_OBSERVATION_COMPLETE',inference_steps_per_s=100)
        write(self.root/'result.json',r)
        s=manual_summary(self.root,c)
        self.assertEqual(s['BOUNDED_SLOW_CAMERA_TEST'],'PASS')
        self.assertEqual(s['REALTIME_STREAM_PASS'],'NOT_APPLICABLE_SLOW_MODEL_DEMO')
        r['reason']='STREAM_STOP_REQUESTED';write(self.root/'result.json',r)
        self.assertFalse(manual_summary(self.root,c)['observation_completed'])

if __name__=='__main__':unittest.main()

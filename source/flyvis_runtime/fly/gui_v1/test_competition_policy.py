"""Small resource-policy checks, no GPU/model/board launch."""
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from competition_policy import presentation_policy, busy_reasons
from competition_renderer import CompetitionRenderer
from data_store import ROOT
from competition_replay import RUN, ACTIVITY_SHA


class PolicyTests(unittest.TestCase):
    def test_light_has_cpu_graphics_and_simplified_real_background(self):
        p=presentation_policy('light')
        self.assertEqual((p['renderer'],p['width'],p['height'],p['max_fps'],p['step_stride']),('cpu',800,500,10,5))
        self.assertTrue(p['background_rois'])
        self.assertEqual(p['background_style'],'simplified_mesh')

    def test_active_compute_forces_cpu_keyframes_even_from_standard(self):
        p=presentation_policy('standard',True)
        self.assertEqual((p['renderer'],p['max_fps'],p['step_stride']),('cpu',2,25))
        self.assertEqual((p['width'],p['height']),(640,400))
        self.assertTrue(p['degraded']);self.assertTrue(p['background_rois'])
        self.assertEqual(p['background_style'],'simplified_mesh')

    def test_unknown_profile_fails_before_launch(self):
        with self.assertRaises(ValueError):presentation_policy('live_FPGA')

    def test_process_guard_is_conservative_and_read_only(self):
        values=busy_reasons(ROOT,{'wsl.exe','vivado.exe','python.exe'})
        self.assertIn('reserved process: wsl.exe',values)
        self.assertIn('reserved process: vivado.exe',values)
        self.assertFalse(any('python.exe' in x for x in values))

    def test_same_gui_compute_yields_before_submission(self):
        renderer=CompetitionRenderer(None);events=[]
        renderer.process=object();renderer.release=lambda:events.append('owned graphics released')
        renderer.yield_for_compute();events.append('new task can be submitted')
        self.assertEqual(events,['owned graphics released','new task can be submitted'])
        with patch('competition_renderer.busy_reasons',return_value=[]):
            p=renderer.policy('standard')
        self.assertEqual(p['renderer'],'cpu');self.assertEqual(p['max_fps'],2)

    def test_idle_gpu_watcher_releases_without_new_frame(self):
        renderer=CompetitionRenderer(None);events=[];renderer.config={'renderer':'gpu'}
        class Stop:
            count=0
            def wait(s,seconds):s.count+=1;return s.count>1
        renderer.monitor_stop=Stop();renderer.release=lambda:events.append('released while idle')
        with patch('competition_renderer.busy_reasons',return_value=['reserved process: wsl.exe']):renderer.watch_gpu()
        self.assertEqual(events,['released while idle'])
        self.assertTrue(renderer.priority_reason)

    def test_resource_scan_cached_but_compute_request_is_immediate(self):
        renderer=CompetitionRenderer(None)
        with patch('competition_renderer.busy_reasons',return_value=[]) as scan:
            renderer.policy('standard');renderer.policy('light');self.assertEqual(scan.call_count,1)
            renderer.yield_for_compute();p=renderer.policy('standard')
        self.assertEqual(p['renderer'],'cpu');self.assertEqual(p['max_fps'],2)

    def test_incorrect_renderer_group_or_background_is_not_published(self):
        types=['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']
        values=[.1]*8
        replay=SimpleNamespace(unchanged=lambda:None,pilot=SimpleNamespace(activity_time={240:.205}),
                               spatial=SimpleNamespace(data={'types':types}),
                               means={240:SimpleNamespace(tolist=lambda:values)})
        renderer=CompetitionRenderer(SimpleNamespace(get=lambda:replay))
        renderer.policy=lambda profile:presentation_policy(profile)
        renderer.start=lambda config:setattr(renderer,'config',config)
        renderer.ready={'service_id':'owned','identity':{'mapping_sha256':'map'},'background_manifest_sha256':'a'*64}
        body=dict(run_id=RUN,activity_sha256=ACTIVITY_SHA,frame_index=240,activity_time_s=.205,
                  request_id='receipt-rejection',type_filter='all',selected_type='T4a')
        receipt=dict(body,service_id='owned',mapping_sha256='map',visible_types=types,
                     type_states=[dict(type=t,value=v) for t,v in zip(types,values)],
                     PL_execution=False,evidence_level='OFFLINE_SOFTWARE_REPLAY',profile='light',
                     rois_visible=True,background_style='simplified_mesh',background_manifest_sha256='a'*64)
        cases=[({'visible_types':['T4a']},'visible type set'),
               ({'background_style':'full_mesh'},'Presentation/background'),
               ({'rois_visible':False},'Presentation/background'),
               ({'background_manifest_sha256':'b'*64},'background manifest changed')]
        for change,message in cases:
            renderer.call=lambda path,payload,change=change:{'metadata':dict(receipt,**change)}
            with self.subTest(change=change),self.assertRaisesRegex(ValueError,message):
                renderer.render(body)
        self.assertIsNone(renderer.process)


if __name__=='__main__':unittest.main(verbosity=2)

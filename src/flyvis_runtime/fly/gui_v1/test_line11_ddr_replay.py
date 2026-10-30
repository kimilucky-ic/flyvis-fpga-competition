"""Focused archive/replay/camera/entry checks; CPU data, no device or listener."""
import io,json,threading,unittest,uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch,MagicMock
import numpy as np
from line11_ddr_flow import archive_frame,FlowConsumer
from line11_ddr_start import DdrGuiSession
from line11_ddr_plan import load_plan
from line11_ddr_bridge import digest,PROFILE,BIT_SHA,HWH_SHA,CORE_CYCLES
from live_protocol import load
from spatial_state import SpatialRegistry

HERE=Path(__file__).parent;E=HERE/'evidence/line11_ddr485_on60_20261018'


class Tests(unittest.TestCase):
    def fixture(self,camera=False):
        root=E/'replay_cases'/uuid.uuid4().hex;root.mkdir(parents=True)
        plan=E/('camera_software_replay/plan' if camera else 'plan')
        m=load(plan/'RUN_PLAN.json');pin=digest((plan/'RUN_PLAN.json').read_bytes())
        inp,states,_=load_plan(plan,485,pin)
        stream=object.__new__(DdrGuiSession)
        stream.lock=threading.RLock();stream.protocol_test=True;stream.session_id='CPU_SESSION';stream.profile=PROFILE
        stream.counter_definition='CPU_MOCK_ONLY';stream.clock=lambda:1_000_000_000
        model=load(HERE/'live_registry.json')['model'];stream.decoder_pin=load(HERE/'live_registry.json')['pins']['decoder']
        spatial=SpatialRegistry();stream.seed=SimpleNamespace(plan=m,plan_input=inp,plan_expected=states,
            spatial=spatial,archive_sha='a'*64)
        stream.anchor=dict(run_id='cpu_run',hardware=dict(boot_id='CPU_BOOT',bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,
            clock_hz=100000000,compute_cycles=CORE_CYCLES,faults=0),model=model,
            plan_metadata=dict(steps=485,input_time_offset_s=m['input_time_offset_s'],condition_id=m['condition_id']))
        stream.flow_consumer=SimpleNamespace(output=root)
        stream.status=lambda:dict(status='FINISHED',result_valid=True,display_complete=True,
            evidence_level='CPU_PROTOCOL_ONLY_NO_PHYSICAL_RUN',run_id='cpu_run',session_id='CPU_SESSION')
        meta=dict(run_id='cpu_run',session_id='CPU_SESSION',frame_id=0,state_sha256=digest(states[:182676]),
            previous_state_sha256=m['initial_state']['sha256'],input_sha256=digest(inp[:2884]),elapsed_seconds=.04)
        snapshot=(meta,inp[:2884],states[:182676],1,None)
        identity=load(E/'plan/RUN_PLAN.json')['decoder']
        binding=dict(identity,run_id='cpu_run',session_id='CPU_SESSION',frame_id=0,full_state_sha256=meta['state_sha256'])
        # Synthetic zeros used only to exercise archive/schema, not a neural prediction.
        flow=np.zeros((2,721),dtype='<f4').tobytes();binding['flow_sha256']=digest(flow)
        return stream,snapshot,binding,flow

    def test_saved_run_replay_timeline_hashes_and_failures(self):
        stream,snapshot,binding,flow=self.fixture()
        archive_frame(stream.flow_consumer.output,snapshot,binding,flow)
        reply=stream.replay(0);p=reply['frame']
        self.assertTrue(p['offline_replay']);self.assertEqual(p['display_kind'],'CPU_PROTOCOL_TEST_ONLY')
        self.assertEqual(p['input_time_s'],-1.);self.assertAlmostEqual(p['activity_time_s'],-.995)
        self.assertEqual(p['flow_binding']['full_state_sha256'],p['full_state_sha256'])
        with self.assertRaises(ValueError):stream.replay(485)
        path=stream.flow_consumer.output/'000000.flow.bin';bad=bytearray(path.read_bytes());bad[0]^=1;path.write_bytes(bad)
        with self.assertRaisesRegex(ValueError,'FILE_IDENTITY'):stream.replay(0)
        stream.status=lambda:dict(status='FAILED',display_complete=False)
        with self.assertRaisesRegex(ValueError,'NOT_COMPLETE'):stream.replay(0)

    def test_async_archive_fsync_failure_and_queue_bound(self):
        stream,snapshot,binding,flow=self.fixture()
        with patch('line11_ddr_flow.os.fsync',side_effect=OSError('injected disk failure')):
            with self.assertRaisesRegex(OSError,'disk failure'):archive_frame(stream.flow_consumer.output,snapshot,binding,flow)
        self.assertFalse((stream.flow_consumer.output/'000000.json').exists())
        consumer=FlowConsumer(stream.flow_consumer.output/'unused',lambda *args:None)
        for _ in range(485):consumer.submit(snapshot)
        self.assertEqual(consumer.accepted,485)
        consumer.submit(snapshot);self.assertEqual(consumer.state,'FAILED');self.assertEqual(consumer.accepted,485)
        self.assertEqual(consumer.queue.qsize(),485)

    def test_camera_actual_pixels_same_run_step_and_no_fallback(self):
        stream,snapshot,binding,flow=self.fixture(camera=True)
        packet=stream.frame_reply((*snapshot[:4],dict(values=np.zeros((2,721)).tolist(),sha256=digest(flow),binding=binding)),stream.status(),1)['frame']
        self.assertEqual(packet['source']['kind'],'recorded_camera_flyvis')
        self.assertEqual(packet['input_time_s'],0.)
        raw=stream.source_frame(0,'cpu_run',packet['full_state_sha256'])
        self.assertEqual(digest(raw),packet['source']['pixel_png_sha256'])
        with self.assertRaisesRegex(ValueError,'IDENTITY'):stream.source_frame(0,'WRONG',packet['full_state_sha256'])
        with self.assertRaisesRegex(ValueError,'STATE'):stream.source_frame(0,'cpu_run','0'*64)
        packet['source']['kind']='recorded_camera_flyvis'
        (E/'CPU_BROWSER_CAMERA_FIXTURE.json').write_text(json.dumps(packet),encoding='utf-8')

    def test_original_handler_download_filename_and_replay_without_socket(self):
        from server import handler_factory
        stream,snapshot,binding,flow=self.fixture();archive_frame(stream.flow_consumer.output,snapshot,binding,flow)
        stream.authenticate_preparation=lambda _:None;stream.link_path=stream.flow_consumer.output/'PRIVATE_CPU_ONLY.zip';stream.link_path.write_bytes(b'CPU')
        handler=handler_factory(None,line11_stream=stream);obj=handler.__new__(handler);captured=[]
        obj.client_address=('127.0.0.1',1);obj.send=lambda data,mime=None,status=200,**kw:captured.append((status,data,kw))
        obj.path='/api/full-pl-stream/link.zip';obj.do_GET()
        self.assertIn('LINE11_DDR_PREPARE.zip',captured[-1][2]['extra']['Content-Disposition'])
        obj.path='/api/full-pl-stream/replay?step=0';obj.do_GET();self.assertTrue(captured[-1][1]['frame']['offline_replay'])
        obj.client_address=('192.0.2.10',1);obj.do_GET();self.assertEqual(captured[-1][0],403)
        packet=stream.replay(0)['frame'];status=stream.status()
        # Simulated UI flags ONLY: the real CPU packet above remains CPU_PROTOCOL_TEST_ONLY.
        packet['display_kind']='OFFLINE_REPLAY_FULL_PL_TRAJECTORY'
        anchor=dict(stream.anchor,archive_sha256=stream.seed.archive_sha)
        status.update(first_step_accepted=True,boot_id='CPU_BOOT')
        fixture=dict(evidence='CPU_FIXTURE_SIMULATED_UI_FLAGS_NOT_BOARD',packet=packet,status=status,anchor=anchor,
            health=dict(projection_cache=dict(upstream_map_sha256=stream.seed.spatial.digest)))
        (E/'CPU_BROWSER_FIXTURE.json').write_text(json.dumps(fixture),encoding='utf-8')

    def test_explicit_capture_uses_existing_session_once_no_separate_preview_window(self):
        sys_path=str(HERE.parent)
        import sys
        if sys_path not in sys.path:sys.path.insert(0,sys_path)
        from line11_ddr_camera import prepare
        folder=E/'capture_control_cases'/uuid.uuid4().hex
        with patch('camera_pipeline.open_camera') as opened,patch('camera_pipeline.record_clip',side_effect=RuntimeError('CPU_CAPTURE_BOUNDARY')) as record:
            opened.return_value=MagicMock()
            with self.assertRaisesRegex(RuntimeError,'CPU_CAPTURE_BOUNDARY'):prepare(folder,capture=True,device=1)
            opened.assert_called_once_with(1,backend='dshow',width=640,height=480,fps=30)
            self.assertEqual(record.call_args.args[2],2.5);self.assertFalse(record.call_args.kwargs['preview'])
            self.assertFalse((folder/'PREPARED.json').exists())

    def test_changed_capture_timestamp_identity_rejected_before_conversion(self):
        import sys
        if str(HERE.parent) not in sys.path:sys.path.insert(0,str(HERE.parent))
        from line11_ddr_camera import prepare
        m=load(E/'camera_software_replay/plan/RUN_PLAN.json');recording=Path(m['recording_directory'])
        source=load(recording/'recording.json');source['timestamp_source']='measured_host_frame_receipt'
        source['data_sha256']['frame_timestamps.csv']='0'*64
        with patch('camera_pipeline.adapter.load_video_source',return_value=(None,None,source)),patch('camera_pipeline.video_to_flyvis_stimulus') as convert:
            with self.assertRaisesRegex(ValueError,'TIMESTAMPS_CHANGED'):
                prepare(E/'capture_control_cases'/uuid.uuid4().hex,recording=recording)
            convert.assert_not_called()

if __name__=='__main__':unittest.main(verbosity=2)

"""CPU-only camera clocks/identity tests; real historical values are TEST ONLY."""
import copy
import hashlib
import sys
import unittest
import uuid
from pathlib import Path,PureWindowsPath,PurePosixPath
import numpy as np
from live_protocol import HERE,Registry,checked_commit,utc,write
from camera_stream_protocol import CausalSelector,DT,admitted_packet,dependencies,check_control,relative_asset_path
from camera_stream_bridge import CameraStreamBridge


class CameraProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=Registry();cls.deps=dependencies()
        source=cls.registry.path_for('intervention').parent/'artifacts/pilot_gpu_r1/ON60/Full'
        cls.values=np.asarray(np.load(source/'activities_full.npy',mmap_mode='r',allow_pickle=False)[0,0,cls.registry.data['central_global_ids']])
        cls.hex=np.asarray(cls.registry.input('ON60')[0,0,0]);cls.run_id=uuid.uuid4().hex
    def frame(self,seq,t):return {'sequence':seq,'relative_s':t}
    def packet(self):
        control={'run_id':self.run_id,'session_id':'CPU_TEST_ONLY','central_global_ids':self.registry.data['central_global_ids'],'binding':{'label':'HISTORICAL_VALUES_CPU_TEST_ONLY'}}
        packet={'schema':'flyvis-live-camera-output/v1',**control,'execution_kind':'CPU_PROTOCOL_TEST_ONLY','evidence_level':'CPU_PROTOCOL_TEST_ONLY',
            'actual_new_computation':False,'PL_execution':False,'device':{'type':'cpu'},'step_id':0,'state_token':1,'input_time_s':0.,'activity_time_s':DT,
            'source':{'sequence':0,'relative_s':0.,'hex_values_sha256':hashlib.sha256(self.hex.astype(np.float32).tobytes()).hexdigest()},
            'activity':self.values.tolist(),'input_hex':self.hex.tolist(),'flow':None,'decoder_status':'NOT_CONNECTED'}
        return packet,control
    def test_01_causal_zoh_30fps_200_steps(self):
        selector=CausalSelector();frames=[self.frame(i,i/30) for i in range(31)]
        for k in range(200):
            f=selector.choose(frames,k);self.assertLessEqual(f['relative_s'],k*DT);self.assertEqual(f['sequence'],int(np.searchsorted([i/30 for i in range(31)],k*DT,side='right')-1));selector.commit(f,k)
        self.assertEqual(selector.next_step,200)
    def test_02_no_future_when_history_missing(self):
        with self.assertRaises(ValueError):CausalSelector().choose([self.frame(1,.03)],0)
    def test_03_skip_model_step_denied(self):
        with self.assertRaises(ValueError):CausalSelector().choose([self.frame(0,0)],1)
    def test_04_duplicate_commit_denied(self):
        s=CausalSelector();f=self.frame(0,0);s.commit(f,0)
        with self.assertRaises(ValueError):s.commit(f,0)
    def test_05_wrong_source_order(self):
        with self.assertRaises(ValueError):CausalSelector().choose([self.frame(1,.03),self.frame(0,0)],0)
    def test_06_nan_source_time(self):
        with self.assertRaises(ValueError):CausalSelector().choose([self.frame(0,float('nan'))],0)
    def test_07_cpu_packet_only_explicit_test(self):
        p,c=self.packet();admitted_packet(p,c,test_only=True)
        with self.assertRaises(ValueError):admitted_packet(p,c)
    def test_08_old_run_denied(self):
        p,c=self.packet();p['run_id']='historical-run'
        with self.assertRaises(ValueError):admitted_packet(p,c,test_only=True)
    def test_09_activity_time_not_input_time(self):
        p,c=self.packet();p['activity_time_s']=0.
        with self.assertRaises(ValueError):admitted_packet(p,c,test_only=True)
    def test_10_future_source_packet(self):
        p,c=self.packet();p['source']['relative_s']=.03
        with self.assertRaises(ValueError):admitted_packet(p,c,test_only=True)
    def test_11_changed_hex_identity(self):
        p,c=self.packet();p['source']['hex_values_sha256']='0'*64
        with self.assertRaises(ValueError):admitted_packet(p,c,test_only=True)
    def test_12_wrong_center_nodes(self):
        p,c=self.packet();p['central_global_ids']=p['central_global_ids'][::-1]
        with self.assertRaises(ValueError):admitted_packet(p,c,test_only=True)
    def test_13_false_pl(self):
        p,c=self.packet();p['PL_execution']=True
        with self.assertRaises(ValueError):admitted_packet(p,c,test_only=True)
    def test_14_unconnected_decoder_cannot_supply_old_flow(self):
        p,c=self.packet();p['flow']=self.hex.tolist()
        with self.assertRaises(ValueError):admitted_packet(p,c,test_only=True)
    def test_15_failed_gate_no_commit(self):
        commits=[]
        def reject(_):raise ValueError('CAMERA_DISCONNECTED')
        with self.assertRaises(ValueError):checked_commit('protocol token',reject,commits.append)
        self.assertEqual(commits,[])
    def test_16_bridge_import_and_no_backend_no_camera(self):
        class Adapter:
            def connected(self):raise ValueError('NOT_CONNECTED')
        bridge=CameraStreamBridge(Adapter())
        with self.assertRaises(ValueError):bridge.start({'camera_id':0})
        self.assertIsNone(bridge.thread);self.assertIsNone(bridge.control);self.assertEqual(bridge.stop()['status'],'NOT_STARTED')
    def test_17_empty_input_queue(self):
        with self.assertRaises(ValueError):CausalSelector().choose([],0)
    def test_18_state_token_mismatch(self):
        p,c=self.packet();p['state_token']=2
        with self.assertRaises(ValueError):admitted_packet(p,c,test_only=True)
    def test_19_changed_model_binding(self):
        p,c=self.packet();p['binding']={'wrong_model':True}
        with self.assertRaises(ValueError):admitted_packet(p,c,test_only=True)
    def test_20_negative_source_time(self):
        with self.assertRaises(ValueError):CausalSelector().choose([self.frame(0,-.01)],0)
    def test_21_windows_to_wsl_relative_path(self):
        root=PureWindowsPath('C:/fly/runtime/camera');value=relative_asset_path(root/'raw/00.npy',root)
        self.assertEqual(value,'raw/00.npy');self.assertEqual(str(PurePosixPath('/mnt/c/fly/runtime/camera')/value),'/mnt/c/fly/runtime/camera/raw/00.npy')
    def test_22_frame_run_guard_before_file_access(self):
        class Adapter:pass
        bridge=CameraStreamBridge(Adapter());bridge.control={'run_id':'current'}
        with self.assertRaisesRegex(ValueError,'FRAME_RUN_IDENTITY'):bridge.frame(0,'old-run')


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(CameraProtocol))
    safe=not any(name in sys.modules for name in ('torch','flyvis','cv2'))
    report={'status':'READY_FOR_USER_CAMERA_TEST' if result.wasSuccessful() and safe else 'FAIL','utc':utc(),'CPU_protocol_tests':result.testsRun,
        'failures':len(result.failures),'errors':len(result.errors),'no_device_imports':safe,'new_GPU_runs':0,'new_neural_steps':0,'new_decoder_calls':0,
        'camera_opens':0,'GUI_service_started':False,'LIVE_CAMERA_GPU_PASS':'NOT_RUN','REALTIME_STREAM_PASS':'NOT_RUN',
        'test_fixture':'real old ON60 slices, CPU_PROTOCOL_TEST_ONLY; production rejects','pending':['Windows device0 access','WSL CPU original BoxEye bridge','actual persistent Full GPU','same-page visualization and stop','actual throughput and latency']}
    write(HERE/'evidence/camera_stream_20261012/cpu_protocol.json',report);print(report);sys.exit(0 if result.wasSuccessful() and safe else 1)

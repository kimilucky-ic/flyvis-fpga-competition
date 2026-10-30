"""CPU-only mapping/routes/instrumentation tests using existing actual GPU rows."""
import ast
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import numpy as np
from live_protocol import HERE,load,sha,write,utc,Registry
from spatial_state import SpatialRegistry,TYPES
from realtime_timing import Timings,CudaProbes,latency_sample,realtime_verdict
from realtime_benchmark import plan
from live_jobs import LiveRoutes,LiveGPUAdapter

OUT=HERE/'evidence/realtime_prepare_20261012'
source=HERE/'evidence/recorded_gpu_20261012_172029_4d03e3fb'


class Realtime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=SpatialRegistry();cls.r=load(source/'result.json');m=load(source/'manifest.json')['files_sha256']
        for name in ('result.json','activities_full.npy'):assert sha(source/name)==m[name]
        cls.full=np.load(source/'activities_full.npy',mmap_mode='r',allow_pickle=False)
    def packet(self):return self.s.packet(self.full[0,311],self.r['run_id'],311,1.56)
    def test_01_real_8_by_721(self):
        self.assertEqual(len(self.s.nodes),5768)
        for t in TYPES:self.assertEqual(sum(n['type']==t for n in self.s.nodes),721)
    def test_02_exact_signed_values(self):
        a=self.s.extract(self.full[0,[0,311,608]])
        self.assertTrue(np.array_equal(a,self.full[0,[0,311,608]][:,self.s.ids]));self.assertLess(float(a.min()),0)
    def test_03_centers_cannot_replace_spatial(self):
        with self.assertRaises(ValueError):self.s.extract(self.full[0,311,:65])
    def test_04_real_h67_not_all_t5c(self):
        self.assertEqual(len(self.s.sets['H67']),67);self.assertEqual(len(set(self.s.sets['H67'])&set(self.s.ids)),11)
    def test_05_keep_exact_counts(self):
        for n in (0,488,1016,1736,2648,3752,5768):
            self.assertEqual(len(self.s.sets[f'KEEP_{n}']),n)
            self.assertEqual(len(self.s.layers(f'KEEP_{n}',200)['disabled_global_ids']),5768-n)
    def test_06_release_not_zero_state(self):
        p=self.s.layers('BLOCK_T4_RELEASE',200);self.assertEqual(len(p['release_blocked_global_ids']),2884);self.assertEqual(p['disabled_global_ids'],[])
    def test_07_intervention_window(self):self.assertEqual(self.s.layers('CLAMP_T4T5',199)['disabled_global_ids'],[])
    def test_08_software_never_pl(self):
        p=self.s.layers('Python_Replacement',0);self.assertEqual(len(p['software_replaced_global_ids']),67);self.assertEqual(p['PL_proven_global_ids'],[])
    def test_09_pl_not_available(self):
        with self.assertRaises(ValueError):self.s.layers('FPGA_Replacement',200)
    def test_10_planned_is_not_mode(self):
        with self.assertRaises(ValueError):self.s.layers('H5768',200)
    def test_11_packet_real_state(self):
        self.assertTrue(np.array_equal(self.s.validate(self.packet(),self.r['run_id'],311,1.56,'Full'),self.full[0,311,self.s.ids]))
    def test_12_wrong_run_rejected(self):
        with self.assertRaises(ValueError):self.s.validate(self.packet(),'old',311,1.56,'Full')
    def test_13_wrong_step_rejected(self):
        with self.assertRaises(ValueError):self.s.validate(self.packet(),self.r['run_id'],312,1.56,'Full')
    def test_14_wrong_axis_rejected(self):
        p=self.packet();p['values']=p['values'][:65]
        with self.assertRaises(ValueError):self.s.validate(p,self.r['run_id'],311,1.56,'Full')
    def test_15_nan_rejected(self):
        p=self.packet();p['values'][0]=float('nan')
        with self.assertRaises(ValueError):self.s.validate(p,self.r['run_id'],311,1.56,'Full')
    def test_16_fake_pl_rejected(self):
        p=self.packet();p['layers']['PL_proven_global_ids']=[28725]
        with self.assertRaises(ValueError):self.s.validate(p,self.r['run_id'],311,1.56,'Full')
    def test_17_software_mode_mismatch(self):
        p=self.packet();p['layers']=self.s.layers('Python_Replacement',311)
        with self.assertRaises(ValueError):self.s.validate(p,self.r['run_id'],311,1.56,'Full')
    def test_18_unsigned_or_reordered_values(self):
        p=self.packet();p['values'].reverse()
        with self.assertRaises(ValueError):self.s.validate(p,self.r['run_id'],311,1.56,'Full')
    def test_19_services_without_ports(self):
        routes=LiveRoutes(LiveGPUAdapter());code,m=routes.route('GET','/api/live/spatial-map')
        self.assertEqual(code,200);self.assertEqual(len(m['nodes']),5768)
        code,r=routes.route('POST','/api/live/jobs',{});self.assertEqual(code,503);self.assertIsNone(r['result'])
    def test_20_power_plan_has_no_execution(self):
        for mode in ('quiet','balanced','performance'):
            for variant in ('baseline','sampled'):
                p=plan(mode,variant);self.assertEqual(p['sampling_wall_s'],10);self.assertFalse(p['program_changes_power_settings']);self.assertEqual(p['REALTIME_STREAM_PASS'],'NOT_RUN')
    def test_21_reject_unknown_power(self):
        with self.assertRaises(ValueError):plan('turbo_unbounded','sampled')
    def test_22_host_timing(self):
        t=Timings();t.add('unit',.001);t.add('unit',.003);self.assertEqual(t.summary()['unit']['p50_ms'],2)
        with self.assertRaises(ValueError):t.add('unit',-1)
    def test_23_clock_pair_units_and_bound(self):
        p=latency_sample({'received_monotonic_ns':1_000_000_000},1_100_000_000,2)
        self.assertEqual(p['upper_ms'],102);self.assertEqual(p['lower_ms'],98)
    def test_24_clock_bad_domain_or_uncertainty(self):
        for stamp,unc in ((0,1),(1_000_000_001,100),(1_000_000_001,float('nan'))):
            with self.assertRaises(ValueError):latency_sample({'received_monotonic_ns':1_000_000_000},stamp,unc)
    def test_25_realtime_needs_all_metrics(self):
        self.assertEqual(realtime_verdict(9,1800,180,[100],0,True),'NOT_RUN')
        self.assertEqual(realtime_verdict(10,1185,200,[100],0,True),'NOT_MET')
        self.assertEqual(realtime_verdict(10,2000,200,[201],0,True),'NOT_MET')
        self.assertEqual(realtime_verdict(10,2000,200,[],0,True),'NOT_RUN')
    def test_26_original_core_checks_remain(self):
        text=(HERE.parent/'gpu_phase2/full_oracle.py').read_text();self.assertIn('torch.isfinite(old_full)',text)
        source=(HERE/'camera_stream_compute.py').read_text();self.assertNotIn("state[control['central_global_ids']].detach().cpu()",source)
        self.assertIn('oracle.step(state,tensor)',source)
    def test_27_cuda_probe_has_no_forced_sync(self):
        from realtime_timing import CudaProbes
        import inspect
        text=inspect.getsource(CudaProbes);self.assertNotIn('.synchronize(',text);self.assertIn('b.query()',text)
    def test_28_all_original_sources(self):self.assertEqual(len(Registry().pins),39)


if __name__=='__main__':
    from test_live_protocol import Protocol
    from test_camera_stream import CameraProtocol
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in (Realtime,Protocol,CameraProtocol)])
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    safe=not any(n in sys.modules for n in ('torch','flyvis','cv2'))
    report=dict(status='PASS_CPU_PREPARATION_ONLY' if result.wasSuccessful() and safe else 'FAIL',utc=utc(),tests=result.testsRun,
        failures=len(result.failures),errors=len(result.errors),no_device_imports=safe,new_GPU_runs=0,camera_opens=0,GUI_launches=0,board_operations=0,
        evidence_level='CPU_ROUTES_FROZEN_MAP_AND_PROTOCOL_TESTS',LIVE_CAMERA_GPU_PASS='NOT_RUN',LIVE_INTERACTIVE_GUI_PASS='NOT_RUN',REALTIME_STREAM_PASS='NOT_RUN')
    write(OUT/'cpu_tests.json',report)
    if result.wasSuccessful():
        s=Realtime.s;p=s.packet(Realtime.full[0,311],Realtime.r['run_id'],311,1.56)
        write(OUT/'node_test_fixture.json',{'label':'CPU_TEST_USING_EXISTING_ACTUAL_GPU_ROW_NOT_NEW_INFERENCE','metadata':s.public(),'packet':p})
    print(json.dumps(report));sys.exit(0 if report['status'].startswith('PASS') else 1)

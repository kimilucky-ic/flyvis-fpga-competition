"""Saved geometry only, current-run admission and exact saved-pixel checks."""
import hashlib
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
from competition_live import LiveSkeleton
from live_protocol import HERE,load,write
from projection_startup import load_static_projection
from realtime_timing import StartupTimings
from spatial_state import SpatialRegistry


class ProjectionStartupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spatial=SpatialRegistry();cls.registry=load(HERE/'live_registry.json')
    def bridge(self,root):
        return SimpleNamespace(adapter=SimpleNamespace(root=root,session={'stream_enabled':True},
            registry=SimpleNamespace(data=self.registry),connected=lambda:None),spatial=self.spatial,control=None)
    def test_prepare_uses_verified_geometry_without_graphics_process_and_fresh_service_identity(self):
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as directory:
            root=Path(directory);consumer=LiveSkeleton(self.bridge(root));begin=time.perf_counter()
            with patch('competition_live.subprocess.Popen',side_effect=AssertionError('graphics must not start')):
                health=consumer.prepare({'renderer':'cpu'})
            elapsed=time.perf_counter()-begin
            self.assertEqual(consumer.status()['status'],'READY')
            self.assertFalse(health['external_renderer_started']);self.assertFalse(health['geometry_origin']['neural_activity_reused'])
            other,_=load_static_projection(self.bridge(root))
            self.assertNotEqual(other['service_id'],health['service_id'])
            self.assertTrue((root/'skeleton/projection.cache').is_file())
            samples=HERE/'runtime/live/ff14862183fc423a90b55eb9e276a706/skeleton'
            for name in ['first','sample_500','sample_1000']:
                receipt=load(samples/(name+'_receipt.json'));rgba,_=consumer.cached.render(receipt['means'],health)
                self.assertEqual(hashlib.sha256(rgba.tobytes()).hexdigest(),receipt['raw_sha256'])
            write(HERE/'evidence/user_native_stall_20261016/static_startup_cpu.json',dict(
                status='PASS_CURRENT_OWNER_STATIC_GEOMETRY_AND_3_ACTUAL_PIXEL_HASHES',prepare_wall_s=elapsed,
                loader_wall_s=health['startup_elapsed_s'],external_graphics_processes_started=0,new_neural_steps=0,
                GPU_camera_GUI_started=False,scope='CPU actual saved geometry and activities only; full next-launch speed NOT measured'))
            consumer.close();self.assertEqual(consumer.status()['status'],'NOT_CONNECTED')
    def test_corrupt_registered_descriptor_rejected(self):
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as directory:
            descriptor=Path(directory)/'bad.json';descriptor.write_text('{}')
            with self.assertRaisesRegex(ValueError,'DESCRIPTOR_CHANGED'):load_static_projection(self.bridge(Path(directory)),descriptor)
    def test_static_cache_pin_change_rejected(self):
        import projection_startup
        original=projection_startup.sha
        with patch('projection_startup.sha',side_effect=lambda p:'0'*64 if Path(p).name=='projection.cache' else original(p)):
            with self.assertRaisesRegex(ValueError,'SOURCE_CHANGED'):load_static_projection(self.bridge(HERE/'runtime'))
    def test_model_identity_mismatch_rejected(self):
        import copy
        bridge=self.bridge(HERE/'runtime');bridge.adapter.registry.data=copy.deepcopy(self.registry)
        bridge.adapter.registry.data['model']['checkpoint_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'PROJECTION_MODEL'):load_static_projection(bridge)
    def test_startup_phase_failure_has_no_ready_claim(self):
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as directory:
            startup=StartupTimings(Path(directory),'CPU_PROTOCOL_ONLY')
            with self.assertRaisesRegex(ValueError,'injected'):
                with startup.measure('cpu_fixture'):raise ValueError('injected')
            saved=load(startup.path);self.assertEqual(saved['status'],'FAILED');self.assertFalse(saved['stages'][0]['success'])


if __name__=='__main__':unittest.main()

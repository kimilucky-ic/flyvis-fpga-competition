"""Bounded CPU rejection checks against actual saved projection/state fixtures."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from cached_skeleton import CachedSkeleton
from competition_live import LiveSkeleton
from live_protocol import HERE,load

class CachedDrawTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder=HERE/'evidence/cached_canvas_20261015/cpu_profile'
        cls.health=load(cls.folder/'cache_health.json');cls.blob=(cls.folder/'projection.cache').read_bytes()
        cls.packet=load(cls.folder/'packets.json')[9]  # actual saved Full ON60 step 213

    def test_corrupt_recipe_rejected(self):
        with self.assertRaisesRegex(ValueError,'CACHE_SHA'):
            CachedSkeleton(self.blob[:-1]+bytes([self.blob[-1]^1]),self.health)
        h=copy.deepcopy(self.health);h['fixed_cpu_projection_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'CACHE_IDENTITY'):CachedSkeleton(self.blob,h)

    def test_ack_requires_exact_pixels_current_run_and_valid_commit(self):
        cached=CachedSkeleton(self.blob,self.health);p=copy.deepcopy(self.packet)
        active=[True];consumer=LiveSkeleton.__new__(LiveSkeleton)
        consumer.cached=cached;consumer.health=self.health;consumer.lock=threading.RLock();consumer.closed=False
        consumer.bridge=SimpleNamespace(lock=threading.RLock(),packets={p['serial']:p},validate=lambda q:None,status=lambda:dict(result_valid=active[0]))
        import numpy as np
        means=np.asarray(p['spatial']['values'],dtype='<f4').reshape(8,721).mean(axis=1,dtype=np.float64)
        pixels,_=cached.render(means,self.health)
        body=dict(run_id=p['run_id'],serial=p['serial'],step_id=p['step_id'],skeleton_wire='FIXED_CPU_CACHE_V1',
                  skeleton_request_id='CPU_SAVED_ONLY',skeleton_cache_sha256=cached.sha256,skeleton_raw_sha256=hashlib.sha256(pixels.tobytes()).hexdigest())
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as folder:
            consumer.folder=Path(folder);consumer.verify_cached_draw(body)
            self.assertEqual(len((consumer.folder/'frames.jsonl').read_text(encoding='utf-8').splitlines()),1)
            for key,value,error in [('run_id','wrong','DRAW_IDENTITY'),('skeleton_cache_sha256','0'*64,'CACHE_IDENTITY'),('skeleton_raw_sha256','0'*64,'PIXELS_SHA')]:
                bad=dict(body,**{key:value})
                with self.assertRaisesRegex(ValueError,error):consumer.verify_cached_draw(bad)
            active[0]=False
            with self.assertRaisesRegex(ValueError,'DRAW_RESULT_REVOKED'):consumer.verify_cached_draw(body)
            self.assertEqual(len((consumer.folder/'frames.jsonl').read_text(encoding='utf-8').splitlines()),1)

if __name__=='__main__':unittest.main()

"""CPU-only display handoff tests using saved real arrays and static geometry.

No inference, camera, socket, GUI launch or board operation. Timing and cache
pressure are test inputs; they are not measurements from another live run.
"""
import copy
import json
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import numpy as np
from cached_skeleton import CachedSkeleton
from joint_camera_bridge import JointCameraBridge
from joint_camera_protocol import digest, validate_snapshot
from live_protocol import HERE, load
from spatial_state import SpatialRegistry

OUT=HERE/'evidence/draw_receipt_handoff_20261018'


class DrawHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved=load(HERE/'runtime/joint/f2fd7b4d54a4445daa8a15065c60088e/final_snapshot.json')
        cls.spatial=SpatialRegistry()
        cls.identity={k:cls.saved[k] for k in ('run_id','session_id','model','mapping_sha256','hardware')}
        for k in ('runtime_policy','live_response_hz'):
            if k in cls.saved:cls.identity[k]=cls.saved[k]
        means=validate_snapshot(cls.saved,cls.identity,cls.spatial)
        config=load(HERE/'static_projection.json')
        cls.geometry=load(Path(config['geometry']))
        cached=CachedSkeleton(Path(config['cache']).read_bytes(),cls.geometry)
        cls.rgba,_=cached.render(means,cls.geometry)
        cls.cache_sha=cached.sha256

    def setUp(self):
        (OUT/'cpu_cases').mkdir(parents=True,exist_ok=True)
        self.folder=tempfile.TemporaryDirectory(dir=OUT/'cpu_cases')
        self.addCleanup(self.folder.cleanup)
        self.root=Path(self.folder.name)
        self.b=JointCameraBridge();b=self.b
        b.path=self.root/'CPU_TEST_SESSION';b.root=self.root
        self.p=copy.deepcopy(self.saved);p=self.p
        b.scope=dict(run_id=p['run_id'],session_id=p['session_id'])
        b.validate=lambda packet:validate_snapshot(packet,self.identity,self.spatial)
        b.geometry=self.geometry
        b.cached=SimpleNamespace(sha256=self.cache_sha,render=Mock(return_value=(self.rgba,[])))
        b.packet=p;b.packets[p['serial']]=p
        b.status=lambda:dict(result_valid=not bool(b.error),error=b.error)
        self.now=time.perf_counter_ns()
        # Saved activity is real; this CPU fixture pairs timestamps within THIS
        # boot. A previous Windows boot monotonic epoch is not comparable.
        p['source']['received_monotonic_ns']=self.now-1_000_000
        self.clock=patch('joint_camera_bridge.time.perf_counter_ns',return_value=self.now)
        self.clock.start();self.addCleanup(self.clock.stop)
        self.body=dict(run_id=p['run_id'],session_id=p['session_id'],serial=p['serial'],
            step_id=p['step_id'],state_token=p['state_token'],
            unified_commit_sha256=p['transaction']['unified_commit_sha256'],
            source_png_sha256=p['source']['png_sha256'],spatial_values_sha256=p['spatial']['values_sha256'],
            flow_sha256=p['flow_sha256'],projection_cache_sha256=self.cache_sha,
            skeleton_raw_sha256=digest(self.rgba.tobytes()),browser_draw_ms=1.,
            draw_server_monotonic_ns=self.now,clock_uncertainty_ms=0.,clock_age_s=0.)

    def rows(self):
        path=self.root/'display_receipts.jsonl'
        return [json.loads(row) for row in path.read_text(encoding='utf-8').splitlines()] if path.exists() else []

    def test_handed_snapshot_survives_incoming_cache_eviction(self):
        given=self.b.latest()['packet']
        self.assertEqual(given,self.p)
        self.b.packets.clear()  # New worker publications evicted the ordinary ring.
        result=self.b.record_draw(self.body)
        self.assertEqual(result['status'],'DRAW_IDENTITY_AND_PIXELS_VERIFIED')
        self.assertEqual(len(self.rows()),1)

    def test_exact_verified_repeat_returns_original_receipt_once(self):
        first=self.b.record_draw(self.body)
        self.b.packets.clear()
        with patch('joint_camera_bridge.time.perf_counter_ns',return_value=self.now+10_000_000_000):
            repeated=self.b.record_draw(copy.deepcopy(self.body))
        self.assertEqual(repeated,dict(first,idempotent_replay=True))
        self.assertEqual(len(self.rows()),1)
        self.assertEqual(self.b.cached.render.call_count,1)

    def test_changed_repeat_is_rejected_including_fresh_clock(self):
        self.b.record_draw(self.body)
        for key,value in (('run_id','another_run'),('session_id','another_session'),
            ('unified_commit_sha256','0'*64),('skeleton_raw_sha256','0'*64),
            ('draw_server_monotonic_ns',self.now+1)):
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError,'JOINT_DRAW_DUPLICATE_CHANGED'):
                    self.b.record_draw(dict(self.body,**{key:value}))
        self.assertEqual(len(self.rows()),1)

    def test_handoffs_bounded_and_result_copies_cannot_change_saved_packet(self):
        got=self.b.latest()['packet'];got['source']['png_sha256']='0'*64
        self.assertEqual(self.b.draw_handoffs[self.p['serial']]['source'],self.p['source'])
        for serial in range(100,200):
            self.b.packet=dict(serial=serial)  # Cache pressure metadata only.
            self.b.latest()
        self.assertEqual(len(self.b.draw_handoffs),32)
        self.assertEqual(min(self.b.draw_handoffs),168)

    def test_receipt_ack_cache_bounded(self):
        for serial in range(100,132):
            self.b.draw_receipts[serial]=dict(request_sha256='unused',response={})
        self.b.record_draw(self.body)
        self.assertEqual(len(self.b.draw_receipts),32)
        self.assertNotIn(100,self.b.draw_receipts)

    def test_revoked_run_never_returns_previous_ack(self):
        self.b.record_draw(self.body);self.b.error='CPU_TEST_REVOKED'
        with self.assertRaisesRegex(ValueError,'JOINT_DRAW_REVOKED'):self.b.record_draw(self.body)
        self.assertIsNone(self.b.latest()['packet'])

    def test_evicted_snapshot_error_identifies_serial(self):
        self.b.packets.clear()
        with self.assertRaisesRegex(ValueError,'JOINT_DRAW_SNAPSHOT_EVICTED serial='+str(self.p['serial'])):
            self.b.record_draw(self.body)
        self.assertEqual(self.rows(),[])

    def test_wrong_run_or_step_never_verified(self):
        for key,value in (('run_id','other'),('session_id','other'),('state_token',1000),('step_id',1000)):
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError,'JOINT_DRAW_IDENTITY'):
                    self.b.record_draw(dict(self.body,**{key:value}))
        self.assertFalse(self.b.draw_pending);self.assertEqual(self.rows(),[])

    def test_commit_and_source_hashes_still_required(self):
        for key in ('unified_commit_sha256','source_png_sha256','spatial_values_sha256','flow_sha256'):
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError,'JOINT_DRAW_COMMIT'):
                    self.b.record_draw(dict(self.body,**{key:'0'*64}))
        self.assertEqual(self.rows(),[])

    def test_unverified_clock_or_pixels_still_rejected(self):
        for edits,error in ((dict(clock_age_s=6),'CLOCK_OR_GEOMETRY'),
            (dict(draw_server_monotonic_ns=self.now-3_000_000_000),'CLOCK_OR_GEOMETRY'),
            (dict(projection_cache_sha256='0'*64),'CLOCK_OR_GEOMETRY'),
            (dict(skeleton_raw_sha256='0'*64),'BRIGHTNESS_PIXELS')):
            with self.subTest(edits=edits):
                with self.assertRaisesRegex(ValueError,error):self.b.record_draw(dict(self.body,**edits))
        self.assertEqual(self.rows(),[])

    def test_corrupt_saved_activity_still_rejected_before_pixels(self):
        self.p['spatial']['values'][0]+=1
        with self.assertRaisesRegex(ValueError,'JOINT_ARRAY_SHA'):self.b.record_draw(self.body)
        self.b.cached.render.assert_not_called();self.assertEqual(self.rows(),[])

    def test_fsync_failure_never_caches_verified_ack(self):
        self.b.latest()
        with patch('joint_camera_bridge.os.fsync',side_effect=OSError('CPU_TEST_FSYNC_FAILED')):
            with self.assertRaisesRegex(OSError,'CPU_TEST_FSYNC_FAILED'):self.b.record_draw(self.body)
        self.assertEqual(len(self.b.draw_receipts),0)
        self.assertNotIn(self.p['serial'],self.b.drawn)
        self.assertIn(self.p['serial'],self.b.draw_handoffs)
        self.assertFalse(self.b.draw_pending)

    def test_invalid_serial_rejected(self):
        for serial in (True,0,-1,'3'):
            with self.subTest(serial=serial):
                with self.assertRaisesRegex(ValueError,'JOINT_DRAW_SERIAL'):
                    self.b.record_draw(dict(self.body,serial=serial))


if __name__=='__main__':unittest.main()

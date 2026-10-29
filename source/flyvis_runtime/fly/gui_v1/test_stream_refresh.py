"""Bounded CPU protocol checks with accepted actual arrays, no inference or capture."""
import base64
import copy
import hashlib
import json
import unittest
from pathlib import Path
import numpy as np
from live_protocol import HERE,load
from stream_wire import encode_packet,decode_packet
from camera_stream_protocol import CausalSelector,PreparedCausalSelector
from stream_bridge import StreamBridge
from stream_runtime import StreamHub
from realtime_timing import CudaProbes,Timings
from types import SimpleNamespace

class Refresh(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture=load(HERE/'evidence/realtime_prepare_20261012/node_test_fixture.json')
        source=HERE/'runtime/live/b872bc4816bc4004ab9bfef9eead9008/stream/snapshots'
        first=next(source.glob('*.npz'))
        arrays=np.load(first,allow_pickle=False)
        cls.packet=dict(spatial=fixture['packet'],flow=arrays['flow'],input_hex=arrays['input'],serial=1)
    def test_wire_all_real_values_exact(self):
        w=encode_packet(self.packet);p=decode_packet(w)
        for key in ('input_hex','flow'):
            self.assertTrue(np.array_equal(np.asarray(p[key],dtype=np.float32),self.packet[key]))
        self.assertTrue(np.array_equal(p['spatial']['values'],self.packet['spatial']['values']))
        self.assertEqual(p['spatial']['values_sha256'],w['wire_arrays']['spatial']['sha256'])
    def test_bad_shape_length_hash_dtype_and_nonfinite_rejected(self):
        for change in ('shape','dtype','length','hash','nonfinite'):
            with self.subTest(change=change):
                w=encode_packet(self.packet);a=w['wire_arrays']['spatial']
                if change=='shape':a['shape']=[5767]
                if change=='dtype':a['dtype']='<f8'
                if change=='length':a['base64']=a['base64'][:-4]
                if change=='hash':a['sha256']='0'*64
                if change=='nonfinite':
                    raw=bytearray(base64.b64decode(a['base64']));raw[:4]=np.float32(np.nan).tobytes()
                    a['base64']=base64.b64encode(raw).decode();a['sha256']=hashlib.sha256(raw).hexdigest()
                with self.assertRaises(ValueError):decode_packet(w)
    def test_original_timeline_exact_3000_steps(self):
        original=CausalSelector();prepared=PreparedCausalSelector();frames=[]
        for k in range(3000):
            if k%7==0:
                frames.append(dict(sequence=len(frames),relative_s=k*.005));prepared.prepare(frames[-96:])
            expected=original.choose(frames[-96:],k);actual,index=prepared.select(k)
            self.assertIs(actual,expected);original.commit(expected,k);prepared.commit(actual,k)
    def test_mutated_selected_time_rejected(self):
        s=PreparedCausalSelector();frames=[dict(sequence=0,relative_s=0.)];s.prepare(frames);frames[0]['relative_s']=.1
        with self.assertRaisesRegex(ValueError,'MUTATED'):s.select(0)
    def test_stale_step_rejected(self):
        s=PreparedCausalSelector();s.prepare([dict(sequence=0,relative_s=0.)])
        with self.assertRaisesRegex(ValueError,'ORDER'):s.select(1)
    def test_malformed_timeline_rejected(self):
        for frames in ([dict(sequence=0,relative_s=float('nan'))],[dict(sequence=1,relative_s=.2)],[dict(sequence=0,relative_s=0.),dict(sequence=0,relative_s=0.)]):
            with self.assertRaises(ValueError):PreparedCausalSelector().prepare(frames)
    def test_latest_none_and_revoke(self):
        b=StreamBridge.__new__(StreamBridge)
        import threading
        b.lock=threading.RLock();b.packet=None;b.wire_packet=None;b.status=lambda:dict(result_valid=True)
        self.assertIsNone(b.latest(wire=True,after=-1)['packet'])
        b.packet={'serial':3};b.wire_packet={'serial':3,'wire_format':'test_only'}
        self.assertIsNone(b.latest(wire=True,after=3)['packet'])
        self.assertIs(b.latest(wire=True,after=2)['packet'],b.wire_packet)
        self.assertIs(b.latest()['packet'],b.packet)
        b.status=lambda:dict(result_valid=False)
        self.assertIsNone(b.latest(wire=True,after=2)['packet'])
        with self.assertRaisesRegex(ValueError,'REVOKED'):b.latest()
    def test_digital_session_rejects_camera_before_io(self):
        import threading
        b=StreamBridge.__new__(StreamBridge);b.lock=threading.RLock();b.control=None
        b.adapter=SimpleNamespace(connected=lambda:None,session=dict(stream_enabled=True,camera_enabled=False))
        with self.assertRaisesRegex(ValueError,'CAMERA_MANUAL_ENTRY_REQUIRED'):b.start(dict(source_kind='real_windows_camera',camera_id=0))
        self.assertIsNone(b.control)
    def test_sampling_never_skips_underlying_checks(self):
        calls=[]
        class Event:
            def init__(self,**kw):pass
            def record(self):pass
            def query(self):return True
            def elapsed_time(self,other):return 1.
        obj=SimpleNamespace(check=lambda x:calls.append(x))
        t=Timings();p=CudaProbes(SimpleNamespace(cuda=SimpleNamespace(Event=Event)),t)
        p.wrap(obj,'check','test_only',sample_every=10)
        for k in range(31):obj.check(k)
        p.close();self.assertEqual(calls,list(range(31)));self.assertEqual(t.counts['test_only'],4)

if __name__=='__main__':unittest.main()

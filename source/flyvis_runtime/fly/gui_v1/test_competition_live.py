"""Bounded CPU consumer checks using actual saved source values, never new GPU evidence."""
import copy
import json
import struct
import threading
import unittest
from types import SimpleNamespace
import numpy as np
from PIL import Image
from competition_live import raw_frame,means_from_packet,ROOT,verify_source_receipt,SERVICE_REL,SERVICE_SHA,GUARD_REL,GUARD_SHA,FIXED_REL,FIXED_SHA

BASE=ROOT/'flyvis-3d-studio/activity_replay_20261014'
FIXTURE=BASE/'live_raw_20261015/evidence/cpu_protocol_r2'


class RawConsumerTests(unittest.TestCase):
    def test_new_guard_delivery_and_receipt_pins(self):
        from live_protocol import sha
        self.assertEqual(sha(BASE/SERVICE_REL),SERVICE_SHA)
        self.assertEqual(sha(BASE/GUARD_REL),GUARD_SHA)
        self.assertEqual(sha(BASE/FIXED_REL),FIXED_SHA)
        pins={SERVICE_REL:SERVICE_SHA,GUARD_REL:GUARD_SHA,FIXED_REL:FIXED_SHA}
        verify_source_receipt({'source_code_sha256':pins})
        for invalid in ({},dict(pins,**{GUARD_REL:'0'*64}),dict(pins,**{SERVICE_REL:'0'*64})):
            with self.assertRaisesRegex(ValueError,'RAW_SERVICE_SOURCE_IDENTITY'):verify_source_receipt({'source_code_sha256':invalid})

    def test_actual_windows_ready_receipt_and_ambiguous_paths(self):
        ready=ROOT/'gui_v1/runtime/live/dd1c654263a448268f9035e7f06851c3/skeleton/ready.json'
        value=json.loads(ready.read_text(encoding='utf-8'))
        # Reuse the actual Windows path spelling as a protocol-only fixture for
        # the explicitly updated delivery pins; this is not execution evidence.
        value['source_code_sha256']={SERVICE_REL.replace('/','\\'):SERVICE_SHA,GUARD_REL.replace('/','\\'):GUARD_SHA,FIXED_REL.replace('/','\\'):FIXED_SHA}
        self.assertIn(SERVICE_REL.replace('/','\\'),value['source_code_sha256'])
        verify_source_receipt(value)
        corrupt=copy.deepcopy(value);corrupt['source_code_sha256'][SERVICE_REL.replace('/','\\')]='0'*64
        with self.assertRaisesRegex(ValueError,'RAW_SERVICE_SOURCE_IDENTITY'):verify_source_receipt(corrupt)
        for name in (SERVICE_REL,'../service.py','/service.py','C:/service.py','a//service.py'):
            duplicate=copy.deepcopy(value);duplicate['source_code_sha256'][name]=SERVICE_SHA
            with self.assertRaisesRegex(ValueError,'RAW_SERVICE_SOURCE_PATH'):verify_source_receipt(duplicate)

    def test_actual_cpu_pixels_and_corruption(self):
        r=json.loads((FIXTURE/'receipt_0213.json').read_text(encoding='utf-8'))
        pixels=Image.open(FIXTURE/'actual_raw_0213.png').convert('RGBA').tobytes()
        header=json.dumps(r).encode();blob=struct.pack('<I',len(header))+header+pixels
        self.assertEqual(raw_frame(blob)[1],pixels)
        for corrupt in (blob[:-1],struct.pack('<I',200001)+blob[4:],blob[:-1]+bytes([blob[-1]^1])):
            with self.assertRaises(ValueError):raw_frame(corrupt)

    def test_mean_definition_and_identity_gate(self):
        model=json.loads((BASE/'model.json').read_text(encoding='utf-8'))
        path=next(s['path'] for s in model['sources'] if s['path'].endswith('activities_full.npy'))
        a=np.load(path,mmap_mode='r',allow_pickle=False)[0,213]
        values=np.concatenate([a[o['model_node_ids']] for o in model['objects']])
        p=dict(run_id='CPU_PROTOCOL_SAVED_SOURCE_ONLY',session_id='CPU_ONLY',serial=2,step_id=213,state_token=214,spatial={'values':values})
        valid=[True];calls=[]
        bridge=SimpleNamespace(lock=threading.RLock(),status=lambda:dict(result_valid=valid[0]),packets={2:p},validate=lambda v:calls.append(v))
        body={k:p[k] for k in ('run_id','session_id','serial','step_id','state_token')};body['request_id']='cpu-protocol'
        _,means=means_from_packet(bridge,body)
        expected=[a[o['model_node_ids']].mean(dtype=np.float64) for o in model['objects']]
        np.testing.assert_array_equal(means,expected);self.assertEqual(len(calls),1)
        for bad in ({'run_id':'wrong'},{'serial':False},{'step_id':214},{'means':[1]*8}):
            with self.assertRaises(ValueError):means_from_packet(bridge,dict(body,**bad))
        valid[0]=False
        with self.assertRaisesRegex(ValueError,'REVOKED'):means_from_packet(bridge,body)

    def test_fixed_contrast_preserves_signed_values(self):
        r=json.loads((FIXTURE/'receipt_0213.json').read_text(encoding='utf-8'));e=r['color_encoding']
        v=np.array(r['means']);expected=.25+.75*np.clip(np.abs(v)/e['intensity_domain'][1],0,1)**.45
        np.testing.assert_array_equal(expected,[s['brightness_factor'] for s in r['type_states']])
        np.testing.assert_array_equal(v,[s['value'] for s in r['type_states']]);self.assertTrue(np.any(v<0))

if __name__=='__main__':unittest.main()

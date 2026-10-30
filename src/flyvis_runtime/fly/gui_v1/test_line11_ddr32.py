"""Saved accepted32 arrays in CPU protocol envelopes; never new PL/neural data."""
import ast
import importlib
import io
import json
from pathlib import Path
import struct
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid
import zipfile

import numpy as np
import line11_ddr_board as board
from line11_ddr_start import DdrGuiSession
from line11_ddr_bridge import BIT_SHA,HWH_SHA,MANIFEST_SHA,INITIAL_BOUNDARY,verify_release,digest
from line11_ddr_plan import STARTUP_FILES,load_plan

HERE=Path(__file__).parent
E=HERE/'evidence/line11_ddr32_20261018'


class LongerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.release,_=verify_release();sys.path.insert(0,str(cls.release))
        cls.fake=importlib.import_module('cpu_replay')
        cls.acceptance=importlib.import_module('ddr_acceptance')

    def setUp(self):
        self.root=E/'cpu_cases'/uuid.uuid4().hex;self.root.mkdir(parents=True)
        self.stream=DdrGuiSession(self.root,software_test=True,total_steps=32)
        self.stream.package('http://192.0.2.1:8771')
        self.inp,self.states,self.plan_id=load_plan(E/'plan',32)
        template=(self.release/'cpu_fixture_ddr.bin').read_bytes()[:188416]
        codec=self.stream.seed.codec;records=[]
        for i in range(32):
            raw=bytearray(template);struct.pack_into('<I',raw,8,i)
            inp=self.inp[i*2884:(i+1)*2884];state=self.states[i*182676:(i+1)*182676]
            raw[128:3012]=inp;raw[4096:186772]=state
            struct.pack_into('<I',raw,48,codec.rolling(inp));struct.pack_into('<I',raw,52,codec.rolling(state))
            records.append(bytes(raw))
        self.records=b''.join(records)
        self.buffer=self.fake.Buffer(32*188416)
        self.mmio=self.fake.MMIO(self.buffer,self.records)
        self.session=self.acceptance.AcceptanceSession(self.mmio,lambda **kwargs:self.buffer,self.buffer.barrier,
            [self.inp[i*2884:(i+1)*2884] for i in range(32)],
            [self.states[i*182676:(i+1)*182676] for i in range(32)],self.root/'records')
        self.operator=dict(schema='flyvis-line2-ddr-operator/v1',preparation_id=self.stream.preparation_id,
            evidence='CPU_MOCK_ONLY',exclusive_board_window=True,boot_id='11111111-2222-3333-4444-555555555555',
            bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,release_manifest_sha256=MANIFEST_SHA,
            pynq_version='2.7.0',machine='armv7l',clock=dict(clock_control=0x200500,io_pll_control=0x1e000,pll_status=4,reference_mhz=33.333333),
            hp0_read_control=0,hp0_write_control=0,cache_policy='CLEAR_FLUSH_DSB_BEFORE_ARM;INVALIDATE_DSB_IMMUTABLE_COPY_AFTER_PUBLISH',
            barrier_library_sha256='a'*64,initial_state_readback=INITIAL_BOUNDARY,
            startup_sha256={n:digest((HERE/n).read_bytes()) for n in STARTUP_FILES})

    def packet(self,context_changes=None):
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
            for name in ('record_000000.bin','receipt_000000.json'):z.write(self.session.output/name,name)
            context=json.loads((self.session.output/'RUN_CONTEXT.json').read_text());context.update(context_changes or {})
            z.writestr('RUN_CONTEXT.json',json.dumps(context));z.writestr('OPERATOR.json',json.dumps(self.operator))
            z.writestr('TIMING.json',json.dumps(self.session.timing[0]))
        return out.getvalue()

    def test_32_strict_sequential_states_to_original_GUI_producer_no_paint_dependency(self):
        owner=self;counts=[]
        class PC:
            def first(_,session,op):
                counts.append(len(session.descriptors))
                return owner.stream.accept_first(owner.packet(),'Bearer '+owner.stream.preparation_token)['connection']
        class HTTP:
            def request(_,method,route,body,headers):
                _.response=owner.stream.accept(body,headers['Authorization']) if route.endswith('/frame') else owner.stream.finish(json.loads(body),headers['Authorization'])
            def getresponse(_):return SimpleNamespace(status=200,read=lambda n:json.dumps(_.response).encode())
            def close(_):pass
        with patch('line11_display_client.http.client.HTTPConnection',return_value=HTTP()):
            result=board.run_bounded(self.session,PC(),self.operator,self.release)
        self.assertEqual(counts,[1]);self.assertEqual(result['states_compared'],1461408)
        self.assertEqual(result['input_words_compared'],23072)
        self.assertEqual(len(list(self.session.output.glob('record_*.bin'))),32)
        self.assertEqual(self.stream.status()['received_steps'],31)
        self.assertEqual(self.stream.status()['browser_receipts'],0)
        last=self.stream.latest()['frame'];self.assertEqual(last['step_id'],31)
        self.assertEqual(last['display_kind'],'CPU_PROTOCOL_TEST_ONLY')
        self.assertEqual(last['full_state_sha256'],digest(self.states[-182676:]))
        self.assertEqual(len(last['spatial']['values']),5768);self.assertIsNone(last['flow'])
        self.assertEqual(sum(a==0 and v==2 for a,v in self.mmio.writes),1)
        self.assertEqual(sum(a==0 and v==1 for a,v in self.mmio.writes),32)
        self.assertEqual(self.buffer.free_calls,0)
        timing=json.loads((self.session.output/'INTEGRATION_TIMING.json').read_text())
        self.assertEqual(len(timing['commit_times']),32)
        self.assertEqual(len(timing['audit_decode_compare_persist']),32)
        self.assertEqual(len(timing['GUI_forward_serialization_roundtrip']),31)
        export=board.export_evidence(self.session.output,self.session.run_id)
        with zipfile.ZipFile(export['path']) as z:
            self.assertIn('record_000031.bin',z.namelist())
            self.assertIn('INTEGRATION_TIMING.json',z.namelist())
            self.assertNotIn('PREPARATION.json',z.namelist())
            m=json.loads(z.read('EXPORT_MANIFEST.json'))
            for name,v in m['files'].items():self.assertEqual(digest(z.read(name)),v['sha256'])
        with self.assertRaisesRegex(RuntimeError,'exhausted'):self.session.produce_next()

    def test_32_package_plan_tamper_and_bootstrap_syntax(self):
        target=self.root/'extract';target.mkdir()
        with zipfile.ZipFile(self.stream.link_path) as z:z.extractall(target)
        config=board.verify(target);self.assertEqual(config['total_steps'],32)
        self.assertFalse(config['board_operations_authorized'])
        nb=json.loads((self.stream.output/'START_DDR.ipynb').read_text(encoding='utf-8'))
        code=''.join(nb['cells'][1]['source']);ast.parse(code,feature_version=(3,8))
        self.assertIn(digest(self.stream.link_path.read_bytes()),code)
        for n in STARTUP_FILES:ast.parse((target/n).read_text(encoding='utf-8'),feature_version=(3,8))
        b=bytearray((target/'plan_expected_states.bin').read_bytes());b[-1]^=1
        (target/'plan_expected_states.bin').write_bytes(b)
        with self.assertRaisesRegex(ValueError,'PLAN_DATA_CHANGED'):board.verify(target)
        self.assertNotIn('pynq',sys.modules)

    def test_short_scope_cannot_admit_32_step_reference(self):
        self.session.start();self.session.produce_next();self.session.audit_next()
        with self.assertRaisesRegex(ValueError,'FIRST_SCOPE'):
            self.stream.accept_first(self.packet(dict(slots=3)),'Bearer '+self.stream.preparation_token)
        self.assertEqual(self.stream.count,0)
        self.assertEqual(len(self.session.descriptors),1)


if __name__=='__main__':unittest.main(verbosity=2)

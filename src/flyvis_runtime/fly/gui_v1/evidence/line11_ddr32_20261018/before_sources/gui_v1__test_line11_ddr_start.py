"""Focused CPU/mock orchestration only. Saved RTL bytes; no neural/device run."""
import ast
import copy
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

from line11_ddr_start import DdrGuiSession,check_operator
from line11_ddr_bridge import BIT_SHA,HWH_SHA,MANIFEST_SHA,INITIAL_BOUNDARY,digest,verify_release
import line11_ddr_board as board

EVIDENCE=Path(__file__).parent/'evidence/line11_ddr_start_20261018'


class StartupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.release,_=verify_release()
        sys.path.insert(0,str(cls.release))
        cls.replay=importlib.import_module('cpu_replay')

    def setUp(self):
        self.root=EVIDENCE/'cpu_cases'/uuid.uuid4().hex
        self.root.mkdir(parents=True)
        self.stream=DdrGuiSession(self.root,software_test=True)
        self.stream.package('http://192.0.2.1:8771')
        self.session,self.mmio,self.buffer=self.replay.session(self.release,self.root/'observations')
        self.operator=dict(schema='flyvis-line2-ddr-operator/v1',preparation_id=self.stream.preparation_id,
            evidence='CPU_MOCK_ONLY',exclusive_board_window=True,boot_id='11111111-2222-3333-4444-555555555555',
            bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,release_manifest_sha256=MANIFEST_SHA,
            pynq_version='2.7.0',machine='armv7l',clock=dict(clock_control=0x200500,io_pll_control=0x1e000,
                pll_status=4,reference_mhz=33.333333),hp0_read_control=0,hp0_write_control=0,
            cache_policy='CLEAR_FLUSH_DSB_BEFORE_ARM;INVALIDATE_DSB_IMMUTABLE_COPY_AFTER_PUBLISH',
            barrier_library_sha256='a'*64,initial_state_readback=INITIAL_BOUNDARY,
            startup_sha256={n:digest((Path(__file__).parent/n).read_bytes()) for n in
                ('line11_ddr_board.py','line11_ddr_bridge.py','line11_display_client.py')})

    def first_blob(self,changes=None,raw=None):
        data={n:(self.session.output/n).read_bytes() for n in
              ('record_000000.bin','receipt_000000.json','RUN_CONTEXT.json')}
        data['OPERATOR.json']=json.dumps(dict(self.operator,**(changes or {}))).encode()
        data['TIMING.json']=json.dumps(self.session.timing[0]).encode()
        if raw is not None:data['record_000000.bin']=raw
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
            for n,b in data.items():z.writestr(n,b)
        return out.getvalue()

    def prepare_one(self):
        self.session.start();self.session.produce_next();self.session.audit_next()

    def test_one_first_step_gate_then_two_steps_existing_GUI_no_browser_wait(self):
        owner=self;first_counts=[]
        class PC:
            def first(_,session,operator):
                first_counts.append(len(session.descriptors))
                return owner.stream.accept_first(owner.first_blob(),'Bearer '+owner.stream.preparation_token)['connection']
        class MemoryHTTP:
            def request(_,method,route,body,headers):
                _.reply=owner.stream.accept(body,headers['Authorization']) if route.endswith('/frame') else owner.stream.finish(json.loads(body),headers['Authorization'])
            def getresponse(_):return SimpleNamespace(status=200,read=lambda n:json.dumps(_.reply).encode())
            def close(_):pass
        with patch('line11_display_client.http.client.HTTPConnection',return_value=MemoryHTTP()):
            result=board.run_bounded(self.session,PC(),self.operator,self.release)
        self.assertEqual(first_counts,[1]);self.assertEqual(result['states_compared'],137007)
        self.assertEqual(self.stream.status()['status'],'FINISHED')
        self.assertEqual(self.stream.status()['received_steps'],2)
        self.assertEqual(self.stream.status()['browser_receipts'],0)
        packet=self.stream.latest()['frame']
        self.assertEqual(packet['display_kind'],'CPU_PROTOCOL_TEST_ONLY');self.assertIsNone(packet['flow'])
        self.assertEqual(len(packet['spatial']['values']),5768)
        self.assertEqual(packet['initial_state_readback'],INITIAL_BOUNDARY)
        self.assertEqual(sum(a==0 and v==1 for a,v in self.mmio.writes),3)
        self.assertEqual(self.buffer.free_calls,0)

    def test_first_rejected_means_no_second_step_and_retained_DDR(self):
        class PC:
            def first(_,s,op):raise OSError('CPU injected PC rejection/disconnect')
        with self.assertRaises(OSError):board.run_bounded(self.session,PC(),self.operator,self.release)
        self.assertEqual(len(self.session.descriptors),1)
        self.assertTrue(self.session.memory.armed);self.assertEqual(self.buffer.free_calls,0)

    def test_last_node_damage_even_with_valid_checksum_rejected(self):
        self.prepare_one();raw=bytearray((self.session.output/'record_000000.bin').read_bytes())
        raw[4096+45668*4]^=1
        struct.pack_into('<I',raw,13*4,self.stream.seed.codec.rolling(raw[4096:4096+182676]))
        with self.assertRaisesRegex(ValueError,'ALL_WORD_COMPARISON'):
            self.stream.accept_first(self.first_blob(raw=raw),'Bearer '+self.stream.preparation_token)
        self.assertEqual(self.stream.status()['status'],'FAILED')
        self.assertIsNone(self.stream.latest()['frame'])

    def test_wrong_scope_CPU_evidence_and_duplicate_admission_rejected(self):
        self.prepare_one()
        with self.assertRaisesRegex(ValueError,'BINDING'):
            check_operator(dict(self.operator,preparation_id='wrong'),self.stream.preparation_id,True)
        with self.assertRaisesRegex(ValueError,'OPERATOR_EVIDENCE'):
            check_operator(self.operator,self.stream.preparation_id,False)
        blob=self.first_blob();auth='Bearer '+self.stream.preparation_token
        self.stream.accept_first(blob,auth)
        with self.assertRaisesRegex(ValueError,'CLOSED'):self.stream.accept_first(blob,auth)
        with self.assertRaisesRegex(ValueError,'UNAUTHORIZED'):self.stream.authenticate_preparation('Bearer wrong')

    def test_bad_clock_HP0_or_startup_identity_rejected_before_admission(self):
        for change in [dict(hp0_write_control=1),dict(clock=dict(self.operator['clock'],pll_status=0))]:
            with self.subTest(change=change),self.assertRaises(ValueError):
                check_operator(dict(self.operator,**change),self.stream.preparation_id,True)
        self.prepare_one()
        with self.assertRaisesRegex(ValueError,'STARTUP_SOURCE_IDENTITY'):
            self.stream.accept_first(self.first_blob(dict(startup_sha256={})), 'Bearer '+self.stream.preparation_token)
        self.assertEqual(self.stream.count,0)

    def test_package_fresh_extract_default_verification_no_PYNQ_import(self):
        target=self.root/'extracted';target.mkdir()
        with zipfile.ZipFile(self.stream.link_path) as z:z.extractall(target)
        config=board.verify(target)
        self.assertFalse(config['board_operations_authorized'])
        self.assertEqual(config['total_steps'],3)
        nb=json.loads((target/'START_DDR.ipynb').read_text(encoding='utf-8'))
        self.assertEqual(len([x for x in nb['cells'] if x['cell_type']=='code']),1)
        self.assertNotIn('pynq',sys.modules)
        for name in ('line11_ddr_board.py','line11_display_client.py','line11_ddr_bridge.py'):
            ast.parse((target/name).read_text(encoding='utf-8'),feature_version=(3,8))
        (target/'line11_ddr_board.py').write_text('# changed',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'Startup source changed'):board.verify(target)

    def test_PC_unavailable_refused_before_hardware_imports(self):
        config={'url':'http://192.0.2.1:8771','token':'x','preparation_id':'x'}
        transport=SimpleNamespace(request=lambda *a,**k:(_ for _ in ()).throw(OSError('CPU offline')),close=lambda:None)
        with patch('line11_ddr_board.http.client.HTTPConnection',return_value=transport):
            with self.assertRaises(OSError):board.PreparationClient(config).ready()
        self.assertNotIn('pynq',sys.modules)

    def test_original_HTTP_handler_first_gate_remote_isolation_no_listener(self):
        from server import handler_factory
        self.prepare_one();handler=handler_factory(None,line11_stream=self.stream)
        obj=handler.__new__(handler);captured=[]
        obj.send=lambda data,mime=None,status=200,**kw:captured.append((status,data))
        obj.client_address=('192.0.2.10',1);obj.server=SimpleNamespace(server_address=('0.0.0.0',8771))
        obj.connection=SimpleNamespace(settimeout=lambda _:None)
        obj.path='/api/full-pl-stream/first';blob=self.first_blob()
        obj.rfile=io.BytesIO(blob);obj.headers={'Authorization':'Bearer '+self.stream.preparation_token,
            'Content-Type':'application/zip','Content-Length':str(len(blob))}
        obj.do_POST();self.assertEqual(captured[-1][0],200)
        self.assertEqual(captured[-1][1]['status'],'FIRST_STEP_ALL_WORDS_ACCEPTED_CONTINUE')
        obj.path='/';obj.do_GET();self.assertEqual(captured[-1][0],403)
        obj.path='/api/live-camera/start';obj.do_POST();self.assertEqual(captured[-1][0],403)

    def test_failure_after_loaded_seed_never_reopens_admission(self):
        self.prepare_one()
        self.stream.seed.admit(self.first_blob())
        self.stream.abort('CPU injected failure before admission ACK')
        with self.assertRaisesRegex(ValueError,'FAILED_NO_RETRY'):self.stream.prepare()
        self.assertEqual(self.stream.status()['status'],'FAILED')
        self.assertIsNone(self.stream.session_id)
        self.assertIsNone(self.stream.latest()['frame'])


if __name__=='__main__':unittest.main(verbosity=2)

"""CPU protocol fixtures: original DDR driver, saved three states, virtual60s.
Never opens a socket, camera, GPU, PYNQ or board. Mock flow is test-only.
"""
import ast
import base64
import importlib
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest

import numpy as np
from line11_live_camera import CameraDdrSession,CAPACITY,LIVE_FILES,digest,HERE
from line11_live_camera_board import run_window
from line11_ddr_bridge import verify_release,BIT_SHA,HWH_SHA,MANIFEST_SHA,INITIAL_BOUNDARY
from line11_live_cpu import audit_bits


class Feed:
    def init__(self,inputs,run):
        self.frames=inputs;self.run=run;self.ready=threading.Event();self.ready.set();self.error=None
        self.inputs=self;self.index=0;self.closed=False
    def start(self):pass
    def close(self):self.closed=True
    def status(self):return dict(captured=self.index,policy='CPU_FIXTURE_ONLY_LATEST')
    def freeze_for_step(self):
        k=self.index;self.index+=1
        # Small PNG is a transport fixture, never an acquired image or GUI experiment.
        png=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=')
        return dict(png=base64.b64encode(png).decode(),values=np.frombuffer(self.frames[k],dtype='<f4').tolist(),
            conversion=dict(backend='ORIGINAL_PREPARED_CAMERA_INPUT_BOXEYE_CPU',test_only=True),
            source=dict(run_id=self.run,source_kind='real_windows_camera',sequence=k,relative_s=k/30,
                received_monotonic_ns=1000000000+k*33333333,received_utc='CPU_FIXTURE_NOT_CAPTURED',
                timestamp_kind='Windows_receipt_not_sensor',png_sha256=digest(png),hex_values_sha256=digest(self.frames[k])))


class CPUConsumer:
    def init__(self,expected):
        self.expected=expected;self.ready=threading.Event();self.ready.set();self.accepted=self.completed=0
        self.error=None;self.state='READY';self.callback=None
    def start(self):pass
    def submit(self,snapshot):
        m,inp,bits,_,_=snapshot;k=m['frame_id']
        if bits!=self.expected[k]:self.error='CPU_FIXTURE_STATE_MISMATCH';raise ValueError(self.error)
        self.accepted+=1;self.completed+=1
        reg=json.loads((HERE/'live_registry.json').read_bytes())
        binding=dict(run_id=m['run_id'],session_id=m['session_id'],frame_id=k,full_state_sha256=digest(bits),
            decoder='DecoderGAVP',recursive_eval=True,decoder_source_sha256=reg['pins']['decoder']['sha256'],
            checkpoint_sha256=reg['pins']['checkpoint']['sha256'] if 'checkpoint' in reg['pins'] else 'd0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f')
        values=np.zeros((2,721),dtype='<f4')  # Mock decoder, explicitly CPU-only.
        self.callback(snapshot,dict(values=values.tolist(),sha256=digest(values.tobytes()),binding=binding))
    def status(self):return dict(status=self.state,accepted=self.accepted,decoded=self.completed,pending=0,error=self.error)
    def finish_input(self):self.state='COMPLETE'
    def close(self):pass


class LiveCameraTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.release,_=verify_release();sys.path.insert(0,str(cls.release))
        cls.replay=importlib.import_module('cpu_replay')
        from offline_check import plan
        cls.inputs,cls.expected=plan(cls.release)

    def setUp(self):
        cases=HERE/'evidence/line11_live_camera60_20261018/cpu_cases';cases.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=cases);self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.now=1_000_000_000
        self.feed=Feed(self.inputs,'unset');self.consumer=CPUConsumer(self.expected)
        self.session=CameraDdrSession(self.root/'PC',software_test=True,capture=self.feed,consumer=self.consumer,clock=lambda:self.now)
        self.feed.run=self.session.preparation_id;self.consumer.callback=self.session._flow_ready
        self.session.package('http://192.0.2.1:8771')
        self.operator=dict(schema='flyvis-line2-ddr-operator/v1',preparation_id=self.session.preparation_id,
            evidence='CPU_MOCK_ONLY',exclusive_board_window=True,boot_id='11111111-2222-3333-4444-555555555555',
            bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,release_manifest_sha256=MANIFEST_SHA,pynq_version='2.7.0',machine='armv7l',
            clock=dict(clock_control=0x200500,io_pll_control=0x1e000,pll_status=4,reference_mhz=33.333333),
            hp0_read_control=0,hp0_write_control=0,barrier_library_sha256='a'*64,
            cache_policy='CLEAR_FLUSH_DSB_BEFORE_ARM;INVALIDATE_DSB_IMMUTABLE_COPY_AFTER_PUBLISH',initial_state_readback=INITIAL_BOUNDARY,
            startup_sha256={n:digest((HERE/n).read_bytes()) for n in LIVE_FILES})

    def run_three(self,*,tamper=False,stop=False):
        from ddr_control import DdrControl,STRIDE
        b=self.replay.Buffer(3*STRIDE);b.nbytes=CAPACITY*STRIDE
        mmio=self.replay.MMIO(b,(self.release/'cpu_fixture_ddr.bin').read_bytes());control=DdrControl(mmio)
        class Memory:
            base=b.physical_address;size=CAPACITY*STRIDE;armed=False
            def pin_before_configure(_):_.armed=True
            def copy_record(_,p):
                start=p.address-b.physical_address
                return bytes(b.ddr[start:start+STRIDE])
        session=self.session;owner=self
        session.ready_board({'preparation_id':session.preparation_id})
        class PC:
            def post(_,route,payload,mime):
                if route.endswith('camera-input'):return session.begin_input(json.loads(payload))
                if route.endswith('camera-record'):
                    owner.now+=20_000_000_000
                    if stop:session.requested_stop=True
                    if tamper:
                        blob=bytearray(payload);blob[-2000]^=1;payload=bytes(blob)
                    return session.receive_camera(payload)
                return session.end_camera(json.loads(payload))
        out=self.root/'PS';out.mkdir()
        config=dict(total_steps=CAPACITY,preparation_id=session.preparation_id)
        result=run_window(control,Memory(),PC(),config,self.operator,out)
        return result,mmio,b

    def test_virtual60_three_real_saved_states_feedback_and_synchronized_output(self):
        result,mmio,b=self.run_three()
        self.assertEqual(result['completed_steps'],3);self.assertEqual(result['PC_window']['reason'],'WALL_60S')
        self.assertEqual(mmio.reg[0x14],3);self.assertFalse(mmio.reg[0x10]&8)  # normal PARTIAL window, no fake full flag
        self.assertEqual(self.session.status()['status'],'FINISHED');self.assertEqual(self.consumer.completed,3)
        frame=self.session.latest()['frame'];self.assertEqual(frame['step_id'],2)
        self.assertEqual(frame['source']['source_frame'],2);self.assertEqual(frame['activity_time_s'],.015)
        self.assertEqual(frame['spatial']['values_sha256'],digest(self.session.seed.spatial.extract(np.frombuffer(self.expected[2],dtype='<f4')).tobytes()))
        self.assertEqual(self.session.source_frame(2,frame['run_id'],frame['full_state_sha256']),(self.session.output/'source_frames/000002.png').read_bytes())
        self.assertEqual(len(list((self.session.output/'raw_records').glob('*.bin'))),3)
        self.assertEqual(sum(a==0 and v==2 for a,v in mmio.writes),1);self.assertEqual(b.free_calls,0)
        self.assertEqual(frame['display_kind'],'CPU_PROTOCOL_TEST_ONLY')

    def test_stop_at_committed_boundary_and_retains_actual_last_state(self):
        result,mmio,b=self.run_three(stop=True)
        self.assertEqual(result['completed_steps'],1);self.assertEqual(result['PC_window']['reason'],'USER_STOP')
        self.assertEqual(mmio.reg[0x14],1);self.assertEqual(b.free_calls,0)

    def test_changed_snapshot_rejected_without_second_step_or_software_fallback(self):
        with self.assertRaises(ValueError):self.run_three(tamper=True)
        self.assertEqual(self.consumer.completed,0);self.assertFalse(self.session.first_verified)

    def test_camera_notebook_python38_scope_and_live_board_entry(self):
        from line11_ddr_notebook import export_notebook,notebook_bundle,installation
        pc=self.root/'notebook_PC';pc.mkdir()
        for name in LIVE_FILES:(pc/name).write_bytes((HERE/name).read_bytes())
        path=export_notebook('http://192.168.2.89:8771',pc,camera_live=True)
        nb=json.loads(path.read_bytes());entry=nb['metadata']['flyvis_pure_fpga'];self.assertTrue(entry['camera_live'])
        ast.parse(entry['source'],feature_version=(3,8));cells=[c for c in nb['cells'] if c['cell_type']=='code'];self.assertEqual(len(cells),1)
        ast.parse(''.join(cells[0]['source']),feature_version=(3,8))
        m=notebook_bundle(self.session,'Bearer '+installation(pc)['pairing_key'],{'op':'manifest'},pc)
        self.assertTrue(m['camera_live']);self.assertEqual(m['steps'],CAPACITY)

    def test_CPU_independent_audit_detects_complete_state_difference(self):
        fake=SimpleNamespace(advance=lambda x:np.frombuffer(self.expected[0],dtype='<f4'))
        audit_bits(fake,self.inputs[0],self.expected[0])
        bad=bytearray(self.expected[0]);bad[150000]^=1
        with self.assertRaisesRegex(ValueError,'45669_STATE_BIT_MISMATCH'):audit_bits(fake,self.inputs[0],bytes(bad))


if __name__=='__main__':unittest.main(verbosity=2)

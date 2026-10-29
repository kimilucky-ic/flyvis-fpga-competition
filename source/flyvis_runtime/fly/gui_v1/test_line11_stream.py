"""CPU/in-memory transport ONLY. Frozen saved arrays are not new PL activity."""
import copy
import io
import json
from pathlib import Path
from types import SimpleNamespace
import struct
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import numpy as np
from line11_display_client import Line11DisplayClient
from line11_result import FullPLResult,digest
from line11_stream import FullPLStream
from live_protocol import HERE,load
from test_line11_result import fixture


def wire(config, inp, state, k=1, **changes):
    header=dict(schema='flyvis-line11-state-stream/v1',session_id=config['session_id'],run_id=config['run_id'],
        boot_id=config['boot_id'],frame_id=k,completed_steps=k+1,previous_state_sha256=config['seed_state_sha256'],
        input_sha256=digest(inp),state_sha256=digest(state),faults=0,compute_cycles=2201418,clock_hz=100000000,elapsed_seconds=.03)
    header.update(changes);raw=json.dumps(header).encode()
    return struct.pack('<I',len(raw))+raw+inp+state


class StreamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent=HERE/'evidence/line11_stream_20261018'
        cls.temp=tempfile.TemporaryDirectory(dir=parent)
        assert Path(cls.temp.name).resolve().is_relative_to(parent.resolve())
        files,_=fixture();cls.files=files
        path=Path(cls.temp.name)/'CPU_PROTOCOL_FIXTURE_ONLY.zip'
        with zipfile.ZipFile(path,'w') as z:
            for name,data in files.items():z.writestr(name,data)
        cls.seed=FullPLResult(path);cls.seed.frame()
        cls.inp,cls.state=files['actual_input.bin'],files['actual_state1.bin']

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def make(self,limit=32):
        clock=SimpleNamespace(now=1_000_000_000)
        stream=FullPLStream(self.seed,True,limit,clock=lambda:clock.now)
        config=stream.connection('http://192.0.2.1:8771')  # documentation-only address, never connected
        return stream,config,'Bearer '+config['token'],clock

    def test_gate_and_unauthorized_cannot_open_or_poison(self):
        blocked=FullPLStream(FullPLResult(),True)
        self.assertFalse(blocked.status()['first_step_accepted'])
        with self.assertRaises(ValueError):blocked.connection('http://192.0.2.1:8771')
        stream,config,auth,_=self.make()
        with self.assertRaises(ValueError):stream.accept(wire(config,self.inp,self.state),'Bearer WRONG')
        self.assertEqual(stream.status()['status'],'READY_WAITING_PRODUCER')

    def test_32_ordered_states_latest_only_and_same_source_input(self):
        stream,config,auth,_=self.make()
        for k in range(1,33):stream.accept(wire(config,self.inp,self.state,k),auth)
        latest=stream.latest();p=latest['frame']
        self.assertEqual(p['step_id'],32);self.assertEqual(latest['status']['received_steps'],32)
        self.assertEqual(p['input_time_s'],32*.005);self.assertEqual(p['activity_time_s'],33*.005)
        self.assertEqual(p['full_state_sha256'],digest(self.state))
        self.assertEqual(p['spatial']['values'],self.seed.spatial.extract(np.frombuffer(self.state,dtype='<f4')).tolist())
        self.assertIsNone(p['flow']);self.assertFalse(latest['status']['all_steps_persisted'])
        self.assertIsNone(stream.latest(after=p['revision'])['frame'])
        receipt=dict(session_id=config['session_id'],run_id=config['run_id'],frame_id=32,full_state_sha256=digest(self.state),
                     receive_to_draw_lower_ms=1.,receive_to_draw_upper_ms=3.)
        stream.paint(receipt)
        self.assertEqual(stream.status()['display_skipped_steps'],31)
        self.assertFalse(stream.paint(receipt)['neural_commit'])

    def test_bad_identity_sequence_chain_counter_and_nonfinite_withdraw(self):
        for changes in [dict(run_id='OTHER'),dict(boot_id='OTHER'),dict(frame_id=2),dict(completed_steps=3),
                        dict(previous_state_sha256='0'*64),dict(faults=1),dict(clock_hz=150000000),dict(elapsed_seconds=float('nan'))]:
            stream,config,auth,_=self.make()
            with self.subTest(changes=changes),self.assertRaises(ValueError):stream.accept(wire(config,self.inp,self.state,**changes),auth)
            self.assertEqual(stream.status()['status'],'FAILED');self.assertIsNone(stream.latest()['frame'])
        stream,config,auth,_=self.make();bad=bytearray(self.state);struct.pack_into('<f',bad,0,float('inf'))
        with self.assertRaisesRegex(ValueError,'NONFINITE'):stream.accept(wire(config,self.inp,bytes(bad)),auth)

    def test_duplicate_truncation_and_window_excess_stop(self):
        stream,config,auth,_=self.make(limit=1)
        stream.accept(wire(config,self.inp,self.state),auth)
        with self.assertRaises(ValueError):stream.accept(wire(config,self.inp,self.state),auth)
        self.assertFalse(stream.status()['result_valid'])
        stream,config,auth,_=self.make(limit=1)
        stream.accept(wire(config,self.inp,self.state),auth)
        with self.assertRaises(ValueError):stream.accept(wire(config,self.inp,self.state,2),auth)
        stream,config,auth,_=self.make()
        with self.assertRaisesRegex(ValueError,'LENGTH'):stream.accept(wire(config,self.inp,self.state)[:-4],auth)

    def test_timeout_withdraws_and_finish_changes_final_label(self):
        stream,config,auth,clock=self.make()
        stream.accept(wire(config,self.inp,self.state),auth);clock.now+=31_000_000_000
        self.assertEqual(stream.status()['status'],'FAILED');self.assertIsNone(stream.latest()['frame'])
        stream,config,auth,_=self.make();stream.accept(wire(config,self.inp,self.state),auth)
        rev=stream.latest()['frame']['revision']
        result=stream.finish(dict(session_id=config['session_id'],run_id=config['run_id'],received_steps=1,last_frame_id=1,full_state_sha256=digest(self.state)),auth)
        self.assertEqual(result['whole_run_acceptance'],'PENDING')
        self.assertEqual(stream.latest(after=rev)['frame']['display_kind'],'FINISHED_FULL_PL_LAST_STATE')
        with self.assertRaises(ValueError):stream.accept(wire(config,self.inp,self.state,2),auth)

    def test_optional_flow_never_merges_other_step(self):
        stream,config,auth,_=self.make();stream.accept(wire(config,self.inp,self.state),auth)
        state=stream.complete_state_for_decoder();self.assertEqual(state['state_bits'],self.state)
        binding={k:v for k,v in state.items() if k!='state_bits'}
        binding.update(decoder='DecoderGAVP',decoder_source_sha256=load(HERE/'live_registry.json')['pins']['decoder']['sha256'],
                       checkpoint_sha256=stream.anchor['model']['checkpoint_sha256'],recursive_eval=True)
        # Saved values only test the envelope. No decoder/neural inference occurs.
        saved=np.load(HERE/'evidence/minimal_gpu_software32_20261018/official_flow.npy',allow_pickle=False)[0]
        bad=dict(binding,frame_id=0)
        with self.assertRaisesRegex(ValueError,'STATE_BINDING'):stream.attach_flow(bad,saved)
        stream.attach_flow(binding,saved)
        self.assertEqual(stream.latest()['frame']['flow_sha256'],digest(np.asarray(saved,dtype='<f4').tobytes()))
        stream.accept(wire(config,self.inp,self.state,2),auth)
        self.assertIsNone(stream.latest()['frame']['flow'])
        with self.assertRaises(ValueError):stream.attach_flow(binding,saved)

    def test_client_reuses_connection_and_never_waits_for_browser(self):
        stream,config,auth,_=self.make();calls=[]
        class MemoryHTTP:
            def request(_,method,route,body,headers):
                calls.append((method,route))
                _.response=stream.accept(body,headers['Authorization']) if route.endswith('/frame') else stream.finish(json.loads(body),headers['Authorization'])
            def getresponse(_):return SimpleNamespace(status=200,read=lambda n:json.dumps(_.response).encode())
            def close(_):pass
        with patch('line11_display_client.http.client.HTTPConnection',return_value=MemoryHTTP()) as constructor:
            client=Line11DisplayClient(config)
            client.bind_retained_state(self.state,1,config['boot_id'])
            for k in range(1,4):client(SimpleNamespace(frame_id=k,completed_steps=k+1,input_bits=self.inp,state_bits=self.state,compute_cycles=2201418,elapsed_seconds=.03))
            client.finish()
            self.assertEqual(constructor.call_count,1)
        self.assertEqual(len(calls),4);self.assertEqual(stream.status()['received_steps'],3)
        self.assertEqual(stream.status()['browser_receipts'],0)

    def test_client_disconnect_and_retained_state_mismatch_no_retry(self):
        _,config,_,_=self.make()
        transport=SimpleNamespace(request=lambda *a,**kw:(_ for _ in ()).throw(OSError('CPU simulated disconnect')),close=lambda:None)
        with patch('line11_display_client.http.client.HTTPConnection',return_value=transport):
            client=Line11DisplayClient(config)
            with self.assertRaises(RuntimeError):client.bind_retained_state(self.state,2,config['boot_id'])
            client=Line11DisplayClient(config);client.bind_retained_state(self.state,1,config['boot_id'])
            frame=SimpleNamespace(frame_id=1,completed_steps=2,input_bits=self.inp,state_bits=self.state,compute_cycles=2201418,elapsed_seconds=.03)
            with self.assertRaises(OSError):client(frame)
            with self.assertRaises(RuntimeError):client(frame)
            self.assertTrue(client.failed)

    def test_original_handler_remote_isolation_and_binary_ingress_without_listening(self):
        from server import handler_factory
        stream,config,auth,_=self.make()
        handler=handler_factory(None,line11_stream=stream)
        obj=handler.__new__(handler);captured=[]
        obj.send=lambda data,mime=None,status=200,**kw:captured.append((status,data))
        obj.client_address=('192.0.2.10',123);obj.server=SimpleNamespace(server_address=('0.0.0.0',8771))
        obj.path='/';obj.do_GET();self.assertEqual(captured[-1][0],403)
        obj.path='/api/live-camera/start';obj.do_POST();self.assertEqual(captured[-1][0],403)
        body=wire(config,self.inp,self.state);obj.path='/api/full-pl-stream/frame'
        obj.headers={'Authorization':auth,'Content-Length':str(len(body)),'Content-Type':'application/octet-stream'}
        obj.rfile=io.BytesIO(body);obj.connection=SimpleNamespace(settimeout=lambda n:None)
        obj.do_POST();self.assertEqual(captured[-1][0],200)
        self.assertEqual(obj.protocol_version,'HTTP/1.1');self.assertFalse(obj.close_connection)
        self.assertEqual(stream.status()['received_steps'],1)
        obj.client_address=('127.0.0.1',123);obj.path='/api/full-pl-stream/status';obj.do_GET()
        self.assertEqual(captured[-1][1]['status'],'RECEIVING')


if __name__=='__main__':unittest.main(verbosity=2)

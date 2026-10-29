"""CPU protocol tests on SAVED real joint arrays. No CUDA/camera/board/socket."""
import base64
import copy
import dataclasses
from datetime import datetime, timedelta, timezone
import io
import json
from pathlib import Path
import tempfile
import time
import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from PIL import Image
from live_protocol import HERE, Registry, load
from live_worker import import_file
from hybrid_full485 import Full485Contract
from joint_camera_protocol import (TEST, LIVE, PROFILE, POLICY, digest, frame_check,
    LatestCameraInput, validate_scope, validate_snapshot)
from joint_camera_engine import CameraJointEngine, JointCameraEvidence
from joint_camera_control import CameraHardwareControl, require_camera_service
from joint_camera_bridge import JointCameraBridge

BASE=HERE.parent.parent/'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/joint_latency485_20261016'
SAVED_RUN='c708f1c9bac14c07ac8f56d59678b95a'
RUN='01'*16
SID='02'*16


def item(values, seq=0, kind='recorded_protocol_fixture'):
    buf=io.BytesIO();Image.new('RGB',(8,8),(127,127,127)).save(buf,format='PNG')
    raw=buf.getvalue();x=np.asarray(values,dtype='<f4')
    return dict(source=dict(run_id=RUN,source_kind=kind,sequence=seq,received_monotonic_ns=time.perf_counter_ns(),
        relative_s=seq*.1,png_sha256=digest(raw),hex_values_sha256=digest(x.tobytes()),timestamp_kind='Windows_receipt_not_sensor'),
        png=base64.b64encode(raw).decode(),values=x.tolist(),
        conversion=dict(backend='ORIGINAL_PREPARED_CAMERA_INPUT_BOXEYE_CPU',dependencies_sha256='1'*64))


class SavedHardwareFixture:
    """Never admitted as hardware. Returns historical bytes for CPU control tests."""
    def init__(self,c,reader):
        self.c,self.reader=c,reader;self.w=c.wire;self.asid=bytes.fromhex('12'*16)
        self.attestation=dict(boot_id='CPU_ONLY',server_session='CPU_ONLY')
        self.requests=[];self.commits=[];self.closed=False;self.lose_ack=False;self.wrong_ack=False
        self.before_ack=lambda:None
    def step(self,old,chemical,x,identity):
        k=identity['step'];payload=old+chemical+x
        expected=self.reader.read(f'request_{k}.bin')[256:]
        np.testing.assert_array_equal(np.frombuffer(payload,dtype='<i4'),np.frombuffer(expected,dtype='<i4'))
        self.header=self.w.Header(self.w.STEP,payload_bytes=len(payload),payload_sha=self.w.digest(payload),**identity)
        self.requests.append(payload)
        candidate=self.reader.read(f'candidate_{k}.bin')
        return candidate,dataclasses.replace(self.header,op=self.w.RESULT,payload_bytes=len(candidate),
            payload_sha=self.w.digest(candidate),compute_cycles=57681,transfer_cycles=83024)
    def commit(self,decision):
        self.commits.append(decision);self.before_ack()
        if self.lose_ack:raise TimeoutError('CPU_FIXTURE_ACK_LOST')
        h=dataclasses.replace(self.header,op=self.w.ACK,payload_bytes=0,payload_sha=self.w.digest(b''),parent_commit=decision)
        return dataclasses.replace(h,step=h.step+1) if self.wrong_ack else h
    def close(self):self.closed=True


class CameraJointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=Full485Contract()
        cls.journal=import_file('camera_test_reader_only',BASE/'a3latency485/evidence_journal.py')
        cls.reader=cls.journal.JournalReader(BASE/'workers'/SAVED_RUN/'pc/evidence.fvej')
    @classmethod
    def a(cls,name):return np.load(io.BytesIO(cls.reader.read(name)),allow_pickle=False)
    def setUp(self):
        folder=HERE/'evidence/camera_joint_20261016/cpu_runs'/uuid.uuid4().hex
        folder.mkdir(parents=True)
        self.temp=SimpleNamespace(name=str(folder))  # Keep fixture/failure evidence in this lane.
        self.ev=JointCameraEvidence(self.journal.JournalWriter(Path(self.temp.name)/'pc',dict(role='CPU_TEST')),3)
        self.hw=SavedHardwareFixture(self.c,self.reader);self.decode_fail=False;self.reference_calls=[]
        self.identity=dict(run_id=RUN,session_id=SID,comparison_id='CPU_CURRENT_INPUT',condition_id='CURRENT_CAMERA',max_steps=3,
            model=self.c.registry['model'],mapping_sha256=self.c.mapping_sha,
            hardware=dict(ASID=self.hw.asid.hex(),boot_id='CPU_ONLY',server_session='CPU_ONLY',bit_sha256=self.c.wire.BIT_SHA,hwh_sha256=self.c.wire.HWH_SHA))
        def produce(old,frame,k):
            np.testing.assert_array_equal(old,self.a(f'old_full_{k}.npy'))
            np.testing.assert_array_equal(frame,self.a(f'input_721_{k}.npy'))
            return dict(chemical_H=self.a(f'chemical_{k}.npy'),new_R=self.a(f'R_candidate_{k}.npy'),r_ids=self.c.r,x_full=self.x(frame))
        def decode(full):
            if self.decode_fail:raise ValueError('CPU_DECODE_FAILED')
            k=len(self.hw.commits)-1
            np.testing.assert_array_equal(full,self.a(f'committed_full_{k}.npy'))
            return self.a(f'flow_{k}.npy')
        def ref(old,frame,out,k):
            self.reference_calls.append((frame.copy(),k));return dict(status='CPU_SAVED_REFERENCE_ONLY')
        self.engine=CameraJointEngine(self.c,self.hw,produce,decode,self.ev,self.identity,lambda:None,
            lambda full:full.copy(),lambda value:value,ref)
    def tearDown(self):
        if not self.ev.writer.closed:self.ev.writer.abandon()
    def x(self,frame):
        reg=Registry()
        with np.load(reg.path_for('parameters'),allow_pickle=False) as z:ids=z['input_node_index']
        out=np.zeros(45669,dtype=np.float32);out[ids]=frame;return out
    def current(self,k):return item(self.a(f'input_721_{k}.npy'),k)
    def test_three_step_original_coordinator_feedback_and_durable_snapshots(self):
        old=self.engine.barrier.state.copy()
        phases=[];self.engine.progress=lambda phase,step:phases.append((phase,step))
        exchanges=[];self.engine.exchange_started=lambda:exchanges.append(phases[-1])
        for k in range(3):
            self.hw.before_ack=lambda:np.testing.assert_array_equal(self.engine.barrier.state,old)
            p=self.engine.step(self.current(k))
            validate_snapshot(p,self.identity,self.c.spatial,allow_test=True)
            self.assertEqual(p['execution_kind'],TEST);self.assertEqual(p['PL_proven_global_ids'],[])
            self.assertEqual(self.engine.barrier.state_token,k+1)
            np.testing.assert_array_equal(self.engine.barrier.publication,self.a(f'committed_full_{k}.npy'))
            if k:self.assertEqual(self.hw.requests[k][:23072],self.reader.read(f'candidate_{k-1}.bin'))
            old=self.engine.barrier.state.copy()
        self.assertEqual(len(self.reference_calls),3)
        self.assertEqual(exchanges,[(phase,k) for k in range(3) for phase in
            ('STEP_EXCHANGE_WAIT_CANDIDATE','COMMIT_EXCHANGE_WAIT_ACK')])
        self.assertEqual([p for p,k in phases if k==0],['GPU_CHEMICAL_R','STEP_EXCHANGE_WAIT_CANDIDATE',
            'VERIFYING_PL_AND_R_CANDIDATES','COMMIT_EXCHANGE_WAIT_ACK','ACK_MATCHED_DECODING_COMMITTED_STATE','STEP_PUBLISHED_DURABLE'])
        with self.assertRaisesRegex(ValueError,'LIMIT'):self.engine.step(self.current(2))
    def test_missing_ack_never_publishes_or_retries(self):
        old=self.engine.barrier.state.copy();self.hw.lose_ack=True
        with self.assertRaises(TimeoutError):self.engine.step(self.current(0))
        np.testing.assert_array_equal(old,self.engine.barrier.state)
        self.assertEqual(self.engine.barrier.phase,'IN_DOUBT');self.assertTrue(self.hw.closed)
        with self.assertRaises(ValueError):self.engine.step(self.current(0))
        self.assertEqual(len(self.hw.requests),1)
    def test_wrong_ack_rejects_publication(self):
        self.hw.wrong_ack=True
        with self.assertRaisesRegex(ValueError,'ACK'):self.engine.step(self.current(0))
        self.assertEqual(self.engine.barrier.state_token,0)
    def test_precommit_fsync_failure_sends_no_commit(self):
        def reject(fd):raise OSError('CPU_FSYNC_FAILURE')
        self.ev.writer.sync_fn=reject
        with self.assertRaises(OSError):self.engine.step(self.current(0))
        self.assertEqual(self.hw.commits,[]);self.assertEqual(self.engine.barrier.state_token,0)
    def test_decoder_failure_preserves_commit_but_has_no_snapshot(self):
        self.decode_fail=True
        with self.assertRaisesRegex(ValueError,'DECODE'):self.engine.step(self.current(0))
        self.assertEqual(self.engine.barrier.state_token,1);self.assertEqual(self.ev.completed,0)
    def test_reentrant_update_refused(self):
        self.engine.owner.acquire()
        try:
            with self.assertRaisesRegex(ValueError,'IN_PROGRESS'):self.engine.step(self.current(0))
        finally:self.engine.owner.release()
    def test_input_tampering_refused_before_step(self):
        p=self.current(0);p['values'][0]+=.01
        with self.assertRaisesRegex(ValueError,'SHA'):self.engine.step(p)
        self.assertEqual(self.hw.requests,[])
    def test_test_snapshot_cannot_be_live(self):
        p=self.engine.step(self.current(0))
        with self.assertRaisesRegex(ValueError,'NOT_LIVE'):validate_snapshot(p,self.identity,self.c.spatial)
    def test_snapshot_corruption_and_false_final_pass(self):
        p=self.engine.step(self.current(0))
        changes=[lambda q:q['flow'][0].__setitem__(0,999),lambda q:q.__setitem__('whole_run_acceptance','PASS'),
            lambda q:q['durable'].__setitem__('barrier','COMMIT_INTENT'),lambda q:q.__setitem__('run_id','ff'*16),
            lambda q:q['source'].__setitem__('png_sha256','0'*64)]
        for mutate in changes:
            q=copy.deepcopy(p);mutate(q)
            with self.assertRaises(ValueError):validate_snapshot(q,self.identity,self.c.spatial,allow_test=True)


class InputAndAdmissionTests(unittest.TestCase):
    def test_mailboxes_coalesce_sources_without_queuing_model_steps(self):
        m=LatestCameraInput(RUN,'recorded_protocol_fixture')
        for k in range(10):
            raw=item(np.full(721,.5,dtype=np.float32),k);raw.pop('values');raw.pop('conversion');m.receive(raw)
        self.assertEqual(m.status()['raw_pending'],1);self.assertEqual(m.status()['dropped_before_conversion'],9)
        selected=m.take_raw();converted=item(np.full(721,.5,dtype=np.float32),9)
        converted['source'].update(selected['source']);m.accept_conversion(converted)
        a=m.freeze_for_step();a['values'][0]=123
        self.assertEqual(m.freeze_for_step()['values'][0],.5);self.assertEqual(m.status()['held_steps'],1)
    def test_unsolicited_or_rebound_conversion_rejected(self):
        m=LatestCameraInput(RUN,'recorded_protocol_fixture');p=item(np.full(721,.5,dtype=np.float32))
        with self.assertRaisesRegex(ValueError,'UNSOLICITED'):m.accept_conversion(p)
        raw=copy.deepcopy(p);raw.pop('values');raw.pop('conversion');m.receive(raw);m.take_raw()
        p['source']['received_monotonic_ns']+=1
        with self.assertRaisesRegex(ValueError,'SOURCE_CHANGED'):m.accept_conversion(p)
    def test_missing_hardware_does_not_create_connections(self):
        with patch('socket.create_connection') as connect:
            bridge=JointCameraBridge();self.assertEqual(bridge.status()['status'],'NOT_CONNECTED')
            with self.assertRaises(ValueError):bridge.start({})
            connect.assert_not_called()
    def test_old_hardware_documentation_is_not_camera_service(self):
        old=load(BASE.parent/'handoff_line2_camera_20261016/INTERFACE.json')
        with self.assertRaisesRegex(ValueError,'NOT_AVAILABLE'):require_camera_service(old,{})
    def test_draft_or_expired_scope_cannot_execute(self):
        with self.assertRaisesRegex(ValueError,'NOT_AUTHORIZED'):validate_scope(dict(schema='flyvis-camera-joint-scope/v1',status='DRAFT_NOT_AUTHORIZED'))
    def test_old_camera_full_gate_keeps_rejecting_pl(self):
        from stream_bridge import StreamBridge
        b=object.__new__(StreamBridge)
        b.control=dict(session_id=SID,run_id=RUN,source_kind='real_windows_camera',binding={})
        p=dict(schema='flyvis-continuous-output/v1',session_id=SID,run_id=RUN,source_kind='real_windows_camera',binding={},
            state_token=1,step_id=0,device=dict(type='cuda'),actual_new_computation=True,PL_execution=True)
        with self.assertRaisesRegex(ValueError,'ACTUAL_GPU_REQUIRED'):b.validate(p)


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.h=dict(run_id=RUN,server_session='03'*16,boot_id='CPU_BOOT',plan_sha256='a'*64,bit_sha256='b'*64,hwh_sha256='c'*64,listener_id='CPU_LISTENER')
        self.s=dict(self.h,max_steps=3,allow_zero_step_cancel=True)
        self.calls=[];self.bad_finish=False
        outer=self
        class Client:
            def request(self,path,body=None):
                outer.calls.append((path,body))
                v=dict(outer.h,state='BOARD_PREPARED',error=None,poisoned=False,pending=False,service_alive=True,requests=0,commits=0,neural_connections=0,
                    camera_joint_contract='flyvis-camera-joint/v1',normal_finish='finish_window/v1')
                if path=='/start':v.update(state='ARMED',identity=body['identity'])
                if path=='/finish_window':v.update(state='FINISHED_PENDING_AUDIT',identity=body['identity'],completed_steps=body['completed_steps']+(1 if outer.bad_finish else 0),
                    last_unified_commit_sha256=body['last_unified_commit_sha256'],last_txn=body['last_txn'],capture_closed=True,PS_capture_sha256='d'*64,
                    requests=body['completed_steps'],commits=body['completed_steps'])
                return v
        self.control=CameraHardwareControl(Client(),self.h,self.s,'e'*64)
        self.ready=dict(status='GPU_READY',board_connected=False,waiting_for='BOARD_READY.json',run_id=RUN,server_session=self.h['server_session'],scope_sha256='e'*64)
    def test_single_authenticated_start_then_bounded_finish(self):
        self.control.prepared();self.control.start(self.ready,30)
        self.control.finish(3,'f'*64,'04'*16,'USER_STOP')
        self.assertEqual([p for p,_ in self.calls],['/status','/start','/finish_window'])
        with self.assertRaises(ValueError):self.control.start(self.ready,30)
        with self.assertRaises(ValueError):self.control.finish(3,'f'*64,'04'*16,'USER_STOP')
    def test_finish_count_mismatch_is_not_retried(self):
        self.control.start(self.ready,30);self.bad_finish=True
        with self.assertRaisesRegex(ValueError,'MISMATCH'):self.control.finish(3,'f'*64,'04'*16,'USER_STOP')
        with self.assertRaises(ValueError):self.control.finish(3,'f'*64,'04'*16,'USER_STOP')
        self.assertEqual(sum(p=='/finish_window' for p,_ in self.calls),1)
    def test_status_wrong_boot_rejected(self):
        s=dict(self.h,boot_id='WRONG')
        with self.assertRaises(ValueError):self.control.check_status(s)
    def test_bad_gpu_ready_does_not_send_start(self):
        with self.assertRaisesRegex(ValueError,'GPU_READY'):self.control.start({},30)
        self.assertEqual(self.calls,[])
    def test_over_limit_finish_not_sent(self):
        self.control.start(self.ready,30)
        with self.assertRaisesRegex(ValueError,'COUNT'):self.control.finish(4,'f'*64,'04'*16,'USER_STOP')
        self.assertEqual(sum(p=='/finish_window' for p,_ in self.calls),0)


class OriginalGUIRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from data_store import DataStore
        from server import handler_factory
        cls.store=DataStore()
        cls.Handler=handler_factory(cls.store)
    def request(self,path,method='GET',body=None,origin='http://127.0.0.1:8771'):
        h=object.__new__(self.Handler)
        raw=json.dumps(body or {}).encode()
        h.path=path;h.rfile=io.BytesIO(raw)
        h.server=SimpleNamespace(server_address=('127.0.0.1',8771))
        h.headers={'Host':'127.0.0.1:8771','Origin':origin,'Content-Length':str(len(raw)),'Content-Type':'application/json'}
        answers=[]
        h.send=lambda value,*args,**kwargs:answers.append((value,kwargs.get('status',200)))
        getattr(h,'do_'+method)()
        return answers[0]
    def test_joint_default_disconnected_and_original_55_unchanged(self):
        result,code=self.request('/api/joint-camera/status')
        self.assertEqual((code,result['status']),(200,'NOT_CONNECTED'))
        catalog,code=self.request('/api/catalog')
        self.assertEqual(sum(len(d['conditions']) for d in catalog['datasets']),55)
    def test_missing_hardware_prepare_does_not_launch(self):
        with patch('subprocess.Popen') as spawn,patch('socket.create_connection') as connect:
            result,code=self.request('/api/joint-camera/prepare','POST')
            self.assertEqual(code,409);spawn.assert_not_called();connect.assert_not_called()
    def test_same_origin_post_required(self):
        result,code=self.request('/api/joint-camera/start','POST',origin='http://untrusted.invalid')
        self.assertEqual(code,409);self.assertIn('SAME_ORIGIN',result['error'])
    def test_static_joint_script_is_original_gui_route(self):
        result,code=self.request('/competition_joint.js')
        self.assertEqual(code,200);self.assertIn(b'FlyVisJointCameraProtocol',result)


class HubLifecycleTests(unittest.TestCase):
    def test_normal_stop_waits_for_worker_ack_and_revokes_latest(self):
        from joint_camera_runtime import JointCameraHub
        hub=JointCameraHub(dict(run_id=RUN,session_id=SID,camera_id=0),SimpleNamespace())
        hub.gpu_ready=hub.converter_ready=True
        hub.dispatch('bridge','start',dict(run_id=RUN,session_id=SID,camera_id=0))
        status=hub.dispatch('bridge','stop',None)
        self.assertTrue(status['stopping']);self.assertFalse(status['stop_acknowledged'])
        self.assertIsNone(hub.dispatch('bridge','latest',{})['packet'])
        hub.check(allow_stop=True)
        with self.assertRaises(ValueError):hub.check()
    def test_error_is_not_a_normal_stop_even_inflight(self):
        from joint_camera_runtime import JointCameraHub
        hub=JointCameraHub(dict(run_id=RUN,session_id=SID),SimpleNamespace())
        hub.revoke('CPU_BAD_ACK')
        with self.assertRaisesRegex(ValueError,'REVOKED'):hub.check(allow_stop=True)
    def test_bridge_stops_acquisition_on_worker_stopping(self):
        bridge=JointCameraBridge()
        bridge.client=SimpleNamespace(call=lambda *args:dict(status=dict(stopping=True,error=None),packet=None))
        bridge.loop()
        self.assertTrue(bridge.stop_event.is_set());self.assertIsNone(bridge.packet)


if __name__=='__main__':unittest.main()

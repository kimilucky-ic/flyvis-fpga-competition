"""Focused CPU-only minimal-loop checks; no CUDA, camera or physical sockets."""
import ast
import contextlib
import dataclasses
import io
import json
from pathlib import Path
import threading
import time
import types
import unittest
from unittest.mock import patch
import uuid
import numpy as np

from live_protocol import HERE,load
from hybrid_full485 import Full485Contract
from joint_camera_control import hardware_module
from joint_minimal_core import AsyncRecords,MinimalEngine,POLICY,transport_residual
from test_joint_camera import SavedHardwareFixture,item,RUN,SID

OUT=HERE/'evidence/minimal_compute_20261017'


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=HERE/'runtime/joint/f2fd7b4d54a4445daa8a15065c60088e'
        Reader=hardware_module(load(root/'hardware_handoff.json'),'evidence_journal').JournalReader
        reader=Reader(root/'pc/evidence.fvej')
        cls.raw={name:reader.read(name) for k in range(3) for name in
            [f'{prefix}_{k}.npy' for prefix in ('old_full','input_721','chemical','R_candidate','committed_full')]
            +[f'request_{k}.bin',f'candidate_{k}.bin']}

    def make(self,recorder=None):
        c=Full485Contract()
        a=lambda name:np.load(io.BytesIO(self.raw[name]),allow_pickle=False)
        hw=SavedHardwareFixture(c,types.SimpleNamespace(read=lambda name:self.raw[name]))
        inputs=[]
        with np.load(c.reg.path_for('parameters'),allow_pickle=False) as z:input_ids=z['input_node_index'].copy()
        def produce(old,frame,k):
            np.testing.assert_array_equal(old,a(f'old_full_{k}.npy'))
            np.testing.assert_array_equal(frame,a(f'input_721_{k}.npy'))
            x=np.zeros(45669,dtype='<f4');x[input_ids]=frame
            return dict(x_full=x,chemical_H=a(f'chemical_{k}.npy'),new_R=a(f'R_candidate_{k}.npy'),r_ids=c.r)
        # Preload every fixture array before prohibiting filesystem calls.
        arrays={name:a(name) for name in self.raw if name.endswith('.npy')}
        a=lambda name:arrays[name]
        identity=dict(run_id=RUN,session_id=SID,comparison_id='CPU_MINIMAL',condition_id='CURRENT_CAMERA',
                      max_steps=3,model=c.registry['model'],mapping_sha256=c.mapping_sha)
        recorder=recorder or types.SimpleNamespace(submit=lambda row:inputs.append(row) or True)
        engine=MinimalEngine(c,hw,produce,lambda full:full.copy(),identity,recorder)
        self.addCleanup(engine.close)
        return c,hw,engine,arrays,inputs

    def test_three_saved_steps_feedback_equal_with_all_file_io_forbidden(self):
        c,hw,e,a,rows=self.make()
        with (patch('pathlib.Path.stat',side_effect=AssertionError('hot stat')),
             patch('pathlib.Path.open',side_effect=AssertionError('hot open')),
             patch('os.fsync',side_effect=AssertionError('hot fsync'))):
            for k in range(3):
                e.step(item(a[f'input_721_{k}.npy'],k))
                np.testing.assert_array_equal(e.barrier.state,a[f'committed_full_{k}.npy'])
        self.assertEqual(len(hw.requests),3);self.assertEqual(len(hw.commits),3)
        self.assertEqual(len(rows),3);self.assertEqual(e.barrier.state_token,3)

    def test_missing_and_wrong_ACK_never_publish_or_retry(self):
        for attr in ('lose_ack','wrong_ack'):
            c,hw,e,a,rows=self.make();setattr(hw,attr,True)
            old=e.barrier.state.copy()
            with self.subTest(attr=attr),self.assertRaises((TimeoutError,ValueError)):
                e.step(item(a['input_721_0.npy']))
            np.testing.assert_array_equal(old,e.barrier.state);self.assertEqual(e.barrier.state_token,0)
            with self.assertRaises(ValueError):e.step(item(a['input_721_0.npy']))
            self.assertEqual(len(hw.requests),1);self.assertEqual(rows,[])

    def test_blocked_recorder_does_not_block_neural_steps(self):
        entered,release=threading.Event(),threading.Event()
        def blocked(record):entered.set();release.wait()
        recorder=AsyncRecords(blocked,capacity=3)
        self.addCleanup(lambda:(release.set(),recorder.close()))
        c,hw,e,a,_=self.make(recorder)
        e.step(item(a['input_721_0.npy']));self.assertTrue(entered.wait(1))
        e.step(item(a['input_721_1.npy'],1));e.step(item(a['input_721_2.npy'],2))
        self.assertFalse(release.is_set());self.assertEqual(e.barrier.state_token,3)
        release.set();self.assertTrue(recorder.close()['complete'])

    def test_logging_error_and_full_queue_do_not_revoke_computation(self):
        def broken(record):raise OSError('CPU_RECORDING_FAILURE')
        recorder=AsyncRecords(broken,capacity=1)
        self.addCleanup(recorder.close)
        c,hw,e,a,_=self.make(recorder)
        for k in range(3):e.step(item(a[f'input_721_{k}.npy'],k))
        state=recorder.close();self.assertEqual(e.barrier.state_token,3)
        self.assertGreater(state['errors']+state['dropped'],0);self.assertFalse(state['complete'])


class ContractTests(unittest.TestCase):
    def test_current_completed_parent_builds_one_minimal_bundle_and_fixed_cell(self):
        from joint_camera_bundle import preparation_parent,build
        from joint_camera_manual import board_cell,ManualGate
        selection=preparation_parent()
        self.assertEqual(selection['completed_fresh']['run_id'],'b3c166fcae404f878730ec3528f9012b')
        folder=OUT/'cpu_cases'/uuid.uuid4().hex;folder.mkdir(parents=True)
        root,archive=build(folder,**selection,minimal_compute=True,cpu_fixture=True)
        scope=load(root/'scope.json');runtime=load(root/'RUNTIME_SHA256.json')
        self.assertEqual(scope['runtime_policy'],POLICY);self.assertFalse(scope['recording_required_before_camera'])
        self.assertEqual(scope['ps_durability_policy'],'ASYNC_AFTER_ACK_NO_CRASH_DURABILITY/v1')
        self.assertEqual(scope['new_loads']+scope['new_resets']+scope['new_allocations'],0)
        self.assertIn('joint_minimal_board.py',runtime);self.assertIn('joint_minimal_core.py',runtime)
        cell=board_cell('31'*32,**selection);ast.parse(cell,feature_version=(3,8))
        self.assertIn('MANUAL_PREPARE_FRESH_COMPLETED',cell)
        gate=ManualGate(folder,**selection,minimal_compute=True)
        self.assertEqual(gate.expected['operation'],'MANUAL_PREPARE_FRESH_COMPLETED')
        packet=gate.operator_packet('192.168.2.99')
        self.assertEqual(packet['body']['prior_run_id'],selection['completed_fresh']['run_id'])
        self.assertIn('MANUAL_PREPARE_FRESH_COMPLETED',packet['body']['source'])

    def test_timing_residual_uses_durations_and_never_claims_one_way(self):
        value=transport_residual(10000,6000)
        self.assertEqual(value['transport_residual_ns'],4000)
        self.assertIn('NOT_IDENTIFIABLE',value['one_way_time'])
        self.assertIsNone(transport_residual(10,20)['transport_residual_ns'])


class BoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_ps_commit_evidence import PSCommitTests
        cls.F=PSCommitTests;cls.F.setUpClass()

    def test_initial_state_config_epoch_are_checked_in_RAM_before_DMA(self):
        from joint_minimal_board import install
        f=self.F('test_original_service_and_driver_three_steps_identical_outputs')
        self.addCleanup(f.doCleanups);c=f.make(n=1,policy=False)
        c.obj.config['runtime_policy']=POLICY;c.scope.update(runtime_policy=POLICY,max_steps=1,max_worker_s=30)
        c.obj._finish=lambda body:None
        runtime=install(c.obj,f.w,c.scope,AsyncRecords)
        self.addCleanup(runtime['recorder'].close)
        h=f.w.Header.unpack(f.requests[0][:256]);payload=f.requests[0][256:];c.d.bound_asid=h.asid.hex()
        c.d.check_bounds(h,payload)
        for bad in (dataclasses.replace(h,old_sha=b'9'*32),dataclasses.replace(h,epoch=1),
                    dataclasses.replace(h,config=b'8'*32)):
            with self.assertRaises(ValueError):c.d.check_bounds(bad,payload)
        with self.assertRaises(ValueError):c.d.check_bounds(h,bytes([payload[0]^1])+payload[1:])
        self.assertEqual((c.d.requests,c.d.commits),(0,0));self.assertFalse(any(x[0]=='DMA' for x in c.trace))

    def test_original_DMA_RUN_RELEASE_ACK_32_steps_without_hot_fsync(self):
        from joint_minimal_board import install
        f=self.F('test_original_service_and_driver_three_steps_identical_outputs')
        self.addCleanup(f.doCleanups);c=f.make(n=32,policy=False)
        c.obj.config['runtime_policy']=POLICY;c.scope.update(runtime_policy=POLICY,max_steps=32,max_worker_s=300)
        c.scope['transport_probe_count']=2
        first=f.w.Header.unpack(f.requests[0][:256]);raw=bytes(f.w.INPUT_BYTES);probes=[]
        for k in range(2):
            h=f.w.Header(f.w.STEP,first.asid,uuid.uuid4().bytes,0,f.w.digest(b'MINIMAL_TRANSPORT_ONLY_PROBE_V1'),
                f.w.digest(raw),len(raw),epoch=1)
            probes.append(h.pack()+raw)
        c.sock.raw=c.sock.raw[:256]+b''.join(probes)+c.sock.raw[256:]
        c.sock.setsockopt=lambda *args:None
        def finish(body):
            c.base.finish_window(dict(body,source_closed=True));return dict(state='FINISHED_PENDING_AUDIT',requests=c.d.requests,commits=c.d.commits)
        c.obj._finish=finish
        original_code=c.d.run.__func__.__code__
        runtime=install(c.obj,f.w,c.scope,AsyncRecords)
        self.assertIs(c.d.run.__func__.__code__,original_code)
        sync_before=c.base.journal.sync_calls
        with (patch('pathlib.Path.read_text',side_effect=AssertionError('hot file read')),
              patch('os.fsync',side_effect=AssertionError('hot fsync'))):
            c.obj.serve_connection(c.sock)
        self.assertEqual(c.base.journal.sync_calls,sync_before)
        self.assertEqual((c.d.requests,c.d.commits),(32,32));self.assertIsNone(c.d.pending)
        results=[raw for raw in c.sock.sent if f.w.Header.unpack(raw[:256]).op==f.w.RESULT]
        self.assertEqual([raw[256:] for raw in results[:2]],[bytes(f.w.WORD_BYTES)]*2)
        self.assertEqual([raw[256:] for raw in results[2:]],f.candidates)
        self.assertEqual(len([x for x in c.trace if x[0]=='RELEASE']),32)
        self.assertEqual(c.d.run.__func__.__code__,original_code)
        summary=c.obj._finish(dict(completed_steps=32,reason='STEP_LIMIT_COMPLETE'))['minimal_compute']
        self.assertEqual(len(summary['timing_rows']),32);self.assertTrue(summary['recording']['complete'])
        self.assertEqual(len(summary['transport_probes']),2)
        self.assertTrue(all(row['PL_calls']==0 for row in summary['transport_probes']))
        self.assertTrue(c.base.journal.closed)


class WorkerAdapterTests(unittest.TestCase):
    def test_saved_three_step_adapter_finishes_and_reports_without_device(self):
        self.saved_adapter()

    def test_live5_decodes_each_committed_full_state_without_device(self):
        self.saved_adapter(live5=True)

    def test_live5_stop_during_decode_preserves_same_committed_final_state(self):
        self.saved_adapter(live5=True,stop_after=1)

    def test_fast_compute_coalesces_publication_without_sleep_or_lost_evidence(self):
        self.saved_adapter(live5=True,step_wall_s=.05)

    def test_slow_compute_publishes_actual_steps_without_catchup_or_sleep(self):
        self.saved_adapter(live5=True,step_wall_s=.35)

    def test_timed_streaming_stops_at_commit_boundary_and_saves_all_selected_steps(self):
        self.saved_adapter(live5=True,step_wall_s=.5,run_duration_s=1)

    def saved_adapter(self,live5=False,stop_after=None,step_wall_s=None,run_duration_s=None):
        from joint_minimal_worker import execute
        from joint_camera_protocol import PROFILE
        saved=HERE/'runtime/joint/f2fd7b4d54a4445daa8a15065c60088e'
        Journal=hardware_module(load(saved/'hardware_handoff.json'),'evidence_journal')
        reader=Journal.JournalReader(saved/'pc/evidence.fvej')
        raw={name:reader.read(name) for k in range(3) for name in
             [f'{prefix}_{k}.npy' for prefix in ('old_full','input_721','chemical','R_candidate','committed_full','flow')]
             +[f'request_{k}.bin',f'candidate_{k}.bin']}
        arrays={name:np.load(io.BytesIO(data),allow_pickle=False) for name,data in raw.items() if name.endswith('.npy')}
        c=Full485Contract();hw=SavedHardwareFixture(c,types.SimpleNamespace(read=raw.__getitem__))
        hw.attestation.update(bit_sha256='CPU_ONLY',hwh_sha256='CPU_ONLY')
        root=OUT/'cpu_cases'/uuid.uuid4().hex;root.mkdir(parents=True)
        from live_protocol import write
        write(root/'CPU_FIXTURE_ONLY.json',dict(GPU=0,PL=0,camera=0,performance='MOCK_CLOCKS_NOT_MEASURED_HARDWARE'))
        write(root/'hardware_handoff.json',dict(endpoint=dict(host='NO_SOCKET_CPU_FIXTURE',port=0)))
        with np.load(c.reg.path_for('parameters'),allow_pickle=False) as z:input_ids=z['input_node_index'].copy()
        def produce(old,frame,**kw):
            k=kw['step_id'];np.testing.assert_array_equal(old,arrays[f'old_full_{k}.npy'])
            x=np.zeros(45669,dtype='<f4');x[input_ids]=frame
            return dict(x_full=x,chemical_H=arrays[f'chemical_{k}.npy'],new_R=arrays[f'R_candidate_{k}.npy'],r_ids=c.r)
        producer=types.SimpleNamespace(produce=produce,check_unchanged=lambda:None,native_H_update_count=0)
        class Event:
            def init__(self,**kw):pass
            def record(self):pass
            def synchronize(self):pass
            def elapsed_time(self,other):return 0.0
        torch=types.SimpleNamespace(cuda=types.SimpleNamespace(Event=Event),float32=np.float32,
            as_tensor=lambda value,**kw:np.asarray(value,dtype=kw.get('dtype')))
        decoded=[];now=[10.]
        def decode(full,**kw):
            k=len(hw.commits)-1
            self.assertEqual(k,len(decoded) if live5 else 2)
            np.testing.assert_array_equal(full[0,0],arrays['committed_full_%d.npy'%k])
            if stop_after and len(hw.commits)==stop_after:hub.stopping=True;hub.packet=None
            if step_wall_s is not None:now[0]+=step_wall_s
            decoded.append(True);return arrays['flow_%d.npy'%k][None,None]
        decoder=types.SimpleNamespace(decode=decode,assert_weights_unchanged=lambda:None)
        hub=types.SimpleNamespace(control=True,inputs=types.SimpleNamespace(),committed=0,stopping=False,error=None,
            update_progress=lambda *a:None,changed=threading.Condition(),check=lambda **kw:None,packet=None)
        hub.inputs.freeze_for_step=lambda:item(arrays[f'input_721_{min(hub.committed,2)}.npy'],hub.committed,kind='real_windows_camera')
        ps=[dict(step_id=k,STEP_ps_residence_ns=0,COMMIT_ps_residence_ns=0,ps_dma_roundtrip_observed_ns=0) for k in range(3)]
        control=types.SimpleNamespace(prepared=lambda:None,start=lambda *a:None,
            finish=lambda *a:dict(minimal_compute=dict(timing_rows=ps,transport_probes=[])))
        budget=types.SimpleNamespace(exchange_started=lambda:None,wait_source_closed=lambda *a:dict(closed=True),
            require_send_margin=lambda:None,clock=time.monotonic)
        scope=dict(run_id=RUN,session_id=SID,comparison_id='CPU_SAVED_ADAPTER',max_steps=3,max_worker_s=30,
            capture_duration_s=30,model=c.registry['model'],numerical_profile=PROFILE,runtime_policy=POLICY,transport_probe_count=0,**hw.attestation)
        if live5:scope['live_response_hz']=5
        if run_duration_s is not None:scope['run_duration_s']=run_duration_s
        virtual_clock=patch('joint_minimal_worker.time.monotonic',side_effect=lambda:now[0]) if step_wall_s is not None else contextlib.nullcontext()
        with (virtual_clock,patch.object(c.wire,'Client',return_value=hw),patch('joint_camera_io.tune_client'),
              patch('joint_minimal_worker.time.sleep',side_effect=AssertionError('Computation must not wait for display cadence'))):
            engine,reason=execute(root,scope,dict(end_unix=time.time()+60),c,producer,decoder,torch,hub,control,
                {},Journal.JournalWriter,lambda:None,lambda:None,budget,lambda:dict(CPU_FIXTURE_ONLY=True))
        self.addCleanup(engine.close)
        count=stop_after or (int(np.ceil(run_duration_s/step_wall_s)) if run_duration_s else 3)
        self.assertEqual(reason,'USER_STOP' if stop_after else 'CAPTURE_WINDOW_COMPLETE' if run_duration_s else 'STEP_LIMIT_COMPLETE')
        self.assertEqual(len(decoded),count if live5 else 1)
        report=load(root/'MINIMAL_PERFORMANCE.json');snapshot=load(root/'final_snapshot.json')
        self.assertEqual(report['steps'],count);self.assertTrue(report['recording']['complete'])
        self.assertTrue((root/'MINIMAL_TIMINGS.csv').exists())
        self.assertEqual(snapshot['display_kind'],'LIVE_LOW_RATE_LATEST_COMMITTED_STATE' if live5 else 'POST_COMPUTE_SAME_RUN_NOT_REALTIME')
        self.assertIsNone(snapshot['transaction']['integer_error'])
        np.testing.assert_array_equal(snapshot['flow'],arrays['flow_%d.npy'%(count-1)])
        if live5:
            self.assertEqual(report['compute_pacing'],'UNTHROTTLED_COMMIT_DRIVEN')
            self.assertEqual(report['display_consumer_limit_hz'],5)
            self.assertEqual(snapshot['compute_pacing'],report['compute_pacing'])
            if step_wall_s is not None:
                published=[row['step_id'] for row in report['display_rows'] if row['published']]
                self.assertEqual(published,[0] if step_wall_s<.2 else list(range(count)))
                self.assertAlmostEqual(report['total_compute_wall_s'],step_wall_s*count)
                self.assertEqual(snapshot['step_id'],count-1)
            # Skipped GUI frames must not discard per-step scientific evidence.
            recorded=Journal.JournalReader(root/'pc/evidence.fvej')
            for k in range(count):
                for saved_name,fixture_name in [('official_flow','flow'),('committed_full','committed_full')]:
                    value=np.load(io.BytesIO(recorded.read('%s_%d.npy'%(saved_name,k))),allow_pickle=False)
                    np.testing.assert_array_equal(value,arrays['%s_%d.npy'%(fixture_name,k)])


class CompletedPreparationTests(unittest.TestCase):
    def test_completed_handles_transfer_once_without_load_reset_allocate_or_old_mutation(self):
        import hashlib
        import joint_camera_fresh as fresh
        from test_joint_camera_fresh import FreshTests
        from test_joint_camera_manual import fixtures,Alive
        from joint_camera_board_entry import load_pinned_package
        f=FreshTests('test_original_read20_zero_writes_actual_zero_counters_idle0')
        f.setUp();self.addCleanup(f.tearDown);old=f.prepare();d=old.driver
        d.requests=d.commits=32;d.committed={b'1'*16:(31,bytes(23072),b'2'*32,b'3'*16,0)}
        old.evidence.journal.close('CPU_ONLY_COMPLETED_FIXTURE',requests=32,acks=32)
        prior={k:f.c[k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id')}
        prior.update(completed_steps=32,last_unified_commit_sha256=(b'2'*32).hex(),last_txn=(b'3'*16).hex(),
            PS_capture_sha256=hashlib.sha256(old.evidence.journal.path.read_bytes()).hexdigest())
        exited=threading.Event();exited.set();http_thread=Alive(True)
        service=types.SimpleNamespace(driver=d,config=f.c,state='FINISHED_PENDING_AUDIT',error=None,connections=1,inflight=False,
            neural_failure=None,listener=None,connection=None,neural_exited=exited,neural_thread=Alive(False),
            lock=threading.RLock(),thread=http_thread,expiry_thread=Alive(False),
            http=types.SimpleNamespace(shutdown=lambda:setattr(http_thread,'yes',False),server_close=lambda:None))
        config=dict(f.c,run_id=uuid.uuid4().hex,server_session=uuid.uuid4().hex,listener_id=uuid.uuid4().hex,
            completed_fresh_parent=prior)
        scope=json.loads(f.scope);scope.update({k:config[k] for k in ('run_id','server_session','completed_fresh_parent')})
        scope_raw=json.dumps(scope).encode();config['scope_sha256']=hashlib.sha256(scope_raw).hexdigest()
        plan=json.loads(f.plan);plan.update({k:config[k] for k in ('run_id','server_session','completed_fresh_parent')})
        plan_raw=json.dumps(plan).encode();config['plan_sha256']=hashlib.sha256(plan_raw).hexdigest()
        guard,*_=fixtures.handshake(config,f.pc,f.ps)
        pins=load(fixtures.ROOT/'templates/HARDWARE_HANDOFF_NOT_PREPARED.json')['software_sha256']
        package=load_pinned_package(fixtures.ROOT,dict(run_id=config['run_id']),pins)
        for k,v in zip((192,196,200),(17304,5768,57681)):f.values[k]=v
        d.dma.read=lambda offset:(f.reads.append(('dma',offset)) or (1 if offset in (0,48) else 0x1002))
        f.reads.clear();f.writes.clear()
        d.pending=object()
        with self.assertRaises(ValueError):fresh.completed_source(service,old,f.owner,config)
        self.assertEqual(f.reads,[]);d.pending=None
        new=fresh.prepare(f.root/'completed_successor',f.owner,config,scope_raw,plan_raw,guard,package,
            cpu=True,unused_service=service,unused_bundle=old)
        self.addCleanup(new.evidence.close)
        self.assertIs(new.driver.src,d.src);self.assertIs(new.driver.dst,d.dst)
        self.assertEqual((d.requests,d.commits),(32,32));self.assertFalse(d.poisoned)
        self.assertEqual((new.driver.requests,new.driver.commits),(0,0));self.assertEqual(f.writes,[])
        self.assertEqual(f.reads,fixtures.READS);self.assertEqual(len(f.calls),1)
        self.assertTrue(new.receipt['completed_fresh_parent_transfer']['completed_capture_preserved'])
        with self.assertRaises(ValueError):fresh.completed_source(service,old,f.owner,config)


if __name__=='__main__':unittest.main()

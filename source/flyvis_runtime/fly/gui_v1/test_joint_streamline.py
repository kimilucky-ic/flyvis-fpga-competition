"""Finite CPU/memory checks for the short joint path. No device/network launch."""
import ast,copy,json,os,threading,time,unittest,uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from live_protocol import HERE,load,sha
from joint_camera_control import hardware_module
from joint_camera_preparation import PCClockClient,PreparationAuthority,clock_binding
from joint_diagnostics import JointDiagnostics
from joint_runtime_audit import RuntimeFiles

OUT=HERE/'evidence/joint_streamline_20261017'

class ClockTests(unittest.TestCase):
    def fixture(self,mode=None):
        h=load(
            HERE.parent.parent/'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/camera_joint_ready_20261016/templates/HARDWARE_HANDOFF_NOT_PREPARED.json')
        h=copy.deepcopy(h);h.update(run_id='CPU_ONLY',server_session='CPU_ONLY',boot_id='NO_BOARD',
            listener_id='CPU_LISTENER',plan_sha256='0'*64,pc_clock_id='CPU_CLOCK',pc_authority_endpoint=dict(host='NO_NETWORK',port=1),
            control_config=dict(control_key='31'*32))
        scope=dict(run_id='CPU_ONLY',server_session='CPU_ONLY',boot_id='NO_BOARD',start_utc='CPU',end_utc='CPU')
        helpers=hardware_module(h,'control2');authority=PreparationAuthority.__new__(PreparationAuthority)
        authority.lock=threading.RLock();authority.error=None;authority.seen=set();authority.helpers=helpers
        authority.clock=SimpleNamespace(check=lambda:None,id='CPU_CLOCK');authority.config=h['control_config'];authority.binding=clock_binding(h,scope,'0'*64)
        history=[]
        class Connection:
            def init__(self,*args,**kwargs):self.sock=None;self.auto_open=True;self.requests=0;self.closes=0;history.append(self)
            def connect(self):self.sock=SimpleNamespace(setsockopt=lambda *args:None)
            def request(self,method,path,body,headers):
                self.requests+=1;self.reply=authority.dispatch(path,json.loads(body))
                if mode=='nonce':
                    value=helpers.verified(self.reply,'31'*32);value['nonce']='f'*32;self.reply=helpers.sign(value,'31'*32)
                if mode=='mac':self.reply['mac']='0'*64
            def getresponse(self):
                if mode=='timeout':raise TimeoutError('CPU_WAIT_TIMEOUT')
                if mode=='disconnect':raise ConnectionError('CPU_DISCONNECTED')
                return SimpleNamespace(status=200,will_close=mode=='closing',read=lambda n:json.dumps(self.reply).encode())
            def close(self):self.closes+=1;self.sock=None
        d=JointDiagnostics('CPU_CLOCK');client=PCClockClient(h,scope,'0'*64,diagnostics=d)
        return client,authority,history,Connection,d

    def test_connection_reused_each_nonce_verified_and_phases_split(self):
        c,a,history,factory,d=self.fixture()
        with patch('joint_camera_preparation.http.client.HTTPConnection',factory):
            for _ in range(3):c.check()
        self.assertEqual(len(history),1);self.assertEqual(history[0].requests,3);self.assertEqual(len(a.seen),3)
        self.assertFalse(history[0].auto_open)
        counts={name:sum(r['name']==name for r in d.rows) for name in ('clock.connect','clock.send_request',
            'clock.wait_response_headers','clock.read_response_body','clock.verify_response')}
        self.assertEqual(counts,{'clock.connect':1,'clock.send_request':3,'clock.wait_response_headers':3,
            'clock.read_response_body':3,'clock.verify_response':3})
        c.close();self.assertIsNone(history[0].sock)
        with self.assertRaisesRegex(ValueError,'REVOKED'):c.check()

    def test_bad_signature_nonce_timeout_disconnect_never_reconnect(self):
        for mode in ('mac','nonce','timeout','disconnect','closing'):
            with self.subTest(mode=mode):
                c,a,history,factory,d=self.fixture(mode)
                with patch('joint_camera_preparation.http.client.HTTPConnection',factory):
                    with self.assertRaises((ValueError,TimeoutError,ConnectionError)):c.check()
                    with self.assertRaisesRegex(ValueError,'REVOKED'):c.check()
                self.assertEqual(len(history),1);self.assertEqual(history[0].requests,1)
                self.assertIsNone(history[0].sock);self.assertTrue(c.failed)

    def test_verification_failure_is_in_the_correct_timing_phase(self):
        c,a,history,factory,d=self.fixture('mac')
        with patch('joint_camera_preparation.http.client.HTTPConnection',factory):
            with self.assertRaises(ValueError):c.check()
        self.assertTrue(next(r for r in d.rows if r['name']=='clock.verify_response')['failed'])

class FileAuditTests(unittest.TestCase):
    def case(self):
        p=OUT/'file_cases'/uuid.uuid4().hex;p.mkdir(parents=True);return p
    def test_duplicates_share_one_stat_per_background_pass(self):
        root=self.case();p=root/'source.py';p.write_bytes(b'abc');g=RuntimeFiles();g.add(p,sha(p));g.add(root/'.'/'source.py',sha(p))
        actual=Path.stat;calls=[]
        def stat(path,*args,**kwargs):calls.append(path);return actual(path,*args,**kwargs)
        with patch.object(Path,'stat',stat):g.check()
        self.assertEqual(len(g.files),1);self.assertEqual(len(calls),1);self.assertEqual(g.metadata_passes,1)
    def test_change_and_deletion_revoke_background_audit(self):
        root=self.case();p=root/'x';p.write_bytes(b'abc');g=RuntimeFiles();g.add(p,sha(p));p.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'FILE_CHANGED'):g.check()
        missing=root/'missing';missing.write_bytes(b'test');h=RuntimeFiles();h.add(missing,sha(missing));missing.rename(root/'moved')
        with self.assertRaises(FileNotFoundError):h.check()
    def test_final_hash_catches_content_even_if_metadata_snapshot_matches(self):
        root=self.case();p=root/'x';p.write_bytes(b'abc');g=RuntimeFiles();g.add(p,sha(p));p.write_bytes(b'xyz')
        # Deliberately emulate metadata restoration to exercise the final SHA.
        g.files[p.resolve()]['stamp']=g.stamp(p.stat())
        with self.assertRaisesRegex(ValueError,'FINAL_SHA'):g.final()
    def test_conflicting_pin_and_change_since_load_rejected(self):
        root=self.case();p=root/'x';p.write_bytes(b'abc');g=RuntimeFiles();g.add(p,sha(p))
        with self.assertRaisesRegex(ValueError,'CONFLICTING'):g.add(p,'0'*64)
        with self.assertRaisesRegex(ValueError,'SINCE_LOAD'):g.add(p,sha(p),prior_stamp=(1,1))
    def test_loaded_static_files_skip_polling_but_still_require_final_SHA(self):
        root=self.case();p=root/'loaded';p.write_bytes(b'abc');g=RuntimeFiles();g.add(p,sha(p),watch=False)
        p.write_bytes(b'xyz');g.check()
        self.assertEqual(g.summary()['runtime_identity_files'],0)
        with self.assertRaisesRegex(ValueError,'FINAL_SHA'):g.final()
    def test_clock_and_static_files_are_outside_main_gate(self):
        tree=ast.parse((HERE/'joint_camera_worker.py').read_text(encoding='utf8'))
        gate=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='gate')
        text=ast.get_source_segment((HERE/'joint_camera_worker.py').read_text(encoding='utf8'),gate)
        self.assertNotIn('pc_guard',text);self.assertNotIn('sha(',text);self.assertIn('monitor.check()',text)
        from stream_transport import AuditMonitor
        monitor=AuditMonitor(lambda:None,interval=10)
        try:
            monitor.at=time.monotonic()-3
            with self.assertRaisesRegex(ValueError,'STALLED'):monitor.check()
        finally:monitor.close()

class HeartbeatTests(unittest.TestCase):
    def case(self):
        p=OUT/'heartbeat_cases'/uuid.uuid4().hex;p.mkdir(parents=True);return p
    def test_stopped_worker_does_not_revalidate_clock_or_replace_error(self):
        from joint_camera_controller import controller_heartbeat
        p=self.case();(p/'ERROR_REQUEST.json').write_text('{"error":"ORIGINAL"}',encoding='utf8')
        clock=SimpleNamespace(check=lambda:(_ for _ in ()).throw(AssertionError('Stopped worker must not check clock')))
        controller_heartbeat(p,'CPU_SESSION',clock,neural_active=False)
        self.assertEqual(load(p/'ERROR_REQUEST.json')['error'],'ORIGINAL')
        self.assertEqual(load(p/'controller.json')['session_id'],'CPU_SESSION')
    def test_active_clock_failure_preserves_first_failure(self):
        from joint_camera_controller import controller_heartbeat
        p=self.case();(p/'ERROR_REQUEST.json').write_text('{"error":"FIRST_FAILURE"}',encoding='utf8')
        clock=SimpleNamespace(check=lambda:(_ for _ in ()).throw(ValueError('CLOCK_FAILED')))
        with self.assertRaisesRegex(ValueError,'CLOCK_FAILED'):controller_heartbeat(p,'CPU_SESSION',clock)
        self.assertEqual(load(p/'ERROR_REQUEST.json')['error'],'FIRST_FAILURE')
        self.assertFalse((p/'controller.json').exists())
    def test_active_clock_failure_is_saved_when_it_is_the_first_error(self):
        from joint_camera_controller import controller_heartbeat
        p=self.case();clock=SimpleNamespace(check=lambda:(_ for _ in ()).throw(ValueError('CLOCK_FAILED')))
        with self.assertRaises(ValueError):controller_heartbeat(p,'CPU_SESSION',clock)
        self.assertIn('CLOCK_FAILED',load(p/'ERROR_REQUEST.json')['error'])

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_joint_camera import CameraJointTests
        CameraJointTests.setUpClass();cls.fixture_class=CameraJointTests
    def case(self):
        from joint_camera_engine import JointCameraEvidence,CameraJointEngine
        c=self.fixture_class('test_three_step_original_coordinator_feedback_and_durable_snapshots');c.setUp();self.addCleanup(c.tearDown)
        prior=c.engine;c.ev.writer.abandon()
        c.ev=JointCameraEvidence(c.journal.JournalWriter(Path(c.temp.name)/'postrun',dict(role='CPU_DEFERRED_TEST')),3)
        c.engine=CameraJointEngine(c.c,c.hw,prior.produce,prior.decode,c.ev,c.identity,lambda:None,
            lambda full:full.copy(),lambda value:value,None)
        return c
    def test_deferred_reference_retains_real_saved_feedback_and_pending_label(self):
        from joint_camera_protocol import TEST,validate_snapshot
        c=self.case()
        for k in range(3):
            p=c.engine.step(c.current(k));validate_snapshot(p,c.identity,c.c.spatial,allow_test=True)
            self.assertEqual(p['execution_kind'],TEST);self.assertEqual(p['validation_policy'],'SAME_OLD_CPU_POST_RUN')
            self.assertEqual(p['whole_run_acceptance'],'PENDING');self.assertEqual(p['transaction']['integer_error'],0)
            self.assertEqual(c.reference_calls,[])
        c.ev.close('CPU_TEST_COMPLETE');reader=c.journal.JournalReader(c.ev.writer.path)
        for k in range(3):
            v=json.loads(reader.read(f'validation_{k}.json'))
            self.assertEqual(v['reference']['status'],'DEFERRED_OFFLINE_REQUIRED')
            self.assertEqual(v['integer_check']['max_integer_code_error'],0)
        self.assertEqual(c.hw.requests[1][:23072],c.reader.read('candidate_0.bin'))
    def test_wrong_ACK_and_Q24_still_block_publication_without_CPU_redo(self):
        for kind in ('ACK','Q24'):
            with self.subTest(kind=kind):
                c=self.case()
                if kind=='ACK':c.hw.wrong_ack=True
                else:
                    original=c.hw.step
                    def corrupt(*args,**kwargs):
                        candidate,r=original(*args,**kwargs);bad=bytearray(candidate);bad[0]^=1
                        # Keep the header checksum valid to target the integer oracle.
                        import dataclasses
                        return bytes(bad),dataclasses.replace(r,payload_sha=c.c.wire.digest(bytes(bad)))
                    c.hw.step=corrupt
                with self.assertRaises(ValueError):c.engine.step(c.current(0))
                self.assertEqual(c.engine.barrier.state_token,0)
                if kind=='Q24':self.assertEqual(c.hw.commits,[])
    def test_before_send_disk_and_transport_fields_are_separate(self):
        c=self.case();actual=c.ev.writer.sync_fn
        def slow(fd):time.sleep(.002);actual(fd)
        c.ev.writer.sync_fn=slow
        original_step,original_commit=c.hw.step,c.hw.commit
        def step(old,chem,x,identity):
            c.ev.observe('tx_intent',old+chem+x);return original_step(old,chem,x,identity)
        def commit(decision):
            c.ev.observe('tx_intent',c.engine.barrier.pending['commit_header'].pack());return original_commit(decision)
        c.hw.step,c.hw.commit=step,commit
        tx=c.engine.step(c.current(0))['transaction']
        for operation in ('STEP','COMMIT'):
            full=tx['PC_'+operation+'_roundtrip_ns'];disk=tx['PC_'+operation+'_before_send_durable_ns']
            self.assertGreater(disk,1_000_000);self.assertLessEqual(disk,full)
            self.assertGreater(tx['PC_'+operation+'_before_send_fsync_ns'],1_000_000)
            self.assertEqual(tx['PC_'+operation+'_excluding_before_send_ns'],full-disk)

if __name__=='__main__':unittest.main()

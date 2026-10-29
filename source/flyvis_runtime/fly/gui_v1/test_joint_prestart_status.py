"""Focused local status reconnect checks; no camera, CUDA or board requests."""
from datetime import datetime,timedelta,timezone
from pathlib import Path
from types import SimpleNamespace
import copy,json,socket,time,unittest,uuid
import hashlib,io
from unittest.mock import Mock,patch
from live_protocol import HERE,load,sha,write
from joint_camera_bridge import JointCameraBridge
from stream_transport import LocalRPC,RPC
import test_joint_fresh_unused as old_transfer
import test_joint_camera_fresh as fresh_fixture
from test_joint_camera_manual import Alive

OUT=HERE/'evidence/startup_wait_user_button_20261017/status_transport_fix'

class StatusTests(unittest.TestCase):
    def setUp(self):
        self.root=OUT/'cpu_cases'/uuid.uuid4().hex;self.root.mkdir(parents=True)
        self.scope=load(HERE/'runtime/joint/3deec72882294aed9afc33a9e7d3da75/scope.json')
        now=datetime.now(timezone.utc)
        self.scope.update(run_id=uuid.uuid4().hex,session_id=uuid.uuid4().hex,gpu_lease_id=uuid.uuid4().hex,
            start_utc=(now-timedelta(seconds=1)).isoformat(),end_utc=(now+timedelta(seconds=800)).isoformat(),
            execution_authority='CPU_FIXTURE_ONLY',human_authorization_reference='CPU_STATUS_TEST_NO_DEVICES')
        write(self.root/'scope.json',self.scope)
        self.b=JointCameraBridge();self.b.path=self.root/'session.json';self.b.root=self.root;self.b.scope=self.scope
        self.b.session=dict(session_id=self.scope['session_id'],scope_sha256=sha(self.root/'scope.json'))
        self.status=dict(status='WAITING_CAMERA_SELECTION',run_id=self.scope['run_id'],session_id=self.scope['session_id'],
            committed_steps=0,identity=None,ready_for_camera=True,error=None)
        self.server=None;self.calls=[]
    def tearDown(self):
        for client in (self.b.client,self.b.input_client):
            if client:client.close()
        if self.server:self.server.close()
    def endpoint(self):
        value=dict(session_id=self.scope['session_id'],port=1,token='CPU_TOKEN')
        write(self.root/'joint_endpoint.json',value);return value
    def test_real_loopback_after_five_second_idle_recovers_status_only(self):
        def dispatch(role,op,body):
            self.calls.append(op);self.assertEqual((role,op),('bridge','status'));return self.status
        self.server=LocalRPC(self.scope['session_id'],dispatch)
        write(self.root/'joint_endpoint.json',self.server.endpoint)
        self.assertTrue(self.b.status()['ready_for_camera'])
        time.sleep(5.3)  # Reproduce the unchanged server's actual 5s idle close.
        lost=self.b.status()
        self.assertFalse(lost['ready_for_camera']);self.assertIsNone(self.b.error)
        recovered=self.b.status()
        self.assertTrue(recovered['ready_for_camera']);self.assertIsNone(recovered['error'])
        self.assertEqual(self.calls,['status','status'])
        self.assertFalse((self.root/'CAMERA_START_REQUEST.json').exists())
    def test_WinError10053_does_not_latch_prestart_failure(self):
        endpoint=self.endpoint();client=SimpleNamespace(sock=None,endpoint=endpoint)
        client.close=Mock();client.call=Mock(side_effect=[ConnectionAbortedError(10053,'CPU_SIMULATED_WSAECONNABORTED'),self.status])
        with patch('joint_camera_bridge.RPC',return_value=client):
            self.assertFalse(self.b.status()['ready_for_camera'])
            self.assertIsNone(self.b.error)
            self.assertTrue(self.b.status()['ready_for_camera'])
        self.assertEqual([c.args[0] for c in client.call.call_args_list],['status','status'])
    def test_wrong_status_identity_latches_failure_no_fallback(self):
        self.endpoint();client=SimpleNamespace(sock=object(),endpoint={},close=Mock(),call=Mock(return_value=dict(self.status,session_id='OTHER')))
        with patch('joint_camera_bridge.RPC',return_value=client):
            self.assertFalse(self.b.status()['ready_for_camera']);self.assertIn('STATUS_IDENTITY',self.b.error)
            self.b.status()
        self.assertEqual(client.call.call_count,1)
    def test_changed_endpoint_never_reconnects_to_another_worker(self):
        ep=self.endpoint();self.b.client=SimpleNamespace(sock=None,endpoint=ep,close=Mock(),call=Mock())
        write(self.root/'joint_endpoint.json',dict(ep,port=2))
        self.assertFalse(self.b.status()['ready_for_camera']);self.assertIn('ENDPOINT_CHANGED',self.b.error)
        self.b.client.call.assert_not_called()
    def test_real_worker_failure_is_not_retried(self):
        write(self.root/'worker_start_failure.json',dict(error='ACTUAL_WORKER_FAILURE'))
        self.b.client=SimpleNamespace(sock=None,close=Mock(),call=Mock())
        self.assertFalse(self.b.status()['ready_for_camera']);self.assertEqual(self.b.error,'ACTUAL_WORKER_FAILURE')
        self.b.client.call.assert_not_called()
    def test_started_or_stopped_session_never_recovers_via_prestart_poll(self):
        self.b.last_status=dict(self.status);self.b.client=SimpleNamespace(close=Mock(),call=Mock())
        self.b.control={'STARTED':True};self.b.error='ACTIVE_CONNECTION_FAILED'
        self.assertFalse(self.b.status()['ready_for_camera']);self.assertEqual(self.b.error,'ACTIVE_CONNECTION_FAILED')
        self.b.client.call.assert_not_called()
        self.b.control=None;self.b.error=None;self.b.stop_event.set()
        self.assertFalse(self.b.status()['ready_for_camera']);self.b.client.call.assert_not_called()

class PreparedTransferTests(old_transfer.FreshUnusedTests):
    def setUp(self):
        # Reuse the accepted constructor/read20 fixture; keep this source in
        # BOARD_PREPARED instead of fabricating an expired terminal capture.
        with patch.object(fresh_fixture,'OUT',OUT/'prepared_cases'):
            fresh_fixture.FreshTests.setUp(self)
        self.bundle=None;self.new_bundle=None
        fresh_fixture.FreshTests.prepare(self)
        from ps_commit_evidence import install_before_bind
        import importlib,threading,hashlib,types
        install_before_bind(self.bundle,self.scope,importlib.import_module(self.package.__name__+'.protocol'))
        self.old=self.bundle;thread=Alive(True)
        self.service=SimpleNamespace(config=self.c,driver=self.old.driver,evidence=self.old.evidence,state='BOARD_PREPARED',error=None,
            identity=None,connections=0,inflight=False,listener=None,connection=None,neural_thread=None,
            thread=thread,expiry_thread=Alive(False),lock=threading.RLock(),secondary_errors=[],
            http=SimpleNamespace(shutdown=lambda:setattr(thread,'yes',False),server_close=lambda:None))
        service_class=importlib.import_module(self.package.__name__+'.service').CameraBoardService
        self.service.stop=types.MethodType(service_class.stop,self.service)
        self.service._close_failed_evidence=types.MethodType(service_class._close_failed_evidence,self.service)
        self.service.event=lambda name,**kw:self.old.evidence.event(name,**kw)
        self.prior={k:self.c[k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id')}
        base={k:v for k,v in self.old.receipt.items() if k!='ps_durability'}
        self.prior.update(preparation_receipt_sha256=hashlib.sha256(json.dumps(base,sort_keys=True).encode()).hexdigest(),allow_manual_prestart_cancel=True)
        self.next_c=dict(self.c,run_id=uuid.uuid4().hex,server_session=uuid.uuid4().hex,listener_id=uuid.uuid4().hex,unused_fresh_parent=self.prior)
        s=json.loads(self.scope);s.update({k:self.next_c[k] for k in ('run_id','server_session','unused_fresh_parent')})
        self.next_scope=json.dumps(s).encode();self.next_c['scope_sha256']=hashlib.sha256(self.next_scope).hexdigest()
        p=json.loads(self.plan);p.update({k:self.next_c[k] for k in ('run_id','server_session','unused_fresh_parent')})
        self.next_plan=json.dumps(p).encode();self.next_c['plan_sha256']=hashlib.sha256(self.next_plan).hexdigest()
        from test_joint_camera_manual import fixtures
        from joint_camera_board_entry import load_pinned_package
        self.next_guard,*_=fixtures.handshake(self.next_c,self.pc,self.ps)
        self.next_package=load_pinned_package(fixtures.ROOT,dict(run_id=self.next_c['run_id']),load(fixtures.ROOT/'templates/HARDWARE_HANDOFF_NOT_PREPARED.json')['software_sha256'])
        self.reads.clear()
    def tearDown(self):
        if self.new_bundle:self.new_bundle.evidence.close()
        elif not self.old.evidence.journal.closed:self.old.evidence.close()
        import joint_camera_fresh as fresh
        fresh.PINNED=self.pins_before

class OperatorEntryTests(unittest.TestCase):
    def packet(self,**changes):
        from joint_camera_manual import mac
        body=dict(schema='flyvis-signed-human-prepare-entry/v1',prior_run_id='cpu_run',prior_scope_sha256='0'*64,
            source='CPU_ENTRY_EXECUTED = True')
        body.update(changes);body['source_sha256']=hashlib.sha256(body['source'].encode()).hexdigest()
        return dict(body=body,mac=mac(body,'31'*32))
    def execute_helper(self,packet,namespace):
        import urllib.request
        with patch.object(urllib.request,'urlopen',return_value=io.BytesIO(json.dumps(packet).encode())):
            exec(compile((HERE/'board_prepare_camera.py').read_text(encoding='utf8'),'CPU_SIGNED_ENTRY_TEST','exec'),namespace,namespace)
    def namespace(self):
        return dict(camera3_service_instance=SimpleNamespace(config=dict(control_key='31'*32,run_id='cpu_run',scope_sha256='0'*64)))
    def test_fixed_helper_executes_only_current_parent_signed_source(self):
        ns=self.namespace();self.execute_helper(self.packet(),ns);self.assertTrue(ns['CPU_ENTRY_EXECUTED'])
    def test_bad_signature_wrong_parent_or_source_never_executes(self):
        bad=self.packet();bad['mac']='00'*32
        tampered=self.packet();tampered['body']['source']='CPU_ENTRY_EXECUTED = False'
        for packet in (bad,self.packet(prior_run_id='OTHER'),self.packet(prior_scope_sha256='1'*64),tampered):
            ns=self.namespace()
            with self.subTest(packet=packet),self.assertRaises(AssertionError):self.execute_helper(packet,ns)
            self.assertNotIn('CPU_ENTRY_EXECUTED',ns)
    def test_only_board_peer_gets_parent_authenticated_existing_cell(self):
        from joint_camera_manual import ManualGate,mac
        gate=ManualGate(OUT/'unused_operator_stage',fresh={'CPU':'NO_DEVICE'},unused_fresh=dict(run_id='cpu_run',scope_sha256='0'*64))
        active=dict(state='STOPPED',run_id='cpu_run',session_id='CPU_SESSION')
        handoff=dict(run_id='cpu_run',control_config=dict(run_id='cpu_run',control_key='31'*32))
        with patch('joint_camera_manual.load',side_effect=[active,handoff]):packet=gate.operator_packet('192.168.2.99')
        self.assertEqual(packet['mac'],mac(packet['body'],'31'*32));self.assertIn('camera_entry.run',packet['body']['source'])
        self.assertFalse(gate.consumed)
        with patch('joint_camera_manual.load') as read,self.assertRaises(ValueError):gate.operator_packet('192.168.2.1')
        read.assert_not_called()
        gate.consumed=True
        with self.assertRaisesRegex(ValueError,'CONSUMED'):gate.operator_packet('192.168.2.99')

if __name__=='__main__':unittest.main()

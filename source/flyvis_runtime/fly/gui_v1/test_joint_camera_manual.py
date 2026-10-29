"""Bounded CPU checks; sockets and devices are forbidden by the runner."""
import copy,hashlib,importlib.util,json,sys,threading,types,unittest,uuid
from pathlib import Path
from unittest.mock import patch
from live_protocol import HERE,sha,load
import joint_camera_retained as transfer
from joint_camera_manual import ManualGate,mac,board_cell

OUT=HERE/'evidence/camera_joint_manual_20261016'
PACKAGE=HERE.parent.parent/'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/camera_joint_ready_20261016'
spec=importlib.util.spec_from_file_location('line2_retained_cpu_fixture',PACKAGE/'test_ready.py')
fixtures=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixtures)
fixtures.RESULTS=OUT/'fixture';(fixtures.RESULTS/'scratch').mkdir(parents=True,exist_ok=True)
import a3ready

class Alive:
    def init__(self,yes=False):self.yes=yes
    def is_alive(self):return self.yes
    def join(self,*a):pass

class TransferTests(unittest.TestCase):
    def setUp(self):
        self.root=OUT/'cases'/uuid.uuid4().hex;self.root.mkdir(parents=True)
        old,scope,plan,pc,ps=fixtures.config();old['run_id']=transfer.EXPIRED_RUN
        s=json.loads(scope);s['run_id']=old['run_id'];scope=json.dumps(s).encode();old['scope_sha256']=hashlib.sha256(scope).hexdigest()
        p=json.loads(plan);p['run_id']=old['run_id'];plan=json.dumps(p).encode();old['plan_sha256']=hashlib.sha256(plan).hexdigest()
        guard,*_=fixtures.handshake(old,pc,ps)
        self.original,self.reads,self.writes,self.values=fixtures.source_fixture(self.root,old)
        b=fixtures.prepare_retained(self.root/'expired',self.original,old,scope,plan,guard,cpu_fixture=True,kernel=lambda:old['kernel_file'],boot=lambda:ps.boot)
        b.driver.poisoned=True;b.evidence.event('FAIL_STOP',error='MANUAL_PREPARATION_EXPIRED',requests=0,commits=0,pending=False);b.evidence.close()
        http_thread=Alive(True)
        self.service=types.SimpleNamespace(config=old,driver=b.driver,state='FAILED_OR_UNKNOWN',error='MANUAL_PREPARATION_EXPIRED',
            identity=None,connections=0,inflight=False,listener=None,connection=None,neural_thread=None,
            thread=http_thread,expiry_thread=Alive(),lock=threading.RLock(),
            http=types.SimpleNamespace(shutdown=lambda:setattr(http_thread,'yes',False),server_close=lambda:None))
        self.c,self.scope,self.plan,self.pc,self.ps=fixtures.config()
        p=json.loads(self.plan);p.update(operation='TRANSFER_ZERO_STEP_EXPIRED_OWNER_READ20',expired_run_id=transfer.EXPIRED_RUN,original_source_run=transfer.ORIGINAL_RUN)
        self.plan=json.dumps(p).encode();self.c['plan_sha256']=hashlib.sha256(self.plan).hexdigest()
        self.guard,*_=fixtures.handshake(self.c,self.pc,self.ps);self.bundle=None
        self.reads.clear();self.original_claim=copy.deepcopy(self.original.driver._camera_ready_claim)
    def tearDown(self):
        if self.bundle:self.bundle.evidence.close()
    def run_prepare(self):
        self.bundle=transfer.prepare(self.root/'new',self.service,self.original,self.c,self.scope,self.plan,self.guard,a3ready,cpu=True)
        return self.bundle
    def test_zero_step_transfer_new_driver_keeps_old_poison_claim_and_read20(self):
        oldsha=sha(self.service.driver.evidence.journal.path);b=self.run_prepare()
        self.assertEqual(self.reads,fixtures.READS);self.assertEqual(self.writes,[])
        self.assertIs(b.driver.src,self.original.driver.src);self.assertIs(b.driver.dst,self.original.driver.dst)
        self.assertTrue(self.service.driver.poisoned);self.assertFalse(b.driver.poisoned)
        self.assertEqual(self.original.driver._camera_ready_claim,self.original_claim)
        self.assertEqual(sha(self.service.driver.evidence.journal.path),oldsha)
        self.assertFalse(self.service.thread.is_alive());self.assertTrue(self.original.thread.is_alive())
        self.assertEqual(b.receipt['zero_step_transfer']['expired_run_id'],transfer.EXPIRED_RUN)
    def test_pending_or_start_or_connections_refused_without_read(self):
        for obj,key,value in ((self.service,'identity',{}),(self.service,'connections',1),(self.service,'neural_thread',Alive()),(self.service.driver,'pending',('x',))):
            old=getattr(obj,key);setattr(obj,key,value)
            with self.assertRaises(ValueError):transfer.inspect_expired(self.service,self.original,a3ready,cpu=True)
            setattr(obj,key,old)
        self.assertEqual(self.reads,[]);self.assertTrue(self.service.thread.is_alive())
    def test_unknown_failure_cannot_reuse_zero_count_buffers(self):
        self.service.error='COMMIT_TIMEOUT'
        with self.assertRaisesRegex(ValueError,'UNUSED_EXPIRY'):self.run_prepare()
        self.assertEqual(self.reads,[])
    def test_changed_original_claim_rejected(self):
        self.original.driver._camera_ready_claim['scope_sha256']='00'*32
        with self.assertRaisesRegex(ValueError,'PARENT_CLAIM'):self.run_prepare()
        self.assertTrue(self.service.thread.is_alive());self.assertEqual(self.reads,[])
    def test_failed_register_read_consumes_new_claim_no_old_unpoison(self):
        self.values[24]=1
        with self.assertRaises(ValueError):self.run_prepare()
        self.assertTrue(self.service.driver._line2_successor_claim);self.assertTrue(self.service.driver.poisoned)
        self.assertEqual(self.writes,[])
        with self.assertRaisesRegex(ValueError,'CONSUMED'):transfer.inspect_expired(self.service,self.original,a3ready,cpu=True)
    def test_http_shutdown_unconfirmed_prevents_claim_and_reads(self):
        self.service.http.shutdown=lambda:None
        with self.assertRaisesRegex(ValueError,'STOP_UNCONFIRMED'):self.run_prepare()
        self.assertFalse(hasattr(self.service.driver,'_line2_successor_claim'));self.assertEqual(self.reads,[])
    def test_corrupt_closed_capture_is_rejected(self):
        with self.service.driver.evidence.journal.path.open('ab') as f:f.write(b'bad')
        with self.assertRaises(ValueError):self.run_prepare()
        self.assertEqual(self.reads,[])
    def test_real_transfer_receipt_and_real_clock_body_pass_original_GUI_reader(self):
        from joint_camera_preparation import verify_prepared_packet
        b=self.run_prepare();clock_receipt=self.guard.receipt(self.c)
        scope=json.loads(self.scope)
        declaration=load(PACKAGE/'templates/HARDWARE_HANDOFF_NOT_PREPARED.json')
        declaration.update({k:self.c[k] for k in ('run_id','server_session','boot_id','listener_id','plan_sha256')})
        declaration.update(transfer_from_expired_run=transfer.EXPIRED_RUN,control_config=dict(control_key=self.c['control_key']))
        binding={k:self.c[k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id','start_utc','end_utc')}
        status=dict(binding,state='BOARD_PREPARED',requests=0,commits=0,pending=False,poisoned=False,error=None,
            neural_connections=0,service_alive=True,clock_policy=clock_receipt['policy'],clock_proof_sha256=clock_receipt['proof_sha256'])
        body=dict(schema='flyvis-camera-retained-prepared/v1',binding=binding,preparation_receipt=b.receipt,clock_receipt=clock_receipt,status=status)
        packet=fixtures.sign(body,self.c['control_key'])
        self.assertEqual(verify_prepared_packet(packet,declaration,scope,self.c['scope_sha256']),body)
        body['preparation_receipt']['zero_step_transfer']['old_control_thread_stopped']=False
        with self.assertRaisesRegex(ValueError,'TRANSFER_NOT_PROVEN'):
            verify_prepared_packet(fixtures.sign(body,self.c['control_key']),declaration,scope,self.c['scope_sha256'])

class ManualTests(unittest.TestCase):
    def test_numeric_bind_never_performs_reverse_dns(self):
        import socket
        from socketserver import TCPServer
        from joint_camera_preparation import LocalAddressHTTPServer
        server=LocalAddressHTTPServer.__new__(LocalAddressHTTPServer)
        server.server_address=('192.168.2.89',18791)
        with patch.object(TCPServer,'server_bind') as bind,patch.object(socket,'getfqdn',side_effect=AssertionError('NO_REVERSE_DNS')):
            server.server_bind()
        bind.assert_called_once_with(server)
        self.assertEqual((server.server_name,server.server_port),('192.168.2.89',18791))
    def test_invalid_peer_mac_or_binding_never_builds_or_starts_authority(self):
        gate=ManualGate(OUT);body=dict(operation='MANUAL_PREPARE_CAMERA3',expired_run_id=transfer.NEXT_EXPIRED_RUN)
        packet=dict(body=body,mac=mac(body,gate.token))
        with patch('joint_camera_bundle.build',side_effect=AssertionError('must not build')):
            for peer,p in [('127.0.0.1',packet),('192.168.2.99',dict(packet,mac='00'*32)),('192.168.2.99',dict(body={},mac=mac({},gate.token)))]:
                with self.assertRaises(ValueError):gate.bundle(p,peer)
        self.assertFalse(gate.consumed);self.assertIsNone(gate.authority)
    def test_scope_created_only_on_one_authenticated_manual_request(self):
        gate=ManualGate(OUT);body=dict(operation='MANUAL_PREPARE_CAMERA3',expired_run_id=transfer.NEXT_EXPIRED_RUN)
        packet=dict(body=body,mac=mac(body,gate.token))
        with patch('joint_camera_bundle.build',side_effect=RuntimeError('fixture build failure')) as build:
            self.assertEqual(build.call_count,0)
            with self.assertRaises(RuntimeError):gate.bundle(packet,'192.168.2.99')
            self.assertEqual(build.call_count,1)
            with self.assertRaisesRegex(ValueError,'CONSUMED'):gate.bundle(packet,'192.168.2.99')
            self.assertEqual(build.call_count,1)
    def test_manual_cell_no_overlay_reset_allocation_and_38_syntax(self):
        import ast
        cell=board_cell('42'*32);ast.parse(cell,feature_version=(3,8))
        self.assertIn('camera_entry.run',cell)
        for forbidden in ('Overlay(','.reset(','.allocate(','.download('):self.assertNotIn(forbidden,cell)
    def test_new_package_namespace_keeps_old_live_objects_untouched(self):
        from joint_camera_board_entry import load_pinned_package
        import importlib
        pins=load(PACKAGE/'templates/HARDWARE_HANDOFF_NOT_PREPARED.json')['software_sha256']
        original=a3ready
        package=load_pinned_package(PACKAGE,dict(run_id=uuid.uuid4().hex),pins)
        driver=importlib.import_module(package.__name__+'.driver')
        self.assertIsNot(driver.Full485Driver,fixtures.Full485Driver)
        self.assertIs(sys.modules['a3ready'],original)
        changed=dict(pins);changed['a3ready/clock.py']='00'*32
        with self.assertRaisesRegex(AssertionError,'SOFTWARE_CHANGED'):
            load_pinned_package(PACKAGE,dict(run_id=uuid.uuid4().hex),changed)


class SecondZeroStepTransferTests(unittest.TestCase):
    def setUp(self):
        TransferTests.setUp(self)
        self.c['run_id']=transfer.NEXT_EXPIRED_RUN
        scope=json.loads(self.scope);scope['run_id']=self.c['run_id'];self.scope=json.dumps(scope).encode()
        self.c['scope_sha256']=hashlib.sha256(self.scope).hexdigest()
        plan=json.loads(self.plan);plan['run_id']=self.c['run_id'];self.plan=json.dumps(plan).encode()
        self.c['plan_sha256']=hashlib.sha256(self.plan).hexdigest();self.guard,*_=fixtures.handshake(self.c,self.pc,self.ps)
        b=TransferTests.run_prepare(self);self.ancestor=self.service
        b.driver.poisoned=True;b.evidence.event('FAIL_STOP',error='MANUAL_PREPARATION_EXPIRED',requests=0,commits=0,pending=False);b.evidence.close()
        thread=Alive(True)
        self.service=types.SimpleNamespace(config=self.c,driver=b.driver,state='FAILED_OR_UNKNOWN',error='MANUAL_PREPARATION_EXPIRED',
            identity=None,connections=0,inflight=False,listener=None,connection=None,neural_thread=None,
            thread=thread,expiry_thread=Alive(),lock=threading.RLock(),
            http=types.SimpleNamespace(shutdown=lambda:setattr(thread,'yes',False),server_close=lambda:None))
        prior_receipt=fixtures.JournalReader(b.evidence.journal.path).read('PREPARATION_RECEIPT.json')
        self.prior_receipt_sha=hashlib.sha256(prior_receipt).hexdigest()
        self.c,self.scope,self.plan,self.pc,self.ps=fixtures.config()
        self.c.update(transfer_from_expired_run=transfer.NEXT_EXPIRED_RUN,prior_preparation_receipt_sha256=self.prior_receipt_sha)
        plan=json.loads(self.plan);plan.update(operation='TRANSFER_ZERO_STEP_EXPIRED_OWNER_READ20',
            expired_run_id=transfer.NEXT_EXPIRED_RUN,original_source_run=transfer.ORIGINAL_RUN,prior_preparation_receipt_sha256=self.prior_receipt_sha)
        self.plan=json.dumps(plan).encode();self.c['plan_sha256']=hashlib.sha256(self.plan).hexdigest();self.guard,*_=fixtures.handshake(self.c,self.pc,self.ps)
        self.reads.clear();self.bundle=None
    def tearDown(self):TransferTests.tearDown(self)
    def next_prepare(self):
        self.bundle=transfer.prepare(self.root/'successor',self.service,self.original,self.c,self.scope,self.plan,self.guard,a3ready,cpu=True,ancestor=self.ancestor)
        return self.bundle
    def test_second_zero_step_transfer_preserves_both_failed_owners(self):
        a=sha(self.ancestor.driver.evidence.journal.path);b=sha(self.service.driver.evidence.journal.path)
        bundle=self.next_prepare()
        self.assertEqual(self.reads,fixtures.READS);self.assertEqual(self.writes,[])
        self.assertTrue(self.ancestor.driver.poisoned and self.service.driver.poisoned)
        self.assertFalse(bundle.driver.poisoned);self.assertIs(bundle.driver.src,self.original.driver.src)
        self.assertEqual((sha(self.ancestor.driver.evidence.journal.path),sha(self.service.driver.evidence.journal.path)),(a,b))
        self.assertEqual(bundle.receipt['zero_step_transfer']['ancestor_run_id'],transfer.EXPIRED_RUN)
        self.assertEqual(bundle.receipt['zero_step_transfer']['prior_preparation_receipt_sha256'],self.prior_receipt_sha)
    def test_second_transfer_wrong_receipt_rejected_before_close_or_read(self):
        self.c['prior_preparation_receipt_sha256']='00'*32
        with self.assertRaises(ValueError):self.next_prepare()
        self.assertTrue(self.service.thread.is_alive());self.assertEqual(self.reads,[])
    def test_second_transfer_wrong_ancestor_claim_rejected_before_read(self):
        self.ancestor.driver._line2_successor_claim['run_id']='00'*16
        with self.assertRaisesRegex(ValueError,'ANCESTOR_SUCCESSOR_CLAIM'):self.next_prepare()
        self.assertTrue(self.service.thread.is_alive());self.assertEqual(self.reads,[])
    def test_second_transfer_any_START_is_not_recoverable(self):
        self.service.identity=dict(run_id=transfer.NEXT_EXPIRED_RUN)
        with self.assertRaisesRegex(ValueError,'START_OR_CONNECTION'):self.next_prepare()
        self.assertEqual(self.reads,[])

if __name__=='__main__':unittest.main()

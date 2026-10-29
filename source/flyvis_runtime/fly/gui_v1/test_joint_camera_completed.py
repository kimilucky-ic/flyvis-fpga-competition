"""Bounded new lifecycle checks. CPU memory only; original completed PS bytes read-only."""
import ast,copy,hashlib,json,threading,types,unittest,uuid
from pathlib import Path
from unittest.mock import patch
from live_protocol import HERE,load,sha,write
import joint_camera_retained as transfer
from joint_camera_bundle import completed_parent
from joint_camera_manual import ManualGate,mac,board_cell
from test_joint_camera_manual import fixtures,Alive,a3ready

OUT=HERE/'evidence/camera_joint32_20261016'
REAL=HERE/'runtime/joint/19c681c711c94cbdacb7b953b1091611'

class CompletedTransferTests(unittest.TestCase):
    def setUp(self):
        self.root=OUT/'cpu_cases'/uuid.uuid4().hex;self.root.mkdir(parents=True)
        self.c,self.scope,self.plan,self.pc,self.ps=fixtures.config()
        self.original,self.reads,self.writes,self.values=fixtures.source_fixture(self.root,self.c)
        finish=load(REAL/'PS_FINISH.json')
        self.expected={k:finish[k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id',
            'completed_steps','last_unified_commit_sha256','last_txn','PS_capture_sha256')}
        self.expected['boot_id']=self.c['boot_id']
        path=REAL/'ps_retrieved_authorized/evidence.fvej'
        old=copy.copy(self.original.driver);old.requests=old.commits=3
        old.evidence=types.SimpleNamespace(journal=types.SimpleNamespace(path=path,closed=True))
        old.bound_asid='12'*16;old.committed={bytes.fromhex(old.bound_asid):(2,None,bytes.fromhex(finish['last_unified_commit_sha256']),bytes.fromhex(finish['last_txn']),0)}
        thread=Alive(True)
        old_config=dict(self.c,**{k:self.expected[k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id')})
        self.service=types.SimpleNamespace(driver=old,config=old_config,state='FINISHED_PENDING_AUDIT',error=None,
            identity={k:old_config[k] for k in ('run_id','server_session','boot_id','scope_sha256','listener_id')},
            connections=1,inflight=False,listener=None,connection=None,neural_thread=Alive(),expiry_thread=Alive(),thread=thread,
            finish_receipt=dict(finish),lock=threading.RLock(),http=types.SimpleNamespace(shutdown=lambda:setattr(thread,'yes',False),server_close=lambda:None))
        self.c.update(completed_parent=self.expected,max_steps=32,max_worker_s=300)
        s=json.loads(self.scope);s.update(max_steps=32,max_worker_s=300);self.scope=json.dumps(s).encode();self.c['scope_sha256']=hashlib.sha256(self.scope).hexdigest()
        p=json.loads(self.plan);p.update(operation='TRANSFER_COMPLETED_CAMERA_OWNER_READ20',completed_parent=self.expected,original_source_run=transfer.ORIGINAL_RUN,max_steps=32)
        self.plan=json.dumps(p).encode();self.c['plan_sha256']=hashlib.sha256(self.plan).hexdigest();self.guard,*_=fixtures.handshake(self.c,self.pc,self.ps)
        self.bundle=None
    def tearDown(self):
        if self.bundle:self.bundle.evidence.close()
    def prepare(self):
        self.bundle=transfer.prepare(self.root/'next',self.service,self.original,self.c,self.scope,self.plan,self.guard,a3ready,cpu=True)
        return self.bundle
    def test_completed_parent_preserved_read20_zero_writes(self):
        oldsha=sha(self.service.driver.evidence.journal.path)
        b=self.prepare();self.assertEqual(self.reads,fixtures.READS);self.assertEqual(self.writes,[])
        self.assertIs(b.driver.src,self.original.driver.src);self.assertEqual(self.service.state,'FINISHED_PENDING_AUDIT')
        self.assertEqual((self.service.driver.requests,self.service.driver.commits),(3,3));self.assertFalse(self.service.driver.poisoned)
        self.assertEqual(sha(self.service.driver.evidence.journal.path),oldsha)
        self.assertTrue(b.receipt['completed_transfer']['old_control_thread_stopped'])
        self.assertEqual(b.config['max_steps'],32)
    def test_uncertain_failed_pending_or_running_parent_refused(self):
        for obj,key,value in ((self.service,'state','FAILED_OR_UNKNOWN'),(self.service.driver,'pending',('p',)),
            (self.service.driver,'poisoned',True),(self.service,'inflight',True),(self.service,'neural_thread',Alive(True))):
            before=getattr(obj,key);setattr(obj,key,value)
            with self.assertRaises(ValueError):transfer.inspect_completed(self.service,self.original,a3ready,self.expected,cpu=True)
            setattr(obj,key,before)
        self.assertEqual(self.reads,[]);self.assertTrue(self.service.thread.is_alive())
    def test_wrong_capture_or_final_commit_refused_before_reads(self):
        for key in ('PS_capture_sha256','last_unified_commit_sha256','last_txn'):
            expected=copy.deepcopy(self.expected);expected[key]='00'* (16 if key=='last_txn' else 32)
            with self.assertRaises(ValueError):transfer.inspect_completed(self.service,self.original,a3ready,expected,cpu=True)
        self.assertEqual(self.reads,[])
    def test_used_parent_claim_is_never_cleared_or_reused(self):
        self.prepare()
        with self.assertRaisesRegex(ValueError,'ALREADY_TRANSFERRED'):transfer.inspect_completed(self.service,self.original,a3ready,self.expected,cpu=True)
    def test_actual_completed_parent_gate_and_manual_38_syntax(self):
        real=completed_parent();gate=ManualGate(self.root,real)
        self.assertEqual(gate.expected,dict(operation='MANUAL_PREPARE_CAMERA_COMPLETED',completed_run_id=real['run_id']))
        cell=board_cell('42'*32,real);ast.parse(cell,feature_version=(3,8))
        self.assertIn('"completed_run_id":"'+real['run_id']+'"',cell)
        self.assertNotIn('393ffe7d6860457ebf9ad4b11fbec943',cell)
        for op in ('.reset(','.download(','Overlay(','.allocate('):self.assertNotIn(op,cell)

class FinalSnapshotTests(unittest.TestCase):
    def fixture(self):
        from joint_camera_bridge import JointCameraBridge
        root=OUT/'final_cases'/uuid.uuid4().hex;root.mkdir(parents=True)
        p=dict(serial=32,state_token=32)
        write(root/'final_snapshot.json',p);write(root/'result.json',dict(status='STOPPED_PENDING_PS_AUDIT',committed_steps=32))
        write(root/'worker_exit.json',dict(committed_steps=32,cleanup_errors=[],GPU_inflight_waited=True,lease_closed=True))
        write(root/'manifest.json',dict(run_id='CPU_TEST',files={'final_snapshot.json':sha(root/'final_snapshot.json')}))
        bridge=JointCameraBridge();bridge.root=root;bridge.scope=dict(run_id='CPU_TEST');bridge.validate=lambda p:None
        return bridge
    def test_normal_end_holds_last_bound_frame(self):
        b=self.fixture();b.hold_final_snapshot();self.assertTrue(b.final_held);self.assertEqual(b.packet['serial'],32)
        self.assertEqual(b.last_status['status'],'STOPPED_PENDING_PS_AUDIT')
    def test_corrupt_or_failed_snapshot_refused(self):
        b=self.fixture();write(b.root/'final_snapshot.json',dict(serial=31,state_token=31))
        with self.assertRaisesRegex(ValueError,'SNAPSHOT_SHA'):b.hold_final_snapshot()
        b=self.fixture();write(b.root/'result.json',dict(status='FAILED_OR_IN_DOUBT',committed_steps=32))
        with self.assertRaisesRegex(ValueError,'NOT_CLEAN'):b.hold_final_snapshot()

if __name__=='__main__':unittest.main()

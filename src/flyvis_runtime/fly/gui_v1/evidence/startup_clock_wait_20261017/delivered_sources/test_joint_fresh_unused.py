"""A few bounded CPU checks for the current zero-step startup handover."""
import copy,hashlib,importlib,json,threading,types,unittest,uuid
from unittest.mock import patch
from live_protocol import HERE,load
import joint_camera_fresh as fresh
import test_joint_camera_fresh as original
from test_joint_camera_manual import fixtures,Alive
from joint_camera_board_entry import load_pinned_package

OUT=HERE/'evidence/startup_clock_wait_20261017'

class FreshUnusedTests(unittest.TestCase):
    def setUp(self):
        with patch.object(original,'OUT',OUT/'handover_cases'):
            original.FreshTests.setUp(self)
        self.bundle=None;self.new_bundle=None
        original.FreshTests.prepare(self)
        from ps_commit_evidence import install_before_bind
        install_before_bind(self.bundle,self.scope,importlib.import_module(self.package.__name__+'.protocol'))
        self.old=self.bundle;self.old.driver.poisoned=True
        self.old.evidence.event('FAIL_STOP',error='MANUAL_PREPARATION_EXPIRED',requests=0,commits=0,pending=False)
        self.old.evidence.close()
        thread=Alive(True)
        self.service=types.SimpleNamespace(config=self.c,driver=self.old.driver,state='FAILED_OR_UNKNOWN',error='MANUAL_PREPARATION_EXPIRED',
            identity=None,connections=0,inflight=False,listener=None,connection=None,neural_thread=None,
            thread=thread,expiry_thread=Alive(False),lock=threading.RLock(),
            http=types.SimpleNamespace(shutdown=lambda:setattr(thread,'yes',False),server_close=lambda:None))
        self.prior={k:self.c[k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id')}
        base={k:v for k,v in self.old.receipt.items() if k!='ps_durability'}
        self.prior['preparation_receipt_sha256']=hashlib.sha256(json.dumps(base,sort_keys=True).encode()).hexdigest()
        self.next_c=dict(self.c,run_id=uuid.uuid4().hex,server_session=uuid.uuid4().hex,listener_id=uuid.uuid4().hex,unused_fresh_parent=self.prior)
        s=json.loads(self.scope);s.update({k:self.next_c[k] for k in ('run_id','server_session','unused_fresh_parent')})
        self.next_scope=json.dumps(s).encode();self.next_c['scope_sha256']=hashlib.sha256(self.next_scope).hexdigest()
        p=json.loads(self.plan);p.update({k:self.next_c[k] for k in ('run_id','server_session','unused_fresh_parent')})
        self.next_plan=json.dumps(p).encode();self.next_c['plan_sha256']=hashlib.sha256(self.next_plan).hexdigest()
        self.next_guard,*_=fixtures.handshake(self.next_c,self.pc,self.ps)
        pins=load(fixtures.ROOT/'templates/HARDWARE_HANDOFF_NOT_PREPARED.json')['software_sha256']
        self.next_package=load_pinned_package(fixtures.ROOT,dict(run_id=self.next_c['run_id']),pins)
        self.reads.clear()

    constructor=original.FreshTests.constructor
    initialize=original.FreshTests.initialize
    configure=original.FreshTests.configure

    def tearDown(self):
        if self.new_bundle:self.new_bundle.evidence.close()
        fresh.PINNED=self.pins_before

    def transfer(self):
        self.new_bundle=fresh.prepare(self.root/'next',self.owner,self.next_c,self.next_scope,self.next_plan,self.next_guard,self.next_package,
            cpu=True,unused_service=self.service,unused_bundle=self.old)
        return self.new_bundle

    def test_zero_step_transfer_exact_handles_no_reload_reset_or_writes(self):
        b=self.transfer()
        self.assertEqual(self.reads,fixtures.READS);self.assertEqual(self.writes,[]);self.assertEqual(len(self.calls),1)
        self.assertIs(b.driver.src,self.old.driver.src);self.assertIs(b.driver.dst,self.old.driver.dst)
        self.assertTrue(self.old.driver.poisoned);self.assertTrue(self.owner.consumed)
        self.assertFalse(self.service.thread.is_alive());self.assertEqual((b.driver.requests,b.driver.commits),(0,0))
        self.assertTrue(b.receipt['unused_fresh_parent_transfer']['old_control_thread_stopped'])

    def test_started_or_wrong_identity_rejected_before_close_or_read(self):
        for name,value in (('identity',{'STARTED':True}),('connections',1),('error','UNKNOWN')):
            before=getattr(self.service,name);setattr(self.service,name,value)
            with self.subTest(name=name),self.assertRaises(ValueError):self.transfer()
            setattr(self.service,name,before)
        self.assertTrue(self.service.thread.is_alive());self.assertEqual(self.reads,[])

    def test_successor_claim_prevents_second_transfer(self):
        self.transfer()
        with self.assertRaises(ValueError):self.transfer()
        self.assertEqual(len(self.reads),20)

    def test_current_PC_parent_and_one_cell_schema(self):
        from joint_camera_bundle import fresh_unused_parent,build
        from joint_camera_manual import board_cell
        selection=fresh_unused_parent()
        self.assertEqual(selection['unused_fresh']['run_id'],'b3ab3d3be1e24ee9b69cf676f3ec4326')
        root,archive=build(self.root/'bundle',cpu_fixture=True,**selection)
        s=load(root/'scope.json');self.assertEqual(s['unused_fresh_parent'],selection['unused_fresh'])
        self.assertEqual(s['new_loads'],0);self.assertTrue(archive.exists())
        cell=board_cell('31'*32,**selection)
        import ast
        ast.parse(cell,feature_version=(3,8))
        self.assertNotIn('latency485_service_instance',cell);self.assertIn('camera_expired_owner,camera_expired_bundle',cell)

if __name__=='__main__':unittest.main()

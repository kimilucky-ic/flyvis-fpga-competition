"""Fresh initialization + original camera interface, fake constructor only."""
import copy,hashlib,importlib,json,types,unittest,uuid
from unittest.mock import patch
from live_protocol import HERE,load,sha
import joint_camera_fresh as fresh
from test_joint_camera_manual import fixtures,a3ready
from joint_camera_board_entry import load_pinned_package

OUT=HERE/'evidence/fresh_camera_start_20261017'

class FreshTests(unittest.TestCase):
    def setUp(self):
        self.root=OUT/'cpu_cases'/uuid.uuid4().hex;self.root.mkdir(parents=True)
        pins=load(fixtures.ROOT/'templates/HARDWARE_HANDOFF_NOT_PREPARED.json')['software_sha256']
        self.package=load_pinned_package(fixtures.ROOT,dict(run_id=uuid.uuid4().hex),pins)
        self.c,self.scope,self.plan,self.pc,self.ps=fixtures.config()
        self.source,self.reads,self.writes,self.values=fixtures.source_fixture(self.root,self.c)
        for k in (192,196,200):self.values[k]=0
        def dma_read(i):self.reads.append(('dma',i));return 1 if i in (0,48) else 0x1000
        self.source.driver.dma.read=dma_read
        self.init_root=self.root/'initialization';self.init_root.mkdir()
        self.init_plan=dict(schema='flyvis-manual-fresh-initialization/v1',max_steps=0,automatic_retry=False,
            new_loads=1,new_resets=1,new_allocations=2,boot_id=self.c['boot_id'],kernel_file=self.c['kernel_file'])
        raw=json.dumps(self.init_plan).encode();(self.init_root/'INIT_PLAN.json').write_bytes(raw)
        self.init_config=dict(mode=fresh.MODE,run_id=uuid.uuid4().hex,boot_id=self.c['boot_id'],kernel_file=self.c['kernel_file'],
            plan=self.init_plan,plan_sha256=hashlib.sha256(raw).hexdigest(),test_fixture=True,execution_authority='CPU_FIXTURE_ONLY',
            bit_path='CPU_ONLY_NO_IMAGE',bit_sha256=self.c['bit_sha256'],hwh_sha256=self.c['hwh_sha256'])
        self.calls=[];self.owner=None;self.bundle=None
        self.pins_before=list(fresh.PINNED);fresh.PINNED=[]
    def tearDown(self):
        if self.bundle:self.bundle.evidence.close()
        fresh.PINNED=self.pins_before
    def constructor(self,d,bit,**kw):
        self.calls.append(dict(bit=bit,authorize_load=kw['authorize_load']))
        for name in ('overlay','src','dst','reg','dma','np','boot_id'):setattr(d,name,getattr(self.source.driver,name))
        d.evidence=kw['evidence'];d.requests=d.commits=0;d.pending=None;d.poisoned=False;d.committed={}
    def initialize(self):
        self.owner=fresh.initialize(self.init_root,self.init_config,self.package,cpu=True,constructor=self.constructor,environment_check=lambda c:None)
        return self.owner
    def configure(self):
        if self.owner is None:self.initialize()
        self.c.update(max_steps=32,max_worker_s=300,fresh_initialized_parent=self.owner.receipt)
        from ps_commit_evidence import POLICY
        self.c.update(ps_durability_policy=POLICY,ps_evidence_adapter_sha256=sha(HERE/'ps_commit_evidence.py'))
        s=json.loads(self.scope);s.update(max_steps=32,max_worker_s=300,
            fresh_initialized_parent=self.owner.receipt,ps_durability_policy=POLICY,ps_evidence_adapter_sha256=self.c['ps_evidence_adapter_sha256'],
            source_sha256={'ps_commit_evidence.py':self.c['ps_evidence_adapter_sha256']})
        self.scope=json.dumps(s).encode();self.c['scope_sha256']=hashlib.sha256(self.scope).hexdigest()
        p=json.loads(self.plan);p.update(operation='FRESH_INITIALIZED_OWNER_READ20',max_steps=32,fresh_initialized_parent=self.owner.receipt)
        self.plan=json.dumps(p).encode();self.c['plan_sha256']=hashlib.sha256(self.plan).hexdigest()
        self.guard,*_=fixtures.handshake(self.c,self.pc,self.ps)
    def prepare(self):
        self.configure()
        self.bundle=fresh.prepare(self.root/'camera',self.owner,self.c,self.scope,self.plan,self.guard,self.package,cpu=True)
        return self.bundle
    def test_init_one_constructor_no_step_or_listener_and_closed_capture(self):
        o=self.initialize();self.assertEqual(len(self.calls),1);self.assertTrue(self.calls[0]['authorize_load'])
        self.assertEqual((o.driver.requests,o.driver.commits),(0,0));self.assertEqual(self.writes,[]);self.assertEqual(self.reads,[])
        self.assertTrue(o.driver.evidence.journal.closed)
        reader=fixtures.JournalReader(o.driver.evidence.journal.path)
        self.assertEqual(reader.terminal['status'],'INITIALIZATION_ONLY_NOT_NEURAL_RUN')
        self.assertEqual((o.receipt['new_loads'],o.receipt['new_resets'],o.receipt['new_allocations']),(1,1,2))
    def test_live_cannot_use_CPU_injection_or_authority(self):
        with self.assertRaisesRegex(ValueError,'AUTHORITY'):
            fresh.initialize(self.init_root,self.init_config,self.package,constructor=self.constructor,environment_check=lambda c:None)
        self.assertEqual(self.calls,[])
    def test_wrong_plan_or_scope_rejected_before_constructor(self):
        self.init_config['plan_sha256']='00'*32
        with self.assertRaises(ValueError):self.initialize()
        self.assertEqual(self.calls,[])
    def test_failed_constructor_poison_and_no_retry(self):
        def fail(d,*a,**kw):self.constructor(d,*a,**kw);raise RuntimeError('CPU_INJECTED_INIT_FAILURE')
        with self.assertRaises(RuntimeError):fresh.initialize(self.init_root,self.init_config,self.package,cpu=True,constructor=fail,environment_check=lambda c:None)
        self.assertTrue(fresh.PINNED[0].poisoned)
        with self.assertRaisesRegex(ValueError,'ALREADY_ATTEMPTED'):self.initialize()
        self.assertEqual(len(self.calls),1)
    def test_original_read20_zero_writes_actual_zero_counters_idle0(self):
        b=self.prepare();self.assertEqual(self.reads,fixtures.READS);self.assertEqual(self.writes,[])
        self.assertEqual([r['value'] for r in b.receipt['reads'] if r['bank']=='reg' and r['offset'] in (192,196,200)],[0,0,0])
        self.assertEqual([r['value'] for r in b.receipt['reads'] if r['bank']=='dma' and r['offset'] in (4,52)],[0x1000,0x1000])
        self.assertTrue(self.owner.consumed);self.assertIs(b.driver.src,self.owner.driver.src)
        self.assertEqual(b.receipt['new_loads'],0);self.assertEqual(len(self.calls),1)
    def test_consumed_source_cannot_prepare_twice(self):
        self.prepare()
        with self.assertRaisesRegex(ValueError,'SOURCE_IDENTITY'):
            fresh.prepare(self.root/'repeat',self.owner,self.c,self.scope,self.plan,self.guard,self.package,cpu=True)
        self.assertEqual(len(self.reads),20)
    def test_used_pending_or_wrong_boot_source_rejected(self):
        self.configure()
        for key,v in (('requests',1),('pending',('x',)),('poisoned',True),('boot_id','REBOOT')):
            before=getattr(self.owner.driver,key);setattr(self.owner.driver,key,v)
            with self.subTest(key=key),self.assertRaises(ValueError):fresh.prepare(self.root/key,self.owner,self.c,self.scope,self.plan,self.guard,self.package,cpu=True)
            setattr(self.owner.driver,key,before)
        self.assertEqual(self.reads,[])
    def test_init_capture_tamper_rejected(self):
        self.configure()
        with self.owner.driver.evidence.journal.path.open('ab') as f:f.write(b'bad')
        with self.assertRaisesRegex(ValueError,'CAPTURE_CHANGED'):
            fresh.prepare(self.root/'bad',self.owner,self.c,self.scope,self.plan,self.guard,self.package,cpu=True)
        self.assertEqual(self.reads,[])
    def test_wrong_registers_stop_no_automatic_reset(self):
        self.values[24]=1
        with self.assertRaisesRegex(ValueError,'INITIAL_IDLE'):self.prepare()
        self.assertEqual(self.writes,[]);self.assertTrue(self.owner.consumed)
    def test_raw_receipt_errors_halted_sg_nonzero_counters_rejected(self):
        b=self.prepare();wire=importlib.import_module(self.package.__name__+'.protocol')
        for bank,offset,value in (('reg',192,17304),('reg',200,57681),('dma',4,1),('dma',52,0x1010),('dma',4,8)):
            r=copy.deepcopy(b.receipt)
            next(row for row in r['reads'] if row['bank']==bank and row['offset']==offset)['value']=value
            with self.subTest(bank=bank,offset=offset,value=value),self.assertRaises(ValueError):fresh.read_receipt(self.c,r,wire)
    def test_legacy_namespace_and_numeric_code_unchanged(self):
        old=importlib.import_module('a3ready.binding').validate_readonly_receipt
        driver=importlib.import_module(self.package.__name__+'.driver');run,finish=driver.Full485Driver.run,driver.Full485Driver.finish
        self.prepare()
        self.assertIs(importlib.import_module('a3ready.binding').validate_readonly_receipt,old)
        self.assertIs(driver.Full485Driver.run,run);self.assertIs(driver.Full485Driver.finish,finish)
    def test_original_GUI_signed_reader_accepts_fresh_without_claiming_old485(self):
        from ps_commit_evidence import install_before_bind
        from joint_camera_preparation import verify_prepared_packet
        b=self.prepare();wire=importlib.import_module(self.package.__name__+'.protocol');install_before_bind(b,self.scope,wire)
        declaration=load(fixtures.ROOT/'templates/HARDWARE_HANDOFF_NOT_PREPARED.json')
        for key in ('run_id','server_session','boot_id','listener_id','plan_sha256','ps_durability_policy','ps_evidence_adapter_sha256','fresh_initialized_parent'):declaration[key]=self.c[key]
        declaration['control_config']=dict(control_key=self.c['control_key'])
        clock=self.guard.receipt(self.c);binding=clock['binding']
        status=dict(binding,state='BOARD_PREPARED',requests=0,commits=0,pending=False,poisoned=False,error=None,neural_connections=0,
            service_alive=True,clock_policy=clock['policy'],clock_proof_sha256=clock['proof_sha256'])
        body=dict(schema='flyvis-camera-retained-prepared/v1',binding=binding,preparation_receipt=b.receipt,clock_receipt=clock,status=status)
        self.assertEqual(verify_prepared_packet(fixtures.sign(body,self.c['control_key']),declaration,json.loads(self.scope),self.c['scope_sha256']),body)
        self.assertNotIn('completed_parent',body['preparation_receipt']);self.assertNotIn('zero_step_transfer',body['preparation_receipt'])
    def test_build_original_32step_archive_with_fresh_parent_CPU_ONLY(self):
        import joint_camera_bundle as bundle,zipfile
        self.initialize();root,archive=bundle.build(self.root/'cpu_bundle',cpu_fixture=True,fresh=self.owner.receipt)
        s=load(root/'scope.json');c=load(root/'PRIVATE_CONFIG.json')
        self.assertEqual(s['fresh_initialized_parent'],self.owner.receipt);self.assertEqual(s['new_loads'],0)
        self.assertEqual((s['boot_id'],c['retained_src_address']),(self.owner.receipt['boot_id'],self.owner.receipt['src_address']))
        self.assertEqual((s['max_steps'],s['capture_duration_s']),(32,30));self.assertTrue(s['recording_required_before_camera'])
        with zipfile.ZipFile(archive) as z:self.assertEqual(hashlib.sha256(z.read('fresh_camera.py')).hexdigest(),sha(HERE/'joint_camera_fresh.py'))
        from joint_camera_board_entry import run
        with self.assertRaisesRegex(AssertionError,'REJECTS_CPU'):run(root,self.owner)

if __name__=='__main__':unittest.main()

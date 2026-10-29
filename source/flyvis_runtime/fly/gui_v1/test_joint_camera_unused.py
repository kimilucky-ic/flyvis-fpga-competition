"""Known pre-START expiry recovery; CPU objects and saved captures only."""
import ast,copy,hashlib,json,threading,types,unittest,uuid,zipfile
from unittest.mock import patch
from live_protocol import HERE,load,sha
import joint_camera_bundle as bundles
import joint_camera_retained as transfer
from joint_camera_manual import ManualGate,mac,board_cell
from test_joint_camera_manual import fixtures,Alive,a3ready

OUT=HERE/'evidence/unused_parent_prepare_20261017'
REAL=HERE/'runtime/joint/7f111da4437843539eeffef2c6c2546e'

class UnusedTransferTests(unittest.TestCase):
    def setUp(self):
        self.root=OUT/'cpu_cases'/uuid.uuid4().hex;self.root.mkdir(parents=True)
        self.c,self.scope,self.plan,self.pc,self.ps=fixtures.config()
        self.original,self.reads,self.writes,self.values=fixtures.source_fixture(self.root,self.c)
        finish=load(REAL/'PS_FINISH.json')
        self.prior={k:finish[k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id',
            'completed_steps','last_unified_commit_sha256','last_txn','PS_capture_sha256')}
        self.prior['boot_id']=self.c['boot_id']
        d=copy.copy(self.original.driver);d.requests=d.commits=32
        d.evidence=types.SimpleNamespace(journal=types.SimpleNamespace(path=REAL/'ps_retrieved_authorized/evidence.fvej',closed=True))
        d.bound_asid='12'*16;d.committed={bytes.fromhex(d.bound_asid):(31,None,bytes.fromhex(finish['last_unified_commit_sha256']),bytes.fromhex(finish['last_txn']),0)}
        parent_config=dict(self.c,**{k:self.prior[k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id')})
        self.parent=types.SimpleNamespace(driver=d,config=parent_config,state='FINISHED_PENDING_AUDIT',error=None,
            identity={k:parent_config[k] for k in ('run_id','server_session','boot_id','scope_sha256','listener_id')},
            connections=1,inflight=False,listener=None,connection=None,neural_thread=Alive(),expiry_thread=Alive(),thread=Alive(),
            finish_receipt=finish,lock=threading.RLock())
        self.old_config=dict(self.c,run_id=transfer.UNUSED_EXPIRED_RUN,server_session=uuid.uuid4().hex,
            scope_sha256='61'*32,plan_sha256='62'*32,listener_id=uuid.uuid4().hex,completed_parent=self.prior)
        d._line2_successor_claim={k:self.old_config[k] for k in ('run_id','server_session','scope_sha256','plan_sha256')}
        self.original.driver._camera_ready_claim=dict(run_id='PRESERVED_OLD_CLAIM')
        old=copy.copy(self.original.driver);old.requests=old.commits=0;old.pending=None;old.poisoned=True
        old.bound_asid=None;old.committed={};old.compute_deadline=None
        old.evidence=fixtures.Evidence(self.root/'unused_ps',self.old_config)
        receipt={k:self.old_config[k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id')}
        receipt['completed_transfer']=dict(parent_run_id=self.prior['run_id'],parent_capture_sha256=self.prior['PS_capture_sha256'],old_control_thread_stopped=True)
        raw=json.dumps(receipt,sort_keys=True).encode();old.evidence.journal.add('PREPARATION_RECEIPT.json',raw)
        old.evidence.event('FAIL_STOP',error='MANUAL_PREPARATION_EXPIRED',requests=0,commits=0,pending=False);old.evidence.close()
        thread=Alive(True)
        self.service=types.SimpleNamespace(driver=old,config=self.old_config,state='FAILED_OR_UNKNOWN',error='MANUAL_PREPARATION_EXPIRED',
            identity=None,connections=0,inflight=False,listener=None,connection=None,neural_thread=None,
            thread=thread,expiry_thread=Alive(),lock=threading.RLock(),
            http=types.SimpleNamespace(shutdown=lambda:setattr(thread,'yes',False),server_close=lambda:None))
        self.expected={k:self.old_config[k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id')}
        self.expected.update(completed_parent=self.prior,preparation_receipt_sha256=hashlib.sha256(raw).hexdigest(),
            preparation_packet_sha256='63'*32,PC_cleanup_sha256='64'*32)
        self.c.update(unused_parent=self.expected,max_steps=32,max_worker_s=300)
        from ps_commit_evidence import POLICY
        self.c.update(ps_durability_policy=POLICY,ps_evidence_adapter_sha256=sha(HERE/'ps_commit_evidence.py'))
        s=json.loads(self.scope);s.update(max_steps=32,max_worker_s=300,
            **{k:self.c[k] for k in ('ps_durability_policy','ps_evidence_adapter_sha256')},
            source_sha256={'ps_commit_evidence.py':self.c['ps_evidence_adapter_sha256']})
        self.scope=json.dumps(s).encode();self.c['scope_sha256']=hashlib.sha256(self.scope).hexdigest()
        p=json.loads(self.plan);p.update(operation='TRANSFER_UNUSED_CAMERA_OWNER_READ20',unused_parent=self.expected,
            original_source_run=transfer.ORIGINAL_RUN,max_steps=32)
        self.plan=json.dumps(p).encode();self.c['plan_sha256']=hashlib.sha256(self.plan).hexdigest()
        self.guard,*_=fixtures.handshake(self.c,self.pc,self.ps);self.bundle=None
        self.old_hashes=(sha(old.evidence.journal.path),sha(d.evidence.journal.path),sha(self.original.driver.evidence.journal.path))
        self.old_claims=copy.deepcopy((d._line2_successor_claim,self.original.driver._camera_ready_claim))
    def tearDown(self):
        if self.bundle:self.bundle.evidence.close()
    def inspect(self):return transfer.inspect_unused_parent(self.service,self.original,a3ready,self.expected,self.parent,cpu=True)
    def prepare(self):
        self.bundle=transfer.prepare(self.root/'next',self.service,self.original,self.c,self.scope,self.plan,self.guard,a3ready,cpu=True,ancestor=self.parent)
        return self.bundle
    def test_transfer_preserves_three_owners_and_original_captures(self):
        b=self.prepare()
        self.assertEqual(self.reads,fixtures.READS);self.assertEqual(self.writes,[])
        for name in ('overlay','src','dst','reg','dma','np'):self.assertIs(getattr(b.driver,name),getattr(self.original.driver,name))
        self.assertTrue(self.service.driver.poisoned);self.assertFalse(b.driver.poisoned)
        self.assertEqual((b.driver.requests,b.driver.commits),(0,0));self.assertIsNone(b.driver.pending)
        self.assertEqual(self.old_claims,(self.parent.driver._line2_successor_claim,self.original.driver._camera_ready_claim))
        self.assertEqual(self.old_hashes,(sha(self.service.driver.evidence.journal.path),sha(self.parent.driver.evidence.journal.path),sha(self.original.driver.evidence.journal.path)))
        self.assertFalse(self.service.thread.is_alive());self.assertTrue(self.original.thread.is_alive())
        self.assertTrue(b.receipt['unused_parent_transfer']['old_control_thread_stopped'])
        b.evidence.close()
        reader=fixtures.JournalReader(b.evidence.journal.path)
        self.assertEqual(hashlib.sha256(reader.read('PARENT_UNUSED_CAPTURE.fvej')).hexdigest(),self.old_hashes[0])
    def test_started_pending_connected_or_unknown_failure_rejected_before_reads(self):
        for obj,key,value in ((self.service,'identity',{}),(self.service,'connections',1),(self.service,'inflight',True),
            (self.service,'error','COMMIT_TIMEOUT'),(self.service,'neural_thread',Alive()),
            (self.service.driver,'pending',('x',)),(self.service.driver,'requests',1),
            (self.service.driver,'bound_asid','12'*16),(self.service.driver,'compute_deadline',1)):
            old=getattr(obj,key);setattr(obj,key,value)
            with self.subTest(key=key),self.assertRaises(ValueError):self.inspect()
            setattr(obj,key,old)
        self.assertEqual(self.reads,[]);self.assertTrue(self.service.thread.is_alive())
    def test_wrong_unused_or_completed_identity_rejected(self):
        for obj,key,value in ((self.service.config,'scope_sha256','00'*32),(self.expected,'preparation_receipt_sha256','00'*32),
            (self.parent.driver._line2_successor_claim,'run_id','00'*16),(self.parent.config,'listener_id','00'*16)):
            old=obj[key];obj[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.inspect()
            obj[key]=old
        self.assertEqual(self.reads,[])
    def test_parent_thread_still_active_rejected(self):
        self.parent.thread.yes=True
        with self.assertRaisesRegex(ValueError,'ANCESTOR_CONTROL_ACTIVE'):self.inspect()
        self.assertEqual(self.reads,[])
    def test_changed_shared_handle_rejected(self):
        self.service.driver.src=object()
        with self.assertRaisesRegex(ValueError,'SHARED_HANDLES'):self.inspect()
        self.assertEqual(self.reads,[])
    def test_changed_boot_rejected_before_close_or_reads(self):
        self.c['boot_id']='REBOOT'
        with self.assertRaises(ValueError):self.prepare()
        self.assertTrue(self.service.thread.is_alive());self.assertEqual(self.reads,[])
    def test_corrupt_old_closed_capture_rejected(self):
        with self.service.driver.evidence.journal.path.open('ab') as f:f.write(b'bad')
        with self.assertRaises(ValueError):self.inspect()
        self.assertEqual(self.reads,[])
    def test_http_close_not_confirmed_prevents_new_claim(self):
        self.service.http.shutdown=lambda:None
        with self.assertRaisesRegex(ValueError,'STOP_UNCONFIRMED'):self.prepare()
        self.assertFalse(hasattr(self.service.driver,'_line2_successor_claim'));self.assertEqual(self.reads,[])
    def test_bad_register_read_consumes_only_new_claim(self):
        self.values[24]=1
        with self.assertRaises(ValueError):self.prepare()
        self.assertTrue(self.service.driver._line2_successor_claim);self.assertTrue(self.service.driver.poisoned)
        self.assertEqual(self.writes,[]);self.assertEqual(self.old_claims,(self.parent.driver._line2_successor_claim,self.original.driver._camera_ready_claim))
    def test_repeated_transfer_refused(self):
        self.prepare()
        with self.assertRaisesRegex(ValueError,'CONSUMED'):self.inspect()
        self.assertEqual(len(self.reads),20)
    def packet(self):
        from ps_commit_evidence import install_before_bind
        b=self.prepare();install_before_bind(b,self.scope,a3ready.protocol)
        clock=self.guard.receipt(self.c);binding=clock['binding']
        declaration=load(fixtures.ROOT/'templates/HARDWARE_HANDOFF_NOT_PREPARED.json')
        declaration.update({k:self.c[k] for k in ('run_id','server_session','boot_id','listener_id','plan_sha256','ps_durability_policy','ps_evidence_adapter_sha256')})
        declaration.update(unused_parent=self.expected,control_config=dict(control_key=self.c['control_key']))
        status=dict(binding,state='BOARD_PREPARED',requests=0,commits=0,pending=False,poisoned=False,error=None,
            neural_connections=0,service_alive=True,clock_policy=clock['policy'],clock_proof_sha256=clock['proof_sha256'])
        body=dict(schema='flyvis-camera-retained-prepared/v1',binding=binding,preparation_receipt=b.receipt,clock_receipt=clock,status=status)
        return declaration,body
    def test_real_signed_transfer_with_current_policy_passes_GUI_reader(self):
        from joint_camera_preparation import verify_prepared_packet
        declaration,body=self.packet();packet=fixtures.sign(body,self.c['control_key'])
        self.assertEqual(verify_prepared_packet(packet,declaration,json.loads(self.scope),self.c['scope_sha256']),body)
        (self.root/'SIGNED_CPU_PACKET.json').write_text(json.dumps(packet,indent=2),encoding='utf8')
    def test_tampered_transfer_policy_clock_or_pending_rejected(self):
        from joint_camera_preparation import verify_prepared_packet
        declaration,body=self.packet()
        for path,value in ((('preparation_receipt','unused_parent_transfer','old_control_thread_stopped'),False),
            (('preparation_receipt','unused_parent_transfer','requests'),1),
            (('preparation_receipt','unused_parent_transfer','preparation_receipt_sha256'),'00'*32),
            (('preparation_receipt','ps_durability','normal_step_barriers'),4),
            (('clock_receipt','binding','run_id'),'00'*16),(('status','pending'),True)):
            bad=copy.deepcopy(body);node=bad
            for key in path[:-1]:node=node[key]
            node[path[-1]]=value
            with self.subTest(path=path),self.assertRaises(ValueError):
                verify_prepared_packet(fixtures.sign(bad,self.c['control_key']),declaration,json.loads(self.scope),self.c['scope_sha256'])
        with self.assertRaises(ValueError):
            verify_prepared_packet(dict(body=body,mac='00'*32),declaration,json.loads(self.scope),self.c['scope_sha256'])

class PCSelectionAndCellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selection=bundles.preparation_parent();cls.unused=cls.selection['unused']
        cls.root,cls.archive=bundles.build(OUT/'cpu_archives',unused=cls.unused,cpu_fixture=True)
    def test_actual_pinned_PC_failure_selected_without_live_proof(self):
        self.assertEqual(self.unused['run_id'],transfer.UNUSED_EXPIRED_RUN);self.assertIsNone(self.selection['completed'])
        self.assertEqual(self.unused['completed_parent']['completed_steps'],32)
        (OUT/'READ_ONLY_PC_SELECTION.json').write_text(json.dumps(dict(status='PC_SOURCE_CHECK_ONLY_NOT_BOARD_PREPARATION',selection=self.selection),indent=2),encoding='utf8')
    def test_unknown_or_running_active_session_refused(self):
        actual=load(HERE/'runtime/joint_active.json');real_load=bundles.load
        for changed in (dict(actual,state='RUNNING'),dict(actual,run_id='00'*16),dict(actual,session_id='00'*16),dict(actual,exit_codes=dict(gui=0,joint_worker=0))):
            with patch.object(bundles,'load',side_effect=lambda p:changed if p==HERE/'runtime/joint_active.json' else real_load(p)),self.assertRaises(ValueError):
                bundles.preparation_parent()
    def test_original_completed_parent_path_remains_supported(self):
        real_load=bundles.load;active=dict(run_id='2884821c976c4fb6851d61e17cbc22c5',session_id=REAL.name,state='STOPPED',exit_codes=dict(gui=0,joint_worker=0))
        with patch.object(bundles,'load',side_effect=lambda p:active if p==HERE/'runtime/joint_active.json' else real_load(p)):
            choice=bundles.preparation_parent()
        self.assertIsNone(choice['unused']);self.assertEqual(choice['completed']['completed_steps'],32)
    def test_archive_nonexecutable_new_ids_and_bound_current_runtime(self):
        s=load(self.root/'scope.json');c=load(self.root/'PRIVATE_CONFIG.json')
        for name in ('scope.json','PLAN.json','PRIVATE_CONFIG.json','USER_AUTHORIZATION.json'):
            self.assertEqual(load(self.root/name)['execution_authority'],'CPU_FIXTURE_ONLY')
        self.assertTrue(c['test_fixture']);self.assertIsNone(s['human_authorization_reference'])
        self.assertNotIn(s['run_id'],(transfer.UNUSED_EXPIRED_RUN,self.unused['completed_parent']['run_id']))
        self.assertEqual((s['max_steps'],s['capture_duration_s'],s['max_worker_s']),(32,30,300));self.assertTrue(s['recording_required_before_camera'])
        with zipfile.ZipFile(self.archive) as z:
            pins=load(self.root/'RUNTIME_SHA256.json')
            for name,digest in pins.items():self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(),digest)
        self.assertEqual(c['unused_parent'],self.unused)
        from joint_camera_protocol import validate_scope
        with self.assertRaisesRegex(ValueError,'NOT_AUTHORIZED'):validate_scope(s)
    def test_CPU_archive_cannot_enter_board_start_path(self):
        from joint_camera_board_entry import run
        with self.assertRaisesRegex(AssertionError,'REJECTS_CPU_FIXTURE'):run(self.root,object())
    def test_one_manual_cell_python38_no_board_initialization_or_START(self):
        cell=board_cell('42'*32,**self.selection);ast.parse(cell,feature_version=(3,8))
        self.assertEqual(cell.count('camera_entry.run('),1)
        self.assertIn('MANUAL_PREPARE_CAMERA_UNUSED',cell);self.assertIn(self.unused['scope_sha256'],cell)
        for op in ('Overlay(','.reset(','.download(','.allocate(','.step(','.commit(','/start'):
            self.assertNotIn(op,cell)
        (OUT/'CPU_CELL_REDACTED.py').write_text(cell.replace('42'*32,'CPU_ONLY_NON_SECRET_TOKEN'),encoding='utf8')
    def test_missing_or_wrong_retained_owner_stops_before_download(self):
        prefix=board_cell('42'*32,**self.selection).split('camera_token = ')[0]
        for env in ({},dict(latency485_service_instance=object(),camera3_service_instance=types.SimpleNamespace(config={'run_id':'wrong'}),camera3_bundle=object())):
            with self.assertRaises(AssertionError):exec(prefix,env)
    def test_invalid_peer_auth_scope_never_builds_and_does_not_consume(self):
        gate=ManualGate(OUT,**self.selection);packet=dict(body=gate.expected,mac=mac(gate.expected,gate.token))
        with patch.object(bundles,'build',side_effect=AssertionError('NO_BUILD')):
            for p,peer in ((packet,'127.0.0.1'),(dict(packet,mac='00'*32),'192.168.2.99'),(dict(body={},mac=mac({},gate.token)),'192.168.2.99')):
                with self.assertRaises(ValueError):gate.bundle(p,peer)
        self.assertFalse(gate.consumed);self.assertIsNone(gate.authority)
    def test_one_authenticated_request_only_and_no_network_fixture(self):
        gate=ManualGate(OUT,**self.selection);packet=dict(body=gate.expected,mac=mac(gate.expected,gate.token))
        class NoNetworkAuthority:
            def init__(self,root):self.root=root;self.started=False
            def start(self):self.started=True
        with patch.object(bundles,'build',return_value=(self.root,self.archive)) as build,patch('joint_camera_manual.PreparationAuthority',NoNetworkAuthority):
            answer=gate.bundle(packet,'192.168.2.99')
            self.assertEqual(build.call_args.kwargs,dict(unused=self.unused));self.assertTrue(gate.authority.started)
            self.assertEqual(answer['mac'],mac(answer['body'],gate.token))
            with self.assertRaisesRegex(ValueError,'CONSUMED'):gate.bundle(packet,'192.168.2.99')
            build.assert_called_once()

if __name__=='__main__':unittest.main()

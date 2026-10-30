"""CPU-only repeat lifecycle and saved-real-data acceptance; no device opens."""
import base64,copy,hashlib,io,json,os,shutil,time,unittest,uuid,zipfile
import threading
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from live_protocol import HERE,load,sha,write
from joint_camera_repeat import WorkspaceUI,RepeatEndpoint
from joint_camera_manual import mac
from joint_camera_repeat_board import verify_bundle,family_deadline

OUT=HERE/'evidence/repeat_workbench_20261018'

class LifecycleTests(unittest.TestCase):
    def test_original_execute_reuses_existing_workspace_gui_and_starts_one_worker_only(self):
        import joint_camera_controller as controller
        from contextlib import nullcontext
        import tempfile
        with tempfile.TemporaryDirectory(dir=OUT) as tmp:
            base=Path(tmp);stage=base/'stage';stage.mkdir();workspace=base/'workspace';workspace.mkdir()
            source=HERE/'runtime/joint/c59286b40c9c4c2e84a3e456a0856540'
            scope=load(source/'scope.json');scope.update(session_id=uuid.uuid4().hex,source_sha256={})
            write(stage/'scope.json',scope);shutil.copy2(source/'hardware_handoff.json',stage/'hardware_handoff.json')
            instance=uuid.uuid4().hex
            write(workspace/'state.json',dict(phase='GPU_PREPARING',instance_id=instance))
            write(workspace/'instances'/instance/'controller.json',dict(unix_time=0,pid=0))
            write(base/'active.json',dict(state='STOPPED'))
            child=SimpleNamespace(pid=12345,poll=lambda:0)
            with patch.object(controller,'HERE',base),patch.object(controller,'ACTIVE',base/'active.json'),\
                patch.object(controller,'check',return_value=(scope,{})),patch.object(controller,'linux',return_value='/CPU_ONLY'),\
                patch.object(controller,'Registry',return_value=SimpleNamespace(data={'runtime':{'python':'CPU_FAKE'}})),\
                patch('launch_recovery.launch_guard',return_value=nullcontext()),\
                patch('launch_recovery.gui_port_available',side_effect=AssertionError('must reuse owned GUI')) as port,\
                patch.object(controller.subprocess,'Popen',return_value=child) as spawn:
                result=controller.execute(stage/'scope.json',stage/'hardware_handoff.json',workspace=workspace)
            port.assert_not_called();self.assertEqual(spawn.call_count,1)
            self.assertEqual(spawn.call_args.args[0][0],'wsl.exe')
            self.assertEqual(load(base/'active.json')['exit_codes'],dict(joint_worker=0))
            self.assertEqual(load(workspace/'state.json')['current_session'],str(result/'session.json'))
            beat=load(workspace/'instances'/instance/'controller.json')
            self.assertEqual(beat['pid'],os.getpid());self.assertGreater(beat['unix_time'],time.time()-5)
            self.assertFalse((workspace/'controller.json').exists())

    def test_standalone_execute_still_rejects_occupied_port_before_worker(self):
        import joint_camera_controller as controller
        from contextlib import nullcontext
        import tempfile
        with tempfile.TemporaryDirectory(dir=OUT) as tmp:
            base=Path(tmp);write(base/'active.json',dict(state='STOPPED'))
            with patch.object(controller,'HERE',base),patch.object(controller,'ACTIVE',base/'active.json'),\
                patch.object(controller,'check',return_value=({},{})),patch.object(controller,'Registry',return_value=None),\
                patch('launch_recovery.launch_guard',return_value=nullcontext()),\
                patch('launch_recovery.gui_port_available',side_effect=ValueError('OCCUPIED')),patch.object(controller.subprocess,'Popen') as spawn:
                with self.assertRaisesRegex(ValueError,'OCCUPIED'):controller.execute('CPU_SCOPE','CPU_HANDOFF')
                spawn.assert_not_called()
    def test_family_expiry_uses_signed_PC_time_and_PS_monotonic_not_PS_calendar(self):
        stamp=dict(utc_upper_ns=1001000000000,rate_error_bound_ppm=1000)
        service=SimpleNamespace(driver=SimpleNamespace(clock_guard=SimpleNamespace(check=lambda c:stamp)),config={})
        family=dict(created_unix=1000,expires_unix=1300,max_runs=100)
        with patch('joint_camera_repeat_board.time.time',side_effect=AssertionError('PS calendar is not PC UTC')),patch('joint_camera_repeat_board.time.monotonic',return_value=50):
            self.assertAlmostEqual(family_deadline(family,service),50+299/1.001)
            with self.assertRaisesRegex(ValueError,'HUMAN_SCOPE'):family_deadline(dict(family,expires_unix=999),service)
    def workspace(self):
        w=HERE/'runtime/joint_workbench'/uuid.uuid4().hex;w.mkdir(parents=True)
        family=dict(family_id=uuid.uuid4().hex,created_unix=time.time(),expires_unix=time.time()+300,max_runs=100)
        write(w/'state.json',dict(family=family,phase='READY_TO_START',instance_id=uuid.uuid4().hex,completed_runs=0,current_session=None))
        write(w/'CPU_FIXTURE_ONLY.json',dict(GPU=0,camera=0,board=0))
        return w,WorkspaceUI(w),family
    def test_start_is_one_use_until_audit_rearms_and_failure_blocks(self):
        w,ui,f=self.workspace();self.assertTrue(ui.status()['can_start'])
        body=dict(family_id=f['family_id']);ui.rearm(body)
        self.assertFalse(ui.status()['can_start'])
        with self.assertRaises(ValueError):ui.rearm(body)
        s=load(w/'state.json');s['phase']='AUDITING';write(w/'state.json',s)
        with self.assertRaises(ValueError):ui.rearm(body)
        s['phase']='COMPLETE';write(w/'state.json',s);ui.rearm(body)
        s['phase']='FAILED';s['error']='BAD_ACK';write(w/'state.json',s)
        self.assertFalse(ui.status()['can_start'])
        with self.assertRaises(ValueError):ui.rearm(body)
    def test_quit_is_scoped_and_never_starts_devices(self):
        w,ui,f=self.workspace();ui.quit()
        self.assertEqual(load(w/'QUIT.json')['instance_id'],load(w/'state.json')['instance_id'])
        self.assertIsNone(ui.bridge);self.assertIsNone(ui.preview()['packet'])
    def test_wrong_family_and_expiry_never_consume_start(self):
        w,ui,f=self.workspace()
        with self.assertRaises(ValueError):ui.rearm(dict(family_id='0'*32))
        s=load(w/'state.json');s['family']['expires_unix']=time.time()-1;write(w/'state.json',s)
        with self.assertRaises(ValueError):ui.rearm(dict(family_id=f['family_id']))
        self.assertFalse((w/'START_REQUEST.json').exists())
    def test_signed_poll_wait_and_peer_identity_rejections(self):
        _,_,f=self.workspace();binding=dict(run_id='1'*32,scope_sha256='2'*64,boot_id='CPU')
        h=dict(binding,control_config=dict(control_key='31'*32));ep=RepeatEndpoint(None,h,f)
        b=dict(family_id=f['family_id'],binding=binding,nonce='4'*32);p=dict(body=b,mac=mac(b,'31'*32))
        reply=ep.next(p,'192.168.2.99');self.assertEqual(reply['body']['status'],'WAIT')
        self.assertIsNone(verify_bundle(reply,'31'*32,binding,f,{}))
        for peer,bad in [('127.0.0.1',p),('192.168.2.99',dict(p,mac='0'*64))]:
            with self.assertRaises(ValueError):ep.next(bad,peer)
        wrong=copy.deepcopy(reply);wrong['body']['binding']['run_id']='8'*32
        with self.assertRaises(ValueError):verify_bundle(wrong,'31'*32,binding,f,{})
    def test_new_bundle_preserves_release_and_original_no_reset_limits(self):
        from joint_camera_bundle import audited_compute_parent,build
        root=HERE/'runtime/joint/c59286b40c9c4c2e84a3e456a0856540'
        active=dict(state='STOPPED',run_id='ad5b4adac2b941f59b4a5271d1bde1fe',session_id=root.name,root=str(root),exit_codes=dict(gui=0,joint_worker=0))
        parent=audited_compute_parent(active,root);_,_,family=self.workspace()
        folder=OUT/'cpu_cases'/uuid.uuid4().hex;folder.mkdir(parents=True)
        new,archive=build(folder,**parent,minimal_compute=True,live5=True,cpu_fixture=True,repeat_family=family)
        scope=load(new/'scope.json');config=load(new/'PRIVATE_CONFIG.json');runtime=load(new/'RUNTIME_SHA256.json')
        self.assertEqual(scope['repeat_family'],config['repeat_family']);self.assertIn('repeat_board.py',runtime)
        binding=dict(run_id=parent['completed_fresh']['run_id'],scope_sha256=parent['completed_fresh']['scope_sha256'],boot_id=scope['boot_id'])
        body=dict(status='PREPARE',binding=binding,family_id=family['family_id'],root_name='CAMERA3_'+scope['run_id'],
            archive_b64=base64.b64encode(archive.read_bytes()).decode(),archive_sha256=sha(archive))
        packet=dict(body=body,mac=mac(body,'31'*32))
        self.assertEqual(verify_bundle(packet,'31'*32,binding,family,runtime)[1],body['root_name'])
        with self.assertRaisesRegex(ValueError,'RELEASE_CHANGED'):verify_bundle(packet,'31'*32,binding,family,{})

    def test_second_double_click_does_not_enter_a_running_round_mutex(self):
        import joint_camera_repeat as repeat
        f=OUT/'cpu_owner'/uuid.uuid4().hex;owned=f/'instance';owned.mkdir(parents=True)
        write(f/'active.json',dict(state='RUNNING',pid=123,instance_dir=str(owned)))
        write(owned/'controller.json',dict(unix_time=time.time()))
        with patch.object(repeat,'ACTIVE',f/'active.json'),patch('launch_recovery.process_alive',return_value=True),\
            patch('launch_recovery.launch_guard',side_effect=AssertionError('second mutex')),patch.object(repeat.webbrowser,'open') as opened:
            repeat.run_workbench(lambda *a,**kw:(_ for _ in ()).throw(AssertionError('second GPU')))
        opened.assert_called_once()

    def test_repeat_installation_must_ack_exact_new_scope_and_helper_source(self):
        _,_,family=self.workspace();folder=OUT/'cpu_ready'/uuid.uuid4().hex;folder.mkdir(parents=True)
        write(folder/'scope.json',dict(run_id='3'*32))
        h=dict(run_id='3'*32,boot_id='CPU',control_config=dict(control_key='31'*32))
        write(folder/'hardware_handoff.json',h)
        endpoint=RepeatEndpoint(SimpleNamespace(root=folder),{},family)
        notice=dict(family_id=family['family_id'],binding=dict(run_id=h['run_id'],boot_id='CPU',scope_sha256=sha(folder/'scope.json')),
            repeat_board_sha256=sha(HERE/'joint_camera_repeat_board.py'))
        wrong=dict(notice,repeat_board_sha256='0'*64)
        with self.assertRaises(ValueError):endpoint.ready(dict(body=wrong,mac=mac(wrong,'31'*32)),'192.168.2.99')
        self.assertIsNone(endpoint.installed_run)
        reply=endpoint.ready(dict(body=notice,mac=mac(notice,'31'*32)),'192.168.2.99')
        self.assertTrue(reply['body']['ok']);self.assertEqual(endpoint.installed_run,h['run_id'])

    def test_board_prepare_failure_is_attempted_once_without_retry_or_owner_mutation(self):
        import joint_camera_repeat_board as board
        root=OUT/'cpu_board'/uuid.uuid4().hex/'first';root.mkdir(parents=True)
        family=dict(family_id='7'*32,created_unix=time.time(),expires_unix=time.time()+30,max_runs=100)
        write(root/'PRIVATE_CONFIG.json',dict(repeat_family=family));write(root/'RUNTIME_SHA256.json',{})
        exited=threading.Event();exited.set()
        driver=SimpleNamespace(poisoned=False,pending=None,requests=1,commits=1,
            clock_guard=SimpleNamespace(check=lambda c:dict(utc_upper_ns=int(time.time()*1e9),rate_error_bound_ppm=1000)))
        service=SimpleNamespace(lock=threading.RLock(),error=None,state='FINISHED_PENDING_AUDIT',driver=driver,
            inflight=False,neural_exited=exited,config=dict(run_id='1'*32,scope_sha256='2'*64,boot_id='CPU',control_key='31'*32))
        owner=object();bundle=object();namespace=dict(line2_fresh_initialized=owner,camera3_service_instance=service,camera3_bundle=bundle)
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:z.writestr('CPU_FIXTURE_ONLY.json','{}')
        reply=SimpleNamespace(__enter__=lambda s:s,__exit__=lambda *a:None,read=lambda n:b'{}')
        # Special methods must be on the type for context-manager lookup.
        class Response:
            def __enter__(self):return self
            def __exit__(self,*a):pass
            def read(self,n):return b'{}'
        calls=[]
        def prepare(*args):calls.append(args);raise ValueError('CPU_IN_DOUBT_NO_RETRY')
        class NoticeResponse(Response):
            def read(self,n):
                b=dict(family_id=family['family_id'],binding={k:service.config[k] for k in ('run_id','scope_sha256','boot_id')},repeat_board_sha256='CPU')
                b['ok']=True
                return json.dumps(dict(body=b,mac=mac(b,'31'*32))).encode()
        write(root/'RUNTIME_SHA256.json',{'repeat_board.py':'CPU'})
        with patch.object(board.urllib.request,'urlopen',side_effect=[NoticeResponse(),Response()]),\
            patch.object(board,'verify_bundle',return_value=(buf.getvalue(),'CAMERA3_'+'8'*32)):
            state=board.install(root,namespace,prepare);state['thread'].join(2)
        self.assertEqual(len(calls),1);self.assertTrue(state['stopped']);self.assertIn('NO_RETRY',state['error'])
        self.assertIs(namespace['camera3_service_instance'],service);self.assertFalse(driver.poisoned)

class SavedAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import joint_camera_audit as audit
        cls.audit=audit
        cls.fixture=OUT/'cpu_saved_case'/uuid.uuid4().hex
        cls.root=cls.fixture/'runtime/joint/c59286b40c9c4c2e84a3e456a0856540';cls.root.mkdir(parents=True)
        actual=HERE/'runtime/joint/c59286b40c9c4c2e84a3e456a0856540'
        for name in ('scope.json','session.json','hardware_handoff.json','PS_FINISH.json','result.json','worker_exit.json','MINIMAL_PERFORMANCE.json'):
            shutil.copy2(actual/name,cls.root/name)
        for src,dst in ((actual/'pc/evidence.fvej',cls.root/'pc/evidence.fvej'),
            (actual/'ps_retrieved_authorized/evidence.fvej',cls.root/'ps_auto/evidence.fvej')):
            dst.parent.mkdir(parents=True)
            try:os.link(src,dst)  # Never mutate either path.
            except PermissionError:shutil.copyfile(src,dst)
        shutil.copytree(HERE/'evidence/camera_joint_live5_20261018/executed_sources',cls.root/'executed_sources')
        write(cls.fixture/'CPU_FIXTURE_ONLY.json',dict(GPU=0,camera=0,board=0,semantics='read-only replay of accepted real capture; output only in isolated test root'))
    def test_existing_real100_saved_capture_auto_accepts_without_run_id_registration(self):
        with patch.object(self.audit,'HERE',self.fixture):
            out=self.audit.audit_saved(self.root);self.audit.approve(self.root);parent=self.audit.accepted_parent(self.root)
        self.assertEqual(out['steps'],100);self.assertEqual(out['PL_integer_error'],0)
        self.assertEqual(parent['completed_fresh']['completed_steps'],100)
    def test_tampered_acceptance_or_capture_is_rejected(self):
        # This test runs after the explicit acceptance above.
        with patch.object(self.audit,'HERE',self.fixture):
            if not (self.root/'AUTO_ACCEPTANCE.json').exists():
                self.audit.audit_saved(self.root);self.audit.approve(self.root)
            original=load(self.root/'AUTO_ACCEPTANCE.json');bad=copy.deepcopy(original);bad['body']['run_id']='0'*32
            write(self.root/'AUTO_ACCEPTANCE.json',bad)
            with self.assertRaises(ValueError):self.audit.accepted_parent(self.root)
            write(self.root/'AUTO_ACCEPTANCE.json',original)
            with patch.object(self.audit,'sha',return_value='0'*64),self.assertRaises(ValueError):self.audit.accepted_parent(self.root)

if __name__=='__main__':unittest.main()

"""Fixed notebook and 60s bounds. CPU/mock/saved arrays only; no sockets/devices."""
import ast,copy,hashlib,io,json,tempfile,time,unittest,uuid,zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from live_protocol import HERE,load,write,sha
import joint_camera_fixed as fixed
import joint_camera_fixed_board as board
from joint_camera_manual import mac

OUT=HERE/'evidence/fixed_camera_one_minute_20261018'

class FixedTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=OUT);self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.config=dict(installation_id='1'*32,key='31'*32,pc_url='http://192.168.2.89:18790',bit_path=fixed.BIT_PATH)
        self.inv=dict(existing_run=None,boot_id=str(uuid.uuid4()),kernel_file='kernel-'+str(uuid.uuid4())+'.json',pid=123,
            bit_path=fixed.BIT_PATH,loaded_bitfile_metadata='CPU_FIXTURE_ONLY')
    def call(self,namespace,transform=lambda b:b,answer='准备',source="CPU_FIXED_SOFTWARE_ONLY=True\n"):
        def open_url(req,**kw):
            request=json.loads(req.data)['body']
            value=dict(status='PREPARE',nonce=request['nonce'],inventory=self.inv,source=source,
                source_sha256=hashlib.sha256(source.encode()).hexdigest())
            packet=dict(body=value,mac=mac(value,self.config['key']));packet=transform(packet)
            class Response:
                def __enter__(s):return s
                def __exit__(s,*args):pass
                def read(s,n):return json.dumps(packet).encode()
            return Response()
        board.run(namespace,self.config,ask=lambda prompt:answer,inspect=lambda *a:self.inv,open_url=open_url)
    def test_new_kernel_same_cell_accepts_authenticated_source_after_confirmation(self):
        ns={};self.call(ns);self.assertTrue(ns['CPU_FIXED_SOFTWARE_ONLY']);self.assertIn('line2_fixed_attempt',ns)
    def test_cancel_does_not_request_PC_or_initialize(self):
        opened=[]
        with self.assertRaisesRegex(ValueError,'取消'):
            board.run({},self.config,ask=lambda p:'取消',inspect=lambda *a:self.inv,open_url=lambda *a:opened.append(a))
        self.assertEqual(opened,[])
    def test_wrong_signature_and_replayed_nonce_never_execute(self):
        for mutate in (lambda p:dict(p,mac='0'*64),lambda p:dict(p,body=dict(p['body'],nonce='0'*32))):
            ns={}
            with self.assertRaises(ValueError):self.call(ns,mutate)
            self.assertNotIn('CPU_FIXED_SOFTWARE_ONLY',ns)
    def test_failed_attempt_is_not_reexecuted(self):
        ns={'line2_fixed_attempt':'old'}
        with self.assertRaisesRegex(ValueError,'未完成准备'):self.call(ns)
        self.assertNotIn('CPU_FIXED_SOFTWARE_ONLY',ns)
    def test_same_prepared_kernel_is_idempotent_without_prompt(self):
        self.inv['existing_run']={'run_id':'2'*32}
        ns={'line2_fixed_attempt':'prior'}
        def prepared(packet):
            b={k:v for k,v in packet['body'].items() if k not in ('source','source_sha256')};b['status']='ALREADY_PREPARED'
            return dict(body=b,mac=mac(b,self.config['key']))
        self.call(ns,prepared,answer='MUST_NOT_BE_NEEDED');self.assertNotIn('CPU_FIXED_SOFTWARE_ONLY',ns)
    def test_notebook_is_one_fixed_cell_and_keeps_installation_pairing(self):
        with patch.object(fixed,'INSTALLATION',self.root/'private.json'),patch.object(fixed,'NOTEBOOK',self.root/'fixed.ipynb'):
            a=fixed.export_notebook();first=sha(fixed.NOTEBOOK);b=fixed.export_notebook()
            self.assertEqual(a,b);self.assertEqual(first,sha(fixed.NOTEBOOK))
            notebook=load(fixed.NOTEBOOK);cells=[c for c in notebook['cells'] if c['cell_type']=='code']
            self.assertEqual(len(cells),1);ast.parse(''.join(cells[0]['source']),feature_version=(3,8))
    def test_single_notebook_cell_reads_its_own_embedded_payload_without_extra_file(self):
        notebook=self.root/fixed.NOTEBOOK.name
        with patch.object(fixed,'INSTALLATION',self.root/'private.json'),patch.object(fixed,'NOTEBOOK',notebook):
            fixed.export_notebook();payload=load(notebook)
        source="def run(namespace,config):namespace['CPU_LOADER_VERIFIED']=config['installation_id']\n"
        payload['metadata']['flyvis_fixed_entry']['source']=source
        payload['metadata']['flyvis_fixed_entry']['source_sha256']=hashlib.sha256(source.encode()).hexdigest()
        raw=json.dumps(payload);code=''.join(payload['cells'][1]['source']);original=Path.read_text
        def read(path,*a,**kw):
            return raw if path.name==notebook.name else original(path,*a,**kw)
        ns={}
        with patch.object(Path,'read_text',read):exec(compile(code,'CPU_NOTEBOOK_LOADER','exec'),ns,ns)
        self.assertEqual(ns['CPU_LOADER_VERIFIED'],payload['metadata']['flyvis_fixed_entry']['config']['installation_id'])
    def test_original_cold_initializer_is_packaged_without_hardware(self):
        from hybrid_full485 import Full485Contract
        c=Full485Contract();self.inv.update(bit_sha256=c.wire.BIT_SHA,hwh_sha256=c.wire.HWH_SHA)
        cold=fixed.build_cold(self.root,self.inv);plan=cold['config']['plan']
        self.assertEqual((plan['max_steps'],plan['new_loads'],plan['new_resets'],plan['new_allocations']),(0,1,1,2))
        root=Path(cold['prefix']).parent
        with zipfile.ZipFile(root/'INITIALIZATION.zip') as z:
            self.assertEqual(z.read('fresh_initializer.py'),(HERE/'joint_camera_fresh.py').read_bytes())
        self.assertFalse((root/'INITIALIZATION_ATTEMPT.json').exists())
        ast.parse(Path(cold['prefix']).read_text(encoding='utf-8'),feature_version=(3,8))
    def test_unapproved_request_and_wrong_peer_never_build_initialization(self):
        endpoint=SimpleNamespace(select=lambda gate:None)
        host=fixed.FixedPreparation(self.root,{},endpoint,self.config)
        b=dict(schema='flyvis-fixed-notebook-request/v1',installation_id=self.config['installation_id'],nonce=uuid.uuid4().hex,
            inventory=self.inv,initialize_approved=False)
        p=dict(body=b,mac=mac(b,self.config['key']))
        with patch.object(fixed,'build_cold',side_effect=AssertionError('must not initialize')):
            for peer in ('127.0.0.1','192.168.2.99'):
                with self.assertRaises(ValueError):host.enter(p,peer)
        self.assertFalse(host.ready.is_set())
    def test_authenticated_PC_first_preparation_is_one_use_and_original_source_only(self):
        from hybrid_full485 import Full485Contract
        c=Full485Contract();self.inv.update(bit_sha256=c.wire.BIT_SHA,hwh_sha256=c.wire.HWH_SHA)
        selected=[];endpoint=SimpleNamespace(select=selected.append)
        host=fixed.FixedPreparation(self.root,dict(run_duration_s=60),endpoint,self.config)
        b=dict(schema='flyvis-fixed-notebook-request/v1',installation_id=self.config['installation_id'],nonce=uuid.uuid4().hex,
            inventory=self.inv,initialize_approved=True)
        packet=dict(body=b,mac=mac(b,self.config['key']))
        reply=host.enter(packet,'192.168.2.99');self.assertEqual(reply['body']['status'],'PREPARE')
        ast.parse(reply['body']['source'],feature_version=(3,8))
        self.assertIn('line2_initializer.initialize(',reply['body']['source']);self.assertEqual(len(selected),1)
        self.assertTrue(host.ready.is_set());self.assertIsNone(host.gate.root)
        with self.assertRaises(ValueError):host.enter(packet,'192.168.2.99')
    def test_saved_data_audit_failure_cannot_approve(self):
        from joint_camera_repeat import audit_finished_run
        with (patch('joint_camera_audit.retrieve'),patch('joint_camera_audit.audit_saved',side_effect=ValueError('BAD_ACK')),
            patch('joint_camera_audit.approve') as approve):
            with self.assertRaisesRegex(ValueError,'BAD_ACK'):audit_finished_run(self.root,lambda:None)
            approve.assert_not_called()
    def test_extra_kernel_is_reported_before_any_port_or_image_operation(self):
        import sys
        original=Path.read_bytes
        def data(path):
            if str(path).replace('\\','/').endswith('/cmdline'):return b'python\0ipykernel_launcher\0'
            return original(path)
        with (patch.dict(sys.modules,{'pynq':SimpleNamespace(Device=object()),
            'ipykernel.connect':SimpleNamespace(get_connection_file=lambda:'CPU_KERNEL.json')}),
            patch.object(board.os,'getpid',return_value=123),patch.object(Path,'iterdir',return_value=iter([Path('/proc/123'),Path('/proc/456')])),
            patch.object(Path,'read_bytes',data),patch.object(board.socket,'socket',side_effect=AssertionError('must not touch port'))):
            with self.assertRaisesRegex(ValueError,'456'):board.inventory({},fixed.BIT_PATH)
    def test_rerunning_fixed_cell_after_later_round_uses_current_parent(self):
        h=dict(run_id='2'*32,scope_sha256='3'*64,boot_id=self.inv['boot_id'])
        endpoint=SimpleNamespace(handoff=h)
        host=fixed.FixedPreparation(self.root,{},endpoint,self.config);host.gate=object()
        self.inv['existing_run']=h
        b=dict(schema='flyvis-fixed-notebook-request/v1',installation_id=self.config['installation_id'],nonce=uuid.uuid4().hex,
            inventory=self.inv,initialize_approved=False)
        reply=host.enter(dict(body=b,mac=mac(b,self.config['key'])),'192.168.2.99')
        self.assertEqual(reply['body']['status'],'ALREADY_PREPARED')

class WorkbenchWiringTests(unittest.TestCase):
    def test_fixed_notebook_routes_to_original_controller_and_audit_without_process_or_socket(self):
        import threading
        from contextlib import nullcontext
        import joint_camera_repeat as repeat
        with tempfile.TemporaryDirectory(dir=OUT) as tmp:
            root=Path(tmp);prepared=root/'prepared';prepared.mkdir()
            write(prepared/'scope.json',dict(run_id='2'*32))
            write(prepared/'hardware_handoff.json',dict(run_id='2'*32,boot_id='CPU'))
            ready=threading.Event();ready.set()
            authority=SimpleNamespace(prepared=ready,scope={},close=lambda:None)
            gate=SimpleNamespace(root=prepared,ready=ready,error=None,authority=authority)
            class First:
                def init__(self,parent,family,endpoint,installation):
                    self.ready=ready;self.gate=gate;endpoint.installed_run='2'*32
            class Server:
                def init__(self,*a):pass
                def serve_forever(self):pass
                def shutdown(self):pass
                def server_close(self):pass
            original_phase=repeat.phase
            def phase(workspace,name,**fields):
                original_phase(workspace,name,**fields)
                if name=='READY_TO_START':original_phase(workspace,'START_REQUESTED')
                if name in ('COMPLETE','FAILED'):
                    write(workspace/'QUIT.json',dict(instance_id=load(workspace/'state.json')['instance_id']))
            output=root/'actual_CPU_FIXTURE_ONLY';output.mkdir()
            write(output/'result.json',dict(status='STOPPED_PENDING_PS_AUDIT'))
            calls=[]
            def execute(*args,**kw):calls.append((args,kw));return output
            with (patch.object(repeat,'HERE',root),patch.object(repeat,'ACTIVE',root/'active.json'),
                patch.object(repeat,'phase',phase),patch.object(repeat,'stop_previous_display'),
                patch('launch_recovery.launch_guard',return_value=nullcontext()),patch('launch_recovery.gui_port_available'),
                patch('joint_camera_fixed.export_notebook',return_value={}),patch('joint_camera_fixed.FixedPreparation',First),
                patch.object(repeat,'LocalAddressHTTPServer',Server),patch.object(repeat,'verify_prepared_handoff'),
                patch.object(repeat.subprocess,'Popen',return_value=SimpleNamespace(pid=123,wait=lambda t:0)) as process,
                patch.object(repeat.webbrowser,'open') as browser,patch.object(repeat,'audit_finished_run') as audit):
                repeat.run_workbench(execute,fixed_notebook=True,run_duration_s=60)
            self.assertEqual(len(calls),1);self.assertEqual(process.call_count,1) # Fake original GUI only.
            self.assertIn('--joint-workspace',process.call_args.args[0]);audit.assert_called_once()
            state=load(root/'active.json');self.assertEqual(state['state'],'STOPPED')
            self.assertEqual(state['completed_runs'],1);self.assertEqual(state['family']['run_duration_s'],60)

class WindowsBoardProtocolTests(unittest.TestCase):
    def test_existing_board_protocol_uses_CPU_registers_only_on_Windows(self):
        from test_joint_minimal import BoardTests
        original=Path.read_text
        def read(path,*a,**kw):
            if str(path).replace('\\','/')=='/proc/sys/kernel/random/boot_id':return 'CPU_FIXTURE_BOOT_ONLY'
            return original(path,*a,**kw)
        BoardTests.setUpClass()
        for name in ('test_initial_state_config_epoch_are_checked_in_RAM_before_DMA','test_original_DMA_RUN_RELEASE_ACK_32_steps_without_hot_fsync'):
            case=BoardTests(name)
            with patch.object(Path,'read_text',read):
                try:getattr(case,name)()
                finally:case.doCleanups()

class DurationTests(unittest.TestCase):
    def test_streaming_queue_full_stops_after_commit_without_retry(self):
        from test_joint_minimal import WorkerAdapterTests
        class Full:
            errors=dropped=0
            def init__(self,*a,**kw):pass
            def submit(self,record):self.dropped+=1;return False
            def close(self,**kw):return dict(closed=True,complete=False)
        helper=WorkerAdapterTests('test_live5_decodes_each_committed_full_state_without_device')
        self.addCleanup(helper.doCleanups)
        with patch('joint_minimal_worker.AsyncRecords',Full):
            with self.assertRaisesRegex(ValueError,'LONG_RUN_EVIDENCE_QUEUE_FULL'):
                helper.saved_adapter(live5=True,step_wall_s=.5,run_duration_s=1)
    def test_streaming_user_stop_keeps_last_same_run_state(self):
        from test_joint_minimal import WorkerAdapterTests
        helper=WorkerAdapterTests('test_live5_decodes_each_committed_full_state_without_device')
        self.addCleanup(helper.doCleanups)
        helper.saved_adapter(live5=True,stop_after=1,run_duration_s=60)
    def test_disk_reserve_failure_cannot_be_reported_as_complete(self):
        from test_joint_minimal import WorkerAdapterTests
        helper=WorkerAdapterTests('test_live5_decodes_each_committed_full_state_without_device')
        self.addCleanup(helper.doCleanups)
        with patch('joint_minimal_worker.shutil.disk_usage',return_value=SimpleNamespace(free=0)):
            with self.assertRaisesRegex(ValueError,'LONG_RUN_'):
                helper.saved_adapter(live5=True,step_wall_s=.5,run_duration_s=1)
    def test_build_timed_scope_and_reject_changed_duration_without_devices(self):
        from joint_camera_bundle import audited_compute_parent,build
        from joint_camera_protocol import validate_scope
        from joint_camera_clock_wait import scoped_clock
        from joint_camera_control import hardware_module
        root=HERE/'runtime/joint/c59286b40c9c4c2e84a3e456a0856540'
        prior=audited_compute_parent(dict(state='STOPPED',run_id='ad5b4adac2b941f59b4a5271d1bde1fe',session_id=root.name,
            root=str(root),exit_codes=dict(gui=0,joint_worker=0)),root)
        family=dict(family_id=uuid.uuid4().hex,max_runs=100,created_unix=time.time(),expires_unix=time.time()+300,run_duration_s=60)
        with tempfile.TemporaryDirectory(dir=OUT) as tmp:
            new,_=build(Path(tmp),**prior,minimal_compute=True,live5=True,cpu_fixture=True,repeat_family=family)
            scope=load(new/'scope.json');config=load(new/'PRIVATE_CONFIG.json')
            self.assertEqual((scope['run_duration_s'],scope['capture_duration_s'],scope['max_steps']),(60,70,12000))
            s=dict(scope,status='APPROVED_BY_HUMAN',human_authorization_reference='CPU_ONLY');validate_scope(s)
            original=hardware_module(load(root/'hardware_handoff.json'),'clock');scoped_clock(original,config,scope)
            for change in ({'run_duration_s':61},{'run_duration_s':True},{'max_steps':60000},{'capture_duration_s':60}):
                with self.assertRaises(ValueError):validate_scope(dict(s,**change))
    def test_streaming_engine_retains_only_metadata_and_same_actual_saved_states(self):
        from test_joint_minimal import EngineTests,item
        import numpy as np
        EngineTests.setUpClass();helper=EngineTests('test_three_saved_steps_feedback_equal_with_all_file_io_forbidden')
        self.addCleanup(helper.doCleanups)
        c,hw,engine,arrays,inputs=helper.make();engine.streaming_records=True
        for k in range(3):
            record=engine.step(item(arrays['input_721_%d.npy'%k],k,kind='real_windows_camera'))
            np.testing.assert_array_equal(record['full'],arrays['committed_full_%d.npy'%k])
        self.assertEqual(len(engine.samples),3);self.assertEqual(inputs,[])
        self.assertTrue(all('full' not in row and 'item' not in row and 'output' not in row for row in engine.samples))

if __name__=='__main__':unittest.main()

"""Repeat lifecycle for the existing controller, GUI bridge and board preparer.

This module never computes a neuron or owns COMMIT authority. Each user Start
creates one fresh bounded run. Only automatic saved-data acceptance may enable
the next Start; failures preserve evidence and latch the family closed.
"""
import base64,json,os,secrets,subprocess,sys,threading,time,uuid,webbrowser
from pathlib import Path
from http.server import BaseHTTPRequestHandler
from live_protocol import HERE,load,write,require,sha,host_path
from joint_camera_manual import ManualGate,mac
from joint_camera_preparation import LocalAddressHTTPServer,verify_prepared_handoff

ACTIVE=HERE/'runtime/joint_workbench_active.json'

def phase(workspace,name,**fields):
    value=load(workspace/'state.json');value.update(phase=name,**fields);write(workspace/'state.json',value)

class WorkspaceUI:
    """The original HTTP handler delegates to one current original bridge."""
    def init__(self,path):
        self.root=host_path(path).resolve()
        require(self.root.parent==(HERE/'runtime/joint_workbench').resolve(),'REPEAT_GUI_ROOT')
        self.bridge=None;self.path=None;self.lock=threading.RLock();self.last_touch=0
    def touch(self):
        with self.lock:
            if time.monotonic()-self.last_touch>1:
                s=load(self.root/'state.json')
                write(self.root/'browser.json',dict(instance_id=s['instance_id'],unix_time=time.time()))
                self.last_touch=time.monotonic()
    def current(self):
        self.touch();s=load(self.root/'state.json');path=s.get('current_session')
        with self.lock:
            if path and path!=self.path:
                target=host_path(path)
                require(target.parent.parent==(HERE/'runtime/joint').resolve() and target.name=='session.json','REPEAT_SESSION_PATH')
                if self.bridge:self.bridge.close()
                from joint_camera_bridge import JointCameraBridge
                self.bridge=JointCameraBridge(path);self.path=path
            return s,self.bridge
    def status(self):
        s,b=self.current();v=b.status() if b else dict(ready_for_camera=False,result_valid=False,FPGA_status='NOT_CONNECTED')
        return dict(v,repeat_enabled=True,family_id=s['family']['family_id'],workbench_phase=s['phase'],
            can_start=s['phase'] in ('READY_TO_START','COMPLETE'),automatic_audit=s.get('audit_status'),
            workbench_error=s.get('error'),completed_runs=s.get('completed_runs',0))
    def rearm(self,body):
        with self.lock:
            s=load(self.root/'state.json')
            require(body==dict(family_id=s['family']['family_id']) and s['phase'] in ('READY_TO_START','COMPLETE'),'REPEAT_START_ALREADY_CONSUMED')
            require(time.time()<s['family']['expires_unix'] and s['completed_runs']<s['family']['max_runs'],'REPEAT_FAMILY_EXPIRED')
            nonce=uuid.uuid4().hex
            write(self.root/'START_REQUEST.json',dict(nonce=nonce,instance_id=s['instance_id'],family_id=body['family_id']))
            phase(self.root,'START_REQUESTED',requested_nonce=nonce)
            return dict(status='START_REQUESTED',nonce=nonce)
    def latest(self):
        s,b=self.current();v=b.latest() if b else dict(packet=None)
        return dict(v,status=self.status())
    def preview(self):
        s,b=self.current()
        return b.preview() if b else dict(run_id=None,session_id=None,live_preview=False,packet=None)
    def clock(self):
        return dict(clock='Windows_perf_counter_ns',server_monotonic_ns=time.perf_counter_ns(),valid_for_s=5)
    def prepare(self):
        _,b=self.current();require(b is not None,'REPEAT_WORKER_NOT_READY');return b.prepare()
    def cache(self):
        _,b=self.current();require(b is not None,'REPEAT_WORKER_NOT_READY');return b.cache()
    def start(self,body):
        s,b=self.current();require(s['phase']=='GPU_PREPARING' and b is not None,'REPEAT_START_PHASE')
        value=b.start(body);phase(self.root,'RUNNING');return value
    def stop(self,body=None):
        _,b=self.current();return b.stop(body) if b else dict(status='NOT_RUNNING')
    def record_draw(self,body):
        _,b=self.current();require(b is not None,'REPEAT_NO_DRAW_RUN');return b.record_draw(body)
    def recording(self,raw):
        _,b=self.current();require(b is not None,'REPEAT_NO_RECORDING_RUN');return b.recording(raw)
    def quit(self):
        s,_=self.current();write(self.root/'QUIT.json',dict(instance_id=s['instance_id']))
        return dict(status='CLOSING_WAIT_GPU_ACK_AND_AUDIT')
    def close(self):
        self.quit()
        if self.bridge:self.bridge.close()

class RepeatEndpoint:
    def init__(self,gate,prior_handoff,family):
        self.gate=gate;self.handoff=prior_handoff;self.family=family;self.cached=None;self.lock=threading.RLock();self.installed_run=None
    def ready(self,packet,peer):
        with self.lock:
            require(peer=='192.168.2.99' and self.gate and self.gate.root,'REPEAT_INSTALL_PEER_OR_SCOPE')
            h=load(self.gate.root/'hardware_handoff.json');key=h['control_config']['control_key']
            expected=dict(family_id=self.family['family_id'],binding=dict(run_id=h['run_id'],scope_sha256=sha(self.gate.root/'scope.json'),boot_id=h['boot_id']),
                repeat_board_sha256=sha(HERE/'joint_camera_repeat_board.py'))
            require(set(packet)=={'body','mac'} and secrets.compare_digest(mac(packet['body'],key),packet['mac']) and packet['body']==expected,'REPEAT_INSTALL_IDENTITY')
            self.installed_run=h['run_id'];body=dict(expected,ok=True)
            return dict(body=body,mac=mac(body,key))
    def select(self,gate):
        with self.lock:self.gate=gate;self.cached=None
    def parent(self,handoff):
        with self.lock:self.handoff=handoff;self.gate=None;self.cached=None
    def next(self,packet,peer):
        with self.lock:
            require(peer=='192.168.2.99','REPEAT_PEER')
            h=self.handoff;key=h['control_config']['control_key']
            require(set(packet)=={'body','mac'} and secrets.compare_digest(mac(packet['body'],key),packet['mac']),'REPEAT_AUTH')
            b=packet['body'];binding={k:h[k] for k in ('run_id','scope_sha256','boot_id')}
            require(b['binding']==binding and b['family_id']==self.family['family_id'] and len(b['nonce'])==32,'REPEAT_BINDING')
            require(time.time()<self.family['expires_unix'],'REPEAT_EXPIRED')
            reply=dict(status='WAIT',binding=binding,family_id=self.family['family_id'])
            if self.gate is not None:
                if self.cached is None:
                    p=dict(body=self.gate.expected,mac=mac(self.gate.expected,self.gate.token))
                    self.cached=self.gate.bundle(p,peer)['body']
                reply.update(self.cached,status='PREPARE')
            return dict(body=reply,mac=mac(reply,key))

def stop_previous_display():
    from launch_recovery import process_alive
    marker=HERE/'runtime/joint_active.json'
    if not marker.exists() or load(marker)['state']=='STOPPED':return
    old=load(marker);root=host_path(old['root'])
    require(root.parent==(HERE/'runtime/joint').resolve() and root.name==old['session_id'],'REPEAT_PREVIOUS_OWNER')
    e=load(root/'worker_exit.json');r=load(root/'result.json');c=load(root/'controller.json')
    require(c['pid']==old['pid'] and c['session_id']==old['session_id'] and process_alive(old['pid'])
        and e['GPU_inflight_waited'] and e['lease_closed'] and not e['cleanup_errors']
        and r['status']=='STOPPED_PENDING_PS_AUDIT','PREVIOUS_DEVICE_STOP_UNKNOWN')
    write(root/'STOP_REQUEST.json',dict(reason='USER_OPEN_REPEAT_WORKBENCH',session_id=old['session_id']))
    until=time.monotonic()+15
    while time.monotonic()<until:
        if load(marker)['state']=='STOPPED':return
        time.sleep(.1)
    raise TimeoutError('PREVIOUS_GUI_STOP_UNCONFIRMED')

def run_workbench(execute):
    from launch_recovery import launch_guard,process_alive,gui_port_available
    from joint_camera_bundle import preparation_parent
    from joint_camera_audit import retrieve,audit_saved,approve,accepted_parent
    # Opening the owned UI cannot wait on a running round's launch mutex.
    if ACTIVE.exists():
        old=load(ACTIVE)
        if old['state']=='RUNNING' and process_alive(old['pid']):
            require(time.time()-load(host_path(old['instance_dir'])/'controller.json')['unix_time']<15,'WORKBENCH_OWNER_STALE')
            webbrowser.open('http://127.0.0.1:8771/#competition');return
    # The legacy controller holds the same mutex for its whole lifetime.
    # Confirm its already-released GPU, request only its GUI close, then acquire.
    stop_previous_display()
    with launch_guard():
        gui_port_available()
        selection=preparation_parent()
        previous=load(ACTIVE) if ACTIVE.exists() else None
        resume=bool(previous and previous['state']=='STOPPED' and previous.get('last_accepted_root')
            and time.time()<previous['family']['expires_unix'])
        family_now=time.time()
        family=previous['family'] if resume else dict(family_id=uuid.uuid4().hex,created_unix=family_now,expires_unix=family_now+28800,max_runs=100)
        workspace=HERE/'runtime/joint_workbench'/family['family_id'];workspace.mkdir(parents=True,exist_ok=True)
        instance=uuid.uuid4().hex;owned=workspace/'instances'/instance;owned.mkdir(parents=True)
        count=previous.get('completed_runs',0) if resume else 0
        s=dict(family=family,instance_id=instance,phase='WAIT_BOARD_PREPARATION',completed_runs=count,current_session=None,error=None)
        write(workspace/'state.json',s)
        active=dict(state='RUNNING',pid=os.getpid(),family=family,workspace=str(workspace),instance_dir=str(owned),completed_runs=count)
        if resume:active['last_accepted_root']=previous['last_accepted_root']
        write(ACTIVE,active)
    def beat():write(owned/'controller.json',dict(pid=os.getpid(),unix_time=time.time()))
    started=time.monotonic()
    def closing():
        q=workspace/'QUIT.json'
        if q.exists() and load(q).get('instance_id')==instance:return True
        browser=workspace/'browser.json'
        seen=browser.exists() and load(browser).get('instance_id')==instance
        age=time.time()-load(browser)['unix_time'] if seen else time.monotonic()-started
        return age>(45 if seen else 1200) or time.time()>=family['expires_unix']
    def wait_for(predicate,limit=None):
        until=time.monotonic()+limit if limit else float('inf')
        while not predicate():
            beat();require(not closing(),'WORKBENCH_CLOSING');require(time.monotonic()<until,'WORKBENCH_PREPARATION_TIMEOUT');time.sleep(.1)
        require(not closing(),'WORKBENCH_CLOSING')
    from joint_camera_controller import ACTIVE as ROUND_ACTIVE
    parent_root=host_path(load(ROUND_ACTIVE)['root'])
    prior=dict(load(parent_root/'hardware_handoff.json'),scope_sha256=sha(parent_root/'scope.json'))
    stage=owned/'prepare';stage.mkdir()
    gate=None if resume else ManualGate(stage,**selection,minimal_compute=True,live5=True,repeat_family=family)
    endpoint=RepeatEndpoint(gate,prior,family)
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                require(self.path=='/operator-entry' and gate is not None,'ONE_MANUAL_PREPARATION_ONLY')
                v=gate.operator_packet(self.client_address[0]);code=200
            except Exception as e:v=dict(error=str(e));code=409
            self.reply(v,code)
        def do_POST(self):
            try:
                n=int(self.headers.get('Content-Length','0'));require(0<n<4096,'REPEAT_REQUEST_SIZE')
                value=json.loads(self.rfile.read(n))
                if self.path=='/bundle':
                    require(gate is not None,'NO_MANUAL_GATE');v=gate.bundle(value,self.client_address[0])
                elif self.path=='/repeat-next':v=endpoint.next(value,self.client_address[0])
                elif self.path=='/repeat-ready':v=endpoint.ready(value,self.client_address[0])
                else:raise ValueError('REPEAT_ENDPOINT')
                code=200
            except Exception as e:v=dict(error=str(e));code=409
            self.reply(v,code)
        def reply(self,value,code):
            raw=json.dumps(value).encode();self.send_response(code);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        def log_message(self,*args):pass
    server=None;gui=None;log=None;failed=None
    try:
        # Old owned manual listener may be finishing its normal shutdown.
        until=time.monotonic()+4
        while server is None:
            try:server=LocalAddressHTTPServer(('192.168.2.89',18790),Handler)
            except OSError:
                require(time.monotonic()<until,'PREPARATION_PORT_BUSY');time.sleep(.1)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        beat();log=(owned/'gui.log').open('ab')
        gui=subprocess.Popen([sys.executable,'-B',str(HERE/'server.py'),'--no-open','--port','8771',
            '--joint-workspace',str(workspace),'--stop-file',str(owned/'GUI_STOP.json'),'--controller-file',str(owned/'controller.json')],
            cwd=str(HERE),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        active['gui_pid']=gui.pid;write(ACTIVE,active)
        webbrowser.open('http://127.0.0.1:8771/#competition')
        print('WORKBENCH_OPEN · '+str(HERE/'board_prepare_camera.py')+' · one preparation for this board family',flush=True)
        if gate:
            wait_for(lambda:gate.ready.is_set(),1200);require(gate.error is None,'MANUAL_PREPARATION_FAILED '+str(gate.error))
            wait_for(lambda:gate.authority.prepared.is_set(),120)
            verify_prepared_handoff(load(gate.root/'hardware_handoff.json'),gate.authority.scope,gate.root)
            wait_for(lambda:endpoint.installed_run==load(gate.root/'scope.json')['run_id'],30)
            endpoint.parent(dict(load(gate.root/'hardware_handoff.json'),scope_sha256=sha(gate.root/'scope.json')))
            phase(workspace,'READY_TO_START')
        else:phase(workspace,'COMPLETE',audit_status='PREVIOUS_RUN_ACCEPTED')
        while count<family['max_runs']:
            wait_for(lambda:load(workspace/'state.json')['phase']=='START_REQUESTED')
            if gate is None:
                selection=accepted_parent(host_path(active['last_accepted_root']))
                target=owned/('prepare_'+str(count));target.mkdir()
                gate=ManualGate(target,**selection,minimal_compute=True,live5=True,repeat_family=family)
                endpoint.select(gate);phase(workspace,'BOARD_PREPARING')
                wait_for(lambda:gate.ready.is_set(),120);require(gate.error is None,'AUTOMATIC_PREPARATION_FAILED '+str(gate.error))
                wait_for(lambda:gate.authority.prepared.is_set(),120)
                verify_prepared_handoff(load(gate.root/'hardware_handoff.json'),gate.authority.scope,gate.root)
                endpoint.parent(dict(load(gate.root/'hardware_handoff.json'),scope_sha256=sha(gate.root/'scope.json')))
            phase(workspace,'GPU_PREPARING')
            root=execute(gate.root/'scope.json',gate.root/'hardware_handoff.json',pc_clock=gate.authority,workspace=workspace,stop_requested=closing)
            require(load(root/'result.json')['status']=='STOPPED_PENDING_PS_AUDIT','RUN_FAILED_OR_IN_DOUBT')
            phase(workspace,'AUDITING',audit_status='CHECKING_SAVED_DATA')
            retrieve(root);audit_saved(root);approve(root)
            count+=1;active.update(last_accepted_root=str(root),completed_runs=count);write(ACTIVE,active)
            gate.authority.close();gate=None
            phase(workspace,'COMPLETE',audit_status='PASS_MINIMAL_SAVED_DATA_CONTRACT',completed_runs=count)
            if closing():break
    except BaseException as error:
        if str(error)!='WORKBENCH_CLOSING':failed=str(error);phase(workspace,'FAILED',error=failed)
        if failed:
            print('WORKBENCH_FAILED '+failed,flush=True)
            # Keep the reason visible until the user closes the page.
            while not closing():beat();time.sleep(.2)
    finally:
        if gate and gate.authority:gate.authority.close()
        write(owned/'GUI_STOP.json',dict(reason='WORKBENCH_CLOSE'))
        if gui:
            try:gui.wait(10)
            except subprocess.TimeoutExpired:failed=failed or 'GUI_STOP_UNCONFIRMED'
        if server:server.shutdown();server.server_close()
        if log:log.close()
        active.update(state='FAILED' if failed else 'STOPPED',error=failed,completed_runs=count);write(ACTIVE,active)

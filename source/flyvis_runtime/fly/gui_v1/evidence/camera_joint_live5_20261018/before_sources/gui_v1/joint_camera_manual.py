"""Operator downloads one private bundle; same Line 2 controller does the rest.

Waiting for a human does NOT consume the 300s device scope or PC clock proof.
No device is touched by this staging endpoint. Only the fixed board IP and a
one-use HMAC request may receive the private source/config package.
"""
import base64,hashlib,hmac,json,secrets,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from live_protocol import HERE,load,require,write,sha
from joint_camera_preparation import PreparationAuthority,verify_prepared_handoff,LocalAddressHTTPServer
from joint_camera_retained import NEXT_EXPIRED_RUN

def mac(body,key):
    return hmac.new(bytes.fromhex(key),json.dumps(body,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()

class ManualGate:
    def init__(self,parent,completed=None,unused=None,fresh=None,unused_fresh=None,completed_fresh=None,minimal_compute=False,cold_init=None):
        self.parent=parent;self.token=secrets.token_hex(32);self.ready=threading.Event();self.lock=threading.Lock()
        self.consumed=False;self.authority=None;self.root=None;self.error=None
        require(not (completed and unused),'MANUAL_AMBIGUOUS_PARENT')
        self.completed,self.unused=completed,unused
        self.fresh,self.unused_fresh=fresh,unused_fresh
        self.completed_fresh,self.minimal_compute=completed_fresh,minimal_compute
        self.cold_init=cold_init
        require(not cold_init or (minimal_compute and not any((completed,unused,fresh,unused_fresh,completed_fresh))),'COLD_INIT_EXCLUSIVE_MINIMAL')
        self.expected=(dict(operation='MANUAL_PREPARE_CAMERA_UNUSED',unused_run_id=unused['run_id'],unused_scope_sha256=unused['scope_sha256']) if unused
            else dict(operation='MANUAL_PREPARE_CAMERA_COMPLETED',completed_run_id=completed['run_id']) if completed
            else dict(operation='MANUAL_PREPARE_CAMERA3',expired_run_id=NEXT_EXPIRED_RUN))
        if fresh:
            require(bool(unused_fresh)!=bool(completed_fresh) and not completed and not unused,'MANUAL_FRESH_PARENT_REQUIRED')
            prior=unused_fresh or completed_fresh
            self.expected=dict(operation='MANUAL_PREPARE_FRESH_COMPLETED' if completed_fresh else 'MANUAL_PREPARE_FRESH_UNUSED',unused_run_id=prior['run_id'],unused_scope_sha256=prior['scope_sha256'])
    def operator_packet(self,peer):
        """Fixed human-run entry, authenticated by the existing parent key.

        A GET never builds a scope or touches the board. The returned original
        cell still uses the one-use POST bundle gate and all source checks.
        """
        if self.cold_init:
            require(peer=='192.168.2.99' and not self.consumed,'COLD_OPERATOR_PEER_OR_CONSUMED')
            text=cold_board_cell(self.token,self.cold_init)
            body=dict(schema='flyvis-signed-cold-prepare-entry/v1',initialization_run_id=self.cold_init['config']['run_id'],
                source=text,source_sha256=hashlib.sha256(text.encode()).hexdigest())
            return dict(body=body,mac=mac(body,self.token))
        prior=self.unused_fresh or self.completed_fresh
        require(peer=='192.168.2.99' and self.fresh and prior,'MANUAL_OPERATOR_PEER_OR_PARENT')
        require(not self.consumed,'MANUAL_BUNDLE_ALREADY_CONSUMED')
        active=load(HERE/'runtime/joint_active.json')
        require(active['state']=='STOPPED' and active['run_id']==prior['run_id'],'MANUAL_OPERATOR_PARENT_CHANGED')
        source=HERE/'runtime/joint'/active['session_id']
        handoff=load(source/'hardware_handoff.json')
        require(handoff['run_id']==prior['run_id']
            and handoff['control_config']['run_id']==handoff['run_id'],'MANUAL_OPERATOR_KEY_IDENTITY')
        text=board_cell(self.token,fresh=self.fresh,unused_fresh=self.unused_fresh,completed_fresh=self.completed_fresh)
        body=dict(schema='flyvis-signed-human-prepare-entry/v1',prior_run_id=prior['run_id'],
            prior_scope_sha256=prior['scope_sha256'],source=text,
            source_sha256=hashlib.sha256(text.encode()).hexdigest())
        return dict(body=body,mac=mac(body,handoff['control_config']['control_key']))
    def bundle(self,packet,peer):
        with self.lock:
            require(peer=='192.168.2.99','MANUAL_BUNDLE_WRONG_PEER')
            require(set(packet)=={'body','mac'} and hmac.compare_digest(mac(packet['body'],self.token),packet['mac']),'MANUAL_BUNDLE_AUTH')
            if self.cold_init:
                require(set(packet['body'])=={'operation','initialization_receipt'} and packet['body']['operation']=='MANUAL_COLD_INIT_READY','COLD_RECEIPT_OPERATION')
                self.fresh=verify_cold_receipt(self.cold_init,packet['body']['initialization_receipt'])
                write(self.parent/'ACTUAL_INITIALIZATION_RECEIPT.json',self.fresh)
            else:require(packet['body']==self.expected,'MANUAL_BUNDLE_BINDING')
            require(not self.consumed,'MANUAL_BUNDLE_ALREADY_CONSUMED');self.consumed=True
            try:
                started=time.perf_counter()
                from joint_camera_bundle import build
                if self.fresh:self.root,archive=build(self.parent,fresh=self.fresh,unused_fresh=self.unused_fresh,completed_fresh=self.completed_fresh,minimal_compute=self.minimal_compute)
                elif self.unused:self.root,archive=build(self.parent,unused=self.unused)
                else:self.root,archive=build(self.parent,completed=self.completed) if self.completed else build(self.parent)
                print('MANUAL_BUNDLE_FROZEN build_s=%.6f'%(time.perf_counter()-started),flush=True)
                self.authority=PreparationAuthority(self.root);self.authority.start()
                print('MANUAL_CLOCK_LISTENER_READY total_s=%.6f'%(time.perf_counter()-started),flush=True)
                body=dict(root_name='CAMERA3_'+load(self.root/'scope.json')['run_id'],archive_sha256=sha(archive),archive_b64=base64.b64encode(archive.read_bytes()).decode())
                return dict(body=body,mac=mac(body,self.token))
            except BaseException as error:
                self.error=str(error);raise
            finally:self.ready.set()

def board_cell(token,completed=None,unused=None,fresh=None,unused_fresh=None,completed_fresh=None):
    code='''# USER MANUAL BOARD STEP: same kernel; no bit download/reset/allocation.
import urllib.request, json, hashlib, hmac, base64, zipfile, io, importlib.util, sys
from pathlib import Path
camera_expired_owner=globals().get("camera3_service_instance")
camera_expired_bundle=globals().get("camera3_bundle")
camera_original_owner=globals().get("latency485_service_instance")
assert camera_original_owner is not None, "Original board owner is missing in this kernel; stop and report, do not run old cells"
assert camera_expired_owner is not None and camera_expired_bundle is not None, "Previous prepared owner is missing; stop"
assert camera_expired_owner.config["run_id"]=="393ffe7d6860457ebf9ad4b11fbec943" and camera_expired_bundle.driver is camera_expired_owner.driver, "Wrong previous owner; stop"
camera_token = %r
camera_body = {"operation":"MANUAL_PREPARE_CAMERA3","expired_run_id":"393ffe7d6860457ebf9ad4b11fbec943"}
camera_mac = lambda v: hmac.new(bytes.fromhex(camera_token), json.dumps(v,sort_keys=True,separators=(",",":")).encode(), hashlib.sha256).hexdigest()
camera_request = urllib.request.Request("http://192.168.2.89:18790/bundle", data=json.dumps({"body":camera_body,"mac":camera_mac(camera_body)}).encode(), headers={"Content-Type":"application/json"})
with urllib.request.urlopen(camera_request, timeout=15) as camera_reply:
    camera_packet=json.loads(camera_reply.read(2_000_001))
assert hmac.compare_digest(camera_mac(camera_packet["body"]),camera_packet["mac"]), "Bundle signature mismatch"
camera_payload=camera_packet["body"]
camera_zip=base64.b64decode(camera_payload["archive_b64"],validate=True)
assert hashlib.sha256(camera_zip).hexdigest()==camera_payload["archive_sha256"], "Bundle SHA mismatch"
camera_new_root=Path(camera_payload["root_name"]).resolve()
assert camera_new_root.parent==Path.cwd().resolve() and not camera_new_root.exists(), "Invalid/new run directory conflict"
with zipfile.ZipFile(io.BytesIO(camera_zip)) as camera_archive:
    assert all(not Path(n).is_absolute() and ".." not in Path(n).parts for n in camera_archive.namelist())
    camera_new_root.mkdir();camera_archive.extractall(camera_new_root)
camera_spec=importlib.util.spec_from_file_location("line2_manual_"+camera_new_root.name,camera_new_root/"prepare_camera.py")
camera_entry=importlib.util.module_from_spec(camera_spec);camera_spec.loader.exec_module(camera_entry)
camera3_bundle,camera3_service_instance=camera_entry.run(camera_new_root,camera_original_owner,camera_expired_owner,camera_expired_bundle)
''' % token
    if fresh:
        require(bool(unused_fresh)!=bool(completed_fresh) and not completed and not unused,'MANUAL_FRESH_PARENT_REQUIRED')
        prior=unused_fresh or completed_fresh
        start=code.index('camera_token = ')
        code=('# LINE2 启动32步：复用当前固件和缓冲区；不加载、不复位、不分配；准备后点GUI启动\n'
            '# 新等待策略：准备约30分钟；实际计算限32步/300秒，不再在等待按钮时消耗计算时间。\n'
            'import urllib.request,json,hashlib,hmac,base64,zipfile,io,importlib.util,sys\nfrom pathlib import Path\n'
            'assert "line2_fresh_initialized" in globals() and "camera3_service_instance" in globals() and "camera3_bundle" in globals(), "Current board objects missing; stop"\n'
            'camera_original_owner=line2_fresh_initialized\ncamera_expired_owner=camera3_service_instance\ncamera_expired_bundle=camera3_bundle\n'
            'assert camera_original_owner.receipt=='+repr(fresh)+', "Initialization changed; stop"\n'
            'assert camera_expired_owner.config["run_id"]=='+repr(prior['run_id'])+' and camera_expired_owner.config["scope_sha256"]=='+repr(prior['scope_sha256'])+', "Prior board identity changed; stop"\n'
            +code[start:])
        code=code.replace('{"operation":"MANUAL_PREPARE_CAMERA3","expired_run_id":"393ffe7d6860457ebf9ad4b11fbec943"}',
            json.dumps(dict(operation='MANUAL_PREPARE_FRESH_COMPLETED' if completed_fresh else 'MANUAL_PREPARE_FRESH_UNUSED',unused_run_id=prior['run_id'],unused_scope_sha256=prior['scope_sha256']),separators=(',',':')))
        return code
    if completed:
        code=code.replace('393ffe7d6860457ebf9ad4b11fbec943',completed['run_id'])
        code=code.replace('{"operation":"MANUAL_PREPARE_CAMERA3","expired_run_id":"'+completed['run_id']+'"}',
            '{"operation":"MANUAL_PREPARE_CAMERA_COMPLETED","completed_run_id":"'+completed['run_id']+'"}')
        code='# LINE2 CAMERA32 — 本轮32步；正常完成态接手；仅手动运行一次\n'+code
    if unused:
        require(completed is None,'MANUAL_AMBIGUOUS_PARENT')
        code=code.replace('393ffe7d6860457ebf9ad4b11fbec943',unused['run_id'])
        code=code.replace('{"operation":"MANUAL_PREPARE_CAMERA3","expired_run_id":"'+unused['run_id']+'"}',
            json.dumps(dict(operation='MANUAL_PREPARE_CAMERA_UNUSED',unused_run_id=unused['run_id'],unused_scope_sha256=unused['scope_sha256']),separators=(',',':')))
        marker='camera_token = '
        check='assert camera_expired_owner.config["scope_sha256"]=='+repr(unused['scope_sha256'])+', "Wrong expired scope; stop"\n'
        code=code.replace(marker,check+marker)
        code='# LINE2 CAMERA32 — 新身份接手未启动的失败会话；本次只运行这一格一次\n'+code
    return code

def load_cold_init(path):
    value=load(path);root=Path(value['root']);config=load(root/'INIT_CONFIG.json')
    require(value['status']=='AWAITING_USER_MANUAL_INITIALIZATION_NOT_EXECUTED'
        and sha(value['archive'])==value['archive_sha256'] and sha(root/'INIT_PLAN.json')==config['plan_sha256'],'COLD_INIT_PACKAGE_CHANGED')
    require(config['execution_authority']=='HUMAN_MANUAL_CELL_ONLY' and config.get('test_fixture') is False
        and config['plan']['new_loads']==config['plan']['new_resets']==1 and config['plan']['new_allocations']==2
        and config['plan']['max_steps']==0,'COLD_INIT_AUTHORITY')
    from hybrid_full485 import Full485Contract
    wire=Full485Contract().wire
    require((config['bit_sha256'],config['hwh_sha256'])==(wire.BIT_SHA,wire.HWH_SHA),'COLD_WRONG_IMAGE')
    return dict(value,config=config)


def verify_cold_receipt(cold,receipt):
    c=cold['config']
    expected=dict(mode='MANUAL_FRESH_INIT_THEN_READ20/v1',initialization_run_id=c['run_id'],boot_id=c['boot_id'],kernel_file=c['kernel_file'],
        initialization_plan_sha256=c['plan_sha256'],bit_sha256=c['bit_sha256'],hwh_sha256=c['hwh_sha256'],
        src_bytes=69216,dst_bytes=23072,new_loads=1,new_resets=1,new_allocations=2,requests=0,commits=0,neural_listeners_started=0)
    require(set(receipt)==set(expected)|{'src_address','dst_address','initialization_capture_sha256'}
        and all(receipt.get(k)==v for k,v in expected.items()),'COLD_INIT_RECEIPT_IDENTITY')
    src,dst=receipt['src_address'],receipt['dst_address']
    require(type(src) is int and type(dst) is int and min(src,dst)>0 and src%64==dst%64==0
        and src+69216<=1<<32 and dst+23072<=1<<32 and (src+69216<=dst or dst+23072<=src),'COLD_INIT_BUFFER_RANGE')
    require(len(bytes.fromhex(receipt['initialization_capture_sha256']))==32,'COLD_INIT_CAPTURE_DIGEST')
    return dict(receipt)


def cold_board_cell(token,cold):
    # Only preparation glue: original initializer, then original prepare.run.
    # No neural loop, no implicit retry, and no old board-owner reuse.
    prefix=Path(cold['prefix']).read_text(encoding='utf-8')
    require(hashlib.sha256(prefix.encode()).hexdigest()==cold['prefix_sha256'],'COLD_INIT_CELL_CHANGED')
    suffix='''
camera_token = %r
camera_mac = lambda v: hmac.new(bytes.fromhex(camera_token),json.dumps(v,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
camera_body = dict(operation='MANUAL_COLD_INIT_READY',initialization_receipt=line2_fresh_initialized.receipt)
camera_packet = dict(body=camera_body,mac=camera_mac(camera_body))
camera_request = urllib.request.Request('http://192.168.2.89:18790/bundle',data=json.dumps(camera_packet).encode(),headers={'Content-Type':'application/json'})
with urllib.request.urlopen(camera_request,timeout=45) as camera_reply:
    camera_response=json.loads(camera_reply.read(2000001))
assert hmac.compare_digest(camera_mac(camera_response['body']),camera_response['mac']),'Camera package signature mismatch'
camera_payload=camera_response['body'];camera_zip=base64.b64decode(camera_payload['archive_b64'],validate=True)
assert hashlib.sha256(camera_zip).hexdigest()==camera_payload['archive_sha256'],'Camera ZIP mismatch'
camera_new_root=Path.cwd()/camera_payload['root_name']
assert camera_new_root.parent==Path.cwd() and not camera_new_root.exists(),'Camera directory conflict; stop'
with zipfile.ZipFile(io.BytesIO(camera_zip)) as camera_archive:
    assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in camera_archive.namelist())
    camera_new_root.mkdir();camera_archive.extractall(camera_new_root)
camera_spec=importlib.util.spec_from_file_location('line2_cold_camera_'+camera_new_root.name,camera_new_root/'prepare_camera.py')
camera_entry=importlib.util.module_from_spec(camera_spec);camera_spec.loader.exec_module(camera_entry)
camera3_bundle,camera3_service_instance=camera_entry.run(camera_new_root,line2_fresh_initialized)
'''%token
    return prefix+suffix


def cold_operator_cell(token,cold):
    return '''# 本次仅运行一次：切回⑦并准备32步；随后在原GUI点开始。失败停止，不重跑。
import urllib.request,json,hashlib,hmac
line2_cold_key=%r
with urllib.request.urlopen('http://192.168.2.89:18790/operator-entry',timeout=10) as line2_reply:
    line2_packet=json.loads(line2_reply.read(500001))
line2_body=line2_packet['body']
line2_mac=hmac.new(bytes.fromhex(line2_cold_key),json.dumps(line2_body,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
assert hmac.compare_digest(line2_mac,line2_packet['mac']),'Cold preparation signature mismatch'
assert line2_body['schema']=='flyvis-signed-cold-prepare-entry/v1' and line2_body['initialization_run_id']==%r,'Wrong initialization run'
assert hashlib.sha256(line2_body['source'].encode()).hexdigest()==line2_body['source_sha256'],'Cold preparation source changed'
exec(compile(line2_body['source'],'LINE2_MANUAL_COLD_PREPARE','exec'),globals(),globals())
'''%(token,cold['config']['run_id'])


def manual_prepare(execute,*,minimal_compute=False,cold_init=None):
    from joint_camera_bundle import preparation_parent
    from launch_recovery import gui_port_available
    gui_port_available()  # Fail before exposing a board preparation request.
    selection=dict(cold_init=load_cold_init(cold_init)) if cold_init else preparation_parent()
    stage=HERE/'runtime/joint_manual'/secrets.token_hex(16);stage.mkdir(parents=True,exist_ok=False)
    gate=ManualGate(stage,**selection,minimal_compute=minimal_compute);deadline=time.monotonic()+1200
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                require(self.path=='/operator-entry','MANUAL_ENDPOINT')
                reply=gate.operator_packet(self.client_address[0]);code=200
            except Exception as error:reply=dict(error=str(error));code=409
            raw=json.dumps(reply).encode();self.send_response(code);self.send_header('Content-Type','application/json')
            self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)))
            self.end_headers();self.wfile.write(raw)
        def do_POST(self):
            try:
                require(self.path=='/bundle','MANUAL_ENDPOINT');self.connection.settimeout(5)
                n=int(self.headers.get('Content-Length','0'));require(0<n<2048,'MANUAL_REQUEST_SIZE')
                reply=gate.bundle(json.loads(self.rfile.read(n)),self.client_address[0]);code=200
            except Exception as error:reply=dict(error=str(error));code=409
            raw=json.dumps(reply).encode();self.send_response(code);self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        def log_message(self,*args):pass
    server=LocalAddressHTTPServer(('192.168.2.89',18790),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    cell=stage/'next_board_cell.py'
    cell.write_text(cold_operator_cell(gate.token,gate.cold_init) if cold_init else board_cell(gate.token,**selection),encoding='utf-8')
    write(HERE/'runtime/joint_manual_active.json',dict(status='WAITING_FOR_USER_BOARD_CELL_NO_GPU',stage=str(stage),cell=str(cell)))
    print('MANUAL_BOARD_CELL_READY '+str(cell),flush=True)
    try:
        while not gate.ready.wait(.05):
            require(time.monotonic()<deadline,'MANUAL_OPERATOR_WAIT_EXPIRED')
        require(gate.error is None,'MANUAL_BUNDLE_FAILED '+str(gate.error))
        authority=gate.authority
        while not authority.prepared.wait(.05):authority.check();require(time.monotonic()<deadline,'MANUAL_PREPARATION_WAIT_EXPIRED')
        verify_prepared_handoff(load(gate.root/'hardware_handoff.json'),authority.scope,gate.root)
        print('ACTUAL_USER_BOARD_PREPARATION_ACCEPTED',flush=True)
        waiting_for_port=False
        while True:
            authority.check()
            try:gui_port_available();break
            except ValueError:
                if not waiting_for_port:print('WAITING_FOR_ORIGINAL_GUI_PORT · no GPU or board START yet',flush=True);waiting_for_port=True
                time.sleep(.5)
        execute(gate.root/'scope.json',gate.root/'hardware_handoff.json',pc_clock=authority)
    finally:
        server.shutdown();server.server_close();thread.join(2)
        if gate.authority:gate.authority.close()
        write(HERE/'runtime/joint_manual_active.json',dict(status='STOPPED',stage=str(stage),cell=str(cell)))

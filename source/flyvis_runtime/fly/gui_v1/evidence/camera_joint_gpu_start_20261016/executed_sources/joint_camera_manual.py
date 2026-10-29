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

def mac(body,key):
    return hmac.new(bytes.fromhex(key),json.dumps(body,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()

class ManualGate:
    def init__(self,parent):
        self.parent=parent;self.token=secrets.token_hex(32);self.ready=threading.Event();self.lock=threading.Lock()
        self.consumed=False;self.authority=None;self.root=None;self.error=None
    def bundle(self,packet,peer):
        with self.lock:
            require(peer=='192.168.2.99','MANUAL_BUNDLE_WRONG_PEER')
            require(set(packet)=={'body','mac'} and hmac.compare_digest(mac(packet['body'],self.token),packet['mac']),'MANUAL_BUNDLE_AUTH')
            require(packet['body']==dict(operation='MANUAL_PREPARE_CAMERA3',expired_run_id='e13f6d0e6bc04fcaa4e5051cb0b37391'),'MANUAL_BUNDLE_BINDING')
            require(not self.consumed,'MANUAL_BUNDLE_ALREADY_CONSUMED');self.consumed=True
            try:
                started=time.perf_counter()
                from joint_camera_bundle import build
                self.root,archive=build(self.parent)
                print('MANUAL_BUNDLE_FROZEN build_s=%.6f'%(time.perf_counter()-started),flush=True)
                self.authority=PreparationAuthority(self.root);self.authority.start()
                print('MANUAL_CLOCK_LISTENER_READY total_s=%.6f'%(time.perf_counter()-started),flush=True)
                body=dict(root_name='CAMERA3_'+load(self.root/'scope.json')['run_id'],archive_sha256=sha(archive),archive_b64=base64.b64encode(archive.read_bytes()).decode())
                return dict(body=body,mac=mac(body,self.token))
            except BaseException as error:
                self.error=str(error);raise
            finally:self.ready.set()

def board_cell(token):
    return '''# USER MANUAL BOARD STEP: same kernel; no bit download/reset/allocation.
import urllib.request, json, hashlib, hmac, base64, zipfile, io, importlib.util, sys
from pathlib import Path
camera_old_module=sys.modules.get("a3ready.prepare")
assert camera_old_module is not None, "Original prepared kernel is missing; stop"
camera_old_owners=[o for o in camera_old_module.PINNED if getattr(o,"config",{}).get("run_id")=="e13f6d0e6bc04fcaa4e5051cb0b37391" and hasattr(o,"neural_thread") and hasattr(o,"driver")]
assert len(camera_old_owners)==1, "Old prepared owner is not unique; stop"
camera_expired_owner=camera_old_owners[0]
camera_token = %r
camera_body = {"operation":"MANUAL_PREPARE_CAMERA3","expired_run_id":"e13f6d0e6bc04fcaa4e5051cb0b37391"}
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
camera3_bundle,camera3_service_instance=camera_entry.run(camera_new_root,latency485_service_instance,camera_expired_owner)
''' % token

def manual_prepare(execute):
    stage=HERE/'runtime/joint_manual'/secrets.token_hex(16);stage.mkdir(parents=True,exist_ok=False)
    gate=ManualGate(stage);deadline=time.monotonic()+1200
    class Handler(BaseHTTPRequestHandler):
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
    cell=stage/'next_board_cell.py';cell.write_text(board_cell(gate.token),encoding='utf-8')
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
        execute(gate.root/'scope.json',gate.root/'hardware_handoff.json',pc_clock=authority)
    finally:
        server.shutdown();server.server_close();thread.join(2)
        if gate.authority:gate.authority.close()
        write(HERE/'runtime/joint_manual_active.json',dict(status='STOPPED',stage=str(stage),cell=str(cell)))

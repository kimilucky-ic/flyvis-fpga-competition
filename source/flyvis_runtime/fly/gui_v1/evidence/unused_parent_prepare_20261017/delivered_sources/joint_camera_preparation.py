"""Preparation phase of the ONE Line 2 controller, not another neural runner.

The private LAN endpoint only answers pinned authenticated time challenges,
checks the same PC clock, and consumes one signed retained-preparation receipt.
It has no upload, shell, reset, register or inference endpoint.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from socketserver import TCPServer
import http.client
import hashlib
import json
import socket
from pathlib import Path
import threading
import time
import uuid

from live_protocol import canonical, host_path, load, require, sha, write
from joint_camera_control import hardware_module
from joint_camera_protocol import validate_scope
from joint_diagnostics import NONE

CLOCK_POLICY = 'PC_AUTHORITY_PS_MONOTONIC_INTERVAL/v1'


class LocalAddressHTTPServer(ThreadingHTTPServer):
    """Bind the explicit interface without HTTPServer's blocking reverse DNS.

    server_name is presentation metadata. No identity/authentication decision
    uses a reverse-resolved hostname; all endpoints already pin numeric IPs.
    """
    def server_bind(self):
        TCPServer.server_bind(self)
        self.server_name=str(self.server_address[0])
        self.server_port=self.server_address[1]


def clock_binding(handoff, scope, scope_sha):
    return dict(run_id=scope['run_id'],server_session=scope['server_session'],boot_id=scope['boot_id'],
        scope_sha256=scope_sha,plan_sha256=handoff['plan_sha256'],listener_id=handoff['listener_id'],
        start_utc=scope['start_utc'],end_utc=scope['end_utc'])


def verify_prepared_packet(packet, declaration, scope, scope_sha):
    helpers=hardware_module(declaration,'control2')
    body=helpers.verified(packet,declaration['control_config']['control_key'])
    expected=clock_binding(declaration,scope,scope_sha)
    require(body.get('schema')=='flyvis-camera-retained-prepared/v1' and body.get('binding')==expected,
            'JOINT_PREPARATION_PACKET_IDENTITY')
    receipt=body['preparation_receipt']
    if scope.get('ps_durability_policy')=='PS_COMMIT_ACK_DURABLE_TWO_BARRIERS/v1':
        from ps_commit_evidence import policy_receipt
        require(declaration.get('ps_durability_policy')==scope['ps_durability_policy']
            and declaration.get('ps_evidence_adapter_sha256')==scope['ps_evidence_adapter_sha256']
            and receipt.get('ps_durability')==policy_receipt(scope,scope_sha),'JOINT_PS_POLICY_NOT_PREPARED')
    config=dict(expected,bit_sha256=scope['bit_sha256'],hwh_sha256=scope['hwh_sha256'],
        initial_full_sha256=scope['initial_full_digest'],initial_H_sha256=scope['initial_H_sha256'],mapping_sha256=scope['mapping_sha256'])
    hardware_module(declaration,'binding').validate_readonly_receipt(config,receipt)
    if declaration.get('unused_parent'):
        transfer=receipt['unused_parent_transfer'];prior=declaration['unused_parent'];parent=prior['completed_parent']
        require(transfer['unused_run_id']==prior['run_id'] and transfer['unused_server_session']==prior['server_session']
            and transfer['unused_scope_sha256']==prior['scope_sha256']
            and transfer['preparation_receipt_sha256']==prior['preparation_receipt_sha256']
            and transfer['completed_parent_run_id']==parent['run_id']
            and transfer['completed_parent_capture_sha256']==parent['PS_capture_sha256']
            and transfer['requests']==transfer['commits']==transfer['neural_connections']==0
            and transfer['start_received'] is False
            and all(transfer[k] is True for k in ('old_poison_preserved','original_claim_preserved','source_capture_closed','old_control_thread_stopped'))
            and len(bytes.fromhex(transfer['unused_capture_sha256']))==32,'JOINT_UNUSED_PARENT_TRANSFER_NOT_PROVEN')
    if declaration.get('completed_parent'):
        transfer=receipt['completed_transfer'];prior=declaration['completed_parent']
        require(transfer['parent_run_id']==prior['run_id'] and transfer['parent_server_session']==prior['server_session']
            and transfer['parent_capture_sha256']==prior['PS_capture_sha256'] and transfer['completed_steps']==prior['completed_steps']
            and transfer['last_txn']==prior['last_txn'] and transfer['last_unified_commit_sha256']==prior['last_unified_commit_sha256']
            and all(transfer[k] is True for k in ('parent_capture_closed','original_claim_preserved','parent_state_preserved','old_control_thread_stopped')),
            'JOINT_COMPLETED_TRANSFER_NOT_PROVEN')
    if declaration.get('transfer_from_expired_run'):
        transfer=receipt['zero_step_transfer']
        require(transfer['expired_run_id']==declaration['transfer_from_expired_run']
            and transfer['requests']==transfer['commits']==transfer['neural_connections']==0
            and transfer['start_received'] is False and transfer['old_poison_preserved'] is True
            and transfer['original_claim_preserved'] is True and transfer['source_capture_closed'] is True
            and transfer['old_control_thread_stopped'] is True and len(transfer['expired_capture_sha256'])==64,
            'JOINT_ZERO_STEP_TRANSFER_NOT_PROVEN')
        if declaration.get('prior_preparation_receipt_sha256'):
            require(transfer['ancestor_run_id']=='e13f6d0e6bc04fcaa4e5051cb0b37391'
                and transfer['prior_preparation_receipt_sha256']==declaration['prior_preparation_receipt_sha256'],
                'JOINT_ZERO_STEP_ANCESTOR_NOT_BOUND')
    clock=body['clock_receipt']
    require(clock['binding']==expected and clock['policy']==CLOCK_POLICY,'JOINT_PREPARATION_CLOCK_BINDING')
    # MonotonicScope.receipt stores the already-verified proof BODY, not its
    # original wire envelope. The signed outer preparation packet authenticates
    # this entire receipt. Do not try to verify a second nonexistent envelope.
    proof=clock['proof']
    require(hashlib.sha256(json.dumps(clock['proof'],sort_keys=True).encode()).hexdigest()==clock['proof_sha256'],
            'JOINT_PREPARATION_PROOF_DIGEST')
    require(proof.get('schema')=='flyvis-clock-proof/v1' and proof.get('policy')==CLOCK_POLICY
            and proof['binding']==expected and proof['pc_clock_id']==clock['pc_clock_id'],'JOINT_PREPARATION_CLOCK_PROOF')
    status=body['status']
    require(status['state']=='BOARD_PREPARED' and status['requests']==status['commits']==0
            and status['pending'] is False and status['poisoned'] is False and status['error'] is None
            and status['neural_connections']==0 and status['service_alive'] is True,'JOINT_PREPARATION_NOT_CLEAN')
    require(all(status[k]==expected[k] for k in ('run_id','server_session','boot_id','plan_sha256','scope_sha256','listener_id')),
            'JOINT_PREPARATION_STATUS_IDENTITY')
    require(status['clock_policy']==CLOCK_POLICY and status['clock_proof_sha256']==clock['proof_sha256'],
            'JOINT_PREPARATION_STATUS_CLOCK')
    return body


def verify_prepared_handoff(handoff,scope,root):
    root=host_path(root)
    require(sha(root/'HARDWARE_DECLARATION.json')==scope['hardware_declaration_sha256'],'JOINT_DECLARATION_CHANGED')
    declaration=load(root/'HARDWARE_DECLARATION.json')
    require(declaration['status']=='DECLARED_NOT_PREPARED','JOINT_DECLARATION_STATUS')
    body=verify_prepared_packet(load(root/'PREPARED_PACKET.json'),declaration,scope,sha(root/'scope.json'))
    expected=dict(declaration,status='PREPARED_FOR_THIS_CAMERA_RUN',declaration_sha256=scope['hardware_declaration_sha256'],
        preparation_packet_sha256=sha(root/'PREPARED_PACKET.json'),clock_proof_sha256=body['clock_receipt']['proof_sha256'],
        pc_clock_id=body['clock_receipt']['pc_clock_id'])
    require(handoff==expected,'JOINT_HANDOFF_NOT_FROM_PREPARATION')
    return body


class PCClockClient:
    def init__(self,handoff,scope,scope_sha,*,diagnostics=NONE):
        self.handoff,self.scope,self.scope_sha=handoff,scope,scope_sha
        self.helpers=hardware_module(handoff,'control2')
        self.expected=clock_binding(handoff,scope,scope_sha)
        self.lock=threading.Lock()
        self.diagnostics=diagnostics;self.connection=None;self.failed=False;self.closed=False
    def check(self):
        d=self.diagnostics
        with d.measure('clock.lock_wait'):self.lock.acquire()
        try:
            require(not self.failed and not self.closed,'JOINT_PC_CLOCK_CONNECTION_REVOKED')
            try:
                nonce=uuid.uuid4().hex
                with d.measure('clock.sign_request'):
                    request=self.helpers.sign(dict(schema='flyvis-pc-clock-check/v1',binding=self.expected,nonce=nonce),
                                              self.handoff['control_config']['control_key'])
                    raw_request=json.dumps(request).encode()
                if self.connection is None:
                    ep=self.handoff['pc_authority_endpoint']
                    self.connection=http.client.HTTPConnection(ep['host'],ep['port'],timeout=2)
                    d.call('clock.connect',self.connection.connect)
                    self.connection.sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
                    # A dead retained connection must never reconnect silently.
                    self.connection.auto_open=False
                connection=self.connection
                require(connection.sock is not None,'JOINT_PC_CLOCK_DISCONNECTED')
                d.call('clock.send_request',connection.request,'POST','/guard',body=raw_request,headers={'Content-Type':'application/json'})
                response=d.call('clock.wait_response_headers',connection.getresponse)
                raw=d.call('clock.read_response_body',response.read,16385)
                require(response.status==200 and len(raw)<=16384 and not response.will_close,'JOINT_PC_CLOCK_AUTHORITY_LOST')
                with d.measure('clock.verify_response'):
                    body=self.helpers.verified(json.loads(raw),self.handoff['control_config']['control_key'])
                    require(body.get('ok') is True and body['nonce']==nonce and body['binding']==self.expected
                            and body['pc_clock_id']==self.handoff['pc_clock_id'],'JOINT_PC_CLOCK_AUTHORITY_CHANGED')
            except BaseException:
                self.failed=True
                if self.connection:self.connection.close()
                raise
        finally:self.lock.release()
    def close(self):
        with self.lock:
            self.closed=True
            if self.connection:self.connection.close()


class PreparationAuthority:
    def init__(self,root,*,clock=None):
        self.root=host_path(root).resolve()
        self.scope=load(self.root/'scope.json');validate_scope(self.scope)
        self.scope_sha=sha(self.root/'scope.json')
        self.declaration=load(self.root/'HARDWARE_DECLARATION.json')
        require(sha(self.root/'HARDWARE_DECLARATION.json')==self.scope['hardware_declaration_sha256'],'JOINT_DECLARATION_CHANGED')
        self.config=load(self.root/'PRIVATE_CONFIG.json')
        require(self.config['scope_sha256']==self.scope_sha,'JOINT_CLOCK_CONFIG_SCOPE')
        self.helpers=hardware_module(self.declaration,'control2')
        self.clock=clock or hardware_module(self.declaration,'clock').PCClockAuthority()
        self.lock=threading.RLock();self.prepared=threading.Event();self.error=None;self.server=None;self.thread=None;self.seen=set()
        self.binding=clock_binding(self.declaration,self.scope,self.scope_sha)
    def check(self):
        with self.lock:
            require(self.error is None,'JOINT_PREPARATION_REVOKED')
            return self.clock.check()
    def dispatch(self,path,packet):
        with self.lock:
            self.check()
            if path=='/clock':
                return self.clock.answer(packet,self.config)
            body=self.helpers.verified(packet,self.config['control_key'])
            if path=='/guard':
                require(body.get('schema')=='flyvis-pc-clock-check/v1' and body.get('binding')==self.binding,'JOINT_GUARD_IDENTITY')
                nonce=body['nonce'];require(isinstance(nonce,str) and len(nonce)==32 and nonce not in self.seen,'JOINT_GUARD_NONCE')
                require(len(self.seen)<30000,'JOINT_GUARD_REQUEST_LIMIT');self.seen.add(nonce)
                return self.helpers.sign(dict(ok=True,nonce=nonce,binding=self.binding,pc_clock_id=self.clock.id),self.config['control_key'])
            require(path=='/prepared' and not self.prepared.is_set(),'JOINT_PREPARATION_CONSUMED_OR_UNKNOWN_PATH')
            verified=verify_prepared_packet(packet,self.declaration,self.scope,self.scope_sha)
            require(verified['clock_receipt']['pc_clock_id']==self.clock.id,'JOINT_PREPARATION_WRONG_PC_PROCESS')
            require(not (self.root/'PREPARED_PACKET.json').exists(),'JOINT_PREPARATION_FILE_ALREADY_EXISTS')
            write(self.root/'PREPARED_PACKET.json',packet)
            hardware=dict(self.declaration,status='PREPARED_FOR_THIS_CAMERA_RUN',declaration_sha256=self.scope['hardware_declaration_sha256'],
                preparation_packet_sha256=sha(self.root/'PREPARED_PACKET.json'),clock_proof_sha256=verified['clock_receipt']['proof_sha256'],
                pc_clock_id=self.clock.id)
            write(self.root/'hardware_handoff.json',hardware)
            self.prepared.set()
            return self.helpers.sign(dict(ok=True,binding=self.binding,pc_clock_id=self.clock.id),self.config['control_key'])
    def start(self):
        owner=self
        class Handler(BaseHTTPRequestHandler):
            protocol_version='HTTP/1.1'
            def setup(self):
                super().setup()
                self.connection.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
            def do_POST(self):
                try:
                    length=int(self.headers.get('Content-Length','0'))
                    require(0<length<=65536,'JOINT_PREPARATION_BODY_SIZE')
                    self.connection.settimeout(3)
                    result=owner.dispatch(self.path,json.loads(self.rfile.read(length)))
                    data=json.dumps(result).encode();self.send_response(200)
                except Exception as error:
                    self.close_connection=True
                    data=json.dumps(dict(error=type(error).__name__+': '+str(error))).encode();self.send_response(409)
                self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)))
                self.end_headers();self.wfile.write(data)
                if not self.close_connection:self.connection.settimeout(10)
            def do_GET(self): self.send_error(405)
            def log_message(self,*args): pass
        ep=self.declaration['pc_authority_endpoint']
        self.server=LocalAddressHTTPServer((ep['host'],ep['port']),Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def close(self):
        if self.server:self.server.shutdown();self.server.server_close()
        if self.thread:self.thread.join(2)


def prepare_and_execute(root,execute):
    authority=PreparationAuthority(root)
    try:
        authority.start()
        print('WAITING_FOR_ACTUAL_BOARD_PREPARATION · time proof and read20 only; no GPU yet',flush=True)
        while not authority.prepared.wait(.05):
            authority.check();validate_scope(authority.scope)
        verify_prepared_handoff(load(authority.root/'hardware_handoff.json'),authority.scope,authority.root)
        authority.check()
        execute(authority.root/'scope.json',authority.root/'hardware_handoff.json',pc_clock=authority)
    finally: authority.close()

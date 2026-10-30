"""Local authenticated, bounded JSON RPC; no pickle, device imports or implicit starts."""
import json
import secrets
import socket
import socketserver
import struct
import threading
import time
from live_protocol import require
from realtime_timing import Timings

LIMIT=4*1024*1024

def receive(sock):
    def read(n):
        data=bytearray()
        while len(data)<n:
            block=sock.recv(n-len(data))
            if not block:raise ConnectionError('STREAM_DISCONNECTED')
            data.extend(block)
        return bytes(data)
    length=struct.unpack('!I',read(4))[0];require(0<length<=LIMIT,'STREAM_MESSAGE_BOUND')
    # Linux TCP delayed ACK can hold the remaining request behind a Windows/WSL
    # forwarding socket. Acknowledge the header promptly; payload/limits unchanged.
    if hasattr(socket,'TCP_QUICKACK'):
        sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_QUICKACK,1)
    return json.loads(read(length))

def send(sock,value):
    data=json.dumps(value,separators=(',',':'),allow_nan=False).encode()
    require(len(data)<=LIMIT,'STREAM_MESSAGE_BOUND');sock.sendall(struct.pack('!I',len(data))+data)

class RPC:
    def init__(self,endpoint,role='bridge'):
        self.endpoint=endpoint;self.role=role;self.sock=None;self.lock=threading.Lock()
        self.timings=Timings()
    def call(self,op,body=None):
        waiting=time.perf_counter()
        with self.lock:
            self.timings.add('client_lock_wait',time.perf_counter()-waiting)
            try:
                if self.sock is None:
                    self.sock=socket.create_connection(('127.0.0.1',self.endpoint['port']),timeout=3)
                    self.sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
                with self.timings.measure('encode_and_send'):
                    send(self.sock,dict(session_id=self.endpoint['session_id'],token=self.endpoint['token'],role=self.role,op=op,body=body))
                with self.timings.measure('receive_and_parse'):
                    reply=receive(self.sock)
                require(reply['ok'],reply.get('error','STREAM_RPC_FAILED'));return reply['value']
            except BaseException:
                self.close();raise
    def close(self):
        if self.sock:
            self.sock.close();self.sock=None

class LocalRPC:
    def init__(self,session_id,dispatch,port=0):
        require(type(port) is int and 0<=port<=65535,'STREAM_PORT_BOUND')
        token=secrets.token_hex(32)
        class Handler(socketserver.BaseRequestHandler):
            def handle(h):
                h.request.settimeout(5)
                h.request.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
                try:
                    while True:
                        q=receive(h.request)
                        require(q.get('session_id')==session_id and secrets.compare_digest(q.get('token',''),token),'STREAM_AUTH')
                        require(q.get('role') in ('bridge','renderer'),'STREAM_ROLE')
                        try:value=dispatch(q['role'],q['op'],q.get('body'));reply=dict(ok=True,value=value)
                        except (ValueError,KeyError,TypeError) as e:reply=dict(ok=False,error=str(e))
                        send(h.request,reply)
                except (OSError,ValueError,KeyError,ConnectionError):pass
        class Server(socketserver.ThreadingTCPServer):daemon_threads=True
        self.server=Server(('127.0.0.1',port),Handler)
        self.endpoint=dict(port=self.server.server_address[1],token=token,session_id=session_id,transport='loopback_authenticated_JSON_v1')
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def close(self):self.server.shutdown();self.server.server_close();self.thread.join(2)

class AuditMonitor:
    """Filesystem/identity auditing off the CUDA submission loop. Fail closed on stall."""
    def init__(self,audit,interval=.25):
        self.audit=audit;self.interval=interval;self.error=None;self.at=0.;self.end=threading.Event()
        audit();self.at=time.monotonic();self.thread=threading.Thread(target=self.loop,daemon=True);self.thread.start()
    def loop(self):
        while not self.end.wait(self.interval):
            try:self.audit();self.at=time.monotonic()
            except BaseException as e:self.error=str(e);return
    def check(self,operation='check'):
        require(self.error is None,'AUDIT_REVOKED '+str(self.error));require(time.monotonic()-self.at<2,'AUDIT_STALLED')
    def close(self):self.end.set();self.thread.join(3)

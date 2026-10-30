"""User-started board service. Import never touches PYNQ or the board.

5771 is preparation/control only; 5768 keeps the accepted neural wire ABI.
The PC cannot upload, initialize, download, allocate or reset through this API.
"""
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import socket
import threading
import time
import uuid

from .control2 import require, sign, verified, same_identity, BIT_SHA, HWH_SHA


def verify_files(root):
    root = Path(root)
    manifest = json.loads((root / 'MANIFEST.json').read_text(encoding='utf-8'))
    for name, expected in manifest['files'].items():
        path = Path(name)
        require(not path.is_absolute() and '..' not in path.parts, 'MANIFEST_PATH')
        require(hashlib.sha256((root / path).read_bytes()).hexdigest() == expected,
                'FILE_MISSING_OR_CHANGED_' + name)
    require(manifest['files']['neuron_a.bit'] == BIT_SHA and
            manifest['files']['neuron_a.hwh'] == HWH_SHA, 'SEALED_IMAGE_REQUIRED')
    return manifest


class ManualBoardService:
    def init__(self, driver, evidence, config, neural_session, *, host='0.0.0.0',
                 control_port=5776, neural_port=5768, peer='192.168.2.89', idle_s=3600):
        self.driver = driver
        self.evidence = evidence
        self.config = config
        self.neural_session = neural_session
        self.host, self.peer = host, peer
        self.neural_port = neural_port
        self.ready_id = secrets.token_hex(24)
        self.lock = threading.RLock()
        self.state = 'BOARD_PREPARED'
        self.error = None
        self.identity = None
        self.connections = 0
        self.idle_deadline = time.monotonic() + idle_s
        self.idle_s = idle_s
        self.listener = None
        self.connection = None
        self.neural_thread = None
        self.seen = set()
        self.http = self._http_server(control_port)
        self.thread = None

    def event(self, name, **values):
        if self.evidence:
            self.evidence.event(name, **values)
        print(name, json.dumps(values, ensure_ascii=True), flush=True)

    def start(self):
        require(self.thread is None, 'MANUAL_SERVICE_ALREADY_STARTED')
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.expiry_thread = threading.Thread(target=self._expire, daemon=True)
        self.expiry_thread.start()
        self.event('BOARD_PREPARED', run_id=self.config['run_id'],
                   control_port=self.http.server_port, idle_timeout_s=self.idle_s,
                   requests=0, commits=0, waiting_for='PC_START')
        return self

    def _expire(self):
        while self.state == 'BOARD_PREPARED':
            if time.monotonic() >= self.idle_deadline:
                self.stop('MANUAL_PREPARATION_EXPIRED')
                return
            time.sleep(.1)

    def status(self, nonce):
        require(isinstance(nonce, str) and len(nonce) == 32, 'STATUS_NONCE')
        # No register reads, download, reset, allocation or neural work here.
        return dict(run_id=self.config['run_id'], server_session=self.config['server_session'],
                    boot_id=self.driver.boot_id, plan_sha256=self.config['plan_sha256'],
                    ready_id=self.ready_id, nonce=nonce, state=self.state, error=self.error,
                    bit_sha256=BIT_SHA, hwh_sha256=HWH_SHA,
                    requests=self.driver.requests, commits=self.driver.commits,
                    pending=self.driver.pending is not None, poisoned=self.driver.poisoned,
                    neural_connections=self.connections, service_alive=bool(self.thread and self.thread.is_alive()),
                    preparation_remaining_s=max(0, self.idle_deadline - time.monotonic()),
                    identity=self.identity, evidence_directory=str(self.evidence.directory),
                    evidence_sync_calls=self.evidence.journal.sync_calls, evidence_sync_ns=self.evidence.journal.sync_ns)

    def handle(self, path, packet):
        body = verified(packet, self.config['control_key'])
        require(body.get('run_id') == self.config['run_id'] and
                body.get('server_session') == self.config['server_session'] and
                body.get('ready_id') == self.ready_id and
                body.get('plan_sha256') == self.config['plan_sha256'], 'WRONG_MANUAL_IDENTITY')
        nonce = body.get('nonce')
        require(isinstance(nonce, str) and len(nonce) == 32, 'COMMAND_NONCE')
        with self.lock:
            require(nonce not in self.seen, 'REPLAYED_COMMAND')
            self.seen.add(nonce)
            if path == '/stop':
                self.stop('PC_STOP_' + str(body.get('reason', 'UNKNOWN')))
                return self.status(nonce)
            if path in ('/evidence_begin','/evidence_chunk'):
                from .capture_transfer import handle_capture
                return dict(self.status(nonce), **handle_capture(self,path,body))
            require(path == '/start', 'CONTROL_ENDPOINT')
            require(self.state == 'BOARD_PREPARED' and time.monotonic() < self.idle_deadline,
                    'START_CONSUMED_OR_EXPIRED')
            require(not self.driver.poisoned and self.driver.pending is None and
                    self.driver.requests == self.driver.commits == 0, 'UNCLEAN_BOARD')
            identity, gpu = body['identity'], body['gpu_ready']
            require(identity['boot_id'] == self.driver.boot_id, 'BOOT_CHANGED')
            for key in ('run_id', 'server_session'):
                require(identity[key] == self.config[key], 'START_IDENTITY')
            require(gpu.get('status') == 'GPU_READY' and gpu.get('board_connected') is False
                    and gpu.get('waiting_for') == 'BOARD_READY.json', 'GPU_NOT_READY')
            for key in ('run_id', 'server_session', 'scope_sha256'):
                require(gpu.get(key) == identity[key], 'GPU_IDENTITY_' + key)
            require(isinstance(identity.get('scope_sha256'), str) and len(identity['scope_sha256']) == 64,
                    'SCOPE_SHA_REQUIRED')
            remaining = body.get('scope_remaining_s', 0)
            require(0 < remaining <= 900, 'SCOPE_DEADLINE')
            # Consume START before any bind. An ambiguous failure is never retried.
            self.identity = dict(identity)
            self.state = 'STARTING'
            self.driver.session_deadline = time.monotonic() + remaining
            self.listener = socket.socket()
            try:
                self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.listener.bind((self.host, self.neural_port))
                self.neural_port = self.listener.getsockname()[1]
                self.listener.listen(1)
                self.listener.settimeout(min(5, remaining))
                self.state = 'ARMED'
                self.neural_thread = threading.Thread(target=self._neural, daemon=True)
                self.neural_thread.start()
                self.event('START_ARMED', **identity)
                return self.status(nonce)
            except BaseException as exc:
                self.stop('START_FAILED_OR_UNKNOWN_' + repr(exc))
                raise

    def _neural(self):
        try:
            connection, peer = self.listener.accept()
            self.listener.close()
            self.listener = None
            self.connection = connection
            self.connections += 1
            require(peer[0] == self.peer, 'WRONG_NEURAL_PEER')
            with connection:
                connection.settimeout(5)
                self.state = 'RUNNING'
                self.event('NEURAL_CONNECTED', peer=peer[0])
                self.neural_session(connection, self.driver, self.evidence, {})
            require(self.driver.requests == self.driver.commits == 1000 and self.driver.pending is None,
                    'INCOMPLETE_BOARD_RESULT')
            require(self.state == 'RUNNING', 'STOPPED_RUN_CANNOT_COMPLETE')
            self.event('BOARD_COMPLETE', requests=1000, commits=1000)
            self.state = 'BOARD_COMPLETE'
        except BaseException as exc:
            self.stop('NEURAL_FAILED_OR_UNKNOWN_' + repr(exc))
        finally:
            self.connection = None

    def stop(self, reason):
        with self.lock:
            if self.state in ('BOARD_COMPLETE', 'FAILED_OR_UNKNOWN'):
                return
            self.state, self.error = 'FAILED_OR_UNKNOWN', str(reason)
            self.driver.poisoned = True
            for sock in (self.listener, self.connection):
                if sock:
                    try:
                        sock.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        pass
                    sock.close()
            self.listener = None
            self.event('FAIL_STOP', error=self.error, requests=self.driver.requests,
                       commits=self.driver.commits, pending=self.driver.pending is not None)
            self.evidence.close()

    def _http_server(self, port):
        owner = self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def reply(self, value, status=200):
                raw = json.dumps(sign(value, owner.config['control_key'])).encode('utf-8')
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Content-Length', str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
            def do_GET(self):
                from urllib.parse import urlsplit, parse_qs
                try:
                    require(self.client_address[0] == owner.peer, 'WRONG_CONTROL_PEER')
                    self.connection.settimeout(5)
                    parsed = urlsplit(self.path)
                    require(parsed.path == '/status', 'CONTROL_ENDPOINT')
                    nonce = parse_qs(parsed.query).get('nonce', [''])[0]
                    self.reply(owner.status(nonce))
                except Exception as exc:
                    self.reply(dict(error=str(exc)), 409)
            def do_POST(self):
                try:
                    require(self.client_address[0] == owner.peer, 'WRONG_CONTROL_PEER')
                    self.connection.settimeout(5)
                    count = int(self.headers.get('Content-Length', '0'))
                    require(0 < count <= 16384, 'CONTROL_LENGTH')
                    raw = self.rfile.read(count)
                    require(len(raw) == count, 'SHORT_CONTROL')
                    self.reply(owner.handle(self.path, json.loads(raw)))
                except Exception as exc:
                    # Invalid identities cannot consume START or execute neural work.
                    self.reply(dict(error=str(exc)), 409)
        http = ThreadingHTTPServer((self.host, port), Handler)
        http.daemon_threads = True
        return http


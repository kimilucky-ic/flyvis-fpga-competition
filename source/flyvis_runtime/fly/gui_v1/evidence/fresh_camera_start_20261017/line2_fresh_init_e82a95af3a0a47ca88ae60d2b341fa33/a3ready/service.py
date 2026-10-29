"""Camera window control; original HMAC and neural ABI, no import side effects."""
import dataclasses, hashlib, json, select, socket, threading, time
from datetime import datetime, timezone
from .legacy_transport import ManualBoardService as PreviousService
from .control2 import require, verified, same_identity
from .contract import validate, window, capabilities, hex_value, REASONS
from . import protocol as w

class CameraBoardService(PreviousService):
    def init__(self,driver,evidence,config,*,host='0.0.0.0',control_port=None,neural_port=None,peer=None,
                 cpu_fixture=False,http_factory=None,listener_factory=None,waiter=None,thread_factory=None,scope_bytes=None,preparation_receipt=None,clock_guard=None):
        validate(config,cpu_fixture=cpu_fixture,clock=clock_guard)
        self.clock_guard=clock_guard
        require(driver.requests==driver.commits==0 and driver.pending is None and not driver.poisoned,'FRESH_CAMERA_DRIVER_REQUIRED')
        require(driver.plan['max_steps']==config['max_steps'] and driver.server_session==config['server_session'] and driver.boot_id==config['boot_id'],'DRIVER_CONFIG_IDENTITY')
        if not cpu_fixture:
            from .binding import validate_scope_binding,validate_readonly_receipt
            validate_scope_binding(config,scope_bytes,clock=clock_guard)
            validate_readonly_receipt(config,preparation_receipt or {})
            from .driver import Full485Driver
            require(type(driver) is Full485Driver,'EXACT_CAMERA_NUMERICAL_DRIVER')
            require(driver.src.nbytes==preparation_receipt['src_bytes'] and driver.dst.nbytes==preparation_receipt['dst_bytes']
                    and int(driver.src.device_address)==preparation_receipt['src_address']
                    and int(driver.dst.device_address)==preparation_receipt['dst_address'],'RETAINED_BUFFER_RECEIPT_CHANGED')
        else:require(http_factory is not None and listener_factory is not None and waiter is not None,'CPU_FIXTURE_NO_NETWORK_FACTORIES')
        require(type(control_port) is int and type(neural_port) is int and isinstance(peer,str) and bool(peer),'EXPLICIT_ENDPOINTS_REQUIRED')
        self.cpu_fixture=cpu_fixture;self.http_factory=http_factory
        self.listener_factory=listener_factory or socket.socket
        self.waiter=waiter or (lambda conn,t:bool(select.select([conn],[],[],t)[0]))
        self.thread_factory=thread_factory or (lambda fn:threading.Thread(target=fn,daemon=True))
        self.inflight=False;self.finish_attempted=False;self.finish_requested=threading.Event();self.neural_exited=threading.Event()
        self.finish_receipt=None;self.neural_failure=None;self.secondary_errors=[]
        super().init__(driver,evidence,config,self.serve_connection,host=host,control_port=control_port,neural_port=neural_port,peer=peer,idle_s=3600)
        self.idle_deadline=min(self.idle_deadline,time.monotonic()+self.clock_guard.remaining_s(config))
        self.clock_receipt=self.clock_guard.receipt(config)
    def _http_server(self,port):
        return self.http_factory(self,port) if self.http_factory is not None else super()._http_server(port)
    def expected_identity(self):
        return {k:self.config[k] for k in ('run_id','server_session','boot_id','scope_sha256','listener_id')}
    def status(self,nonce):
        result=super().status(nonce)
        result.update(capabilities(self.config),listener_id=self.config['listener_id'],scope_sha256=self.config['scope_sha256'],
            initial_full_digest=self.config['initial_full_sha256'],initial_H_sha256=self.config['initial_H_sha256'],mapping_sha256=self.config['mapping_sha256'],
            inflight=self.inflight,completed_steps=self.driver.commits,prepared_status='PREPARED_FOR_THIS_CAMERA_RUN')
        if self.finish_receipt:result.update(self.finish_receipt)
        result.update(clock_policy=self.clock_receipt['policy'],clock_proof_sha256=self.clock_receipt['proof_sha256'],
            clock_status_scope='PREPARATION_SNAPSHOT_NOT_A_NEW_TIME_SAMPLE')
        return result
    def _admit(self,packet):
        body=verified(packet,self.config['control_key'])
        for k,v in (('run_id',self.config['run_id']),('server_session',self.config['server_session']),('plan_sha256',self.config['plan_sha256']),('ready_id',self.ready_id)):
            require(body.get(k)==v,'CAMERA_CONTROL_IDENTITY_'+k)
        nonce=body.get('nonce');require(isinstance(nonce,str) and len(nonce)==32,'COMMAND_NONCE')
        require(nonce not in self.seen,'REPLAYED_COMMAND');self.seen.add(nonce)
        return body
    def handle(self,path,packet):
        with self.lock:
            body=self._admit(packet)
            # Consumed successful finish remains immutable; never replay the receipt.
            if path=='/finish_window':
                require(not self.finish_attempted and self.state=='RUNNING','FINISH_ALREADY_CONSUMED_OR_NOT_RUNNING')
                same_identity(body.get('identity',{}),self.expected_identity())
                require(body['identity']==self.identity,'FINISH_IDENTITY_CHANGED')
                self.finish_attempted=True
            elif path in ('/evidence_begin','/evidence_chunk'):
                from .capture_transfer import handle_capture
                return dict(self.status(body['nonce']),**handle_capture(self,path,body))
            elif path=='/stop':
                self.stop('PC_STOP_'+str(body.get('reason','UNKNOWN')));return self.status(body['nonce'])
            else:
                require(path=='/start','CONTROL_ENDPOINT')
                window(self.config,clock=self.clock_guard)
                return self._start(body)
        # Finish cannot hold the service lock while joining the receiver.
        try:return self._finish(body)
        except BaseException as exc:
            self.stop('FINISH_FAILED_OR_UNKNOWN_'+repr(exc));raise
    def _start(self,body):
        require(self.state=='BOARD_PREPARED' and time.monotonic()<self.idle_deadline,'START_CONSUMED_OR_EXPIRED')
        d=self.driver;require(d.requests==d.commits==0 and d.pending is None and not d.poisoned,'UNCLEAN_BOARD')
        identity=body['identity'];same_identity(identity,self.expected_identity());require(identity==self.expected_identity(),'START_FULL_IDENTITY')
        gpu=body['gpu_ready']
        require(gpu.get('status')=='GPU_READY' and gpu.get('board_connected') is False and gpu.get('waiting_for')=='BOARD_READY.json','GPU_NOT_READY')
        require(all(gpu.get(k)==identity[k] for k in ('run_id','server_session','scope_sha256')),'GPU_IDENTITY')
        remaining=body.get('scope_remaining_s',0)
        require(type(remaining) in (int,float) and 0<remaining<=1500,'SCOPE_DEADLINE')
        utc_left=self.clock_guard.remaining_s(self.config)
        require(utc_left>0,'CAMERA_SCOPE_EXPIRED')
        self.identity=dict(identity);self.state='STARTING'
        d.session_deadline=time.monotonic()+min(remaining,utc_left,self.config['max_worker_s'])
        try:
            self.listener=self.listener_factory();self.listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            self.listener.bind((self.host,self.neural_port));self.neural_port=self.listener.getsockname()[1]
            self.listener.listen(1);self.listener.settimeout(min(5,remaining));self.state='ARMED'
            self.neural_thread=self.thread_factory(self._neural);self.neural_thread.start()
            self.event('START_ARMED',**identity)
            return self.status(body['nonce'])
        except BaseException as exc:self.stop('START_FAILED_OR_UNKNOWN_'+repr(exc));raise
    def _neural(self):
        connection=None
        try:
            connection,peer=self.listener.accept();self.listener.close();self.listener=None
            with self.lock:
                self.connection=connection
                require(self.connections==0 and self.state=='ARMED','ONLY_ONE_NEURAL_CONNECTION')
                require(peer[0]==self.peer,'WRONG_NEURAL_PEER')
                self.connections+=1;self.connection=connection;self.state='RUNNING'
            with connection:
                connection.settimeout(5);self.event('NEURAL_CONNECTED',peer=peer[0]);self.serve_connection(connection)
            require(self.finish_requested.is_set() and self.state=='FINISHING','UNFINISHED_TCP_CLOSE')
        except BaseException as exc:
            self.neural_failure=repr(exc);self.stop('NEURAL_FAILED_OR_UNKNOWN_'+repr(exc))
        finally:
            if connection is not None:
                try:connection.close()
                except OSError:pass
            self.connection=None;self.neural_exited.set()
            if self.state=='FAILED_OR_UNKNOWN':self._close_failed_evidence()
    def serve_connection(self,conn,*unused):
        """Poll only between complete frames; partial frames retain the 5s bound."""
        first=True;idle_deadline=time.monotonic()+5
        while True:
            with self.lock:
                if self.finish_requested.is_set():return
                require(self.state=='RUNNING','NEURAL_SESSION_STOPPED')
                window(self.config,clock=self.clock_guard);self.driver.check_deadline()
                require(time.monotonic()<idle_deadline,'NEURAL_FRAME_IDLE_TIMEOUT')
            # Do not hold the control lock while select waits. Otherwise an
            # idle receiver can starve /finish_window and /stop.
            if not self.waiter(conn,.02):continue
            with self.lock:
                if self.finish_requested.is_set():return
                require(self.state=='RUNNING','NEURAL_SESSION_STOPPED')
                self.inflight=True
            try:
                deadline=min(time.monotonic()+5,self.driver.session_deadline)
                if self.driver.compute_deadline is not None:deadline=min(deadline,self.driver.compute_deadline)
                h,payload=w.recv_frame(conn,self.evidence.wire,deadline=deadline)
                if first:
                    require(h.op==w.HELLO,'HELLO_REQUIRED');raw=json.dumps(self.driver.attest(h),sort_keys=True).encode()
                    self.driver.bound_asid=h.asid.hex()
                    w.send_frame(conn,dataclasses.replace(h,op=w.ATTEST,payload_bytes=len(raw),payload_sha=w.digest(raw)),raw,self.evidence.wire)
                    first=False
                else:
                    require(h.asid.hex()==self.driver.bound_asid,'UNATTESTED_ASID')
                    if h.op==w.STEP:
                        require(self.driver.requests<self.config['max_steps'],'CAMERA_STEP_QUOTA')
                        if self.driver.compute_deadline is None:
                            self.driver.compute_deadline=min(self.driver.session_deadline,time.monotonic()+self.config['max_worker_s'])
                            self.evidence.event('COMPUTE_WINDOW_STARTED')
                        receipt,candidate,timing=self.driver.run(h,payload)
                        self.driver.check_deadline();w.send_frame(conn,receipt,candidate,self.evidence.wire)
                        self.evidence.event('CANDIDATE_SENT',step=h.step,**timing)
                    elif h.op==w.COMMIT:
                        # A fast controller can receive ACK before send_frame
                        # returns. Serialize the finish inspection with ACK
                        # bookkeeping so a valid normal finish cannot observe
                        # a stale inflight flag after that ACK.
                        with self.lock:
                            require(self.state=='RUNNING','NEURAL_SESSION_STOPPED')
                            ack=self.driver.finish(h,True);self.driver.check_deadline()
                            w.send_frame(conn,ack,observer=self.evidence.wire);self.evidence.event('ACK_SENT',step=h.step)
                            self.inflight=False
                    else:raise ValueError('Only STEP/COMMIT; no recovery')
                idle_deadline=time.monotonic()+5
            finally:
                with self.lock:self.inflight=False
    def _finish(self,body):
        with self.lock:
            window(self.config,clock=self.clock_guard);d=self.driver
            require(self.state=='RUNNING' and not self.inflight and not self.neural_failure,'FINISH_INFLIGHT_OR_FAILED')
            require(not d.poisoned and d.pending is None,'FINISH_PENDING_OR_POISON')
            n=body.get('completed_steps');require(type(n) is int and 0<=n<=self.config['max_steps'],'FINISH_COUNT_BOUND')
            require(d.requests==d.commits==n,'FINISH_COUNT_MISMATCH')
            require(n>0 or self.config.get('allow_zero_step_cancel') is True,'ZERO_CANCEL_NOT_AUTHORIZED')
            reason=body.get('reason');require(reason in REASONS and body.get('source_closed') is True,'FINISH_SOURCE_OR_REASON')
            require(reason!='STEP_LIMIT_COMPLETE' or n==self.config['max_steps'],'STEP_LIMIT_NOT_REACHED')
            require(hex_value(body.get('last_unified_commit_sha256'),64) and hex_value(body.get('last_txn'),32),'FINISH_DIGEST_FORMAT')
            if n:
                require(d.bound_asid is not None and len(d.committed)==1,'FINISH_ASID')
                prior=d.committed.get(bytes.fromhex(d.bound_asid));require(prior is not None and prior[0]==n-1 and prior[4]==0,'FINISH_LAST_STEP')
                commit,txn=prior[2].hex(),prior[3].hex()
            else:commit,txn='00'*32,'00'*16
            require(body['last_unified_commit_sha256']==commit and body['last_txn']==txn,'FINISH_LAST_COMMIT_TXN')
            require(self.connection is not None and not self.waiter(self.connection,0),'UNREAD_NEURAL_FRAME_OR_DISCONNECT')
            d.runtime_check()
            require(d._read('reg',0x14)==0 and d._read('reg',0x18)==0,'FINISH_PL_NOT_CLEAN_IDLE')
            self.finish_requested.set();self.state='FINISHING'
        require(self.neural_exited.wait(1),'NEURAL_FINISH_TIMEOUT')
        with self.lock:
            require(self.state=='FINISHING' and self.neural_failure is None and not self.inflight,'NEURAL_FINISH_UNKNOWN')
            record=dict(run_id=self.config['run_id'],server_session=self.config['server_session'],identity=self.identity,
                completed_steps=n,last_unified_commit_sha256=commit,last_txn=txn,reason=reason,source_closed=True)
            self.evidence.finish_window(record)
            digest_state=hashlib.sha256()
            with self.evidence.journal.path.open('rb') as stream:
                for block in iter(lambda:stream.read(1024*1024),b''):digest_state.update(block)
            digest=digest_state.hexdigest()
            self.state='FINISHED_PENDING_AUDIT'
            self.finish_receipt=dict(identity=dict(self.identity),completed_steps=n,requests=n,commits=n,pending=False,
                last_unified_commit_sha256=commit,last_txn=txn,capture_closed=True,PS_capture_sha256=digest,error=None)
            return self.status(body['nonce'])
    def _close_failed_evidence(self):
        try:self.evidence.close()
        except BaseException as exc:
            self.secondary_errors.append(repr(exc))
            try:self.evidence.journal.abandon()
            except BaseException as extra:self.secondary_errors.append(repr(extra))
    def stop(self,reason):
        with self.lock:
            if self.state in ('FINISHED_PENDING_AUDIT','FAILED_OR_UNKNOWN'):return
            self.state='FAILED_OR_UNKNOWN';self.error=str(reason);self.driver.poisoned=True
            for conn in (self.listener,self.connection):
                if conn:
                    try:conn.shutdown(socket.SHUT_RDWR)
                    except (OSError,AttributeError):pass
                    try:conn.close()
                    except OSError:pass
            self.listener=None
            try:self.event('FAIL_STOP',error=self.error,requests=self.driver.requests,commits=self.driver.commits,pending=self.driver.pending is not None)
            except BaseException as exc:self.secondary_errors.append(repr(exc))
            if self.neural_thread is None or not self.neural_thread.is_alive():self._close_failed_evidence()

ManualBoardService=CameraBoardService

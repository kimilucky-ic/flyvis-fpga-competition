"""PS evidence policy adapter; Python 3.8+, no hardware/network on import.

Reuses the sealed driver, service, protocol and original bounded journal.
Two normal-step barriers: COMMIT received before RELEASE, ACK before send.
Uncommitted STEP/candidate diagnostics may be lost on process/power failure.
"""
import dataclasses
import errno
import hashlib
import json
from pathlib import Path
import socket
import time
import types

POLICY='PS_COMMIT_ACK_DURABLE_TWO_BARRIERS/v1'
LEGACY='PS_FOUR_WIRE_BARRIERS/v1'
MMIO_ENCODING='IDENTICAL_JSONL_FIXED_MMIO_ENCODER/v1'
RUNTIME_HELPERS='ORIGINAL_RUN_NUMPY_BOUNDS_BOUND_EVIDENCE/v1'
MMIO_EVENTS=frozenset(('MMIO_READ_INTENT','MMIO_READ_RETURNED','MMIO_WRITE_INTENT','MMIO_WRITE_RETURNED'))


def encoded_mmio(event,stamp,values):
    """Exact default json.dumps bytes for the sealed driver's fixed scalar fields.

    Unknown fields/order/types use the original encoder instead. No change to
    register accesses, identity echoes, numeric checks or durability barriers.
    """
    keys=('bank','offset','value') if event.endswith('_RETURNED') or event=='MMIO_WRITE_INTENT' else ('bank','offset')
    if (event not in MMIO_EVENTS or tuple(values)!=keys or values.get('bank') not in ('reg','dma')
            or type(values.get('offset')) is not int or not 0<=values['offset']<=0xff
            or ('value' in values and (type(values['value']) is not int or not 0<=values['value']<=0xffffffff))):return None
    suffix=', "value": %d'%values['value'] if 'value' in values else ''
    return ('{"event": "%s", "monotonic_ns": %d, "bank": "%s", "offset": %d%s}\n'%
        (event,stamp,values['bank'],values['offset'],suffix)).encode('utf8')


def require(ok,message):
    if not ok:raise ValueError(message)


class BoundDriverHelpers:
    """Reuse the exact run bytecode with equivalent pure helpers, instance-only.

    No driver source/module global is changed. All state transitions, MMIO,
    checks, polling, deadlines and COMMIT/ACK keep their original code.
    """
    def init__(self,driver,evidence):
        run=driver.run.__func__
        require(run.__name__=='run' and all(k in run.__code__.co_names for k in
            ('validate_words','save_bytes','save_json')),'PS_ORIGINAL_RUN_HELPERS_REQUIRED')
        self.original_run=run;self.evidence=evidence;self.np=driver.np
        self.directory=evidence.base.directory
        self.original_save=run.__globals__['save_bytes']
        self.original_validate=run.__globals__['validate_words']
        owners=self.original_save.__globals__['OWNERS']
        require(owners.get(self.directory.resolve()) is evidence.base,'PS_BOUND_EVIDENCE_OWNER')
        self.bound_files=self.vector_checks=0
        namespace=dict(run.__globals__)
        namespace.update(validate_words=self.validate_words,save_bytes=self.save_bytes,save_json=self.save_json)
        adapted=types.FunctionType(run.__code__,namespace,run.__name__,run.__defaults__,run.__closure__)
        adapted.__kwdefaults__=run.__kwdefaults__
        require(adapted.__code__ is run.__code__,'PS_RUN_BYTECODE_CHANGED')
        self.adapted=adapted
        driver.run=types.MethodType(adapted,driver)

    def validate_words(self,payload):
        if type(payload) is not bytes:return self.original_validate(payload)
        if len(payload)%4:raise ValueError('unaligned words')
        words=self.np.frombuffer(payload,dtype='<i4')
        if self.np.any(words<-(1<<30)) or self.np.any(words>=(1<<30)):
            raise ValueError('signed31 Q24 range')
        self.vector_checks+=1

    def save_bytes(self,path,data):
        path=Path(path)
        if path.parent==self.directory:
            # Original save_bytes ignores the JournalWriter.add return. Keep
            # add's exact bounds, duplicate detection and hashing behavior.
            self.evidence.journal.add(path.name,data);self.bound_files+=1
            if path.name.endswith('PREPARED.json'):self.evidence.journal.checkpoint('PREPARED_METADATA')
            return
        return self.original_save(path,data)

    def save_json(self,path,record):
        return self.save_bytes(path,(json.dumps(record,indent=2)+'\n').encode('utf8'))


def policy_receipt(scope,scope_sha):
    return dict(policy=POLICY,adapter_sha256=scope['ps_evidence_adapter_sha256'],
        run_id=scope['run_id'],server_session=scope['server_session'],scope_sha256=scope_sha,
        normal_step_barriers=2,uncommitted_diagnostics='VOLATILE_UNTIL_COMMIT',
        committed_history='FSYNC_BEFORE_RELEASE_AND_ACK',mmio_event_encoding=MMIO_ENCODING,
        runtime_helpers=RUNTIME_HELPERS,power_loss_testing='NOT_PERFORMED')


class BarrierJournal:
    def init__(self,writer,owner):self.writer,self.owner=writer,owner
    def __getattr__(self,name):return getattr(self.writer,name)
    @property
    def sync_fn(self):return self.writer.sync_fn
    @sync_fn.setter
    def sync_fn(self,value):self.writer.sync_fn=value
    def checkpoint(self,barrier,terminal=None):
        self.writer._ready()
        stage=self.owner.stage
        if terminal is None and ((stage=='STEP_RX' and barrier=='WIRE_RX') or
                (stage=='RESULT_TX' and barrier=='WIRE_TX_INTENT')):
            self.owner.deferred_wire_barriers+=1
            self.owner.max_pending_bytes=max(self.owner.max_pending_bytes,self.writer.pending_bytes)
            return
        before=dict(getattr(self.writer,'phase_ns',{}));index=len(self.owner.timing_rows)
        try:return self.owner.timed('journal.'+barrier,self.writer.checkpoint,barrier,terminal)
        finally:
            if len(self.owner.timing_rows)>index:
                self.owner.timing_rows[-1]['journal_phase_delta_ns']={k:v-before.get(k,0) for k,v in getattr(self.writer,'phase_ns',{}).items()}


class CommitEvidence:
    """Decorate an existing fresh Evidence, retaining its format and all records."""
    def init__(self,evidence,wire,receipt):
        self.base,self.wire_module,self.receipt=evidence,wire,dict(receipt)
        self.stage=None;self.phase='HELLO';self.step_header=self.commit_header=None
        self.candidate=None;self.previous=None;self.completed=0;self.release_seen=False
        self.failed=False;self.deferred_wire_barriers=self.max_pending_bytes=0
        self.secondary_receive_callbacks=0
        self.timing_rows=[];self.timing_dropped=0;self.timing_capacity=8192
        self.mmio_encoded=0
        self.socket_owner=self.bound_socket=None
        self.socket_policy=dict(policy='PS_NODELAY_QUICKACK_WHEN_SUPPORTED/v1',NODELAY_verified=False,
            QUICKACK_supported=hasattr(socket,'TCP_QUICKACK'),QUICKACK_calls=0)
        evidence.journal=BarrierJournal(evidence.journal,self)
        self.journal=evidence.journal
        self.journal.add('PS_DURABILITY_POLICY.json',json.dumps(self.receipt,sort_keys=True).encode())
        self.journal.checkpoint('PS_DURABILITY_POLICY_ADMITTED')
    def __getattr__(self,name):return getattr(self.base,name)

    def timed(self,name,function,*args,**kwargs):
        start=time.monotonic_ns();cpu=time.thread_time_ns();step=self.completed;failed=False
        try:return function(*args,**kwargs)
        except BaseException:failed=True;raise
        finally:
            row=dict(name=name,step_id=step,phase=self.phase,duration_ns=time.monotonic_ns()-start,
                thread_cpu_ns=time.thread_time_ns()-cpu,failed=failed)
            if len(self.timing_rows)<self.timing_capacity:self.timing_rows.append(row)
            else:self.timing_dropped+=1

    def attach_service(self,service):
        """Store the original fresh service; does not bind or open a socket."""
        require(self.socket_owner is None and service.evidence is self and service.driver.evidence is self
            and service.driver.requests==service.driver.commits==0 and getattr(service,'connections',0)==0,'PS_SOCKET_OWNER_NOT_FRESH')
        self.socket_owner=service
        self.driver_helpers=BoundDriverHelpers(service.driver,self)
        # Observe existing methods on this fresh driver only, without replacing
        # any module global or adding a hardware read. CPU fixtures may omit it.
        for name in ('check_bounds','runtime_check'):
            original=getattr(service.driver,name,None)
            if original is not None:
                def measured(*args,_name=name,_original=original,**kwargs):
                    return self.timed('driver.'+_name,_original,*args,**kwargs)
                setattr(service.driver,name,measured)

    def _receive_socket_options(self):
        if self.socket_owner is None:return  # CPU memory-only fixtures need no socket.
        conn=self.socket_owner.connection
        require(conn is not None,'PS_SOCKET_CONNECTION_MISSING')
        if self.bound_socket is None:
            conn.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
            require(conn.getsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY)==1,'PS_NODELAY_NOT_APPLIED')
            self.bound_socket=conn;self.socket_policy['NODELAY_verified']=True
        require(conn is self.bound_socket,'PS_NEURAL_CONNECTION_CHANGED')
        if self.socket_policy['QUICKACK_supported']:
            try:
                conn.setsockopt(socket.IPPROTO_TCP,socket.TCP_QUICKACK,1)
                self.socket_policy['QUICKACK_calls']+=1
            except OSError as error:
                if error.errno not in (errno.ENOPROTOOPT,errno.EINVAL,errno.ENOTSUP):raise
                self.socket_policy['QUICKACK_supported']=False

    def event(self,event,**values):
        with self.journal.lock:
            try:
                if event in MMIO_EVENTS and self.base.in_compute and not (self.failed or self.base.failed):
                    stamp=time.monotonic_ns();raw=encoded_mmio(event,stamp,values)
                    if raw is not None:
                        self.base.last_event=event
                        self.journal.append_line('events.jsonl',raw)
                        self.mmio_encoded+=1
                        return dict(event=event,monotonic_ns=stamp,**values)
                if event=='RELEASE_CONFIRMED':
                    h=self.commit_header
                    require(self.phase=='ACK' and h is not None,'PS_RELEASE_BEFORE_DURABLE_COMMIT')
                    require(values.get('step')==h.step and values.get('txn')==h.txn.hex()
                        and values.get('commit_sha')==h.parent_commit.hex()
                        and values.get('state')==0 and values.get('error')==0,'PS_RELEASE_IDENTITY_OR_STATE')
                    result=self.base.event(event,**values);self.release_seen=True;return result
                return self.base.event(event,**values)
            except BaseException:
                self.failed=self.base.failed=True
                raise

    def wire(self,direction,raw):
        with self.journal.lock:
            if (self.failed or self.base.failed) and direction in ('rx_rejected_header','rx_incomplete'):
                # recv_frame reports a failed observer a second time. Keep the
                # original fsync/identity exception, never replace it or resume.
                self.secondary_receive_callbacks+=1
                try:self.base.wire(direction,raw)
                except BaseException:pass
                return
            try:
                require(not self.failed and not self.base.failed,'PS_POLICY_REVOKED')
                require(direction in ('rx','tx_intent'),'PS_INCOMPLETE_WIRE')
                w=self.wire_module;h=w.Header.unpack(raw[:w.HEADER_BYTES]);payload=raw[w.HEADER_BYTES:]
                require(len(payload)==h.payload_bytes and w.digest(payload)==h.payload_sha,'PS_POLICY_WIRE_INTEGRITY')
                if direction=='rx':self._receive_socket_options()
                stage,next_phase=None,None
                if self.phase=='HELLO':
                    require(direction=='rx' and h.op==w.HELLO,'PS_HELLO_REQUIRED')
                    self.hello=h;next_phase='ATTEST'
                elif self.phase=='ATTEST':
                    require(direction=='tx_intent' and h.op==w.ATTEST and h.identity()==self.hello.identity(),'PS_ATTEST_IDENTITY')
                    next_phase='STEP'
                elif self.phase=='STEP':
                    require(direction=='rx' and h.op==w.STEP and h.asid==self.hello.asid and h.step==self.completed,'PS_STEP_ORDER')
                    if self.previous:
                        require(h.parent_commit==self.previous[0] and h.previous_txn==self.previous[1]
                            and payload[:w.WORD_BYTES]==self.previous[2],'PS_CANONICAL_FEEDBACK')
                    stage,next_phase='STEP_RX','RESULT';self.step_header=h
                elif self.phase=='RESULT':
                    require(direction=='tx_intent' and h.op==w.RESULT and h.identity()==self.step_header.identity()
                        and h.status==0 and h.compute_cycles==10*w.N+1,'PS_RESULT_IDENTITY')
                    stage,next_phase='RESULT_TX','COMMIT';self.candidate=payload
                elif self.phase=='COMMIT':
                    require(direction=='rx' and h.op==w.COMMIT and h.parent_commit!=bytes(32),'PS_COMMIT_REQUIRED')
                    expected=dataclasses.replace(self.step_header,op=w.COMMIT,payload_bytes=0,payload_sha=w.digest(b''),parent_commit=h.parent_commit)
                    require(h==expected,'PS_COMMIT_IDENTITY')
                    next_phase='ACK';self.commit_header=h;self.release_seen=False
                elif self.phase=='ACK':
                    require(direction=='tx_intent' and self.release_seen and h==dataclasses.replace(self.commit_header,op=w.ACK),'PS_ACK_WITHOUT_RELEASE_OR_IDENTITY')
                    next_phase='STEP'
                else:raise ValueError('PS_POLICY_PHASE')
                before=self.journal.sync_calls
                self.stage=stage
                self.timed('wire.'+direction,self.base.wire,direction,raw)
                require(self.journal.sync_calls-before==(0 if stage else 1),'PS_POLICY_BARRIER_COUNT')
                if self.phase=='ACK':
                    self.previous=(h.parent_commit,h.txn,self.candidate);self.completed+=1
                self.phase=next_phase
            except BaseException as error:
                self.failed=self.base.failed=True
                self.stage=None
                # Preserve rejected/incomplete bytes if the original bounded
                # writer is still usable. Never replace the primary failure.
                try:
                    self.base.wire('rx_incomplete',raw)
                    self.base.event('PS_POLICY_FAILED',error=repr(error))
                except BaseException:pass
                raise
            finally:self.stage=None

    def finish_window(self,record):
        with self.journal.lock:
            require(not self.failed and not self.base.failed and self.phase=='STEP' and self.completed==record['completed_steps'],'PS_POLICY_FINISH_INCOMPLETE')
            self._save_timing()
            self.journal.add('PS_DURABILITY_SUMMARY.json',json.dumps(dict(self.receipt,completed=self.completed,
                deferred_wire_barriers=self.deferred_wire_barriers,max_pending_bytes=self.max_pending_bytes,
                socket_policy=self.socket_policy,mmio_fast_encoded=self.mmio_encoded,
                runtime_helper_counts=dict(vector_checks=self.driver_helpers.vector_checks,bound_files=self.driver_helpers.bound_files)
                    if hasattr(self,'driver_helpers') else None),sort_keys=True).encode())
            return self.base.finish_window(record)

    def _save_timing(self):
        if getattr(self,'timing_saved',False):return
        self.journal.add('PS_HOST_TIMING.json',json.dumps(dict(schema='flyvis-ps-host-timing/v1',
            run_id=self.receipt['run_id'],server_session=self.receipt['server_session'],scope_sha256=self.receipt['scope_sha256'],
            clock='PS_LOCAL_MONOTONIC_NS',semantics='Inclusive nested spans, mixed CPU/io/scheduling; never sum overlaps or compare host epochs',
            timing_complete=self.timing_dropped==0,dropped_spans=self.timing_dropped,spans=self.timing_rows),separators=(',',':')).encode())
        self.timing_saved=True

    def close(self):
        if self.phase not in ('HELLO','STEP'):self.failed=self.base.failed=True
        if not self.journal.closed and not self.journal.poisoned:
            try:self._save_timing()
            except BaseException:self.failed=self.base.failed=True
        return self.base.close()


def install_before_bind(prepared,scope_bytes,wire,adapter_file=None):
    """Explicit fresh-scope installation only; no MMIO, bind, START or DMA here."""
    c=prepared.config;s=json.loads(scope_bytes.decode('utf8'))
    require(prepared.service is None and not prepared.bind_attempted and not getattr(prepared,'ps_policy_installed',False),'PS_POLICY_AFTER_BIND_OR_REUSE')
    require(prepared.driver.requests==prepared.driver.commits==0 and prepared.driver.pending is None
        and not prepared.driver.poisoned and prepared.driver.evidence is prepared.evidence,'PS_POLICY_NOT_FRESH')
    require(scope_bytes==prepared.scope_bytes and hashlib.sha256(scope_bytes).hexdigest()==c['scope_sha256'],'PS_POLICY_SCOPE_BYTES')
    require(c.get('ps_durability_policy')==s.get('ps_durability_policy')==POLICY,'PS_POLICY_SCOPE_NOT_SELECTED')
    actual=hashlib.sha256(Path(adapter_file or __file__).read_bytes()).hexdigest()
    require(actual==c.get('ps_evidence_adapter_sha256')==s.get('ps_evidence_adapter_sha256')
        ==s.get('source_sha256',{}).get('ps_commit_evidence.py'),'PS_POLICY_ADAPTER_SHA')
    require(all(c[k]==s[k] for k in ('run_id','server_session','boot_id')),'PS_POLICY_RUN_BINDING')
    require((c.get('test_fixture') is True and s.get('execution_authority')=='CPU_FIXTURE_ONLY') or
        (c.get('test_fixture') is not True and s.get('status')=='APPROVED_BY_HUMAN'
         and s.get('human_authorization_reference')),'PS_POLICY_NOT_AUTHORIZED')
    prepared.ps_policy_installed=True
    try:
        receipt=policy_receipt(s,c['scope_sha256'])
        adapter=CommitEvidence(prepared.evidence,wire,receipt)
        prepared.driver.evidence=prepared.evidence=adapter
        prepared.receipt['ps_durability']=receipt
        return adapter
    except BaseException:
        prepared.driver.poisoned=True
        raise

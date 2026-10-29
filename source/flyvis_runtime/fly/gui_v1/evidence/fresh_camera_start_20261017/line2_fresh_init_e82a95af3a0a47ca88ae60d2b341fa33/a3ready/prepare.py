"""Explicit retained-c708 handoff, no load/reset/allocate and no automatic start.

Import is pure. Calling prepare_retained on a REAL board requires a fresh exact
authorization; this task exercises it ONLY with explicit CPU dummy objects.
"""
import hashlib,inspect,json,sys,threading,time
from pathlib import Path
from .control2 import require
from .binding import validate_scope_binding,validate_readonly_receipt
from .clock import boot_id
from .driver import Full485Driver
from .light_evidence import Evidence
from .evidence_journal import JournalReader
from .protocol import CONFIG,INPUT_BYTES,WORD_BYTES

SOURCE_RUN='c708f1c9bac14c07ac8f56d59678b95a'
SOURCE_SESSION='199b66c8c683449bb177a6a9c3beb3ac'
SOURCE_DRIVER_SHA='7045e1f497f03160d8e86813cbef47c6d78b7192394277b44e66ef7fa653e023'
SOURCE_CAPTURE_SHA='b6329fefe198929cca45a684175badb18e90a3eeaa4023a6724c3a4517b91ae3'
READS=[('reg',i) for i in (0,4,8,20,24,192,196,200,224,228,232,236,240,244,248,252)]+[('dma',i) for i in (0,4,48,52)]
LOCK=threading.RLock()
PINNED=[]
def sha_file(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
    return h.hexdigest()
def current_kernel():
    from ipykernel.connect import get_connection_file
    return Path(get_connection_file()).name
def owner_snapshot(service,c,*,cpu_fixture=False):
    require(service is not None and service.config.get('run_id')==SOURCE_RUN,'ONLY_COMPLETED_C708_OWNER')
    d=service.driver
    require(d.server_session==SOURCE_SESSION and service.state=='BOARD_COMPLETE','SOURCE_SESSION_OR_STATE')
    require(d.requests==d.commits==485 and d.pending is None and not d.poisoned and service.error is None,'SOURCE_NOT_SUCCESSFUL_485')
    require(service.neural_thread is not None and not service.neural_thread.is_alive() and service.listener is None and service.connection is None,'SOURCE_STILL_NEURAL_ACTIVE')
    require(d.evidence.journal.closed and not getattr(d,'_camera_ready_claim',None),'SOURCE_NOT_CLOSED_OR_ALREADY_CLAIMED')
    if not cpu_fixture:
        require(type(d).__name__=='Full485Driver' and type(d).__module__=='a3latency485.driver','SOURCE_NOT_EXACT_LATENCY485_DRIVER')
        require(sha_file(inspect.getfile(type(d)))==SOURCE_DRIVER_SHA,'SOURCE_DRIVER_FILE_CHANGED')
    require(d.boot_id==c['boot_id'],'SOURCE_BOOT_CHANGED')
    require(d.src.nbytes==INPUT_BYTES and d.dst.nbytes==WORD_BYTES and not getattr(d.src,'freed',False) and not getattr(d.dst,'freed',False),'RETAINED_BUFFERS_MISSING')
    require(int(d.src.device_address)==c['retained_src_address'] and int(d.dst.device_address)==c['retained_dst_address'],'RETAINED_BUFFER_ADDRESSES_CHANGED')
    src,dst=int(d.src.device_address),int(d.dst.device_address)
    require(src>0 and dst>0 and src%64==dst%64==0 and src+INPUT_BYTES<=1<<32 and dst+WORD_BYTES<=1<<32
            and (src+INPUT_BYTES<=dst or dst+WORD_BYTES<=src),'RETAINED_BUFFER_RANGE_OR_OVERLAP')
    require(not hasattr(d.reg,'inner') and not hasattr(d.dma,'inner') and d.overlay.is_loaded(),'SOURCE_MMIO_OR_LOADED_IDENTITY')
    if not cpu_fixture:
        from .protocol import BIT_SHA,HWH_SHA
        bit=Path(d.overlay.bitfile_name)
        require(sha_file(bit)==BIT_SHA and sha_file(bit.with_suffix('.hwh'))==HWH_SHA,'SOURCE_IMAGE_FILES_CHANGED')
    capture=Path(d.evidence.journal.path);digest=sha_file(capture)
    expected=c.get('CPU_source_capture_sha256') if cpu_fixture else SOURCE_CAPTURE_SHA
    require(digest==expected,'SOURCE_COMPLETED_CAPTURE_CHANGED')
    r=JournalReader(capture)
    require(r.terminal['status']=='CAPTURE_COMPLETE_NOT_HARDWARE_ADMISSION' and r.terminal['requests']==r.terminal['acks']==485,'SOURCE_CAPTURE_NOT_COMPLETE')
    events=[json.loads(line) for line in r.read('events.jsonl').splitlines()]
    require(events[-1]['event']=='BOARD_COMPLETE','SOURCE_COMPLETION_EVENT')
    require(all(sum(row['event']==e for row in events)==485 for e in ('DMA_LAUNCH_RETURNED','CANDIDATE_READY','RELEASE_CONFIRMED','ACK_SENT')),'SOURCE_CAPTURE_EVENT_COUNTS')
    if service.thread and service.thread.is_alive():
        require(c['control_port']!=service.http.server_port,'ORIGINAL_HTTP_PORT_STILL_IN_USE')
    return dict(source_run=SOURCE_RUN,source_session=SOURCE_SESSION,source_capture_sha256=digest,
        old_HTTP_policy='KEEP_COMPLETED_SERVICE_UNCHANGED_ON_SEPARATE_PORT',old_driver_requests=485,old_driver_commits=485)

class PreparedRetained:
    def init__(self,driver,evidence,config,scope,guard,receipt,old_service):
        self.driver,self.evidence,self.config,self.scope_bytes=driver,evidence,config,scope
        self.clock_guard,self.receipt,self.old_service=guard,receipt,old_service;self.service=None;self.bind_attempted=False
    def bind_service(self,*,cpu_factories=None):
        require(not self.bind_attempted,'SERVICE_BIND_ALREADY_CONSUMED');self.bind_attempted=True
        self.clock_guard.check(self.config)
        from .service import CameraBoardService
        cpu=self.config.get('test_fixture') is True
        require(cpu or cpu_factories is None,'LIVE_FACTORIES_NOT_ALLOWED')
        kw=cpu_factories or {}
        self.service=CameraBoardService(self.driver,self.evidence,self.config,host=self.config['bind_host'],control_port=self.config['control_port'],
            neural_port=self.config['neural_port'],peer=self.config['pc_host'],cpu_fixture=cpu,scope_bytes=self.scope_bytes,
            preparation_receipt=self.receipt,clock_guard=self.clock_guard,**kw)
        PINNED.append(self.service)
        return self.service  # Caller must explicitly start once; never auto-start.

def prepare_retained(root,source_service,config,scope_bytes,plan_bytes,clock_guard,*,cpu_fixture=False,kernel=None,boot=None):
    validate_scope_binding(config,scope_bytes,cpu_fixture=cpu_fixture,clock=clock_guard)
    require(isinstance(plan_bytes,bytes) and hashlib.sha256(plan_bytes).hexdigest()==config['plan_sha256'],'EXACT_PLAN_BYTES_REQUIRED')
    plan=json.loads(plan_bytes.decode('utf-8'))
    require(all(plan.get(k)==config.get(k) for k in ('run_id','server_session','boot_id','max_steps','new_loads','new_resets','new_allocations',
        'kernel_file','retained_src_address','retained_dst_address','control_port','neural_port','pc_host','bind_host')),'PLAN_BINDING')
    require(plan.get('operation')=='RETAIN_C708_READ20_NEW_CAMERA_SERVICE','PLAN_OPERATION')
    require(plan.get('source_run')==SOURCE_RUN and plan.get('source_capture_sha256')==SOURCE_CAPTURE_SHA
            and plan.get('read_set')==[dict(bank=b,offset=o) for b,o in READS],'PLAN_SOURCE_AND_READ_SET')
    require(cpu_fixture==bool(config.get('test_fixture')),'PREPARATION_MODE')
    require(cpu_fixture or (kernel is None and boot is None),'LIVE_PROVIDER_OVERRIDE_FORBIDDEN')
    kernel=kernel or current_kernel;boot=boot or boot_id
    require(boot()==config['boot_id'] and kernel()==config['kernel_file'],'CURRENT_BOOT_OR_KERNEL_CHANGED')
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=True)
    with LOCK:
        snapshot=owner_snapshot(source_service,config,cpu_fixture=cpu_fixture);old=source_service.driver
        claim=dict(run_id=config['run_id'],server_session=config['server_session'],scope_sha256=config['scope_sha256'],plan_sha256=config['plan_sha256'])
        clock_guard.check(config)
        with (root/'RETAINED_OWNER_CLAIM.json').open('x',encoding='utf-8') as f:
            json.dump(claim,f);f.flush()
            import os
            os.fsync(f.fileno())
        old._camera_ready_claim=dict(claim) # Consumed even if subsequent prepare fails.
        evidence=Evidence(root/'ps',config);d=Full485Driver.__new__(Full485Driver)
        for name in ('overlay','src','dst','reg','dma','np','boot_id'):setattr(d,name,getattr(old,name))
        d.evidence=evidence;d.plan=config;d.clock_guard=clock_guard;d.server_session=config['server_session'];d.last_registers={}
        d.requests=d.commits=0;d.pending=None;d.committed={};d.poisoned=False;d.bound_asid=None;d.compute_deadline=None
        d.session_deadline=time.monotonic()+clock_guard.remaining_s(config)
        PINNED.extend((source_service,old,d,evidence))
        try:
            evidence.event('RETAINED_C708_OWNER_CLAIMED',**claim,**snapshot)
            rows=[]
            for bank,offset in READS:
                clock_guard.check(config);require(boot()==config['boot_id'],'BOOT_CHANGED_DURING_PREPARATION')
                rows.append(dict(bank=bank,offset=offset,value=d._read(bank,offset)))
            receipt={k:config[k] for k in ('run_id','server_session','boot_id','plan_sha256','scope_sha256','listener_id','bit_sha256','hwh_sha256','initial_full_sha256','initial_H_sha256','mapping_sha256')}
            receipt.update(requests=0,commits=0,pending=False,poisoned=False,old_receiver_stopped=True,new_loads=0,new_resets=0,new_allocations=0,
                kernel_id=config['kernel_file'],src_bytes=d.src.nbytes,dst_bytes=d.dst.nbytes,src_address=int(d.src.device_address),dst_address=int(d.dst.device_address),reads=rows)
            validate_readonly_receipt(config,receipt);clock_guard.check(config)
            evidence.journal.add('CLOCK_PROOF.json',json.dumps(clock_guard.receipt(config),sort_keys=True).encode())
            evidence.journal.add('PREPARATION_RECEIPT.json',json.dumps(receipt,sort_keys=True).encode());evidence.journal.checkpoint('RETAINED_PREPARED_READ20')
            return PreparedRetained(d,evidence,config,scope_bytes,clock_guard,receipt,source_service)
        except BaseException as exc:
            d.poisoned=True
            try:evidence.event('PREPARATION_FAILED_NO_RETRY',error=repr(exc));evidence.close()
            except BaseException:evidence.journal.abandon()
            raise # Old service state, evidence and buffers remain untouched.

"""Explicit cold initialization adapter. No board operations on import.

Initialization is a separate, user-executed zero-STEP operation (1 load, 1 DMA
initialization reset, 2 buffers). The camera execution scope still permits no
initialization. Original Full485Driver run/finish and CameraBoardService remain
unchanged. Fresh counter/DMA validation is explicitly separate from retained
post-transfer validation; raw register observations are never synthesized.
"""
import hashlib,importlib,json,os,shutil,socket,sys,time,types
from pathlib import Path

MODE='MANUAL_FRESH_INIT_THEN_READ20/v1'
PINNED=[]

def require(v,message):
    if not v:raise ValueError(message)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def current():
    from ipykernel.connect import get_connection_file
    return (Path('/proc/sys/kernel/random/boot_id').read_text().strip(),Path(get_connection_file()).name)

def environment(config):
    require(current()==(config['boot_id'],config['kernel_file']),'FRESH_BOOT_OR_KERNEL_CHANGED')
    require(sys.executable=='/usr/local/share/pynq-venv/bin/python3' and os.geteuid()==0,'FRESH_PYNQ_KERNEL_ROOT')
    require(Path('/usr/lib/libxrt_core.so').is_file(),'FRESH_XRT_LIBRARY')
    owners=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:args=(p/'cmdline').read_bytes().split(b'\0')
        except OSError:continue
        if any(b'ipykernel_launcher' in a for a in args):owners.append(int(p.name))
    require(owners==[os.getpid()],'FRESH_OTHER_NOTEBOOK_KERNEL_ACTIVE')
    for port in (5768,5790):
        with socket.socket() as probe:probe.bind(('0.0.0.0',port))

def read_receipt(config,receipt,wire):
    """Raw fresh-initial-state evidence, not a post-transfer Idle-bit check."""
    for k in ('run_id','server_session','boot_id','plan_sha256','scope_sha256','listener_id','bit_sha256','hwh_sha256','initial_full_sha256','initial_H_sha256','mapping_sha256'):
        require(receipt.get(k)==config.get(k),'FRESH_RECEIPT_'+k)
    require(receipt.get('requests')==receipt.get('commits')==0 and receipt.get('pending') is False
        and receipt.get('poisoned') is False and receipt.get('old_receiver_stopped') is True,'FRESH_RECEIPT_NOT_CLEAN')
    require(receipt.get('new_loads')==receipt.get('new_resets')==receipt.get('new_allocations')==0,'FRESH_READ_PHASE_CANNOT_INITIALIZE')
    require(receipt.get('kernel_id') and receipt.get('src_bytes')==69216 and receipt.get('dst_bytes')==23072,'FRESH_RECEIPT_BUFFER_SIZE')
    src,dst=receipt.get('src_address'),receipt.get('dst_address')
    require(type(src) is int and type(dst) is int and min(src,dst)>0 and src%64==dst%64==0
        and src+69216<=1<<32 and dst+23072<=1<<32 and (src+69216<=dst or dst+23072<=src),'FRESH_RECEIPT_BUFFER_RANGE')
    offsets=[('reg',i) for i in (0,4,8,20,24,192,196,200,224,228,232,236,240,244,248,252)]+[('dma',i) for i in (0,4,48,52)]
    rows=receipt.get('reads',[])
    require(len(rows)==20 and [(r.get('bank'),r.get('offset')) for r in rows]==offsets,'FRESH_READ_SET')
    require(all(type(r.get('value')) is int and 0<=r['value']<=0xffffffff for r in rows),'FRESH_READ_WORD')
    values={(r['bank'],r['offset']):r['value'] for r in rows}
    # A3R1 RTL reset branch clears received_words/sent_words/result_cycles.
    require(tuple(values['reg',i] for i in (0,4,8,20,24,192,196,200))==(0x33415646,1,5768,0,0,0,0,0),'FRESH_CORE_NOT_INITIAL_IDLE')
    require(b''.join(values['reg',i].to_bytes(4,'big') for i in range(224,256,4))==wire.CONFIG,'FRESH_CORE_CONFIG')
    require(all(values['dma',i]&1 and not values['dma',i]&4 for i in (0,48)),'FRESH_DMA_CONTROL')
    # Accepted line7 fresh-DMA fix: Idle may be 0 before the first transfer;
    # require direct-register mode, nonhalted/no error. No status is rewritten.
    require(all(not values['dma',i]&0x779 for i in (4,52)),'FRESH_DMA_HALTED_ERROR_OR_WRONG_MODE')
    proof=receipt.get('fresh_initialized_parent',{})
    require(proof==config.get('fresh_initialized_parent') and proof.get('mode')==MODE,'FRESH_INITIALIZATION_PARENT')
    return receipt

def initialize(root,config,package,*,cpu=False,constructor=None,environment_check=None):
    """Only the human's initialization cell calls this. No listener or STEP."""
    root=Path(root);plan=json.loads((root/'INIT_PLAN.json').read_text(encoding='utf8'))
    require(sha(root/'INIT_PLAN.json')==config['plan_sha256'] and plan==config['plan'],'FRESH_EXACT_INIT_PLAN')
    require(config.get('mode')==MODE and plan['max_steps']==0 and plan['automatic_retry'] is False
        and (plan['new_loads'],plan['new_resets'],plan['new_allocations'])==(1,1,2),'FRESH_INIT_SCOPE')
    require(all(plan[k]==config[k] for k in ('boot_id','kernel_file')),'FRESH_INIT_PLAN_BINDING')
    require(bool(config.get('test_fixture'))==cpu and config['execution_authority']==('CPU_FIXTURE_ONLY' if cpu else 'HUMAN_MANUAL_CELL_ONLY'),'FRESH_INIT_AUTHORITY')
    require(not PINNED and not (root/'INITIALIZATION_ATTEMPT.json').exists(),'FRESH_INIT_ALREADY_ATTEMPTED')
    if not cpu:require(constructor is environment_check is None,'FRESH_LIVE_OVERRIDE_FORBIDDEN')
    (environment_check or environment)(config)
    helper=lambda n:importlib.import_module(package.__name__+'.'+n)
    wire=helper('protocol');bs=helper('board_service')
    require(config['bit_sha256']==wire.BIT_SHA and config['hwh_sha256']==wire.HWH_SHA,'FRESH_EXACT_IMAGE')
    if not cpu:bs.verify_image(config['bit_path'])
    require(shutil.disk_usage(root).free>=256*1024*1024,'FRESH_DISK_SPACE')
    with (root/'INITIALIZATION_ATTEMPT.json').open('x',encoding='utf8') as f:
        json.dump(plan,f);f.flush();os.fsync(f.fileno())
    evidence=helper('light_evidence').Evidence(root/'init_ps',dict(config,max_steps=0))
    d=helper('driver').Full485Driver.__new__(helper('driver').Full485Driver)
    PINNED.extend((d,evidence));bs.PINNED_DRIVERS.append(d)
    try:
        evidence.event('MANUAL_FRESH_INITIALIZATION_APPROVED',**plan)
        os.environ['XILINX_XRT']='/usr'
        (constructor or bs.PLDriver.init__)(d,config['bit_path'],authorize_load=True,evidence=evidence)
        require(d.boot_id==config['boot_id'] and d.requests==d.commits==0 and d.pending is None and not d.poisoned,'FRESH_INITIALIZED_STATE')
        receipt=dict(mode=MODE,initialization_run_id=config['run_id'],boot_id=config['boot_id'],kernel_file=config['kernel_file'],
            initialization_plan_sha256=config['plan_sha256'],bit_sha256=wire.BIT_SHA,hwh_sha256=wire.HWH_SHA,
            src_address=int(d.src.device_address),dst_address=int(d.dst.device_address),src_bytes=d.src.nbytes,dst_bytes=d.dst.nbytes,
            new_loads=1,new_resets=1,new_allocations=2,requests=0,commits=0,neural_listeners_started=0)
        require(receipt['src_bytes']==69216 and receipt['dst_bytes']==23072,'FRESH_BUFFER_SIZES')
        evidence.journal.add('INITIALIZATION_RECEIPT.json',json.dumps(receipt,sort_keys=True).encode())
        evidence.event('INITIALIZATION_COMPLETE_NO_NEURAL_RUN',run_id=config['run_id'])
        evidence.journal.close('INITIALIZATION_ONLY_NOT_NEURAL_RUN',requests=0,acks=0,source_closed=True)
        receipt['initialization_capture_sha256']=sha(evidence.journal.path)
        owner=types.SimpleNamespace(driver=d,config=config,receipt=receipt,package=package,consumed=False)
        PINNED.append(owner);return owner
    except BaseException:
        d.poisoned=True
        try:evidence.close()
        except BaseException:evidence.journal.abandon()
        raise

def prepare(root,owner,config,scope_bytes,plan_bytes,clock,package,*,cpu=False):
    helper=lambda n:importlib.import_module(package.__name__+'.'+n)
    binding=helper('binding');p=helper('prepare');wire=helper('protocol')
    binding.validate_scope_binding(config,scope_bytes,cpu_fixture=cpu,clock=clock)
    plan=json.loads(plan_bytes);expected=config['fresh_initialized_parent']
    require(sha_bytes(plan_bytes)==config['plan_sha256'] and plan.get('operation')=='FRESH_INITIALIZED_OWNER_READ20'
        and plan.get('fresh_initialized_parent')==expected,'FRESH_CAMERA_PLAN')
    require(all(plan[k]==config[k] for k in ('run_id','server_session','boot_id','max_steps','new_loads','new_resets','new_allocations',
        'kernel_file','retained_src_address','retained_dst_address','control_port','neural_port','pc_host','bind_host')),'FRESH_CAMERA_PLAN_BINDING')
    require(cpu==bool(config.get('test_fixture'))==bool(owner.config.get('test_fixture')),'FRESH_CAMERA_SOURCE_MODE')
    require(owner.config['plan_sha256']==expected['initialization_plan_sha256'],'FRESH_INITIALIZATION_PLAN_CHANGED')
    require(expected==owner.receipt and expected['mode']==MODE and owner.consumed is False,'FRESH_CAMERA_SOURCE_IDENTITY')
    old=owner.driver
    require(old.boot_id==config['boot_id']==expected['boot_id'] and config['kernel_file']==expected['kernel_file'],'FRESH_CAMERA_BOOT_KERNEL')
    require(old.requests==old.commits==0 and old.pending is None and not old.poisoned and not old.committed,'FRESH_CAMERA_SOURCE_USED')
    require(old.evidence.journal.closed and sha(old.evidence.journal.path)==expected['initialization_capture_sha256'],'FRESH_INIT_CAPTURE_CHANGED')
    if not cpu:
        import inspect
        require(current()==(config['boot_id'],config['kernel_file']),'FRESH_CURRENT_BOOT_KERNEL')
        require(sha(inspect.getfile(type(old)))==sha(Path(package.__file__).parent/'driver.py'),'FRESH_ORIGINAL_DRIVER_SOURCE')
        require(old.overlay.is_loaded(),'FRESH_IMAGE_NOT_LOADED')
        helper('board_service').verify_image(old.overlay.bitfile_name)
    require(int(old.src.device_address)==config['retained_src_address']==expected['src_address']
        and int(old.dst.device_address)==config['retained_dst_address']==expected['dst_address'],'FRESH_SOURCE_BUFFER_ADDRESS')
    root=Path(root);root.mkdir(parents=True,exist_ok=False)
    with (root/'FRESH_OWNER_CLAIM.json').open('x',encoding='utf8') as f:
        json.dump(dict(run_id=config['run_id'],scope_sha256=config['scope_sha256'],parent=expected),f);f.flush();os.fsync(f.fileno())
    owner.consumed=True
    evidence=helper('light_evidence').Evidence(root/'ps',config)
    d=helper('driver').Full485Driver.__new__(helper('driver').Full485Driver)
    for key in ('overlay','src','dst','reg','dma','np','boot_id'):setattr(d,key,getattr(old,key))
    d.evidence=evidence;d.plan=config;d.clock_guard=clock;d.server_session=config['server_session'];d.last_registers={}
    d.requests=d.commits=0;d.pending=None;d.committed={};d.poisoned=False;d.bound_asid=None;d.compute_deadline=None
    d.session_deadline=time.monotonic()+clock.remaining_s(config);PINNED.extend((owner,d,evidence))
    try:
        rows=[]
        for bank,offset in p.READS:
            clock.check(config)
            if not cpu:require(current()==(config['boot_id'],config['kernel_file']),'FRESH_BOOT_DURING_READ')
            rows.append(dict(bank=bank,offset=offset,value=d._read(bank,offset)))
        receipt={k:config[k] for k in ('run_id','server_session','boot_id','plan_sha256','scope_sha256','listener_id','bit_sha256','hwh_sha256','initial_full_sha256','initial_H_sha256','mapping_sha256')}
        receipt.update(requests=0,commits=0,pending=False,poisoned=False,old_receiver_stopped=True,new_loads=0,new_resets=0,new_allocations=0,
            kernel_id=config['kernel_file'],src_bytes=d.src.nbytes,dst_bytes=d.dst.nbytes,src_address=int(d.src.device_address),dst_address=int(d.dst.device_address),
            reads=rows,fresh_initialized_parent=expected)
        read_receipt(config,receipt,wire)
        evidence.journal.add('PARENT_INITIALIZATION_CAPTURE.fvej',old.evidence.journal.path.read_bytes())
        evidence.journal.add('CLOCK_PROOF.json',json.dumps(clock.receipt(config),sort_keys=True).encode())
        evidence.journal.add('PREPARATION_RECEIPT.json',json.dumps(receipt,sort_keys=True).encode());evidence.journal.checkpoint('FRESH_INITIALIZED_READ20')
        # Only this new SHA-pinned namespace gets the fresh-zero validator;
        # retained services and all on-disk frozen source bytes stay unchanged.
        binding.validate_readonly_receipt=lambda c,r:read_receipt(c,r,wire)
        return p.PreparedRetained(d,evidence,config,scope_bytes,clock,receipt,owner)
    except BaseException:
        d.poisoned=True
        try:evidence.close()
        except BaseException:evidence.journal.abandon()
        raise

def sha_bytes(raw):return hashlib.sha256(raw).hexdigest()

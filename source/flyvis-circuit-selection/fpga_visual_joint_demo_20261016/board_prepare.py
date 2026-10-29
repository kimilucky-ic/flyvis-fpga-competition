"""Fresh owned run from a completed healthy retained A3R1 session; no init."""
import hashlib, inspect, json, os, shutil, socket, time
from pathlib import Path
from .driver import Full485Driver
from .light_evidence import Evidence
from .evidence import save_json
from .manual_transport import ManualBoardService
from .neural_session import neural_session
from .control2 import require, BIT_SHA, HWH_SHA
from . import protocol as w
PINNED=[]

def owner_check(old_service,c):
    require(old_service.config['run_id']==c['source_run'] and old_service.driver.server_session==c['source_session'],'SOURCE_IDENTITY')
    old=old_service.driver
    require(old_service.state=='BOARD_COMPLETE' and old.requests==old.commits==c['source_requests'],'SOURCE_NOT_COMPLETE')
    require(old.pending is None and not old.poisoned,'SOURCE_UNSAFE')
    require(old_service.neural_thread and not old_service.neural_thread.is_alive(),'SOURCE_RUNNING')
    require(not getattr(old,'_line4_claimed',False),'ALREADY_CLAIMED')
    require(old.boot_id==c['expected_boot_id'],'SOURCE_BOOT')
    require(old.src.nbytes==w.INPUT_BYTES and old.dst.nbytes==w.WORD_BYTES,'CMA_SHAPE')
    require(not getattr(old.src,'freed',False) and not getattr(old.dst,'freed',False),'CMA_FREED')
    src,dst=int(old.src.device_address),int(old.dst.device_address)
    require(src%64==dst%64==0 and src+w.INPUT_BYTES<2**32 and dst+w.WORD_BYTES<2**32 and (src+w.INPUT_BYTES<=dst or dst+w.WORD_BYTES<=src),'CMA_ADDRESS')
    return old

def prepare(root,old_service,exact_sha):
    root=Path(root);c=json.loads((root/'PLAN.json').read_text(encoding='utf-8'))
    require(hashlib.sha256((root/'PLAN.json').read_bytes()).hexdigest()==exact_sha,'PLAN_IDENTITY')
    manifest=json.loads((root/'BOARD_MANIFEST.json').read_text(encoding='utf-8'))
    for name,digest in manifest.items():require(hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,'SOURCE_CHANGED_'+name)
    require(c['max_requests']==c['max_commits']==1000 and not c['automatic_retry'],'BOUNDED_SCOPE')
    require(c['new_loads']==c['new_resets']==c['new_allocations']==c['new_kernels']==0,'NO_INIT')
    from ipykernel.connect import get_connection_file
    require(Path(get_connection_file()).name=='kernel-'+c['kernel_id']+'.json','KERNEL_CHANGED')
    require(Path('/proc/sys/kernel/random/boot_id').read_text().strip()==c['expected_boot_id'],'BOOT_CHANGED')
    require(not PINNED and not (root/'ATTEMPT.json').exists(),'ONE_ATTEMPT')
    old=owner_check(old_service,c)
    require(old.overlay.is_loaded(),'LOADED_IMAGE_CHANGED')
    bit=Path(old.overlay.bitfile_name)
    require(hashlib.sha256(bit.read_bytes()).hexdigest()==BIT_SHA and hashlib.sha256(bit.with_suffix('.hwh').read_bytes()).hexdigest()==HWH_SHA,'IMAGE_FILES')
    require(os.geteuid()==0 and shutil.disk_usage(root).free>=768*1024**2,'BOARD_DISK')
    for port in (c['control_port'],c['neural_port']):
        with socket.socket() as probe:probe.bind(('0.0.0.0',port))
    (root/'ATTEMPT.json').write_text(json.dumps(dict(run_id=c['run_id'],plan_sha256=exact_sha)),encoding='utf-8')
    old._line4_claimed=True
    config=dict(c,plan_sha256=exact_sha)
    evidence=Evidence(root/('board_evidence_'+c['run_id']),config)
    driver=Full485Driver.__new__(Full485Driver)
    for name in ('overlay','reg','dma','src','dst','np','boot_id'):setattr(driver,name,getattr(old,name))
    driver.evidence=evidence;driver.server_session=c['server_session'];driver.plan=config
    driver.pending=None;driver.committed={};driver.poisoned=False;driver.last_registers={}
    driver.requests=driver.commits=0;driver.bound_asid=None;driver.compute_deadline=None
    driver.session_deadline=time.monotonic()+900
    PINNED.extend([old_service,driver,evidence])
    try:
        evidence.event('LINE4_RETAINED_HANDOFF',run_id=c['run_id'],source_run=c['source_run'],source_commits=old.commits,new_loads=0,new_resets=0,new_allocations=0)
        core={i:driver._read('reg',i) for i in c['preparation_MMIO_reads']['core_offsets']}
        dma={i:driver._read('dma',i) for i in c['preparation_MMIO_reads']['dma_offsets']}
        require(tuple(core[i] for i in (0,4,8,20,24))==(0x33415646,1,5768,0,0),'CORE_NOT_CLEAN')
        require(b''.join(core[i].to_bytes(4,'big') for i in range(224,256,4))==w.CONFIG,'CONFIG_CHANGED')
        require(all(dma[i]&1 and not dma[i]&4 for i in (0,48)),'DMA_CONTROL')
        require(all(dma[i]&2 and not dma[i]&0x771 for i in (4,52)),'DMA_STATUS')
        save_json(evidence.directory/'MANUAL_PREPARED.json',dict(run_id=c['run_id'],boot_id=driver.boot_id,
            server_session=c['server_session'],core=core,dma=dma,prep_MMIO_reads=len(core)+len(dma),new_loads=0,new_resets=0,new_allocations=0))
        service=ManualBoardService(driver,evidence,config,neural_session,control_port=c['control_port'],neural_port=c['neural_port'],peer=c['pc_host'],idle_s=900)
        PINNED.append(service);service.start()
        print('LINE4_BOARD_PREPARED',c['run_id'],'1000-step one-shot; NO load/reset/allocation')
        return service
    except BaseException as exc:
        driver.poisoned=True;evidence.event('LINE4_PREPARATION_FAILED',error=repr(exc));evidence.close();raise

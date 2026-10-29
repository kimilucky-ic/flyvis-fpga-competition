"""Validate supplied bytes/receipts only. Never discovers or prepares hardware."""
import hashlib,json
from .contract import validate
from .control2 import require

def validate_scope_binding(config,scope_bytes,*,cpu_fixture=False,clock=None):
    validate(config,cpu_fixture=cpu_fixture,clock=clock)
    require(isinstance(scope_bytes,bytes),'EXACT_SCOPE_BYTES_REQUIRED')
    require(hashlib.sha256(scope_bytes).hexdigest()==config['scope_sha256'],'CAMERA_SCOPE_BYTES_CHANGED')
    scope=json.loads(scope_bytes.decode('utf-8'))
    require(scope.get('schema')=='flyvis-camera-joint-scope/v1','CAMERA_SCOPE_SCHEMA')
    for key in ('run_id','server_session','boot_id','max_steps','max_worker_s','source_kind','condition_id',
                'numerical_profile','input_policy','initial_H_sha256','mapping_sha256','bit_sha256','hwh_sha256',
                'start_utc','end_utc','new_loads','new_resets','new_allocations','automatic_retry'):
        require(scope.get(key)==config.get(key),'CAMERA_SCOPE_BINDING_'+key)
    require(scope.get('initial_full_digest')==config['initial_full_sha256'] and scope.get('dt_s')==.005,'CAMERA_SCOPE_INITIAL_DT')
    require(scope.get('allow_zero_step_cancel',False)==config.get('allow_zero_step_cancel',False),'CAMERA_ZERO_CANCEL_SCOPE')
    if cpu_fixture:require(scope.get('execution_authority')=='CPU_FIXTURE_ONLY','CPU_SCOPE_ONLY')
    else:require(scope.get('execution_authority')=='APPROVED_BY_HUMAN' and scope.get('status')=='APPROVED_BY_HUMAN'
                 and bool(scope.get('human_authorization_reference')),'CAMERA_SCOPE_NOT_APPROVED')
    return scope

def validate_readonly_receipt(config,receipt):
    """Format/consistency check, NOT an attestation that any register was read.

    A future separately approved board preparation must supply current evidence;
    calling this pure function cannot confer PREPARED status or authorization.
    """
    for key in ('run_id','server_session','boot_id','plan_sha256','scope_sha256','listener_id','bit_sha256','hwh_sha256','initial_full_sha256','initial_H_sha256','mapping_sha256'):
        require(receipt.get(key)==config.get(key),'PREPARATION_RECEIPT_'+key)
    require(receipt.get('requests')==receipt.get('commits')==0 and receipt.get('pending') is False
            and receipt.get('poisoned') is False and receipt.get('old_receiver_stopped') is True,'PREPARATION_NOT_CLEAN')
    require(receipt.get('new_loads')==receipt.get('new_resets')==receipt.get('new_allocations')==0,'PREPARATION_INITIALIZATION_FORBIDDEN')
    require(receipt.get('kernel_id') and receipt.get('src_bytes')==69216 and receipt.get('dst_bytes')==23072,'PREPARATION_KERNEL_BUFFERS')
    require(all(type(receipt.get(k)) is int and receipt[k]>0 and receipt[k]%64==0 for k in ('src_address','dst_address'))
            and receipt['src_address']!=receipt['dst_address'],'PREPARATION_BUFFER_ADDRESS')
    src,dst=receipt['src_address'],receipt['dst_address']
    require(src+69216<=1<<32 and dst+23072<=1<<32 and (src+69216<=dst or dst+23072<=src),'PREPARATION_BUFFER_OVERLAP_OR_RANGE')
    rows=receipt.get('reads',[])
    offsets=[('reg',i) for i in (0,4,8,20,24,192,196,200,224,228,232,236,240,244,248,252)]+[('dma',i) for i in (0,4,48,52)]
    require(len(rows)==20 and [(r.get('bank'),r.get('offset')) for r in rows]==offsets,'PREPARATION_READ_SET')
    require(all(type(r.get('value')) is int and 0<=r['value']<=0xffffffff for r in rows),'PREPARATION_WORD')
    values={(r['bank'],r['offset']):r['value'] for r in rows}
    require(tuple(values['reg',i] for i in (0,4,8,20,24,192,196,200))==(0x33415646,1,5768,0,0,17304,5768,57681),'PREPARATION_CORE_NOT_CLEAN')
    from .protocol import CONFIG
    require(b''.join(values['reg',i].to_bytes(4,'big') for i in range(224,256,4))==CONFIG,'PREPARATION_CONFIG')
    require(all(values['dma',i]&1 and not values['dma',i]&4 for i in (0,48)),'PREPARATION_DMA_CONTROL')
    require(all(values['dma',i]&2 and not values['dma',i]&0x771 for i in (4,52)),'PREPARATION_DMA_NOT_IDLE')
    return dict(status='PASS_RECEIPT_FORMAT_ONLY_NOT_BOARD_VALIDATION',execution_authority='NONE',reads_checked=20)

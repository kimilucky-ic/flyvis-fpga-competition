"""Fixed human-run notebook entry. Python 3.8; no device work on import.

The notebook carries a private installation key once, not an expired run key.
All neuron computation and preparation use the existing pinned implementation.
"""
import hashlib,hmac,json,os,socket,time,urllib.error,urllib.request,uuid
from pathlib import Path

def require(ok,message):
    if not ok:raise ValueError(message)

def signature(body,key):
    return hmac.new(bytes.fromhex(key),json.dumps(body,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()

def inventory(namespace,bit_path):
    from ipykernel.connect import get_connection_file
    from pynq import Device
    owners=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:args=(p/'cmdline').read_bytes().split(b'\0')
        except OSError:continue
        if any(b'ipykernel_launcher' in a for a in args):owners.append(int(p.name))
    extra=sorted(pid for pid in owners if pid!=os.getpid())
    require(not extra,'其他Notebook内核仍在运行，PID='+str(extra)+'；请确认其任务结束后在Running正常关闭。本程序不会关闭它们。')
    files={}
    for path in (Path(bit_path),Path(bit_path).with_suffix('.hwh')):
        require(path.is_file(),'固件文件缺失：'+str(path))
        files[path.suffix]=hashlib.sha256(path.read_bytes()).hexdigest()
    service=namespace.get('camera3_service_instance')
    other=[name for name,v in list(namespace.items()) if name.endswith('_service_instance') and hasattr(v,'driver') and v is not service]
    require(not other,'当前内核还有其他板端服务：'+str(other)+'；停止准备，不接管。')
    value=dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
        kernel_file=Path(get_connection_file()).name,pid=os.getpid(),bit_path=str(bit_path),
        bit_sha256=files['.bit'],hwh_sha256=files['.hwh'],
        loaded_bitfile_metadata=str(getattr(Device.active_device,'bitfile_name',None)),existing_run=None)
    if service is not None:
        d=service.driver
        require(service.error is None and not d.poisoned and d.pending is None and not service.inflight,
            '上一轮异常或提交状态不确定；保留现场，不重新初始化。')
        require(service.state in ('BOARD_PREPARED','FINISHED_PENDING_AUDIT'),'已有实验尚未结束，请回实验台正常停止。')
        value['existing_run']={k:service.config[k] for k in ('run_id','scope_sha256','boot_id')}
    else:
        require('line2_fresh_initialized' not in namespace,'初始化对象已存在但服务不完整；保留现场，不重复加载。')
        for port in (5768,5790):
            with socket.socket() as probe:
                try:probe.bind(('0.0.0.0',port))
                except OSError:raise ValueError('板端端口'+str(port)+'被占用；不会抢占或复位。')
    return value

def run(namespace,config,*,ask=input,inspect=None,open_url=None):
    inv=(inspect or inventory)(namespace,config['bit_path'])
    approved=False
    if inv['existing_run'] is None:
        print('当前固件：'+inv['loaded_bitfile_metadata'])
        answer=ask('确认板卡已交回，允许本次加载⑦A3R1一次、DMA初始化复位一次、分配两个缓冲区？输入“准备”继续：')
        require(answer.strip()=='准备','已取消；未加载、未复位、未分配。')
        approved=True
    body=dict(schema='flyvis-fixed-notebook-request/v1',installation_id=config['installation_id'],
        nonce=uuid.uuid4().hex,inventory=inv,initialize_approved=approved)
    packet=dict(body=body,mac=signature(body,config['key']))
    req=urllib.request.Request(config['pc_url']+'/fixed-entry',data=json.dumps(packet).encode(),headers={'Content-Type':'application/json'})
    try:
        with (open_url or urllib.request.urlopen)(req,timeout=30) as reply:raw=reply.read(2_500_001)
    except urllib.error.HTTPError as error:
        try:detail=json.loads(error.read(4097)).get('error','准备被拒绝')
        except (ValueError,AttributeError):detail='准备被拒绝'
        raise RuntimeError('电脑拒绝准备：'+str(detail)+'。未执行电脑返回的准备代码。') from error
    except OSError as error:
        raise RuntimeError('电脑实验台未就绪或拒绝准备。先双击“打开FlyVis实验台”，查看页面原因；板端不自动重试。') from error
    require(len(raw)<=2_500_000,'准备响应过大；停止')
    response=json.loads(raw);b=response['body']
    require(hmac.compare_digest(signature(b,config['key']),response['mac'])
        and b['nonce']==body['nonce'] and b['inventory']==inv,'准备响应身份不匹配；停止')
    if b['status']=='ALREADY_PREPARED':
        print('板端已准备，无需重复加载。回FlyVis实验台点“开始”。');return
    require(b['status']=='PREPARE' and hashlib.sha256(b['source'].encode()).hexdigest()==b['source_sha256'],'准备代码校验失败')
    if 'line2_fixed_attempt' in namespace:
        service=namespace.get('camera3_service_instance')
        require(inv['existing_run'] is not None and service is not None and service.state=='FINISHED_PENDING_AUDIT',
            '本内核已有未完成准备；保留现场，不重复执行。')
    prior=namespace.get('camera_repeat_handle')
    if prior is not None and not prior.get('stopped'):
        require(inv['existing_run'] is not None,'已有重复准备线程；停止')
        prior['stop_requested'].set();prior['thread'].join(7)
        require(prior['stopped'] and not prior['thread'].is_alive(),'旧准备线程未结束；停止，不重新准备。')
    namespace['line2_fixed_attempt']=body['nonce']
    # Same original zero-STEP initializer/preparer, authenticated by this
    # installation key. No unsigned PC source or old notebook cell is used.
    exec(compile(b['source'],'FLYVIS_FIXED_HUMAN_PREPARATION','exec'),namespace,namespace)
    print('板端准备完成。回FlyVis实验台点“开始”；正常结束并自动核验后可再次开始。')

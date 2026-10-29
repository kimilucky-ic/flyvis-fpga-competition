"""ID-only operator diagnostic. Import is inert. No sensor configuration."""
import collections, hashlib, json, os, platform, shutil, sys, time, uuid
from pathlib import Path
BIT_SHA='781981526e8cc9916c096ff46b92046d90021d56c9438718fe5566cfdf1df7d7'
HWH_SHA='61465634adaa0e421a5b07c77b38e0739fdcfdf8e68e977f25bf2d803b9097ae'
OLD_BOOT='14e5f2cb-f4d0-454e-813d-c371ca86e63b'
FAILED_BOOT='6107d12e-9fb3-4ae9-90cb-22e8c8b2782f'
FAILED_RUN='ID_cd4dcb6069e64c36a4ef76372ee1fcb9'
REVISION='IIC21_R2'
FAILED_RESULT_SHA='c3603f76b07a9a9e24599cb3569a01edaa75f04b5b676123fc30f3d0c62521e6'
SAFE_REGS=[('ISR',0x20),('CR',0x100),('SR',0x104),('TX_OCCUPANCY',0x114),('RX_OCCUPANCY',0x118),('RX_DEPTH',0x120)]
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):
    with Path(path).open('x',encoding='utf-8') as f:
        json.dump(value,f,indent=2,ensure_ascii=False);f.flush();os.fsync(f.fileno())

class TraceIO:
    # No disk I/O during timed transactions. Keep bounded first/last calls.
    def init__(self,mmio,clock=time.monotonic_ns):
        self.mmio,self.clock=mmio,clock
        self.phase='PRECHECK';self.sensor_register=None
        self.first=[];self.tail=collections.deque(maxlen=64);self.events=[]
        self.last_reads={};self.counts={'read':0,'write':0};self.max_call_ns=0
    def access(self,op,address,value=None):
        before=self.clock()
        e=dict(op=op,offset=hex(address),phase=self.phase,sensor_register=self.sensor_register,start_ns=before)
        if value is not None:e['value']=value
        self.counts[op]+=1
        try:
            if op=='read':value=int(self.mmio.read(address));e['value']=value
            else:self.mmio.write(address,value)
            return value
        except BaseException as exc:e['error']=repr(exc);raise
        finally:
            e['end_ns']=self.clock();e['host_call_ns']=e['end_ns']-before
            self.max_call_ns=max(self.max_call_ns,e['host_call_ns'])
            if op=='read':self.last_reads[hex(address)]=dict(e)
            if len(self.first)<64:self.first.append(e)
            self.tail.append(e)
    def read(self,address):return self.access('read',address)
    def write(self,address,value):return self.access('write',address,value)
    def snapshot(self):return {name:self.read(a) for name,a in SAFE_REGS}
    def report(self):
        return dict(counts=self.counts,max_host_call_ns=self.max_call_ns,first_calls=self.first,last_calls=list(self.tail),last_reads=self.last_reads,stages=self.events,
          timing='Host monotonic intervals include Python/scheduling; not isolated AXI latency or a bus waveform',
          failure_snapshot='Last observed reads only; no extra post-failure MMIO')

def read_id(mmio,timeout=.25,clock=time.monotonic,ns=time.monotonic_ns):
    from bounded_io import Iic
    class DiagnosticIic(Iic):
        def _poll(self,condition,read_final=False):
            caller=sys._getframe(1)
            phase='{}:{}'.format(caller.f_code.co_name,caller.f_lineno)
            self.io.phase=phase
            e=dict(phase=phase,sensor_register=self.io.sensor_register,start_ns=ns(),deadline=self.deadline)
            self.io.events.append(e)
            try:return super()._poll(condition,read_final)
            except BaseException as exc:e['error']=repr(exc);raise
            finally:e['end_ns']=ns()
    trace=TraceIO(mmio,ns)
    result=dict(status='ID_READ_NOT_COMPLETED',sensor_configuration_writes=0,camera_starts=0,neural_steps=0,DDR_allocations=0,automatic_retry=False,transaction_timeout_seconds=timeout)
    bus=DiagnosticIic(trace,timeout=timeout,clock=clock)
    try:
        result['before']=trace.snapshot();sr=result['before']['SR']
        if sr&4 or sr&0xc0!=0xc0 or result['before']['ISR']&3:
            raise RuntimeError('IIC not clean/idle; no reset, drain or transaction attempted')
        values={}
        for reg in (0x300b,0x300a):
            trace.sensor_register=hex(reg);values[hex(reg)]=bus.read16(reg);result['id_bytes']=dict(values)
        result['sensor_id']=(values['0x300a']<<8)|values['0x300b']
        if result['sensor_id']!=0x5640:raise RuntimeError('Sensor ID mismatch: '+hex(result['sensor_id']))
        trace.phase='FINAL_STATUS';result['after']=trace.snapshot()
        if result['after']['SR']&4 or result['after']['SR']&0xc0!=0xc0 or result['after']['ISR']&3:
            raise RuntimeError('ID received but final controller not clean/idle')
        result['status']='PASS_OPERATOR_REPORTED_OV5640_ID_ONLY'
    except BaseException as exc:
        result.update(status='STOPPED_ID_DIAGNOSTIC',error=repr(exc),failed_stage=trace.phase,sensor_register=trace.sensor_register)
    result['trace']=trace.report()
    result['transport_revision']=REVISION
    result['bound_limit']='Deadline assumes each MMIO call returns. Cannot interrupt a wedged AXI access; no automatic recovery.'
    return result

def check_clock(regs):
    clk,pll,locked=(regs[k] for k in ('FPGA0_CLK_CTRL','IO_PLL_CTRL','PLL_STATUS'))
    if ((clk>>4)&3,(pll>>12)&127,(clk>>8)&63,(clk>>20)&63)!=(0,30,5,2):raise RuntimeError('Unexpected dividers; no automatic clock changes')
    if pll&0x1b or not locked&4:raise RuntimeError('IO PLL reset/powerdown/bypass/unlocked')
    return 33.333333*30/5/2

def validate_handoff(base,boot):
    # A reviewed failure may be replaced only by this explicit revised run/load.
    # Keep all old reservations/results. Reject any different prior attempt.
    old_marker=base/('ATTEMPT_'+boot+'.json')
    if boot==OLD_BOOT:raise RuntimeError('Unreviewed old boot; stopped before hardware')
    if not old_marker.exists():
        if boot==FAILED_BOOT:raise RuntimeError('Reviewed failure marker missing; no bypass')
        return dict(kind='NEW_BOOT_NO_PRIOR_DIAGNOSTIC')
    marker=json.loads(old_marker.read_text())
    if boot!=FAILED_BOOT or marker.get('boot_id')!=boot or marker.get('run_id')!=FAILED_RUN:
        raise RuntimeError('Different previous attempt; preserve and review before loading')
    if digest(base/FAILED_RUN/'RESULT.json')!=FAILED_RESULT_SHA:
        raise RuntimeError('Prior result bytes differ from reviewed evidence; no load')
    result=json.loads((base/FAILED_RUN/'RESULT.json').read_text())
    diag=result.get('result',{})
    if (result.get('boot_id')!=boot or result.get('run_id')!=FAILED_RUN or
        result.get('bit_sha256')!=BIT_SHA or result.get('hwh_sha256')!=HWH_SHA or
        any(result.get(k)!=0 for k in ('camera_starts','neural_steps','DDR_allocations','sensor_configuration_writes')) or
        diag.get('status')!='STOPPED_ID_DIAGNOSTIC' or diag.get('failed_stage')!='transaction:49' or
        diag.get('sensor_register')!='0x300b' or diag.get('error')!="TimeoutError('late MMIO return')"):
        raise RuntimeError('Prior failure differs from reviewed ID-only case; no load')
    return dict(kind='EXPLICIT_REVISED_RUN_AFTER_REVIEWED_FAILURE',prior_run=FAILED_RUN,
                prior_result_sha256=digest(base/FAILED_RUN/'RESULT.json'))

def reserve(base,boot,run_id):
    handoff=validate_handoff(base,boot)
    save(base/('ATTEMPT_'+REVISION+'_'+boot+'.json'),dict(boot_id=boot,run_id=run_id,revision=REVISION,automatic_retry=False,handoff=handoff))
    return handoff

def run(root,ask=input):
    root=Path(root).resolve()
    for name,sha in [('flyvis_ov5640.bit',BIT_SHA),('flyvis_ov5640.hwh',HWH_SHA)]:
        if digest(root/name)!=sha:raise RuntimeError('Package identity mismatch: '+name)
    if platform.machine()!='armv7l':raise RuntimeError('Run on the confirmed Leader ZYNQ-7020 PYNQ board only')
    boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    if boot==OLD_BOOT:raise RuntimeError('Old boot identity; do not reuse yesterday failed session')
    base=Path('/home/xilinx/jupyter_notebooks/LINE11_OV5640_ID_DIAG');base.mkdir(parents=True,exist_ok=True)
    handoff=validate_handoff(base,boot)
    if (base/('ATTEMPT_'+REVISION+'_'+boot+'.json')).exists():
        raise RuntimeError('R2 already attempted in this boot; preserve results, no retry')
    print('IIC21_R2：仅适用领航者7020 V3.9 + ATK-MC5640，接口未变；请确认没有其他实验/内核操作硬件。')
    print('本次将重新加载同一版BIT/HWH一次，以清除上次未完成的控制器事务。旧结果保留。')
    print('随后只读0x300b/0x300a型号，不写摄像头配置、不采图、不分配DDR、不运行神经STEP。')
    print('实际时钟/电气波形未测量；失败停止，不自动重试、复位或重载。')
    if ask('确认独占板卡并允许本次加载，输入 加载原固件并验证型号：')!='加载原固件并验证型号':
        print('已取消，未访问板端寄存器或加载。');return
    import pynq
    if not str(pynq.__version__).startswith('2.7.'):raise RuntimeError('Expected PYNQ 2.7.x')
    loaded=str(pynq.PL.bitfile_name or '');stamp=str(pynq.PL.timestamp)
    print('当前PYNQ固件记录：',loaded,'时间：',stamp)
    run_id='ID_R2_'+uuid.uuid4().hex;out=base/run_id;out.mkdir()
    if shutil.disk_usage(str(base)).free<16*1024*1024:raise RuntimeError('Insufficient evidence storage; no hardware actions')
    handoff=reserve(base,boot,run_id)
    context=dict(boot_id=boot,run_id=run_id,pynq=pynq.__version__,old_overlay=loaded,old_overlay_timestamp=stamp,bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,
      revision=REVISION,handoff=handoff,actual_program_calls=0,attempted_program_calls=0,automatic_retry=False,evidence='OPERATOR_EXECUTION_NOT_INDEPENDENTLY_ATTESTED',
      physical_clock_measured=False,sensor_configuration_writes=0,camera_starts=0,neural_steps=0,DDR_allocations=0)
    phase='PREPARE';result=None
    try:
        save(out/'INTENT.json',context)
        phase='LOAD';print('LINE11_ID_PHASE',phase,flush=True)
        save(out/'LOAD_INTENT.json',dict(bit_sha256=BIT_SHA,boot_id=boot,revision=REVISION,operator_confirmation='加载原固件并验证型号'))
        overlay=pynq.Overlay(str(root/'flyvis_ov5640.bit'),download=False)
        context['attempted_program_calls']=1;overlay.download();context['actual_program_calls']=1
        phase='CLOCK_AND_RESET';print('LINE11_ID_PHASE',phase,flush=True);slcr=pynq.MMIO(0xf8000000,4096)
        regs={k:int(slcr.read(a)) for k,a in [('FPGA0_CLK_CTRL',0x170),('IO_PLL_CTRL',0x108),('PLL_STATUS',0x10c),('FPGA_RST_CTRL',0x240)]}
        save(out/'CLOCK.json',regs);context['nominal_MHz']=check_clock(regs)
        if regs['FPGA_RST_CTRL']!=0:raise RuntimeError('PL reset asserted; no automatic release')
        phase='IDLE_ABI';print('LINE11_ID_PHASE',phase,flush=True);control=pynq.MMIO(0x43c40000,4096)
        abi={hex(a):int(control.read(a)) for a in (0x30,0x34,0x38,0x3c,0x10,0x14,0x18,0x24)};save(out/'NEURAL_ABI.json',abi)
        if tuple(abi[hex(a)] for a in (0x30,0x34,0x38,0x3c))!=(45669,1513231,0x00110004,188416):raise RuntimeError('Wrong neural ABI; no IIC operations')
        if any(abi[hex(a)] for a in (0x10,0x14,0x18,0x24)):raise RuntimeError('Fresh unused neural controller required; no reset/reload')
        cam=pynq.MMIO(0x41200000,4096);dma=pynq.MMIO(0x43000000,4096)
        idle=dict(camera_run=int(cam.read(0)),camera_status=int(cam.read(8)),vdma_status=int(dma.read(0x34)));save(out/'CAPTURE_IDLE.json',idle)
        if idle['camera_run'] or idle['camera_status']&7 or not idle['vdma_status']&1 or idle['vdma_status']&0xfff0:raise RuntimeError('Capture not clean/stopped; no IIC transaction')
        phase='READ_ID';print('LINE11_ID_PHASE',phase,flush=True);save(out/'READ_ID_INTENT.json',dict(registers=['0x300b','0x300a'],timeout_seconds=.25,no_sensor_configuration=True))
        time.sleep(.020);result=read_id(pynq.MMIO(0x41600000,4096));save(out/'ID_DIAGNOSTIC.json',result)
    except BaseException as exc:result=dict(status='STOPPED_BEFORE_OR_DURING_ID',phase=phase,error=repr(exc))
    finally:
        context['last_phase']=phase;context['result']=result;save(out/'RESULT.json',context)
        archive=shutil.make_archive(str(out)+'_RESULT','zip',str(out))
        print('LINE11_ID_STATUS',result['status'] if result else 'IN_DOUBT')
        if result and 'sensor_id' in result:print('SENSOR_ID',hex(result['sensor_id']))
        if result and 'error' in result:print('STOP_REASON',result['error'])
        print('LINE11_ID_RESULT_ZIP',archive)
        print('请下载ZIP交回核查。不要重复运行、复位或继续单帧实验。')
    return out

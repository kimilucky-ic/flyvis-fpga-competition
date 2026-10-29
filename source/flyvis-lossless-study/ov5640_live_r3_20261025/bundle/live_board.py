"""Bounded operator-owned camera/PL producer, independent of PC display ACKs."""
import json,platform,shutil,time,uuid
import step_profile as prof
from pathlib import Path
from capture_binding import save_json
from official_bridge import OfficialBridge
from cycle_contract import check_cycles
from live_protocol import atomic,canonical,index_from_committed,sha
from live_transport import Uploader,request
_RETAINED={}

class Timings:
    def init__(self):self.values={};self.step_write_ns=None
    def wrap(self,obj,name,label):
        fn=getattr(obj,name)
        def call(*a,**k):
            begin=time.monotonic_ns()
            try:return fn(*a,**k)
            finally:self.values[label]=(time.monotonic_ns()-begin)/1e6
        setattr(obj,name,call)
    def control(self,c):
        old=c._w;pub=c.publication
        def write(a,v):
            if a==0 and v==1:self.step_write_ns=time.monotonic_ns()
            return old(a,v)
        def publication():
            if self.step_write_ns is not None:self.values['step_command_to_completed_check_ms']=(time.monotonic_ns()-self.step_write_ns)/1e6
            return pub()
        c._w=write;c.publication=publication
        self.wrap(c,'advance','input_upload_step_and_publication_ms')

def execute(root,base,config,*,authorized=False,boot_id=None,runtime_factory=None,send=request,upload_wait=60):
    if not authorized or _RETAINED:raise RuntimeError('explicit fresh once-only session required')
    from offline_check import verify
    identity=verify(root);root=Path(root);base=Path(base)
    if not 1<=config['max_steps']<=32:raise ValueError('bounded32 only')
    out=base/('RUN_'+uuid.uuid4().hex);out.mkdir(parents=True,exist_ok=False);(out/'transport').mkdir()
    if shutil.disk_usage(str(out)).free<256*1024*1024:raise RuntimeError('Need256MiB free before hardware')
    if runtime_factory is None:
        from board_runtime import PynqRuntime
        runtime_factory=PynqRuntime
    runtime=runtime_factory(root,out);_RETAINED[out.name]=runtime
    context=dict(revision='LINE11_OFFICIAL_LIVE_R3',run_id=out.name,boot_id=boot_id,identity=identity,
                 evidence=runtime.evidence,session_id=config['session_id'],physical_clock_measured=False,
                 network_controls_neurons=False,max_steps=config['max_steps'])
    save_json(out/'RUN_CONTEXT.json',context)
    uploader=Uploader(out,config,send=send);uploader.start()
    bridge=control=None;phase='PREPARE';completed=0;camera_closed=False;packets=[];failure=None
    def enter(name):
        nonlocal phase
        phase=name;print('LINE11_LIVE_PHASE',name,flush=True)
        save_json(out/('PHASE_'+name+'.json'),dict(monotonic_ns=time.monotonic_ns()))
    try:
        enter('PREPARE');runtime.prepare()
        enter('LOAD');runtime.load()
        enter('CLOCK_HP');runtime.inspect()
        enter('FRESH_ABI');control=runtime.control()
        before={hex(a):control._r(a) for a in (0x10,0x14,0x18,0x24,0x30,0x34,0x38,0x3c)}
        save_json(out/'NEURAL_BEFORE.json',before)
        if any(before[hex(a)] for a in (0x10,0x14,0x18,0x24)):raise RuntimeError('fresh unused neural ABI required')
        enter('ALLOCATE_RESTORE');memory=runtime.memory(slots=config['max_steps']);memory.pin_before_configure()
        save_json(out/'DDR_OWNERSHIP.json',dict(base=memory.base,bytes=memory.size,slots=config['max_steps'],retained=True))
        control.restore_initial();control.configure(memory.base,memory.size,config['max_steps'],int(out.name[-8:],16))
        enter('OFFICIAL_SENSOR_AND_VIDEO_START');video=runtime.start_camera(memory)
        bridge=OfficialBridge(video,control,memory,out/'capture',config['max_steps'],evidence=runtime.evidence)
        runtime.owner['bridge']=bridge
        timing=Timings();timing.control(control);timing.wrap(video,'readframe','capture_and_cache_ms')
        timing.wrap(bridge.mapper,'render','ps_mapping_ms');timing.wrap(memory,'copy_record','ddr_copy_and_cache_ms')
        previous=sha((root/'initial_state.bin').read_bytes())
        enter('BOUNDED_CAPTURE_AND_STEPS')
        for k in range(config['max_steps']):
            begin=time.monotonic();timing.values={};timing.step_write_ns=None;prof.begin()
            descriptor=bridge.step();completed=bridge.binding.next
            check=check_cycles(descriptor.cycles);d=out/'capture/bound'/('%06d'%k)
            save_json(d/'CYCLE_CHECK.json',check);save_json(d/'PUBLICATION.json',descriptor.__dict__)
            if not check['matches']:raise RuntimeError('DDR core-phase cycle mismatch')
            timing.values.update(bridge_step_and_durable_record_ms=(time.monotonic()-begin)*1000,
                                 core_counter_nominal_ms=descriptor.cycles/100000,
                                 core_counter_is_total_frame_time=False)
            save_json(d/'TIMING.json',timing.values)
            packet_begin=time.monotonic();index=index_from_committed(bridge,k,config,context,previous,dict(timing.values))
            atomic(out/'transport'/('%06d.ready.json'%k),canonical(index));packets.append(index['packet_sha256'])
            previous=bridge.binding.last_committed[1].state_sha256
            save_json(d/'PACKET_TIMING.json',dict(packet_build_and_persist_ms=(time.monotonic()-packet_begin)*1000,
                 full_iteration_before_pacing_ms=(time.monotonic()-begin)*1000,
                 producer_profile=prof.snapshot(),profile_scope='Through ready-index fsync; excludes this PACKET_TIMING file and uploader thread',
                 packet_mode='durable source files plus small ready-index; full wire assembly in uploader'))
            print('LINE11_LIVE_SAVED',k+1,'/',config['max_steps'],'PC_ACKED',uploader.next,flush=True)
            time.sleep(max(0,config['minimum_period_s']-(time.monotonic()-begin)))
        enter('CHECK_COMPLETE')
        after={hex(a):control._r(a) for a in (0x10,0x14,0x18,0x24)};save_json(out/'NEURAL_AFTER.json',after)
        if after['0x10']&1 or not after['0x10']&8 or after['0x14']!=config['max_steps'] or after['0x24']:
            raise RuntimeError('final count/full/idle/fault mismatch')
        enter('NORMAL_CAMERA_CLOSE');bridge.close_success();camera_closed=True
    except BaseException as exc:
        failure=repr(exc)
        if control is not None:control.failed=True
        if bridge is not None:bridge.failed=True
        save_json(out/'IN_DOUBT.json',dict(phase=phase,error=failure,automatic_retry=False,
                  instruction='KEEP_KERNEL_AND_BUFFERS; NO_RESET_RELOAD_RETRY_OR_FREE'))
        print('LINE11_LIVE_STOP',failure,flush=True)
    finally:
        result=dict(status='NORMAL_CAMERA_CLOSED_ALL_STEPS_SAVED_ORACLE_PENDING' if camera_closed else 'STOPPED_KEEP_KERNEL_AND_BUFFERS',
                    session_id=config['session_id'],run_id=out.name,boot_id=boot_id,completed_steps=completed,
                    camera_closed=camera_closed,error=failure,packet_sha256=packets,
                    numerical_acceptance='PENDING_PC_ALL_STATES',allocations_retained=True)
        save_json(out/'RESULT.json',result)
        # Only transferable prefix can be finalized; raw incomplete records stay in board ZIP.
        finish=dict(result,completed_steps=len(packets),hardware_completed_steps=completed,
                    packet_timings={d.parent.name:json.loads(d.read_text()) for d in out.glob('capture/bound/*/PACKET_TIMING.json')},
                    context={p.name:json.loads(p.read_text()) for p in out.glob('*.json') if p.name not in ('TRANSFER.json',)})
        save_json(out/'FINISH.json',finish)
        try:uploader.close(upload_wait)
        except Exception as exc:print('TRANSFER_STOP_PRESERVE',repr(exc),flush=True)
        try:
            z=shutil.make_archive(str(out)+'_RESULT','zip',str(out));print('LINE11_LIVE_RESULT_ZIP',z,flush=True)
        except BaseException as exc:print('ZIP_FAILED_KEEP_DIRECTORY',out,repr(exc),flush=True)
        print('LINE11_LIVE_STATUS',result['status'],'PC_ACKED',uploader.next,'/',completed,flush=True)
        print('保留内核和缓冲区；不要重复运行。网络失败只重传文件，不重新计算。',flush=True)
    return out

def run(root,config,ask=input):
    from offline_check import verify
    root=Path(root);verify(root)
    if platform.machine()!='armv7l':raise RuntimeError('This entry is for operator PYNQ board only')
    base=Path('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_R3')
    base.mkdir(parents=True,exist_ok=True)
    if list(base.glob('ATTEMPT_*.json')):raise RuntimeError('Prior attempt retained; no repeat. Return evidence.')
    # Network admission is file-only and precedes any load/MMIO/allocation.
    h=request(config,'/hello')
    if h.get('session_id')!=config['session_id'] or h.get('received')!=0 or h.get('max_steps')!=config['max_steps']:
        raise RuntimeError('PC receiver is not this fresh session; no hardware action')
    print('电脑连接已确认。请确认板卡独占、旧相机已正常关闭、同一领航者7020/OV5640接口，本Notebook独立新内核。')
    print('本次加载一次固件，官方相机采集并连续计算32步；每步全部状态保存。电脑只显示，断线不重算。')
    print('同步官方驱动仍可能阻塞；出错保留内核/缓冲区，无自动复位或重试。')
    if ask('确认并授权，输入 运行R3相机32步：')!='运行R3相机32步':
        print('已取消，无硬件操作。');return
    boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    save_json(base/('ATTEMPT_'+boot+'.json'),dict(boot_id=boot,session_id=config['session_id'],authorized=True))
    return execute(root,base,config,authorized=True,boot_id=boot)

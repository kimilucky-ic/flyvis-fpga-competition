from camera_config import WIDTH,HEIGHT,MAPPING
import motion_trial
"""Bounded operator-owned camera/PL producer, independent of PC display ACKs."""
import json,platform,shutil,time,uuid
import step_profile as prof
import ram_records
from pathlib import Path
from record_worker import RecordWorker
from batch_records import BatchRecords
from duration_run import RunWindow,read_memory_plan
from gc_events import GcEvents
KEY_PHASES=frozenset(('binding_path_setup','binding_input_checks','binding_prepare_metadata_and_ram','binding_commit_checks_and_ram','ddr_record_decode','decode_header_and_slice','decode_native_checksums_and_finite','decode_payload_sha256'))
from capture_binding import save_json
from official_bridge import OfficialBridge
from cycle_contract import check_cycles
from live_protocol import atomic,canonical,index_from_committed,sha
from live_transport import Uploader,request
_RETAINED={}

def stored_archive(root,target):
    # No image payload; ZIP_STORED avoids the prior ARM compression tail.
    import zipfile
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_STORED) as z:
        for p in sorted(Path(root).rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(root)))
    return target

class Timings:
    def __init__(self):self.values={};self.step_write_ns=None;self.input_write_ns=None
    def wrap(self,obj,name,label):
        fn=getattr(obj,name)
        def call(*a,**k):
            begin=time.monotonic_ns();cpu_begin=time.thread_time_ns() if label=='ps_mapping_ms' else None
            try:return fn(*a,**k)
            finally:
                self.values[label]=(time.monotonic_ns()-begin)/1e6
                if cpu_begin is not None:
                    self.values['ps_mapping_thread_cpu_ms']=(time.thread_time_ns()-cpu_begin)/1e6
                    self.values['ps_mapping_start_ns']=begin
                    self.values['ps_mapping_end_ns']=time.monotonic_ns()
        setattr(obj,name,call)
    def control(self,c):
        old=c._w;pub=c.publication
        def write(a,v):
            if a==0 and v==1:self.step_write_ns=time.monotonic_ns()
            return old(a,v)
        def publication():
            if self.step_write_ns is not None:self.values['step_command_to_completed_check_ms']=(time.monotonic_ns()-self.step_write_ns)/1e6
            begin=time.monotonic_ns()
            try:return pub()
            finally:self.values['publication_read_ms']=(time.monotonic_ns()-begin)/1e6
        c._w=write;c.publication=publication
        self.wrap(c,'write_inputs','input_721_mmio_write_ms')
        self.wrap(c,'advance','input_upload_step_and_publication_ms')

def execute(root,base,config,*,authorized=False,boot_id=None,runtime_factory=None,send=request,upload_wait=60,window_factory=RunWindow,memory_admission=None):
    if not authorized or _RETAINED:raise RuntimeError('explicit fresh once-only session required')
    prof.ENABLED=bool(config.get('diagnostics',False))
    mode=config.get('transfer_mode','live_compact')
    if mode not in ('live_compact','after_run','local_only'):raise ValueError('invalid transfer mode')
    startup_begin=time.monotonic();startup={}
    print('LINE11_STARTUP 校验本轮文件，尚未加载固件',flush=True)
    from offline_check import verify
    identity=verify(root);root=Path(root);base=Path(base)
    startup['package_verify_ms']=(time.monotonic()-startup_begin)*1000
    storage_begin=time.monotonic()
    if not 1<=config['max_steps']<=4096 or config.get('duration_s')!=60.0:raise ValueError('bounded60s only')
    if type(config.get('ring_slots')) is not int or not 32<=config['ring_slots']<=64:
        raise ValueError('Ring slots must cover at least two16-record persistence batches')
    config=dict(config);motion_trial.condition(config)
    if runtime_factory is None:
        fresh_plan=read_memory_plan(config)
        memory_admission=fresh_plan
        config.update(ring_slots=fresh_plan['slots'],minimum_period_s=0.0)
    window=window_factory(config)
    out=base/('RUN_'+uuid.uuid4().hex);out.mkdir(parents=True,exist_ok=False);(out/'transport').mkdir()
    if shutil.disk_usage(str(out)).free<1024*1024*1024:raise RuntimeError('Need1GiB free before hardware')
    if runtime_factory is None:
        from board_runtime import PynqRuntime
        runtime_factory=PynqRuntime
    runtime=runtime_factory(root,out)
    if runtime.evidence not in ('CPU_MOCK_ONLY','OPERATOR_PHYSICAL_RUN_UNATTESTED'):raise RuntimeError('Unknown runtime evidence')
    runtime.camera_diagnostics=bool(config.get('camera_diagnostics',False));_RETAINED[out.name]=runtime
    journal=BatchRecords(out);ram_records.CURRENT=journal;runtime.owner['ram_records']=journal
    print('LINE11_STARTUP 准备记录索引，尚未加载固件',flush=True)
    path_begin=time.monotonic()
    startup['path_index']=journal.prevalidate_generated_steps(out,config['max_steps'])
    startup['path_index_ms']=(time.monotonic()-path_begin)*1000
    startup['storage_and_runtime_prepare_ms']=(time.monotonic()-storage_begin)*1000
    startup['before_prepare_ms']=(time.monotonic()-startup_begin)*1000
    print('LINE11_STARTUP_READY %.3fs；即将加载驱动和固件'%(startup['before_prepare_ms']/1000),flush=True)
    context=dict(revision='LINE11_OFFICIAL_LIVE_V261_60S',run_id=out.name,boot_id=boot_id,identity=identity,
                 evidence=runtime.evidence,session_id=config['session_id'],physical_clock_measured=False,
                 detail_profile_ordinals=[6,14,22,30],key_phase_timing_every_step=True,gc_event_capacity=256,progress_every_steps=64,timing_cpu_scope='current Python thread only; wall minus CPU is not solely GIL wait',camera_calltree_ordinals=[4,16] if config.get('camera_diagnostics') else [],network_controls_neurons=False,max_steps=config['max_steps'],transfer_mode=mode,source_images_transferred=motion_trial.condition(config)!='demo',source_pixels_retained=motion_trial.condition(config)!='demo',camera_width=WIDTH,camera_height=HEIGHT,input_mapping=MAPPING,storage='BOUNDED_RAM_WITH_INDEPENDENT_DURABLE_WRITER',persistence_queue_batches=2,persistence_batch_steps=16,diagnostic_sidecars_durable=False)
    context.update(startup_timing=startup,duration_s=config['duration_s'],memory_admission=memory_admission,minimum_period_s=config['minimum_period_s'])
    save_json(out/'RUN_CONTEXT.json',context)
    uploader=Uploader(out,config,send=send)
    if mode=='live_compact':uploader.start()
    worker=None;gc_trace=None
    step_timings={}
    bridge=control=None;phase='PREPARE';completed=0;camera_closed=False;packets=[];failure=None;neural_complete=False
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
        enter('ALLOCATE_RESTORE');memory=runtime.memory(slots=config['ring_slots']);memory.pin_before_configure()
        save_json(out/'DDR_OWNERSHIP.json',dict(base=memory.base,bytes=memory.size,slots=config['ring_slots'],retained=True))
        control.restore_initial();control.configure(memory.base,memory.size,config['ring_slots'],int(out.name[-8:],16))
        enter('OFFICIAL_SENSOR_AND_VIDEO_START');video=runtime.start_camera(memory)
        bridge=OfficialBridge(video,control,memory,out/'capture',config['max_steps'],evidence=runtime.evidence,payload_checker=getattr(runtime,'payload_checker',None))
        bridge.binding.retain_source=motion_trial.condition(config)!='demo'
        runtime.owner['bridge']=bridge
        timing=Timings();timing.control(control);timing.wrap(video,'readframe','capture_and_cache_ms')
        timing.wrap(bridge.mapper,'render','ps_mapping_ms');timing.wrap(memory,'copy_record','ddr_copy_and_cache_ms')
        previous=sha((root/'initial_state.bin').read_bytes())
        enter('BOUNDED_CAPTURE_AND_STEPS');journal.start()
        gc_trace=GcEvents();gc_trace.start();runtime.owner['gc_trace']=gc_trace
        worker=RecordWorker(out,config,context,packets,uploader=uploader);runtime.owner['record_worker']=worker
        original_advance=control.advance
        def guarded_advance(*args,**kwargs):
            worker.check()
            return original_advance(*args,**kwargs)
        control.advance=guarded_advance
        original_write=control._w
        def guarded_write(address,value):
            # Disk worker can fail while inputs are being staged; check again at STEP.
            if address==0 and value==1:worker.check()
            return original_write(address,value)
        control._w=guarded_write
        def credit_ready():
            worker.check()
            control.release_durable(journal.durable_prefix())
            return not (control._r(0x10)&8)
        if motion_trial.condition(config)!='demo':
            context['experiment_start_ns']=time.monotonic_ns()
            worker.context['experiment_start_ns']=context['experiment_start_ns']
            save_json(out/'EXPERIMENT.json',dict(condition=motion_trial.condition(config),start_ns=context['experiment_start_ns'],segments=[] if motion_trial.condition(config)=='capture' else motion_trial.SEGMENTS,events_are_planned=motion_trial.condition(config)!='capture'))
        previous_iteration_end=time.monotonic();window.begin()
        for k in range(config['max_steps']+1):
            worker.check()
            credit_begin=time.monotonic()
            if not window.admit_when_ready(worker.check,credit_ready):break
            credit_wait_ms=(time.monotonic()-credit_begin)*1000
            loop_entry=time.monotonic();gc_trace.step=k;worker.check()
            begin=time.monotonic();timing.values={'ring_credit_wait_ms':credit_wait_ms,'between_iterations_ms':(loop_entry-previous_iteration_end)*1000};timing.step_write_ns=None;detail_sample=k in (6,14,22,30);prof.begin(active=True,keys=None if prof.ENABLED or detail_sample else KEY_PHASES)
            bridge_start_ns=time.monotonic_ns();bridge_cpu_ns=time.thread_time_ns()
            descriptor=bridge.step();completed=bridge.binding.next
            timing.values.update(bridge_start_ns=bridge_start_ns,bridge_end_ns=time.monotonic_ns(),bridge_thread_cpu_ms=(time.thread_time_ns()-bridge_cpu_ns)/1e6)
            check=check_cycles(descriptor.cycles);d=out/'capture/bound'/('%06d'%k)
            if prof.ENABLED:
                save_json(d/'CYCLE_CHECK.json',check,durable=False);save_json(d/'PUBLICATION.json',descriptor.__dict__,durable=False)
            if not check['matches']:raise RuntimeError('DDR core-phase cycle mismatch')
            timing.values.update(detail_profiled=detail_sample,camera_calltree_profiled=bool(config.get('camera_diagnostics')) and k in (4,16),bridge_step_and_ram_record_ms=(time.monotonic()-begin)*1000,
                                 core_counter_nominal_ms=descriptor.cycles/100000,
                                 core_counter_is_total_frame_time=False)
            if prof.ENABLED:save_json(d/'TIMING.json',timing.values,durable=False)
            enqueue_begin=time.monotonic()
            worker.submit(bridge,k,previous,dict(timing.values),prof.snapshot())
            previous=bridge.binding.last_committed[1].state_sha256
            step_timings['%06d'%k]=dict(timing.values,
                packet_enqueue_ms=(time.monotonic()-enqueue_begin)*1000,
                full_iteration_before_pacing_ms=(time.monotonic()-begin)*1000)
            step_timings['%06d'%k]['producer_profile']=prof.snapshot()
            prof.begin(active=False)
            print_begin=time.monotonic()
            progress_printed=(k+1)%64==0
            if progress_printed:print('LINE11_RAM_RECORDED',k+1,'/',config['max_steps'],'PC_ACKED',uploader.next,flush=True)
            print_end=time.monotonic()
            sleep_s=0 # no fixed pacing; ring credits and worker queue provide backpressure
            if sleep_s>0:time.sleep(sleep_s)
            iteration_end=time.monotonic()
            step_timings['%06d'%k].update(progress_printed=progress_printed,console_output_ms=(print_end-print_begin)*1000,pacing_ms=(iteration_end-print_end)*1000,whole_iteration_ms=(iteration_end-begin)*1000)
            previous_iteration_end=iteration_end;gc_trace.step=None
        duration_receipt=window.receipt(completed);save_json(out/'DURATION.json',duration_receipt)
        drain_begin=time.monotonic();worker.drain();drain_ms=(time.monotonic()-drain_begin)*1000
        tail_begin=time.monotonic()
        journal.drain()
        control.release_durable(journal.durable_prefix())
        save_json(out/'LOOP_TAIL.json',dict(worker_drain_ms=drain_ms,final_durable_release_ms=(time.monotonic()-tail_begin)*1000))
        if 'camera_memory' in runtime.owner:save_json(out/'CAMERA_MEMORY_FINAL.json',runtime.owner['camera_memory'].summary())
        enter('CHECK_COMPLETE')
        after={hex(a):control._r(a) for a in (0x10,0x14,0x18,0x24,0x4c,0x50)};save_json(out/'NEURAL_AFTER.json',after)
        if (after['0x10']&1 or after['0x10']&8 or after['0x4c']!=completed or after['0x50']!=0 or after['0x14']!=completed or after['0x18'] or after['0x24']):
            raise RuntimeError('final count/full/idle/fault mismatch')
        neural_complete=True
    except BaseException as exc:
        failure=repr(exc)
        if control is not None:control.failed=True
        if bridge is not None:bridge.failed=True
        save_json(out/'IN_DOUBT.json',dict(phase=phase,error=failure,automatic_retry=False,
                  instruction='KEEP_KERNEL_AND_BUFFERS; NO_RESET_RELOAD_RETRY_OR_FREE'))
        print('LINE11_LIVE_STOP',failure,flush=True)
    finally:
        prof.begin(active=False)
        if gc_trace is not None:
            gc_trace.close()
            save_json(out/'GC_EVENTS.json',gc_trace.report())
        # Worker must stop before RAM flush. On worker failure keep raw capsules.
        if worker is not None:
            worker.finished.set();worker.thread.join(10)
            if worker.thread.is_alive():
                uploader.stop.set();uploader.wake.set()
                raise RuntimeError('Worker active; preserve RAM and kernel, no flush/close')
        # Stop further computation before bulk persistence; RAM remains owned on failure.
        try:
            storage=journal.flush();save_json(out/'RAM_FLUSH.json',storage)
        except BaseException as exc:
            uploader.stop.set();uploader.wake.set()
            print('LINE11_RAM_FLUSH_FAILED_KEEP_KERNEL',repr(exc),flush=True)
            raise
        result=dict(status='ALL_STEPS_SAVED_CAMERA_CLOSE_PENDING' if neural_complete else 'STOPPED_KEEP_KERNEL_AND_BUFFERS',
                    duration=duration_receipt if neural_complete else None,
                    session_id=config['session_id'],run_id=out.name,boot_id=boot_id,completed_steps=completed,
                    camera_closed=camera_closed,error=failure,packet_sha256=packets,
                    numerical_acceptance='NOT_RUN_LOCAL_ONLY' if mode=='local_only' else 'PENDING_PC_ALL_STATES',allocations_retained=True)
        save_json(out/'RESULT.json',result)
        # Only transferable prefix can be finalized; raw incomplete records stay in board ZIP.
        finish=dict(result,completed_steps=len(packets),hardware_completed_steps=completed,
                    packet_timings=step_timings,worker_timings=dict(worker.timings) if worker is not None else {},
                    context={p.name:json.loads(p.read_text()) for p in out.glob('*.json') if p.name not in ('TRANSFER.json','VIDEO_DRIVER_SOURCE.json')})
        save_json(out/'FINISH.json',finish)
        if mode=='after_run':uploader.start()
        if mode!='local_only':
            try:uploader.close(upload_wait)
            except Exception as exc:print('TRANSFER_STOP_PRESERVE',repr(exc),flush=True)
        else:
            save_json(out/'TRANSFER.json',dict(status='LOCAL_ONLY_NOT_SUBMITTED',acked=0,neural_commands=0,full_state_oracle='NOT_RUN'))
        # A durable neural receipt and file transfer precede the synchronous vendor close.
        # Keep this snapshot even if close never returns. It never asserts camera closure.
        try:
            print('LINE11_LIVE_RESULT_DIRECTORY',out,flush=True)
            if config.get('automatic_archives',False):
                z=stored_archive(out,str(out)+'_NEURAL_RESULT.zip');print('LINE11_LIVE_RESULT_ZIP',z,flush=True)
        except BaseException as exc:print('ZIP_FAILED_KEEP_DIRECTORY',out,repr(exc),flush=True)
        print('LINE11_NEURAL_STATUS',result['status'],'PC_ACKED',uploader.next,'/',completed,flush=True)
        if neural_complete and (uploader.finish_sent or mode=='local_only'):
            enter('NORMAL_CAMERA_CLOSE')
            close_begin=time.monotonic()
            close_error=None
            try:
                bridge.close_success();camera_closed=True
            except BaseException as exc:
                close_error=repr(exc)
                save_json(out/'IN_DOUBT.json',dict(phase=phase,error=close_error,automatic_retry=False,
                    instruction='KEEP_KERNEL_AND_BUFFERS; NO_RESET_RELOAD_RETRY_OR_FREE'))
            receipt=dict(schema='line11-camera-close/v1',session_id=config['session_id'],run_id=out.name,
                boot_id=boot_id,completed_steps=completed,packet_sha256=packets,
                status='CLOSED' if camera_closed else 'FAILED',camera_closed=camera_closed,error=close_error,
                close_duration_ms=(time.monotonic()-close_begin)*1000)
            save_json(out/'CAMERA_CLOSE.json',receipt)
            try:
                ack={'durable':True,'status':receipt['status']} if mode=='local_only' else send(config,'/camera-close',canonical(receipt))
                if ack.get('durable') is not True or ack.get('status')!=receipt['status']:raise ValueError('invalid camera-close ACK')
            except Exception as exc:print('CAMERA_CLOSE_RECEIPT_NOT_ACKED',repr(exc),'local receipt preserved',flush=True)
            try:
                if config.get('automatic_archives',False):
                    z=stored_archive(out,str(out)+'_RESULT.zip');print('LINE11_LIVE_RESULT_ZIP',z,flush=True)
            except BaseException as exc:print('ZIP_FAILED_KEEP_DIRECTORY',out,repr(exc),flush=True)
        elif neural_complete:
            print('CAMERA_CLOSE_DEFERRED_TRANSFER_PENDING; keep kernel and buffers; no rerun',flush=True)
        print('LINE11_LIVE_STATUS', 'NORMAL_CAMERA_CLOSED' if camera_closed else 'KEEP_KERNEL_CAMERA_NOT_CONFIRMED_CLOSED',flush=True)
        print('保留内核和缓冲区；不要重复运行。网络失败只重传文件，不重新计算。',flush=True)
    return out

def run(root,config,ask=input):
    from offline_check import verify
    root=Path(root);verify(root)
    if platform.machine()!='armv7l':raise RuntimeError('This entry is for operator PYNQ board only')
    base=Path('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_V261_60S')
    base.mkdir(parents=True,exist_ok=True)
    if list(base.glob('ATTEMPT_*.json')):raise RuntimeError('Prior attempt retained; no repeat. Return evidence.')
    # Network admission is file-only and precedes any load/MMIO/allocation.
    config=dict(config)
    config['transfer_mode']='live_compact'
    h=request(config,'/hello')
    if h.get('session_id')!=config['session_id'] or h.get('received')!=0 or h.get('max_steps')!=config['max_steps']:
        raise RuntimeError('PC receiver is not this fresh session; no hardware action')
    print('默认实时发送721项输入和全部状态，无需选择输出方式。')
    print('请确认板卡独占、旧相机已正常关闭、同一领航者7020/OV5640接口，本Notebook独立新内核。')
    print('运行60秒；实验内容由你自行安排，无需选择模式。',flush=True)
    try:plan=read_memory_plan(config)
    except RuntimeError as exc:
        print('LINE11_MEMORY_PREFLIGHT_STOP',str(exc),flush=True)
        print('本次未加载固件、未启动相机、未计算神经步。请复制LINE11_MEMORY_DIAGNOSTIC及此行交回核查。',flush=True)
        return
    print('60秒从采集循环开始计；初始化和保存另计，到时完成当前帧后停止。每16步后台保存一次；本轮保留80×48原始采集帧、721项输入和全部神经状态。掉电会丢失未保存批次。')
    print('内存预算（尚未实际分配）：DDR记录槽',plan['slots'],'；DDR MiB',round(plan['ddr_bytes']/1048576,1),'；取消固定限速，只有保存队列或DDR满时等待。这不是实际分配成功证明。')
    print('授权后加载固件并只申请一次DDR；申请成功才恢复神经初态和启动相机。申请失败立即停止，不重试、不清理其他会话。')
    print('同步官方驱动仍可能阻塞；出错保留内核/缓冲区，无自动复位或重试。')
    if ask('确认并授权，输入 运行2026.1铺满版60秒：')!='运行2026.1铺满版60秒':
        print('已取消，无硬件操作。');return
    boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    save_json(base/('ATTEMPT_'+boot+'.json'),dict(boot_id=boot,session_id=config['session_id'],authorized=True))
    return execute(root,base,config,authorized=True,boot_id=boot)

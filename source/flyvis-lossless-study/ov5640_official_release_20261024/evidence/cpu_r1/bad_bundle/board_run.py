"""One authorized frame/step, with durable evidence and no failure cleanup."""
import json,shutil,time,uuid
from pathlib import Path
from capture_binding import save_json
from official_bridge import OfficialBridge
_RETAINED={}

def execute(root,base,*,authorized=False,runtime_factory=None,boot_id=None):
    if authorized is not True:raise RuntimeError('No explicit operator authorization')
    if _RETAINED:raise RuntimeError('Prior session retained; no retry/reload')
    root,base=Path(root),Path(base)
    from offline_check import verify
    identity=verify(root)
    if runtime_factory is None:
        from board_runtime import PynqRuntime
        runtime_factory=PynqRuntime
    out=base/('RUN_'+uuid.uuid4().hex);out.mkdir(parents=True,exist_ok=False)
    if shutil.disk_usage(str(out)).free<64*1024*1024:raise RuntimeError('Need64MiB free before hardware actions')
    runtime=runtime_factory(root,out);_RETAINED[out.name]=runtime
    evidence=runtime.evidence
    phase='PREPARE';bridge=None;control=None
    save_json(out/'RUN_CONTEXT.json',dict(revision='LINE11_OFFICIAL_FULL_R1',run_id=out.name,boot_id=boot_id,
        identity=identity,evidence=evidence,board_result=False,automatic_retry=False,
        physical_clock_measured=False,initial_state_readback='Unavailable; restore-clean plus full post-step oracle',
        nominal_board='operator confirms Leader ZYNQ7020 and same OV5640 interface as successful official run'))
    def enter(name):
        nonlocal phase
        phase=name;print('LINE11_OFFICIAL_PHASE',phase,flush=True)
        save_json(out/('PHASE_'+name+'.json'),dict(phase=name,monotonic_ns=time.monotonic_ns()))
    try:
        enter('PREPARE');runtime.prepare()
        enter('LOAD');runtime.load()
        enter('CLOCK_HP');nominal=runtime.inspect()
        enter('FRESH_ABI');control=runtime.control()
        if any(control._r(a) for a in (0x10,0x14,0x18,0x24)):raise RuntimeError('Fresh unused neural ABI required')
        enter('ALLOCATE_RESTORE');memory=runtime.memory();memory.pin_before_configure()
        save_json(out/'DDR_OWNERSHIP.json',dict(base=memory.base,bytes=memory.size,slots=1,retained=True))
        control.restore_initial();control.configure(memory.base,memory.size,1,int(out.name[-8:],16))
        enter('OFFICIAL_SENSOR_AND_VIDEO_START');video=runtime.start_camera(memory)
        bridge=OfficialBridge(video,control,memory,out/'capture',1,evidence=evidence)
        runtime.owner['bridge']=bridge
        enter('CAPTURE_BIND_AND_STEP');record=bridge.step()
        if record.cycles!=2201418:raise RuntimeError('Unexpected full-network compute cycle count')
        enter('CHECK_COMPLETE')
        status=control._r(0x10)
        if status&1 or not status&8 or control._r(0x14)!=1 or control._r(0x24):raise RuntimeError('Final neural count/full/idle/fault mismatch')
        enter('NORMAL_CAMERA_CLOSE');bridge.close_success()
        result=dict(status='ONE_OFFICIAL_FRAME_ONE_PL_STEP_SAVED_ORACLE_PENDING',evidence=evidence,
           board_result=False,completed_steps=1,compute_cycles=record.cycles,nominal_clocks_MHz=nominal,
           physical_clock_measured=False,actual_input_words=721,state_words=45669,
           numerical_acceptance='PENDING_PC_STRICT_FP32_ALL_STATE_AUDIT',allocations_retained=True)
        save_json(out/'RESULT.json',result)
        # Optional preview follows durable neural record; it cannot authorize another step.
        try:
            import numpy as np
            from PIL import Image
            raw=(out/'capture/bound/000000/source_frame.bin').read_bytes()
            pixels=np.frombuffer(raw,np.uint8).reshape(480,800,3)
            Image.fromarray(pixels[:,:,::-1].copy(),'RGB').save(str(out/'camera.png'))
        except Exception as exc:
            print('PREVIEW_UNAVAILABLE_RECORDS_RETAINED',repr(exc),flush=True)
    except BaseException as exc:
        if control is not None:control.failed=True
        if bridge is not None:bridge.failed=True
        try:save_json(out/'IN_DOUBT.json',dict(phase=phase,error=repr(exc),evidence=evidence,
            automatic_retry=False,instruction='KEEP_KERNEL_AND_BUFFERS; NO_RESET_RELOAD_RETRY_OR_FREE'))
        except BaseException:pass
        print('LINE11_OFFICIAL_STOP',repr(exc),flush=True)
        raise
    finally:
        # Evidence only; never releases a DMA buffer or retries hardware on failure.
        try:
            z=shutil.make_archive(str(out)+'_RESULT','zip',str(out))
            print('LINE11_OFFICIAL_RESULT_ZIP',z,flush=True)
        except BaseException as exc:print('ZIP_FAILED_KEEP_DIRECTORY',out,repr(exc),flush=True)
        print('LINE11_OFFICIAL_RESULT_DIRECTORY',out,flush=True)
    return out

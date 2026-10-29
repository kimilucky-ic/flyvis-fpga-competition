"""One reviewed old-session camera close. Run in ORIGINAL retained Notebook kernel.
No overlay load/reset/STEP/IIC init/DDR allocation/free. No retry after attempt.
"""
import hashlib,json,sys,time,shutil
from pathlib import Path
from types import SimpleNamespace
RUN_ID='RUN_b0a5cd8079b045bdb1b97c07523c6c55'
BOOT_ID='082f292d-83b5-4217-af2f-2e405a5e4a72'
BASE=Path('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_FULL_20261024')
FILE_SHA={'RUN_CONTEXT.json': '9d33ff141aa2246c7bdfec39e57c83417c8565afdfb76fe07c69e0921b48f90e', 'IN_DOUBT.json': '09107ae9e886de512a4a527c2f451cb34bbbdc3e796e1a4dff9f6855453797ef', 'DDR_OWNERSHIP.json': '88c42d354243bfd4016dc0f1a3fa6b18c4d0d32af152f8c74aaa88bdc766e0c2', 'DRIVERS.json': 'e819a200da4a0072858ce4742dad48b3799a7a4a84866969d0abcee767ab856e', 'NEURAL_BEFORE.json': '268d376e834f6c537ae4f5f66519e2a351b4347afd93ebe9fb26eacbfc4cd8b3', 'capture/PROFILE.json': '94fd630f82a0ba2307d092d2131eeaeb9922cc942bc4b00c92105d2951e158e9', 'capture/bound/000000/PREPARED.json': '6b29d8e9f996f4ba1fb267efc84e1df7ac2fc2b2e0a1d68c168b5328063ca98d', 'capture/bound/000000/COMMITTED.json': 'ea0914903e6a9f5a884bc6dd30ca23fff88adb627f92bb9084ffa03d98d2eada', 'capture/bound/000000/source_frame.bin': 'b68c5753f9f51dcdfd51d71e22b93483ad0315a92da2d2d4607e08673a341915', 'capture/bound/000000/input.bin': 'a0610d71c40d067d8869c8775ef29067d9afec88828a5a3bbe7fb24d54409a52', 'capture/bound/000000/actual_input.bin': 'a0610d71c40d067d8869c8775ef29067d9afec88828a5a3bbe7fb24d54409a52', 'capture/bound/000000/actual_state.bin': '4bfa9ddf8b2e499eb70294bcbbb454887c844d623773b4591ceeb8418a6e1a8c', 'capture/bound/000000/record.bin': 'e7dc8127a4a00ab2740f1848f77834652b13f08a6ecf17e51823021237958b47'}

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,value):
    import os
    with Path(p).open('x',encoding='utf-8') as f:
        json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())

def close_reviewed(runtime,run,boot,ask=input):
    run=Path(run)
    if boot!=BOOT_ID or run.name!=RUN_ID:raise RuntimeError('Boot/run differs; no hardware action')
    if Path(runtime.out).resolve()!=run.resolve():raise RuntimeError('Retained object run mismatch')
    for name,expected in FILE_SHA.items():
        if digest(run/name)!=expected:raise RuntimeError('Reviewed evidence changed: '+name)
    stop=json.loads((run/'IN_DOUBT.json').read_text())
    if stop['error']!="RuntimeError('Unexpected full-network compute cycle count')":raise RuntimeError('Not the reviewed cycle-only stop')
    if (run/'CLOSE_ATTEMPT.json').exists():raise RuntimeError('Close already attempted; preserve kernel and return evidence')
    owner=runtime.owner;control=owner['control'];memory=owner['memory'];bridge=owner['bridge'];video=owner['checked_video']
    if (not control.failed or not bridge.failed or bridge.closed or bridge.held_frame is not None or bridge.binding.next!=1
            or bridge.video is not video or video.video is not owner['video'] or bridge.memory is not memory
            or bridge.control is not control or not memory.armed or memory.released):
        raise RuntimeError('Retained ownership differs; no hardware action')
    own=json.loads((run/'DDR_OWNERSHIP.json').read_text())
    cookie=int(RUN_ID[-8:],16)
    if memory.base!=own['base'] or memory.size!=188416 or memory.slots!=1 or control.session!=(memory.base,memory.base+188416,1,cookie,0):
        raise RuntimeError('Retained DDR/session mismatch')
    print('仅收尾已验收的原会话：检查当前神经状态和DDR记录，调用一次官方相机close。')
    print('不加载固件、不复位、不计算、不释放神经DDR；请确认当前板卡仍独占且未被其他程序改变。')
    if ask('输入 关闭本次相机：')!='关闭本次相机':
        print('已取消；无MMIO/相机操作。');return None
    save(run/'CLOSE_ATTEMPT.json',dict(run_id=RUN_ID,boot_id=boot,monotonic_ns=time.monotonic_ns(),authorization='关闭本次相机'))
    phase='READ_NEURAL_BEFORE';close_called=False
    def registers():
        addresses=(4,8,12,0x10,0x14,0x18,0x20,0x24,0x28,0x2c,0x30,0x34,0x38,0x3c,0x40,0x80,0x84,0x88,0x8c,0x90,0x94,0x98,0x9c,0xa0)
        return {hex(a):control._r(a) for a in addresses}
    def check(r):
        expected={4:memory.base,8:memory.base+188416,12:1,0x10:46,0x14:1,0x18:0,0x20:2199975,0x24:0,0x28:0,
            0x2c:cookie,0x30:45669,0x34:1513231,0x38:0x110004,0x3c:188416,0x40:1,
            0x80:1,0x84:memory.base,0x88:0,0x8c:2199975,0x90:1,0x94:cookie,0x98:0,0x9c:45669,0xa0:1513231}
        if any(r[hex(a)]!=v for a,v in expected.items()):raise RuntimeError('Current neural state differs; no cleanup/retry')
    try:
        before=registers();save(run/'CLOSE_NEURAL_BEFORE.json',before);check(before)
        phase='VERIFY_RETAINED_DDR'
        data=memory.copy_record(SimpleNamespace(address=memory.base,frame_id=0))
        if hashlib.sha256(data).hexdigest()!=FILE_SHA['capture/bound/000000/record.bin']:raise RuntimeError('Retained DDR differs from reviewed full-state record')
        save(run/'CLOSE_DDR_MATCH.json',dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),matches_reviewed_record=True))
        phase='OFFICIAL_CAMERA_CLOSE';print('LINE11_CLOSE_PHASE',phase,flush=True)
        save(run/'CLOSE_CAMERA_CALL.json',dict(monotonic_ns=time.monotonic_ns(),calls=1))
        close_called=True;video.close()  # existing official close; may block; never retry
        bridge.closed=True  # failure latches remain true, preventing further STEP
        phase='READ_NEURAL_AFTER';after=registers();save(run/'CLOSE_NEURAL_AFTER.json',after);check(after)
        if after!=before:raise RuntimeError('Neural state changed during camera close')
        result=dict(status='PASS_OPERATOR_CAMERA_CLOSE_NEURAL_IDLE_FULL_DDR_RETAINED',
            evidence='OPERATOR_EXECUTION_PENDING_PC_REVIEW',run_id=RUN_ID,boot_id=boot,
            camera_close_returned=True,neural_registers_unchanged=True,retained_record_matches_audited=True,
            neural_steps_added=0,overlay_loads=0,neural_resets=0,neural_DDR_freed=False,
            original_IN_DOUBT_preserved=True,failed_latches_preserved=True)
        save(run/'CLOSE_RESULT.json',result);print('LINE11_CLOSE_STATUS',result['status'],flush=True)
        return result
    except BaseException as exc:
        save(run/'CLOSE_STOPPED.json',dict(phase=phase,error=repr(exc),camera_close_called=close_called,
            automatic_retry=False,instruction='KEEP_KERNEL_BUFFERS_NO_RETRY_RESET_FREE'))
        print('LINE11_CLOSE_STOP',repr(exc),flush=True);raise
    finally:
        try:
            z=shutil.make_archive(str(run)+'_CLOSE_RESULT','zip',str(run))
            print('LINE11_CLOSE_RESULT_ZIP',z,flush=True)
        except BaseException as exc:print('LINE11_CLOSE_ZIP_FAILED',repr(exc),flush=True)

def main():
    # Do not import/recreate board_run: only the exact retained original kernel.
    br=sys.modules.get('board_run');oc=sys.modules.get('offline_check')
    if br is None or oc is None or set(br._RETAINED)!={RUN_ID}:raise RuntimeError('Use the ORIGINAL stopped Notebook kernel; do not reload/recreate objects')
    runtime=br._RETAINED[RUN_ID]
    expected=BASE/'package_abe397e809a7'
    if Path(runtime.root).resolve()!=expected.resolve():raise RuntimeError('Wrong retained package')
    identity=oc.verify(expected)
    if identity['revision']!='LINE11_OFFICIAL_FULL_R1':raise RuntimeError('Wrong original revision')
    ol=runtime.owner['overlay']
    if not ol.is_loaded():raise RuntimeError('Original overlay no longer recorded as loaded')
    # Pin native video driver files captured by this exact reviewed run.
    drivers=json.loads((BASE/RUN_ID/'DRIVERS.json').read_text())
    for key,meta in drivers.items():
        if key.startswith('/') and ('video2lcd/' in key or '/_video.' in key):
            if digest(key)!=meta['sha256']:raise RuntimeError('Official video driver changed')
    return close_reviewed(runtime,BASE/RUN_ID,Path('/proc/sys/kernel/random/boot_id').read_text().strip())

if __name__=='__main__':main()

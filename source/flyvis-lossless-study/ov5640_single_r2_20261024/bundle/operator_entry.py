"""Single-file delivery entry. Only the human can authorize one frame and step."""
import hashlib,json,os,platform,time
from pathlib import Path
REVIEWED_RUN='ID_R2_b6a46cee2e544e7ebcd7c135df5f1797'
REVIEWED_SHA='6f2bc9cf28a5a8b3fc1c290b1f2fc009f6bac9b7420a10c528f56e587b3dc722'
REVISION='LINE11_SINGLE_R2'

def prior_id(base):
    raw=(base/REVIEWED_RUN/'RESULT.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=REVIEWED_SHA:raise RuntimeError('Reviewed ID PASS record missing or changed; no hardware actions')
    r=json.loads(raw)
    if r['result']['sensor_id']!=0x5640 or r['revision']!='IIC21_R2':raise RuntimeError('Wrong ID prerequisite')
    return dict(run_id=REVIEWED_RUN,boot_id=r['boot_id'],result_sha256=REVIEWED_SHA)

def run(root,ask=input):
    root=Path(root).resolve()
    from offline_check import verify
    identity=verify(root)
    if platform.machine()!='armv7l':raise RuntimeError('Use confirmed Leader7020/PYNQ board')
    prior=prior_id(Path('/home/xilinx/jupyter_notebooks/LINE11_OV5640_ID_DIAG'))
    boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    base=Path('/home/xilinx/jupyter_notebooks/LINE11_OV5640_SINGLE_R2');base.mkdir(parents=True,exist_ok=True)
    marker=base/'SINGLE_FRAME_ATTEMPT.json'
    if marker.exists():raise RuntimeError('This single-frame candidate already attempted; keep results/kernel, no retry or reset')
    c=json.loads((root/'entry_conditions.json').read_text())
    print('已核对型号验证记录。仅适用领航者7020 V3.9 + ATK-MC5640，请确认接口未变、无其他程序操作板卡。')
    print('本次：加载同一版固件一次 → 初始化摄像头 → 采一帧 → PS生成721项输入 → PL算一步 → 保存全部45669状态。')
    print('保留完整网络/严格FP32/100MHz设计。电气波形和物理时钟仍未测量；条件性单帧测试，不是实时演示。')
    print('当前BGR通道顺序尚未经色条确认；不据此宣称颜色正确。成功或失败均保留内核/缓冲区，禁止自动重试。')
    if ask('允许本次加载、摄像头初始化、采集及一步计算，输入 同意单帧测试：')!='同意单帧测试':
        print('已取消，没有加载、MMIO、分配或计算。');return
    c.update(operator_confirmation='同意单帧测试',exclusive_board_ownership=True,pinmap_and_orientation_verified=True,
             prior_id_acceptance=prior,current_boot_id=boot,operator_monotonic_ns=time.monotonic_ns())
    from board_capture import check_conditions
    check_conditions(c)
    # Cross-kernel persistent reservation before any hardware/native helper action.
    with marker.open('x',encoding='utf-8') as f:
        json.dump(dict(revision=REVISION,boot_id=boot,prior_id=prior,identity=identity,automatic_retry=False),f,indent=2)
        f.flush();os.fsync(f.fileno())
    import board_capture
    try:
        out=board_capture.run(base,c,authorize_load_and_one_step=True)
    except BaseException as exc:
        print('LINE11_SINGLE_R2_STOP',repr(exc))
        print('请提供已打印的结果ZIP；若无ZIP，请提供最后输出。保留内核，不重跑、复位或释放缓冲区。')
        return
    print('LINE11_SINGLE_R2_STATUS ONE_FRAME_ONE_STEP_SAVED_ORACLE_PENDING')
    print('已保存一帧及一步记录；全部状态是否正确，等待电脑独立验收。')
    print('LINE11_SINGLE_R2_RESULT_ZIP',str(out)+'_RESULT.zip')
    print('请下载ZIP交回；保留当前内核，不重复运行或继续采图。')
    return out

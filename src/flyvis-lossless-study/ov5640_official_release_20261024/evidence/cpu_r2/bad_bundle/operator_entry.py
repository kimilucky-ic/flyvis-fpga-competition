"""One explicit human confirmation. No hardware calls before it."""
import json,os,platform,time
from pathlib import Path
from capture_binding import save_json

def run(root,ask=input,*,base=None,boot=None,execute_fn=None):
    from offline_check import verify
    root=Path(root).resolve();identity=verify(root)
    if platform.machine()!='armv7l':raise RuntimeError('Run this Notebook on the confirmed Leader ZYNQ7020/PYNQ board')
    boot=boot or Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    if not boot or any(c not in '0123456789abcdef-' for c in boot):raise ValueError('Invalid boot identity')
    base=Path(base) if base else Path('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_FULL_20261024')
    base.mkdir(parents=True,exist_ok=True);marker=base/('ATTEMPT_'+boot+'.json')
    # Any previous attempt remains reserved even across reboot until human review.
    if list(base.glob('ATTEMPT_*.json')):raise RuntimeError('Previous attempt retained. Do not repeat or delete marker; return results for review.')
    print('请确认：领航者ZYNQ7020与正点原子OV5640接口未变，原官方相机已正常关闭，板卡独占，本Notebook使用独立新内核。')
    print('本次将加载新固件一次，按官方800x480模式采一帧，绑定721项输入，PL计算一步并保存全部45669状态。')
    print('外部时序/颜色尚未实测；官方同步驱动调用可能阻塞，无自动超时恢复。全状态数值比对在电脑侧进行。')
    if ask('确认上述条件并授权本次操作，输入 运行官方完整网络：')!='运行官方完整网络':
        print('已取消，无加载、MMIO、DDR分配或神经计算。');return None
    # Exclusive creation + fsync before native code, overlay or MMIO.
    save_json(marker,dict(boot_id=boot,identity=identity,operator_confirmation='运行官方完整网络',exclusive=True,
        monotonic_ns=time.monotonic_ns(),automatic_retry=False))
    if execute_fn is None:
        from board_run import execute
        execute_fn=execute
    try:out=execute_fn(root,base,authorized=True,boot_id=boot)
    except BaseException as exc:
        print('LINE11_OFFICIAL_STOP',repr(exc))
        print('下载已打印的结果ZIP；无ZIP则提供最后输出。保留内核与缓冲区，不重跑、不复位。');return None
    print('LINE11_OFFICIAL_STATUS ONE_FRAME_ONE_STEP_SAVED_ORACLE_PENDING')
    print('请下载结果ZIP交回核查全部状态。保留此内核，不重复运行。')
    try:
        if (out/'camera.png').exists():
            from IPython.display import display,Image
            display(Image(filename=str(out/'camera.png')))
    except Exception as exc:print('Preview unavailable; saved records remain:',repr(exc))
    return out

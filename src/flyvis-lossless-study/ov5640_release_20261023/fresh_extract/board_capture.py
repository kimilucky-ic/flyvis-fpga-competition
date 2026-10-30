"""Future human-operated board entry. Import/default is inert; never run by packaging/tests."""
import json,platform,time,uuid,shutil
from pathlib import Path
from capture_binding import save_json
_RETAINED=globals().get('_RETAINED',{})

def check_conditions(c):
    required=('pinmap_and_orientation_verified','camera_io_3v3_verified',
      'module_oscillator_24MHz_verified','PS_reference_33_333333MHz_verified',
      'PS_HP0_HP1_64bit_verified','conditional_DVP_timing_and_nonCCIO_exception_accepted',
      'SCCB_pullups_voltage_and_rise_time_checked','exclusive_board_ownership')
    if c.get('part')!='xc7z020clg400-2' or c.get('board_family')!='Leader ZYNQ-7020':raise ValueError('Wrong board/part')
    if not isinstance(c.get('baseboard_revision'),str) or not c['baseboard_revision'].strip():raise ValueError('Actual baseboard revision required')
    if any(c.get(k) is not True for k in required):raise ValueError('Unconfirmed physical conditions; no board imports/actions')
    if c.get('channel_order') not in ('RGB','BGR','GBR'):raise ValueError('Explicit byte order required')

def nominal_clock(registers):
    clk,pll,locked=[int(registers[k]) for k in ('FPGA0_CLK_CTRL','IO_PLL_CTRL','PLL_STATUS')]
    if ((clk>>4)&3)!=0 or ((pll>>12)&127)!=30 or ((clk>>8)&63)!=5 or ((clk>>20)&63)!=2:
        raise RuntimeError('Unexpected PLL/dividers; no automatic clock rewrite')
    if pll&0x1b or not locked&4:raise RuntimeError('IO PLL reset/powerdown/bypass/unlocked')
    return 33.333333*30/5/2

def run(output_parent,conditions,*,authorize_load_and_one_step=False):
    if authorize_load_and_one_step is not True:raise RuntimeError('No board authorization; stopped before imports')
    if _RETAINED:raise RuntimeError('Prior session retained; no reload/retry in this kernel')
    check_conditions(conditions)
    root=Path(__file__).resolve().parent
    from offline_check import verify
    identity=verify(root)
    if platform.machine()!='armv7l':raise RuntimeError('ARMv7 PYNQ target required')
    import pynq
    if not str(pynq.__version__).startswith('2.7.'):raise RuntimeError('PYNQ2.7 required')
    out=Path(output_parent)/('LINE11_OV5640_'+uuid.uuid4().hex);out.mkdir(parents=True,exist_ok=False)
    if shutil.disk_usage(str(out)).free<32*1024*1024:raise RuntimeError('Need32MiB free result space before hardware actions')
    context=dict(evidence='OPERATOR_PHYSICAL_RUN_UNATTESTED',board_result=False,identity=identity,
      conditions=conditions,run_id=out.name,automatic_retry=False,phase='PREPARE',
      initial_state_readback='NOT_SUPPORTED; restore-clean plus post-step full-state audit',
      boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),pynq_version=pynq.__version__)
    save_json(out/'RUN_CONTEXT.json',context)
    owner={};_RETAINED[out.name]=owner
    try:
        from ddr_memory import pynq_allocator_and_barrier,OwnedDdr
        # Native helper compiled before programming; no ARM compilation was done on the PC.
        allocate,barrier=pynq_allocator_and_barrier(out/'native',operator_authorized=True)
        phase='LOAD';save_json(out/'LOAD_INTENT.json',dict(phase=phase,bit_sha256=identity['bit_sha256']))
        overlay=pynq.Overlay(str(root/'flyvis_ov5640.bit'),download=False);owner['overlay']=overlay
        overlay.download() # ONE human-authorized load. Never retried.
        phase='CLOCK'
        slcr=pynq.MMIO(0xf8000000,0x1000)
        regs={k:slcr.read(a) for k,a in [('FPGA0_CLK_CTRL',0x170),('IO_PLL_CTRL',0x108),('PLL_STATUS',0x10c)]}
        save_json(out/'CLOCK_REGISTERS.json',dict(regs,reference_MHz=33.333333,
           PYNQ_reported_FCLK0_MHz=float(pynq.Clocks.fclk0_mhz),evidence='REGISTER_DERIVED_NOMINAL_NOT_MEASURED'))
        nominal=nominal_clock(regs)
        from ddr_control import DdrControl,BASE
        from bounded_io import Iic,CameraControl,OneFrameVdma
        from camera_memory import CameraDdr
        from capture_binding import CapturePool
        from sensor_init import initialize
        from single_frame import capture_and_step
        phase='FRESH_ABI'
        control=DdrControl(pynq.MMIO(BASE,4096));owner['control']=control
        if any(control._r(a) for a in (0x10,0x14,0x18,0x24)):raise RuntimeError('Fresh unused neural ABI required')
        camera=CameraControl(pynq.MMIO(0x41200000,4096));camera.require_stopped()
        vdma=pynq.MMIO(0x43000000,4096)
        if not vdma.read(0x34)&1 or vdma.read(0x34)&0xfff0:raise RuntimeError('VDMA must be clean/halted')
        phase='SENSOR_INIT'
        bus=Iic(pynq.MMIO(0x41600000,4096),timeout=.25)
        writes=initialize(bus.read16,bus.write16,time.sleep)
        expected={0x3035:0x11,0x3036:0x5a,0x3037:0x13,0x3108:0x01,0x3824:0x02,
                  0x460c:0x22,0x4300:0x61,0x501f:0x01,0x4740:0x20,0x3808:2,0x3809:128,0x380a:1,0x380b:224}
        observed={hex(a):bus.read16(a) for a in expected}
        save_json(out/'SENSOR_READBACK.json',dict(writes=writes,observed=observed,expected={hex(a):v for a,v in expected.items()}))
        if any(observed[hex(a)]!=v for a,v in expected.items()):raise RuntimeError('Sensor clock/polarity/size mismatch')
        phase='ALLOCATE_RESTORE'
        neural=OwnedDdr(allocate,barrier,1);owner['neural']=neural
        cam=CameraDdr(allocate,barrier,[(neural.base,neural.base+neural.size)]);owner['camera']=cam
        save_json(out/'DDR_OWNERSHIP.json',dict(neural_base=neural.base,neural_bytes=neural.size,camera_base=cam.base,camera_bytes=cam.size,camera_addresses=cam.addresses))
        neural.pin_before_configure();cam.pin()
        control.restore_initial();control.configure(neural.base,neural.size,1,int(out.name[-8:],16))
        pool=CapturePool(921600);owner['pool']=pool
        capture=OneFrameVdma(vdma,pool,cam.addresses,[(cam.base,cam.base+cam.size)],[(neural.base,neural.base+neural.size)],cam.copy,camera)
        owner['capture']=capture;phase='CAPTURE_AND_ONE_STEP'
        result=capture_and_step(capture,pool,control,neural,out/'bound',conditions['channel_order'])
        camera.require_stopped()
        if control._r(0x10)&1 or not control._r(0x10)&8 or control._r(0x14)!=1 or control._r(0x24):raise RuntimeError('Final neural idle/full/count/fault mismatch')
        if not vdma.read(0x34)&1 or vdma.read(0x34)&0xfff0:raise RuntimeError('Final VDMA not clean halted')
        result.update(nominal_FCLK0_MHz=nominal,allocations_retained=True,physical_clock_measured=False,
          camera_color_order_verified=conditions.get('channel_order_colorbar_verified') is True)
        save_json(out/'RESULT.json',result)
    except BaseException as exc:
        if 'control' in owner:owner['control'].failed=True
        if 'capture' in owner:owner['capture'].failed=True
        try:save_json(out/'IN_DOUBT.json',dict(phase=locals().get('phase','PREPARE'),error=repr(exc),automatic_retry=False,
            instruction='KEEP_KERNEL_AND_ALLOCATIONS; DO_NOT_RESET_RELOAD_RETRY_OR_FREE'))
        except OSError:pass
        raise
    finally:
        # Archive is for evidence, never cleanup of the armed buffers/kernel.
        try:shutil.make_archive(str(out)+'_RESULT','zip',str(out))
        except Exception as exc:print('Result ZIP failed; preserve directory:',str(out),repr(exc))
        print('LINE11_RESULT_DIRECTORY',out)
    return out

if __name__=='__main__':
    from offline_check import verify
    print(json.dumps(verify(Path(__file__).resolve().parent),indent=2))

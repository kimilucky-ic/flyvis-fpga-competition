"""One diagnostic of the retained failed run. No resets, writes or bus transfers.

Run ONLY in the existing failed Notebook kernel; a new kernel deliberately stops.
Do not read RX data FIFO (0x10c), which would consume data. Read snapshots are
sequential observations, not an atomic snapshot or a bus waveform measurement.
"""
import json
from pathlib import Path
import sys
import time

EXPECTED_BOOT='14e5f2cb-f4d0-454e-813d-c371ca86e63b'
EXPECTED_RUN='LINE11_OV5640_bbfe25b4b55f4a19b78ccd393bbc3448'
EXPECTED_PACKAGE='391b2cc3673549b191eaf8f1566ae863'
REGISTERS=(('ISR',0x20),('CR',0x100),('SR',0x104),('TX_OCCUPANCY',0x114),('RX_OCCUPANCY',0x118),('RX_DEPTH',0x120))


def inspect(read32,clock=time.monotonic_ns):
    raw={};intervals={};begin=clock()
    for name,offset in REGISTERS:
        before=clock();value=read32(offset);after=clock()
        if not isinstance(value,int) or not 0<=value<=0xffffffff:raise ValueError('Not a32bit register: '+name)
        raw[name]=value;intervals[name]=(after-before)/1e6
    sr,irq=raw['SR'],raw['ISR']
    return dict(schema='flyvis-ov5640-failed-iic-readonly/v1',raw_registers=raw,
        raw_hex={k:hex(v) for k,v in raw.items()},read_host_intervals_ms=intervals,total_host_ms=(clock()-begin)/1e6,
        timing_definition='Host intervals include Python scheduling and MMIO; not isolated AXI latency',
        sequential_snapshot=True,observations=dict(bus_busy=bool(sr&4),TX_FIFO_empty=bool(sr&0x80),
          RX_FIFO_empty=bool(sr&0x40),TX_FIFO_full=bool(sr&0x10),
          controller_enabled=bool(raw['CR']&1),irq_arbitration_lost=bool(irq&1),
          irq_tx_error=bool(irq&2),irq_TX_empty=bool(irq&4),irq_bus_not_busy=bool(irq&0x10)),
        register_writes=0,RX_FIFO_data_reads=0,overlay_loads=0,resets=0,DDR_allocations=0,camera_starts=0,neural_steps=0,
        meaning='Current retained failure status only; no retry, recovery or PASS claim')


def run(*,operator_authorized=False):
    if operator_authorized is not True:raise RuntimeError('Manual readonly authorization required')
    boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    if boot!=EXPECTED_BOOT:raise RuntimeError('Boot changed; stopped before MMIO. Do not reuse this diagnosis.')
    board=sys.modules.get('board_capture')
    if board is None:raise RuntimeError('Use the ORIGINAL failed Notebook kernel; no MMIO attempted')
    if Path(board.__file__).parent.name!=EXPECTED_PACKAGE:raise RuntimeError('Wrong retained package; no MMIO attempted')
    owner=board._RETAINED.get(EXPECTED_RUN)
    if not owner or 'control' not in owner or not owner['control'].failed:
        raise RuntimeError('Matching failed owner absent; no MMIO attempted')
    out=Path(board.__file__).parent.parent/'results'/EXPECTED_RUN
    failure=json.loads((out/'IN_DOUBT.json').read_text())
    if failure.get('phase')!='SENSOR_INIT':raise RuntimeError('Different failed phase; no MMIO attempted')
    if (out/'DDR_OWNERSHIP.json').exists() or (out/'RESULT.json').exists():
        raise RuntimeError('Run progressed beyond known failure; no MMIO attempted')
    import pynq
    mmio=pynq.MMIO(0x41600000,4096)
    result=inspect(lambda offset:int(mmio.read(offset)))
    result.update(boot_id=boot,run_id=EXPECTED_RUN,controller_base='0x41600000')
    return result


if __name__=='__main__':
    print('仅用于刚才失败的原Notebook内核；不发送IIC事务、不复位、不重载、不采图。')
    if input('确认当前板卡没有其他操作，输入 检查：')!='检查':raise RuntimeError('Cancelled; no MMIO')
    print('OV5640_IIC_FAILURE_READ_ONLY',json.dumps(run(operator_authorized=True),ensure_ascii=False))

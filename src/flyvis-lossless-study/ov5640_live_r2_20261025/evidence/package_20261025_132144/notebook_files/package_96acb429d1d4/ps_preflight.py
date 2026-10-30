"""One-time PS preflight. Default import does not import PYNQ or access devices.

UG585: FPGA_RST_CTRL 0xF8000240; HP0/1 AFI_RDCHAN_CTRL offsets
0x0 and AFI_WRCHAN_CTRL 0x14, bit0=32BitEn (0=64bit).
Conservative admission: all FPGA reset-control bits must already be zero.
An unknown/nonzero reset state is reported, never changed or retried.
"""


def inspect(read32):
    """Injected read-only callable; no writes, allocations, loads, or STEP."""
    raw = {}

    def read(address):
        value = read32(address)
        if not isinstance(value, int) or not 0 <= value <= 0xffffffff:
            raise ValueError('PS_READ_NOT_UINT32')
        raw[hex(address)] = value
        return value

    reset = read(0xf8000240)
    result = dict(schema='flyvis-ov5640-ps-readonly/v1', raw_registers=raw,
                  register_writes=0, overlay_loads=0, resets=0, DDR_allocations=0,
                  camera_starts=0, neural_steps=0, automatic_retry=False,
                  physical_clock_measured=False, HP0_HP1_64bit_verified=False)
    if reset != 0:
        result.update(status='STOP_RESET_STATE_NOT_PROVEN_RELEASED',
                      meaning='HP registers not accessed; reset untouched. Not proof of broken hardware.')
        return result
    widths = {}
    for name, base in [('HP0',0xf8008000), ('HP1',0xf8009000)]:
        rd, wr = read(base), read(base+0x14)
        widths[name] = dict(read_bits=32 if rd & 1 else 64, write_bits=32 if wr & 1 else 64)
    result['widths'] = widths
    result['HP0_HP1_64bit_verified'] = all(v['read_bits']==v['write_bits']==64 for v in widths.values())
    result['status'] = 'PASS_CURRENT_HP_WIDTH_ONLY' if result['HP0_HP1_64bit_verified'] else 'STOP_HP_WIDTH_MISMATCH'
    result['meaning'] = 'Current PS register evidence only; not camera, clock measurement or neural acceptance.'
    return result


def run(*, operator_authorized=False):
    if operator_authorized is not True:
        raise RuntimeError('Human authorization required even for hardware register reads')
    from pathlib import Path
    import platform
    if platform.machine() != 'armv7l' or b'xlnx,zynq-7000' not in Path('/proc/device-tree/compatible').read_bytes():
        raise RuntimeError('Zynq7000 ARMv7 board required')
    import pynq
    if not str(pynq.__version__).startswith('2.7.'):
        raise RuntimeError('Prepared for PYNQ2.7 only')
    pages = {}

    def read(address):
        base = address & ~0xfff
        if base not in pages:
            pages[base] = pynq.MMIO(base,0x1000)
        return int(pages[base].read(address-base))

    result = inspect(read)
    result['boot_id'] = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    return result

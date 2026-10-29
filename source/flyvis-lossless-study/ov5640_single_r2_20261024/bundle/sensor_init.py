"""Official Vitis register sequence, injected checked bus, no implicit hardware."""
import json
from pathlib import Path

def initialize(read16, write16, sleep, *, width=640, height=480, total_width=1800, total_height=1000):
    if not (0<width<total_width<=65535 and 0<height<total_height<=65535):
        raise ValueError('invalid frame totals')
    # Preserve source initial 20ms delay and ID order; no writes on mismatch.
    sleep(.020)
    if read16(0x300b) | (read16(0x300a)<<8) != 0x5640:
        raise RuntimeError('OV5640 ID mismatch; no initialization writes')
    values={'cmos_h_pixel':width,'cmos_v_pixel':height,'total_h_pixel':total_width,'total_v_pixel':total_height}
    def value(expr):
        if expr.startswith('0x'): return int(expr,16)
        for name,v in values.items():
            if expr.startswith(name):
                return v>>8 if '>>' in expr else v&255
        raise ValueError('unknown source expression '+expr)
    actions=json.loads((Path(__file__).parent/'init_actions.json').read_text())
    writes=0
    for op,*args in actions[1:]:
        if op=='usleep': sleep(int(args[0])/1e6)
        else:
            # Transport must raise on NACK/timeout; False explicitly rejects.
            if write16(value(args[0]),value(args[1])) is False:
                raise RuntimeError('sensor write rejected; no retry')
            writes+=1
    return writes

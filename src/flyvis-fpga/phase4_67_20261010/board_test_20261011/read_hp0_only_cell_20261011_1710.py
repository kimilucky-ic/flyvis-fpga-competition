import os
import mmap
import json
import uuid
import platform
import numpy as np
from pathlib import Path

hp = {"status": "PENDING", "registers": {}, "register_writes": 0}

def read_ps(address):
    if address not in (0xF8000240, 0xF8008000, 0xF8008014):
        raise ValueError("Address outside PS read-only allowlist")
    base = address & ~(mmap.PAGESIZE - 1)
    fd = os.open("/dev/mem", os.O_RDONLY | os.O_SYNC)
    try:
        with mmap.mmap(fd, mmap.PAGESIZE, access=mmap.ACCESS_READ,
                       offset=base) as memory:
            words = np.frombuffer(memory, dtype="<u4", count=1,
                                  offset=address - base)
            try:
                value = int(words[0])
            finally:
                del words
    finally:
        os.close(fd)
    hp["registers"]["0x%08X" % address] = "0x%08X" % value
    return value

try:
    compatible = Path("/sys/firmware/devicetree/base/compatible").read_bytes()
    if platform.machine() != "armv7l" or b"xlnx,zynq-7000" not in compatible:
        raise RuntimeError("Zynq-7000 host identity unresolved")
    hp["boot_id"] = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    reset = read_ps(0xF8000240)
    if reset & 0x01F33F00:
        hp["status"] = "STOP_RESET_PRECONDITION_HP0_NOT_READ"
    else:
        rd = read_ps(0xF8008000)
        wr = read_ps(0xF8008014)
        if read_ps(0xF8000240) != reset:
            raise RuntimeError("Reset register changed during check")
        hp["hp0_read_width_bits"] = 32 if rd & 1 else 64
        hp["hp0_write_width_bits"] = 32 if wr & 1 else 64
        hp["status"] = ("READ_ONLY_HP0_64BIT_OBSERVED"
                        if not (rd | wr) & 1 else "STOP_HP0_WIDTH_MISMATCH")
except Exception as error:
    hp["status"] = "STOP_READ_ONLY_CHECK_ERROR"
    hp["error"] = "%s: %s" % (type(error).__name__, error)

record = Path("hp0_readonly_" + uuid.uuid4().hex[:8] + ".json")
with record.open("x") as stream:
    json.dump(hp, stream, indent=2)
print(json.dumps(hp, indent=2))
print("Saved:", record)

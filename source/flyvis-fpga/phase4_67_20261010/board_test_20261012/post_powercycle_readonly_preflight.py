from pathlib import Path
import json
import mmap
import os
import struct
import subprocess

EXPECTED_BOOT = "2c7cec1e-d7ba-4b07-8283-ebb6f3a6b010"
report = {
    "status": "READ_ONLY_POST_POWER_CYCLE",
    "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
    "registers": {}, "register_reads": 0, "register_writes": 0,
    "pl_axi_reads": 0, "pl_downloads": 0, "pl_requests": 0,
}
if report["boot_id"] != EXPECTED_BOOT:
    raise RuntimeError("STOP: boot changed again; report the new boot before proceeding")

def read_ps(address):
    if address not in (0xF8000240, 0xF8008000, 0xF8008014):
        raise ValueError("Address outside the PS-only read allowlist")
    base = address & ~(mmap.PAGESIZE - 1)
    fd = os.open("/dev/mem", os.O_RDONLY | os.O_SYNC)
    try:
        with mmap.mmap(fd, mmap.PAGESIZE, access=mmap.ACCESS_READ, offset=base) as memory:
            value = struct.unpack_from("<I", memory, address - base)[0]
    finally:
        os.close(fd)
    report["register_reads"] += 1
    report["registers"]["0x%08X" % address] = "0x%08X" % value
    return value

try:
    compatible = Path("/sys/firmware/devicetree/base/compatible").read_bytes()
    if b"xlnx,zynq-7000" not in compatible:
        raise RuntimeError("Zynq-7000 host identity unresolved")
    reset = read_ps(0xF8000240)
    if reset & 0x01F33F00:
        report["status"] = "STOP_RESET_PRECONDITION_HP0_NOT_READ"
    else:
        rd = read_ps(0xF8008000)
        wr = read_ps(0xF8008014)
        if read_ps(0xF8000240) != reset:
            raise RuntimeError("Reset register changed during the read-only check")
        report["hp0_read_width_bits"] = 32 if rd & 1 else 64
        report["hp0_write_width_bits"] = 32 if wr & 1 else 64
        report["status"] = (
            "READ_ONLY_CURRENT_BOOT_HP0_64BIT_OBSERVED"
            if not ((rd | wr) & 1) else "STOP_CURRENT_BOOT_HP0_WIDTH_MISMATCH"
        )
except Exception as error:
    report["status"] = "STOP_READ_ONLY_PS_CHECK_ERROR"
    report["error"] = "%s: %s" % (type(error).__name__, error)

for name in ("name", "state", "status"):
    path = Path("/sys/class/fpga_manager/fpga0") / name
    try:
        report["fpga_manager_" + name] = path.read_text().strip() if path.is_file() else "MISSING"
    except OSError as error:
        report["fpga_manager_" + name] = "UNREADABLE: " + str(error)

report["manager_state_is_not_bit_identity_attestation"] = True
print(json.dumps(report, indent=2))

# Read Linux logs only. No recovery, service restart or sudo command.
for command in (
    ["dmesg"],
    ["journalctl", "-b", "-1", "-k", "--no-pager", "-n", "35"],
):
    print("\nREAD_ONLY_LOG:", " ".join(command))
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, timeout=5)
        lines = result.stdout.splitlines()
        if command[0] == "dmesg":
            terms = ("fpga", "devcfg", "xlnx", "zynq", "mmc", "ext4", "error", "panic", "watchdog", "xrt")
            lines = [line for line in lines if any(term in line.lower() for term in terms)]
        print("\n".join(lines[-60:]) or "NO_LOG_TEXT")
        if result.stderr:
            print(result.stderr[-3000:])
        print("RETURN_CODE:", result.returncode)
    except (OSError, subprocess.TimeoutExpired) as error:
        print("LOG_UNAVAILABLE:", str(error))

print("\nSTOP_HERE: READ_ONLY; NO BIT LOAD, HLS START OR RETRY.")

"""Prepared R3 load phase. Human authorization is deliberately empty.

Run in a new Notebook only after the human authorizes this specific reset-corrected
attempt. It loads once, persists stages, and stops without HLS register access.
Original firmware, release software and the old evidence session are preserved.
"""
CONFIRM = ""
REQUIRED = "AUTHORIZE_RESETFIX_LOAD_ONCE_AND_ROW0_ONCE_BOOT_894292a3"
if CONFIRM != REQUIRED:
    raise RuntimeError("STOP: R3 exact load and row0 authorization is required")

from argparse import Namespace
import hashlib
import json
import os
import mmap
import struct
from pathlib import Path
import sys
import time

PACKAGE = Path("/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1/unpacked_resetfix_6d686a21b53a4303821311d7395becdd/pynq_v1_resetfix_20261012_191002")
RELEASE = PACKAGE / "release"
OLD_SESSION = Path("/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1/unpacked_cd91d2f5cffb47e3a400d1dbae5c7854/row0_session_ae9612d9da4947278c77c3b520ce874a")
R3 = PACKAGE.parent / "row0_resetfix_894292a3_attempt3"
BOOT = "894292a3-1b60-4abf-aba3-e7b18b9e75c8"
BIT_SHA = "23cf5da15db221f399b54cae95e341e6a90a699c88d321d0a883aecca15f7569"
HWH_SHA = "3ea3f1e27c7b214e0f7a965455799875cbae94fb87bee6455a58ecbed4813f7d"
MANIFEST_SHA = "90e522246d99322e574c33ec5a6378a6e35660eb1130079198a83313fda2c81f"
SOFTWARE = {
    "first_board_step.py": "f1641b9d79b120f37aedf1bc59f3c9aa3391daa02952e11fc242051ba2e6c6c8",
    "flyvis_v1_evidence_driver.py": "11ba472f6a97c83d213226ebe49868a1b3635fb80a10a9fb6ca519a4feedf6b8",
    "flyvis_v1_driver.py": "832352f8c4ba09cbe712f127cd59bb808fe1efec34722ea2369f3805632f5a50",
}

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def sync_dir(path):
    fd = os.open(str(path), os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)

def durable_file(path, raw):
    with Path(path).open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    sync_dir(Path(path).parent)

def durable_json(path, obj):
    durable_file(path, (json.dumps(obj, indent=2) + "\n").encode("utf-8"))

if Path("/proc/sys/kernel/random/boot_id").read_text().strip() != BOOT:
    raise RuntimeError("STOP: boot changed since resetfix file verification")
if sys.executable != "/usr/local/share/pynq-venv/bin/python3":
    raise RuntimeError("STOP: different Notebook runtime")
if digest(RELEASE / "release_manifest.json") != MANIFEST_SHA:
    raise RuntimeError("STOP: sealed release manifest differs")
for name, expected in SOFTWARE.items():
    if digest(RELEASE / "pynq" / name) != expected:
        raise RuntimeError("STOP: sealed software differs: " + name)
if digest(OLD_SESSION / "board_review.json") != "043b0b5f28d804ecbc1e23de331adc8cc9f9559a813a9c643de1b0cf3f1b9b48":
    raise RuntimeError("STOP: original review unavailable or changed")

R3.mkdir(exist_ok=False)
sync_dir(R3.parent)
ps_report = {"boot_id": BOOT, "registers": {}, "register_reads": 0,
             "register_writes": 0, "pl_axi_reads": 0, "pl_downloads": 0}
def read_ps(address):
    if address not in (0xF8000240, 0xF8008000, 0xF8008014):
        raise RuntimeError("STOP: PS read outside allowlist")
    fd = os.open("/dev/mem", os.O_RDONLY | os.O_SYNC)
    base = address & ~(mmap.PAGESIZE - 1)
    try:
        with mmap.mmap(fd, mmap.PAGESIZE, access=mmap.ACCESS_READ, offset=base) as memory:
            value = struct.unpack_from("<I", memory, address - base)[0]
    finally:
        os.close(fd)
    ps_report["register_reads"] += 1
    ps_report["registers"]["0x%08X" % address] = "0x%08X" % value
    return value

try:
    reset = read_ps(0xF8000240)
    if reset & 0x01F33F00:
        raise RuntimeError("STOP: PS reset precondition failed")
    rd, wr = read_ps(0xF8008000), read_ps(0xF8008014)
    if read_ps(0xF8000240) != reset or (rd | wr) & 1:
        raise RuntimeError("STOP: unstable reset or HP0 is not 64-bit")
    ps_report.update({"status": "READ_ONLY_CURRENT_BOOT_HP0_64BIT_OBSERVED",
                      "hp0_read_width_bits": 64, "hp0_write_width_bits": 64})
except BaseException as error:
    ps_report.update({"status": "STOP_READ_ONLY_PS_CHECK_ERROR", "error": repr(error)})
    durable_json(R3 / "ps_precheck.json", ps_report)
    raise
durable_json(R3 / "ps_precheck.json", ps_report)
print("00_CURRENT_BOOT_PS_READ_ONLY", json.dumps(ps_report), flush=True)

review = json.loads((OLD_SESSION / "board_review.json").read_text())
review.update({
    "boot_id": BOOT,
    "bit_sha256": BIT_SHA, "hwh_sha256": HWH_SHA,
    "release_manifest_sha256": MANIFEST_SHA,
    "human_load_authorization": CONFIRM,
    "hp0_observation_scope": "CURRENT_BOOT_PS_ONLY_4_READS; NO REGISTER WRITES",
    "hp0_observation_boot_id": BOOT,
    "hp0_measured_in_current_boot": True,
    "hp0_registers": ps_report["registers"],
    "r3_scope": "ONE_RESETFIX_LOAD_THEN_STOP; ROW0_ONLY_IN_A_SEPARATE_MANUAL_CELL_AFTER_LOAD_RESULT_REVIEW",
    "video_reference": "R3_OPERATOR_RECORDING_PENDING; video file and SHA not supplied",
})
durable_json(R3 / "board_review.json", review)
args = Namespace(release_dir=RELEASE, board_review=R3 / "board_review.json",
                 authorize_bit_sha256=BIT_SHA, authorize_hwh_sha256=HWH_SHA,
                 authorize_review_sha256=digest(R3 / "board_review.json"))
sys.path.insert(0, str(RELEASE / "pynq"))
import first_board_step
import flyvis_v1_driver
import flyvis_v1_evidence_driver
for name, module in (("first_board_step.py", first_board_step),
                     ("flyvis_v1_driver.py", flyvis_v1_driver),
                     ("flyvis_v1_evidence_driver.py", flyvis_v1_evidence_driver)):
    if Path(module.__file__).resolve() != (RELEASE / "pynq" / name).resolve():
        raise RuntimeError("STOP: different cached module: " + name)
manifest, bit, hwh, request, oracle, fixture, review = first_board_step.review_before_load(args)
durable_file(R3 / "request_i32le.bin", request.tobytes())
durable_file(R3 / "integer_oracle_i32le.bin", oracle.tobytes())
durable_json(R3 / "LOAD_ATTEMPT_CONSUMED.json", {
    "boot_id": BOOT, "authorization": CONFIRM,
    "bit_sha256": BIT_SHA, "hwh_sha256": HWH_SHA,
    "request_sha256": digest(R3 / "request_i32le.bin"),
    "oracle_sha256": digest(R3 / "integer_oracle_i32le.bin"),
    "scope": "LOAD_ONCE; ROW0_ONCE_ONLY_AFTER_MANUAL_PHASE_TRANSITION; NO_RETRY_NO_COMMIT",
})

def phase(name, **details):
    record = {"phase": name, "boot_id": BOOT, "monotonic_s": time.monotonic(), **details}
    durable_json(R3 / (name + ".json"), record)
    print(name, json.dumps(details), "EVIDENCE_DIR:", R3, flush=True)

try:
    phase("01_BEFORE_PYNQ_IMPORT")
    from pynq import Overlay
    phase("02_BEFORE_METADATA_PARSE")
    overlay = Overlay(str(bit), download=False)
    ip = overlay.ip_dict.get("flyvis_h", {})
    if (ip.get("type") != "xilinx.com:hls:flyvis_t5c_source_raw:1.0"
            or int(ip.get("phys_addr", -1)) != 0x43C00000
            or int(ip.get("addr_range", 0)) != 0x10000):
        raise RuntimeError("STOP: HWH HLS identity/address/range differs")
    phase("03_BEFORE_OVERLAY_DOWNLOAD", bit_sha256=BIT_SHA, hwh_sha256=HWH_SHA,
          clock_dict=overlay.clock_dict)
    load_started = time.monotonic()
    overlay.download()  # Exactly one authorized overlay download.
    phase("04_OVERLAY_DOWNLOAD_RETURNED", elapsed_s=time.monotonic() - load_started)
    if not overlay.is_loaded():
        raise RuntimeError("STOP: PYNQ does not record the requested overlay as loaded")
    load_record = {
        "status": "LOAD_ONLY_RETURNED_ROW0_NOT_STARTED", "boot_id": BOOT,
        "bit_sha256": BIT_SHA, "hwh_sha256": HWH_SHA,
        "bitfile_name": str(overlay.bitfile_name), "timestamp": str(overlay.timestamp),
        "pynq_is_loaded": True, "pl_requests": 0, "hls_mmio_reads": 0,
        "pynq_internal_shutdown_register_access": "NOT_COUNTED; standard Overlay.download may manage previous shutdown IPs",
        "board_execution_proven": False,
        "attestation_scope": "PYNQ runtime identity; not cryptographic PL readback",
    }
    durable_json(R3 / "load_result.json", load_record)
    phase("05_LOAD_ONLY_COMPLETE", **load_record)
    print("STOP_HERE: RETURN_THIS_OUTPUT; DO_NOT_START_ROW0_YET.", flush=True)
except BaseException as error:
    phase("99_LOAD_FAULT", error=repr(error), no_retry=True)
    raise

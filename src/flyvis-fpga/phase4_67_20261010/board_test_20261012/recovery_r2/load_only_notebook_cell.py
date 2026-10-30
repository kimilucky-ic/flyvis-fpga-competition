"""Prepared R2 load phase. Human authorization is deliberately empty.

Run in a new Notebook only after the human authorizes this specific second
attempt. It loads once, persists stages, and stops without HLS register access.
Original firmware, release software and the old evidence session are preserved.
"""
CONFIRM = ""
REQUIRED = "AUTHORIZE_BANKFIX_RELOAD_ONCE_AND_ROW0_ONCE_BOOT_2c7cec1e"
if CONFIRM != REQUIRED:
    raise RuntimeError("STOP: R2 exact load and row0 authorization is required")

from argparse import Namespace
import hashlib
import json
import os
from pathlib import Path
import sys
import time

PACKAGE = Path("/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1/unpacked_cd91d2f5cffb47e3a400d1dbae5c7854/pynq_v1_single_step_20261011_1620")
RELEASE = PACKAGE / "release"
OLD_SESSION = PACKAGE.parent / "row0_session_ae9612d9da4947278c77c3b520ce874a"
R2 = PACKAGE.parent / "row0_recovery_2c7cec1e_attempt2"
BOOT = "2c7cec1e-d7ba-4b07-8283-ebb6f3a6b010"
BIT_SHA = "e45bbe0d7795ee835fb7486444199460733196373ea4f363a8ff1c93431b7383"
HWH_SHA = "fb40c671c06f41923e4cd41cff055c0b549e2db69bbfcee05810960a95885d82"
MANIFEST_SHA = "54a40c9951388ccb4e6d4cc89da7c0f93f039cdf14b247dfb4278ba3d4def9c6"
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
    raise RuntimeError("STOP: boot changed since the new PS preflight")
if sys.executable != "/usr/local/share/pynq-venv/bin/python3":
    raise RuntimeError("STOP: different Notebook runtime")
if digest(RELEASE / "release_manifest.json") != MANIFEST_SHA:
    raise RuntimeError("STOP: sealed release manifest differs")
for name, expected in SOFTWARE.items():
    if digest(RELEASE / "pynq" / name) != expected:
        raise RuntimeError("STOP: sealed software differs: " + name)
if digest(OLD_SESSION / "board_review.json") != "043b0b5f28d804ecbc1e23de331adc8cc9f9559a813a9c643de1b0cf3f1b9b48":
    raise RuntimeError("STOP: original review unavailable or changed")

review = json.loads((OLD_SESSION / "board_review.json").read_text())
review.update({
    "boot_id": BOOT,
    "human_load_authorization": CONFIRM,
    "hp0_observation_scope": "CURRENT_BOOT_USER_READ_ONLY_OUTPUT: read64/write64, reset0, 4 PS reads, no writes",
    "hp0_observation_boot_id": BOOT,
    "hp0_measured_in_current_boot": True,
    "hp0_registers": {"0xF8000240": "0x00000000", "0xF8008000": "0x00000000", "0xF8008014": "0x00000F00"},
    "r2_scope": "ONE_LOAD_THEN_STOP; ROW0_ONLY_IN_A_SEPARATE_MANUAL_CELL_AFTER_LOAD_RESULT_REVIEW",
    "video_reference": "R2_OPERATOR_RECORDING_PENDING; video file and SHA not supplied",
})
R2.mkdir(exist_ok=False)
sync_dir(R2.parent)
durable_json(R2 / "board_review.json", review)
args = Namespace(release_dir=RELEASE, board_review=R2 / "board_review.json",
                 authorize_bit_sha256=BIT_SHA, authorize_hwh_sha256=HWH_SHA,
                 authorize_review_sha256=digest(R2 / "board_review.json"))
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
durable_file(R2 / "request_i32le.bin", request.tobytes())
durable_file(R2 / "integer_oracle_i32le.bin", oracle.tobytes())
durable_json(R2 / "LOAD_ATTEMPT_CONSUMED.json", {
    "boot_id": BOOT, "authorization": CONFIRM,
    "bit_sha256": BIT_SHA, "hwh_sha256": HWH_SHA,
    "request_sha256": digest(R2 / "request_i32le.bin"),
    "oracle_sha256": digest(R2 / "integer_oracle_i32le.bin"),
    "scope": "LOAD_ONCE; ROW0_ONCE_ONLY_AFTER_MANUAL_PHASE_TRANSITION; NO_RETRY_NO_COMMIT",
})

def phase(name, **details):
    record = {"phase": name, "boot_id": BOOT, "monotonic_s": time.monotonic(), **details}
    durable_json(R2 / (name + ".json"), record)
    print(name, json.dumps(details), "EVIDENCE_DIR:", R2, flush=True)

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
    durable_json(R2 / "load_result.json", load_record)
    phase("05_LOAD_ONLY_COMPLETE", **load_record)
    print("STOP_HERE: RETURN_THIS_OUTPUT; DO_NOT_START_ROW0_YET.", flush=True)
except BaseException as error:
    phase("99_LOAD_FAULT", error=repr(error), no_retry=True)
    raise

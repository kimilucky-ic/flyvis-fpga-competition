"""Prepared operation; execute on the board only after the exact human approval.

The confirmation also asserts the same SD/PYNQ boot image, stable power and
exclusive board use. Physical PCB revisions remain explicitly unknown.
No original firmware, release driver or operating-system image is modified.
"""
CONFIRM = ""  # Filled only after this chat receives the exact human approval.
REQUIRED_CONFIRMATION = "AUTHORIZE_V1_LOAD_ROW0_ONCE_SAME_SD_STABLE_POWER_EXCLUSIVE"
if CONFIRM != REQUIRED_CONFIRMATION:
    raise RuntimeError("STOP: exact human load/row0 approval and operator facts are required")

from argparse import Namespace
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

PACKAGE = Path("/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1/unpacked_cd91d2f5cffb47e3a400d1dbae5c7854/pynq_v1_single_step_20261011_1620")
SESSION = PACKAGE.parent / "row0_session_ae9612d9da4947278c77c3b520ce874a"
RELEASE = PACKAGE / "release"
BOOT = "dbbf5a83-cf0b-4c3a-bd74-3148ff1b90c5"
BIT_SHA = "e45bbe0d7795ee835fb7486444199460733196373ea4f363a8ff1c93431b7383"
HWH_SHA = "fb40c671c06f41923e4cd41cff055c0b549e2db69bbfcee05810960a95885d82"
MANIFEST_SHA = "54a40c9951388ccb4e6d4cc89da7c0f93f039cdf14b247dfb4278ba3d4def9c6"
PACKAGE_MANIFEST_SHA = "e96537356385fd875fee2c225b5638d4c7deafcbc6669992c6aae7a9837f21ca"
REQUEST_SHA = "ea1cb4a5f1d655183cad390ef0226ca138eb77d783f4edf271fb37711d9be8b4"
ORACLE_SHA = "50f212ffd6e47abebc8758b8c48999eb40957aabd0106b467ad4cc47a4f92a00"
SOFTWARE = {
    "first_board_step.py": "f1641b9d79b120f37aedf1bc59f3c9aa3391daa02952e11fc242051ba2e6c6c8",
    "flyvis_v1_evidence_driver.py": "11ba472f6a97c83d213226ebe49868a1b3635fb80a10a9fb6ca519a4feedf6b8",
    "flyvis_v1_driver.py": "832352f8c4ba09cbe712f127cd59bb808fe1efec34722ea2369f3805632f5a50",
}

def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save_new(path, data):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())

if Path("/proc/sys/kernel/random/boot_id").read_text().strip() != BOOT:
    raise RuntimeError("STOP: board rebooted since row0 preparation")
if sys.executable != "/usr/local/share/pynq-venv/bin/python3":
    raise RuntimeError("STOP: notebook Python differs from the prepared runtime")
if (SESSION / "ONE_ATTEMPT_CONSUMED.json").exists():
    raise RuntimeError("STOP: this session already consumed its one attempt; no retry")
if file_sha(PACKAGE / "package_manifest.json") != PACKAGE_MANIFEST_SHA:
    raise RuntimeError("STOP: package manifest changed")
spec = importlib.util.spec_from_file_location("_flyvis_authorized_filecheck", PACKAGE / "board.py")
filecheck = importlib.util.module_from_spec(spec)
spec.loader.exec_module(filecheck)
filecheck.verify_package()  # File reads only; does not run its hardware entry points.
for name, digest in SOFTWARE.items():
    if file_sha(RELEASE / "pynq" / name) != digest:
        raise RuntimeError("STOP: sealed first-step software changed: " + name)
for name, digest in (("request_row0_i32le.bin", REQUEST_SHA),
                     ("integer_oracle_row0_i32le.bin", ORACLE_SHA)):
    if file_sha(SESSION / name) != digest:
        raise RuntimeError("STOP: prepared row0 data changed")

# The required confirmation is the operator assertion for the three current
# facts. It does not turn unknown physical revisions or old HP0 reads into
# new measurements. This scope is recorded explicitly in the review below.
review = {
    "status": "FIRST_STEP_BOARD_PRECHECK_REVIEWED",
    "fpga_part": "xc7z020clg400-2",
    "core_revision": "UNKNOWN; CT7010B/7020B model observed in operator photo",
    "carrier_revision": "UNKNOWN; ATK-DF7010/7020P model observed in operator photo",
    "physical_revision_verified": False,
    "physical_ddr_marking": "PHOTO_READING H5TC4G63EFR; suffix appears RDA",
    "power_verified": True, "boot_mode": "SD_CARD", "exclusive_board_use": True,
    "operator_facts_source": "EXPLICIT_USER_REPLY_AND_REQUIRED_NOTEBOOK_CONFIRMATION",
    "runtime_sources_reviewed": True, "pynq_version": "2.7.0", "boot_id": BOOT,
    "runtime_review_scope": "Carry forward reviewed installed PYNQ2.7 source behavior; sealed launcher checks live package version",
    "hp0_width_bits": 64,
    "hp0_observation_scope": "20261011 user readback, read64/write64; carried forward at user direction; not a current-boot register measurement",
    "hp0_observation_boot_id": "4474a142-fe3e-4f6f-b314-6ed9c5e2c11f",
    "hp0_measured_in_current_boot": False,
    "ddr_preset_reviewed": True,
    "ddr_review_scope": "Hynix geometry/DDR3 compatibility reviewed; current existing SD boot initialized DDR; proposed PL overlay does not execute XSA PS7 DDR/MIO boot init",
    "full_ddr_timing_or_rail_validation": False,
    "first_request_row": 0, "request_count": 1, "commit_authorized": False,
    "bit_sha256": BIT_SHA, "hwh_sha256": HWH_SHA,
    "release_manifest_sha256": MANIFEST_SHA,
    "fixture_comparison_id": "f1229caa438e440afbb21bd532a954b4946d6ec3de1d3e02f80569ae6586e798",
    "request_sha256": REQUEST_SHA, "integer_oracle_sha256": ORACLE_SHA,
    "software_sha256": SOFTWARE,
    "video_reference": "PLANNED_OPERATOR_RECORDING flyvis67_v1_row0_20261012; file and SHA not yet supplied",
    "video_file_independently_reviewed": False,
    "human_load_authorization": CONFIRM,
    "scientific_q22_acceptance": "NOT_GRANTED",
    "true_closed_loop": False,
}
review_path = SESSION / "board_review.json"
save_new(review_path, review)
review_sha = file_sha(review_path)
args = Namespace(release_dir=RELEASE, board_review=review_path,
                 output_dir=SESSION / "run", authorize_bit_sha256=BIT_SHA,
                 authorize_hwh_sha256=HWH_SHA, authorize_review_sha256=review_sha)
sys.path.insert(0, str(RELEASE / "pynq"))
import first_board_step
import flyvis_v1_driver
import flyvis_v1_evidence_driver
for name, module in (("first_board_step.py", first_board_step),
                     ("flyvis_v1_driver.py", flyvis_v1_driver),
                     ("flyvis_v1_evidence_driver.py", flyvis_v1_evidence_driver)):
    if Path(module.__file__).resolve() != (RELEASE / "pynq" / name).resolve():
        raise RuntimeError("STOP: different cached Python module: " + name)
first_board_step.review_before_load(args)  # Checks only; no PYNQ import or MMIO.
save_new(SESSION / "ONE_ATTEMPT_CONSUMED.json", {
    "manual_confirmation": CONFIRM, "boot_id": BOOT,
    "bit_sha256": BIT_SHA, "hwh_sha256": HWH_SHA,
    "board_review_sha256": review_sha, "output_dir": str(args.output_dir),
    "scope": "ONE_CORRECTED_OVERLAY_LOAD_AND_ROW0_ONCE_NO_COMMIT_NO_RETRY",
})
print("REVIEW_SHA256:", review_sha, flush=True)
print("EVIDENCE_DIR:", args.output_dir, flush=True)
started = time.monotonic()
try:
    result = first_board_step.execute_one(args)
    print("HOST_COMPLETION_ELAPSED_S:",
          result["driver_trace_summary"]["host_completion_elapsed_s"], flush=True)
    save_new(SESSION / "notebook_completion.json", {
        "status": result["status"], "notebook_call_elapsed_s": time.monotonic() - started,
        "timing_scope": "Host elapsed time with logging and overlay load; not pure PL cycle latency",
        "evidence_dir": str(args.output_dir), "board_review_sha256": review_sha,
    })
except BaseException:
    print("FAIL_CLOSED: STOP. NO RETRY, RESET OR FALLBACK.", flush=True)
    if flyvis_v1_evidence_driver.PINNED_UNCERTAIN_BUFFERS:
        print("DDR BUFFERS PINNED: KEEP THIS NOTEBOOK KERNEL ALIVE.", flush=True)
    raise

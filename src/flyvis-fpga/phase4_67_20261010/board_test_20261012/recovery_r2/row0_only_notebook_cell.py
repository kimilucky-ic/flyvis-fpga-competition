"""Prepared R2 row0 phase; deliver only after load-only result is reviewed.

Requires the live globals and Overlay object from the load-only cell in the
same kernel. Does not load again or recover automatically. Existing sealed
EvidenceStepDriver performs all pointer/start/status/buffer operations.
"""
if CONFIRM != REQUIRED or REQUIRED != "AUTHORIZE_BANKFIX_RELOAD_ONCE_AND_ROW0_ONCE_BOOT_2c7cec1e":
    raise RuntimeError("STOP: R2 row0 authorization missing")
if Path("/proc/sys/kernel/random/boot_id").read_text().strip() != BOOT:
    raise RuntimeError("STOP: board rebooted after the R2 load")
if json.loads((R2 / "load_result.json").read_text()).get("status") != "LOAD_ONLY_RETURNED_ROW0_NOT_STARTED":
    raise RuntimeError("STOP: reviewed load phase has not completed")
if not overlay.is_loaded():
    raise RuntimeError("STOP: runtime overlay changed")
if digest(R2 / "request_i32le.bin") != "ea1cb4a5f1d655183cad390ef0226ca138eb77d783f4edf271fb37711d9be8b4":
    raise RuntimeError("STOP: row0 request changed")
if digest(R2 / "integer_oracle_i32le.bin") != "50f212ffd6e47abebc8758b8c48999eb40957aabd0106b467ad4cc47a4f92a00":
    raise RuntimeError("STOP: row0 oracle changed")
durable_json(R2 / "ROW0_ATTEMPT_CONSUMED.json", {
    "boot_id": BOOT, "authorization": CONFIRM,
    "scope": "ROW0_ONCE_NO_LOAD_NO_COMMIT_NO_RETRY",
})
import numpy as np
from pynq import allocate
from pynq.mmio import MMIO

class R2EvidenceDriver(flyvis_v1_evidence_driver.EvidenceStepDriver):
    def event(self, kind, **values):
        super().event(kind, **values)
        sync_dir(self.directory)

    def read(self, offset):
        self.event("mmio_read_intent", offset=offset)
        return super().read(offset)

    def save_report(self, report):
        super().save_report(report)
        path = self.directory / "step_report.json"
        with path.open("rb") as stream:
            os.fsync(stream.fileno())
        sync_dir(self.directory)

try:
    request = np.fromfile(str(R2 / "request_i32le.bin"), dtype="<i4")
    oracle = np.fromfile(str(R2 / "integer_oracle_i32le.bin"), dtype="<i4")
    phase("06_BEFORE_FIRST_HLS_AXI_ACCESS", address="0x43C00000", request_words=1498)
    mmio = MMIO(0x43C00000, 0x10000)
    driver = R2EvidenceDriver(overlay, mmio, allocate, R2 / "step0")
    sync_dir(R2)
    response = driver.step(request)  # One request; no CPU fallback.
    output = response["candidate_h_q22_i32"]
    durable_file(R2 / "PL_output_i32le.bin", output.tobytes())
    exact_match = bool(np.array_equal(output, oracle))
    for index, (actual, expected) in enumerate(zip(output.tolist(), oracle.tolist())):
        print("H[{:02d}] PL={} ORACLE={} MATCH={}".format(index, actual, expected, actual == expected), flush=True)
    result = {
        "status": "PASS_REAL_BOARD_ONE_STEP_INTEGER_ORACLE" if exact_match else "FAIL_CLOSED_INTEGER_MISMATCH",
        "boot_id": BOOT, "bit_sha256": BIT_SHA, "hwh_sha256": HWH_SHA,
        "load_result_sha256": digest(R2 / "load_result.json"),
        "request_sha256": digest(R2 / "request_i32le.bin"),
        "oracle_sha256": digest(R2 / "integer_oracle_i32le.bin"),
        "pl_output_sha256": digest(R2 / "PL_output_i32le.bin"),
        "exact_integer_match": exact_match,
        "mismatched_indices": np.flatnonzero(output != oracle).tolist(),
        "driver_trace_summary": response["report"],
        "board_execution_proven": exact_match,
        "scientific_acceptance": "NOT_GRANTED", "true_closed_loop": False,
        "python_fallback": False, "committed": False,
        "video_file_review_and_sha": "PENDING",
    }
    durable_json(R2 / "board_run.json", result)
    inventory = [{"path": str(path.relative_to(R2)), "bytes": path.stat().st_size,
                  "sha256": digest(path)} for path in sorted(R2.rglob("*")) if path.is_file()]
    durable_json(R2 / "evidence_manifest.json", inventory)
    phase("07_ROW0_COMPLETED", status=result["status"], pl_output_sha256=result["pl_output_sha256"])
    print("HOST_COMPLETION_ELAPSED_S:", response["report"]["host_completion_elapsed_s"], flush=True)
    if not exact_match:
        raise RuntimeError("STOP: PL output differs from the independent integer oracle")
except BaseException as error:
    phase("98_ROW0_FAULT", error=repr(error),
          buffers_pinned=bool(flyvis_v1_evidence_driver.PINNED_UNCERTAIN_BUFFERS), no_retry=True)
    print("FAIL_CLOSED: NO RETRY/RESET/FALLBACK. KEEP THIS KERNEL ALIVE.", flush=True)
    raise

from pathlib import Path
import hashlib
import json
import struct

SESSION = Path(
    "/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1/"
    "unpacked_cd91d2f5cffb47e3a400d1dbae5c7854/"
    "row0_session_ae9612d9da4947278c77c3b520ce874a"
)
RUN = SESSION / "run"
OLD_BOOT = "dbbf5a83-cf0b-4c3a-bd74-3148ff1b90c5"
EXPECTED_OUTPUT_SHA = "50f212ffd6e47abebc8758b8c48999eb40957aabd0106b467ad4cc47a4f92a00"

# File reads only: no PYNQ import, MMIO, overlay load, reset or retry.
boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
print(json.dumps({
    "status": "READ_ONLY_PREVIOUS_ATTEMPT_FILES",
    "current_boot_id": boot,
    "original_attempt_boot_id": OLD_BOOT,
    "same_boot_as_original_attempt": boot == OLD_BOOT,
    "session_exists": SESSION.is_dir(),
    "run_dir_exists": RUN.is_dir(),
    "hardware_operations_by_this_cell": 0,
}, indent=2))

for path in (
    SESSION / "ONE_ATTEMPT_CONSUMED.json",
    RUN / "board_run.json",
    RUN / "step0" / "step_report.json",
    SESSION / "notebook_completion.json",
):
    print("\nFILE:", path)
    if not path.is_file():
        print("MISSING")
        continue
    raw = path.read_bytes()
    print("SHA256:", hashlib.sha256(raw).hexdigest())
    try:
        print(json.dumps(json.loads(raw.decode("utf-8")), indent=2))
    except (ValueError, UnicodeError) as error:
        print("INCOMPLETE_OR_UNREADABLE_JSON:", str(error))
        print(raw[-4096:].decode("utf-8", errors="replace"))

output = RUN / "PL_output_i32le.bin"
print("\nSAVED_PL_OUTPUT:", output)
if output.is_file():
    raw = output.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    print("BYTES:", len(raw), "SHA256:", digest)
    print("SAVED_OUTPUT_MATCHES_FROZEN_ROW0_ORACLE_SHA:", digest == EXPECTED_OUTPUT_SHA)
    if len(raw) == 268:
        print("SAVED_67_OUTPUT_CODES:", list(struct.unpack("<67i", raw)))
else:
    print("MISSING")

for path in (RUN / "console.log", RUN / "step0" / "register_trace.jsonl"):
    print("\nLOG_TAIL:", path)
    if not path.is_file():
        print("MISSING")
        continue
    with path.open("rb") as stream:
        stream.seek(0, 2)
        size = stream.tell()
        stream.seek(max(0, size - 32768))
        tail = stream.read().decode("utf-8", errors="replace")
    print("\n".join(tail.splitlines()[-100:]))

print("\nREAD_ONLY_DONE; NO LOAD, START, RESET OR RETRY WAS PERFORMED.")

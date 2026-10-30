from pathlib import Path
import hashlib
import json
import struct
import sys
import uuid

package_dir = Path("/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1/unpacked_cd91d2f5cffb47e3a400d1dbae5c7854/pynq_v1_single_step_20261011_1620")
release = package_dir / "release"
with (release / "vectors/requests_i32le.bin").open("rb") as stream:
    request = stream.read(1498 * 4)
with (release / "vectors/expected_i32le.bin").open("rb") as stream:
    oracle = stream.read(67 * 4)
request_sha = hashlib.sha256(request).hexdigest()
oracle_sha = hashlib.sha256(oracle).hexdigest()
if request_sha != "ea1cb4a5f1d655183cad390ef0226ca138eb77d783f4edf271fb37711d9be8b4":
    raise RuntimeError("STOP: row0 input identity differs")
if oracle_sha != "50f212ffd6e47abebc8758b8c48999eb40957aabd0106b467ad4cc47a4f92a00":
    raise RuntimeError("STOP: row0 integer oracle identity differs")
session = package_dir.parent / ("row0_session_" + uuid.uuid4().hex)
session.mkdir(exist_ok=False)
report = {
    "status": "ROW0_READY_AWAITING_EXACT_LOAD_AUTHORIZATION",
    "package_dir": str(package_dir), "session_dir": str(session),
    "python_executable": sys.executable,
    "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
    "request_row": 0, "request_words": 1498, "output_words": 67,
    "request_sha256": request_sha, "integer_oracle_sha256": oracle_sha,
    "expected_h_q22_i32": list(struct.unpack("<67i", oracle)),
    "board_register_reads": 0, "board_register_writes": 0, "pl_downloads": 0,
    "board_execution_proven": False,
    "hp0_observation": "CARRY_FORWARD_20261011_64BIT; NOT_REMEASURED_IN_THIS_CELL",
    "human_load_authorization": "PENDING",
}
(session / "request_row0_i32le.bin").write_bytes(request)
(session / "integer_oracle_row0_i32le.bin").write_bytes(oracle)
with (session / "row0_preparation.json").open("x") as stream:
    json.dump(report, stream, indent=2)
print(json.dumps(report, indent=2))
print("SESSION_DIR:", session)

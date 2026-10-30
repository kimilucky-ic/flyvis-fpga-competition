"""Copy the verified HLS build to a fresh shorter implementation directory."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
source = ROOT / "build/vitis_2026_1_q22_animation_enterprise_20261010_1842"
DESTINATION = ROOT / "build/vitis_2026_1_q22_animation_s2"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ignore(directory, names):
    excluded = {"sim", ".debug", "logs", ".Xil"}
    if Path(directory).name == "impl":
        excluded.update(name for name in names if name != "ip")
    return excluded.intersection(names)


if DESTINATION.exists():
    raise RuntimeError("Short implementation directory already exists; preserve it")
if not DESTINATION.resolve().is_relative_to((ROOT / "build").resolve()):
    raise RuntimeError("Output must remain inside this independent build directory")
shutil.copytree(source, DESTINATION, ignore=ignore)
identities = {}
for source in sorted((source / "hls/syn/verilog").glob("*")):
    if not source.is_file():
        continue
    relative = source.relative_to(source)
    digest = sha(source)
    if sha(DESTINATION / relative) != digest:
        raise RuntimeError(f"Copied generated RTL identity mismatch: {relative}")
    identities[str(relative)] = digest
manifest = {
    "scope": "same generated HLS RTL/IP; copied build state; no resynthesis or numerical change",
    "source": str(source), "destination": str(DESTINATION),
    "failed_path_length": 267, "windows_tool_limit": 260,
    "failed_log": str(source / "hls/impl/verilog/vivado.log"),
    "failed_log_sha256": sha(source / "hls/impl/verilog/vivado.log"),
    "generated_verilog_identities": identities,
    "board_execution": False,
}
(ROOT / "artifacts/SHORT_HLS_IMPL_COPY.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"destination": str(DESTINATION), "generated_files_verified": len(identities)}))

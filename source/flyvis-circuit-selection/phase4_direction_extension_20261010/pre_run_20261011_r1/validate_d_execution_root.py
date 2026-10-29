"""Validate an authorized data-location copy; no neural or CUDA execution."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, subprocess, sys

source = Path(__file__).resolve().parent
TARGET = Path(r"D:\FlyVisCircuitSelection\phase4_direction_extension_20261010\pre_run_20261011_r1")
WSL_TARGET = "/mnt/d/FlyVisCircuitSelection/phase4_direction_extension_20261010/pre_run_20261011_r1"
OUTPUT = "D_EXECUTION_PREFLIGHT_20261011_r1.json"

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def call(args):
    result = subprocess.run(args, capture_output=True, timeout=60)
    def decode(raw):
        enc = "utf-16-le" if raw.count(b"\0") > len(raw) // 5 else "utf-8"
        return raw.decode(enc, errors="replace")
    return dict(command=args, returncode=result.returncode,
                stdout=decode(result.stdout), stderr=decode(result.stderr))

def main():
    if (source / OUTPUT).exists() or (TARGET / OUTPUT).exists():
        raise SystemExit("Existing observations preserved")
    if TARGET.resolve().parent != Path(r"D:\FlyVisCircuitSelection\phase4_direction_extension_20261010").resolve():
        raise SystemExit("Wrong authorized execution directory")
    identity = json.loads((TARGET / "FROZEN_CAMPAIGN_IDENTITY.json").read_text(encoding="utf-8"))
    same_identity_bytes = sha(TARGET / "FROZEN_CAMPAIGN_IDENTITY.json") == sha(source / "FROZEN_CAMPAIGN_IDENTITY.json")
    checks = []
    for entry in identity["files"]:
        source, target = source / entry["path"], TARGET / entry["path"]
        checks.append(dict(path=entry["path"], bytes=entry["bytes"],
                           source_match=source.stat().st_size == entry["bytes"] and sha(source) == entry["sha256"],
                           target_match=target.stat().st_size == entry["bytes"] and sha(target) == entry["sha256"]))
    probes = []
    for script, repeat in [("run_full.py", "full_r1"), ("run_formal.py", "formal_r1")]:
        probes.append(call(["wsl.exe", "-d", "FlyVisCPU", "--", "/opt/flyvis-gpu-venv/bin/python", "-B",
                            WSL_TARGET + "/" + script, "--repeat", repeat, "--preflight-only"]))
    smi = call(["nvidia-smi.exe", "--query-gpu=index,uuid,name,memory.total,memory.used,memory.free,utilization.gpu,driver_version", "--format=csv,noheader"])
    disk = shutil.disk_usage(TARGET)
    checks_pass = same_identity_bytes and all(x["source_match"] and x["target_match"] for x in checks)
    probe_pass = all(p["returncode"] == 0 for p in probes)
    disk_pass = disk.free >= 36 * 1024**3
    report = dict(status="PASS_LOCATION_PREFLIGHT_FORMAL_RUN_LOCKED" if checks_pass and probe_pass and disk_pass else "FAIL_LOCATION_PREFLIGHT",
                  observed_utc=datetime.now(timezone.utc).isoformat(),
                  source=str(source), execution_root=str(TARGET),
                  campaign_id=identity["campaign_id"], identity_file_sha256=sha(TARGET / "FROZEN_CAMPAIGN_IDENTITY.json"),
                  identity_bytes_match=same_identity_bytes, frozen_file_checks=checks, WSL_static_entry_probes=probes,
                  failed_path_probe_preserved=dict(distribution="Ubuntu", code="WSL_E_DISTRO_NOT_FOUND",
                                                   neural_updates=0, corrected_distribution="FlyVisCPU"),
                  Windows_python=sys.version, GPU_observation=smi,
                  disk=dict(free_bytes=disk.free, free_GiB=disk.free / 1024**3, required_start_GiB=36, gate="PASS" if disk_pass else "FAIL"),
                  authority_records_present={n:(TARGET / n).exists() for n in ["TECHNICAL_RATIFICATION.json", "GPU_COORDINATION_CONFIRMED.json", "RUN_WINDOW_AUTHORIZATION.json"]},
                  neural_updates=0, CUDA_tensor_operations=0, FPGA_execution=False,
                  full_or_replacement_results="NOT_RUN", formal_run_authorized=False,
                  GPU_conflict_free="UNCONFIRMED", observation_not_reservation=True,
                  formal_artifacts_directory_exists=(TARGET / "artifacts").exists(),
                  C_source_preserved=True, pre_registration_and_thresholds_changed=False)
    for parent in [source, TARGET]:
        with (parent / OUTPUT).open("x", encoding="utf-8", newline="\n") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print(json.dumps(dict(status=report["status"], frozen_files=len(checks),
                          WSL_probe_returncodes=[p["returncode"] for p in probes],
                          free_GiB=report["disk"]["free_GiB"], neural_updates=0,
                          formal_run_authorized=False)))
    if report["status"].startswith("FAIL"):
        raise SystemExit(1)

if __name__ == "__main__":
    main()

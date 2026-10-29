"""Snapshot final preparation evidence, never a neural launch or result PASS."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, sys

HERE = Path(__file__).resolve().parent
TARGET = Path(r"D:\FlyVisCircuitSelection\phase4_direction_extension_20261010\pre_run_20261011_r1")
sys.path.insert(0, str(TARGET))
from run_gate import LaunchBlocked, require_launch, verify_frozen_files

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def write_both(name, data):
    for parent in [HERE, TARGET]:
        with (parent / name).open("x", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")

def main():
    frozen = verify_frozen_files()
    technical = json.loads((TARGET / "TECHNICAL_RATIFICATION.json").read_text(encoding="utf-8"))
    coord = json.loads((TARGET / "GPU_COORDINATION_PENDING_SOURCE_20261011.json").read_text(encoding="utf-8"))
    assert technical["decision"] == "APPROVE_UNCHANGED_v1"
    assert technical["campaign_id"] == coord["campaign_id"] == frozen["campaign_id"]
    assert coord["conflict_free"] is False
    assert not (TARGET / "GPU_COORDINATION_CONFIRMED.json").exists()
    assert not (TARGET / "RUN_WINDOW_AUTHORIZATION.json").exists()
    assert not (TARGET / "artifacts").exists() and not (HERE / "artifacts").exists()
    try:
        require_launch()
    except LaunchBlocked as exc:
        guard_reason = str(exc)
    else:
        raise AssertionError("Unexpected launch permission")
    now = datetime.now(timezone.utc)
    disk = shutil.disk_usage(TARGET)
    assert disk.free >= 36 * 1024**3
    status = dict(status="TECHNICAL_AND_STORAGE_READY_GPU_SLOT_PENDING_NOT_RUN",
                  observed_utc=now.isoformat(), source=str(HERE), execution_root=str(TARGET),
                  campaign_id=frozen["campaign_id"], comparison_ids=frozen["comparison_ids"],
                  identity_file_sha256=sha(TARGET / "FROZEN_CAMPAIGN_IDENTITY.json"),
                  frozen_file_count=len(frozen["files"]), frozen_file_verification="PASS",
                  technical_decision=technical["decision"], technical_audit_checks=technical["audit_checks"],
                  technical_record_sha256=sha(TARGET / "TECHNICAL_RATIFICATION.json"),
                  storage_authorized=True, disk=dict(free_bytes=disk.free, free_GiB=disk.free/1024**3, required_start_GiB=36, gate="PASS"),
                  A_GPU_status=coord["status"], A_conflict_free=False,
                  A_observed_at=coord["recorded_at"], A_pending_record_valid_until=coord["valid_until"],
                  A_pending_observation_refresh_required=now > datetime.fromisoformat(coord["valid_until"]),
                  A_source_sha256=sha(TARGET / "GPU_COORDINATION_PENDING_SOURCE_20261011.json"),
                  available_start=None, available_end=None, A_blockers=coord["blockers"],
                  actual_launch_guard_after_technical_import=dict(status="PASS_EXPECTED_REJECTION", reason=guard_reason,
                      neural_or_CUDA_code_imported=False),
                  human_run_authorized=False, new_Full_steps=0, new_H_R_commits=0,
                  CUDA_tensor_operations=0, FPGA_execution=False,
                  planned_only=dict(Full_condition_runs=48, Replacement_condition_runs=192,
                                    Full_steps=23280, H_R_commits=93120),
                  next_action="Architecture schedules non-conflicting resources; A confirms an explicit90-minute interval; then obtain the user's explicit launch window",
                  scientific_thresholds_ROIs_and_model_changed=False,
                  evidence_level="INPUT_CODE_IDENTITY_CPU_GATES_RESOURCE_PREPARATION_ONLY",
                  functional_result_acceptance="NOT_EVALUATED_NOT_RUN")
    write_both("PRE_RUN_FINAL_STATUS_20261011_r1.json", status)
    manifest = dict(schema="flyvis-preparation-delivery-manifest/v1", created_utc=now.isoformat(),
                    execution_root=str(TARGET), campaign_id=frozen["campaign_id"],
                    scope="Preparation package including external records; not formal experimental outputs",
                    files=[dict(path=p.relative_to(TARGET).as_posix(), bytes=p.stat().st_size, sha256=sha(p))
                           for p in sorted(TARGET.rglob("*")) if p.is_file() and "__pycache__" not in p.parts],
                    detailed_report=dict(path=str(HERE / "PRE_RUN_REPORT_20261011.md"), sha256=sha(HERE / "PRE_RUN_REPORT_20261011.md")),
                    new_neural_updates=0, formal_GPU_run_authorized=False)
    write_both("PREPARATION_DELIVERY_MANIFEST_20261011_r1.json", manifest)
    print(json.dumps(dict(status=status["status"], files=len(manifest["files"]),
                          free_GiB=status["disk"]["free_GiB"], technical=technical["decision"],
                          launch_guard=status["actual_launch_guard_after_technical_import"], new_neural_updates=0)))

if __name__ == "__main__":
    main()

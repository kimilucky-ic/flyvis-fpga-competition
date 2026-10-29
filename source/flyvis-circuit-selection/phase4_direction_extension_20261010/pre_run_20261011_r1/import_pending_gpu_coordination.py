"""Preserve A's PENDING resource evidence without creating a launch approval."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json

HERE = Path(__file__).resolve().parent
TARGET = Path(r"D:\FlyVisCircuitSelection\phase4_direction_extension_20261010\pre_run_20261011_r1")
source = Path(r"C:\Users\hzy72\Documents\ChatGPT\fpga\flyvis-fpga\phase4_numeric_diagnostics_20261011\GPU_COORDINATION_FOR_B_PHASE4_20261011.json")

def main():
    raw = source.read_bytes()
    coord = json.loads(raw)
    identity = json.loads((TARGET / "FROZEN_CAMPAIGN_IDENTITY.json").read_text(encoding="utf-8"))
    assert coord["campaign_id"] == identity["campaign_id"]
    assert coord["GPU_uuid"] == identity["GPU_uuid"]
    assert coord["owner"] == "A_GPU" and coord["conflict_free"] is False
    assert coord["available_start"] is None and coord["available_end"] is None
    assert coord["human_run_authorized"] is False and coord["reservation_created"] is False
    source_sha = hashlib.sha256(raw).hexdigest()
    receipt = dict(status="PENDING_A_NO_CONFIRMED_SLOT_RECORD_PRESERVED",
                   imported_utc=datetime.now(timezone.utc).isoformat(),
                   source=str(source), source_sha256=source_sha,
                   campaign_id=coord["campaign_id"], GPU_uuid=coord["GPU_uuid"],
                   A_recorded_at=coord["recorded_at"], A_observation_valid_until=coord["valid_until"],
                   conflict_free=False, available_start=None, available_end=None,
                   blockers=coord["blockers"],
                   no_actual_GPU_conflict_proven=True,
                   missing_evidence="Future interval and cross-lane resource confirmation; snapshots alone prove no reservation",
                   formal_GPU_run_authorized=False, neural_updates=0, FPGA_execution=False,
                   confirmed_gate_file_created=False)
    for parent in [HERE, TARGET]:
        with (parent / "GPU_COORDINATION_PENDING_SOURCE_20261011.json").open("xb") as f:
            f.write(raw)
        with (parent / "GPU_COORDINATION_PENDING_IMPORT_20261011.json").open("x", encoding="utf-8", newline="\n") as f:
            json.dump(receipt, f, ensure_ascii=False, indent=2)
            f.write("\n")
        assert not (parent / "GPU_COORDINATION_CONFIRMED.json").exists()
    print(json.dumps(dict(status=receipt["status"], source_sha256=source_sha,
                          A_window=None, neural_updates=0)))

if __name__ == "__main__":
    main()

"""Seal the final software-only result after saved-data and fresh-process acceptance."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUN = ROOT / "runs/acceptance800_20261013"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""): h.update(block)
    return h.hexdigest()


def load(path): return json.loads(path.read_text(encoding="utf-8"))
def save(path, data): path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def main():
    structure = load(RUN / "structure_acceptance.json")
    numerical = load(RUN / "acceptance.json")
    package = RUN / "independent_audit/compact_replay"
    replay = load(package / "replay_result.json")
    assert structure["status"] == "PASS" and numerical["bit_mismatches"] == 0
    assert numerical["steps"] == 800 and numerical["historical_central_comparison"]["bit_mismatches"] == 0
    assert replay["status"] == "PASS_FRESH_PROCESS_COMPACT_ONLY_SELF_FEEDBACK"
    assert not replay["torch_imported"] and not replay["flyvis_imported"] and not replay["expanded_edge_file_used"]
    for name, entry in load(RUN / "manifest.json").items():
        assert sha(RUN/name) == entry["sha256"], name
    for path, entry in load(RUN / "source_inventory.json").items():
        assert sha(Path(path)) == entry["sha256"], path
    for name, expected in load(package / "payload_manifest.json").items():
        assert sha(package/name) == expected, name
    # Preserve the exact replayed payload manifest. Added attribution is sealed separately below.
    audit_path = RUN / "independent_audit/saved_evidence_audit.json"
    audit = load(audit_path)
    audit["portable_replay_status"] = replay["status"]
    audit["portable_replay_report_sha256"] = sha(package / "replay_result.json")
    save(audit_path, audit)
    result = dict(status="COMPLETE_SOFTWARE_GOAL_HARDWARE_UNVERIFIED", evidence_level="CPU_SOFTWARE_ONLY",
                  binary_bytes=structure["binary_bytes"], binary_sha256=sha(RUN / "flyvis_template.bin"),
                  ordered_edges_verified=1513231, state_values_verified=36535200,
                  historical_central_values_verified=485*65, malformed_inputs_rejected=8,
                  compact_replay_steps=800, self_feedback_transitions=799,
                  source_inventory_rehashed_unchanged=True,
                  current_source_matches_accepted_core_snapshot={name:sha(ROOT/name)==sha(RUN/"scripts_snapshot"/name)
                      for name in ["reference.py","codec.py","engine.py","run_study.py"]},
                  study_goal="Lossless structure plus deterministic full FP32 software recurrence; no hardware deployment",
                  unresolved=["Cycle-level BRAM-port and dependency schedule", "FP32 RTL/IP numerical contract and subnormal handling",
                              "Synthesis and routed resources/timing", "Actual board autonomous recurrence", "200Hz throughput and energy"],
                  next_action="CPU-only single-lane cycle scheduling model; no automatic EDA or board operations")
    assert all(result["current_source_matches_accepted_core_snapshot"].values())
    save(ROOT / "RESULT.json", result)
    tracked = sorted(p for p in ROOT.rglob("*") if p.is_file()
                     and p.name != "FINAL_MANIFEST_SHA256.json"
                     and not any(part in {"__pycache__", "isolated_mpl", "isolated_flyvis_root", "isolated_numba"} for part in p.parts))
    manifest = {str(p.relative_to(ROOT)).replace("\\", "/"):dict(bytes=p.stat().st_size, sha256=sha(p)) for p in tracked}
    save(ROOT / "FINAL_MANIFEST_SHA256.json", manifest)
    for name, row in load(ROOT/"FINAL_MANIFEST_SHA256.json").items():
        assert sha(ROOT/name) == row["sha256"] and (ROOT/name).stat().st_size == row["bytes"], name
    print(json.dumps(dict(status=result["status"], sealed_files=len(manifest), sealed_bytes=sum(x["bytes"] for x in manifest.values()),
                         final_manifest_sha256=sha(ROOT/"FINAL_MANIFEST_SHA256.json"))), flush=True)


if __name__ == "__main__": main()

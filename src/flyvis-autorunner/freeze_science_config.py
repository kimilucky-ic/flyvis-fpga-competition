"""Create a new A/B CLI config, disabled GPU by default; never overwrite."""
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from autorunner import HERE, load_json, own_path, require, sha, write_json
from plugin_contract import SCHEMA, validate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("A", "B"), required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--campaign", default="research_AB_20261011_r1")
    parser.add_argument("--predecessor-run", default="autorun_researchA_20261011_r1")
    parser.add_argument("--authorize", action="store_true")
    parser.add_argument("--authorization-reference")
    args = parser.parse_args()
    lane = HERE.parent / "flyvis-circuit-selection"
    a = lane / "t4t5_confirm_20261011"
    b = lane / "t4t5_sparse_recovery_20261011"
    source = (a / "EXPERIMENT_A.json") if args.stage == "A" else (b / "EXPERIMENT_B.json")
    spec = load_json(source)
    config = {"schema": SCHEMA, "mode": "fast", "stage": args.stage, "campaign_id": args.campaign,
        "spec_path": str(source), "spec_sha256": sha(source), "identity_id": spec["identity_id"],
        "fresh_run": True, "output_dir": str((a if args.stage == "A" else b) / "artifacts/gpu_r1"),
        "queue_s": 15, "stop_grace_s": 20, "runtime": {"python": "/opt/flyvis-gpu-venv/bin/python"},
        "scope": {"authorized": False, "confirmed_by_user": False}}
    if args.stage == "B":
        config["predecessor"] = {"run_id": args.predecessor_run, "identity_id": load_json(a / "EXPERIMENT_A.json")["identity_id"],
                                 "delivery_result": str(a / "artifacts/analysis_r1/result.json")}
    _, key = validate(config)
    if args.authorize:
        require(bool(args.authorization_reference), "RUN_NOT_AUTHORIZED", "Direct human research authorization reference required")
        now = datetime.now(timezone.utc)
        config["scope"] = {"authorized": True, "confirmed_by_user": True, "conflict_free": True,
            "board_resources_reserved": False, "stage": args.stage, "identity_key": key, "max_attempts": 1,
            "max_cases": len(spec["cases"]), "max_steps": spec["actual_neural_steps_budget"],
            "start": now.isoformat(), "end": (now + timedelta(seconds=900)).isoformat(),
            "authorization_reference": args.authorization_reference}
    destination = own_path(args.out)
    require(not destination.exists(), "CONFIG_EXISTS", "Preserve frozen config")
    write_json(destination, config)
    print(__import__("json").dumps({"config": str(destination), "identity_key": key, "GPU_authorized": args.authorize}))


if __name__ == "__main__":
    main()

"""One bounded acceptance sequence. CPU/cache only; explicitly tests GPU refusal."""
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path

sys.dont_write_bytecode = True
from autorunner import HERE, load_json, own_path, write_json


def main():
    session = "readonly_" + uuid.uuid4().hex[:10]
    root = own_path("verification", session)
    root.mkdir(parents=True)
    cfg = HERE / "configs/camera609.fast.json"
    pending = load_json(cfg)
    pending["fresh_replacement"] = True
    pending_path = root / "smoke.pending.json"
    write_json(pending_path, pending)
    ids = {kind: session + "_" + kind for kind in ("preflight", "cache", "dry", "refusal")}
    commands = [
        ("preflight", ["preflight", "--config", str(cfg), "--id", ids["preflight"]], 0),
        ("cache", ["run", "--config", str(cfg), "--cache-only", "--id", ids["cache"]], 0),
        ("dry", ["run", "--config", str(cfg), "--dry-run", "--id", ids["dry"]], 0),
        ("audit", ["audit", "--run", ids["cache"]], 0),
        ("status", ["status", ids["cache"]], 0),
        ("refusal", ["run", "--config", str(pending_path), "--id", ids["refusal"]], 2),
    ]
    rows = []
    start = time.perf_counter()
    for name, arguments, expected in commands:
        command = [sys.executable, "-B", str(HERE / "runner.py"), *arguments]
        tic = time.perf_counter()
        proc = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=30)
        wall = time.perf_counter() - tic
        (root / (name + ".stdout.json")).write_text(proc.stdout, encoding="utf-8")
        (root / (name + ".stderr.log")).write_text(proc.stderr, encoding="utf-8")
        value = json.loads(proc.stdout)
        rows.append({"command": command, "case": name, "cli_wall_s": wall, "expected_exit": expected,
                     "actual_exit": proc.returncode, "status": value.get("status", value.get("stage")),
                     "run_id": value.get("run_id"), "reported_wall_s": value.get("wall_s", value.get("audit_s")),
                     "pass": proc.returncode == expected})
        if proc.returncode != expected:
            raise RuntimeError("Acceptance sequence failed; logs retained: " + str(root))
    failed = load_json(HERE / "runs" / ids["refusal"] / "run_summary.json")
    if failed["failure"]["code"] != "RUN_NOT_AUTHORIZED" or failed["gpu_worker_invocations"]:
        raise RuntimeError("GPU refusal evidence differs")
    cache = load_json(HERE / "runs" / ids["cache"] / "run_summary.json")
    if cache["actual_new_computation"] or cache["PL_execution"] or cache["comparison"]["metrics"]["full"]["violations"]:
        raise RuntimeError("Cache acceptance differs")
    report = {"status": "PASS_READONLY_ACCEPTANCE", "session": session, "cases": rows,
              "total_wall_s": time.perf_counter() - start, "GPU_status": "RUN_NOT_AUTHORIZED",
              "GPU_invocations": 0, "PL_execution": False, "new_neural_computation": False,
              "cache_job": ids["cache"], "refused_gpu_job": ids["refusal"], "artifact_directory": str(root)}
    write_json(root / "report.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

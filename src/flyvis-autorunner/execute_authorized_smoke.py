"""Activate the user-approved one-shot smoke after verified external completion.

This entry is for the recorded 2026-10-11 authorization, not a general scheduler.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

sys.dont_write_bytecode = True
from autorunner import Engine, HERE, load_json, own_path, require, sha, utc, write_json


def main():
    deferred_path = HERE / "deferred_smoke.json"
    deferred = load_json(deferred_path)
    run_id = "autorun_camera609_after_b_20261011"
    require(deferred["status"] == "WAITING_B_FINISH", "DEFERRED_STATE", "Not waiting for a first attempt")
    require(not own_path("runs", run_id).exists(), "RUN_EXISTS", "One-shot output already exists")
    b_root = HERE.parent / "flyvis-circuit-selection/t4t5_criticality_20261011/artifacts/pilot_gpu_r1"
    b_status, b_result = load_json(b_root / "STATUS.json"), load_json(b_root / "result.json")
    require(b_status["phase"] == "GPU_COMPUTATION_COMPLETE" and
            b_result["status"] == "PASS_ACTUAL_GPU_PILOT_COMPUTATION" and
            b_status["run_id"] == b_result["run_id"], "B_NOT_DONE", "B pilot completion record")
    probe = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,process_name,used_gpu_memory",
                            "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5, check=True)
    require(not probe.stdout.strip(), "GPU_BUSY", "Resource occupied; never interrupt")
    base_path = HERE / "configs/camera609.fast.json"
    engine = Engine(base_path)
    engine.validate()
    full = engine.cached("FullGPU", register=False)
    require(full["execution_kind"] == "accepted_cache_replay", "FULL_MUST_BE_CACHE", "No new Full is authorized")
    for marker in engine.config["runtime"]["busy_markers"]:
        require(not (HERE / marker).exists(), "RESOURCE_RESERVED", marker)
    now = datetime.now(timezone.utc)
    config = engine.config
    config["fresh_full"], config["fresh_replacement"] = False, True
    config["scope"]["gpu"].update(authorized=True, confirmed_by_user=True, conflict_free=True,
         board_resources_reserved=False, start=now.isoformat(), end=(now + timedelta(seconds=300)).isoformat(),
         authorization_reference="Direct user: 等4跑完自己开始我休息一会; reconfirmed: 4跑完了你开始吧",
         cache_keys=engine.keys, max_invocations={"FullGPU": 0, "PythonReplacement": 1})
    config_path = HERE / "configs/camera609.after_b.authorized.json"
    require(not config_path.exists(), "CONFIG_EXISTS", "Approved config is immutable")
    write_json(config_path, config)
    evidence = {"checked_utc": utc(), "B_run_id": b_status["run_id"], "B_status": b_status,
                "B_result_sha256": sha(b_root / "result.json"), "gpu_query": probe.stdout,
                "gpu_query_returncode": probe.returncode, "board_lane": "idle, no running board task; no board I/O",
                "direct_user_reconfirmation": "4跑完了你开始吧", "read_only_resource_checks": True}
    write_json(HERE / "verification/after_b_resource_release.json", evidence)
    deferred.update(status="RUNNING", activated_utc=utc(), start=config["scope"]["gpu"]["start"],
                    end=config["scope"]["gpu"]["end"], activated_config=str(config_path),
                    resource_evidence="verification/after_b_resource_release.json")
    deferred["heartbeat"]["status"] = "PAUSED"
    write_json(deferred_path, deferred)
    command = [sys.executable, "-B", str(HERE / "runner.py"), "run", "--config", str(config_path), "--id", run_id]
    started = time.perf_counter()
    with (HERE / "verification/after_b_smoke.stdout.json").open("wb") as stdout, \
         (HERE / "verification/after_b_smoke.stderr.log").open("wb") as stderr:
        proc = subprocess.Popen(command, stdout=stdout, stderr=stderr)
        returncode = proc.wait()
    wall_s = time.perf_counter() - started
    launch = {"command": command, "returncode": returncode, "CLI_wall_s": wall_s,
              "completed_utc": utc(), "automatic_retry": False}
    write_json(HERE / "verification/after_b_smoke_command.json", launch)
    summary_path = HERE / "runs" / run_id / "run_summary.json"
    summary = load_json(summary_path) if summary_path.exists() else {"status": "FAILED_NO_SUMMARY"}
    success = returncode == 0 and summary["status"] == "PASS_FAST_ACTUAL_SOFTWARE"
    worker_failure_path = HERE / "runs" / run_id / "PythonReplacement/failure.json"
    worker_failure = load_json(worker_failure_path) if worker_failure_path.exists() else {}
    deferred.update(status="COMPLETE" if success else "FAILED", completed_utc=utc(),
         summary_path=str(summary_path), summary_status=summary["status"], CLI_wall_s=wall_s,
         new_GPU_steps=609 if success else worker_failure.get("completed_steps", 0),
         new_GPU_run_attempts=1, automatic_retry=False)
    write_json(deferred_path, deferred)
    print(json.dumps({"status": deferred["status"], "summary_status": summary["status"],
                      "CLI_wall_s": wall_s, "run_id": run_id, "returncode": returncode}, indent=2), flush=True)
    raise SystemExit(returncode)


if __name__ == "__main__":
    main()

"""Bounded independent-CLI scheduler; existing camera609 engine is unchanged."""
import json
import os
import subprocess
import sys
import time
import traceback
import uuid
from pathlib import Path

from autorunner import (HERE, RunnerError, load_json, own_path, require, sha, utc,
                        write_json, wsl_path)
from plugin_contract import SCHEMA, authorize, fast_check, path, predecessor, validate


def cache_read(key):
    index = own_path("cache", "science", key + ".json")
    if not index.exists():
        return None
    record = load_json(index)
    job = own_path("runs", record["run_id"])
    seal = load_json(job / "plugin_seal.json")
    require(seal["identity_key"] == key, "CACHE_IDENTITY", "Cache key mismatch")
    for value, digest in seal["essential_sha256"].items():
        require(sha(path(value)) == digest, "CACHE_CORRUPT", value)
    for value, stamp in seal["raw_file_stamps"].items():
        stat = path(value).stat()
        require([stat.st_size, stat.st_mtime_ns] == stamp, "CACHE_CORRUPT", value)
    result = load_json(job / "run_summary.json")
    require(result["status"] == "PASS_FAST_ACTUAL_SCIENCE" and result["identity_key"] == key,
            "CACHE_UNACCEPTED", "Only complete sealed actual jobs can seed cache")
    return result


def audit_plugin(job):
    seal = load_json(job / "plugin_seal.json")
    result = cache_read(seal["identity_key"])
    require(result is not None and result["run_id"] == job.name, "CACHE_IDENTITY", "Different accepted job")
    return {"status": "PASS_BOUNDED_PLUGIN_SEAL_CHECK", "run_id": job.name,
            "essential_files": len(seal["essential_sha256"]), "GPU_called": False}


class PluginEngine:
    def init__(self, config_path, mode=None):
        self.config = load_json(config_path)
        if mode:
            self.config["mode"] = mode
        self.run = None
        self.started = time.monotonic()
        self.timings = {}

    def event(self, state, **details):
        row = {"schema": SCHEMA, "run_id": self.run.name, "stage": state,
               "science_stage": self.config["stage"], "updated_utc": utc(),
               "elapsed_s": time.monotonic() - self.started, "PL_execution": False, **details}
        write_json(self.run / "job.json", row)
        with (self.run / "events.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row) + "\n")

    def launch(self, key):
        config = self.config
        authorize(config, key)
        require(not path(config["output_dir"]).exists(), "OUTPUT_EXISTS", "Existing scientific evidence is preserved")
        predecessor(config)
        ticket = {"schema": SCHEMA, "identity_key": key, "job_dir": str(self.run), "config": config}
        write_json(self.run / "plugin_ticket.json", ticket)
        runtime = config["runtime"]
        if os.name == "nt":
            command = ["wsl.exe", "-e", runtime["python"], "-B", wsl_path(HERE / "plugin_host.py"),
                       "--ticket", wsl_path(self.run / "plugin_ticket.json")]
        else:
            command = [runtime["python"], "-B", str(HERE / "plugin_host.py"), "--ticket", str(self.run / "plugin_ticket.json")]
        write_json(self.run / "launch.json", {"command": command, "started_utc": utc(), "invocations": 1})
        begin = time.monotonic()
        self.event("QUEUED")
        with (self.run / "stdout.log").open("w", encoding="utf-8") as out, (self.run / "stderr.log").open("w", encoding="utf-8") as err:
            child = subprocess.Popen(command, stdout=out, stderr=err)
            deadline = begin + config["queue_s"] + 900 + 20
            stop_time = None
            last = None
            while child.poll() is None:
                progress = path(config["output_dir"]) / "STATUS.json"
                if progress.exists():
                    try:
                        row = load_json(progress)
                        if row != last:
                            last = row
                            self.event("RUNNING", progress=row)
                    except (OSError, ValueError):
                        pass
                if time.monotonic() >= deadline and stop_time is None:
                    write_json(self.run / "STOP_REQUEST.json", {"reason": "PARENT_TIMEOUT", "requested_utc": utc()})
                    stop_time = time.monotonic()
                if stop_time is not None and time.monotonic() - stop_time >= config["stop_grace_s"]:
                    write_json(own_path("runtime", "RESOURCE_QUARANTINE.json"), {
                        "job_dir": str(self.run), "reason": "OWNED_PLUGIN_COMPLETION_UNCONFIRMED", "launcher_pid": child.pid})
                    raise RunnerError("PLUGIN_TIMEOUT_UNCONFIRMED", "Cooperative stop requested; no second process started")
                time.sleep(.2)
        self.timings["subprocess_wall_s"] = time.monotonic() - begin
        if child.returncode:
            failure_path = self.run / "host_failure.json"
            failure = load_json(failure_path) if failure_path.exists() else {}
            raise RunnerError(failure.get("code", "PLUGIN_EXIT"), failure.get("error", "Worker exited " + str(child.returncode)))
        exit_record = load_json(self.run / "host_exit.json")
        require(exit_record["exit_code"] == 0 and exit_record["lock_released"]
                and exit_record["GPU_work_completion_confirmed"], "PLUGIN_COMPLETION", "Actual worker completion required")
        self.event("WORKER_DONE")

    def seal(self, spec, key):
        out = path(self.config["output_dir"])
        essential = [out / name for name in ("result.json", "run_identity.json", "step_status.jsonl")]
        essential += [self.run / name for name in ("host_exit.json", "host_result.json", "fast_check.json", "run_summary.json")]
        raw = [out / q["condition"] / q["mode"] / name for q in spec["cases"]
               for name in ("activities_full.npy", "flow.npy", "final_state_full.npy")]
        seal = {"identity_key": key, "essential_sha256": {str(p): sha(p) for p in essential},
                "raw_file_stamps": {str(p): [p.stat().st_size, p.stat().st_mtime_ns] for p in raw},
                "raw_guard": "size+mtime; scientific producer checks every candidate finite and fixed-reference tolerance",
                "sealed_utc": utc()}
        write_json(self.run / "plugin_seal.json", seal)
        write_json(own_path("cache", "science", key + ".json"), {"run_id": self.run.name, "identity_key": key})

    def execute(self, preflight=False, dry_run=False, cache_only=False, run_id=None):
        self.started = time.monotonic()
        self.run = own_path("runs", run_id or "science_" + self.config["stage"] + "_" + uuid.uuid4().hex[:12])
        require(not self.run.exists(), "RUN_ID_EXISTS", "Existing result/attempt is preserved; use status/audit")
        self.run.mkdir(parents=True)
        write_json(self.run / "config_snapshot.json", self.config)
        last_valid = None
        try:
            begin = time.monotonic()
            spec, key = validate(self.config)
            self.timings["preflight_s"] = time.monotonic() - begin
            write_json(self.run / "preflight.json", {"status": "PASS_AST_IDENTITY_PREFLIGHT", "identity_key": key,
                "identity_id": spec["identity_id"], "GPU_called": False, "torch_imported": "torch" in sys.modules,
                "public_signature": "run_experiment(spec_path, output_path, check_scope)"})
            last_valid = "PREFLIGHT_DONE"
            self.event(last_valid)
            base = {"schema": SCHEMA, "run_id": self.run.name, "campaign_id": self.config["campaign_id"],
                    "stage": self.config["stage"], "identity_id": spec["identity_id"], "identity_key": key,
                    "PL_execution": False, "actual_new_computation": False, "stopped_at_acceptance": True}
            if preflight or dry_run:
                result = {**base, "status": "PASS_PREFLIGHT" if preflight else "PASS_DRY_RUN",
                    "plan": "FRESH_REQUIRED" if self.config["fresh_run"] else "ACCEPTED_CACHE_OR_SINGLE_FRESH",
                    "case_budget": len(spec["cases"]), "timings": self.timings,
                    "A_delivery_required_at_launch": self.config["stage"] == "B"}
            else:
                predecessor(self.config)
                cached = None if self.config["fresh_run"] else cache_read(key)
                if cached:
                    result = {**base, "status": "PASS_FAST_CACHE_REPLAY", "original_run_id": cached["run_id"],
                              "output_dir": cached["output_dir"], "new_GPU_invocations": 0, "timings": self.timings}
                else:
                    require(not cache_only, "CACHE_MISS_OR_FRESH_REQUIRED", "No authorized new computation in cache-only mode")
                    self.launch(key)
                    last_valid = "WORKER_DONE"
                    begin = time.monotonic()
                    check = fast_check(spec, self.config["output_dir"])
                    self.timings["fast_check_s"] = time.monotonic() - begin
                    write_json(self.run / "fast_check.json", check)
                    worker = check["result"]
                    self.timings.update(model_load_s=worker["model_load_s"], science_worker_wall_s=worker["elapsed_s"],
                        neural_and_record_wall_s=sum(q["neural_wall_s"] for q in worker["modes"]),
                        decoder_wall_s=sum(q["decode_wall_s"] for q in worker["modes"]),
                        pure_GPU_compute_s=None, pure_transfer_s=None)
                    result = {**base, "status": "PASS_FAST_ACTUAL_SCIENCE", "actual_new_computation": True,
                              "new_GPU_invocations": 1, "worker_run_id": worker["run_id"],
                              "output_dir": str(path(self.config["output_dir"])), "timings": self.timings,
                              "actual_neural_steps": worker["actual_neural_steps"],
                              "actual_decoder_frames": worker["actual_decoder_frames"], "reference_violations": 0}
            self.timings["runner_wall_s"] = time.monotonic() - self.started
            write_json(self.run / "run_summary.json", result)
            if result["actual_new_computation"]:
                self.seal(spec, key)
            self.event("COMPLETE", status=result["status"], identity_key=key)
            return result
        except BaseException as exc:
            code = getattr(exc, "code", "PLUGIN_ERROR")
            failure = {"status": "FAILED", "code": code, "error": repr(exc), "last_valid_state": last_valid,
                "traceback": traceback.format_exc(), "elapsed_s": time.monotonic() - self.started,
                "output_dir": self.config.get("output_dir"), "automatic_retry": False, "PL_execution": False}
            write_json(self.run / "failure.json", failure)
            write_json(self.run / "run_summary.json", {**failure, "run_id": self.run.name})
            self.event("FAILED", code=code)
            raise RunnerError(code, str(exc), self.run.name) from exc

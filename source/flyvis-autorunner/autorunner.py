"""CPU-only preflight, accepted-cache index, bounded state machine and sealing."""
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SCHEMA = "flyvis-autorunner/v1"
STAGES = ["FROZEN_INPUT", "READY_FULL", "FULL_DONE", "REPLACEMENT_DONE",
          "FAST_CHECK_DONE", "SEALED", "COMPLETE"]


class RunnerError(RuntimeError):
    def init__(self, code, message, run_id=None):
        super().init__(message)
        self.code, self.run_id = code, run_id


def require(ok, code, message):
    if not ok:
        raise RunnerError(code, message)


def utc():
    return datetime.now(timezone.utc).isoformat()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                              allow_nan=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


def host_path(value):
    s = str(value)
    if os.name == "nt" and s.startswith("/mnt/") and len(s) > 7 and s[6] == "/":
        s = s[5].upper() + ":/" + s[7:]
    elif os.name != "nt" and re.match(r"^[A-Za-z]:[/\\]", s):
        s = "/mnt/" + s[0].lower() + "/" + s[3:].replace("\\", "/")
    return Path(s)


def wsl_path(path):
    s = str(path)
    if re.match(r"^[A-Za-z]:[/\\]", s):
        return "/mnt/" + s[0].lower() + "/" + s[3:].replace("\\", "/")
    return s


def own_path(*parts):
    result = HERE.joinpath(*parts).resolve()
    require(result.is_relative_to(HERE) and result != HERE, "WRITE_SCOPE", str(result))
    return result


def entries(manifest):
    files = manifest["files"]
    if isinstance(files, dict):
        return {name: digest for name, digest in files.items()}
    return {row["path"]: row["sha256"] for row in files}


def methods(path, cls, specification):
    tree = ast.parse(Path(path).read_text(encoding="utf-8-sig"))
    node = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls), None)
    require(node is not None, "API_CLASS", cls)
    found = {n.name: n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for name, arguments in specification.items():
        require(name in found, "API_METHOD", cls + "." + name)
        args = found[name].args
        available = {a.arg for a in [*args.posonlyargs, *args.args, *args.kwonlyargs]}
        require(set(arguments) <= available, "API_SIGNATURE", cls + "." + name)
    return {"class": cls, "methods": list(specification), "check": "AST_NO_IMPORT_NO_GPU"}


def read_clock(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(parsed.tzinfo is not None, "GPU_SCOPE", "timezone required")
    return parsed


def authorize(config, backend, key, now=None):
    ticket = config["scope"].get("gpu", {})
    require(ticket.get("authorized") is True and ticket.get("confirmed_by_user") is True,
            "RUN_NOT_AUTHORIZED", "A new explicit GPU time window is required")
    require(ticket.get("conflict_free") is True and ticket.get("board_resources_reserved") is False,
            "GPU_SCOPE", "Conflict-free software slot must be confirmed")
    require(ticket.get("experiment_id") == config["experiment_id"] and
            ticket.get("steps") == 609 and ticket.get("ablation") == "NONE" and
            ticket.get("cache_keys", {}).get(backend) == key and
            ticket.get("max_invocations", {}).get(backend) == 1 and
            bool(ticket.get("authorization_reference")), "GPU_SCOPE", "Ticket scope/key mismatch")
    start, end = read_clock(ticket["start"]), read_clock(ticket["end"])
    require(0 < (end - start).total_seconds() <= 600, "GPU_SCOPE", "Window must be <=600s")
    now = now or datetime.now(timezone.utc)
    require(start <= now < end, "SLOT_EXPIRED", "Outside the confirmed GPU window")
    return ticket


def quick_compare(full_path, replacement_path, h_ids, progress=None):
    """One bounded array comparison, no CPU neural oracle or replay computation."""
    started = time.perf_counter()
    full = np.load(full_path, mmap_mode="r", allow_pickle=False)
    replacement = np.load(replacement_path, mmap_mode="r", allow_pickle=False)
    require(full.shape == replacement.shape == (1, 609, 45669), "SHAPE", "Full trajectories")
    require(full.dtype == replacement.dtype == np.float32, "DTYPE", "Float32 required")
    mask = np.ones(45669, dtype=bool)
    mask[h_ids] = False
    groups = {"H": np.asarray(h_ids), "R": np.flatnonzero(mask), "full": np.arange(45669)}
    metrics = {g: {"max_abs": 0., "sum_square": 0., "count": 0, "violations": 0} for g in groups}
    for start in range(0, 609, 32):
        left = np.asarray(full[0, start:start + 32], dtype=np.float64)
        right = np.asarray(replacement[0, start:start + 32], dtype=np.float64)
        require(np.isfinite(left).all() and np.isfinite(right).all(), "NONFINITE", "Saved state")
        delta = np.abs(right - left)
        tolerance = 1e-5 + 1e-5 * np.abs(left)
        for group, ids in groups.items():
            selected = delta[:, ids]
            m = metrics[group]
            m["max_abs"] = max(m["max_abs"], float(selected.max()))
            m["sum_square"] += float(np.square(selected).sum())
            m["count"] += selected.size
            m["violations"] += int(np.count_nonzero(selected > tolerance[:, ids]))
        if progress:
            progress(min(start + 32, 609))
    for m in metrics.values():
        m["rmse"] = float(np.sqrt(m.pop("sum_square") / m.pop("count")))
    require(metrics["full"]["violations"] == 0, "NUMERICAL_MISMATCH", json.dumps(metrics))
    return {"status": "PASS_FAST_NUMERICAL", "atol": 1e-5, "rtol": 1e-5,
            "metrics": metrics, "comparison_s": time.perf_counter() - started,
            "steps": 609, "cpu_neural_oracle_calls": 0}


class Engine:
    def init__(self, config_path, mode=None):
        self.config_path = config_path.resolve()
        self.config = load_json(self.config_path)
        require(self.config.get("scope", {}).get("writes") is True,
                "WRITE_NOT_AUTHORIZED", "Config must authorize writes inside flyvis-autorunner")
        self.mode = mode or self.config.get("mode", "fast")
        self.hashes = {}
        self.run = None
        self.last_valid = None
        self.stage_times = {}
        self.results = {}
        self.invocations = []
        self.started = time.perf_counter()
        self.phase = "PREFLIGHT"

    def path(self, value):
        p = host_path(value)
        return p.resolve() if p.is_absolute() else (HERE / p).resolve()

    def digest(self, path):
        path = Path(path).resolve()
        if str(path) not in self.hashes:
            self.hashes[str(path)] = sha(path)
        return self.hashes[str(path)]

    def validate(self):
        c = self.config
        require(c["schema"] == SCHEMA and self.mode in ("fast", "dev", "formal"), "CONFIG", "schema/mode")
        require(c["scope"]["writes"] is True and c["scope"]["board"] is False and
                c["scope"]["ablation"] == "NONE" and c["scope"]["steps"] == 609,
                "UNSUPPORTED_SCOPE", "Phase1 camera609, no board or ablation")
        require(c.get("decoder") == {"enabled": False, "status": "NOT_USED_PHASE1"},
                "DECODER_SCOPE", "Decoder is not part of accepted camera609 neural comparison")
        require(c["experiment_id"] == "camera_rectB_c5689ab635cc425ea672029502d0d402",
                "UNSUPPORTED_SCOPE", "Only frozen accepted camera609 input")
        require(0 < c["timeouts"]["worker_s"] <= 600 and 0 <= c["timeouts"]["queue_s"] <= 600,
                "CONFIG", "bounded timeouts required")
        if self.mode == "dev":
            require(set(c.get("affected_modules", [])) <= {"scheduler", "adapter", "comparison"},
                    "DEV_SCOPE", "Only phase1 modules")
        for name, pin in c["pins"].items():
            require(self.digest(self.path(pin["path"])) == pin["sha256"], "HASH_MISMATCH", name)
        self.bundle = self.path(c["bundle"])
        self.binding = load_json(self.bundle / "camera_backend_identity.json")
        b = self.binding
        require(b["backend_binding_id"] == c["backend_binding_id"] and b["steps"] == 609 and
                b["h_nodes"] == 67 and b["n_nodes"] == 45669 and b["board_used"] is False,
                "IDENTITY", "frozen binding")
        require(canonical({k: v for k, v in b.items() if k != "backend_binding_id"}) == b["backend_binding_id"],
                "IDENTITY", "canonical backend binding")
        for name, expected in entries(load_json(self.bundle / "artifact_manifest.json")).items():
            p = (self.bundle / name).resolve()
            require(p.is_relative_to(self.bundle), "PATH", name)
            require(self.digest(p) == expected, "HASH_MISMATCH", name)
        shapes = {"stimulus.npy": ((1, 609, 1, 721), np.float32),
                  "initial_state_full.npy": ((1, 45669), np.float32),
                  "time.npy": ((609,), np.float64), "activity_time.npy": ((609,), np.float64),
                  "input_node_indices.npy": ((8, 721), np.int64)}
        for name, (shape, dtype) in shapes.items():
            a = np.load(self.bundle / name, mmap_mode="r", allow_pickle=False)
            require(a.shape == shape and a.dtype == dtype, "INPUT_SHAPE", name)
            require(np.isfinite(a).all(), "NONFINITE", name)
        t = np.load(self.bundle / "time.npy", allow_pickle=False)
        require(np.array_equal(t, np.arange(609) * .005) and
                np.array_equal(np.load(self.bundle / "activity_time.npy"), t + .005), "CLOCK", "dt/after-update")
        self.candidate = load_json(self.bundle / "candidates/B_T5c/candidate_manifest.json")
        require(len(set(self.candidate["h_global_node_indices"])) == 67, "H_MAP", "H identity")
        sources = {name: self.path(value) for name, value in c["sources"].items()}
        self.sources = sources
        self.api = [methods(sources["full"], "FullNetworkOracle", {"init__": ["identity_path", "device"],
                    "step": ["old_full", "hex_frame"], "assert_weights_unchanged": []}),
                    methods(sources["r_only"], "RStepService", {"init__": ["parameter_path", "identity_path", "candidate_path", "device"],
                    "step": ["old_full", "hex_frame", "step_id", "run_id", "condition_id"]}),
                    methods(sources["bound_r"], "BoundRService", {"step": ["old", "frame", "step_id", "run_id", "condition_id"],
                    "assert_weights_unchanged": []}),
                    methods(sources["coordinator"], "Coordinator", {"prepare": ["step_id", "x_full"], "commit": ["transaction"]}),
                    methods(sources["h_step"], "HUpdater", {"step": ["request"]}),
                    methods(sources["gpu_adapter"], "GPUAdapter", {"evaluate": ["old_full", "x_full", "tag"]})]
        core = {name: self.digest(sources[name]) for name in ("full", "r_only", "h_step", "coordinator", "gpu_adapter")}
        identity_fields = ("stimulus_sha256", "time_sha256", "activity_time_sha256", "initial_state_sha256",
                           "expanded_parameters_sha256", "checkpoint_sha256", "source_commit", "numeric_profile_sha256",
                           "candidate_sha256", "node_map_sha256", "edge_partition_sha256", "static_boundary_sha256",
                           "input_manifest_sha256", "input_reader_sha256", "nodes_full_sha256", "dt_s", "steps")
        self.cache_context = {k: b[k] for k in identity_fields}
        self.keys = {}
        for backend in ("FullGPU", "PythonReplacement"):
            names = ("full", "r_only") if backend == "FullGPU" else ("r_only", "h_step", "coordinator", "gpu_adapter")
            ctx = dict(self.cache_context, backend=backend, ablation={"definition": "NONE", "start_step": None},
                       kernel_sources={n: core[n] for n in names},
                       backend_numeric="ORIGINAL_FP32_GPU" if backend == "FullGPU" else "ORIGINAL_FP32_GPU_NATIVE_R_NUMPY_FP32_H")
            self.keys[backend] = canonical(ctx)
        return {"status": "PASS_PREFLIGHT_CPU_ONLY", "cache_keys": self.keys,
                "interfaces": self.api, "decoder": c["decoder"], "checkpoint": "BOUND_SHA_RUNTIME_FILE_CHECK_ON_GPU_WORKER",
                "input_shape": [1, 609, 1, 721], "gpu_called": False, "board_used": False,
                "hashes_checked_once": len(self.hashes)}

    def record(self, stage, **extra):
        self.phase = stage
        value = {"schema": SCHEMA + "/job", "run_id": self.run.name,
                 "experiment_id": self.config["experiment_id"], "mode": self.mode,
                 "stage": stage, "last_valid_state": self.last_valid, "updated_utc": utc(),
                 "elapsed_s": time.perf_counter() - self.started, "step": 0, "total_steps": 609,
                 "eta_s": None, "gpu_called": any(r.get("actual_new_computation") for r in self.results.values()),
                 "gpu_worker_invocations": list(self.invocations), "PL_execution": False, **extra}
        write_json(self.run / "job.json", value)
        with (self.run / "events.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(value, allow_nan=False) + "\n")
        if stage in STAGES:
            self.last_valid = stage
        return value

    def progress(self, step):
        self.record(self.phase, step=step)

    def accepted(self, backend):
        source = self.config["accepted"][backend]
        root = self.path(source["root"])
        receipt = load_json(self.path(source["receipt"]))
        require(receipt.get("status", "").startswith("PASS"), "CACHE_UNACCEPTED", backend)
        result = load_json(root / "result.json")
        identity = load_json(root / "run_identity.json")
        require(result["status"].startswith("PASS") and result["steps"] == 609 and
                identity["run_id"] == source["run_id"] and identity["backend_binding_id"] == self.binding["backend_binding_id"] and
                identity["comparison_id"] == self.config["experiment_id"] and identity["mode"] == backend,
                "CACHE_IDENTITY", backend)
        for field, expected in self.cache_context.items():
            if field in identity:
                require(identity[field] == expected, "CACHE_IDENTITY", backend + ":" + field)
        source_hashes = set(identity["code_sha256"].values())
        names = ("full", "r_only") if backend == "FullGPU" else ("r_only", "h_step", "coordinator", "gpu_adapter")
        require(all(self.digest(self.sources[n]) in source_hashes for n in names), "CACHE_SOURCE", backend)
        if backend == "PythonReplacement":
            require(result["unified_committed_steps"] == result["independent_H_steps"] == 609 and
                    result["native_H_production_updates"] == 0 and result["FPGA_execution"] is False,
                    "CACHE_COMMIT", backend)
            require(any(row["run_id"] == identity["run_id"] for row in receipt["Python_runs"]), "CACHE_UNACCEPTED", "receipt run")
        else:
            require(result["board_used"] is False and receipt["backend_binding_id"] == self.binding["backend_binding_id"],
                    "CACHE_UNACCEPTED", "Full receipt")
        return self.result_files(root, backend, identity["run_id"], actual=False, key=self.keys[backend])

    def result_files(self, root, backend, run_id, actual, key):
        manifest = entries(load_json(root / "artifact_manifest.json"))
        essential = ("result.json", "run_identity.json", "activities_full.npy", "step_status.jsonl")
        for name in essential:
            require(name in manifest and self.digest(root / name) == manifest[name], "CACHE_CORRUPT", str(root / name))
        trajectory = np.load(root / "activities_full.npy", mmap_mode="r", allow_pickle=False)
        require(trajectory.shape == (1, 609, 45669) and trajectory.dtype == np.float32, "SHAPE", backend)
        statuses = [json.loads(line) for line in (root / "step_status.jsonl").read_text().splitlines() if line.strip()]
        commit = "COMMITTED" if backend == "PythonReplacement" else "FULL_REFERENCE_ONLY"
        rows = [row for row in statuses if row.get("status") == commit]
        require([row["step_id"] for row in rows] == list(range(609)), "STEP_COMMIT", backend)
        if backend == "PythonReplacement":
            require(all(row["state_token"] == row["step_id"] + 1 and row["native_H_update_count"] == 0 for row in rows),
                    "STEP_COMMIT", "Replacement tokens")
        else:
            require(all(row["run_id"] == run_id for row in rows), "STEP_IDENTITY", "Full run IDs")
        return {"backend": backend, "cache_key": key, "path": str(root), "source_run_id": run_id,
                "actual_new_computation": actual, "execution_kind": "actual_new_computation" if actual else "accepted_cache_replay",
                "PL_execution": False, "essential_sha256": {name: manifest[name] for name in essential}}

    def cached(self, backend, register=True):
        index = own_path("cache", backend, self.keys[backend] + ".json")
        if index.exists():
            value = load_json(index)
            require(value["cache_key"] == self.keys[backend] and value["backend"] == backend,
                    "CACHE_IDENTITY", str(index))
            root = self.path(value["path"])
            if root.is_relative_to(own_path("runs")):
                summary = audit(root.parent)
                require(summary["status"] == "PASS_BOUNDED_AUDIT", "CACHE_UNACCEPTED", "unsealed generated result")
                sealed_summary = load_json(root.parent / "run_summary.json")
                require(sealed_summary["cache_keys"][backend] == self.keys[backend] and
                        sealed_summary["results"][backend]["source_run_id"] == value["source_run_id"],
                        "CACHE_IDENTITY", "generated cached context differs")
                return self.result_files(root, backend, value["source_run_id"], False, self.keys[backend])
        value = self.accepted(backend)
        if register:
            write_json(index, value)
        return value

    def worker(self, backend):
        authorize(self.config, backend, self.keys[backend])
        require(self.mode != "formal", "FORMAL_PROTOCOL_REQUIRED", "Phase1 cannot substitute fast checks for a preregistered formal run")
        require(self.config["runtime"]["kind"] in ("wsl", "linux"), "RUNTIME", "GPU workers require existing WSL/Linux CUDA env")
        write_json(self.run / "worker_spec.json", {"config": self.config, "cache_keys": self.keys,
                   "resolved_sources": {n: str(p) for n, p in self.sources.items()}, "bundle": str(self.bundle)})
        script, spec = HERE / "worker.py", self.run / "worker_spec.json"
        args = [wsl_path(script), "--spec", wsl_path(spec), "--backend", backend, "--out", wsl_path(self.run / backend)]
        runtime = self.config["runtime"]
        command = (["wsl.exe", "-e", runtime["python"], "-B", *args] if os.name == "nt" else
                   [runtime["python"], "-B", *args])
        request_log = {"command": command, "started_utc": utc(), "invocation_uuid": str(uuid.uuid4())}
        write_json(self.run / (backend + "_launch.json"), request_log)
        started = time.perf_counter()
        with (self.run / (backend + ".log")).open("wb") as output:
            proc = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT)
            self.invocations.append(backend)
            try:
                deadline = started + self.config["timeouts"]["worker_s"] + self.config["timeouts"]["queue_s"] + 10
                while proc.poll() is None:
                    require(time.perf_counter() < deadline, "WORKER_TIMEOUT", backend)
                    progress = self.run / backend / "progress.json"
                    if progress.exists():
                        row = load_json(progress)
                        self.record(self.phase, step=row.get("step", 0), worker_status=row.get("status"),
                                    eta_s=row.get("eta_s"))
                    time.sleep(.5)
            except BaseException:
                # Cooperative worker owns its GPU step/lock and enforces its own deadline.
                # Never kill a WSL launcher and assume its CUDA child has stopped.
                write_json(self.run / "STOP_REQUEST.json", {"requested_utc": utc(), "reason": "runner interruption/timeout"})
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    write_json(self.run / "RESOURCE_QUARANTINE.json", {"backend": backend, "pid": proc.pid,
                               "status": "WORKER_COMPLETION_UNCONFIRMED_DO_NOT_RETRY"})
                request_log.update(stop_requested_utc=utc(), returncode=proc.poll(),
                                   wall_s=time.perf_counter() - started,
                                   completion_confirmed=proc.poll() is not None)
                write_json(self.run / (backend + "_launch.json"), request_log)
                raise
        request_log.update(completed_utc=utc(), wall_s=time.perf_counter() - started, returncode=proc.returncode)
        write_json(self.run / (backend + "_launch.json"), request_log)
        require(proc.returncode == 0, "WORKER_FAILED", backend + ": see retained log/failure.json")
        root = self.run / backend
        identity = load_json(root / "run_identity.json")
        require(identity["backend_binding_id"] == self.binding["backend_binding_id"] and identity["cache_key"] == self.keys[backend],
                "WORKER_IDENTITY", backend)
        result = load_json(root / "result.json")
        require(result["status"] == "PASS_FAST_COMPUTE" and result["steps"] == 609, "WORKER_INCOMPLETE", backend)
        return self.result_files(root, backend, identity["run_id"], True, self.keys[backend])

    def execute(self, preflight=False, dry_run=False, cache_only=False, run_id=None):
        name = run_id or ("job_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:8])
        require(re.fullmatch(r"[A-Za-z0-9_-]{1,100}", name) is not None, "RUN_ID", name)
        self.run = own_path("runs", name)
        require(not self.run.exists(), "RUN_EXISTS", "Existing run preserved: " + name)
        self.run.mkdir(parents=True)
        write_json(self.run / "config_snapshot.json", self.config)
        try:
            start = time.perf_counter()
            report = self.validate()
            self.stage_times["preflight"] = time.perf_counter() - start
            write_json(self.run / "preflight.json", report)
            self.record("FROZEN_INPUT")
            plan = {}
            start = time.perf_counter()
            for backend in ("FullGPU", "PythonReplacement"):
                # formal fresh-process obligations are never met by cache.
                fresh = self.config.get("fresh_full" if backend == "FullGPU" else "fresh_replacement", False)
                if self.mode == "formal" or fresh:
                    plan[backend] = "FRESH_REQUIRED"
                    continue
                try:
                    self.results[backend] = self.cached(backend)
                    plan[backend] = "ACCEPTED_CACHE_HIT"
                except (FileNotFoundError, RunnerError) as exc:
                    if isinstance(exc, RunnerError) and exc.code != "CACHE_UNACCEPTED":
                        raise
                    plan[backend] = "CACHE_MISS"
            self.stage_times["cache_lookup"] = time.perf_counter() - start
            self.record("READY_FULL", plan=plan)
            write_json(self.run / "plan.json", {"mode": self.mode, "backends": plan, "cache_keys": self.keys,
                       "steps": 609, "PL_execution": False, "will_call_gpu": not (preflight or dry_run or cache_only) and len(self.results) < 2})
            if preflight or dry_run:
                return self.finish("PASS_DRY_RUN" if dry_run else "PASS_PREFLIGHT", complete=False, plan=plan)
            if cache_only:
                require(len(self.results) == 2, "CACHE_MISS", "cache-only cannot start computation")
            for backend, stage in (("FullGPU", "FULL_DONE"), ("PythonReplacement", "REPLACEMENT_DONE")):
                start = time.perf_counter()
                self.phase = "RUNNING_" + backend
                if backend not in self.results:
                    self.results[backend] = self.worker(backend)
                self.stage_times[backend] = time.perf_counter() - start
                self.record(stage, step=609, result=self.results[backend])
            start = time.perf_counter()
            self.phase = "FAST_CHECK_RUNNING"
            comparison = quick_compare(Path(self.results["FullGPU"]["path"]) / "activities_full.npy",
                                       Path(self.results["PythonReplacement"]["path"]) / "activities_full.npy",
                                       self.candidate["h_global_node_indices"], self.progress)
            write_json(self.run / "fast_check.json", comparison)
            self.stage_times["fast_check"] = time.perf_counter() - start
            self.record("FAST_CHECK_DONE", step=609)
            return self.finish("PASS_FAST_CACHE_REPLAY" if not any(r["actual_new_computation"] for r in self.results.values()) else
                               "PASS_FAST_ACTUAL_SOFTWARE", complete=True, comparison=comparison)
        except BaseException as exc:
            value = {"type": type(exc).__name__, "code": getattr(exc, "code", "UNHANDLED_ERROR"),
                     "message": str(exc), "traceback": traceback.format_exc(), "failed_phase": self.phase,
                     "last_valid_state": self.last_valid, "failed_utc": utc(), "automatic_retry": False}
            write_json(self.run / "failure.json", value)
            self.record("FAILED", error=value)
            self.finish("FAILED", complete=False, failure=value)
            raise RunnerError(value["code"], value["message"], name) from exc

    def finish(self, status, complete, **extra):
        timing = {backend: load_json(Path(r["path"]) / "result.json").get("timing", {})
                  for backend, r in self.results.items() if r["actual_new_computation"]}
        summary = {"schema": SCHEMA + "/summary", "run_id": self.run.name, "status": status,
                   "mode": self.mode, "experiment_id": self.config["experiment_id"], "created_utc": utc(),
                   "stage_timings_s": self.stage_times, "wall_s": time.perf_counter() - self.started,
                   "actual_new_computation": any(r["actual_new_computation"] for r in self.results.values()),
                   "gpu_worker_invocations": self.invocations,
                   "PL_execution": False, "FPGA_status": "NOT_CONNECTED", "results": self.results,
                   "worker_timings": timing, "cache_keys": getattr(self, "keys", {}),
                   "last_valid_state": self.last_valid, "automatic_retry": False,
                   "hashes_checked_once": len(self.hashes), "stopped_at_acceptance": complete, **extra}
        summary["partial_worker_evidence"] = {}
        for backend in self.invocations:
            failure_path = self.run / backend / "failure.json"
            if failure_path.exists():
                partial = load_json(failure_path)
                summary["partial_worker_evidence"][backend] = partial
                summary["actual_new_computation"] |= partial.get("completed_steps", 0) > 0
        if complete:
            summary["final_stage"] = "COMPLETE"
        elif status == "FAILED":
            summary["final_stage"] = "FAILED"
        actual_worker_wall = sum(row.get("worker_wall_s", 0.) for row in timing.values())
        summary["timing_accounting"] = {"runner_wall_before_seal_s": summary["wall_s"],
             "compute_backend_calls_s": sum(row.get("compute_backend_calls_s", 0.) for row in timing.values()),
             "actual_worker_wall_s": actual_worker_wall,
             "orchestration_outside_worker_s": max(0., summary["wall_s"] - actual_worker_wall),
             "model_load_count": sum(row.get("model_load_count", 0) for row in timing.values()),
             "redundant_model_loads": sum(row.get("redundant_model_loads", 0) for row in timing.values()),
             "transfer_only_s": 0. if not timing else None,
             "note": "CLI total wall including startup/seal measured externally in verification; cache replay has zero new compute/loads/transfers"}
        write_json(self.run / "run_summary.json", summary)
        if complete:
            write_json(self.run / "seal.json", {"schema": SCHEMA + "/seal", "files": {
                name: sha(self.run / name) for name in ("config_snapshot.json", "preflight.json", "plan.json",
                                                       "fast_check.json", "run_summary.json")}})
            self.record("SEALED", step=609)
            self.record("COMPLETE", step=609)
            for backend, value in self.results.items():
                if value["actual_new_computation"]:
                    write_json(own_path("cache", backend, self.keys[backend] + ".json"), value)
        else:
            if status != "FAILED":
                self.record(status)
        return summary


def audit(root):
    """Single bounded verification of seal and essential results, no recomputation."""
    started = time.perf_counter()
    require(load_json(root / "job.json")["stage"] == "COMPLETE", "AUDIT_STATUS", "Job has not completed")
    seal = load_json(root / "seal.json")
    for name, expected in seal["files"].items():
        require((root / name).resolve().is_relative_to(root.resolve()), "PATH", name)
        require(sha(root / name) == expected, "SEAL_MISMATCH", name)
    summary = load_json(root / "run_summary.json")
    require(summary["status"].startswith("PASS_FAST") and summary["PL_execution"] is False,
            "AUDIT_STATUS", "Only sealed fast result is accepted")
    for value in summary["results"].values():
        for name, expected in value["essential_sha256"].items():
            require(sha(host_path(value["path"]) / name) == expected, "RESULT_CHANGED", name)
    return {"status": "PASS_BOUNDED_AUDIT", "run_id": root.name, "audit_s": time.perf_counter() - started,
            "source_status": summary["status"], "actual_new_computation": summary["actual_new_computation"],
            "PL_execution": False, "neural_computation_calls": 0}

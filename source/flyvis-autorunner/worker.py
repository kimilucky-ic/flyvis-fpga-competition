"""One authorized CUDA computation using read-only accepted neural cores.

No neural equations, camera capture, decoder, PL access, or auto retries.
"""
import argparse
import importlib.metadata
import os
if os.name != "nt":
    import fcntl
import subprocess
import sys
import time
import traceback
import uuid
from pathlib import Path

sys.dont_write_bytecode = True
import numpy as np
from autorunner import (HERE, RunnerError, authorize, canonical, entries, host_path,
                        load_json, own_path, require, sha, utc, write_json)


def runtime_probe(checkpoint, expected):
    require(sha(checkpoint) == expected, "CHECKPOINT", "Installed checkpoint differs")
    return {"status": "PASS_RUNTIME_FILE_PROBE_NO_GPU", "checkpoint_sha256": expected,
            "python": sys.version, "numpy": np.__version__,
            "torch_installed_version": importlib.metadata.version("torch"),
            "torch_imported": "torch" in sys.modules, "GPU_called": False}


class Window:
    def init__(self, spec, backend, out):
        self.spec, self.backend, self.out = spec, backend, out
        self.config = spec["config"]
        self.key = spec["cache_keys"][backend]
        self.started = time.perf_counter()
        self.deadline = None

    def check(self):
        authorize(self.config, self.backend, self.key)
        require(not (self.out.parent / "STOP_REQUEST.json").exists(), "STOP_REQUESTED", "runner requested cooperative stop")
        require(not own_path("runtime", "RESOURCE_QUARANTINE.json").exists(), "RESOURCE_QUARANTINE", "GPU completion unresolved")
        if self.deadline is not None:
            require(time.perf_counter() < self.deadline, "COMPUTE_TIMEOUT", "No further step or COMMIT")

    def progress(self, status, step=0):
        write_json(self.out / "progress.json", {"status": status, "step": step, "total_steps": 609,
                   "updated_utc": utc(), "elapsed_s": time.perf_counter() - self.started,
                   "eta_s": None if step == 0 else (time.perf_counter() - self.started) / step * (609 - step)})

    def acquire(self):
        self.check()
        lock = own_path("runtime", "gpu.lock")
        lock.parent.mkdir(parents=True, exist_ok=True)
        handle = lock.open("a+")
        started = time.perf_counter()
        queue_deadline = started + self.config["timeouts"]["queue_s"]
        while True:
            self.check()
            acquired = False
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
            except BlockingIOError:
                pass
            external_busy = any((host_path(p) if host_path(p).is_absolute() else HERE / host_path(p)).exists()
                                for p in self.config["runtime"]["busy_markers"])
            if acquired and not external_busy:
                try:
                    probe = subprocess.run(["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader,nounits"],
                                           capture_output=True, text=True, timeout=5, check=True)
                    busy = bool(probe.stdout.strip())
                except (subprocess.SubprocessError, OSError) as exc:
                    handle.close()
                    raise RunnerError("GPU_RESOURCE_UNKNOWN", str(exc)) from exc
                if not busy:
                    ticket = self.config["scope"]["gpu"]
                    ledger = own_path("runtime", "invocations", canonical(ticket) + "_" + self.backend + ".json")
                    ledger.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        with ledger.open("x", encoding="utf-8") as stream:
                            import json
                            json.dump({"started_utc": utc(), "worker_uuid": str(uuid.uuid4()),
                                       "backend": self.backend, "cache_key": self.key, "out": str(self.out)}, stream)
                    except FileExistsError as exc:
                        handle.close()
                        raise RunnerError("INVOCATION_LIMIT", "This GPU scope already attempted this backend") from exc
                    self.deadline = time.perf_counter() + self.config["timeouts"]["worker_s"]
                    self.check()
                    self.progress("LOADING")
                    return handle, time.perf_counter() - started
            if acquired:
                fcntl.flock(handle, fcntl.LOCK_UN)
            self.progress("QUEUED_GPU_BUSY")
            if time.perf_counter() >= queue_deadline:
                handle.close()
                raise RunnerError("GPU_BUSY_TIMEOUT", "GPU locked/busy; no process was interrupted")
            time.sleep(min(.5, max(.01, queue_deadline - time.perf_counter())))


def configure(out):
    scratch = out / "runtime"
    os.environ.update(CUDA_VISIBLE_DEVICES="0", FLYVIS_ROOT_DIR=str(scratch / "flyvis"),
                      MPLBACKEND="Agg", MPLCONFIGDIR=str(scratch / "matplotlib"),
                      NUMBA_CACHE_DIR=str(scratch / "numba"), CUBLAS_WORKSPACE_CONFIG=":4096:8",
                      PYTHONDONTWRITEBYTECODE="1")
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.manual_seed(0)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    require(torch.cuda.is_available(), "CUDA_UNAVAILABLE", "No CPU fallback")
    return torch


class CameraBoundR:
    """Runner-owned binding adapter around the unchanged RStepService."""
    def init__(self, service, stimulus, window):
        self.service, self.stimulus, self.window = service, stimulus, window
        names = ("_r", "_source", "_target", "_weight", "_bias", "_tau", "_inv_tau", "_input_r", "_hex_index")
        self.before = {n: self.tensor_digest(n) for n in names}
        self.r_compute_s = 0.

    def __getattr__(self, name):
        return getattr(self.service, name)

    def tensor_digest(self, name):
        a = np.ascontiguousarray(getattr(self.service, name).detach().cpu().numpy())
        return canonical({"shape": list(a.shape), "dtype": str(a.dtype), "bytes": __import__("hashlib").sha256(a.tobytes()).hexdigest()})

    def assert_weights_unchanged(self):
        require(all(self.tensor_digest(n) == value for n, value in self.before.items()), "R_PARAMETERS_CHANGED", "resident R parameters")

    def step(self, old_full, hex_frame, *, step_id, run_id, condition_id):
        self.window.check()
        require(condition_id == "selected_100_190" and 0 <= step_id < 609, "STEP_IDENTITY", "camera condition")
        require(np.array_equal(hex_frame.detach().cpu().numpy(), self.stimulus[0, step_id, 0]), "FRAME_MISMATCH", "frozen input")
        import torch
        torch.cuda.synchronize()
        started = time.perf_counter()
        response = self.service.step(old_full, hex_frame, step_id=step_id, run_id=run_id, condition_id=condition_id)
        torch.cuda.synchronize()
        self.r_compute_s += time.perf_counter() - started
        return response


def compute(spec, backend, out):
    window = Window(spec, backend, out)
    lock = None
    torch = None
    state = None
    coordinator = None
    completed = 0
    started = time.perf_counter()
    binding = load_json(host_path(spec["bundle"]) / "camera_backend_identity.json")
    try:
        runtime = spec["config"]["runtime"]
        runtime_probe(runtime["checkpoint"], binding["checkpoint_sha256"])
        sources = {n: host_path(p) for n, p in spec["resolved_sources"].items()}
        sys.path.insert(0, str(sources["full"].parent))
        sys.path.insert(0, str(sources["h_step"].parent))
        expected_sources = {n: sha(p) for n, p in sources.items()}
        for name, pin in spec["config"]["pins"].items():
            if name.startswith("source_"):
                p = host_path(pin["path"])
                require(sha(p if p.is_absolute() else HERE / p) == pin["sha256"], "SOURCE_CHANGED", name)
        bundle = host_path(spec["bundle"])
        for name, expected in entries(load_json(bundle / "artifact_manifest.json")).items():
            path = (bundle / name).resolve()
            require(path.is_relative_to(bundle.resolve()) and sha(path) == expected,
                    "INPUT_CHANGED", "worker entry: " + name)
        stimulus = np.load(bundle / "stimulus.npy", mmap_mode="r", allow_pickle=False)
        initial = np.load(bundle / "initial_state_full.npy", allow_pickle=False).reshape(-1)
        lock, queue_s = window.acquire()
        load_started = time.perf_counter()
        torch = configure(out)
        from full_oracle import FullNetworkOracle
        if backend == "FullGPU":
            service = FullNetworkOracle(bundle / "identity_manifest.json", model_path=runtime["model_path"], device="cuda:0")
            require(service.net.training is False, "EVAL_MODE", "Full model must stay eval")
            old = torch.as_tensor(initial.copy(), device="cuda:0")
        else:
            from r_only import RStepService
            from h_step import HUpdater
            from coordinator import Coordinator
            from gpu_adapter import GPUAdapter
            from run_closed_loop import validate_parameters, native_full_forbidden
            class TimedHUpdater(HUpdater):
                compute_s = 0.
                def step(self, request):
                    started = time.perf_counter()
                    result = super().step(request)
                    self.compute_s += time.perf_counter() - started
                    return result
            class TimedGPUAdapter(GPUAdapter):
                transfer_and_adapter_s = 0.
                def evaluate(self, old_full, x_full, tag):
                    started = time.perf_counter()
                    before = self.service.r_compute_s
                    result = super().evaluate(old_full, x_full, tag)
                    self.transfer_and_adapter_s += time.perf_counter() - started - (self.service.r_compute_s - before)
                    return result
            h = TimedHUpdater(bundle / "static_boundary_gpu_native.npz")
            inputs = validate_parameters(h, bundle / "expanded_parameters.npz")
            service = CameraBoundR(RStepService(bundle / "expanded_parameters.npz", bundle / "identity_manifest.json",
                                   bundle / "candidates/B_T5c/candidate_manifest.json", device="cuda:0"), stimulus, window)
            adapter = TimedGPUAdapter(service, inputs)
        torch.cuda.synchronize()
        load_s = time.perf_counter() - load_started
        identity = {**binding, "run_id": str(uuid.uuid4()), "mode": backend,
                    "cache_key": spec["cache_keys"][backend], "started_utc": utc(), "command": [sys.executable, *sys.argv],
                    "execution_kind": "actual_new_computation", "PL_execution": False,
                    "runner_sources": {p.name: sha(p) for p in (HERE / "runner.py", HERE / "autorunner.py", HERE / "worker.py")},
                    "kernel_sources": expected_sources, "torch": torch.__version__, "numpy": np.__version__,
                    "pid": os.getpid(), "gpu": torch.cuda.get_device_name(0)}
        write_json(out / "run_identity.json", identity)
        state = np.lib.format.open_memmap(out / "activities_full.npy", mode="w+", shape=(1, 609, 45669), dtype=np.float32)
        if backend == "PythonReplacement":
            coordinator = Coordinator(h, adapter, initial, identity["run_id"], binding["comparison_id"], binding["condition_id"])
        compute_s = 0.
        transfer_record_s = 0.
        loop_started = time.perf_counter()
        from contextlib import nullcontext
        guard_context = native_full_forbidden() if backend == "PythonReplacement" else nullcontext(None)
        with (out / "step_status.jsonl").open("a", encoding="utf-8") as log, guard_context as guard:
            for k in range(609):
                window.check()
                tick = time.perf_counter()
                if backend == "FullGPU":
                    frame = torch.as_tensor(np.array(stimulus[0, k, 0], copy=True), device="cuda:0")
                    torch.cuda.synchronize()
                    transfer_record_s += time.perf_counter() - tick
                    tick = time.perf_counter()
                    candidate = service.step(old, frame)
                    torch.cuda.synchronize()
                    compute_s += time.perf_counter() - tick
                    window.check()
                    tick = time.perf_counter()
                    old = candidate
                    actual = old.cpu().numpy().copy()
                    row = {"status": "FULL_REFERENCE_ONLY", "step_id": k, "run_id": identity["run_id"]}
                else:
                    x = np.zeros(45669, dtype=np.float32)
                    x[inputs.reshape(-1)] = np.tile(stimulus[0, k, 0], 8)
                    prepared = coordinator.prepare(k, x, "SOURCE_RAW")
                    window.check()
                    actual = coordinator.commit(prepared)
                    torch.cuda.synchronize()
                    compute_s += time.perf_counter() - tick
                    tick = time.perf_counter()
                    row = coordinator.logs[-1]
                    log.write(__import__("json").dumps(coordinator.logs[-2]) + "\n")
                require(np.isfinite(actual).all(), "NONFINITE", "computed candidate")
                state[0, k] = actual
                log.write(__import__("json").dumps(row) + "\n")
                log.flush()
                completed = k + 1
                transfer_record_s += time.perf_counter() - tick
                window.progress("COMPUTING", completed)
            if backend == "PythonReplacement":
                require(h.step_count == adapter.calls == coordinator.next_step_id == 609 and
                        guard["forbidden_native_call_count"] == 0, "COMMIT_COUNT", "H/R/atomic COMMIT")
        window.check()
        service.assert_weights_unchanged()
        require(all(sha(p) == expected_sources[n] for n, p in sources.items()), "SOURCE_CHANGED", "during computation")
        state.flush()
        np.save(out / "final_state_full.npy", state[0, -1])
        torch.cuda.synchronize()
        loop_wall_s = time.perf_counter() - loop_started
        backend_compute_s = compute_s if backend == "FullGPU" else service.r_compute_s + h.compute_s
        write_json(out / "result.json", {"status": "PASS_FAST_COMPUTE", "steps": completed, "run_id": identity["run_id"],
                   "backend": backend, "actual_new_computation": True, "PL_execution": False,
                   "timing": {"worker_wall_s": time.perf_counter() - started, "queue_s": queue_s, "model_load_s": load_s,
                   "loop_wall_s": loop_wall_s, "compute_backend_calls_s": backend_compute_s,
                   "replacement_prepare_commit_s": compute_s if coordinator else None,
                   "transfer_and_recording_s": transfer_record_s,
                   "r_transfer_and_adapter_s": adapter.transfer_and_adapter_s if coordinator else None,
                   "transfer_only_s": None,
                   "transfer_scope": "CUDA calls measured with synchronization; R transfer interval includes immutable GPUAdapter validation; transfer-only not claimed",
                   "model_load_count": 1, "redundant_model_loads": 0,
                   "state_uploads": completed if coordinator else 1, "frame_uploads": completed,
                   "candidate_downloads": completed, "steps": completed}, "completed_utc": utc(), "native_H_production_updates": 0 if coordinator else 609})
        # Seal essential scientific evidence only; runtime caches are not audited.
        write_json(out / "artifact_manifest.json", {"files": {name: sha(out / name) for name in
                   ("run_identity.json", "result.json", "activities_full.npy", "final_state_full.npy", "step_status.jsonl")}})
        window.progress("COMPLETE", completed)
    except BaseException as exc:
        if state is not None:
            state.flush()
        if coordinator is not None:
            np.save(out / "last_committed_full_state.npy", coordinator.state)
        elif state is not None and completed:
            np.save(out / "last_committed_full_state.npy", state[0, completed - 1])
        write_json(out / "failure.json", {"code": getattr(exc, "code", "WORKER_ERROR"), "type": type(exc).__name__,
                   "message": str(exc), "traceback": traceback.format_exc(), "completed_steps": completed,
                   "pending_step": coordinator.pending.tag.step_id if coordinator and coordinator.pending else None,
                   "failed_utc": utc(), "automatic_retry": False, "incomplete_arrays_are_results": False})
        window.progress("FAILED", completed)
        raise
    finally:
        cleanup_error = None
        already_failing = sys.exc_info()[0] is not None
        if torch is not None:
            try:
                torch.cuda.synchronize()
            except BaseException as exc:
                cleanup_error = exc
                write_json(own_path("runtime", "RESOURCE_QUARANTINE.json"), {"status": "CUDA_COMPLETION_UNCONFIRMED",
                           "out": str(out), "error": str(exc), "automatic_retry": False})
                failure_path = out / "failure.json"
                failure = load_json(failure_path) if failure_path.exists() else {"code": "CUDA_COMPLETION_UNCONFIRMED",
                          "type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc(),
                          "completed_steps": completed, "failed_utc": utc(), "incomplete_arrays_are_results": False}
                failure["cleanup_error"] = str(exc)
                write_json(failure_path, failure)
                window.progress("FAILED", completed)
        if lock is not None:
            fcntl.flock(lock, fcntl.LOCK_UN)
            lock.close()
        if cleanup_error is not None and not already_failing:
            raise RunnerError("CUDA_COMPLETION_UNCONFIRMED", str(cleanup_error))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--spec")
    p.add_argument("--backend", choices=("FullGPU", "PythonReplacement"))
    p.add_argument("--out")
    p.add_argument("--probe-checkpoint")
    p.add_argument("--expected-sha")
    args = p.parse_args()
    if args.probe_checkpoint:
        print(__import__("json").dumps(runtime_probe(args.probe_checkpoint, args.expected_sha)))
        return
    out = host_path(args.out).resolve()
    require(out.is_relative_to(own_path("runs")), "WRITE_SCOPE", str(out))
    require(not out.exists(), "RUN_EXISTS", "worker output preserved")
    spec = load_json(host_path(args.spec))
    authorize(spec["config"], args.backend, spec["cache_keys"][args.backend])
    out.mkdir(parents=True)
    compute(spec, args.backend, out)


if __name__ == "__main__":
    main()

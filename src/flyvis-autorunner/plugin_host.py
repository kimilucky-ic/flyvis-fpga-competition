"""Independent CLI adapter for B4's public scientific plugin, one process only."""
import argparse
import importlib.util
import json
import os
import sys
import time
import traceback
from pathlib import Path

sys.dont_write_bytecode = True
from autorunner import load_json, own_path, utc, write_json
from plugin_contract import Lease, path, predecessor, validate


def module_for(spec):
    module_path = path(spec["computational_module"])
    sys.path.insert(0, str(module_path.parent))
    found = importlib.util.spec_from_file_location("b4_science_plugin", module_path)
    module = importlib.util.module_from_spec(found)
    found.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticket")
    parser.add_argument("--cpu-check", metavar="CONFIG")
    args = parser.parse_args()
    if args.cpu_check:
        config = load_json(args.cpu_check)
        spec, key = validate(config)
        # B needs A only at actual launch; both stages may prepare on CPU first.
        result = {"status": "PASS_CPU_PUBLIC_INTERFACE", "identity_key": key,
                  "AST_checked": True, "GPU_called": False, "torch_imported": "torch" in sys.modules}
        print(json.dumps(result))
        return 0
    ticket = load_json(args.ticket)
    config = ticket["config"]
    job = path(ticket["job_dir"])
    lock = None
    started = time.monotonic()
    code = 0
    try:
        spec, key = validate(config)
        if key != ticket["identity_key"]:
            raise ValueError("Ticket identity changed")
        predecessor(config)
        lease = Lease(ticket)
        lock, queue_s = lease.acquire()
        write_json(job / "host_identity.json", {"pid": os.getpid(), "command": sys.argv,
                   "started_utc": utc(), "identity_key": key, "lock": str(own_path("runtime", "gpu.lock")),
                   "queue_s": queue_s, "stage": config["stage"], "PL_execution": False})
        module = module_for(spec)
        lease.check("before_public_plugin")
        result = module.run_experiment(str(path(config["spec_path"])), str(path(config["output_dir"])), lease.check)
        write_json(job / "host_result.json", {"status": "COMPLETE", "worker_run_id": result["run_id"],
                   "queue_s": queue_s, "host_wall_s": time.monotonic() - started})
    except BaseException as exc:
        code = 2
        write_json(job / "host_failure.json", {"status": "FAILED_PRESERVED_NO_RETRY",
                   "code": getattr(exc, "code", "PLUGIN_EXCEPTION"), "error": repr(exc),
                   "traceback": traceback.format_exc(), "elapsed_s": time.monotonic() - started})
        print(traceback.format_exc(), file=sys.stderr, flush=True)
    finally:
        try:
            torch = sys.modules.get("torch")
            if torch is not None and torch.cuda.is_initialized():
                torch.cuda.synchronize()
        except BaseException as exc:
            code = 2
            write_json(own_path("runtime", "RESOURCE_QUARANTINE.json"), {
                "job_dir": str(job), "reason": "CUDA_COMPLETION_UNCONFIRMED", "error": repr(exc), "updated_utc": utc()})
        if lock is not None:
            lock.close()
        write_json(job / "host_exit.json", {"pid": os.getpid(), "exit_code": code,
                   "completed_utc": utc(), "host_wall_s": time.monotonic() - started,
                   "lock_released": True, "GPU_work_completion_confirmed": code == 0})
    return code


if __name__ == "__main__":
    raise SystemExit(main())

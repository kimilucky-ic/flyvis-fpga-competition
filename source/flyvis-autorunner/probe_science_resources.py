"""Read-only WSL resource release evidence; never imports torch or board tools."""
import argparse
import fcntl
import json
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
from autorunner import own_path, utc, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    probe = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,process_name,used_gpu_memory", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=10)
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.free,memory.total", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=10)
    processes = subprocess.run(["ps", "-eo", "pid,comm,args"], capture_output=True, text=True, timeout=10)
    selected = [row for row in processes.stdout.splitlines() if any(name in row for name in
                ("plugin_host.py", "science_worker.py", "run_pilot.py", "worker.py", "nvidia-smi", "vivado", "xsim"))]
    markers = [str(own_path("runtime", name)) for name in ("RESOURCE_QUARANTINE.json", "EXTERNAL_GPU_BUSY.json", "BOARD_RESERVED.json")
               if own_path("runtime", name).exists()]
    lock_path = own_path("runtime", "gpu.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_free = False
    with lock_path.open("a+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_free = True
        except BlockingIOError:
            pass
    value = {"checked_utc": utc(), "compute_query_exit": probe.returncode, "compute_processes": probe.stdout.strip(),
        "compute_query_error": probe.stderr, "GPU": gpu.stdout.strip(), "relevant_processes": selected,
        "resource_markers": markers, "GPU_lock_free": lock_free, "disk_free_bytes": shutil.disk_usage(lock_path.parent).free,
        "ready": probe.returncode == gpu.returncode == 0 and not probe.stdout.strip() and not markers and lock_free,
        "CUDA_initialized": False, "board_IO": False}
    write_json(own_path(args.out), value)
    print(json.dumps(value, indent=2))


if __name__ == "__main__":
    main()

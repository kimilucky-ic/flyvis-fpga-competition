"""Independent process/lease readback after cooperative stop; no CUDA import."""
import fcntl,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
out=Path(__file__).resolve().parent
probe=subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],capture_output=True,text=True,timeout=10)
lock=Path('/mnt/c/Users/hzy72/Documents/ChatGPT/fpga/flyvis-autorunner/runtime/gpu.lock')
free=False
with lock.open('r') as stream:
    try:fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True
    except BlockingIOError:pass
result=dict(utc=datetime.now(timezone.utc).isoformat(),compute_query_exit=probe.returncode,compute_processes=probe.stdout.strip(),GPU_lock_free=free,CUDA_initialized=False,board_IO=False)
result['status']='PASS_RELEASED' if probe.returncode==0 and not probe.stdout.strip() and free else 'RELEASE_NOT_CONFIRMED'
(out/'independent_release.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result))

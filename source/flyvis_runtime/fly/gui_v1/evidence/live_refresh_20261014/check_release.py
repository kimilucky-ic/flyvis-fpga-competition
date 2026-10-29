import json,fcntl,subprocess,datetime
from pathlib import Path
lock=Path('/mnt/c/Users/hzy72/Documents/ChatGPT/fpga/flyvis-autorunner/runtime/gpu.lock')
free=False
with lock.open('r') as handle:
 try:
  fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(handle,fcntl.LOCK_UN)
 except BlockingIOError: pass
p=subprocess.run(['/usr/lib/wsl/lib/nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5)
r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),compute_query_exit=p.returncode,compute_processes=p.stdout.strip(),GPU_lock_free=free,CUDA_initialized=False,board_IO=False)
Path('/mnt/c/Users/hzy72/Documents/ChatGPT/fly/gui_v1/evidence/live_refresh_20261014/independent_release.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r))

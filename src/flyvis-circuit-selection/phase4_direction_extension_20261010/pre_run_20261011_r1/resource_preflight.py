"""Read-only Windows/WSL environment and resource observations, no CUDA tensors."""
from pathlib import Path
from datetime import datetime,timezone
import ctypes,csv,io,json,shutil,subprocess

HERE=Path(__file__).resolve().parent
def call(args):
    p=subprocess.run(args,capture_output=True,timeout=40)
    # WSL diagnostics may combine UTF16 Windows errors with UTF8 Linux stdout.
    def decode(b):
        return b.decode('utf-16-le',errors='replace') if b.count(b'\0')>len(b)//5 else b.decode('utf-8',errors='replace')
    return dict(args=args,returncode=p.returncode,stdout=decode(p.stdout),stderr=decode(p.stderr))
def main():
    out=HERE/'resource_observation_20261011_r1.json'
    if out.exists():raise SystemExit('Existing resource observation preserved')
    smi=call(['nvidia-smi.exe','--query-gpu=index,uuid,name,memory.total,memory.used,memory.free,utilization.gpu,driver_version','--format=csv,noheader'])
    apps=call(['nvidia-smi.exe','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'])
    # Imports report installed versions only; no cuda.is_available/context/op/model.
    probe='import json,os,sys,torch,numpy; m={k:int(v.split()[0])*1024 for k,v in (x.split(":",1) for x in open("/proc/meminfo"))}; rows=[]\nfor p in os.listdir("/proc"):\n if p.isdigit() and int(p)!=os.getpid():\n  try:\n   n=open("/proc/"+p+"/comm").read().strip()\n   if "python" in n:rows.append(dict(pid=int(p),comm=n))\n  except (FileNotFoundError,ProcessLookupError,PermissionError):pass\nprint(json.dumps(dict(python=sys.version,torch=torch.__version__,numpy=numpy.__version__,cuda_build=torch.version.cuda,WSL_available_memory_bytes=m["MemAvailable"],other_python_processes=rows,CUDA_tensor_operations=0,neural_updates=0)))'
    wsl=call(['wsl.exe','-d','FlyVisCPU','--','/opt/flyvis-gpu-venv/bin/python','-B','-c',probe])
    class Memory(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),('total_phys',ctypes.c_ulonglong),('avail_phys',ctypes.c_ulonglong),('total_page',ctypes.c_ulonglong),('avail_page',ctypes.c_ulonglong),('total_virtual',ctypes.c_ulonglong),('avail_virtual',ctypes.c_ulonglong),('avail_extended',ctypes.c_ulonglong)]
    mem=Memory();mem.length=ctypes.sizeof(mem)
    ok=ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
    rows=list(csv.reader(io.StringIO(smi['stdout']))) if smi['returncode']==0 else []
    observed_wsl=json.loads(wsl['stdout']) if wsl['returncode']==0 else None
    d=shutil.disk_usage(HERE)
    report=dict(status='RESOURCE_OBSERVATIONS_ONLY_NOT_EXCLUSIVE_GPU_APPROVAL',observed_utc=datetime.now(timezone.utc).isoformat(),
        disk=dict(target=str(HERE),total_bytes=d.total,free_bytes=d.free,free_GiB=d.free/1024**3,
            required_start_GiB=36,disk_start_gate='PASS' if d.free>=36*1024**3 else 'FAIL'),
        GPU_raw=smi,GPU_compute_apps_raw=apps,GPU_rows=rows,
        GPU_conflict='UNRESOLVED_UNTIL_A_COORDINATION',GPU_process_memory_attribution_available='Insufficient Permissions' not in apps['stdout'],
        Windows_memory=dict(query_success=bool(ok),free_bytes=mem.avail_phys if ok else None,total_bytes=mem.total_phys if ok else None),
        WSL_raw=wsl,WSL_environment=observed_wsl,
        CUDA_runtime_kernel_probe='NOT_RUN_BEFORE_CONFIRMED_SLOT',new_neural_updates=0,FPGA_execution=False,
        formal_run_authorized=False,observation_not_reservation=True)
    with out.open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(status=report['status'],free_GiB=report['disk']['free_GiB'],disk_gate=report['disk']['disk_start_gate'],GPU_conflict=report['GPU_conflict'],WSL_probe_returncode=wsl['returncode'],neural_updates=0)))
if __name__=='__main__':main()

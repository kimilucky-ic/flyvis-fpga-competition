import sys,os,subprocess,time,json,psutil
from pathlib import Path
p=Path(__file__).resolve().parent;r=p/sys.argv[1];stage=sys.argv[2]
start=time.monotonic();peak=0;minimum=psutil.virtual_memory().available
assert minimum>1024*2**20,'insufficient memory'
with (r/(stage+'_launcher.log')).open('w') as log:
 proc=subprocess.Popen(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(r/'launch.ps1'),'-Stage',stage],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
 root=psutil.Process(proc.pid);stop=None
 while proc.poll() is None:
  processes=[root]+root.children(recursive=True)
  rss=sum(x.memory_info().rss for x in processes if x.is_running());peak=max(peak,rss)
  minimum=min(minimum,psutil.virtual_memory().available)
  if time.monotonic()-start>1800 or rss>6500*2**20 or psutil.virtual_memory().available<128*2**20:
   stop='resource_or_time_limit'
   for x in reversed(processes):
    try:x.kill()
    except psutil.NoSuchProcess:pass
   break
  time.sleep(1)
 proc.wait()
result=dict(stage=stage,exit_code=proc.returncode,stop=stop,elapsed_seconds=time.monotonic()-start,peak_owned_MiB=peak/2**20,min_host_available_MiB=minimum/2**20,board_operations=0)
(r/(stage+'_RUN.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result))

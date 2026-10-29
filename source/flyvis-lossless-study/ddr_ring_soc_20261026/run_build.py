# Single isolated Vivado job. No bitstream or hardware commands.
from pathlib import Path
import subprocess,psutil,time,os,json
P=Path(__file__).resolve().parent;B=Path('C:/fpga_work/line11_ring_20261026');stages=[]
for proc in psutil.process_iter(['name']):
 try:
  if (proc.info['name'] or '').lower() in ('vivado.exe','vivado','xsim.exe'):raise RuntimeError('Another heavy EDA process active; no launch')
 except psutil.NoSuchProcess:pass
env=os.environ.copy();env.update(TEMP=str(B/'tmp'),TMP=str(B/'tmp'),OMP_NUM_THREADS='1',PROCESSOR_ARCHITECTURE='AMD64');(B/'tmp').mkdir(exist_ok=True)
for stage in ('migrate3','combine','synth','route'):
 if psutil.virtual_memory().available<2500*2**20:raise RuntimeError('Insufficient headroom before '+stage)
 cmd=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(B/'launch.ps1'),'-Stage',stage]
 log=P/'evidence'/(stage+'_console.log');start=time.monotonic();peak=0;minimum=psutil.virtual_memory().available;seen={};low_since=None;stop=None
 with log.open('w',encoding='utf-8') as out:
  out.write(json.dumps(cmd)+'\n');out.flush()
  child=subprocess.Popen(cmd,cwd=B,env=env,stdout=out,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
  process=psutil.Process(child.pid);seen[child.pid]=process.create_time()
  while child.poll() is None:
   try:
    for c in process.children(recursive=True):seen[c.pid]=c.create_time()
   except psutil.NoSuchProcess:pass
   rss=0
   for pid,created in list(seen.items()):
    try:
     c=psutil.Process(pid)
     if c.create_time()==created:rss+=c.memory_info().rss
    except (psutil.NoSuchProcess,psutil.AccessDenied):pass
   available=psutil.virtual_memory().available;minimum=min(minimum,available);peak=max(peak,rss);now=time.monotonic()
   if available<256*2**20:
    if low_since is None:low_since=now
   else:low_since=None
   if low_since is not None and now-low_since>15:stop='HOST_HEADROOM_BELOW256MiB_FOR15s'
   if rss>6500*2**20:stop='OWNED_RSS_OVER6500MiB'
   if now-start>2400:stop='STAGE_OVER40MIN'
   (P/'evidence/BUILD_STATUS.json').write_text(json.dumps(dict(stage=stage,seconds=now-start,owned_RSS_MiB=rss/2**20,available_MiB=available/2**20,stop=stop,child_pid=child.pid)))
   if stop:
    for pid,created in reversed(list(seen.items())):
     try:
      c=psutil.Process(pid)
      if c.create_time()==created:c.kill()
     except (psutil.NoSuchProcess,psutil.AccessDenied):pass
    break
   time.sleep(2)
  child.wait(timeout=15)
 row=dict(stage=stage,returncode=child.returncode,stop=stop,seconds=time.monotonic()-start,peak_owned_RSS_MiB=peak/2**20,minimum_host_available_MiB=minimum/2**20,command=cmd)
 stages.append(row);(P/'evidence/BUILD_RUN.json').write_text(json.dumps(stages,indent=2));print(json.dumps(row),flush=True)
 if child.returncode or stop:raise RuntimeError('Stage failed: '+stage+'; see '+str(log))
(P/'evidence/BUILD_STATUS.json').write_text(json.dumps(dict(stage='COMPLETE_REVIEW_PENDING',board_operations=0,bit_generated=False)))
print('All stages exited; routed reports still require review',flush=True)

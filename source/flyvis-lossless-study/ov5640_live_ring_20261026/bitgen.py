from pathlib import Path
import hashlib,json,os,psutil,shutil,subprocess,time
P=Path(__file__).resolve().parent
S=P.parent/'ddr_ring_soc_20261026/release'
B=Path('C:/fpga_work/line11_ring_release_20261026')
assert hashlib.sha256((S/'combined_routed.dcp').read_bytes()).hexdigest()=='b2fa0780d5278c4af8c508b45b60a5e4cb7b05c1d5f9482e8620f18ec25f026d'
if psutil.virtual_memory().available<2000*2**20:raise RuntimeError('Need2000MiB available before bitgen; no launch')
for proc in psutil.process_iter(['name']):
 if (proc.info['name'] or '').lower() in ('vivado.exe','xsim.exe'):raise RuntimeError('Other EDA running; no launch')
B.mkdir(exist_ok=False);(B/'tmp').mkdir()
shutil.copy2(S/'combined_routed.dcp',B/'source.dcp')
(B/'bitgen.tcl').write_text('set_param general.maxThreads 1\nopen_checkpoint source.dcp\nreport_drc -file bitgen_drc.rpt\nwrite_bitstream flyvis_official.bit\nclose_design\nexit\n')
(B/'launch.ps1').write_text("Set-Location -LiteralPath $PSScriptRoot\n& 'C:/AMDDesignTools/2026.1.1/Vivado/bin/vivado.bat' -mode batch -notrace -source bitgen.tcl -log bitgen.log -journal bitgen.jou\nexit $LASTEXITCODE\n")
env=os.environ.copy();env.update(TEMP=str(B/'tmp'),TMP=str(B/'tmp'),OMP_NUM_THREADS='1',PROCESSOR_ARCHITECTURE='AMD64')
cmd=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(B/'launch.ps1')]
start=time.monotonic();peak=0;minimum=psutil.virtual_memory().available;stop=None;seen={};low=None
with (P/'evidence/bitgen_console.log').open('w') as out:
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
  avail=psutil.virtual_memory().available;minimum=min(minimum,avail);peak=max(peak,rss)
  low=(low or time.monotonic()) if avail<256*2**20 else None
  if low is not None and time.monotonic()-low>15:stop='LOW_HOST_MEMORY'
  if rss>6000*2**20 or time.monotonic()-start>600:stop='BOUNDED_RESOURCE_STOP'
  (P/'evidence/BITGEN_STATUS.json').write_text(json.dumps(dict(seconds=time.monotonic()-start,available_MiB=avail/2**20,owned_RSS_MiB=rss/2**20,stop=stop)))
  if stop:
   for pid,created in reversed(list(seen.items())):
    try:
     c=psutil.Process(pid)
     if c.create_time()==created:c.kill()
    except (psutil.NoSuchProcess,psutil.AccessDenied):pass
   break
  time.sleep(2)
 child.wait(timeout=15)
r=dict(command=cmd,tool='Vivado2026.1.1',returncode=child.returncode,stop=stop,seconds=time.monotonic()-start,peak_owned_RSS_MiB=peak/2**20,minimum_available_MiB=minimum/2**20,board_operations=0)
(P/'evidence/BITGEN.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
if child.returncode or stop:raise RuntimeError('bitgen failed')
for name in ('bitgen.log','bitgen_drc.rpt'):shutil.copy2(B/name,P/'evidence'/name)
shutil.copy2(B/'flyvis_official.bit',P/'bundle/flyvis_official.bit')
shutil.copy2(S/'base.hwh',P/'bundle/flyvis_official.hwh')
print('BIT/HWH generated; package verification pending',flush=True)

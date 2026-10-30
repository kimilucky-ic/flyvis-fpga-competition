from pathlib import Path
from datetime import datetime,timezone,timedelta
import argparse,sys,json,hashlib,shutil,subprocess,time,csv
import psutil
P=Path(__file__).resolve().parent;B=P.parent;ROOT=B.parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(B/'fullscale_direct_20261012'));sys.path.insert(0,str(B/'physical_20261012'))
from windows_host import HostMemory
from gate_policy import collect_eda_snapshot,evaluate_gate,terminate_owned,isolation_reason

def now():return datetime.now(timezone(timedelta(hours=8))).isoformat()
def load(f):return json.loads(Path(f).read_text(encoding='utf-8-sig'))
def save(f,d):Path(f).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def gate(host,stage,allow_low_memory=False):
 s=host.sample();snapshot=collect_eda_snapshot();policy=evaluate_gate(s,snapshot,True,False,B)
 # Observed native PS7 full-scale simulation uses about5GiB; serialize all EDA.
 minimum=5376 if stage=='simulate' else 3072
 policy['reasons']=[reason for reason in policy['reasons'] if reason!='AVAILABLE_PHYSICAL_BELOW_3072_MIB']
 if s['available_MiB']<minimum:policy['reasons'].append('AVAILABLE_PHYSICAL_BELOW_'+str(minimum)+'_MIB')
 policy['capacity_allowed']=s['available_MiB']>=minimum and s['commit_headroom_MiB']>=4096
 policy['allowed']=not policy['reasons']
 # Current 16GB-host request: serialize B against every active EDA job.
 if snapshot['groups']:
  policy['reasons'].append('CURRENT_SOC_STAGE_REQUIRES_NO_OTHER_EDA')
  policy['allowed']=False
 waived=[]
 if allow_low_memory:
  waived=[r for r in policy['reasons'] if r.startswith('AVAILABLE_PHYSICAL_BELOW_') or r.startswith('COMMIT_HEADROOM_BELOW_')]
  policy['reasons']=[r for r in policy['reasons'] if r not in waived]
  policy['allowed']=not policy['reasons']
 return dict(at=now(),stage=stage,allow_low_memory=allow_low_memory,waived_startup_reasons=waived,minimum_available_MiB=minimum,host=s,active_eda=snapshot,**policy)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['unit','prepare','elaborate','diagnose','simulate','implement']);ap.add_argument('--standalone-xsim',action='store_true');ap.add_argument('--rebuild-snapshot',action='store_true');ap.add_argument('--allow-low-memory',action='store_true',help='Explicit user-authorized attempt despite startup capacity warning; runtime protections remain');args=ap.parse_args()
 if args.standalone_xsim and args.stage not in ('simulate','elaborate','diagnose'):ap.error('Standalone XSim is for simulation only')
 if args.rebuild_snapshot and not args.standalone_xsim:ap.error('Rebuild uses standalone XSim')
 host=HostMemory();g=gate(host,args.stage,args.allow_low_memory);(P/'resource_gates').mkdir(exist_ok=True);save(P/'resource_gates'/(args.stage+'_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.json'),g);save(P/'LATEST_GATE.json',g);print(json.dumps(g),flush=True)
 if not g['allowed']:host.close();return 2
 if args.stage in ('prepare','unit'):
  build=P/'work'/(args.stage+'_'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d_%H%M%S_%f'))
  for folder in ('source','rom','tmp','stages'):(build/folder).mkdir(parents=True,exist_ok=False)
  accepted=load(B/'pipeline_a_20261012/ACCEPTED.json')
  sources={}
  for name,digest in accepted['rtl_sha256'].items():
   src=B/'pipeline_a_20261012/rtl'/name;assert sha(src)==digest;shutil.copyfile(src,build/'source'/name);sources[name]=digest
  for f in (P/'rtl').glob('*.sv'):shutil.copyfile(f,build/'source'/f.name);sources[f.name]=sha(f)
  vendor=ROOT/'flyvis-fpga/phase4_67_20261010/artifacts/leader_ps7_user_params.tcl'
  shutil.copyfile(vendor,build/'source'/vendor.name)
  # Reuse frozen vectors; no graph extraction or integer oracle regeneration.
  vectors=B/'fullscale_20261012/vectors';prep=load(B/'fullscale_20261012/PREPARATION.json');rom={}
  for name in ('weights.mem','neurons.mem','requests.mem','edges.mem','expected.mem'):
   assert sha(vectors/name)==prep['files'][name]['sha256'];shutil.copyfile(vectors/name,build/'rom'/name);rom[name]=sha(vectors/name)
  ident=dict(at=now(),scope='B bulk DDR revision, source RAM head/tail split, ABI2, no board',part='xc7z020clg400-2',tool='2026.1.1 SW6605303',source_sha256=sources,rom_sha256=rom,vendor_ps_params_sha256=sha(vendor),accepted_sha256=sha(B/'pipeline_a_20261012/ACCEPTED.json'),H=5768,S=16402,E=433880,W=645,control_base='0x43C20000',FCLK0_MHz=100,AXI_TIMEOUT=65536,STEP_TIMEOUT=50000000)
  save(build/'INPUT_IDENTITY.json',ident);save(P/'LATEST_BUILD.json',dict(build=str(build.relative_to(P))))
 else:build=P/load(P/'LATEST_BUILD.json')['build']
 if args.stage=='implement':
  audit=load(build/'SYSTEM_AUDIT.json')
  assert audit['status']=='PASS_ACTUAL_PRODUCTION_BD_SYSTEM_FILE_AUDIT'
  for name,value in audit['source_sha256'].items():assert sha(build/'source'/name)==value
  for name,value in audit['generated_file_sha256'].items():assert sha(build/name)==value
  simdir=build/'project/b_soc.sim/sim_1/behav/xsim'
  for name,value in audit['evidence_sha256'].items():assert sha(simdir/name)==value
 existing=list((build/'stages').glob(args.stage+'_*'))
 if args.stage=='implement' and existing:host.close();raise RuntimeError('One full SoC implementation attempt; do not repeat automatically')
 if len(existing)>=16:host.close();raise RuntimeError('Bounded stage repair count exceeded')
 stage_dir=build/'stages'/(args.stage+'_'+str(len(existing)+1));stage_dir.mkdir()
 save(stage_dir/'INITIAL_GATE.json',g)
 g=gate(host,args.stage,args.allow_low_memory);save(stage_dir/'PRELAUNCH_GATE.json',g)
 if not g['allowed']:host.close();return 2
 budget={'unit':300,'prepare':900,'elaborate':900,'diagnose':600,'simulate':1800,'implement':2700}[args.stage]
 save(stage_dir/'IDENTITY.json',dict(at=now(),stage=args.stage,build=str(build),allow_low_memory=args.allow_low_memory,standalone_xsim=args.standalone_xsim,rebuild_snapshot=args.rebuild_snapshot,script_sha256=sha(P/'scripts/build_soc.tcl'),launcher_sha256=sha(P/'scripts/launch.ps1'),runner_sha256=sha(__file__),budget_seconds=budget,source_sha256={f.name:sha(f) for f in (build/'source').glob('*.sv')}))
 for source_file in (build/'source').glob('*.sv'):shutil.copyfile(source_file,stage_dir/source_file.name)
 shutil.copyfile(__file__,stage_dir/'run_soc.py')
 shutil.copyfile(P/'scripts/launch.ps1',stage_dir/'launch.ps1')
 shutil.copyfile(P/'scripts/build_soc.tcl',stage_dir/'build_soc.tcl')
 seen={};peak_rss=peak_private=0;min_free=g['host']['available_MiB'];min_commit=g['host']['commit_headroom_MiB'];low=paging=0;last=0;stop=None;actions=[];start=time.perf_counter()
 with (stage_dir/'console.log').open('w',encoding='utf-8') as log,(stage_dir/'resources.csv').open('w',newline='',encoding='utf-8') as csvfile:
  writer=csv.writer(csvfile);writer.writerow(['elapsed','free_MiB','commit_headroom_MiB','owned_processes','working_set_MiB','private_MiB','hard_pages_per_second'])
  command=['pwsh','-NoProfile','-File',str(P/'scripts/launch.ps1'),'-Build',str(build),'-Stage',args.stage,'-StageDir',str(stage_dir)]
  if args.standalone_xsim:command.append('-StandaloneXsim')
  if args.rebuild_snapshot:command.append('-RebuildSnapshot')
  proc=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  root=psutil.Process(proc.pid)
  while proc.poll() is None:
   elapsed=time.perf_counter()-start;rss=private=0
   try:owned=[root]+root.children(recursive=True)
   except psutil.NoSuchProcess:owned=[]
   for process in owned:
    try:
     key=(process.pid,process.create_time());mi=process.memory_info()
     seen.setdefault(key,dict(pid=key[0],created=key[1],name=process.name()));rss+=mi.rss;private+=getattr(mi,'private',mi.vms)
    except (psutil.NoSuchProcess,psutil.AccessDenied):pass
   try:
    s=host.sample();dt=elapsed-last;min_free=min(min_free,s['available_MiB']);min_commit=min(min_commit,s['commit_headroom_MiB'])
    low=low+dt if s['available_MiB']<256 else 0
    paging=paging+dt if s['available_MiB']<768 and s['pages_input_per_sec']>8192 else 0
    if s['commit_headroom_MiB']<1024:stop='LOW_COMMIT_HEADROOM'
    if low>=3:stop='PHYSICAL_BELOW_256_MIB'
    if paging>=5:stop='LOW_MEMORY_SUSTAINED_PAGING'
    if dt>30:stop='MONITOR_DELAY'
   except Exception as exc:stop='MONITOR_ERROR '+str(exc)
   last=elapsed;peak_rss=max(peak_rss,rss);peak_private=max(peak_private,private)
   writer.writerow([round(elapsed,3),s['available_MiB'],s['commit_headroom_MiB'],len(owned),round(rss/2**20,2),round(private/2**20,2),s['pages_input_per_sec']]);csvfile.flush()
   if elapsed>=budget:stop='BOUNDED_STAGE_TIMEOUT'
   if stop:actions=terminate_owned(owned,seen);break
   time.sleep(.5)
  try:code=proc.wait(timeout=10)
  except subprocess.TimeoutExpired:code=None
 host.close();result=dict(at=now(),stage=args.stage,exit_code=code,stop_reason=stop,wall_seconds=time.perf_counter()-start,peak_working_set_MiB=peak_rss/2**20,peak_private_MiB=peak_private/2**20,min_free_MiB=min_free,min_commit_MiB=min_commit,processes=list(seen.values()),termination_actions=actions)
 save(stage_dir/'RUNTIME.json',result);print(json.dumps(result),flush=True)
 if args.stage in ('simulate','elaborate','diagnose'):
  simdir=build/'project/b_soc.sim/sim_1/behav/xsim'
  for name in ('compile.log','elaborate.log','simulate.log','xsim.log','system_pass.txt','write_diagnostic.txt','system_candidates.csv','system_edges.csv','system_progress.log'):
   if (simdir/name).is_file():shutil.copyfile(simdir/name,stage_dir/name)
 return 0 if code==0 and stop is None else 1
if __name__=='__main__':raise SystemExit(main())

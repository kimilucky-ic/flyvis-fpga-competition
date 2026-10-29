from pathlib import Path
from datetime import datetime,timezone,timedelta
import argparse,csv,json,hashlib,sys,shutil,subprocess,time
import psutil
HERE=Path(__file__).resolve().parent;B=HERE.parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(B/'fullscale_direct_20261012'))
from windows_host import HostMemory
EDA={'vivado.exe','xsim.exe','xsimk.exe','xelab.exe','xvlog.exe','vitis_hls.exe','vitis-run.exe','v++.exe','rdi_synth.exe'}
def now():return datetime.now(timezone(timedelta(hours=8))).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def eda_processes():
    found=[]
    for p in psutil.process_iter(['pid','name']):
        try:
            if (p.info['name'] or '').lower() in EDA:found.append(p.info)
        except (psutil.NoSuchProcess,psutil.AccessDenied):pass
    return found
def main():
    ap=argparse.ArgumentParser();ap.add_argument('kind',choices=['directed','math','reader','fullpeak','fullstress','ooc']);args=ap.parse_args()
    host=HostMemory();sample=host.sample();conflicts=eda_processes()
    gate=dict(at=now(),host=sample,active_eda=conflicts,allowed=not conflicts and sample['commit_headroom_MiB']>=1536,scope=args.kind)
    print(json.dumps(gate),flush=True)
    if not gate['allowed']:host.close();return 2
    run=HERE/'build'/(args.kind+'_'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d_%H%M%S_%f'))
    run.mkdir(parents=True);(run/'rom').mkdir();(run/'tmp').mkdir()
    save(run/'RESOURCE_GATE.json',gate)
    for p in (HERE/'rtl').glob('*.sv'):shutil.copyfile(p,run/p.name)
    full=args.kind.startswith('full') or args.kind=='ooc'
    vectors=B/'fullscale_20261012/vectors' if full else HERE/'directed_vectors'
    if full:
        prep=load(B/'fullscale_20261012/PREPARATION.json')
        for name,v in prep['files'].items():assert sha(vectors/name)==v['sha256'],name
        shutil.copyfile(B/'fullscale_20261012/PREPARATION.json',run/'PREPARATION.json')
    for p in vectors.glob('*.mem'):shutil.copyfile(p,run/'rom'/p.name)
    for p in vectors.glob('*.svh'):shutil.copyfile(p,run/p.name)
    tb='tb_pipeline_full' if args.kind.startswith('full') else 'tb_'+args.kind
    if args.kind=='ooc':
        accepted=load(HERE/'ACCEPTED.json')
        for name,digest in accepted['rtl_sha256'].items():assert sha(run/name)==digest,name
        for name in ('synth_pipeline.tcl','clock.xdc'):shutil.copyfile(HERE/name,run/name)
    else:shutil.copyfile(HERE/(tb+'.sv'),run/(tb+'.sv'))
    ident=dict(at=now(),kind=args.kind,tb_top=tb,tool='2026.1.1 SW6605303',part='xc7z020clg400-2',
        source_sha256={p.name:sha(p) for p in run.glob('*.sv')},rom_sha256={p.name:sha(p) for p in (run/'rom').glob('*.mem')},
        runner_sha256=sha(__file__),launcher_sha256=sha(HERE/'launch.ps1'),wall_budget_seconds=900,
        generics=dict(H_COUNT=5768,SOURCE_COUNT=16402,EDGE_COUNT=433880,WEIGHT_COUNT=645,FIFO_DEPTH=128,AXI_TIMEOUT=64,STEP_TIMEOUT=8000000,reader_outstanding=4) if full else {},
        scope='User-selected A pipeline; isolated revision; no board or SoC')
    if args.kind=='ooc':ident.update(accepted_sha256=sha(HERE/'ACCEPTED.json'),tcl_sha256=sha(run/'synth_pipeline.tcl'),xdc_sha256=sha(run/'clock.xdc'))
    save(run/'RUN_IDENTITY.json',ident);save(HERE/('LATEST_'+args.kind+'.json'),dict(run=str(run.relative_to(HERE))))
    if eda_processes():raise RuntimeError('EDA appeared during copy; no launch')
    start=time.perf_counter();seen={};peak_rss=peak_private=0;min_free=sample['available_MiB'];min_commit=sample['commit_headroom_MiB']
    peak_pages=0;low_seconds=paging_seconds=0;last=0;stop=None
    with (run/'console.log').open('w',encoding='utf-8') as log,(run/'host_resources.csv').open('w',newline='',encoding='utf-8') as rf:
        writer=csv.writer(rf);writer.writerow(['elapsed_seconds','available_MiB','commit_headroom_MiB','owned_processes','sum_working_set_MiB','sum_private_MiB','pages_input_per_sec','page_reads_per_sec'])
        proc=subprocess.Popen(['pwsh','-NoProfile','-File',str(HERE/'launch.ps1'),'-RunDir',str(run)],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        root=psutil.Process(proc.pid)
        while proc.poll() is None:
            elapsed=time.perf_counter()-start;rss=private=0
            try:owned=[root]+root.children(recursive=True)
            except psutil.NoSuchProcess:owned=[]
            for p in owned:
                try:
                    key=(p.pid,p.create_time());mi=p.memory_info();ct=p.cpu_times()
                    rec=seen.setdefault(key,dict(pid=p.pid,created=key[1],name=p.name(),peak_working_set_bytes=0,peak_private_bytes=0,cpu_seconds=0))
                    rec['peak_working_set_bytes']=max(rec['peak_working_set_bytes'],mi.rss,getattr(mi,'peak_wset',0));rec['peak_private_bytes']=max(rec['peak_private_bytes'],getattr(mi,'private',mi.vms));rec['cpu_seconds']=max(rec['cpu_seconds'],ct.user+ct.system)
                    rss+=mi.rss;private+=getattr(mi,'private',mi.vms)
                except (psutil.NoSuchProcess,psutil.AccessDenied):pass
            try:
                sample=host.sample();dt=elapsed-last
                min_free=min(min_free,sample['available_MiB']);min_commit=min(min_commit,sample['commit_headroom_MiB']);peak_pages=max(peak_pages,sample['pages_input_per_sec'])
                low_seconds=low_seconds+dt if sample['available_MiB']<256 else 0
                paging_seconds=paging_seconds+dt if sample['available_MiB']<768 and sample['pages_input_per_sec']>8192 else 0
                if sample['commit_headroom_MiB']<1024:stop='COMMIT_HEADROOM_BELOW_1024_MIB'
                if low_seconds>=3:stop='PHYSICAL_BELOW_256_MIB_FOR_3_SECONDS'
                if paging_seconds>=5:stop='SUSTAINED_LOW_MEMORY_HARD_PAGING'
                if dt>30:stop='MONITOR_DELAY_ABOVE_30_SECONDS'
            except Exception as exc:stop='MONITOR_FAILED: '+str(exc)
            last=elapsed;peak_rss=max(peak_rss,rss);peak_private=max(peak_private,private)
            writer.writerow([round(elapsed,3),sample['available_MiB'],sample['commit_headroom_MiB'],len(owned),round(rss/2**20,2),round(private/2**20,2),sample['pages_input_per_sec'],sample['page_reads_per_sec']]);rf.flush()
            if elapsed>=900:stop='WALL_BUDGET_900_SECONDS'
            if stop:
                for p in reversed(owned):
                    try:
                        if (p.pid,p.create_time()) in seen:p.terminate()
                    except (psutil.NoSuchProcess,psutil.AccessDenied):pass
                break
            time.sleep(.5)
        try:code=proc.wait(timeout=10)
        except subprocess.TimeoutExpired:code=None
    host.close()
    runtime=dict(at=now(),exit_code=code,stop_reason=stop,wall_seconds=time.perf_counter()-start,
        peak_sampled_sum_working_set_MiB=round(peak_rss/2**20,2),peak_sampled_sum_private_MiB=round(peak_private/2**20,2),
        min_available_physical_MiB=round(min_free,2),min_commit_headroom_MiB=round(min_commit,2),max_pages_input_per_sec=peak_pages,
        processes=list(seen.values()),sample_interval_seconds=.5,scope='Owned process tree; sample sums may double-count shared pages and miss short-lived children; host RAM not PL utilization')
    save(run/'RUNTIME.json',runtime)
    print(json.dumps(dict(run=str(run),runtime=runtime)),flush=True)
    return 0 if code==0 and stop is None else 1
if __name__=='__main__':raise SystemExit(main())

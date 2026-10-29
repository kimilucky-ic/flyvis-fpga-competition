"""Fresh exclusive EDA/resource gate, then at most ONE full-scale XSim run.

Default is gate-only. --run requires a current release record saved from A's
completed turn, >=4GiB available RAM, <=50% CPU and no EDA process. Monitoring
records this launch's descendants; only those owned processes are stopped if
the fixed 600-second wall budget expires. Never closes other applications.
"""
from pathlib import Path
import argparse,csv,hashlib,json,shutil,subprocess,time,sys
from datetime import datetime,timezone,timedelta
import psutil

HERE=Path(__file__).resolve().parent;B=HERE.parent;ROOT=B.parents[1]
EDA={'vivado.exe','xsim.exe','xelab.exe','xvlog.exe','vitis_hls.exe','vitis-run.exe','v++.exe'}
def now():return datetime.now(timezone(timedelta(hours=8))).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def processes():
    found=[]
    for p in psutil.process_iter(['pid','name']):
        try:
            if (p.info['name'] or '').lower() in EDA:found.append(p.info)
        except (psutil.NoSuchProcess,psutil.AccessDenied):pass
    return found
def gate():
    release_path=HERE/'A_EDA_RELEASE.json'
    release=json.loads(release_path.read_text(encoding='utf-8')) if release_path.exists() else {}
    release_ok=(release.get('thread_status')=='idle' and release.get('turn_status')=='completed'
        and release.get('no_eda_capacity_held') is True and release.get('observed_local_date')=='2026-10-12')
    if release_ok:
        doc=ROOT/release['source_document'];release_ok=doc.is_file() and sha(doc)==release['source_document_sha256']
    cpu=psutil.cpu_percent(interval=1.0);memory=psutil.virtual_memory();eda=processes()
    free=memory.available/2**20
    reasons=[]
    if not release_ok:reasons.append('A_RELEASE_NOT_CONFIRMED_OR_CHANGED')
    if free<4096:reasons.append('AVAILABLE_PHYSICAL_MEMORY_BELOW_4096_MIB')
    if cpu>50:reasons.append('CPU_ABOVE_50_PERCENT')
    if eda:reasons.append('EDA_PROCESS_ACTIVE')
    d=dict(checked_at=now(),available_physical_MiB=round(free,2),total_physical_MiB=round(memory.total/2**20,2),
        cpu_percent=cpu,active_eda=eda,A_release_confirmed=release_ok,minimum_free_MiB=4096,maximum_cpu_percent=50,
        shortfall_MiB=round(max(0,4096-free),2),allowed=not reasons,reasons=reasons,scope='ONE_FULL_433880_EDGE_RTL_SIM_NO_SYNTH',
        release_record_sha256=sha(release_path) if release_path.exists() else None)
    dest=HERE/'resource_gates';dest.mkdir(exist_ok=True)
    path=dest/(datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d_%H%M%S_%f')+'.json')
    save(path,d);save(HERE/'LATEST_RESOURCE_GATE.json',dict(path=str(path.relative_to(HERE)),**d))
    print(json.dumps(d,ensure_ascii=False),flush=True);return path,d
def verify_prepared():
    prep=json.loads((HERE/'PREPARATION.json').read_text(encoding='utf-8'))
    assert prep['status']=='PASS_FULLSCALE_CPU_PREPARATION'
    for name,v in prep['files'].items():
        p=HERE/'vectors'/name;assert sha(p)==v['sha256'] and p.stat().st_size==v['bytes']
    for name,v in prep['source_files'].items():assert sha(ROOT/name)==v['sha256']
    for name,v in prep['protected_parent_rtl_sha256'].items():assert sha(B/'rtl'/name)==v
    assert sha(B/'MANIFEST_SHA256.json')==prep['parent_delivery_manifest_sha256']
    return prep
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');args=ap.parse_args()
    prep=verify_prepared();gate_path,g=gate()
    if not args.run:return 0
    if not g['allowed']:return 2
    # A new gate is required for every attempted launch; a prior run consumes
    # today's single-full-request allowance, even if that run fails.
    ledger=HERE/'LAUNCH_RECORD.json'
    if ledger.exists():raise RuntimeError('One full-scale launch was already recorded; no automatic retry')
    run=HERE/'build'/datetime.now(timezone(timedelta(hours=8))).strftime('full_%Y%m%d_%H%M%S_%f')
    run.mkdir(parents=True);(run/'rom').mkdir();(run/'tmp').mkdir()
    for name in prep['protected_parent_rtl_sha256']:shutil.copyfile(B/'rtl'/name,run/name)
    shutil.copyfile(HERE/'tb_fullscale.sv',run/'tb_fullscale.sv')
    for p in (HERE/'vectors').glob('*.mem'):shutil.copyfile(p,run/'rom'/p.name)
    shutil.copyfile(HERE/'vectors/full_config.svh',run/'full_config.svh')
    shutil.copyfile(HERE/'PREPARATION.json',run/'PREPARATION.json')
    ident=dict(at=now(),intended_device='xc7z020clg400-2',tool='XSim 2026.1.1',request_count=1,
        preparation_sha256=sha(HERE/'PREPARATION.json'),gate_path=str(gate_path.relative_to(HERE)),gate_sha256=sha(gate_path),
        A_release_sha256=g['release_record_sha256'],wall_budget_seconds=600,
        sources={p.name:sha(p) for p in run.glob('*.sv')},config_sha256=sha(run/'full_config.svh'),
        runner_sha256=sha(__file__),launcher_sha256=sha(HERE/'launch_xsim.ps1'),
        auditor_sha256=sha(HERE/'audit_fullscale.py'))
    save(run/'RUN_IDENTITY.json',ident)
    # No EDA process may have appeared during the short identity/copy phase.
    if processes():raise RuntimeError('EDA started during preparation; no launch')
    with ledger.open('x',encoding='utf-8') as f:json.dump(dict(run=str(run.relative_to(HERE)),started_at=now()),f,indent=2)
    start=time.perf_counter();seen={};peak_sum_rss=peak_sum_private=0;min_available=psutil.virtual_memory().available
    timed_out=False
    with (run/'console.log').open('w',encoding='utf-8') as log,(run/'host_resources.csv').open('w',newline='',encoding='utf-8') as rf:
        writer=csv.writer(rf);writer.writerow(['elapsed_seconds','available_MiB','owned_processes','sum_working_set_MiB','sum_private_MiB'])
        proc=subprocess.Popen(['pwsh','-NoProfile','-File',str(HERE/'launch_xsim.ps1'),'-RunDir',str(run)],
            stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        root=psutil.Process(proc.pid)
        while proc.poll() is None:
            elapsed=time.perf_counter()-start;rss=private=0
            try:owned=[root]+root.children(recursive=True)
            except psutil.NoSuchProcess:owned=[]
            for p in owned:
                try:
                    key=(p.pid,p.create_time());mi=p.memory_info();ct=p.cpu_times()
                    record=seen.setdefault(key,dict(pid=p.pid,created=key[1],name=p.name(),peak_working_set_bytes=0,peak_private_bytes=0,cpu_seconds=0))
                    record['peak_working_set_bytes']=max(record['peak_working_set_bytes'],mi.rss,getattr(mi,'peak_wset',0))
                    record['peak_private_bytes']=max(record['peak_private_bytes'],getattr(mi,'private',mi.vms))
                    record['cpu_seconds']=max(record['cpu_seconds'],ct.user+ct.system)
                    rss+=mi.rss;private+=getattr(mi,'private',mi.vms)
                except (psutil.NoSuchProcess,psutil.AccessDenied):pass
            available=psutil.virtual_memory().available;min_available=min(min_available,available)
            peak_sum_rss=max(peak_sum_rss,rss);peak_sum_private=max(peak_sum_private,private)
            writer.writerow([round(elapsed,3),round(available/2**20,2),len(owned),round(rss/2**20,2),round(private/2**20,2)]);rf.flush()
            if elapsed>=600:
                timed_out=True
                # Only this launch's current descendants, identity rechecked.
                for p in reversed(owned):
                    try:
                        if (p.pid,p.create_time()) in seen:p.terminate()
                    except (psutil.NoSuchProcess,psutil.AccessDenied):pass
                break
            time.sleep(.5)
        try:code=proc.wait(timeout=10)
        except subprocess.TimeoutExpired:code=None
    runtime=dict(ended_at=now(),exit_code=code,wall_seconds=time.perf_counter()-start,wall_timeout=timed_out,
        min_available_physical_MiB=round(min_available/2**20,2),peak_sampled_sum_working_set_MiB=round(peak_sum_rss/2**20,2),
        peak_sampled_sum_private_MiB=round(peak_sum_private/2**20,2),processes=list(seen.values()),sample_interval_seconds=.5,
        limitation='Sampled sums can double-count shared pages and miss short-lived children; not PL utilization',
        resource_type='HOST_PROCESS_MEASUREMENTS_NOT_FPGA_SYNTHESIS')
    save(run/'RUNTIME.json',runtime);print(json.dumps(dict(run=str(run),runtime=runtime)),flush=True)
    if code!=0 or timed_out:return 1
    return subprocess.call([sys.executable,str(HERE/'audit_fullscale.py'),'--run',str(run)])
if __name__=='__main__':raise SystemExit(main())

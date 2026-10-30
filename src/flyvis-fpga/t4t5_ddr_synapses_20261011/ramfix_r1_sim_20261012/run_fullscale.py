"""Fresh exclusive EDA/resource gate, then at most ONE full-scale XSim run.

User explicitly ordered direct launch; prelaunch RAM/commit/CPU thresholds
are telemetry only. Preserve one-EDA exclusion, one-full-run ledger, integer
checks and existing runtime watchdogs. No synthesis or board operations.
"""
from pathlib import Path
import argparse,csv,hashlib,json,shutil,subprocess,time,sys
from datetime import datetime,timezone,timedelta
import psutil
from windows_host import HostMemory,pressure_reason

HERE=Path(__file__).resolve().parent;B=HERE.parent;ROOT=B.parents[1]
PREP=B/"fullscale_20261012"
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
def gate(host):
    release_path=HERE/'A_EDA_RELEASE.json'
    release=json.loads(release_path.read_text(encoding='utf-8')) if release_path.exists() else {}
    release_ok=((release.get('thread_status')=='idle' and release.get('turn_status')=='completed'
        or release.get('release_basis')=='DIRECT_USER_RELEASE_THIS_TURN')
        and release.get('no_eda_capacity_held') is True and release.get('observed_local_date')=='2026-10-12')
    if release_ok:
        doc=ROOT/release['source_document'];release_ok=doc.is_file() and sha(doc)==release['source_document_sha256']
    cpu=psutil.cpu_percent(interval=1.0);memory=host.sample();eda=processes()
    free=memory['available_MiB']
    reasons=[]
    if not release_ok:reasons.append('A_RELEASE_NOT_CONFIRMED_OR_CHANGED')
    # Direct user instruction overrides the previous prelaunch resource thresholds.



    if eda:reasons.append('EDA_PROCESS_ACTIVE')
    d=dict(checked_at=now(),available_physical_MiB=round(free,2),total_physical_MiB=round(memory['total_MiB'],2),
        commit_headroom_MiB=round(memory['commit_headroom_MiB'],2),host_counters=memory,
        cpu_percent=cpu,active_eda=eda,A_release_confirmed=release_ok,minimum_free_MiB=None,minimum_commit_headroom_MiB=None,maximum_cpu_percent=None,
        below_original_4096_policy=free<4096,policy='USER_DIRECT_LAUNCH_RESOURCE_THRESHOLDS_OVERRIDDEN',user_override=True,
        shortfall_MiB=None,allowed=not reasons,reasons=reasons,scope='ONE_FULL_433880_EDGE_RTL_SIM_NO_SYNTH',
        release_record_sha256=sha(release_path) if release_path.exists() else None)
    dest=HERE/'resource_gates';dest.mkdir(exist_ok=True)
    path=dest/(datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d_%H%M%S_%f')+'.json')
    save(path,d);save(HERE/'LATEST_RESOURCE_GATE.json',dict(path=str(path.relative_to(HERE)),**d))
    print(json.dumps(d,ensure_ascii=False),flush=True);return path,d
def verify_prepared():
    prep=json.loads((PREP/'PREPARATION.json').read_text(encoding='utf-8'))
    assert prep['status']=='PASS_FULLSCALE_CPU_PREPARATION'
    for name,v in prep['files'].items():
        p=PREP/'vectors'/name;assert sha(p)==v['sha256'] and p.stat().st_size==v['bytes']
    for name,v in prep['source_files'].items():assert sha(ROOT/name)==v['sha256']
    for name,v in prep['protected_parent_rtl_sha256'].items():assert sha(B/'rtl'/name)==v
    assert sha(B/'MANIFEST_SHA256.json')==prep['parent_delivery_manifest_sha256']
    revision=json.loads((HERE/'REVISION.json').read_text(encoding='utf-8'))
    for name,digest in revision['rtl_sha256'].items():assert sha(HERE/'rtl'/name)==digest
    return prep
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');args=ap.parse_args()
    prep=verify_prepared();host=HostMemory();gate_path,g=gate(host)
    if not args.run:host.close();return 0
    if not g['allowed']:host.close();return 2
    # A new gate is required for every attempted launch; a prior run consumes
    # today's single-full-request allowance, even if that run fails.
    ledger=HERE/'REVISION_LAUNCH.json'
    if ledger.exists():
        raise RuntimeError('One full-scale launch was already recorded; no automatic retry')
    run=HERE/'build'/datetime.now(timezone(timedelta(hours=8))).strftime('full_%Y%m%d_%H%M%S_%f')
    run.mkdir(parents=True);(run/'rom').mkdir();(run/'tmp').mkdir()
    for name in prep['protected_parent_rtl_sha256']:shutil.copyfile(HERE/'rtl'/name,run/name)
    shutil.copyfile(HERE/'tb_fullscale.sv',run/'tb_fullscale.sv')
    for p in (PREP/'vectors').glob('*.mem'):shutil.copyfile(p,run/'rom'/p.name)
    shutil.copyfile(PREP/'vectors/full_config.svh',run/'full_config.svh')
    shutil.copyfile(PREP/'PREPARATION.json',run/'PREPARATION.json')
    ident=dict(revision_sha256=sha(HERE/'REVISION.json'),at=now(),intended_device='xc7z020clg400-2',tool='XSim 2026.1.1',request_count=1,
        preparation_sha256=sha(PREP/'PREPARATION.json'),gate_path=str(gate_path.relative_to(HERE)),gate_sha256=sha(gate_path),
        A_release_sha256=g['release_record_sha256'],wall_budget_seconds=600,
        sources={p.name:sha(p) for p in run.glob('*.sv')},config_sha256=sha(run/'full_config.svh'),
        runner_sha256=sha(__file__),launcher_sha256=sha(HERE/'launch_xsim.ps1'),
        auditor_sha256=sha(HERE/'audit_fullscale.py'),monitor_sha256=sha(HERE/'windows_host.py'),
        static_review_sha256=sha(HERE/'STATIC_REVIEW.json'),upper_cycle_budget_with_fifo_margin=7860104,
        direct_launch_authorization_sha256=sha(HERE/'DIRECT_LAUNCH_AUTHORIZATION.json'))
    save(run/'RUN_IDENTITY.json',ident)
    # No EDA process may have appeared during the short identity/copy phase.
    if processes():raise RuntimeError('EDA started during preparation; no launch')
    launch=dict(run=str(run.relative_to(B)),started_at=now(),allowed_launches=1)
    with ledger.open('x',encoding='utf-8') as f:json.dump(launch,f,indent=2)
    save(HERE/'LAUNCH_RECORD.json',launch)
    start=time.perf_counter();seen={};peak_sum_rss=peak_sum_private=0;min_available=psutil.virtual_memory().available
    timed_out=False;stop_reason=None;paging_seconds=0;last_sample=0;min_commit=g['commit_headroom_MiB'];max_pages_input=0
    with (run/'console.log').open('w',encoding='utf-8') as log,(run/'host_resources.csv').open('w',newline='',encoding='utf-8') as rf:
        writer=csv.writer(rf);writer.writerow(['elapsed_seconds','available_MiB','owned_processes','sum_working_set_MiB','sum_private_MiB',
            'commit_headroom_MiB','pages_input_per_sec','page_reads_per_sec'])
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
            try:
                sample=host.sample();available=sample['available_MiB']*2**20
                min_available=min(min_available,available);min_commit=min(min_commit,sample['commit_headroom_MiB'])
                max_pages_input=max(max_pages_input,sample['pages_input_per_sec'])
                paging_seconds=(paging_seconds+elapsed-last_sample) if sample['available_MiB']<2048 and sample['pages_input_per_sec']>4096 else 0
                stop_reason=pressure_reason(sample,elapsed,paging_seconds)
                if elapsed-last_sample>15:stop_reason='HOST_MONITOR_DELAY_ABOVE_15_SECONDS'
            except Exception as exc:
                sample={k:None for k in ('commit_headroom_MiB','pages_input_per_sec','page_reads_per_sec')}
                available=psutil.virtual_memory().available;stop_reason='MONITOR_FAILED: '+str(exc)
            last_sample=elapsed
            peak_sum_rss=max(peak_sum_rss,rss);peak_sum_private=max(peak_sum_private,private)
            writer.writerow([round(elapsed,3),round(available/2**20,2),len(owned),round(rss/2**20,2),round(private/2**20,2),
                sample['commit_headroom_MiB'],sample['pages_input_per_sec'],sample['page_reads_per_sec']]);rf.flush()
            if stop_reason:
                timed_out=elapsed>=600
                # Only this launch's current descendants, identity rechecked.
                for p in reversed(owned):
                    try:
                        if (p.pid,p.create_time()) in seen:p.terminate()
                    except (psutil.NoSuchProcess,psutil.AccessDenied):pass
                break
            time.sleep(.5)
        try:code=proc.wait(timeout=10)
        except subprocess.TimeoutExpired:code=None
    host.close()
    runtime=dict(ended_at=now(),exit_code=code,wall_seconds=time.perf_counter()-start,wall_timeout=timed_out,
        stop_reason=stop_reason,min_commit_headroom_MiB=round(min_commit,2),max_pages_input_per_sec=max_pages_input,
        min_available_physical_MiB=round(min_available/2**20,2),peak_sampled_sum_working_set_MiB=round(peak_sum_rss/2**20,2),
        peak_sampled_sum_private_MiB=round(peak_sum_private/2**20,2),processes=list(seen.values()),sample_interval_seconds=.5,
        limitation='Sampled sums can double-count shared pages and miss short-lived children; not PL utilization',
        resource_type='HOST_PROCESS_MEASUREMENTS_NOT_FPGA_SYNTHESIS')
    save(run/'RUNTIME.json',runtime);print(json.dumps(dict(run=str(run),runtime=runtime)),flush=True)
    if code!=0 or timed_out or stop_reason:return 1
    return subprocess.call([sys.executable,str(HERE/'audit_fullscale.py'),'--run',str(run)])
if __name__=='__main__':raise SystemExit(main())

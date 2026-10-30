from pathlib import Path
from datetime import datetime,timezone,timedelta
import argparse,json,hashlib,sys,shutil,subprocess,time,csv
import psutil
from gate_policy import collect_eda_snapshot,evaluate_gate,terminate_owned
P=Path(__file__).resolve().parent;HERE=P;B=P.parent;ROOT=B.parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(B/'fullscale_direct_20261012'))
from windows_host import HostMemory
def now():return datetime.now(timezone(timedelta(hours=8))).isoformat()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def resource_gate(host,allow_concurrent,release,fresh,phase):
    sample=host.sample();snapshot=collect_eda_snapshot()
    policy=evaluate_gate(sample,snapshot,allow_concurrent,fresh,B)
    return dict(at=now(),phase=phase,host=sample,active_eda=snapshot,A_release=release,
        A_release_fresh=fresh,**policy,
        scope='One physical attempt; optional one isolated concurrent Vivado job; 3GiB free/4GiB commit are run policy, not vendor limits')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true')
    ap.add_argument('--allow-concurrent-vivado',action='store_true',help='Explicitly authorized override: one other isolated Vivado job; no A-thread release gate')
    args=ap.parse_args()
    host=HostMemory()
    release_path=P/'A_CURRENT_RELEASE.json';release=load(release_path) if release_path.exists() else {}
    fresh=False
    if release and not args.allow_concurrent_vivado:
        age=datetime.now(timezone.utc).timestamp()-release['observed_unix']
        fresh=0<=age<=300 and release['current_task_startedAt']>=1791800713 and release['current_turn_completed'] and release['thread_idle'] and release['milestone_release_confirmed']
    gate=resource_gate(host,args.allow_concurrent_vivado,release,fresh,'INITIAL')
    save(P/'LATEST_RESOURCE_GATE.json',gate);print(json.dumps(gate),flush=True)
    if not args.run or not gate['allowed']:host.close();return 0 if not args.run else 2
    if (P/'LAUNCH_RECORD.json').exists():host.close();raise RuntimeError('Single physical attempt already consumed; no automatic retry')
    identity=load(P/'INPUT_IDENTITY.json');static=load(P/'STATIC_REVIEW.json')
    assert sha(P/'INPUT_IDENTITY.json')==static['input_identity_sha256']
    for name,digest in static['prepared_files_sha256'].items():assert sha(P/name)==digest,name
    for name,digest in static['helper_sha256'].items():assert sha(P/name)==digest,name
    assert sha(P/'CONCURRENCY_AUTHORIZATION.json')==static['concurrency_authorization_sha256']
    assert sha(ROOT/identity['dcp_path'])==identity['dcp_sha256']
    assert sha(ROOT/identity['accepted_path']/'ACCEPTED.json')==identity['accepted_sha256']
    assert sha(ROOT/identity['accepted_path']/'OOC_RESULT.json')==identity['ooc_result_sha256']
    run=P/'build'/('route_'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d_%H%M%S_%f'))
    run.mkdir(parents=True);(run/'tmp').mkdir()
    for name in ('context.xdc','implement.tcl'):shutil.copyfile(P/name,run/name)
    shutil.copyfile(ROOT/identity['dcp_path'],run/'input_synthesis.dcp')
    save(run/'RESOURCE_GATE.json',gate)
    ident=dict(at=now(),stage='ONE_OOC_PHYSICAL_ATTEMPT',input_identity=identity,input_identity_sha256=sha(P/'INPUT_IDENTITY.json'),
        static_sha256=sha(P/'STATIC_REVIEW.json'),context_sha256=sha(run/'context.xdc'),tcl_sha256=sha(run/'implement.tcl'),
        launcher_sha256=sha(P/'launch.ps1'),runner_sha256=sha(__file__),wall_budget_seconds=1200,
        command=[sys.executable,str(P/'run.py'),'--run']+(['--allow-concurrent-vivado'] if args.allow_concurrent_vivado else []),
        concurrency_authorization_sha256=sha(P/'CONCURRENCY_AUTHORIZATION.json'),
        gate_policy_sha256=sha(P/'gate_policy.py'),allow_concurrent_vivado=args.allow_concurrent_vivado)
    save(run/'RUN_IDENTITY.json',ident)
    prelaunch=resource_gate(host,args.allow_concurrent_vivado,release,fresh,'AFTER_DCP_COPY_BEFORE_LAUNCH')
    save(run/'PRELAUNCH_RESOURCE_GATE.json',prelaunch);save(P/'LATEST_RESOURCE_GATE.json',prelaunch)
    if not prelaunch['allowed']:
        host.close();print(json.dumps(dict(status='NOT_LAUNCHED_PRELAUNCH_GATE',gate=prelaunch)),flush=True);return 2
    sample=prelaunch['host']
    save(P/'LAUNCH_RECORD.json',dict(at=now(),run=str(run.relative_to(P)),vendor_invocations=1))
    start=time.perf_counter();seen={};peak_rss=peak_private=0;min_free=sample['available_MiB'];min_commit=sample['commit_headroom_MiB']
    peak_pages=0;low_seconds=paging_seconds=0;last=0;stop=None;termination_actions=[]
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
            if elapsed>=1200:stop='WALL_BUDGET_1200_SECONDS'
            if stop:
                termination_actions=terminate_owned(owned,seen)
                break
            time.sleep(.5)
        try:code=proc.wait(timeout=10)
        except subprocess.TimeoutExpired:code=None
    host.close()
    runtime=dict(at=now(),exit_code=code,stop_reason=stop,wall_seconds=time.perf_counter()-start,
        peak_sampled_sum_working_set_MiB=round(peak_rss/2**20,2),peak_sampled_sum_private_MiB=round(peak_private/2**20,2),
        min_available_physical_MiB=round(min_free,2),min_commit_headroom_MiB=round(min_commit,2),max_pages_input_per_sec=peak_pages,
        processes=list(seen.values()),sample_interval_seconds=.5,scope='Owned process tree; sample sums may double-count shared pages and miss short-lived children; host RAM not PL utilization')
    runtime['termination_actions']=termination_actions
    save(run/'RUNTIME.json',runtime)
    print(json.dumps(dict(run=str(run),runtime=runtime)),flush=True)
    return 0 if code==0 and stop is None else 1
if __name__=='__main__':raise SystemExit(main())

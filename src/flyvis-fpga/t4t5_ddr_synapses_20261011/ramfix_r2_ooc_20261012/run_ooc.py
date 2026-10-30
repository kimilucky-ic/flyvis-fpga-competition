"""One isolated synthesis launch; reuse accepted RTL/ROM without replay.

The old 2.5/4GiB free-RAM policy is not a vendor requirement or launch gate.
Record current physical/commit/paging and reject an EDA conflict or concrete
low-commit/severe-pressure condition. Bound and monitor only this process tree.
"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,sys,shutil,subprocess,time,ast
import psutil
HERE=Path(__file__).resolve().parent;B=HERE.parent
ACCEPTED=B/'ramfix_r2_sim_20261012'
sys.dont_write_bytecode=True
sys.path.insert(0,str(ACCEPTED))
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
def verify():
    manifest=load(ACCEPTED/'MANIFEST_SHA256.json');accepted=load(ACCEPTED/'FULL_RTL_RESULT.json')
    assert sha(ACCEPTED/'MANIFEST_SHA256.json')==load(ACCEPTED/'DELIVERY_VERIFICATION.json')['manifest_sha256']
    assert sha(ACCEPTED/'FULL_RTL_RESULT.json')==manifest['files']['FULL_RTL_RESULT.json']['sha256']
    assert accepted['status']=='PASS_FULLSCALE_RTL_ONE_REQUEST' and accepted['exact_integer_mismatches']==0
    sim=ACCEPTED/accepted['run'];identity=load(sim/'RUN_IDENTITY.json')
    assert sha(sim/'RUN_IDENTITY.json')==accepted['raw_files']['RUN_IDENTITY.json']['sha256']
    prep=load(sim/'PREPARATION.json');assert sha(sim/'PREPARATION.json')==identity['preparation_sha256']
    c=prep['contract'];assert (c['H'],c['source_count'],c['edge_count'],c['weight_count'],c['step_timeout_cycles'],c['axi_timeout_cycles'])==(5768,16402,433880,645,8000000,64)
    bound={}
    for name in ('axi_edge_reader.sv','edge_fifo.sv','ddr_synapse_core.sv','ddr_synapse_top.sv'):
        assert sha(ACCEPTED/'rtl'/name)==sha(sim/name)==identity['sources'][name]
        bound[name]=sha(sim/name)
    for name in ('weights.mem','neurons.mem'):
        assert sha(sim/'rom'/name)==prep['files'][name]['sha256']
        bound['rom/'+name]=sha(sim/'rom'/name)
    assert sha(sim/'full_config.svh')==identity['config_sha256']
    return sim,accepted,c,bound
def main():
    sim,accepted,contract,bound=verify()
    if (HERE/'LAUNCH_RECORD.json').exists():raise RuntimeError('A synthesis launch is already recorded; no automatic resynthesis')
    host=HostMemory();cpu=psutil.cpu_percent(interval=1);sample=host.sample();conflicts=eda_processes();reasons=[]
    if conflicts:reasons.append('CONCURRENT_EDA')
    if sample['commit_headroom_MiB']<1536:reasons.append('LESS_THAN_1536_MIB_SYSTEM_COMMIT_HEADROOM')
    if sample['available_MiB']<512 and sample['pages_input_per_sec']>8192:reasons.append('LOW_PHYSICAL_MEMORY_WITH_HIGH_HARD_PAGE_INPUT')
    gate=dict(at=now(),cpu_percent=cpu,host=sample,active_eda=conflicts,allowed=not reasons,reasons=reasons,
        old_free_ram_threshold_enforced=False,scope='ONE_SINGLE_THREAD_OOC_SYNTHESIS_NO_IMPLEMENTATION',
        risk_policy='1536MiB commit launch floor; stop below1024MiB commit, or physical<256MiB for3s, or physical<768MiB and hard-page input>8192/s for5s;900s wall bound. No other-process termination.')
    save(HERE/'RESOURCE_GATE.json',gate);print(json.dumps(gate),flush=True)
    if reasons:host.close();return 2
    run=HERE/'build'/datetime.now(timezone(timedelta(hours=8))).strftime('syn_%Y%m%d_%H%M%S_%f')
    run.mkdir(parents=True);(run/'rom').mkdir();(run/'tmp').mkdir()
    for name in bound:shutil.copyfile(sim/name,run/name)
    for name in ('clock.xdc','synth_fullscale.tcl'):shutil.copyfile(HERE/name,run/name)
    shutil.copyfile(sim/'PREPARATION.json',run/'PREPARATION.json');shutil.copyfile(sim/'full_config.svh',run/'accepted_full_config.svh')
    ident=dict(at=now(),stage='OOC_SYNTHESIS_ONLY',top='ddr_synapse_top',part='xc7z020clg400-2',tool='Vivado2026.1.1',threads=1,flatten_hierarchy='none',
        generics=dict(H_COUNT=5768,SOURCE_COUNT=16402,EDGE_COUNT=433880,WEIGHT_COUNT=645,FIFO_DEPTH=4,AXI_TIMEOUT=64,STEP_TIMEOUT=8000000),
        accepted_simulation_directory=str(sim),accepted_result_sha256=sha(ACCEPTED/'FULL_RTL_RESULT.json'),accepted_manifest_sha256=sha(ACCEPTED/'MANIFEST_SHA256.json'),
        accepted_core_cycles=2643658,preparation_sha256=sha(sim/'PREPARATION.json'),original_full_config_sha256=sha(sim/'full_config.svh'),
        original_edge_stream_sha256='208da3b1a8984928bcc338e0f773a664398ef5df1e53a9a889d29e3fed197ff2',source_and_rom_sha256=bound,
        new_constraint_sha256=sha(run/'clock.xdc'),tcl_sha256=sha(run/'synth_fullscale.tcl'),runner_sha256=sha(__file__),launcher_sha256=sha(HERE/'launch_vivado.ps1'),
        monitor_sha256=sha(ACCEPTED/'windows_host.py'),resource_gate_sha256=sha(HERE/'RESOURCE_GATE.json'),wall_budget_seconds=900,
        clock_assumption='Abstract10ns synchronous clk; no HD.CLK_SRC/PS FCLK/pin; input max2/min0ns, output max2/min0ns; no false paths',
        scope='Full B prototype including AXI read subset/FIFO/compute/trace ports; core statistics are hierarchical subset, not a second synthesis')
    save(run/'RUN_IDENTITY.json',ident)
    if eda_processes():raise RuntimeError('EDA appeared during input copy; no launch')
    with (HERE/'LAUNCH_RECORD.json').open('x',encoding='utf-8') as f:json.dump(dict(run=str(run.relative_to(HERE)),at=now()),f,indent=2)
    start=time.perf_counter();seen={};peak_rss=peak_private=0;min_free=sample['available_MiB'];min_commit=sample['commit_headroom_MiB']
    peak_pages=0;low_seconds=paging_seconds=0;last=0;stop=None
    with (run/'console.log').open('w',encoding='utf-8') as log,(run/'host_resources.csv').open('w',newline='',encoding='utf-8') as rf:
        writer=csv.writer(rf);writer.writerow(['elapsed_seconds','available_MiB','commit_headroom_MiB','owned_processes','sum_working_set_MiB','sum_private_MiB','pages_input_per_sec','page_reads_per_sec'])
        proc=subprocess.Popen(['pwsh','-NoProfile','-File',str(HERE/'launch_vivado.ps1'),'-RunDir',str(run)],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
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

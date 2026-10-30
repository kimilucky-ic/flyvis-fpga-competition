"""Authorized isolated synthesis/route, guarded owned process tree only."""
import argparse
import csv
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import psutil

P=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def load_status(result):return result.get('status')=='PASS_SYNTH_COMMANDS' and result.get('returncode')==0


def commit_available():
    class MemoryStatus(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(n,ctypes.c_ulonglong) for n in
            ('total_phys','avail_phys','total_page','avail_page','total_virtual','avail_virtual','avail_extended')]
    memory=MemoryStatus();memory.length=ctypes.sizeof(memory)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):raise OSError('Cannot read Windows commit headroom')
    return memory.avail_page


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['synth','route'],required=True);ap.add_argument('--tag',default='soc_r1')
    ap.add_argument('--direct-start',action='store_true',help='Explicit 2026-10-18 user instruction to launch now; retain runtime memory guard')
    ap.add_argument('--reuse-synth',help='New route-only attempt from an immutable complete SoC synthesis run')
    args=ap.parse_args()
    assert args.tag.replace('_','').isalnum()
    check=json.loads((P/'control_r1/summary.json').read_text(encoding='utf-8'))
    assert check['state_mismatches']==0 and check['completed_steps']==3 and check['reader_stall_cycles']>2000000
    for name,h in json.loads((P/'control_r1/IDENTITY.json').read_text(encoding='utf-8')).items():assert sha(Path(name))==h,name
    run=P/args.tag
    if args.reuse_synth:
        assert args.stage=='route' and args.reuse_synth.replace('_','').isalnum()
        src=P/args.reuse_synth
        assert load_status(json.loads((src/'RESULT_synth.json').read_text(encoding='utf-8')))
        original=json.loads((src/'INPUT_SNAPSHOT.json').read_text(encoding='utf-8'))
        for name,h in original.items():assert sha(src/name)==h,name
        synthesis=json.loads((src/'RESULT_synth.json').read_text(encoding='utf-8'))
        for name,item in synthesis['reports'].items():assert sha(src/'release'/name)==item['sha256'],name
        run.mkdir(exist_ok=False);(run/'tmp').mkdir()
        for name in list(original)+['INPUT_SNAPSHOT.json','synth_completed.txt','RESULT_synth.json','tool_version.txt']:
            shutil.copyfile(src/name,run/name)
        shutil.copytree(src/'release',run/'release')
        generated='bd/flyvis_ddr/synth/flyvis_ddr.v';(run/generated).parent.mkdir(parents=True)
        shutil.copyfile(src/generated,run/generated)
        save(run/'REUSED_SYNTH.json',dict(source=str(src),checkpoint_sha256=sha(src/'release/ddr_soc_synth.dcp'),
            source_result_sha256=sha(src/'RESULT_synth.json'),new_synthesis=False))
    if args.stage=='synth':
        run.mkdir(exist_ok=False);(run/'tmp').mkdir()
        for f in (P/'rtl').glob('*.sv'):shutil.copyfile(f,run/f.name)
        for n in ('build_soc.tcl','route_soc.tcl','launch.ps1','thread_limit.tcl','run_vivado.py'):shutil.copyfile(P/n,run/n)
        shutil.copyfile(P/'platform/ps7_vendor_params.tcl',run/'ps7_vendor_params.tcl')
        save(run/'INPUT_SNAPSHOT.json',{f.name:sha(f) for f in run.iterdir() if f.is_file()})
    else:
        assert (run/'synth_completed.txt').exists() and (run/'release/ddr_soc_synth.dcp').exists()
        assert not (run/'RESULT_route.json').exists()
        for name,h in json.loads((run/'INPUT_SNAPSHOT.json').read_text(encoding='utf-8')).items():assert sha(run/name)==h,name
    available=psutil.virtual_memory().available
    launch_floor=1024 if args.direct_start else 3.3*1024
    pre=dict(stage=args.stage,available_MiB=available/2**20,minimum_launch_available_MiB=launch_floor,
        own_memory_limit_MiB=6144,host_stop_available_MiB=128 if args.direct_start else 512,
        host_stop_low_physical_duration_s=10 if args.direct_start else 0,
        available_commit_MiB=commit_available()/2**20,minimum_commit_MiB=1024,
        physical_warning_MiB=512,wall_limit_s=3600,threads=1,
        authorization='2026-10-18 user: independent PS7/HP0 control/input/publication, Vivado synthesis+place/route100MHz; no board',
        direct_start_user_authorized=args.direct_start,
        launcher_sha256=sha(Path(__file__)),reused_synth=args.reuse_synth,
        device='xc7z020clg400-2',new_board_operations=0,new_GPU_operations=0,
        path_ASCII=all(str(p).isascii() for p in (run.resolve(),P.resolve(),Path('C:/AMDDesignTools/2026.1.1/Vivado'))))
    assert pre['path_ASCII'];save(run/('PREFLIGHT_'+args.stage+'.json'),pre)
    print(json.dumps(pre),flush=True)
    if available<launch_floor*2**20 or pre['available_commit_MiB']<1024:
        save(run/('RESULT_'+args.stage+'.json'),dict(status='NOT_LAUNCHED_MEMORY',preflight=pre));return 2
    for p in psutil.process_iter(['name']):
        if 'vivado' in (p.info['name'] or '').lower() and not args.direct_start:raise RuntimeError('Another Vivado process is active; no launch')
    command=['cmd.exe','/d','/c','C:/AMDDesignTools/2026.1.1/Vivado/bin/vivado.bat',
             '-mode','batch','-notrace','-source','build_soc.tcl' if args.stage=='synth' else 'route_soc.tcl',
             '-log',args.stage+'.log','-journal',args.stage+'.jou']
    env=os.environ.copy();env['TEMP']=str(run/'tmp');env['TMP']=env['TEMP']
    env['OMP_NUM_THREADS']='1';env['PROCESSOR_ARCHITECTURE']='AMD64'
    seen={};peak_rss=peak_private=0;minimum=available;min_commit=commit_available();low_since=None;stop=None;start=time.monotonic()
    with (run/(args.stage+'_console.log')).open('w',encoding='utf-8') as log,(run/(args.stage+'_resources.csv')).open('w',newline='') as metrics:
        log.write(json.dumps(command)+'\n');log.flush()
        writer=csv.writer(metrics);writer.writerow(['elapsed_s','available_MiB','owned_RSS_MiB','owned_private_MiB','live_PIDs','available_commit_MiB'])
        proc=subprocess.Popen(command,cwd=run,env=env,stdout=log,stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        root=psutil.Process(proc.pid);seen[root.pid]=root.create_time()
        while proc.poll() is None:
            try:
                for child in root.children(recursive=True):
                    seen[child.pid]=child.create_time()
                    try:child.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                    except (psutil.AccessDenied,psutil.NoSuchProcess):pass
            except psutil.NoSuchProcess:pass
            rss=private=0;live=[]
            for pid,created in list(seen.items()):
                try:
                    child=psutil.Process(pid)
                    if child.create_time()!=created:continue
                    info=child.memory_info();rss+=info.rss;private+=getattr(info,'private',info.rss);live.append(pid)
                except (psutil.NoSuchProcess,psutil.AccessDenied):pass
            available=psutil.virtual_memory().available;minimum=min(minimum,available)
            peak_rss=max(peak_rss,rss);peak_private=max(peak_private,private);elapsed=time.monotonic()-start
            commit=commit_available();min_commit=min(min_commit,commit)
            writer.writerow([elapsed,available/2**20,rss/2**20,private/2**20,live,commit/2**20]);metrics.flush()
            if available<pre['host_stop_available_MiB']*2**20:
                if low_since is None:low_since=elapsed
                if elapsed-low_since>=pre['host_stop_low_physical_duration_s']:stop='HOST_HEADROOM'
            else:low_since=None
            if commit<1024*2**20:stop='COMMIT_HEADROOM'
            elif max(rss,private)>6144*2**20:stop='OWNED_MEMORY'
            elif elapsed>3600:stop='WALL_LIMIT'
            if stop:
                for pid,created in reversed(list(seen.items())):
                    try:
                        child=psutil.Process(pid)
                        if child.create_time()==created:child.kill()
                    except (psutil.NoSuchProcess,psutil.AccessDenied):pass
                break
            time.sleep(1)
        proc.wait(timeout=30)
    marker='synth_completed.txt' if args.stage=='synth' else 'completed.txt'
    result=dict(status='PASS_'+args.stage.upper()+'_COMMANDS' if proc.returncode==0 and (run/marker).exists() and not stop else 'STOPPED_OR_FAILED',
        returncode=proc.returncode,stop_reason=stop,seconds=time.monotonic()-start,
        peak_owned_RSS_MiB=peak_rss/2**20,peak_owned_private_MiB=peak_private/2**20,
        minimum_host_available_MiB=minimum/2**20,minimum_commit_available_MiB=min_commit/2**20,owned_processes=seen,
        reports={f.name:dict(bytes=f.stat().st_size,sha256=sha(f)) for f in (run/'release').glob('*') if f.is_file()})
    save(run/('RESULT_'+args.stage+'.json'),result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('reports','owned_processes')},indent=2),flush=True)
    return 0 if result['status'].startswith('PASS_') else 1


if __name__=='__main__':raise SystemExit(main())

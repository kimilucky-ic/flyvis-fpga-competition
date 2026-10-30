"""Isolated BIT generation from a sealed route. No FPGA connection or load."""
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import psutil

P=Path(__file__).resolve().parent
S=P.parent/'ddr_soc_20261018'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def verify_seals():
    out={}
    for name in ('hole_pipeline_20261016','ddr_snapshot_20261018','ddr_soc_20261018'):
        root=P.parent/name;manifest=root/'FINAL_MANIFEST_SHA256.json'
        data=json.loads(manifest.read_text(encoding='utf-8'))
        for n,item in data.items():
            f=root/n
            assert f.stat().st_size==item['bytes'] and sha(f)==item['sha256'],str(f)
        out[name]={'files':len(data),'manifest_sha256':sha(manifest)}
    return out

def main():
    baseline=verify_seals();save(P/'BASELINE_BEFORE.json',baseline)
    a=json.loads((S/'AUDIT.json').read_text(encoding='utf-8'))
    assert a['status']=='PASS_FULL_DDR_SOC_100MHZ_LOCAL_IMPLEMENTATION_ONLY'
    run=P/'bit_r1';run.mkdir(exist_ok=False);(run/'tmp').mkdir()
    for src,name in [(S/'soc_r9/release/ddr_soc_routed.dcp','source_routed.dcp'),
                     (S/'soc_r9/release/flyvis_ddr.hwh','flyvis_ddr.hwh'),(P/'bitgen.tcl','bitgen.tcl')]:
        shutil.copyfile(src,run/name)
    assert sha(run/'source_routed.dcp')=='c693e828c6028d0d6c41462e10aa52dfe1faa4bfc2ecc3b1e7d7f4e2b6227506'
    assert sha(run/'flyvis_ddr.hwh')=='69a4332593e32852aec9dbc7b177341f3303af067ee1f182c44152744f8598f1'
    save(run/'INPUT_SNAPSHOT.json',{f.name:sha(f) for f in run.iterdir() if f.is_file()})
    spec=importlib.util.spec_from_file_location('frozen_guard',S/'run_vivado.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    pre=dict(authorization='2026-10-18 user: generate/verify new BIT/HWH offline package, CPU DDR/cache/full-state acceptance; no board',
        available_physical_MiB=psutil.virtual_memory().available/2**20,available_commit_MiB=guard.commit_available()/2**20,
        maximum_owned_MiB=6144,minimum_commit_MiB=1024,physical_floor_MiB=128,physical_floor_duration_s=10,
        wall_limit_s=600,threads=1,board_operations=0,GPU_operations=0)
    save(run/'PREFLIGHT.json',pre);print(json.dumps(pre),flush=True)
    if pre['available_physical_MiB']<1024 or pre['available_commit_MiB']<3072:raise RuntimeError('Insufficient bitgen headroom; not launched')
    cmd=['cmd.exe','/d','/c','C:/AMDDesignTools/2026.1.1/Vivado/bin/vivado.bat','-mode','batch','-notrace','-source','bitgen.tcl','-log','bitgen.log','-journal','bitgen.jou']
    env=os.environ.copy();env.update(TEMP=str(run/'tmp'),TMP=str(run/'tmp'),OMP_NUM_THREADS='1',PROCESSOR_ARCHITECTURE='AMD64')
    seen={};peak=0;minimum=guard.commit_available();low=None;stop=None;start=time.monotonic()
    with (run/'console.log').open('w',encoding='utf-8') as log,(run/'resources.csv').open('w',newline='') as metrics:
        log.write(json.dumps(cmd)+'\n');log.flush();w=csv.writer(metrics);w.writerow(['elapsed_s','physical_MiB','commit_MiB','owned_RSS_MiB','owned_private_MiB'])
        proc=subprocess.Popen(cmd,cwd=run,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        root=psutil.Process(proc.pid);seen[root.pid]=root.create_time()
        while proc.poll() is None:
            try:
                for child in root.children(recursive=True):seen[child.pid]=child.create_time()
            except psutil.NoSuchProcess:pass
            rss=private=0
            for pid,created in list(seen.items()):
                try:
                    child=psutil.Process(pid)
                    if child.create_time()!=created:continue
                    child.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS);m=child.memory_info();rss+=m.rss;private+=getattr(m,'private',m.rss)
                except (psutil.NoSuchProcess,psutil.AccessDenied):pass
            physical=psutil.virtual_memory().available;commit=guard.commit_available();minimum=min(minimum,commit);peak=max(peak,rss,private);elapsed=time.monotonic()-start
            w.writerow([elapsed,physical/2**20,commit/2**20,rss/2**20,private/2**20]);metrics.flush()
            if physical<128*2**20:
                if low is None:low=elapsed
                elif elapsed-low>=10:stop='PHYSICAL_HEADROOM'
            else:low=None
            if commit<1024*2**20:stop='COMMIT_HEADROOM'
            elif max(rss,private)>6144*2**20:stop='OWNED_MEMORY'
            elif elapsed>600:stop='WALL_LIMIT'
            if stop:
                for pid,created in reversed(list(seen.items())):
                    try:
                        child=psutil.Process(pid)
                        if child.create_time()==created:child.kill()
                    except (psutil.NoSuchProcess,psutil.AccessDenied):pass
                break
            time.sleep(1)
        proc.wait(timeout=30)
    result=dict(status='PASS_BITGEN_COMMANDS_LOCAL_ONLY' if proc.returncode==0 and (run/'completed.txt').exists() and not stop else 'STOPPED_OR_FAILED',
        returncode=proc.returncode,stop_reason=stop,seconds=time.monotonic()-start,peak_owned_MiB=peak/2**20,minimum_available_commit_MiB=minimum/2**20,
        owned_processes=seen,board_operations=0,outputs={n:{'bytes':(run/n).stat().st_size,'sha256':sha(run/n)} for n in ('flyvis_ddr.bit','flyvis_ddr.hwh') if (run/n).exists()})
    save(run/'RESULT.json',result);print(json.dumps(result,indent=2),flush=True)
    return 0 if result['status'].startswith('PASS_') else 1

if __name__=='__main__':raise SystemExit(main())

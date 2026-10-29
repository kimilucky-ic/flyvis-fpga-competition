from pathlib import Path
P=Path(__file__).resolve().parent
s=(P.parent/'ramfix_r2_ooc_20261012/run_ooc.py').read_text(encoding='utf-8')
monitor=s[s.index('    start=time.perf_counter();seen={}'):s.index("if __name__=='__main__'")]
monitor=monitor.replace("str(HERE/'launch_vivado.ps1')","str(HERE/'launch.ps1')")
head='''from pathlib import Path
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
def save(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\\n',encoding='utf-8')
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
'''
(P/'run.py').write_text(head+monitor+"if __name__=='__main__':raise SystemExit(main())\n",encoding='utf-8')

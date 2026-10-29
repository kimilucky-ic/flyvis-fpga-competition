"""One bounded, below-normal CPU RTL job; no EDA synthesis, GPU or board."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil

P=Path(__file__).resolve().parent
VR=P.parent/'rtl_behavior_20261013/tools/verilator_5_48_0/verilator'
CC=Path('C:/AMDDesignTools/2026.1.1/tps/mingw/10.0.0/win64.o/nt/bin/g++.exe')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--kind',choices=['unit','full'],required=True);ap.add_argument('--tag',required=True)
    args=ap.parse_args();assert args.tag.replace('_','').isalnum();assert args.kind=='full'
    out=P/args.tag;out.mkdir(exist_ok=False)
    env=os.environ.copy();env['VERILATOR_ROOT']=str(VR);env['PATH']=str(CC.parent)+os.pathsep+env['PATH']
    phases=[]
    def execute(command,name,limit):
        start=time.monotonic();seen={};peak=0;minimum=psutil.virtual_memory().available;stop=None
        if minimum<640*2**20:raise RuntimeError('Insufficient host headroom before '+name)
        with (out/(name+'.log')).open('w',encoding='utf-8') as log:
            log.write(json.dumps(command)+'\n');log.flush()
            proc=subprocess.Popen(command,cwd=P,env=env,stdout=log,stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            root=psutil.Process(proc.pid);seen[root.pid]=root.create_time()
            while proc.poll() is None:
                try:
                    for child in root.children(recursive=True):seen[child.pid]=child.create_time()
                except psutil.NoSuchProcess:pass
                rss=0
                for pid,created in list(seen.items()):
                    try:
                        child=psutil.Process(pid)
                        if child.create_time()==created:rss+=child.memory_info().rss
                    except (psutil.NoSuchProcess,psutil.AccessDenied):pass
                available=psutil.virtual_memory().available;minimum=min(minimum,available);peak=max(peak,rss)
                if available<384*2**20:stop='HOST_HEADROOM'
                elif rss>768*2**20:stop='OWNED_RSS'
                elif time.monotonic()-start>limit:stop='WALL_LIMIT'
                if stop:
                    for pid,created in reversed(list(seen.items())):
                        try:
                            child=psutil.Process(pid)
                            if child.create_time()==created:child.kill()
                        except (psutil.NoSuchProcess,psutil.AccessDenied):pass
                    break
                time.sleep(.5)
            proc.wait(timeout=10)
        row=dict(stage=name,returncode=proc.returncode,stop_reason=stop,seconds=time.monotonic()-start,
                 peak_owned_rss_MiB=peak/2**20,minimum_host_available_MiB=minimum/2**20,
                 sample_interval_s=.5,owned_processes=seen)
        phases.append(row);(out/'RUN.json').write_text(json.dumps(phases,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(row),flush=True)
        if proc.returncode or stop:
            raise RuntimeError((out/(name+'.log')).read_text(encoding='utf-8',errors='replace')[-5000:])
    sources=[P/'rtl/snapshot_axi_writer.sv']
    params=[];top='snapshot_axi_writer';test=P/'tests/test_writer.cpp'
    if args.kind=='unit':params=['-GN=257','-GNE=17','-GINPUT_WORDS=7','-GBUS_TIMEOUT=96']
    else:
        top='flyvis_ddr_soc_ip';test=P/'tests/test_soc_ip.cpp'
        sources += [P/'rtl'/n for n in ['fp32_rne.sv','banked_state_mem.sv','sync_mem.sv','compact_edge_gen.sv','flyvis_lane.sv','flyvis_ddr_snapshot_top.sv','flyvis_ddr_soc_ip.sv']]
    execute([str(VR/'bin/verilator_bin.exe'),'--cc','--assert','--no-timing','--compiler','gcc','-Wno-fatal',
             '--output-split','3000','--output-split-cfuncs','500','--prefix','Vdut','--top-module',top,
             '--Mdir',str(out),*params,*map(str,sources)],'verilate',120)
    cpp=sorted(out.glob('*.cpp'))+[VR/'include/verilated.cpp',VR/'include/verilated_threads.cpp',test]
    if args.kind=='full':cpp.append(P/'rtl/host_reference.cpp')
    execute([str(CC),'-std=c++17','-O1','-ffp-contract=off','-fno-fast-math','-frounding-math','-msse2','-mfpmath=sse',
             '-pthread','-static','-DDPI_DLLISPEC=','-DDPI_DLLESPEC=','-DVL_TIME_CONTEXT',
             '-I'+str(out),'-I'+str(VR/'include'),'-I'+str(VR/'include/vltstd'),'-I'+str(P/'tests'),
             *map(str,cpp),'-o',str(out/'sim.exe')],'compile',240)
    command=[str(out/'sim.exe'),str(out)]
    if args.kind=='full':
        images=P.parent/'hole_pipeline_20261016/images'
        command += ['+META='+str(images/'meta.hex'),'+MAP='+str(images/'map.hex'),'+ROWS='+str(images/'rows.hex'),'+INIT='+str(images/'initial.hex'),'+verilator+seed+20261018']
    execute(command,'simulation',180)
    inputs=sources+[test,P/'tests/ddr_model.hpp',Path(__file__),CC,VR/'bin/verilator_bin.exe']
    (out/'IDENTITY.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},indent=2)+'\n',encoding='utf-8')
    print((out/'summary.json').read_text(encoding='utf-8'),flush=True)


if __name__=='__main__':main()

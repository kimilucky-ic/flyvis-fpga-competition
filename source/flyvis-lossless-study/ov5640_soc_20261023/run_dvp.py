import os,subprocess,json,time
from pathlib import Path
p=Path(__file__).resolve().parent
vr=p.parent/'rtl_behavior_20261013/tools/verilator_5_48_0/verilator'
cc=Path('C:/AMDDesignTools/2026.1.1/tps/mingw/10.0.0/win64.o/nt/bin/g++.exe')
out=p/'sim_r2';out.mkdir(exist_ok=False)
env=os.environ.copy();env['VERILATOR_ROOT']=str(vr);env['PATH']=str(cc.parent)+os.pathsep+env['PATH']
records=[]
def run(cmd,name):
    t=time.monotonic()
    with (out/(name+'.log')).open('w') as f:
        f.write(json.dumps(cmd)+'\n');f.flush()
        r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
    records.append(dict(stage=name,returncode=r.returncode,seconds=time.monotonic()-t))
    (out/'RUN.json').write_text(json.dumps(records,indent=2))
    if r.returncode: raise RuntimeError((out/(name+'.log')).read_text()[-3000:])
run([str(vr/'bin/verilator_bin.exe'),'--cc','--no-timing','--compiler','gcc','-Wno-fatal','--prefix','Vdut','--top-module','cmos_capture_data','--Mdir',str(out),str(p/'rtl/cmos_capture_data.v')],'verilate')
cpp=list(out.glob('*.cpp'))+[vr/'include/verilated.cpp',vr/'include/verilated_threads.cpp',p/'test_dvp.cpp']
run([str(cc),'-std=c++17','-O0','-pthread','-static','-DDPI_DLLISPEC=','-DDPI_DLLESPEC=','-DVL_TIME_CONTEXT','-I'+str(out),'-I'+str(vr/'include'),'-I'+str(vr/'include/vltstd'),*map(str,cpp),'-o',str(out/'sim.exe')],'compile')
run([str(out/'sim.exe')],'simulate')
print((out/'simulate.log').read_text())

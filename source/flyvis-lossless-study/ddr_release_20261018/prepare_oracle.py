"""Tiny one-process CPU build and independent three-step full-network reference."""
import hashlib,json,subprocess,time
from pathlib import Path
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=P/'oracle_r1';out.mkdir(exist_ok=False)
    cc=Path('C:/AMDDesignTools/2026.1.1/tps/mingw/10.0.0/win64.o/nt/bin/g++.exe')
    ref=P.parent/'ddr_soc_20261018/rtl/host_reference.cpp'
    cmd=[str(cc),'-O2','-std=c++17','-ffp-contract=off','-fno-fast-math','-frounding-math','-msse2','-mfpmath=sse','-static',str(P/'make_reference.cpp'),str(ref),'-o',str(out/'reference.exe')]
    commands=[]
    for name,args in [('compile',cmd),('oracle',[str(out/'reference.exe'),str(P.parent),str(out)])]:
        start=time.monotonic()
        r=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        (out/(name+'.log')).write_bytes(r.stdout);commands.append(dict(phase=name,command=args,returncode=r.returncode,seconds=time.monotonic()-start));r.check_returncode()
    assert (out/'expected_states.bin').stat().st_size==3*45669*4
    records=(P.parent/'ddr_soc_20261018/control_r1/ddr_records.bin').read_bytes()
    expected=(out/'expected_states.bin').read_bytes();inputs=(out/'inputs.bin').read_bytes()
    for i in range(3):
        assert records[i*188416+128:i*188416+128+2884]==inputs[i*2884:(i+1)*2884]
        assert records[i*188416+4096:i*188416+4096+182676]==expected[i*182676:(i+1)*182676]
    files=[P/'make_reference.cpp',ref,cc,P.parent/'rtl_behavior_20261013/vectors/initial32/edges.bin',P.parent/'rtl_behavior_20261013/vectors/initial32/initial.bin',P.parent/'rtl_behavior_20261013/vectors/initial32/stimulus.bin',P.parent/'hole_pipeline_20261016/images/meta.hex',P.parent/'preboard_20261018/bundle_r1/expected_state1.bin']
    result=dict(status='PASS_INDEPENDENT_SERIAL_FP32_REFERENCE_CPU_ONLY',steps=3,state_words=137007,input_words=2163,
        commands=commands,input_sha256={str(f):sha(f) for f in files},output_sha256={f.name:sha(f) for f in out.glob('*.bin')},
        RTL_records_match=True,board_operations=0,GPU_operations=0,reference_profile='Frozen edge order, binary32 RNE each add/mul, no FMA/FTZ/DAZ; not CUDA scatter bitwise oracle')
    (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k in ('status','steps','state_words','input_words','RTL_records_match')},indent=2))
if __name__=='__main__':main()

from pathlib import Path
import subprocess,json,time,hashlib
P=Path(__file__).resolve().parent;B=P/'bundle';out=P/'oracle_check';out.mkdir(exist_ok=False)
cc='C:/AMDDesignTools/2026.1.1/tps/mingw/10.0.0/win64.o/nt/bin/g++.exe'
cmd=[cc,'-O2','-std=c++17','-ffp-contract=off','-fno-fast-math','-frounding-math','-msse2','-mfpmath=sse','-static',str(B/'reference.cpp'),str(B/'host_reference.cpp'),'-o',str(B/'reference.exe')]
records=[]
for name,args in [('compile',cmd),('known_three_steps',[str(B/'reference.exe'),str(B),str(P.parent/'ddr_release_20261018/bundle_r2/inputs.bin'),str(out/'expected_states.bin')])]:
 start=time.monotonic();r=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
 (out/(name+'.log')).write_bytes(r.stdout);records.append(dict(command=args,exit_code=r.returncode,seconds=time.monotonic()-start));r.check_returncode()
expected=(P.parent/'ddr_release_20261018/bundle_r2/expected_states.bin').read_bytes();actual=(out/'expected_states.bin').read_bytes();assert actual==expected
result=dict(status='PASS_CPU_ORACLE_REUSE_3_STEPS_137007_STATES',state_words=137007,steps=3,commands=records,expected_sha256=hashlib.sha256(actual).hexdigest(),board_operations=0)
(out/'RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

from pathlib import Path
import subprocess,json,os
from sensor_init import initialize
p=Path(__file__).resolve().parent
s=(p/'vendor/ov5640_init.c').read_text(encoding='gb18030');s=s[s.index('u8 ov5640_init('):]
header='''#include <cstdio>
using u8=unsigned char; using u16=unsigned short;
void usleep(unsigned x){printf("D %u\\n",x);}
u8 sccb_read_reg16(u16 a){printf("R %u\\n",a);return a==0x300b?0x40:0x56;}
void sccb_write_reg16(u16 a,u8 b){printf("W %u %u\\n",a,b);}
'''
(p/'vendor_trace.cpp').write_text(header+s+'\nint main(){return ov5640_init(640,480,1800,1000);}',encoding='utf-8')
cc=Path('C:/AMDDesignTools/2026.1.1/tps/mingw/10.0.0/win64.o/nt/bin/g++.exe')
env=os.environ.copy();env['PATH']=str(cc.parent)+os.pathsep+env['PATH']
subprocess.run([str(cc),'-O0',str(p/'vendor_trace.cpp'),'-o',str(p/'vendor_trace.exe')],check=True,timeout=40,env=env)
reference=subprocess.check_output([str(p/'vendor_trace.exe')],text=True,timeout=5).splitlines()
trace=[]
def read(a): trace.append('R '+str(a));return 0x40 if a==0x300b else 0x56
def write(a,b):trace.append('W %d %d'%(a,b))
def delay(s):trace.append('D '+str(round(s*1000000)))
n=initialize(read,write,delay)
assert trace==reference
bad=[]
try:initialize(lambda a:0,lambda a,b:bad.append((a,b)),lambda s:None)
except RuntimeError:pass
else:raise AssertionError('bad ID accepted')
assert not bad
calls=[]
def reject(a,b):calls.append((a,b));return False
try:initialize(lambda a:0x40 if a==0x300b else 0x56,reject,lambda s:None)
except RuntimeError:pass
else:raise AssertionError('NACK accepted')
assert len(calls)==1
(p/'init_trace.txt').write_text('\n'.join(trace)+'\n')
(p/'INIT_RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_VENDOR_C_TRACE_EQUIVALENT',writes=n,events=len(trace),bad_id_no_writes=True,nack_no_retry=True,hardware_actions=0),indent=2))
print(n,len(trace))

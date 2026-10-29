"""CPU host-control tests only, never claims RTL/system simulation."""
import numpy as np,json,ast
from pathlib import Path
from arm_controller import FlyvisB
P=Path(__file__).resolve().parent
class Edge:
 def init__(self):self.flushes=0;self.freed=False
 def flush(self):self.flushes+=1
 def freebuffer(self):self.freed=True
class MMIO:
 def init__(self):self.regs={0x1c:0,0x64:0,0x68:0};self.writes=[];self.error=0
 def write(self,offset,value):
  self.writes.append((offset,value));self.regs[offset]=value
  if offset==0x18 and value==1:self.regs[0x64]=0
  if 0x1000<=offset<0x1000+4*22170:self.regs[0x64]+=1
  if offset==0x18 and value==2:self.regs[0x1c]=6;self.regs[0x68]+=1
 def read(self,offset):
  if offset in (0x34,0x38,0x3c):return self.error
  if offset==0x44:return 433880
  if offset in (0x48,0x4c):return self.regs[offset-0x1c]
  if offset in (0x50,0x54):return self.regs[offset-0x30]
  if 0x18000<=offset<0x18000+4*5768:return 0xffffffff if (offset-0x18000)//4%2 else 0
  return self.regs.get(offset,0)
def controller():
 c=FlyvisB.__new__(FlyvisB);c.mmio=MMIO();c.edges=Edge();c.address=0x10000000;return c
cases=[];src=np.zeros(16402,dtype=np.int32);oldx=np.zeros(5768,dtype=np.int32)
c=controller();r=c.run_once(src,oldx,17,0xe1ca6d82,0x52f17c8733341788)
assert r['candidate'].shape==(5768,) and r['candidate'][1]==-1
loads=[(a,v) for a,v in c.mmio.writes if 0x1000<=a<0x1000+4*22170]
assert len(loads)==22170 and [a for a,v in loads]==list(range(0x1000,0x1000+4*22170,4))
assert c.mmio.writes.count((0x18,2))==1 and c.edges.flushes==1
cases.append('all_22170_state_words_ordered_one_START_identity_signed_candidate')
c=controller();c.mmio.regs[0x1c]=9
try:c.run_once(src,oldx,17,0,0);raise AssertionError('busy accepted')
except RuntimeError:assert not c.mmio.writes
cases.append('busy_request_refused_before_writes')
c=controller();bad=src.astype(np.int64);bad[0]=1<<30
try:c.run_once(bad,oldx,17,0,0);raise AssertionError('overflow accepted')
except ValueError:assert not c.mmio.writes
cases.append('signed31_overflow_refused_without_truncation')
c=controller();c.mmio.error=0x40
try:c.run_once(src,oldx,17,0,0);raise AssertionError('failed result accepted')
except RuntimeError:pass
cases.append('core_transport_error_no_candidate')
c=controller();c.mmio.regs[0x1c]=9
try:c.close();raise AssertionError('busy buffer freed')
except RuntimeError:assert not c.edges.freed
c.mmio.regs[0x1c]=0;c.close();assert c.edges is None
cases.append('DDR_buffer_retained_until_reader_idle')
for f in P.glob('*.py'):ast.parse(f.read_text(encoding='utf-8'))
result={'status':'PASS_CPU_ARM_CONTROLLER_ONLY','case_count':len(cases),'cases':cases,'RTL_or_BD_simulation':False,'board_IO':0,'GPU':0}
(P/'CPU_HOST_TESTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))

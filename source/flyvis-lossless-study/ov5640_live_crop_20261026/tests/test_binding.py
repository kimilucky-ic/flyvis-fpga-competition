"""Three new cropped inputs through real bridge/record binding with CPU fixtures."""
from pathlib import Path
import sys,json,struct,subprocess,hashlib
import numpy as np
P=Path(__file__).resolve().parents[1];B=P/'bundle';sys.path.insert(0,str(B))
from official_bridge import OfficialBridge
from ddr_control import Published,STRIDE
from snapshot_records import rolling
from capture_binding import read_capsule
T=P/'evidence/binding';T.mkdir(exist_ok=False)
inputs=(P/'evidence/test_inputs.bin').read_bytes();assert len(inputs)==3*2884
cmd=[str((B/'reference.exe').resolve()),str(B.resolve()),str((P/'evidence/test_inputs.bin').resolve()),str((T/'expected_states.bin').resolve())]
r=subprocess.run(cmd,capture_output=True,timeout=60);(T/'oracle.log').write_bytes(r.stdout+r.stderr);assert r.returncode==0
states=(T/'expected_states.bin').read_bytes();assert len(states)==3*182676
frames=[]
for k in range(3):
 raw=(P.parent/'ov5640_live_r2_20261025/pc/records'/('%06d.packet'%k)).read_bytes();n=struct.unpack_from('<I',raw)[0]
 frames.append(np.frombuffer(raw[4+n:4+n+800*480*3],np.uint8).reshape(480,800,3)[::10,::10].copy())
template=(P.parent/'ov5640_live_ring_20261026/pc/records/000000.packet').read_bytes()[-STRIDE:]
class Frame(np.ndarray):
 def freebuffer(self):self.owner.freed+=1
class Video:
 def init__(self):self.i=0;self.freed=0;self.closed=False
 def readframe(self):
  f=frames[self.i].copy().view(Frame);f.owner=self;self.i+=1;return f
 def close(self):self.closed=True
class Control:
 def init__(self,mode=None):self.calls=[];self.raw=None;self.mode=mode
 def advance(self,payload):
  k=len(self.calls);assert payload==inputs[k*2884:(k+1)*2884]
  self.calls.append(payload);raw=bytearray(template)
  raw[128:3012]=payload;raw[4096:186772]=states[k*182676:(k+1)*182676]
  struct.pack_into('<I',raw,8,k);struct.pack_into('<2I',raw,80,k+1,0xc0ffee)
  if self.mode=='input_mismatch':raw[128]^=1
  struct.pack_into('<2I',raw,48,rolling(raw[128:3012]),rolling(raw[4096:186772]))
  if self.mode=='state_corruption':raw[4096]^=1
  self.raw=bytes(raw);return Published(k+1,0x10000000+k*STRIDE,k,2199975,0xc0ffee)
class Memory:
 def init__(self,c):self.c=c
 def copy_record(self,d):return self.c.raw
v=Video();c=Control();bridge=OfficialBridge(v,c,Memory(c),T/'positive',3,evidence='CPU_MOCK_ONLY')
for k in range(3):
 d=bridge.step();prepared,actual=read_capsule(T/'positive/bound'/('%06d'%k)/'PREPARED.bin',2884)
 committed,raw=read_capsule(T/'positive/bound'/('%06d'%k)/'COMMITTED.bin',STRIDE)
 assert actual==inputs[k*2884:(k+1)*2884]==raw[128:3012]
 assert raw[4096:186772]==states[k*182676:(k+1)*182676]
 assert prepared['step_id']==committed['step_id']==k and committed['sequence']==k+1
assert len(c.calls)==3 and v.freed==3
profile=json.loads((T/'positive/PROFILE.json').read_text());assert profile['mapping']=='direct-grey-center-square-area/v2' and profile['mapping_contract']['crop']==dict(top=0,left=16,height=48,width=48)
for mode in ('input_mismatch','state_corruption'):
 v=Video();c=Control(mode);out=T/mode;b=OfficialBridge(v,c,Memory(c),out,3,evidence='CPU_MOCK_ONLY')
 try:b.step()
 except (RuntimeError,ValueError):pass
 else:raise AssertionError('corrupt record accepted')
 assert b.failed and b.binding.next==0 and len(c.calls)==1 and not v.closed
 assert (out/'bound/000000/PREPARED.bin').exists() and not (out/'bound/000000/COMMITTED.bin').exists()
 assert (out/'bound/000000/RETURNED_UNCOMMITTED.bin').exists()
 try:b.step()
 except RuntimeError:pass
 else:raise AssertionError('failed bridge rerun')
 assert len(c.calls)==1
result=dict(status='PASS_CPU_NEW_CROP_INPUT_BINDING',new_CPU_reference_steps=3,state_words_in_fixture=3*45669,input_words=3*721,exact_input_stage_record_match=True,crop_contract_saved=True,wrong_published_input_rejected=True,corrupted_state_rejected=True,failed_retry_rejected=True,source='new ordered CPU reference output replayed as mock PL response; not independent RTL validation',command=cmd,board_operations=0,GPU_operations=0)
(P/'evidence/BINDING_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

"""Three full-network software-oracle frames through actual control/buffer/bridge.
Fake camera, MMIO, DDR producer only: not RTL/native ARM or real-time evidence.
"""
from pathlib import Path
import json,struct,subprocess,sys
import numpy as np
R=Path(__file__).resolve().parent;B=R/'bundle';sys.path.insert(0,str(B))
from official_bridge import OfficialBridge
from board_runtime import CheckedVideo
from ddr_control import DdrControl
from ddr_memory import OwnedDdr
from snapshot_records import LatestDisplay,rolling
from ps_input import PsInput
from audit_bridge import audit
from continuous_prepare import next_committed_frame
O=R/'evidence/continuous_cpu';O.mkdir(exist_ok=False)
raw=(R.parent/'ov5640_official_audit_20261024_b0a5/raw/capture/bound/000000/source_frame.bin').read_bytes()
f=np.frombuffer(raw,np.uint8).reshape(480,800,3)
frames=[f.copy(),f[:,::-1,:].copy(),np.zeros_like(f)]
inputs=[PsInput(480,800,'BGR').render(x).astype('<f4').tobytes() for x in frames]
(O/'inputs.bin').write_bytes(b''.join(inputs))
cmd=[str((B/'reference.exe').resolve()),str(B.resolve()),str((O/'inputs.bin').resolve()),str((O/'expected.bin').resolve())]
p=subprocess.run(cmd,capture_output=True,timeout=60);(O/'oracle.log').write_bytes(p.stdout+p.stderr);p.check_returncode()
(O/'COMMAND.json').write_text(json.dumps({'command':cmd,'fixture':'Sequential CPU oracle, not independent DUT'}))
expected=(O/'expected.bin').read_bytes();assert len(expected)==3*182676
CYCLES=json.loads((R.parent/'ddr_soc_20261018/AUDIT.json').read_text())['cycle_counter']['record_values'][0]
events=[]
class Buffer(np.ndarray):
 def __new__(cls,size):
  a=np.zeros(size,np.uint8);x=a.view(cls);x.cache=a;x.device=np.zeros_like(a);x.physical_address=0x1000000;x.coherent=False;return x
 def __array_finalize__(self,p):
  for n in ('cache','device','physical_address','coherent'):
   if hasattr(p,n):setattr(self,n,getattr(p,n))
 def flush(self):self.device[:]=self.cache
 def invalidate(self):self.cache[:]=self.device;events.append('invalidate')
 def freebuffer(self):raise AssertionError('neural DDR freed')
class Frame(np.ndarray):
 def __new__(cls,k):
  x=frames[k].copy().view(cls);x.physical_address=0x2000000;x.coherent=False;return x
 def invalidate(self):pass
 def freebuffer(self):self.fill(255);events.append('free_frame')
class Video:
 def init__(self):self.k=0
 def readframe(self):
  if self.k>=3:raise AssertionError('camera read past audit capacity')
  x=Frame(self.k);self.k+=1;events.append('capture');return x
 def close(self):events.append('close')
mem=OwnedDdr(lambda shape,**k:Buffer(shape[0]),lambda:None,3);mem.pin_before_configure()
class MMIO:
 def init__(self):self.r={0x30:45669,0x34:1513231,0x38:0x110004,0x3c:188416};self.words=[];self.steps=0
 def read(self,a):return self.r.get(a,0)
 def write(self,a,v):
  if a>=0x400:self.words.append(v);self.r[0x18]=len(self.words);return
  if a!=0:self.r[a]=v;return
  if v==2:self.r[0x10]=2
  elif v==4:self.r[0x10]=6
  elif v==1:
   k=self.steps;actual=struct.pack('<721I',*self.words);assert actual==inputs[k]
   d=O/'capture/bound'/('%06d'%k);assert (d/'input.bin').read_bytes()==actual and (d/'PREPARED.json').exists()
   state=expected[k*182676:(k+1)*182676];h=[0]*32
   for j,x in {0:0x5331314c,1:0x10000,2:k,4:45669,5:1513231,6:2884,7:182676,8:CYCLES,9:1513231,10:45669,11:188416,12:rolling(actual),13:rolling(state),14:128,15:4096,16:0x110003,17:0x3ba3d70a}.items():h[j]=x
   b=bytearray(188416);struct.pack_into('<32I',b,0,*h);b[128:3012]=actual;b[4096:186772]=state
   mem.buffer.device[k*188416:(k+1)*188416]=np.frombuffer(b,np.uint8)
   self.steps+=1;self.words=[];self.r.update({0x10:46 if self.steps==3 else 38,0x14:self.steps,0x18:0});events.append('step')
  elif v==8:
   k=self.steps-1;self.r.update({0x80:k+1,0x84:mem.base+k*188416,0x88:k,0x8c:CYCLES,0x90:k+1,0x94:self.r[0x2c],0x98:0,0x9c:45669,0xa0:1513231})
mm=MMIO();control=DdrControl(mm);control.restore_initial();control.configure(mem.base,mem.size,3,123)
video=Video();checked=CheckedVideo(video,mem,lambda:None,O)
bridge=OfficialBridge(checked,control,mem,O/'capture',3,evidence='CPU_MOCK_ONLY');latest=LatestDisplay()
next_committed_frame(bridge,latest);lease=latest.acquire();assert lease.frame_id==0
# Simulate a slow display holding frame0: producer must still complete frames1,2.
next_committed_frame(bridge,latest);next_committed_frame(bridge,latest)
assert mm.steps==3 and latest.reading.frame_id==0 and latest.latest.frame_id==2
latest.release(0);assert latest.acquire().frame_id==2;latest.release(2)
assert latest.skipped_display_frames==1
before=list(events)
try:next_committed_frame(bridge,latest)
except RuntimeError as e:assert 'capacity' in str(e)
else:raise AssertionError('unbounded extra step')
assert events==before and video.k==3
bridge.close_success();result=audit(O/'capture',O/'audit',B)
assert result['state_words_compared']==137007 and result['mismatch_words']==0
assert len(list(O.glob('CAMERA_BUFFER*.json')))==3
for k in range(3):assert (O/'capture/bound'/('%06d'%k)/'source_frame.bin').read_bytes()==frames[k].tobytes()
(O/'RESULT.json').write_text(json.dumps(dict(status='PASS_THREE_STEP_CPU_PREPARATION_ONLY',steps=3,
 actual_input_words=2163,state_words_compared=137007,mismatch_words=0,feedback_transitions=2,
 display_acquired_frames=[0,2],display_skipped=1,all_neural_records_preserved=True,
 blocked_display_did_not_block_producer=True,bounded_capacity_refused_before_capture=True,
 hardware_operations=0,independent_RTL_math=False,native_ARM=False,real_time=False),indent=2)+'\n')
print('PASS_THREE_STEP_CPU_PREPARATION_ONLY')

"""CPU fixtures only: actual R3 payload replay is NOT a new neural/board run."""
import sys,json,struct,time,threading,hashlib,shutil,unittest,os
from pathlib import Path
from unittest.mock import patch
import numpy as np
P=Path(__file__).resolve().parents[1];S=P/'bundle';sys.path.insert(0,str(S))
from ddr_control import DdrControl,N,NE,VERSION,STRIDE
from duration_run import RunWindow,memory_plan
from batch_records import BatchRecords
from snapshot_records import decode_record
from live_protocol import load_packet,unpack,Store,sha
from camera_config import WIDTH,HEIGHT
import ram_records,live_board
T=P/'evidence'/('cpu_'+time.strftime('%Y%m%d_%H%M%S'));T.mkdir()
BASE=P.parent/'ov5640_live_60s_r3_20261026/bundle'
RECORDS=P.parent/'ov5640_live_60s_20261026/pc/records'
# Use copied, immutable inputs/state bytes from already accepted R3; replace only
# ring header ABI/sequence/cookie for CPU fixtures. No camera or neural arithmetic.
raw_records=[(RECORDS/('%06d.packet'%k)).read_bytes()[-STRIDE:] for k in range(210)]
class MMIO:
 def init__(self,clock=None):
  self.reg={0x30:N,0x34:NE,0x38:VERSION,0x3c:STRIDE,0x10:0,0x14:0,0x18:0,0x24:0,0x4c:0};self.writes=[];self.words=[];self.memory=None;self.clock=clock;self.acks=[];self.ack_fail=False
 def read(self,a):
  if a==0x50:return self.reg[0x14]-self.reg[0x4c]
  return self.reg.get(a,0)
 def write(self,a,v):
  if isinstance(v,bytes):
   for i,(w,) in enumerate(struct.iter_unpack('<I',v)):self.write(a+4*i,w)
   return
  self.writes.append((a,v))
  if a>=0x400:
   assert a==0x400+4*self.reg[0x18];self.words.append(v);self.reg[0x18]+=1;return
  if a:self.reg[a]=v;return
  if v==2:self.reg[0x10]=2
  elif v==4:self.reg[0x10]|=4
  elif v==16:
   if self.ack_fail:raise OSError('uncertain release MMIO')
   seq=self.reg[0x44];assert self.reg[0x4c]<=seq<=self.reg[0x14] and self.reg[0x48]==self.reg[0x2c]
   if ram_records.CURRENT is not None:assert seq<=ram_records.CURRENT.durable_prefix(),'ACK before fsync'
   self.reg[0x4c]=seq;self.acks.append(seq)
   if self.read(0x50)<self.reg[12]:self.reg[0x10]&=~8
  elif v==1:
   k=self.reg[0x14];assert self.reg[0x18]==721 and self.read(0x50)<self.reg[12]
   if self.memory is not None:
    raw=bytearray(raw_records[k]);assert struct.pack('<721I',*self.words)==raw[128:3012]
    struct.pack_into('<I',raw,64,VERSION);struct.pack_into('<2I',raw,80,k+1,self.reg[0x2c])
    offset=(k%self.reg[12])*STRIDE;self.memory.raw[offset:offset+STRIDE]=raw
   self.reg[0x14]+=1;self.reg[0x18]=0;self.words=[];self.reg[0x10]|=32
   if self.read(0x50)==self.reg[12]:self.reg[0x10]|=8
   if self.clock:self.clock.t+=.31
  elif v==8:
   seq=self.reg[0x14];self.reg.update({0x80:seq,0x84:self.reg[4]+((seq-1)%self.reg[12])*STRIDE,0x88:seq-1+self.reg[0x1c],0x8c:2199975,0x90:seq,0x94:self.reg[0x2c],0x98:0,0x9c:N,0xa0:NE})
  else:raise AssertionError(v)
class Clock:
 def init__(self):self.t=0.;self.sleeps=[]
 def clock(self):return self.t
 def sleep(self,t):self.sleeps.append(t);self.t+=t;time.sleep(min(t,.001))
class Memory:
 def init__(self,slots):self.base=0x10000000;self.size=slots*STRIDE;self.raw=bytearray(self.size)
 def pin_before_configure(self):pass
 def copy_record(self,d):
  off=d.address-self.base;assert 0<=off<=self.size-STRIDE;return bytes(self.raw[off:off+STRIDE])
class Frame(np.ndarray):
 def freebuffer(self):pass
class Video:
 def init__(self):self.frames=0;self.closed=False
 def readframe(self):self.frames+=1;return np.zeros((HEIGHT,WIDTH,3),np.uint8).view(Frame)
 def close(self):self.closed=True
class Runtime:
 evidence='CPU_MOCK_ONLY'
 def init__(self,root,out):self.owner={};self.mm=MMIO(virtual);self.video=Video();self.owner['fixture']='R3 payload replay, not computation'
 def prepare(self):pass
 def load(self):pass
 def inspect(self):pass
 def control(self):self.control_obj=DdrControl(self.mm,bulk_input=True);return self.control_obj
 def memory(self,slots):self.mm.memory=Memory(slots);return self.mm.memory
 def start_camera(self,m):return self.video
config=dict(motion_condition='white_black',max_steps=256,ring_slots=64,duration_s=60.,minimum_period_s=0.,transfer_mode='local_only',session_id='cpu_ring',bit_sha256='CPU_ONLY_NO_RING_BIT',hwh_sha256='CPU_ONLY_NO_RING_HWH',initial_state_sha256=sha((BASE/'initial_state.bin').read_bytes()),diagnostics=False,camera_diagnostics=False)
checks=[]
def passed(s):checks.append(s);print('PASS',s,flush=True)
def rejects(fn,errors=(RuntimeError,ValueError,OSError)):
 try:fn()
 except errors:return
 raise AssertionError('must reject')
def fresh(slots=2):
 m=MMIO();d=DdrControl(m);d.restore_initial();d.configure(0x10000000,slots*STRIDE,slots,0x12345678);return m,d
# Control and model negatives; RTL independently implements the same protocol.
m=MMIO();m.reg[0x38]=0x00110004;rejects(lambda:DdrControl(m));assert not m.writes
m,d=fresh();inp=raw_records[0][128:3012];d.advance(inp);d.advance(inp);before=len(m.writes);rejects(lambda:d.advance(inp));assert len(m.writes)==before
rejects(lambda:d.release_durable(3));assert len(m.writes)==before
d.release_durable(1);assert d.advance(inp).address==0x10000000
before=len(m.writes);d.release_durable(1);assert len(m.writes)==before
rejects(lambda:d.release_durable(0));d.release_durable(3);rejects(d.publication)
passed('old ABI no writes; full blocks STEP; modulo descriptor; duplicate idempotent; future/stale and released read rejected')
m,d=fresh();d.advance(inp);errs=[]
def bad_thread():
 try:d.release_durable(1)
 except RuntimeError as e:errs.append(str(e))
t=threading.Thread(target=bad_thread);t.start();t.join();assert errs and m.read(0x4c)==0
m.ack_fail=True;rejects(lambda:d.release_durable(1));n=len(m.writes);assert d.failed;rejects(lambda:d.advance(inp));rejects(lambda:d.release_durable(1));assert len(m.writes)==n
passed('only owner thread ACKs; uncertain release is sticky and never retried')
plan=memory_plan(config,'CmaTotal: 131072 kB\nCmaFree: 3972 kB\nMemAvailable: 731172 kB\n');assert plan['slots']==64 and plan['minimum_period_s']==0 and plan['ddr_bytes']==12058624
v=Clock();w=RunWindow(config,v.clock,v.sleep);w.begin()
for i in range(100):assert w.admit();v.t+=.01
assert not v.sleeps
v.t=59.998;assert not w.admit_when_ready(lambda:None,lambda:False);assert w.starts==100 and w.stop_reason=='DURATION_REACHED'
passed('no capacity-derived pacing; virtual deadline stops while credits unavailable; memory budget independent of60s steps')
# Fresh CPU runtime exercises actual orchestration, bridge checks, worker, batches,
# release, tail flush, and all saved payloads through >2 complete64slot wraps.
fixture=T/'fixture';fixture.mkdir();shutil.copy2(BASE/'initial_state.bin',fixture/'initial_state.bin')
virtual=Clock();disk_stalls=[];real_sync=os.fsync
def mapped(self,frame):
 rt=next(iter(live_board._RETAINED.values()));return np.frombuffer(raw_records[rt.mm.read(0x14)][128:3012],dtype='<f4').copy()
def stall_once(fd):
 if threading.current_thread().name=='line11-batch-save' and not disk_stalls:disk_stalls.append(True);time.sleep(.35)
 real_sync(fd)
def no_network(*a,**kw):raise AssertionError('CPU test must not contact network')
with patch('offline_check.verify',return_value={'evidence':'CPU_FIXTURE_ONLY'}),patch('direct_input.DirectAreaInput.render',mapped),patch('batch_records.os.fsync',stall_once):
 out=live_board.execute(fixture,T/'producer',config,authorized=True,boot_id='00000000-0000-0000-0000-000000000001',runtime_factory=Runtime,send=no_network,upload_wait=0,window_factory=lambda c:RunWindow(c,virtual.clock,virtual.sleep))
rt=next(iter(live_board._RETAINED.values()));finish=json.loads((out/'FINISH.json').read_text());n=finish['completed_steps']
assert 129<=n<=200 and finish['status']=='ALL_STEPS_SAVED_CAMERA_CLOSE_PENDING',finish.get('error')
assert rt.video.frames==n and rt.video.closed and rt.mm.read(0x4c)==n and rt.mm.read(0x50)==0
assert rt.owner['ram_records'].queue.maxsize==2 and not rt.owner['ram_records'].thread.is_alive()
assert rt.owner['record_worker'].queue.maxsize==32 and rt.owner['ram_records'].durable_prefix()==n
assert all(x%16==0 for x in rt.mm.acks[:-1]) and rt.mm.acks[-1]==n
# All persisted packets are decoded, associated with prepared inputs, and compared
# against old independently accepted expected-feedback oracle outputs.
ram_records.CURRENT=rt.owner['ram_records'];store=Store(T/'receiver',config);state_words=0
for k in range(n):
 raw=load_packet(out,k);m,_,r=unpack(raw,config);assert r.input_bits==raw_records[k][128:3012] and r.state_bits==raw_records[k][4096:186772]
 first=(k//3)*3;expected=(RECORDS/'audit'/('%06d_expected.bin'%first)).read_bytes();assert r.state_bits==expected[(k-first)*182676:(k-first+1)*182676]
 if k==0:
  damaged=bytearray(raw);damaged[-10000]^=1;rejects(lambda:store.accept(bytes(damaged)))
  rejects(lambda:store.accept(load_packet(out,1)))
  receipt=store.accept(raw);assert store.accept(raw)['duplicate'] and len(store.meta)==1
 else:store.accept(raw)
 state_words+=45669
store.finish(finish);store.record_camera_close(json.loads((out/'CAMERA_CLOSE.json').read_text()))
assert len(Store(T/'receiver',config).meta)==n
assert all(p['minimum_period_s']==0 for p in [finish['duration']])
passed('virtual60s replay with slow fsync: %d records across64slot ring; tail durably ACKed; all %d state words equal saved oracle'%(n,state_words))
passed('receiver duplicate/reorder/corruption protections and reopening preserve every input-state pair; no neural recomputation')
rejects(lambda:live_board.execute(None,None,{},authorized=False))
passed('no operator authorization rejects before hardware construction')
result=dict(status='PASS_CPU_ASYNC_WRITER_RING_REPLAY_ONLY',checks=checks,fixture_steps=n,state_words_checked=state_words,independent_neural_recompute=False,fixture='R3 saved inputs and expected state replay; only ring headers changed',virtual_seconds=virtual.t,board_operations=0,ring_slots=64,queue_capacity=32,ddr_bytes=64*STRIDE,memory_plan=plan,output=str(out),slow_fsync_injected_seconds=.35,real_board_timing=False)
(T/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8');(P/'evidence/latest_cpu.txt').write_text(str(T),encoding='utf-8');print('RESULT',T)

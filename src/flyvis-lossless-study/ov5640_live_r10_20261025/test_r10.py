"""Focused CPU tests: no board, PYNQ, GPU or EDA."""
import json,sys,struct,types,time
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'bundle'))
from camera_memory import CameraMemory
from ddr_control import DdrControl,N,NE,VERSION,STRIDE
checks=[]
def reject(fn):
 try:fn()
 except (RuntimeError,ValueError,OSError):return
 raise AssertionError('expected rejection')
class Memory:
 def init__(self):self.calls=[];self.fail=False
 def allocate(self,*args,**kwargs):
  if self.fail:raise OSError('injected allocation failure')
  self.calls.append((args,dict(kwargs)));return kwargs.get('pointer',77)
class Device:
 def init__(self):self.lookups=0;self.memory=Memory()
 @property
 def default_memory(self):self.lookups+=1;return self.memory
active=Device()
def allocate(*args,target=None,**kwargs):
 return (active.default_memory if target is None else target).allocate(*args,**kwargs)
# Exact reviewed vendor implementation from the accepted R9 source evidence.
e=json.loads((P.parent/'ov5640_live_r9_analysis_20261025/VIDEO_DRIVER_EXCERPTS.json').read_text())
def find_getframe(x):
 if isinstance(x,dict):
  if x.get('name')=='getframe':return x.get('source')
  for v in x.values():
   r=find_getframe(v)
   if r:return r
 if isinstance(x,list):
  for v in x:
   r=find_getframe(v)
   if r:return r
source=find_getframe(e)
assert source and 'self._cache.pop()' in source
import textwrap
scope=dict(allocate=allocate,np=np)
exec(textwrap.dedent(source),scope)
class Cache:
 def init__(self):self._cache=[];self._mode=types.SimpleNamespace(shape=(48,80,3));self._cacheable=0
 getframe=scope['getframe']
def channel():return types.SimpleNamespace(_cache=Cache(),_mmio=types.SimpleNamespace(device=active))
a=channel();original_global=scope['allocate'];fix=CameraMemory(a)
for k in range(32):
 if k%2:a._cache._cache.append(k)
 assert a._cache.getframe()==(k if k%2 else 77)
assert active.lookups==1 and fix.calls==32 and scope['allocate'] is original_global
assert all(v[1]['cache'] is a._cache and v[1]['cacheable']==0 and v[1]['shape']==(48,80,3) for v in active.memory.calls)
b=channel();b._cache.getframe();assert active.lookups==2
reject(lambda:CameraMemory(a));a._cache._cache.append(123);fix.close();reject(a._cache.getframe);assert a._cache._cache==[123]
c=channel();f=CameraMemory(c);old=c._cache;old._cache.append(3);c._cache=Cache();reject(old.getframe);assert old._cache==[3]
c=channel();f=CameraMemory(c);c._mmio.device=Device();reject(c._cache.getframe)
c=channel();f=CameraMemory(c);active.memory.fail=True;reject(c._cache.getframe);active.memory.fail=False;reject(c._cache.getframe);assert f.failed
checks.append('exact vendor getframe: one memory lookup, cache/uncached branches, no global mutation, close/stale/failure stops')
# MMIO byte API emulates the public PYNQ write_mm loop exactly.
class MMIO:
 def init__(self,short=False,fail=False):self.words=[];self.staged=0;self.short=short;self.fail=fail
 def read(self,a):return {0x30:N,0x34:NE,0x38:VERSION,0x3c:STRIDE,0x18:self.staged}.get(a,0)
 def write(self,a,data):
  if isinstance(data,bytes):
   buf=np.frombuffer(data,np.uint32)
   for i in range(len(buf)):
    if i==13 and self.fail:raise OSError('injected partial upload')
    if i==720 and self.short:return
    self.write(a+4*i,int(buf[i]))
  else:
   self.words.append((a,data))
   if 0x400<=a<=0xf40:self.staged+=1
root=P.parent/'ov5640_live_r9_board_20261025/pc/records'
files=sorted(root.rglob('*.packet'));assert len(files)==32
sys.path.insert(0,str(P/'pc'))
from live_protocol import unpack
cfg=json.loads((P.parent/'ov5640_live_r9_board_20261025/pc/session.json').read_text())
for file in files:
 _,_,record=unpack(file.read_bytes(),cfg)
 x,y=MMIO(),MMIO();DdrControl(x).write_inputs(record.input_bits);DdrControl(y,True).write_inputs(record.input_bits)
 assert x.words==y.words and len(y.words)==721
 assert [a for a,v in y.words]==list(range(0x400,0xf44,4))
for kwargs in ({'short':True},{'fail':True}):
 mm=MMIO(**kwargs);d=DdrControl(mm,True);d.session=(0x100000,0x800000,32,1,0)
 reject(lambda:d.advance(record.input_bits));assert d.failed and not any(a==0 for a,v in mm.words)
 before=list(mm.words);reject(lambda:d.advance(record.input_bits));assert mm.words==before
mm=MMIO();d=DdrControl(mm,True);reject(lambda:d.advance(b'x'));assert not mm.words
checks.append('32 physical R9 input vectors: all 23072 ordered stores match; short/exception uploads never STEP or retry')
# Official startup creates the frame cache in start(), before target binding.
from official_bridge import start_official
order=[]
class Sensor:
 def init__(self,*a):pass
 def init(self):order.append('sensor_init')
 def set_outsize(self,*a):order.append('outsize')
class Video:
 def configure(self,*a):order.append('configure')
 def start(self):self.cache_ready=True;order.append('start')
v=Video();ol=types.SimpleNamespace(ip_dict={'cam_iic':{}},video=types.SimpleNamespace(video_in=v))
def hook(video):
 assert video is v and video.cache_ready;order.append('bind')
start_official(ol,lambda x:x,Sensor,lambda *a:a,bind_cache=hook)
assert order==['sensor_init','outsize','configure','start','bind']
checks.append('memory binding occurs after official start creates cache and before first readframe')
r=dict(status='PASS_R10_FOCUSED_CPU_ONLY',checks=checks,board_operations=0,ARM_performance_measured=False)
(P/'evidence/FOCUSED_RESULT.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))

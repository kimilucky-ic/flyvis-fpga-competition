"""Explicit CPU fixture replay. Never a hardware backend or fallback."""
import json
from pathlib import Path
import struct
import sys
from types import SimpleNamespace

from ddr_control import N,NE,VERSION,STRIDE
from ddr_acceptance import AcceptanceSession

class Buffer:
    def init__(self,size,base=0x02000000):
        self.nbytes=size;self.physical_address=base;self.ndim=1;self.dtype=SimpleNamespace(itemsize=1)
        self.flags=SimpleNamespace(c_contiguous=True,writeable=True);self.coherent=False
        self.cpu=bytearray(size);self.ddr=bytearray(size);self.events=[];self.invalidate_error=False;self.skip_invalidate=False
        self.free_calls=0
    def fill(self,value):
        if not self.flags.writeable:raise RuntimeError('CPU write after PL ownership')
        self.events.append('fill');self.cpu[:]=bytes([value])*self.nbytes
    def flush(self):
        if not self.flags.writeable:raise RuntimeError('Dirty writeback after PL ownership')
        self.events.append('flush');self.ddr[:]=self.cpu
    def invalidate(self):raise RuntimeError('Use one committed slot, not the entire live buffer')
    def __getitem__(self,key):return View(self,key.start,key.stop)
    def barrier(self):self.events.append('dsb')
    def freebuffer(self):self.free_calls+=1;self.events.append('freebuffer')

class View:
    def init__(self,root,start,end):self.root=root;self.start=start;self.end=end
    def invalidate(self):
        b=self.root;b.events.append(('invalidate',self.start,self.end))
        if b.invalidate_error:raise OSError('Injected cache failure')
        if not b.skip_invalidate:b.cpu[self.start:self.end]=b.ddr[self.start:self.end]
    def tobytes(self,order):self.root.events.append(('copy',self.start,self.end));return bytes(self.root.cpu[self.start:self.end])

class MMIO:
    is_hardware=False
    def init__(self,buffer,records):
        self.buffer=buffer;self.records=records;self.writes=[];self.hang=False;self.wrong_cycles=False;self.staged=[]
        self.reg={0x30:N,0x34:NE,0x38:VERSION,0x3c:STRIDE,0x10:0,0x14:0,0x18:0,0x24:0}
    def read(self,a):return self.reg.get(a,0)
    def write(self,a,v):
        self.writes.append((a,v))
        if a>=0x400:
            if a!=0x400+self.reg[0x18]*4:raise RuntimeError('Fake ordered input')
            self.staged.append(v);self.reg[0x18]+=1;return
        if a:self.reg[a]=v;return
        if v==2:self.reg[0x10]=2
        elif v==4:
            if self.reg[4]!=self.buffer.physical_address or self.reg[8]!=self.reg[4]+self.buffer.nbytes:raise RuntimeError('Not allocator-returned physical range')
            self.reg[0x10]|=4
        elif v==1:
            if self.hang:self.reg[0x10]|=1;return
            i=self.reg[0x14];raw=self.records[i*STRIDE:(i+1)*STRIDE]
            if struct.pack('<721I',*self.staged)!=raw[128:128+2884]:raise RuntimeError('Actual complete input differs')
            self.buffer.ddr[i*STRIDE:(i+1)*STRIDE]=raw;self.buffer.events.append(('STEP_COMMIT',i))
            self.reg[0x14]+=1;self.reg[0x18]=0;self.staged=[];self.reg[0x10]|=32
            if self.reg[0x14]==self.reg[12]:self.reg[0x10]|=8
        elif v==8:
            seq=self.reg[0x14];cycles=struct.unpack_from('<I',self.records,(seq-1)*STRIDE+32)[0]+int(self.wrong_cycles)
            self.reg.update({0x80:seq,0x84:self.reg[4]+(seq-1)*STRIDE,0x88:seq-1,0x8c:cycles,
                0x90:seq,0x94:self.reg[0x2c],0x98:0,0x9c:N,0xa0:NE})
        else:raise RuntimeError('Unknown command')

class Dma:
 def init__(self,mode='ok'):self.mode=mode;self.w=[];self.started=False;self.polls=0
 def read(self,a):
  if a!=0x34:return 0
  if not self.started:return 1
  self.polls+=1
  if self.mode=='error':return 0x1011
  if self.mode=='stuck':return 0x1000
  return 0x1000 if self.polls<3 else 0x1001
 def write(self,a,v):
  self.w.append((a,v))
  if a==0xa0:self.started=True;self.polls=0
  if a==0x34 and v==0x1000:self.started=False
class CameraBus:
 def init__(self):self.run=0;self.fault=0;self.w=[]
 def read(self,a):return (self.fault|(6 if self.run else 0)) if a==8 else self.run
 def write(self,a,v):self.w.append((a,v));self.run=v

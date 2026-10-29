import sys,json,unittest
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'ov5640_runtime_20261023'))
from capture_binding import CapturePool
from bounded_io import Iic,OneFrameVdma,CameraControl
class Bus:
 def init__(self,mode='ok'):self.mode=mode;self.sr=0xc0;self.irq=0;self.w=[];self.rx=0x56;self.reading=False
 def read(self,a):
  if a==0x20:return self.irq|(2 if self.mode=='nack' else 1 if self.mode=='arb' else 0)
  if a==0x104:return 0xc4 if self.mode=='busy' else self.sr
  if a==0x10c:self.sr|=0x40;return self.rx
  return 0
 def write(self,a,v):
  self.w.append((a,v))
  if a==0x20:self.irq^=v
  if a==0x108:
   if v&0x100 and not v&0x200:self.sr|=4;self.reading=bool(v&1)
   if v&0x200 and self.mode!='stuck':
    self.sr=0x80 if self.reading else 0xc0;self.irq|=0x10
    if self.reading:self.irq|=2
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
class Tests(unittest.TestCase):
 def test_iic_protocol(self):
  b=Bus();d=Iic(b,max_polls=10);self.assertEqual(d.read16(0x300a),0x56);d.write16(0x3008,0x82)
  self.assertEqual([v for a,v in b.w if a==0x108],[0x178,0x30,0x20a,0x179,0x201,0x178,0x30,8,0x282])
 def test_iic_fault_bounds(self):
  for mode in ('busy','stuck','nack','arb'):
   b=Bus(mode);d=Iic(b,max_polls=7)
   with self.assertRaises((RuntimeError,TimeoutError)):d.write16(0x3008,0x82)
   n=len(b.w)
   with self.assertRaises(RuntimeError):d.read16(0x300a)
   self.assertEqual(n,len(b.w));self.assertFalse(any(a==0x40 for a,v in b.w))
 def test_deadline(self):
  count=[0]
  def clock():count[0]+=.1;return count[0]
  d=Iic(Bus('busy'),timeout=.2,clock=clock,max_polls=100)
  with self.assertRaises(TimeoutError):d.read16(0x300a)
  self.assertLess(count[0],1)
 def setup_dma(self,mode='ok'):
  p=CapturePool(921600);b=Dma(mode);copied=[];addresses=[0x100000,0x200000,0x300000]
  def copy(a,n):self.assertGreaterEqual(b.polls,3);copied.append(a);return bytes(n)
  d=OneFrameVdma(b,p,addresses,[(0x100000,0x400000)],[(0x10000000,0x16000000)],copy,CameraControl(CameraBus()),max_polls=8)
  return p,b,copied,d
 def test_dma_halt_before_copy_and_held_excluded(self):
  p,b,c,d=self.setup_dma();d.capture(0,0);held=p.acquire_latest()[0];d.capture(1,1)
  self.assertEqual(c,[0x100000,0x200000]);self.assertEqual(p.states[held[0]],'HELD')
  self.assertEqual([v for a,v in b.w if a==0x30],[0x10011]*2)
  self.assertEqual(b.w[8],(0xa0,480))
 def test_dma_error_timeout_no_copy(self):
  for mode in ('stuck','error'):
   p,b,c,d=self.setup_dma(mode)
   with self.assertRaises((TimeoutError,RuntimeError)):d.capture(0,0)
   self.assertEqual(c,[]);self.assertIn('WRITING',p.states);n=len(b.w)
   with self.assertRaises(RuntimeError):d.capture(1,1)
   self.assertEqual(n,len(b.w))
 def test_video_overflow_retains_token_and_no_retry(self):
  p,b,c,d=self.setup_dma();bus=d.camera.io
  oldread=b.read
  def read(a):
   if b.started:bus.fault=1
   return oldread(a)
  b.read=read
  with self.assertRaisesRegex(RuntimeError,'overflow'):d.capture(1,1)
  self.assertEqual(c,[]);self.assertIn('WRITING',p.states)
  self.assertEqual(bus.w,[(0,1)]) # no automatic stop/reset on failure
  with self.assertRaises(RuntimeError):d.capture(2,2)
 def test_stop_before_copy_and_stale_fault_refused(self):
  p,b,c,d=self.setup_dma();bus=d.camera.io;copy=d.copy
  def checkcopy(a,n):
   self.assertEqual(bus.run,0);return copy(a,n)
  d.copy=checkcopy;d.capture(0,0);self.assertEqual(bus.w,[(0,1),(0,0)])
  bus.fault=1;n=len(b.w)
  with self.assertRaises(RuntimeError):d.capture(1,1)
  self.assertEqual(len(b.w),n)
 def test_late_fault_during_copy_not_published(self):
  p,b,c,d=self.setup_dma()
  def badcopy(a,n):d.camera.io.fault=1;return bytes(n)
  d.copy=badcopy
  with self.assertRaises(RuntimeError):d.capture(0,0)
  self.assertNotIn('READY',p.states);self.assertIn('WRITING',p.states)
 def test_overlap_refused_before_write(self):
  p=CapturePool(921600);b=Dma()
  with self.assertRaises(ValueError):OneFrameVdma(b,p,[0x100000]*3,[(0x100000,0x400000)],[],lambda a,n:bytes(n),CameraControl(CameraBus()))
  self.assertEqual(b.w,[])
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 (P/'CPU_RESULT.json').write_text(json.dumps(dict(passed=r.wasSuccessful(),tests=r.testsRun,errors=len(r.errors),failures=len(r.failures),board_result=False),indent=2))
 sys.exit(not r.wasSuccessful())

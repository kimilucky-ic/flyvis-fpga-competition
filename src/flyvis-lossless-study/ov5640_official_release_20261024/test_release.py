"""CPU-only real control/buffer/bridge + explicit fake MMIO/DMA, never PYNQ."""
import json,struct,sys,subprocess,unittest,shutil,zipfile,io,ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
import numpy as np
R=Path(__file__).resolve().parent;B=R/'bundle';sys.path.insert(0,str(B))
import board_run,ddr_memory,capture_binding,operator_entry
from board_runtime import CheckedVideo,clocks
from ddr_control import DdrControl
from ddr_memory import OwnedDdr
from ps_input import PsInput
from snapshot_records import rolling
from verify_result import validate_run,unpack
from offline_check import verify
O=R/('evidence/'+(sys.argv[1] if len(sys.argv)>1 else 'cpu_r1'));O.mkdir(exist_ok=False)
raw=(R.parent/'ov5640_official_flyvis_20261024/baseline/frame_raw.bin').read_bytes()
frame=np.frombuffer(raw,np.uint8).reshape(480,800,3)
inp=PsInput(480,800,'BGR').render(frame).astype('<f4').tobytes();(O/'input.bin').write_bytes(inp)
cmd=[str((B/'reference.exe').resolve()),str(B.resolve()),str((O/'input.bin').resolve()),str((O/'gold.bin').resolve())]
p=subprocess.run(cmd,capture_output=True,timeout=60);(O/'oracle.log').write_bytes(p.stdout+p.stderr);p.check_returncode()
(O/'ORACLE_COMMAND.json').write_text(json.dumps(dict(command=cmd,fixture='CPU oracle, not DUT')))
gold=(O/'gold.bin').read_bytes();assert len(gold)==45669*4

def record(inputs,state):
 h=[0]*32
 for k,v in {0:0x5331314c,1:0x10000,2:0,4:45669,5:1513231,6:2884,7:182676,8:2201418,9:1513231,10:45669,11:188416,12:rolling(inputs),13:rolling(state),14:128,15:4096,16:0x00110003,17:0x3ba3d70a}.items():h[k]=v
 b=bytearray(188416);struct.pack_into('<32I',b,0,*h);b[128:3012]=inputs;b[4096:186772]=state;return bytes(b)

class Buffer(np.ndarray):
 def __new__(cls,size,rt):
  a=np.zeros(size,np.uint8);x=a.view(cls);x.cache=a;x.device=np.zeros_like(a);x.rt=rt;x.physical_address=0x1000000;x.coherent=False;x.frees=0;return x
 def __array_finalize__(self,parent):
  for a in ['cache','device','rt','physical_address','coherent','frees']:
   if hasattr(parent,a):setattr(self,a,getattr(parent,a))
 def flush(self):self.rt.events.append('flush');self.device[:]=self.cache
 def invalidate(self):
  self.rt.events.append('invalidate')
  if self.rt.mode!='stale_cache':self.cache[:]=self.device
 def freebuffer(self):self.frees+=1;self.rt.events.append('free_neural')
class Frame(np.ndarray):
 def __new__(cls,rt):
  a=np.array(frame,copy=True)
  if rt.mode=='geometry':a=a[:400].copy()
  x=a.view(cls);x.rt=rt;x.physical_address=0x2000000 if rt.mode!='overlap' else 0x1000000;x.coherent=False;x.freed=False;return x
 def invalidate(self):self.rt.events.append('camera_invalidate')
 def freebuffer(self):self.freed=True;self.fill(255);self.rt.events.append('free_frame')
class Video:
 def init__(self,rt):self.rt=rt;self.frame=Frame(rt)
 def readframe(self):
  self.rt.events.append('readframe')
  if self.rt.mode=='read_failure':raise RuntimeError('injected read failure')
  return self.frame
 def close(self):
  self.rt.events.append('close_camera')
  if self.rt.mode=='close_failure':raise RuntimeError('injected close failure')
class MMIO:
 def init__(self,rt):
  self.rt=rt;self.reg={0x30:45669,0x34:1513231,0x38:0x00110004,0x3c:188416};self.input=[];self.steps=0
  if rt.mode=='abi':self.reg[0x30]=45668
 def read(self,a):return self.reg.get(a,0)
 def write(self,a,v):
  if a>=0x400:self.input.append(v);self.reg[0x18]=len(self.input);return
  if a!=0:self.reg[a]=v;return
  if v==2:self.reg[0x10]=2
  elif v==4:self.reg[0x10]=6
  elif v==1:
   d=self.rt.out/'capture/bound/000000'
   assert (d/'PREPARED.json').exists() and (d/'source_frame.bin').read_bytes()==raw
   bits=struct.pack('<721I',*self.input);assert bits==inp and (d/'input.bin').read_bytes()==bits
   self.steps+=1;self.rt.events.append('step');state=gold
   if self.rt.mode=='step_failure':raise RuntimeError('injected uncertain STEP')
   if self.rt.mode=='last_bit':state=gold[:-4]+struct.pack('<I',struct.unpack('<I',gold[-4:])[0]^1)
   if self.rt.mode=='input_mismatch':bits=b'\0'*2884
   data=record(bits,state);self.rt.buf.device[:]=np.frombuffer(data,np.uint8)
   self.reg.update({0x10:46,0x14:1,0x18:0})
  elif v==8:
   self.reg.update({0x80:1,0x84:self.reg[4],0x88:0,0x8c:2201418,0x90:1,0x94:self.reg[0x2c],0x98:0,0x9c:45669,0xa0:1513231})
   if self.rt.mode=='sequence':self.reg[0x80]=2
class Runtime:
 evidence='CPU_MOCK_ONLY'
 def init__(self,root,out,mode='good'):self.root=root;self.out=out;self.mode=mode;self.owner={};self.events=[];self.mm=MMIO(self)
 def prepare(self):self.events.append('prepare')
 def load(self):self.events.append('load')
 def inspect(self):
  self.events.append('inspect')
  if self.mode=='clock':raise RuntimeError('clock mismatch')
  return clocks(dict(IO_PLL_CTRL=0x1e000,PLL_STATUS=4,FPGA0_CLK_CTRL=0x200500,FPGA1_CLK_CTRL=0x200500))
 def control(self):return DdrControl(self.mm)
 def barrier(self):self.events.append('barrier')
 def allocate(self,shape,dtype,cacheable):self.buf=Buffer(shape[0],self);return self.buf
 def memory(self):
  m=OwnedDdr(self.allocate,self.barrier,1);self.owner['memory']=m;return m
 def start_camera(self,memory):
  self.events.append('camera_start')
  if self.mode=='init_failure':raise RuntimeError('injected sensor init failure')
  self.video=Video(self);return CheckedVideo(self.video,memory,self.barrier,self.out)

class Tests(unittest.TestCase):
 def setUp(self):board_run._RETAINED.clear();ddr_memory._PINNED.clear();self.rt=None
 def execute(self,mode='good',name=None):
  dest=O/(name or self._testMethodName);dest.mkdir()
  def factory(root,out):self.rt=Runtime(root,out,mode);return self.rt
  return board_run.execute(B,dest,authorized=True,runtime_factory=factory,boot_id='cpu-only')
 def test_good_full(self):
  out=self.execute();a=validate_run(out,O/'audit_good',B);self.assertEqual(a['state_words_compared'],45669)
  self.assertEqual((out/'capture/bound/000000/source_frame.bin').read_bytes(),raw)
  self.assertTrue(self.rt.video.frame.freed);self.assertTrue(np.all(self.rt.video.frame==255))
  self.assertEqual(self.rt.mm.steps,1);self.assertEqual(self.rt.buf.frees,0)
  self.assertEqual(self.rt.events.count('load'),1);self.assertEqual(self.rt.events.count('close_camera'),1)
  self.assertIn('invalidate',self.rt.events)
  archive=Path(str(out)+'_RESULT.zip');ex=unpack(archive,O/'good_zip');validate_run(ex,O/'audit_zip',B)
  (O/'good_run.txt').write_text(str(out.resolve()))
  with self.assertRaises(RuntimeError):board_run.execute(B,O/'repeat',authorized=True,runtime_factory=lambda *a:None)
 def test_failures_stop(self):
  for mode,steps in [('clock',0),('abi',0),('init_failure',0),('read_failure',0),('overlap',0),('geometry',0),('step_failure',1),('stale_cache',1),('input_mismatch',1),('sequence',1),('close_failure',1)]:
   with self.subTest(mode=mode):
    board_run._RETAINED.clear();ddr_memory._PINNED.clear()
    with self.assertRaises((RuntimeError,ValueError)):self.execute(mode,mode)
    self.assertEqual(self.rt.mm.steps,steps)
    self.assertTrue((self.rt.out/'IN_DOUBT.json').exists());self.assertTrue(Path(str(self.rt.out)+'_RESULT.zip').exists())
    if hasattr(self.rt,'buf'):self.assertEqual(self.rt.buf.frees,0)
    if mode!='close_failure':self.assertNotIn('close_camera',self.rt.events)
    with self.assertRaises(ValueError):validate_run(self.rt.out,O/('bad_audit_'+mode),B)
 def test_last_bit_rejected(self):
  out=self.execute('last_bit')
  with self.assertRaisesRegex(ValueError,'all-state mismatch'):validate_run(out,O/'audit_last_bit',B)
  c=json.loads((O/'audit_last_bit/COMPARE.json').read_text());self.assertEqual(c['mismatch_words'],1)
  self.assertEqual(c['steps'][0]['first_mismatches'][0]['global_id'],45668)
 def test_disk_before_step(self):
  old=capture_binding.save_new
  def fail(p,d):
   if Path(p).name=='input.bin':raise OSError('injected disk failure')
   return old(p,d)
  with patch('capture_binding.save_new',side_effect=fail):
   with self.assertRaises(OSError):self.execute()
  self.assertEqual(self.rt.mm.steps,0);self.assertNotIn('close_camera',self.rt.events)
 def test_actual_pynq_runtime_with_fake_devices(self):
  import board_runtime
  from board_runtime import PynqRuntime
  from verify_result import validate_preflight
  holder={};modules={}
  baseline=R.parent/'ov5640_official_flyvis_20261024/baseline'
  class Iic:
   bindto=['xilinx.com:ip:axi_iic:2.0']
   def init__(self,d):holder['rt'].events.append('official_iic')
  class Sensor:
   def init__(self,*a):pass
   def init(self):holder['rt'].events.append('official_init')
   def set_outsize(self,*a):assert a==(800,480,1800,1000)
  modules['pynq.lib.iic']=NS(__file__=str(baseline/'pynq_lib_iic.py'),AxiIIC=Iic)
  modules['pynq.lib.ov5640.ov5640']=NS(__file__=str(baseline/'pynq_lib_ov5640_ov5640.py'),OV5640=Sensor)
  modules['pynq.lib.video2lcd']=NS(__file__=str(baseline/'pynq_lib_video2lcd.py'),VideoMode=lambda *a:a)
  def overlay(path,download):
   assert download is False and Path(path).name=='flyvis_official.bit'
   rt=holder['rt'];v=Video(rt);holder['video']=v
   v.configure=lambda mode:rt.events.append(('configure',mode))
   v.start=lambda:rt.events.append('official_video_start')
   return NS(download=lambda:rt.events.append('download'),ip_dict={'cam_iic':{}},video=NS(video_in=v))
  registers={0xf8000108:0x1e000,0xf800010c:4,0xf8000170:0x200500,0xf8000180:0x200500,0xf8000240:0,0xf8008000:0,0xf8008014:0,0xf8009000:0,0xf8009014:0}
  def mmio(base,length):
   if base==0x43c40000:return holder['rt'].mm
   return NS(read=lambda off:registers[base+off])
  modules['pynq']=NS(__version__='2.7.0',Overlay=overlay,MMIO=mmio,Clocks=NS(fclk0_mhz=150))
  def factory(root,out):
   holder['rt']=Runtime(root,out);x=PynqRuntime(root,out);x.evidence='CPU_MOCK_ONLY';holder['api']=x;return x
  def native(*a,**k):return holder['rt'].allocate,holder['rt'].barrier
  oldread=Path.read_bytes;oldimport=board_runtime.importlib.import_module
  def read(p):return b'xlnx,zynq-7000' if str(p).replace(chr(92),'/')=='/proc/device-tree/compatible' else oldread(p)
  with patch('board_runtime.platform.machine',return_value='armv7l'),patch('board_runtime.importlib.import_module',side_effect=lambda n:modules[n] if n in modules else oldimport(n)),patch('board_runtime.pynq_allocator_and_barrier',side_effect=native),patch.object(Path,'read_bytes',read):
   out=board_run.execute(B,O/'actual_runtime_fake',authorized=True,runtime_factory=factory,boot_id='cpu-only')
  validate_preflight(out)
  a=validate_run(out,O/'audit_actual_runtime_fake',B);self.assertEqual(a['status'],'PASS_CPU_MOCK_ALL_45669_STATES')
  self.assertEqual(holder['rt'].events.count('download'),1)
  self.assertEqual(holder['rt'].events.count('official_init'),1)
  self.assertEqual(holder['rt'].events.count('official_video_start'),1)
  self.assertTrue(holder['video'].frame.freed)
  self.assertEqual(json.loads((out/'CLOCK.json').read_text())['pynq_reported_MHz'],150)
 def test_not_authorized(self):
  with self.assertRaises(RuntimeError):board_run.execute(B,O/'never',runtime_factory=lambda *a:self.fail('factory must not run'))
 def test_clock_negative(self):
  r=dict(IO_PLL_CTRL=0x1e000,PLL_STATUS=4,FPGA0_CLK_CTRL=0x200500,FPGA1_CLK_CTRL=0x200500)
  for k,v in [('PLL_STATUS',0),('IO_PLL_CTRL',0x1e010),('FPGA1_CLK_CTRL',0x200300),('FPGA0_CLK_CTRL',0x200510)]:
   with self.assertRaises(RuntimeError):clocks(dict(r,**{k:v}))
 def test_entry_cancel_and_reservation(self):
  base=O/'entry';boot='00000000-1111-2222-3333-444444444444'
  with patch('operator_entry.platform.machine',return_value='armv7l'):
   operator_entry.run(B,ask=lambda _: '取消',base=base,boot=boot,execute_fn=lambda *a,**k:self.fail('cancel ran'))
   self.assertFalse(list(base.glob('ATTEMPT*')))
   def fail(*args,**kwargs):
    self.assertEqual(len(list(base.glob('ATTEMPT*'))),1);raise RuntimeError('fake failure')
   operator_entry.run(B,ask=lambda _: '运行官方完整网络',base=base,boot=boot,execute_fn=fail)
   with self.assertRaises(RuntimeError):operator_entry.run(B,ask=lambda _:self.fail('repeat asked'),base=base,boot=boot,execute_fn=fail)
 def test_bad_bundle(self):
  dst=O/'bad_bundle';shutil.copytree(B,dst)
  p=dst/'flyvis_official.hwh';p.write_bytes(p.read_bytes()+b'changed')
  with self.assertRaises(ValueError):verify(dst)
 def test_unsafe_zip(self):
  z=O/'unsafe.zip'
  with zipfile.ZipFile(z,'w') as f:f.writestr('../escape','x')
  with self.assertRaises(ValueError):unpack(z,O/'unsafe_extract')
  self.assertFalse((O/'escape').exists())
 def test_python38(self):
  for p in B.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'),feature_version=(3,8))

result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
(O/'RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_ONLY' if result.wasSuccessful() else 'FAIL',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),negative_runtime_cases=11,source_frame_sha256=__import__('hashlib').sha256(raw).hexdigest(),state_words_compared=45669,oracle_fixture=True,independent_RTL_math_test=False,board_operations=0,native_driver_executed=False),indent=2)+'\n')
sys.exit(not result.wasSuccessful())

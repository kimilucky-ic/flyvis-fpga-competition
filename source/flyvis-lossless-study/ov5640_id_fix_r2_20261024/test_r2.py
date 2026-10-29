import unittest,sys,json,io,tempfile,zipfile,importlib.util,contextlib,ast,hashlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import id_diag as d
from bounded_io import Iic
P=Path(__file__).resolve().parent;OLD=P.parent/'ov5640_id_diag_20261024';B=P.parent/'ov5640_release_20261023/bundle'
class Bus21:
 def init__(self,mode='ok'):
  self.mode=mode;self.sr=0xc0;self.irq=0;self.w=[];self.ops=[];self.pending=False;self.reading=False;self.reg=0;self.now=0;self.received=False;self.rx_ticks=0
 def clock(self):self.now+=.0001;return self.now
 def read(self,a):
  self.ops.append(('r',a))
  if self.mode=='exception' and self.received:raise OSError('injected after count')
  if a==0x20:return self.irq
  if a==0x104:
   if self.mode=='delayed_rx' and self.received and self.sr&4:
    self.rx_ticks+=1
    if self.rx_ticks==4:self.sr=0x80;self.irq|=0x12
   return 0xc4 if self.mode=='initial_busy' else self.sr
  if a==0x10c:
   self.sr|=0x40
   return 0 if self.mode=='bad_id' else 0x40 if self.reg==0x300b else 0x56
  return 0
 def write(self,a,v):
  self.ops.append(('w',a,v));self.w.append((a,v))
  if a==0x20:self.irq^=v
  if a!=0x108:return
  if v==0x178:self.reg=0;self.reading=False;self.sr|=4
  elif v==0x179:
   self.pending=True;self.reading=True;self.sr=0xc0 # no BB until count
  elif self.reading:
   assert self.pending and v==0x201
   self.pending=False;self.received=True;self.rx_ticks=0
   if self.mode=='delayed_rx':self.sr=0xc4;return
   if self.mode=='no_rx':self.sr=0xc4;return
   if self.mode=='nack':self.sr=0xc0;self.irq|=0x12;return
   if self.mode=='arb':self.irq|=1;return
   self.sr=0x84 if self.mode=='stop_stuck' else 0x80
   self.irq|=0x12 # immediate completion, final NACK expected alongside RX
  else:
   self.reg=(self.reg<<8)|(v&255)
   if v&0x200:self.sr=0xc0;self.irq|=0x10
class Tests(unittest.TestCase):
 def test_original_deadlocks_new_passes(self):
  spec=importlib.util.spec_from_file_location('old_transport',OLD/'bounded_io.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  old=Bus21();transport=mod.Iic(old,clock=old.clock)
  with self.assertRaises(TimeoutError):transport.read16(0x300b)
  self.assertTrue(old.pending);self.assertNotIn((0x108,0x201),old.w)
  b=Bus21();r=d.read_id(b,clock=b.clock)
  self.assertEqual(r['status'],'PASS_OPERATOR_REPORTED_OV5640_ID_ONLY');self.assertEqual(r['sensor_id'],0x5640)
 def test_exact_fifo_words_and_no_config(self):
  b=Bus21();r=d.read_id(b,clock=b.clock)
  self.assertEqual([v for a,v in b.w if a==0x108],[0x178,0x30,0x20b,0x179,0x201,0x178,0x30,0x20a,0x179,0x201])
  self.assertTrue(all(a in (0x20,0x100,0x108,0x120) for a,v in b.w))
  self.assertEqual(r['sensor_configuration_writes'],0)
 def test_immediate_completion_does_not_need_busy_edge(self):
  b=Bus21();r=d.read_id(b,clock=b.clock)
  self.assertEqual(r['sensor_id'],0x5640);self.assertFalse(b.pending)
 def test_delayed_rx_after_count(self):
  b=Bus21('delayed_rx');r=d.read_id(b,clock=b.clock);self.assertEqual(r['status'],'PASS_OPERATOR_REPORTED_OV5640_ID_ONLY');self.assertEqual(r['sensor_id'],0x5640)
 def test_read_nack_without_data(self):
  b=Bus21('nack');r=d.read_id(b,clock=b.clock)
  self.assertIn('NACK without received',r['error']);self.assertEqual(r['sensor_register'],'0x300b');self.assertNotIn(('r',0x10c),b.ops)
 def test_arb(self):
  b=Bus21('arb');r=d.read_id(b,clock=b.clock);self.assertIn('arbitration',r['error'])
 def test_rx_timeout(self):
  b=Bus21('no_rx');r=d.read_id(b,clock=b.clock);self.assertIn('TimeoutError',r['error']);self.assertEqual(r['sensor_register'],'0x300b')
 def test_stop_timeout(self):
  b=Bus21('stop_stuck');r=d.read_id(b,clock=b.clock);self.assertIn('TimeoutError',r['error']);self.assertIn(('r',0x10c),b.ops)
 def test_bad_id(self):
  b=Bus21('bad_id');r=d.read_id(b,clock=b.clock);self.assertIn('mismatch',r['error'])
 def test_busy_no_writes(self):
  b=Bus21('initial_busy');r=d.read_id(b,clock=b.clock);self.assertFalse(b.w)
 def test_exception_no_followup_io(self):
  b=Bus21('exception');r=d.read_id(b,clock=b.clock);self.assertIn('injected',r['error']);self.assertEqual(b.ops[-1],('r',0x20))
 def test_failed_transport_blocks_retry(self):
  b=Bus21('nack');x=Iic(b,clock=b.clock)
  with self.assertRaises(RuntimeError):x.read16(0x300b)
  n=len(b.ops)
  with self.assertRaises(RuntimeError):x.read16(0x300b)
  self.assertEqual(len(b.ops),n)
 def test_clock_gate(self):
  good=dict(FPGA0_CLK_CTRL=0x200500,IO_PLL_CTRL=0x1e000,PLL_STATUS=63)
  self.assertAlmostEqual(d.check_clock(good),100,places=5)
  with self.assertRaises(RuntimeError):d.check_clock(dict(good,PLL_STATUS=0))
 def prior(self,base,boot):
  base.mkdir(exist_ok=True)
  (base/('ATTEMPT_'+boot+'.json')).write_text(json.dumps(dict(boot_id=boot,run_id=d.FAILED_RUN)))
  out=base/d.FAILED_RUN;out.mkdir()
  with zipfile.ZipFile(OLD/'operator_cd4dcb60_review/ID_cd4dcb6069e64c36a4ef76372ee1fcb9_RESULT.zip') as z:(out/'RESULT.json').write_bytes(z.read('RESULT.json'))
 def test_reviewed_handoff_preserves_marker(self):
  base=Path(tempfile.mkdtemp(dir=P,prefix='test_handoff_'));self.prior(base,d.FAILED_BOOT)
  before=(base/('ATTEMPT_'+d.FAILED_BOOT+'.json')).read_bytes()
  h=d.reserve(base,d.FAILED_BOOT,'new');self.assertEqual(h['prior_run'],d.FAILED_RUN)
  self.assertEqual((base/('ATTEMPT_'+d.FAILED_BOOT+'.json')).read_bytes(),before)
  with self.assertRaises(FileExistsError):d.reserve(base,d.FAILED_BOOT,'again')
 def test_unknown_prior_or_missing_marker_blocks(self):
  base=Path(tempfile.mkdtemp(dir=P,prefix='test_reject_'))
  with self.assertRaises(RuntimeError):d.validate_handoff(base,d.FAILED_BOOT)
  self.prior(base,'unreviewed-boot')
  with self.assertRaises(RuntimeError):d.validate_handoff(base,'unreviewed-boot')
 def test_prior_capture_blocks_handoff(self):
  base=Path(tempfile.mkdtemp(dir=P,prefix='test_prior_'));self.prior(base,d.FAILED_BOOT)
  f=base/d.FAILED_RUN/'RESULT.json';r=json.loads(f.read_text());r['DDR_allocations']=1;f.write_text(json.dumps(r))
  with self.assertRaises(RuntimeError):d.validate_handoff(base,d.FAILED_BOOT)
 def entry(self,answer,mode='ok',boot='new-boot'):
  temp=Path(tempfile.mkdtemp(dir=P,prefix='test_entry_'));(temp/'boot').write_text(boot)
  if boot==d.FAILED_BOOT:self.prior(temp/'output',boot)
  calls=[];b=Bus21(mode)
  regs={0xf8000000:{0x170:0x200500,0x108:0x1e000,0x10c:63,0x240:0},0x43c40000:{0x30:45669,0x34:1513231,0x38:0x00110004,0x3c:188416},0x41200000:{},0x43000000:{0x34:1}}
  if mode=='abi':regs[0x43c40000][0x30]=1
  class MM:
   def init__(self,a,n):self.a=a;calls.append(('map',a))
   def read(self,o):return regs[self.a].get(o,0)
  class Overlay:
   def init__(self,path,download):calls.append(('prepare',download))
   def download(self):
    calls.append(('load',))
    if mode=='load_fail':raise RuntimeError('load failed')
  fake=SimpleNamespace(__version__='2.7.0',PL=SimpleNamespace(bitfile_name=str(B/'flyvis_ov5640.bit'),timestamp='old'),MMIO=lambda a,n:b if a==0x41600000 else MM(a,n),Overlay=Overlay)
  def path(p):
   if str(p)=='/proc/sys/kernel/random/boot_id':return temp/'boot'
   if str(p)=='/home/xilinx/jupyter_notebooks/LINE11_OV5640_ID_DIAG':return temp/'output'
   return Path(p)
  with patch.object(d,'Path',path),patch.object(d.platform,'machine',return_value='armv7l'),patch.dict(sys.modules,{'pynq':fake}),contextlib.redirect_stdout(io.StringIO()):out=d.run(B,ask=lambda p:answer)
  return out,calls,b
 def test_decline_no_hardware(self):
  out,calls,b=self.entry('取消');self.assertIsNone(out);self.assertFalse(calls);self.assertFalse(b.ops)
 def test_newboot_one_explicit_load(self):
  out,calls,b=self.entry('加载原固件并验证型号');self.assertEqual(calls.count(('load',)),1)
  r=json.loads((out/'RESULT.json').read_text());self.assertEqual(r['result']['status'],'PASS_OPERATOR_REPORTED_OV5640_ID_ONLY');self.assertTrue(Path(str(out)+'_RESULT.zip').exists())
 def test_reviewedboot_one_explicit_load(self):
  out,calls,b=self.entry('加载原固件并验证型号',boot=d.FAILED_BOOT);self.assertEqual(calls.count(('load',)),1)
  r=json.loads((out/'RESULT.json').read_text());self.assertEqual(r['handoff']['prior_run'],d.FAILED_RUN)
 def test_load_failure_no_mmio(self):
  out,calls,b=self.entry('加载原固件并验证型号','load_fail');self.assertFalse(any(c[0]=='map' for c in calls));self.assertFalse(b.ops)
 def test_bad_abi_no_iic(self):
  out,calls,b=self.entry('加载原固件并验证型号','abi');self.assertFalse(b.ops)
 def test_py38_and_originals_preserved(self):
  for f in ('id_diag.py','bounded_io.py'):ast.parse((P/f).read_text(),feature_version=(3,8))
  for f,h in json.loads((P/'BASELINE.json').read_text()).items():self.assertEqual(hashlib.sha256((OLD/f).read_bytes()).hexdigest(),h)
if __name__=='__main__':
 s=io.StringIO();r=unittest.TextTestRunner(stream=s,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 (P/'CPU_TEST.log').write_text(s.getvalue(),encoding='utf-8');(P/'CPU_RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_MOCK_ONLY' if r.wasSuccessful() else 'FAIL',tests=r.testsRun,failures=len(r.failures),errors=len(r.errors),board_operations=0,GPU_operations=0,Vivado_operations=0),indent=2));print(s.getvalue());sys.exit(0 if r.wasSuccessful() else 1)

import sys,json,io,unittest,tempfile,zipfile,hashlib,struct,shutil,contextlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
P=Path(__file__).resolve().parent;B=P/'bundle';OLD=P.parent/'ov5640_release_20261023'
sys.path.insert(0,str(OLD));sys.path.insert(0,str(B))
import board_capture as bc,operator_entry as op,ddr_memory
from sensor_trace import SensorBus
from sensor_init import initialize
from cpu_support import Buffer,MMIO,Dma,CameraBus
from ddr_control import STRIDE
from verify_run import audit
from snapshot_records import rolling
from capture_binding import sha
FIX=OLD/'cpu_tests_999eaf60/42feb0159e/bound/000000'
FRAME=(FIX/'source_frame.bin').read_bytes();RAW=(FIX/'record.bin').read_bytes()
class Sensor:
 def init__(self,bad=False):
  self.sr=0xc0;self.irq=0;self.pointer=0;self.payload=[];self.reading=False;self.regs={0x300b:0 if bad else 0x40,0x300a:0x56,0x4740:0x20};self.config=[]
 def read(self,a):
  if a==0x20:return self.irq
  if a==0x104:return self.sr
  if a==0x10c:self.sr|=0x40;return self.regs.get(self.pointer,0)
  return 0
 def write(self,a,v):
  if a==0x20:self.irq^=v;return
  if a!=0x108:return
  if v==0x178:self.payload=[];self.reading=False;self.sr=0xc4;return
  if v==0x179:self.reading=True;self.sr=0xc0;return
  if self.reading:
   assert v==0x201;self.sr=0x80;self.irq|=0x12;return
  self.payload.append(v&255)
  if v&0x200:
   self.pointer=(self.payload[0]<<8)|self.payload[1]
   if len(self.payload)==3:self.regs[self.pointer]=self.payload[2];self.config.append((self.pointer,self.payload[2]))
   else:assert len(self.payload)==2
   self.sr=0xc0;self.irq|=0x10
class Tests(unittest.TestCase):
 def setup_run(self,mode='ok'):
  tmp=Path(tempfile.mkdtemp(dir=P,prefix='cpu_flow_'));(tmp/'boot').write_text('CPU_FIXTURE_BOOT')
  nb=Buffer(STRIDE);cb=Buffer(3*921600,0x03000000);control=MMIO(nb,RAW);sensor=Sensor(mode=='bad_id');dma=Dma('error' if mode=='dma_error' else 'ok')
  class Cam(CameraBus):
   def write(self,a,v):
    super().write(a,v)
    if v==1:cb.ddr[:len(FRAME)]=FRAME
  cam=Cam();calls=[];allocated=[]
  def allocate(**kwargs):
   buf=nb if not allocated else cb;allocated.append(buf);return buf
  reg={0xf8000000:{0x170:0x200500,0x108:0x1e000,0x10c:63,0x240:0},0xf8008000:{0:1 if mode=='hp_bad' else 0,0x14:3840},0xf8009000:{0:0,0x14:3840}}
  class R:
   def init__(self,a):self.a=a
   def read(self,o):return reg[self.a].get(o,0)
  def mmio(a,n):
   calls.append(('map',a))
   return {0x43c40000:control,0x41600000:sensor,0x43000000:dma,0x41200000:cam}.get(a) or R(a)
  class Overlay:
   def init__(self,*a,**kw):pass
   def download(self):calls.append(('load',))
  fake=SimpleNamespace(__version__='2.7.0',MMIO=mmio,Overlay=Overlay,Clocks=SimpleNamespace(fclk0_mhz=150))
  cond=json.loads((B/'entry_conditions.json').read_text());cond['operator_confirmation']='同意单帧测试'
  original_save=bc.save_json
  def save_cpu(path,value):
   if Path(path).name=='RUN_CONTEXT.json':value=dict(value,evidence='CPU_MOCK_ONLY',fixture_note='All MMIO/native/helper/allocator/camera replaced by explicit CPU fakes')
   original_save(path,value)
  def paths(p):return tmp/'boot' if str(p)=='/proc/sys/kernel/random/boot_id' else Path(p)
  error=None;out=None
  with patch.dict(bc._RETAINED,{},clear=True),patch.object(bc,'Path',paths),patch.object(bc.platform,'machine',return_value='armv7l'),patch.dict(sys.modules,{'pynq':fake}),patch.object(ddr_memory,'pynq_allocator_and_barrier',return_value=(allocate,lambda:None)),patch.object(bc.time,'sleep',lambda _:None),patch.object(bc,'save_json',save_cpu),contextlib.redirect_stdout(io.StringIO()):
   try:out=bc.run(tmp,cond,authorize_load_and_one_step=True)
   except Exception as exc:error=exc;out=next(tmp.glob('LINE11_OV5640_*'))
  return out,error,calls,allocated,control,sensor,nb,cb
 def test_initializer_248writes_and_corrected_reads(self):
  s=Sensor();bus=SensorBus(s);n=initialize(bus.read16,bus.write16,lambda _:None)
  self.assertEqual(n,248);self.assertEqual(len(s.config),248);self.assertEqual(bus.read16(0x3808),2);self.assertEqual(bus.read16(0x3809),128)
  self.assertEqual(bus.report()['configuration_write_attempts'],248)
 def test_full_entry_capture_binding_oracle(self):
  out,e,calls,alloc,control,sensor,nb,cb=self.setup_run()
  self.assertIsNone(e);self.assertEqual(calls.count(('load',)),1);self.assertEqual(len(alloc),2);self.assertEqual(control.read(0x14),1)
  d=out/'bound/000000';self.assertEqual((d/'source_frame.bin').read_bytes(),FRAME);self.assertEqual((d/'input.bin').read_bytes(),(d/'actual_input.bin').read_bytes())
  self.assertEqual(len((d/'actual_state.bin').read_bytes()),182676);self.assertEqual(nb.free_calls+cb.free_calls,0)
  trace=json.loads((out/'SENSOR_TRACE.json').read_text());self.assertEqual(trace['configuration_write_attempts'],248);self.assertFalse(trace['failed'])
  result=audit(str(out)+'_RESULT.zip',out.parent/'audit',B);self.assertEqual(result['mismatch_words'],0);self.assertEqual(result['evidence'],'CPU_MOCK_ONLY')
  (P/'full_flow_acceptance_path.txt').write_text(str(out.parent/'audit/ACCEPTANCE.json'))
 def test_bad_id_stops_before_allocation(self):
  out,e,calls,alloc,control,sensor,nb,cb=self.setup_run('bad_id');self.assertIsNotNone(e);self.assertFalse(alloc);self.assertFalse(sensor.config);self.assertEqual(control.read(0x14),0)
  self.assertEqual(json.loads((out/'IN_DOUBT.json').read_text())['phase'],'SENSOR_INIT');self.assertTrue((out/'SENSOR_TRACE.json').exists())
 def test_hp_gate_stops_sensor(self):
  out,e,calls,alloc,control,sensor,nb,cb=self.setup_run('hp_bad');self.assertIsNotNone(e);self.assertFalse(alloc);self.assertFalse(sensor.config)
  self.assertNotIn(('map',0x41600000),calls)
 def test_dma_error_keeps_buffers_no_step(self):
  out,e,calls,alloc,control,sensor,nb,cb=self.setup_run('dma_error');self.assertIsNotNone(e);self.assertEqual(len(alloc),2);self.assertEqual(control.read(0x14),0);self.assertEqual(nb.free_calls+cb.free_calls,0)
 def test_last_state_corruption_rejected(self):
  tmp=Path(tempfile.mkdtemp(dir=P,prefix='cpu_negative_'));out=tmp/'run';shutil.copytree(FIX.parent.parent,out);d=out/'bound/000000'
  state=bytearray((d/'actual_state.bin').read_bytes());state[-4]^=1;state=bytes(state);(d/'actual_state.bin').write_bytes(state)
  raw=bytearray((d/'record.bin').read_bytes());raw[4096:4096+len(state)]=state;struct.pack_into('<I',raw,52,rolling(state));(d/'record.bin').write_bytes(raw)
  c=json.loads((d/'COMMITTED.json').read_text());c['state_sha256']=sha(state);(d/'COMMITTED.json').write_text(json.dumps(c))
  with self.assertRaisesRegex(RuntimeError,'full-state mismatch'):audit(out,tmp/'audit',B)
 def test_prior_id_pinned(self):
  tmp=Path(tempfile.mkdtemp(dir=P,prefix='prior_'));out=tmp/op.REVIEWED_RUN;out.mkdir()
  with zipfile.ZipFile(P/'ID_R2_b6a46cee2e544e7ebcd7c135df5f1797_RESULT.zip') as z:(out/'RESULT.json').write_bytes(z.read('RESULT.json'))
  self.assertEqual(op.prior_id(tmp)['run_id'],op.REVIEWED_RUN)
  (out/'RESULT.json').write_text('{}')
  with self.assertRaises(RuntimeError):op.prior_id(tmp)
 def test_cpu_scope_unchanged_models(self):
  self.assertEqual((B/'bounded_io.py').read_bytes(),(P.parent/'ov5640_id_fix_r2_20261024/bounded_io.py').read_bytes())
  original=json.loads((P/'BASELINE.json').read_text())
  for n in ['flyvis_ov5640.bit','flyvis_ov5640.hwh','single_frame.py','sensor_init.py','init_actions.json','ps_input.py','capture_binding.py','ddr_control.py','ddr_memory.py','camera_memory.py','edges.bin','initial_state.bin','reference.exe']:
   self.assertEqual(hashlib.sha256((B/n).read_bytes()).hexdigest(),original[n])
if __name__=='__main__':
 stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 (P/'CPU_TEST.log').write_text(stream.getvalue(),encoding='utf-8');(P/'CPU_RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_MOCK_INTEGRATION_ONLY' if r.wasSuccessful() else 'FAIL',tests=r.testsRun,errors=len(r.errors),failures=len(r.failures),board_operations=0,GPU_operations=0,Vivado_operations=0),indent=2));print(stream.getvalue());sys.exit(not r.wasSuccessful())

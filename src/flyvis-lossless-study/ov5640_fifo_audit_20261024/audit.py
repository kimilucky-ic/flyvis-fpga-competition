"""Offline saved-evidence audit and unchanged-driver fault injection; no hardware imports.
Injected timing/events are assumptions, NOT a physical or vendor-RTL reproduction.
"""
import hashlib,json,sys,shutil,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent
B=P.parent/'ov5640_single_r2_20261024/bundle'
R=P.parent/'ov5640_reset_20261023/build_r7'
sys.path.insert(0,str(B))
from bounded_io import CameraControl,OneFrameVdma
from capture_binding import CapturePool

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

class Scenario:
 def init__(self,mode):
  self.mode=mode;self.run=False;self.sr=1;self.fault=False;self.events=[]
  self.polls=0;self.copies=0;self.stops=0;self.regs={};self.now=0.;self.frames=0
 def clock(self):self.now+=.00001;return self.now
 def camera_read(self,a):
  if a==0:return int(self.run)
  if self.run:
   self.polls+=1
   if self.polls==2:
    if self.mode=='during_capture_overflow':
     self.fault=True;self.events.append('INJECT overflow before completed frame')
    elif self.mode=='after_halt_overflow':
     self.sr=0x1001;self.frames=1;self.fault=True
     self.events.append('INJECT completed frame/halt then source overflow before PS poll')
    elif self.mode=='dma_error_masked_by_overflow':
     self.sr=0x4021;self.fault=True;self.events.append('INJECT slave error plus overflow')
    elif self.mode=='dma_error_only':self.sr=0x4021
    else:self.sr=0x1001;self.frames=1
  v=(6 if self.run else 0)|int(self.fault)
  self.events.append(['camera_read',a,v]);return v
 def camera_write(self,a,v):
  self.events.append(['camera_write',a,v]);self.run=bool(v&1)
  if not self.run:self.stops+=1
 def read(self,a):
  v=self.sr if a==0x34 else self.regs.get(a,0)
  self.events.append(['vdma_read',a,v]);return v
 def write(self,a,v):
  self.events.append(['vdma_write',a,v]);self.regs[a]=v
  if a==0xa0:self.sr=0
  if a==0x34:self.sr&=~v
 def copy(self,a,n):
  self.copies+=1;assert self.sr==0x1001 and not self.run
  if self.mode=='late_fault_before_publication':self.fault=True
  return bytes(n)

def exercise(mode):
 s=Scenario(mode)
 class GPIO:
  read=staticmethod(s.camera_read)
  write=staticmethod(s.camera_write)
 pool=CapturePool(921600);addresses=[0x3000000+i*921600 for i in range(3)]
 d=OneFrameVdma(s,pool,addresses,[(addresses[0],addresses[-1]+921600)],[],s.copy,
                CameraControl(GPIO()),clock=s.clock,max_polls=20)
 error=None
 try:d.capture(0,0)
 except RuntimeError as exc:error=str(exc)
 if mode=='healthy':
  assert error is None and pool.states[0]=='READY' and s.copies==1 and s.stops==1
 else:
  assert error is not None and d.failed and pool.states[0]=='WRITING' and not pool.frames
  count=len(s.events)
  try:d.capture(1,1);raise AssertionError('retry accepted')
  except RuntimeError as exc:assert 'failed session' in str(exc)
  assert len(s.events)==count
  if mode!='late_fault_before_publication':assert s.copies==0 and s.stops==0
  expected='VDMA capture error' if mode=='dma_error_only' else 'video FIFO overflow; frame not publishable'
  assert error==expected
 if mode in ('after_halt_overflow','dma_error_masked_by_overflow'):
  assert s.events[-1][0]=='camera_read' # throws before current VDMA status read
 return dict(mode=mode,error=error,injected_complete_frames=s.frames,model_final_vdma_status=hex(s.sr),
  pool_states=pool.states,copies=s.copies,normal_stop_writes=s.stops,
  result='PASS_EXPECTED_CPU_MODEL_BEHAVIOR',trace=s.events)

def main():
 src=Path(sys.argv[1]);watched=list(B.glob('*'))+[R/'camera_guard.v',R/'cmos_capture_data.v']
 before={str(p):sha(p) for p in watched if p.is_file()}
 archive_sha=sha(src)
 assert archive_sha=='88411402bdf64f5ec73f35d2a1282f0e82b0e6dd60c200997f40d1158092ce7b'
 dst=P/src.name
 if not dst.exists():shutil.copyfile(src,dst)
 assert sha(dst)==archive_sha
 with zipfile.ZipFile(dst) as z:
  assert z.testzip() is None
  names=z.namelist();docs={n:json.loads(z.read(n)) for n in names if n.endswith('.json')}
  save('ZIP_MEMBERS.json',[dict(name=n,bytes=z.getinfo(n).file_size,sha256=hashlib.sha256(z.read(n)).hexdigest()) for n in names])
 rb=docs['SENSOR_READBACK.json'];tr=docs['SENSOR_TRACE.json'];ddr=docs['DDR_OWNERSHIP.json']
 assert rb['expected']==rb['observed'] and rb['writes']==248
 assert not tr['failed'] and len(tr['operations'])==263
 assert [x['result'] for x in tr['operations'][:2]]==[64,86]
 assert sum(x['operation']=='write' for x in tr['operations'])==248
 assert not any('error' in x for x in tr['operations'])
 ranges=[(ddr['neural_base'],ddr['neural_base']+ddr['neural_bytes'])]
 for a in ddr['camera_addresses']:
  assert a%4096==0 and 0x100000<=a and a+921600<=0x40000000
  assert ddr['camera_base']<=a and a+921600<=ddr['camera_base']+ddr['camera_bytes']
  assert all(a+921600<=lo or a>=hi for lo,hi in ranges)
  ranges.append((a,a+921600))
 assert not any(n.startswith('bound/') and n!='bound/' for n in names)
 hwh=R/'bd/flyvis_ddr/hw_handoff/flyvis_ddr.hwh'
 assert sha(hwh)=='61465634adaa0e421a5b07c77b38e0739fdcfdf8e68e977f25bf2d803b9097ae'
 params={}
 for m in ET.parse(hwh).iter('MODULE'):
  if m.get('INSTANCE') in ('camera_stream','camera_dma'):
   params[m.get('INSTANCE')]={x.get('NAME'):x.get('VALUE') for x in m.findall('./PARAMETERS/PARAMETER')}
 assert params['camera_stream']['C_ADDR_WIDTH']=='10'
 assert params['camera_dma']['C_USE_S2MM_FSYNC']=='2'
 assert params['camera_dma']['C_S_AXIS_S2MM_TDATA_WIDTH']=='24'
 results=[exercise(m) for m in ('healthy','during_capture_overflow','after_halt_overflow',
  'dma_error_masked_by_overflow','dma_error_only','late_fault_before_publication')]
 save('CPU_REPRODUCTION.json',dict(evidence='CPU_REGISTER_MODEL_FAULT_INJECTION_ONLY',
  physical_root_cause_confirmed=False,tests=results,
  limitation='Injected events are assumptions; no physical timing, AXI, or vendor VDMA/FIFO simulation.'))
 assert all(sha(p)==h for p,h in before.items())
 save('BASELINE_AFTER.json',dict(unchanged=True,sha256=before))
 save('AUDIT.json',dict(status='OFFLINE_AUDIT_COMPLETE_PHYSICAL_ROOT_CAUSE_UNRESOLVED',
  archive_sha256=archive_sha,run_id=docs['RUN_CONTEXT.json']['run_id'],operator_failure=docs['IN_DOUBT.json'],
  sensor_id='0x5640',sensor_write_count=248,sensor_readback_matches=13,trace_operations=263,
  camera_ranges_hex=[[hex(lo),hex(hi)] for lo,hi in ranges[1:]],saved_frame_or_input_or_state=False,
  neural_STEP='Not reached in inspected software path; no independent post-failure board counter read',
  missing_evidence=['capture MMIO trace and times','GPIO status word at failure','VDMA CR/SR/geometry/address readbacks',
   'completion-versus-overflow order','physical PCLK and video timing'],implementation_parameters=params,
  cpu_cases_passed=len(results),old_runtime_and_R7_RTL_unchanged=True,
  command=[sys.executable,'-X','utf8','-B',str(Path(__file__).resolve()),str(src)]))
 print('PASS_OFFLINE_ARCHIVE_CHECKS_AND_6_CPU_FAULT_INJECTION_CASES')
 print('Physical root cause remains unresolved; runtime/RTL unchanged; no board access.')
if __name__=='__main__':main()

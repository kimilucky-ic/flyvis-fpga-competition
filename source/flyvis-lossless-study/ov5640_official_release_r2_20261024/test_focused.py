"""Focused CPU regressions for actual recorded cycles and specific close procedure."""
from pathlib import Path
import json,sys,hashlib,shutil,importlib.util,struct
from types import SimpleNamespace as NS
R=Path(__file__).resolve().parent;B=R/'bundle';sys.path.insert(0,str(B))
from cycle_contract import check_cycles
from snapshot_records import decode_record
from audit_bridge import audit
from verify_result import validate_run
from offline_check import verify
O=R/'evidence/focused';O.mkdir(exist_ok=False)
RAW=R.parent/'ov5640_official_audit_20261024_b0a5/raw'
record=decode_record((RAW/'capture/bound/000000/record.bin').read_bytes(),0)
assert check_cycles(record.cycles)['matches']
assert not check_cycles(2201418)['matches']
assert not check_cycles(record.cycles+1)['matches']
prior=json.loads((R.parent/'ddr_soc_20261018/AUDIT.json').read_text())
assert prior['cycle_counter']['record_values']==[record.cycles]*3
for x in (0,-1,True,1.0,2**32):
 try:check_cycles(x)
 except ValueError:pass
 else:raise AssertionError('invalid cycle accepted')
comparison=audit(RAW/'capture',O/'actual_record_audit',B)
assert comparison['mismatch_words']==0
# R1 stopped session stays rejected by R2 verifier; do not invent normal close.
try:validate_run(RAW,O/'must_not_accept',B)
except ValueError as e:assert 'Uncertain session' in str(e)
else:raise AssertionError('stopped session admitted')
spec=importlib.util.spec_from_file_location('close_current',R/'close_current_session.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
results=[]
for mode in ('good','cancel','wrong_boot','source_tamper','busy','fault','ddr_changed','close_failure','after_changed'):
 run=O/mode/c.RUN_ID;shutil.copytree(RAW,run)
 events=[];cookie=int(c.RUN_ID[-8:],16);base=json.loads((run/'DDR_OWNERSHIP.json').read_text())['base']
 regs={4:base,8:base+188416,12:1,0x10:46,0x14:1,0x18:0,0x20:record.cycles,0x24:0,0x28:0,0x2c:cookie,
 0x30:45669,0x34:1513231,0x38:0x110004,0x3c:188416,0x40:1,0x80:1,0x84:base,0x88:0,0x8c:record.cycles,0x90:1,0x94:cookie,0x98:0,0x9c:45669,0xa0:1513231}
 if mode=='busy':regs[0x10]|=1
 if mode=='fault':regs[0x24]=1
 def read(a):events.append('read');return regs[a]
 control=NS(failed=True,session=(base,base+188416,1,cookie,0),_r=read)
 def copy(d):
  events.append('copy_ddr');data=(run/'capture/bound/000000/record.bin').read_bytes()
  return data[:-1]+bytes([data[-1]^1]) if mode=='ddr_changed' else data
 memory=NS(base=base,size=188416,slots=1,armed=True,released=False,copy_record=copy)
 def close():
  events.append('close')
  if mode=='close_failure':raise RuntimeError('injected close failure')
  if mode=='after_changed':regs[0x14]=2
 vendor=object();video=NS(video=vendor,close=close)
 bridge=NS(failed=True,closed=False,held_frame=None,binding=NS(next=1),video=video,memory=memory,control=control)
 rt=NS(out=run,owner=dict(control=control,memory=memory,bridge=bridge,checked_video=video,video=vendor))
 if mode=='source_tamper':(run/'capture/bound/000000/input.bin').write_bytes(b'bad')
 try:
  result=c.close_reviewed(rt,run,'wrong' if mode=='wrong_boot' else c.BOOT_ID,ask=lambda _:'取消' if mode=='cancel' else '关闭本次相机')
  assert mode in ('good','cancel'),mode
  assert (result is None)==(mode=='cancel')
 except RuntimeError:
  assert mode not in ('good','cancel'),mode
 assert control.failed and bridge.failed and not memory.released
 assert events.count('close')==(1 if mode in ('good','close_failure','after_changed') else 0)
 if mode in ('cancel','wrong_boot','source_tamper'):assert not events
 if (run/'CLOSE_ATTEMPT.json').exists():
  count=len(events)
  try:c.close_reviewed(rt,run,c.BOOT_ID,ask=lambda _:'关闭本次相机')
  except RuntimeError:pass
  else:raise AssertionError('close repeated')
  assert len(events)==count
 results.append(dict(mode=mode,close_calls=events.count('close'),reads=events.count('read'),passes=True))
# Main entry refuses new kernels without importing PYNQ or creating a replacement runtime.
assert 'board_run' not in sys.modules
try:c.main()
except RuntimeError as e:assert 'ORIGINAL' in str(e)
else:raise AssertionError('new kernel accepted')
(O/'RESULT.json').write_text(json.dumps(dict(status='PASS_FOCUSED_CPU_ONLY',actual_record_cycles=record.cycles,
 actual_state_words=45669,mismatch_words=0,wrong_old_constant_rejected=True,closed_session_not_fabricated=True,
 close_cases=results,original_kernel_guard=True,board_operations=0,native_official_close_executed=False),indent=2)+'\n')
print('PASS_FOCUSED_CPU_ONLY')

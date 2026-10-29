import sys,zipfile,json,hashlib,shutil
from pathlib import Path
base=Path('flyvis-lossless-study/ov5640_id_diag_20261024').resolve()
sys.path.insert(0,str(base))
from test_id_diag import Bus
from id_diag import read_id
# Documented v2.1 behavior: a dynamic read does not start before byte count.
class CountGatedBus(Bus):
 def write(self,a,v):
  super().write(a,v)
  if a==0x108 and v==0x179:self.sr&=~4
 def clock(self):
  if self.reading:self.now+=.01
  return self.now
b=CountGatedBus();r=read_id(b,clock=b.clock)
assert r['failed_stage']=='transaction:49'
assert [v for a,v in b.w if a==0x108]==[0x178,0x30,0x20b,0x179]
assert 'TimeoutError' in r['error']
source=Path(r'C:/Users/hzy72/Downloads/ID_cd4dcb6069e64c36a4ef76372ee1fcb9_RESULT.zip')
out=base/'operator_cd4dcb60_review';out.mkdir(exist_ok=False)
shutil.copy2(source,out/source.name)
with zipfile.ZipFile(source) as z:
 d=json.loads(z.read('ID_DIAGNOSTIC.json'));run=json.loads(z.read('RESULT.json'))
 t=d['trace'];stage=t['stages'][-1]
 report=dict(status='READ_ONLY_OPERATOR_EVIDENCE_REVIEW_SOFTWARE_ORDER_DEFECT_IDENTIFIED_NOT_BOARD_FIXED',archive_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),boot_id=run['boot_id'],failed_stage=d['failed_stage'],sensor_register=d['sensor_register'],wait_stage_ms=(stage['end_ns']-stage['start_ns'])/1e6,max_host_mmio_call_ms=t['max_host_call_ns']/1e6,counts=t['counts'],last_ISR=t['last_reads']['0x20']['value'],last_SR=t['last_reads']['0x104']['value'],transmitted_FIFO_words=[hex(e['value']) for e in t['first_calls'] if e['op']=='write' and e['offset']=='0x108'],program_calls=run['actual_program_calls'],nominal_MHz=run['nominal_MHz'],physical_clock_measured=False,diagnosis='Driver waits for BB after read-address but before byte-count; AXI IIC2.1 starts dynamic read only after byte-count. Circular wait explains exact observed stage. Separate electrical faults still untested.',cpu_reproduction=dict(evidence='DOCUMENTATION_BASED_CPU_MODEL_ONLY',status=r['status'],failed_stage=r['failed_stage'],count_command_sent=False),agent_board_actions=0,program_sources_changed=False,references=['https://lists.infradead.org/pipermail/linux-arm-kernel/2022-June/754479.html','https://docs.amd.com/r/en-US/pg090-axi-iic/Read-Four-Bytes-from-an-IIC-Device-Addressed-as-0x34','https://github.com/torvalds/linux/blob/master/drivers/i2c/busses/i2c-xiic.c'],next_action='Isolated software-only v2.1 transaction-order fix with count-gated CPU regression, retain old releases. No board retry until separately prepared manual procedure.')
 (out/'REVIEW.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 (out/'CPU_REPRODUCTION.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))

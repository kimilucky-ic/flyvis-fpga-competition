import sys,json,time,threading,tempfile,importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'bundle'))
import record_worker as rw
import ram_records,step_profile as prof
from capture_binding import read_capsule
from snapshot_records import decode_record
from live_protocol import index_from_committed,canonical
from camera_diagnostic import CallTiming
from ddr_control import DdrControl
T=P/'evidence'/('async_'+time.strftime('%Y%m%d_%H%M%S'));T.mkdir()
prior=Path((P/'evidence/latest_cpu.txt').read_text())
result=json.loads((prior/'RESULT.json').read_text());out=Path(result['producer_output'])
config=json.loads((P/'pc/session.json').read_text());context=json.loads((out/'RUN_CONTEXT.json').read_text())
jobs=[];previous=config['initial_state_sha256']
for k in range(3):
    d=out/'capture/bound'/('%06d'%k);p,_=read_capsule(d/'PREPARED.bin',2884);c,raw=read_capsule(d/'COMMITTED.bin',188416)
    r=decode_record(raw,k)
    bridge=SimpleNamespace(failed=False,last_record_bytes=raw,binding=SimpleNamespace(failed=False,next=k+1,
        last_committed=(bytes(80*48*3),r,canonical(p),canonical(c))))
    jobs.append((bridge,k,previous,{},{}));previous=r.state_sha256
checks=[]
def reject(fn):
    try:fn()
    except (ValueError,RuntimeError,MemoryError):return
    raise AssertionError('expected rejection')
# Worker retains its snapshot while producer object changes; next task can be enqueued.
root=T/'ordered';root.mkdir();journal=ram_records.RamRecords(root);journal.start();ram_records.CURRENT=journal
started=threading.Event();release=threading.Event();original=rw.index_from_committed
expected0=index_from_committed(*jobs[0][:2],config,context,jobs[0][2],{})
def delayed(*a):
    if a[1]==0:started.set();assert release.wait(3)
    return original(*a)
rw.index_from_committed=delayed;packets=[];worker=rw.RecordWorker(root,config,context,packets,capacity=1)
worker.submit(*jobs[0]);assert started.wait(2)
worker.submit(*jobs[1]);assert worker.done==0
blocked=threading.Event();done=threading.Event()
def third():blocked.set();worker.submit(*jobs[2]);done.set()
th=threading.Thread(target=third);th.start();assert blocked.wait(1);assert not done.wait(.03)
# Mutating the original bridge must not alter the queued snapshot.
jobs[0][0].binding.next=99;jobs[0][0].last_record_bytes=b'changed'
release.set();th.join(3);worker.drain();assert worker.done==3 and len(packets)==3
assert packets[0]==expected0['packet_sha256'];assert len([x for x in journal.files if x.endswith('.ready.json')])==3
checks+=['overlap while prior packet blocked','bounded queue backpressure no drop','immutable snapshot isolates next step','three jobs preserve order']
# Inject packing failure; subsequent submission rejected, failed payload retained.
rw.index_from_committed=lambda *a:(_ for _ in ()).throw(ValueError('injected pack error'))
worker2=rw.RecordWorker(root,config,context,[],capacity=1)
job=jobs[1];job[0].binding.next=1
# valid k=0 snapshot comes from restored job0
jobs[0][0].binding.next=1;jobs[0][0].last_record_bytes=worker.failed_job if worker.failed_job else (out/'capture/bound/000000/COMMITTED.bin').read_bytes()
# use correct raw capsule again
_,raw=read_capsule(out/'capture/bound/000000/COMMITTED.bin',188416);jobs[0][0].last_record_bytes=raw
try:worker2.submit(*jobs[0])
except RuntimeError:pass
reject(worker2.drain);assert worker2.failed_job is not None;reject(worker2.check)
assert read_capsule(out/'capture/bound/000000/COMMITTED.bin',188416)[1]==raw
checks.append('packing failure retains raw committed evidence and fails gate')
rw.index_from_committed=original;ram_records.CURRENT=None
# Prevalidated hot path uses no resolve; unknown/outside paths still use fallback validation.
r=T/'paths';r.mkdir();j=ram_records.RamRecords(r);dest=r/'a.bin';j.prevalidate([dest]);j.start()
with patch.object(Path,'resolve',side_effect=AssertionError('unexpected resolve')):
    assert j.put(dest,b'evidence');assert j.get(dest)==b'evidence'
assert j.key(r/'..'/'outside') is None
checks.append('prepared RAM paths avoid repeated filesystem resolution')
# Call diagnostic distinguishes time below wait from parent processing; always restores profiler.
def wait_for_frame():time.sleep(.005)
def readframe():wait_for_frame();return b'frame'
c=CallTiming();assert c.call(readframe)==b'frame';report=c.report();assert sys.getprofile() is None
assert any(k.endswith(':wait_for_frame') and v['inclusive_ms']>=4 for k,v in report['functions'].items())
try:c.call(lambda:(_ for _ in ()).throw(ValueError('camera error')))
except ValueError:pass
assert sys.getprofile() is None
checks.append('call profiler accounts nested wait and restores on exception')
# Compare complete MMIO transcript against unchanged R7, not timing guesses.
class MMIO:
    def init__(self):self.trace=[];self.staged=0;self.count=0
    def read(self,a):
        self.trace.append(('r',a))
        return {0x30:45669,0x34:1513231,0x38:0x110004,0x3c:188416,0x10:38,0x14:self.count,
            0x18:self.staged,0x80:self.count,0x84:0x100000,0x88:0,0x8c:2199975,0x90:self.count,
            0x94:7,0x98:0,0x9c:45669,0xa0:1513231}.get(a,0)
    def write(self,a,v):
        self.trace.append(('w',a,v))
        if a>=0x400:self.staged+=1
        if a==0 and v==1:self.count+=1;self.staged=0
spec=importlib.util.spec_from_file_location('r7_control',P.parent/'ov5640_live_r7_20261025/bundle/ddr_control.py')
old=importlib.util.module_from_spec(spec);sys.modules[spec.name]=old;spec.loader.exec_module(old)
traces=[]
for cls in (old.DdrControl,DdrControl):
    mm=MMIO();ctrl=cls(mm);ctrl.session=(0x100000,0x100000+188416,1,7,0);prof.begin()
    ctrl.advance(bytes(2884));traces.append(mm.trace)
assert traces[0]==traces[1]
assert sum(x[0]=='w' and x[1]>=0x400 for x in traces[1])==721
assert all(n in prof.snapshot() for n in ('control_preflight','control_input_721_mmio_writes','control_staged_check','control_step_wait','control_completed_count_check','control_publication'))
checks.append('same MMIO reads writes values order and 721 input writes; six timing scopes')
(T/'RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_ASYNC_NEGATIVE_AND_CONTROL_ONLY',tests=checks,board_actions=0,camera_internal_cause='NOT_MEASURED',profiler_test=report),indent=2))
(P/'evidence/latest_async.txt').write_text(str(T));print(json.dumps(checks,indent=2))

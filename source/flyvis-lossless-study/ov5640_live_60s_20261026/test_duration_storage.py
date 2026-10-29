"""CPU-only clock/admission/storage tests; no camera, MMIO, PYNQ, GPU or EDA."""
from pathlib import Path
import sys,json,time,math,threading,zipfile,hashlib
from unittest.mock import patch
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'bundle'))
from duration_run import *
from batch_records import BatchRecords
T=P/'evidence'/('duration_storage_'+time.strftime('%Y%m%d_%H%M%S'));T.mkdir()
checks=[]
def ok(n):checks.append(n);print('PASS',n,flush=True)
def rejects(fn):
 try:fn()
 except (ValueError,RuntimeError,OSError):return
 raise AssertionError('not rejected')
config=json.loads((P/'pc/session.json').read_text())
def mem(cma,avail):return 'CmaFree: %d kB\nCmaTotal: %d kB\nMemAvailable: %d kB\n'%(cma*1024,cma*1024,avail*1024)
large=memory_plan(config,mem(256,400));small=memory_plan(config,mem(128,300))
assert large['slots']==1201 and large['minimum_period_s']==.05
assert small['slots']<large['slots'] and small['maximum_start_rate_hz']<20
assert small['ddr_bytes']<=112*MIB
rejects(lambda:memory_plan(config,mem(32,128)))
rejects(lambda:memory_plan(config,'MemAvailable: 1 kB'))
ok('CMA subset and ordinary RAM both reserved;128MiB CMA adapts pacing; missing/low memory rejected')
class Clock:
 def init__(self):self.t=100.
 def clock(self):return self.t
 def sleep(self,n):self.t+=n
for plan in (large,small):
 c=dict(config,max_steps=plan['slots'],minimum_period_s=plan['minimum_period_s']);v=Clock();w=RunWindow(c,v.clock,v.sleep);w.begin();starts=[]
 while w.admit():starts.append(v.t);v.t+=.001
 r=w.receipt(len(starts));validate_receipt(r,config,len(starts))
 assert len(starts)<=c['max_steps'] and all(x<160 for x in starts) and v.t>=160
 assert all(y-x+1e-9>=c['minimum_period_s'] for x,y in zip(starts,starts[1:]))
 bad=dict(r,elapsed_seconds=59);rejects(lambda:validate_receipt(bad,config,len(starts)))
 bad=dict(r,completed_steps=len(starts)-1);rejects(lambda:validate_receipt(bad,config,len(starts)))
 bad=dict(r,last_frame_start_seconds=60);rejects(lambda:validate_receipt(bad,config,len(starts)))
 bad=dict(r,elapsed_seconds=float('nan'));rejects(lambda:validate_receipt(bad,config,len(starts)))
 rejects(w.admit)
ok('fast virtual producer stays within60s/capacity; exact deadline no extra frame; counterfeit timed FINISH rejected')
v=Clock();w=RunWindow(config,v.clock,v.sleep);w.begin();assert w.admit();v.t+=61
assert not w.admit();r=w.receipt(1);assert r['elapsed_seconds']==61 and r['last_frame_start_seconds']==0
ok('slow already-admitted frame completes beyond deadline without starting another frame')
# Full-sized storage payloads, deliberately NOT valid neural simulation records.
(T/'stress').mkdir();j=BatchRecords(T/'stress');j.start();expected={}
for k in range(1201):
 record=k.to_bytes(4,'little')+bytes([k%251])*(188416-4)
 prep=b'p'*2884;packet=b'h'+record;commit=b'c'+record
 d=j.root/'capture/bound'/('%06d'%k);path=j.root/'transport'/('%06d.packet'%k)
 assert j.put(d/'PREPARED.bin',prep) and j.put(d/'COMMITTED.bin',commit) and j.put(path,packet,replace=True)
 j.retire_duplicate_commit(d/'COMMITTED.bin',path,record)
 j.put(path.with_suffix('.ack.json'),b'{"durable":true}',replace=True)
 expected[k]=hashlib.sha256(packet).hexdigest();j.persist_completed(k)
 if k in (15,16,511,1199):assert hashlib.sha256(j.get(path)).hexdigest()==expected[k]
stat=j.flush();assert stat['persisted_steps']==1201 and len(stat['batches'])==76 and stat['peak_ram_bytes']<4*MIB
for k,digest in expected.items():assert hashlib.sha256(j.get(j.root/'transport'/('%06d.packet'%k))).hexdigest()==digest
assert sum(len(zipfile.ZipFile(z).namelist()) for z in (j.root/'spool').glob('*.zip'))==2402
ok('1201 full-size synthetic packets plus bound inputs:76 durable batches incl tail;all reread unchanged;peak RAM<4MiB')
# Writer delays while readers still see immutable RAM; after commit readers see ZIP.
(T/'race').mkdir();r=BatchRecords(T/'race',batch_steps=1);r.start();d=r.root/'capture/bound/000000';p=r.root/'transport/000000.packet'
r.put(d/'PREPARED.bin',b'p');r.put(p,b'record')
entered=threading.Event();release=threading.Event();real_fsync=__import__('os').fsync
errors=[]
def delayed(fd):entered.set();assert release.wait(5);real_fsync(fd)
def writer():
 try:r.persist_completed(0)
 except BaseException as exc:errors.append(repr(exc))
with patch('batch_records.os.fsync',delayed):
 th=threading.Thread(target=writer);th.start();assert entered.wait(5);assert r.get(p)==b'record';release.set();th.join(5)
assert not th.is_alive() and not errors and r.get(p)==b'record'
ok('concurrent upload read safe before and after RAM eviction;ZIP entries portable')
(T/'failed').mkdir();f=BatchRecords(T/'failed',batch_steps=1);f.start();d=f.root/'capture/bound/000000';p=f.root/'transport/000000.packet'
f.put(d/'PREPARED.bin',b'p');f.put(p,b'record')
with patch('batch_records.os.fsync',side_effect=OSError('injected disk failure')):rejects(lambda:f.persist_completed(0))
assert f.persisted_steps==0 and f.get(p)==b'record' and not list((f.root/'spool').glob('*.zip'))
rejects(f.flush);assert f.get(p)==b'record'
ok('disk sync failure publishes no batch,retains RAM;pending file blocks automatic overwrite/retry')
result=dict(status='PASS_CPU_60S_CLOCK_MEMORY_AND_STORAGE_ONLY',checks=checks,board_actions=0,physical_runtime=False,
 duration_clock='VIRTUAL_60_SECONDS',storage_payloads='1201 synthetic full-sized packets;not neural results',
 large_memory_plan=large,small_memory_plan=small,storage=stat)
(T/'RESULT.json').write_text(json.dumps(result,indent=2));(P/'evidence/latest_duration_storage.txt').write_text(str(T))
print('RESULT',T)

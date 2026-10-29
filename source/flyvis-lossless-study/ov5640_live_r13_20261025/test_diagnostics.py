"""CPU-only R13 observer tests; forced GC exists only in this test."""
from pathlib import Path
import json,sys,gc,threading,time
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'bundle'))
from gc_events import GcEvents
import step_profile as prof
T=P/'evidence'/('diagnostics_'+time.strftime('%Y%m%d_%H%M%S'));T.mkdir()
original_callbacks=list(gc.callbacks);policy=(gc.isenabled(),gc.get_threshold())
trace=GcEvents();trace.start();trace.step=11
# Deterministic diagnostic correlation with real CPU GC.
prof.begin(True,keys=frozenset(('native_test',)))
assert prof.tick()==0 and prof.tick('other')==0
start=prof.tick('native_test');gc.collect(0);time.sleep(.025);prof.add('native_test',start)
d=prof.snapshot()['native_test'];assert d['ms']>=20 and d['ms']>d['thread_cpu_ms']
trace.close();report=trace.report();assert report['complete']
assert any(e[0]=='start' and e[4]==11 and d['start_ns']<=e[1]<=d['end_ns'] for e in report['events'])
assert list(gc.callbacks)==original_callbacks and (gc.isenabled(),gc.get_threshold())==policy
trace.close();assert list(gc.callbacks)==original_callbacks
# Bound enforcement is explicit; it never claims a truncated event list is complete.
bounded=GcEvents(2);bounded.start()
try:
 for i in range(6):bounded.callback('start',{'generation':0})
finally:bounded.close()
r=bounded.report();assert len(r['events'])==2 and r['dropped_events']>=4 and not r['complete']
# Unrelated callbacks preserved; failure path always detaches ours.
def other(*args):pass
gc.callbacks.append(other)
t=GcEvents()
try:
 t.start();raise RuntimeError('injected outer failure')
except RuntimeError:pass
finally:t.close()
assert other in gc.callbacks and t.callback not in gc.callbacks;gc.callbacks.remove(other)
# Thread-local selective profile cannot leak into worker thread.
prof.begin(True,keys=frozenset(('keep',)));start=prof.tick('keep');seen=[]
def worker():
 prof.begin();seen.append((prof.tick('keep'),prof.snapshot()))
th=threading.Thread(target=worker);th.start();th.join();prof.add('keep',start)
assert seen==[(0,{})] and set(prof.snapshot())=={'keep'}
prof.begin(False);assert prof.tick('keep')==0
# Instrumentation calls are bounded and measured as CPU-only observation.
measure={}
for enabled in (False,True):
 begin=time.perf_counter_ns()
 for step in range(128):
  prof.begin(enabled,keys=frozenset(('k',)))
  for j in range(8):
   start=prof.tick('k');prof.add('k',start)
 measure[str(enabled)]=(time.perf_counter_ns()-begin)/128/1e6
prof.begin(False)
assert list(gc.callbacks)==original_callbacks and (gc.isenabled(),gc.get_threshold())==policy
result=dict(status='PASS_R13_DIAGNOSTIC_CPU_ONLY',selective_timing=True,GC_timestamp_step_correlation=True,GC_policy_unchanged=True,other_callbacks_preserved=True,overflow_explicit=True,callback_removed_on_failure=True,thread_isolation=True,controlled_pause=d,desktop8intervals_perstep_ms=measure,board_operations=0,ARM_timing=False)
(T/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(P/'evidence/latest_diagnostics.txt').write_text(str(T));print(json.dumps(result,indent=2))

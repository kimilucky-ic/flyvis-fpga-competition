"""Bounded CPU checks of R11 timing and unchanged numeric expressions; no board."""
from pathlib import Path
import importlib.util,sys,json,time,threading,statistics as st
import numpy as np
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'bundle'))
import step_profile as prof
from direct_input import DirectAreaInput
spec=importlib.util.spec_from_file_location('r10_mapper',P.parent/'ov5640_live_r10_20261025/bundle/direct_input.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
a=old.DirectAreaInput(48,80,'BGR');b=DirectAreaInput(48,80,'BGR')
assert np.array_equal(a.area_indices,b.area_indices) and np.array_equal(a.area_weights,b.area_weights) and np.array_equal(a.bias,b.bias)
from live_protocol import Store
r2=P.parent/'ov5640_live_r2_20261025';store=Store(r2/'pc/records',json.loads((r2/'pc/session.json').read_text()))
frames=[]
for k in range(32):
 _,raw,_=store.read(k)
 x=np.frombuffer(raw,np.uint8).reshape(48,10,80,10,3).astype(np.uint32)
 frames.append(((x.sum(axis=(1,3))+50)//100).astype(np.uint8))
frames += [np.zeros((48,80,3),np.uint8),np.full((48,80,3),255,np.uint8)]
for f in frames:
 prof.begin(False);expected=a.render(f).tobytes();actual=b.render(f).tobytes();assert actual==expected
 prof.begin(True);sampled=b.render(f).tobytes();assert sampled==expected
 d=prof.snapshot();assert all(d[n]['calls']==1 for n in ('map_gather','map_grey','map_weighted_sum','map_range_check_clip','preprocess_direct_grey_721'))
# Inactive paths return immediately; another worker cannot inherit sampled timings.
prof.begin(True);t=prof.tick();seen=[]
def worker():
 prof.begin();seen.append((prof.tick(),prof.snapshot()))
th=threading.Thread(target=worker);th.start();th.join();prof.add('parent',t)
assert seen==[(0,{})] and 'parent' in prof.snapshot()
prof.begin(False);assert prof.tick()==0 and prof.snapshot()=={}
# Deterministic wall/CPU separation without a sleep-based assertion.
original_time=prof.time
class Clock:
 wall=1000000;cpu=100000
 def perf_counter_ns(self):return self.wall
 def thread_time_ns(self):return self.cpu
clock=Clock();prof.time=clock
try:
 prof.begin(True);t=prof.tick();clock.wall+=10000000;clock.cpu+=2000000;prof.add('interval',t)
 assert prof.snapshot()['interval']['ms']==10 and prof.snapshot()['interval']['thread_cpu_ms']==2
finally:prof.time=original_time;prof.begin(False)
# Bounded desktop timing is only an instrumentation cost observation, NOT ARM performance.
measure={}
for enabled in (False,True):
 values=[]
 for k in range(128):
  prof.begin(enabled);start=time.perf_counter_ns();b.render(frames[k%32]);values.append((time.perf_counter_ns()-start)/1e6)
 measure['sampled' if enabled else 'off']=dict(median_ms=st.median(values),mean_ms=st.mean(values),calls=128)
prof.begin(False)
r=dict(status='PASS_R11_TIMING_AND_INPUT_CPU_ONLY',frames=34,input_words_compared_per_mode=34*721,bit_mismatch=0,source='32 retained R2 images area-downsampled to80x48 plus black/white; not R10 source images',coefficients_identical=True,thread_local_isolation=True,deterministic_wall_cpu_split=True,sample_clock_semantics='thread CPU excludes descheduling and CPU consumed by other threads; difference is NOT solely GIL wait',desktop_instrumentation=measure,max_taps=int(b.area_indices.shape[0]),gathered_pixel_slots=int(b.area_indices.size),board_operations=0,native_ARM=False)
(P/'evidence/DIAGNOSTICS_RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

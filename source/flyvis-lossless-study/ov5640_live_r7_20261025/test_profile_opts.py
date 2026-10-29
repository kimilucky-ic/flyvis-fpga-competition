"""CPU-only profile partition and safe micro-optimization validation."""
from pathlib import Path
import importlib.util,sys,json,time,statistics,hashlib
import numpy as np
P=Path(__file__).resolve().parent;B=P/'bundle';R6=P.parent/'ov5640_live_r6_20261025'
sys.path.insert(0,str(B))
import step_profile as prof
from snapshot_records import decode_record,rolling,_rolling_geometry
from live_protocol import Store
from ps_input import PsInput

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
old=module('r6_codec',R6/'bundle/snapshot_records.py')
cfg=json.loads((R6/'pc/session.json').read_text());s=Store(R6/'pc/records',cfg)
blobs=[]
for k in range(32):
 blob=(R6/'pc/records'/('%06d.packet'%k)).read_bytes()[-188416:];blobs.append(blob)
 assert decode_record(blob,k).__dict__==old.decode_record(blob,k).__dict__
 bad=bytearray(blob);bad[4096]^=1
 try:decode_record(bad,k)
 except ValueError:pass
 else:raise AssertionError('corruption accepted')
rng=np.random.default_rng(7020)
for n in [0,1,31,32,721,45669]:
 for j in range(4):
  blob=rng.integers(0,2**32,n,dtype=np.uint32).tobytes();assert rolling(blob)==old.rolling(blob)
for a in _rolling_geometry(721):assert not a.flags.writeable
base=[];new=[]
for rep in range(3):
 for k,blob in enumerate(blobs):
  for fn,values in ([(old.decode_record,base),(decode_record,new)] if (rep+k)%2 else [(decode_record,new),(old.decode_record,base)]):
   t=time.perf_counter_ns();fn(blob,k);values.append((time.perf_counter_ns()-t)/1e6)
# Candidate exact256-entry normalization LUT; derived fixture pixels, no real400x240 raw available.
src=(B/'ps_input.py').read_text().replace('self.height, self.width = height, width','self.height, self.width = height, width\n        self.gray_lut=np.arange(256,dtype=np.float32)/np.float32(255.)').replace('gray=lum.astype(np.float32)/np.float32(255.)','gray=self.gray_lut[lum]')
trial_path=P/'evidence/ps_input_lut_trial.py';trial_path.write_text(src)
trial=module('lut_trial',trial_path).PsInput(240,400,'BGR');baseline=PsInput(240,400,'BGR')
r2=P.parent/'ov5640_live_r2_20261025';ss=Store(r2/'pc/records',json.loads((r2/'pc/session.json').read_text()));frames=[]
for k in range(32):
 _,raw,_=ss.read(k);v=np.frombuffer(raw,np.uint8).reshape(240,2,400,2,3).astype(np.uint32)
 frame=((v.sum(axis=(1,3))+2)//4).astype(np.uint8);frames.append(frame)
 assert trial.render(frame).tobytes()==baseline.render(frame).tobytes()
frames.extend([np.full((240,400,3),x,np.uint8) for x in (0,1,127,254,255)])
frames.append(rng.integers(0,256,(240,400,3),dtype=np.uint8))
for f in frames:assert trial.render(f).tobytes()==baseline.render(f).tobytes()
mb=[];mt=[]
for rep in range(3):
 for k,f in enumerate(frames[:32]):
  for mapper,values in ([(baseline,mb),(trial,mt)] if (rep+k)%2 else [(trial,mt),(baseline,mb)]):
   t=time.perf_counter_ns();mapper.render(f);values.append((time.perf_counter_ns()-t)/1e6)
def stat(v):return dict(n=len(v),median_ms=statistics.median(v),mean_ms=statistics.mean(v))
r=dict(status='PASS_CPU_CODEC_EXACT_AND_LUT_TRIAL',codec_actual32_exact=True,corrupt32_rejected=True,rolling_cases=24,
 codec_old=stat(base),codec_new=stat(new),mapper_old=stat(mb),mapper_lut_trial=stat(mt),mapping_cases=len(frames),
 LUT_shipped=False,ARM_speed_measured=False,board_actions=0)
(P/'evidence/OPTIMIZATION_TEST.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

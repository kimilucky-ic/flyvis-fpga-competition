"""CPU/native C equivalence only. Reads saved records; no board/network."""
from pathlib import Path
import sys,importlib.util,json,hashlib,struct,time,statistics as st
import numpy as np
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'bundle'))
from native_payload import build_checker
from snapshot_records import decode_record,rolling
from direct_input import DirectAreaInput
from live_protocol import Store
import step_profile as prof
T=P/'evidence'/('focused_'+time.strftime('%Y%m%d_%H%M%S'));T.mkdir()
cc='C:/AMDDesignTools/2026.1.1/tps/mingw/10.0.0/win64.o/nt/bin/gcc.exe'
checker,identity=build_checker(T/'native',authorized=True,compiler=cc)
oldroot=P.parent/'ov5640_live_r11_20261025'
spec=importlib.util.spec_from_file_location('r11_mapper',oldroot/'bundle/direct_input.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
a=old.DirectAreaInput(48,80,'BGR');b=DirectAreaInput(48,80,'BGR')
for n in ('area_indices','area_weights','bias'):assert np.array_equal(getattr(a,n),getattr(b,n))
r2=P.parent/'ov5640_live_r2_20261025';ss=Store(r2/'pc/records',json.loads((r2/'pc/session.json').read_text()))
frames=[]
for k in range(32):
 _,raw,_=ss.read(k);x=np.frombuffer(raw,np.uint8).reshape(48,10,80,10,3).astype(np.uint32);frames.append(((x.sum(axis=(1,3))+50)//100).astype(np.uint8))
rng=np.random.default_rng(1211)
frames += [rng.integers(0,256,(48,80,3),np.uint8) for _ in range(128)]
frames += [np.full((48,80,3),v,np.uint8) for v in (0,1,127,128,254,255)]
frames += [frames[0][:,::-1,:],frames[0][::-1,:,:]]
for f in frames:
 prof.begin(False);e=a.render(f).tobytes();assert b.render(f).tobytes()==e
 prof.begin(True);assert b.render(f).tobytes()==e
prof.begin(False)
store=Store(oldroot/'pc/records',json.loads((oldroot/'pc/session.json').read_text()));records=[]
for k in range(32):
 raw=(oldroot/'pc/records'/('%06d.packet'%k)).read_bytes()[-188416:];records.append(raw)
 assert decode_record(raw,k)==decode_record(raw,k,payload_checker=checker)
 assert checker(raw)==(rolling(raw[128:3012]),rolling(raw[4096:186772]),0)
negative=[]
def outcome(raw,k):
 def invoke(native):
  try:return ('ok',decode_record(raw,k,payload_checker=checker if native else None))
  except ValueError as e:return ('error',str(e))
 x,y=invoke(False),invoke(True);assert x==y,(x,y);return x
raw=records[0]
for off in (0,8,16,56,76,128,129,3008,4096,65536,186768):
 bad=bytearray(raw);bad[off]^=1;assert outcome(bytes(bad),0)[0]=='error';negative.append('flip_'+str(off))
for off in (128,4096,186768):
 for bits in (0x7f800000,0xff800000,0x7fc01234,0x7f800001):
  bad=bytearray(raw);struct.pack_into('<I',bad,off,bits)
  struct.pack_into('<I',bad,48,rolling(bad[128:3012]));struct.pack_into('<I',bad,52,rolling(bad[4096:186772]))
  assert outcome(bytes(bad),0)==('error','Non-finite state/input');negative.append('nonfinite_%d_%x'%(off,bits))
for blob in (b'',raw[:-1],raw+b'x'):
 assert outcome(blob,0)[0]=='error';negative.append('length_'+str(len(blob)))
assert outcome(raw,1)[0]=='error';negative.append('wrong_step')
# Direct native length/null ABI bounds return error without dereferencing.
import ctypes
out=(ctypes.c_uint32*3)()
assert checker.fn(None,188416,out)==-1 and checker.fn(ctypes.c_char_p(raw),188415,out)==-1
assert checker.fn(ctypes.c_char_p(raw),188416,None)==-1
try:checker(bytearray(raw))
except ValueError:pass
else:raise AssertionError('mutable record admitted')
# Native failure must propagate; no silent Python fallback.
saved=checker.fn;checker.fn=lambda *a:-1
try:
 try:decode_record(raw,0,payload_checker=checker)
 except RuntimeError:pass
 else:raise AssertionError('native error ignored')
finally:checker.fn=saved
try:build_checker(T/'forbidden',compiler=cc)
except RuntimeError:pass
else:raise AssertionError('missing authorization')
assert not (T/'forbidden').exists()
bench={}
for label,fn,data in [('map_R11',a.render,frames[:32]),('map_R12',b.render,frames[:32]),('decode_numpy',lambda x:decode_record(x[1],x[0]),list(enumerate(records))),('decode_native',lambda x:decode_record(x[1],x[0],payload_checker=checker),list(enumerate(records)))]:
 vals=[]
 for item in data:
  start=time.perf_counter_ns();fn(item);vals.append((time.perf_counter_ns()-start)/1e6)
 bench[label]=dict(mean_ms=st.mean(vals),median_ms=st.median(vals),samples=len(vals))
r=dict(status='PASS_NATIVE_PAYLOAD_AND_GREY_ONCE_CPU_ONLY',mapping_frames=len(frames),mapping_input_words_per_mode=len(frames)*721,mapping_bit_mismatch=0,physical_saved_records=32,negative_cases=negative,negative_count=len(negative),native_bounds_checks=True,native_failure_no_fallback=True,missing_authorization_rejected=True,compiler=identity,desktop_only_timing=bench,grayscale_pixel_count_old=18025,grayscale_pixel_count_new=3840,neural_math_changed=False,board_operations=0,native_ARM=False)
(T/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');(P/'evidence/latest_focused.txt').write_text(str(T));print(json.dumps(r,indent=2))

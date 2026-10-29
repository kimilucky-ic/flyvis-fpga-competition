"""Use all32 accepted physical frames/inputs/states; no board access."""
import importlib.util,json,statistics,struct,sys,time
from pathlib import Path
from types import SimpleNamespace
import numpy as np
P=Path(__file__).resolve().parent;B=P/'bundle';OLD=P.parent/'ov5640_live_20261024';sys.path.insert(0,str(B))
from ps_input import PsInput
from snapshot_records import rolling,decode_record
from live_protocol import Store,packet_from_committed,sha

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
old_mapper=load('baseline_ps_input',OLD/'bundle/ps_input.py').PsInput
old_codec=load('baseline_codec',OLD/'bundle/snapshot_records.py')
T=P/'evidence'/('actual32_'+time.strftime('%Y%m%d_%H%M%S'));T.mkdir()
config=json.loads((OLD/'pc/session.json').read_text());store=Store(OLD/'pc/records',config)
assert len(store.meta)==32 and store.final['camera_closed'] and store.final['run_id']=='RUN_a70b2226527446e9a7ef120ed04aefd7'
old,new=old_mapper(480,800,'BGR'),PsInput(480,800,'BGR');rows=[];old_times=[];new_times=[];codec_old=[];codec_new=[]
for k in range(32):
 m,raw,r=store.read(k);image=np.frombuffer(raw,np.uint8).reshape(480,800,3)
 start=time.perf_counter();a=old.render(image);old_times.append((time.perf_counter()-start)*1000)
 start=time.perf_counter();b=new.render(image);new_times.append((time.perf_counter()-start)*1000)
 assert a.tobytes()==b.tobytes()==r.input_bits,('721 FP32 mismatch',k)
 packet=(OLD/'pc/records'/('%06d.packet'%k)).read_bytes();record=packet[-188416:]
 start=time.perf_counter();r0=old_codec.decode_record(record,k);codec_old.append((time.perf_counter()-start)*1000)
 start=time.perf_counter();r1=decode_record(record,k);codec_new.append((time.perf_counter()-start)*1000)
 assert r0.input_bits==r1.input_bits and r0.state_bits==r1.state_bits
 binding=SimpleNamespace(failed=False,next=k+1,last_committed=(raw,r1,json.dumps(m['prepared']).encode(),json.dumps(m['committed']).encode()))
 bridge=SimpleNamespace(failed=False,binding=binding,last_record_bytes=record)
 context={key:m[key] for key in ('run_id','boot_id','evidence')}
 rebuilt=packet_from_committed(bridge,k,config,context,m['previous_state_sha256'],m['timing'])
 assert rebuilt==packet,('changed wire bytes',k)
 rows.append(dict(step_id=k,input_words=721,input_bits_equal=True,state_words=45669,state_bits_equal=True,wire_bytes_equal=True,
                  source_sha256=sha(raw),input_sha256=sha(r.input_bits),state_sha256=sha(r.state_bits)))
# Exact integer codec proof samples; no floating point arithmetic in checksum.
rng=np.random.default_rng(2564);lengths=[0,1,2,31,32,33,63,64,65,721,45669]
for n in lengths:
 for data in [rng.integers(0,2**32,n,dtype=np.uint32),np.full(n,0xffffffff,np.uint32),np.zeros(n,np.uint32)]:
  assert rolling(data.tobytes())==old_codec.rolling(data.tobytes()),n
# Exercise pixel extremes and alternate geometries admitted by original mapping.
extra=[]
for h,w,order in [(480,800,'BGR'),(480,640,'RGB'),(240,320,'GBR')]:
 a,b=old_mapper(h,w,order),PsInput(h,w,order)
 for label,image in [('black',np.zeros((h,w,3),np.uint8)),('white',np.full((h,w,3),255,np.uint8)),('noise',rng.integers(0,256,(h,w,3),dtype=np.uint8))]:
  assert a.render(image).tobytes()==b.render(image).tobytes(),(h,w,order,label)
  extra.append([h,w,order,label])
# Original decoder rejection behavior must remain for checksum/NaN/header errors.
base=(OLD/'pc/records/000000.packet').read_bytes()[-188416:];negative=[]
for label,mutate in [('checksum',lambda x:x.__setitem__(4096,x[4096]^1)),('header',lambda x:x.__setitem__(0,0)),
                     ('nonfinite_valid_checksum',lambda x:(struct.pack_into('<I',x,4096,0x7fc00000),struct.pack_into('<I',x,52,rolling(x[4096:186772]))))]:
 blob=bytearray(base);mutate(blob)
 for decoder in (old_codec.decode_record,decode_record):
  try:decoder(blob,0)
  except ValueError:pass
  else:raise AssertionError(label)
 negative.append(label)
result=dict(status='PASS_ACTUAL32_CPU_BITWISE_EQUIVALENCE',source_run=store.final['run_id'],
 input_words_compared=32*721,state_words_compared=32*45669,mismatch_words=0,all32_wire_packets_byte_identical=True,
 checksum_cases=len(lengths)*3,extra_input_cases=extra,codec_negative_cases=negative,rows=rows,
 host_cpu_timing_ms=dict(old_mapping_mean=statistics.mean(old_times),new_mapping_mean=statistics.mean(new_times),
 old_record_decode_mean=statistics.mean(codec_old),new_record_decode_mean=statistics.mean(codec_new)),
 timing_scope='Windows CPU, not ARM or end-to-end performance; single pass each per32frame',
 board_actions=0,neural_model_changes=0)
(T/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(P/'evidence/latest_actual32.txt').write_text(str(T))
print(json.dumps({k:v for k,v in result.items() if k not in ('rows','extra_input_cases')},indent=2))

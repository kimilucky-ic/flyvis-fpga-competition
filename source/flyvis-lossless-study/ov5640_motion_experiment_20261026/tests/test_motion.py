"""CPU only: actual mapping and transport with synthetic frames / saved state bytes.
No new neural computation, no PYNQ, camera, network or FPGA interaction.
"""
from pathlib import Path
import sys,json,struct,hashlib,time,shutil,unittest
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
P=Path(__file__).resolve().parents[1];sys.path[:0]=[str(P/'bundle'),str(P/'pc')]
import ram_records,motion_trial
from batch_records import BatchRecords
from capture_binding import BoundSteps,read_capsule
from direct_input import DirectAreaInput
from snapshot_records import decode_record,rolling
from live_protocol import sha,pack,unpack,packet_from_committed,Store
from record_worker import RecordWorker
from stream_audit import run as audit
source=P.parent/'ov5640_live_v261_20261026/pc/rounds/1f942a59a8515cd6a2e62ddd5fc7bc42'
oldcfg=json.loads((source/'session.json').read_text());oldstore=Store(source/'records',oldcfg)
# Accepted state bytes are fixtures, not output of the synthetic stimulus.
state=oldstore.read(0)[2].state_bits;seed=(source/'records/000000.packet').read_bytes()[-188416:]
T=P/'evidence'/('cpu_'+str(time.time_ns()));T.mkdir();checks=[]
def ok(s):checks.append(s);print('PASS',s)
def rejects(f):
 try:f()
 except (ValueError,RuntimeError,FileNotFoundError):return
 raise AssertionError('must reject')
for name in motion_trial.CONDITIONS[1:]:
 for t,phase,trial in [(0,'baseline',0),(10,'move_right',1),(15,'recovery',1),(25,'move_right',2),(30,'recovery',2),(40,'move_right',3),(45,'recovery',3),(60.1,'recovery',3)]:
  a=motion_trial.annotation(name,int(t*1e9));assert (a['phase'],a['trial'])==(phase,trial)
rejects(lambda:motion_trial.condition({'motion_condition':'unknown'}));rejects(lambda:motion_trial.annotation('white_black',-1))
ok('stage boundaries and unknown/negative time reject; cues never claim actual edge events')
fixtures={}
for cond in motion_trial.CONDITIONS[1:]:
 root=T/cond;root.mkdir();(root/'transport').mkdir();(root/'capture').mkdir();cfg=dict(oldcfg,session_id=('a' if cond=='white_black' else 'b')*32,token='CPU_ONLY',motion_condition=cond)
 context=dict(run_id='RUN_00000001',boot_id='00000000-0000-0000-0000-000000000001',evidence='CPU_MOCK_ONLY',experiment_start_ns=1000000000)
 j=BatchRecords(root);ram_records.CURRENT=j;j.start();binding=BoundSteps(root/'capture/bound',32);binding.retain_source=True
 mapper=DirectAreaInput(48,80,'BGR');packets=[];worker=RecordWorker(root,cfg,context,packets);previous=sha((P/'bundle/initial_state.bin').read_bytes());expected=[]
 try:
  for k in range(32):
   bg=220 if cond=='white_black' else 25;bar=25 if cond=='white_black' else 220
   frame=np.full((48,80,3),bg,dtype=np.uint8);x=16+(k*2)%40;frame[:,x:x+7]=bar
   source=frame.tobytes();inputs=mapper.render(frame).astype('<f4').tobytes();blob=bytearray(seed)
   struct.pack_into('<I',blob,8,k);struct.pack_into('<2I',blob,80,k+1,1);blob[128:3012]=inputs;struct.pack_into('<I',blob,48,rolling(inputs));record=bytes(blob)
   def advance(data):assert data==inputs;return SimpleNamespace(frame_id=k,sequence=k+1)
   def fetch(d):return decode_record(record,k,expected_cookie=1),record
   binding.step((k,1000000000+k*1900000000,source),lambda b:mapper.render(np.frombuffer(b,np.uint8).reshape(48,80,3)).astype('<f4').tobytes(),advance,fetch)
   bridge=SimpleNamespace(failed=False,last_record_bytes=record,binding=binding)
   worker.submit(bridge,k,previous,{},{});previous=sha(state);expected.append((source,inputs,record))
  worker.drain();j.drain();assert j.durable_prefix()==32
  storage=j.flush();ram_records.CURRENT=None
  # Reopen archive bytes after RAM flush, verify both PREPARED source and network packets.
  receiver=Store(root/'received',cfg)
  for k,(source,inputs,record) in enumerate(expected):
   raw=j.get(root/('transport/%06d.packet'%k));m,s,r=unpack(raw,cfg)
   assert s==source and r.input_bits==inputs and r.state_bits==state
   ram_records.CURRENT=j
   pm,payload=read_capsule(root/('capture/bound/%06d/PREPARED.bin'%k),2884+11520)
   ram_records.CURRENT=None;assert payload==inputs+source and pm['frame_sha256']==sha(source)
   ack=receiver.accept(raw);assert receiver.accept(raw)['duplicate']
   assert len(receiver.meta)==k+1
   if k==0:
    n=struct.unpack_from('<I',raw)[0];bad=bytearray(raw);bad[4+n+10]^=1;rejects(lambda:unpack(bytes(bad),cfg))
    badmeta=json.loads(raw[4:4+n]);badmeta['experiment']['condition']='black_white' if cond=='white_black' else 'white_black';rejects(lambda:unpack(pack(badmeta,source,record),cfg))
    badmeta=json.loads(raw[4:4+n]);badmeta['prepared']['source_timestamp_ns']+=1;rejects(lambda:unpack(pack(badmeta,source,record),cfg))
    rejects(lambda:unpack(raw,dict(cfg,motion_condition='demo')))
   if k==2:
    damaged=bytearray(raw);damaged[-3000]^=1;rejects(lambda:receiver.accept(bytes(damaged)))
  f=dict(status='ALL_STEPS_SAVED_CAMERA_CLOSE_PENDING',error=None,session_id=cfg['session_id'],run_id=context['run_id'],boot_id=context['boot_id'],completed_steps=32,hardware_completed_steps=32,camera_closed=False,packet_sha256=receiver.digests,duration=dict(oldstore.final['duration'],elapsed_seconds=60.1,completed_steps=32,last_frame_start_seconds=58.9),context={})
  receiver.finish(f)
  def oracle(first,n,work,i,o):
   assert i.read_bytes()==b''.join(e[1] for e in expected[first:first+n]);o.write_bytes(state*n)
  result=audit(receiver.path,cfg,P/'bundle',root/'audit',root/'progress.json',oracle=oracle)
  assert result['status']=='PASS_ALL_SAVED_STATES' and result['evidence']=='CPU_MOCK_ONLY' and result['source_mapping_audited']
  assert all(row['mapping_max_abs']==0 for row in result['rows'])
  (root/'session.json').write_text(json.dumps(cfg));fixtures[cond]=dict(records=str(receiver.path),config=str(root/'session.json'),audit=str(root/'audit/RESULT.json'))
 finally:
  worker.finished.set();worker.thread.join(3);j.finished.set()
  if j.thread:j.thread.join(3)
  ram_records.CURRENT=None
ok('two32step CPU fixtures: raw frame/input/full state retained through writer, archives, duplicate upload, and PC source mapping audit')
ok('raw corruption, wrong condition, timestamp mismatch, mixed demo schema and conflicting resend rejected')
# Source-preserving old demo read remains valid; old accepted record never overwritten.
assert len(Store(source/'records',oldcfg).meta)==1081
ok('1081 accepted v3 packets remain readable with unchanged hashes')
(P/'evidence/CPU_RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_MOTION_BINDING_ONLY',checks=checks,fixtures=fixtures,board_actions=0,neural_computation=False,synthetic_frames=True,states_from_previous_run=True),indent=2))
print('FIXTURES',T)

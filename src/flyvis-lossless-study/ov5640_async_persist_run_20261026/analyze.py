from pathlib import Path
import json,sys,statistics as st,hashlib
E=Path(__file__).resolve().parent;P=E.parent/'ov5640_live_v261_20261026';sid='1f942a59a8515cd6a2e62ddd5fc7bc42';root=P/'pc/rounds'/sid;r=root/'records';sys.path.insert(0,str(P/'bundle'))
from live_protocol import Store,sha
from board_runtime import clocks
cfg=json.loads((root/'session.json').read_text());store=Store(r,cfg);f=store.final;c=store.camera_close;a=json.loads((r/'audit/RESULT.json').read_text());n=len(store.meta)
assert n==f['completed_steps']==a['steps']==c['completed_steps']==1081 and a['status']=='PASS_ALL_SAVED_STATES' and a['mismatch_words']==0 and c['status']=='CLOSED' and f['error'] is None
assert f['packet_sha256']==c['packet_sha256']==store.digests;assert f['duration']['elapsed_seconds']>=60 and f['duration']['last_frame_start_seconds']<60 and f['duration']['stop_reason']=='DURATION_REACHED'
assert f['context']['NEURAL_AFTER.json']=={'0x10':38,'0x14':n,'0x18':0,'0x24':0,'0x4c':n,'0x50':0};clocks(f['context']['CLOCK.json']['raw'])
cmds=json.loads((r/'audit/COMMANDS.json').read_text());pos=0;prev=sha((P/'bundle/initial_state.bin').read_bytes());sealed={}
for cmd in cmds:
 first,count=cmd['first_step'],cmd['steps'];assert pos==first and cmd['initial_expected_sha256']==prev and cmd['returncode']==0
 ip=r/'audit'/('%06d_inputs.bin'%first);ep=r/'audit'/('%06d_expected.bin'%first);inputs=ip.read_bytes();expected=ep.read_bytes();assert len(inputs)==count*2884 and len(expected)==count*182676;sealed[str(ip)]=sha(inputs);sealed[str(ep)]=sha(expected)
 for j in range(count):
  k=first+j;m,source,rec=store.read(k);assert rec.input_bits==inputs[j*2884:(j+1)*2884] and rec.state_bits==expected[j*182676:(j+1)*182676]
  assert a['rows'][k]['actual_state_sha256']==a['rows'][k]['expected_state_sha256']==sha(rec.state_bits)
 prev=sha(expected[-182676:]);pos+=count
assert pos==n
for path in [*r.glob('*.packet'),r/'FINISH.json',r/'CAMERA_CLOSE.json',r/'audit/RESULT.json',r/'audit/COMMANDS.json']:sealed[str(path)]=sha(path.read_bytes())
def stats(v):
 v=sorted(v);return dict(mean=st.mean(v),median=st.median(v),p95=v[int(.95*(len(v)-1))],maximum=max(v))
def board(f):
 return dict(steps=f['completed_steps'],elapsed_s=f['duration']['elapsed_seconds'],ms_per_step=f['duration']['elapsed_seconds']*1000/f['completed_steps'],steps_per_second=f['completed_steps']/f['duration']['elapsed_seconds'],iteration_ms=stats([x['whole_iteration_ms'] for x in f['packet_timings'].values()]),queue_wait_ms=stats([x['queue_wait_ms'] for x in f['worker_timings'].values()]),batch_ms=stats([x['persist_ms'] for x in f['context']['RAM_FLUSH.json']['batches']]),upload_ack_ms=stats([x['round_trip_seconds']*1000 for x in f['transfer_timings'].values()]))

old=board(json.loads((P/'pc/rounds/cfc66b09bad15b5aab478d8317c618d1/records/FINISH.json').read_text()));current=board(f)
metrics={k:stats([x[k] for x in f['packet_timings'].values() if k in x]) for k in ['ps_mapping_ms','capture_and_cache_ms','input_upload_step_and_publication_ms','packet_enqueue_ms','ring_credit_wait_ms']}
result=dict(status='PASS_SAVED_OPERATOR_RECORDS',steps=n,state_words=n*45669,input_words=n*721,mismatches=0,current=current,previous=old,mean_step_change_percent=(current['ms_per_step']/old['ms_per_step']-1)*100,metrics=metrics,storage=f['context']['RAM_FLUSH.json']['storage'],camera_close_ms=c['close_duration_ms'],board_operations=0,new_neural_runs=0,browser_fps_verified=False)
(E/'RESULT.json').write_text(json.dumps(result,indent=2));(E/'SOURCE_SHA256.json').write_text(json.dumps(sealed,indent=2));print(json.dumps(result,indent=2))

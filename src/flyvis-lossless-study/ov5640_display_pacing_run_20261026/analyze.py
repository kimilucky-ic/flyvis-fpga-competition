from pathlib import Path
import json,sys,statistics as st,hashlib
E=Path(__file__).resolve().parent;P=E.parent/'ov5640_live_v261_20261026';sid='cfc66b09bad15b5aab478d8317c618d1';root=P/'pc/rounds'/sid;r=root/'records';sys.path.insert(0,str(P/'bundle'))
from live_protocol import Store,sha
from board_runtime import clocks
cfg=json.loads((root/'session.json').read_text());store=Store(r,cfg);f=store.final;c=store.camera_close;a=json.loads((r/'audit/RESULT.json').read_text());n=len(store.meta)
assert n==f['completed_steps']==a['steps']==c['completed_steps']==1089 and a['status']=='PASS_ALL_SAVED_STATES' and a['mismatch_words']==0 and c['status']=='CLOSED' and f['error'] is None
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
old=board(json.loads((P/'pc/rounds/604780dd181959f4ad8bb08c94a1f241/records/FINISH.json').read_text()));current=board(f)
b=json.loads((E/'BROWSER_TIMING.json').read_text());assert b['session_id']==sid;rows=b['rows'];paints=[x for x in rows if x['painted']];assert len(paints)==677 and paints[0]['step_id']==0 and paints[-1]['step_id']==n-1 and all(x['step_id']<y['step_id'] for x,y in zip(paints,paints[1:]))
indexes=[i for i,x in enumerate(rows) if x['painted']];gaps=[]
for start,end in zip(indexes,indexes[1:]):
 x,y=rows[start],rows[end]
 if y['paint_interval_ms']>500:
  rr=rows[start:end+1];gaps.append(dict(next_step=y['step_id'],gap_ms=y['paint_interval_ms'],poll_count=end-start,received_before=x['received'],received_after=y['received'],maximum_fetch_ms=max(v['fetch_ms'] for v in rr),maximum_between_poll_sleep_ms=max(rr[i]['started_unix_ms']-rr[i-1]['started_unix_ms']-rr[i-1]['cycle_ms'] for i in range(1,len(rr)))))
interval=stats([x['paint_interval_ms'] for x in paints if x.get('paint_interval_ms') is not None]);span=(paints[-1]['paint_at_ms']-paints[0]['paint_at_ms'])/1000
out=dict(status='PASS_OPERATOR_60S_AND_BROWSER_PACING_MEASURED',session_id=sid,run_id=f['run_id'],board=current,previous_board=old,step_time_change_percent=(current['ms_per_step']/old['ms_per_step']-1)*100,all_input_words=n*721,all_state_words=n*45669,bitwise_mismatches=0,saved_oracle_chunks=len(cmds),new_oracle_runs=0,camera_close_ms=c['close_duration_ms'],audit_after_finish_seen_s=a['after_finish_seen_seconds'],browser=dict(shown=len(paints),display_only_skipped=n-len(paints),first_last_span_s=span,update_rate_hz=(len(paints)-1)/span,interval_ms=interval,stages_ms={k:stats([x[k] for x in paints]) for k in ['fetch_ms','image_ms','skeleton_ms','paint_ms','cycle_ms']},gaps_over_500ms=gaps,remaining_behind_response_count=stats([x['received']-x['step_id']-1 for x in paints])),limits=['Browser FPS is first-to-last displayed interval,not modelstep rate','No synchronized physical camera-to-screen measurement','Different scenes/runs: small boardtime variation is not causal proof','after_finish_seen_s zero is measured resolution;not zero total finishing delay','Metrics buffer4096 includes idlepolls;export preserved all677paint samples now'],board_actions=0,runtime_edits=0)
for path,digest in sealed.items():assert sha(Path(path).read_bytes())==digest
(E/'SOURCE_SHA256.json').write_text(json.dumps(sealed,indent=2));(E/'RESULT.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))

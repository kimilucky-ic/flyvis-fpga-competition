from pathlib import Path
import sys,json,statistics as st
E=Path(__file__).resolve().parent;P=E.parent/'ov5640_live_v261_20261026';sys.path.insert(0,str(P/'bundle'))
from live_protocol import Store,sha
sid=json.loads((P/'pc/ACTIVE_ROUND.json').read_text())['session_id'];root=P/'pc/rounds'/sid;r=root/'records';cfg=json.loads((root/'session.json').read_text());store=Store(r,cfg);f=store.final;a=json.loads((r/'audit/RESULT.json').read_text());n=len(store.meta)
assert n==f['completed_steps']==a['steps']==store.camera_close['completed_steps'];assert store.camera_close['status']=='CLOSED' and f['error'] is None and a['status']=='PASS_ALL_SAVED_STATES' and a['mismatch_words']==0
for k,row in enumerate(a['rows']):
 m,_,rec=store.read(k);assert row['step_id']==k and row['input_sha256']==sha(rec.input_bits) and row['actual_state_sha256']==sha(rec.state_bits)==row['expected_state_sha256'] and row['mismatch_words']==0
assert f['packet_sha256']==store.camera_close['packet_sha256']==store.digests
prev=json.loads((P/'pc/rounds/7fa0282e80fd55e9973790fe05060eb2/records/FINISH.json').read_text())
def stats(xs):
 xs=sorted(xs);return dict(mean=st.mean(xs),p95=xs[int(.95*(len(xs)-1))],maximum=max(xs))
def summary(f):
 return dict(steps=f['completed_steps'],seconds=f['duration']['elapsed_seconds'],ms_per_step=f['duration']['elapsed_seconds']*1000/f['completed_steps'],iteration_ms=stats([v['whole_iteration_ms'] for v in f['packet_timings'].values()]),queue_wait_ms=stats([v['queue_wait_ms'] for v in f['worker_timings'].values()]),round_trip_ms=stats([v['round_trip_seconds']*1000 for v in f['transfer_timings'].values()]),batch_persistence_ms=stats([v['persist_ms'] for v in f['context']['RAM_FLUSH.json']['batches']]))
new,old=summary(f),summary(prev)
result=dict(status='PASS_SAVED_STREAM_AUDIT_RUN_DISPLAY_LATENCY_DIAGNOSIS',session=sid,current=new,previous=old,step_time_change_percent=(new['ms_per_step']/old['ms_per_step']-1)*100,state_words=n*45669,all_actual_hashes_match_saved_expected_hashes=True,camera_closed=True,audit_active_s=a['active_seconds'],audit_after_finish_seen_s=a['after_finish_seen_seconds'],browser_poll_delay_after_work_ms=150,browser_update_rate_upper_bound_hz=1000/150,browser_render_time_measured=False,physical_end_to_end_latency_measured=False,board_actions=0,runtime_edits=0,new_oracle_runs=0,findings=['No material mean or p95 board-step slowdown observed in separate runs; not controlled causal proof','UI serial fetch/decode/render followed by150ms sleep caps visible update rate below6.67Hz','Packaging worker synchronously saves each16-step batch; queue stalls can exceed1s','Uploader can read pending packets from RAM; batch durability is NOT a universal per-packet upload prerequisite','Incremental audit tail after observing FINISH0.094s is not complete last-frame-to-ready delay'])
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

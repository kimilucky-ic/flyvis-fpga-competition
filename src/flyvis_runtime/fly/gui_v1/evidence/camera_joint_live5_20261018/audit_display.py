"""Read-only audit of this actual run's saved draw identities and timings."""
import hashlib,io,json,sys
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;G=P.parents[1];sys.path.insert(0,str(G))
from live_protocol import load,require,write,sha
from joint_camera_control import hardware_module
from spatial_state import SpatialRegistry
root=G/'runtime/joint/c59286b40c9c4c2e84a3e456a0856540'
scope,perf,finish,result=[load(root/n) for n in ('scope.json','MINIMAL_PERFORMANCE.json','PS_FINISH.json','result.json')]
require(scope['run_id']=='ad5b4adac2b941f59b4a5271d1bde1fe' and result['committed_steps']==100,'EXACT_LIVE5_RUN')
Reader=hardware_module(load(root/'hardware_handoff.json'),'evidence_journal').JournalReader
pc=Reader(root/'pc/evidence.fvej');spatial=SpatialRegistry()
a=lambda name:np.load(io.BytesIO(pc.read(name)),allow_pickle=False)
digest=lambda data:hashlib.sha256(data).hexdigest()
rows=[json.loads(x) for x in (root/'display_receipts.jsonl').read_text(encoding='utf-8').splitlines()]
prior=-1
for row in rows:
 k=row['step_id'];require(k>prior and row['serial']==row['state_token']==k+1,'DRAW_ORDER_NO_BACKLOG')
 require(row['run_id']==scope['run_id'] and row['session_id']==scope['session_id'],'DRAW_RUN')
 source=json.loads(pc.read('source_%d.json'%k))
 full=a('committed_full_%d.npy'%k);flow=a('official_flow_%d.npy'%k)
 require(row['source_png_sha256']==source['png_sha256']==digest(pc.read('source_%d.png'%k)),'DRAW_SAME_INPUT')
 require(row['spatial_values_sha256']==digest(spatial.extract(full).tobytes()),'DRAW_SAME_SPATIAL')
 require(row['flow_sha256']==digest(np.asarray(flow,dtype='<f4').tobytes()),'DRAW_SAME_OFFICIAL_FLOW')
 decision=json.loads(pc.read('timing_%d.json'%k))['decision']
 require(row['unified_commit_sha256']==decision,'DRAW_SAME_COMMIT')
 prior=k
require(prior==99 and finish['requests']==finish['commits']==100,'FINAL_DRAW_AND_BOARD_COUNTS')
require(load(root/'worker_exit.json')['lease_closed'] and load(root/'camera_capture.json')['closed'],'DEVICES_CLOSED')
percent=lambda values:dict(zip(('p50','p95','max'),map(float,np.percentile(values,[50,95,100]))))
selected=[json.loads(pc.read('source_%d.json'%k))['sequence'] for k in range(100)]
require(all(b>=a for a,b in zip(selected,selected[1:])),'SOURCE_ORDER')
require(all(row['PL_core_ms_at_configured_100MHz']==.57681 for row in perf['rows']),'PL_CYCLES')
v=dict(status='PASS_BOUNDED_LIVE_LOW_RATE_DISPLAY_SAVED_EVIDENCE',run_id=scope['run_id'],session_id=scope['session_id'],
 GPU_FPGA_steps=100,wall_s=perf['total_compute_wall_s'],actual_commit_hz=perf['actual_commit_rate_hz'],
 model_time_s=.5,model_dt_s=.005,display_draw_receipts=len(rows),first_draw_step=rows[0]['step_id'],last_draw_step=prior,
 steady_first_to_last_draw_hz=(len(rows)-1)*1000/(rows[-1]['browser_draw_ms']-rows[0]['browser_draw_ms']),
 receipt_to_browser_RAF_ms=percent([r['receipt_to_render_estimate_ms'] for r in rows]),
 latency_upper_bound_ms=percent([r['upper_ms'] for r in rows]),clock_uncertainty_max_ms=max(r['clock_uncertainty_ms'] for r in rows),
 decode_and_snapshot_ms=percent([r['decode_snapshot_ns']/1e6 for r in perf['display_rows']]),
 GPU_candidate_host_ms=percent([r['GPU_produce_wall_ns']/1e6 for r in perf['rows']]),
 camera_frames_delivered=load(root/'camera_capture.json')['frames_delivered'],distinct_selected_frames=len(set(selected)),
 source_first=selected[0],source_last=selected[-1],latest_input_policy=scope['input_policy'],
 PS_requests=finish['requests'],PS_commits=finish['commits'],pending=finish['pending'],poisoned=finish['poisoned'],
 PL_core_cycles=perf['rows'][-1]['core_cycles'],native_H_GPU_updates=result['native_H_GPU_updates'],
 numerical_audit_sha256=sha(P/'SAVED_DATA_AUDIT.json'),PC_capture_sha256=sha(root/'pc/evidence.fvej'),PS_capture_sha256=finish['PS_capture_sha256'],
 limitations=['This is low-rate online acquisition/compute, not wall-time 200Hz model execution',
 'Browser receipts measure RAF submission, not physical scanout; clock uncertainty is reported',
 'Actual camera preview draw FPS and sensor exposure timestamps were not instrumented',
 'Minimal PS journal is signed finish/timings, not independent per-step raw candidate evidence; no pre-ACK crash durability'],
 REALTIME_STREAM_PASS='NOT_CLAIMED',whole_run_acceptance='PENDING_FULL_PS_RAW_EVIDENCE_CONTRACT',new_GPU_runs=0,new_board_operations=0)
write(P/'DISPLAY_VERIFICATION.json',v)
print(json.dumps({k:v[k] for k in ('status','run_id','GPU_FPGA_steps','actual_commit_hz','display_draw_receipts','steady_first_to_last_draw_hz','receipt_to_browser_RAF_ms','camera_frames_delivered','distinct_selected_frames','PS_requests','PS_commits','native_H_GPU_updates','REALTIME_STREAM_PASS')},ensure_ascii=True,indent=2))

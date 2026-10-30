"""Serialize saved camera frames only; no inference or endpoint access."""
import base64,copy,io,json,statistics,sys,time
from pathlib import Path
P=Path(__file__).resolve().parent;G=P.parents[1];sys.path.insert(0,str(G))
import numpy as np
from joint_camera_control import hardware_module
from joint_camera_protocol import conversion_receipt,frame_check
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
h=load(G/'runtime/joint/7f111da4437843539eeffef2c6c2546e/hardware_handoff.json')
r=hardware_module(h,'evidence_journal').JournalReader(G/'runtime/joint/7f111da4437843539eeffef2c6c2546e/pc/evidence.fvej')
rows=[];frames=[]
encode=lambda p:json.dumps(p,separators=(',',':'),allow_nan=False).encode()
for k in range(32):
    f=dict(source=json.loads(r.read('source_%d.json'%k)),conversion=json.loads(r.read('conversion_%d.json'%k)),
        png=base64.b64encode(r.read('source_%d.png'%k)).decode(),
        values=np.load(io.BytesIO(r.read('input_721_%d.npy'%k)),allow_pickle=False).tolist())
    frames.append(f);compact=conversion_receipt(f)
    a,b=encode(f),encode(compact)
    # Saved selected frames omit unselected camera sequences. Do not fake a
    # consecutive capture stream; verify reconstruction directly instead.
    q=json.loads(b);q.pop('schema');q['png']=f['png']
    frame_check(q,f['source']['run_id'],f['source']['source_kind']);assert q==f
    rows.append(dict(saved_step=k,source_sequence=f['source']['sequence'],legacy_bytes=len(a),
        compact_bytes=len(b),saved_bytes=len(a)-len(b),reconstructed_exact=True))
timings=[]
for repeat in range(4):
    for compact in ((False,True) if repeat%2==0 else (True,False)):
        start=time.perf_counter_ns()
        for f in frames:
            q=json.loads(encode(conversion_receipt(f) if compact else f))
            assert q['values']==f['values'] and q['source']==f['source']
        timings.append(dict(repeat=repeat,compact=compact,json_roundtrip_ms=(time.perf_counter_ns()-start)/1e6))
old=sum(x['legacy_bytes'] for x in rows);new=sum(x['compact_bytes'] for x in rows)
perf=load(G/'evidence/camera_joint32_20261016/PERFORMANCE.json')
findings=load(G/'evidence/joint_latency_selfcheck_20261017/READ_ONLY_FINDINGS.json')
sync_ns=[x['phase_ns']['fsync'] for x in findings['physical_run']['PS_profiles']]
# This is only a transparent what-if for two of four similarly expensive barriers.
# New two-barrier PS SD latency is unmeasured and need not scale linearly.
old_step_ms=468.532;old_sync_ms=statistics.median(sync_ns)/1e6
value=dict(evidence='CPU_SAVED_FRAME_SERIALIZATION_ONLY',frames=32,rows=rows,timings=timings,
    legacy_total_bytes=old,compact_total_bytes=new,return_payload_reduction_percent=100*(1-new/old),
    json_roundtrip_32_frames_median_ms={str(c):statistics.median(x['json_roundtrip_ms'] for x in timings if x['compact']==c) for c in (False,True)},
    limits='One converter-return payload only. Raw frame still reaches converter, retained preview still reaches GUI; not end-to-end bandwidth or step-rate measurement.',
    saved_real_baseline=dict(run_id=perf['run_id'],overall_steps_s=perf['overall_steps_per_s_including_handshake'],
        typical_intercommit_ms=old_step_ms,STEP_ms=perf['STEP_roundtrip_ms']['p50'],COMMIT_ms=perf['COMMIT_roundtrip_ms']['p50'],
        PS_four_fsync_p50_ms=old_sync_ms),
    conditional_estimate=dict(assumption='Only save half of old four-fsync time; other costs constant; medians are not additive statistical estimates',
        typical_step_ms=old_step_ms-old_sync_ms/2,typical_steps_s=1000/(old_step_ms-old_sync_ms/2),
        actual_new_joint_steps_s='NOT_MEASURED',planning_target_steps_s=[3,5],target_is_guaranteed=False),
    board_connections=0,GPU_runs=0,camera_starts=0,GUI_starts=0,new_neural_steps=0)
(P/'CPU_COMPARISON.json').write_text(json.dumps(value,indent=2),encoding='utf8')
print(json.dumps({k:value[k] for k in ('evidence','frames','legacy_total_bytes','compact_total_bytes',
    'return_payload_reduction_percent','json_roundtrip_32_frames_median_ms','conditional_estimate')},indent=2))

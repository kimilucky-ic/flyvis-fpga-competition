"""Read saved PC records only. No GPU/decoder inference, network or board I/O.

This is NOT the production acceptance auditor. Missing PS FINISH/capture and
terminal records remain missing; no AUTO_ACCEPTANCE or run result is changed.
"""
import dataclasses,hashlib,io,json
from pathlib import Path
import sys
OUT=Path(__file__).resolve().parent;GUI=OUT.parents[1];sys.path.insert(0,str(GUI))
import numpy as np
from live_protocol import load,sha,write
from joint_camera_control import hardware_module
from spatial_state import SpatialRegistry
from hybrid_full485 import Full485Contract
from hybrid_a3 import module

root=GUI/'runtime/joint/6f7b1a68ac8d40029926b04a8a4bc327'
scope=load(root/'scope.json');result=load(root/'result.json');exited=load(root/'worker_exit.json')
assert scope['run_id']==exited['run_id']=='f7ad8295f6944b3b9ac2b90eee1e0a92'
handoff=load(root/'hardware_handoff.json');w=hardware_module(handoff,'protocol')
Reader=hardware_module(handoff,'evidence_journal').JournalReader
reader=Reader(root/'pc/evidence.fvej',allow_incomplete=True)
assert reader.context['run_id']==scope['run_id']
array=lambda name:np.load(io.BytesIO(reader.read(name)),allow_pickle=False)
digest=lambda data:hashlib.sha256(data).hexdigest()
contract=Full485Contract();hmod=module('actual60_saved_hash_helper',contract.paths['h_step'])
spatial=SpatialRegistry();ids=spatial.ids;r_ids=contract.r
steps=result['committed_steps'];times=[];previous=None;previous_H=None;parent=bytes(32);txn=bytes(16)
source_sequences=[]
for k in range(steps):
    raw=reader.read('request_%d.bin'%k);header=w.Header.unpack(raw[:w.HEADER_BYTES]);payload=raw[w.HEADER_BYTES:]
    candidate=reader.read('candidate_%d.bin'%k);receipt=w.Header.unpack(reader.read('RESULT_%d.bin'%k))
    commit=w.Header.unpack(reader.read('COMMIT_%d.bin'%k));ack=w.Header.unpack(reader.read('ACK_%d.bin'%k))
    assert header.step==k and header.parent_commit==parent and header.previous_txn==txn and header.payload_sha==w.digest(payload)
    assert receipt.identity()==header.identity() and receipt.payload_sha==w.digest(candidate) and receipt.compute_cycles==57681
    assert ack==dataclasses.replace(commit,op=w.ACK)
    assert commit.identity()==dataclasses.replace(header,parent_commit=commit.parent_commit).identity()
    old=array('old_full_%d.npy'%k);full=array('committed_full_%d.npy'%k);rr=array('R_candidate_%d.npy'%k)
    assert old.shape==full.shape==(45669,) and hmod.array_hash(old)==header.old_sha.hex()
    if previous is not None:
        assert np.array_equal(old,previous) and payload[:w.WORD_BYTES]==previous_H
    else:
        assert header.old_sha.hex()==scope['initial_full_digest'] and digest(payload[:w.WORD_BYTES])==scope['initial_H_sha256']
    assert np.array_equal(full[r_ids],rr)
    # Preserve raw Q24 feedback evidence. This does not recompute the H oracle.
    assert np.isfinite(full).all()
    timing=json.loads(reader.read('timing_%d.json'%k));assert timing['decision']==commit.parent_commit.hex()
    flow=array('official_flow_%d.npy'%k);assert flow.shape==(2,721) and np.isfinite(flow).all()
    source=json.loads(reader.read('source_%d.json'%k));frame=array('input_721_%d.npy'%k)
    assert source['run_id']==scope['run_id'] and digest(frame.tobytes())==source['hex_values_sha256']
    assert digest(reader.read('source_%d.png'%k))==source['png_sha256']
    times.append(timing);source_sequences.append(source['sequence'])
    previous=full;previous_H=candidate;parent=commit.parent_commit;txn=header.txn
assert all(a<=b for a,b in zip(source_sequences,source_sequences[1:]))

draws=[json.loads(row) for row in (root/'display_receipts.jsonl').read_text(encoding='utf-8').splitlines()]
for row in draws:
    k=row['step_id'];full=array('committed_full_%d.npy'%k);flow=array('official_flow_%d.npy'%k)
    assert row['run_id']==scope['run_id'] and row['session_id']==scope['session_id'] and row['serial']==row['state_token']==k+1
    assert row['spatial_values_sha256']==digest(spatial.extract(full).tobytes()) and row['flow_sha256']==digest(flow.tobytes())
    assert row['source_png_sha256']==digest(reader.read('source_%d.png'%k))
    assert row['unified_commit_sha256']==json.loads(reader.read('timing_%d.json'%k))['decision']
assert len(set(row['serial'] for row in draws))==len(draws)
observed=times[-1]['compute_elapsed_ns']/1e9
span=(draws[-1]['draw_server_monotonic_ns']-draws[0]['draw_server_monotonic_ns'])/1e9
report=dict(status='ACTUAL_60S_COMPUTE_OBSERVED_LOCAL_CHAIN_CHECKED_RUN_FAILED_FINALIZATION',
    run_id=scope['run_id'],session_id=scope['session_id'],model=scope['model'],numerical_profile=scope['numerical_profile'],
    GPU_device=load(root/'GPU_READY.json').get('device'),
    actual_compute_steps=steps,steps_with_matching_COMMIT_ACK=steps,
    observed_elapsed_last_commit_s=observed,
    elapsed_anchor='MinimalEngine construction before first STEP, not the unavailable final performance report',
    approximate_steps_per_s=steps/observed,model_dt_s=.005,model_time_s=steps*.005,
    saved_official_flows=steps,saved_complete_step_records=steps,
    camera=load(root/'camera_capture.json'),journal_bytes=(root/'pc/evidence.fvej').stat().st_size,
    journal_terminal=reader.terminal,journal_truncated=reader.truncated,
    display=dict(saved_verified_receipts=len(draws),first_step=draws[0]['step_id'],last_step=draws[-1]['step_id'],
        successful_receipt_span_s=span,successful_receipt_rate_hz=(len(draws)-1)/span,
        receipt_to_raf_p50_ms=float(np.percentile([x['receipt_to_render_estimate_ms'] for x in draws],50)),
        receipt_to_raf_upper_p95_ms=float(np.percentile([x['upper_ms'] for x in draws],95)),
        physical_scanout_measured=False),
    failure=dict(primary_saved_GUI_error=load(root/'ERROR_REQUEST.json')['error'],worker_error=result['error'],
        failed_draw_serial='NOT_RECORDED',expired_vs_duplicate='NOT_DISTINGUISHABLE_FROM_SAVED_ERROR',
        inference='A stale draw or duplicate receipt is possible; actual failing request is not saved, so neither is proven'),
    cleanup=exited,missing=[name for name in ('PS_FINISH.json','MINIMAL_PERFORMANCE.json','AUTO_AUDIT.json','AUTO_ACCEPTANCE.json','final_snapshot.json') if not (root/name).exists()],
    evidence_level='SAVED_PC_CHAIN_INPUT_STATE_FLOW_AND_BROWSER_RECEIPTS_ONLY',
    limitations=['No independent board FINISH/capture retrieved','No new same-old CPU numerical oracle or official decoder inference was run',
        'A complete PC batch chain without a terminal is not whole-run acceptance','No per-step PL raw capture independently audited'],
    whole_run_acceptance='FAILED_OR_IN_DOUBT',REALTIME_STREAM_PASS='NOT_CLAIMED',
    review_operations=dict(GPU_runs=0,camera_runs=0,board_connections=0,hardware_operations=0,reruns=0),
    files={name:sha(root/name) for name in ('scope.json','result.json','worker_exit.json','camera_capture.json','ERROR_REQUEST.json','display_receipts.jsonl')})
write(OUT/'ACTUAL_60S_REVIEW.json',report)
print(json.dumps({key:report[key] for key in ('status','actual_compute_steps','observed_elapsed_last_commit_s','approximate_steps_per_s','model_time_s','display','missing')},ensure_ascii=False))

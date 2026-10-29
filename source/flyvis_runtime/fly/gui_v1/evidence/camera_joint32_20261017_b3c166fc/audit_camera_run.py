"""Read-only audit of this run's closed PC/PS journals. No device execution."""
import dataclasses, hashlib, io, json, sys, time
from pathlib import Path
from types import SimpleNamespace
import numpy as np

GUI=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(GUI))
from live_protocol import Registry, load, require, sha, write
from joint_camera_control import hardware_module
from hybrid_full485 import Full485Contract
from hybrid_a3 import module
from projection_startup import load_static_projection

started=time.perf_counter()
root=GUI/'runtime/joint/f2fd7b4d54a4445daa8a15065c60088e'
out=Path(__file__).parent/'actual_audit'
out.mkdir(exist_ok=False)
scope,session,handoff,finish,result,manifest=[load(root/n) for n in ('scope.json','session.json','hardware_handoff.json','PS_FINISH.json','result.json','manifest.json')]
for name,digest in manifest['files'].items():require(sha(root/name)==digest,'RUN_MANIFEST '+name)
for name,digest in scope['source_sha256'].items():require(sha(GUI/name)==digest,'EXECUTED_SOURCE '+name)
require(result['status']=='STOPPED_PENDING_PS_AUDIT' and result['committed_steps']==32 and result['native_H_GPU_updates']==0,'PC_RESULT')
require(sha(root/'scope.json')==session['scope_sha256']==finish['scope_sha256'],'SCOPE_SHA')
require(finish['state']=='FINISHED_PENDING_AUDIT' and finish['requests']==finish['commits']==32 and finish['capture_closed'] and not finish['pending'] and not finish['poisoned'],'PS_FINISH')
ps_file=root/'ps_retrieved_authorized/evidence.fvej'
require(sha(ps_file)==finish['PS_capture_sha256'],'PS_CAPTURE_SHA')
Reader=hardware_module(handoff,'evidence_journal').JournalReader
pc,ps=Reader(root/'pc/evidence.fvej'),Reader(ps_file)
require(pc.context['run_id']==scope['run_id'] and pc.terminal['completed']==32 and ps.terminal['requests']==ps.terminal['acks']==32,'CLOSED_JOURNALS')
require(pc.terminal['reason']==ps.terminal['reason']=='STEP_LIMIT_COMPLETE','NORMAL_CLOSE')
c,reg=Full485Contract(),Registry()
w=c.wire
hmod=module('audit_camera3_h_step',c.paths['h_step'])
initial,initial_h,_=c.initial()
array=lambda name:np.load(io.BytesIO(pc.read(name)),allow_pickle=False)
j=lambda reader,name:json.loads(reader.read(name))
require(np.array_equal(array('initial_full.npy'),initial) and pc.read('initial_H.bin')==initial_h,'INITIAL_CANONICAL')
identity=j(pc,'session_identity.json')
require(identity['run_id']==scope['run_id'] and identity['session_id']==session['session_id'] and identity['mapping_sha256']==c.mapping_sha,'IDENTITY_MAP')
require(identity['hardware']['boot_id']==scope['boot_id'] and identity['hardware']['server_session']==scope['server_session'],'BOARD_IDENTITY')
with np.load(reg.path_for('parameters'),allow_pickle=False) as z:
    parameters={k:np.array(z[k],copy=True) for k in ('bias','time_const','effective_weight','source_global','target_global','input_node_index')}
src,dst,weights=[parameters[k] for k in ('source_global','target_global','effective_weight')]
inv=np.float32(1)/np.maximum(parameters['time_const'],np.float32(.005))
events=[json.loads(s) for s in ps.read('events.jsonl').splitlines()]
require(sum(e['event']=='START_ARMED' for e in events)==sum(e['event']=='NEURAL_CONNECTED' for e in events)==1,'ONE_START_CONNECTION')
require(sum(e['event']=='DMA_LAUNCH_RETURNED' for e in events)==32,'THREE_REAL_DMA')
wire_pc=sorted(n for n in pc.files if n.startswith('wire_'))
wire_ps=sorted(n for n in ps.files if n.startswith('wire_'))
require(len(wire_pc)==len(wire_ps)==130,'WIRE_COUNT')
for a,b in zip(wire_pc,wire_ps):
    require(('_tx_intent' in a and '_rx' in b) or ('_rx' in a and '_tx_intent' in b),'WIRE_DIRECTION')
    require(pc.read(a)==ps.read(b),'PC_PS_WIRE_BYTES')
barriers={b['sequence']:b for b in pc.batches}
batch_of={e['name']:b['sequence'] for b in pc.batches for e in b['records']}
ps_batch_of={e['name']:b['sequence'] for b in ps.batches for e in b['records']}
policy=j(ps,'PS_DURABILITY_SUMMARY.json')
require(scope['ps_durability_policy']==policy['policy']=='PS_COMMIT_ACK_DURABLE_TWO_BARRIERS/v1' and policy['normal_step_barriers']==2 and policy['completed']==32 and policy['deferred_wire_barriers']==64,'PS_DURABILITY_PROFILE')
require(scope['ps_evidence_adapter_sha256']==policy['adapter_sha256']==sha(GUI/'ps_commit_evidence.py'),'PS_POLICY_SOURCE_SHA')
ps_barriers={b['sequence']:b for b in ps.batches}
snapshots=[];previous=initial;canonical_h=initial_h;parent=bytes(32);previous_txn=bytes(16)
for k in range(32):
    old,frame,chemical,rr,full,spatial,flow=[array(f'{n}_{k}.npy') for n in ('old_full','input_721','chemical','R_candidate','committed_full','spatial','flow')]
    require(np.array_equal(old,previous),'FULL_STATE_FEEDBACK')
    raw=pc.read(f'request_{k}.bin');header=w.Header.unpack(raw[:w.HEADER_BYTES]);payload=raw[w.HEADER_BYTES:]
    require(raw==ps.read(f'request_{k}.bin') and header.step==k and header.asid.hex()==identity['hardware']['ASID'],'REQUEST_IDENTITY')
    require(header.old_sha.hex()==hmod.array_hash(old) and header.payload_sha==w.digest(payload) and header.parent_commit==parent and header.previous_txn==previous_txn,'SAME_OLD_COMMIT_CHAIN')
    require(payload[:w.WORD_BYTES]==canonical_h,'CANONICAL_RAW_PL_FEEDBACK')
    x=np.zeros(45669,dtype='<f4');x[parameters['input_node_index']]=frame
    require(payload[w.WORD_BYTES:2*w.WORD_BYTES]==w.encode_activity(chemical) and payload[2*w.WORD_BYTES:]==w.encode_activity(x[c.h]),'PAYLOAD_ORDER')
    currents=np.zeros(45669,dtype='<f4')
    np.add.at(currents,dst,weights*np.maximum(old[src],np.float32(0)))
    expected_r=(old+inv*(-old+parameters['bias']+currents+x)*np.float32(.005))[c.r]
    require(np.allclose(chemical,currents[c.h],atol=1e-5,rtol=1e-5),'INDEPENDENT_SAVED_CHEMICAL')
    require(np.allclose(rr,expected_r,atol=1e-5,rtol=1e-5),'INDEPENDENT_SAVED_R')
    candidate=pc.read(f'candidate_{k}.bin')
    require(candidate==ps.read(f'candidate_{k}.bin'),'PS_CANDIDATE_BYTES')
    integer_check=c.validate_H(payload,candidate)
    receipt=w.Header.unpack(pc.read(f'RESULT_{k}.bin'))
    require(receipt.identity()==header.identity() and receipt.op==w.RESULT and not receipt.status and receipt.payload_sha==w.digest(candidate),'RESULT_HEADER')
    commit=w.Header.unpack(pc.read(f'COMMIT_{k}.bin'));ack=w.Header.unpack(pc.read(f'ACK_{k}.bin'))
    require(ack==dataclasses.replace(commit,op=w.ACK),'EXACT_ACK')
    require(np.array_equal(full[c.h],c.decode(candidate)) and np.array_equal(full[c.r],rr) and np.array_equal(full,array(f'proposed_full_{k}.npy')),'UNIFIED_FULL_MERGE')
    snap=j(pc,f'committed_step_{k}.json');tx=snap['transaction']
    require(tx['unified_commit_sha256']==commit.parent_commit.hex() and commit.payload_sha==w.digest(b'') and tx['old_full_sha256']==hmod.array_hash(old) and tx['full_after_sha256']==hmod.array_hash(full),'PUBLISH_IDENTITY')
    require(snap['input_time_s']==k*.005 and snap['activity_time_s']==k*.005+.005 and snap['step_id']==k and snap['state_token']==k+1,'MODEL_TIMES')
    require(snap['source_kind']=='real_windows_camera' and snap['actual_new_computation'] and snap['numerical_profile']==scope['numerical_profile'],'ACTUAL_CAMERA_NOT_REPLAY')
    require(snap['PL_participating_global_ids']==c.spatial.ids.tolist(),'PL_GLOBAL_ID_MAP')
    source=j(pc,f'source_{k}.json');conversion=j(pc,f'conversion_{k}.json')
    require(hashlib.sha256(pc.read(f'source_{k}.png')).hexdigest()==source['png_sha256'] and hashlib.sha256(frame.tobytes()).hexdigest()==source['hex_values_sha256'],'SOURCE_721_IDENTITY')
    require(source==snap['source'] and conversion==snap['conversion'] and conversion['dependencies_sha256']==session['camera_dependencies_sha256'],'SOURCE_CONVERTER_IDENTITY')
    require(np.array_equal(spatial,c.spatial.extract(full)) and spatial.shape==(5768,),'SPACE_FROM_COMMITTED_FULL')
    require(flow.shape==(2,721) and np.isfinite(flow).all() and hashlib.sha256(flow.tobytes()).hexdigest()==snap['flow_sha256'],'OFFICIAL_FLOW_IDENTITY')
    require(barriers[batch_of[f'ACK_{k}.bin']]['barrier']=='COMMIT_ACK' and barriers[batch_of[f'committed_step_{k}.json']]['barrier']=='STEP_PUBLISHED' and batch_of[f'COMMIT_{k}.bin']<batch_of[f'ACK_{k}.bin']<batch_of[f'committed_step_{k}.json'],'PC_DURABLE_BEFORE_PUBLICATION')
    require(barriers[batch_of[f'COMMIT_{k}.bin']]['barrier']=='COMMIT_INTENT_BEFORE_SEND','PC_MERGED_INTENT_BEFORE_SEND')
    ps_step=ps_batch_of[f'wire_{2+4*k:03d}_rx.bin'];ps_result=ps_batch_of[f'wire_{3+4*k:03d}_tx_intent.bin']
    ps_commit=ps_batch_of[f'wire_{4+4*k:03d}_rx.bin'];ps_ack=ps_batch_of[f'wire_{5+4*k:03d}_tx_intent.bin']
    require(ps_step==ps_result==ps_commit<ps_ack and ps_barriers[ps_commit]['barrier']=='WIRE_RX' and ps_barriers[ps_ack]['barrier']=='WIRE_TX_INTENT','PS_TWO_BARRIER_COMMIT_ACK_ORDER')
    release=[e for e in events if e['event']=='RELEASE_CONFIRMED' and e['step']==k]
    sent=[e for e in events if e['event']=='ACK_SENT' and e['step']==k]
    require(len(release)==len(sent)==1 and release[0]['txn']==header.txn.hex() and release[0]['commit_sha']==tx['unified_commit_sha256'] and release[0]['state']==release[0]['error']==0 and release[0]['monotonic_ns']<sent[0]['monotonic_ns'],'PS_RELEASE_BEFORE_ACK')
    snapshot=dict(step=k,source_sequence=source['sequence'],capture_relative_s=source['relative_s'],input_time_s=snap['input_time_s'],activity_time_s=snap['activity_time_s'],wall_elapsed_s=snap['wall_elapsed_s'],PL_integer_values=5768,integer_error=integer_check['max_integer_code_error'],R_max_abs=float(np.max(np.abs(expected_r-rr))),chemical_max_abs=float(np.max(np.abs(currents[c.h]-chemical))),core_cycles=receipt.compute_cycles,adapter_cycles=receipt.transfer_cycles,STEP_roundtrip_ms=tx['PC_STEP_roundtrip_ns']/1e6,COMMIT_roundtrip_ms=tx['PC_COMMIT_roundtrip_ns']/1e6,unified_commit_sha256=tx['unified_commit_sha256'],eight_type_means=spatial.reshape(8,721).mean(axis=1,dtype=np.float64).tolist(),full_sha256=hmod.array_hash(full),flow_sha256=snap['flow_sha256'])
    (out/f'source_{k}.png').write_bytes(pc.read(f'source_{k}.png'))
    write(out/f'step_{k}.json',snapshot);snapshots.append(snapshot)
    previous,canonical_h,parent,previous_txn=full,candidate,commit.parent_commit,header.txn
require(finish['last_unified_commit_sha256']==parent.hex() and finish['last_txn']==previous_txn.hex(),'FINAL_ACK_CHAIN')
geometry,cached=load_static_projection(SimpleNamespace(adapter=SimpleNamespace(registry=reg),spatial=c.spatial))
draws=[json.loads(s) for s in (root/'display_receipts.jsonl').read_text().splitlines()]
for d in draws:
    k=d['step_id'];snap=snapshots[k]
    require(d['run_id']==scope['run_id'] and d['session_id']==session['session_id'] and d['state_token']==k+1 and d['unified_commit_sha256']==snap['unified_commit_sha256'],'DRAW_BINDING')
    rgba,_=cached.render(snap['eight_type_means'],geometry)
    require(hashlib.sha256(rgba.tobytes()).hexdigest()==d['skeleton_raw_sha256'] and cached.sha256==d['projection_cache_sha256'],'REAL_ACTIVITY_BRIGHTNESS_PIXELS')
    require(d['flow_sha256']==snap['flow_sha256'] and d['source_png_sha256']==j(pc,f'source_{k}.json')['png_sha256'],'DRAW_SOURCE_AND_FLOW')
capture,exit_state,active=[load(p) for p in (root/'camera_capture.json',root/'worker_exit.json',GUI/'runtime/joint_active.json')]
require(capture['closed'] and capture['error'] is None and exit_state['GPU_inflight_waited'] and exit_state['lease_closed'] and not exit_state['cleanup_errors'],'OWNED_RESOURCES_CLOSED')
require(active['session_id']==session['session_id'] and active.get('worker_exit_code',active.get('exit_codes',{}).get('joint_worker'))==0,'WORKER_CLEAN_STOP_GUI_RETAINED')
final=dict(status='PASS_CAMERA_GPU_FPGA_32STEP_SAVED_DATA_PATH_AUDIT',run_id=scope['run_id'],session_id=session['session_id'],steps=32,PL_integer_values_checked=sum(s['PL_integer_values'] for s in snapshots),PL_max_integer_error=0,canonical_feedback_words_checked=(len(snapshots)-1)*5768,Full_nodes=45669,GPU_R_nodes=39901,PL_H_nodes=5768,native_H_GPU_updates=0,numerical_profile=scope['numerical_profile'],PC_capture_sha256=sha(root/'pc/evidence.fvej'),PS_capture_sha256=sha(ps_file),same_old_R_and_chemical_independent_numpy_recheck=True,official_flow='ACTUAL_SAVED_ORIGINAL_DECODER_OUTPUT_AFTER_COMMIT_NOT_INDEPENDENTLY_REDECODED',captured_frames=capture['frames_delivered'],browser_draws=len(draws),browser_steps=[d['step_id'] for d in draws],all_steps_drawn=len({d['step_id'] for d in draws})==32,continuous_GUI_or_real_time_acceptance='NOT_CLAIMED',video_recording='PRESTART_RECORDING_SAVED_PENDING_INDEPENDENT_VIDEO_CHECK',model_duration_s=.160,snapshots=snapshots,elapsed_audit_s=time.perf_counter()-started,scope_source_files_verified=len(scope['source_sha256']),new_GPU_or_board_execution_during_audit=0)
write(out/'FINAL_AUDIT.json',final)
print(json.dumps({k:v for k,v in final.items() if k!='snapshots'},ensure_ascii=False))

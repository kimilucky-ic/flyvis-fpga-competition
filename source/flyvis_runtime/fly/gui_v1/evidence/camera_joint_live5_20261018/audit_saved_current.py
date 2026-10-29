"""CPU audit of this one run's saved values. No inference, socket or board call."""
import dataclasses,hashlib,io,json,sys,time
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;G=P.parents[1];sys.path.insert(0,str(G))
from live_protocol import load,sha,require,canonical,write
from joint_camera_control import hardware_module
from hybrid_full485 import Full485Contract
from hybrid_a3 import module
started=time.perf_counter();root=G/'runtime/joint/c59286b40c9c4c2e84a3e456a0856540'
scope,session,handoff,finish,result,perf=[load(root/n) for n in ['scope.json','session.json','hardware_handoff.json','PS_FINISH.json','result.json','MINIMAL_PERFORMANCE.json']]
require(scope['run_id']=='ad5b4adac2b941f59b4a5271d1bde1fe' and result['committed_steps']==100,'EXACT_CURRENT_RUN')
require(sha(root/'scope.json')==session['scope_sha256']==finish['scope_sha256'],'SCOPE_BYTES')
executed={n:sha(P/'executed_sources'/n)==v for n,v in scope['source_sha256'].items()};require(all(executed.values()),'EXECUTED_SOURCE_CHANGED')
require(finish['state']=='FINISHED_PENDING_AUDIT' and finish['requests']==finish['commits']==100
    and not finish['pending'] and not finish['poisoned'] and finish['capture_closed'],'CLEAN_BOARD_FINISH')
pspath=root/'ps_retrieved_authorized/evidence.fvej';require(sha(pspath)==finish['PS_capture_sha256'],'PS_CAPTURE_SHA')
Reader=hardware_module(handoff,'evidence_journal').JournalReader
pc=Reader(root/'pc/evidence.fvej');ps=Reader(pspath)
require(pc.context['run_id']==json.loads(ps.read('PREPARATION_RECEIPT.json'))['run_id']==scope['run_id'],'CAPTURE_RUN')
require(pc.terminal['completed']==100 and pc.terminal['recording']['complete'] and ps.terminal['requests']==ps.terminal['acks']==100,'COMPLETE_CAPTURES')
c=Full485Contract();w=c.wire;reg=c.reg;hmod=module('audit_current_minimal_h_step',c.paths['h_step'])
with np.load(reg.path_for('parameters'),allow_pickle=False) as z:
    params={n:np.array(z[n],copy=True) for n in ['bias','time_const','effective_weight','source_global','target_global','input_node_index']}
inv=np.float32(1)/np.maximum(params['time_const'],np.float32(.005))
old_expected,old_words,_=c.initial();parent=bytes(32);previous_txn=bytes(16)
arr=lambda n:np.load(io.BytesIO(pc.read(n)),allow_pickle=False)
max_r=max_chem=0.;rows=[]
for k in range(100):
    old,frame,chemical,rr,full=[arr('%s_%d.npy'%(n,k)) for n in ['old_full','input_721','chemical','R_candidate','committed_full']]
    require(np.array_equal(old,old_expected),'FULL_STATE_FEEDBACK')
    raw=pc.read('request_%d.bin'%k);header=w.Header.unpack(raw[:w.HEADER_BYTES]);payload=raw[w.HEADER_BYTES:]
    require(header.step==k and header.epoch==0 and header.old_sha.hex()==hmod.array_hash(old)
        and header.payload_sha==w.digest(payload) and header.parent_commit==parent and header.previous_txn==previous_txn,'REQUEST_IDENTITY_CHAIN')
    require(payload[:w.WORD_BYTES]==old_words,'RAW_INTEGER_FEEDBACK')
    x=np.zeros(45669,dtype='<f4');x[params['input_node_index']]=frame
    require(payload[w.WORD_BYTES:2*w.WORD_BYTES]==w.encode_activity(chemical)
        and payload[2*w.WORD_BYTES:]==w.encode_activity(x[c.h]),'CURRENT_H_INPUTS')
    currents=np.zeros(45669,dtype='<f4')
    np.add.at(currents,params['target_global'],params['effective_weight']*np.maximum(old[params['source_global']],np.float32(0)))
    expected_r=(old+inv*(-old+params['bias']+currents+x)*np.float32(.005))[c.r]
    max_r=max(max_r,float(np.max(np.abs(rr-expected_r))));max_chem=max(max_chem,float(np.max(np.abs(chemical-currents[c.h]))))
    require(np.allclose(rr,expected_r,atol=1e-5,rtol=1e-5) and np.allclose(chemical,currents[c.h],atol=1e-5,rtol=1e-5),'SAME_OLD_NUMPY_REFERENCE')
    candidate=pc.read('candidate_%d.bin'%k);expected_h,_=c.expected_H(payload)
    require(candidate==expected_h,'ALL_Q24_INTEGERS')
    receipt=w.Header.unpack(pc.read('RESULT_%d.bin'%k));commit=w.Header.unpack(pc.read('COMMIT_%d.bin'%k));ack=w.Header.unpack(pc.read('ACK_%d.bin'%k))
    require(receipt.identity()==header.identity() and receipt.op==w.RESULT and not receipt.status
        and receipt.payload_sha==w.digest(candidate) and receipt.compute_cycles==57681,'RESULT_BINDING')
    require(ack==dataclasses.replace(commit,op=w.ACK),'EXACT_COMMIT_ACK')
    require(np.array_equal(full[c.h],c.decode(candidate)) and np.array_equal(full[c.r],rr),'UNIFIED_MERGE')
    binding=dict(run_id=scope['run_id'],comparison_id=scope['comparison_id'],condition_id='CURRENT_CAMERA',epoch=0,step_id=k,
        old_full_digest=hmod.array_hash(old),input_digest=hmod.array_hash(x),mapping_sha256=c.mapping_sha,model=c.registry['model'],
        native_H_update_count=0,execution_kind='LIVE_CAMERA_GPU_FPGA_PENDING_AUDIT',chemical_digest=hmod.array_hash(chemical))
    decision=canonical(dict(schema='flyvis-unified-commit/v1',binding=binding,transaction=header.txn.hex(),request_payload_sha=header.payload_sha.hex(),
        candidate_H_sha=receipt.payload_sha.hex(),candidate_R_sha=hmod.array_hash(rr),full_after_sha=hmod.array_hash(full),parent_commit=parent.hex(),numeric_profile=w.PROFILE))
    require(commit.parent_commit.hex()==decision and commit.identity()==dataclasses.replace(header,parent_commit=bytes.fromhex(decision)).identity(),'UNIFIED_COMMIT_RECOMPUTE')
    source=json.loads(pc.read('source_%d.json'%k));conversion=json.loads(pc.read('conversion_%d.json'%k))
    require(hashlib.sha256(pc.read('source_%d.png'%k)).hexdigest()==source['png_sha256']
        and hashlib.sha256(frame.tobytes()).hexdigest()==source['hex_values_sha256']
        and conversion['dependencies_sha256']==session['camera_dependencies_sha256'],'REAL_INPUT_AND_CONVERTER_IDENTITY')
    require(source['run_id']==scope['run_id'],'SOURCE_RUN')
    flow=arr('official_flow_%d.npy'%k)
    require(flow.shape==(2,721) and np.isfinite(flow).all(),'SAVED_OFFICIAL_FLOW_SHAPE')
    old_expected=full;old_words=candidate;parent=bytes.fromhex(decision);previous_txn=header.txn
    rows.append(dict(step=k,source_sequence=source['source_sequence'] if 'source_sequence' in source else source.get('sequence'),unified_commit=decision))
require(parent.hex()==finish['last_unified_commit_sha256'] and previous_txn.hex()==finish['last_txn'],'FINAL_BOARD_COMMIT')
out=dict(status='PASS_SAVED_PC_NUMERICAL_CHAIN_AND_SIGNED_PS_FINISH',run_id=scope['run_id'],steps=100,
    PL_Q24_values_checked=100*5768,PL_integer_error=0,raw_H_feedback_words_checked=99*5768,
    full_state_values_checked=100*45669,R_max_abs=max_r,chemical_max_abs=max_chem,tolerance=dict(atol=1e-5,rtol=1e-5),
    PC_capture_sha256=sha(root/'pc/evidence.fvej'),PS_capture_sha256=sha(pspath),executed_source_hashes_matched=executed,
    actual_compute_wall_s=perf['total_compute_wall_s'],actual_compute_steps_per_s=100/perf['total_compute_wall_s'],
    limitations=['PS minimal journal stores timing and signed finish, not independent per-step raw candidate captures',
        'Async evidence is not durable before ACK; no 200Hz realtime claim'],
    neural_GPU_runs=0,board_operations=0,CPU_audit_wall_s=time.perf_counter()-started,rows=rows)
write(P/'SAVED_DATA_AUDIT.json',out)
print(json.dumps({k:v for k,v in out.items() if k not in ['rows','executed_source_hashes_matched','limitations']},ensure_ascii=True,indent=2))

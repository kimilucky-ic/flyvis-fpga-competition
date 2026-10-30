"""Automatic post-run audit of the existing minimal contract, no neural execution.

Reuses accepted saved-data checks: original same-old NumPy reference, Q24
oracle, exact COMMIT/ACK and raw feedback. Signed PS finish/timing remains a
lower evidence level than dual independent per-step PS byte captures.
"""
import base64,dataclasses,hashlib,io,json,os,time
from pathlib import Path
import numpy as np
from live_protocol import HERE,load,sha,require,canonical,write,host_path
from joint_camera_control import hardware_module,board_client
from hybrid_full485 import Full485Contract
from hybrid_a3 import module


def retrieve(root):
    finish=load(root/'PS_FINISH.json');out=root/'ps_auto'
    require(finish['state']=='FINISHED_PENDING_AUDIT' and finish['capture_closed']
        and finish['requests']==finish['commits']==finish['completed_steps']
        and not finish['pending'] and not finish['poisoned'],'PS_NOT_CLOSED')
    if out.exists():
        require(sha(out/'evidence.fvej')==finish['PS_capture_sha256'],'EXISTING_PS_CAPTURE_INCOMPLETE')
        return
    out.mkdir()
    client=board_client(load(root/'hardware_handoff.json'));client.ready_id=finish['ready_id']
    begin=client.request('/evidence_begin',{})
    require(begin['capture_sha256']==finish['PS_capture_sha256'] and 0<begin['capture_bytes']<=512*1024*1024,'PS_CAPTURE_IDENTITY')
    write(out/'begin.json',begin);offset=0
    with (out/'evidence.fvej').open('xb') as stream:
        while offset<begin['capture_bytes']:
            packet=client.request('/evidence_chunk',dict(offset=offset))
            data=base64.b64decode(packet['data_b64'],validate=True)
            require(packet['offset']==offset and packet['bytes']==len(data) and packet['capture_bytes']==begin['capture_bytes']
                and hashlib.sha256(data).hexdigest()==packet['chunk_sha256'],'PS_CAPTURE_CHUNK')
            stream.write(data);offset+=len(data)
        stream.flush();os.fsync(stream.fileno())
    require(sha(out/'evidence.fvej')==finish['PS_capture_sha256'],'PS_CAPTURE_SHA')


def audit_saved(root,*,output=None,sources=None,ps_capture=None):
    root=host_path(root).resolve();started=time.perf_counter()
    require(root.parent==(HERE/'runtime/joint').resolve(),'AUDIT_ROOT')
    scope,session,handoff,finish,result,perf=[load(root/n) for n in ['scope.json','session.json','hardware_handoff.json','PS_FINISH.json','result.json','MINIMAL_PERFORMANCE.json']]
    n=result['committed_steps']
    require(result['status']=='STOPPED_PENDING_PS_AUDIT' and 0<n<=scope['max_steps'],'NOT_CLEAN_COMPUTE')
    exited=load(root/'worker_exit.json')
    require(exited['run_id']==scope['run_id'] and exited['committed_steps']==n and exited['GPU_inflight_waited'] and exited['lease_closed'] and not exited['cleanup_errors'],'GPU_EXIT_NOT_CLEAN')
    require(sha(root/'scope.json')==session['scope_sha256']==finish['scope_sha256'],'SCOPE_BYTES')
    sources=host_path(sources) if sources else root/'executed_sources'
    executed={n:sha(sources/n)==v for n,v in scope['source_sha256'].items()};require(all(executed.values()),'EXECUTED_SOURCE_CHANGED')
    require(finish['state']=='FINISHED_PENDING_AUDIT' and finish['requests']==finish['commits']==n
        and not finish['pending'] and not finish['poisoned'] and finish['capture_closed'],'CLEAN_BOARD_FINISH')
    pspath=host_path(ps_capture) if ps_capture else root/'ps_auto/evidence.fvej';require(sha(pspath)==finish['PS_capture_sha256'],'PS_CAPTURE_SHA')
    Reader=hardware_module(handoff,'evidence_journal').JournalReader
    pc=Reader(root/'pc/evidence.fvej');ps=Reader(pspath)
    require(pc.context['run_id']==json.loads(ps.read('PREPARATION_RECEIPT.json'))['run_id']==scope['run_id'],'CAPTURE_RUN')
    require(pc.terminal['completed']==n and pc.terminal['recording']['complete'] and ps.terminal['requests']==ps.terminal['acks']==n,'COMPLETE_CAPTURES')
    from frozen28_input import joint_contract
    c=joint_contract(scope);w=c.wire;reg=c.reg;hmod=module('audit_current_minimal_h_step',c.paths['h_step'])
    with np.load(reg.path_for('parameters'),allow_pickle=False) as z:
        params={n:np.array(z[n],copy=True) for n in ['bias','time_const','effective_weight','source_global','target_global','input_node_index']}
    inv=np.float32(1)/np.maximum(params['time_const'],np.float32(.005))
    old_expected,old_words,_=c.initial();parent=bytes(32);previous_txn=bytes(16)
    arr=lambda n:np.load(io.BytesIO(pc.read(n)),allow_pickle=False)
    max_r=max_chem=0.;rows=[]
    for k in range(n):
        old,frame,chemical,rr,full=[arr('%s_%d.npy'%(n,k)) for n in ['old_full','input_721','chemical','R_candidate','committed_full']]
        require(np.array_equal(old,old_expected),'FULL_STATE_FEEDBACK')
        if scope.get('scientific_input'):
            from frozen28_input import Frozen28Input
            if k==0:scientific_feed=Frozen28Input(scope['run_id'],scope['condition_id'])
            frozen=scientific_feed.for_step(k)
            require(np.array_equal(frame,np.asarray(frozen['values'],dtype='<f4')),'SCIENTIFIC_AUDIT_INPUT_STEP')
            require(pc.read('source_%d.png'%k)==__import__('base64').b64decode(frozen['png']),'SCIENTIFIC_AUDIT_PIXELS')
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
        binding=dict(run_id=scope['run_id'],comparison_id=scope['comparison_id'],condition_id=scope['condition_id'],epoch=0,step_id=k,
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
    out=dict(status='PASS_SAVED_PC_NUMERICAL_CHAIN_AND_SIGNED_PS_FINISH',run_id=scope['run_id'],steps=n,
        PL_Q24_values_checked=n*5768,PL_integer_error=0,raw_H_feedback_words_checked=(n-1)*5768,
        full_state_values_checked=n*45669,R_max_abs=max_r,chemical_max_abs=max_chem,tolerance=dict(atol=1e-5,rtol=1e-5),
        PC_capture_sha256=sha(root/'pc/evidence.fvej'),PS_capture_sha256=sha(pspath),executed_source_hashes_matched=executed,
        actual_compute_wall_s=perf['total_compute_wall_s'],actual_compute_steps_per_s=n/perf['total_compute_wall_s'],
        limitations=['PS minimal journal stores timing and signed finish, not independent per-step raw candidate captures',
            'Async evidence is not durable before ACK; no 200Hz realtime claim'],
        neural_GPU_runs=0,board_operations=0,CPU_audit_wall_s=time.perf_counter()-started,rows=rows)
    if scope.get('scientific_input'):out.update(scientific_input=scope['scientific_input'],scientific_condition_complete=n==485,expected_steps=485)
    write(output or root/'AUTO_AUDIT.json',out)
    return out

def approve(root):
    root=host_path(root);scope=load(root/'scope.json');finish=load(root/'PS_FINISH.json')
    audit=load(root/'AUTO_AUDIT.json');handoff=load(root/'hardware_handoff.json')
    require(audit['status']=='PASS_SAVED_PC_NUMERICAL_CHAIN_AND_SIGNED_PS_FINISH'
        and audit['run_id']==scope['run_id'] and audit['steps']==finish['completed_steps'],'AUTO_AUDIT_NOT_ACCEPTED')
    names=('scope.json','session.json','PS_FINISH.json','worker_exit.json','result.json','AUTO_AUDIT.json','pc/evidence.fvej','ps_auto/evidence.fvej')
    body=dict(schema='flyvis-camera-auto-acceptance/v1',run_id=scope['run_id'],session_id=scope['session_id'],
        files={n:sha(root/n) for n in names},fresh=scope['fresh_initialized_parent'],
        completed_fresh={k:finish[k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id',
            'completed_steps','last_unified_commit_sha256','last_txn','PS_capture_sha256')},
        evidence_level='SAVED_PC_NUMERICAL_CHAIN_AND_SIGNED_PS_FINISH_NOT_DUAL_RAW_CAPTURE')
    if scope.get('scientific_input'):body.update(scientific_input=scope['scientific_input'],scientific_condition_complete=audit.get('scientific_condition_complete') is True)
    helpers=hardware_module(handoff,'control2')
    write(root/'AUTO_ACCEPTANCE.json',helpers.sign(body,handoff['control_config']['control_key']))
    return dict(fresh=body['fresh'],completed_fresh=body['completed_fresh'])

def accepted_parent(root):
    root=host_path(root).resolve()
    require(root.parent==(HERE/'runtime/joint').resolve(),'AUTO_ACCEPTANCE_ROOT')
    handoff=load(root/'hardware_handoff.json');helpers=hardware_module(handoff,'control2')
    body=helpers.verified(load(root/'AUTO_ACCEPTANCE.json'),handoff['control_config']['control_key'])
    scope=load(root/'scope.json')
    require(body['schema']=='flyvis-camera-auto-acceptance/v1' and body['run_id']==scope['run_id']
        and body['session_id']==scope['session_id']==root.name,'AUTO_ACCEPTANCE_IDENTITY')
    for name,digest in body['files'].items():require(sha(root/name)==digest,'AUTO_ACCEPTANCE_CHANGED '+name)
    return dict(fresh=body['fresh'],completed_fresh=body['completed_fresh'])

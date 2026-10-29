"""Bounded real Client -> existing Coordinator -> GPU publication adapter.

No automatic launch. connect_live requires a separate explicit short-run scope,
independently accepted board receipts, and an already leased original CUDA pair.
Fixtures can only use the private test entry and never produce admitted PL IDs.
"""
import dataclasses
from datetime import datetime,timezone
import io,json,os,time,uuid,threading
from pathlib import Path
import numpy as np
from hybrid_a3 import _CoordinatorBarrier
from live_protocol import canonical,require,sha,load


class DurableEvidence:
    def init__(self,root):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=False);self.wire_index=0
    def blob(self,name,data):
        path=self.root/name
        require(path.parent==self.root and path.name==name,'EVIDENCE_PATH')
        with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        return {'path':name,'sha256':sha(path),'bytes':len(data)}
    def array(self,name,value):
        buffer=io.BytesIO();np.save(buffer,value,allow_pickle=False);return self.blob(name,buffer.getvalue())
    def json(self,name,value):
        return self.blob(name,json.dumps(value,sort_keys=True,allow_nan=False).encode())
    def event(self,value):
        with (self.root/'transactions.jsonl').open('a',encoding='utf8') as f:
            f.write(json.dumps(value,sort_keys=True,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
    def observe(self,direction,wire):
        self.blob(f'wire_{self.wire_index:03}_{direction}.bin',wire);self.wire_index+=1


def validate_short_scope(scope,c,acceptance,now=None):
    """All checks precede Client construction. This function grants no authority."""
    now=now or datetime.now(timezone.utc)
    require(scope.get('schema')=='flyvis-approved-joint-short/v1' and scope.get('status')=='APPROVED_BY_HUMAN'
        and bool(scope.get('human_authorization_reference')),'SHORT_JOINT_NOT_AUTHORIZED')
    require(scope.get('condition')=='ON60' and scope.get('model_steps')==[200,201,202]
        and scope.get('max_requests')==3 and scope.get('max_commits')==3 and scope.get('automatic_retry') is False,'EXACT_THREE_STEP_SCOPE')
    require(scope.get('board_acceptance_sha256')==canonical(acceptance) and acceptance.get('status')=='PASS_INDEPENDENT_SAVED_BOARD_REPLAY'
        and acceptance.get('requests')==3 and acceptance.get('values')==17304,'BOARD_ACCEPTANCE_REQUIRED')
    require(scope.get('bit_sha256')==c.wire.BIT_SHA and scope.get('hwh_sha256')==c.wire.HWH_SHA
        and scope.get('mapping_sha256')==c.mapping_sha and scope.get('tolerance')==c.tolerance,'SCOPE_PROFILE')
    require(scope.get('endpoint')=={'host':'192.168.2.99','port':5768} and scope.get('expected_boot_id')
        and scope.get('expected_server_session') and scope['expected_server_session']!=acceptance['old_server_session'],'FRESH_APPROVED_BOARD_SESSION')
    begin=datetime.fromisoformat(scope['start_utc']);end=datetime.fromisoformat(scope['end_utc'])
    require(begin.tzinfo and end.tzinfo and 0<(end-begin).total_seconds()<=600 and begin<=now<end,'SHORT_SCOPE_EXPIRED')
    require(scope.get('model')==c.registry['model'] and scope.get('gpu_lease_id') and scope.get('run_id')
        and scope.get('comparison_id') and scope.get('input_sha256')=='67e490d4790a7bec5ad90dabd6ced7747c797a720a9e197d2750903b48350fa7','INPUT_RUN_MODEL_SCOPE')


class _JointAdapter:
    """Single owner. Only connect_live sets a live origin; tests are explicit."""
    def init__(self,c,client,producer,decoder,evidence,scope,gate,publication_factory,publication_reader,*,origin,frames=None,candidate_validator=None):
        require(origin in ('CPU_PROTOCOL_TEST','LIVE_ENDPOINT_PENDING_PS_AUDIT'),'ORIGIN')
        self.c=c;self.w=c.wire;self.client=client;self.producer=producer;self.decoder=decoder
        self.evidence=evidence;self.scope=scope;self.gate=gate;self.origin=origin;self.completed=0;self.failed=False
        self.publication_reader=publication_reader;self.owner=threading.Lock()
        self.candidate_validator=candidate_validator
        if frames is not None:self._frames=np.array(frames,copy=True)
        self.start_step,self.step_count=(0,485) if scope.get('schema')=='flyvis-approved-joint-full485/v1' else (200,3)
        a,words,_=c.initial()
        self.barrier=_CoordinatorBarrier(c,a,words,scope['run_id'],scope['comparison_id'],'ON60',client.asid,evidence.event,
            execution_kind=origin,start_step=self.start_step,publication_factory=publication_factory)
        self.evidence.array('initial_full.npy',a);self.evidence.blob('initial_H.bin',words)
        self.evidence.json('run_scope.json',scope);self.evidence.json('firmware_session.json',client.attestation)

    def step(self,hex_frame):
        require(self.owner.acquire(blocking=False),'JOINT_STEP_ALREADY_IN_PROGRESS')
        try:return self._step(hex_frame)
        finally:self.owner.release()

    def _step(self,hex_frame):
        b=self.barrier;start=time.perf_counter_ns();k=b.state_token
        try:
            require(not self.failed and self.completed<self.step_count and k==self.start_step+self.completed,'BOUNDED_STEP_ORDER')
            self.gate();frame=np.asarray(hex_frame)
            require(frame.dtype==np.float32 and frame.shape==(721,) and np.isfinite(frame).all(),'INPUT_SCHEMA')
            # Every current source frame is pinned; source selection cannot drift.
            from live_protocol import Registry
            if not hasattr(self,'_frames'):self._frames=np.array(Registry().input('ON60')[0,self.start_step:self.start_step+self.step_count,0],copy=True)
            require(np.array_equal(frame,self._frames[self.completed]),'FROZEN_ON60_STEP_MISMATCH')
            old=b.state;old_digest=b.hmod.array_hash(old)
            require(np.array_equal(self.publication_reader(b.publication),old),'GPU_VISIBLE_OLD_STATE_MISMATCH')
            output=self.producer(b.publication,frame,k)
            require(b.hmod.array_hash(b.state)==old_digest,'VISIBLE_STATE_MUTATED')
            software_check=self.candidate_validator(old,output,k) if self.candidate_validator else {'status':'NOT_REQUESTED'}
            x=output['x_full'];chem=output['chemical_H'];new_r=output['new_R'];r_ids=output['r_ids']
            cb={**b.binding(x),'chemical_digest':b.hmod.array_hash(chem)}
            rb={**b.binding(x),'r_candidate_digest':b.hmod.array_hash(new_r),'r_ids_digest':b.hmod.array_hash(r_ids)}
            raw,payload=b.prepare(uuid.uuid4().bytes,x,chem,cb);header=self.w.Header.unpack(raw)
            self.evidence.array(f'old_full_{k}.npy',old);self.evidence.array(f'input_721_{k}.npy',frame)
            self.evidence.array(f'chemical_{k}.npy',chem);self.evidence.array(f'R_candidate_{k}.npy',new_r)
            self.evidence.blob(f'request_{k}.bin',raw+payload)
            self.gate();tick=time.perf_counter_ns()
            identity={name:getattr(header,name) for name in ('asid','txn','step','old_sha','epoch','config','parent_commit','previous_txn')}
            n=self.w.WORD_BYTES
            candidate,receipt=self.client.step(payload[:n],payload[n:2*n],payload[2*n:],identity)
            step_ns=time.perf_counter_ns()-tick
            check=self.c.validate_H(payload,candidate)  # current payload, exact integer reference
            self.evidence.blob(f'candidate_{k}.bin',candidate);self.evidence.blob(f'RESULT_{k}.bin',receipt.pack())
            staged=b.accept_candidates(receipt.pack(),candidate,new_r,r_ids,rb)
            p=b.pending
            # Full candidate and all evidence are durable before COMMIT can leave.
            self.evidence.array(f'proposed_full_{k}.npy',p['staged'].state)
            self.evidence.json(f'validation_{k}.json',{**check,**staged,'old_full_sha':old_digest,'software_reference':software_check})
            self.gate();commit=b.commit_frame();self.evidence.blob(f'COMMIT_{k}.bin',commit)
            tick=time.perf_counter_ns();ack=self.client.commit(bytes.fromhex(staged['unified_commit_sha256']))
            commit_ns=time.perf_counter_ns()-tick
            self.evidence.blob(f'ACK_{k}.bin',ack.pack())
            # An expired scope after an acknowledged commit must still record the
            # known committed state; it cannot erase the fact that PS committed.
            full=b.acknowledge(ack.pack());self.completed+=1
            self.evidence.array(f'committed_full_{k}.npy',full)
            self.gate()
            flow=np.asarray(self.decoder(full))
            require(flow.shape==(2,721) and flow.dtype==np.float32 and np.isfinite(flow).all(),'OFFICIAL_FLOW_SCHEMA')
            spatial=self.c.spatial.extract(full)
            self.evidence.array(f'spatial_{k}.npy',spatial);self.evidence.array(f'flow_{k}.npy',flow)
            row=dict(schema='flyvis-joint-committed-step/v1',run_id=self.scope['run_id'],model_step=k,local_step=k-self.start_step,
                state_token=b.state_token,input_time_s=k*.005-1,activity_time_s=k*.005-1+.005,
                old_full_sha=old_digest,full_after_sha=b.hmod.array_hash(full),input_sha=b.hmod.array_hash(frame),
                mapping_sha=self.c.mapping_sha,unified_commit_sha=staged['unified_commit_sha256'],
                ASID=self.client.asid.hex(),transaction=header.txn.hex(),boot_id=self.client.attestation['boot_id'],
                server_session=self.client.attestation['server_session'],core_cycles=receipt.compute_cycles,adapter_cycles=receipt.transfer_cycles,
                PC_STEP_roundtrip_ns=step_ns,PC_COMMIT_roundtrip_ns=commit_ns,step_wall_ns=time.perf_counter_ns()-start,
                integer_check=check,commit='ACK_MATCHED_AND_PUBLISHED',execution_kind=self.origin,
                PS_run_audit='PENDING',PL_proven_global_ids=[],realtime_claim=False)
            self.evidence.json(f'committed_step_{k}.json',row)
            return row
        except BaseException as exc:
            self.failed=True;b.fail(exc)
            try:self.evidence.event({'event':'DISPLAY_REVOKED','error':repr(exc),'visible_state_token':b.state_token,'phase':b.phase})
            except Exception:pass
            # Closing TCP is not ABORT/reset/retry. In-flight board evidence stays.
            self.client.close()
            raise

    def close(self):self.client.close()


def connect_live(c,scope,acceptance,producer,decoder,output_directory,check_gpu_lease,*,candidate_validator=None):
    """Only explicit caller invocation connects; no programming/MMIO/restart here.

    The caller must hold the existing AutoRunner GPU lease throughout this run.
    A prepared plan or historical replay receipt is insufficient authorization.
    """
    validator=validate_short_scope
    if scope.get('schema')=='flyvis-approved-joint-full485/v1':
        from hybrid_full485 import validate_full_scope
        validator=validate_full_scope
    validator(scope,c,acceptance)
    from hybrid_joint_evidence import board_acceptance
    require(acceptance==board_acceptance(c),'INDEPENDENT_BOARD_RECEIPT_REQUIRED')
    from hybrid_gpu import GPUCandidates
    require(type(producer) is GPUCandidates and producer.c is c and producer.oracle.device.type=='cuda','ORIGINAL_GPU_PRODUCER_REQUIRED')
    import inspect
    from live_protocol import Registry,host_path
    reg=Registry()
    require(type(decoder).__name__=='OfficialDecoderService'
        and host_path(inspect.getfile(type(decoder))).resolve()==reg.path_for('decoder').resolve(),'OFFICIAL_DECODER_REQUIRED')
    torch=producer.torch;device=producer.oracle.device
    def gate():
        validator(scope,c,acceptance);check_gpu_lease();c.unchanged()
    def publication(full):
        tensor=torch.as_tensor(np.array(full,copy=True),device=device,dtype=torch.float32)
        torch.cuda.synchronize()
        require(np.array_equal(tensor.detach().cpu().numpy(),full),'GPU_STAGING_COPY_MISMATCH')
        return tensor
    first,last=(0,485) if scope.get('schema')=='flyvis-approved-joint-full485/v1' else (200,203)
    frames=np.array(reg.input('ON60')[0,first:last,0],copy=True)
    gate();evidence=DurableEvidence(output_directory);client=None
    try:
        client=c.wire.Client(scope['endpoint']['host'],scope['endpoint']['port'],observer=evidence.observe)
        a=client.attestation
        require(a['boot_id']==scope['expected_boot_id'] and a['server_session']==scope['expected_server_session'],'NEW_SESSION_IDENTITY')
        return _JointAdapter(c,client,lambda state,frame,k:producer.produce(state,torch.as_tensor(frame.copy(),device=device),run_id=scope['run_id'],step_id=k),
            lambda full:decoder.decode(full[None,None],chunk_frames=1)[0,0],evidence,scope,gate,publication,
            lambda tensor:tensor.detach().cpu().numpy(),origin='LIVE_ENDPOINT_PENDING_PS_AUDIT',frames=frames,candidate_validator=candidate_validator)
    except BaseException:
        if client is not None:client.close()
        raise

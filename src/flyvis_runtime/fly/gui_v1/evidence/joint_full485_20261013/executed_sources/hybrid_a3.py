"""CPU-only A3R1 wire/identity preparation. No sockets, GPU or board execution.

Use the frozen A3 Header/codec and original Coordinator.commit validation.
The rehearsal cannot be promoted to hardware evidence by a caller-supplied flag.
"""
import copy
import dataclasses
import importlib.util
import sys
import threading
from functools import lru_cache
from types import SimpleNamespace
import numpy as np
from live_protocol import HERE,canonical,host_path,load,require,sha
from spatial_state import SpatialRegistry


def module(name,path):
    if name in sys.modules:
        require(host_path(sys.modules[name].__file__).resolve()==path.resolve(),'MODULE_SOURCE_CONFLICT')
        return sys.modules[name]
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m


class A3Contract:
    def init__(self):
        self.registry=load(HERE/'hybrid_registry.json');self.paths={};self.stamps={}
        require(self.registry['schema']=='flyvis-hybrid-integration-registry/v1','HYBRID_SCHEMA')
        require(self.registry['board_backend'] is None and not self.registry['execution_enabled'],'HARDWARE_BACKEND_NOT_ADMITTED')
        for key,pin in self.registry['pins'].items():
            path=host_path(pin['path']);require(sha(path)==pin['sha256'],'HYBRID_SOURCE_CHANGED '+key)
            self.paths[key]=path;self.stamps[key]=(path.stat().st_size,path.stat().st_mtime_ns)
        self.wire=module('gui_frozen_A3R1_protocol',self.paths['a3_protocol'])
        self.fixture=load(self.paths['a3_fixture']);payload=self.fixture['identity_payload']
        require(self.fixture['config_id']==self.wire.CONFIG.hex(),'A3_CONFIG')
        self.h=np.asarray(payload['ordered_global_H_ids'],dtype='<i8')
        spatial=SpatialRegistry();self.spatial=spatial
        require(self.registry['model']==spatial.data['model'],'HYBRID_MODEL')
        require(self.h.shape==(5768,) and len(set(self.h.tolist()))==5768 and set(self.h)==set(spatial.ids),'A3_EXACT_H_SET')
        self.h.flags.writeable=False;self.r=np.setdiff1d(np.arange(45669,dtype='<i8'),self.h);self.r.flags.writeable=False
        positions={int(g):i for i,g in enumerate(self.h)}
        self.spatial_from_wire=np.asarray([positions[int(g)] for g in spatial.ids],dtype='<i8')
        self.mapping_sha=canonical(dict(ordered_H=self.h.tolist(),ordered_R=self.r.tolist(),spatial_from_wire=self.spatial_from_wire.tolist(),
            config=self.fixture['config_id'],model=self.registry['model'],node_source_sha=spatial.data['pins']['nodes']['sha256']))
    def unchanged(self):
        for k,p in self.paths.items():require((p.stat().st_size,p.stat().st_mtime_ns)==self.stamps[k],'HYBRID_SOURCE_CHANGED '+k)
        self.spatial.unchanged()
    def decode(self,words):
        require(type(words) is bytes and len(words)==self.wire.WORD_BYTES,'A3_WORD_LENGTH');self.wire.validate_words(words)
        return (np.frombuffer(words,dtype='<i4').astype(np.float64)/(1<<24)).astype('<f4')
    def status(self):
        self.unchanged();a=load(self.paths['a3_result']);b=load(self.paths['board67_verification'])
        return dict(schema='flyvis-hybrid-integration/v1',backend='NOT_CONNECTED',FPGA_status='NOT_CONNECTED',execution_enabled=False,
            PL_proven_global_ids=[],mapping_sha256=self.mapping_sha,planned_H_count=len(self.h),R_count=len(self.r),
            mapping=dict(wire_order_global_ids=self.h.tolist(),spatial_from_wire=self.spatial_from_wire.tolist(),spatial_map_sha256=self.spatial.digest),
            A3R1=dict(evidence_level='SYSTEM_SIMULATION_AND_FIRMWARE',status=a['status'],board=a['board'],GPU_feedback_closed_loop=a['GPU_feedback_closed_loop'],
                image_sha256=a['image_sha256'],config=self.fixture['config_id']),
            H67=dict(evidence_level='ACTUAL_BOARD_RECORDED_32_REQUEST_REPLAY',display_kind='offline replay',requests=b['requests_completed'],
                outputs=b['integer_matches'],true_closed_loop=b['true_closed_loop'],board_connected_now=None,source_sha256=self.registry['pins']['board67_verification']['sha256']),
            live_requirements=['A3R1 exact board/boot/BIT/HWH and accepted raw board report',
                'current original GPU chemical_H from same full old state, no native H update',
                'validated R-only candidate partition for ordered H5768/R39901',
                'durable coordinator COMMIT intent + exact ACK or quarantine + original decoder after publish',
                'independent full-state/flow numerical comparison for named Q24 profile'],
            timings=dict(PL_compute_cycles=None,PL_adapter_cycles=None,PC_PS_roundtrip_ms=None,GPU_chemical_ms=None,GPU_R_ms=None,unified_commit_ms=None))


class _CoordinatorBarrier:
    """Shared staging barrier; no device connection or evidence admission here.

    A private staged original Coordinator validates the merge. One pointer makes
    the full state plus canonical H words visible only after matching ACK.
    journal must durably record intent before commit_frame returns in a live
    future adapter. A publication factory prepares an owned GPU buffer BEFORE
    COMMIT; the same visible tuple publishes CPU state and that buffer after ACK.
    """
    def init__(self,contract,initial_full,old_h_words,run_id,comparison_id,condition_id,asid,journal,
                 *,execution_kind,start_step=0,publication_factory=None):
        require(type(start_step) is int and start_step>=0,'INITIAL_STEP')
        self.execution_kind=execution_kind;self.publication_factory=publication_factory or (lambda full:None)
        self.c=contract;self.w=contract.wire;self.journal=journal;self.lock=threading.RLock()
        self.hmod=module('h_step',contract.paths['h_step']);self.core=module('gui_reused_Coordinator',contract.paths['coordinator'])
        require(type(asid) is bytes and len(asid)==16,'ASID')
        require(np.array_equal(initial_full[contract.h],contract.decode(old_h_words)),'CANONICAL_H_VISIBLE_STATE')
        updater=SimpleNamespace(h_ids=contract.h,source_ids=contract.r,h_order_digest=self.hmod.array_hash(contract.h),circuit_digest=contract.mapping_sha)
        r_stub=SimpleNamespace(state_semantics='STATELESS_CANDIDATE_ONLY')
        coord=self.core.Coordinator(updater,r_stub,initial_full,run_id,comparison_id,condition_id)
        coord.next_step_id=start_step
        self._visible=(coord,old_h_words,bytes(32),bytes(16),self.publication_factory(coord.state));self.asid=asid;self.pending=None;self.phase='READY';self.used_txns=set()
    @property
    def state(self):return self._visible[0].state
    @property
    def state_token(self):return self._visible[0].next_step_id
    @property
    def publication(self):return self._visible[4]
    def _fail(self,error):
        self.phase='IN_DOUBT' if self.phase in ('COMMIT_SENT','IN_DOUBT') else 'FAILED'
        self.pending=None
        try:self.journal(dict(event=self.phase,error=str(error),state_token=self.state_token,display_valid=False,execution_kind=self.execution_kind))
        except Exception:pass
    def fail(self,error):
        with self.lock:self._fail(error)
    def binding(self,x_full):
        coord=self._visible[0]
        return dict(run_id=coord.run_id,comparison_id=coord.comparison_id,condition_id=coord.condition_id,epoch=coord.epoch,step_id=coord.next_step_id,
            old_full_digest=self.hmod.array_hash(coord.state),input_digest=self.hmod.array_hash(x_full),mapping_sha256=self.c.mapping_sha,
            model=self.c.registry['model'],native_H_update_count=0,execution_kind=self.execution_kind)
    def prepare(self,txn,x_full,chemical_H,producer_binding):
        with self.lock:
            try:
                require(self.phase=='READY' and self.pending is None,'ONE_PENDING_TRANSACTION')
                require(type(txn) is bytes and len(txn)==16 and txn not in self.used_txns,'TRANSACTION_ID')
                self.c.unchanged();coord,words,parent,previous=self._visible[:4]
                x=self.hmod.frozen(self.hmod.vector(x_full,45669,'x_full'))
                chem=self.hmod.frozen(self.hmod.vector(chemical_H,5768,'chemical_H'))
                require(producer_binding=={**self.binding(x),'chemical_digest':self.hmod.array_hash(chem)},'CURRENT_CHEMICAL_BINDING')
                tag=self.hmod.StepTag(coord.run_id,coord.comparison_id,coord.condition_id,coord.epoch,coord.next_step_id,self.hmod.array_hash(coord.state))
                request=self.hmod.HRequest(tag,'A3_CHEMICAL_ALL_Q24',self.hmod.frozen(coord.state[self.c.h]),self.hmod.frozen(x[self.c.h]),chem,self.c.h,None,self.c.mapping_sha)
                payload=words+self.w.encode_activity(chem)+self.w.encode_activity(x[self.c.h])
                header=self.w.Header(self.w.STEP,self.asid,txn,coord.next_step_id,bytes.fromhex(tag.old_full_digest),self.w.digest(payload),len(payload),epoch=coord.epoch,parent_commit=parent,previous_txn=previous)
                self.pending=dict(header=header,payload=payload,request=request,binding=copy.deepcopy(producer_binding),x=x)
                self.used_txns.add(txn);self.phase='WAITING_CANDIDATES'
                return header.pack(),payload
            except Exception as e:self._fail(e);raise
    def accept_candidates(self,header_bytes,candidate_words,new_R,r_ids,producer_binding):
        with self.lock:
            try:
                require(self.phase=='WAITING_CANDIDATES','CANDIDATE_PHASE');p=self.pending;h=self.w.Header.unpack(header_bytes)
                require(h.op==self.w.RESULT and not h.status and h.identity()==p['header'].identity(),'PL_RESPONSE_IDENTITY')
                require(h.payload_bytes==len(candidate_words) and h.payload_sha==self.w.digest(candidate_words),'PL_CANDIDATE_SHA')
                require(h.compute_cycles==57681 and h.transfer_cycles>=h.compute_cycles,'PL_CYCLE_SCOPE')
                require(producer_binding=={**self.binding(p['x']),'r_candidate_digest':self.hmod.array_hash(new_R),
                    'r_ids_digest':self.hmod.array_hash(r_ids)},'R_SAME_OLD_STATE_BINDING')
                request=p['request'];new_h=self.c.decode(candidate_words)
                hr=self.hmod.HResult(request.tag,request.layout,self.hmod.frozen(new_h),request.boundary,self.hmod.array_hash(self.c.h),self.c.mapping_sha,self.hmod.request_hash(request))
                rr=self.core.RResult(request.tag,self.hmod.frozen(new_R),self.hmod.frozen(r_ids),producer_binding['native_H_update_count'],{'execution_kind':self.execution_kind})
                transaction=self.core.PreparedStep(request.tag,request,hr,rr,self.hmod.array_hash(p['x']),self.hmod.request_hash(request))
                staged=copy.copy(self._visible[0]);staged.logs=[];staged.pending=transaction;staged.status='PREPARED'
                proposed=staged.commit(transaction) # Original validation/merge, private until ACK.
                decision=canonical(dict(schema='flyvis-unified-commit/v1',binding=p['binding'],transaction=p['header'].txn.hex(),
                    request_payload_sha=p['header'].payload_sha.hex(),candidate_H_sha=h.payload_sha.hex(),candidate_R_sha=self.hmod.array_hash(new_R),
                    full_after_sha=self.hmod.array_hash(proposed),parent_commit=p['header'].parent_commit.hex(),numeric_profile=self.w.PROFILE))
                publication=self.publication_factory(proposed)
                p.update(staged=staged,words=candidate_words,receipt=header_bytes,decision=decision,publication=publication);self.phase='VALIDATED_NOT_COMMITTED'
                return dict(unified_commit_sha256=decision,proposed_full_digest=self.hmod.array_hash(proposed),visible_state_token=self.state_token)
            except Exception as e:self._fail(e);raise
    def commit_frame(self):
        with self.lock:
            try:
                require(self.phase=='VALIDATED_NOT_COMMITTED','COMMIT_PHASE');p=self.pending
                self.journal(dict(event='COMMIT_INTENT',decision=p['decision'],request_header_sha256=self.w.digest(p['header'].pack()).hex(),
                    candidate_sha256=self.w.digest(p['words']).hex(),old_state_token=self.state_token,execution_kind=self.execution_kind))
                p['commit_header']=dataclasses.replace(p['header'],op=self.w.COMMIT,payload_bytes=0,payload_sha=self.w.digest(b''),parent_commit=bytes.fromhex(p['decision']))
                self.phase='COMMIT_SENT';return p['commit_header'].pack()
            except Exception as e:self._fail(e);raise
    def acknowledge(self,header_bytes):
        with self.lock:
            try:
                require(self.phase=='COMMIT_SENT','ACK_PHASE');p=self.pending;ack=self.w.Header.unpack(header_bytes)
                require(ack.op==self.w.ACK and not ack.status and not ack.compute_cycles and not ack.transfer_cycles and ack.payload_sha==self.w.digest(b'')
                    and ack.identity()==p['commit_header'].identity(),'FULL_COMMIT_ACK_IDENTITY')
                self.journal(dict(event='COMMIT_ACK',decision=p['decision'],ack_sha256=self.w.digest(header_bytes).hex(),execution_kind=self.execution_kind))
                self._visible=(p['staged'],p['words'],bytes.fromhex(p['decision']),p['header'].txn,p['publication'])
                self.pending=None;self.phase='READY';return self.state
            except Exception as e:self._fail(e);raise
    def status(self):
        return dict(phase=self.phase,state_token=self.state_token,display_valid=False,execution_kind=self.execution_kind,
            FPGA_status='NOT_CONNECTED',PL_proven_global_ids=[],native_h_updates=0)


class CoordinatorRehearsal(_CoordinatorBarrier):
    """Compatibility CPU entry: a caller's flag cannot promote fixtures to PL."""
    def init__(self,contract,initial_full,old_h_words,run_id,comparison_id,condition_id,asid,journal,execution_kind='CPU_PROTOCOL_TEST'):
        require(execution_kind=='CPU_PROTOCOL_TEST','LIVE_HARDWARE_NOT_ADMITTED')
        super().init__(contract,initial_full,old_h_words,run_id,comparison_id,condition_id,asid,journal,
                         execution_kind=execution_kind)


def inspect_local_board_replay(contract,root,pins):
    """Explicit sealed files only. Does not admit a live or closed-loop backend.

    `pins` must come from an independently accepted handoff, not a scanned folder.
    Protocol bytes cannot cryptographically attest silicon execution; report
    that provenance remains an independent requirement even if all checks pass.
    """
    root=host_path(root).resolve();w=contract.wire;v2=getattr(w,'VERSION',1)==2
    required={'BOARD_RESULT.json'}|{f'{kind}_{i}.bin' for kind in ('request','receipt','candidate') for i in range(3)}
    if v2:required|={'FIRMWARE_SESSION.json','wire_000_tx_intent.bin','wire_001_rx.bin'}|{f'commit_ack_{i}.bin' for i in range(3)}
    require(set(pins)==required,'EXPLICIT_REPLAY_PIN_SET')
    for name,digest in pins.items():require(sha(root/name)==digest,'BOARD_REPLAY_FILE_CHANGED '+name)
    report=load(root/'BOARD_RESULT.json')
    require(report['status']=='PASS' and report['evidence']=='ACTUAL_BOARD_LOCAL_REPLAY_ONLY' and report['GPU_closed_loop']=='NOT_RUN','REPLAY_EVIDENCE_SCOPE')
    require(report['nodes']==5768 and report['requests']==3 and report['states']==17304 and len(report['rows'])==3,'REPLAY_COUNTS')
    require(report['old_digest_scope']=='H_ONLY_LOCAL_REPLAY','REPLAY_NOT_GLOBAL_OLD_STATE')
    if v2:
        firmware=load(root/'FIRMWARE_SESSION.json');hello=w.Header.unpack((root/'wire_000_tx_intent.bin').read_bytes())
        raw=(root/'wire_001_rx.bin').read_bytes();att=w.Header.unpack(raw[:256])
        import json
        require(hello.op==w.HELLO and hello.old_sha==w.IMAGE_PAIR and att.op==w.ATTEST and not att.status
            and not att.compute_cycles and not att.transfer_cycles and att.identity()==hello.identity()
            and att.payload_bytes==len(raw)-256 and att.payload_sha==w.digest(raw[256:]),'REPLAY_ATTEST_WIRE')
        require(json.loads(raw[256:])==firmware==report['firmware_session'],'REPLAY_ATTEST_RECORD')
        require(firmware['bit_sha256']==w.BIT_SHA and firmware['hwh_sha256']==w.HWH_SHA and firmware['config_sha256']==w.CONFIG.hex()
            and firmware['image_pair_sha256']==w.IMAGE_PAIR.hex() and firmware['asid']==hello.asid.hex()
            and firmware['hello_txn']==hello.txn.hex() and firmware['pynq_is_loaded'] is True
            and firmware['boot_id'] and firmware['server_session'],'REPLAY_IMAGE_SESSION')
    previous=None;last=None;seen=set()
    def frozen_words(key):return np.asarray([int(x,16) for x in contract.paths[key].read_text().split()],dtype='<u4').tobytes()
    expected=frozen_words('a3_expected');requests=frozen_words('a3_requests')
    for i,row in enumerate(report['rows']):
        request=(root/f'request_{i}.bin').read_bytes();candidate=(root/f'candidate_{i}.bin').read_bytes();header=(root/f'receipt_{i}.bin').read_bytes();h=w.Header.unpack(header)
        require(len(request)==w.INPUT_BYTES and len(candidate)==w.WORD_BYTES,'REPLAY_ARRAY_LENGTH');w.validate_words(request);w.validate_words(candidate)
        require(candidate==expected[i*w.WORD_BYTES:(i+1)*w.WORD_BYTES] and request==requests[i*w.INPUT_BYTES:(i+1)*w.INPUT_BYTES],'INDEPENDENT_FROZEN_ORACLE_MISMATCH')
        require(h.op==w.RESULT and not h.status and h.step==198+i and h.old_sha==w.digest(request[:w.WORD_BYTES]) and h.payload_sha==w.digest(candidate),'REPLAY_WIRE_BINDING')
        require(h.txn not in seen and h.compute_cycles==57681 and h.transfer_cycles>=h.compute_cycles,'REPLAY_CYCLES_OR_TXN');seen.add(h.txn)
        if previous is not None:require(request[:w.WORD_BYTES]==previous and h.asid==last.asid and h.epoch==last.epoch and h.previous_txn==last.txn and h.parent_commit==last_commit,'REPLAY_RECURRENCE')
        else:require(h.parent_commit==bytes(32) and h.previous_txn==bytes(16),'REPLAY_INITIAL_PARENT')
        last_commit=w.digest(b'LOCAL_BOARD_REPLAY\0'+(w.IMAGE_PAIR if v2 else b'')+header+candidate)
        require(row['case']==i and row['step']==h.step and row['txn']==h.txn.hex() and row['outputs']==5768 and row['candidate_sha']==h.payload_sha.hex()
            and row['replay_commit_sha']==last_commit.hex() and row['core_cycles']==h.compute_cycles and row['adapter_cycles']==h.transfer_cycles,'REPLAY_REPORT_BINDING')
        if v2:
            require(h.asid==hello.asid and row['release_ack_verified'] is True,'REPLAY_SESSION_ACK')
            ack=w.Header.unpack((root/f'commit_ack_{i}.bin').read_bytes())
            expected_ack=dataclasses.replace(h,op=w.ACK,payload_bytes=0,payload_sha=w.digest(b''),parent_commit=last_commit,compute_cycles=0,transfer_cycles=0)
            require(ack==expected_ack,'REPLAY_FULL_ACK')
            for name in ('pc_step_roundtrip_ns','pc_commit_roundtrip_ns'):
                require(type(row[name]) is int and row[name]>=0,'REPLAY_TIMING')
        else:require(type(row['pc_roundtrip_ns']) is int and row['pc_roundtrip_ns']>=0,'REPLAY_TIMING')
        previous=candidate;last=h
    return dict(status='PASS_FILE_CONSISTENCY_ONLY',origin_claim=report['evidence'],display_kind='offline replay',
        physical_provenance='REQUIRES_INDEPENDENT_ACCEPTANCE_AND_BOARD_IMAGE_IDENTITY',GPU_closed_loop='NOT_RUN',FPGA_status='NOT_CONNECTED',
        PL_proven_global_ids=[],raw_node_order=contract.h.tolist(),historical_timing_rows=report['rows'])


@lru_cache(maxsize=1)
def contract():return A3Contract()

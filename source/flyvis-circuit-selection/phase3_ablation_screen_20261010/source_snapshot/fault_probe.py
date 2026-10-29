"""Three-candidate real GPU protocol faults and live H-R-H dependency probes."""
from dataclasses import replace
import time,uuid
from common import *
from h_step import HRequest,StepTag
from coordinator import Coordinator
from run_negative_tests import FaultH

class FaultR:
    state_semantics='STATELESS_CANDIDATE_ONLY'
    def init__(self,adapter,h,fault):self.adapter,self.h,self.fault=adapter,h,fault
    def evaluate(self,old,x,tag):
        if self.fault=='future_H':
            req=HRequest(tag,'SOURCE_RAW',frozen(old[self.h.h_ids]),frozen(x[self.h.h_ids]),frozen(old[self.h.source_ids]),self.h.h_ids,self.h.source_ids,self.h.circuit_digest)
            future=old.copy();future[self.h.h_ids]=self.h.step(req).new_h
            return self.adapter.evaluate(future,x,tag)
        result=self.adapter.evaluate(old,x,tag)
        if self.fault=='nan_R':
            data=result.new_r.copy();data[0]=np.nan;return replace(result,new_r=frozen(data))
        if self.fault=='swapped_R_ids':
            ids=result.r_global_ids.copy();ids[[0,1]]=ids[[1,0]];return replace(result,r_global_ids=frozen(ids))
        return result

def main():
    out=HERE/'artifacts/fault_feedback_r1'
    if out.exists():raise SystemExit('Existing result preserved')
    out.mkdir(parents=True);torch=configure_gpu()
    from r_only import RStepService
    from gpu_adapter import GPUAdapter
    meta=load(BUNDLE/'screen_manifest.json');initial=np.load(BUNDLE/'initial_state_full.npy');stim=np.load(BUNDLE/'stimulus.npy')
    summaries=[];events=[]
    for profile in meta['profiles']:
        name=profile['candidate'];case=out/name;case.mkdir();candidate=BUNDLE/'candidates'/name
        h=HUpdater(candidate/'static_boundary_gpu_native.npz');inputs=validate_parameters(h,BUNDLE/'expanded_parameters.npz')
        service=RStepService(BUNDLE/'expanded_parameters.npz',BUNDLE/'identity_manifest.json',candidate/'candidate_manifest.json',device='cuda')
        adapter=GPUAdapter(service,inputs);x=input_full(stim[0,0,0],inputs);tests=[]
        with native_full_forbidden() as guard:
            for fault,expected in [('wrong_request_step','OUT_OF_ORDER'),('nan_H','NONFINITE'),('nan_R','NONFINITE'),('failure','CORE_ERROR'),('worker_exit','CORE_ERROR'),
                ('timeout','CORE_ERROR'),('swapped_H_ids','LAYOUT_MISMATCH'),('swapped_source_ids','LAYOUT_MISMATCH'),('swapped_R_ids','LAYOUT_MISMATCH'),
                ('wrong_result_step','OUT_OF_ORDER'),('wrong_epoch','OUT_OF_ORDER'),('stale_request','STATE_MISMATCH'),('future_H','STATE_MISMATCH')]:
                c=Coordinator(h,FaultR(adapter,h,fault),initial,str(uuid.uuid4()),meta['common_data_id'],'0')
                before=array_hash(c.state);calls=adapter.calls;caught=None
                try:c.commit(c.prepare(1 if fault=='wrong_request_step' else 0,x,h_backend=FaultH(h,fault)))
                except StepError as error:caught=error.code
                assert caught==expected and c.next_step_id==0 and array_hash(c.state)==before and c.status=='FAILED'
                assert not any(row['status']=='COMMITTED' for row in c.logs)
                tests.append(dict(test=fault,status='PASS',error=caught,actual_GPU_R_calls=adapter.calls-calls,committed_steps=0,full_state_unchanged=True,fallback_count=0))
                events.extend(dict(candidate=name,test=fault,**row) for row in c.logs)
            c=Coordinator(h,adapter,initial,str(uuid.uuid4()),meta['common_data_id'],'0');p=c.prepare(0,x);c.commit(p);after=array_hash(c.state)
            try:c.commit(p);raise AssertionError('duplicate accepted')
            except StepError as error:assert error.code=='ALREADY_COMMITTED'
            assert c.next_step_id==1 and array_hash(c.state)==after
            tests.append(dict(test='duplicate_commit',status='PASS',committed_steps=1,no_second_commit=True))
            events.extend(dict(candidate=name,test='duplicate_commit',**row) for row in c.logs)
        assert guard['forbidden_native_call_count']==0
        source=HERE/'artifacts/no_intervention_r1'/name
        baseline=load(source/'result.json');assert baseline['status'].startswith('PASS')
        activity=np.load(source/'activities_full.npy',mmap_mode='r');branch_step=220;common=activity[0,branch_step-1].copy()
        with np.load(candidate/'static_boundary_gpu_native.npz') as z:edges={key:z[key] for key in z.files}
        by_source={}
        for j,(s,w) in enumerate(zip(edges['incoming_source_index'],edges['incoming_weight'])):
            if abs(w)>.01:by_source.setdefault(int(s),[]).append(j)
        pairs=[]
        for i,(s,d,w) in enumerate(zip(edges['outgoing_source_index'],edges['outgoing_target_index'],edges['outgoing_weight'])):
            if abs(w)>.01 and common[s]>0 and common[d]>0:
                for j in by_source.get(int(d),[]):pairs.append((float(abs(w*edges['incoming_weight'][j])),i,j))
        assert pairs,'no active two-edge feedback for candidate at chosen checkpoint'
        _,hr,rh=max(pairs);hs=int(edges['outgoing_source_index'][hr]);rs=int(edges['outgoing_target_index'][hr]);ht=int(edges['incoming_target_index'][rh])
        starts={mode:common.copy() for mode in ['control','H_plus','R_plus']};starts['H_plus'][hs]+=np.float32(.25);starts['R_plus'][rs]+=np.float32(.25)
        cs={mode:Coordinator(HUpdater(candidate/'static_boundary_gpu_native.npz'),adapter,state,str(uuid.uuid4()),'ISOLATED_DEPENDENCY_PROBE','0') for mode,state in starts.items()}
        traces={mode:[state.copy()] for mode,state in starts.items()}
        for c in cs.values():c.next_step_id=branch_step
        with native_full_forbidden() as probe_guard:
            for k in range(branch_step,branch_step+8):
                x=input_full(stim[0,k,0],inputs)
                for mode,c in cs.items():
                    traces[mode].append(c.step(k,x).copy());events.extend(dict(candidate=name,probe=mode,**row) for row in c.logs[-2:])
        traces={mode:np.stack(value) for mode,value in traces.items()}
        dr=float(traces['H_plus'][1,rs]-traces['control'][1,rs]);dh=float(traces['R_plus'][1,ht]-traces['control'][1,ht])
        assert abs(dr)>1e-8 and abs(dh)>1e-8 and probe_guard['forbidden_native_call_count']==0
        after=traces['H_plus'][1];boundary=frozen(after[h.source_ids]);clamped=boundary.copy();clamped[np.searchsorted(h.source_ids,rs)]=traces['control'][1,rs]
        tag=StepTag(str(uuid.uuid4()),'RETURN_EDGE_DIAGNOSTIC','0',0,branch_step+1,array_hash(after))
        req=HRequest(tag,'SOURCE_RAW',frozen(after[h.h_ids]),frozen(input_full(stim[0,branch_step+1,0],inputs)[h.h_ids]),boundary,h.h_ids,h.source_ids,h.circuit_digest)
        live=h.step(req).new_h;clamp=h.step(replace(req,boundary=frozen(clamped))).new_h
        returned=float(live[np.searchsorted(h.h_ids,ht)]-clamp[np.searchsorted(h.h_ids,ht)])
        assert np.array_equal(live,traces['H_plus'][2,h.h_ids]) and abs(returned)>1e-8
        for mode,array in traces.items():np.save(case/(mode+'_full.npy'),array)
        record=dict(candidate=name,status='PASS_THREE_CANDIDATE_LIVE_PROTOCOL_AND_FEEDBACK',tests=tests,
            H_source=hs,R_intermediate=rs,H_return_target=ht,HR_original_edge_id=int(edges['outgoing_edge_id'][hr]),RH_original_edge_id=int(edges['incoming_edge_id'][rh]),
            H_to_R_delta=dr,R_to_H_delta=dh,returned_R_effect_on_second_H=returned,
            old_checkpoint_sha256=array_hash(common),branch_steps=list(range(220,228)),condition=0,probe_guard=probe_guard,fault_guard=guard,
            GPU_R_calls=adapter.calls,source_checkpoint_from_own_baseline=True,recorded_R_production=False,formal_ablation=False,timeout_scope='injected software exception only')
        dump(case/'result.json',record);seal(case);summaries.append(record)
        print('FAULT_FEEDBACK',name,json.dumps(dict(H_to_R=dr,R_to_H=dh,return_to_H=returned)),flush=True)
        del service,adapter;torch.cuda.empty_cache()
    dump(out/'result.json',dict(status='PASS_THREE_CANDIDATE_FAULTS_AND_DEPENDENCY_PROBES',candidates=summaries,formal_ablation_executed=False,evidence_level='ACTUAL_GPU_R_AND_PYTHON_H_SOFTWARE_EXPERIMENT',FPGA_execution=False))
    (out/'trace.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in events),encoding='utf-8');seal(out)

if __name__=='__main__':main()

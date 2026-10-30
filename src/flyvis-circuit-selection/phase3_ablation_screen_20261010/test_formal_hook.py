"""New frozen gate faults and old-H causal control, separate from batch results."""
from dataclasses import replace
import uuid
from common import *
from fault_probe import FaultR
from run_negative_tests import FaultH

def main():
    out=HERE/'artifacts/formal_hook_tests'
    if out.exists():raise SystemExit('Preserve tests')
    out.mkdir(parents=True);torch=configure_gpu()
    from r_only import RStepService,InterfaceError
    from gate_service import HRReleaseService
    from bound_adapter import BoundAdapter,make_identity
    from coordinator import Coordinator
    from h_step import StepTag
    initial=np.load(BUNDLE/'initial_state_full.npy');stim=np.load(BUNDLE/'stimulus.npy');meta=load(BUNDLE/'screen_manifest.json')
    alltests=[];events=[]
    with np.load(BUNDLE/'expanded_parameters.npz') as z:p={k:z[k] for k in z.files}
    for name in ['B_T5c','A_T4c','C_T4T5_all_centers']:
        cp=BUNDLE/'candidates'/name;h=HUpdater(cp/'static_boundary_gpu_native.npz');inputs=validate_parameters(h,BUNDLE/'expanded_parameters.npz')
        hr=np.load(HERE/'spec_snapshot'/(name+'_HR_edge_ids.npy'));case=out/name;case.mkdir()
        native=RStepService(BUNDLE/'expanded_parameters.npz',BUNDLE/'identity_manifest.json',cp/'candidate_manifest.json',device='cuda')
        services={mode:HRReleaseService(BUNDLE/'expanded_parameters.npz',BUNDLE/'identity_manifest.json',cp/'candidate_manifest.json',device='cuda',hr_edge_ids=hr,start_step=200,mode=mode) for mode in ['Sham','Ablation']}
        adapters={mode:BoundAdapter(service,inputs,make_identity(name,mode)) for mode,service in services.items()}
        trace=np.load(HERE/'artifacts/no_intervention_r1'/name/'activities_full.npy',mmap_mode='r');old=trace[0,199].copy()
        source_candidates=np.unique(p['source_global'][hr[(p['effective_weight'][hr]!=0)&(old[p['source_global'][hr]]>0)]])
        assert len(source_candidates);s=int(source_candidates[0]);perturb=old.copy();perturb[s]+=np.float32(.25)
        frame=torch.tensor(stim[0,200,0],device='cuda');told=torch.tensor(old,device='cuda');tperturb=torch.tensor(perturb,device='cuda')
        with native_full_forbidden() as guard:
            full_r=native.step(told,frame,step_id=200,run_id='HOOK_CONTROL',condition_id='0').activity
            sh=services['Sham'].step(told,frame,step_id=200,run_id='HOOK_CONTROL',condition_id='0').activity
            ab=services['Ablation'].step(told,frame,step_id=200,run_id='HOOK_CONTROL',condition_id='0').activity
            shp=services['Sham'].step(tperturb,frame,step_id=200,run_id='HOOK_CONTROL',condition_id='0').activity
            abp=services['Ablation'].step(tperturb,frame,step_id=200,run_id='HOOK_CONTROL',condition_id='0').activity
            assert torch.equal(full_r,sh) and not torch.equal(sh,shp) and torch.equal(ab,abp) and not torch.equal(sh,ab)
            # Independent original-ID full-edge current gate; check the R-only scatter.
            allcurrent=torch.tensor(p['effective_weight'],device='cuda')*torch.relu(told[torch.tensor(p['source_global'],device='cuda')])
            allcurrent[torch.tensor(hr,device='cuda')]*=0
            current=torch.zeros(45669,device='cuda');current.scatter_add_(0,torch.tensor(p['target_global'],device='cuda'),allcurrent)
            ix=torch.tensor(native.r_indices,device='cuda');bias=torch.tensor(p['bias'][native.r_indices],device='cuda');tau=torch.tensor(p['time_const'][native.r_indices],device='cuda')
            expected=told[ix]+(1/torch.maximum(tau,torch.tensor(.005,device='cuda')))*(-told[ix]+bias+current[ix]+native.external_r(frame))*.005
            assert torch.equal(expected,ab)
            inactive=services['Ablation'].step(told,frame,step_id=199,run_id='HOOK_CONTROL',condition_id='0').activity
            assert torch.equal(inactive,full_r)
        np.savez(case/'old_H_perturb_control.npz',old_full=old,perturbed_full=perturb,H_source=s,Sham_R=sh.cpu().numpy(),Sham_perturbed_R=shp.cpu().numpy(),Ablation_R=ab.cpu().numpy(),Ablation_perturbed_R=abp.cpu().numpy(),R_ids=native.r_indices)
        tests=[];adapter=adapters['Ablation'];x=input_full(stim[0,200,0],inputs)
        with native_full_forbidden() as faults_guard:
            for fault,expected_error in [('wrong_request_step','OUT_OF_ORDER'),('nan_H','NONFINITE'),('nan_R','NONFINITE'),('failure','CORE_ERROR'),('worker_exit','CORE_ERROR'),('timeout','CORE_ERROR'),
                ('swapped_H_ids','LAYOUT_MISMATCH'),('swapped_source_ids','LAYOUT_MISMATCH'),('swapped_R_ids','LAYOUT_MISMATCH'),('wrong_result_step','OUT_OF_ORDER'),('wrong_epoch','OUT_OF_ORDER'),('stale_request','STATE_MISMATCH'),('future_H','STATE_MISMATCH')]:
                co=Coordinator(h,FaultR(adapter,h,fault),old,str(uuid.uuid4()),adapter.identity['comparison_id'],'0');co.next_step_id=200;before=array_hash(co.state);calls=adapter.calls
                caught=None
                try:co.commit(co.prepare(201 if fault=='wrong_request_step' else 200,x,h_backend=FaultH(h,fault)))
                except StepError as error:caught=error.code
                assert caught==expected_error and co.next_step_id==200 and array_hash(co.state)==before and co.status=='FAILED'
                assert not any(e['status']=='COMMITTED' for e in co.logs)
                tests.append(dict(test=fault,error=caught,status='PASS',committed=0,full_state_unchanged=True,actual_GPU_calls=adapter.calls-calls,fallback=0));events.extend(dict(candidate=name,test=fault,**e) for e in co.logs)
            co=Coordinator(h,adapter,old,str(uuid.uuid4()),adapter.identity['comparison_id'],'0');co.next_step_id=200;transaction=co.prepare(200,x);co.commit(transaction);after=array_hash(co.state)
            try:co.commit(transaction);raise AssertionError('duplicate accepted')
            except StepError as error:assert error.code=='ALREADY_COMMITTED'
            assert co.next_step_id==201 and array_hash(co.state)==after;tests.append(dict(test='duplicate_commit',status='PASS',second_commit=0))
            # Inject envelope identity mismatch into production evaluate; barrier fails before R kernel.
            class BadIdentity(BoundAdapter):
                def request(self,old,x,tag):
                    q=super().request(old,x,tag);q['spec_sha256']='WRONG';return q
            bad=BadIdentity(services['Ablation'],inputs,adapter.identity);co=Coordinator(h,bad,old,str(uuid.uuid4()),adapter.identity['comparison_id'],'0');co.next_step_id=200
            before=array_hash(co.state)
            try:co.prepare(200,x);raise AssertionError('bad identity accepted')
            except StepError as error:assert error.code=='IDENTITY_MISMATCH'
            assert co.next_step_id==200 and array_hash(co.state)==before and bad.calls==0
            tests.append(dict(test='wrong_spec_identity',status='PASS',committed=0,full_state_unchanged=True))
            tag=StepTag('IDENTITY_CONTROL',adapter.identity['comparison_id'],'0',0,200,array_hash(old));q=adapter.request(old,x,tag)
            for key in adapter.identity:
                broken=dict(q);broken[key]='WRONG'
                try:adapter.check_request(broken,tag);raise AssertionError('identity accepted '+key)
                except StepError as error:assert error.code=='IDENTITY_MISMATCH'
                tests.append(dict(test='request_identity_'+key,status='PASS'))
            response=dict(run_id=q['run_id'],condition_id=q['condition_id'],step_id=q['step_id'],candidate_manifest_sha256=q['candidate_manifest_sha256'],spec_sha256=q['spec_sha256'],operator=q['operator'],mode=q['mode'],HR_release_gain=q['HR_release_gain'],global_node_indices=native.r_indices,activity=ab.cpu().numpy(),status='CANDIDATE_NOT_COMMITTED')
            for key in ['run_id','condition_id','step_id','candidate_manifest_sha256','spec_sha256','operator','mode','HR_release_gain','status']:
                broken=dict(response);broken[key]='WRONG'
                try:adapter.check_response(broken,q);raise AssertionError('response accepted '+key)
                except StepError as error:assert error.code=='IDENTITY_MISMATCH'
                tests.append(dict(test='response_identity_'+key,status='PASS'))
        try:HRReleaseService(BUNDLE/'expanded_parameters.npz',BUNDLE/'identity_manifest.json',cp/'candidate_manifest.json',device='cuda',hr_edge_ids=hr[1:],start_step=200,mode='Ablation');raise AssertionError('subset accepted')
        except InterfaceError:tests.append(dict(test='missing_original_HR_edge',status='PASS'))
        for service in services.values():service.assert_weights_unchanged()
        record=dict(candidate=name,status='PASS_NEW_FORMAL_GATE_CONTROLS_AND_FAULTS',tests=tests,Sham_native_bitwise=True,independent_masked_full_R_bitwise=True,
            H_perturb_global_id=s,H_perturb=.25,Sham_R_perturb_max=float((shp-sh).abs().max()),Ablation_R_perturb_max=float((abp-ab).abs().max()),
            gate_inactive_before_200=True,old_snapshot_unchanged=np.array_equal(old,trace[0,199]),weights_unchanged=True,guard=guard,fault_guard=faults_guard,
            timeout_scope='injected software timeout exception; physical hardware timeout untested',FPGA_execution=False)
        dump(case/'result.json',record);seal(case);alltests.append(record);print('FORMAL_HOOK_PASS',name,len(tests),flush=True)
        del services,adapters,native;torch.cuda.empty_cache()
    dump(out/'result.json',dict(status='PASS_NEW_FORMAL_HOOK_TESTS',candidates=alltests,code_sha256={p.name:file_hash(p) for p in [Path(__file__),HERE/'gate_service.py',HERE/'bound_adapter.py']},spec_sha256=load(HERE/'PRE_RUN_REGISTRATION.json')['spec_sha256']))
    (out/'fault_events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events),encoding='utf-8');seal(out)

if __name__=='__main__':main()

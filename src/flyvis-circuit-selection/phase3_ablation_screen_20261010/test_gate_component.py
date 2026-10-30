"""Same-old-state edge-gate component controls, not a formal Ablation run."""
from common import *

def main():
    out=HERE/'artifacts/gate_component_r1'
    if out.exists():raise SystemExit('Existing controls preserved')
    out.mkdir(parents=True);torch=configure_gpu()
    from r_only import RStepService,InterfaceError
    from gate_service import HRReleaseService
    meta=load(BUNDLE/'screen_manifest.json');stim=np.load(BUNDLE/'stimulus.npy');proofs=[]
    for profile in meta['profiles']:
        name=profile['candidate'];candidate=BUNDLE/'candidates'/name
        with np.load(candidate/'validated_partition_ids.npz') as z:hr=z['HR']
        paths=(BUNDLE/'expanded_parameters.npz',BUNDLE/'identity_manifest.json',candidate/'candidate_manifest.json')
        baseline=np.load(HERE/'artifacts/no_intervention_r1'/name/'activities_full.npy',mmap_mode='r')
        old=torch.tensor(baseline[0,199].copy(),device='cuda:0');frame=torch.tensor(stim[0,200,0].copy(),device='cuda:0')
        native=RStepService(*paths,device='cuda');sham=HRReleaseService(*paths,hr_edge_ids=hr,start_step=200,mode='Sham',device='cuda')
        probe=HRReleaseService(*paths,hr_edge_ids=hr,start_step=200,mode='Ablation',device='cuda')
        tag=dict(step_id=200,run_id='COMPONENT_ONLY_NO_COMMIT',condition_id='0')
        r=native.step(old,frame,**tag);s=sham.step(old,frame,**tag);a=probe.step(old,frame,**tag)
        assert torch.equal(r.activity,s.activity)
        assert not torch.equal(a.activity,s.activity) and torch.equal(old,torch.tensor(baseline[0,199].copy(),device='cuda:0'))
        assert probe.last_gate_evidence['hr_after_nonzero_terms']==0
        probe.assert_weights_unchanged();sham.assert_weights_unchanged()
        wrong=hr.copy();wrong[0]=0
        try:HRReleaseService(*paths,hr_edge_ids=wrong,start_step=200,mode='Ablation',device='cuda');raise AssertionError('bad edge IDs accepted')
        except InterfaceError as error:bad=str(error)
        # Onset-1 uses a different frozen frame and its own correct baseline checkpoint.
        old_before=torch.tensor(baseline[0,198].copy(),device='cuda:0');frame_before=torch.tensor(stim[0,199,0].copy(),device='cuda:0')
        n_before=native.step(old_before,frame_before,step_id=199,run_id='COMPONENT_ONLY_NO_COMMIT',condition_id='0')
        a_before=probe.step(old_before,frame_before,step_id=199,run_id='COMPONENT_ONLY_NO_COMMIT',condition_id='0')
        assert torch.equal(n_before.activity,a_before.activity)
        proofs.append(dict(candidate=name,sham_R_bitwise_native=True,pre_gate_R_bitwise_native=True,HR_gate_changes_R=True,
            R_max_difference=float((r.activity-a.activity).abs().max().item()),original_weights_unchanged=True,old_state_unchanged=True,
            invalid_HR_ids_rejected=bad,committed_steps=0,prototype_start_step=200,formal_spec_bound=False))
        del native,sham,probe;torch.cuda.empty_cache()
    dump(out/'result.json',dict(status='PASS_HR_GATE_COMPONENT_CONTROLS',proofs=proofs,
        evidence_level='ACTUAL_GPU_COMPONENT_DIAGNOSTIC_NO_STATE_COMMIT',formal_ablation_executed=False,FPGA_execution=False))
    seal(out);print('GATE_COMPONENT_PASS',flush=True)

if __name__=='__main__':main()

"""All 23,280 state transitions and H recurrences, original IDs, gate, repeat audit."""
import csv,time
from common import *
from h_step import HRequest,StepTag,request_hash

def main():
    out=HERE/'artifacts/formal_audit'
    if out.exists():raise SystemExit('Preserve audit')
    out.mkdir(parents=True);started=time.monotonic();reg=load(HERE/'PRE_RUN_REGISTRATION.json');spec=load(HERE/'spec_snapshot/spec_config.json')
    assert load(HERE/'artifacts/formal_hook_tests/result.json')['status']=='PASS_NEW_FORMAL_HOOK_TESTS'
    assert load(HERE/'artifacts/formal_conflict_tests/result.json')['status']=='PASS_FORMAL_CONFLICTING_DUPLICATE_REQUESTS'
    manifest_verify(BUNDLE);meta=load(BUNDLE/'screen_manifest.json')
    fullpath=host_path(meta['Full_reference_path'])/'activities_full.npy';assert file_hash(fullpath)==reg['Full_reference']['source_full_sha256'];full=np.load(fullpath,mmap_mode='r')
    initial=np.load(BUNDLE/'initial_state_full.npy');stim=np.load(BUNDLE/'stimulus.npy');clock=np.load(BUNDLE/'time.npy');proofs=[];reproductions=[];pids=[]
    with np.load(BUNDLE/'expanded_parameters.npz') as z:params={k:z[k] for k in z.files}
    assert np.array_equal(params['original_edge_index'],np.arange(1513231,dtype=np.int64))
    for repeat in ['formal_r1','formal_r2']:
        root=HERE/'artifacts'/repeat;manifest_verify(root);res=load(root/'result.json');assert res['steps']==11640 and res['condition_runs']==24;pids.append(res['pid'])
        for name in ['B_T5c','A_T4c','C_T4T5_all_centers']:
            cp=BUNDLE/'candidates'/name;h=HUpdater(cp/'static_boundary_gpu_native.npz');inputs=validate_parameters(h,BUNDLE/'expanded_parameters.npz');r=np.setdiff1d(np.arange(45669,dtype=np.int64),h.h_ids)
            hmask=np.zeros(45669,bool);hmask[h.h_ids]=True;original=dict(HH=np.flatnonzero(hmask[params['source_global']]&hmask[params['target_global']]),RH=np.flatnonzero(~hmask[params['source_global']]&hmask[params['target_global']]),
                HR=np.flatnonzero(hmask[params['source_global']]&~hmask[params['target_global']]),RR=np.flatnonzero(~hmask[params['source_global']]&~hmask[params['target_global']]))
            with np.load(cp/'validated_partition_ids.npz') as z:
                for k,v in original.items():assert np.array_equal(z[k],v)
            assert np.array_equal(np.sort(np.concatenate(list(original.values()))),np.arange(1513231))
            hr=np.load(HERE/'spec_snapshot'/(name+'_HR_edge_ids.npy'));assert np.array_equal(hr,original['HR'])
            sham=np.load(root/name/'Sham/activities_full.npy',mmap_mode='r')
            for mode in ['Sham','Ablation']:
                source=root/name/mode;identity=load(source/'run_identity.json');manifest_verify(source)
                assert identity['candidate_id']==name and identity['mode']==mode and identity['campaign_id']==reg['campaign_id'] and identity['comparison_id']==reg['comparison_ids'][name]
                assert identity['spec_sha256']==reg['spec_sha256'] and identity['HR_edge_ids_sha256']==spec['candidates'][name]['HR_edge_ids']['sha256']
                for path,sha in identity['code_sha256'].items():assert file_hash(HERE/path)==sha
                activity=np.load(source/'activities_full.npy',mmap_mode='r');assert activity.shape==(4,485,45669) and activity.dtype==np.float32
                events=[json.loads(line) for line in (source/'step_status.jsonl').read_text().splitlines()];envelopes=[json.loads(line) for line in (source/'request_bindings.jsonl').read_text().splitlines()]
                gates=list(csv.DictReader((source/'gate_steps.csv').open(encoding='utf-8')));assert len(events)==3880 and len(envelopes)==len(gates)==1940
                for c,cond in enumerate(spec['fixture']['conditions']):
                    v=np.load(source/f'condition_{c:02d}/SOURCE_RAW_step_io.npz');old=initial;assert np.array_equal(v['time_label'],clock) and np.array_equal(v['state_after_time'],clock+.005)
                    assert np.array_equal(v['H_global_ids'],h.h_ids) and np.array_equal(v['source_global_ids'],h.source_ids)
                    for k in range(485):
                        pre,post=events[2*(c*485+k):2*(c*485+k)+2];env=envelopes[c*485+k];gate=gates[c*485+k]
                        assert pre['status']=='PREPARED' and post['status']=='COMMITTED' and pre['condition']==post['condition']==c
                        assert pre['step_id']==post['step_id']==env['step_id']==env['old_state_step_id']==k and post['state_token']==k+1
                        assert pre['old_full_digest']==env['old_full_digest']==array_hash(old)
                        assert pre['live_R_source_digest']==array_hash(old[h.source_ids]) and pre['old_H_digest']==array_hash(old[h.h_ids])
                        x=input_full(stim[c,k,0],inputs);assert pre['input_digest']==post['input_digest']==array_hash(x) and env['hex_frame_digest']==array_hash(stim[c,k,0])
                        assert env['run_id']==identity['run_id'] and env['condition_id']==cond['original_sample']
                        for key in ['campaign_id','comparison_id','candidate_id','candidate_manifest_sha256','HR_edge_ids_sha256','spec_sha256','operator','mode','activation_step_id','parameter_profile_sha256','stimulus_sha256','initial_state_sha256']:
                            assert env[key]==identity[key]
                        assert env['candidate_response_status']=='CANDIDATE_NOT_COMMITTED' and env['candidate_response_activity_digest']==post['R_after_digest'] and env['candidate_response_ids_digest']==array_hash(r)
                        for key,data in [('old_H',old[h.h_ids]),('boundary_before',old[h.source_ids]),('x_H',x[h.h_ids]),('new_H_expected',activity[c,k,h.h_ids])]:assert np.array_equal(v[key][k],data),(repeat,name,mode,c,k,key)
                        tag=StepTag(identity['run_id'],identity['comparison_id'],cond['original_sample'],0,k,array_hash(old));request=HRequest(tag,'SOURCE_RAW',frozen(v['old_H'][k]),frozen(v['x_H'][k]),frozen(v['boundary_before'][k]),h.h_ids,h.source_ids,h.circuit_digest)
                        computed=h.step(request);assert np.array_equal(computed.new_h,activity[c,k,h.h_ids]) and np.array_equal(computed.chemical,v['chemical_expected'][k])
                        assert pre['request_digest']==post['H_request_digest']==request_hash(request)
                        assert post['full_after_digest']==array_hash(activity[c,k]) and post['H_after_digest']==array_hash(activity[c,k,h.h_ids]) and post['R_after_digest']==array_hash(activity[c,k,r]) and post['native_H_update_count']==0
                        assert np.isfinite(activity[c,k]).all()
                        if mode=='Sham':assert np.all(np.abs(activity[c,k].astype(np.float64)-full[c,k])<=1e-5+1e-5*np.abs(full[c,k].astype(np.float64)))
                        if mode=='Ablation' and k<200:assert np.array_equal(activity[c,k],sham[c,k])
                        if mode=='Ablation' and k==200:assert np.array_equal(activity[c,k,h.h_ids],sham[c,k,h.h_ids])
                        gain=0 if mode=='Ablation' and k>=200 else 1
                        assert int(gate['step_id'])==k and int(gate['condition'])==c and int(gate['selected_HR_gain'])==env['HR_release_gain']==gain and int(gate['all_other_edge_gain'])==1
                        assert int(gate['selected_original_HR_edges'])==len(hr) and int(gate['HH_RH_RR_gate'])==1
                        currents=params['effective_weight'][hr]*np.maximum(old[params['source_global'][hr]],np.float32(0))
                        assert int(gate['removed_hr_nonzero_terms'])==(np.count_nonzero(currents) if gain==0 else 0)
                        assert np.isclose(float(gate['hr_before_abs_sum']),np.abs(currents).sum(dtype=np.float64),atol=1e-5,rtol=1e-5)
                        if gain==0:assert float(gate['hr_after_abs_sum'])==float(gate['hr_after_signed_sum'])==0 and int(gate['hr_after_nonzero_terms'])==0
                        if k in [199,200,201,484]:
                            diag=np.load(source/f'condition_{c:02d}/HR_edge_current_step_{k:03d}.npz')
                            assert np.array_equal(diag['original_edge_ids'],hr) and np.array_equal(diag['before'],currents) and np.array_equal(diag['after'],currents*np.float32(gain))
                        old=activity[c,k]
                proofs.append(dict(repeat=repeat,candidate=name,mode=mode,status='PASS_ALL_1940_TRANSITIONS',all_H_recomputed_bitwise=True,live_own_R_boundaries=True,old_state_and_input_hash_chain=True,
                    original_1513231_edge_partition_exact=True,all_step_gate_checked=True,original_H_production_updates=0,activity_sha256=file_hash(source/'activities_full.npy')))
                print('FORMAL_AUDIT',repeat,name,mode,flush=True)
    assert pids[0]!=pids[1]
    for name in ['B_T5c','A_T4c','C_T4T5_all_centers']:
        signed=np.load(HERE/'artifacts/signed_all_node_differences_r1'/(name+'_A_minus_S_float64.npy'),mmap_mode='r')
        sa=np.load(HERE/'artifacts/formal_r1'/name/'Sham/activities_full.npy',mmap_mode='r');aa=np.load(HERE/'artifacts/formal_r1'/name/'Ablation/activities_full.npy',mmap_mode='r')
        assert signed.shape==(4,485,45669) and signed.dtype==np.float64
        for c in range(4):
            for k in range(485):assert np.array_equal(signed[c,k],aa[c,k].astype(np.float64)-sa[c,k].astype(np.float64))
        for mode in ['Sham','Ablation']:
            a=np.load(HERE/'artifacts/formal_r1'/name/mode/'activities_full.npy',mmap_mode='r');b=np.load(HERE/'artifacts/formal_r2'/name/mode/'activities_full.npy',mmap_mode='r')
            maximum=0.;violations=0;bitwise=True
            for c in range(4):
                for k in range(485):
                    d=np.abs(a[c,k].astype(np.float64)-b[c,k].astype(np.float64));maximum=max(maximum,float(d.max()));violations+=int((d>1e-5+1e-5*np.abs(a[c,k].astype(np.float64))).sum());bitwise=bitwise and np.array_equal(a[c,k],b[c,k])
            assert violations==0
            reproductions.append(dict(candidate=name,mode=mode,all_state_points=4*485*45669,max_abs=maximum,tolerance_violations=violations,bitwise_equal=bitwise))
    source=HERE.parent.parent/'docs/flyvis_visual_hybrid/architect_ablation_20261010'
    for e in load(HERE/'spec_snapshot/manifest.json')['files']:assert file_hash(source/e['path'])==e['sha256']
    manifest_verify(BUNDLE)
    dump(out/'result.json',dict(status='PASS_SOFTWARE_ABLATION_IMPLEMENTATION',G_AB0='PASS',G_AB1='PASS',G_AB2='PASS',process_ids=pids,actual_closed_loop_steps=23280,proofs=proofs,reproductions=reproductions,
        original_spec_and_bundle_unchanged=True,new_hook_faults=file_hash(HERE/'artifacts/formal_hook_tests/artifact_manifest.json'),Full_reference_use='reused_verified_original_GPU_Full; post-commit comparison only',
        scientific_loss_pass=False,FPGA_execution=False,wall_s=time.monotonic()-started,code_sha256=file_hash(Path(__file__))))
    seal(out);print('FORMAL_ACCEPTANCE_PASS',json.dumps(reproductions),flush=True)

if __name__=='__main__':main()

"""Live no-intervention H/R control; not yet a formally signed Sham/Ablation."""
import argparse,csv,time,uuid,platform
from common import *

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--candidate',default='all',choices=['all','B_T5c','A_T4c','C_T4T5_all_centers'])
    args=p.parse_args();out=HERE/'artifacts'/args.run
    if out.exists():raise SystemExit('Existing run preserved')
    out.mkdir(parents=True);torch=configure_gpu()
    from r_only import RStepService
    from gpu_adapter import GPUAdapter
    from coordinator import Coordinator
    entries=manifest_verify(BUNDLE);meta=load(BUNDLE/'screen_manifest.json')
    initial=np.load(BUNDLE/'initial_state_full.npy');stimulus=np.load(BUNDLE/'stimulus.npy');clock=np.load(BUNDLE/'time.npy')
    assert initial.shape==(45669,) and stimulus.shape==(4,485,1,721) and np.array_equal(clock,np.arange(485)*.005-1)
    reference_path=host_path(meta['Full_reference_path'])/'activities_full.npy'
    assert file_hash(reference_path)==meta['Full_reference_sha256']
    reference=np.load(reference_path,mmap_mode='r')
    assert reference.shape==(4,485,45669)
    conditions=list(csv.DictReader((BUNDLE/'conditions.csv').open(encoding='utf-8')))
    central=np.load(BUNDLE/'central_node_indices.npy');types=np.load(BUNDLE/'cell_types.npy')
    tt=central[np.isin(types,['T4'+s for s in 'abcd']+['T5'+s for s in 'abcd'])]
    source_files=[Path(__file__),HERE/'common.py',*(HERE/'dependencies/b_core'/s for s in ['h_step.py','coordinator.py','gpu_adapter.py']),HERE/'dependencies/a_snapshot/r_only.py']
    code={str(s.relative_to(HERE).as_posix()):file_hash(s) for s in source_files}
    all_results=[];start=time.monotonic()
    for profile in meta['profiles']:
        name=profile['candidate']
        if args.candidate!='all' and args.candidate!=name:continue
        dest=out/name;dest.mkdir();candidate=BUNDLE/'candidates'/name
        h=HUpdater(candidate/'static_boundary_gpu_native.npz');inputs=validate_parameters(h,BUNDLE/'expanded_parameters.npz')
        service=RStepService(BUNDLE/'expanded_parameters.npz',BUNDLE/'identity_manifest.json',candidate/'candidate_manifest.json',device='cuda')
        assert service.partition_counts==profile['partition_counts']
        adapter=GPUAdapter(service,inputs);r=service.r_indices
        groups=dict(H=h.h_ids,R=r,full=np.arange(45669),central=central,T4T5=tt)
        run_id=str(uuid.uuid4());comparison=digest(dict(common=meta['common_data_id'],candidate=profile['candidate_sha256'],mode='NO_INTERVENTION_BASELINE',metrics=file_hash(BUNDLE/'baseline_metric_profile.json')))
        identity=dict(run_id=run_id,comparison_id=comparison,common_data_id=meta['common_data_id'],candidate=name,mode='NO_INTERVENTION_BASELINE',
            formal_sham_status='WAITING_ARCH_SPEC_BINDING',formal_ablation_executed=False,profile=profile,common=meta['common'],
            steps_per_condition=485,conditions=conditions,dt_s=.005,code_sha256=code,
            Full_reference_file_sha256=file_hash(reference_path),original_expanded_parameters=file_hash(BUNDLE/'expanded_parameters.npz'),
            original_a0=file_hash(BUNDLE/'initial_state_full.npy'),stimulus_sha256=file_hash(BUNDLE/'stimulus.npy'),time_sha256=file_hash(BUNDLE/'time.npy'),
            evidence_level='ACTUAL_GPU_R_INDEPENDENT_PYTHON_H_CLOSED_LOOP',FPGA_execution=False,
            python=platform.python_version(),numpy=np.__version__,torch=torch.__version__,gpu=torch.cuda.get_device_name(0),command=[sys.executable,*sys.argv])
        dump(dest/'run_identity.json',identity)
        trace=np.lib.format.open_memmap(dest/'activities_full.npy',mode='w+',dtype=np.float32,shape=(4,485,45669))
        status=(dest/'step_status.jsonl').open('w',encoding='utf-8');records=[]
        for c,condition in enumerate(conditions):
            case=dest/f'condition_{c:02d}';case.mkdir();started=time.monotonic()
            h=HUpdater(candidate/'static_boundary_gpu_native.npz');coordinator=Coordinator(h,adapter,initial,run_id,comparison,str(condition['original_sample']))
            rows=[];per_node=np.zeros(45669,dtype=np.float64)
            old_h=np.empty((485,len(h.h_ids)),dtype=np.float32);boundary=np.empty((485,len(h.source_ids)),dtype=np.float32)
            x_h=np.empty_like(old_h);chemical=np.empty_like(old_h)
            with native_full_forbidden() as guard:
                for k in range(485):
                    old=coordinator.state;x=input_full(stimulus[c,k,0],inputs)
                    prepared=coordinator.prepare(k,x,'SOURCE_RAW')
                    old_h[k]=prepared.h_request.old_h;boundary[k]=prepared.h_request.boundary;x_h[k]=prepared.h_request.x_h;chemical[k]=prepared.h_result.chemical
                    actual=coordinator.commit(prepared);trace[c,k]=actual
                    row=dict(step_id=k,time_after_label=float(clock[k]))
                    for group,ids in groups.items():
                        row.update({group+'_'+key:value for key,value in errors(actual,reference[c,k],ids).items()})
                        row[group+'_nonfinite']=int((~np.isfinite(actual[ids])).sum())
                    rows.append(row);per_node[:]=np.maximum(per_node,np.abs(actual.astype(np.float64)-reference[c,k].astype(np.float64)))
                    for event in coordinator.logs[-2:]:status.write(json.dumps(dict(condition=c,**event))+'\n')
                assert h.step_count==coordinator.next_step_id==485 and guard['forbidden_native_call_count']==0
            with (case/'step_errors.csv').open('w',newline='',encoding='utf-8') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
            np.save(case/'per_node_max_abs.npy',per_node);np.save(case/'activity_central.npy',trace[c,:,central].T);np.save(case/'activity_T4T5.npy',trace[c,:,tt].T)
            np.savez(case/'SOURCE_RAW_step_io.npz',old_H=old_h,boundary_before=boundary,x_H=x_h,new_H_expected=trace[c,:,h.h_ids].T,
                chemical_expected=chemical,H_global_ids=h.h_ids,source_global_ids=h.source_ids,step_id=np.arange(485),time_after_label=clock,dt_s=np.float32(.005))
            records.append(dict(condition=condition,steps=485,guard=guard,committed_steps=485,H_steps=485,max_abs={g:max(row[g+'_max_abs'] for row in rows) for g in groups},
                violations={g:sum(row[g+'_violations'] for row in rows) for g in groups},nonfinite={g:sum(row[g+'_nonfinite'] for row in rows) for g in groups},wall_s=time.monotonic()-started))
            trace.flush();print('BASELINE_CONDITION',name,condition['original_sample'],json.dumps(records[-1]['max_abs']),flush=True)
        status.close();trace.flush();assert adapter.calls==1940
        passed=all(sum(record['violations'].values())==sum(record['nonfinite'].values())==0 for record in records)
        result=dict(status='PASS_THREE_CANDIDATE_COMPONENT_BASELINE' if passed else 'FAIL_BASELINE_NUMERICAL',run_identity=identity,conditions=records,
            H_steps=1940,R_steps=adapter.calls,prepared=1940,committed=1940,native_H_production_updates=0,FPGA_execution=False,
            formal_sham=False,formal_ablation=False,Full_used_as_production_R=False)
        dump(dest/'result.json',result);seal(dest);all_results.append(result)
        del trace,adapter,service;torch.cuda.empty_cache()
    assert all(file_hash(BUNDLE/e['path'])==e['sha256'] for e in entries)
    assert all(file_hash(HERE/path)==value for path,value in code.items())
    dump(out/'result.json',dict(status='PASS_CANDIDATE_NO_INTERVENTION_BASELINES' if all(r['status'].startswith('PASS') for r in all_results) else 'FAIL',
        candidates=[r['run_identity']['candidate'] for r in all_results],wall_s=time.monotonic()-start,formal_spec_status='PENDING',formal_ablation_executed=False))
    seal(out);print('BASELINES_DONE',time.monotonic()-start,flush=True)

if __name__=='__main__':main()

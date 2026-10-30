"""Post-run audit of all recorded H/R states and exact old-state requests."""
import csv
from common import *
from h_step import HRequest,StepTag,request_hash

def main():
    out=HERE/'artifacts/baseline_audit_r1'
    if out.exists():raise SystemExit('Preserve existing audit')
    out.mkdir(parents=True)
    meta=load(BUNDLE/'screen_manifest.json');reference=np.load(host_path(meta['Full_reference_path'])/'activities_full.npy',mmap_mode='r')
    initial=np.load(BUNDLE/'initial_state_full.npy');stim=np.load(BUNDLE/'stimulus.npy');clock=np.load(BUNDLE/'time.npy')
    central=np.load(BUNDLE/'central_node_indices.npy');types=np.load(BUNDLE/'cell_types.npy');tt=central[np.isin(types,['T4'+s for s in 'abcd']+['T5'+s for s in 'abcd'])]
    table=[];proofs=[]
    for profile in meta['profiles']:
        name=profile['candidate'];source=HERE/'artifacts/no_intervention_r1'/name;manifest_verify(source)
        info=load(source/'run_identity.json');res=load(source/'result.json');assert res['status'].startswith('PASS')
        assert info['common_data_id']==meta['common_data_id'] and info['profile']==profile
        for path,digest in info['code_sha256'].items():assert file_hash(HERE/path)==digest
        h=HUpdater(BUNDLE/'candidates'/name/'static_boundary_gpu_native.npz');inputs=validate_parameters(h,BUNDLE/'expanded_parameters.npz')
        r=np.setdiff1d(np.arange(45669,dtype=np.int64),h.h_ids);groups=dict(H=h.h_ids,R=r,full=np.arange(45669),central=central,T4T5=tt)
        activity=np.load(source/'activities_full.npy',mmap_mode='r');assert activity.shape==reference.shape==(4,485,45669)
        events=[json.loads(line) for line in (source/'step_status.jsonl').read_text().splitlines()];assert len(events)==3880
        for c,condition in enumerate(info['conditions']):
            case=source/f'condition_{c:02d}';v=np.load(case/'SOURCE_RAW_step_io.npz');csvrows=list(csv.DictReader((case/'step_errors.csv').open(encoding='utf-8')))
            assert v['old_H'].shape==(485,len(h.h_ids)) and v['boundary_before'].shape==(485,len(h.source_ids))
            assert np.array_equal(v['H_global_ids'],h.h_ids) and np.array_equal(v['source_global_ids'],h.source_ids) and np.array_equal(v['time_after_label'],clock)
            accum={g:dict(max_abs=0.,sum_abs=0.,sum_square=0.,violations=0) for g in groups};pernode=np.zeros(45669,dtype=np.float64);old=initial
            for k in range(485):
                pre,post=events[2*(c*485+k):2*(c*485+k)+2];assert pre['status']=='PREPARED' and post['status']=='COMMITTED'
                assert pre['condition']==post['condition']==c and pre['step_id']==post['step_id']==k and post['state_token']==k+1
                assert pre['old_full_digest']==array_hash(old) and pre['live_R_source_digest']==array_hash(old[h.source_ids]) and pre['old_H_digest']==array_hash(old[h.h_ids])
                x=input_full(stim[c,k,0],inputs);assert pre['input_digest']==post['input_digest']==array_hash(x)
                for key,data in [('old_H',old[h.h_ids]),('boundary_before',old[h.source_ids]),('x_H',x[h.h_ids]),('new_H_expected',activity[c,k,h.h_ids])]:assert np.array_equal(v[key][k],data),(name,c,k,key)
                tag=StepTag(info['run_id'],info['comparison_id'],str(condition['original_sample']),0,k,array_hash(old))
                req=HRequest(tag,'SOURCE_RAW',frozen(v['old_H'][k]),frozen(v['x_H'][k]),frozen(v['boundary_before'][k]),h.h_ids,h.source_ids,h.circuit_digest)
                computed=h.step(req);assert np.array_equal(computed.new_h,activity[c,k,h.h_ids]) and np.array_equal(computed.chemical,v['chemical_expected'][k])
                assert pre['request_digest']==post['H_request_digest']==request_hash(req)
                assert post['full_after_digest']==array_hash(activity[c,k]) and post['H_after_digest']==array_hash(activity[c,k,h.h_ids]) and post['R_after_digest']==array_hash(activity[c,k,r]) and post['native_H_update_count']==0
                assert np.isfinite(activity[c,k]).all()
                delta=activity[c,k].astype(np.float64)-reference[c,k].astype(np.float64);pernode[:]=np.maximum(pernode,np.abs(delta))
                for g,ids in groups.items():
                    m=errors(activity[c,k],reference[c,k],ids)
                    for key,value in m.items():assert float(csvrows[k][g+'_'+key])==value,(name,c,k,g,key)
                    a=accum[g];a['max_abs']=max(a['max_abs'],m['max_abs']);a['sum_abs']+=np.abs(delta[ids]).sum();a['sum_square']+=(delta[ids]**2).sum();a['violations']+=m['violations']
                old=activity[c,k]
            assert np.array_equal(pernode,np.load(case/'per_node_max_abs.npy'))
            for g,ids in groups.items():
                a=accum[g];assert a['violations']==0
                table.append(dict(candidate=name,condition=meta['conditions'][c],group=g,n_nodes=len(ids),steps=485,max_abs=a['max_abs'],
                    mae=a['sum_abs']/(485*len(ids)),rmse=float(np.sqrt(a['sum_square']/(485*len(ids)))),violations=0,nonfinite=0,
                    final_max_abs=errors(activity[c,-1],reference[c,-1],ids)['max_abs']))
        proofs.append(dict(candidate=name,status='PASS',prepared=1940,committed=1940,all1940_H_recomputed_bitwise=True,live_own_old_R_boundaries=True,
            native_H_production_updates=0,source_manifest_sha256=file_hash(source/'artifact_manifest.json')))
        print('BASELINE_AUDIT',name,flush=True)
    with (out/'baseline_error_summary.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
    dump(out/'result.json',dict(status='PASS_THREE_CANDIDATE_ALL_STATE_CHAIN_AND_H_VECTOR_AUDIT',proofs=proofs,
        common_data_id=meta['common_data_id'],formal_sham=False,formal_ablation=False,FPGA_execution=False,evidence_level='READ_ONLY_RECOMPUTED_POST_RUN_AUDIT'))
    seal(out)

if __name__=='__main__':main()

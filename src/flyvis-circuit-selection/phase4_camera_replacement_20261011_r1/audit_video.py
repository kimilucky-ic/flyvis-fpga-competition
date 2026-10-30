"""Independent recorded-evidence audit, never a production R provider."""
import argparse,csv
from common import *
from h_step import HRequest,StepTag,request_hash


def main():
    p=argparse.ArgumentParser();p.add_argument('--source-run',default='python_camera_609_r1');p.add_argument('--run',default='audit_camera_609_r1')
    args=p.parse_args();out=HERE/'artifacts'/args.run
    if out.exists():raise SystemExit('Preserve existing audit; choose new namespace')
    out.mkdir(parents=True)
    meta,model,h,inputs,stimulus,initial,t,after,entries=read_input();n=len(t)
    source=HERE/'artifacts'/args.source_run;manifest_verify(source)
    info=load(source/'run_identity.json');result=load(source/'result.json')
    receipt=load(HERE/'A_ACCEPTED_REFERENCE.json');ref=host_path(receipt['Full_reference_path']);verify_reference(ref)
    ri=load(ref/'run_identity.json')
    assert info['comparison_id']==ri['comparison_id']==meta['comparison_id']
    assert result['status']=='PASS_CLOSED_LOOP_NUMERICAL'
    assert result['native_H_production_updates']==0 and result['production_guard']['forbidden_native_call_count']==0
    assert result['independent_H_steps']==result['unified_committed_steps']==n
    for key in ['expanded_parameters_sha256','initial_state_sha256','stimulus_sha256','checkpoint_sha256',
        'candidate_sha256','node_map_sha256','time_sha256','activity_time_sha256','numeric_profile_sha256','metric_profile_sha256']:
        assert info[key]==ri[key],key
    actual=np.load(source/'activities_full.npy',mmap_mode='r');reference=np.load(ref/'activities_full.npy',mmap_mode='r')
    assert actual.shape==reference.shape==(1,n,45669)
    events=[json.loads(line) for line in (source/'step_status.jsonl').read_text().splitlines()]
    assert len(events)==2*n
    central=np.load(BUNDLE/'central_node_indices.npy');types=np.load(BUNDLE/'cell_types.npy')
    tt=central[np.isin(types,['T4'+s for s in 'abcd']+['T5'+s for s in 'abcd'])]
    r=np.setdiff1d(np.arange(45669,dtype=np.int64),h.h_ids)
    groups=dict(H=h.h_ids,R=r,full=np.arange(45669),central=central,T4T5=tt)
    csv_rows=list(csv.DictReader((source/'step_errors.csv').open(encoding='utf-8')))
    assert len(csv_rows)==n
    accum={name:dict(max_abs=0.,sum_abs=0.,sum_square=0.,violations=0,nonfinite=0,max_step_mae=0.,max_step_rmse=0.) for name in groups}
    v=np.load(source/'SOURCE_RAW_step_io.npz',allow_pickle=False)
    assert v['boundary_before'].shape==(n,1364)
    assert np.array_equal(v['H_global_ids'],h.h_ids) and np.array_equal(v['incoming_source_global_ids'],h.source_ids)
    assert np.array_equal(v['step_id'],np.arange(n)) and np.array_equal(v['input_time'],t) and np.array_equal(v['activity_time'],after)
    old=initial
    for k in range(n):
        prep,commit=events[2*k:2*k+2]
        assert prep['status']=='PREPARED' and commit['status']=='COMMITTED'
        assert prep['step_id']==commit['step_id']==k and commit['state_token']==k+1
        assert prep['epoch']==commit['epoch']==0 and commit['native_H_update_count']==0
        x=make_input(stimulus[0,k,0],inputs)
        assert prep['old_full_digest']==array_hash(old) and prep['old_H_digest']==array_hash(old[h.h_ids])
        assert prep['live_R_source_digest']==array_hash(old[h.source_ids])
        assert prep['input_digest']==commit['input_digest']==array_hash(x)
        for key,data in [('old_H',old[h.h_ids]),('boundary_before',old[h.source_ids]),('x_H',x[h.h_ids]),('new_H_expected',actual[0,k,h.h_ids])]:
            assert np.array_equal(v[key][k],data),(key,k)
        tag=StepTag(info['run_id'],meta['comparison_id'],CONDITION,0,k,array_hash(old))
        req=HRequest(tag,'SOURCE_RAW',frozen(v['old_H'][k]),frozen(v['x_H'][k]),frozen(v['boundary_before'][k]),h.h_ids,h.source_ids,h.circuit_digest)
        assert prep['request_digest']==commit['H_request_digest']==request_hash(req)
        replay=h.step(req)
        assert np.array_equal(replay.new_h,v['new_H_expected'][k]) and np.array_equal(replay.chemical,v['chemical_expected'][k])
        assert commit['full_after_digest']==array_hash(actual[0,k])
        assert commit['H_after_digest']==array_hash(actual[0,k,h.h_ids]) and commit['R_after_digest']==array_hash(actual[0,k,r])
        assert int(csv_rows[k]['step_id'])==k
        for name,ids in groups.items():
            metric=errors(actual[0,k],reference[0,k],ids)
            for key,val in metric.items():assert float(csv_rows[k][name+'_'+key])==val,(name,key,k)
            delta=actual[0,k,ids].astype(np.float64)-reference[0,k,ids].astype(np.float64)
            item=accum[name];item['max_abs']=max(item['max_abs'],metric['max_abs'])
            item['sum_abs']+=np.abs(delta).sum();item['sum_square']+=(delta*delta).sum()
            item['max_step_mae']=max(item['max_step_mae'],metric['mae']);item['max_step_rmse']=max(item['max_step_rmse'],metric['rmse'])
            item['violations']+=metric['violations'];item['nonfinite']+=int((~np.isfinite(actual[0,k,ids])).sum())
        old=actual[0,k]
    summary=[]
    for name,ids in groups.items():
        a=accum[name];count=n*len(ids)
        summary.append(dict(group=name,n_nodes=len(ids),steps=n,max_abs=a['max_abs'],mae=a['sum_abs']/count,
            rmse=float(np.sqrt(a['sum_square']/count)),max_step_mae=a['max_step_mae'],max_step_rmse=a['max_step_rmse'],
            violations=a['violations'],nonfinite=a['nonfinite'],final_max_abs=errors(actual[0,-1],reference[0,-1],ids)['max_abs']))
        assert a['nonfinite']==a['violations']==0
    assert np.array_equal(np.load(source/'activity_central.npy'),actual[0,:,central].T)
    assert np.array_equal(np.load(source/'activity_T4T5.npy'),actual[0,:,tt].T)
    assert np.array_equal(np.load(source/'final_full_state.npy'),actual[0,-1])
    with (out/'error_summary.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    dump(out/'result.json',dict(status='PASS_INDEPENDENT_CAMERA609_STATE_CHAIN_AND_VECTOR_AUDIT',evidence_level='READ_ONLY_POST_RUN_EVIDENCE_AUDIT',
        comparison_id=meta['comparison_id'],Full_run_id=ri['run_id'],Python_run_id=info['run_id'],
        summary=summary,prepared=n,committed=n,all_state_hashes_match=True,live_R_boundary_from_own_old_state=True,
        all_camera_steps_H_recomputed_bitwise=True,initial_state_exact=True,model_dt_s=.005,
        native_H_production_updates=0,source_run=str(source),Full_reference=str(ref),
        source_manifest_sha256=file_hash(source/'artifact_manifest.json'),Full_manifest_sha256=file_hash(ref/'artifact_manifest.json'),
        vectors_sha256=file_hash(source/'SOURCE_RAW_step_io.npz'),state_chain_sha256=file_hash(source/'step_status.jsonl'),
        atol=1e-5,rtol=1e-5,FPGA_execution=False,code_sha256=file_hash(Path(__file__))))
    seal(out);print(json.dumps(summary),flush=True)

if __name__=='__main__':main()

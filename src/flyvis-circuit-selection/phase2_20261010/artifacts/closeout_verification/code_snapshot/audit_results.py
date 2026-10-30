"""Independent offline validation of complete trajectories and transaction chain."""
from pathlib import Path
import argparse, csv, json
import numpy as np
from h_step import HUpdater, array_hash, file_hash

HERE=Path(__file__).resolve().parent
ART=HERE/'artifacts'
BUNDLE=HERE.parents[2]/'fly/gpu_phase2/artifacts/reference_bundle_v1'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--bundle',type=Path,default=BUNDLE)
    parser.add_argument('--static-path',type=Path,default=HERE.parent/'round1_20261010/artifacts/B_T5c/static_boundary.npz')
    parser.add_argument('--full-run',default='full_cpu_r2')
    parser.add_argument('--source-run',default='source_gpu_r1')
    parser.add_argument('--aggregate-run',default='aggregate_gpu_r1')
    parser.add_argument('--feedback-run',default='live_feedback_r1')
    parser.add_argument('--reproduce-run',default='reproduce_prefix_r1')
    parser.add_argument('--profile',choices=['CPU_CANONICAL','OFFICIAL_NATIVE_GPU_EXPANDED'],default='CPU_CANONICAL')
    parser.add_argument('--run',default='final_audit')
    args=parser.parse_args()
    bundle=args.bundle
    out=ART/args.run
    if out.exists():raise SystemExit('Existing audit preserved')
    out.mkdir()
    u=HUpdater(args.static_path)
    a0=np.load(bundle/'initial_state_full.npy',allow_pickle=False)
    full=np.load(ART/args.full_run/'activities_full.npy',mmap_mode='r',allow_pickle=False)
    metadata=json.loads((ART/args.full_run/'run_identity.json').read_text())
    central=np.load(bundle/'central_node_indices.npy',allow_pickle=False)
    types=np.load(bundle/'cell_types.npy',allow_pickle=False)
    t4t5=central[np.isin(types,['T4'+s for s in 'abcd']+['T5'+s for s in 'abcd'])]
    r_ids=np.setdiff1d(np.arange(45669,dtype=np.int64),u.h_ids)
    scopes=dict(H=u.h_ids,R=r_ids,full=np.arange(45669),central=central,T4T5=t4t5)
    files_verified=0
    for run in [args.full_run,args.source_run,args.aggregate_run,args.feedback_run,args.reproduce_run]:
        manifest=json.loads((ART/run/'artifact_manifest.json').read_text())
        for item in manifest:
            path=ART/run/item['path'].replace('\\','/')
            assert path.stat().st_size==item['bytes'] and file_hash(path)==item['sha256']
            files_verified+=1
    results=[]
    for run in [args.source_run,args.aggregate_run]:
        identity=json.loads((ART/run/'run_identity.json').read_text())
        assert identity['comparison_id']==metadata['comparison_id']
        for field in ['checkpoint_sha256','expanded_parameters_sha256','initial_state_sha256','stimulus_sha256',
                'time_axis_sha256','candidate_sha256','H_ids_hash','node_map_sha256','edge_partition_sha256']:
            assert identity[field]==metadata[field]
        assert identity['circuit_sha256']==u.circuit_digest
        run_result=json.loads((ART/run/'result.json').read_text())
        assert run_result['status']=='PASS_CLOSED_LOOP_NUMERICAL'
        assert run_result['input_bundle_unchanged'] and run_result['native_H_production_updates']==0
        assert len(run_result['production_guards'])==4
        assert all(g['forbidden_native_call_count']==0 and g['independent_H_steps']==g['committed_steps']==485
            for g in run_result['production_guards'])
        actual=np.load(ART/run/'activities_full.npy',mmap_mode='r',allow_pickle=False)
        assert actual.shape==full.shape==(4,485,45669)
        trace=[json.loads(line) for line in (ART/run/'step_status.jsonl').read_text().splitlines()]
        assert len(trace)==4*485*2
        cases=[]
        for c in range(4):
            csv_rows=list(csv.DictReader((ART/run/f'condition_{c:02d}/step_errors.csv').open()))
            maximum=0.0;violations=0;bitwise=True
            per_node=np.zeros(45669,dtype=np.float64)
            h_both=np.load(ART/run/f'condition_{c:02d}/H_before_after.npy',allow_pickle=False)
            assert np.array_equal(h_both[0,0],a0[u.h_ids])
            events=[row for row in trace if row['condition']==c]
            for k in range(485):
                prepared,committed=events[2*k:2*k+2]
                old=a0 if k==0 else np.asarray(actual[c,k-1])
                current=np.asarray(actual[c,k])
                assert prepared['status']=='PREPARED' and committed['status']=='COMMITTED'
                assert prepared['step_id']==committed['step_id']==k and committed['state_token']==k+1
                assert prepared['old_full_digest']==array_hash(old)
                assert prepared['live_R_source_digest']==array_hash(np.ascontiguousarray(old[u.source_ids]))
                assert committed['full_after_digest']==array_hash(current)
                assert committed['native_H_update_count']==0
                assert np.array_equal(h_both[k,0],old[u.h_ids]) and np.array_equal(h_both[k,1],current[u.h_ids])
                delta=np.abs(current.astype(np.float64)-full[c,k].astype(np.float64))
                allowed=1e-5+1e-5*np.abs(full[c,k].astype(np.float64))
                count=int((delta>allowed).sum())
                for name,ids in scopes.items():
                    signed=current[ids].astype(np.float64)-full[c,k,ids].astype(np.float64)
                    values=dict(max_abs=float(np.abs(signed).max()),mae=float(np.abs(signed).mean()),
                        rmse=float(np.sqrt((signed*signed).mean())),violations=int((delta[ids]>allowed[ids]).sum()))
                    for metric,value in values.items():
                        assert float(csv_rows[k][name+'_'+metric])==value
                per_node=np.maximum(per_node,delta)
                maximum=max(maximum,float(delta.max()));violations+=count
                bitwise=bitwise and np.array_equal(current,full[c,k])
            assert np.array_equal(per_node,np.load(ART/run/f'condition_{c:02d}/per_node_max_abs.npy'))
            assert violations==0
            assert np.array_equal(np.load(ART/run/f'condition_{c:02d}/final_full_error.npy'),
                actual[c,-1].astype(np.float64)-full[c,-1].astype(np.float64))
            cases.append(dict(condition=c,max_full_abs=maximum,violations=violations,bitwise_equal_to_official_Full=bitwise,
                live_snapshot_chain_verified_steps=485))
        results.append(dict(run=run,status='PASS_OFFLINE_FULL_STATE_AND_LIVE_CHAIN_AUDIT',cases=cases))
    feedback=json.loads((ART/args.feedback_run/'result.json').read_text())
    reproduction=json.loads((ART/args.reproduce_run/'result.json').read_text())
    assert feedback['status']=='PASS_LIVE_FEEDBACK_AND_GPU_NEGATIVE_TESTS'
    assert all(test['status']=='PASS' for test in feedback['negative_tests'])
    assert reproduction['status']=='PASS_BITWISE_LIVE_PREFIX_REPRODUCTION'
    params=json.loads((bundle/'identity_manifest.json').read_text())
    stimulus=json.loads((bundle/'stimulus_manifest.json').read_text())
    source=np.load(ART/args.source_run/'activities_full.npy',mmap_mode='r')
    aggregate=np.load(ART/args.aggregate_run/'activities_full.npy',mmap_mode='r')
    pair=[]
    for c in range(4):
        difference=aggregate[c].astype(np.float64)-source[c].astype(np.float64)
        pair.append(dict(condition=c,max_full_abs=float(np.abs(difference).max()),
            max_H_abs=float(np.abs(difference[:,u.h_ids]).max()),mae=float(np.abs(difference).mean()),
            rmse=float(np.sqrt((difference*difference).mean())),
            violations=int((np.abs(difference)>1e-5+1e-5*np.abs(source[c].astype(np.float64))).sum())))
    assert all(row['violations']==0 for row in pair)
    (out/'aggregate_vs_source.json').write_text(json.dumps(pair,indent=2),encoding='utf-8')
    numeric=dict(state='IEEE754 float32',dt_s=.005,activation='ReLU at presynaptic release',
        Euler='inverse_tau * (((-old+bias)+chemical)+x), then old+velocity*dt',
        expansion_device=args.profile,full_reference_device=metadata['device'],
        expansion_rule='H/R/Full use identical expanded float32 arrays; CPU and native CUDA profiles are separate comparisons',
        SOURCE_RAW='NumPy add.at in original HH/RH edge order',CURRENT_AGG='NumPy HH reduction plus live NumPy RH reduction',
        R='PyTorch CUDA scatter_add over HR/RR only',hardware_profile=None)
    metric=dict(atol=1e-5,rtol=1e-5,criterion='abs(actual-reference)<=atol+rtol*abs(reference)',
        scope='all45669 nodes, every485 steps, each4 conditions; H/R/central/T4T5',
        causal_probes='isolated +0.25 H/R branches; nonzero next-state and returned-R contribution',
        faults='15 actual-GPU-service tests, all must pass; no partial R commit or fallback')
    for name,value in [('numeric_profile.json',numeric),('metric_profile.json',metric)]:
        (out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    result=dict(status='PASS_SOFTWARE_CLOSED_LOOP',gate='G2 reference floating-point four-condition scope',
        evidence_level='SOFTWARE_CLOSED_LOOP',files_hash_verified=files_verified,comparison_id=metadata['comparison_id'],
        model_id=params['model_id'],source_commit=params['source_commit'],checkpoint_sha256=params['checkpoint_sha256'],
        connectome_sha256=params['connectome_spec_sha256'],expanded_parameters_sha256=params['expanded_parameters_sha256'],
        initial_state_sha256=params['initial_state_sha256'],stimulus_sha256=stimulus['stimulus_sha256'],
        preprocess_sha256=file_hash(bundle/'stimulus_manifest.json'),time_axis_sha256=stimulus['time_sha256'],
        numeric_profile_sha256=file_hash(out/'numeric_profile.json'),metric_profile_sha256=file_hash(out/'metric_profile.json'),
        H_ids_hash=u.h_order_digest,node_map_sha256=metadata['node_map_sha256'],edge_partition_sha256=metadata['edge_partition_sha256'],
        condition_original_samples=[0,1,12,13],nodes=45669,H_nodes=67,R_nodes=45602,steps_per_condition=485,dt_s=.005,
        numerical_audits=results,live_feedback=feedback['feedback'],actual_GPU_negative_tests=len(feedback['negative_tests']),
        fresh_process_prefix_reproduction=reproduction['status'],
        native_H_production_updates=0,production_inputs_from_live_committed_R=True,atomic_commit_fault_tests='PASS',
        parameter_profile=args.profile,full_reference_provenance=metadata.get('provenance','Official Full executed in this lane'),
        stage2_scope_limits=[
            'CURRENT_AGG tested with NumPy host RH reduction; GPU RH/PL reduction not accepted',
            'Final FPGA H/numeric/physical interface/header remain unfrozen','No RTL, synthesis, bitstream or board evidence',
            'Fresh-process repetition covers OFF0 first32 steps; complete four-condition repeat not performed'])
    (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=result['status'],files_hash_verified=files_verified,runs=[r['run'] for r in results],
        actual_GPU_negative_tests=result['actual_GPU_negative_tests'])),flush=True)

if __name__=='__main__':main()

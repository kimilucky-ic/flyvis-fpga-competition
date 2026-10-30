"""Freeze three original candidates and G2 four conditions; no intervention."""
from pathlib import Path
import sys,json,shutil,hashlib
import numpy as np

HERE=Path(__file__).resolve().parent
PREVIOUS=HERE.parent/'phase2_20261010'
A=HERE.parents[2]/'fly/gpu_phase2'
source=A/'artifacts/reference_bundle_gpu_native_v1'
sys.path.insert(0,str(PREVIOUS))
from h_step import HUpdater,file_hash,array_hash
from run_closed_loop import manifest_verify,validate_parameters

def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def seal(path):dump(path/'artifact_manifest.json',dict(files=[dict(path=p.relative_to(path).as_posix(),bytes=p.stat().st_size,sha256=file_hash(p)) for p in sorted(path.rglob('*')) if p.is_file() and p.name!='artifact_manifest.json']))
def a_array_sha(value):return hashlib.sha256(str(value.dtype).encode()+str(value.shape).encode()+value.tobytes()).hexdigest()
def copy_verified(source,target):
    if target.exists():assert file_hash(source)==file_hash(target),'preserve existing dependency'
    else:shutil.copyfile(source,target)

def main():
    bundle=HERE/'input_bundle_r2'
    if bundle.exists():raise SystemExit('Preserve frozen input; use new namespace')
    manifest_verify(source)
    deps=HERE/'dependencies';(deps/'b_core').mkdir(parents=True,exist_ok=True);(deps/'a_snapshot').mkdir(exist_ok=True)
    for name in ['h_step.py','coordinator.py','gpu_adapter.py','run_closed_loop.py','run_negative_tests.py']:
        copy_verified(PREVIOUS/name,deps/'b_core'/name)
    for name in ['r_only.py','full_oracle.py']:
        assert file_hash(A/name)==file_hash(PREVIOUS/'dependencies/a_snapshot'/name)
        copy_verified(A/name,deps/'a_snapshot'/name)
    bundle.mkdir()
    for name in ['expanded_parameters.npz','initial_state_full.npy','stimulus.npy','time.npy','conditions.csv',
        'stimulus_manifest.json','identity_manifest.json','nodes_full.csv','input_node_indices.npy','central_node_indices.npy','cell_types.npy']:
        shutil.copyfile(source/name,bundle/name)
    full=PREVIOUS/'artifacts/full_gpu_reference_a'
    assert file_hash(full/'activities_full.npy')=='1b8a684c18225100bd4b34e3ba61e8f55b3bf97a15eaecb4aca311932ab9ac80'
    ref_id=json.loads((full/'run_identity.json').read_text())
    identity=json.loads((bundle/'identity_manifest.json').read_text())
    for key,name in [('expanded_parameters_sha256','expanded_parameters.npz'),('initial_state_sha256','initial_state_full.npy'),('stimulus_sha256','stimulus.npy'),('time_axis_sha256','time.npy')]:
        assert ref_id[key]==file_hash(bundle/name)
    copy_verified(full/'run_identity.json',deps/'Full_G2_reference_identity.json')
    with np.load(bundle/'expanded_parameters.npz') as archive:p={key:archive[key] for key in archive.files}
    assert np.array_equal(p['original_edge_index'],np.arange(1513231,dtype=np.int64))
    profiles=[]
    for name,n,hh in [('B_T5c',67,970),('A_T4c',92,1437),('C_T4T5_all_centers',298,7663)]:
        dest=bundle/'candidates'/name;shutil.copytree(source/'candidates'/name,dest)
        manifest=json.loads((dest/'candidate_manifest.json').read_text())
        with np.load(HERE.parent/'round1_20261010/artifacts'/name/'static_boundary.npz') as z:data={k:z[k].copy() for k in z.files}
        ids=np.array(manifest['h_global_node_indices'],dtype=np.int64)
        assert len(ids)==n and np.array_equal(ids,data['global_node_id'])
        mask=np.zeros(45669,dtype=bool);mask[ids]=True
        partitions=dict(HH=np.flatnonzero(mask[p['source_global']]&mask[p['target_global']]),
            RH=np.flatnonzero(~mask[p['source_global']]&mask[p['target_global']]),
            HR=np.flatnonzero(mask[p['source_global']]&~mask[p['target_global']]),
            RR=np.flatnonzero(~mask[p['source_global']]&~mask[p['target_global']]))
        assert {k:len(v) for k,v in partitions.items()}==manifest['partition_counts']
        assert len(partitions['HH'])==hh and np.array_equal(np.sort(np.concatenate(list(partitions.values()))),np.arange(1513231))
        assert all(a_array_sha(v)==manifest['partition_ids_digests'][k] for k,v in partitions.items())
        data['bias']=p['bias'][ids].copy();data['raw_initial_bias']=data['bias'].copy()
        data['time_const_s']=p['time_const'][ids].copy()
        data['inv_max_tau_dt']=np.ones(n,dtype=np.float32)/np.maximum(data['time_const_s'],np.float32(.005))
        for route,part in [('internal','HH'),('incoming','RH'),('outgoing','HR')]:
            edges=data[route+'_edge_id'];assert np.array_equal(edges,partitions[part])
            assert np.array_equal(data[route+'_source_index'],p['source_global'][edges]) and np.array_equal(data[route+'_target_index'],p['target_global'][edges])
            for field,expanded in [('weight','effective_weight'),('sign','sign'),('syn_count','syn_count'),('syn_strength','syn_strength')]:data[route+'_'+field]=p[expanded][edges].copy()
        np.savez_compressed(dest/'static_boundary_gpu_native.npz',**data)
        np.savez(dest/'validated_partition_ids.npz',**partitions)
        updater=HUpdater(dest/'static_boundary_gpu_native.npz');validate_parameters(updater,bundle/'expanded_parameters.npz')
        profiles.append(dict(candidate=name,n_h=n,n_r=45669-n,partition_counts=manifest['partition_counts'],
            candidate_sha256=file_hash(dest/'candidate_manifest.json'),H_ids_sha256=updater.h_order_digest,
            source_ids_sha256=updater.source_order_digest,n_boundary_sources=len(updater.source_ids),static_sha256=updater.circuit_digest,
            validated_partition_sha256=file_hash(dest/'validated_partition_ids.npz'),original_edge_order_and_all1513231_coverage=True))
    metrics=dict(schema='B_screen_numeric_baseline/v1',atol=1e-5,rtol=1e-5,scope='every H/R/full/central65/centralT4T5 state every485 steps fourconditions',
        nonfinite_allowed=0,pre_registered=True,formal_functional_metric_profile='WAITING_ARCH_SPEC',
        prospective_outputs=['stepmax/mae/rmse','all-node deltas','target/central T4T5 traces','outgoing/incoming current changes'],
        ablation_operation=None,ablation_start_step=None,formal_ablation_executed=False)
    dump(bundle/'baseline_metric_profile.json',metrics)
    common=dict(checkpoint=identity['checkpoint_sha256'],expanded=file_hash(bundle/'expanded_parameters.npz'),a0=file_hash(bundle/'initial_state_full.npy'),
        stimulus=file_hash(bundle/'stimulus.npy'),time=file_hash(bundle/'time.npy'),conditions=file_hash(bundle/'conditions.csv'),metrics=file_hash(bundle/'baseline_metric_profile.json'))
    common_id=hashlib.sha256(json.dumps(common,sort_keys=True).encode()).hexdigest()
    dump(bundle/'screen_manifest.json',dict(status='PASS_THREE_CANDIDATE_FROZEN_INPUT_AND_ALL_EDGE_AUDIT',common_data_id=common_id,common=common,
        conditions=['OFF0','ON0','OFF180','ON180'],shape=[4,485,1,721],dt_s=.005,initial_shape=[45669],
        time_semantics='Preserve original G2 saved-after-update labels time[k]=k*.005-1; before state a[k], after a[k+1]; no relabel shift',
        Full_reference_path=str(full),Full_reference_sha256=file_hash(full/'activities_full.npy'),profiles=profiles,
        formal_spec_status='NOT_FOUND_PENDING_ARCH_FILE',hardware67_workstream_unchanged=True,code_sha256=file_hash(Path(__file__))))
    seal(bundle);seal(deps)
    print(json.dumps(dict(status='PASS_PREPARED_THREE_CANDIDATES',common_data_id=common_id,profiles=profiles)),flush=True)

if __name__=='__main__':main()

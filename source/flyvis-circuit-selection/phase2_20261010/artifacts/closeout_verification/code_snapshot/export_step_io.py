"""Export accepted live-run H input/output arrays; verify each exported H.step.

These are float32 software fixtures, not an RTL/finite-width format freeze.
Old R sources come from each Replacement run's own previous committed state.
"""
from pathlib import Path
import json, shutil
import numpy as np
from h_step import HUpdater, HRequest, StepTag, frozen, array_hash, file_hash
from prepare_native_profile import seal

HERE=Path(__file__).resolve().parent
BUNDLE=HERE.parents[2]/'fly/gpu_phase2/artifacts/reference_bundle_gpu_native_v1'
STATIC=HERE/'artifacts/native_gpu_inputs/static_boundary_gpu_native.npz'
OUT=HERE/'artifacts/native_gpu_step_io'


def main():
    if OUT.exists():raise SystemExit('Existing IO export preserved')
    OUT.mkdir()
    a0=np.load(BUNDLE/'initial_state_full.npy',allow_pickle=False)
    stimulus=np.load(BUNDLE/'stimulus.npy',allow_pickle=False)
    time_axis=np.load(BUNDLE/'time.npy',allow_pickle=False)
    with np.load(BUNDLE/'expanded_parameters.npz',allow_pickle=False) as params:
        input_ids=params['input_node_index'].copy()
    for name in ['initial_state_full.npy','stimulus.npy','time.npy','conditions.csv']:
        shutil.copyfile(BUNDLE/name,OUT/name)
    for name in ['node_map.csv','candidate_manifest.json','edge_partition_ids.npz']:
        shutil.copyfile(BUNDLE/'candidates/B_T5c'/name,OUT/name)
    shutil.copyfile(STATIC,OUT/'static_boundary_gpu_native.npz')
    records=[]
    for run,layout in [('source_gpu_native_r1','SOURCE_RAW'),('aggregate_gpu_native_r1','CURRENT_AGG')]:
        directory=HERE/'artifacts'/run
        meta=json.loads((directory/'run_identity.json').read_text())
        assert meta['circuit_sha256']==file_hash(STATIC)
        assert meta['expanded_parameters_sha256']==file_hash(BUNDLE/'expanded_parameters.npz')
        activity=np.load(directory/'activities_full.npy',mmap_mode='r',allow_pickle=False)
        u=HUpdater(STATIC)
        old_h=np.empty((4,485,67),dtype=np.float32)
        x_h=np.empty_like(old_h)
        boundary=np.empty((4,485,1364 if layout=='SOURCE_RAW' else 67),dtype=np.float32)
        chemical=np.empty_like(old_h)
        new_h=np.empty_like(old_h)
        for c in range(4):
            for k in range(485):
                old=a0 if k==0 else np.asarray(activity[c,k-1])
                x=np.zeros(45669,dtype=np.float32)
                x[input_ids.reshape(-1)]=np.tile(stimulus[c,k,0],8)
                sources=frozen(old[u.source_ids])
                incoming=sources if layout=='SOURCE_RAW' else u.aggregate_sources(sources)
                tag=StepTag(meta['run_id'],meta['comparison_id'],str([0,1,12,13][c]),0,k,array_hash(old))
                request=HRequest(tag,layout,frozen(old[u.h_ids]),frozen(x[u.h_ids]),incoming,
                    u.h_ids,u.source_ids if layout=='SOURCE_RAW' else None,u.circuit_digest)
                computed=u.step(request)
                assert np.array_equal(computed.new_h,activity[c,k,u.h_ids])
                old_h[c,k]=request.old_h;x_h[c,k]=request.x_h;boundary[c,k]=incoming
                new_h[c,k]=computed.new_h;chemical[c,k]=computed.chemical
        file=OUT/(layout+'_step_io.npz')
        np.savez_compressed(file,old_H=old_h,x_H=x_h,boundary_before=boundary,new_H_expected=new_h,
            chemical_expected=chemical,H_global_ids=u.h_ids,H_local_ids=np.arange(67,dtype=np.int64),
            incoming_source_global_ids=u.source_ids,step_id=np.arange(485,dtype=np.int64),
            time_after_label=time_axis,condition_original_samples=np.array([0,1,12,13],dtype=np.int64),dt_s=np.float32(.005))
        records.append(dict(run=run,layout=layout,steps_checked=1940,all_H_recomputed_bitwise_equal=True,
            trajectory_sha256=file_hash(directory/'activities_full.npy'),export_sha256=file_hash(file),
            boundary_source='a0 for k=0, this Replacement run own committed a[k] for k>0; never Full R',
            comparison_id=meta['comparison_id']))
    result=dict(status='PASS_EXPORTED_LIVE_H_STEP_IO',evidence_level='SOFTWARE_FLOAT32_STEP_FIXTURES',
        records=records,code_sha256=file_hash(Path(__file__)),
        field_rule='Arrays [condition, step, local]; boundary excludes HH/bias/leak/x_H. new_H is uncommitted candidate.',
        limitation='No fixed point, transport header, RTL format or PL ownership decision.')
    (OUT/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    seal(OUT)
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()

"""800 actual GPU Full or live R-only + independent SOURCE_RAW H steps.

No Full trajectory feeds the production H/R path. FPGA mode fails closed until
the C board/numeric backend is delivered and reviewed; no Python fallback.
"""
import argparse,csv,platform,sys,time,uuid
import numpy as np
from common import *


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['FullGPU','PythonReplacement','FPGAReplacement'],required=True)
    parser.add_argument('--run',required=True)
    parser.add_argument('--reference',type=Path)
    args=parser.parse_args()
    if args.mode=='FPGAReplacement':
        raise StepError('NOT_READY','C reviewed real PL/numeric backend not delivered; FPGA mode unavailable, no fallback')
    agreement=load(HERE/'A_B_STRICT_IDENTITY_CONFIRMATION.json')
    assert agreement['status']=='PASS_A_B_STRICT_IDENTITY_CONFIRMED_BY_B'
    out=HERE/'artifacts'/args.run
    if out.exists():raise SystemExit('Existing run preserved; choose a new --run')
    out.mkdir(parents=True)
    torch=configure_gpu()
    from a_video_adapter import backend,BoundRService
    from gpu_adapter import GPUAdapter
    from coordinator import Coordinator
    start=time.monotonic()
    meta,model,h,inputs,stimulus,initial,input_time,after_time,entries=read_input()
    source_paths=[Path(__file__),HERE/'common.py',HERE/'a_video_adapter.py',
        HERE/'dependencies/b_core/h_step.py',HERE/'dependencies/b_core/coordinator.py',HERE/'dependencies/b_core/gpu_adapter.py']
    code={p.relative_to(HERE).as_posix():file_hash(p) for p in source_paths}
    central=np.load(BUNDLE/'central_node_indices.npy',allow_pickle=False)
    types=np.load(BUNDLE/'cell_types.npy',allow_pickle=False)
    t4t5=central[np.isin(types,['T4'+s for s in 'abcd']+['T5'+s for s in 'abcd'])]
    r_ids=np.setdiff1d(np.arange(45669,dtype=np.int64),h.h_ids)
    groups=dict(H=h.h_ids,R=r_ids,full=np.arange(45669),central=central,T4T5=t4t5)
    identity=dict(run_id=str(uuid.uuid4()),comparison_id=meta['comparison_id'],condition_id='01_off_right',original_sample=1,
        mode=args.mode,layout='SOURCE_RAW',steps=800,dt_s=.005,
        model_id=model['model_id'],checkpoint_sha256=model['checkpoint_sha256'],source_commit=model['source_commit'],
        expanded_parameters_sha256=model['expanded_parameters_sha256'],initial_state_sha256=model['initial_state_sha256'],
        stimulus_sha256=file_hash(BUNDLE/'stimulus.npy'),time_sha256=file_hash(BUNDLE/'time.npy'),
        activity_time_sha256=file_hash(BUNDLE/'activity_time.npy'),node_map_sha256=file_hash(BUNDLE/'candidates/B_T5c/node_map.csv'),
        candidate_sha256=file_hash(parameters_paths()[2]),circuit_sha256=h.circuit_digest,H_ids_hash=h.h_order_digest,
        numeric_profile_sha256=file_hash(BUNDLE/'numeric_profile.json'),metric_profile_sha256=file_hash(BUNDLE/'metric_profile.json'),
        code_sha256=code,A_backend_sha256=agreement['A_backend_sha256'],A_manifest_sha256=agreement['A_manifest_sha256'],
        A_callable_sha256=agreement['A_existing_callables_exact'],
        execution_kind='actual_new_computation',processing_mode='offline',
        execution_evidence_level='SOFTWARE_ACTUAL_GPU_FULL' if args.mode=='FullGPU' else 'SOFTWARE_ACTUAL_CLOSED_LOOP',
        torch=torch.__version__,numpy=np.__version__,python=platform.python_version(),gpu=torch.cuda.get_device_name(0),
        command=[sys.executable,*sys.argv],atol=1e-5,rtol=1e-5,no_new_warmup=True,no_extra_preframes=True)
    dump(out/'run_identity.json',identity)
    if args.mode=='FullGPU':
        full=backend('full');old=full.initial_state()
        assert np.array_equal(old.cpu().numpy(),initial)
    else:
        if args.reference is None:raise StepError('NO_REFERENCE','matching actual Full required')
        ref_identity=load(args.reference/'run_identity.json')
        assert ref_identity['mode']=='FullGPU' and ref_identity['comparison_id']==meta['comparison_id']
        reference=np.load(args.reference/'activities_full.npy',mmap_mode='r',allow_pickle=False)
        assert reference.shape==(1,800,45669) and reference.dtype==np.float32
        service=BoundRService();adapter=GPUAdapter(service,inputs)
        assert service.partition_counts==dict(HH=970,RH=5567,HR=8159,RR=1498535)
        with np.load(BUNDLE/'expanded_parameters.npz',allow_pickle=False) as p:
            assert not np.isin(p['target_global'][service.original_edge_ids],h.h_ids).any()
        c=Coordinator(h,adapter,initial,identity['run_id'],meta['comparison_id'],'01_off_right')
    states=np.lib.format.open_memmap(out/'activities_full.npy',mode='w+',dtype=np.float32,shape=(1,800,45669))
    old_h=np.empty((800,67),dtype=np.float32);new_h=np.empty_like(old_h)
    x_h=np.empty_like(old_h);boundary=np.empty((800,1364),dtype=np.float32);chemical=np.empty_like(old_h)
    rows=[];latency=[];per_node=np.zeros(45669,dtype=np.float64)
    audit={'forbidden_native_call_count':0}
    status=(out/'step_status.jsonl').open('w',encoding='utf-8')
    def record_step(k,old_np,result,started):
        states[0,k]=result;old_h[k]=old_np[h.h_ids];new_h[k]=result[h.h_ids]
        if args.mode!='FullGPU':
            row=dict(step_id=k,input_time_s=float(input_time[k]),activity_after_time_s=float(after_time[k]))
            for name,ids in groups.items():
                row.update({name+'_'+key:value for key,value in errors(result,reference[0,k],ids).items()})
                row[name+'_nonfinite']=int((~np.isfinite(result[ids])).sum())
            rows.append(row)
            per_node[:]=np.maximum(per_node,np.abs(result.astype(np.float64)-reference[0,k].astype(np.float64)))
        latency.append((time.monotonic()-started)*1000)
        if (k+1)%200==0:print('STEPS_COMPLETE',args.mode,k+1,flush=True)
    if args.mode=='FullGPU':
        for k in range(800):
            started=time.monotonic();old_np=old.cpu().numpy().copy()
            old=full.step(old,full.frame(k),step_id=k,run_id=identity['run_id'],condition_id='01_off_right',comparison_id=meta['comparison_id'])
            result=old.cpu().numpy().copy()
            status.write(json.dumps(dict(status='FULL_REFERENCE_ONLY',step_id=k,before_digest=array_hash(old_np),
                input_digest=array_hash(stimulus[0,k,0]),after_digest=array_hash(result)))+'\n')
            record_step(k,old_np,result,started)
        full.oracle.assert_weights_unchanged()
    else:
        with native_full_forbidden() as audit:
            for k in range(800):
                started=time.monotonic();old_np=c.state
                x=make_input(stimulus[0,k,0],inputs)
                transaction=c.prepare(k,x,'SOURCE_RAW')
                x_h[k]=transaction.h_request.x_h;boundary[k]=transaction.h_request.boundary
                chemical[k]=transaction.h_result.chemical
                result=c.commit(transaction)
                for event in c.logs[-2:]:status.write(json.dumps(dict(condition=0,**event))+'\n')
                record_step(k,old_np,result,started)
        assert h.step_count==c.next_step_id==adapter.calls==800 and audit['forbidden_native_call_count']==0
    status.close();states.flush()
    np.save(out/'H_before_after.npy',np.stack([old_h,new_h],axis=1))
    np.save(out/'activity_central.npy',np.ascontiguousarray(states[0,:,central].T))
    np.save(out/'activity_T4T5.npy',np.ascontiguousarray(states[0,:,t4t5].T))
    np.save(out/'final_full_state.npy',states[0,-1])
    if args.mode!='FullGPU':
        with (out/'step_errors.csv').open('w',newline='',encoding='utf-8') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        np.save(out/'per_node_max_abs.npy',per_node)
        np.save(out/'final_full_error.npy',states[0,-1].astype(np.float64)-reference[0,-1].astype(np.float64))
        np.savez_compressed(out/'SOURCE_RAW_step_io.npz',old_H=old_h,x_H=x_h,boundary_before=boundary,
            new_H_expected=new_h,chemical_expected=chemical,H_global_ids=h.h_ids,H_local_ids=np.arange(67,dtype=np.int64),
            incoming_source_global_ids=h.source_ids,step_id=np.arange(800,dtype=np.int64),input_time=input_time,
            activity_time=after_time,dt_s=np.float32(.005))
    assert unchanged(entries)
    assert all(file_hash(HERE/name)==digest for name,digest in code.items())
    assert file_hash(host_path(agreement['A_backend_path']))==agreement['A_backend_sha256']
    counts=None if args.mode=='FullGPU' else {name:sum(row[name+'_violations'] for row in rows) for name in groups}
    passed=args.mode=='FullGPU' or all(value==0 for value in counts.values())
    result=dict(status='PASS_ACTUAL_FULL_800' if args.mode=='FullGPU' else ('PASS_CLOSED_LOOP_NUMERICAL' if passed else 'FAIL_CLOSED_LOOP_NUMERICAL'),
        execution_evidence_level=identity['execution_evidence_level'],run_identity=identity,steps=800,
        warmup_steps_in_run=0,full_arrays_as_production_boundary=False,
        native_H_production_updates='Full_reference_only' if args.mode=='FullGPU' else 0,
        max_abs=None if args.mode=='FullGPU' else {name:max(row[name+'_max_abs'] for row in rows) for name in groups},
        violations=counts,nonfinite=0,
        final=None if args.mode=='FullGPU' else {name:errors(states[0,-1],reference[0,-1],ids) for name,ids in groups.items()},
        production_guard=audit,independent_H_steps=0 if args.mode=='FullGPU' else h.step_count,
        unified_committed_steps=0 if args.mode=='FullGPU' else c.next_step_id,
        wall_s=time.monotonic()-start,step_latency_ms={q:float(np.percentile(latency,p)) for q,p in [('p50',50),('p95',95),('p99',99),('max',100)]},
        timing_scope='per-step host/GPU exchange, validation and recorded comparisons; offline, not200Hz claim',
        peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),input_bundle_unchanged=True,
        stage_gate='numerical only; causal/fault/independent audit still required',FPGA_execution=False)
    dump(out/'result.json',result);seal(out)
    print('RUN_RESULT',json.dumps(dict(status=result['status'],mode=args.mode,wall_s=result['wall_s'],max_abs=result['max_abs'])),flush=True)


if __name__=='__main__':main()

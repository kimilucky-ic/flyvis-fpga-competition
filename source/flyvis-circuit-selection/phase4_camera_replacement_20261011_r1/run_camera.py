"""Actual live GPU-R plus independent SOURCE_RAW H for selected real-camera input."""
import argparse,csv,platform,shutil,time,uuid
from common import *

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--preflight-only',action='store_true');args=p.parse_args()
    agreement,model,h,inputs,stim,initial,t,a,entries=read_input();n=len(t)
    ref=host_path(agreement['Full_reference_path']);verify_reference(ref)
    reference=np.load(ref/'activities_full.npy',mmap_mode='r');assert reference.shape==(1,n,45669) and reference.dtype==np.float32
    if args.preflight_only:print('PASS_CAMERA609_STATIC_BINDING_NO_GPU');return
    ticket=require_camera_slot()
    out=HERE/'artifacts'/args.run
    if out.exists():raise SystemExit('Existing attempt preserved')
    out.mkdir(parents=True);torch=configure_gpu()
    from a_video_adapter import BoundRService
    from gpu_adapter import GPUAdapter
    from coordinator import Coordinator
    service=BoundRService();adapter=GPUAdapter(service,inputs)
    central=np.load(BUNDLE/'central_node_indices.npy');types=np.load(BUNDLE/'cell_types.npy')
    t4t5=central[np.isin(types,['T4'+s for s in 'abcd']+['T5'+s for s in 'abcd'])]
    groups=dict(H=h.h_ids,R=service.r_indices,full=np.arange(45669),central=central,T4T5=t4t5)
    code={p.relative_to(HERE).as_posix():file_hash(p) for p in [Path(__file__),HERE/'common.py',HERE/'a_video_adapter.py',
        *[HERE/'dependencies/b_core'/s for s in ['h_step.py','coordinator.py','gpu_adapter.py','run_closed_loop.py']],HERE/'dependencies/a_snapshot/r_only.py']}
    identity=dict(run_id=str(uuid.uuid4()),pid=os.getpid(),started_utc=datetime.now(timezone.utc).isoformat(),comparison_id=CID,condition_id=CONDITION,mode='PythonReplacement',layout='SOURCE_RAW',
        numeric_profile='ORIGINAL_FP32_GPU_NATIVE_R_NUMPY_FP32_H',steps=n,dt_s=.005,
        shared_identity=agreement['shared_identity'],backend_binding_id=agreement['shared_identity'],checkpoint_sha256=model['checkpoint_sha256'],source_commit=model['source_commit'],
        expanded_parameters_sha256=file_hash(BUNDLE/'expanded_parameters.npz'),initial_state_sha256=file_hash(BUNDLE/'initial_state_full.npy'),
        stimulus_sha256=file_hash(BUNDLE/'stimulus.npy'),time_sha256=file_hash(BUNDLE/'time.npy'),activity_time_sha256=file_hash(BUNDLE/'activity_time.npy'),
        candidate_sha256=service.candidate_sha256,node_map_sha256=file_hash(BUNDLE/'candidates/B_T5c/node_map.csv'),
        circuit_sha256=h.circuit_digest,code_sha256=code,Full_reference_identity=agreement['Full_run_identity'],
        numeric_profile_sha256=file_hash(BUNDLE/'numeric_profile.json'),metric_profile_sha256=file_hash(BUNDLE/'metric_profile.json'),
        execution_kind='actual_new_computation',execution_evidence_level='SOFTWARE_ACTUAL_CLOSED_LOOP',processing_mode='offline',
        python=platform.python_version(),torch=torch.__version__,numpy=np.__version__,gpu=torch.cuda.get_device_name(0),
        command=[sys.executable,*sys.argv],atol=1e-5,rtol=1e-5,FPGA_execution=False,
        no_extra_preframes=True,no_additional_warmup=True,activity_semantics='saved[k]=a[k+1], activity_time=input_time+.005')
    dump(out/'run_identity.json',identity)
    state=np.lib.format.open_memmap(out/'activities_full.npy',mode='w+',dtype=np.float32,shape=(1,n,45669))
    oldh=np.empty((n,67),np.float32);newh=np.empty_like(oldh);xh=np.empty_like(oldh);chemical=np.empty_like(oldh);raw=np.empty((n,len(h.source_ids)),np.float32)
    co=Coordinator(h,adapter,initial,identity['run_id'],CID,CONDITION);rows=[];latency=[];start=time.monotonic()
    torch.cuda.reset_peak_memory_stats()
    try:
        with (out/'step_status.jsonl').open('w',encoding='utf-8') as log,native_full_forbidden() as guard:
            for k in range(n):
                require_step_time(ticket);tic=time.monotonic();old=co.state
                prepared=co.prepare(k,make_input(stim[0,k,0],inputs),'SOURCE_RAW')
                oldh[k]=prepared.h_request.old_h;xh[k]=prepared.h_request.x_h;raw[k]=prepared.h_request.boundary;chemical[k]=prepared.h_result.chemical
                require_step_time(ticket);actual=co.commit(prepared);state[0,k]=actual;newh[k]=actual[h.h_ids]
                for event in co.logs[-2:]:log.write(json.dumps(event)+'\n')
                row=dict(step_id=k,input_time_s=float(t[k]),activity_after_time_s=float(a[k]))
                for group,ids in groups.items():row.update({group+'_'+key:value for key,value in errors(actual,reference[0,k],ids).items()})
                assert row['full_violations']==0 and np.isfinite(actual).all()
                rows.append(row);latency.append((time.monotonic()-tic)*1000)
                if (k+1)%200==0:print('CAMERA_STEPS',k+1,flush=True)
            assert h.step_count==adapter.calls==co.next_step_id==n and guard['forbidden_native_call_count']==0
    except BaseException as exc:
        np.save(out/'last_committed_full_state.npy',co.state)
        dump(out/'failure.json',dict(type=type(exc).__name__,message=str(exc),next_step_id=co.next_step_id,
            last_committed_digest=array_hash(co.state),pending_step=co.pending.tag.step_id if co.pending is not None else None,
            acceptance='FAILED_INCOMPLETE_ARRAYS_NOT_RESULTS',fallback_count=0))
        raise
    service.assert_weights_unchanged();state.flush()
    np.save(out/'activity_central.npy',np.ascontiguousarray(state[0,:,central].T));np.save(out/'activity_T4T5.npy',np.ascontiguousarray(state[0,:,t4t5].T))
    np.save(out/'final_full_state.npy',state[0,-1])
    for name in ['initial_state_full.npy','time.npy','activity_time.npy']:
        shutil.copyfile(BUNDLE/name,out/name);assert file_hash(BUNDLE/name)==file_hash(out/name)
    np.savez_compressed(out/'SOURCE_RAW_step_io.npz',old_H=oldh,x_H=xh,boundary_before=raw,chemical_expected=chemical,new_H_expected=newh,
        H_global_ids=h.h_ids,H_local_ids=np.arange(67),incoming_source_global_ids=h.source_ids,step_id=np.arange(n),input_time=t,activity_time=a,dt_s=np.float32(.005))
    with (out/'step_errors.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    assert all(file_hash(BUNDLE/e['path'])==e['sha256'] for e in entries)
    assert all(file_hash(HERE/p)==s for p,s in code.items())
    result=dict(status='PASS_CLOSED_LOOP_NUMERICAL',run_identity=identity,steps=n,independent_H_steps=h.step_count,unified_committed_steps=co.next_step_id,
        native_H_production_updates=0,full_arrays_as_production_boundary=False,production_guard=guard,
        original_R_parameter_tensor_digests_unchanged=True,input_bundle_unchanged=True,
        max_abs={g:max(row[g+'_max_abs'] for row in rows) for g in groups},violations={g:sum(row[g+'_violations'] for row in rows) for g in groups},
        final={g:errors(state[0,-1],reference[0,-1],ids) for g,ids in groups.items()},wall_s=time.monotonic()-start,
        GPU_peak_allocated_bytes=torch.cuda.max_memory_allocated(),step_latency_ms={q:float(np.percentile(latency,v)) for q,v in [('p50',50),('p95',95),('max',100)]},
        FPGA_execution=False,completed_utc=datetime.now(timezone.utc).isoformat(),evidence_level='ACTUAL_SOFTWARE_CLOSED_LOOP',stage_gate='numerical only; independent audit and causal/fault probes pending')
    dump(out/'result.json',result);seal(out);print('CAMERA_RESULT',json.dumps(dict(status=result['status'],steps=n,max_abs=result['max_abs'],wall_s=result['wall_s'])),flush=True)

if __name__=='__main__':main()

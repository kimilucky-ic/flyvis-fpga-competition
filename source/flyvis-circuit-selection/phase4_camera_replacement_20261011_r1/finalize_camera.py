"""Pure CPU repeat/readout/handoff audit. Does not initialize a CUDA context."""
import csv,shutil
from common import *

def main():
    out=HERE/'artifacts/final_camera_audit_r2'
    if out.exists():raise SystemExit('Existing final evidence preserved')
    out.mkdir(parents=True)
    agreement,model,h,inputs,stim,initial,t,a,entries=read_input()
    runs=[HERE/'artifacts'/name for name in ['python_camera_609_r2','python_camera_609_r3']]
    audit=[HERE/'artifacts'/name for name in ['audit_camera_609_r2','audit_camera_609_r3']]
    for p in runs+audit:manifest_verify(p)
    ids=[load(p/'run_identity.json') for p in runs]
    assert ids[0]['run_id']!=ids[1]['run_id']
    assert ids[0]['command'][-1]=='python_camera_609_r2' and ids[1]['command'][-1]=='python_camera_609_r3'
    assert datetime.fromisoformat(load(runs[0]/'result.json')['completed_utc']) < datetime.fromisoformat(ids[1]['started_utc'])
    process_evidence=load(HERE/'EXECUTION_PROCESS_RECORD.json')
    assert [q['tool_session_id'] for q in process_evidence['invocations']]==[3671,50823]
    assert ids[0]['code_sha256']==ids[1]['code_sha256']
    arrays=[np.load(p/'activities_full.npy',mmap_mode='r') for p in runs]
    repeat_rows=[]
    for k in range(609):
        assert np.array_equal(arrays[0][0,k],arrays[1][0,k]),k
        repeat_rows.append(dict(step_id=k,input_time_s=float(t[k]),activity_time_s=float(a[k]),max_abs=0.,bitwise_equal=True))
    with (out/'repeat_step_errors.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(repeat_rows[0]));w.writeheader();w.writerows(repeat_rows)
    audits=[load(p/'result.json') for p in audit]
    for report in audits:
        assert report['status']=='PASS_INDEPENDENT_CAMERA609_STATE_CHAIN_AND_VECTOR_AUDIT'
        assert report['prepared']==report['committed']==609 and report['all_camera_steps_H_recomputed_bitwise']
        assert report['native_H_production_updates']==0 and report['initial_state_exact']
    auxiliary=load(HERE/'artifacts/camera_live_feedback_r1/result.json')
    assert auxiliary['status']=='PASS_LIVE_FEEDBACK_AND_GPU_NEGATIVE_TESTS' and len(auxiliary['negative_tests'])==15
    assert all(q['status']=='PASS' for q in auxiliary['negative_tests'])
    with (BUNDLE/'nodes_full.csv').open(encoding='utf-8') as f:nodes=list(csv.DictReader(f))
    tt=np.array([int(r['global_node_index']) for r in nodes if r['cell_type'][:2] in ('T4','T5')],dtype=np.int64)
    ref=host_path(agreement['Full_reference_path']);verify_reference(ref);full=np.load(ref/'activities_full.npy',mmap_mode='r')
    all_tt_errors=[]
    for k in range(609):all_tt_errors.append(dict(step_id=k,**errors(arrays[0][0,k],full[0,k],tt)))
    assert sum(q['violations'] for q in all_tt_errors)==0
    with (out/'all_T4T5_step_errors.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(all_tt_errors[0]));w.writeheader();w.writerows(all_tt_errors)
    np.save(out/'all_T4T5_global_ids.npy',tt)
    np.save(out/'all_T4T5_Full.npy',np.ascontiguousarray(full[0,:,tt].T))
    np.save(out/'all_T4T5_Python.npy',np.ascontiguousarray(arrays[0][0,:,tt].T))
    source=host_path(load(HERE/'CAMERA_EXPERIMENT_SOURCE.json')['input_directory']).parents[1]/'handoff_selected_100_190/original_frame_alignment.csv'
    shutil.copyfile(source,out/'original_frame_alignment.csv')
    labels={str(i):nodes[i] for i in [auxiliary['feedback'][k] for k in ['H_source_global','R_intermediate_global','H_return_target_global']]}
    record=dict(status='PASS_REAL_CAMERA609_SOFTWARE_CLOSED_LOOP',comparison_id=CID,backend_binding_id=agreement['shared_identity'],
        evidence_level='ACTUAL_RECORDED_CAMERA_INPUT_ORIGINAL_FULL_GPU_AND_LIVE_GPU_R_PYTHON_H',
        input_scope='selected original frames100..190; 609 causal model steps, no800 padding',
        complete_network_nodes=45669,H_nodes=67,R_nodes=45602,dt_s=.005,steps_each=609,
        Full_reference=str(ref),Full_run_id=agreement['Full_run_identity']['run_id'],
        Python_runs=[dict(path=str(p),run_id=q['run_id'],pid=q['pid']) for p,q in zip(runs,ids)],
        repeated_Python_full_state_bitwise_equal=True,repeat_max_abs=0.,accepted_Python_commits=1218,
        distinct_process_evidence=process_evidence,PID_values_may_repeat_between_independent_WSL_invocations=True,
        all_step_H_vectors_recomputed_bitwise=True,native_H_production_updates=0,
        H_R_same_old_state_all_steps=True,recorded_R_used_in_production=False,
        error_summary=audits[0]['summary'],
        all_T4T5=dict(n_nodes=len(tt),max_abs=max(q['max_abs'] for q in all_tt_errors),violations=0),
        negative_tests=15,auxiliary_live_GPU_R_calls=auxiliary['actual_GPU_R_calls'],
        live_feedback=auxiliary['feedback'],feedback_node_labels=labels,
        original_frame_alignment_sha256=file_hash(source),
        initial_state_sha256=file_hash(BUNDLE/'initial_state_full.npy'),expanded_parameters_sha256=file_hash(BUNDLE/'expanded_parameters.npz'),
        stimulus_sha256=file_hash(BUNDLE/'stimulus.npy'),time_sha256=file_hash(BUNDLE/'time.npy'),activity_time_sha256=file_hash(BUNDLE/'activity_time.npy'),
        failed_attempt=dict(path=str(HERE/'artifacts/python_camera_609_r1'),status='FAILED_POSTPROCESSING_PRESERVED_NOT_ACCEPTED',actual_commits=609),
        limitations=['offline recorded input','selected3.04second clip not full4s playback or clean direction benchmark',
            'H/R perturbations are isolated causal diagnostics, not formal ablation or functional restoration',
            'noQ22/Q24 quantization, noPL orFPGA recovery','formal24condition campaign remainsNOT_RUN'],
        FPGA_execution=False,completed_utc=datetime.now(timezone.utc).isoformat())
    dump(out/'result.json',record);seal(out)
    handoff=dict(schema='B-camera609-handoff/v1',status=record['status'],comparison_id=CID,backend_binding_id=agreement['shared_identity'],
        Full_reference=str(ref),Python_reference=str(runs[0]),Python_independent_repeat=str(runs[1]),
        final_audit=str(out/'result.json'),step_errors=str(runs[0]/'step_errors.csv'),SOURCE_RAW_step_io=str(runs[0]/'SOURCE_RAW_step_io.npz'),
        initial_state=str(BUNDLE/'initial_state_full.npy'),expanded_parameters=str(BUNDLE/'expanded_parameters.npz'),
        input_node_indices=str(BUNDLE/'input_node_indices.npy'),node_map=str(BUNDLE/'candidates/B_T5c/node_map.csv'),
        time=str(BUNDLE/'time.npy'),activity_time=str(BUNDLE/'activity_time.npy'),
        activity_central=str(runs[0]/'activity_central.npy'),activity_central_shape=[609,65],
        activity_T4T5_centers=str(runs[0]/'activity_T4T5.npy'),activity_T4T5_centers_shape=[609,8],
        activities_full=str(runs[0]/'activities_full.npy'),activities_full_shape=[1,609,45669],
        profile='ORIGINAL_FP32_GPU_NATIVE_R_NUMPY_FP32_H',same_shared_profile_sha256=ids[0]['numeric_profile_sha256'],
        source_is_camera=True,live_camera_inference=False,processing_mode='offline',steps=609,dt_s=.005,
        FPGA_execution=False,formal24_started=False,
        hashes={key:record[key] for key in ['initial_state_sha256','expanded_parameters_sha256','stimulus_sha256','time_sha256','activity_time_sha256']})
    dump(HERE/'B_CAMERA_609_HANDOFF.json',handoff)
    print(json.dumps(dict(status=record['status'],repeat_max_abs=0.,all_T4T5=record['all_T4T5'],negative_tests=15)))

if __name__=='__main__':main()

"""Bind verified A Full/common bytes; never execute a model or rewrite A/E."""
import argparse,shutil
from common import *

DEFAULT_A=Path(r'C:\Users\hzy72\Documents\ChatGPT\fpga\flyvis-gpu-validation\phase4_camera_rectb_20261011')
def main():
    p=argparse.ArgumentParser();p.add_argument('--A-root',type=Path,default=DEFAULT_A);p.add_argument('--Full-run',default='full_gpu_609_r1');args=p.parse_args()
    if (HERE/'A_ACCEPTED_REFERENCE.json').exists():raise SystemExit('Existing accepted binding preserved')
    root=host_path(args.A_root);bundle=root/'common_bundle';reference=root/'artifacts'/args.Full_run
    verify_reference(bundle);ref_manifest=verify_reference(reference)
    binding=load(bundle/'camera_backend_identity.json');ri=load(reference/'run_identity.json');rr=load(reference/'result.json')
    assert binding['comparison_id']==ri['comparison_id']==CID
    assert binding['backend_binding_id']==ri['backend_binding_id']==rr['backend_binding_id']
    assert rr['status']=='PASS_FULL_GPU_609' and rr['steps']==609 and rr['Full_steps']==609
    assert ri['mode']=='FullGPU' and ri['condition_id']==CONDITION and ri['steps']==609 and ri['dt_s']==.005
    assert ri['execution_kind']=='actual_new_computation' and ri['no_extra_preframes'] and ri['no_new_warmup']
    assert rr['weight_state_exact_before'] and rr['weight_state_exact_after'] and rr['nonfinite_count']==0
    checks=[]
    for name in ['stimulus.npy','time.npy','activity_time.npy','expanded_parameters.npz','input_node_indices.npy','nodes_full.csv',
                 'static_boundary_gpu_native.npz','input_hex_coordinates.csv','central_node_indices.npy','cell_types.npy',
                 'candidates/B_T5c/candidate_manifest.json','candidates/B_T5c/node_map.csv','candidates/B_T5c/edge_partition_ids.npz']:
        assert file_hash(BUNDLE/name)==file_hash(bundle/name),name
        checks.append(dict(file=name,sha256=file_hash(bundle/name),B_source_matches=True))
    for name in ['initial_state_full.npy','identity_manifest.json','numeric_profile.json','metric_profile.json']:
        assert not (BUNDLE/name).exists(),name
        shutil.copyfile(bundle/name,BUNDLE/name);assert file_hash(bundle/name)==file_hash(BUNDLE/name)
    for key,name in [('stimulus_sha256','stimulus.npy'),('time_sha256','time.npy'),('activity_time_sha256','activity_time.npy'),
                     ('expanded_parameters_sha256','expanded_parameters.npz'),('initial_state_sha256','initial_state_full.npy'),
                     ('candidate_sha256','candidates/B_T5c/candidate_manifest.json'),('node_map_sha256','candidates/B_T5c/node_map.csv'),
                     ('numeric_profile_sha256','numeric_profile.json'),('metric_profile_sha256','metric_profile.json')]:
        assert binding[key]==ri[key]==file_hash(BUNDLE/name),key
    model=load(BUNDLE/'identity_manifest.json');h=HUpdater(STATIC);validate_parameters(h,BUNDLE/'expanded_parameters.npz')
    assert file_hash(BUNDLE/'initial_state_full.npy')==model['initial_state_sha256']
    assert np.load(BUNDLE/'initial_state_full.npy').dtype==np.float32
    assert np.load(reference/'activities_full.npy',mmap_mode='r').shape==(1,609,45669)
    receipt=dict(status='PASS_SAME_CAMERA_MODEL_STATE_INPUT_IDENTITY',comparison_id=CID,shared_identity=binding['backend_binding_id'],
        initial_state_sha256=binding['initial_state_sha256'],expanded_parameters_sha256=binding['expanded_parameters_sha256'],
        Full_reference_path=str(reference),Full_manifest_sha256=ref_manifest,Full_run_identity=ri,
        A_binding_path=str(bundle/'camera_backend_identity.json'),A_binding_sha256=file_hash(bundle/'camera_backend_identity.json'),
        same_bytes_checks=checks,actual_A_Full_steps=609,B_GPU_steps=0,FPGA_execution=False)
    dump(HERE/'A_ACCEPTED_REFERENCE.json',receipt);seal(BUNDLE)
    print(json.dumps(dict(status=receipt['status'],binding=receipt['shared_identity'],matching_files=len(checks),B_steps=0)))

if __name__=='__main__':main()

"""B acknowledges A's local handoff by exact semantic/file identities."""
from common import *


def main():
    a=HERE.parents[2]/'fly/gpu_phase3_fixed_video_20261010'
    ours=load(BUNDLE/'video_manifest.json')
    theirs=load(a/'bundle/video_manifest.json')
    mapping=dict(expanded_parameters_sha256='expanded',candidate_manifest_sha256='candidate',node_map_sha256='node_map',
        edge_partition_sha256='edge_partition',stimulus_sha256='stimulus',initial_state_sha256='initial',
        time_sha256='time',activity_time_sha256='activity_time')
    for key,field in mapping.items():assert theirs[key]==ours['identity_fingerprint'][field],key
    for field in ['condition_id','original_sample','steps','dt_s']:assert theirs[field]==ours[field],field
    model=load(BUNDLE/'identity_manifest.json')
    for key in ['model_id','checkpoint_sha256','source_commit']:assert theirs[key]==model[key],key
    for file in ['stimulus.npy','initial_state_full.npy','expanded_parameters.npz','time.npy','activity_time.npy',
        'input_node_indices.npy','central_node_indices.npy','cell_types.npy','candidates/B_T5c/node_map.csv','candidates/B_T5c/edge_partition_ids.npz']:
        assert file_hash(a/'bundle'/file)==file_hash(BUNDLE/file)
    accepted=[path for path in (a/'artifacts').glob('single_step_gpu_*/acceptance.json')
        if load(path).get('status')=='PASS_ACTUAL_GPU_SINGLE_STEP']
    single=max(accepted,key=lambda p:p.stat().st_mtime_ns) if accepted else a/'artifacts/single_step_gpu_r1/acceptance.json'
    dump(HERE/'A_B_IDENTITY_PROPOSAL_RECEIPT.json',dict(status='PASS_B_ACK_A_VIDEO_BYTE_IDENTITIES',
        B_selected_comparison_id=ours['comparison_id'],A_proposed_comparison_id=theirs['proposed_comparison_id'],
        B_actual_preflight=str(HERE/'artifacts/preflight_r1/result.json'),
        A_profile_and_input_files_match_exact=True,B_identity_fingerprint=ours['identity_fingerprint'],
        A_single_step_acceptance_path=str(single),
        requested_A_action='Bind B selected comparison_id override; acknowledge this local receipt. B800 waits for A actual single-step acceptance.'))
    if not single.exists():raise SystemExit('A actual single-step acceptance still pending;800-step execution blocked')
    step=load(single)
    assert step['status']=='PASS_ACTUAL_GPU_SINGLE_STEP' and step['Full_R_bitwise'] and step['original_weight_state_exact']
    for key in ['stimulus_sha256','initial_state_sha256','expanded_parameters_sha256']:assert step[key]==theirs[key]
    agreement=dict(schema='B_ACK_A_SINGLE_VIDEO_HANDOFF/v1',status='PASS_A_B_STRICT_IDENTITY_CONFIRMED_BY_B',
        condition_id='01_off_right',comparison_id=ours['comparison_id'],
        A_proposed_comparison_id=theirs['proposed_comparison_id'],
        comparison_rule='A callable explicitly accepts comparison_id override; use B SHA256 fingerprint including numeric/metric profiles for Full/Python/C/GUI',
        A_manifest_path=str(a/'bundle/video_manifest.json'),A_manifest_sha256=file_hash(a/'bundle/video_manifest.json'),
        A_single_step_path=str(single),A_single_step_sha256=file_hash(single),
        A_backend_path=str(a/'backend.py'),A_backend_sha256=file_hash(a/'backend.py'),
        B_bundle_path=str(BUNDLE),B_video_manifest_sha256=file_hash(BUNDLE/'video_manifest.json'),
        fingerprints=ours['identity_fingerprint'],B_confirmed=True,A_countersign_file_required_for_cross_line_adoption=True,
        A_existing_callables_exact=theirs['sourcecode_sha256'],
        strict_run_authority='Original A model/profile and video input identity exact; A actual single-step accepted; B explicitly binds same comparison to A API',
        numeric_scope='float32 reference only; hardware numeric/PSPL semantics pending')
    dump(HERE/'A_B_STRICT_IDENTITY_CONFIRMATION.json',agreement)
    handoff=load(HERE/'B_INPUT_IDENTITY_HANDOFF.json')
    handoff.update(status='PASS_B_VIDEO_INPUT_AND_A_PROFILE_CONFIRMED',preflight_result=str(HERE/'artifacts/preflight_r1/result.json'),
        strict_identity_ack_path=str(HERE/'A_B_STRICT_IDENTITY_CONFIRMATION.json'),
        A_adoption_request='Read B acknowledgement; bind comparison_id override above. No change to A bundle files required.')
    dump(HERE/'B_INPUT_IDENTITY_HANDOFF.json',handoff)
    print(agreement['status'],agreement['comparison_id'],flush=True)


if __name__=='__main__':main()

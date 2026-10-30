"""Read-only verify A's sealed actual800 reference and countersigned identity."""
import shutil
from common import *

A=HERE.parents[1].parent/'fly/gpu_phase3_fixed_video_20261010'
ref=A/'artifacts/full_gpu_800_r1'
meta,model,h,inputs,stimulus,initial,t,after,entries=read_input()
agreement=load(A/'comparison_agreement.json')
assert agreement['A_confirmed'] and agreement['B_confirmed']
assert agreement['comparison_id']==meta['comparison_id']
manifest=manifest_verify(ref)
identity=load(ref/'run_identity.json');result=load(ref/'result.json')
assert result['status']=='PASS_ACTUAL_FULL_800'
assert identity['mode']=='FullGPU' and identity['steps']==800 and identity['dt_s']==.005
for key,expected in dict(comparison_id=meta['comparison_id'],condition_id='01_off_right',
    checkpoint_sha256=model['checkpoint_sha256'],expanded_parameters_sha256=file_hash(BUNDLE/'expanded_parameters.npz'),
    stimulus_sha256=file_hash(BUNDLE/'stimulus.npy'),initial_state_sha256=file_hash(BUNDLE/'initial_state_full.npy'),
    numeric_profile_sha256=file_hash(BUNDLE/'numeric_profile.json'),metric_profile_sha256=file_hash(BUNDLE/'metric_profile.json'),
    time_sha256=file_hash(BUNDLE/'time.npy'),activity_time_sha256=file_hash(BUNDLE/'activity_time.npy'),
    candidate_sha256=file_hash(parameters_paths()[2]),node_map_sha256=file_hash(BUNDLE/'candidates/B_T5c/node_map.csv')).items():
    assert identity[key]==expected,(key,identity[key],expected)
trajectory=np.load(ref/'activities_full.npy',mmap_mode='r',allow_pickle=False)
assert trajectory.shape==(1,800,45669) and trajectory.dtype==np.float32 and np.isfinite(trajectory).all()
assert np.array_equal(trajectory[0,-1],np.load(ref/'final_full_state.npy').reshape(-1))
out=HERE/'dependencies/A_phase3_receipt';out.mkdir(exist_ok=True)
for path in [A/'comparison_agreement.json',A/'A_SINGLE_VIDEO_HANDOFF.json',ref/'run_identity.json',ref/'result.json',ref/'artifact_manifest.json']:
    name=path.name if path.parent==A else 'Full_'+path.name
    target=out/name
    if target.exists():assert file_hash(target)==file_hash(path),'existing receipt differs; use new namespace'
    else:shutil.copyfile(path,target)
receipt=dict(status='PASS_B_INDEPENDENT_A_800_FILE_IDENTITY_CHECK',comparison_id=meta['comparison_id'],
    A_confirmed=True,B_confirmed=True,A_reference_path=str(ref),A_reference_run_id=identity['run_id'],
    A_manifest_sha256=file_hash(ref/'artifact_manifest.json'),A_agreement_sha256=file_hash(A/'comparison_agreement.json'),
    trajectory_file_sha256=file_hash(ref/'activities_full.npy'),files_verified=len(manifest),
    evidence_level='READ_ONLY_IDENTITY_AND_ARRAY_CHECK_OF_A_ACTUAL_GPU_EXECUTION',
    A_actual_execution_status=result['status'],reference_as_production_R=False)
dump(HERE/'A_FULL_800_RECEIPT.json',receipt);seal(out);print(receipt)

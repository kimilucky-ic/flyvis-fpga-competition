"""Freeze exactly sample 1 of the existing video; never decode/render it again."""
from pathlib import Path
import hashlib, json, shutil, sys
import numpy as np

HERE=Path(__file__).resolve().parent
PREVIOUS=HERE.parent/'phase2_20261010'
FLY=HERE.parents[2]/'fly'
VIDEO=FLY/'camera_pipeline/controlled_video_20261010_r1'
A_BUNDLE=FLY/'gpu_phase2/artifacts/reference_bundle_gpu_native_v1'
sys.path.insert(0,str(PREVIOUS))
from h_step import file_hash, array_hash, HUpdater


def dump(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')


def seal(path):
    dump(path/'artifact_manifest.json',dict(files=[dict(path=p.relative_to(path).as_posix(),bytes=p.stat().st_size,
        sha256=file_hash(p)) for p in sorted(path.rglob('*')) if p.is_file() and p.name!='artifact_manifest.json']))


def main():
    bundle=HERE/'input_bundle'
    if bundle.exists():raise SystemExit('Existing input bundle preserved')
    parent_stim=VIDEO/'input/stimulus.npy'
    video_a0=VIDEO/'gpu_full_r1/initial_state_full.npy'
    assert file_hash(parent_stim)=='4a55fa37d3a4f1064270b258f314047f059af2880a9ed95689ed438793b654e6'
    assert file_hash(video_a0)=='4e09f6eb57dbc84b68294d486fa8684764b2081f1c942ca25ec57228fbd39c0e'
    matrix=np.load(parent_stim,allow_pickle=False)
    initial=np.load(video_a0,allow_pickle=False)
    assert matrix.shape==(6,800,1,721) and matrix.dtype==np.float32
    assert initial.shape in [(1,45669),(45669,)] and initial.dtype==np.float32 and np.isfinite(initial).all()
    time_axis=np.load(VIDEO/'input/time.npy',allow_pickle=False)
    assert np.array_equal(time_axis,np.arange(800)*.005)
    prior= json.loads((PREVIOUS/'artifacts/source_gpu_native_r1/run_identity.json').read_text())
    dependencies=HERE/'dependencies';dependencies.mkdir()
    core=dependencies/'b_core';core.mkdir()
    for name in ['h_step.py','coordinator.py','gpu_adapter.py','run_closed_loop.py']:
        assert file_hash(PREVIOUS/name)==prior['code_sha256'][name]
        shutil.copyfile(PREVIOUS/name,core/name)
    shutil.copyfile(PREVIOUS/'run_negative_tests.py',core/'run_negative_tests.py')
    a_copy=dependencies/'a_snapshot';a_copy.mkdir()
    for name,digest in prior['A_snapshot_sha256'].items():
        source=FLY/'gpu_phase2'/name
        assert file_hash(source)==file_hash(PREVIOUS/'dependencies/a_snapshot'/name)==digest
        shutil.copyfile(source,a_copy/name)
    # Parameterized accepted causal/fault harness; solver/transaction code remains unchanged.
    shutil.copyfile(PREVIOUS/'verify_live_feedback.py',HERE/'verify_live_feedback.py')
    snapshots=dependencies/'input_evidence';snapshots.mkdir()
    for source in [VIDEO/'gpu_full_r1/result.json',VIDEO/'acceptance.json',
            VIDEO/'input/metadata.json',VIDEO/'inputs/01_off_right/metadata.json',
            HERE.parents[1]/'docs/flyvis_visual_hybrid/PHASE3_FIXED_VIDEO_MVP_20261010.md']:
        shutil.copyfile(source,snapshots/(source.parent.name+'_'+source.name))
    bundle.mkdir()
    np.save(bundle/'stimulus.npy',np.ascontiguousarray(matrix[1:2]))
    assert file_hash(bundle/'stimulus.npy')==file_hash(VIDEO/'inputs/01_off_right/stimulus.npy')
    shutil.copyfile(video_a0,bundle/'initial_state_full.npy')
    shutil.copyfile(VIDEO/'input/time.npy',bundle/'time.npy')
    shutil.copyfile(VIDEO/'gpu_full_r1/activity_time.npy',bundle/'activity_time.npy')
    for name in ['expanded_parameters.npz','nodes_full.csv','input_node_indices.npy']:
        shutil.copyfile(A_BUNDLE/name,bundle/name)
    for name in ['central_node_indices.npy','cell_types.npy']:
        assert file_hash(A_BUNDLE/name)==file_hash(VIDEO/'gpu_full_r1'/name)
        shutil.copyfile(A_BUNDLE/name,bundle/name)
    candidate=bundle/'candidates/B_T5c';candidate.mkdir(parents=True)
    for name in ['candidate_manifest.json','node_map.csv','edge_partition_ids.npz']:
        shutil.copyfile(A_BUNDLE/'candidates/B_T5c'/name,candidate/name)
    shutil.copyfile(PREVIOUS/'artifacts/native_gpu_inputs/static_boundary_gpu_native.npz',bundle/'static_boundary_gpu_native.npz')
    shutil.copyfile(VIDEO/'input/input_hex_coordinates.csv',bundle/'input_hex_coordinates.csv')
    shutil.copyfile(VIDEO/'inputs/01_off_right/time_alignment.csv',bundle/'time_alignment.csv')
    model=json.loads((A_BUNDLE/'identity_manifest.json').read_text())
    needed=['model_id','source_commit','checkpoint_sha256','n_nodes','n_edges','dt_s','dynamic_state_keys',
        'dynamic_edge_state_keys','expanded_parameter_digests','expanded_parameters_sha256','nodes_full_sha256',
        'connectome_spec_sha256','dynamics_type','activation_type','parameter_expansion_device','parameter_expansion_torch','parameter_profile']
    identity={key:model[key] for key in needed}
    identity.update(schema='flyvis-video-common-identity/v1',initial_state_sha256=file_hash(bundle/'initial_state_full.npy'),
        initial_state_shape=list(initial.shape),initial_state_flat_digest=array_hash(initial.reshape(-1)),
        canonical_initial_state_device='cuda',initialization='use frozen animation a0; no additional warmup',
        initialization_source=str(video_a0),initialization_source_result_sha256=file_hash(VIDEO/'gpu_full_r1/result.json'))
    dump(bundle/'identity_manifest.json',identity)
    numeric=dict(schema='flyvis-B-video-fp32/v1',dt_s=.005,state='IEEE754 float32',
        H='NumPy SOURCE_RAW original HH/RH edge order, independent continuous Euler',
        R='A CUDA target-R HR/RR original edge order',parameter_profile='OFFICIAL_NATIVE_GPU_EXPANDED',
        hardware_numeric_profile=None,initial_shape_rule='same file bytes [1,N]; reshape view to [N] before step')
    metrics=dict(atol=1e-5,rtol=1e-5,criterion='abs(actual-Full)<=atol+rtol*abs(Full)',
        scope='all H/R/full/central65/centralT4T5 eight nodes, every800 steps, final full state',
        nonfinite_allowed=0,registered_before_execution=True,post_hoc_tolerance_relaxation=False)
    dump(bundle/'numeric_profile.json',numeric);dump(bundle/'metric_profile.json',metrics)
    fingerprint=dict(model=identity['checkpoint_sha256'],expanded=identity['expanded_parameters_sha256'],
        candidate=file_hash(candidate/'candidate_manifest.json'),node_map=file_hash(candidate/'node_map.csv'),
        edge_partition=file_hash(candidate/'edge_partition_ids.npz'),stimulus=file_hash(bundle/'stimulus.npy'),
        initial=file_hash(bundle/'initial_state_full.npy'),time=file_hash(bundle/'time.npy'),
        activity_time=file_hash(bundle/'activity_time.npy'),numeric=file_hash(bundle/'numeric_profile.json'),metrics=file_hash(bundle/'metric_profile.json'))
    comparison=hashlib.sha256(json.dumps(fingerprint,sort_keys=True).encode()).hexdigest()
    dump(bundle/'video_manifest.json',dict(schema='flyvis-single-video-frozen-input/v1',status='PASS_FROZEN_SINGLE_VIDEO_INPUT',
        condition_id='01_off_right',original_sample=1,steps=800,dt_s=.005,comparison_id=comparison,
        identity_fingerprint=fingerprint,source_mp4=str(VIDEO/'sources/01_off_right.mp4'),
        source_mp4_sha256=file_hash(VIDEO/'sources/01_off_right.mp4'),source_is_camera=False,
        parent_stimulus_path=str(parent_stim),parent_stimulus_sha256=file_hash(parent_stim),
        slice_rule='C-contiguous little-endian float32 parent[1:2,:,:,:]; exact preprocessed sample1 bytes',
        shape=[1,800,1,721],time_rule='input_time=k*.005; activity_time=input_time+.005; no G2 -1s shift',
        no_extra_preframes=True,no_additional_warmup=True,no_rerender=True,
        old_video_full_scope='only central65 per-step and complete final states; new all-node Full required',
        A_existing_callable='dependencies/a_snapshot/{full_oracle.py:FullNetworkOracle,r_only.py:RStepService}',
        A_new_phase3_handoff_seen=False,strict_match_preflight_required=True))
    h=HUpdater(bundle/'static_boundary_gpu_native.npz')
    assert len(h.h_ids)==67 and len(h.source_ids)==1364
    seal(bundle)
    dump(HERE/'dependencies/provenance.json',dict(B_core_reused_unchanged=prior['code_sha256'],
        A_callable_reused_unchanged=prior['A_snapshot_sha256'],source_phase2_manifest_sha256=file_hash(PREVIOUS/'artifact_manifest.json'),
        copied_fault_harness_sha256=file_hash(HERE/'verify_live_feedback.py')))
    print(json.dumps(dict(status='PASS_PREPARED_ANIMATION_INPUT',comparison_id=comparison,
        single_stimulus_sha256=fingerprint['stimulus'],video_a0_sha256=fingerprint['initial'])),flush=True)


if __name__=='__main__':main()

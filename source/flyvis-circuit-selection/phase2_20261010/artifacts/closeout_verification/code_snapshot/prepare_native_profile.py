"""Copy a verified A official GPU Full oracle and extract native H parameters.

The copied Full trajectory is comparison data only; live R never reads it.
All generated files belong to B. A inputs remain read-only.
"""
from pathlib import Path
import hashlib, json, shutil, uuid
import numpy as np
from h_step import HUpdater, file_hash
from run_closed_loop import manifest_verify, validate_parameters

HERE = Path(__file__).resolve().parent
A = HERE.parents[2] / 'fly/gpu_phase2'
BUNDLE = A / 'artifacts/reference_bundle_gpu_native_v1'
STATIC_CPU = HERE.parent / 'round1_20261010/artifacts/B_T5c/static_boundary.npz'
OUT = HERE / 'artifacts/native_gpu_inputs'
REFERENCE = HERE / 'artifacts/full_gpu_reference_a'


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def seal(directory):
    dump(directory / 'artifact_manifest.json', [dict(path=p.relative_to(directory).as_posix(),
        bytes=p.stat().st_size, sha256=file_hash(p)) for p in sorted(directory.rglob('*'))
        if p.is_file() and p.name != 'artifact_manifest.json'])


def main():
    if OUT.exists() or REFERENCE.exists():
        raise SystemExit('Existing preparation preserved; do not overwrite')
    entries = manifest_verify(BUNDLE)
    identity = json.loads((BUNDLE / 'identity_manifest.json').read_text())
    stim = json.loads((BUNDLE / 'stimulus_manifest.json').read_text())
    acceptance_path = A / 'artifacts/r_only_gpu_r2/acceptance.json'
    accepted = json.loads(acceptance_path.read_text())
    replay_path = A / 'artifacts/final_acceptance_v1/recorded_timeseries_acceptance.json'
    replay = json.loads(replay_path.read_text())
    source = A / 'artifacts/r_only_gpu_r2/full_activity.npy'
    proof = replay['files']['artifacts/r_only_gpu_r2/full_activity.npy']
    assert accepted['status'] == 'PASS_R_ONLY_SERVICE_SINGLE_STEP'
    assert accepted['device'] == 'cuda' and accepted['steps'] == 1940 and accepted['weight_state_exact_after']
    for key in ['checkpoint_sha256', 'expanded_parameters_sha256', 'initial_state_sha256']:
        assert accepted[key] == identity[key]
    assert accepted['stimulus_sha256'] == stim['stimulus_sha256']
    assert proof['independent_replay_stream_match']
    assert file_hash(source) == proof['npy_sha256'] == '1b8a684c18225100bd4b34e3ba61e8f55b3bf97a15eaecb4aca311932ab9ac80'
    oracle = np.load(source, mmap_mode='r', allow_pickle=False)
    assert oracle.shape == (4, 485, 45669) and oracle.dtype == np.float32
    with np.load(STATIC_CPU, allow_pickle=False) as old, np.load(BUNDLE / 'expanded_parameters.npz', allow_pickle=False) as params:
        data = {key: old[key].copy() for key in old.files}
        ids = data['global_node_id']
        data['bias'] = params['bias'][ids].copy()
        data['raw_initial_bias'] = data['bias'].copy()  # source-derived bias, NOT the warmup initial state
        data['time_const_s'] = params['time_const'][ids].copy()
        data['inv_max_tau_dt'] = np.ones(len(ids), dtype=np.float32) / np.maximum(data['time_const_s'], np.float32(.005))
        differences = {}
        for route in ['internal', 'incoming', 'outgoing']:
            edges = data[route + '_edge_id']
            assert np.array_equal(data[route + '_source_index'], params['source_global'][edges])
            assert np.array_equal(data[route + '_target_index'], params['target_global'][edges])
            for local, expanded in [('weight', 'effective_weight'), ('sign', 'sign'), ('syn_count', 'syn_count'), ('syn_strength', 'syn_strength')]:
                value = params[expanded][edges].copy()
                delta = np.abs(value.astype(np.float64) - data[route + '_' + local].astype(np.float64))
                differences[route + '_' + local] = dict(changed=int(np.count_nonzero(delta)), max_abs=float(delta.max()))
                data[route + '_' + local] = value
        assert [len(data[route + '_edge_id']) for route in ['internal', 'incoming', 'outgoing']] == [970, 5567, 8159]
    OUT.mkdir(parents=True)
    native_path = OUT / 'static_boundary_gpu_native.npz'
    np.savez_compressed(native_path, **data)
    updater = HUpdater(native_path)
    validate_parameters(updater, BUNDLE / 'expanded_parameters.npz')
    candidate_path = BUNDLE / 'candidates/B_T5c/candidate_manifest.json'
    assert accepted['candidate_sha256'] == file_hash(candidate_path)
    comparison = hashlib.sha256(json.dumps(dict(checkpoint=identity['checkpoint_sha256'],
        expanded=identity['expanded_parameters_sha256'], candidate=file_hash(candidate_path),
        initial=file_hash(BUNDLE / 'initial_state_full.npy'), stimulus=file_hash(BUNDLE / 'stimulus.npy'),
        time=file_hash(BUNDLE / 'time.npy'), metrics='atol=rtol=1e-5;all_H_R_full_central_T4T5'), sort_keys=True).encode()).hexdigest()
    dump(OUT / 'extraction.json', dict(status='PASS_NATIVE_GPU_H_PARAMETER_EXTRACTION',
        profile='OFFICIAL_NATIVE_GPU_EXPANDED', bundle=str(BUNDLE), manifest_entries_verified=len(entries),
        static_sha256=file_hash(native_path), input_static_cpu_sha256=file_hash(STATIC_CPU),
        identity=identity, differences_vs_CPU_expansion=differences,
        caveat='CPU/CUDA exp expansion differs in float32; never mix profiles. raw_initial_bias is NOT a0.',
        code_sha256=file_hash(Path(__file__))))
    seal(OUT)
    REFERENCE.mkdir()
    shutil.copyfile(source, REFERENCE / 'activities_full.npy')
    assert file_hash(REFERENCE / 'activities_full.npy') == proof['npy_sha256']
    for path in [acceptance_path, replay_path, A / 'artifacts/final_acceptance_v1/acceptance.json', A / 'handoff.json']:
        shutil.copyfile(path, REFERENCE / (path.parent.name + '_' + path.name))
    spec = dict(run_id=str(uuid.uuid4()), comparison_id=comparison, mode='Full', device='cuda',
        provenance='Verified copy of A official GPU Full; B did not rerun Full in this preparation',
        source_full_path=str(source), source_full_sha256=proof['npy_sha256'],
        source_full_stream_sha256=proof['raw_stream_sha256'], independent_A_replay_bitwise=True,
        checkpoint_sha256=identity['checkpoint_sha256'], source_commit=identity['source_commit'],
        expanded_parameters_sha256=identity['expanded_parameters_sha256'],
        initial_state_sha256=identity['initial_state_sha256'], stimulus_sha256=stim['stimulus_sha256'],
        time_axis_sha256=stim['time_sha256'], conditions_sha256=stim['conditions_sha256'],
        H_ids_hash=updater.h_order_digest, node_map_sha256=file_hash(BUNDLE / 'candidates/B_T5c/node_map.csv'),
        edge_partition_sha256=file_hash(BUNDLE / 'candidates/B_T5c/edge_partition_ids.npz'),
        candidate_sha256=file_hash(candidate_path), circuit_sha256=updater.circuit_digest,
        dt_s=.005, atol=1e-5, rtol=1e-5, python=accepted['python'], torch=accepted['torch'],
        A_original_command=accepted['command'], reference_use='post-step numerical comparison only; no production boundary')
    dump(REFERENCE / 'run_identity.json', spec)
    dump(REFERENCE / 'result.json', dict(status='PASS_ORIGINAL_GPU_FULL_REFERENCE_FROM_A',
        evidence_level='SOFTWARE_ORIGINAL_FULL_REFERENCE', run_identity=spec))
    seal(REFERENCE)
    print(json.dumps(dict(status='PASS_PREPARED_NATIVE_PROFILE', comparison_id=comparison,
        static_sha256=updater.circuit_digest, reference_sha256=proof['npy_sha256'], differences=differences)), flush=True)


if __name__ == '__main__':
    main()

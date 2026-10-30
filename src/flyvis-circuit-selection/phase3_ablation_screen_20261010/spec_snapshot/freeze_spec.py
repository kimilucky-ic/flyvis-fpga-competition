"""Freeze the architecture spec, structural visual readout and handoff identity.

No inference, no ablation outcome inspection, no writes outside this folder.
"""
from pathlib import Path
import hashlib, json, re
import numpy as np

P = Path(__file__).resolve().parent

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def dump(name, value):
    path = P / name
    if path.exists():
        raise RuntimeError('Preserve existing output: ' + str(path))
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

audit = json.loads((P / 'source_audit.json').read_text(encoding='utf-8'))
rois = audit['readout_sets'].copy()
d = np.load(rois['common_direct_downstream_R']['path'], allow_pickle=False)
t = np.load(rois['common_R_T4_T5']['path'], allow_pickle=False)
v = np.intersect1d(d, t).astype(np.int64)
path = P / 'common_direct_downstream_T4_T5_ids.npy'
assert not path.exists()
np.save(path, v, allow_pickle=False)
rois['primary_visual_readout'] = {'path': str(path), 'n': len(v), 'sha256': sha(path),
    'array_digest': hashlib.sha256(str(v.dtype).encode() + str(v.shape).encode() + v.tobytes()).hexdigest()}
assert len(v) == 1057
full_id = audit['Full_provenance']
full_path = next(x['path'] for x in audit['sources'] if x['path'].endswith('activities_full.npy'))
f = np.load(full_path, mmap_mode='r', allow_pickle=False)
x = np.asarray(f[:, :, v], dtype=np.float64)
z = x[:, 200:] - x[:, 160:200].mean(axis=1)[:, None, :]
eta = 1e-5 + 1e-5 * np.max(np.abs(x), axis=(0, 1))
floor = float(np.sqrt(np.mean((4 * eta) ** 2)))
checks = {}
for pol, c0, c180 in [('OFF', 0, 2), ('ON', 1, 3)]:
    u = z[c0] - z[c180]
    rms = float(np.sqrt(np.mean(u ** 2)))
    checks[pol] = {'Full_direction_trace_RMS': rms, 'tolerance_floor_RMS': floor,
                   'resolved_by_10x_floor_rule': rms > 10 * floor}
dump('readout_plan.json', {
    'schema': 'flyvis-ablation-readout-plan/v1', 'evidence_level': 'STRUCTURAL_ROI_AND_SAVED_FULL_ONLY',
    'ablation_results_inspected': False, 'ROIs': rois, 'primary_visual_readout_Full_only_check': checks,
    'candidate_center_membership': {c: x['T4_T5_centers_membership'] for c, x in audit['candidates'].items()},
    'Full_reference_path': full_path, 'Full_reference_sha256': full_id['source_full_sha256'],
})
doc = P / 'ABLATION_SPEC_v1.md'
text = doc.read_text(encoding='utf-8')
known_hashes = {x['sha256_before'] for x in audit['sources']}
known_hashes.update(v for v in full_id.values() if isinstance(v, str) and len(v) == 64)
known_hashes.update(v for v in audit['model_identity'].values() if isinstance(v, str) and len(v) == 64)
for val in re.findall(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])', text):
    assert val in known_hashes, 'Document SHA does not match audited source: ' + val
for heading in ['## 1.', '## 2.', '## 3.', '## 4.', '## 5.', '## 6.', '## 7.', '## 8.', '## 9.', '## 10.']:
    assert heading in text
config = {
    'schema': 'flyvis-ablation-spec/v1', 'spec_version': 1, 'date': '2026-10-10', 'timezone': 'Asia/Shanghai',
    'status': 'SPEC_ISSUED_FOR_EXECUTION', 'experiment_status': 'NOT_EXECUTED_BY_ARCHITECT',
    'spec_document': {'path': str(doc), 'sha256': sha(doc)},
    'user_confirmed_scheme': 'A', 'hardware_mainline': {'candidate_id': 'B_T5c', 'n_H': 67, 'profile': 'SOURCE_RAW', 'unchanged': True, 'final_hardware_freeze': False},
    'operator': 'BLOCK_HR_RELEASE', 'gain_application': 'original_edge_current_before_scatter_add',
    'H_state_updates_enabled': True, 'HH_RH_RR_unchanged': True,
    'model': {k: audit['model_identity'][k] for k in ['model_id', 'source_commit', 'checkpoint_sha256',
        'expanded_parameters_sha256', 'initial_state_sha256', 'nodes_full_sha256', 'dt_s', 'n_nodes', 'n_edges',
        'dynamics_type', 'activation_type', 'canonical_initial_state_device', 'parameter_profile']},
    'fixture': {'stimulus_sha256': full_id['stimulus_sha256'], 'time_sha256': full_id['time_axis_sha256'],
        'conditions_sha256': full_id['conditions_sha256'], 'shape': [4, 485, 1, 721], 'conditions': audit['conditions'],
        'reset_each_condition': True, 'additional_warmup': False, 'saved_activity': 'activity_after[k]=a[k+1]',
        'saved_official_time': 't_label[k]=k*0.005-1; unchanged input-grid pairing',
        'state_before_time': 't_label[k]', 'state_after_time': 't_label[k]+0.005'},
    'windows_zero_based_inclusive': audit['time_windows_zero_based_inclusive'],
    'modes': {
        'Full': {'backend': 'original_official_GPU', 'release_gain': '1 for every original edge/step',
                 'reuse_verified_Full_allowed': True, 'source_reference': full_id},
        'Sham': {'backend': 'independent_H_plus_controlled_R', 'release_gain': '1 including masked HR and all steps', 'new_execution_required': True},
        'Ablation': {'backend': 'independent_H_plus_controlled_R', 'release_gain': '0 iff original_edge_id in E_HR and step_id>=200; else 1', 'new_execution_required': True},
    },
    'candidates': audit['candidates'], 'readouts': rois,
    'primary_metric': {'populations': ['primary_visual_readout', 'common_direct_downstream_R'],
        'polarity_pairs': {'OFF': [0, 2], 'ON': [1, 3]}, 'baseline': 'mean(activity_after[c,160:200,r])',
        'direction_trace': 'v_m=(a_m[0deg]-baseline_m[0deg])-(a_m[180deg]-baseline_m[180deg]); k=200..484',
        'Full_direction_axis': 'u=v_Full, no outcome-based neuron selection',
        'retention_S': 'dot(v_m,u)/dot(u,u)', 'relative_direction_change_E': 'norm(v_m-u)/norm(u)',
        'eta_r': '1e-5+1e-5*max_abs_Full_r_across_all_conditions_and_steps',
        'direction_floor': 'RMS_r(4*eta_r)', 'resolved': 'RMS(u)>10*direction_floor',
        'unresolved_ratios': None, 'official_12_direction_DSI_in_four_conditions': False},
    'software_validity': {'pointwise_atol': 1e-5, 'pointwise_rtol': 1e-5, 'finite_required': True,
        'independent_processes': 2, 'condition_runs_per_process': 24, 'total_Shams_and_Ablations_steps': 23280,
        'success_status': 'PASS_SOFTWARE_ABLATION_IMPLEMENTATION', 'functional_loss_required_for_validity': False,
        'pre_intervention_steps': [0, 199], 'first_H_step_not_directly_intervened': 200,
        'edge_audit_steps': [199, 200, 201, 484]},
    'extension_24_conditions': {
        'effect_threshold': {'abs_1_minus_S_or_E': 0.20, 'numerical_margin': 10,
            'change_resolved': 'RMS(A-S)>10*max(RMS(S-F),RMS(eta)); same qualifying polarity in independent process',
            'metric_repeat_abs_difference_max': 0.01},
        'coverage_rule': 'historical accepted target-center DSI>=0.05 and PD distance to nearest 0/180 axis>45deg, OR unresolved first-round primary V baseline',
        'all_candidate_results_required_before_selection': True, 'execution_list_requires_user_confirmation': True,
        'recommended_first_batch_max_candidates': 2, 'tie_priority': 'B_T5c existing hardware',
        'no_detected_effect_does_not_prove_no_contribution': True,
        'matching_full_init_and_params_required': True},
    'state_commit': 'all H/R candidates read same a[k]; host alone atomically commits; explicit old_H stateless candidate STEP',
    'request_required_fields': ['campaign_id', 'comparison_id', 'run_id', 'condition_id', 'step_id', 'old_state_step_id',
        'candidate_id', 'candidate_manifest_sha256', 'HR_edge_ids_sha256', 'spec_sha256', 'operator', 'mode',
        'activation_step_id', 'HR_release_gain', 'parameter_profile_sha256', 'stimulus_sha256', 'initial_state_sha256',
        'old_full', 'hex_frame', 'dt_s', 'device'],
    'candidate_response_required_fields': ['run_id', 'condition_id', 'step_id', 'candidate_manifest_sha256', 'spec_sha256',
        'operator', 'mode', 'HR_release_gain', 'global_node_indices', 'activity', 'status=CANDIDATE_NOT_COMMITTED'],
    'run_identity_rule': 'campaign_id hashes spec/fixture/param/a0/readout; per-candidate comparison_id adds H/HR identity; actual run_id unique per execution; preserved Full source run_id plus reference_binding',
    'new_ablation_run_ids': None, 'FPGA_execution_status': 'NOT_PART_OF_THIS_SOFTWARE_SCREEN',
    'estimate': {'implementation_and_acceptance_work_days': [1, 2], 'extension_work_days_per_candidate': 1,
        'disk_reservation_GB': [6, 8], 'GPU_batch_runtime': None, 'timing_status': 'ESTIMATE_NOT_MEASURED_NEW_BATCH'},
}
dump('spec_config.json', config)
manifest = {'schema': 'flyvis-architect-ablation-spec-manifest/v1',
    'status': 'SPEC_AND_READONLY_AUDIT_ONLY', 'new_ablation_experiment_pass': False,
    'files': [{'path': x.name, 'bytes': x.stat().st_size, 'sha256': sha(x)} for x in sorted(P.iterdir()) if x.is_file() and x.name != 'manifest.json']}
dump('manifest.json', manifest)
print(json.dumps({'status': 'PASS_SPEC_CONSISTENCY_AND_MANIFEST_CREATION', 'files': len(manifest['files']),
    'spec_sha256': sha(doc), 'manifest_sha256': sha(P / 'manifest.json'),
    'primary_V_n': len(v), 'Full_only_check': checks, 'new_ablation_executed': False}, ensure_ascii=False, indent=2))

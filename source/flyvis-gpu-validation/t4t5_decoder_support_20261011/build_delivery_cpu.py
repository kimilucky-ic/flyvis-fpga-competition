"""Freeze interface metadata from actual CPU audit and accepted receipts only."""
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
import numpy as np
from service import HERE, canonical, load_json, sha

REPO = HERE.parents[1]
FLY = REPO.parent / 'fly'
B = REPO / 'flyvis-circuit-selection/t4t5_criticality_20261011'
CAMERA = REPO / 'flyvis-gpu-validation/phase4_camera_rectb_20261011'
G2 = FLY / 'gpu_phase2/artifacts'


def windows(path):
    s = str(path)
    if s.startswith('/mnt/c/'):
        return 'C:/' + s[7:]
    return s.replace('\\', '/')


def pin(path):
    return dict(path=windows(path), sha256=sha(path))


def dump(name, value):
    path = HERE / name
    if path.exists():
        raise ValueError('EXISTING_DELIVERY_PRESERVED: ' + name)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


def main():
    audit = load_json(HERE / 'cpu_audit_r1/result.json')
    assert audit['status'] == 'PASS_CPU_DECODER_CHECKPOINT_TYPE_AUDIT'
    prereg = load_json(B / 'PREREGISTRATION_v1.json')
    inputs = load_json(B / 'INPUT_IDENTITY.json')
    original = REPO / 'flyvis-circuit-selection/phase4_direction_extension_20261010/pre_run_20261011_r1/input_bundle'
    # Verify fixed shared identity and four frozen arrays once; no rendering.
    for name, key in [('initial_state_full.npy', 'initial_state_sha256'),
                      ('expanded_parameters.npz', 'expanded_parameters_sha256'),
                      ('nodes_full.csv', 'nodes_full_sha256')]:
        expected = inputs['model'].get(key, 'c2c367f77083c791c4329d5d3557c0a923ed731d7b47cee35061c49d5b9d79fa')
        assert sha(original / name) == expected
    original_stim = np.load(original / 'stimulus.npy', mmap_mode='r', allow_pickle=False)
    selected = []
    for c in inputs['conditions']:
        path = B / 'cpu_preparation_r1' / c['filename']
        a = np.load(path, mmap_mode='r', allow_pickle=False)
        assert a.dtype == np.float32 and a.shape == (1, 485, 1, 721)
        assert np.array_equal(a[0], original_stim[c['original_sample']])
        assert sha(path) == c['stimulus_sha256']
        selected.append(dict(c, path=windows(path), Full_cache_status='MISS_FOR_THIS_CONDITION'))
    full_ids = np.load(HERE / 'cpu_audit_r1/decoder_input_global_ids.npy')
    coords = np.load(HERE / 'cpu_audit_r1/hex_coordinates_uv.npy')
    rows = list(csv.DictReader((original / 'nodes_full.csv').open()))
    assert len(rows) == 45669
    for ch, ct in enumerate(c['cell_type'] for c in audit['channels']):
        assert all(rows[g]['cell_type'] == ct and int(rows[g]['u']) == coords[j, 0] and int(rows[g]['v']) == coords[j, 1]
                   for j, g in enumerate(full_ids[ch]))
    assert np.array_equal(coords, np.load(B / 'cpu_preparation_r1/hex_coordinates.npy'))
    source_files = audit['source_files']
    objective = FLY / 'upstream/flyvis/flyvis/task/objectives.py'
    source_files['task/objectives.py'] = pin(objective)
    type_audit = dict(schema='flyvis-decoder-type-audit/v1', status=audit['status'],
                      evidence_level='ACTUAL_CPU_CHECKPOINT_AND_ORIGINAL_GATHER_NO_FORWARD',
                      checkpoint_sha256=audit['checkpoint_sha256'], channels=audit['channels'],
                      total_input_types=34, total_input_nodes=24514, full_network_nodes=45669,
                      T4_nodes=2884, T5_nodes=2884, T4T5_nodes=5768,
                      full_T4T5_global_index_range=[24039, 29806],
                      input_relu=True, direct_T4T5_channels=list(range(4, 12)),
                      all_eight_types_have_nonzero_first_layer_weights=True,
                      causal_strength_not_inferred_from_weight_magnitude=True,
                      global_mapping=pin(HERE / 'cpu_audit_r1/decoder_input_global_ids.npy'),
                      t4t5_mapping=pin(HERE / 'cpu_audit_r1/t4t5_global_ids.npy'),
                      coordinates=pin(HERE / 'cpu_audit_r1/hex_coordinates_uv.npy'),
                      mapping_CSV=pin(HERE / 'cpu_audit_r1/decoder_input_nodes.csv'),
                      B_type_map_equal=True, B_full_node_table_equal=True,
                      type_counts_all65=audit['node_type_counts'], audit_receipt=pin(HERE / 'cpu_audit_r1/result.json'))
    dump('TYPE_INPUT_AUDIT.json', type_audit)
    contract = dict(schema='flyvis-full-decoder-contract/v1', status='CPU_AUDITED_GPU_CHUNK_EXECUTION_NOT_RUN',
                    owner='A_official_Full_decoder_support', model=inputs['model'],
                    shared_complete_state=pin(original / 'initial_state_full.npy'),
                    expanded_parameters=pin(original / 'expanded_parameters.npz'),
                    all_nodes=pin(original / 'nodes_full.csv'), input_node_map=pin(original / 'input_node_indices.npy'),
                    time=pin(original / 'time.npy'), frozen_conditions=selected,
                    input_shape=['B', 'T', 45669], input_dtype='float32',
                    input_semantics='complete signed continuous nodes.activity in original global order; decoder applies ReLU internally',
                    output_shape=['B', 'T', 2, 721], output_dtype='float32',
                    output_time_semantics='flow[k] decodes result[k]=a[k+1]; activity_time[k]=input_time[k]+dt; no temporal operation in decoder',
                    ordered_input_types=[c['cell_type'] for c in audit['channels']],
                    input_global_ids_canonical_sha256=canonical(full_ids.tolist()),
                    input_mapping=type_audit['global_mapping'], coordinates=type_audit['coordinates'],
                    square_storage_shape=audit['square_storage_shape'], spatial_axes='axial u/v storage, NOT optical-flow x/y components',
                    component_convention=['x_right_positive', 'y_up_positive'],
                    angle_projection='[cos(theta_deg*pi/180),sin(theta_deg*pi/180)] in x-right/y-up image plane',
                    angle_source_status='derived from increasing horizontal offset then positive PIL rotation; small CPU source-render test in TEST_RESULTS.json',
                    units=dict(raw='official_Sintel_box_sum_normalized_displacement_target_units',
                               source_formula='Sintel .flo pixels/frame-pair divided by ORIGINAL image height; y sign inverted; BoxEye sum over13x13',
                               training_box_kernel=13, training_box_area=169,
                               optional_display_formula='raw/169 gives nominal box-area-mean normalized frame-pair displacement; label derived, retain raw',
                               physical_velocity_calibrated=False, model_step_displacement=False,
                               never_divide_raw_by_model_dt=True,
                               training_dataset_dt_s=audit['task_config']['dataset']['dt'],
                               inference_dt_s=0.005, resampling='target interpolated/repeated, not scaled by inference dt'),
                    learned_normalizer='two raw head channels divided by softplus(third head channel)+1 inside original forward; no extra per-mode normalization',
                    training_loss=audit['task_config']['loss'],
                    official_losses=dict(l2norm='mean_B(sqrt(sum_T,C,H((estimate-target)^2)))',
                                         epe='mean_B,T,H(sqrt(sum_C((estimate-target)^2)))',
                                         synthetic_target_available=False,
                                         Full_comparison_label='model endpoint DIFFERENCE, not ground-truth EPE'),
                    decoder_config=audit['decoder_config'], decoder_state_sha256=audit['decoder_state_sha256'],
                    decoder_state_digest_algorithm=audit['decoder_state_digest_algorithm'],
                    module_training_flags=audit['module_training_flags'], recursive_eval_required=True,
                    checkpoint_tensors_buffers_immutable=True, original_hex_weight_projection_retained=True,
                    default_decode_batch_samples=1, max_chunk_frames=32,
                    chunk_profile='SERIAL_B1_T32_ORIGINAL_EVAL_FP32; numerical equivalence to old bulk decode NOT_TESTED_YET',
                    source_files=source_files,
                    interventions=dict(release_block='all selected source outgoing edges HH+HR before scatter; activity may persist and remain directly visible to decoder',
                                       decoder_only_mask='zero selected type inputs only in private decoder activity copy from k200; no network dynamics change',
                                       activity_clamp='B-owned old-state/commit clamp changes network feedback AND decoder activity; separate control'),
                    no_new_neural_steps=True, no_new_GPU_calls=True, scheduler_owner='8_AutoRunner')
    dump('FULL_DECODER_CONTRACT.json', contract)
    readout = dict(schema='flyvis-flow-readout/v1', decoder_contract=pin(HERE / 'FULL_DECODER_CONTRACT.json'),
                   B_preregistration=pin(B / 'PREREGISTRATION_v1.json'), preregistration_id=prereg['preregistration_id'],
                   B_metric_source=pin(B / 'metrics.py'), fixed_ROI=pin(B / 'cpu_preparation_r1/flow_ROI_hex_indices.npy'),
                   fixed_ROI_hexals=331, fixed_ROI_radius=10, windows=prereg['windows'],
                   shared_baseline='same-condition Sham mean overk160..199 subtracted from BOTH Sham and mode',
                   primary_definition=prereg['primary_metric'], thresholds_owner='B unchanged preregistration v1',
                   thresholds=prereg['thresholds'], weak_reference='ineligible -> ratios/angle null, no impairment verdict',
                   Full_vs_Sham_required_first=prereg['sham_numerical_tolerance'],
                   stimulus_projection_direction='source verified cos/sin; no neuron preferred-direction assumption',
                   outputs=['Q', 'aligned_drop', 'magnitude_ratio', 'field_error_E', 'angle_deg',
                            'mean_stimulus_projection_sham', 'mean_stimulus_projection_mode'],
                   signed_Q_is_not_remaining_visual_function_percentage=True, raw_units_unchanged=True)
    dump('READOUT_CONTRACT.json', readout)
    binding = load_json(CAMERA / 'common_bundle/camera_backend_identity.json')
    camera_root = CAMERA / 'artifacts/full_gpu_609_r1'
    camera_handoff = load_json(CAMERA / 'CAMERA_BACKEND_HANDOFF.json')
    fields = ['stimulus_sha256', 'time_sha256', 'activity_time_sha256', 'initial_state_sha256',
              'expanded_parameters_sha256', 'checkpoint_sha256', 'source_commit', 'numeric_profile_sha256',
              'candidate_sha256', 'node_map_sha256', 'nodes_full_sha256', 'dt_s', 'steps']
    camera_id = {k: binding[k] for k in fields}
    camera_id.update(backend='FullGPU', ablation={'definition': 'NONE', 'start_step': None},
                     original_samples=['selected_100_190'], full_source_sha256=sha(FLY / 'gpu_phase2/full_oracle.py'))
    g2_accept = load_json(G2 / 'r_only_gpu_r2/acceptance.json')
    g2_id = {k: g2_accept[k] for k in ['stimulus_sha256', 'initial_state_sha256', 'expanded_parameters_sha256',
                                     'checkpoint_sha256', 'source_commit', 'dt_s']}
    g2_id.update(time_sha256=sha(G2 / 'reference_bundle_gpu_native_v1/time.npy'), steps=485,
                 original_samples=[0, 1, 12, 13], nodes_full_sha256=binding['nodes_full_sha256'],
                 backend='FullGPU', numeric_profile='OFFICIAL_NATIVE_GPU_EXPANDED_TORCH2.7.1_FP32',
                 candidate_sha256=g2_accept['candidate_sha256'],
                 full_source_sha256=g2_accept['implementation_sha256']['full_oracle.py'],
                 ablation={'definition': 'NONE', 'start_step': None})
    old_decoder = REPO / 'flyvis-visual-experiments/artifacts/decoder_cuda_r3'
    flow_result = load_json(old_decoder / 'result.json')
    assert flow_result['status'] == 'PASS'
    flow_id = dict(source_commit=audit['source_commit'], checkpoint_sha256=audit['checkpoint_sha256'],
                   original_samples=[0, 1, 12, 13], decoder_state_sha256=audit['decoder_state_sha256'],
                   input_activity_identity='not exported all nodes in historical decoder run',
                   initial_state_sha256=None, backend='OfficialDecoderGAVP_GPU_eval',
                   ablation={'definition': 'NONE', 'start_step': None},
                   strict_G2_baseline_eligible=False)
    refs = {}
    for name, path, identity, shape, receipt, source_run, limits in [
        ('camera609_Full', camera_root / 'activities_full.npy', camera_id, [1, 609, 45669],
         CAMERA / 'INDEPENDENT_REPLAY_ACCEPTANCE.json', camera_handoff['full_gpu_reference_run_id'],
         ['exact frozen camera609 only; distinct GPU-adapted a0; no cached decoder output']),
        ('G2_edge0_180_Full', G2 / 'r_only_gpu_r2/full_activity.npy', g2_id, [4, 485, 45669],
         G2 / 'r_only_gpu_r2/acceptance.json', 'historical:r_only_gpu_r2_original_Full',
         ['original Full traces recorded during R-only single-step verification; NOT replacement traces',
          'only original samples0/1/12/13; no60/90/240/270; H annotation67, rebinding5768 requires separate derived identity']),
        ('edge0_180_decoder_preview', old_decoder / 'flow.npy', flow_id, [4, 485, 2, 721],
         old_decoder / 'result.json', 'historical:decoder_cuda_r3',
         ['accepted original eval preview; no saved complete a0/all-node-input identity; not exact shared-G2 reference',
          'only0/180; camera decoder NOT_RUN; no new four-condition predictions'])]:
        array = np.load(path, mmap_mode='r', allow_pickle=False)
        assert list(array.shape) == shape and array.dtype == np.float32
        refs[name] = dict(status='ACCEPTED_HISTORICAL_RESULT', array_path=windows(path), identity=identity,
                          identity_sha256=canonical(identity), shape=shape, dtype='float32', source_run_id=source_run,
                          pins=[pin(path), pin(receipt)], limits=limits)
    assert refs['camera609_Full']['pins'][0]['sha256'] == camera_handoff['full_gpu_reference_sha256']
    assert refs['G2_edge0_180_Full']['pins'][0]['sha256'] == '1b8a684c18225100bd4b34e3ba61e8f55b3bf97a15eaecb4aca311932ab9ac80'
    dump('REFERENCE_REGISTRY.json', dict(schema='flyvis-accepted-reference-registry/v1', references=refs,
                                        requested_four_condition_Full='CACHE_MISS', auto_compute_on_miss=False,
                                        fresh_process_formal_satisfied_by_cache=False))
    old_measurements = dict(source_receipt=pin(old_decoder / 'result.json'),
                            original_Full_1940_step_calls_s=g2_accept['timed_full_s'],
                            original_Full_1940_peak_allocated_MiB=g2_accept['peak_cuda_allocated_bytes'] / 2**20,
                            decoder_historical_stats={k: flow_result[k] for k in ('model_load', 'inference', 'decode')},
                            limits='old bulk decoder cumulative reservation nearly8GiB; B1x32 memory/time not yet measured')
    dump('RESOURCE_BUDGET.json', dict(schema='flyvis-decoder-resource-budget/v1', status='PLANNING_ESTIMATE_NOT_NEW_GPU_MEASUREMENT',
         preregistration_id=prereg['preregistration_id'], conditions=4, steps_per_condition=485,
         original_samples=[5, 17, 6, 18], neural_modes=6, decoder_modes=7, planned_neural_steps=11640,
         planned_decoded_frames=13580, full_state_bytes_per_neural_mode=4*485*45669*4,
         all_six_full_state_raw_bytes=6*4*485*45669*4, flow_bytes_per_decoder_mode=4*485*2*721*4,
         all_seven_flow_raw_bytes=7*4*485*2*721*4, input_chunk_B1_T32_raw_bytes=32*45669*4,
         decoder_square_input_chunk_raw_bytes=32*34*31*31*4, batch_samples=1, chunk_frames=32,
         storage_budget_GiB=4, start_free_storage_min_GiB=8,
         GPU_VRAM_estimate_MiB=[500, 1500], new_GPU_memory_measurement=None,
         compute_estimate_s=[60, 180], time_estimate_status='B planning only; intervention hooks and chunks unbenchmarked',
         historical_evidence=old_measurements, runner_owner='8_AutoRunner', no_model_reloading_between_modes_requested=True,
         actual_neural_steps_this_delivery=0, actual_GPU_calls_this_delivery=0, board_operations=0,
         B_requested_window='2026-10-11 18:05-18:20 Asia/Shanghai', window_user_authorized=False,
         A_resource_statement='A has no new GPU job in this task; future slot needs8/6 exclusion and user scope; no exclusive reservation issued',
         CUDA_execution_permitted_by_this_document=False))
    runner = REPO / 'flyvis-autorunner'
    config = load_json(runner / 'configs/camera609.fast.json')
    runner_cache = runner / 'cache/FullGPU/8f66d510404b65e956f5c03d598b24de70ec7ecab7dda8914b9722039acea4e0.json'
    dump('AUTORUNNER_ADAPTER.json', dict(schema='flyvis-autorunner-decoder-adapter/v1',
          supported_read_only_now=dict(schema=config['schema'], camera_Full_cache=pin(runner_cache),
                                      original_Full_core=pin(FLY / 'gpu_phase2/full_oracle.py')),
          scheduler_owner='8_AutoRunner', schedules_queues_retries_locks_in_A=False,
          adapter_module=pin(HERE / 'service.py'), readout_module=pin(HERE / 'flow_readout.py'),
          methods=dict(cache='AcceptedReferenceCache.open(reference_id, identity, fresh_process=False)',
                       decoder_load='OfficialDecoderService(model_path, contract_path, device, check_scope)',
                       decode='decode(activity, chunk_frames=32, mask_types=(), mask_start_step=200)',
                       assert_state='assert_weights_unchanged()'),
          caller_requirements=['import adapter without Torch/CUDA; AST check methods first',
                               '8 obtains existing exclusive GPU lease and valid per-study scope, initializes deterministic FP32 default CUDA0',
                               'bind input/a0/params/source/node map/ablation and decoder contract/state/chunk profile before execution',
                               'check_scope(operation) raises on expiry/conflict/stop; adapter calls before load and each chunk',
                               '8 owns run UUID, output path, failure record and accepted manifest; mark new decoder of cached activity accurately'],
          actual_runner_v1_limit='current validate() permits only609/no-ablation/decoder disabled; no decoder dispatch yet',
          integration_status='CPU_CACHE_AND_STATIC_API_COMPATIBLE; DECODER_PLUGIN_WIRING_AND_GPU_SMOKE_NOT_RUN',
          pending=['B+8 intervention worker/hook, separate from original untouched Full reference',
                   '8 plugin/config support for4x485/decoder; valid scope key and resource lease',
                   'short authorized original decoder chunk smoke incl weights/finite/results; no fullCPU crossvalidation'],
          Full_repeat609_required=False))
    dump('BUILD_RECEIPT.json', dict(status='PASS_CPU_INTERFACE_FREEZE', new_neural_steps=0, new_GPU_calls=0,
                                   new_decoder_forward_calls=0, command=[sys.executable, *sys.argv],
                                   conditions=[c['condition_id'] for c in selected],
                                   B_shared_inputs_and_coordinates_equal=True,
                                   scientific_preregistration_unchanged=pin(B / 'PREREGISTRATION_v1.json')))
    print('PASS_CPU_INTERFACE_FREEZE: no new neural/GPU/decoder forward; four condition Full CACHE_MISS')


if __name__ == '__main__':
    main()

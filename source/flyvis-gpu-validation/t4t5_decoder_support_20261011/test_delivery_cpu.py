"""Bounded CPU-only contract/cache/readout tests, no neural/decoder forward."""
import ast
import argparse
import inspect
import json
import os
import sys

os.environ.update(CUDA_VISIBLE_DEVICES='-1', FLYVIS_ROOT_DIR='/opt/flyvis-phase3-data',
                  MPLBACKEND='Agg', MPLCONFIGDIR='/tmp/flyvis-decoder-audit-mpl',
                  NUMBA_CACHE_DIR='/tmp/flyvis-decoder-audit-numba', PYTHONDONTWRITEBYTECODE='1')
sys.dont_write_bytecode = True
import numpy as np
from service import HERE, AcceptedReferenceCache, OfficialDecoderService, canonical, capabilities, load_json, sha
from flow_readout import frozen_B_metrics, official_loss_equivalents, stimulus_direction

checks = []


def check(label, condition):
    assert condition, label
    checks.append(label)


def reject(label, callback, text):
    try:
        callback()
    except ValueError as exc:
        check(label, text in str(exc))
    else:
        raise AssertionError(label + ' did not reject')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repeat', type=int, default=1)
    args = parser.parse_args()
    dest = HERE / ('tests_r' + str(args.repeat))
    dest.mkdir(exist_ok=False)
    check('adapter_import_does_not_import_Torch_FlyVis', 'torch' not in sys.modules and 'flyvis' not in sys.modules)
    check('adapter_not_a_scheduler', not capabilities()['scheduler'])
    cache = AcceptedReferenceCache()
    previews = {}
    for name, entry in cache.registry['references'].items():
        a, receipt = cache.open(name, entry['identity'])
        check('cache_readonly_' + name, not a.flags.writeable)
        check('cache_replay_label_' + name, receipt['execution_kind'] == 'accepted_cache_replay' and not receipt['actual_new_neural_computation'])
        previews[name] = dict(shape=list(a.shape), dtype=str(a.dtype), first_value=float(a.flat[0]),
                              source_run_id=receipt['source_run_id'], limits=receipt['limits'])
        reject('formal_cache_rejected_' + name, lambda: cache.open(name, entry['identity'], fresh_process=True), 'FRESH_PROCESS')
    camera = cache.registry['references']['camera609_Full']
    reject('stale_a0_cache_rejected', lambda: cache.open('camera609_Full', dict(camera['identity'], initial_state_sha256='e1ca_cpu_not_camera')), 'IDENTITY')
    reject('new_angle_not_renamed_cache', lambda: cache.open('ON60_Full', camera['identity']), 'CACHE_MISS')
    check('historical_G2_not_new_angles', cache.registry['references']['G2_edge0_180_Full']['identity']['original_samples'] == [0, 1, 12, 13])
    check('old_flow_preview_not_shared_G2_baseline', cache.registry['references']['edge0_180_decoder_preview']['identity']['strict_G2_baseline_eligible'] is False)
    # Numerical formula equality against original loss on small CPU tensors only.
    import torch
    torch.set_num_threads(1)
    import flyvis
    from flyvis.task.objectives import epe, l2norm
    from flyvis.datasets.sintel_utils import sample_flow
    from flyvis.datasets.rendering.utils import render_bars_cartesian
    from flyvis.datasets.rendering.eye import BoxEye
    x = np.zeros((2, 3, 2, 721), dtype=np.float64)
    y = x.copy(); y[:, :, 0] = 3; y[:, :, 1] = 4
    scores = official_loss_equivalents(x, y)
    check('official_l2norm_formula_small_CPU', np.isclose(scores['l2norm_difference'], float(l2norm(torch.tensor(x), torch.tensor(y)))))
    check('official_epe_formula_small_CPU', np.isclose(scores['mean_endpoint_difference'], float(epe(torch.tensor(x), torch.tensor(y)))) and scores['mean_endpoint_difference'] == 5)
    reject('nonfinite_flow_reject', lambda: official_loss_equivalents(x*np.nan, y), 'FINITE_FLOW')
    # Test source coordinate and target unit pipeline, on tiny synthetic image/file.
    flo = dest / 'coordinate_probe.flo'
    raw = np.empty((2, 3, 2), dtype=np.float32); raw[:, :, 0] = 4; raw[:, :, 1] = 6
    with flo.open('wb') as f:
        np.array([202021.25], np.float32).tofile(f)
        np.array([3, 2], np.int32).tofile(f)
        raw.tofile(f)
    target = sample_flow(flo)
    check('sample_flow_x_right_y_up_height_normalization', np.all(target[0] == 2) and np.all(target[1] == -3))
    eye = BoxEye(extent=0, kernel_size=13)
    ones = torch.ones(1, 1, 31, 31)
    check('BoxEye_target_sum_area169_not_mean', float(eye(ones, ftype='sum')[0, 0, 0, 0]) == 169 and
          float(eye(ones, ftype='mean')[0, 0, 0, 0]) == 1)
    directions = []
    for angle in [0, 60, 90, 180, 240, 270]:
        centroids = []
        for offset in [-8, 8]:
            im = render_bars_cartesian(101, 101, 3, 61, 50+offset, 50, 1, 1., 0., rotate=angle)
            yy, xx = np.indices(im.shape)
            centroids.append(np.array([(im*xx).sum()/im.sum(), -(im*yy).sum()/im.sum()]))
        delta = centroids[1] - centroids[0]
        d = delta / np.linalg.norm(delta)
        expected = stimulus_direction(angle)
        check('source_bar_direction_' + str(angle), np.dot(d, expected) > 0.9999)
        directions.append(dict(angle_deg=angle, measured_xy_direction=d.tolist(), expected_xy_direction=expected.tolist()))
    # Load actual original decoder via new adapter, CPU audit only: zero forward.
    scopes = []
    service = OfficialDecoderService('/opt/flyvis-visual-experiments-data/results/flow/0000/000',
                                     HERE / 'FULL_DECODER_CONTRACT.json', device='cpu', check_scope=scopes.append)
    check('adapter_actual_recursive_eval', not any(m.training for m in service.decoder.modules()))
    check('adapter_checkpoint_state_unchanged', service.assert_weights_unchanged())
    reject('central65_is_not_decoder_input', lambda: service.decode(np.zeros((1, 1, 65), np.float32)), 'FULL_SPATIAL')
    reject('no_automatic_CPU_inference', lambda: service.decode(np.zeros((1, 1, 45669), np.float32)), 'CPU_AUDIT_ONLY')
    reject('no_scope_no_decoder_load', lambda: OfficialDecoderService('', HERE / 'FULL_DECODER_CONTRACT.json', device='cpu', check_scope=None), 'SCOPE')
    check('adapter_zero_decoder_forward', service.forward_calls == 0)
    check('scope_checked_before_import_load', scopes == ['decoder_load'])
    for method, arguments in [('init__', ['model_path', 'contract_path', 'device', 'check_scope']),
                              ('decode', ['activity', 'chunk_frames', 'mask_types', 'mask_start_step']),
                              ('assert_weights_unchanged', [])]:
        check('public_signature_' + method, set(arguments) <= set(inspect.signature(getattr(OfficialDecoderService, method)).parameters))
    # Reuse B scientific thresholds; toy vectors are not biological outcomes.
    sham = np.zeros((485, 2, 721), np.float32); sham[200:286, 0] = 1
    scores_same = frozen_B_metrics(sham, sham, angle_deg=60)['primary']
    check('frozen_B_identity_Q1_E0', scores_same['Q'] == 1 and scores_same['field_error_E'] == 0)
    amplified = sham*2
    scores_amplified = frozen_B_metrics(sham, amplified, angle_deg=60)['primary']
    check('no_per_mode_max_normalization', scores_amplified['magnitude_ratio'] == 2 and scores_amplified['Q'] == 2)
    weak = np.zeros_like(sham)
    weak_score = frozen_B_metrics(weak, weak, angle_deg=60)['primary']
    check('weak_reference_ineligible_and_null', not weak_score['reference_eligible'] and weak_score['Q'] is None and weak_score['angle_deg'] is None)
    rotated = np.zeros_like(sham); rotated[200:286, 1] = 1
    check('frozen_B_rotation_reported_separately', np.isclose(frozen_B_metrics(sham, rotated, angle_deg=60)['primary']['angle_deg'], 90))
    # Recompute 8's exact current camera Full cache key without running scheduler.
    runner = HERE.parents[1] / 'flyvis-autorunner'
    config = load_json(runner / 'configs/camera609.fast.json')
    binding = load_json(HERE.parent / 'phase4_camera_rectb_20261011/common_bundle/camera_backend_identity.json')
    identity_fields = ('stimulus_sha256', 'time_sha256', 'activity_time_sha256', 'initial_state_sha256',
                      'expanded_parameters_sha256', 'checkpoint_sha256', 'source_commit', 'numeric_profile_sha256',
                      'candidate_sha256', 'node_map_sha256', 'edge_partition_sha256', 'static_boundary_sha256',
                      'input_manifest_sha256', 'input_reader_sha256', 'nodes_full_sha256', 'dt_s', 'steps')
    from service import host_path
    core = {n: sha((runner / config['sources'][n]).resolve()) for n in ('full', 'r_only')}
    context = dict({k: binding[k] for k in identity_fields}, backend='FullGPU',
                   ablation={'definition': 'NONE', 'start_step': None}, kernel_sources=core,
                   backend_numeric='ORIGINAL_FP32_GPU')
    runner_key = canonical(context)
    record = load_json(runner / 'cache/FullGPU' / (runner_key + '.json'))
    check('AutoRunner_existing_Full_cache_exact_key', record['cache_key'] == runner_key and
          record['essential_sha256']['activities_full.npy'] == camera['pins'][0]['sha256'])
    check('AutoRunner_current_decoder_disabled_explicit', 'NOT_USED_PHASE1' in (runner / 'autorunner.py').read_text())
    result = dict(status='PASS_CPU_CONTRACT_CACHE_READOUT', checks=len(checks), passed=checks,
                  execution_kind='actual_CPU_structure_and_small_software_unit_tests', neural_steps=0,
                  decoder_forward_calls=0, CUDA_operations=0, board_operations=0,
                  GPU_chunk_equivalence='NOT_RUN', AutoRunner_decoder_dispatch='NOT_IMPLEMENTED_BY_RUNNER_YET',
                  cache_previews=previews, source_bar_direction_probe=directions,
                  runner_camera_Full_cache_key=runner_key, decoder_scopes_called=scopes,
                  command=[sys.executable, *sys.argv], software_versions=dict(numpy=np.__version__, torch=torch.__version__, flyvis=flyvis.__version__))
    (dest / 'result.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    (HERE / 'TEST_RESULTS.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print('PASS_CPU_CONTRACT_CACHE_READOUT:', len(checks), 'checks; neural/decoder forward/CUDA/board=0')


if __name__ == '__main__':
    main()

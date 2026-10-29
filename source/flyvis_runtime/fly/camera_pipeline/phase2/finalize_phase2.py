"""Independently verify second-stage state files and preserve first-stage identity."""
from __future__ import annotations
import csv
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
import torch
from types import SimpleNamespace
from camera_pipeline.common import ROOT, sha256, utc_now, write_json
from camera_pipeline.phase2.gui_handoff import load_experiment
from camera_pipeline.phase2.network_state import validate_payload


def run():
    state_dir = ROOT/'phase2/results/continuous_state_r2'
    descriptor = ROOT/'phase2/results/gui_real_video_r1/experiment.json'
    report = json.loads((state_dir/'state_validation.json').read_text(encoding='utf-8'))
    assert report['status'] == report['fresh_process_resume']['status'] == 'PASS'
    for name, digest in report['data_sha256'].items():
        assert sha256(state_dir/name) == digest, name
    runtime = SimpleNamespace(torch=torch, identity=report['identity'])
    identity = {key: report[key] for key in ('input_sha256', 'coordinates_sha256')}
    all_nodes = np.load(state_dir/'activity_all_nodes_monolithic.npy', mmap_mode='r')
    assert all_nodes.shape == (1, 1202, 45669) and all_nodes.dtype == np.float32
    for start in range(0, 1202, 128):
        assert np.isfinite(all_nodes[:, start:start+128]).all()
    checkpoints = []
    for name in ('state_final_monolithic.pt', 'state_final_fresh_process.pt', 'state_after_001202.pt'):
        payload = torch.load(state_dir/name, map_location='cpu', weights_only=True)
        state = validate_payload(payload, runtime, next_step=1202, **identity)
        assert np.array_equal(state['nodes']['activity'].numpy(), all_nodes[:, -1]), name
        checkpoints.append(name)
    for block in report['blocks']:
        step = block['stop_step_exclusive']
        payload = torch.load(state_dir/block['checkpoint'], map_location='cpu', weights_only=True)
        state = validate_payload(payload, runtime, next_step=step, **identity)
        assert np.array_equal(state['nodes']['activity'].numpy(), all_nodes[:, step-1])
        assert block['warmup_in_block'] == 0
    for name, count, first in [('step_comparison.csv', 1202, 0), ('fresh_process_step_comparison.csv', 1201, 1)]:
        with (state_dir/name).open(newline='') as file:
            rows = list(csv.DictReader(file))
        assert len(rows) == count
        assert [int(row['step']) for row in rows] == list(range(first, 1202))
        assert all(row['bitwise_equal'] == 'True' and float(row['max_abs_all_45669_nodes']) == 0
                   and float(row['rmse_all_45669_nodes']) == 0 for row in rows)
    experiment = load_experiment(descriptor)
    central_indices = np.load(ROOT/'results/real_camera_gpu_zoh_r1/central_node_indices.npy', allow_pickle=False)
    assert np.array_equal(all_nodes[:, :, central_indices], experiment.activity)
    old_manifest = json.loads((ROOT/'results/validation/manifest.json').read_text(encoding='utf-8'))
    mismatches = [name for name, digest in old_manifest['files'].items() if sha256(ROOT/name) != digest]
    assert not mismatches, f'First-stage package changed: {mismatches}'
    protected = json.loads((ROOT/'phase2/logs/protected_after.json').read_text(encoding='utf-8'))
    assert protected['protected_hashes_unchanged'] and not protected['tracked_upstream_status']
    gui_evidence = ROOT.parent/'gui_v1/evidence/phase2/import_acceptance.json'
    gui = json.loads(gui_evidence.read_text(encoding='utf-8'))
    assert gui['status'] == 'PASS'
    assert gui['camera']['input_sha256'] == sha256(experiment.paths['stimulus'])
    assert gui['camera']['output_sha256'] == sha256(experiment.paths['activity'])
    assert gui['camera']['all_1202_zoh_steps_exact'] and gui['camera']['euler_after_time_exact']
    for filename, count in [('timing_contract_tests.log', 6), ('state_contract_tests.log', 10)]:
        log = (ROOT/'phase2/logs'/filename).read_text(encoding='utf-8')
        assert f'Ran {count} tests' in log and log.rstrip().endswith('OK'), filename
    chunk_s = sum(block['simulation_s'] for block in report['blocks'])
    result = {'schema': 'flyvis-camera-phase2-acceptance-v1', 'status': 'PASS', 'checked_utc': utc_now(),
              'scope': 'complete network state and local GUI handoff tools; controlled physical video remains pending',
              'state_steps': 1202, 'nodes_per_step': 45669, 'edges': 1513231,
              'same_process_disk_resumed_chunks': len(report['blocks']), 'all_nodes_all_steps_bitwise_equal': True,
              'fresh_process_resumed_steps': 1201, 'fresh_process_warmup': 0, 'final_states_independently_verified': checkpoints,
              'all_chunk_checkpoint_nodes_match_monolithic_boundary': True, 'weights_exact_before_and_after': True,
              'descriptor_sha256': sha256(descriptor), 'descriptor_read_and_time_alignment': 'PASS',
              'gui_contract_confirmation': 'Confirmed by GUI lane; camera-specific source/input/post-update clocks',
              'gui_phase1_dataset_import': {'status': 'PASS', 'evidence': str(gui_evidence), 'sha256': sha256(gui_evidence),
                                            'v2_descriptor_automatically_loaded': False,
                                            'scope': gui['evidence_level']},
              'first_stage_sealed_files_unchanged': len(old_manifest['files']),
              'protected_reference_files_unchanged': len(protected['protected_files']),
              'original_source_tracked_status': protected['tracked_upstream_status'],
              'tests': {'timing_contract_cases': 6, 'state_contract_cases': 10, 'status': 'PASS'},
              'offline_timing': {'monolithic_gpu_simulation_s': report['monolithic_simulation_s'],
                                 'monolithic_steps_per_s': 1202/report['monolithic_simulation_s'],
                                 'chunk_simulation_sum_s': chunk_s, 'chunk_steps_per_s_excluding_io': 1202/chunk_s,
                                 'scope': report['timing_scope']},
              'controlled_capture': 'PENDING_PHYSICAL_SETUP_USER_UNAVAILABLE',
              'live_end_to_end_test': 'NOT_RUN_THIS_ROUND_USER_PRIORITIZED_STATE_AND_GUI',
              'processing_mode': 'offline', 'real_time_claim': False,
              'gui_code_modified_by_this_lane': False, 'camera_opened_this_round': False,
              'raw_video_data_sent_to_other_thread_or_remote': False, 'fpga_or_board_operations': False}
    write_json(ROOT/'phase2/results/acceptance.json', result)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result


if __name__ == '__main__':
    run()

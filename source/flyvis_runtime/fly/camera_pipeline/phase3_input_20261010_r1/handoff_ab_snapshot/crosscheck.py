"""Read-only A/B frozen-input crosscheck; does not execute their neural backends."""
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from identity import HERE, CAMERA, PATHS, array, check, payload_sha, read_json, sha, write_json

OUT = Path(__file__).resolve().parent
FLY = CAMERA.parent
A = FLY / 'gpu_phase3_fixed_video_20261010'
B = FLY.parent / 'fpga/flyvis-circuit-selection/phase3_20261010'
av = read_json(A / 'bundle/video_manifest.json')
bh = read_json(B / 'B_INPUT_IDENTITY_HANDOFF.json')
bv = read_json(B / 'input_bundle/video_manifest.json')
refs = {}; matches = {}
for name, filename, source_key in [('stimulus','stimulus.npy','single_stimulus'), ('a0','initial_state_full.npy','initial_state'),
                                  ('input_time','time.npy','input_time'), ('activity_time','activity_time.npy','activity_time'),
                                  ('coordinates','input_hex_coordinates.csv','coordinates')]:
    expected = sha(PATHS[source_key])
    for owner, root in [('A', A/'bundle'), ('B', B/'input_bundle')]:
        path = root / filename
        check(sha(path) == expected, f'{owner} {name} differs from camera input source')
        refs[f'{owner}_{name}'] = {'path': str(path), 'sha256': sha(path), 'bytes': path.stat().st_size}
    matches[name] = {'status': 'PASS_FILE_BYTES', 'sha256': expected}
for name, filename, a_field, b_field in [
    ('expanded_parameters','expanded_parameters.npz','expanded_parameters_sha256','parameter_sha256'),
    ('node_map','candidates/B_T5c/node_map.csv','node_map_sha256',None),
    ('input_node_indices','input_node_indices.npy',None,None)]:
    ap, bp = A/'bundle'/filename, B/'input_bundle'/filename
    digest = sha(ap); check(digest == sha(bp), f'A/B {name} file bytes disagree')
    if a_field: check(av[a_field] == digest, f'A declared {name} hash disagrees')
    if b_field: check(bh[b_field] == digest, f'B declared {name} hash disagrees')
    if name == 'node_map': check(bh['identity_fingerprint']['node_map'] == digest, 'B declared node map mismatch')
    matches[name] = {'status': 'PASS_A_B_FILE_BYTES_ONLY', 'sha256': digest}
    for owner, path in [('A',ap),('B',bp)]: refs[f'{owner}_{name}'] = {'path':str(path),'sha256':digest,'bytes':path.stat().st_size}
documents = {'A_video_manifest': A/'bundle/video_manifest.json', 'B_input_handoff': B/'B_INPUT_IDENTITY_HANDOFF.json',
             'B_video_manifest': B/'input_bundle/video_manifest.json',
             'A_single_step_report': A/'artifacts/single_step_gpu_r2/acceptance.json',
             'B_single_step_report': B/'artifacts/preflight_r1/result.json'}
for key,path in documents.items(): refs[key] = {'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size}
result = {'schema':'flyvis-input-lane-A-B-read-only-crosscheck-v1', 'checked_utc':datetime.now(timezone.utc).isoformat(),
    'status':'INPUT_DATA_MATCH_COMPARISON_ID_PENDING', 'scope':'actual read-only file identities; neural reports observed, not rerun or independently accepted by input lane',
    'condition_id':'01_off_right', 'checks':matches,
    'x_payload_sha256':payload_sha(array(PATHS['single_stimulus'])[0,:,0]),
    'a0_payload_sha256':payload_sha(array(PATHS['initial_state'])[0]),
    'comparison_ids_observed':{'A_video_confirmed':av['comparison_id'], 'A_proposed':av['proposed_comparison_id'],
                               'B_manifest':bv['comparison_id']},
    'A_report_status_observed':read_json(documents['A_single_step_report'])['status'],
    'B_report_status_observed':read_json(documents['B_single_step_report'])['status'],
    'single_step_neural_values_verified_by_input_lane':False, 'eight_hundred_step_acceptance_by_input_lane':False,
    'decision_owner':'A/B must confirm one comparison_id and corresponding parameter/numeric/metric identity', 'files':refs}
write_json(OUT/'read_only_crosscheck.json',result)
write_json(OUT/'manifest.json',{'schema':'flyvis-input-crosscheck-snapshot-seal-v1',
    'files':[{'path':p.name,'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='manifest.json']})
print(json.dumps({'status':result['status'],'matched_identities':list(matches),'comparison_ids_observed':result['comparison_ids_observed']}))

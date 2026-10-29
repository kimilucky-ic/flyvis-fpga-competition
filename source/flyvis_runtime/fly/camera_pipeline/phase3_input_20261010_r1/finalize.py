"""Create this input-lane acceptance and seal; never write the historical bundle."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from identity import HERE, source, load_bundle, read_json, sha, verify_historical_seal, write_json

if '--verify' in sys.argv:
    seal = read_json(HERE / 'manifest.json')
    for item in seal['files']:
        path = (HERE / item['path']).resolve()
        if not path.is_relative_to(HERE.resolve()) or path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
            raise ValueError(f'Sealed file changed: {path}')
    load_bundle()
    print(json.dumps({'status': 'PASS', 'sealed_files': len(seal['files']), 'historical_files_unchanged': verify_historical_seal()}))
else:
    bundle = load_bundle(); identity = bundle['identity']
    historical_count = verify_historical_seal()
    wsl = read_json(HERE / 'logs/wsl_verification.json')
    protected = read_json(HERE / 'logs/protected_after.json')
    test_log = (HERE / 'logs/handoff_tests.log').read_text(encoding='utf-8-sig')
    if 'Ran 7 tests' not in test_log or '\nOK' not in test_log:
        raise ValueError('Windows contract tests did not pass')
    if wsl['identity_verify']['exit_code'] != 0 or wsl['handoff_tests']['status'] != 'OK':
        raise ValueError('WSL validation did not pass')
    baseline = read_json(HERE.parent / 'logs/protected_before.json')
    if protected['protected_files'] != baseline['protected_files'] or protected['tracked_upstream_status'] != baseline['tracked_upstream_status'] or protected['source_commit'] != baseline['source_commit']:
        raise ValueError('Protected reference files or upstream tracked status changed')
    acceptance = {'schema': 'flyvis-phase3-input-lane-acceptance-v1', 'status': 'PASS',
        'checked_utc': datetime.now(timezone.utc).isoformat(), 'artifact': 'INPUT_SINGLE_VIDEO_IDENTITY',
        'scope': 'camera/visual input lane only; not Gate S1/S2/S3/S4 or completed hybrid loop',
        'condition_id': '01_off_right', 'aggregate_sample': 1,
        'identity_sha256': sha(HERE / 'INPUT_SINGLE_VIDEO_IDENTITY.json'),
        'single_stimulus_file_sha256': identity['files']['single_stimulus']['sha256'],
        'single_stimulus_numeric_payload_sha256': identity['input']['x_tensor']['c_order_payload_sha256'],
        'initial_state_file_sha256': identity['files']['initial_state']['sha256'],
        'initial_state_numeric_payload_sha256': identity['initial_state']['flat_tensor']['c_order_payload_sha256'],
        'x_shape': list(bundle['x'].shape), 'a0_shape': list(bundle['a0'].shape),
        'Windows_read_only_consumer': 'PASS', 'WSL_read_only_consumer': 'PASS',
        'Windows_negative_contract_tests': 7, 'WSL_negative_contract_tests': 7,
        'checks': identity['checks'], 'protected_reference_files_unchanged': len(protected['protected_files']),
        'historical_files_unchanged': historical_count,
        'new_GPU_inference': False, 'new_preprocessing': False, 'new_camera_capture': False,
        'Python_H_R_closed_loop_executed_by_this_lane': False, 'RTL_simulation_executed_by_this_lane': False,
        'live_FPGA_executed_by_this_lane': False, 'comparison_id': None,
        'next_dependency': 'A/B independently confirm GPU-native parameter/node mapping identity and produce matched Full/Python 800-step state traces; C owns RTL/SoC/board execution'}
    write_json(HERE / 'acceptance.json', acceptance)
    files = []
    for path in sorted(HERE.rglob('*')):
        if path.is_file() and path.name != 'manifest.json' and '__pycache__' not in path.parts and path.suffix != '.pyc':
            files.append({'path': path.relative_to(HERE).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha(path)})
    write_json(HERE / 'manifest.json', {'schema': 'flyvis-phase3-input-lane-seal-v1', 'files': files,
        'scope': 'only the new identity namespace; no neural arrays regenerated or copied',
        'identity_file_sha256': acceptance['identity_sha256']})
    print(json.dumps({'status': 'PASS', 'identity_sha256': acceptance['identity_sha256'], 'sealed_files': len(files)}))

"""Local negative gate checks only. Never imports PYNQ, downloads or executes PL."""
import argparse
import ast
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'pynq'))
import first_board_step as launcher


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    release = args.release_dir.resolve()
    manifest, bit, hwh = launcher.load_release(release)
    requests, oracle, fixture = launcher.verify_fixture(release, manifest)
    review = {'status': 'FIRST_STEP_BOARD_PRECHECK_REVIEWED', 'fpga_part': 'xc7z020clg400-2',
              'power_verified': True, 'boot_mode': 'SD_CARD', 'runtime_sources_reviewed': True,
              'hp0_width_bits': 64, 'ddr_preset_reviewed': True, 'first_request_row': 0,
              'request_count': 1, 'commit_authorized': False,
              'bit_sha256': launcher.sha_file(bit), 'hwh_sha256': launcher.sha_file(hwh),
              'release_manifest_sha256': launcher.sha_file(release / 'release_manifest.json'),
              'fixture_comparison_id': fixture['comparison_id'],
              'request_sha256': launcher.sha_bytes(requests[0].tobytes()),
              'integer_oracle_sha256': launcher.sha_bytes(oracle[0].tobytes()),
              'core_revision': 'SOFTWARE_FIXTURE_ONLY', 'carrier_revision': 'SOFTWARE_FIXTURE_ONLY',
              'pynq_version': 'SOFTWARE_FIXTURE_ONLY', 'boot_id': 'SOFTWARE_FIXTURE_ONLY',
              'video_reference': 'SOFTWARE_FIXTURE_ONLY', 'software_sha256': {}}
    for name in ('first_board_step.py', 'flyvis_v1_evidence_driver.py', 'flyvis_v1_driver.py'):
        review['software_sha256'][name] = launcher.sha_file(ROOT / 'pynq' / name)
    cases = [('wrong_BIT_authorization', None, None), ('wrong_HWH_authorization', None, None),
             ('wrong_review_authorization', None, None)]
    for field in ('status', 'fpga_part', 'power_verified', 'boot_mode', 'runtime_sources_reviewed',
                  'hp0_width_bits', 'ddr_preset_reviewed', 'first_request_row', 'request_count',
                  'commit_authorized', 'bit_sha256', 'hwh_sha256', 'core_revision', 'carrier_revision',
                  'pynq_version', 'boot_id', 'video_reference'):
        cases.append(('missing_' + field, field, 'delete'))
    for field in ('release_manifest_sha256', 'fixture_comparison_id', 'request_sha256', 'integer_oracle_sha256'):
        cases.append(('missing_' + field, field, 'delete'))
        cases.append(('wrong_' + field, field, '0' * 64))
    cases += [('multiple_requests', 'request_count', 32), ('commit_enabled', 'commit_authorized', True),
              ('software_changed', 'software_sha256', {}), ('non_Zynq_host', None, None)]
    results = []
    for name, field, mutation in cases:
        fixture = json.loads(json.dumps(review))
        if mutation == 'delete':
            del fixture[field]
        elif field:
            fixture[field] = mutation
        review_path = output / (name + '.SOFTWARE_FIXTURE_NOT_APPROVAL.json')
        review_path.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')
        call = SimpleNamespace(release_dir=release, board_review=review_path,
                               authorize_bit_sha256=review['bit_sha256'],
                               authorize_hwh_sha256=review['hwh_sha256'],
                               authorize_review_sha256=launcher.sha_file(review_path))
        if name == 'wrong_BIT_authorization': call.authorize_bit_sha256 = '0' * 64
        if name == 'wrong_HWH_authorization': call.authorize_hwh_sha256 = '0' * 64
        if name == 'wrong_review_authorization': call.authorize_review_sha256 = '0' * 64
        try:
            launcher.review_before_load(call)
        except launcher.FlyVisBoardFault as exc:
            results.append({'case': name, 'blocked': True, 'reason': str(exc)})
        else:
            raise AssertionError('Negative gate did not reject: ' + name)
    for path in (ROOT / 'pynq').glob('*.py'):
        if path.name in review['software_sha256']:
            ast.parse(path.read_text(encoding='utf-8'), feature_version=(3, 8))
    if 'pynq' in sys.modules or 'pynq.mmio' in sys.modules:
        raise AssertionError('Local gate check unexpectedly imported PYNQ')
    report = {'status': 'PASS_LOCAL_NEGATIVE_FIRST_STEP_GATE_CHECKS_ONLY',
              'evidence_level': 'SOFTWARE_ONLY_NO_PYNQ_IMPORT_NO_BOARD_EXECUTION',
              'board_io_operations': 0, 'python38_syntax_checked': True,
              'checks': results, 'case_count': len(results),
              'software_sha256': review['software_sha256'],
              'does_not_validate_actual_pynq_runtime_or_pl': True}
    (output / 'SOFTWARE_REPORT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

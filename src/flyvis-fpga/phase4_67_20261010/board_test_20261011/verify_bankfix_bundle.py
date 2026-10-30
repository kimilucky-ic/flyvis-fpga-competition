"""Independently recompute every packaged identity and XSA contents; file-only."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'pynq'))
from flyvis_v1_driver import load_release, verify_fixture, sha_file, sha_bytes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    release = args.release_dir.resolve()
    manifest, bit, hwh = load_release(release)
    requests, oracle, fixture = verify_fixture(release, manifest)
    checks = []
    for group in ('files', 'build_logs', 'copied_vectors', 'first_step_software'):
        for name, entry in manifest[group].items():
            if not isinstance(entry, dict) or 'sha256' not in entry or name == 'hls_component_xml':
                continue
            path = release / entry['path']
            actual = sha_file(path)
            if actual != entry['sha256']:
                raise ValueError('Packaged identity changed: ' + str(path))
            checks.append({'group': group, 'path': entry['path'], 'sha256': actual})
    for entry in manifest['source_identity']:
        path = release / entry['path']
        if sha_file(path) != entry['sha256']:
            raise ValueError('Packaged source identity changed: ' + str(path))
        checks.append({'group': 'source_identity', 'path': entry['path'], 'sha256': sha_file(path)})
    embedded = []
    with zipfile.ZipFile(release / manifest['files']['xsa']['path']) as archive:
        for member, path in (('flyvis_t5c_source_raw_v1.bit', bit), ('flyvis_v1.hwh', hwh)):
            digest = hashlib.sha256(archive.read(member)).hexdigest()
            if digest != sha_file(path):
                raise ValueError('XSA embedded BIT/HWH differs from release: ' + member)
            embedded.append({'member': member, 'sha256': digest, 'matches_external_release': True})
    report = {'status': 'PASS_FILE_ONLY_BANKFIX_BUNDLE_IDENTITY',
              'board_io_operations': 0, 'board_execution_proven': False,
              'release_manifest_sha256': sha_file(release / 'release_manifest.json'),
              'file_checks': checks, 'xsa_embedded_pair': embedded,
              'first_request': {'row': 0, 'request_words': int(requests[0].size),
                                'oracle_words': int(oracle[0].size),
                                'request_sha256': sha_bytes(requests[0].tobytes()),
                                'integer_oracle_sha256': sha_bytes(oracle[0].tobytes()),
                                'fixture_comparison_id': fixture['comparison_id']},
              'hardware_gate': 'CLOSED_PHYSICAL_RUNTIME_REVIEW_AND_EXACT_USER_AUTHORIZATION_PENDING'}
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'file_checks'}, indent=2))
    print('PACKAGED_FILE_CHECKS:', len(checks))


if __name__ == '__main__':
    main()

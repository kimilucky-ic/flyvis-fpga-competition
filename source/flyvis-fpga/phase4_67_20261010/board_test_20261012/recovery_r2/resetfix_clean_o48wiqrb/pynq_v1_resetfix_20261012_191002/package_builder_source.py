"""Package a sealed resetfix release and row0 identities; no board operations."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-dir', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    release, target = args.release_dir.resolve(), args.output_dir.resolve()
    manifest = json.loads((release / 'release_manifest.json').read_text())
    if not release.name.startswith('V1_resetfix_') or manifest.get('aux_reset_asserted_by_constant') is not False:
        raise ValueError('Expected sealed resetfix release')
    for key in ('bitstream', 'hwh', 'xsa', 'implementation_timing', 'implementation_utilization',
                'implementation_drc', 'implementation_io', 'synthesis_timing', 'synthesis_utilization'):
        entry = manifest['files'][key]
        if sha(release / entry['path']) != entry['sha256']:
            raise ValueError('Release identity mismatch: ' + entry['path'])
    target.mkdir(parents=True, exist_ok=False)
    shutil.copytree(release, target / 'release', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copyfile(Path(__file__).resolve(), target / 'package_builder_source.py')
    vectors = target / 'release' / 'vectors'
    request = (vectors / 'requests_i32le.bin').read_bytes()[:1498 * 4]
    oracle = (vectors / 'expected_i32le.bin').read_bytes()[:67 * 4]
    if hashlib.sha256(request).hexdigest() != 'ea1cb4a5f1d655183cad390ef0226ca138eb77d783f4edf271fb37711d9be8b4':
        raise ValueError('Row0 request identity mismatch')
    if hashlib.sha256(oracle).hexdigest() != '50f212ffd6e47abebc8758b8c48999eb40957aabd0106b467ad4cc47a4f92a00':
        raise ValueError('Row0 oracle identity mismatch')
    (target / 'row0_request_i32le.bin').write_bytes(request)
    (target / 'row0_oracle_i32le.bin').write_bytes(oracle)
    (target / 'readme.txt').write_text(
        'FlyVis 67-node SOURCE_RAW Q22 resetfix release.\n'
        'File packaging and full implementation evidence only; no live-board PASS.\n'
        'Both reset inputs explicitly active-high; auxiliary input tied to zero.\n'
        'Old BIT/HWH and previous evidence must be preserved.\n'
        'Do not load before reviewing new BIT/HWH hashes and obtaining exact authorization.\n'
        'Load-only and one row0 request are separate manual operations. No retry/COMMIT/32/800.\n',
        encoding='utf-8')
    files = [{'path': p.relative_to(target).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
             for p in sorted(target.rglob('*')) if p.is_file()]
    package = {'status': 'RESETFIX_PACKAGE_FILE_ONLY_NO_BOARD_EXECUTION', 'files': files,
               'release_manifest_sha256': sha(release / 'release_manifest.json'), 'board_operations': 0}
    (target / 'package_manifest.json').write_text(json.dumps(package, indent=2) + '\n')
    archive = target.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(target.rglob('*')):
            if p.is_file():
                z.write(p, p.relative_to(target.parent).as_posix())
    identity = {'directory': str(target), 'zip': str(archive), 'zip_sha256': sha(archive),
                'package_manifest_sha256': sha(target / 'package_manifest.json'),
                'bit_sha256': manifest['files']['bitstream']['sha256'],
                'hwh_sha256': manifest['files']['hwh']['sha256'], 'board_operations': 0}
    with target.with_suffix('.identity.json').open('x') as stream:
        json.dump(identity, stream, indent=2)
    print(json.dumps(identity, indent=2))


if __name__ == '__main__':
    main()

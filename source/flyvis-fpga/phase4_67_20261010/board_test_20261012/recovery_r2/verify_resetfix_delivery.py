"""Verify clean extracted delivery, XSA pair and 67 oracle words; no board access."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
NAME = 'pynq_v1_resetfix_20261012_191002'
archive = ROOT / 'delivery' / (NAME + '.zip')
identity = json.loads(archive.with_suffix('.identity.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(archive) == identity['zip_sha256']
clean = Path(tempfile.mkdtemp(prefix='RESETFIX_CLEAN_', dir=Path(__file__).parent))
with zipfile.ZipFile(archive) as z:
    for item in z.infolist():
        assert clean.resolve() in (clean / item.filename).resolve().parents
    z.extractall(clean)
package = clean / NAME
manifest = json.loads((package / 'package_manifest.json').read_text())
assert sha(package / 'package_manifest.json') == identity['package_manifest_sha256']
for item in manifest['files']:
    p = package / item['path']
    assert p.stat().st_size == item['bytes'] and sha(p) == item['sha256'], item['path']
release = package / 'release'
release_manifest = json.loads((release / 'release_manifest.json').read_text())
assert sha(release / 'release_manifest.json') == manifest['release_manifest_sha256']
with zipfile.ZipFile(release / 'flyvis_t5c_source_raw_v1.xsa') as xsa:
    embedded = {}
    for extension, key in (('.bit', 'bitstream'), ('.hwh', 'hwh')):
        names = [name for name in xsa.namelist() if name.endswith(extension)]
        assert len(names) == 1, names
        digest = hashlib.sha256(xsa.read(names[0])).hexdigest()
        assert digest == release_manifest['files'][key]['sha256']
        embedded[key] = {'xsa_entry': names[0], 'sha256': digest}
for item in release_manifest['source_identity']:
    assert sha(release / item['path']) == item['sha256']
report = {
    'status': 'PASS_CLEAN_EXTRACTED_FILES_AND_XSA_PAIR_ONLY',
    'zip': str(archive), 'zip_sha256': sha(archive), 'clean_extraction': str(clean),
    'checked_files': len(manifest['files']), 'xsa_embedded_pair': embedded,
    'source_snapshots_verified': len(release_manifest['source_identity']),
    'expected_row0_q22_i32': list(struct.unpack('<67i', (package / 'row0_oracle_i32le.bin').read_bytes())),
    'board_operations': 0, 'board_execution_proven': False, 'scientific_acceptance': 'NOT_GRANTED',
}
with Path(__file__).with_name('RESETFIX_DELIVERY_VERIFICATION.json').open('x') as stream:
    json.dump(report, stream, indent=2)
print(json.dumps(report, indent=2))

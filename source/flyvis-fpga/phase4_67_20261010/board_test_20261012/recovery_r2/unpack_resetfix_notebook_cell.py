"""File-only unpack/verification; exact ZIP identity is filled after sealing."""
from pathlib import Path
import hashlib
import json
import uuid
import zipfile

EXPECTED_ZIP_SHA256 = '91c0b730c731a7d27147155b6192d188f75567280b2874e83926f0a7d450442d'
BASE = Path('/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1')
ZIP = BASE / 'pynq_v1_resetfix_20261012_191002.zip'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if len(EXPECTED_ZIP_SHA256) != 64:
    raise RuntimeError('STOP: exact sealed resetfix ZIP identity not supplied')
if digest(ZIP) != EXPECTED_ZIP_SHA256:
    raise RuntimeError('STOP: uploaded resetfix ZIP identity mismatch')
UNPACK = BASE / ('unpacked_resetfix_' + uuid.uuid4().hex)
UNPACK.mkdir(exist_ok=False)
with zipfile.ZipFile(str(ZIP)) as archive:
    for member in archive.infolist():
        target = (UNPACK / member.filename).resolve()
        if UNPACK.resolve() not in target.parents:
            raise RuntimeError('STOP: ZIP path escapes isolated extraction')
        if (member.external_attr >> 16) & 0o170000 == 0o120000:
            raise RuntimeError('STOP: ZIP symbolic link not permitted')
    archive.extractall(str(UNPACK))
PACKAGE = UNPACK / 'pynq_v1_resetfix_20261012_191002'
manifest = json.loads((PACKAGE / 'package_manifest.json').read_text())
for item in manifest['files']:
    path = (PACKAGE / item['path']).resolve()
    if PACKAGE.resolve() not in path.parents:
        raise RuntimeError('STOP: manifest path escapes package')
    if path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
        raise RuntimeError('STOP: file mismatch: ' + item['path'])
RELEASE = PACKAGE / 'release'
if digest(RELEASE / 'release_manifest.json') != manifest['release_manifest_sha256']:
    raise RuntimeError('STOP: sealed release manifest mismatch')
release = json.loads((RELEASE / 'release_manifest.json').read_text())
if release.get('reset_checked_parameters') != {'C_EXT_RESET_HIGH': '1', 'C_AUX_RESET_HIGH': '1'}:
    raise RuntimeError('STOP: expected explicit corrected reset polarities absent')
report = {
    'status': 'PASS_FILE_ONLY_RESETFIX_PACKAGE', 'package_dir': str(PACKAGE),
    'checked_files': len(manifest['files']), 'zip_sha256': digest(ZIP),
    'bit_sha256': digest(RELEASE / 'flyvis_t5c_source_raw_v1.bit'),
    'hwh_sha256': digest(RELEASE / 'flyvis_t5c_source_raw_v1.hwh'),
    'release_manifest_sha256': digest(RELEASE / 'release_manifest.json'),
    'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
    'board_register_reads': 0, 'board_register_writes': 0,
    'pl_downloads': 0, 'board_execution_proven': False,
}
with (UNPACK / 'unpack_verification.json').open('x') as stream:
    json.dump(report, stream, indent=2)
print(json.dumps(report, indent=2))
print('PACKAGE_DIR:', PACKAGE)
print('STOP_HERE: FILE VERIFICATION ONLY; RETURN OUTPUT')

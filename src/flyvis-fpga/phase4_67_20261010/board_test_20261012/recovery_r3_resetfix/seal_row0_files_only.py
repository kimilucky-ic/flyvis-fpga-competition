"""Notebook cell: seal existing successful row0 files; no PYNQ or hardware I/O."""
from pathlib import Path
import hashlib
import json
import os
import uuid
import zipfile

base = Path('/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1/unpacked_resetfix_6d686a21b53a4303821311d7395becdd')
run = base / 'row0_resetfix_894292a3_attempt3_jupyter'
release = base / 'pynq_v1_resetfix_20261012_191002' / 'release'
def sha(data):
    return hashlib.sha256(data).hexdigest()
def require(ok, message):
    if not ok:
        raise RuntimeError('STOP_FILE_CHECK: ' + message)

result = json.loads((run / 'board_run.json').read_text())
report = json.loads((run / 'step0/step_report.json').read_text())
trace = [json.loads(line) for line in (run / 'step0/register_trace.jsonl').read_text().splitlines() if line.strip()]
request = (run / 'request_i32le.bin').read_bytes()
oracle = (run / 'integer_oracle_i32le.bin').read_bytes()
output = (run / 'PL_output_i32le.bin').read_bytes()
require(result['status'] == 'PASS_REAL_BOARD_ONE_STEP_INTEGER_ORACLE', 'result is not PASS')
require(result['exact_integer_match'] is True and result['mismatched_indices'] == [], 'integer mismatch')
require(result['python_fallback'] is False and result['committed'] is False, 'unexpected fallback or COMMIT')
require(report['completed'] is True and report['hls_status'] == 0, 'driver did not complete successfully')
require(report['completion_ctrl'] & 2 and report['registers_after']['CTRL'] & 4, 'DONE/IDLE missing')
require(not (report['registers_after']['CTRL'] & 0x81), 'START or AUTO_RESTART remains set')
starts = [e for e in trace if e.get('action') == 'mmio_write_returned' and e.get('offset') == 0]
require(len(starts) == 1 and starts[0]['value'] == 1, 'expected exactly one returned START write')
require(len(request) == 5992 and sha(request) == 'ea1cb4a5f1d655183cad390ef0226ca138eb77d783f4edf271fb37711d9be8b4', 'request identity')
require(len(output) == 268 and output == oracle and sha(output) == '50f212ffd6e47abebc8758b8c48999eb40957aabd0106b467ad4cc47a4f92a00', '67-word output identity')
require((run / 'step0/PL_candidate_i32le.bin').read_bytes() == output, 'driver output differs')
require((run / 'row0_console.log').is_file(), 'console missing')

expected = {
    'flyvis_t5c_source_raw_v1.bit': '23cf5da15db221f399b54cae95e341e6a90a699c88d321d0a883aecca15f7569',
    'flyvis_t5c_source_raw_v1.hwh': '3ea3f1e27c7b214e0f7a965455799875cbae94fb87bee6455a58ecbed4813f7d',
    'release_manifest.json': '90e522246d99322e574c33ec5a6378a6e35660eb1130079198a83313fda2c81f',
}
for name, digest in expected.items():
    require(sha((release / name).read_bytes()) == digest, name + ' identity')
require(result['bit_sha256'] == expected['flyvis_t5c_source_raw_v1.bit'] and result['hwh_sha256'] == expected['flyvis_t5c_source_raw_v1.hwh'], 'run firmware identity')

archive = base / ('V1_ROW0_EVIDENCE_' + uuid.uuid4().hex[:12] + '.zip')
inventory = []
with zipfile.ZipFile(str(archive), 'x', zipfile.ZIP_DEFLATED) as z:
    entries = [(p, 'run/' + p.relative_to(run).as_posix()) for p in sorted(run.rglob('*')) if p.is_file()]
    entries += [(release / name, 'release/' + name) for name in expected]
    for path, entry in entries:
        data = path.read_bytes()
        z.writestr(entry, data)
        inventory.append({'path': entry, 'bytes': len(data), 'sha256': sha(data)})
    seal = {
        'status': 'PASS_FILE_ONLY_SEALED_ROW0_EVIDENCE',
        'files': inventory, 'boot_id_of_run': result['boot_id'],
        'request_sha256': sha(request), 'pl_output_sha256': sha(output),
        'integer_matches': 67, 'returned_start_writes': len(starts),
        'host_completion_elapsed_s': report['host_completion_elapsed_s'],
        'timing_scope': 'HOST_COMPLETION_INCLUDING_EVIDENCE_IO_NOT_PURE_PL_CYCLES',
        'scientific_acceptance': 'NOT_GRANTED', 'true_closed_loop': False,
        'live_run_video_recorded': False,
        'selected_demo_input': {
            'name': '01_off_right.mp4',
            'sha256': '0ce06450d5c59da25157780197dd64f7080969331301371027406fcb6c69d880',
            'role': 'EXISTING_STIMULUS_FOR_RESULT_PRESENTATION; NOT_VIDEO_OF_THIS_BOARD_RUN',
            'included_in_archive': False,
        },
        'hardware_operations_by_this_cell': 0,
    }
    z.writestr('FINAL_SEAL.json', json.dumps(seal, indent=2))
with archive.open('rb') as f:
    os.fsync(f.fileno())
with zipfile.ZipFile(str(archive)) as z:
    for entry in inventory:
        require(sha(z.read(entry['path'])) == entry['sha256'], 'archive entry mismatch: ' + entry['path'])
print(json.dumps({k: v for k, v in seal.items() if k != 'files'}, indent=2))
print('ARCHIVE:', str(archive))
print('ARCHIVE_SHA256:', sha(archive.read_bytes()))
print('DOWNLOAD_THIS_ZIP_AND_RETURN_OUTPUT; NO_LOAD_START_RESET_OR_RETRY_PERFORMED')

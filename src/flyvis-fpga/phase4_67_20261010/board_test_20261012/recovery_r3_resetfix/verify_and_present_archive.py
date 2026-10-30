"""Verify received board evidence and make a labelled presentation video."""
from pathlib import Path
import hashlib, json, struct, zipfile, shutil
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent / 'sealed_v1_row0_b895835f9643'
ZIP = Path('C:/Users/hzy72/Downloads/V1_ROW0_EVIDENCE_b895835f9643.zip')
STIMULUS = Path('C:/Users/hzy72/Documents/ChatGPT/fly/camera_pipeline/controlled_video_20261010_r1/sources/01_off_right.mp4')
def sha(data): return hashlib.sha256(data).hexdigest()
def check(ok, message):
    if not ok: raise RuntimeError(message)

check(not OUT.exists(), 'Preserve existing output: choose a new directory')
data = ZIP.read_bytes()
check(sha(data) == 'b70fdd8e03d2cdea047fd5032820b5aa35fa0d08a0fee31c72a761cca395108d', 'ZIP identity')
with zipfile.ZipFile(ZIP) as z:
    names = z.namelist()
    check(len(names) == len(set(names)), 'Duplicate archive entries')
    for name in names:
        check(not name.startswith(('/', '\\')) and '..' not in Path(name).parts and ':' not in name and '\\' not in name, 'Unsafe archive path')
    seal = json.loads(z.read('FINAL_SEAL.json'))
    listed = seal['files']
    check(set(names) == {e['path'] for e in listed} | {'FINAL_SEAL.json'}, 'Archive inventory coverage')
    for e in listed:
        raw = z.read(e['path'])
        check(len(raw) == e['bytes'] and sha(raw) == e['sha256'], 'Inventory identity: ' + e['path'])
    result = json.loads(z.read('run/board_run.json'))
    report = json.loads(z.read('run/step0/step_report.json'))
    load = json.loads(z.read('run/load_result.json'))
    trace = [json.loads(s) for s in z.read('run/step0/register_trace.jsonl').decode().splitlines()]
    output = z.read('run/PL_output_i32le.bin')
    request = z.read('run/request_i32le.bin')
    check(sha(request) == 'ea1cb4a5f1d655183cad390ef0226ca138eb77d783f4edf271fb37711d9be8b4' and len(request) == 1498 * 4, 'Request identity')
    check(sha(output) == '50f212ffd6e47abebc8758b8c48999eb40957aabd0106b467ad4cc47a4f92a00' and len(output) == 67 * 4, 'Output identity')
    check(output == z.read('run/integer_oracle_i32le.bin') == z.read('run/step0/PL_candidate_i32le.bin'), 'Raw output/oracle')
    check(request == z.read('run/step0/request_i32le.bin'), 'Driver request identity')
    local_oracle = np.load(ROOT / 'phase3_20261010/testdata_animation_q22/oracle_q22.npy', allow_pickle=False)
    check(output == np.asarray(local_oracle[0], dtype='<i4').tobytes(), 'Independent local sealed row0 oracle')
    firmware = {
        'flyvis_t5c_source_raw_v1.bit': '23cf5da15db221f399b54cae95e341e6a90a699c88d321d0a883aecca15f7569',
        'flyvis_t5c_source_raw_v1.hwh': '3ea3f1e27c7b214e0f7a965455799875cbae94fb87bee6455a58ecbed4813f7d',
        'release_manifest.json': '90e522246d99322e574c33ec5a6378a6e35660eb1130079198a83313fda2c81f',
    }
    for name, digest in firmware.items(): check(sha(z.read('release/' + name)) == digest, name + ' identity')
    check(result['bit_sha256'] == load['bit_sha256'] == firmware['flyvis_t5c_source_raw_v1.bit'], 'Loaded BIT identity')
    check(result['hwh_sha256'] == load['hwh_sha256'] == firmware['flyvis_t5c_source_raw_v1.hwh'], 'Loaded HWH identity')
    check(result['load_result_sha256'] == sha(z.read('run/load_result.json')), 'Load record binding')
    check(result['boot_id'] == load['boot_id'] == seal['boot_id_of_run'] == '894292a3-1b60-4abf-aba3-e7b18b9e75c8', 'Boot identity')
    check(result['status'] == 'PASS_REAL_BOARD_ONE_STEP_INTEGER_ORACLE' and result['exact_integer_match'] and not result['mismatched_indices'], 'Board comparison status')
    check(not result['python_fallback'] and not result['committed'] and not result['true_closed_loop'], 'Evidence scope')
    check(report['completed'] and report['hls_status'] == 0, 'Driver status')
    writes = [e for e in trace if e['action'] == 'mmio_write_returned']
    intents = [e for e in trace if e['action'] == 'mmio_write_intent']
    check([(e['offset'], e['value']) for e in writes] == [(e['offset'], e['value']) for e in intents], 'Write intent/return pairing')
    starts = [e for e in writes if e['offset'] == 0]
    check(len(starts) == 1 and starts[0]['value'] == 1, 'Exactly one START')
    after_start = trace[trace.index(starts[0]) + 1:]
    check(any(e['action'] == 'mmio_read' and e['offset'] == 0 and e['value'] & 2 for e in after_start), 'DONE read after START')
    check(report['completion_ctrl'] == 14 and report['registers_after']['CTRL'] == 4, 'DONE and final IDLE')
    buffers = report['buffers']
    ia, oa = buffers['input_address'], buffers['output_address']
    check(buffers['input_bytes'] == 5992 and buffers['output_bytes'] == 268 and ia % 4 == oa % 4 == 0, 'DDR buffers')
    check(0x100000 <= ia < ia + 5992 <= 0x40000000 and 0x100000 <= oa < oa + 268 <= 0x40000000, 'DDR range')
    check(ia + 5992 <= oa or oa + 268 <= ia, 'DDR non-overlap')
    check(report['registers_after']['request_low'] == ia and report['registers_after']['result_low'] == oa, 'Pointer readback')
    check(report['registers_after']['request_high'] == report['registers_after']['result_high'] == 0, 'Pointer high words')
    console = z.read('run/row0_console.log').decode()
    values = struct.unpack('<67i', output)
    for i, value in enumerate(values):
        check(f'H[{i:02d}] PL={value} ORACLE={value} MATCH=True' in console, 'Console result binding')
    OUT.mkdir()
    for name in names:
        p = OUT / 'original_archive_contents' / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(z.read(name))
shutil.copyfile(ZIP, OUT / ZIP.name)

verification = {
    'status': 'PASS_INDEPENDENT_ARCHIVE_VERIFICATION_REAL_BOARD_ROW0_INTEGER',
    'provenance': 'User-operated physical-board run; archived runtime, MMIO trace and raw output independently inspected locally. Not cryptographic silicon attestation.',
    'archive_sha256': sha(data), 'verified_inventory_files': len(listed),
    'boot_id': result['boot_id'], 'firmware': firmware,
    'request_sha256': sha(request), 'pl_output_sha256': sha(output),
    'local_sealed_oracle_independent_comparison': '67/67 exact int32 codes',
    'returned_start_writes': 1, 'completion_ctrl': 14, 'final_ctrl': 4,
    'hls_status': 0, 'buffers': buffers, 'host_completion_elapsed_s': report['host_completion_elapsed_s'],
    'timing_scope': 'Host START/DONE completion including evidence I/O, not pure PL cycle latency',
    'scientific_acceptance': 'NOT_GRANTED', 'true_closed_loop': False,
    'live_board_run_video_recorded': False, 'hardware_operations_by_this_script': 0,
}
(OUT / 'ARCHIVE_VERIFICATION.json').write_text(json.dumps(verification, indent=2), encoding='utf-8')
(OUT / 'results_67.csv').write_text('index,pl_q22_i32,oracle_q22_i32,match\n' + ''.join(f'{i},{v},{v},true\n' for i,v in enumerate(values)), encoding='utf-8')

check(sha(STIMULUS.read_bytes()) == '0ce06450d5c59da25157780197dd64f7080969331301371027406fcb6c69d880', 'Stimulus identity')
cap = cv2.VideoCapture(str(STIMULUS))
frames = []
while True:
    ok, frame = cap.read()
    if not ok: break
    frames.append(frame)
cap.release()
check(len(frames) == 240, 'Stimulus frame count')
video = OUT / 'FlyVis67_V1_result_presentation_NOT_LIVE.mp4'
writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*'mp4v'), 30, (1280, 800))
check(writer.isOpened(), 'Video encoder')
def text(im, s, x, y, scale=.55, color=(210,220,230)):
    cv2.putText(im, s, (x,y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)
for k in range(300):
    im = np.full((800,1280,3), (24,20,16), dtype=np.uint8)
    text(im, 'FlyVis T5c67 | verified FPGA row0 result', 35,45,.9)
    text(im, 'PRESENTATION: existing input animation + archived board result',35,80,.6)
    text(im, 'Input replay: 01_off_right.mp4 (4 seconds)',35,130,.55)
    im[155:655,35:535] = cv2.resize(frames[(k * 2) % 240], (500,500))
    text(im, 'Archived ONE STEP: 67 / 67 exact integer matches',575,130,.57,(100,235,130))
    for i,v in enumerate(values):
        col, row = divmod(i,23)
        text(im, f'H[{i:02d}] {v:>8d} OK',575 + col*230,170 + row*20,.46,(140,235,165))
    text(im, '1364 raw boundary + 67 old_H + 67 x_H',35,690,.57)
    text(im, 'PL: 970 HH + 5567 RH edges; 67 candidate neuron updates',35,723,.57)
    text(im, 'Host completion: 18.999 ms (includes logging; not pure PL latency)',35,756,.54)
    text(im, 'Not live footage | No COMMIT | No 32/800 loop | Scientific precision pending',35,785,.5,(110,190,250))
    writer.write(im)
    if k == 0: cv2.imwrite(str(OUT / 'presentation_preview.jpg'), im)
writer.release()
cap = cv2.VideoCapture(str(video))
decoded = 0
while True:
    ok, frame = cap.read()
    if not ok: break
    check(frame.shape[:2] == (800,1280), 'Video decoded dimensions')
    decoded += 1
cap.release()
check(decoded == 300, 'Video decoded frames')
(OUT / 'PRESENTATION_MANIFEST.json').write_text(json.dumps({
    'role': 'Result presentation, not live board recording or closed-loop animation',
    'video_file': video.name, 'video_sha256': sha(video.read_bytes()),
    'fps': 30, 'frames': decoded, 'duration_s': 10,
    'stimulus_sha256': sha(STIMULUS.read_bytes()),
    'archived_output_sha256': sha(output), 'all_result_values_static_archived_row0': True,
}, indent=2), encoding='utf-8')
print(json.dumps(verification, indent=2))
print('VIDEO:', video)

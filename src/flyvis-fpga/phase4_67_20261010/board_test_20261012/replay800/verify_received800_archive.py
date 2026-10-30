"""Independently inspect user-operated physical board replay800 raw evidence."""
from pathlib import Path
import csv, hashlib, io, json, shutil, statistics, struct, zipfile
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = Path('C:/Users/hzy72/Downloads/V3_800_REQUEST_EVIDENCE_7c53b766f037.zip')
OUT = Path(__file__).parent / 'sealed_v3_800_7c53b766f037'
EXPECTED_ZIP = 'aba7b8a54b61dc421eca48045b77d040d5c8e0fc9b9e67187b05dc77045d6c79'
def sha(data): return hashlib.sha256(data).hexdigest()
def check(ok, message):
    if not ok: raise RuntimeError(message)

check(not OUT.exists(), 'Preserve existing evidence; choose another verification directory')
check(sha(ARCHIVE.read_bytes()) == EXPECTED_ZIP, 'Received ZIP identity')
timings, results, rows_verified = [], [], []
with zipfile.ZipFile(ARCHIVE) as z:
    names = z.namelist()
    check(len(names) == len(set(names)), 'Duplicate archive entries')
    for name in names:
        check(not name.startswith(('/', '\\')) and '..' not in Path(name).parts and ':' not in name and '\\' not in name, 'Unsafe archive path')
    seal = json.loads(z.read('FINAL_SEAL.json'))
    check(set(names) == {e['path'] for e in seal['files']} | {'FINAL_SEAL.json'}, 'Inventory coverage')
    for e in seal['files']:
        raw = z.read(e['path'])
        check(len(raw) == e['bytes'] and sha(raw) == e['sha256'], 'Inventory mismatch: ' + e['path'])
    check('run/FAIL_CLOSED.json' not in names, 'Fault record exists')
    plan_bytes = z.read('run/PREPARATION.json')
    check(sha(plan_bytes) == 'fc94b39e0a7f1820505c49e1ffb613a3cbdf7fc52ffe805c7f1a1f3c08998209', 'Approved plan identity')
    plan = json.loads(plan_bytes)
    receipt = json.loads(z.read('run/ATTEMPT_CONSUMED.json'))
    result = json.loads(z.read('run/board_run800.json'))
    check(receipt['authorization'] == 'AUTHORIZE_800_RECORDED_OLD_H_REQUESTS_ONCE_replay800_prepared_5c4f1d3336cb' and receipt['plan_sha256'] == sha(plan_bytes), 'Operation authorization binding')
    check(plan['boot_id'] == receipt['boot_id'] == result['boot_id'] == seal['boot_id_of_run'] == '894292a3-1b60-4abf-aba3-e7b18b9e75c8', 'Boot binding')
    check(plan['rows_first'] == 0 and plan['rows_last'] == 799 and plan['requests'] == result['requests_completed'] == seal['requests_completed'] == 800, 'Request scope')
    check(result['status'] == 'PASS_REAL_BOARD_800_REQUEST_REPLAY_INTEGER_ORACLE' and result['integer_matches'] == 53600, 'Board report status')
    check(not result['committed'] and not result['python_fallback'] and not result['true_closed_loop'] and result['pl_downloads_by_this_campaign'] == 0, 'Scope violation')
    firmware = {
        'flyvis_t5c_source_raw_v1.bit': '23cf5da15db221f399b54cae95e341e6a90a699c88d321d0a883aecca15f7569',
        'flyvis_t5c_source_raw_v1.hwh': '3ea3f1e27c7b214e0f7a965455799875cbae94fb87bee6455a58ecbed4813f7d',
        'release_manifest.json': '90e522246d99322e574c33ec5a6378a6e35660eb1130079198a83313fda2c81f',
    }
    for name,digest in firmware.items():
        check(sha(z.read('release/' + name)) == result['firmware'][name] == plan['firmware'][name] == digest, 'Firmware binding: ' + name)
    request = z.read('run/requests_800_i32le.bin')
    oracle = z.read('run/oracle_800_i32le.bin')
    output = z.read('run/PL_outputs_800_i32le.bin')
    check(len(request) == 4793600 and sha(request) == plan['request_sha256'] == result['request_sha256'] == 'dd996561a574a01e607fb727385fae2fa812530331024f149243ed68105f166c', 'Request bytes')
    check(len(output) == 214400 and output == oracle and sha(output) == result['pl_output_sha256'] == result['oracle_sha256'] == '1a1dd93416a310d292c2294a999d4c8d965b1887a8eb67d08b3a6b1249829665', '53600 raw output codes')
    vectors = ROOT / 'phase4_67_20261010/build/v1_resetfix_20261012_191002/vectors'
    local_requests = (vectors / 'requests_i32le.bin').read_bytes()
    check(sha(local_requests) == '12bd07ee49a40c9d92109463497eaf00b49db0d8ece75865e3a1d8907a3fecd2' and local_requests[:len(request)] == request, 'Independent local source requests')
    local_oracle = np.load(ROOT / 'phase3_20261010/testdata_animation_q22/oracle_q22.npy', allow_pickle=False)
    check(np.asarray(local_oracle[:800], dtype='<i4').tobytes() == output, 'Independent local integer oracle')
    mapping = list(csv.DictReader((vectors / 'request_map.csv').open()))[:800]
    check(all(int(r['request_id']) == i and int(r['step_id']) == i and r['condition_id'] == '01_off_right' for i,r in enumerate(mapping)), 'Actual animation row mapping')
    console = z.read('run/console.log').decode()
    check(console.count(' PASS 67/67;') == 800 and 'FAIL_CLOSED' not in console, 'Console campaign result')
    for row in range(800):
        prefix = f'run/step{row:04d}/'
        rep = json.loads(z.read(prefix + 'step_report.json'))
        comp = json.loads(z.read(f'run/ROW_{row:04d}_COMPARISON.json'))
        intent = json.loads(z.read(f'run/ROW_{row:04d}_INTENT.json'))
        trace = [json.loads(s) for s in z.read(prefix + 'register_trace.jsonl').decode().splitlines()]
        request_row, output_row = request[row*5992:(row+1)*5992], output[row*268:(row+1)*268]
        check(z.read(prefix + 'request_i32le.bin') == request_row and z.read(prefix + 'PL_candidate_i32le.bin') == output_row, 'Raw row binding')
        check(rep['request_sha256'] == comp['request_sha256'] == intent['request_sha256'] == sha(request_row), 'Request row SHA')
        check(rep['pl_output_sha256'] == comp['pl_output_sha256'] == comp['oracle_sha256'] == sha(output_row), 'Output row SHA')
        check(intent['row'] == comp['row'] == row and comp['matches'] == 67 and not comp['mismatched_indices'], 'Row comparison')
        check(rep['completed'] and rep['hls_status'] == 0 and rep['compute_owner'] == 'FPGA_PL_HLS' and not rep['buffers_pinned'] and not rep['python_fallback'] and not rep['committed'], 'Driver completion')
        check(rep['registers_before']['CTRL'] == 4 and rep['completion_ctrl'] == 14 and rep['registers_after']['CTRL'] == 4 and rep['registers_after']['ap_return'] == 0, 'Idle/DONE/status')
        writes = [e for e in trace if e['action'] == 'mmio_write_returned']
        intents = [e for e in trace if e['action'] == 'mmio_write_intent']
        check([(e['offset'],e['value']) for e in writes] == [(e['offset'],e['value']) for e in intents], 'Write intent/return pairing')
        check([e['offset'] for e in writes] == [24,28,36,40,0] and writes[-1]['value'] == 1, 'Only four pointer writes plus one START')
        after_start = trace[trace.index(writes[-1])+1:]
        check(any(e['action'] == 'mmio_read' and e['offset'] == 0 and e['value'] == 14 for e in after_start), 'DONE read after START')
        check(any(e['action'] == 'step_completed' and e['output_sha256'] == sha(output_row) for e in trace), 'Step completed trace')
        check(any(e['action'] == 'buffers_released_after_safe_completion_or_before_start' for e in trace) and not any(e['action'] == 'fail_closed' for e in trace), 'Safe completed buffer lifecycle')
        b = rep['buffers']; ia,oa = b['input_address'],b['output_address']
        check(b['input_bytes'] == 5992 and b['output_bytes'] == 268 and ia%4 == oa%4 == 0, 'Buffer sizes/alignment')
        check(0x100000 <= ia < ia+5992 <= 0x40000000 and 0x100000 <= oa < oa+268 <= 0x40000000 and (ia+5992 <= oa or oa+268 <= ia), 'DDR range/non-overlap')
        check(writes[0]['value'] == rep['registers_after']['request_low'] == ia and writes[2]['value'] == rep['registers_after']['result_low'] == oa, 'DDR pointer readback')
        check(writes[1]['value'] == writes[3]['value'] == rep['registers_after']['request_high'] == rep['registers_after']['result_high'] == 0, 'Pointer high words')
        t = rep['host_completion_elapsed_s']
        check(t == comp['host_completion_elapsed_s'] == result['host_completion_seconds'][row] and t > 0, 'Timing binding')
        check(f'ROW_{row:04d} PASS 67/67;' in console, 'Console row')
        timings.append(t)
        rows_verified.append({'row':row,'request_sha256':sha(request_row),'output_sha256':sha(output_row),'host_completion_s':t,'returned_start_writes':1,'hls_status':0})
        for i,v in enumerate(struct.unpack('<67i',output_row)):
            results.append((row,i,v,v,'true'))
    for e in json.loads(z.read('run/EXECUTION_FILES_MANIFEST.json')):
        check(sha(z.read('run/'+e['path'])) == e['sha256'], 'Original execution manifest')
    OUT.mkdir()
    for name in names:
        path = OUT / 'original_archive_contents' / name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(z.read(name))
shutil.copyfile(ARCHIVE,OUT / ARCHIVE.name)
verification = {
    'status':'PASS_INDEPENDENT_ARCHIVE_VERIFICATION_REAL_BOARD_800_REQUEST_REPLAY_INTEGER',
    'provenance':'User-operated physical-board run; raw files and MMIO traces independently inspected locally; not cryptographic silicon attestation',
    'archive_sha256':EXPECTED_ZIP,'verified_inventory_files':len(seal['files']),
    'requests_completed':800,'integer_matches':53600,'returned_start_writes':800,
    'all_done_ctrl':14,'all_final_ctrl':4,'all_hls_status':0,
    'boot_id':result['boot_id'],'firmware':firmware,
    'request_sha256':sha(request),'pl_output_sha256':sha(output),
    'local_request_and_oracle_independent_match':True,
    'campaign_elapsed_s':result['campaign_elapsed_s'],
    'host_completion_ms':{'min':min(timings)*1000,'mean':statistics.mean(timings)*1000,'max':max(timings)*1000},
    'timing_scope':'Host completion including evidence IO; not pure PL cycles or GPU/FPGA closed-loop timing',
    'true_closed_loop':False,'scientific_acceptance':'NOT_GRANTED',
    'pl_downloads_by_campaign':0,'hardware_operations_by_verifier':0,
    'live_board_video_provided':False,'rows':rows_verified,
}
(OUT / 'ARCHIVE_VERIFICATION.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
with (OUT / 'results_53600.csv').open('w',newline='') as f:
    w = csv.writer(f); w.writerow(['row','neuron_index','pl_q22_i32','oracle_q22_i32','match']); w.writerows(results)
with (OUT / 'timing_800.csv').open('w',newline='') as f:
    w = csv.writer(f); w.writerow(['row','host_completion_s']); w.writerows(enumerate(timings))
print(json.dumps({k:v for k,v in verification.items() if k!='rows'},indent=2))
print('SEALED_DIR:',OUT)

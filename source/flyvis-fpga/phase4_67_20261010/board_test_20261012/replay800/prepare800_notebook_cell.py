"""Prepared file-only800request selection; no PYNQ import or PL access.

Use the same kernel as V2. Do not execute any800request until fresh authorization.
"""
import csv, json, uuid
from pathlib import Path
previous800 = B32_BASE / 'replay32_prepared_14e89df951c2/board_run32.json'
b32_check(b32_sha(previous800.read_bytes()) == '472dca9c6713d19b4b8d6b1aab5ef0406cec61ec42a6e9e7e9232cbee34350d1', 'verified V2 record changed')
v2 = json.loads(previous800.read_text())
B800_BOOT = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
b32_check(v2['status'] == 'PASS_REAL_BOARD_32_REQUEST_REPLAY_INTEGER_ORACLE' and v2['requests_completed'] == 32 and v2['integer_matches'] == 2144, 'V2 acceptance')
b32_check(B800_BOOT == v2['boot_id'] == B32_BOOT, 'board rebooted; do not reload automatically')
B800_OVERLAY = B32_OVERLAY
B800_RELEASE, B800_BASE = B32_RELEASE, B32_BASE
B800_FIRMWARE, B800_SOFTWARE = dict(B32_FIRMWARE), dict(B32_SOFTWARE)
load800 = json.loads((B32_PREVIOUS / 'load_result.json').read_text())
b32_check(str(B800_OVERLAY.bitfile_name) == load800['bitfile_name'] and str(B800_OVERLAY.timestamp) == load800['timestamp'], 'existing overlay object changed')
for name,digest in B800_FIRMWARE.items():
    b32_check(b32_sha((B800_RELEASE / name).read_bytes()) == digest, 'firmware identity')
for name,digest in B800_SOFTWARE.items():
    b32_check(b32_sha((B800_RELEASE / 'pynq' / name).read_bytes()) == digest, 'driver identity')
requests800 = (B800_RELEASE / 'vectors/requests_i32le.bin').read_bytes()
oracle800 = (B800_RELEASE / 'vectors/expected_i32le.bin').read_bytes()
b32_check(b32_sha(requests800) == '12bd07ee49a40c9d92109463497eaf00b49db0d8ece75865e3a1d8907a3fecd2' and len(requests800) == 801*1498*4, 'full requests identity')
b32_check(b32_sha(oracle800) == '63de13ac8247125a6493fbe32c3454f780950a50f2c31362a7685e9def6581f8' and len(oracle800) == 801*67*4, 'full oracle identity')
requests800, oracle800 = requests800[:800*1498*4], oracle800[:800*67*4]
b32_check(b32_sha(requests800) == 'dd996561a574a01e607fb727385fae2fa812530331024f149243ed68105f166c', 'selected800requests')
b32_check(b32_sha(oracle800) == '1a1dd93416a310d292c2294a999d4c8d965b1887a8eb67d08b3a6b1249829665', 'selected800oracle')
with (B800_RELEASE / 'vectors/request_map.csv').open(newline='') as f:
    rows800 = list(csv.DictReader(f))[:800]
b32_check(len(rows800) == 800 and all(int(r['request_id']) == i and int(r['step_id']) == i and r['condition_id'] == '01_off_right' for i,r in enumerate(rows800)), '800actual animation rows')
B800_DIR = B800_BASE / ('replay800_prepared_' + uuid.uuid4().hex[:12])
B800_DIR.mkdir(exist_ok=False)
b32_write(B800_DIR / 'requests_800_i32le.bin',requests800)
b32_write(B800_DIR / 'oracle_800_i32le.bin',oracle800)
B800_PLAN = {
    'status':'READY_FILE_ONLY_AWAITING_EXACT_800_REQUEST_AUTHORIZATION',
    'boot_id':B800_BOOT,'rows_first':0,'rows_last':799,'requests':800,
    'condition_id':'01_off_right','expected_output_words':53600,
    'firmware':B800_FIRMWARE,'request_sha256':b32_sha(requests800),
    'oracle_sha256':b32_sha(oracle800),
    'prior_v2_record_sha256':b32_sha(previous800.read_bytes()),
    'state_semantics':'Recorded reference old_H each row; no PL output feedback',
    'true_closed_loop':False,'commit':False,'reload':False,'retry':False,
    'scientific_acceptance':'NOT_GRANTED','hardware_operations_by_this_cell':0,
    'session_dir':str(B800_DIR),
}
b32_json(B800_DIR / 'PREPARATION.json',B800_PLAN)
B800_PLAN_SHA = b32_sha((B800_DIR / 'PREPARATION.json').read_bytes())
B800_CONFIRM = ''
B800_REQUIRED = 'AUTHORIZE_800_RECORDED_OLD_H_REQUESTS_ONCE_' + B800_DIR.name
print(json.dumps(B800_PLAN,indent=2))
print('PLAN_SHA256:',B800_PLAN_SHA)
print('STOP_HERE: FILE_ONLY; RETURN_OUTPUT; NO800PLREQUESTAUTHORIZED')

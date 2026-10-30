"""File-only sealing of existing800request evidence. No PYNQ/MMIO access."""
from pathlib import Path
import hashlib, json, uuid, zipfile, os
from IPython.display import FileLink, display

base800 = Path('/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1/unpacked_resetfix_6d686a21b53a4303821311d7395becdd')
run800 = base800 / 'replay800_prepared_5c4f1d3336cb'
release800 = base800 / 'pynq_v1_resetfix_20261012_191002/release'
def sha800(data): return hashlib.sha256(data).hexdigest()
def check800(ok,why):
    if not ok: raise RuntimeError('STOP_FILE_SEAL: ' + why)

r800 = json.loads((run800 / 'board_run800.json').read_text())
check800(r800['status'] == 'PASS_REAL_BOARD_800_REQUEST_REPLAY_INTEGER_ORACLE' and r800['requests_completed'] == 800 and r800['integer_matches'] == 53600,'result status')
check800(r800['boot_id'] == '894292a3-1b60-4abf-aba3-e7b18b9e75c8','run boot identity')
check800(not r800['python_fallback'] and not r800['committed'] and not r800['true_closed_loop'] and r800['pl_downloads_by_this_campaign'] == 0,'operation scope')
check800(not (run800 / 'FAIL_CLOSED.json').exists(),'fault record exists')
check800(sha800((run800 / 'PREPARATION.json').read_bytes()) == 'fc94b39e0a7f1820505c49e1ffb613a3cbdf7fc52ffe805c7f1a1f3c08998209','plan identity')
request800 = (run800 / 'requests_800_i32le.bin').read_bytes()
oracle800 = (run800 / 'oracle_800_i32le.bin').read_bytes()
output800 = (run800 / 'PL_outputs_800_i32le.bin').read_bytes()
check800(len(request800) == 4793600 and sha800(request800) == 'dd996561a574a01e607fb727385fae2fa812530331024f149243ed68105f166c','request identity')
check800(len(output800) == 214400 and output800 == oracle800 and sha800(output800) == '1a1dd93416a310d292c2294a999d4c8d965b1887a8eb67d08b3a6b1249829665','53600output identity')
for row in range(800):
    step = run800 / ('step%04d' % row)
    rep = json.loads((step / 'step_report.json').read_text())
    comp = json.loads((run800 / ('ROW_%04d_COMPARISON.json' % row)).read_text())
    trace = [json.loads(s) for s in (step / 'register_trace.jsonl').read_text().splitlines()]
    starts = [e for e in trace if e['action'] == 'mmio_write_returned' and e['offset'] == 0]
    check800(len(starts) == 1 and starts[0]['value'] == 1,'START count row%d' % row)
    check800(rep['completed'] and rep['hls_status'] == 0 and rep['completion_ctrl'] & 2 and rep['registers_after']['CTRL'] == 4,'completion row%d' % row)
    check800(comp['row'] == row and comp['matches'] == 67 and not comp['mismatched_indices'],'comparison row%d' % row)
    check800((step / 'PL_candidate_i32le.bin').read_bytes() == output800[row*268:(row+1)*268],'raw output row%d' % row)
    check800((step / 'request_i32le.bin').read_bytes() == request800[row*5992:(row+1)*5992],'raw request row%d' % row)
    if (row+1) % 100 == 0: print('FILE_CHECK: %d/800' % (row+1),flush=True)

firmware800 = {
    'flyvis_t5c_source_raw_v1.bit':'23cf5da15db221f399b54cae95e341e6a90a699c88d321d0a883aecca15f7569',
    'flyvis_t5c_source_raw_v1.hwh':'3ea3f1e27c7b214e0f7a965455799875cbae94fb87bee6455a58ecbed4813f7d',
    'release_manifest.json':'90e522246d99322e574c33ec5a6378a6e35660eb1130079198a83313fda2c81f',
}
for name,digest in firmware800.items():
    check800(sha800((release800 / name).read_bytes()) == digest and r800['firmware'][name] == digest,'firmware identity: ' + name)
archive800 = base800 / ('V3_800_REQUEST_EVIDENCE_' + uuid.uuid4().hex[:12] + '.zip')
inventory800 = []
print('PACKING_EXISTING_FILES; NO_HARDWARE_OPERATIONS',flush=True)
with zipfile.ZipFile(str(archive800),'x',zipfile.ZIP_DEFLATED) as z:
    files = [(p,'run/'+p.relative_to(run800).as_posix()) for p in sorted(run800.rglob('*')) if p.is_file()]
    files += [(release800 / name,'release/'+name) for name in firmware800]
    for p,name in files:
        data = p.read_bytes(); z.writestr(name,data)
        inventory800.append({'path':name,'bytes':len(data),'sha256':sha800(data)})
    seal800 = {
        'status':'PASS_FILE_ONLY_800_REQUEST_EVIDENCE_ARCHIVED',
        'requests_completed':800,'integer_matches':53600,
        'boot_id_of_run':r800['boot_id'],'pl_output_sha256':sha800(output800),
        'campaign_elapsed_s':r800['campaign_elapsed_s'],
        'true_closed_loop':False,'scientific_acceptance':'NOT_GRANTED',
        'hardware_operations_by_this_cell':0,'files':inventory800,
    }
    z.writestr('FINAL_SEAL.json',json.dumps(seal800,indent=2))
with archive800.open('rb') as f: os.fsync(f.fileno())
with zipfile.ZipFile(str(archive800)) as z:
    for e in inventory800: check800(sha800(z.read(e['path'])) == e['sha256'],'ZIP entry: '+e['path'])
print(json.dumps({k:v for k,v in seal800.items() if k!='files'},indent=2))
print('ARCHIVE:',str(archive800))
print('ARCHIVE_SHA256:',sha800(archive800.read_bytes()))
display(FileLink(str(archive800.relative_to(Path('/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1')))))
print('FILE_ONLY_DONE; NO LOAD/START/RESET/RETRY')

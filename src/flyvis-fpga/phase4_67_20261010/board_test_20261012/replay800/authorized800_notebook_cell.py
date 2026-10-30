B800_CONFIRM = 'AUTHORIZE_800_RECORDED_OLD_H_REQUESTS_ONCE_replay800_prepared_5c4f1d3336cb'
"""Prepared, not authorized:800recordedold_H requests. No overlay download.

Requires the existing kernel and globals from prepare800_notebook_cell.py.
"""
import sys, time, statistics
b32_check(B800_DIR.name == 'replay800_prepared_5c4f1d3336cb', 'different800session')
b32_check(B800_BOOT == '894292a3-1b60-4abf-aba3-e7b18b9e75c8', 'different reviewed boot')
b32_check(b32_sha((B800_DIR / 'PREPARATION.json').read_bytes()) == 'fc94b39e0a7f1820505c49e1ffb613a3cbdf7fc52ffe805c7f1a1f3c08998209', 'reviewed800plan changed')
B800_PLAN = json.loads((B800_DIR / 'PREPARATION.json').read_text())
b32_check(B800_PLAN['requests'] == 800 and B800_PLAN['rows_first'] == 0 and B800_PLAN['rows_last'] == 799, 'request scope')
b32_check(B800_REQUIRED == 'AUTHORIZE_800_RECORDED_OLD_H_REQUESTS_ONCE_replay800_prepared_5c4f1d3336cb' and B800_CONFIRM == B800_REQUIRED, 'specific800request authorization missing')
b32_check(Path('/proc/sys/kernel/random/boot_id').read_text().strip() == B800_BOOT, 'boot changed')
b32_check(not (B800_DIR / 'ATTEMPT_CONSUMED.json').exists(), 'campaign already attempted; no retry')
prepared_req800 = (B800_DIR / 'requests_800_i32le.bin').read_bytes()
prepared_gold800 = (B800_DIR / 'oracle_800_i32le.bin').read_bytes()
b32_check(len(prepared_req800) == 4793600 and b32_sha(prepared_req800) == B800_PLAN['request_sha256'] == 'dd996561a574a01e607fb727385fae2fa812530331024f149243ed68105f166c', '800request identity')
b32_check(len(prepared_gold800) == 214400 and b32_sha(prepared_gold800) == B800_PLAN['oracle_sha256'] == '1a1dd93416a310d292c2294a999d4c8d965b1887a8eb67d08b3a6b1249829665', '800oracle identity')
B800_FIRMWARE = dict(B800_PLAN['firmware'])
for name,digest in B800_FIRMWARE.items():
    b32_check(b32_sha((B800_RELEASE / name).read_bytes()) == digest, 'firmware identity')
software800 = {
    'flyvis_v1_driver':'832352f8c4ba09cbe712f127cd59bb808fe1efec34722ea2369f3805632f5a50',
    'flyvis_v1_evidence_driver':'11ba472f6a97c83d213226ebe49868a1b3635fb80a10a9fb6ca519a4feedf6b8',
}
for name,digest in software800.items():
    source = B800_RELEASE / 'pynq' / (name + '.py')
    module = sys.modules.get(name)
    b32_check(b32_sha(source.read_bytes()) == digest and module is not None and Path(module.__file__).resolve() == source.resolve(), 'sealed driver module')
B800_DRIVER_MODULE = sys.modules['flyvis_v1_evidence_driver']
b32_check(not B800_DRIVER_MODULE.PINNED_UNCERTAIN_BUFFERS, 'uncertain buffers exist; stop')
b32_check(B800_OVERLAY.is_loaded(), 'runtime overlay changed; do not reload')
load800 = json.loads((B32_PREVIOUS / 'load_result.json').read_text())
b32_check(str(B800_OVERLAY.bitfile_name) == load800['bitfile_name'] and str(B800_OVERLAY.timestamp) == load800['timestamp'], 'runtime overlay identity')
ip800 = B800_OVERLAY.ip_dict.get('flyvis_h',{})
b32_check(ip800.get('type') == 'xilinx.com:hls:flyvis_t5c_source_raw:1.0' and int(ip800.get('phys_addr',-1)) == 0x43C00000 and int(ip800.get('addr_range',0)) == 0x10000, 'HLS ABI')
requests800 = np.frombuffer(prepared_req800,dtype='<i4').reshape(800,1498)
oracle800 = np.frombuffer(prepared_gold800,dtype='<i4').reshape(800,67)
b32_check(np.all(requests800 >= -(1<<28)) and np.all(requests800 < (1<<28)), 'Q22state range')
b32_json(B800_DIR / 'ATTEMPT_CONSUMED.json', {
    'authorization':B800_CONFIRM,'boot_id':B800_BOOT,
    'plan_sha256':b32_sha((B800_DIR / 'PREPARATION.json').read_bytes()),
    'scope':'UP_TO800REQUESTS_ROWS0TO799_ONCE; NO_RELOAD_RESET_RETRY_COMMIT_GPU',
})
from pynq import allocate
from pynq.mmio import MMIO
class B800EvidenceDriver(B800_DRIVER_MODULE.EvidenceStepDriver):
    def read(self,offset):
        self.event('mmio_read_intent',offset=offset)
        return super().read(offset)
    def save_report(self,report): b32_json(self.directory / 'step_report.json',report)
    def event(self,action,**fields):
        super().event(action,**fields)
        fd = os.open(str(self.directory),os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)
class B800Tee:
    def init__(self,target,stream): self.target,self.stream = target,stream
    def write(self,s):
        self.target.write(s); self.stream.write(s); self.flush(); return len(s)
    def flush(self):
        self.target.flush(); self.stream.flush(); os.fsync(self.stream.fileno())
console800 = (B800_DIR / 'console.log').open('x')
old_stdout800,old_stderr800 = sys.stdout,sys.stderr
sys.stdout,sys.stderr = B800Tee(old_stdout800,console800),B800Tee(old_stderr800,console800)
outputs800,timings800,completed800 = [],[],0
started800 = time.monotonic()
try:
    print('EVIDENCE_DIR:',str(B800_DIR),flush=True)
    b32_json(B800_DIR / 'FIRST_AXI_INTENT.json',{'base':'0x43C00000','boot_id':B800_BOOT})
    mmio800 = MMIO(0x43C00000,0x10000)
    for row800 in range(800):
        b32_check(Path('/proc/sys/kernel/random/boot_id').read_text().strip() == B800_BOOT,'boot changed mid-campaign')
        b32_json(B800_DIR / ('ROW_%04d_INTENT.json' % row800),{'row':row800,'request_sha256':b32_sha(requests800[row800].tobytes())})
        print('ROW_%04d_BEFORE_AXI_REQUEST' % row800,flush=True)
        driver800 = B800EvidenceDriver(B800_OVERLAY,mmio800,allocate,B800_DIR / ('step%04d' % row800))
        response800 = driver800.step(requests800[row800])
        candidate800 = response800['candidate_h_q22_i32']
        for name in ('request_i32le.bin','PL_candidate_i32le.bin'):
            with (driver800.directory / name).open('rb') as f: os.fsync(f.fileno())
        mismatches800 = np.flatnonzero(candidate800 != oracle800[row800]).tolist()
        t800 = response800['report']['host_completion_elapsed_s']
        b32_json(B800_DIR / ('ROW_%04d_COMPARISON.json' % row800), {
            'row':row800,'matches':67-len(mismatches800),'mismatched_indices':mismatches800,
            'request_sha256':b32_sha(requests800[row800].tobytes()),
            'pl_output_sha256':b32_sha(candidate800.tobytes()),
            'oracle_sha256':b32_sha(oracle800[row800].tobytes()),'host_completion_elapsed_s':t800,
        })
        b32_check(not mismatches800,'integer mismatch at row%d; stop before next request' % row800)
        outputs800.append(candidate800.copy()); timings800.append(t800); completed800 += 1
        print('ROW_%04d PASS 67/67; host_completion_s=%.9f' % (row800,t800),flush=True)
    raw_output800 = np.stack(outputs800).astype('<i4').tobytes()
    b32_write(B800_DIR / 'PL_outputs_800_i32le.bin',raw_output800)
    b32_check(b32_sha(raw_output800) == B800_PLAN['oracle_sha256'],'combined800output identity')
    result800 = {
        'status':'PASS_REAL_BOARD_800_REQUEST_REPLAY_INTEGER_ORACLE',
        'requests_completed':800,'integer_matches':53600,'boot_id':B800_BOOT,
        'firmware':B800_FIRMWARE,'request_sha256':B800_PLAN['request_sha256'],
        'pl_output_sha256':b32_sha(raw_output800),'oracle_sha256':B800_PLAN['oracle_sha256'],
        'host_completion_seconds':timings800,
        'host_completion_ms':{'min':min(timings800)*1000,'mean':statistics.mean(timings800)*1000,'max':max(timings800)*1000},
        'campaign_elapsed_s':time.monotonic()-started800,
        'timing_scope':'HOST INCLUDING EVIDENCE IO; NOT PURE PL LATENCY',
        'state_semantics':B800_PLAN['state_semantics'],'true_closed_loop':False,
        'committed':False,'python_fallback':False,'scientific_acceptance':'NOT_GRANTED',
        'pl_downloads_by_this_campaign':0,
    }
    b32_json(B800_DIR / 'board_run800.json',result800)
    print(json.dumps({k:v for k,v in result800.items() if k!='host_completion_seconds'},indent=2),flush=True)
except BaseException as error:
    b32_json(B800_DIR / 'FAIL_CLOSED.json',{
        'error':repr(error),'verified_requests_completed':completed800,
        'buffers_pinned':bool(B800_DRIVER_MODULE.PINNED_UNCERTAIN_BUFFERS),
        'retry':False,'recovery':'Keep kernel and power alive; return logs. No reload/reset/retry.',
    })
    print('FAIL_CLOSED; KEEP KERNEL AND POWER ALIVE; NO RETRY/RESET/RELOAD',flush=True)
    raise
finally:
    sys.stdout,sys.stderr = old_stdout800,old_stderr800
    console800.flush(); os.fsync(console800.fileno()); console800.close()
    inventory800 = [{'path':str(p.relative_to(B800_DIR)),'bytes':p.stat().st_size,'sha256':b32_sha(p.read_bytes())} for p in sorted(B800_DIR.rglob('*')) if p.is_file()]
    b32_json(B800_DIR / 'EXECUTION_FILES_MANIFEST.json',inventory800)
print('STOP_AFTER800; RETURN_FINAL_SUMMARY; NO_TRUE_CLOSED_LOOP_PERFORMED')
print('EVIDENCE_DIR:',str(B800_DIR))

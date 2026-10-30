"""Software-only driver checks using recorded xsim outputs, never a board.

The MMIO double performs no FlyVis arithmetic. It verifies upload bytes and
returns the already hashed actual RTL simulation output for the same request.
This verifies driver logic, not another hardware execution or live closed loop.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from pynq_candidate_driver import HardwareNotReady, SourceRawAxiDriver, quantize_request
from prepare_hls_fixtures import sha256

ROOT = Path(__file__).resolve().parent


class RecordedMmio:
    def init__(self, words, result, mode='ok'):
        self.words = words
        self.result = result.astype(np.int32).view(np.uint32)
        self.mode = mode
        self.reads = []
        self.writes = []
        self.upload = []
        self.started = False

    def write(self, address, value):
        self.writes.append((address, value))
        if self.mode == 'disconnect':
            raise OSError('simulated disconnected transport')
        if address == 0x20 and value == 1:
            self.upload = []
        elif address == 0x20 and value == 2:
            assert np.array_equal(np.asarray(self.upload, dtype=np.uint32).view(np.int32), self.words)
            self.started = True
        else:
            assert address == 0x1000 + 4*len(self.upload)
            self.upload.append(value)

    def read(self, address):
        self.reads.append(address)
        identity = {0: 0x46565333, 4: 0x0616141d, 8: 67, 12: 1364, 16: 6537,
                    20: 1498, 40: 0x04cc0571, 44: 1}
        if address in identity:
            return 0 if self.mode == 'wrong_identity' and address == 0 else identity[address]
        if address == 0x24:
            if self.mode == 'busy': return 1
            if not self.started or self.mode == 'timeout': return 0
            return 2 if self.mode == 'invalid_candidate' else 6
        if address == 0x1c: return 4 if self.mode == 'overflow' else 0
        if address == 0x18: return 26618
        if 0x4000 <= address < 0x410c:
            if self.mode == 'malformed_output' and address == 0x4000: return 0x40000000
            return int(self.result[(address-0x4000)//4])
        raise AssertionError(f'Unexpected register {address:#x}')


def main():
    raw = np.load(ROOT.parents[1]/'flyvis-circuit-selection/phase3_20261010/c_reference/SOURCE_RAW_step_io.npz', allow_pickle=False)
    inputs = np.fromfile(ROOT/'testdata_animation_q22/requests_i32le.bin', dtype='<i4').reshape(801,1498)
    pointer = json.loads((ROOT/'artifacts/LATEST_AXI_RUN.json').read_text())
    rtl_report_path = Path(pointer['report'])
    rtl_report = json.loads(rtl_report_path.read_text())
    dump = rtl_report_path.parent/'axi_animation_output.mem'
    declared = rtl_report['evidence_sha256']['artifacts\\axi_animation_output.mem']
    assert sha256(dump) == declared
    actual = np.asarray([int(s,16) for s in dump.read_text().splitlines()],dtype=np.uint32).view(np.int32).reshape(801,67)
    for k in range(800):
        words = quantize_request(raw['boundary_before'][k],raw['old_H'][k],raw['x_H'][k])
        assert np.array_equal(words,inputs[k])
        mmio = RecordedMmio(words,actual[k])
        driver = SourceRawAxiDriver(mmio,board_io_authorized=True,overlay_identity_verified=True)
        digest = hashlib.sha256(f'SOFTWARE_TEST_ONLY:{k}'.encode()).hexdigest()
        candidate = driver.compute_candidate(raw['boundary_before'][k],raw['old_H'][k],raw['x_H'][k],request_digest=digest)
        assert np.array_equal(candidate.new_h,(actual[k].astype(np.float64)/(1<<22)).astype(np.float32))
        assert candidate.request_digest == digest and candidate.compute_cycles == 26618
        assert candidate.chemical_diagnostic is None and candidate.committed is False
        assert not candidate.new_h.flags.writeable
        assert len(mmio.writes) == 1500
    kwargs = dict(boundary=raw['boundary_before'][0],old_h=raw['old_H'][0],x_h=raw['x_H'][0],request_digest='0'*64)
    failures = {}
    for mode in ['unauthorized','wrong_identity','busy','overflow','invalid_candidate','malformed_output','timeout','disconnect']:
        mmio = RecordedMmio(inputs[0],actual[0],mode)
        driver = SourceRawAxiDriver(mmio,board_io_authorized=mode!='unauthorized',overlay_identity_verified=True)
        try:
            driver.compute_candidate(**kwargs,timeout_s=0.03)
        except (HardwareNotReady,TimeoutError,OSError) as exc:
            failures[mode] = {'exception':type(exc).__name__,'writes':len(mmio.writes),'candidate_returned':False}
        else: raise AssertionError(f'Failure mode returned a candidate: {mode}')
        if mode in ['unauthorized','wrong_identity','busy']: assert len(mmio.writes)==0
        if mode in ['overflow','invalid_candidate','timeout','disconnect']: assert not any(0x4000<=r<0x410c for r in mmio.reads)
    mmio = RecordedMmio(inputs[0],actual[0])
    driver = SourceRawAxiDriver(mmio,board_io_authorized=True,overlay_identity_verified=True)
    driver.compute_candidate(**kwargs)
    before = len(mmio.writes)
    try: driver.compute_candidate(**kwargs)
    except HardwareNotReady: failures['duplicate']={'writes_added':len(mmio.writes)-before,'candidate_returned':False}
    else: raise AssertionError('Duplicate request accepted')
    assert len(mmio.writes)==before
    for value in [np.full(1364,np.nan),np.full(1364,64),np.zeros(3)]:
        try: quantize_request(value,raw['old_H'][0],raw['x_H'][0])
        except (ValueError,OverflowError): pass
        else: raise AssertionError('Invalid input accepted')
    report = {'status':'PASS_DRIVER_SOFTWARE_ONLY','evidence_level':'SOFTWARE_MMIO_TEST_DOUBLE_WITH_RECORDED_XSIM_OUTPUTS',
              'animation_uploads_checked':800,'driver_output_mismatches':0,'failure_controls':failures,
              'source_sha256':sha256(ROOT/'pynq_candidate_driver.py'),
              'rtl_output_source':str(dump),'rtl_output_sha256':sha256(dump),
              'board_connected':False,'board_io_operations':0,'live_PL_execution':False,
              'production_backend_ready':False,'notes':'Synthetic test digests; HRequest/COMMIT/chemical adapter review remains pending.'}
    (ROOT/'artifacts/DRIVER_SOFTWARE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__': main()

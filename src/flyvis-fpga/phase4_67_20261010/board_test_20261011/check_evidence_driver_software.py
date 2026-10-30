"""Fault-path checks with explicit MMIO/allocator substitutes; no PL compute.

The substitute copies sealed oracle words to model transport completion. This
is driver software evidence only and cannot establish FPGA numerical parity.
"""
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'pynq'))
import flyvis_v1_evidence_driver as module
from flyvis_v1_driver import FlyVisBoardFault


class MockBuffer(np.ndarray):
    def __new__(cls, shape, dtype, address):
        item = np.zeros(shape, dtype=dtype).view(cls)
        item.device_address = address
        item.freed = False
        return item

    def flush(self):
        pass

    def invalidate(self):
        pass

    def freebuffer(self):
        self.freed = True


class SoftwareStub:
    def init__(self, oracle, mode='success'):
        self.oracle = oracle
        self.mode = mode
        self.buffers = []
        self.registers = {0: 4, 16: 1 if mode == 'status_fault' else 0}
        self.launches = 0
        self.done_read = False

    def is_loaded(self):
        return self.mode != 'unloaded'

    def allocate(self, shape, dtype):
        if self.mode == 'allocation_fault' and self.buffers:
            raise RuntimeError('mock allocation failure')
        address = 0x38000000 + len(self.buffers) * 0x10000
        if self.mode == 'outside_ddr':
            address = 0x40000000
        buffer = MockBuffer(shape, dtype, address)
        self.buffers.append(buffer)
        return buffer

    def write(self, offset, value):
        if offset == 0:
            self.launches += 1
            if self.mode == 'start_bus_exception':
                raise RuntimeError('mock write return uncertain')
            # Explicit software completion substitute. No arithmetic/hardware.
            self.buffers[1][:] = self.oracle
        else:
            self.registers[offset] = value

    def read(self, offset):
        if offset == 0:
            if not self.launches:
                return 0 if self.mode == 'busy_before' else 0x84 if self.mode == 'auto_before' else 4
            if self.mode == 'timeout':
                return 0
            if self.mode == 'auto_after':
                return 0x80
            if not self.done_read:
                self.done_read = True
                return 6
            return 0 if self.mode == 'not_idle_after' else 4
        if offset == 24 and self.mode == 'pointer_fault':
            return 123
        return self.registers.get(offset, 0)


def main():
    fixture = ROOT / 'build/V1_20261010_210347/vectors'
    request = np.fromfile(str(fixture / 'requests_i32le.bin'), dtype='<i4').reshape(801,1498)[0].copy()
    oracle = np.fromfile(str(fixture / 'expected_i32le.bin'), dtype='<i4').reshape(801,67)[0].copy()
    stamp = time.strftime('%Y%m%d_%H%M%S')
    directory = ROOT / 'board_test_20261011' / ('MOCK_DRIVER_CHECK_' + stamp)
    directory.mkdir(exist_ok=False)
    results = []
    cases = ['success', 'timeout', 'status_fault', 'outside_ddr', 'pointer_fault',
             'unloaded', 'busy_before', 'auto_before', 'start_bus_exception',
             'not_idle_after', 'allocation_fault', 'auto_after', 'float_input',
             'overflow_input', 'wrong_shape']
    for case in cases:
        stub = SoftwareStub(oracle, case)
        driver = module.EvidenceStepDriver(stub, stub, stub.allocate, directory / case,
                                           timeout_seconds=0.003)
        values = request
        if case == 'float_input':
            values = request.astype(float)
        elif case == 'overflow_input':
            values = request.astype(np.int64)
            values[0] = 1 << 28
        elif case == 'wrong_shape':
            values = request[:-1]
        rejected = False
        try:
            response = driver.step(values)
        except (FlyVisBoardFault, RuntimeError):
            rejected = True
        assert rejected == (case != 'success'), case
        should_pin = case in ('timeout', 'start_bus_exception', 'not_idle_after', 'auto_after')
        if should_pin:
            assert stub.launches == 1 and len(stub.buffers) == 2, case
            assert all(not item.freed for item in stub.buffers), case
            assert any(item is stub.buffers[0] for item in module.PINNED_UNCERTAIN_BUFFERS), case
        else:
            assert all(item.freed for item in stub.buffers), case
        if case == 'success':
            assert np.array_equal(response['candidate_h_q22_i32'], oracle)
            assert response['report']['status'] == 'PL_STEP_COMPLETED_ORACLE_COMPARISON_PENDING'
            assert not response['report']['committed']
            try:
                driver.step(request)
                raise AssertionError('Second attempt was accepted')
            except FlyVisBoardFault:
                pass
            assert stub.launches == 1
        elif case not in ('timeout', 'status_fault', 'start_bus_exception', 'not_idle_after', 'auto_after'):
            assert stub.launches == 0, case
        if not driver.trace.closed:
            driver.trace.close()
        results.append({'case': case, 'software_check_pass': True,
                        'mock_start_count': stub.launches, 'buffers_pinned': should_pin})
    assert all(isinstance(buffer, MockBuffer) for buffer in module.PINNED_UNCERTAIN_BUFFERS)
    report = {'status': 'PASS_15_DRIVER_SOFTWARE_FAULT_PATHS_ONLY',
              'evidence_level': 'SOFTWARE_MMIO_ALLOCATOR_SUBSTITUTES_NO_PL_EXECUTION',
              'board_io_operations': 0, 'mock_output_source': 'sealed recorded integer oracle copied by substitute',
              'does_not_validate_hls_compute': True, 'cases': results}
    (directory / 'SOFTWARE_REPORT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    print('EVIDENCE_DIRECTORY:', str(directory))


if __name__ == '__main__':
    main()

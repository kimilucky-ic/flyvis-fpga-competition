"""Focused CPU mock checks; never import PYNQ, configure FPGA or infer neurons."""
import ast
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

import board_check as b
import flyvis_driver as d

ROOT = Path(__file__).resolve().parent


class MockMMIO:
    def init__(self, initial, expected):
        self.initial, self.expected = initial, expected
        self.reg = {0x30:d.N, 0x34:d.NE, 0x38:d.VERSION, 0x10:0, 0x14:0, 0x2c:0, 8:0}
        self.writes = []
        self.state = initial
        self.hang = False
        self.cycles = b.EXPECTED_CYCLES

    def read(self, address):
        if address == 0x3c:
            return struct.unpack_from('<I', self.state, self.reg[8] * 4)[0]
        return self.reg.get(address, 0)

    def write(self, address, value):
        self.writes.append((address, value))
        self.reg[address] = value
        if address == 0 and value == 2:
            self.state = self.initial
            self.reg.update({0x10:8, 0x14:0})
        if address == 0 and value == 1:
            self.state = self.expected
            self.reg.update({0x10:9 if self.hang else 8, 0x14:1,
                             0x1c:d.NE, 0x20:d.N, 0x18:self.cycles, 0x24:0})


class MockBackend:
    is_hardware = False

    def init__(self):
        self.mmio = MockMMIO((ROOT/'initial_state.bin').read_bytes(), (ROOT/'expected_state1.bin').read_bytes())
        self.downloads = 0
        self.prepares = 0
        self.ports = []
        self.mhz = 100.0

    def snapshot(self):
        return dict(pynq_version='2.7.0', machine='armv7l', device_tree_compatible='xlnx,zynq-7000',
                    own_pid=123, relevant_processes=[], listening_TCP_ports=self.ports,
                    current=dict(bitfile=dict(ok=True, value='old.bit'), ip_metadata=dict(ok=True, value=[])))

    def prepare(self):self.prepares += 1
    def download(self):self.downloads += 1
    def loaded(self):return True
    def clock(self):return self.mhz
    def driver(self):return d.FlyVisFull(self.mmio)


class PreparedFlow(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='line11_cpu_mock_')
        self.out = Path(self.temp.name)/'result'
        self.backend = MockBackend()

    def tearDown(self):
        path=Path(self.temp.name).resolve()
        self.assertEqual(path.parent,Path(tempfile.gettempdir()).resolve())
        self.assertTrue(path.name.startswith('line11_cpu_mock_'))
        self.temp.cleanup()

    def run_flow(self):
        return b.execute(ROOT, self.backend, self.out, exclusive=True, timeout=0)

    def test_offline_does_not_import_hardware(self):
        self.assertEqual(b.verify(ROOT)['board_operations'], 0)
        self.assertNotIn('pynq', sys.modules)

    def test_python38_syntax(self):
        for name in ['board_check.py','flyvis_driver.py','frame_stepper.py','snapshot_board.py']:
            ast.parse((ROOT/name).read_text(encoding='utf-8'), feature_version=(3,8))

    def test_full_initial_and_one_step(self):
        result = self.run_flow()
        self.assertEqual(result['status'], 'PASS_CPU_MOCK_ONE_STEP_FLOW')
        self.assertFalse(result['board_result'])
        self.assertEqual(result['state_words_checked'],45669)
        self.assertEqual(self.backend.downloads,1)
        self.assertEqual(self.backend.mmio.writes.count((0,1)),1)
        self.assertEqual(self.backend.mmio.writes.count((0,2)),1)
        self.assertEqual(len([a for a,v in self.backend.mmio.writes if 0x400<=a<0xf44]),721)
        self.assertEqual((self.out/'actual_state1.bin').read_bytes(),(ROOT/'expected_state1.bin').read_bytes())

    def test_no_exclusive_window_no_operations(self):
        with self.assertRaises(RuntimeError):
            b.execute(ROOT,self.backend,self.out)
        self.assertEqual(self.backend.downloads,0)
        self.assertFalse(self.out.exists())

    def test_occupied_board_stops_before_program(self):
        self.backend.ports=[5771]
        with self.assertRaises(RuntimeError):self.run_flow()
        self.assertEqual(self.backend.downloads,0)
        self.assertEqual(self.backend.mmio.writes,[])

    def test_wrong_clock_stops_before_register_writes(self):
        self.backend.mhz=150.0
        with self.assertRaises(RuntimeError):self.run_flow()
        self.assertEqual(self.backend.downloads,1)
        self.assertEqual(self.backend.mmio.writes,[])

    def test_wrong_identity_no_restore(self):
        self.backend.mmio.reg[0x38]=0
        with self.assertRaises(RuntimeError):self.run_flow()
        self.assertEqual(self.backend.mmio.writes,[])

    def test_initial_mismatch_no_step(self):
        bad=bytearray(self.backend.mmio.initial);bad[-1]^=1
        self.backend.mmio.initial=bytes(bad)
        with self.assertRaises(RuntimeError):self.run_flow()
        self.assertNotIn((0,1),self.backend.mmio.writes)

    def test_last_neuron_one_bit_error_detected(self):
        bad=bytearray(self.backend.mmio.expected);bad[-1]^=1
        self.backend.mmio.expected=bytes(bad)
        with self.assertRaises(RuntimeError):self.run_flow()
        report=json.loads((self.out/'state1_compare.json').read_text())
        self.assertEqual(report['mismatch_words'],1)
        self.assertEqual(report['first_mismatches'][0]['node'],45668)
        self.assertEqual(self.backend.mmio.writes.count((0,1)),1)
        self.assertEqual(self.backend.mmio.writes.count((0,2)),1)

    def test_timeout_no_retry_or_second_restore(self):
        self.backend.mmio.hang=True
        with self.assertRaises(TimeoutError):self.run_flow()
        self.assertEqual(self.backend.mmio.writes.count((0,1)),1)
        self.assertEqual(self.backend.mmio.writes.count((0,2)),1)
        report=json.loads((self.out/'result.json').read_text())
        self.assertEqual(report['transition_outcome'],'IN_DOUBT_DO_NOT_REPEAT_OR_RESET')

    def test_unexpected_cycles_fail_with_evidence(self):
        self.backend.mmio.cycles=123
        with self.assertRaises(RuntimeError):self.run_flow()
        self.assertTrue((self.out/'actual_state1.bin').exists())
        self.assertEqual(self.backend.mmio.writes.count((0,1)),1)

    def test_short_state_is_not_accepted(self):
        with self.assertRaises(RuntimeError):b.compare_state(bytes(4),(ROOT/'expected_state1.bin').read_bytes())


if __name__=='__main__':
    unittest.main(verbosity=2)

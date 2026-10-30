"""Candidate11 first-step entry; default is offline verification only.

Python3.8 compatible. PYNQ is imported only by an explicitly requested board
execution. No CPU neural computation, automatic retry, reset recovery or DMA.
"""
import argparse
import hashlib
import io
import json
import os
import platform
import runpy
import struct
import sys
import time
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

from flyvis_driver import FlyVisFull, N, NE, BASE, SPAN

BIT_SHA = 'a48924c80037a820e3241ad4582b0b982c939428b7fa029b558582d56da30b8f'
HWH_SHA = '9b9f1481a0a9e4e0bd58a2ca3fb23b9d12cee8427654af255aaab369bba630ca'
EXPECTED_CYCLES = 2201418


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def verify(root):
    root = Path(root).resolve()
    manifest = json.loads((root / 'release_manifest.json').read_text(encoding='utf-8'))
    required = {'flyvis_full.bit', 'flyvis_full.hwh', 'flyvis_driver.py', 'frame_stepper.py',
                'initial_state.bin', 'input_frame0.bin', 'expected_state1.bin',
                'snapshot_board.py', 'board_check.py', 'PROVENANCE.json'}
    if not required.issubset(manifest):
        raise ValueError('Required bundle files missing from manifest')
    for name, info in manifest.items():
        path = (root / name).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            raise ValueError('Manifest path escapes bundle: ' + name)
        if not path.is_file() or path.stat().st_size != info['bytes'] or digest(path.read_bytes()) != info['sha256']:
            raise ValueError('Bundle identity mismatch: ' + name)
    for name, expected in [('flyvis_full.bit', BIT_SHA), ('flyvis_full.hwh', HWH_SHA)]:
        if manifest[name]['sha256'] != expected:
            raise ValueError('Wrong frozen candidate: ' + name)
    for name, size in [('initial_state.bin', N * 4), ('expected_state1.bin', N * 4), ('input_frame0.bin', 721 * 4)]:
        if (root / name).stat().st_size != size:
            raise ValueError('Invalid full-network vector length: ' + name)
    hwh = ET.parse(str(root / 'flyvis_full.hwh')).getroot()
    info = hwh.find('SYSTEMINFO')
    if info is None or any(info.get(k) != v for k, v in
                           [('DEVICE', '7z020'), ('PACKAGE', 'clg400'), ('SPEEDGRADE', '-2')]):
        raise ValueError('Wrong HWH silicon target')
    ranges = [r for r in hwh.iter('MEMRANGE') if r.get('INSTANCE') == 'network']
    if len(ranges) != 1 or int(ranges[0].get('BASEVALUE'), 16) != BASE or int(ranges[0].get('HIGHVALUE'), 16) != BASE + SPAN - 1:
        raise ValueError('Wrong network AXI range')
    return dict(status='PASS_OFFLINE_BUNDLE_ONLY', files=len(manifest), board_operations=0,
                candidate='hole_pipeline_20261016/soc_r2', bit_sha256=BIT_SHA, hwh_sha256=HWH_SHA,
                expected_cycles=EXPECTED_CYCLES, expected_core_ms=22.01418)


def compare_state(actual, expected):
    if len(actual) != N * 4 or len(expected) != N * 4:
        raise RuntimeError('Incomplete full-network state payload')
    bad = []
    count = 0
    for node, (a, b) in enumerate(zip(struct.iter_unpack('<I', actual), struct.iter_unpack('<I', expected))):
        if a[0] != b[0]:
            count += 1
            if len(bad) < 16:
                bad.append(dict(node=node, actual_hex='%08x' % a[0], expected_hex='%08x' % b[0]))
    return dict(words=N, mismatch_words=count, first_mismatches=bad,
                actual_sha256=digest(actual), expected_sha256=digest(expected))


class PynqBackend:
    is_hardware = True
    def init__(self, root):
        # The caller must establish explicit execution intent before construction.
        import pynq
        from pynq import Overlay, MMIO
        from pynq.ps import Clocks
        self.root, self.Overlay, self.MMIO, self.Clocks = root, Overlay, MMIO, Clocks
        self.version = str(pynq.__version__)

    def snapshot(self):
        output = io.StringIO()
        with redirect_stdout(output):
            runpy.run_path(str(self.root / 'snapshot_board.py'), run_name='line11_snapshot')
        data = json.loads(output.getvalue())
        compatible = Path('/proc/device-tree/compatible').read_bytes().replace(b'\0', b',').decode('ascii', 'replace')
        data.update(pynq_version=self.version, machine=platform.machine(), device_tree_compatible=compatible)
        return data

    def prepare(self):
        self.overlay = self.Overlay(str(self.root / 'flyvis_full.bit'), download=False)
        matches = [x for x in self.overlay.ip_dict.values() if int(x.get('phys_addr', -1)) == BASE]
        if len(matches) != 1 or int(matches[0].get('addr_range', -1)) != SPAN:
            raise RuntimeError('PYNQ2.7 HWH parsing did not expose the expected network range; no load attempted')

    def download(self):
        # Overlay.download applies HWH clock settings and configures PL once.
        self.overlay.download()

    def loaded(self):
        return bool(self.overlay.is_loaded())

    def clock(self):
        return float(self.Clocks.fclk0_mhz)

    def driver(self):
        return FlyVisFull(self.MMIO(BASE, SPAN))


def preflight(snapshot):
    if not snapshot.get('pynq_version', '').startswith('2.7.'):
        raise RuntimeError('Current PYNQ differs from prepared2.7 runtime; stop before programming')
    if snapshot.get('machine') != 'armv7l' or 'xlnx,zynq-7000' not in snapshot.get('device_tree_compatible', ''):
        raise RuntimeError('Current machine is not the prepared Zynq7000 runtime')
    current = snapshot.get('current', {})
    if not current.get('bitfile', {}).get('ok') or not current.get('ip_metadata', {}).get('ok'):
        raise RuntimeError('Current overlay metadata could not be inspected')
    ports = set(snapshot.get('listening_TCP_ports', []))
    if ports.intersection({5771, 5772}):
        raise RuntimeError('Existing A3R1/service listener still present; release board ownership first')
    own = snapshot.get('own_pid')
    others = [p for p in snapshot.get('relevant_processes', []) if p.get('pid') != own and
              set(p.get('markers', [])).intersection({'ipykernel', 'flyvis', 'a3r1'})]
    if others:
        raise RuntimeError('Other notebook/FPGA-related processes remain; ownership is not exclusive')


def execute(root, backend, output, exclusive=False, timeout=5.0):
    if not exclusive:
        raise RuntimeError('An explicitly released exclusive board window is required')
    root, output = Path(root), Path(output)
    offline = verify(root)
    output.mkdir(parents=True, exist_ok=False)
    phase, hardware_action = 'PREFLIGHT', False
    real = backend is None or bool(getattr(backend, 'is_hardware', False))
    result = dict(status='NOT_COMPLETED', board_result=real,
                  evidence_level='PHYSICAL_BOARD' if real else 'CPU_MOCK_ONLY', candidate='hole_pipeline_20261016/soc_r2',
                  bit_sha256=BIT_SHA, hwh_sha256=HWH_SHA, board_family_source='user confirmed Leader ZYNQ7020',
                  physical_silk_independently_observed=False, automatic_retry=False, DMA=False)

    def event(name, **values):
        with (output / 'events.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps(dict(event=name, host_UTC=datetime.now(timezone.utc).isoformat(),
                                    monotonic_ns=time.monotonic_ns(), **values)) + '\n')
            f.flush()
            os.fsync(f.fileno())

    try:
        save(output / 'bundle_check.json', offline)
        if backend is None:
            backend = PynqBackend(root)
        snapshot = backend.snapshot()
        save(output / 'board_before.json', snapshot)
        preflight(snapshot)
        backend.prepare()
        phase = 'PROGRAM'
        event('PROGRAM_BEGIN')
        hardware_action = True
        backend.download()
        event('PROGRAM_RETURNED')
        if not backend.loaded():
            raise RuntimeError('PYNQ did not confirm this overlay loaded')
        clock = backend.clock()
        result['observed_FCLK0_MHz'] = clock
        if abs(clock - 100.0) > .01:
            raise RuntimeError('Observed clock differs from100MHz; no manual clock rewrite attempted')
        driver = backend.driver()  # read exact dimensions/version before writes
        phase = 'RESTORE'
        event('RESTORE_BEGIN')
        driver.restore(timeout=timeout)
        event('RESTORE_RETURNED')
        phase = 'INITIAL_READBACK'
        initial = driver.read_state_bits()
        (output / 'actual_initial.bin').write_bytes(initial)
        initial_check = compare_state(initial, (root / 'initial_state.bin').read_bytes())
        save(output / 'initial_compare.json', initial_check)
        if initial_check['mismatch_words']:
            raise RuntimeError('Restored full state differs from the frozen initial state')
        phase = 'INPUT'
        begin = time.monotonic_ns()
        driver.load_frame_bits((root / 'input_frame0.bin').read_bytes())
        input_ns = time.monotonic_ns() - begin
        phase = 'STEP'
        event('STEP_BEGIN', requested_steps=1)
        begin = time.monotonic_ns()
        info = driver.run_steps(1, timeout=timeout)
        step_wait_ns = time.monotonic_ns() - begin
        result['hardware_counters'] = info
        event('STEP_RETURNED', **info)
        phase = 'READBACK'
        begin = time.monotonic_ns()
        state = driver.read_state_bits()
        readback_ns = time.monotonic_ns() - begin
        (output / 'actual_state1.bin').write_bytes(state)
        comparison = compare_state(state, (root / 'expected_state1.bin').read_bytes())
        save(output / 'state1_compare.json', comparison)
        if comparison['mismatch_words']:
            raise RuntimeError('One-step full-state bit comparison failed')
        if info['completed_steps'] != 1 or info['last_cycles'] != EXPECTED_CYCLES:
            raise RuntimeError('Completed-step/cycle count differs from the frozen one-step contract')
        result.update(status='PASS_BOARD_ONE_STEP_ALL_STATES' if real else 'PASS_CPU_MOCK_ONE_STEP_FLOW', state_words_checked=N,
                      mismatch_words=0, full_network_edges=NE, completed_steps=1,
                      timing=dict(input_seconds=input_ns/1e9, step_call_seconds=step_wait_ns/1e9,
                                  readback_seconds=readback_ns/1e9,
                                  core_seconds_from_counter=info['last_cycles']/(clock*1e6)),
                      display_frames=0, display_hookup='NEXT_STAGE_NOT_RUN',
                      final_neural_state='post_step1 retained; no automatic restore/reload')
        event('VERIFICATION_PASS')
    except BaseException as exc:
        status = 'STOPPED_AFTER_HARDWARE_ACTION' if hardware_action else 'STOPPED_BEFORE_PROGRAM'
        result.update(status=status if real else 'CPU_MOCK_' + status,
                      failed_phase=phase, error=type(exc).__name__ + ': ' + str(exc),
                      transition_outcome='IN_DOUBT_DO_NOT_REPEAT_OR_RESET' if hardware_action else 'NO_PROGRAM_ATTEMPT')
        event('STOP', **{k: result[k] for k in ('status', 'failed_phase', 'error')})
        save(output / 'result.json', result)
        raise
    save(output / 'result.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true', help='actually configure PL and run one full-network step')
    parser.add_argument('--exclusive-board-window', action='store_true', help='operator has released this board for candidate11')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    if not args.execute:
        print(json.dumps(verify(root), indent=2))
        return
    if not args.exclusive_board_window:
        parser.error('--execute requires --exclusive-board-window; hardware has not been imported')
    # No background task or board access occurs until this explicit branch.
    output = root / ('board_result_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ'))
    print('Board results: ' + str(output), flush=True)
    result = execute(root, None, output, exclusive=True)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

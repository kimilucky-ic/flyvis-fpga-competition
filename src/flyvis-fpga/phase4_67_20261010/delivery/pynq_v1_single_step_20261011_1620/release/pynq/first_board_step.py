"""Reviewed first-load launcher: exactly row0 once, no COMMIT or fallback.

Do not execute before the human reviews the exact BIT/HWH and approves this
load plus one request. A review JSON records completed prechecks; it is not
human authorization by itself. This script has no automatic recovery.
"""
import argparse
import json
from pathlib import Path
import platform
import sys
import time
import traceback

import numpy as np
from flyvis_v1_driver import FlyVisBoardFault, load_release, verify_fixture, sha_file, sha_bytes
from flyvis_v1_evidence_driver import EvidenceStepDriver, PINNED_UNCERTAIN_BUFFERS


class ConsoleTee:
    def init__(self, original, stream):
        self.original, self.stream = original, stream

    def write(self, content):
        self.original.write(content)
        self.stream.write(content)
        self.stream.flush()
        return len(content)

    def flush(self):
        self.original.flush()
        self.stream.flush()


def review_before_load(args):
    manifest, bit, hwh = load_release(args.release_dir)
    requests, oracle, fixture = verify_fixture(args.release_dir, manifest)
    bit_sha, hwh_sha = sha_file(bit), sha_file(hwh)
    if (args.authorize_bit_sha256, args.authorize_hwh_sha256) != (bit_sha, hwh_sha):
        raise FlyVisBoardFault('Exact BIT/HWH authorization hashes do not match')
    if sha_file(args.board_review) != args.authorize_review_sha256:
        raise FlyVisBoardFault('Board review identity does not match the approved review')
    review = json.loads(args.board_review.read_text(encoding='utf-8'))
    required = {'status': 'FIRST_STEP_BOARD_PRECHECK_REVIEWED',
                'fpga_part': 'xc7z020clg400-2', 'power_verified': True,
                'boot_mode': 'SD_CARD', 'runtime_sources_reviewed': True,
                'hp0_width_bits': 64, 'ddr_preset_reviewed': True,
                'first_request_row': 0, 'request_count': 1,
                'commit_authorized': False, 'bit_sha256': bit_sha, 'hwh_sha256': hwh_sha,
                'release_manifest_sha256': sha_file(args.release_dir / 'release_manifest.json'),
                'fixture_comparison_id': fixture['comparison_id'],
                'request_sha256': sha_bytes(requests[0].tobytes()),
                'integer_oracle_sha256': sha_bytes(oracle[0].tobytes())}
    for field, value in required.items():
        if field not in review or review[field] != value:
            raise FlyVisBoardFault('Board precheck field is unresolved/mismatched: ' + field)
    for field in ('core_revision', 'carrier_revision', 'pynq_version', 'boot_id', 'video_reference'):
        if not isinstance(review.get(field), str) or not review[field].strip():
            raise FlyVisBoardFault('Board precheck field missing: ' + field)
    identities = review.get('software_sha256', {})
    for name in ('first_board_step.py', 'flyvis_v1_evidence_driver.py', 'flyvis_v1_driver.py'):
        if sha_file(Path(__file__).parent / name) != identities.get(name):
            raise FlyVisBoardFault('Reviewed software changed: ' + name)
    if platform.machine() not in ('armv7l', 'armv7', 'armv8l'):
        raise FlyVisBoardFault('This launcher must run on the reviewed Zynq-7000 Linux host')
    boot_id = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    if boot_id != review['boot_id']:
        raise FlyVisBoardFault('Board rebooted since the reviewed runtime snapshot')
    # Inspect installed package version without importing PYNQ or creating a device.
    import importlib.metadata as metadata
    if metadata.version('pynq') != review['pynq_version']:
        raise FlyVisBoardFault('Installed PYNQ version changed since precheck')
    return manifest, bit, hwh, requests[0].copy(), oracle[0].copy(), fixture, review


def execute_one(args):
    manifest, bit, hwh, request, oracle, fixture, review = review_before_load(args)
    directory = args.output_dir.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    report = {'status': 'FAIL_CLOSED', 'board_programming_attempted': False,
              'board_execution_proven': False, 'pl_readback_attestation': False,
              'request_row': 0, 'requested_steps': 1, 'committed': False,
              'python_fallback': False, 'fixture_comparison_id': fixture['comparison_id'],
              'scientific_acceptance': fixture['scientific_acceptance'],
              'state_semantics': 'recorded explicit old_H, single stateless candidate; not a true closed loop',
              'firmware_identity': {'bit_sha256': sha_file(bit), 'hwh_sha256': sha_file(hwh)},
              'software_sha256': dict(review['software_sha256']),
              'board_review_sha256': sha_file(args.board_review), 'board_review': review,
              'timestamp_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
              'platform': platform.platform(), 'python': sys.version}
    (directory / 'approved_board_review.json').write_bytes(args.board_review.read_bytes())
    (directory / 'release_manifest.json').write_bytes((args.release_dir / 'release_manifest.json').read_bytes())
    (directory / 'request_i32le.bin').write_bytes(request.tobytes())
    (directory / 'integer_oracle_i32le.bin').write_bytes(oracle.tobytes())
    report['request_sha256'] = sha_bytes(request.tobytes())
    report['integer_oracle_sha256'] = sha_bytes(oracle.tobytes())
    stage = 'PYNQ import and HWH metadata inspection'
    with (directory / 'console.log').open('x', encoding='utf-8') as console:
        original_stdout, original_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = ConsoleTee(sys.stdout, console), ConsoleTee(sys.stderr, console)
        try:
            print('FIRST_BOARD_LOAD_AND_SINGLE_STEP; REQUEST_ROW=0; COMMIT=False', flush=True)
            print('BIT_SHA256', report['firmware_identity']['bit_sha256'], flush=True)
            print('HWH_SHA256', report['firmware_identity']['hwh_sha256'], flush=True)
            from pynq import Overlay, allocate
            from pynq.mmio import MMIO
            overlay = Overlay(str(bit), download=False)
            ip = overlay.ip_dict.get('flyvis_h', {})
            if (ip.get('type') != 'xilinx.com:hls:flyvis_t5c_source_raw:1.0'
                    or int(ip.get('phys_addr', -1)) != 0x43C00000
                    or int(ip.get('addr_range', 0)) != 0x10000):
                raise FlyVisBoardFault('Parsed HWH IP type/address/range mismatch before load')
            report['ip_metadata'] = {key: ip[key] for key in ('type', 'phys_addr', 'addr_range')}
            stage = 'approved overlay download'
            report['board_programming_attempted'] = True
            (directory / 'board_run.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
            # No hardware-changing call occurs before the identity/precheck gate.
            print('PROGRAMMING_EXACT_REVIEWED_PL_OVERLAY', flush=True)
            overlay.download()
            if not overlay.is_loaded():
                raise FlyVisBoardFault('PYNQ did not record the requested overlay as loaded')
            report['overlay_runtime_identity'] = {'bitfile_name': str(overlay.bitfile_name),
                                                   'timestamp': str(overlay.timestamp),
                                                   'is_loaded': True}
            stage = 'one HLS request'
            mmio = MMIO(0x43C00000, 0x10000)
            driver = EvidenceStepDriver(overlay, mmio, allocate, directory / 'step0')
            response = driver.step(request)
            candidate = response['candidate_h_q22_i32']
            raw = candidate.tobytes()
            (directory / 'PL_output_i32le.bin').write_bytes(raw)
            report['pl_output_sha256'] = sha_bytes(raw)
            report['driver_trace_summary'] = response['report']
            report['exact_integer_match'] = bool(np.array_equal(candidate, oracle))
            report['mismatched_indices'] = np.flatnonzero(candidate != oracle).tolist()
            # Compare only after PL completion. Oracle is never sent as input.
            for index, (actual, expected) in enumerate(zip(candidate.tolist(), oracle.tolist())):
                print('H[{:02d}] PL={:d} ORACLE={:d} MATCH={}'.format(index, actual, expected, actual == expected))
            if not report['exact_integer_match']:
                raise FlyVisBoardFault('PL candidate differs from integer oracle')
            report['status'] = 'PASS_REAL_BOARD_ONE_STEP_INTEGER_ORACLE'
            report['board_execution_proven'] = True
            report['evidence_level'] = 'LIVE_PYNQ_PL_SINGLE_STEP_WITH_RAW_WORDS_AND_REGISTER_TRACE'
            report['video_status'] = 'USER_RECORDING_REFERENCE_PRESENT; VIDEO_FILE_REVIEW_AND_SHA_PENDING'
            print(report['status'], flush=True)
        except BaseException as exc:
            report['stage'] = stage
            report['error'] = '{}: {}'.format(type(exc).__name__, exc)
            report['buffers_pinned'] = bool(PINNED_UNCERTAIN_BUFFERS)
            traceback.print_exc()
            raise
        finally:
            (directory / 'board_run.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
            console.flush()
            sys.stdout, sys.stderr = original_stdout, original_stderr
            inventory = []
            for path in sorted(directory.rglob('*')):
                if path.is_file():
                    inventory.append({'path': str(path.relative_to(directory)), 'bytes': path.stat().st_size,
                                      'sha256': sha_file(path)})
            (directory / 'evidence_manifest.json').write_text(json.dumps(inventory, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-dir', type=Path, required=True)
    parser.add_argument('--board-review', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--authorize-bit-sha256', required=True)
    parser.add_argument('--authorize-hwh-sha256', required=True)
    parser.add_argument('--authorize-review-sha256', required=True)
    args = parser.parse_args()
    try:
        execute_one(args)
    except BaseException:
        traceback.print_exc()
        if PINNED_UNCERTAIN_BUFFERS:
            print('FAIL_CLOSED: DDR BUFFERS PINNED. KEEP PROCESS ALIVE. NO RETRY OR AUTOMATIC RESET.', flush=True)
            print('Recovery requires separate explicit authorization to stop the PL master.', flush=True)
            # Prevent normal CLI exit/KeyboardInterrupt from freeing memory
            # while the PL master may be active. Forced kill/power loss cannot
            # be prevented here and must not be treated as a safe recovery.
            while True:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    print('Buffers still pinned; keep process alive pending recovery approval.', flush=True)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

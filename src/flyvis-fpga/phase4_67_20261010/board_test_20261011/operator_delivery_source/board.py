"""Operator entry: file verification, read-only preflight, review, one PL step.

Importing this module does not import PYNQ, map registers, or load an overlay.
Only run-one can call the sealed first_board_step launcher. No retry/COMMIT.
"""
import argparse
import hashlib
import importlib.metadata as metadata
import json
import mmap
import os
from pathlib import Path
import platform
import struct
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parent
RELEASE = ROOT / 'release'
BIT_SHA = 'e45bbe0d7795ee835fb7486444199460733196373ea4f363a8ff1c93431b7383'
HWH_SHA = 'fb40c671c06f41923e4cd41cff055c0b549e2db69bbfcee05810960a95885d82'
RELEASE_SHA = '54a40c9951388ccb4e6d4cc89da7c0f93f039cdf14b247dfb4278ba3d4def9c6'
CONFIRM = 'LOAD_REVIEWED_V1_AND_RUN_ROW0_ONCE'
BOOT_ID = Path('/proc/sys/kernel/random/boot_id')
FPGA_RST_CTRL = 0xF8000240
HP0_RD = 0xF8008000
HP0_WR = 0xF8008014
# Conservatively reject every legacy AXI/internal reset bit. Current UG585
# marks several of these reserved/always-write-zero; this tool NEVER writes.
AXI_RESET_MASK = 0x01F33F00
ARM_HOSTS = ('armv7l', 'armv7', 'armv8l')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def save_json(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def new_directory(kind):
    result = ROOT / 'evidence' / ('{}_{}_{}'.format(
        kind, time.strftime('%Y%m%d_%H%M%S'), uuid.uuid4().hex[:8]))
    result.mkdir(parents=True, exist_ok=False)
    return result


def verify_package():
    package = read_json(ROOT / 'package_manifest.json')
    checked = []
    for entry in package['files']:
        relative = Path(entry['path'])
        target = (ROOT / relative).resolve()
        if relative.is_absolute() or ROOT not in target.parents:
            raise ValueError('Package path escapes delivery: ' + str(relative))
        if not target.is_file() or target.stat().st_size != entry['bytes'] or sha(target) != entry['sha256']:
            raise ValueError('Delivery file identity changed: ' + str(relative))
        checked.append(entry['path'])
    for target, expected in (
        (RELEASE / 'release_manifest.json', RELEASE_SHA),
        (RELEASE / 'flyvis_t5c_source_raw_v1.bit', BIT_SHA),
        (RELEASE / 'flyvis_t5c_source_raw_v1.hwh', HWH_SHA),
    ):
        if sha(target) != expected:
            raise ValueError('Sealed V1 identity differs: ' + str(target))
    return {'status': 'PASS_FILE_ONLY_DELIVERY_IDENTITIES',
            'checked_files': len(checked), 'files': checked,
            'bit_sha256': BIT_SHA, 'hwh_sha256': HWH_SHA,
            'release_manifest_sha256': RELEASE_SHA,
            'package_manifest_sha256': sha(ROOT / 'package_manifest.json'),
            'board_execution_proven': False, 'board_register_reads': 0}


def read_ps_word(address):
    """Only a reviewed PS register, O_RDONLY mapping; never HLS/PL access."""
    if platform.system() != 'Linux' or platform.machine() not in ARM_HOSTS:
        raise RuntimeError('PS reads require the Zynq-7000 Linux host')
    if address not in (FPGA_RST_CTRL, HP0_RD, HP0_WR):
        raise ValueError('Address is outside the PS read-only allowlist')
    page = address & ~(mmap.PAGESIZE - 1)
    fd = os.open('/dev/mem', os.O_RDONLY | os.O_SYNC)
    try:
        with mmap.mmap(fd, mmap.PAGESIZE, access=mmap.ACCESS_READ, offset=page) as mapped:
            return struct.unpack_from('<I', mapped, address - page)[0]
    finally:
        os.close(fd)


def hp0_snapshot(reader=read_ps_word):
    result = {'status': 'PENDING', 'timestamp_utc': utc(),
              'board_register_writes': 0, 'reads': [],
              'reset_precondition_mask': '0x{:08x}'.format(AXI_RESET_MASK),
              'scope': 'PS FPGA_RST_CTRL then HP0 width registers; no PL registers'}
    try:
        reset = reader(FPGA_RST_CTRL)
        result['reads'].append({'address': '0xf8000240', 'value': reset})
        if reset & AXI_RESET_MASK:
            result['status'] = 'PENDING_RESET_PRECONDITION; HP0_NOT_READ'
            return result
        rd, wr = reader(HP0_RD), reader(HP0_WR)
        result['reads'].extend([{'address': '0xf8008000', 'value': rd},
                                {'address': '0xf8008014', 'value': wr}])
        after = reader(FPGA_RST_CTRL)
        result['reads'].append({'address': '0xf8000240', 'value': after})
        if after != reset:
            raise RuntimeError('PS reset register changed during read-only precheck')
        result['read_width_bits'] = 32 if rd & 1 else 64
        result['write_width_bits'] = 32 if wr & 1 else 64
        result['status'] = ('READ_ONLY_HP0_64BIT_OBSERVED' if not (rd | wr) & 1
                            else 'BLOCKED_HP0_WIDTH_MISMATCH')
    except (OSError, RuntimeError, ValueError) as exc:
        result['error'] = '{}: {}'.format(type(exc).__name__, exc)
    return result


def inspect_runtime():
    sys.path.insert(0, str(ROOT / 'tools'))
    from read_only_board_probe import inspect_board
    snapshot = inspect_board()
    snapshot['machine'] = platform.machine()
    snapshot['python_supported'] = sys.version_info >= (3, 8)
    try:
        snapshot['numpy_version'] = metadata.version('numpy')
    except metadata.PackageNotFoundError:
        snapshot['numpy_version'] = None
    return snapshot


def validate_runtime(snapshot):
    if snapshot.get('machine') not in ARM_HOSTS or not snapshot.get('python_supported'):
        raise ValueError('Need Zynq-7000 ARM Linux and Python >=3.8; no automatic installation')
    if not snapshot.get('numpy_version') or not snapshot['pynq'].get('version'):
        raise ValueError('PYNQ/NumPy not registered in this Python environment')
    compatibility = snapshot['files'].get('/sys/firmware/devicetree/base/compatible', '')
    if not isinstance(compatibility, str) or 'xlnx,zynq-7000' not in compatibility:
        raise ValueError('Device-tree Zynq-7000 identity unresolved')
    for name in ('pynq/overlay.py', 'pynq/bitstream.py',
                 'pynq/pl_server/embedded_device.py', 'pynq/buffer.py'):
        if not snapshot['pynq'].get('source_files', {}).get(name):
            raise ValueError('Runtime source inspection unavailable: ' + name)
    boot = snapshot['files'].get(str(BOOT_ID))
    if not isinstance(boot, str) or not boot.strip():
        raise ValueError('Live boot identity unavailable')


def require_current_runtime(previous):
    current = inspect_runtime()
    validate_runtime(current)
    for field in ('machine', 'numpy_version'):
        if current[field] != previous[field]:
            raise ValueError('Runtime changed since preflight: ' + field)
    if current['files'][str(BOOT_ID)] != previous['files'][str(BOOT_ID)]:
        raise ValueError('Board rebooted since preflight; review again')
    if current['pynq']['version'] != previous['pynq']['version']:
        raise ValueError('PYNQ changed since preflight')
    old_sources = previous['pynq']['source_files']
    sources = current['pynq']['source_files']
    if set(sources) != set(old_sources):
        raise ValueError('Installed PYNQ source inventory changed')
    for name, old in old_sources.items():
        if sources[name]['sha256'] != old['sha256']:
            raise ValueError('Installed PYNQ source changed: ' + name)
    return current


def require_hp0(snapshot):
    if snapshot.get('status') != 'READ_ONLY_HP0_64BIT_OBSERVED':
        raise ValueError('HP0 precheck unresolved: ' + snapshot.get('status', 'UNKNOWN'))
    if snapshot.get('read_width_bits') != 64 or snapshot.get('write_width_bits') != 64:
        raise ValueError('HP0 must be 64-bit in both directions')


def preflight(args):
    identity = verify_package()
    directory = args.output_dir.resolve() if args.output_dir else new_directory('preflight')
    if args.output_dir:
        directory.mkdir(parents=True, exist_ok=False)
    save_json(directory / 'package_identity.json', identity)
    snapshot = inspect_runtime()
    save_json(directory / 'runtime_snapshot.json', snapshot)
    hp0 = ({'status': 'PENDING_OS_ONLY_NO_REGISTER_READS', 'board_register_writes': 0,
            'reads': []} if args.os_only else hp0_snapshot())
    save_json(directory / 'hp0_readonly.json', hp0)
    unresolved = []
    try:
        validate_runtime(snapshot)
        require_hp0(hp0)
    except ValueError as exc:
        unresolved.append(str(exc))
    summary = {'status': 'PREFLIGHT_COLLECTED_HUMAN_REVIEW_PENDING',
               'timestamp_utc': utc(), 'directory': str(directory),
               'package_identity': identity, 'pynq_version': snapshot['pynq'].get('version'),
               'python': snapshot['python'], 'numpy_version': snapshot['numpy_version'],
               'boot_id': snapshot['files'].get(str(BOOT_ID)), 'hp0': hp0,
               'unresolved_machine_checks': unresolved,
               'board_execution_proven': False, 'pl_downloads': 0, 'board_register_writes': 0,
               'human_review_pending': ['board/core version, part and DDR',
                                        'power, SD boot and exclusive use',
                                        'installed PYNQ load/clock/buffer behavior',
                                        'unedited video reference and exact one-step approval']}
    save_json(directory / 'preflight_summary.json', summary)
    config = {'core_revision': None, 'carrier_revision': None,
              'fpga_part': None, 'physical_ddr_marking': None,
              'power_verified': None, 'boot_mode': None,
              'exclusive_board_use': None, 'ddr_preset_reviewed': None,
              'runtime_sources_reviewed': None, 'reviewer': None, 'video_reference': None}
    save_json(directory / 'operator_config.json', config)
    print(json.dumps({k: v for k, v in summary.items() if k != 'package_identity'},
                     ensure_ascii=False, indent=2))
    print('PREFLIGHT_DIR:', directory)
    print('First action complete. Send preflight_summary.json + runtime_snapshot.json + hp0_readonly.json for review.')
    return 0


def check_operator_config(config):
    for field in ('core_revision', 'carrier_revision', 'physical_ddr_marking',
                  'reviewer', 'video_reference'):
        if not isinstance(config.get(field), str) or not config[field].strip():
            raise ValueError('Operator fact/review missing: ' + field)
    if config.get('fpga_part') != 'xc7z020clg400-2' or config.get('boot_mode') != 'SD_CARD':
        raise ValueError('Wrong/unresolved FPGA part or boot mode')
    for field in ('power_verified', 'exclusive_board_use', 'ddr_preset_reviewed', 'runtime_sources_reviewed'):
        if config.get(field) is not True:
            raise ValueError('Operator has not completed review: ' + field)


def review(args):
    identity = verify_package()
    directory = args.preflight_dir.resolve()
    config_path = args.config.resolve() if args.config else directory / 'operator_config.json'
    config = read_json(config_path)
    check_operator_config(config)
    snapshot_path = directory / 'runtime_snapshot.json'
    previous = read_json(snapshot_path)
    require_current_runtime(previous)
    require_hp0(read_json(directory / 'hp0_readonly.json'))
    current_hp0 = hp0_snapshot()
    require_hp0(current_hp0)
    sys.path.insert(0, str(RELEASE / 'pynq'))
    from flyvis_v1_driver import load_release, verify_fixture, sha_bytes
    manifest, bit, hwh = load_release(RELEASE)
    requests, oracle, fixture = verify_fixture(RELEASE, manifest)
    result = dict(config)
    result.update({'status': 'FIRST_STEP_BOARD_PRECHECK_REVIEWED',
                   'pynq_version': previous['pynq']['version'],
                   'boot_id': previous['files'][str(BOOT_ID)],
                   'runtime_snapshot_sha256': sha(snapshot_path),
                   'runtime_snapshot_file': str(snapshot_path),
                   'hp0_width_bits': 64, 'hp0_read_width_bits': 64, 'hp0_write_width_bits': 64,
                   'hp0_register_readback_evidence': current_hp0,
                   'first_request_row': 0, 'request_count': 1, 'commit_authorized': False,
                   'bit_sha256': BIT_SHA, 'hwh_sha256': HWH_SHA,
                   'release_manifest_sha256': RELEASE_SHA,
                   'fixture_comparison_id': fixture['comparison_id'],
                   'request_sha256': sha_bytes(requests[0].tobytes()),
                   'integer_oracle_sha256': sha_bytes(oracle[0].tobytes()),
                   'software_sha256': {name: sha(RELEASE / 'pynq' / name)
                                       for name in manifest['first_step_software']},
                   'operator_config_sha256': sha(config_path),
                   'package_manifest_sha256': identity['package_manifest_sha256'],
                   'physical_board_facts_source': 'USER_REPORTED; NOT_REMOTE_PHYSICAL_ATTESTATION',
                   'runtime_review_source': 'EXPLICIT_HUMAN_SOURCE_REVIEW_ASSERTION',
                   'timestamp_utc': utc(), 'human_load_authorization': 'PENDING_RUN_ONE_CONFIRMATION'})
    review_path = directory / 'board_review.json'
    save_json(review_path, result)
    save_json(directory / 'review_receipt.json', {'board_review_sha256': sha(review_path),
                                               'package_manifest_sha256': identity['package_manifest_sha256']})
    print('BOARD_REVIEW:', review_path)
    print('BOARD_REVIEW_SHA256:', sha(review_path))
    print('BIT_SHA256:', BIT_SHA)
    print('HWH_SHA256:', HWH_SHA)
    print('ONE OPERATION: replace PL overlay, configure its FCLK0, allocate DDR, start row0 once; no COMMIT.')
    print('RISK: existing PL work stops; unknown active masters/boot HP0 mismatch can corrupt data.')
    print('FAULT: stop; do not reload/reset/retry/kill a process with uncertain pinned buffers.')
    print('AFTER EXACT USER APPROVAL AND STARTING VIDEO, manually run:')
    print('{} board.py run-one --preflight-dir "{}" --confirm {}'.format(sys.executable, directory, CONFIRM))
    return 0


def run_one(args):
    if args.confirm != CONFIRM:
        raise ValueError('Exact load plus row0-only confirmation missing; no board write')
    identity = verify_package()
    directory = args.preflight_dir.resolve()
    if (directory / 'ONE_ATTEMPT_CONSUMED.json').exists():
        raise ValueError('This reviewed session already consumed its one attempt; no retry')
    review_path = directory / 'board_review.json'
    receipt = read_json(directory / 'review_receipt.json')
    reviewed = read_json(review_path)
    if sha(review_path) != receipt['board_review_sha256']:
        raise ValueError('Reviewed JSON changed; no board write')
    if identity['package_manifest_sha256'] != receipt['package_manifest_sha256']:
        raise ValueError('Reviewed delivery package changed; no board write')
    snapshot_path = directory / 'runtime_snapshot.json'
    if sha(snapshot_path) != reviewed['runtime_snapshot_sha256']:
        raise ValueError('Reviewed runtime snapshot changed; no board write')
    require_current_runtime(read_json(snapshot_path))
    hp0 = hp0_snapshot()
    require_hp0(hp0)
    # One persistent token per reviewed session; no loop or automatic retry.
    # Written before calling the launcher, including failures before download.
    output = new_directory('one_step')
    save_json(directory / 'ONE_ATTEMPT_CONSUMED.json', {
        'timestamp_utc': utc(), 'manual_confirmation': args.confirm,
        'board_review_sha256': receipt['board_review_sha256'],
        'bit_sha256': BIT_SHA, 'hwh_sha256': HWH_SHA, 'output_directory': str(output),
        'scope': 'EXACT_OVERLAY_LOAD_AND_ROW0_ONCE_NO_COMMIT',
        'fresh_readonly_hp0': hp0})
    # Sealed execute_one creates its own new result directory. Keep the parent
    # as the attempt container rather than rewriting the sealed launcher.
    save_json(output / 'attempt_identity.json', read_json(directory / 'ONE_ATTEMPT_CONSUMED.json'))
    sys.path.insert(0, str(RELEASE / 'pynq'))
    import first_board_step
    original_argv = sys.argv
    sys.argv = [str(RELEASE / 'pynq' / 'first_board_step.py'),
                '--release-dir', str(RELEASE), '--board-review', str(review_path),
                '--output-dir', str(output / 'run'),
                '--authorize-bit-sha256', BIT_SHA, '--authorize-hwh-sha256', HWH_SHA,
                '--authorize-review-sha256', receipt['board_review_sha256']]
    print('EVIDENCE_DIR:', output, flush=True)
    try:
        # Same process: do not spawn a short-lived child that could release
        # DDR buffers after an uncertain HLS start. main() pins and stays alive.
        return first_board_step.main()
    finally:
        sys.argv = original_argv


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('verify', help='File-only package identity verification')
    p = sub.add_parser('preflight', help='Read Linux/PYNQ files and guarded PS registers; no writes')
    p.add_argument('--output-dir', type=Path)
    p.add_argument('--os-only', action='store_true', help='Skip all register reads (review remains pending)')
    p = sub.add_parser('review', help='Bind explicit operator facts and read-only observations; no loading')
    p.add_argument('--preflight-dir', type=Path, required=True)
    p.add_argument('--config', type=Path)
    p = sub.add_parser('run-one', help='Only after exact approval: load sealed overlay and row0 once')
    p.add_argument('--preflight-dir', type=Path, required=True)
    p.add_argument('--confirm', required=True)
    args = parser.parse_args(argv)
    if args.command == 'verify':
        print(json.dumps(verify_package(), indent=2))
        return 0
    return {'preflight': preflight, 'review': review, 'run-one': run_one}[args.command](args)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, RuntimeError, KeyError, ImportError) as error:
        print('FAIL_CLOSED:', '{}: {}'.format(type(error).__name__, error), file=sys.stderr, flush=True)
        raise SystemExit(1)

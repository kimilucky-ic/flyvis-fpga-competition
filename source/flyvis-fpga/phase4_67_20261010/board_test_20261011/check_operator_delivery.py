"""Local file-only delivery checks with explicit substitutes; no board proof."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import zipfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--delivery-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    delivery, output = args.delivery_dir.resolve(), args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    checks = []
    def check(name, function):
        function()
        checks.append({'name': name, 'status': 'PASS_SOFTWARE_ONLY'})
    def equal(actual, expected):
        if actual != expected:
            raise AssertionError('{} != {}'.format(actual, expected))
    def reject(function, contains):
        try:
            function()
        except (ValueError, RuntimeError) as exc:
            if contains not in str(exc):
                raise AssertionError('Wrong failure: ' + str(exc))
        else:
            raise AssertionError('Expected rejection: ' + contains)
    # Explicitly trap PYNQ import for local preparation checks.
    class NoPynq:
        def find_spec(self, fullname, path=None, target=None):
            if fullname == 'pynq' or fullname.startswith('pynq.'):
                raise AssertionError('Local checks attempted a PYNQ import')
    trap = NoPynq()
    sys.meta_path.insert(0, trap)
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('operator_board', delivery / 'board.py')
    board = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(board)
    for path in sorted(delivery.rglob('*.py')):
        check('Python3.8 syntax: ' + path.relative_to(delivery).as_posix(),
              lambda path=path: ast.parse(path.read_text(encoding='utf-8'), feature_version=8))
    check('Fresh delivery manifest and sealed BIT/HWH/release hashes', board.verify_package)
    check('No PYNQ import during module/file verification', lambda: equal('pynq' in sys.modules, False))
    notebook = json.loads((delivery / 'FIRST_STEP.ipynb').read_text(encoding='utf-8'))
    check('Notebook has no prior execution/output', lambda: equal(
        all(c.get('execution_count') is None and not c.get('outputs') for c in notebook['cells'] if c['cell_type'] == 'code'), True))
    last = ''.join(notebook['cells'][-1]['source'])
    check('Notebook load confirmation starts empty', lambda: equal("CONFIRM = ''" in last, True))
    def ps_case(reset, rd=0, wr=0, final=None):
        events = []
        values = {board.FPGA_RST_CTRL: reset, board.HP0_RD: rd, board.HP0_WR: wr}
        def reader(address):
            events.append(address)
            if len(events) == 4 and final is not None:
                return final
            return values[address]
        return board.hp0_snapshot(reader=reader), events
    def reset_block():
        result, reads = ps_case(board.AXI_RESET_MASK)
        equal(reads, [board.FPGA_RST_CTRL])
        equal(result['status'], 'PENDING_RESET_PRECONDITION; HP0_NOT_READ')
    check('Simulated asserted internal reset prevents all HP0 reads', reset_block)
    for rd, wr, expected in ((0, 0, 'READ_ONLY_HP0_64BIT_OBSERVED'),
                             (1, 0, 'BLOCKED_HP0_WIDTH_MISMATCH'),
                             (0, 1, 'BLOCKED_HP0_WIDTH_MISMATCH'),
                             (1, 1, 'BLOCKED_HP0_WIDTH_MISMATCH')):
        check('Simulated HP0 width bits rd={} wr={}'.format(rd, wr),
              lambda rd=rd, wr=wr, expected=expected: equal(ps_case(0, rd, wr)[0]['status'], expected))
    check('Simulated reset change rejected', lambda: equal('error' in ps_case(0, final=1)[0], True))
    check('Unresolved OS-only precheck rejected', lambda: reject(
        lambda: board.require_hp0({'status': 'PENDING_OS_ONLY_NO_REGISTER_READS'}), 'unresolved'))
    if sys.platform != 'linux' or board.platform.machine() not in board.ARM_HOSTS:
        check('Actual non-Zynq host stops before /dev/mem', lambda: reject(
            lambda: board.read_ps_word(board.FPGA_RST_CTRL), 'Zynq-7000'))
    config = {'core_revision': 'SIMULATED_CORE', 'carrier_revision': 'SIMULATED_CARRIER',
              'physical_ddr_marking': 'SIMULATED_DDR', 'reviewer': 'SOFTWARE_TEST_ONLY',
              'video_reference': 'NOT_A_REAL_RECORDING', 'fpga_part': 'xc7z020clg400-2',
              'boot_mode': 'SD_CARD', 'power_verified': True, 'exclusive_board_use': True,
              'ddr_preset_reviewed': True, 'runtime_sources_reviewed': True}
    check('Simulated complete operator config accepted structurally', lambda: board.check_operator_config(config))
    for name in config:
        modified = dict(config)
        modified[name] = None
        check('Missing operator field rejected: ' + name,
              lambda modified=modified: reject(lambda: board.check_operator_config(modified), ''))
    for value in ('true', 1, False):
        modified = dict(config, runtime_sources_reviewed=value)
        check('Non-true source review rejected: ' + repr(value),
              lambda modified=modified: reject(lambda: board.check_operator_config(modified), 'not completed'))
    # Stop run-one before any PS access or launcher import.
    check('Wrong exact confirmation rejected without hardware', lambda: reject(
        lambda: board.run_one(SimpleNamespace(confirm='yes')), 'confirmation missing'))
    consumed = output / 'SIMULATED_ALREADY_CONSUMED'
    consumed.mkdir()
    (consumed / 'ONE_ATTEMPT_CONSUMED.json').write_text('{"scope":"SOFTWARE_TEST_ONLY"}', encoding='utf-8')
    check('Consumed session rejected before any PS access', lambda: reject(
        lambda: board.run_one(SimpleNamespace(confirm=board.CONFIRM, preflight_dir=consumed)), 'already consumed'))
    # Fault-inject a copied package path, not the sealed release or delivery.
    original_root, original_release = board.ROOT, board.RELEASE
    board.ROOT = output / 'SIMULATED_BAD_MANIFEST'
    board.ROOT.mkdir()
    board.RELEASE = board.ROOT / 'release'
    (board.ROOT / 'package_manifest.json').write_text(json.dumps({'files': [
        {'path': '../outside.txt', 'bytes': 1, 'sha256': '0' * 64}]}), encoding='utf-8')
    check('Delivery path traversal rejected', lambda: reject(board.verify_package, 'escapes delivery'))
    board.ROOT, board.RELEASE = original_root, original_release
    # Fresh extraction is independent of the source package copy.
    archive = delivery.with_suffix('.zip')
    extracted = output / 'clean_extraction'
    with zipfile.ZipFile(archive) as stream:
        stream.extractall(extracted)
    fresh = extracted / delivery.name
    board.ROOT, board.RELEASE = fresh, fresh / 'release'
    check('Clean ZIP extraction passes all file hashes', board.verify_package)
    bit = board.RELEASE / 'flyvis_t5c_source_raw_v1.bit'
    with bit.open('r+b') as stream:
        first = stream.read(1)
        stream.seek(0)
        stream.write(bytes([first[0] ^ 1]))
    check('Tampered BIT in clean extraction rejected', lambda: reject(board.verify_package, 'identity changed'))
    board.ROOT, board.RELEASE = original_root, original_release
    sys.meta_path.remove(trap)
    report = {'status': 'PASS_LOCAL_OPERATOR_DELIVERY_CHECKS', 'evidence_level': 'LOCAL_FILES_AND_EXPLICIT_PS_READER_SUBSTITUTES',
              'board_io_operations': 0, 'board_execution_proven': False,
              'real_pl_computations': 0, 'checks': checks,
              'delivery_zip_sha256': sha(archive),
              'package_manifest_sha256': sha(delivery / 'package_manifest.json'),
              'limitations': ['No live PYNQ/PS register access; reader is an explicit function substitute',
                              'No first-step execution, PL load, output or video validation']}
    (output / 'SOFTWARE_REPORT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PASS_LOCAL_OPERATOR_DELIVERY_CHECKS:', len(checks))
    print('BOARD_IO_OPERATIONS: 0; REAL_PL_COMPUTATIONS: 0')
    print('REPORT:', output / 'SOFTWARE_REPORT.json')


if __name__ == '__main__':
    main()

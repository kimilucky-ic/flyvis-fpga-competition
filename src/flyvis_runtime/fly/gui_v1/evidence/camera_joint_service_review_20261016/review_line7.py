"""Bounded independent CPU recheck; never writes to the delivered Line 7 package."""
import contextlib
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import sys
import time
import unittest
from unittest.mock import patch

OUT = Path(__file__).resolve().parent
GUI = OUT.parents[1]
PACKAGE = GUI.parent.parent / 'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/camera_joint_service_20261016'
sys.path.insert(0, str(GUI))


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    delivery = json.loads((PACKAGE / 'DELIVERY.json').read_text(encoding='utf-8'))
    assert digest(PACKAGE / delivery['archive']) == delivery['archive_SHA256'] == '16549e704eb96cfd991aceb85d1cbabaa9185f6b61d526c327300971c2cc0be2'
    assert digest(PACKAGE / delivery['manifest']) == delivery['manifest_SHA256']
    manifest = json.loads((PACKAGE / delivery['manifest']).read_text(encoding='utf-8'))['files']
    for relative, expected in manifest.items():
        path = (PACKAGE / relative).resolve()
        assert path.is_relative_to(PACKAGE.resolve()) and digest(path) == expected, relative
    protected = json.loads((PACKAGE / 'PROTECTED_SHA256.json').read_text(encoding='utf-8'))
    for name, expected in protected.items():
        assert digest(Path(name)) == expected, name
    before = {name: digest(PACKAGE / name) for name in ('DELIVERY.json', 'results/RESULT.json', 'results/CPU_TESTS.log', 'DELIVERY_SHA256.json')}
    for name in ('joint_camera_worker.py', 'joint_camera_engine.py', 'joint_camera_controller.py', 'joint_camera_runtime.py'):
        target = OUT / 'before' / name
        target.parent.mkdir(exist_ok=True)
        assert not target.exists(), 'Do not overwrite previous review snapshots'
        target.write_bytes((GUI / name).read_bytes())
    spec = importlib.util.spec_from_file_location('line2_review_line7_tests', PACKAGE / 'test_camera_service.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.RESULTS = OUT / 'line7_recheck'
    (module.RESULTS / 'scratch').mkdir(parents=True, exist_ok=True)
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in
        (module.ServiceTests, module.ConfigTests, module.BindingTests, module.ConsumerTests))
    suite.addTests(module.CompatibilityTests(name) for name in module.CompatibilityTests.__dict__ if name.startswith('test_'))
    began = time.perf_counter()
    with patch.object(socket, 'socket', side_effect=AssertionError('NO_REAL_SOCKET')), \
         patch.object(socket, 'create_connection', side_effect=AssertionError('NO_REAL_CONNECTION')):
        with (module.RESULTS / 'CPU_TESTS.log').open('w', encoding='utf-8') as log, contextlib.redirect_stdout(log):
            result = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=module.TimedResult).run(suite)
    report = dict(status='PASS_CPU_SOFTWARE_REVIEW' if result.wasSuccessful() else 'FAIL',
        tests=result.testsRun, failures=len(result.failures), errors=len(result.errors), elapsed_s=time.perf_counter()-began,
        delivered_files_verified=len(manifest), protected_files_verified_before_edits=len(protected),
        archive_sha256=delivery['archive_SHA256'], delivered_results_before=before,
        delivered_results_unchanged=all(digest(PACKAGE/name) == value for name, value in before.items()),
        execution_authority='NONE', GPU_operations=0, camera_operations=0, GUI_launches=0, board_operations=0,
        network_operations=0, evidence_level='CPU_MEMORY_TRANSPORT_DUMMY_MMIO_ONLY', test_timings=module.TEST_TIMINGS)
    (module.RESULTS / 'RESULT.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'test_timings'}))
    return 0 if result.wasSuccessful() and report['delivered_results_unchanged'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

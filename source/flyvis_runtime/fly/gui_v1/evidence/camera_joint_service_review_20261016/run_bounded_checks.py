"""40 explicit CPU checks; inherited integration cases are not repeated."""
import ast
import contextlib
import json
from pathlib import Path
import socket
import sys
import time
import unittest
from unittest.mock import patch

OUT = Path(__file__).resolve().parent
GUI = OUT.parents[1]
sys.path.insert(0, str(GUI))
import test_joint_camera as original
import test_joint_camera_finish as finish

suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(original), finish.suite()])
began = time.perf_counter()
with patch.object(socket, 'socket', side_effect=AssertionError('NO_REAL_SOCKET')), \
     patch.object(socket, 'create_connection', side_effect=AssertionError('NO_REAL_CONNECTION')):
    with (OUT/'bounded_cpu_tests.log').open('w', encoding='utf-8') as log, contextlib.redirect_stdout(log):
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
changed = ('joint_camera_finish.py', 'joint_camera_engine.py', 'joint_camera_runtime.py',
           'joint_camera_worker.py', 'joint_camera_controller.py', 'test_joint_camera.py', 'test_joint_camera_finish.py')
for name in changed:
    ast.parse((GUI/name).read_text(encoding='utf-8'))
for name in ('torch', 'flyvis', 'pynq', 'cv2'):
    assert name not in sys.modules, 'Unexpected device/scientific runtime import: '+name
report = dict(status='PASS_CPU_FINISH_BUDGET_AND_GUI_REGRESSION' if result.wasSuccessful() else 'FAIL',
    tests=result.testsRun, failures=len(result.failures), errors=len(result.errors), elapsed_s=time.perf_counter()-began,
    original_camera_checks=27, added_finish_budget_checks=13, parsed_files=list(changed),
    execution_authority='NONE', GPU_operations=0, camera_operations=0, GUI_launches=0, board_operations=0,
    network_operations=0, actual_camera_joint_acceptance='NOT_RUN',
    no_device_runtime_imports=True, evidence_level='CPU_SAVED_DATA_AND_MEMORY_TRANSPORT_ONLY')
(OUT/'bounded_cpu_result.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps(report))
raise SystemExit(not result.wasSuccessful())

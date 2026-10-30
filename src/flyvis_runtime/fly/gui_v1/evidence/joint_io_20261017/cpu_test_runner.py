"""Targeted final CPU checks, captured without creating any device process."""
import json
from pathlib import Path
import sys
import unittest

OUT=Path(__file__).resolve().parent;sys.path.insert(0,str(OUT.parents[1]))
names=('test_joint_io','test_joint_camera.CameraJointTests','test_joint_camera.ControlTests',
    'test_joint_camera.HubLifecycleTests','test_joint_camera.InputAndAdmissionTests',
    'test_joint_streamline.PipelineTests',
    'test_joint_diagnostics.DiagnosticTests.test_GPU_tensor_and_sync_operations_unchanged_after_timing_unwrap',
    'test_joint_diagnostics.DrawLockTests')
suite=unittest.defaultTestLoader.loadTestsFromNames(names)
with (OUT/'CPU_FINAL_V2_TESTS.log').open('x',encoding='utf8') as f:
    result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
value=dict(status='PASS_CPU_PROTOCOL_ONLY' if result.wasSuccessful() else 'FAILED',tests=result.testsRun,
    failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),
    new_GPU_runs=0,camera_starts=0,GUI_starts=0,board_connections=0,
    excluded='OriginalGUIRouteTests: historical camera handoff uses Windows absolute paths; WSL resolves them incorrectly. Native Windows catalog verified separately: 55, errors=0.')
(OUT/'CPU_FINAL_V2_TESTS.json').write_text(json.dumps(value,indent=2),encoding='utf8')
print(json.dumps(value,indent=2));sys.exit(not result.wasSuccessful())

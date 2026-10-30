"""Bounded CPU suite. No board/GPU/camera/GUI; all register objects are fake."""
import json,sys,time,unittest
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parents[1]))
import test_ps_commit_evidence
test_ps_commit_evidence.OUT=P
suite=unittest.defaultTestLoader.loadTestsFromNames(['test_joint_step_latency','test_ps_commit_evidence',
    'test_joint_io.SocketTests','test_joint_camera.CameraJointTests.test_three_step_original_coordinator_feedback_and_durable_snapshots'])
start=time.perf_counter()
with (P/'CPU_TESTS.log').open('x',encoding='utf8') as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
v=dict(status='PASS_CPU_ONLY' if result.wasSuccessful() else 'FAILED',tests=result.testsRun,failures=len(result.failures),
    errors=len(result.errors),elapsed_s=time.perf_counter()-start,GPU_runs=0,camera_starts=0,GUI_starts=0,
    board_connections=0,real_MMIO=0,new_neural_calculations=0,actual_joint_steps_s='NOT_MEASURED')
(P/'CPU_RESULT.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v,indent=2));sys.exit(not result.wasSuccessful())

"""Bounded PS policy tests; all frames/MMIO are memory fixtures, no sockets."""
import json,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parents[1]))
suite=unittest.defaultTestLoader.loadTestsFromNames(['test_ps_commit_evidence','test_joint_camera_preparation',
    'test_joint_camera.ControlTests','test_joint_camera.InputAndAdmissionTests'])
with (P/'CPU_TESTS_FINAL2.log').open('x',encoding='utf8') as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
value=dict(status='PASS_CPU_SAVED_WIRE_DUMMY_MMIO_ONLY' if result.wasSuccessful() else 'FAILED',tests=result.testsRun,
    failures=len(result.failures),errors=len(result.errors),board_connections=0,real_MMIO=0,GPU_runs=0,camera_starts=0,GUI_starts=0,
    note='Original PS service/Full485Driver methods executed only with dummy registers, numpy buffers and saved historical words; not PL validation')
(P/'CPU_RESULT_FINAL2.json').write_text(json.dumps(value,indent=2),encoding='utf8');print(json.dumps(value,indent=2));sys.exit(not result.wasSuccessful())

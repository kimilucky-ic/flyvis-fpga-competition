"""One bounded CPU run, memory fixtures plus localhost-only option test."""
import json,sys,time,unittest
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parents[1]))
import test_ps_commit_evidence
test_ps_commit_evidence.OUT=P  # Keep all new CPU evidence within this delivery.
suite=unittest.defaultTestLoader.loadTestsFromNames(['test_joint_transport','test_ps_commit_evidence',
    'test_joint_camera.InputAndAdmissionTests'])
start=time.perf_counter()
with (P/'CPU_TESTS.log').open('x',encoding='utf8') as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
value=dict(status='PASS_CPU_ONLY' if result.wasSuccessful() else 'FAILED',tests=result.testsRun,
    failures=len(result.failures),errors=len(result.errors),elapsed_s=time.perf_counter()-start,
    board_connections=0,real_MMIO=0,GPU_runs=0,camera_starts=0,GUI_starts=0,
    loopback='127.0.0.1 ephemeral only; no application/board service',actual_joint_speed='NOT_MEASURED')
(P/'CPU_RESULT.json').write_text(json.dumps(value,indent=2),encoding='utf8')
print(json.dumps(value,indent=2));sys.exit(not result.wasSuccessful())

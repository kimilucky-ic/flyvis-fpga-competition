"""Targeted follow-up only; retain first full log and fixture failure."""
import json,sys,time,unittest
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parents[1]))
import test_ps_commit_evidence
test_ps_commit_evidence.OUT=P
suite=unittest.defaultTestLoader.loadTestsFromNames([
    'test_joint_step_latency.EncodingTests',
    'test_joint_step_latency.PSTimingAndEventsTests.test_original_MMIO_events_words_ACK_and_barriers_preserved',
    'test_ps_commit_evidence.PSCommitTests.test_commit_fsync_failure_prevents_RELEASE_and_ACK',
    'test_ps_commit_evidence.PSCommitTests.test_ACK_fsync_failure_after_RELEASE_never_sends_ACK'])
start=time.perf_counter()
with (P/'CPU_TESTS_FINAL.log').open('x',encoding='utf8') as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
v=dict(status='PASS_CPU_TARGETED' if result.wasSuccessful() else 'FAILED',tests=result.testsRun,
    failures=len(result.failures),errors=len(result.errors),elapsed_s=time.perf_counter()-start,
    board_connections=0,GPU_runs=0,camera_starts=0,GUI_starts=0,real_MMIO=0)
(P/'CPU_RESULT_FINAL.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v,indent=2));sys.exit(not result.wasSuccessful())

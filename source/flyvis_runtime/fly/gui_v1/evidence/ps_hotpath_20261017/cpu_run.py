"""Bounded CPU tests. Forbid any real network connection or socket bind."""
import json,sys,time,unittest
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parents[1]))
import test_ps_commit_evidence
test_ps_commit_evidence.OUT=P
suite=unittest.defaultTestLoader.loadTestsFromNames(['test_ps_hotpath','test_ps_commit_evidence',
    'test_joint_step_latency.PSTimingAndEventsTests'])
start=time.perf_counter()
with patch('socket.create_connection',side_effect=AssertionError('CPU_ONLY_NO_NETWORK')),patch('socket.socket',side_effect=AssertionError('CPU_ONLY_NO_SOCKET')):
    with (P/'CPU_TESTS.log').open('x',encoding='utf8') as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
v=dict(status='PASS_CPU_ONLY' if result.wasSuccessful() else 'FAILED',tests=result.testsRun,
    failures=len(result.failures),errors=len(result.errors),elapsed_s=time.perf_counter()-start,
    board_connections=0,real_MMIO=0,GPU_runs=0,camera_starts=0,GUI_starts=0,new_scopes=0,
    evidence='Original PS run code, fake registers/buffers, saved real protocol arrays; no new neural inference',actual_PS_ms='NOT_MEASURED')
(P/'CPU_RESULT.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v,indent=2));sys.exit(not result.wasSuccessful())

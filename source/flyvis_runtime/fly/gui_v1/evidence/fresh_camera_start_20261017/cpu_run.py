"""Bounded CPU-only cold-start adaptation; prohibit every real socket."""
import json,sys,time,unittest
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parents[1]))
import test_joint_camera_manual as legacy
legacy.OUT=P/'legacy';legacy.fixtures.RESULTS=P/'fixture';(legacy.fixtures.RESULTS/'scratch').mkdir(parents=True,exist_ok=True)
suite=unittest.defaultTestLoader.loadTestsFromNames(['test_joint_camera_fresh','test_joint_camera_manual.TransferTests',
    'test_joint_camera_manual.ManualTests'])
start=time.perf_counter()
with patch('socket.socket',side_effect=AssertionError('CPU_ONLY_NO_SOCKET')),patch('socket.create_connection',side_effect=AssertionError('CPU_ONLY_NO_NETWORK')):
    log=P/('CPU_TESTS_r2.log' if (P/'CPU_TESTS.log').exists() else 'CPU_TESTS.log')
    with log.open('x',encoding='utf8') as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
v=dict(status='PASS_CPU_ONLY' if result.wasSuccessful() else 'FAILED',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),
    elapsed_s=time.perf_counter()-start,log=log.name,real_sockets=0,board_initializations=0,GPU_runs=0,camera_starts=0,GUI_starts=0,
    evidence='Fake original constructor, original frozen driver methods retained, original signed GUI reader; not physical cold-start validation')
(P/'CPU_RESULT.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v,indent=2));sys.exit(not result.wasSuccessful())

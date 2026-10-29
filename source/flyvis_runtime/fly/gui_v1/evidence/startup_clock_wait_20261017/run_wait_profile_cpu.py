import io,json,socket,sys,time,unittest
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent.parent))
import test_joint_clock_wait_profile as current
import test_joint_fresh_unused as handover
import test_joint_camera_fresh as original
original.OUT=P/'wait_profile_legacy_cases'
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(current.WaitProfileTests),
    unittest.defaultTestLoader.loadTestsFromTestCase(handover.FreshUnusedTests),
    original.FreshTests('test_original_read20_zero_writes_actual_zero_counters_idle0'),
    original.FreshTests('test_original_GUI_signed_reader_accepts_fresh_without_claiming_old485')])
log=io.StringIO();begin=time.perf_counter()
with patch.object(socket,'socket',side_effect=AssertionError('REAL_SOCKET_FORBIDDEN')), \
     patch.object(socket,'create_connection',side_effect=AssertionError('REAL_CONNECTION_FORBIDDEN')):
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
record=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),elapsed_s=time.perf_counter()-begin,
    evidence_level='CPU_FAKE_TIME_ORIGINAL_ALGORITHM_NEW_ADMINISTRATIVE_WAIT_PROFILE',successful=result.wasSuccessful(),real_sockets_forbidden=True)
(P/'WAIT_PROFILE_CPU_TESTS.log').write_text(log.getvalue(),encoding='utf8')
(P/'WAIT_PROFILE_CPU_RESULT.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
print(json.dumps(record))
if not result.wasSuccessful():print(log.getvalue())
sys.exit(0 if result.wasSuccessful() else 1)

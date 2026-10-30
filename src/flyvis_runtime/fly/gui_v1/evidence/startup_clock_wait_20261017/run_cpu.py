"""One bounded native-Windows lifecycle check; all real sockets forbidden."""
import io,json,socket,sys,time,unittest
from pathlib import Path
from unittest.mock import patch

OUT=Path(__file__).resolve().parent
GUI=OUT.parent.parent
sys.path.insert(0,str(GUI))
import test_joint_camera_preparation as previous
import test_joint_preparation_clock_lifecycle as lifecycle
import test_joint_streamline as streamline

previous.OUT=OUT/'existing_admission_cases'
streamline.OUT=OUT/'existing_connection_cases'
suite=unittest.TestSuite([
    unittest.defaultTestLoader.loadTestsFromTestCase(lifecycle.ClockLifecycleTests),
    unittest.defaultTestLoader.loadTestsFromTestCase(previous.PreparationTests),
    unittest.defaultTestLoader.loadTestsFromTestCase(streamline.ClockTests),
])
log=io.StringIO();started=time.perf_counter()
with patch.object(socket,'socket',side_effect=AssertionError('REAL_SOCKET_FORBIDDEN')), \
     patch.object(socket,'create_connection',side_effect=AssertionError('REAL_CONNECTION_FORBIDDEN')):
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
elapsed=time.perf_counter()-started
(OUT/'CPU_TESTS.log').write_text(log.getvalue(),encoding='utf-8')
record=dict(evidence_level='CPU_FAKE_TIME_ORIGINAL_CLOCK_HELPER',tests=result.testsRun,
    failures=len(result.failures),errors=len(result.errors),elapsed_s=elapsed,
    GPU_starts=0,camera_starts=0,GUI_starts=0,board_connections=0,real_sockets_forbidden=True,
    successful=result.wasSuccessful())
(OUT/'CPU_RESULT.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
if not result.wasSuccessful():print(log.getvalue())
sys.exit(0 if result.wasSuccessful() else 1)

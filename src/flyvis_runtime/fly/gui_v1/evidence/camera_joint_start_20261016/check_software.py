"""One bounded new-version review, with all outputs in Line 2's folder."""
import ast,contextlib,hashlib,importlib.util,json,socket,sys,time,unittest
from pathlib import Path
from unittest.mock import patch
OUT=Path(__file__).resolve().parent;GUI=OUT.parents[1]
PACKAGE=GUI.parent.parent/'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/camera_joint_ready_20261016'
sys.path.insert(0,str(GUI))
from live_protocol import load,sha
delivery=load(PACKAGE/'DELIVERY.json')
assert sha(PACKAGE/delivery['archive'])==delivery['archive_SHA256']=='b127abd1d35ec9b68a00f580542fd749a31221d21ea7e520d5547c27bbd9f1d0'
assert sha(PACKAGE/'DELIVERY_SHA256.json')==delivery['manifest_SHA256']
manifest=load(PACKAGE/'DELIVERY_SHA256.json')['files']
for n,h in manifest.items():assert sha(PACKAGE/n)==h,n
spec=importlib.util.spec_from_file_location('line2_ready_delivery_test',PACKAGE/'test_ready.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.RESULTS=OUT/'ready_recheck';(m.RESULTS/'scratch').mkdir(parents=True,exist_ok=True)
import test_joint_camera as old
import test_joint_camera_finish as finish
import test_joint_camera_preparation as prepared
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in (m.ClockTests,m.PrepareTests,m.PreservationTests))
suite.addTests(m.ServiceTests(n) for n in m.ServiceTests.__dict__ if n.startswith('test_'))
suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(old));suite.addTests(finish.suite())
suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(prepared))
began=time.perf_counter()
with patch.object(socket,'socket',side_effect=AssertionError('NO_REAL_SOCKET')),patch.object(socket,'create_connection',side_effect=AssertionError('NO_REAL_CONNECTION')):
    with (OUT/'CPU_TESTS.log').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log):
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
ast.parse((GUI/'joint_camera_board_entry.py').read_text(encoding='utf-8'),feature_version=(3,8))
for name in ('torch','flyvis','pynq','cv2'):assert name not in sys.modules,name
report=dict(status='PASS_BOUNDED_READY_INTEGRATION_CPU' if result.wasSuccessful() else 'FAIL',
    tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),elapsed_s=time.perf_counter()-began,
    delivered_files_checked=len(manifest),archive_sha256=delivery['archive_SHA256'],
    GPU_operations=0,camera_operations=0,GUI_launches=0,board_operations=0,network_operations=0,
    level='CPU_CLOCKS_MEMORY_TRANSPORT_SAVED_DATA_ONLY')
(OUT/'CPU_RESULT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report));raise SystemExit(not result.wasSuccessful())

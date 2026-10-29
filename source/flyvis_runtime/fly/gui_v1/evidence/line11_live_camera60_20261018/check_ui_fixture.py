"""Software envelope fixture only; reuse received states and actual CPU-decoded flow."""
import json
from pathlib import Path
import sys
import numpy as np
OUT=Path(__file__).resolve().parent;HERE=OUT.parents[1];sys.path.insert(0,str(HERE))
from test_line11_live_camera import LiveCameraTests
from line11_ddr_bridge import digest
LiveCameraTests.setUpClass()
case=LiveCameraTests('test_virtual60_three_real_saved_states_feedback_and_synchronized_output');case.setUp()
try:
    case.run_three()
    reply=case.session.latest();p=reply['frame'];status=reply['status'];anchor=case.session.seed.frame()
    # A protocol validator fixture does not assert that these are live board data.
    raw=(OUT/'actual_cpu_worker_r2/000002.flow.bin').read_bytes()
    p['flow']=np.frombuffer(raw,dtype='<f4').reshape(2,721).tolist();p['flow_sha256']=digest(raw)
    p['display_kind']='FINISHED_FULL_PL_LAST_STATE'
    result=dict(evidence='CPU_SCHEMA_FIXTURE_NOT_GUI_OR_PHYSICAL_RUN',frame=p,status=status,anchor=anchor,
                health={'projection_cache':{'upstream_map_sha256':p['spatial']['map_sha256']}})
    (OUT/'UI_PROTOCOL_FIXTURE.json').write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
    print('UI_PROTOCOL_FIXTURE_FROM_SAVED_STATE_AND_CPU_FLOW_ONLY')
finally:case.doCleanups()

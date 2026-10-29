"""One explicit correction of the failed zero-STEP preparation, not a retry.

Retains old scope, package, capture and poisoned unused driver. Uses only the
existing fresh.prepare prestart-cancel/unused handoff; never constructs hardware.
After this correction the production entry uses its normal accepted-parent path.
"""
import sys,json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(HERE))
from live_protocol import load,write,sha,require
from joint_camera_preparation import verify_prepared_handoff
import joint_camera_repeat as repeat
import joint_camera_bundle as bundle
from joint_camera_manual import ManualGate,board_cell
from joint_camera_controller import execute

old=HERE/'runtime/joint_workbench/ee9c996a50c04b11891b77a3d300d73d/instances/de2e293ff16e492f8a8c387dd22903d4/prepare/39e88abcc33c417ba0832f9d816844f8'
scope=load(old/'scope.json');handoff=load(old/'hardware_handoff.json')
body=verify_prepared_handoff(handoff,scope,old)
receipt={k:v for k,v in body['preparation_receipt'].items() if k not in ('ps_durability','minimal_compute')}
require(body['status']['state']=='BOARD_PREPARED' and receipt['requests']==receipt['commits']==0,'REPAIR_NOT_UNSTARTED')
prior=dict(body['binding'],preparation_receipt_sha256=hashlib.sha256(json.dumps(receipt,sort_keys=True).encode()).hexdigest(),
    allow_manual_prestart_cancel=True,inherited_completed_counters=True)
selection=dict(fresh=scope['fresh_initialized_parent'],unused_fresh=prior)
write(Path(__file__).parent/'FINAL_PC_CORRECTION.json',dict(old_scope_sha256=sha(old/'scope.json'),old_run=scope['run_id'],
    reason='repeat installation compared PC expiry with PS calendar; preparation succeeded, no START',selection=selection,
    new_loads=0,new_resets=0,new_allocations=0,automatic_neural_retry=False))
bundle.preparation_parent=lambda:selection
def gate_factory(*args,**kwargs):
    gate=ManualGate(*args,**kwargs)
    if gate.unused_fresh:
        source="# Explicit prestart software cancellation, no neural frame, reset or allocation.\nassert camera3_service_instance.config['run_id']=='39e88abcc33c417ba0832f9d816844f8'\nassert camera3_service_instance.driver.requests==camera3_service_instance.driver.commits==0 and camera3_service_instance.identity is None\nassert camera_repeat_handle['prepared_runs']==1 and camera_repeat_handle['error'] is None\ncamera3_service_instance.stop('PC_PRESTART_CANCELLED_FOR_GUI_RECONNECT')\ncamera_repeat_handle['thread'].join(3)\nassert not camera_repeat_handle['thread'].is_alive() and camera_repeat_handle['error']=='REPEAT_PREVIOUS_FAILED_OR_UNKNOWN'\nglobals().setdefault('camera_retired_repeat_handles',[]).append(camera_repeat_handle)\ndel camera_repeat_handle\n"+board_cell(gate.token,fresh=gate.fresh,unused_fresh=gate.unused_fresh)
        source+='\ncamera_entry.install_repeat(camera_new_root,globals())\n'
        (Path(__file__).parent/'FINAL_BOARD_CELL.py').write_text(source,encoding='utf8')
    return gate
repeat.ManualGate=gate_factory
repeat.run_workbench(execute)

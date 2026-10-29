"""Reproduce the observed board UTC mismatch without hardware/network access."""
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
GUI = OUT.parents[1]
FPGA = GUI.parent.parent/'fpga'
sys.path.insert(0, str(GUI))
from live_protocol import load, sha

package = FPGA/'flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/camera_joint_service_20261016'
sys.path.insert(0, str(package))
from a3camera.contract import window

inventory = load(OUT/'actual_board_inventory.json')
host_now = datetime.now(timezone.utc)
scope_time = dict(start_utc=(host_now-timedelta(seconds=1)).isoformat(), end_utc=(host_now+timedelta(seconds=299)).isoformat())
window(scope_time, host_now)
try:
    window(scope_time, datetime.fromisoformat(inventory['utc']))
except ValueError as exc:
    assert str(exc) == 'CAMERA_SCOPE_EXPIRED'
    rejected = str(exc)
else:
    raise AssertionError('Observed board UTC must not pass the new scope')
result = dict(status='START_BLOCKER_REPRODUCED_IN_SOFTWARE', observed_board_inventory_sha256=sha(OUT/'actual_board_inventory.json'),
    host_utc=host_now.isoformat(), supplied_board_utc=inventory['utc'], rejection=rejected,
    code_sha256=sha(package/'a3camera/contract.py'), timing_scope_fixture=scope_time,
    window_is_format_fixture_not_authorization=True, control_service_creation=0,
    GPU_operations=0,camera_operations=0,MMIO_reads=0,MMIO_writes=0,DMA_operations=0,
    interpretation='No actual service launch attempted; existing window validator correctly rejects unsynchronised clock')
(OUT/'start_gate_result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=result['status'],rejection=rejected,supplied_board_utc=inventory['utc'],host_utc=host_now.isoformat())))

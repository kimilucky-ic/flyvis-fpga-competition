"""Freeze the human-approved single 485-step experiment; no GPU/board operations."""
import sys, shutil
from pathlib import Path
from datetime import datetime, timezone, timedelta
HERE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(HERE))
from live_protocol import load,write,sha,canonical
from hybrid_full485_run import preflight,checked_scope
from hybrid_full485 import source_pins,SOURCE_NAMES
out=Path(__file__).parent
board=HERE.parent.parent/'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/joint_full485_20261013'
handoff=load(board/'LINE7_HANDOFF.json'); prepared=load(board/'BOARD_PREPARED.json'); own=load(out/'LINE2_PREPARE.json')
assert prepared['status']=='READONLY_READY_NOT_LISTENING' and prepared['run_id']==own['run_id']
p=preflight();write(out/'preflight_final.json',p)
s=load(HERE/'evidence/joint_live_20261013/approved_scope.json')
now=datetime.now(timezone.utc)
s.update(schema='flyvis-approved-joint-full485/v1',human_authorization_reference=own['human_authorization_reference'],
 model_steps=list(range(485)),max_requests=485,max_commits=485,new_allocations=0,
 expected_server_session=handoff['server_session'],expected_boot_id=handoff['expected_boot_id'],
 start_utc=now.isoformat(),end_utc=(now+timedelta(seconds=2700)).isoformat(),
 gpu_lease_id='full485_'+own['run_id'],run_id=own['run_id'],comparison_id='ON60_FULL485_'+own['run_id'],
 initial_full_digest=p['initial_full_digest'],initial_H_sha256=p['initial_H_sha256'],initial_file_sha256=p['initial_file_sha256'],
 initial_kind='FROZEN_GRAY_ADAPTED_A0_QUANTIZE_H_ONCE',source_sha256=source_pins(),
 short_receipt_sha256=p['short_receipt_sha256'],max_worker_seconds=2700,max_compute_seconds=2400,
 board_host_files={str(board/n):d for n,d in handoff['upload_files'].items()},full_485_authorized=True)
s.pop('reference_manifest_sha256',None)
target=out/'approved_scope.json';assert not target.exists()
write(target,s);checked_scope(target)
snap=out/'executed_sources';snap.mkdir(exist_ok=False)
for name in SOURCE_NAMES:shutil.copy2(HERE/name,snap/name)
write(out/'scope_frozen_receipt.json',dict(status='PASS_READONLY_SCOPE_FROZEN',scope_sha256=sha(target),run_id=own['run_id'],
 board_handoff_sha256=sha(board/'LINE7_HANDOFF.json'),board_prepared_sha256=sha(board/'BOARD_PREPARED.json'),CPU_tests=103))
print(target)

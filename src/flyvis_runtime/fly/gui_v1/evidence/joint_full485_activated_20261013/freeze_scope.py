"""Freeze one newly approved execution after line7's actual read-only activation."""
import argparse,sys,shutil
from pathlib import Path
from datetime import datetime,timezone,timedelta
HERE=Path(__file__).resolve().parents[2];sys.path.insert(0,str(HERE))
from live_protocol import load,write,sha,host_path
from hybrid_full485_run import checked_scope
from hybrid_full485 import source_pins,SOURCE_NAMES
ap=argparse.ArgumentParser();ap.add_argument('--prepared',required=True);ap.add_argument('--handoff',required=True);args=ap.parse_args()
out=Path(__file__).parent;own=load(out/'LINE2_PREPARE.json')
prepared_path=host_path(args.prepared);handoff_path=host_path(args.handoff);prepared=load(prepared_path);handoff=load(handoff_path)
assert prepared['status']=='READONLY_READY_NOT_LISTENING'
assert prepared['run_id']==own['run_id'] and prepared['server_session']==own['server_session']
assert prepared['authorized_parent_run']==own['authorized_parent_run']
assert prepared['new_loads']==prepared['new_resets']==prepared['new_allocations']==prepared['PL_requests']==prepared['commits']==0
old=HERE/'runtime/hybrid_full485_runs'/own['authorized_parent_run'];s=load(old/'scope.json')
assert sha(old/'scope.json')==own['old_scope_sha256'] and sha(old/'STOP_REQUEST.json')==own['old_stop_sha256']
assert load(old/'result.json')['completed']==0 and load(old/'exit.json')['lease_closed'] and not (old/'pc').exists()
assert prepared['boot_id']==s['expected_boot_id']
board=HERE.parent.parent/'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/joint_full485_activation_20261013'
plan=load(board/'ACTIVATION_PLAN.json');pins=load(board/'ACTIVATION_SHA256.json')
assert plan['run_id']==own['run_id'] and plan['server_session']==own['server_session'] and plan['max_requests']==plan['max_commits']==485
assert plan['initial_full_sha256']==s['initial_full_digest'] and plan['initial_H_sha256']==s['initial_H_sha256']
assert source_pins()==load(out/'source_unchanged.json')['source_sha256']
for name,digest in pins.items():assert sha(board/name)==digest
now=datetime.now(timezone.utc)
s.update(human_authorization_reference=own['human_authorization_reference'],human_exact_answer=own['human_exact_answer'],
 authorized_parent_run=own['authorized_parent_run'],authority_thread=own['authority_thread'],authority_turn=own['authority_turn'],authority_message=own['authority_message'],
 run_id=own['run_id'],gpu_lease_id='full485_'+own['run_id'],comparison_id='ON60_FULL485_'+own['run_id'],
 start_utc=now.isoformat(),end_utc=(now+timedelta(seconds=2700)).isoformat(),source_sha256=source_pins(),
 activation_prepared_sha256=sha(prepared_path),activation_handoff_sha256=sha(handoff_path))
s['board_host_files'].update({str(board/n):digest for n,digest in pins.items()})
target=out/'approved_scope.json';assert not target.exists();write(target,s);checked_scope(target)
snap=out/'executed_sources';snap.mkdir(exist_ok=False)
for name in SOURCE_NAMES:shutil.copy2(HERE/name,snap/name)
shutil.copy2(prepared_path,out/'LINE7_PREPARED_FROZEN.json');shutil.copy2(handoff_path,out/'LINE7_HANDOFF_FROZEN.json')
write(out/'scope_frozen_receipt.json',dict(status='PASS_EXACT_DIRECT_APPROVAL_EXECUTION_ASSOCIATION',run_id=own['run_id'],scope_sha256=sha(target),prepared_sha256=sha(prepared_path),source_sha256=source_pins(),authorized_parent_run=own['authorized_parent_run']))
print(target)

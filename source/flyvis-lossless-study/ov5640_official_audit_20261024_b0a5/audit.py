"""Offline diagnosis only; no board access or execution of code from result ZIP."""
from pathlib import Path
import hashlib,json,sys,struct
HERE=Path(__file__).resolve().parent
BUNDLE=HERE.parent/'ov5640_official_release_20261024/bundle'
source=Path('C:/Users/hzy72/Downloads/RUN_b0a5cd8079b045bdb1b97c07523c6c55_RESULT.zip')
sys.path.insert(0,str(BUNDLE))
from offline_check import verify,BIT_SHA,HWH_SHA
from verify_result import unpack,validate_preflight,validate_run
from audit_bridge import audit
from snapshot_records import decode_record
from board_runtime import clocks

def save(name,value):
    with (HERE/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2);f.write('\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
identity=verify(BUNDLE)
archive=HERE/source.name
with archive.open('xb') as f:f.write(source.read_bytes())
assert sha(archive)==sha(source)
run=unpack(archive,HERE/'raw')
context=json.loads((run/'RUN_CONTEXT.json').read_text())
stop=json.loads((run/'IN_DOUBT.json').read_text())
assert context['identity']['bit_sha256']==BIT_SHA and context['identity']['hwh_sha256']==HWH_SHA
assert context['revision']=='LINE11_OFFICIAL_FULL_R1'
assert context['evidence']=='OPERATOR_PHYSICAL_RUN_UNATTESTED'
assert stop['phase']=='CAPTURE_BIND_AND_STEP'
assert stop['error']=="RuntimeError('Unexpected full-network compute cycle count')"
assert not (run/'RESULT.json').exists() and not (run/'NEURAL_AFTER.json').exists()
validate_preflight(run)
before=json.loads((run/'NEURAL_BEFORE.json').read_text())
assert all(before[hex(a)]==0 for a in (0x10,0x14,0x18,0x24))
assert [before[hex(a)] for a in (0x30,0x34,0x38,0x3c)]==[45669,1513231,0x110004,188416]
ownership=json.loads((run/'DDR_OWNERSHIP.json').read_text())
cam=json.loads((run/'CAMERA_BUFFER.json').read_text())
assert ownership['bytes']==188416 and ownership['slots']==1
assert cam['bytes']==1152000 and cam['coherent'] is False
assert cam['neural_base']==ownership['base'] and cam['neural_bytes']==ownership['bytes']
assert cam['address']>=ownership['base']+ownership['bytes'] or ownership['base']>=cam['address']+cam['bytes']
record_path=run/'capture/bound/000000/record.bin'
record=decode_record(record_path.read_bytes(),0)
header=struct.unpack_from('<32I',record_path.read_bytes())
assert record.cycles==2199975
# Preserve top-level IN_DOUBT. Audit only the committed record as a distinct
# numerical diagnosis, without declaring successful session close.
try:
    validate_run(run,HERE/'normal_acceptance',BUNDLE)
except ValueError as exc:
    assert str(exc)=='Uncertain session is not accepted'
    save('NORMAL_ACCEPTANCE_REJECTION.json',dict(rejected=True,reason=str(exc)))
else:raise AssertionError('Stopped session wrongly accepted')
comparison=audit(run/'capture',HERE/'numerical_audit',BUNDLE)
assert comparison['state_words_compared']==45669 and comparison['mismatch_words']==0
prior=HERE.parent/'ddr_soc_20261018/AUDIT.json'
prior_data=json.loads(prior.read_text())
assert prior_data['cycle_counter']['record_values']==[2199975]*3
neural=HERE.parent/'ov5640_official_2026_20261024/neural'
refs=[BUNDLE/'board_run.py',BUNDLE/'verify_result.py',BUNDLE/'audit_bridge.py',BUNDLE/'reference.exe',neural/'flyvis_ddr_snapshot_top.sv',neural/'flyvis_lane.sv',prior]
save('SOURCE_EVIDENCE.json',{str(p):sha(p) for p in refs})
save('RESULT.json',dict(
 status='PASS_OFFLINE_SAVED_SINGLE_STEP_ALL_STATES_SESSION_REMAINS_STOPPED',
 evidence='OFFLINE_AUDIT_OF_OPERATOR_SUBMITTED_PHYSICAL_RUN_RECORDS',
 archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
 run_id=context['run_id'],bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,
 nodes=45669,edges=1513231,actual_input_words=721,state_words_compared=45669,mismatch_words=0,
 actual_cycles=record.cycles,incorrect_software_expected_cycles=2201418,
 difference_cycles=2201418-record.cycles,nominal_core_phase_ms=record.cycles/100000,
 full_step_wall_time_measured=False,physical_clock_measured=False,
 derived_clocks_MHz=clocks(json.loads((run/'CLOCK.json').read_text())['raw']),
 header_edge_count=header[9],header_state_count=header[10],header_faults=header[18],
 root_cause='Release software used older MMIO cycle count for unchanged DDR phase-only counter. Historical DDR RTL record value matches actual.',
 test_gap='CPU fake descriptors and DDR records copied the same incorrect 2201418 constant; tests were not tied to existing DDR RTL timing evidence.',
 numerical=comparison,
 session_status='IN_DOUBT_PRESERVED',normal_camera_close_reached=False,final_register_snapshot_present=False,
 physical_execution_independently_observed=False,board_operations_by_auditor=0,gpu_operations=0,
 limitations=['One saved model step only; no multi-step feedback or sustained camera proof',
              'No final register snapshot or normal camera close because outer cycle guard stopped first',
              'Nominal frequency from PS registers, not physical clock measurement',
              'Color/exposure correctness not established by numerical acceptance'],
 next_action='Separate software-only correction and focused CPU regression; preserve current board kernel/buffers, no retry/reset/free'))
print(json.dumps(json.loads((HERE/'RESULT.json').read_text()),indent=2))

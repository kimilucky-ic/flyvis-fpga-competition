"""Freeze this bounded software review; create ONLY a new unapproved scope."""
import ast
import copy
import json
from pathlib import Path
import sys
import uuid

OUT = Path(__file__).resolve().parent
GUI = OUT.parents[1]
FPGA = GUI.parent.parent/'fpga'
LINE7 = FPGA/'flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/camera_joint_service_20261016'
BASE = GUI/'evidence/camera_joint_20261016'
sys.path.insert(0, str(GUI))
from live_protocol import load, sha
from joint_camera_controller import source_pins
from joint_camera_finish import BOARD_IDLE_S, SOURCE_CLOSE_WITHIN_S, FINISH_SEND_WITHIN_S


def save_new(name, value):
    with (OUT/name).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


delivery7 = load(LINE7/'DELIVERY.json')
assert sha(LINE7/delivery7['archive']) == delivery7['archive_SHA256']
assert sha(LINE7/delivery7['manifest']) == delivery7['manifest_SHA256']
files7 = load(LINE7/delivery7['manifest'])['files']
for name, expected in files7.items():
    assert sha(LINE7/name) == expected, name
baseline = load(BASE/'delivery.json')
for item in baseline['preserved_original_compute'].values():
    assert sha(item['path']) == item['sha256'], item['path']
old7 = load(FPGA/'flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/handoff_line2_camera_20261016/SOURCE_SHA256.json')
for item in old7['files']:
    assert sha(item['path']) == item['sha256'], item['path']
allowed_gui_changes = {'joint_camera_controller.py','joint_camera_engine.py','joint_camera_runtime.py','joint_camera_worker.py','test_joint_camera.py'}
protected_differences = []
for name, expected in load(LINE7/'PROTECTED_SHA256.json').items():
    actual = sha(name)
    if actual != expected:
        path = Path(name)
        assert path.parent == GUI and path.name in allowed_gui_changes, 'Unexpected protected change: '+name
        protected_differences.append(dict(path=name, baseline=expected, current=actual, reason='LINE2_AUTHORIZED_FINISH_BUDGET_REVISION'))
recheck = load(OUT/'line7_recheck/RESULT.json')
for name, expected in recheck['delivered_results_before'].items():
    assert sha(LINE7/name) == expected, name
assert recheck['status'] == 'PASS_CPU_SOFTWARE_REVIEW'
assert load(OUT/'bounded_cpu_result.json')['status'] == 'PASS_CPU_FINISH_BUDGET_AND_GUI_REGRESSION'
for name in ('joint_camera_finish.py','joint_camera_worker.py','joint_camera_engine.py','joint_camera_runtime.py','joint_camera_controller.py'):
    ast.parse((GUI/name).read_text(encoding='utf-8'))

draft = copy.deepcopy(load(BASE/'scope_draft_r1.json'))
for key in ('run_id','session_id','gpu_lease_id','server_session'):
    draft[key] = uuid.uuid4().hex
draft.update(comparison_id='CAMERA_'+draft['run_id'], status='DRAFT_NOT_AUTHORIZED', execution_authority='NONE',
    human_authorization_reference=None, max_steps=3, capture_duration_s=10, max_worker_s=180,
    boot_id=None, start_utc=None, end_utc=None, hardware_handoff_sha256=None, source_sha256=source_pins())
save_new('scope_draft_r2.json', draft)
requirements = copy.deepcopy(load(BASE/'REQUIREMENTS_TO_LINE7.json'))
requirements.update(status='SOFTWARE_INTERFACES_CPU_VERIFIED_HARDWARE_NOT_PREPARED',
    scope_draft=str(OUT/'scope_draft_r2.json'), scope_draft_sha256=sha(OUT/'scope_draft_r2.json'),
    planned_bounds=dict(max_steps=3, capture_duration_s=10, max_worker_s=180, status='DRAFT_NOT_AUTHORIZED'),
    timing_addendum=str(FPGA/'docs/workstreams/FLYVIS_LINE2_CAMERA_FINISH_BUDGET_20261016.md'),
    timing_addendum_sha256=sha(FPGA/'docs/workstreams/FLYVIS_LINE2_CAMERA_FINISH_BUDGET_20261016.md'),
    finish_budget=dict(board_idle_s=BOARD_IDLE_S, source_close_within_s=SOURCE_CLOSE_WITHIN_S,
        finish_send_within_s=FINISH_SEND_WITHIN_S, anchor='LAST_NEURAL_REQUEST_START_WORKER_MONOTONIC'),
    accepted_software_package=str(LINE7), accepted_software_archive_sha256=delivery7['archive_SHA256'],
    actual_hardware_status='NOT_PREPARED_NOT_CONNECTED', actual_camera_joint_acceptance='NOT_RUN')
save_new('REQUIREMENTS_TO_LINE7_R2.json', requirements)
sources = source_pins()
for name in ('test_joint_camera.py','test_joint_camera_finish.py'):
    sources[name] = sha(GUI/name)
report = dict(status='PASS_BOUNDED_CPU_INTEGRATION_HARDWARE_NOT_CONNECTED', execution_authority='NONE',
    source_sha256=sources, requirements_sha256=sha(OUT/'REQUIREMENTS_TO_LINE7_R2.json'),
    scope_draft_sha256=sha(OUT/'scope_draft_r2.json'),
    line7_archive_sha256=delivery7['archive_SHA256'], line7_delivered_files_unchanged=len(files7),
    line7_original_results_unchanged=True, original_compute_files_unchanged=len(baseline['preserved_original_compute']),
    original_line7_source_firmware_pins_unchanged=len(old7['files']), intended_line2_protected_differences=protected_differences,
    independent_line7_cpu_recheck=dict(tests=recheck['tests'],elapsed_s=recheck['elapsed_s'],result='line7_recheck/RESULT.json'),
    line2_bounded_checks=load(OUT/'bounded_cpu_result.json'),
    hardware_service='NOT_PREPARED_NOT_CONNECTED', actual_camera_joint_acceptance='NOT_RUN',
    GPU_operations=0,camera_operations=0,GUI_launches=0,board_operations=0,network_operations=0,
    unresolved=['New exact human-approved device scope and current preparation proof',
        'Actual camera close and LAN/ARM/SD deadline behaviour',
        'Actual joint CUDA/camera numerical/display/cleanup check',
        'New camera two-sided final audit integration; PC output remains PENDING_PS_AUDIT'])
save_new('delivery_r2.json', report)
print(json.dumps(dict(status=report['status'], line7_files_verified=len(files7),
    protected_changes=len(protected_differences), original_compute_files_unchanged=report['original_compute_files_unchanged'],
    scope_status=draft['status'], execution_authority='NONE')))

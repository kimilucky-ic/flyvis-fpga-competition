"""Freeze this SOFTWARE delivery and preservation evidence; never starts devices."""
import json
from pathlib import Path
import sys

OUT=Path(__file__).resolve().parent
GUI=OUT.parents[1]
FLY=GUI.parent
sys.path.insert(0,str(GUI))
from live_protocol import Registry,load,sha
from joint_camera_controller import source_pins

reg=Registry()
keys=('full','r_only','decoder','initial','parameters','identity','nodes')
preserved={}
for k in keys:
    pin=reg.pins[k]
    p=reg.path_for(k)
    actual=sha(p)
    if actual!=pin['sha256']:raise ValueError('Frozen compute source changed: '+k)
    preserved[k]=dict(path=str(p),sha256=actual)

sources=source_pins()
for name in ('viewer/competition_joint.js','viewer/competition_stage.js','viewer/fixed_skeleton.js','viewer/index.html','start_joint_camera.ps1'):
    sources[name]=sha(FLY/name)
draft=load(OUT/'scope_draft_r1.json')
if draft['source_sha256']!=source_pins():raise ValueError('Latest draft source pins stale')

fpga=FLY.parent/'fpga'
line7=fpga/'flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/handoff_line2_camera_20261016'
for pin in load(line7/'SOURCE_SHA256.json')['files']:
    if sha(pin['path'])!=pin['sha256']:raise ValueError('Line7 accepted source changed')

report=dict(status='PASS_SOFTWARE_DELIVERY_ONLY',preserved_original_compute=preserved,source_sha256=sources,
    line7_accepted_source_and_firmware_pins_checked=12,
    checks=dict(bounded_regression='54 PASS in bounded_tests_r4.log',targeted='27 PASS in targeted_final.log',
        final_core_progress='12 PASS in final_core_progress.log',JS=load(OUT/'display_fixture/js_result.json')),
    evidence_level='CPU_PROTOCOL_AND_SAVED_DATA_CONSUMER_ONLY',
    browser_acceptance='NOT_RUN',GPU_operations=0,camera_operations=0,GUI_launches=0,board_operations=0,
    actual_camera_joint_acceptance='NOT_RUN',hardware_service='NOT_CONNECTED',
    open_items=['Line7 new camera preparation/normal_finish implementation and software acceptance',
                'New operation-specific human authorization and actual current hardware identities',
                'Actual CUDA camera joint numerical/timing/stop tests and browser draw/recording validation'])
(OUT/'delivery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
requirements=dict(schema='flyvis-line2-camera-joint-requirements/v1',status='SOFTWARE_CONSUMER_READY_PENDING_HARDWARE_ADAPTATION',
    execution_authority='NONE',scope_draft=str(OUT/'scope_draft_r1.json'),scope_draft_sha256=sha(OUT/'scope_draft_r1.json'),
    contract=str(fpga/'docs/workstreams/FLYVIS_LINE2_CAMERA_JOINT_CONTRACT_20261016.md'),
    contract_sha256=sha(fpga/'docs/workstreams/FLYVIS_LINE2_CAMERA_JOINT_CONTRACT_20261016.md'),
    input=dict(source_kind='real_windows_camera',condition_id='CURRENT_CAMERA',values=721,math_dt_s=.005,policy=draft['input_policy']),
    initial=dict(model=draft['model'],full_digest=draft['initial_full_digest'],canonical_H_sha256=draft['initial_H_sha256'],mapping_sha256=draft['mapping_sha256']),
    planned_bounds=dict(max_steps=32,capture_duration_s=30,max_worker_s=180,status='DRAFT_NOT_AUTHORIZED'),
    required_capabilities=dict(camera_joint_contract='flyvis-camera-joint/v1',normal_finish='finish_window/v1'),
    normal_finish=dict(path='/finish_window',authentication='REUSE_LINE7_BOARDCLIENT_HMAC',
        request_fields=['identity','completed_steps','last_unified_commit_sha256','last_txn','reason','source_closed'],
        response_required=['FINISHED_PENDING_AUDIT','matching_count_commit_txn','no_pending','capture_closed','PS_capture_sha256']),
    control='LINE2_SINGLE_CONTROLLER_NO_SECOND_FULL_GPU_WORKER',hardware_operations_performed=0)
(OUT/'REQUIREMENTS_TO_LINE7.json').write_text(json.dumps(requirements,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(status=report['status'],frozen_compute_files=len(preserved),line7_pins=12,
    output=str(OUT/'delivery.json'),execution_authority='NONE')))

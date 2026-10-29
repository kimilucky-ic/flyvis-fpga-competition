"""Bounded local regression and provenance receipt. Never starts a device/service."""
import ast
import difflib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

OUT=Path(__file__).resolve().parent
GUI=OUT.parents[1]
sys.path.insert(0,str(GUI))
import test_joint_draw_handoff as cases

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline=OUT/'before_sources/joint_camera_bridge.py'
spec=importlib.util.spec_from_file_location('draw_handoff_before',baseline)
before=importlib.util.module_from_spec(spec);spec.loader.exec_module(before)
repro_names=['test_handed_snapshot_survives_incoming_cache_eviction',
             'test_exact_verified_repeat_returns_original_receipt_once']
repro=unittest.TestResult()
with patch.object(cases,'JointCameraBridge',before.JointCameraBridge):
    unittest.TestSuite(cases.DrawHandoffTests(name) for name in repro_names).run(repro)
expected=repro.errors+repro.failures
assert len(expected)==2 and all('JOINT_DRAW_EXPIRED_OR_DUPLICATE' in trace for _,trace in expected)
(OUT/'BEFORE_REPRODUCTION.json').write_text(json.dumps(dict(
    evidence_level='CPU_SAVED_ARRAYS_CACHE_AND_HTTP_RECEIPT_SIMULATION_ONLY',
    expected_failures=[dict(test=test.id(),trace=trace) for test,trace in expected],
    interpretation='Both old-code failure paths reproduced; the actual failed request serial was not recorded, so its exact branch remains unknown.'),
    ensure_ascii=False,indent=2),encoding='utf-8')

names=['test_joint_draw_handoff','test_joint_diagnostics.DrawLockTests',
       'test_joint_camera_completed.FinalSnapshotTests']
suite=unittest.defaultTestLoader.loadTestsFromNames(names)
log=io.StringIO()
result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
(OUT/'cpu_tests.log').write_text(log.getvalue(),encoding='utf-8')
print(log.getvalue())
assert result.wasSuccessful()

old=json.loads((GUI/'evidence/fixed_camera_one_minute_20261018/VERIFICATION.json').read_text(encoding='utf-8'))
guard_names={'FlyVis.exe','FlyVis摄像头联合实验.ipynb','joint_minimal_core.py','joint_minimal_worker.py',
    'joint_minimal_board.py','joint_camera_protocol.py','joint_camera_fixed_board.py',
    'joint_camera_repeat.py','competition_joint.js','joint_camera_fixed.py'}
protected=[]
for row in old['files']:
    p=Path(row['path'])
    if p.name in guard_names:
        assert sha(p)==row['sha256'],p.name+' changed against prior delivery'
        protected.append(dict(path=str(p),sha256=sha(p)))
assert {'FlyVis.exe','FlyVis摄像头联合实验.ipynb','joint_minimal_worker.py','joint_minimal_board.py'}<={Path(row['path']).name for row in protected}

ast.parse((GUI/'joint_camera_bridge.py').read_text(encoding='utf-8'))
after=GUI/'joint_camera_bridge.py'
(OUT/'PRODUCTION.diff').write_text(''.join(difflib.unified_diff(
    baseline.read_text(encoding='utf-8').splitlines(keepends=True),
    after.read_text(encoding='utf-8').splitlines(keepends=True),
    fromfile='before/joint_camera_bridge.py',tofile='after/joint_camera_bridge.py')),encoding='utf-8')
run=GUI/'runtime/joint/6f7b1a68ac8d40029926b04a8a4bc327'
state=json.loads((run/'result.json').read_text(encoding='utf-8'))
scope=json.loads((run/'scope.json').read_text(encoding='utf-8'))
assert state['status']=='FAILED_OR_IN_DOUBT' and state['committed_steps']==1376
assert not (run/'AUTO_ACCEPTANCE.json').exists()
receipt=dict(status='PASS_FOCUSED_SOFTWARE_DRAW_HANDOFF_CHECKS_ONLY',
    evidence_level='CPU_SAVED_REAL_ARRAYS_STATIC_PIXEL_REFERENCE_AND_MOCKED_CACHE_IO',
    tests_passed=result.testsRun,old_failure_paths_reproduced=2,
    exact_live_failure_branch='UNKNOWN_NOT_RECORDED',
    production_files_changed=[dict(path=str(after),sha256=sha(after),before_sha256=sha(baseline))],
    protected_against_prior_delivery=protected,
    data_fixture=dict(path=str(cases.HERE/'runtime/joint/f2fd7b4d54a4445daa8a15065c60088e/final_snapshot.json'),
        sha256=sha(cases.HERE/'runtime/joint/f2fd7b4d54a4445daa8a15065c60088e/final_snapshot.json')),
    original_60s_run=dict(run_id=scope['run_id'],status=state['status'],committed_steps=1376,
        result_sha256=sha(run/'result.json'),auto_acceptance_present=False,modified=False),
    model_or_precision_changes=False,COMMIT_ACK_changes=False,
    board_connections=0,GPU_runs=0,camera_runs=0,GUI_launches=0,network_listeners=0,
    actual_device_retest='NOT_RUN',REALTIME_STREAM_PASS='NOT_CLAIMED',
    rollback='Restore before_sources/joint_camera_bridge.py after normally closing the PC workbench. No board rollback is needed.',
    next_action='User-scheduled fresh bounded run; do not resume or retrofit acceptance into the failed run.')
(OUT/'VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(receipt['status'],result.testsRun)

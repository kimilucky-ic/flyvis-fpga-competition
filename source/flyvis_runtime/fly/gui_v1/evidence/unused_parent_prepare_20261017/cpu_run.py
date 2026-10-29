"""Bounded preparation checks only. Reject every real socket and connection."""
import json,sys,time,unittest
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parents[1]))
import test_joint_camera_manual as manual
manual.OUT=P/'legacy_checks';manual.fixtures.RESULTS=P/'fixture';(manual.fixtures.RESULTS/'scratch').mkdir(parents=True,exist_ok=True)
import test_joint_camera_completed as completed
completed.OUT=P/'legacy_checks'
suite=unittest.defaultTestLoader.loadTestsFromNames(['test_joint_camera_unused',
    'test_joint_camera_manual.TransferTests','test_joint_camera_manual.SecondZeroStepTransferTests','test_joint_camera_manual.ManualTests',
    *['test_joint_camera_completed.CompletedTransferTests.'+n for n in (
        'test_completed_parent_preserved_read20_zero_writes','test_uncertain_failed_pending_or_running_parent_refused',
        'test_wrong_capture_or_final_commit_refused_before_reads','test_used_parent_claim_is_never_cleared_or_reused')]])
start=time.perf_counter()
with patch('socket.create_connection',side_effect=AssertionError('CPU_ONLY_NO_NETWORK')),patch('socket.socket',side_effect=AssertionError('CPU_ONLY_NO_SOCKET')):
    with (P/'CPU_TESTS.log').open('x',encoding='utf8') as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
v=dict(status='PASS_CPU_ONLY' if result.wasSuccessful() else 'FAILED',tests=result.testsRun,
    failures=len(result.failures),errors=len(result.errors),elapsed_s=time.perf_counter()-start,
    real_sockets=0,board_connections=0,real_MMIO=0,GPU_runs=0,camera_starts=0,GUI_starts=0,
    live_scopes=0,CPU_ONLY_archives=1,evidence='Fake retained objects and fake registers, admitted historical capture read-only; not board preparation or a neural run')
(P/'CPU_RESULT.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v,indent=2));sys.exit(not result.wasSuccessful())

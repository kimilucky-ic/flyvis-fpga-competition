"""Stale launch recovery with CPU fixtures; no process/port/device is started."""
import os
from pathlib import Path
import tempfile
import unittest

from launch_recovery import inspect_stale_launch,recover_stale_launch,process_alive
from live_protocol import HERE,load,write


class Recovery(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=HERE/'runtime');self.directory=Path(self.temp.name)
        self.base=self.directory/'live';self.sid='a'*32;self.root=self.base/self.sid;self.root.mkdir(parents=True)
        self.active=self.directory/'demo_active.json'
        self.state=dict(state='RUNNING',session_id=self.sid,root=str(self.root),pid=123456,gpu_enabled=True,
            children=[dict(name='gui',pid=123457),dict(name='worker',pid=123458),dict(name='desktop',pid=123459)])
        write(self.active,self.state)
        write(self.root/'session.json',dict(session_id=self.sid,gpu_enabled=True))
        write(self.root/'controller.json',dict(session_id=self.sid,pid=123456,unix_time=100))
        write(self.root/'heartbeat.json',dict(session_id=self.sid,state='STOPPED',device=None,error=None))
        write(self.root/'worker_exit.json',dict(session_id=self.sid,exit_code=0))
        write(self.root/'worker_shutdown.json',dict(CUDA_synchronized=True,shared_lock_closed=True))
        self.checks=dict(base=self.base,alive=lambda pid:False,port_free=lambda:True,now=200)
    def tearDown(self):self.temp.cleanup()
    def recover(self,**overrides):return recover_stale_launch(self.active,**{**self.checks,**overrides})
    def reject(self,error,**overrides):
        before=self.active.read_bytes()
        with self.assertRaisesRegex((ValueError,PermissionError),error):self.recover(**overrides)
        self.assertEqual(self.active.read_bytes(),before)

    def test_verified_orphan_recovers_and_preserves_exact_original_marker(self):
        before=self.active.read_bytes();exit_before=(self.root/'worker_exit.json').read_bytes()
        proof=self.recover();state=load(self.active)
        self.assertEqual(state['state'],'STOPPED');self.assertEqual(proof['processes_killed'],0)
        backup=Path(state['recovery_evidence']).parent
        self.assertEqual((backup/'demo_active.before.json').read_bytes(),before)
        self.assertEqual((self.root/'worker_exit.json').read_bytes(),exit_before)
        self.assertNotIn('exit_codes',state)

    def test_live_owner_is_never_overridden(self):self.reject('进程仍在运行',alive=lambda pid:pid==123456)
    def test_live_child_or_reused_pid_is_never_killed(self):self.reject('进程仍在运行',alive=lambda pid:pid==123459)
    def test_fresh_controller_prevents_recovery(self):self.reject('新心跳',now=110)
    def test_unknown_process_access_prevents_recovery(self):
        def denied(pid):raise PermissionError('CPU_TEST_ACCESS_DENIED')
        self.reject('ACCESS_DENIED',alive=denied)
    def test_occupied_or_unverified_port_prevents_recovery(self):self.reject('PORT_UNKNOWN',port_free=lambda:False)
    def test_missing_cuda_ack_prevents_recovery(self):
        write(self.root/'worker_shutdown.json',dict(CUDA_synchronized=False,shared_lock_closed=True))
        self.reject('CUDA_RELEASE_UNKNOWN')
    def test_wrong_exit_session_prevents_recovery(self):
        write(self.root/'worker_exit.json',dict(session_id='b'*32,exit_code=0));self.reject('WORKER_EXIT_UNKNOWN')
    def test_worker_failure_is_preserved_for_inspection(self):
        write(self.root/'worker_exit.json',dict(session_id=self.sid,exit_code=1));self.reject('WORKER_EXIT_UNKNOWN')
    def test_cross_scope_root_is_rejected(self):
        self.state['root']=str(self.directory/'elsewhere'/self.sid);write(self.active,self.state);self.reject('WRITE_SCOPE')
    def test_gpu_scope_cannot_be_downgraded_to_skip_release(self):
        self.state['gpu_enabled']=False;write(self.active,self.state);self.reject('GPU_SCOPE_IDENTITY')
    def test_current_session_controller_is_required(self):
        write(self.root/'controller.json',dict(session_id='b'*32,pid=123456,unix_time=100));self.reject('CONTROLLER_IDENTITY')
    def test_terminal_marker_is_idempotent_and_no_os_probe_runs(self):
        self.state['state']='STOPPED';write(self.active,self.state)
        def forbidden(*a):raise AssertionError('NO_PROBE_EXPECTED')
        self.assertIsNone(self.recover(alive=forbidden,port_free=forbidden))
    def test_concurrent_marker_change_during_probe_is_not_overwritten(self):
        def changed():
            write(self.active,{**self.state,'session_id':'b'*32});return True
        with self.assertRaisesRegex(ValueError,'MARKER_CHANGED'):self.recover(port_free=changed)
        self.assertEqual(load(self.active)['session_id'],'b'*32)
    def test_current_process_is_detected_read_only(self):self.assertTrue(process_alive(os.getpid()))


if __name__=='__main__':unittest.main()

"""CPU-only owned GUI lifecycle checks. No listener, browser or device launch."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from operator_selection import Selection,reconnect_owned,HERE


class ExitTests(unittest.TestCase):
    def setUp(self):
        base=HERE/'evidence/operator_exit_20261021';base.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=base);self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.s=Selection(self.root)
        self.body=dict(root_id=self.root.name)

    def test_window_close_exits_idle_after_reload_grace(self):
        self.s.activity(self.body,now=100)
        self.s.activity(self.body,detached=True,now=101)
        self.assertFalse(self.s.idle_closed(now=130))
        self.assertTrue(self.s.idle_closed(now=131))

    def test_reload_or_handoff_does_not_close_new_page(self):
        self.s.activity(self.body,now=100);self.s.activity(self.body,detached=True,now=101)
        self.s.activity(self.body,now=102)
        self.assertFalse(self.s.idle_closed(now=106))

    def test_document_reopen_before_slow_assets_cancels_detach(self):
        self.s.activity(self.body,now=100)
        self.s.activity(self.body,detached=True,now=101)
        self.s.activity(self.body,now=105)  # GET / before scripts load
        self.assertFalse(self.s.idle_closed(now=135))

    def test_lost_beacon_recovers_idle_with_heartbeat_timeout(self):
        self.s.activity(self.body,now=100)
        self.assertFalse(self.s.idle_closed(now=219))
        self.assertTrue(self.s.idle_closed(now=221))

    def test_selected_backend_never_uses_idle_force_shutdown(self):
        (self.root/'CURRENT.json').write_text('{}')
        self.s.activity(self.body,detached=True,now=100)
        self.assertFalse(self.s.idle_closed(now=1000))

    def test_stale_tab_cannot_touch_a_new_session(self):
        with self.assertRaises(ValueError):self.s.activity(dict(root_id='wrong'),detached=True)
        self.assertFalse((self.root/'DETACHED.json').exists())

    def test_partial_heartbeat_file_cannot_crash_or_close_server(self):
        (self.root/'BROWSER.json').write_text('{')
        self.assertFalse(self.s.idle_closed(now=1000))

    def reconnect(self,owner,record=None):
        record=record or dict(schema='flyvis-operator-owner/v1',root_id='a'*32,child_pid=123)
        active=self.root/'ACTIVE.json';active.write_text(json.dumps(record))
        opened=[]
        ok=reconnect_owned(active,opener=lambda *a,**k:io.BytesIO(json.dumps(owner).encode()),open_browser=opened.append)
        return ok,opened

    def test_reopen_existing_idle_server_without_new_process(self):
        ok,opened=self.reconnect(dict(schema='flyvis-operator-owner/v1',root_id='a'*32,server_pid=123,parent_pid=99,closing=False))
        self.assertTrue(ok);self.assertEqual(len(opened),1)

    def test_reopen_original_joint_child_without_new_gpu_run(self):
        ok,opened=self.reconnect(dict(schema='flyvis-operator-owner/v1',root_id='a'*32,server_pid=456,parent_pid=123,closing=False))
        self.assertTrue(ok);self.assertEqual(len(opened),1)

    def test_unknown_owner_changed_pid_and_closing_never_reused(self):
        for change in (dict(root_id='b'*32),dict(server_pid=456,parent_pid=789),dict(closing=True)):
            owner=dict(schema='flyvis-operator-owner/v1',root_id='a'*32,server_pid=123,parent_pid=99,closing=False)
            owner.update(change)
            ok,opened=self.reconnect(owner)
            self.assertFalse(ok);self.assertFalse(opened)


if __name__=='__main__':unittest.main()

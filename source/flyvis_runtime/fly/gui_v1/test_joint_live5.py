"""Changed live5 paths only: CPU saved-data/protocol tests, no device opens."""
import copy
import tempfile
import threading
import unittest
from unittest.mock import patch
from live_protocol import HERE,load
from joint_camera_protocol import LatestCameraInput,validate_snapshot,validate_scope
from joint_camera_bridge import JointCameraBridge
from spatial_state import SpatialRegistry

class Live5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=load(HERE/'runtime/joint/f2fd7b4d54a4445daa8a15065c60088e/final_snapshot.json')
        cls.spatial=SpatialRegistry()

    def packet(self):
        p=copy.deepcopy(self.original)
        p.update(runtime_policy='MINIMAL_COMPUTE_ASYNC_V1',live_response_hz=5,
            display_kind='LIVE_LOW_RATE_LATEST_COMMITTED_STATE',evidence_level='ACK_MATCHED_RAM_ONLY_ASYNC_RECORDING')
        p['transaction'].update(integer_error=None,numerical_check='DEFERRED_OFFLINE')
        p['durable']=dict(barrier='NOT_SYNCHRONOUS',recording=dict(complete=False))
        identity={k:p[k] for k in ('run_id','session_id','model','mapping_sha256','hardware','runtime_policy','live_response_hz')}
        return p,identity

    def test_same_commit_saved_arrays_accepted_at_live5(self):
        p,i=self.packet();validate_snapshot(p,i,self.spatial)

    def test_mixed_run_wrong_time_and_false_pass_rejected(self):
        for edit in (lambda p:p.update(run_id='0'*32),lambda p:p.update(activity_time_s=1),
            lambda p:p.update(REALTIME_STREAM_PASS='PASS'),lambda p:p.update(live_response_hz=20),
            lambda p:p.update(display_kind='POST_COMPUTE_SAME_RUN_NOT_REALTIME')):
            p,i=self.packet();edit(p)
            with self.assertRaises((ValueError,KeyError)):validate_snapshot(p,i,self.spatial)

    def test_latest_raw_conversion_never_builds_step_queue(self):
        p,_=self.packet();mail=LatestCameraInput(p['run_id'])
        for k in range(10):
            item=dict(source=copy.deepcopy(p['source']),png=p['preview_png'],values=p['input_hex'],conversion=p['conversion'])
            item['source'].update(sequence=k,relative_s=p['source']['relative_s']+k*.01,
                received_monotonic_ns=p['source']['received_monotonic_ns']+k)
            mail.receive(dict(source=item['source'],png=item['png']))
            raw=mail.take_raw();mail.accept_conversion(item)
        selected=mail.freeze_for_step();self.assertEqual(selected['source']['sequence'],9)
        self.assertEqual(mail.freeze_for_step()['source']['sequence'],9)
        self.assertIsNone(mail.raw)

    def test_preview_cache_is_separate_revoked_on_stop_or_error(self):
        p,_=self.packet();b=JointCameraBridge()
        b.scope=dict(run_id=p['run_id'],session_id=p['session_id'])
        b.control=True;b.capture_closed=False
        b.preview_packet=dict(source=p['source'],png=p['preview_png'])
        self.assertTrue(b.preview()['live_preview']);self.assertIsNone(b.packet)
        b.error='TEST';self.assertIsNone(b.preview()['packet'])
        b.error=None;b.stop_event.set();self.assertFalse(b.preview()['live_preview'])

    def test_camera_burst_overwrites_pending_frames_and_holds_latest_without_wait(self):
        p,_=self.packet();mail=LatestCameraInput(p['run_id'])
        def raw(k):
            source=dict(p['source'],sequence=k,relative_s=p['source']['relative_s']+k*.01,
                received_monotonic_ns=p['source']['received_monotonic_ns']+k)
            return dict(source=source,png=p['preview_png'])
        mail.receive(raw(0));first=mail.take_raw()
        # Camera outruns conversion: only the newest raw frame remains pending.
        for k in range(1,20):mail.receive(raw(k))
        self.assertIsNone(mail.take_raw())
        mail.accept_conversion(dict(first,values=p['input_hex'],conversion=p['conversion']))
        self.assertEqual(mail.freeze_for_step()['source']['sequence'],0)
        latest=mail.take_raw();self.assertEqual(latest['source']['sequence'],19)
        mail.accept_conversion(dict(latest,values=p['input_hex'],conversion=p['conversion']))
        for _ in range(50):self.assertEqual(mail.freeze_for_step()['source']['sequence'],19)
        self.assertIsNone(mail.take_raw());self.assertEqual(mail.dropped_raw,18)

    def test_exact_finished_compute_parent_builds_fresh_live5_scope(self):
        from joint_camera_bundle import preparation_parent,build,audited_compute_parent
        root=HERE/'runtime/joint/40feba4eb4ae49fca7d1df686cb62b0f'
        old=dict(state='STOPPED',run_id='1e1a77c8a6ba459cb3b79a9447cec3c8',
            session_id=root.name,root=str(root),exit_codes=dict(gui=0,joint_worker=1))
        parent=audited_compute_parent(old,root)
        self.assertEqual(parent['completed_fresh']['run_id'],'1e1a77c8a6ba459cb3b79a9447cec3c8')
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as folder:
            from pathlib import Path
            root,_=build(Path(folder),**parent,minimal_compute=True,live5=True,cpu_fixture=True)
            s=load(root/'scope.json');c=load(root/'PRIVATE_CONFIG.json')
            self.assertEqual(s['max_steps'],100);self.assertEqual(s['dt_s'],.005)
            self.assertEqual(c['live_response_hz'],s['live_response_hz'])
            self.assertEqual(c['new_loads']+c['new_resets']+c['new_allocations'],0)
            s.update(status='APPROVED_BY_HUMAN',human_authorization_reference='CPU_TEST')
            validate_scope(s)
            s['live_response_hz']=20
            with self.assertRaises(ValueError):validate_scope(s)
        # A fixed known-run fixture must not depend on the user's mutable run.
        active=dict(old,state='RUNNING')
        with self.assertRaisesRegex(ValueError,'NOT_STOPPED'):
            audited_compute_parent(active,root)

    def test_new_live100_acceptance_is_explicit_and_requires_closed_PC(self):
        from joint_camera_bundle import audited_compute_parent
        root=HERE/'runtime/joint/c59286b40c9c4c2e84a3e456a0856540'
        cpu=dict(state='STOPPED',run_id='ad5b4adac2b941f59b4a5271d1bde1fe',
            session_id=root.name,root=str(root),exit_codes=dict(gui=0,joint_worker=0))
        parent=audited_compute_parent(cpu,root)
        self.assertEqual(parent['completed_fresh']['completed_steps'],100)
        cpu['state']='RUNNING'
        with self.assertRaisesRegex(ValueError,'NOT_STOPPED'):audited_compute_parent(cpu,root)
        cpu['run_id']='a'*32
        with self.assertRaisesRegex(ValueError,'UNKNOWN_RUN'):audited_compute_parent(cpu,root)

if __name__=='__main__':unittest.main()

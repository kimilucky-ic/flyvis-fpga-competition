"""Finite CPU-only tests: no GPU, camera, GUI app, board or network session."""
import ast,copy,hashlib,io,json,os,threading,time,unittest,uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
from live_protocol import HERE,load,sha
from joint_diagnostics import JointDiagnostics,TimedJournal,measured_sync
from joint_camera_bridge import JointCameraBridge
from joint_camera_control import hardware_module

OUT=HERE/'evidence/joint_software_timing_20261016'

class DiagnosticTests(unittest.TestCase):
    def case(self):
        p=OUT/'cpu_cases'/uuid.uuid4().hex;p.mkdir(parents=True);return p
    def test_bounded_nested_spans_and_failure_preserve_exception(self):
        d=JointDiagnostics('CPU_TEST',capacity=2)
        with d.step(15):
            with self.assertRaisesRegex(OSError,'ORIGINAL_ERROR'):
                d.call('CPU.failure',lambda:(_ for _ in ()).throw(OSError('ORIGINAL_ERROR')))
        d.call('overflow',lambda:None)
        r=d.save(self.case()/'trace.json','CPU_SESSION','cpu_run')
        self.assertEqual(len(r['spans']),2);self.assertEqual(r['dropped_spans'],1)
        self.assertFalse(r['diagnostic_complete']);self.assertTrue(r['spans'][0]['failed'])
        self.assertEqual(r['spans'][0]['step_id'],15);self.assertIsNone(d.step_id)
    def test_writer_bytes_barriers_and_fsync_count_identical(self):
        root=self.case();h=load(HERE/'runtime/joint/7f111da4437843539eeffef2c6c2546e/hardware_handoff.json')
        module=hardware_module(h,'evidence_journal');calls=[[],[]];writers=[];d=JointDiagnostics('CPU_TEST')
        for index in range(2):
            sync=lambda fd,index=index:calls[index].append('fsync')
            w=module.JournalWriter(root/str(index),dict(role='CPU_ONLY'),sync=measured_sync(d,sync) if index else sync)
            if index:w=TimedJournal(w,d)
            w.add('raw.bin',bytes(range(256))*8);w.checkpoint('BEFORE_SEND')
            w.add('commit.json',b'{"COMMIT":1}');w.checkpoint('COMMIT_INTENT')
            w.add('ack.bin',b'EXACT_ACK');w.checkpoint('COMMIT_ACK');w.checkpoint('STEP_PUBLISHED')
            w.close('CPU_TEST_COMPLETE',completed=1);writers.append(w)
        self.assertEqual(writers[0].path.read_bytes(),writers[1].path.read_bytes())
        self.assertEqual(calls[0],calls[1]);self.assertEqual(len(calls[0]),6)
        self.assertEqual(len([r for r in d.rows if r['name']=='PC_journal.fsync']),6)
        self.assertEqual(module.JournalReader(writers[1].path).terminal['completed'],1)
    def test_sync_failure_is_not_retried_or_converted_to_success(self):
        root=self.case();h=load(HERE/'runtime/joint/7f111da4437843539eeffef2c6c2546e/hardware_handoff.json')
        mod=hardware_module(h,'evidence_journal');d=JointDiagnostics('CPU_TEST');calls=[]
        def sync(fd):
            calls.append(fd)
            if len(calls)==2:raise OSError('CPU_SYNC_INJECTED_FAILURE')
        w=TimedJournal(mod.JournalWriter(root/'pc',{},sync=measured_sync(d,sync)),d)
        try:
            with self.assertRaisesRegex(OSError,'INJECTED_FAILURE'):w.checkpoint('COMMIT_ACK')
            self.assertTrue(w.poisoned)
            with self.assertRaisesRegex(RuntimeError,'poisoned'):w.checkpoint('STEP_PUBLISHED')
            self.assertEqual(len(calls),2)
        finally:w.abandon()
    def test_GPU_tensor_and_sync_operations_unchanged_after_timing_unwrap(self):
        baseline=HERE/'evidence/camera_joint32_20261016/executed_sources/hybrid_gpu.py'
        class Unwrap(ast.NodeTransformer):
            def visit_With(self,node):
                node=self.generic_visit(node)
                if len(node.items)==1 and isinstance(node.items[0].context_expr,ast.Call):
                    f=node.items[0].context_expr.func
                    if isinstance(f,ast.Attribute) and f.attr=='measure':return node.body
                return node
        a=Unwrap().visit(ast.parse(baseline.read_text(encoding='utf8')))
        b=Unwrap().visit(ast.parse((HERE/'hybrid_gpu.py').read_text(encoding='utf8')))
        self.assertEqual(ast.dump(a,include_attributes=False),ast.dump(b,include_attributes=False))
    def test_enabled_trace_preserves_saved_three_step_feedback(self):
        from test_joint_camera import CameraJointTests
        CameraJointTests.setUpClass()
        case=CameraJointTests('test_three_step_original_coordinator_feedback_and_durable_snapshots');case.setUp()
        d=JointDiagnostics('CPU_SAVED_PROTOCOL')
        case.engine.diagnostics=d;case.ev.diagnostics=d
        case.ev.writer.sync_fn=measured_sync(d,case.ev.writer.sync_fn)
        case.ev.writer=TimedJournal(case.ev.writer,d)
        try:
            case.test_three_step_original_coordinator_feedback_and_durable_snapshots()
            names={r['name'] for r in d.rows}
            self.assertTrue({'GPU.produce_inclusive','CPU.same_old_reference','hardware.STEP_roundtrip_inclusive',
                'hardware.COMMIT_roundtrip_inclusive','coordinator.ACK_durable_publish','PC_journal.fsync'}<=names)
            cycles=[r for r in d.rows if r['name']=='engine.step_total']
            self.assertEqual(sum(not r['failed'] for r in cycles),3)
            self.assertEqual(sum(r['failed'] for r in cycles),1) # Fixture also checks step-limit rejection.
            self.assertEqual(case.engine.barrier.state_token,3)
            d.save(self.case()/'enabled_saved_protocol_trace.json','CPU_SESSION','CPU_SAVED_ONLY')
        finally:case.tearDown()


class DrawLockTests(unittest.TestCase):
    def fixture(self):
        root=OUT/'draw_cases'/uuid.uuid4().hex;root.mkdir(parents=True)
        b=JointCameraBridge();b.path=root/'CPU_SESSION';b.root=root;b.scope=dict(run_id='cpu_run',session_id='CPU_SESSION')
        b.validate=lambda p:None;b.diagnostics=JointDiagnostics('CPU_GUI')
        rgba=np.zeros((2,2,4),dtype=np.uint8);pixels=hashlib.sha256(rgba.tobytes()).hexdigest()
        b.cached=SimpleNamespace(sha256='1'*64,render=lambda values,geometry:(rgba,[]));b.geometry={}
        p=dict(run_id='cpu_run',session_id='CPU_SESSION',step_id=0,state_token=1,serial=1,
            transaction=dict(unified_commit_sha256='2'*64),source=dict(png_sha256='3'*64,received_monotonic_ns=time.perf_counter_ns()-1000000),
            spatial=dict(values=[0.]*5768,values_sha256='4'*64),flow_sha256='5'*64)
        b.packets[1]=p
        body=dict(run_id=p['run_id'],session_id=p['session_id'],step_id=0,state_token=1,serial=1,
            unified_commit_sha256='2'*64,source_png_sha256='3'*64,spatial_values_sha256='4'*64,flow_sha256='5'*64,
            projection_cache_sha256='1'*64,skeleton_raw_sha256=pixels,clock_age_s=0.,draw_server_monotonic_ns=time.perf_counter_ns(),clock_uncertainty_ms=0.)
        return b,body
    def test_blocked_fsync_does_not_hold_snapshot_lock_or_return_early_ACK(self):
        b,body=self.fixture();entered=threading.Event();release=threading.Event();done=threading.Event();rows=[]
        real_sync=os.fsync
        def blocked(fd):
            entered.set()
            if not release.wait(2):raise TimeoutError('CPU_TEST_RELEASE_TIMEOUT')
            return real_sync(fd)
        def run():
            try:rows.append(b.record_draw(body))
            except BaseException as error:rows.append(error)
            finally:done.set()
        with patch('joint_camera_bridge.os.fsync',side_effect=blocked):
            thread=threading.Thread(target=run);thread.start()
            try:
                self.assertTrue(entered.wait(2));self.assertFalse(done.is_set());self.assertNotIn(1,b.drawn)
                acquired=b.lock.acquire(timeout=.1)
                self.assertTrue(acquired,'The next snapshot must not wait for draw fsync')
                if acquired:b.lock.release()
                with self.assertRaisesRegex(ValueError,'DUPLICATE'):b.record_draw(body)
            finally:release.set();thread.join(2)
        self.assertTrue(done.is_set());self.assertEqual(rows[0]['status'],'DRAW_IDENTITY_AND_PIXELS_VERIFIED')
        self.assertIn(1,b.drawn);self.assertEqual(b.draw_pending,set())
    def test_draw_fsync_error_never_marks_receipt_as_verified(self):
        b,body=self.fixture()
        with patch('joint_camera_bridge.os.fsync',side_effect=OSError('CPU_DRAW_SYNC_FAILED')):
            with self.assertRaisesRegex(OSError,'CPU_DRAW_SYNC_FAILED'):b.record_draw(body)
        self.assertNotIn(1,b.drawn);self.assertFalse(b.draw_pending)

if __name__=='__main__':unittest.main()

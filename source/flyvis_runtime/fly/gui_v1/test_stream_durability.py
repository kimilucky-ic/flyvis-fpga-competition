"""CPU fault injection only. Candidates are identity tokens, not neural activity."""
import json
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from stream_evidence import CommitJournal,EvidenceWriter
from realtime_timing import Timings
from stream_runtime import StreamHub
from stream_manual_summary import manual_summary
from desktop_live import ManagedDesktopBackend
from live_protocol import HERE,load,write


class Durability(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=HERE/'runtime');self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def row(self,k):
        return dict(run_id='CPU_PROTOCOL_TEST_ONLY',step_id=k,state_token=k+1,status='COMMITTED',source_sequence=0)
    def accept(self,j,k):
        token=j.prepare(self.row(k));candidate=object()
        self.assertIs(j.accept(token,candidate,lambda *a:None,lambda c:c),candidate)
    def test_saved_asset_byte_count_uses_actual_files(self):
        import base64,numpy as np
        s=HERE/'runtime/live/af1d19116be744b4a6c2ef009c94ca0b/stream'
        p=sorted((s/'sources').glob('*.json'))[0];source=load(p)
        w=EvidenceWriter.__new__(EvidenceWriter);w.root=self.root;w.bytes=0;w.timing=Timings()
        w._save('source',dict(source=source,png=base64.b64encode(p.with_suffix('.png').read_bytes()).decode(),
                             values=np.load(p.with_name(p.stem+'_hex.npy'),allow_pickle=False)))
        p=sorted((s/'snapshots').glob('*.json'))[0];packet=load(p)
        with np.load(p.with_suffix('.npz'),allow_pickle=False) as z:
            packet.update(input_hex=z['input'],flow=z['flow'])
            w._save('snapshot',(packet,z['full']))
        self.assertEqual(w.bytes,sum(p.stat().st_size for p in self.root.rglob('*') if p.is_file()))
        with patch('stream_evidence.STORAGE_LIMIT_BYTES',1):
            with self.assertRaisesRegex(ValueError,'STREAM_EVIDENCE_STORAGE_LIMIT'):w._save('snapshot',(packet,np.load(p.with_suffix('.npz'))['full']))
    def test_1344_steps_no_missing_tail(self):
        j=CommitJournal(self.root/'step_commits.jsonl')
        for k in range(1344):
            self.accept(j,k)
            if j.pending==j.capacity:j.flush()
        self.assertEqual(j.durable_steps,1340);self.assertEqual(j.accepted_steps,1344)
        j.close();rows=[json.loads(x) for x in (self.root/'step_commits.jsonl').read_text().splitlines()]
        self.assertEqual([r['step_id'] for r in rows],list(range(1344)));self.assertEqual(j.durable_steps,1344)
    def test_no_public_commit_before_fsync(self):
        j=CommitJournal(self.root/'steps');self.accept(j,0)
        def sync(fd):self.assertEqual(j.durable_steps,0)
        with patch('stream_evidence.os.fsync',side_effect=sync):self.assertEqual(j.flush(),1)
        j.close()
    def test_fsync_failure_never_advances_watermark(self):
        j=CommitJournal(self.root/'steps');self.accept(j,0)
        with patch('stream_evidence.os.fsync',side_effect=OSError('CPU injected disk failure')):
            with self.assertRaises(OSError):j.flush()
        self.assertEqual(j.durable_steps,0);self.assertEqual(j.accepted_steps,1);self.assertIsNotNone(j.error)
        with self.assertRaises(ValueError):j.prepare(self.row(1))
        with self.assertRaises(ValueError):j.close()
        self.assertTrue(j.closed)
    def test_short_write_is_completed_before_ack(self):
        j=CommitJournal(self.root/'steps');self.accept(j,0);original=j.file
        wrapper=SimpleNamespace(write=lambda x:original.write(x[:7]),fileno=original.fileno,close=original.close)
        j.file=wrapper;j.close();self.assertEqual(j.durable_steps,1)
        self.assertEqual(json.loads((self.root/'steps').read_text())['step_id'],0)
    def test_zero_write_fails_without_public_commit(self):
        j=CommitJournal(self.root/'steps');self.accept(j,0);original=j.file
        j.file=SimpleNamespace(write=lambda x:0,fileno=original.fileno,close=original.close)
        with self.assertRaisesRegex(ValueError,'SHORT_WRITE'):j.flush()
        self.assertEqual(j.durable_steps,0)
        with self.assertRaises(ValueError):j.close()
    def test_reservation_full_before_calculation(self):
        j=CommitJournal(self.root/'steps',batch_steps=1);self.accept(j,0)
        with self.assertRaisesRegex(ValueError,'BEFORE_COMPUTE'):j.prepare(self.row(1))
        self.assertEqual(j.accepted_steps,1);j.close()
    def test_revoked_or_invalid_candidate_not_recorded(self):
        j=CommitJournal(self.root/'steps');token=j.prepare(self.row(0));commits=[]
        def revoked(*a):raise ValueError('CPU_CANCEL')
        with self.assertRaisesRegex(ValueError,'CPU_CANCEL'):j.accept(token,object(),revoked,commits.append)
        self.assertEqual(commits,[]);self.assertEqual(j.accepted_steps,0);j.cancel(token)
        token=j.prepare(self.row(0))
        with self.assertRaisesRegex(ValueError,'CPU_CANCEL'):j.accept(token,object(),lambda *a:None,revoked)
        j.cancel(token);j.close();self.assertEqual((self.root/'steps').read_bytes(),b'')
    def test_duplicate_foreign_ticket_rejected(self):
        j=CommitJournal(self.root/'steps');t=j.prepare(self.row(0))
        with self.assertRaises(ValueError):j.accept((object(),b''),None,lambda *a:None,lambda c:c)
        j.accept(t,None,lambda *a:None,lambda c:c)
        with self.assertRaises(ValueError):j.accept(t,None,lambda *a:None,lambda c:c)
        j.close()
    def test_slow_assets_cannot_steal_step_slots(self):
        started=threading.Event();release=threading.Event()
        class Slow(EvidenceWriter):
            def _save(self,kind,value):started.set();release.wait(2)
        w=Slow(self.root,capacity=1);j=CommitJournal(self.root/'steps')
        try:
            w.put('source',None);self.assertTrue(started.wait(1))
            with self.assertRaisesRegex(ValueError,'BEFORE_COMPUTE'):w.reserve('snapshot',timeout=.001)
            for k in range(4):self.accept(j,k)
            j.close();self.assertEqual(j.durable_steps,4)
        finally:release.set();w.close()
        self.assertEqual(w.info()['saved_assets'],1)
    def test_reservation_cancel_and_duplicate_submit(self):
        class NoIO(EvidenceWriter):
            def _save(self,*a):pass
        w=NoIO(self.root,capacity=1)
        t=w.reserve('snapshot');w.cancel(t);t=w.reserve('source');w.submit(t,None)
        with self.assertRaises(ValueError):w.submit(t,None)
        w.close();self.assertEqual(w.info()['reserved'],0)
    def test_asset_disk_failure_does_not_lose_commit_log(self):
        done=threading.Event()
        class Broken(EvidenceWriter):
            def _save(self,*a):done.set();raise OSError('CPU_ASSET_DISK_FAILURE')
        w=Broken(self.root,1);j=CommitJournal(self.root/'steps');self.accept(j,0);w.put('snapshot',None)
        self.assertTrue(done.wait(1));w.thread.join(1);j.close()
        self.assertEqual(j.durable_steps,1)
        with self.assertRaisesRegex(ValueError,'WRITE_FAILED'):w.reserve('source')
        with self.assertRaisesRegex(ValueError,'CLOSE_FAILED'):w.close()
    def test_first_failure_not_overwritten_by_stop(self):
        h=StreamHub('test');h.revoke('CPU_FIRST_DISK_FAILURE');h.dispatch('bridge','stop',dict(error='SECONDARY_STOP'))
        self.assertEqual(h.error,'CPU_FIRST_DISK_FAILURE')
    def test_unsaved_spatial_packet_cannot_reach_gui(self):
        from stream_bridge import StreamBridge
        b=StreamBridge.__new__(StreamBridge);b.control=dict(run_id='CPU_TEST',session_id='CPU_TEST',binding={},source_kind='digital_direct')
        p=dict(**b.control,schema='flyvis-continuous-output/v1',step_id=0,state_token=1,
               commit_semantics='FSYNC_CONFIRMED_PUBLIC_WATERMARK',durable_commit_steps=0)
        with self.assertRaisesRegex(ValueError,'UNSAVED_STATE_REJECTED'):b.validate(p)


class ManualSummary(unittest.TestCase):
    setUp=Durability.setUp
    tearDown=Durability.tearDown
    row=Durability.row
    def fixture(self,complete=True):
        control=dict(run_id='CPU_PROTOCOL_TEST_ONLY',session_id='CPU_SESSION')
        rows=[self.row(k) for k in range(2)];(self.root/'step_commits.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        r=dict(**control,success=complete,reason='CPU_TEST_ONLY',computed_steps=2,committed_steps=2 if complete else 1,
            evidence_complete=complete,commit_journal=dict(durable_steps=2 if complete else 1),inference_steps_per_s=199.99,elapsed_s=20)
        write(self.root/'result.json',r)
        draws=[dict(run_id=control['run_id'],draw_server_monotonic_ns=1000000000+k*50000000,upper_ms=100,
                    render_ms=19,raf_wait_ms=12,display_host='CPU_PROTOCOL_TEST_ONLY',document_visible=True) for k in range(201)]
        (self.root/'display_receipts.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in draws))
        return control
    def test_manual_fps_uses_draws_not_snapshots(self):
        s=manual_summary(self.root,self.fixture());self.assertEqual(s['display_FPS'],20);self.assertTrue(s['evidence_complete'])
        self.assertTrue(s['nominal_200_step_pacing']);self.assertEqual(s['REALTIME_STREAM_PASS'],'NOT_MET')
    def test_manual_missing_tail_cannot_pass(self):
        s=manual_summary(self.root,self.fixture(False));self.assertEqual(s['status'],'FAILED');self.assertFalse(s['evidence_complete'])
    def test_browser_failure_cannot_be_masked_by_saved_compute(self):
        c=self.fixture();write(self.root/'browser_failure.json',dict(**c,error='BROWSER_CONSUMER: test fetch failure'))
        s=manual_summary(self.root,c);self.assertEqual(s['status'],'FAILED');self.assertTrue(s['evidence_complete'])
        self.assertIn('fetch failure',s['reason']);self.assertEqual(s['REALTIME_STREAM_PASS'],'NOT_MET')
        write(self.root/'browser_failure.json',dict(run_id='OTHER',session_id=c['session_id'],error='test'))
        with self.assertRaisesRegex(ValueError,'SUMMARY_BROWSER_FAILURE_RUN'):manual_summary(self.root,c)
    def test_manual_cross_run_rejected(self):
        c=self.fixture();c['run_id']='OTHER'
        with self.assertRaises(ValueError):manual_summary(self.root,c)
    def test_manual_wait_is_not_success(self):
        self.assertEqual(manual_summary(self.root,dict(run_id='CPU_TEST_ONLY'))['status'],'WAITING_FOR_GPU_AND_EVIDENCE_FINALIZATION')
    def test_truncated_disk_record_reported_as_failure(self):
        c=self.fixture()
        with (self.root/'step_commits.jsonl').open('a') as f:f.write('{incomplete')
        s=manual_summary(self.root,c);self.assertEqual(s['status'],'FAILED');self.assertFalse(s['evidence_complete']);self.assertIsNotNone(s['journal_read_error'])
    def test_desktop_attach_requires_exact_owner(self):
        b=ManagedDesktopBackend.__new__(ManagedDesktopBackend);b.session=dict(session_id='CPU_TEST_ONLY')
        with self.assertRaises(ValueError):b.verify(dict(schema='flyvis-live-capabilities/v1',session_id='OTHER'))
        self.assertEqual(b.verify(dict(schema='flyvis-live-capabilities/v1',session_id='CPU_TEST_ONLY')),'http://127.0.0.1:8771/#liveCamera')
    def test_desktop_path_escape_has_no_side_effect(self):
        with self.assertRaisesRegex(ValueError,'SCOPE'):ManagedDesktopBackend(None,HERE/'outside/session.json')
    def test_desktop_close_only_requests_its_session_stop(self):
        b=ManagedDesktopBackend.__new__(ManagedDesktopBackend);b.root=self.root;b.path=self.root/'session.json';b.session=dict(session_id='CPU_TEST_ONLY')
        b.stop=threading.Event();b.lock=threading.Lock();events=[];b.record=SimpleNamespace(write=lambda *a,**kw:events.append(kw))
        write(b.path,b.session);b.close();b.close()
        self.assertEqual(load(self.root/'STOP_REQUEST.json')['reason'],'OWNED_DESKTOP_WINDOW_CLOSED');self.assertEqual(len(events),1)
        self.assertFalse(events[0]['backend_stopped']);self.assertEqual(events[0]['CUDA_release'],'AWAIT_WORKER_ACK')
    def test_launcher_reuses_desktop_window_and_suppresses_browser(self):
        import demo_launcher
        calls=[]
        class Child:
            pid=123
            def init__(self,command,**kwargs):calls.append(command)
            def poll(self):return 0
            def wait(self,**kwargs):return 0
        python=self.root/'desktop_env/Scripts/python.exe';python.parent.mkdir(parents=True);python.touch()
        with patch.object(demo_launcher,'HERE',self.root),patch.object(demo_launcher,'ACTIVE',self.root/'active.json'),\
                patch.object(demo_launcher,'Registry',return_value=SimpleNamespace(data={'runtime':{'python':'CPU_TEST_ONLY'}})),\
                patch.object(demo_launcher,'sha',return_value='CPU_TEST_ONLY'),patch.object(demo_launcher.subprocess,'Popen',Child),\
                patch.object(demo_launcher.socket,'socket') as socket,patch('builtins.print'):
            socket.return_value.__enter__.return_value.connect_ex.return_value=1
            demo_launcher.start(stream=True,desktop=True,stream_seconds=20)
        self.assertEqual(len(calls),3);self.assertIn('--no-open',calls[0]);self.assertIn('live_worker.py',calls[1][-3])
        self.assertTrue(calls[2][2].endswith('desktop.py'));self.assertIn('--managed-session',calls[2])
        active=load(self.root/'active.json');self.assertEqual(active['state'],'STOPPED')
        session=load(Path(active['root'])/'session.json');self.assertFalse(session['camera_enabled']);self.assertFalse(session['board_enabled'])

if __name__=='__main__':unittest.main()

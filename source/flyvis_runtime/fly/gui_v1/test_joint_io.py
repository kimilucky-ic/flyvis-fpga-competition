"""CPU-only socket/memory and filesystem failure tests. No physical endpoint."""
import errno
import dataclasses
import json
from pathlib import Path
import socket
import tempfile
from types import SimpleNamespace
import unittest
import uuid
from unittest.mock import patch

from live_protocol import HERE,load
from joint_camera_control import hardware_module
from joint_camera_io import LowLatencySocket,tune_client,NativePCJournal
from joint_camera_engine import JointCameraEvidence


class FakeSocket:
    def init__(self):self.data=b'unchanged';self.sent=[];self.options=[];self.closed=False;self.error=None
    def setsockopt(self,*args):
        self.options.append(args)
        if self.error:raise self.error
    def getsockopt(self,*args):return 1
    def recv(self,n):return self.data[:n]
    def sendall(self,data):self.sent.append(data)
    def close(self):self.closed=True


class SocketTests(unittest.TestCase):
    def test_preserve_bytes_and_set_NODELAY(self):
        s=FakeSocket();p=LowLatencySocket(s);p.sendall(b'raw request');self.assertEqual(p.recv(9),b'unchanged')
        self.assertEqual(s.sent,[b'raw request']);self.assertIn((socket.IPPROTO_TCP,socket.TCP_NODELAY,1),s.options)
        self.assertEqual(p.summary()['bytes_sent'],11);self.assertEqual(p.summary()['bytes_received'],9)
    def test_unsupported_optional_QUICKACK_is_reported(self):
        s=FakeSocket();p=LowLatencySocket(s);p.quickack=True;s.error=OSError(errno.ENOPROTOOPT,'CPU unsupported')
        self.assertEqual(p.recv(2),b'un');self.assertFalse(p.summary()['TCP_QUICKACK_available'])
    def test_actual_receive_error_propagates(self):
        s=FakeSocket();s.recv=lambda n:(_ for _ in ()).throw(TimeoutError('CPU timeout'));p=LowLatencySocket(s)
        with self.assertRaisesRegex(TimeoutError,'CPU timeout'):p.recv(256)
        self.assertEqual(p.receive_calls,0)
    def test_setting_failure_poisons_and_closes_without_retry(self):
        s=FakeSocket();s.error=OSError('CPU option failure');c=SimpleNamespace(sock=s,pending=None,poisoned=False,close=s.close)
        with self.assertRaisesRegex(OSError,'CPU option failure'):tune_client(c)
        self.assertTrue(c.poisoned);self.assertTrue(s.closed);self.assertEqual(len(s.options),1)
    def test_pending_transaction_cannot_be_reconfigured(self):
        s=FakeSocket();c=SimpleNamespace(sock=s,pending=('STEP',),poisoned=False,close=s.close)
        with self.assertRaisesRegex(ValueError,'NOT_CLEAN'):tune_client(c)
        self.assertEqual(s.options,[])


class StorageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        h=load(HERE/'runtime/joint/7f111da4437843539eeffef2c6c2546e/hardware_handoff.json')
        cls.journal=hardware_module(h,'evidence_journal')
    def case(self):
        t=tempfile.TemporaryDirectory(prefix='line2-io-cpu-');self.addCleanup(t.cleanup);base=Path(t.name)
        root=base/'session';root.mkdir();run,sid=uuid.uuid4().hex,uuid.uuid4().hex
        store=NativePCJournal(root,run,sid,native_base=base/'native')
        w=self.journal.JournalWriter(store.directory,dict(role='CPU_NO_BOARD'))
        store.attach(w);self.addCleanup(lambda:w.abandon() if not w.closed else None)
        return base,root,store,w
    def test_identical_bytes_barriers_and_sync_calls_after_export(self):
        base,root,s,w=self.case();plain=self.journal.JournalWriter(base/'direct',dict(role='CPU_NO_BOARD'))
        for writer in (plain,w):
            writer.add('candidate.bin',b'exact candidate');writer.checkpoint('BEFORE_SEND')
            writer.add('commit.bin',b'exact commit');writer.checkpoint('COMMIT_INTENT')
            writer.add('ACK.bin',b'exact ACK');writer.checkpoint('COMMIT_ACK')
            writer.checkpoint('STEP_PUBLISHED');writer.close('CPU_REPLAY',completed=1)
        exported=s.export_closed();self.assertEqual(plain.path.read_bytes(),(root/'pc/evidence.fvej').read_bytes())
        self.assertEqual(plain.sync_calls,w.sync_calls);self.assertEqual(w.sync_calls,6)
        self.assertTrue(s.source.exists());self.assertFalse(exported['writer_poisoned'])
        self.assertEqual(self.journal.JournalReader(root/'pc/evidence.fvej').terminal['completed'],1)
    def test_export_rejects_open_writer(self):
        _,root,s,w=self.case()
        with self.assertRaisesRegex(ValueError,'NOT_CLOSED'):s.export_closed()
        self.assertFalse((root/'pc').exists());self.assertTrue(s.source.exists())
    def test_export_sync_failure_preserves_native_and_never_publishes_final(self):
        _,root,s,w=self.case();w.close('CPU_REPLAY')
        with patch('joint_camera_io.os.fsync',side_effect=OSError('CPU export sync')):
            with self.assertRaisesRegex(OSError,'CPU export sync'):s.export_closed()
        self.assertTrue(s.source.exists());self.assertFalse((root/'pc/evidence.fvej').exists())
        with self.assertRaisesRegex(ValueError,'ALREADY_ATTEMPTED'):s.export_closed()
    def test_export_hash_failure_cannot_publish_or_delete_source(self):
        _,root,s,w=self.case();w.close('CPU_REPLAY')
        with patch('joint_camera_io.sha',return_value='0'*64):
            with self.assertRaisesRegex(ValueError,'EXPORT_SHA'):s.export_closed()
        self.assertTrue(s.source.exists());self.assertFalse((root/'pc/evidence.fvej').exists())
    def test_checkpoint_failure_still_poisoned_and_incomplete(self):
        _,root,s,w=self.case();w.sync_fn=lambda fd:(_ for _ in ()).throw(OSError('CPU fsync'))
        with self.assertRaisesRegex(OSError,'CPU fsync'):w.checkpoint('COMMIT_INTENT')
        self.assertTrue(w.poisoned);w.abandon();r=s.export_closed();self.assertTrue(r['writer_poisoned'])
        with self.assertRaisesRegex(ValueError,'Incomplete'):self.journal.JournalReader(root/'pc/evidence.fvej')
    def test_existing_destination_is_not_overwritten(self):
        _,root,s,w=self.case();w.close('CPU_REPLAY');(root/'pc').mkdir();f=root/'pc/keep';f.write_text('original')
        with self.assertRaises(FileExistsError):s.export_closed()
        self.assertEqual(f.read_text(),'original');self.assertTrue(s.source.exists())
    def test_same_identity_cannot_create_second_native_owner(self):
        base,root,s,w=self.case()
        with self.assertRaises(FileExistsError):NativePCJournal(root,s.identity['run_id'],s.identity['session_id'],native_base=base/'native')


class MergedCommitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        h=load(HERE/'runtime/joint/7f111da4437843539eeffef2c6c2546e/hardware_handoff.json')
        cls.journal=hardware_module(h,'evidence_journal')
        from hybrid_a3 import module
        cls.wire=module('cpu_merge_pinned_wire',Path(load(HERE/'hybrid_joint_registry.json')['pins']['v2_protocol']['path'].replace('C:\\','/mnt/c/').replace('\\','/')))
    def case(self,policy='MERGED_INTENT_BEFORE_SEND/v1'):
        t=tempfile.TemporaryDirectory(prefix='line2-merged-cpu-');self.addCleanup(t.cleanup)
        j=self.journal.JournalWriter(Path(t.name)/'pc',dict(role='CPU_MERGED_NO_BOARD'))
        e=JointCameraEvidence(j,1,commit_policy=policy,wire=self.wire);self.addCleanup(lambda:j.abandon() if not j.closed else None)
        w=self.wire;payload=bytes(w.INPUT_BYTES)
        step=w.Header(w.STEP,b'1'*16,b'2'*16,0,b'3'*32,w.digest(payload),len(payload))
        intent=dict(event='COMMIT_INTENT',decision='4'*64,request_header_sha256=w.digest(step.pack()).hex(),old_state_token=0)
        commit=dataclasses.replace(step,op=w.COMMIT,payload_bytes=0,payload_sha=w.digest(b''),parent_commit=bytes.fromhex(intent['decision']))
        e.observe('tx_intent',step.pack()+payload)
        return e,j,step,intent,commit
    def test_one_less_fsync_and_same_intent_wire_records(self):
        counts=[];logical=[]
        for policy in ('IMMEDIATE/v1','MERGED_INTENT_BEFORE_SEND/v1'):
            e,j,step,intent,commit=self.case(policy);before=j.sync_calls
            e.event(intent)
            self.assertEqual(j.sync_calls-before,1 if policy=='IMMEDIATE/v1' else 0)
            self.wire.send_frame(SimpleNamespace(sendall=lambda raw:None),commit,observer=e.observe)
            e.event(dict(event='COMMIT_ACK'));e.published();e.close('CPU_NO_BOARD')
            counts.append(j.sync_calls);r=self.journal.JournalReader(j.path)
            logical.append({n:r.read(n) for n in r.files})
        self.assertEqual(counts[0]-counts[1],1);self.assertEqual(logical[0],logical[1])
    def test_failed_merged_fsync_sends_no_COMMIT_and_no_publication(self):
        e,j,step,intent,commit=self.case();e.event(intent);sent=[]
        j.sync_fn=lambda fd:(_ for _ in ()).throw(OSError('CPU merged fsync'))
        with self.assertRaisesRegex(OSError,'CPU merged fsync'):
            self.wire.send_frame(SimpleNamespace(sendall=sent.append),commit,observer=e.observe)
        self.assertEqual(sent,[]);self.assertTrue(j.poisoned)
        with self.assertRaisesRegex(ValueError,'UNSENT'):e.published()
    def test_wrong_COMMIT_identity_or_decision_never_sent(self):
        for field,value in (('step',1),('txn',b'9'*16),('parent_commit',b'9'*32)):
            with self.subTest(field=field):
                e,j,step,intent,commit=self.case();e.event(intent);sent=[]
                with self.assertRaisesRegex(ValueError,'NOT_BOUND'):
                    self.wire.send_frame(SimpleNamespace(sendall=sent.append),dataclasses.replace(commit,**{field:value}),observer=e.observe)
                self.assertEqual(sent,[])
    def test_ACK_cannot_arrive_before_merged_intent_durable(self):
        e,j,step,intent,commit=self.case();e.event(intent)
        with self.assertRaisesRegex(ValueError,'ACK_BEFORE'):e.event(dict(event='COMMIT_ACK'))
    def test_new_STEP_cannot_skip_deferred_COMMIT(self):
        e,j,step,intent,commit=self.case();e.event(intent)
        with self.assertRaisesRegex(ValueError,'UNSENT'):e.observe('tx_intent',step.pack()+bytes(self.wire.INPUT_BYTES))
    def test_stop_before_send_keeps_intent_and_marks_incomplete(self):
        e,j,step,intent,commit=self.case();e.event(intent);e.close('CPU_CANCEL_BEFORE_SEND')
        r=self.journal.JournalReader(j.path)
        self.assertEqual(r.terminal['status'],'FAILED_OR_INCOMPLETE');self.assertIn(b'COMMIT_INTENT',r.read('transactions.jsonl'))
    def saved_pipeline(self):
        from test_joint_camera import CameraJointTests
        from joint_camera_engine import CameraJointEngine
        if not hasattr(self.__class__,'saved_class'):
            CameraJointTests.setUpClass();self.__class__.saved_class=CameraJointTests
        c=self.saved_class('test_three_step_original_coordinator_feedback_and_durable_snapshots');c.setUp();self.addCleanup(c.tearDown)
        prior=c.engine;c.ev.writer.abandon()
        c.ev=JointCameraEvidence(c.journal.JournalWriter(Path(c.temp.name)/'merged',dict(role='CPU_MERGED_REPLAY')),3,
            commit_policy='MERGED_INTENT_BEFORE_SEND/v1',wire=c.c.wire)
        c.identity=dict(c.identity,validation_policy='SAME_OLD_CPU_POST_RUN')
        c.engine=CameraJointEngine(c.c,c.hw,prior.produce,prior.decode,c.ev,c.identity,lambda:None,
            lambda a:a.copy(),lambda a:a,None)
        sent=[];step,commit=c.hw.step,c.hw.commit;w=c.c.wire
        def exchange_step(old,chem,x,identity):
            payload=old+chem+x;h=w.Header(w.STEP,payload_bytes=len(payload),payload_sha=w.digest(payload),**identity)
            w.send_frame(SimpleNamespace(sendall=sent.append),h,payload,observer=c.ev.observe)
            candidate,result=step(old,chem,x,identity);c.ev.observe('rx',result.pack()+candidate)
            return candidate,result
        def exchange_commit(decision):
            h=dataclasses.replace(c.hw.header,op=w.COMMIT,payload_bytes=0,payload_sha=w.digest(b''),parent_commit=decision)
            w.send_frame(SimpleNamespace(sendall=sent.append),h,observer=c.ev.observe)
            ack=commit(decision);c.ev.observe('rx',ack.pack());return ack
        c.hw.step,c.hw.commit=exchange_step,exchange_commit
        return c,sent
    def test_merged_saved_three_steps_preserve_full_state_and_raw_feedback(self):
        import numpy as np
        c,sent=self.saved_pipeline()
        for k in range(3):
            p=c.engine.step(c.current(k));self.assertEqual(p['pc_commit_journal_policy'],'MERGED_INTENT_BEFORE_SEND/v1')
            np.testing.assert_array_equal(c.engine.barrier.state,c.a(f'committed_full_{k}.npy'))
            if k:self.assertEqual(c.hw.requests[k][:23072],c.reader.read(f'candidate_{k-1}.bin'))
        c.ev.close('CPU_REPLAY');r=c.journal.JournalReader(c.ev.writer.path)
        barriers=[b['barrier'] for b in r.batches]
        self.assertEqual(barriers.count('COMMIT_INTENT_BEFORE_SEND'),3);self.assertEqual(barriers.count('COMMIT_ACK'),3)
        self.assertEqual(barriers.count('STEP_PUBLISHED'),3);self.assertEqual(len(sent),6)
    def test_pipeline_merged_fsync_failure_prevents_actual_send_and_state_change(self):
        c,sent=self.saved_pipeline();sync=c.ev.writer.sync_fn
        def fail(fd):
            if c.ev.writer.attempted_barrier=='COMMIT_INTENT_BEFORE_SEND':raise OSError('CPU merged precommit failure')
            sync(fd)
        c.ev.writer.sync_fn=fail
        with self.assertRaisesRegex(OSError,'precommit failure'):c.engine.step(c.current(0))
        self.assertEqual(len(sent),1);self.assertEqual(c.hw.commits,[]);self.assertEqual(c.engine.barrier.state_token,0)


if __name__=='__main__':unittest.main()

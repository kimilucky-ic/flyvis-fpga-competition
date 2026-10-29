"""CPU protocol checks using saved software preflight arrays; no devices/sockets."""
import dataclasses
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from live_protocol import HERE
from hybrid_v2 import V2Contract
from hybrid_joint import _JointAdapter, DurableEvidence, connect_live


class FixtureClient:
    def init__(self,c):
        self.c=c;self.w=c.wire;self.asid=bytes.fromhex('12'*16)
        self.attestation={'boot_id':'CPU_FIXTURE','server_session':'CPU_FIXTURE'}
        self.requests=[];self.commits=[];self.closed=False;self.before_ack=lambda:None;self.lose_ack=False
    def step(self,old,chem,x,identity):
        payload=old+chem+x;self.requests.append(payload)
        self.header=self.w.Header(self.w.STEP,payload_bytes=len(payload),payload_sha=self.w.digest(payload),**identity)
        result,_=self.c.expected_H(payload)
        return result,dataclasses.replace(self.header,op=self.w.RESULT,payload_bytes=len(result),
            payload_sha=self.w.digest(result),compute_cycles=57681,transfer_cycles=83024)
    def commit(self,decision):
        self.commits.append(decision);self.before_ack()
        if self.lose_ack:raise TimeoutError('FIXTURE_ACK_LOST')
        return dataclasses.replace(self.header,op=self.w.ACK,payload_bytes=0,payload_sha=self.w.digest(b''),parent_commit=decision)
    def close(self):self.closed=True


class JointProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=V2Contract()
        cls.source=HERE/'runtime/hybrid_software_checks/ca3f3c24c04d4c5d9c0dde9d36c8a511'
        cls.states=np.load(cls.source/'software_mixed_states.npy',allow_pickle=False)
        cls.frames=np.load(cls.source/'stimulus_721.npy',allow_pickle=False)
        cls.flows=np.load(cls.source/'official_flow.npy',allow_pickle=False)
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='joint_cpu_',dir=HERE/'runtime');self.addCleanup(self.temp.cleanup)
        self.client=FixtureClient(self.c);self.index=0;self.factory_calls=0;self.fail_copy=False;self.fail_decoder=False
        def produce(old,frame,k):
            with np.load(self.source/f'candidates_{k}.npz',allow_pickle=False) as z:
                np.testing.assert_array_equal(old,z['old_full'])
                return {name:z[name].copy() for name in ('chemical_H','new_R','r_ids','x_full')}
        def decode(full):
            if self.fail_decoder:raise RuntimeError('FIXTURE_DECODE_ERROR')
            np.testing.assert_array_equal(full,self.states[self.index])
            result=self.flows[self.index].copy();self.index+=1;return result
        def publication(full):
            self.factory_calls+=1
            if self.fail_copy and self.factory_calls>1:raise RuntimeError('FIXTURE_COPY_ERROR')
            return full.copy()
        self.adapter=_JointAdapter(self.c,self.client,produce,decode,DurableEvidence(Path(self.temp.name)/'evidence'),
            {'run_id':'CPU_FIXTURE','comparison_id':'CPU_FIXTURE'},lambda:None,publication,np.asarray,origin='CPU_PROTOCOL_TEST')
        self.initial=self.adapter.barrier.state.copy()
    def unchanged(self):
        self.assertEqual(self.adapter.barrier.state_token,200)
        np.testing.assert_array_equal(self.adapter.barrier.state,self.initial)
    def test_three_saved_steps_publish_only_after_ack_and_feed_back_words(self):
        for j in range(3):
            b=self.adapter.barrier;old=b.state.copy();old_publication=b.publication
            def before_ack():
                self.assertEqual(b.state_token,200+j)
                self.assertIs(b.publication,old_publication)
                np.testing.assert_array_equal(b.state,old)
            self.client.before_ack=before_ack
            row=self.adapter.step(self.frames[j])
            self.assertEqual(row['execution_kind'],'CPU_PROTOCOL_TEST');self.assertEqual(row['PL_proven_global_ids'],[])
            np.testing.assert_array_equal(b.publication,self.states[j])
            if j:self.assertEqual(self.client.requests[j][:self.c.wire.WORD_BYTES],self.c.expected_H(self.client.requests[j-1])[0])
        self.assertEqual(self.adapter.barrier.state_token,203)
        with self.assertRaisesRegex(ValueError,'BOUNDED'):self.adapter.step(self.frames[0])
        self.assertEqual(len(self.client.requests),3)
    def test_buffer_failure_sends_no_commit(self):
        self.fail_copy=True
        with self.assertRaisesRegex(RuntimeError,'COPY_ERROR'):self.adapter.step(self.frames[0])
        self.unchanged();self.assertEqual(self.client.commits,[]);self.assertTrue(self.client.closed)
    def test_lost_ack_never_publishes_or_retries(self):
        self.client.lose_ack=True
        with self.assertRaises(TimeoutError):self.adapter.step(self.frames[0])
        self.unchanged();self.assertEqual(self.adapter.barrier.phase,'IN_DOUBT')
        with self.assertRaisesRegex(ValueError,'BOUNDED'):self.adapter.step(self.frames[0])
        self.assertEqual(len(self.client.requests),1)
    def test_publication_mismatch_blocks_request(self):
        self.adapter.barrier.publication[0]+=1
        with self.assertRaisesRegex(ValueError,'GPU_VISIBLE_OLD_STATE'):self.adapter.step(self.frames[0])
        self.unchanged();self.assertEqual(self.client.requests,[])
    def test_wrong_input_blocks_request(self):
        frame=self.frames[0].copy();frame[0]+=.01
        with self.assertRaisesRegex(ValueError,'FROZEN_ON60'):self.adapter.step(frame)
        self.unchanged();self.assertEqual(self.client.requests,[])
    def test_decoder_failure_preserves_commit_and_revokes_display(self):
        self.fail_decoder=True
        with self.assertRaisesRegex(RuntimeError,'DECODE_ERROR'):self.adapter.step(self.frames[0])
        self.assertEqual(self.adapter.barrier.state_token,201);self.assertTrue(self.adapter.failed)
        self.assertIn('DISPLAY_REVOKED',(self.adapter.evidence.root/'transactions.jsonl').read_text())
    def test_missing_approval_cannot_construct_client(self):
        with patch.object(self.c.wire,'Client') as client:
            with self.assertRaisesRegex(ValueError,'NOT_AUTHORIZED'):
                connect_live(self.c,{}, {},None,None,Path(self.temp.name)/'no_live',lambda:None)
            client.assert_not_called()
    def test_reentrant_step_is_rejected(self):
        self.adapter.owner.acquire()
        try:
            with self.assertRaisesRegex(ValueError,'ALREADY_IN_PROGRESS'):self.adapter.step(self.frames[0])
        finally:self.adapter.owner.release()
        self.unchanged();self.assertEqual(self.client.requests,[])
    def test_current_gpu_reference_failure_sends_no_step(self):
        def reject(old,output,k):raise ValueError('FIXTURE_REFERENCE_FAILURE')
        self.adapter.candidate_validator=reject
        with self.assertRaisesRegex(ValueError,'REFERENCE_FAILURE'):self.adapter.step(self.frames[0])
        self.unchanged();self.assertEqual(self.client.requests,[])
    def test_saved_reference_checks_same_old_and_values(self):
        from hybrid_joint_run import SavedReference
        ref=SavedReference();data=ref.candidates[0]
        self.assertEqual(ref.check(data['old_full'],data,200)['status'],'PASS_SAME_OLD_GPU_REFERENCE')
        bad={**data,'new_R':data['new_R'].copy()};bad['new_R'][0]+=1
        with self.assertRaisesRegex(ValueError,'REFERENCE_MISMATCH'):ref.check(data['old_full'],bad,200)
        old=data['old_full'].copy();old[0]+=1
        with self.assertRaisesRegex(ValueError,'EXACT_SAME_OLD'):ref.check(old,data,200)


if __name__=='__main__':unittest.main()

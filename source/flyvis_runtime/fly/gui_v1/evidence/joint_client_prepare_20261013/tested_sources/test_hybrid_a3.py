"""No-device protocol fixtures: existing recorded values, never new neural outputs."""
import dataclasses
import tempfile
import unittest
from pathlib import Path
import numpy as np
from hybrid_a3 import A3Contract,CoordinatorRehearsal,inspect_local_board_replay
from live_protocol import HERE,Registry,load,sha,write


def words(path):
    return np.array([int(x,16) for x in path.read_text().split()],dtype='<u4').tobytes()


class HybridProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=A3Contract();cls.reg=Registry();cls.initial=np.load(cls.reg.path_for('initial'),allow_pickle=False)
        cls.requests=words(cls.c.paths['a3_requests']);cls.outputs=words(cls.c.paths['a3_expected'])
    def setUp(self):
        self.log=[];self.w=self.c.wire;self.old=self.requests[:self.w.WORD_BYTES]
        a=self.initial.copy();a[self.c.h]=self.c.decode(self.old)
        self.b=CoordinatorRehearsal(self.c,a,self.old,'cpu-fixture-run','cpu-fixture-comparison','RECORDED_PROTOCOL_FIXTURE',bytes.fromhex('12'*16),self.log.append)
        # A1/A2/A3 frozen old/chemical/x and expected codes; no model executes.
        self.x=np.zeros(45669,dtype='<f4');self.x[self.c.h]=self.c.decode(self.requests[2*self.w.WORD_BYTES:3*self.w.WORD_BYTES])
        self.chem=self.c.decode(self.requests[self.w.WORD_BYTES:2*self.w.WORD_BYTES])
        self.binding={**self.b.binding(self.x),'chemical_digest':self.b.hmod.array_hash(self.chem)}
        self.candidate=self.outputs[:self.w.WORD_BYTES];self.r=self.initial[self.c.r].copy()
        self.rb={**self.b.binding(self.x),'r_candidate_digest':self.b.hmod.array_hash(self.r),'r_ids_digest':self.b.hmod.array_hash(self.c.r)}
        self.before=self.b.state.copy()
    def prepare(self):return self.b.prepare(bytes.fromhex('34'*16),self.x,self.chem,self.binding)
    def response(self):
        h,_=self.prepare();h=self.w.Header.unpack(h)
        return dataclasses.replace(h,op=self.w.RESULT,payload_bytes=self.w.WORD_BYTES,payload_sha=self.w.digest(self.candidate),compute_cycles=57681,transfer_cycles=120857)
    def stage(self):
        h=self.response();return self.b.accept_candidates(h.pack(),self.candidate,self.r,self.c.r,self.rb)
    def ack(self,frame):return dataclasses.replace(self.w.Header.unpack(frame),op=self.w.ACK).pack()
    def unchanged(self):
        np.testing.assert_array_equal(self.before,self.b.state);self.assertEqual(self.b.state_token,0)
    def test_exact_mapping_and_separate_h67(self):
        self.assertEqual(len(self.c.r),39901);self.assertEqual(len(set(self.c.h)&set(self.c.r)),0)
        np.testing.assert_array_equal(self.c.h[self.c.spatial_from_wire],self.c.spatial.ids)
        self.assertEqual(len(set(self.c.h)&set(self.c.spatial.sets['H67'])),11)
    def test_existing_evidence_does_not_enable_PL(self):
        s=self.c.status();self.assertEqual(s['H67']['requests'],32);self.assertFalse(s['H67']['true_closed_loop'])
        self.assertEqual(s['A3R1']['board'],'NOT_RUN');self.assertEqual(s['PL_proven_global_ids'],[])
    def test_live_flag_cannot_promote_fixture(self):
        with self.assertRaisesRegex(ValueError,'NOT_ADMITTED'):
            CoordinatorRehearsal(self.c,self.before,self.old,'a','b','c',bytes(16),self.log.append,execution_kind='ACTUAL_BOARD')
    def test_wire_roundtrip_and_global_old_digest(self):
        raw,payload=self.prepare();h=self.w.Header.unpack(raw)
        self.assertEqual(len(raw),256);self.assertEqual(len(payload),69216)
        self.assertEqual(h.old_sha.hex(),self.binding['old_full_digest']);self.assertEqual(payload[:23072],self.old)
        self.assertNotEqual(h.old_sha,self.w.digest(self.old));self.unchanged()
    def test_candidates_do_not_publish(self):
        self.stage();self.unchanged();self.assertEqual(self.b.phase,'VALIDATED_NOT_COMMITTED')
    def test_matching_ack_is_only_publish_point(self):
        self.stage();frame=self.b.commit_frame();self.unchanged();self.assertEqual(self.log[0]['event'],'COMMIT_INTENT')
        new=self.b.acknowledge(self.ack(frame));self.assertEqual(self.b.state_token,1)
        np.testing.assert_array_equal(new[self.c.h],self.c.decode(self.candidate));np.testing.assert_array_equal(new[self.c.r],self.r)
        self.assertEqual([r['event'] for r in self.log],['COMMIT_INTENT','COMMIT_ACK'])
        with self.assertRaises(ValueError):new[0]=123
        new.flags.writeable=True;new[0]=123
        self.assertNotEqual(float(self.b.state[0]),123.)
    def test_next_step_retains_original_integer_H(self):
        self.stage();frame=self.b.commit_frame();self.b.acknowledge(self.ack(frame))
        binding={**self.b.binding(self.x),'chemical_digest':self.b.hmod.array_hash(self.chem)};raw,payload=self.b.prepare(bytes.fromhex('56'*16),self.x,self.chem,binding)
        self.assertEqual(payload[:23072],self.candidate);self.assertEqual(self.w.Header.unpack(raw).step,1)
    def test_wrong_producer_old_state(self):
        bad={**self.binding,'old_full_digest':'0'*64}
        with self.assertRaisesRegex(ValueError,'BINDING'):self.b.prepare(bytes.fromhex('34'*16),self.x,self.chem,bad)
        self.unchanged()
    def test_wrong_chemical_order_identity(self):
        bad={**self.binding,'mapping_sha256':'0'*64}
        with self.assertRaisesRegex(ValueError,'BINDING'):self.b.prepare(bytes.fromhex('34'*16),self.x,self.chem,bad)
    def test_nonfinite_chemical(self):
        self.chem[0]=float('nan')
        with self.assertRaises(Exception):self.prepare()
        self.unchanged()
    def test_overflow_chemical(self):
        self.chem[0]=1000.
        self.binding['chemical_digest']=self.b.hmod.array_hash(self.chem)
        with self.assertRaisesRegex(ValueError,'overflow'):self.prepare()
        self.unchanged()
    def test_wrong_candidate_identity(self):
        h=dataclasses.replace(self.response(),epoch=99)
        with self.assertRaisesRegex(ValueError,'IDENTITY'):self.b.accept_candidates(h.pack(),self.candidate,self.r,self.c.r,self.rb)
        self.unchanged()
    def test_candidate_tamper(self):
        h=self.response();bad=bytearray(self.candidate);bad[0]^=1
        with self.assertRaisesRegex(ValueError,'SHA'):self.b.accept_candidates(h.pack(),bytes(bad),self.r,self.c.r,self.rb)
        self.unchanged()
    def test_wrong_R_mapping(self):
        h=self.response()
        bad={**self.rb,'r_ids_digest':self.b.hmod.array_hash(self.c.r[::-1])}
        with self.assertRaisesRegex(Exception,'LAYOUT'):self.b.accept_candidates(h.pack(),self.candidate,self.r,self.c.r[::-1],bad)
        self.unchanged()
    def test_R_native_H_forbidden(self):
        h=self.response();bad={**self.rb,'native_H_update_count':5768}
        with self.assertRaisesRegex(ValueError,'BINDING'):self.b.accept_candidates(h.pack(),self.candidate,self.r,self.c.r,bad)
        self.unchanged()
    def test_nonfinite_R_rejected(self):
        h=self.response();self.r[0]=float('nan')
        self.rb['r_candidate_digest']=self.b.hmod.array_hash(self.r)
        with self.assertRaisesRegex(Exception,'NONFINITE'):self.b.accept_candidates(h.pack(),self.candidate,self.r,self.c.r,self.rb)
        self.unchanged()
    def test_mismatched_commit_ack_quarantines(self):
        self.stage();h=self.w.Header.unpack(self.b.commit_frame());ack=dataclasses.replace(h,op=self.w.ACK,old_sha=bytes(32))
        with self.assertRaisesRegex(ValueError,'ACK_IDENTITY'):self.b.acknowledge(ack.pack())
        self.unchanged();self.assertEqual(self.b.phase,'IN_DOUBT')
    def test_ack_epoch_checked_more_strictly_than_released_client(self):
        self.stage();h=self.w.Header.unpack(self.b.commit_frame());ack=dataclasses.replace(h,op=self.w.ACK,epoch=1)
        with self.assertRaisesRegex(ValueError,'ACK_IDENTITY'):self.b.acknowledge(ack.pack())
        self.unchanged()
    def test_lost_ack_stops_future_steps(self):
        self.stage();self.b.commit_frame();self.b.fail('DISCONNECTED_AFTER_COMMIT')
        self.assertEqual(self.b.phase,'IN_DOUBT');self.unchanged()
        with self.assertRaises(ValueError):self.prepare()
        self.unchanged();self.assertEqual(self.b.phase,'IN_DOUBT')
    def test_timeout_before_commit(self):
        self.prepare();self.b.fail('PL_CANDIDATE_TIMEOUT');self.unchanged()
        with self.assertRaises(ValueError):self.b.commit_frame()
    def test_intent_journal_failure_returns_no_commit_packet(self):
        self.stage()
        def disk_full(event):raise OSError('DISK_FULL')
        self.b.journal=disk_full
        with self.assertRaises(OSError):self.b.commit_frame()
        self.unchanged()
    def test_ack_journal_failure_never_publishes(self):
        self.stage();frame=self.b.commit_frame()
        def disk_full(event):raise OSError('DISK_FULL')
        self.b.journal=disk_full
        with self.assertRaises(OSError):self.b.acknowledge(self.ack(frame))
        self.assertEqual(self.b.phase,'IN_DOUBT');self.unchanged()
    def test_duplicate_ack_cannot_advance_twice(self):
        self.stage();frame=self.b.commit_frame();ack=self.ack(frame);self.b.acknowledge(ack)
        with self.assertRaises(ValueError):self.b.acknowledge(ack)
        self.assertEqual(self.b.state_token,1)
    def test_unknown_board_directory_not_admitted(self):
        with self.assertRaisesRegex(ValueError,'PIN_SET'):inspect_local_board_replay(self.c,HERE,{})
    def test_chemical_values_must_match_producer_digest(self):
        self.chem[0]+=.001
        with self.assertRaisesRegex(ValueError,'CHEMICAL_BINDING'):self.prepare()
        self.unchanged()
    def test_R_values_must_match_producer_digest(self):
        h=self.response();self.r[0]+=.001
        with self.assertRaisesRegex(ValueError,'R_SAME_OLD_STATE_BINDING'):self.b.accept_candidates(h.pack(),self.candidate,self.r,self.c.r,self.rb)
        self.unchanged()

if __name__=='__main__':unittest.main()

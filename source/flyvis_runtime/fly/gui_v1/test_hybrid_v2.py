"""v2 protocol + fixed-point reference tests; no board/network/GPU imports."""
import dataclasses
import unittest
import numpy as np
from hybrid_v2 import V2Contract
from test_hybrid_a3 import HybridProtocol,words
from live_protocol import Registry


class V2Protocol(HybridProtocol):
    @classmethod
    def setUpClass(cls):
        cls.c=V2Contract();cls.reg=Registry();cls.initial=np.load(cls.reg.path_for('initial'),allow_pickle=False)
        cls.requests=words(cls.c.paths['a3_requests']);cls.outputs=words(cls.c.paths['a3_expected'])

    def test_v1_frames_are_rejected(self):
        frame,payload=self.prepare();bad=bytearray(frame);bad[4:6]=(1).to_bytes(2,'little')
        with self.assertRaisesRegex(ValueError,'ABI'):self.w.Header.unpack(bytes(bad))

    def test_integer_reference_matches_all_frozen_system_outputs(self):
        for i in range(3):
            req=self.requests[i*self.w.INPUT_BYTES:(i+1)*self.w.INPUT_BYTES]
            out=self.outputs[i*self.w.WORD_BYTES:(i+1)*self.w.WORD_BYTES]
            self.assertEqual(self.c.validate_H(req,out)['max_integer_code_error'],0)

    def test_one_integer_code_error_rejects_before_commit(self):
        bad=np.frombuffer(self.candidate,dtype='<i4').copy();bad[0]+=1
        with self.assertRaisesRegex(ValueError,'ORACLE'):self.c.validate_H(self.requests[:self.w.INPUT_BYTES],bad.tobytes())

    def test_warm_start_retains_R_and_canonical_H(self):
        a,old,raw=self.c.initial()
        np.testing.assert_array_equal(a[self.c.r],raw[self.c.r])
        np.testing.assert_array_equal(a[self.c.h],self.c.decode(old))
        self.assertEqual(old,self.w.encode_activity(raw[self.c.h]))

    def test_v2_does_not_admit_preboard_software(self):
        r=self.c.readiness()
        self.assertEqual(r['backend'],'NOT_CONNECTED');self.assertEqual(r['PL_proven_global_ids'],[])
        self.assertFalse(r['full_485_authorized']);self.assertIsNone(r['endpoint'])

    def test_v2_commit_ack_all_fields(self):
        self.stage();frame=self.b.commit_frame()
        ack=dataclasses.replace(self.w.Header.unpack(frame),op=self.w.ACK,status=1)
        with self.assertRaisesRegex(ValueError,'ACK'):self.b.acknowledge(ack.pack())
        self.unchanged();self.assertEqual(self.b.phase,'IN_DOUBT')

if __name__=='__main__':unittest.main()

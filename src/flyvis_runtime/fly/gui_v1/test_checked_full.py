"""CPU protocol tests. Tensors here are identity-only fixtures, not neural data."""
import unittest
from types import SimpleNamespace
from checked_full import CombinedCheckedFull
from live_protocol import checked_commit


class CheckedFullProtocol(unittest.TestCase):
    def setUp(self):
        self.a=CombinedCheckedFull.__new__(CombinedCheckedFull)
        self.a.steps=4;self.a.commits=0;self.a.candidate_proof=None;self.a.committed_proof=None
        self.tensor=SimpleNamespace(_version=0)
    def validated(self):self.a.candidate_proof=(self.a.proof(self.tensor),self.a.steps)
    def test_new_object_cannot_borrow_proof(self):
        self.assertFalse(self.a.matches(self.a.proof(self.tensor),SimpleNamespace(_version=0)))
    def test_inplace_mutation_invalidates_proof(self):
        p=self.a.proof(self.tensor);self.tensor._version+=1
        self.assertFalse(self.a.matches(p,self.tensor))
    def test_unchecked_candidate_rejected(self):
        with self.assertRaisesRegex(ValueError,'PROOF'):self.a.commit(self.tensor)
    def test_commit_consumes_proof(self):
        self.validated();self.assertIs(self.a.commit(self.tensor),self.tensor)
        self.assertTrue(self.a.matches(self.a.committed_proof,self.tensor))
        with self.assertRaisesRegex(ValueError,'PROOF'):self.a.commit(self.tensor)
        self.assertEqual(self.a.commits,1)
    def test_stale_candidate_step_rejected(self):
        self.validated();self.a.steps+=1
        with self.assertRaisesRegex(ValueError,'PROOF'):self.a.commit(self.tensor)
    def test_candidate_mutation_rejected(self):
        self.validated();self.tensor._version+=1
        with self.assertRaisesRegex(ValueError,'PROOF'):self.a.commit(self.tensor)
    def test_scope_revocation_prevents_commit(self):
        self.validated()
        def gate(*args):raise ValueError('REVOKED')
        with self.assertRaisesRegex(ValueError,'REVOKED'):checked_commit(self.tensor,gate,self.a.commit)
        self.assertEqual(self.a.commits,0);self.assertIsNone(self.a.committed_proof)

if __name__=='__main__':unittest.main()

"""CPU-only equivalence checks for original run bytecode + pure helper bindings."""
import copy
import dataclasses
import json
from pathlib import Path
import struct
import unittest
from unittest.mock import patch

from ps_commit_evidence import BoundDriverHelpers,RUNTIME_HELPERS
from test_joint_transport import OptionSocket


class PSHotPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_ps_commit_evidence import PSCommitTests
        cls.fixture_class=PSCommitTests;PSCommitTests.setUpClass()

    def fixture(self,n=3,optimized=True,fail=None):
        f=self.fixture_class('test_original_service_and_driver_three_steps_identical_outputs')
        self.addCleanup(f.doCleanups);c=f.make(n=n,fail=fail)
        original=c.d.run.__func__
        if optimized:
            c.obj.connection=OptionSocket();c.e.attach_service(c.obj)
            self.assertIs(c.d.run.__func__.__code__,original.__code__)
        return f,c

    def test_range_validation_all_saved_requests_and_candidates_and_edges(self):
        f,c=self.fixture(n=1);helper=c.e.driver_helpers
        for raw in [r[256:] for r in f.requests]+f.candidates:
            self.assertIsNone(helper.original_validate(raw));self.assertIsNone(helper.validate_words(raw))
        samples=[b'',b'bad']+[struct.pack('<i',x) for x in
            (-(1<<31),-(1<<30)-1,-(1<<30),-1,0,(1<<30)-1,1<<30,(1<<31)-1)]
        for raw in samples:
            outcomes=[]
            for fn in (helper.original_validate,helper.validate_words):
                try:outcomes.append(('OK',fn(raw)))
                except Exception as e:outcomes.append((type(e).__name__,str(e)))
            self.assertEqual(outcomes[0],outcomes[1])
        self.assertIsNone(helper.validate_words(bytearray(struct.pack('<i',1))))

    def test_original_code_modules_and_other_instance_not_mutated(self):
        f,a=self.fixture(n=1,optimized=False);original=a.d.run.__func__;before=dict(original.__globals__)
        g,b=self.fixture(n=1)
        self.assertIs(a.d.run.__func__,original);self.assertIs(b.d.run.__func__.__code__,original.__code__)
        self.assertEqual(set(original.__globals__),set(before))
        self.assertTrue(all(original.__globals__[k] is v for k,v in before.items()))
        for key in before:
            if key not in ('save_bytes','save_json','validate_words'):
                self.assertIs(b.d.run.__func__.__globals__[key],before[key])

    def test_three_steps_candidate_ACK_registers_and_all_events_identical(self):
        captures=[]
        for optimized in (False,True):
            f,c=self.fixture(optimized=optimized);start=c.e.journal.sync_calls
            f.run_service(c);self.assertEqual((c.d.requests,c.d.commits),(3,3))
            self.assertEqual(c.e.journal.sync_calls-start,8);f.finish(c)
            r=f.reader_module.JournalReader(c.e.journal.path)
            e=[json.loads(x) for x in r.read('events.jsonl').splitlines()]
            e=[{k:v for k,v in row.items() if k!='monotonic_ns'} for row in e if row['event'].startswith('MMIO_')]
            w=f.w;replies=[raw for raw in c.sock.sent if w.Header.unpack(raw[:256]).op in (w.RESULT,w.ACK)]
            captures.append(dict(replies=replies,events=e,registers=dict(c.reg),
                side_effects=[x for x in c.trace if x[0] in ('DMA','RELEASE')],
                requests=[r.read('request_%d.bin'%k) for k in range(3)],
                candidates=[r.read('candidate_%d.bin'%k) for k in range(3)]))
            if optimized:
                self.assertEqual(c.e.driver_helpers.vector_checks,6)
                self.assertEqual(c.e.driver_helpers.bound_files,9)
                s=json.loads(r.read('PS_DURABILITY_SUMMARY.json'))
                self.assertEqual(s['runtime_helpers'],RUNTIME_HELPERS)
        self.assertEqual(captures[0],captures[1])

    def test_invalid_input_stops_before_DMA_with_original_error(self):
        f,c=self.fixture(n=1);h=f.w.Header.unpack(f.requests[0][:256]);c.d.bound_asid=h.asid.hex()
        p=bytearray(f.requests[0][256:]);struct.pack_into('<i',p,f.w.WORD_BYTES,1<<30);p=bytes(p)
        h=dataclasses.replace(h,payload_sha=f.w.digest(p))
        with self.assertRaisesRegex(ValueError,'signed31 Q24 range'):c.d.run(h,p)
        self.assertFalse(any(x[0] in ('DMA','RELEASE') for x in c.trace));self.assertEqual(c.d.requests,0)

    def test_invalid_candidate_never_sends_result_or_COMMIT_ACK(self):
        f,c=self.fixture(n=1);bad=bytearray(f.candidates[0]);struct.pack_into('<i',bad,0,1<<30)
        with patch.object(f,'candidates',[bytes(bad)]):
            with self.assertRaisesRegex(ValueError,'signed31 Q24 range'):f.run_service(c)
        w=f.w;self.assertFalse(any(w.Header.unpack(x[:256]).op in (w.RESULT,w.ACK) for x in c.sock.sent))
        self.assertTrue(c.d.poisoned);self.assertEqual(c.d.commits,0)

    def test_bound_file_preserves_duplicate_failure_and_outside_delegation(self):
        f,c=self.fixture(n=1);helper=c.e.driver_helpers;seen=[]
        helper.original_save=lambda path,data:seen.append((path,data))
        outside=c.folder/'other'/'file.bin';helper.save_bytes(outside,b'outside')
        self.assertEqual(seen,[(outside,b'outside')]);self.assertEqual(helper.bound_files,0)
        helper.save_bytes(c.base.directory/'unique.bin',b'one')
        with self.assertRaisesRegex(ValueError,'Duplicate evidence file'):helper.save_bytes(c.base.directory/'unique.bin',b'two')
        self.assertTrue(c.e.journal.poisoned)

    def test_wrong_journal_owner_rejected_before_driver_rebind(self):
        f,c=self.fixture(n=1,optimized=False);before=c.d.run.__func__
        original=c.d.run.__func__.__globals__['save_bytes'];owners=original.__globals__['OWNERS']
        with patch.dict(owners,{c.base.directory.resolve():object()}):
            with self.assertRaisesRegex(ValueError,'OWNER'):BoundDriverHelpers(c.d,c.e)
        self.assertIs(c.d.run.__func__,before)

    def test_both_fsync_failures_still_block_corresponding_side_effect(self):
        for phase in ('COMMIT','ACK'):
            with self.subTest(phase=phase):
                f,c=self.fixture(n=1,fail=phase)
                with self.assertRaisesRegex(OSError,'CPU_FSYNC_'+phase):f.run_service(c)
                self.assertFalse(any(f.w.Header.unpack(x[:256]).op==f.w.ACK for x in c.sock.sent))
                if phase=='COMMIT':self.assertFalse(any(x[0]=='RELEASE' for x in c.trace))


if __name__=='__main__':unittest.main()

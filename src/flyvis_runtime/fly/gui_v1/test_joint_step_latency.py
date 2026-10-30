"""CPU-only exact event encoding and timing boundaries; saved hardware words."""
import json
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joint_diagnostics import JointDiagnostics
from joint_camera_io import LowLatencySocket
from ps_commit_evidence import encoded_mmio,MMIO_EVENTS,CommitEvidence
from test_joint_transport import OptionSocket


class EncodingTests(unittest.TestCase):
    def test_event_return_record_matches_original_API_and_encoded_line(self):
        lines=[];e=CommitEvidence.__new__(CommitEvidence)
        e.base=SimpleNamespace(in_compute=True,failed=False,last_event=None)
        e.failed=False;e.mmio_encoded=0;e.journal=SimpleNamespace(lock=threading.RLock(),append_line=lambda n,r:lines.append(r))
        record=e.event('MMIO_READ_INTENT',bank='reg',offset=0x14)
        self.assertEqual(record,json.loads(lines[0]));self.assertEqual(e.mmio_encoded,1)

    def test_exact_original_JSONL_for_every_fixed_event_and_boundary(self):
        for event in MMIO_EVENTS:
            for bank in ('reg','dma'):
                for offset in (0,0x14,0xfc,0xff):
                    for value in (0,1,0x7fffffff,0x80000000,0xffffffff):
                        v=dict(bank=bank,offset=offset)
                        if event.endswith('_RETURNED') or event=='MMIO_WRITE_INTENT':v['value']=value
                        expected=(json.dumps(dict(event=event,monotonic_ns=123456789,**v))+'\n').encode()
                        self.assertEqual(encoded_mmio(event,123456789,v),expected)

    def test_non_fixed_schema_always_uses_original_encoder(self):
        for values in (dict(bank='other',offset=0),dict(offset=0,bank='reg'),
                dict(bank='reg',offset=True),dict(bank='reg',offset=256),
                dict(bank='reg',offset=0,unknown=1)):
            self.assertIsNone(encoded_mmio('MMIO_READ_INTENT',123,values))
        self.assertIsNone(encoded_mmio('MMIO_READ_RETURNED',123,dict(bank='reg',offset=0,value=-1)))
        self.assertIsNone(encoded_mmio('OTHER_EVENT',123,dict(bank='reg',offset=0)))


class PSTimingAndEventsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_ps_commit_evidence import PSCommitTests
        cls.fixture_class=PSCommitTests;PSCommitTests.setUpClass()

    def fixture(self,n=3):
        f=self.fixture_class('test_original_service_and_driver_three_steps_identical_outputs')
        self.addCleanup(f.doCleanups);c=f.make(n=n)
        c.obj.connection=OptionSocket();c.e.attach_service(c.obj)
        return f,c

    def test_original_MMIO_events_words_ACK_and_barriers_preserved(self):
        captures=[]
        for fast in (False,True):
            f,c=self.fixture()
            if fast:f.run_service(c)
            else:
                with patch('ps_commit_evidence.encoded_mmio',return_value=None):f.run_service(c)
            self.assertEqual((c.d.requests,c.d.commits),(3,3));f.finish(c)
            r=f.reader_module.JournalReader(c.e.journal.path)
            events=[json.loads(x) for x in r.read('events.jsonl').splitlines()]
            mmio=[{k:v for k,v in e.items() if k!='monotonic_ns'} for e in events if e['event'] in MMIO_EVENTS]
            w=f.w
            captures.append(([raw for raw in c.sock.sent if w.Header.unpack(raw[:256]).op in (w.RESULT,w.ACK)],mmio))
            self.assertEqual(c.e.mmio_encoded,len(mmio) if fast else 0)
            for k in range(3):
                self.assertEqual(r.read('candidate_%d.bin'%k),f.candidates[k])
            profile=json.loads(r.read('PS_HOST_TIMING.json'))
            self.assertTrue(profile['timing_complete']);self.assertEqual(profile['run_id'],c.config['run_id'])
            names=[s['name'] for s in profile['spans']]
            self.assertEqual(names.count('driver.check_bounds'),3)
            self.assertEqual(names.count('driver.runtime_check'),7)  # HELLO, STEP and COMMIT
            barriers=[s for s in profile['spans'] if s['name'].startswith('journal.WIRE')]
            self.assertEqual(len(barriers),8)  # two handshake + 3*(COMMIT,ACK)
            self.assertTrue(all('journal_phase_delta_ns' in s for s in barriers))
        self.assertEqual(captures[0],captures[1])

    def test_limited_diagnostics_report_incomplete_without_changing_transactions(self):
        f,c=self.fixture(n=1);c.e.timing_rows=[];c.e.timing_capacity=2;c.e.timing_dropped=0
        f.run_service(c);f.finish(c)
        r=f.reader_module.JournalReader(c.e.journal.path);p=json.loads(r.read('PS_HOST_TIMING.json'))
        self.assertFalse(p['timing_complete']);self.assertGreater(p['dropped_spans'],0)
        self.assertEqual((c.d.requests,c.d.commits),(1,1))


class PCReceiveTimingTests(unittest.TestCase):
    def test_fragmented_header_and_payload_timers_preserve_bytes(self):
        s=OptionSocket();s.sendall=lambda b:None
        chunks=iter((b'a'*100,b'b'*156,b'c'*4));s.recv=lambda n:next(chunks)
        d=JointDiagnostics('CPU_SOCKET_TIMING');p=LowLatencySocket(s,d)
        p.sendall(b'request');data=p.recv(256)+p.recv(156)+p.recv(4)
        self.assertEqual(data,b'a'*100+b'b'*156+b'c'*4)
        names=[x['name'] for x in d.rows]
        self.assertEqual(names.count('wire.recv_header_wait'),2)
        self.assertEqual(names.count('wire.recv_payload_wait'),1)
        self.assertEqual(names.count('wire.socket_receive_wait'),3)


if __name__=='__main__':unittest.main()

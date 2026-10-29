"""Bounded CPU tests: source-preserving receipts and PS socket options. No devices."""
import copy
import dataclasses
import errno
import socket
from types import SimpleNamespace
import unittest

import numpy as np
from joint_camera_protocol import LatestCameraInput, conversion_receipt
from ps_commit_evidence import CommitEvidence
from test_joint_camera import RUN, item


class CompactReceiptTests(unittest.TestCase):
    def prepared(self):
        p=item(np.linspace(0,1,721,dtype='<f4'))
        m=LatestCameraInput(RUN,'recorded_protocol_fixture')
        raw=copy.deepcopy(p);raw.pop('values');raw.pop('conversion')
        m.receive(raw);m.take_raw()
        return m,p

    def test_same_source_pixels_and_721_values_as_legacy(self):
        m,p=self.prepared();n=LatestCameraInput(RUN,'recorded_protocol_fixture')
        raw=copy.deepcopy(p);raw.pop('values');raw.pop('conversion');n.receive(raw);n.take_raw()
        receipt=conversion_receipt(p);before=copy.deepcopy(receipt)
        m.accept_conversion(receipt);n.accept_conversion(p)
        self.assertEqual(m.freeze_for_step(),n.freeze_for_step())
        self.assertEqual(receipt,before);self.assertNotIn('png',receipt)
        s=m.status();self.assertEqual(s['compact_conversion_receipts'],1)
        self.assertEqual(s['elided_return_png_characters'],len(p['png']))

    def test_forged_identity_or_values_rejected_without_consuming_inflight(self):
        for field,value in [('run_id','ff'*16),('sequence',99),('received_monotonic_ns',1),
                ('png_sha256','0'*64),('hex_values_sha256','0'*64),('relative_s',.9),
                ('source_kind','real_windows_camera')]:
            with self.subTest(field=field):
                m,p=self.prepared();q=copy.deepcopy(conversion_receipt(p));q['source'][field]=value
                with self.assertRaises(ValueError):m.accept_conversion(q)
                self.assertEqual(m.status()['conversion_inflight'],1)
                self.assertEqual(m.status()['compact_conversion_receipts'],0)
                m.accept_conversion(conversion_receipt(p))
        m,p=self.prepared();q=copy.deepcopy(conversion_receipt(p));q['values'][0]=.1
        with self.assertRaisesRegex(ValueError,'BOXEYE_SHA'):m.accept_conversion(q)
        q=copy.deepcopy(conversion_receipt(p));q['conversion']['backend']='SUBSTITUTE'
        with self.assertRaisesRegex(ValueError,'OFFICIAL_CONVERTER'):m.accept_conversion(q)

    def test_bad_receipt_schema_and_embedded_image_rejected(self):
        for change in [dict(schema='unknown'),dict(png='extra'),dict(unexpected=True)]:
            m,p=self.prepared();q=copy.deepcopy(conversion_receipt(p));q.update(change)
            with self.assertRaisesRegex(ValueError,'RECEIPT_SCHEMA'):m.accept_conversion(q)

    def test_duplicate_or_unsolicited_receipt_cannot_advance_state(self):
        m,p=self.prepared();q=conversion_receipt(p);m.accept_conversion(q)
        with self.assertRaisesRegex(ValueError,'UNSOLICITED'):m.accept_conversion(q)
        self.assertEqual(m.status()['compact_conversion_receipts'],1)
        self.assertEqual(m.freeze_for_step()['source']['sequence'],0)

    def test_latest_input_and_held_steps_stay_bounded(self):
        m,p=self.prepared()
        for seq in range(1,4):
            q=copy.deepcopy(p);q['source'].update(sequence=seq,relative_s=seq*.1,
                received_monotonic_ns=p['source']['received_monotonic_ns']+seq)
            m.receive(dict(source=q['source'],png=q['png']))
        m.accept_conversion(conversion_receipt(p));m.freeze_for_step();m.freeze_for_step()
        self.assertEqual(m.status()['held_steps'],1);self.assertEqual(m.status()['raw_pending'],1)
        self.assertEqual(m.status()['dropped_before_conversion'],2)
        newest=m.take_raw();self.assertEqual(newest['source']['sequence'],3)


class OptionSocket:
    def init__(self,error=None,verified=1):self.calls=[];self.error=error;self.verified=verified
    def setsockopt(self,level,option,value):
        self.calls.append((level,option,value))
        if self.error and option==self.error[0]:raise OSError(self.error[1],'CPU_INJECTED_SOCKET_OPTION')
    def getsockopt(self,level,option):return self.verified


def options_owner(conn):
    e=CommitEvidence.__new__(CommitEvidence)
    e.socket_owner=SimpleNamespace(connection=conn);e.bound_socket=None
    e.socket_policy=dict(NODELAY_verified=False,QUICKACK_supported=hasattr(socket,'TCP_QUICKACK'),QUICKACK_calls=0)
    return e


class SocketOptionTests(unittest.TestCase):
    def test_NODELAY_once_and_QUICKACK_each_receive_if_supported(self):
        s=OptionSocket();e=options_owner(s);e._receive_socket_options();e._receive_socket_options()
        self.assertEqual(sum(c[1]==socket.TCP_NODELAY for c in s.calls),1)
        self.assertTrue(e.socket_policy['NODELAY_verified'])
        self.assertEqual(e.socket_policy['QUICKACK_calls'],2 if hasattr(socket,'TCP_QUICKACK') else 0)

    def test_unverified_NODELAY_and_changed_connection_rejected(self):
        e=options_owner(OptionSocket(verified=0))
        with self.assertRaisesRegex(ValueError,'NOT_APPLIED'):e._receive_socket_options()
        e=options_owner(OptionSocket());e._receive_socket_options();e.socket_owner.connection=OptionSocket()
        with self.assertRaisesRegex(ValueError,'CONNECTION_CHANGED'):e._receive_socket_options()

    @unittest.skipUnless(hasattr(socket,'TCP_QUICKACK'),'QUICKACK not offered by this OS')
    def test_unsupported_QUICKACK_is_explicit_but_io_failure_is_not_ignored(self):
        e=options_owner(OptionSocket(error=(socket.TCP_QUICKACK,errno.ENOPROTOOPT)))
        e._receive_socket_options();self.assertFalse(e.socket_policy['QUICKACK_supported'])
        self.assertTrue(e.socket_policy['NODELAY_verified']);e._receive_socket_options()
        e=options_owner(OptionSocket(error=(socket.TCP_QUICKACK,errno.EIO)))
        with self.assertRaises(OSError):e._receive_socket_options()

    def test_real_CPU_loopback_receives_same_bytes_and_NODELAY(self):
        # Only localhost, ephemeral port; no camera/GUI/board endpoint.
        with socket.socket() as listener:
            listener.settimeout(2);listener.bind(('127.0.0.1',0));listener.listen(1)
            with socket.socket() as client:
                client.settimeout(2);client.connect(listener.getsockname());conn,_=listener.accept()
                with conn:
                    conn.settimeout(2);e=options_owner(conn)
                    client.sendall(b'CPU_ONLY');self.assertEqual(conn.recv(8),b'CPU_ONLY')
                    e._receive_socket_options();self.assertEqual(conn.getsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY),1)
                    conn.sendall(b'ACK_FIXTURE');self.assertEqual(client.recv(11),b'ACK_FIXTURE')


class PSServiceOptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_ps_commit_evidence import PSCommitTests
        cls.fixture_class=PSCommitTests;PSCommitTests.setUpClass()

    def fixture(self,conn=None):
        f=self.fixture_class('test_original_service_and_driver_three_steps_identical_outputs')
        self.addCleanup(f.doCleanups);c=f.make(n=1)
        c.obj.connection=conn or OptionSocket();c.e.attach_service(c.obj)
        return f,c

    def test_original_service_result_ACK_and_two_barriers_unchanged(self):
        f,c=self.fixture();start=c.e.journal.sync_calls;f.run_service(c)
        self.assertEqual((c.d.requests,c.d.commits),(1,1));self.assertIsNone(c.d.pending)
        self.assertEqual(c.e.journal.sync_calls-start,4)  # HELLO, ATTEST, COMMIT, ACK
        self.assertTrue(c.e.socket_policy['NODELAY_verified'])
        w=f.w;replies=[r for r in c.sock.sent if w.Header.unpack(r[:256]).op in (w.RESULT,w.ACK)]
        self.assertEqual(replies[0][256:],f.candidates[0])
        self.assertEqual(replies[1],dataclasses.replace(w.Header.unpack(f.commits[0]),op=w.ACK).pack())
        f.finish(c)

    def test_socket_option_error_fails_before_any_DMA_or_result(self):
        f,c=self.fixture(OptionSocket(error=(socket.TCP_NODELAY,errno.EIO)))
        with self.assertRaises(OSError):f.run_service(c)
        self.assertEqual(c.d.requests,0);self.assertEqual(c.sock.sent,[])
        self.assertFalse(any(x[0] in ('DMA','RELEASE') for x in c.trace));self.assertTrue(c.e.failed)


if __name__=='__main__':unittest.main()

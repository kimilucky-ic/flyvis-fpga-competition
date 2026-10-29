"""CPU saved-wire replay with original PS service/driver and dummy MMIO only."""
import dataclasses
import copy
import hashlib
import json
import os
from pathlib import Path
import threading
import time
from types import SimpleNamespace
import unittest
import uuid
from unittest.mock import patch

import numpy as np
from live_protocol import HERE,load,sha
from joint_camera_control import hardware_module
from ps_commit_evidence import CommitEvidence,install_before_bind,policy_receipt,POLICY

OUT=HERE/'evidence/ps_commit_journal_20261017'

class MemorySocket:
    def init__(self,raw):self.raw=raw;self.at=0;self.sent=[]
    def recv(self,n):v=self.raw[self.at:self.at+n];self.at+=len(v);return v
    def sendall(self,raw):self.sent.append(raw)
    def settimeout(self,value):pass

class PSCommitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        h=load(HERE/'runtime/joint/7f111da4437843539eeffef2c6c2546e/hardware_handoff.json')
        cls.service=hardware_module(h,'service');cls.driver=hardware_module(h,'driver')
        cls.evidence=hardware_module(h,'light_evidence');cls.reader_module=hardware_module(h,'evidence_journal')
        cls.w=cls.service.w
        cls.reader=cls.reader_module.JournalReader(HERE/'runtime/joint/7f111da4437843539eeffef2c6c2546e/pc/evidence.fvej')
        cls.requests=[cls.reader.read('request_%d.bin'%k) for k in range(32)]
        cls.commits=[cls.reader.read('COMMIT_%d.bin'%k) for k in range(32)]
        cls.candidates=[cls.reader.read('candidate_%d.bin'%k) for k in range(32)]
        cls.results=[cls.w.Header.unpack(cls.reader.read('RESULT_%d.bin'%k)) for k in range(32)]

    def make(self,n=3,policy=True,fail=None):
        folder=OUT/'cpu_cases'/uuid.uuid4().hex;folder.mkdir(parents=True)
        w=self.w;first=w.Header.unpack(self.requests[0][:256]);trace=[];holder={}
        def sync(fd):
            e=holder.get('e');phase=getattr(e,'phase',None)
            trace.append(('fsync',phase))
            if fail is not None and phase==fail:raise OSError('CPU_FSYNC_'+fail)
            os.fsync(fd)
        config=dict(test_fixture=True,run_id=uuid.uuid4().hex,server_session=uuid.uuid4().hex,max_steps=n,max_worker_s=180)
        base=self.evidence.Evidence(folder/'ps',config,sync=sync)
        scope=dict(run_id=config['run_id'],server_session=config['server_session'],ps_evidence_adapter_sha256=sha(HERE/'ps_commit_evidence.py'))
        e=CommitEvidence(base,w,policy_receipt(scope,'0'*64)) if policy else base;holder['e']=e
        def cleanup():
            if not base.journal.closed:
                if base.journal.poisoned:base.journal.abandon()
                else:base.close()
        self.addCleanup(cleanup)
        class Buffer(np.ndarray):
            def flush(self):pass
            def invalidate(self):pass
        src=np.zeros(3*w.N,dtype='<i4').view(Buffer);dst=np.zeros(w.N,dtype='<i4').view(Buffer)
        src.device_address=0x100000;dst.device_address=0x200000
        reg={0x14:0,0x18:0,0xc0:3*w.N,0xc4:w.N,0xc8:10*w.N+1}
        def write_reg(offset,value):
            reg[offset]=value
            if offset==0x10 and value==1:reg[0x14]=1
            if offset==0x10 and value==2:
                trace.append(('RELEASE',reg[0x30]));reg[0x14]=0
        def write_dma(offset,value):
            if offset==0x28:
                k=reg[0x30];trace.append(('DMA',k));dst[:]=np.frombuffer(self.candidates[k],dtype='<i4')
                reg.update({0x14:6,0xd0:k,0xd4:0,0xcc:self.results[k].transfer_cycles})
        d=self.driver.Full485Driver.__new__(self.driver.Full485Driver)
        d.evidence=e;d.src=src;d.dst=dst;d.np=np;d.last_registers={}
        d.reg=SimpleNamespace(read=lambda off:reg.get(off,0),write=write_reg)
        d.dma=SimpleNamespace(read=lambda off:2,write=write_dma)
        d.plan=dict(max_steps=n,initial_full_sha256=first.old_sha.hex(),initial_H_sha256=w.digest(self.requests[0][256:256+w.WORD_BYTES]).hex())
        d.requests=d.commits=0;d.pending=None;d.committed={};d.poisoned=False;d.bound_asid=None
        d.boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        d.overlay=SimpleNamespace(is_loaded=lambda:True,bitfile_name='CPU_DUMMY_NO_BITSTREAM',timestamp='CPU_ONLY')
        d.server_session=config['server_session'];d.session_deadline=time.monotonic()+180;d.compute_deadline=None
        d.clock_guard=SimpleNamespace(check=lambda c:None)
        hello=w.Header(w.HELLO,first.asid,uuid.uuid4().bytes,0,w.IMAGE_PAIR,w.digest(b''),0)
        raw=hello.pack()+b''.join(self.requests[k]+self.commits[k] for k in range(n));sock=MemorySocket(raw)
        obj=SimpleNamespace(driver=d,evidence=e,config=config,lock=threading.RLock(),state='RUNNING',
            finish_requested=threading.Event(),clock_guard=d.clock_guard,inflight=False)
        def waiter(conn,t):
            if conn.at<len(conn.raw):return True
            obj.finish_requested.set();return False
        obj.waiter=waiter
        result=SimpleNamespace(base=base,e=e,d=d,scope=scope,config=config,sock=sock,obj=obj,trace=trace,reg=reg,folder=folder)
        return result

    def run_service(self,c):self.service.CameraBoardService.serve_connection(c.obj,c.sock)
    def finish(self,c):
        h=self.w.Header.unpack(self.commits[c.d.commits-1]);c.e.finish_window(dict(completed_steps=c.d.commits,
            last_txn=h.txn.hex(),last_unified_commit_sha256=h.parent_commit.hex(),source_closed=True,reason='STEP_LIMIT_COMPLETE'))
    def handshake_only(self,c):
        w=self.w;hello=w.Header.unpack(c.sock.raw[:256]);c.e.wire('rx',hello.pack())
        payload=b'{"CPU_fixture":true}'
        c.e.wire('tx_intent',dataclasses.replace(hello,op=w.ATTEST,payload_bytes=len(payload),payload_sha=w.digest(payload)).pack()+payload)
        c.e.event('COMPUTE_WINDOW_STARTED')

    def test_original_service_and_driver_three_steps_identical_outputs(self):
        rows=[]
        for policy in (False,True):
            c=self.make(policy=policy);start=c.e.journal.sync_calls;self.run_service(c);end=c.e.journal.sync_calls
            self.assertEqual((c.d.requests,c.d.commits),(3,3));self.assertIsNone(c.d.pending)
            replies=[x for x in c.sock.sent if self.w.Header.unpack(x[:256]).op in (self.w.RESULT,self.w.ACK)]
            rows.append(replies);self.assertEqual(end-start,2+(6 if policy else 12))
            if policy:self.assertEqual(c.e.deferred_wire_barriers,6)
            self.finish(c)
        self.assertEqual(rows[0],rows[1])
    def test_32_steps_have_64_barriers_and_bounded_pending(self):
        c=self.make(n=32);start=c.e.journal.sync_calls;self.run_service(c)
        self.assertEqual(c.e.journal.sync_calls-start,2+64);self.assertEqual(c.e.deferred_wire_barriers,64)
        self.assertLess(c.e.max_pending_bytes,1024*1024);self.finish(c)
        r=self.reader_module.JournalReader(c.e.journal.path)
        self.assertEqual(r.terminal['requests'],32);self.assertEqual(r.terminal['acks'],32)
    def test_commit_fsync_failure_prevents_RELEASE_and_ACK(self):
        c=self.make(n=1,fail='COMMIT')
        with self.assertRaisesRegex(OSError,'CPU_FSYNC_COMMIT'):self.run_service(c)
        self.assertFalse(any(e[0]=='RELEASE' for e in c.trace));self.assertEqual(c.d.commits,0)
        self.assertFalse(any(self.w.Header.unpack(x[:256]).op==self.w.ACK for x in c.sock.sent))
    def test_ACK_fsync_failure_after_RELEASE_never_sends_ACK(self):
        c=self.make(n=1,fail='ACK')
        with self.assertRaisesRegex(OSError,'CPU_FSYNC_ACK'):self.run_service(c)
        self.assertEqual(sum(e[0]=='RELEASE' for e in c.trace),1);self.assertEqual(c.d.commits,1)
        self.assertFalse(any(self.w.Header.unpack(x[:256]).op==self.w.ACK for x in c.sock.sent))
        self.assertTrue(c.e.failed)
    def test_received_COMMIT_is_durable_before_original_RELEASE(self):
        c=self.make(n=1);self.run_service(c)
        release=next(i for i,v in enumerate(c.trace) if v[0]=='RELEASE')
        self.assertIn(('fsync','COMMIT'),c.trace[:release]);self.assertIn(('fsync','ACK'),c.trace[release+1:])
    def test_disk_cut_before_COMMIT_has_no_uncommitted_wire(self):
        c=self.make(n=1);self.handshake_only(c)
        c.e.wire('rx',self.requests[0]);r=self.results[0]
        c.e.wire('tx_intent',r.pack()+self.candidates[0])
        disk=self.reader_module.JournalReader(c.e.journal.path,allow_incomplete=True)
        self.assertNotIn('wire_002_rx.bin',disk.files)
        c.e.wire('rx',self.commits[0]);disk=self.reader_module.JournalReader(c.e.journal.path,allow_incomplete=True)
        self.assertEqual(disk.read('wire_002_rx.bin'),self.requests[0]);self.assertEqual(disk.read('wire_003_tx_intent.bin'),r.pack()+self.candidates[0])
        self.assertEqual(disk.read('wire_004_rx.bin'),self.commits[0])
        self.assertIsNone(disk.terminal)
    def test_wrong_COMMIT_identity_cannot_release(self):
        c=self.make(n=1);self.handshake_only(c);c.e.wire('rx',self.requests[0]);c.e.wire('tx_intent',self.results[0].pack()+self.candidates[0])
        h=self.w.Header.unpack(self.commits[0])
        with self.assertRaisesRegex(ValueError,'COMMIT_IDENTITY'):c.e.wire('rx',dataclasses.replace(h,txn=b'9'*16).pack())
        self.assertTrue(c.e.failed)
    def test_ACK_requires_matching_RELEASE_and_exact_identity(self):
        for wrong in ('missing','state','txn','ACK'):
            with self.subTest(wrong=wrong):
                c=self.make(n=1);self.handshake_only(c);c.e.wire('rx',self.requests[0]);c.e.wire('tx_intent',self.results[0].pack()+self.candidates[0]);c.e.wire('rx',self.commits[0]);h=self.w.Header.unpack(self.commits[0])
                if wrong in ('state','txn'):
                    values=dict(step=0,txn=h.txn.hex(),state=0,error=0,commit_sha=h.parent_commit.hex());values.update({wrong:1 if wrong=='state' else '00'*16})
                    with self.assertRaises(ValueError):c.e.event('RELEASE_CONFIRMED',**values)
                else:
                    if wrong=='ACK':c.e.event('RELEASE_CONFIRMED',step=0,txn=h.txn.hex(),state=0,error=0,commit_sha=h.parent_commit.hex())
                    ack=dataclasses.replace(h,op=self.w.ACK,step=1 if wrong=='ACK' else 0)
                    with self.assertRaises(ValueError):c.e.wire('tx_intent',ack.pack())
    def test_memory_bound_stops_before_dummy_DMA(self):
        c=self.make(n=1);self.handshake_only(c);c.e.journal.writer.max_pending=1024
        with self.assertRaises(BufferError):c.e.wire('rx',self.requests[0])
        self.assertTrue(c.e.journal.poisoned);self.assertFalse(any(v[0]=='DMA' for v in c.trace))
    def test_incomplete_frame_revokes_policy(self):
        c=self.make(n=1)
        with self.assertRaisesRegex(ValueError,'INCOMPLETE'):c.e.wire('rx_incomplete',b'partial')
        with self.assertRaisesRegex(ValueError,'REVOKED'):c.e.wire('rx',c.sock.raw[:256])
    def test_finish_cannot_accept_uncommitted_step(self):
        c=self.make(n=1);self.handshake_only(c);c.e.wire('rx',self.requests[0])
        with self.assertRaisesRegex(ValueError,'FINISH_INCOMPLETE'):c.e.finish_window(dict(completed_steps=1))
    def test_install_requires_fresh_bound_scope_and_records_policy(self):
        for wrong in (None,'hash','policy','started'):
            with self.subTest(wrong=wrong):
                c=self.make(n=1,policy=False);digest=sha(HERE/'ps_commit_evidence.py')
                scope=dict(run_id=c.config['run_id'],server_session=c.config['server_session'],boot_id=c.d.boot_id,
                    execution_authority='CPU_FIXTURE_ONLY',ps_durability_policy=POLICY,ps_evidence_adapter_sha256=digest,source_sha256={'ps_commit_evidence.py':digest})
                raw=json.dumps(scope,sort_keys=True).encode();config=dict(c.config,boot_id=c.d.boot_id,scope_sha256=hashlib.sha256(raw).hexdigest(),
                    ps_durability_policy=POLICY,ps_evidence_adapter_sha256=digest)
                p=SimpleNamespace(config=config,driver=c.d,evidence=c.base,service=None,bind_attempted=False,scope_bytes=raw,receipt={})
                if wrong=='hash':config['ps_evidence_adapter_sha256']='0'*64
                if wrong=='policy':config['ps_durability_policy']='VOLATILE_AT_END'
                if wrong=='started':p.bind_attempted=True
                if wrong:
                    with self.assertRaises(ValueError):install_before_bind(p,raw,self.w)
                else:
                    adapter=install_before_bind(p,raw,self.w);self.assertIs(p.driver.evidence,p.evidence);self.assertIs(p.evidence,adapter)
                    self.assertEqual(p.receipt['ps_durability'],policy_receipt(scope,config['scope_sha256']))
                    with self.assertRaises(ValueError):install_before_bind(p,raw,self.w)

class PSAdmissionTests(unittest.TestCase):
    def test_PC_requires_signed_matching_policy_receipt_before_admission(self):
        from test_joint_camera_preparation import PreparationTests
        from joint_camera_preparation import PreparationAuthority,clock_binding,verify_prepared_packet
        from live_protocol import write
        fixture=PreparationTests('test_real_clock_receipt_body_can_publish_signed_preparation');fixture.setUp()
        digest=sha(HERE/'ps_commit_evidence.py');s=fixture.scope;decl=fixture.declaration
        s.update(ps_durability_policy=POLICY,ps_evidence_adapter_sha256=digest)
        s['source_sha256']=dict(s['source_sha256'],**{'ps_commit_evidence.py':digest})
        decl.update(ps_durability_policy=POLICY,ps_evidence_adapter_sha256=digest)
        write(fixture.root/'HARDWARE_DECLARATION.json',decl);s['hardware_declaration_sha256']=sha(fixture.root/'HARDWARE_DECLARATION.json')
        write(fixture.root/'scope.json',s);scope_sha=sha(fixture.root/'scope.json')
        config=dict(clock_binding(decl,s,scope_sha),control_key='31'*32);write(fixture.root/'PRIVATE_CONFIG.json',config)
        authority=PreparationAuthority(fixture.root)
        clock=hardware_module(decl,'clock');mono=[100_000_000_000];wall=[1_637_000_000_000_000_000]
        board=clock.BoardClockHandshake(config,mono_ns=lambda:mono[0],wall_ns=lambda:wall[0],boot=lambda:'CPU_BOOT')
        answer=authority.dispatch('/clock',board.challenge());mono[0]+=1_000_000;wall[0]+=1_000_000
        receipt=board.accept(answer).receipt(config)
        status=dict(authority.binding,state='BOARD_PREPARED',requests=0,commits=0,pending=False,poisoned=False,
            error=None,neural_connections=0,service_alive=True,clock_policy=receipt['policy'],clock_proof_sha256=receipt['proof_sha256'])
        body=dict(schema='flyvis-camera-retained-prepared/v1',binding=authority.binding,
            preparation_receipt={'ps_durability':policy_receipt(s,scope_sha)},clock_receipt=receipt,status=status)
        helpers=authority.helpers;binding=hardware_module(decl,'binding')
        with patch.object(binding,'validate_readonly_receipt',return_value={}) as read20:
            verify_prepared_packet(helpers.sign(body,'31'*32),decl,s,scope_sha);self.assertEqual(read20.call_count,1)
            for field in ('missing','adapter_sha256','run_id','normal_step_barriers'):
                bad=copy.deepcopy(body)
                if field=='missing':bad['preparation_receipt'].pop('ps_durability')
                else:bad['preparation_receipt']['ps_durability'][field]=4 if field=='normal_step_barriers' else 'wrong'
                read20.reset_mock()
                with self.subTest(field=field),self.assertRaisesRegex(ValueError,'PS_POLICY_NOT_PREPARED'):
                    verify_prepared_packet(helpers.sign(bad,'31'*32),decl,s,scope_sha)
                read20.assert_not_called()

if __name__=='__main__':unittest.main()

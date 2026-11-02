"""Bounded producer + independent full-record auditor. No PYNQ/board launcher."""
import hashlib
import json
import os
from pathlib import Path
import struct
import threading
import time
import uuid

from ddr_control import DdrControl,N,NE
from ddr_memory import OwnedDdr
from snapshot_records import decode_record,AuditSequence,LatestDisplay

def write_new(path,data):
    with Path(path).open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def save_new(path,value):write_new(path,(json.dumps(value,indent=2)+'\n').encode('utf-8'))
def compare_bits(actual,expected):
    if len(actual)!=N*4 or len(expected)!=N*4:raise ValueError('Full45669-state payload required')
    count=0;bad=[]
    for i,(a,b) in enumerate(zip(struct.iter_unpack('<I',actual),struct.iter_unpack('<I',expected))):
        if a!=b:
            count+=1
            if len(bad)<16:bad.append(dict(global_id=i,actual_hex='%08x'%a[0],expected_hex='%08x'%b[0]))
    return dict(words=N,mismatch_words=count,first_mismatches=bad,
        actual_sha256=hashlib.sha256(actual).hexdigest(),expected_sha256=hashlib.sha256(expected).hexdigest())


class AcceptanceSession:
    def __init__(self,mmio,allocator,barrier,inputs,expected,output,evidence='CPU_MOCK_ONLY'):
        if evidence not in ('CPU_MOCK_ONLY','OPERATOR_PHYSICAL_READS_UNATTESTED'):raise ValueError('Evidence scope')
        self.inputs=tuple(bytes(x) for x in inputs);self.expected=tuple(bytes(x) for x in expected)
        if not self.inputs or len(self.inputs)!=len(self.expected) or any(len(x)!=2884 for x in self.inputs) or any(len(x)!=N*4 for x in self.expected):raise ValueError('Complete bounded plan required')
        self.control=DdrControl(mmio)  # exact candidate ABI before any writes/allocation
        if self.control._r(0x10)!=0 or self.control._r(0x14) or self.control._r(0x18) or self.control._r(0x24):
            raise RuntimeError('Fresh unused candidate required; no restore/retry from uncertain state')
        self.output=Path(output);self.output.mkdir(parents=True,exist_ok=False)
        self.evidence=evidence;self.run_id=uuid.uuid4().hex;self.cookie=int(self.run_id[:8],16)
        self.failed=False;self.descriptors=[];self.audited=0;self.audit=AuditSequence(len(self.inputs));self.display=LatestDisplay()
        self._producer=threading.Lock();self._auditor=threading.Lock();self._metadata=threading.Lock()
        self.memory=OwnedDdr(allocator,barrier,len(self.inputs));self.timing=[]
        try:
            save_new(self.output/'RUN_CONTEXT.json',dict(run_id=self.run_id,evidence=evidence,board_result=False,
                slots=len(self.inputs),physical_base=self.memory.base,allocated_bytes=self.memory.size,cookie=self.cookie,
                initial_state_readback='UNAVAILABLE_IN_ABI_00110004; restore-clean flag plus full post-step comparisons only',
                automatic_retry=False,automatic_reset=False,clock='100MHz accepted implementation; actual clock must be checked by operator',
                input_sha256=[hashlib.sha256(x).hexdigest() for x in self.inputs],
                expected_sha256=[hashlib.sha256(x).hexdigest() for x in self.expected]))
        except BaseException:self.memory.release_unarmed();raise

    def _fail(self,exc):
        self.failed=True;self.control.failed=True
        try:save_new(self.output/'STOP.json',dict(status='IN_DOUBT_KEEP_DDR_AND_KERNEL_DO_NOT_RETRY_RESET_OR_FREE',
            evidence=self.evidence,error=type(exc).__name__+': '+str(exc),produced=len(self.descriptors),audited=self.audited,
            allocation_retained=self.memory.armed,board_result=False))
        except OSError:pass  # original exception wins; authoritative DDR remains pinned

    def start(self,timeout=5):
        if self.failed or self.memory.armed:raise RuntimeError('Session already started/failed')
        try:
            self.memory.pin_before_configure()  # conservative retention even on uncertain restore/configure
            self.control.restore_initial(timeout)
            self.control.configure(self.memory.base,self.memory.size,len(self.inputs),self.cookie)
        except BaseException as exc:self._fail(exc);raise

    def produce_next(self,timeout=5):
        with self._producer:
            if self.failed:raise RuntimeError('Failed session; no next STEP')
            index=len(self.descriptors)
            if index>=len(self.inputs):raise RuntimeError('Bounded plan exhausted; no next STEP')
            try:
                before=time.monotonic_ns();p=self.control.advance(self.inputs[index],timeout)
                elapsed=time.monotonic_ns()-before
                if p.frame_id!=index or p.sequence!=index+1:raise RuntimeError('Publication sequence')
                with self._metadata:
                    self.descriptors.append(p);self.timing.append(dict(frame_id=index,input_and_STEP_ns=elapsed))
                return p
            except BaseException as exc:self._fail(exc);raise

    def audit_next(self):
        # No producer lock during cache I/O, all-state compare, fsync or display.
        with self._auditor:
            if self.failed:raise RuntimeError('Failed session; reconcile retained DDR')
            with self._metadata:
                if self.audited>=len(self.descriptors):return None
                i=self.audited;p=self.descriptors[i]
            try:
                raw=self.memory.copy_record(p)
                write_new(self.output/('record_%06d.bin'%i),raw)  # preserve bad observations too
                record=decode_record(raw,i)
                comparison=compare_bits(record.state_bits,self.expected[i])
                comparison['input_exact']=record.input_bits==self.inputs[i]
                comparison['descriptor_cycles_exact']=record.cycles==p.cycles
                save_new(self.output/('compare_%06d.json'%i),comparison)
                if comparison['mismatch_words'] or not comparison['input_exact'] or not comparison['descriptor_cycles_exact']:
                    raise RuntimeError('Complete actual input/state/descriptor comparison failed')
                self.audit.append(record)
                save_new(self.output/('receipt_%06d.json'%i),dict(self.audit.receipts[-1],
                    run_id=self.run_id,cookie=self.cookie,record_bytes=len(raw),record_sha256=hashlib.sha256(raw).hexdigest(),
                    evidence=self.evidence,board_result=False))
                self.audited+=1;self.display.publish(record)
                return record
            except BaseException as exc:self._fail(exc);raise

    def finish(self):
        if self.failed or self.audited!=len(self.inputs) or len(self.descriptors)!=self.audited:
            raise RuntimeError('Every produced step needs a durable complete-state receipt')
        status=self.control._r(0x10)
        if status&1 or not status&8 or self.control._r(0x24) or self.control._r(0x14)!=self.audited:
            exc=RuntimeError('Final idle/full/error/count mismatch; keep DDR retained')
            self._fail(exc);raise exc
        result=dict(status='PASS_BOUNDED_FULL_STATE_COMPARISON',evidence=self.evidence,board_result=False,
            run_id=self.run_id,completed_steps=self.audited,states_compared=self.audited*N,input_words_compared=self.audited*721,
            nodes=N,edges=NE,mismatch_words=0,receipt_chain=self.audit.chain,timing=self.timing,
            display_frames_skipped=self.display.skipped_display_frames,allocation_retained=True,
            initial_state_readback='NOT_SUPPORTED_BY_THIS_ABI',physical_clock_measured=False,
            real_time_or_power_measured=False)
        save_new(self.output/'RESULT.json',result);return result

    def release_verified_full(self):
        # Explicit normal close only AFTER finish persisted its result. No
        # context-manager/finally cleanup can free an uncertain hardware target.
        if self.failed or not (self.output/'RESULT.json').is_file():raise RuntimeError('No complete durable result')
        self.memory.release_after_verified_full(self.control,self.audited)

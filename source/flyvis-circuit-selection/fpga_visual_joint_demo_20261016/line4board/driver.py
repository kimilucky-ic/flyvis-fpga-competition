"""Explicit full-run quota; reuse accepted A3R1 DMA/BRAM transaction code.

The run method below is an exact source copy of the sealed driver, except
for an added scope check and the explicit MAX_REQUESTS guard. No PYNQ I/O
on import. No constructor, download, allocation or reset is used here.
"""
import dataclasses
import pathlib
import time

from . import board_service as bs
from .protocol import *
from .evidence import save_bytes, save_json

MAX_REQUESTS = 1000


class Full485Driver(bs.PLDriver):
    def init__(self, *args, **kwargs):
        raise RuntimeError('Use validated retained-buffer reuse; no new constructor')

    def check_deadline(self):
        now = time.monotonic()
        if self.session_deadline is None or now > self.session_deadline:
            raise TimeoutError('Full485 session deadline; stop without recovery')
        if self.compute_deadline is not None and now > self.compute_deadline:
            raise TimeoutError('Short3 60-second compute deadline')

    def runtime_check(self):
        self.check_deadline()
        super().runtime_check()

    def check_bounds(self, h, payload):
        self.check_deadline()
        if self.requests != self.commits or self.pending is not None:
            raise RuntimeError('Previous candidate must have confirmed COMMIT')
        if h.step != self.requests or h.epoch != 0 or not 0 <= h.step < MAX_REQUESTS:
            raise ValueError('Only this plan steps0..999 epoch0, strictly sequential')
        if self.bound_asid is None or h.asid.hex() != self.bound_asid or h.config != CONFIG:
            raise ValueError('Full485 ASID/config mismatch')
        if self.requests == 0:
            if h.old_sha.hex() != self.plan['initial_full_sha256']:
                raise ValueError('Wrong frozen complete initial state')
            if digest(payload[:WORD_BYTES]).hex() != self.plan['initial_H_sha256']:
                raise ValueError('Wrong initial canonical H words')
        if self.evidence:
            import shutil
            if shutil.disk_usage(self.evidence.directory).free < 8 * 1024 * 1024:
                raise RuntimeError('PS evidence disk low; no new request')

    def finish(self, h, commit):
        self.check_deadline()
        if not commit or h.op != COMMIT:
            raise ValueError('Full485 permits COMMIT only; no automatic ABORT')
        if self.commits >= MAX_REQUESTS or self.requests != self.commits + 1:
            raise RuntimeError('Full485 COMMIT quota/order')
        return super().finish(h, True)

    def run(self,h,payload):
        self.check_bounds(h,payload)
        if self.poisoned or self.pending is not None or self.requests>=MAX_REQUESTS:raise RuntimeError('driver quarantined/pending/request limit')
        validate_words(payload)
        if h.op!=STEP or len(payload)!=INPUT_BYTES or digest(payload)!=h.payload_sha:raise ValueError('input integrity')
        prev=self.committed.get(h.asid)
        if prev and (h.step!=prev[0]+1 or h.epoch!=prev[4] or payload[:WORD_BYTES]!=prev[1] or h.parent_commit!=prev[2] or h.previous_txn!=prev[3]):raise ValueError('canonical PL recurrence/COMMIT chain mismatch')
        if not prev and (h.parent_commit!=bytes(32) or h.previous_txn!=bytes(16)):raise ValueError('first COMMIT chain')
        try:
            self.runtime_check()
            if self.evidence:save_bytes(self.evidence.directory/f'request_{self.requests}.bin',h.pack()+payload)
            self._event('REQUEST_ACCEPTED',step=h.step,txn=h.txn.hex(),asid=h.asid.hex(),payload_sha=h.payload_sha.hex())
            if self._read('reg',0x14)!=0 or self._read('reg',0x18)!=0:raise RuntimeError('request requires clean IDLE')
            ps_start=time.monotonic_ns()
            self.src[:]=self.np.frombuffer(payload,dtype='<i4');self.src.flush()
            self.dst.fill(self.np.int32(0x5a5a5a5a));self.dst.flush()
            flush_end=time.monotonic_ns()
            self._write('reg',0x20,PROFILE);self._write('reg',0x24,DT_Q24);self._write('reg',0x28,DT_NS)
            for offset,value in [(0x30,h.step),(0x38,h.epoch)]:
                self._write('reg',offset,value&0xffffffff);self._write('reg',offset+4,value>>32)
            self._sha_regs(0x40,h.asid);self._sha_regs(0x50,h.txn)
            self._sha_regs(0x60,h.config);self._sha_regs(0x80,h.old_sha);self._sha_regs(0xa0,h.payload_sha)
            # Input/candidate buffers stay pinned on every uncertain outcome.
            self._write('dma',0x48,self.dst.device_address);self._write('dma',0x4c,0)
            self._write('dma',0x18,self.src.device_address);self._write('dma',0x1c,0)
            self._event('DMA_LAUNCH_INTENT',commands=[['dma',0x58,WORD_BYTES],['reg',0x10,1],['dma',0x28,INPUT_BYTES]])
            start=time.monotonic_ns()
            # No filesystem waits between ARM and MM2S: PL watchdog is 100ms.
            self.dma.write(0x58,WORD_BYTES);self.reg.write(0x10,1)
            self.requests+=1;self.dma.write(0x28,INPUT_BYTES)
            self._event('DMA_LAUNCH_RETURNED',step=h.step)
            in_complete=None;compute_seen=None;out_complete=None;last=None
            deadline=time.monotonic()+1
            self._event('POLL_BEGIN',timeout_ns=1000000000)
            while True:
                # No fsync between polling reads: timings include only transition logs.
                a=int(self.dma.read(4));b=int(self.dma.read(0x34));state=int(self.reg.read(0x14));error=int(self.reg.read(0x18))
                self.last_registers.update({'dma:04':a,'dma:34':b,'reg:14':state,'reg:18':error})
                now=time.monotonic_ns()
                if a&2 and in_complete is None:in_complete=now
                if state in (5,6) and compute_seen is None:compute_seen=now
                if b&2 and state==6:out_complete=now
                if (a,b,state,error)!=last:
                    self._event('POLL_STATE',mm2s=a,s2mm=b,state=state,error=error);last=(a,b,state,error)
                if error or a&0x770 or b&0x770 or state==7:raise RuntimeError(f'PL/DMA error {error:#x} {a:#x} {b:#x}')
                if time.monotonic()>deadline:raise TimeoutError('DMA request timeout')
                if out_complete is not None:break
                time.sleep(0.001)
            self.dst.invalidate();candidate=self.dst.astype('<i4',copy=False).tobytes()
            invalidate_end=time.monotonic_ns()
            if self.evidence:save_bytes(self.evidence.directory/f'candidate_{self.requests-1}.bin',candidate)
            validate_words(candidate)
            cycles=self._read('reg',0xc8);echo=self._read('reg',0xd0)|(self._read('reg',0xd4)<<32)
            if (cycles,echo,self._read('reg',0xc0),self._read('reg',0xc4))!=(10*N+1,h.step,3*N,N):raise RuntimeError('PL counters/step mismatch')
            if (self._read('reg',0x38)|(self._read('reg',0x3c)<<32))!=h.epoch:raise RuntimeError('PL epoch mismatch')
            for offset,data in [(0x40,h.asid),(0x50,h.txn),(0x60,h.config),(0x80,h.old_sha),(0xa0,h.payload_sha)]:
                if b''.join(self._read('reg',offset+i).to_bytes(4,'big') for i in range(0,len(data),4))!=data:raise RuntimeError('PL identity echo mismatch')
            receipt=dataclasses.replace(h,op=RESULT,payload_bytes=WORD_BYTES,payload_sha=digest(candidate),compute_cycles=cycles,transfer_cycles=self._read('reg',0xcc))
            self.pending=(h,receipt,candidate)
            timing=dict(ps_dma_roundtrip_observed_ns=out_complete-start,input_idle_observed_ns=None if in_complete is None else in_complete-start,compute_done_observed_ns=None if compute_seen is None else compute_seen-start,output_after_compute_observed_ns=None if compute_seen is None else out_complete-compute_seen,input_copy_flush_ns=flush_end-ps_start,output_invalidate_copy_ns=invalidate_end-out_complete,ps_total_until_candidate_ns=time.monotonic_ns()-ps_start,poll_sleep_ns=1000000,core_cycles=cycles,adapter_elapsed_cycles=receipt.transfer_cycles,configured_clock_hz=100000000,timing_scope='PS_OBSERVATIONS_INCLUDE_POLL_LOG_IO; NOT_PRECISE_DMA_PHASE_LATENCIES')
            if self.evidence:save_json(self.evidence.directory/f'timing_{self.requests-1}.json',timing)
            self._event('CANDIDATE_READY',step=h.step,**timing)
            return receipt,candidate,timing
        except Exception:
            self.poisoned=True
            raise

"""Injectable CPU/PS control contract; no PYNQ import, connection or CLI.

The future operator must bind the exact HWH/image, own the contiguous DDR
allocation and provide a tested cache-invalidation/memory-order callback.
No reset/reload/retry is attempted after any uncertain step transition.
"""
from dataclasses import dataclass
import struct
import threading
import time
import step_profile as prof

N,NE,VERSION,BASE,STRIDE=45669,1513231,0x00110005,0x43c40000,188416


@dataclass(frozen=True)
class Published:
    sequence:int
    address:int
    frame_id:int
    cycles:int
    cookie:int


class DdrControl:
    def __init__(self,mmio,bulk_input=False):
        self.bulk_input=bulk_input;self.mmio=mmio;self.failed=False;self.session=None
        self._publication_lock=threading.Lock();self._owner_thread=threading.get_ident()
        if tuple(self._r(x) for x in (0x30,0x34,0x38,0x3c))!=(N,NE,VERSION,STRIDE):
            raise RuntimeError('Wrong complete-network candidate ABI; no writes')

    def _r(self,address):return int(self.mmio.read(address))&0xffffffff
    def _w(self,address,value):self.mmio.write(address,int(value)&0xffffffff)
    def _check(self,idle=False):
        if self.failed:raise RuntimeError('Failed session; reconcile without automatic retry/reset')
        if self._r(0x24):raise RuntimeError('DDR/neural error; preserve state and records')
        if idle and self._r(0x10)&1:raise RuntimeError('Candidate is busy')

    def _wait(self,timeout):
        end=time.monotonic()+timeout
        while True:
            self._check()
            if not self._r(0x10)&1:return
            if time.monotonic()>=end:raise TimeoutError('Candidate timeout; no automatic reset/retry')
            time.sleep(.001)

    def restore_initial(self,timeout=5):
        self._check(idle=True)
        if self._r(0x10)&4:raise RuntimeError('Configured audit session cannot be restored/reused')
        try:
            self._w(0,2);self._wait(timeout)
            if not self._r(0x10)&2 or self._r(0x14):raise RuntimeError('Complete restore failed')
        except BaseException:self.failed=True;raise

    def configure(self,address,length,slots,cookie,first_frame=0):
        if (address%4096 or address<0x100000 or length<STRIDE*slots or slots<1 or slots>65535
                or address+length>0x40000000 or not 0<=first_frame<=0xffffffff
                or first_frame+slots>0x100000000 or not 0<=cookie<=0xffffffff):
            raise ValueError('Invalid owned DDR/session bounds')
        self._check(idle=True)
        if self.session is not None or not self._r(0x10)&2 or self._r(0x10)&4:
            raise RuntimeError('Restore once before configuring a fresh session')
        try:
            for register,value in ((4,address),(8,address+length),(12,slots),(0x1c,first_frame),(0x2c,cookie)):
                self._w(register,value)
            self._w(0,4);self._check()
            if not self._r(0x10)&4:raise RuntimeError('Configuration not accepted')
            self.session=(address,address+length,slots,cookie,first_frame)
        except BaseException:self.failed=True;raise

    def write_inputs(self,payload):
        if self.bulk_input:
            # Public API still performs aligned ordered32bit stores, not an AXI burst.
            self.mmio.write(0x400,payload)
        else:
            for index,(word,) in enumerate(struct.iter_unpack('<I',payload)):self._w(0x400+index*4,word)

    def advance(self,input_bits,timeout=5):
        phase_t=prof.tick()
        payload=bytes(input_bits)
        if len(payload)!=721*4:raise ValueError('Exactly721 little-endian FP32 input words required')
        self._check(idle=True)
        if self.session is None:raise RuntimeError('No configured owned audit allocation')
        if self._r(0x10)&8:raise RuntimeError('Audit full; no neural step attempted')
        if self._r(0x18)!=0:raise RuntimeError('Partial/old input already staged; reconcile before loading')
        before=self._r(0x14)
        prof.add('control_preflight',phase_t)
        try:
            phase_t=prof.tick()
            self.write_inputs(payload)
            prof.add('control_input_721_mmio_writes',phase_t,len(payload));phase_t=prof.tick()
            if self._r(0x18)!=721:raise RuntimeError('Complete input was not staged')
            prof.add('control_staged_check',phase_t);phase_t=prof.tick()
            self._w(0,1);self._wait(timeout)
            prof.add('control_step_wait',phase_t);phase_t=prof.tick()
            if self._r(0x14)!=before+1:raise RuntimeError('Exactly one committed record was not produced')
            prof.add('control_completed_count_check',phase_t);phase_t=prof.tick()
            result=self.publication()
            prof.add('control_publication',phase_t)
            if result.sequence!=before+1:raise RuntimeError('Publication differs from completed count')
            return result
        except BaseException:self.failed=True;raise

    def release_durable(self,sequence):
        """Foreground owner only; caller supplies journal's fsynced contiguous prefix.
        Timeout/uncertain write never retries; identical known ACK is idempotent.
        """
        if threading.get_ident()!=self._owner_thread:raise RuntimeError('Only the foreground owner releases DDR')
        self._check(idle=True)
        if self.session is None:raise RuntimeError('no ring session')
        before=self._r(0x4c);committed=self._r(0x14)
        if type(sequence) is not int or not before<=sequence<=committed:
            raise ValueError('release must be a monotonic committed prefix')
        if sequence==before:return
        try:
            self._w(0x44,sequence);self._w(0x48,self.session[3]);self._w(0,16)
            self._check()
            if self._r(0x4c)!=sequence:raise RuntimeError('uncertain release; preserve buffers')
        except BaseException:self.failed=True;raise

    def publication(self):
        # One process owns the MMIO object. Only descriptor capture/read is
        # serialized between its producer and display threads; bulk copying,
        # validation and rendering must happen after this short lock releases.
        with self._publication_lock:return self._publication()

    def _publication(self):
        self._check()
        if self.session is None or not self._r(0x10)&32:raise RuntimeError('No complete published record')
        try:
            self._w(0,8)  # capture all descriptor fields from ONE live epoch
            seq=self._r(0x80);address=self._r(0x84);fid=self._r(0x88);cycles=self._r(0x8c)
            count=self._r(0x90);cookie=self._r(0x94);faults=self._r(0x98)
            base,end,slots,expected_cookie,first=self.session
            if (seq<1 or seq<=self._r(0x4c) or seq!=count or address!=base+((seq-1)%slots)*STRIDE
                    or address+STRIDE>end or fid!=first+seq-1 or cookie!=expected_cookie or faults
                    or cycles==0 or self._r(0x9c)!=N or self._r(0xa0)!=NE):
                raise RuntimeError('Coherent publication identity/bounds mismatch')
            return Published(seq,address,fid,cycles,cookie)
        except BaseException:self.failed=True;raise


def copy_published(record,owned_base,owned_bytes,invalidate_and_barrier,read_bytes):
    """Callbacks must act on an owned allocation; no implicit cache assumption.

    read_bytes(offset,length) must copy immutable committed record bytes. This
    function has no MMIO, allocation, DMA or board connection of its own.
    This is an immutable copy, not payload validation: use decode_record on the
    returned bytes before admitting the record into the complete audit.
    """
    offset=record.address-owned_base
    if offset<0 or offset+STRIDE>owned_bytes:raise ValueError('Record escapes owned allocation')
    if not callable(invalidate_and_barrier):raise ValueError('Explicit cache/order callback required')
    invalidate_and_barrier(offset,STRIDE)
    raw=bytes(read_bytes(offset,STRIDE))
    if len(raw)!=STRIDE:raise RuntimeError('Incomplete copied record')
    if (struct.unpack_from('<I',raw,8)[0]!=record.frame_id or
        struct.unpack_from('<I',raw,64)[0]!=VERSION or
        struct.unpack_from('<2I',raw,80)!=(record.sequence,record.cookie)):
        raise RuntimeError('Copied ring record generation/session identity differs')
    return raw

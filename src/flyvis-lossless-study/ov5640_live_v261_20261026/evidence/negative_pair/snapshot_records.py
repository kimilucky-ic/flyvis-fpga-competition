"""Offline record codec and latest-display ownership; no board/network access.

Before ARM release, DDR owns each record; afterward the durable batch retains it.
The display owns immutable copies; replacing a display never releases DDR.
The future PS reader must establish DMA completion/cache visibility before
calling decode_record; parsing a header alone is not a hardware commit proof.
"""
from dataclasses import dataclass
import hashlib
import struct
import threading
import numpy as np
from functools import lru_cache
import step_profile as prof


@lru_cache(maxsize=4)
def _rolling_geometry(n):
    index=np.arange(n,dtype=np.uint32)
    shifts=(np.uint32(n-1)-index)&np.uint32(31)
    right=np.uint32(32)-shifts
    for a in (index,shifts,right):a.flags.writeable=False
    return index,shifts,right

def rolling(blob):
    # Exact closed form of h = rotl32(h,1) XOR word XOR index.
    # XOR each term after the remaining n-1-index rotations, modulo32.
    words=np.frombuffer(blob,dtype='<u4')
    if not len(words):return 0
    index,shifts,right=_rolling_geometry(len(words))
    terms=words^index
    rotated=(terms<<shifts)|(terms>>right)
    return int(np.bitwise_xor.reduce(rotated,dtype=np.uint32))



@dataclass(frozen=True)
class Snapshot:
    frame_id:int
    input_bits:bytes
    state_bits:bytes
    cycles:int
    input_sha256:str
    state_sha256:str


def decode_record(raw,expected_frame,n=45669,ne=1513231,input_words=721,payload_checker=None,expected_sequence=None,expected_cookie=None):
    t=prof.tick('decode_header_and_slice');raw=bytes(raw)
    stride=((4096+4*n+4095)//4096)*4096
    if len(raw)!=stride:raise ValueError('Incomplete DDR record')
    h=struct.unpack_from('<32I',raw)
    expected={0:0x5331314c,1:0x10000,2:expected_frame,3:0,4:n,5:ne,
              6:4*input_words,7:4*n,9:ne,10:n,11:stride,14:128,15:4096,
              16:0x00110005,17:0x3ba3d70a,18:0,19:0,
              20:expected_frame+1 if expected_sequence is None else expected_sequence}
    expected.update({k:0 for k in range(22,32)})
    if expected_cookie is not None:expected[21]=expected_cookie
    if any(h[k]!=v for k,v in expected.items()):raise ValueError('Record header/profile mismatch')
    inp=raw[128:128+4*input_words];state=raw[4096:4096+4*n]
    prof.add('decode_header_and_slice',t);t=prof.tick('decode_native_checksums_and_finite' if payload_checker is not None else 'decode_rolling_checksums')
    if payload_checker is None:
        if rolling(inp)!=h[12] or rolling(state)!=h[13]:raise ValueError('Record payload checksum mismatch')
        prof.add('decode_rolling_checksums',t);t=prof.tick()
        for payload in (inp,state):
            if np.any((np.frombuffer(payload,dtype='<u4')&np.uint32(0x7f800000))==np.uint32(0x7f800000)):
                raise ValueError('Non-finite state/input')
        prof.add('decode_finite_check',t);t=prof.tick()
    else:
        if (n,ne,input_words)!=(45669,1513231,721):raise ValueError('native checker requires full-network shape')
        ci,cs,bad=payload_checker(raw)
        if ci!=h[12] or cs!=h[13]:raise ValueError('Record payload checksum mismatch')
        if bad:raise ValueError('Non-finite state/input')
        prof.add('decode_native_checksums_and_finite',t);t=prof.tick('decode_payload_sha256')
    ih=hashlib.sha256(inp).hexdigest();sh=hashlib.sha256(state).hexdigest()
    prof.add('decode_payload_sha256',t)
    return Snapshot(expected_frame,inp,state,h[8],ih,sh)


class AuditSequence:
    """Single-writer PC receipts for a finite, non-overwriting DDR session."""
    def __init__(self,capacity,first_frame=0):
        if capacity<1:raise ValueError('Finite positive capacity required')
        self.capacity,self.next_frame=capacity,first_frame
        self.records=[];self.receipts=[];self.chain='0'*64

    def append(self,record):
        if len(self.records)>=self.capacity:raise RuntimeError('Audit capacity exhausted; do not overwrite')
        if record.frame_id!=self.next_frame:raise ValueError('Missing, duplicate or reordered audit step')
        chain=hashlib.sha256(bytes.fromhex(self.chain)+struct.pack('<I',record.frame_id)
                             +bytes.fromhex(record.input_sha256)+bytes.fromhex(record.state_sha256)).hexdigest()
        self.records.append(record)
        self.receipts.append(dict(frame_id=record.frame_id,input_sha256=record.input_sha256,
                                  state_sha256=record.state_sha256,previous_chain=self.chain,chain=chain))
        self.chain=chain;self.next_frame+=1


class LatestDisplay:
    """One immutable reader lease + one latest reference, no producer wait.

The third ownership role is the hardware writer's uncommitted DDR record.
All records remain in the audit; no physical full-state triple copy is needed.
"""
    def __init__(self):
        self.lock=threading.Lock();self.latest=None;self.reading=None
        self.last_acquired=-1;self.skipped_display_frames=0

    def publish(self,record):
        with self.lock:
            if self.latest is not None and record.frame_id<=self.latest.frame_id:
                raise ValueError('Display publication order')
            self.latest=record

    def acquire(self):
        with self.lock:
            if self.reading is not None:raise RuntimeError('Only one display lease allowed')
            if self.latest is None or self.latest.frame_id==self.last_acquired:return None
            self.reading=self.latest
            self.skipped_display_frames+=max(0,self.reading.frame_id-self.last_acquired-1)
            self.last_acquired=self.reading.frame_id
            return self.reading

    def release(self,frame_id):
        with self.lock:
            if self.reading is None or self.reading.frame_id!=frame_id:raise ValueError('Wrong display lease release')
            self.reading=None

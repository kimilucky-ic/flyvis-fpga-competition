"""Owned contiguous DDR + explicit cache ordering. No automatic hardware import."""
import ctypes
import step_profile as prof
import hashlib
import json
from numbers import Integral
from pathlib import Path
import platform
import shutil
import subprocess

from ddr_control import STRIDE

# Armed allocations survive exceptions and loss of caller references. A kernel
# exit still destroys this protection; IN_DOUBT requires human reconciliation.
_PINNED={}


class OwnedDdr:
    def __init__(self,allocator,barrier,slots):
        if not isinstance(slots,int) or isinstance(slots,bool) or not 1<=slots<=65535:
            raise ValueError('Invalid exact slot count')
        if slots*STRIDE>0x3ff00000 or not callable(barrier):raise ValueError('DDR bounds/barrier')
        self.slots=slots;self.size=slots*STRIDE;self.barrier=barrier;self.armed=False;self.released=False
        self.buffer=allocator(shape=(self.size,),dtype='u1',cacheable=True)
        try:
            b=self.buffer;base=b.physical_address
            if (not isinstance(base,Integral) or base%4096 or base<0x100000 or base+self.size>0x40000000
                    or b.nbytes!=self.size or b.ndim!=1 or b.dtype.itemsize!=1 or not b.flags.c_contiguous
                    or b.coherent is not False or not callable(getattr(b,'flush',None))
                    or not callable(getattr(b,'invalidate',None)) or not callable(getattr(b,'freebuffer',None))):
                raise ValueError('Allocator did not return exact owned cacheable HP0 DDR')
            self.base=int(base)
            b.fill(0);b.flush();barrier()  # eliminate all dirty CPU lines BEFORE PL ownership
            b.flags.writeable=False       # no CPU writes/flushes once the PL can write
        except BaseException:
            free=getattr(self.buffer,'freebuffer',None)
            if callable(free):free()  # never configured: this allocation cannot be a PL target
            self.buffer=None;raise

    def pin_before_configure(self):
        if self.released or self.armed:raise RuntimeError('Allocation ownership transition repeated')
        self.armed=True;_PINNED[id(self)]=self

    def copy_record(self,descriptor):
        if self.released or not self.armed:raise RuntimeError('No retained armed DDR')
        offset=descriptor.address-self.base
        if offset<0 or offset%STRIDE or offset+STRIDE>self.size:raise ValueError('Record escapes owned slot')
        view=self.buffer[offset:offset+STRIDE]
        t=prof.tick();self.barrier();prof.add('ddr_barrier_before',t);t=prof.tick()
        view.invalidate();prof.add('ddr_cache_invalidate',t);t=prof.tick()
        self.barrier();prof.add('ddr_barrier_after',t);t=prof.tick()
        raw=view.tobytes(order='C');prof.add('ddr_immutable_copy',t,len(raw))
        if len(raw)!=STRIDE:raise RuntimeError('Incomplete cache-visible copy')
        return raw

    def release_unarmed(self):
        if self.armed:raise RuntimeError('Armed DDR cannot be automatically freed')
        self.buffer.freebuffer()
        self.buffer=None;self.released=True

    def release_after_verified_full(self,control,verified_records):
        # Ring credit release is NOT freeing the allocation. This candidate has
        # no hardware quiesce/unconfigure protocol; retain the entire allocation.
        raise RuntimeError('Ring allocation stays pinned; only individual durable slots can be ACKed')


def pynq_allocator_and_barrier(native_dir,operator_authorized=False):
    """Future board-local binding only; never programs, resets or starts PL.

    Caller must separately establish exclusive board ownership, exact loaded
    BIT/HWH, nominal clock and HP0 width. Current default rejects BEFORE imports,
    compilation or allocation. CPU tests inject their own allocator/barrier.
    """
    if not operator_authorized:raise RuntimeError('Board-local binding is not authorized')
    if platform.machine()!='armv7l':raise RuntimeError('Only prepared ARMv7 Zynq runtime supported')
    import pynq
    if not str(pynq.__version__).startswith('2.7.'):raise RuntimeError('Prepared PYNQ2.7 API required')
    cc=shutil.which('cc') or shutil.which('gcc')
    if not cc:raise RuntimeError('ARM compiler absent; no allocation attempted')
    out=Path(native_dir);out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).with_name('arm_barrier.c');library=out/'line11_barrier.so'
    cmd=[cc,'-shared','-fPIC','-O2',str(source),'-o',str(library)]
    result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
    (out/'compile.log').write_bytes(result.stdout);result.check_returncode()
    lib=ctypes.CDLL(str(library.resolve()));fn=lib.line11_dsb;fn.argtypes=[];fn.restype=None
    (out/'identity.json').write_text(json.dumps(dict(command=cmd,
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        library_sha256=hashlib.sha256(library.read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8')
    return pynq.allocate,lambda:fn()

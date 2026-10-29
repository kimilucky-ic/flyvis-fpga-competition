"""Owned HP1 camera allocation; retained after arming. No auto-free/reset."""
from numbers import Integral
SIZE=640*480*3
_PINNED={}
class CameraDdr:
    def init__(self,allocate,barrier,forbidden):
        self.barrier=barrier;self.armed=False
        b=self.buffer=allocate(shape=(3*SIZE,),dtype='u1',cacheable=True)
        try:
            a=b.physical_address
            if (not isinstance(a,Integral) or a%4096 or a<0x100000 or a+3*SIZE>0x40000000
                or b.nbytes!=3*SIZE or b.ndim!=1 or b.dtype.itemsize!=1 or not b.flags.c_contiguous
                or b.coherent is not False or any(a<hi and lo<a+3*SIZE for lo,hi in forbidden)
                or not all(callable(getattr(b,n,None)) for n in ('flush','invalidate','freebuffer'))):
                raise ValueError('Invalid/overlapping HP1 allocation')
            self.base=int(a);self.size=3*SIZE;self.addresses=[self.base+i*SIZE for i in range(3)]
            b.fill(0);b.flush();barrier();b.flags.writeable=False
        except BaseException:
            if callable(getattr(b,'freebuffer',None)):b.freebuffer()
            raise
    def pin(self):
        if self.armed:raise RuntimeError('Camera allocation already armed')
        self.armed=True;_PINNED[id(self)]=self
    def copy(self,address,size):
        if not self.armed or address not in self.addresses or size!=SIZE:raise ValueError('Unowned camera buffer')
        off=address-self.base;view=self.buffer[off:off+SIZE]
        self.barrier();view.invalidate();self.barrier();raw=view.tobytes(order='C')
        if len(raw)!=SIZE:raise RuntimeError('Incomplete frame copy')
        return raw

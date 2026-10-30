"""Bounded MMIO transactions; no hardware import, automatic reset or retry.
Bounds assume each individual MMIO access returns; AXI interconnect hang is a
separate hardware fault. One caller owns the controller for the entire session.
"""
import time
class Bounded:
    def init__(self,mmio,timeout=.25,clock=time.monotonic,max_polls=100000):
        if timeout<=0 or max_polls<1:raise ValueError('invalid bounds')
        self.io,self.timeout,self.clock,self.max_polls=mmio,timeout,clock,max_polls
        self.failed=False
    def wait(self,predicate):
        for _ in range(self.max_polls):
            if self.clock()>=self.deadline:raise TimeoutError('transaction deadline')
            ready=predicate()
            if self.clock()>=self.deadline:raise TimeoutError('late MMIO return')
            if ready:return
        raise TimeoutError('poll budget')
    def begin(self):
        if self.failed:raise RuntimeError('failed session; preserve hardware state')
        self.deadline=self.clock()+self.timeout

class Iic(Bounded):
    def _poll(self,condition,read_final=False):
        def check():
            irq=self.io.read(0x20)
            if irq&(1 if read_final else 3):raise RuntimeError('IIC arbitration/NACK')
            return condition(self.io.read(0x104),irq)
        self.wait(check)
    def _idle(self):
        self._poll(lambda sr,irq:not sr&4)
        if self.io.read(0x104)&0xc0!=0xc0:raise RuntimeError('IIC FIFO not empty')
        self.io.write(0x20,self.io.read(0x20)&0x17) # toggle-on-write: clear asserted only
        self.io.write(0x120,15)
        self.io.write(0x100,1) # enable, no reset
    def _put(self,value):
        self._poll(lambda sr,irq:not sr&0x10)
        self.io.write(0x108,value)
    def _send(self,payload):
        self._idle();self._put(0x178)
        for i,value in enumerate(payload):self._put(value|(0x200 if i==len(payload)-1 else 0))
        self._poll(lambda sr,irq:bool(irq&0x10) and not sr&4 and bool(sr&0x80))
    def transaction(self,reg,value=None):
        if type(reg)is not int or not 0<=reg<=65535 or (value is not None and (type(value)is not int or not 0<=value<=255)):raise ValueError('register/data bounds')
        self.begin()
        try:
            payload=[reg>>8,reg&255]
            if value is not None:self._send(payload+[value]);return True
            self._send(payload);self._idle();self._put(0x179)
            self._poll(lambda sr,irq:bool(sr&4))
            self.io.write(0x20,self.io.read(0x20)&0x10)
            self._put(0x201) # dynamic stop plus one receive byte
            self._poll(lambda sr,irq:not sr&0x40,read_final=True)
            data=self.io.read(0x10c)&255
            self._poll(lambda sr,irq:bool(irq&0x10) and not sr&4,read_final=True)
            # Final receiver NACK is expected; do not leak it to next transaction.
            self.io.write(0x20,self.io.read(0x20)&0x17)
            return data
        except BaseException:self.failed=True;raise
    def read16(self,reg):return self.transaction(reg)
    def write16(self,reg,value):return self.transaction(reg,value)

class OneFrameVdma(Bounded):
    def init__(self,mmio,pool,addresses,owned_ranges,forbidden_ranges,cache_copy,**kwargs):
        super().init__(mmio,**kwargs)
        self.pool,self.addresses,self.copy=pool,tuple(addresses),cache_copy
        self.size=640*480*3
        if pool.size!=self.size or len(addresses)!=len(pool.states):raise ValueError('fixed VGA RGB888 buffers required')
        regions=[]
        for a in addresses:
            end=a+self.size
            if type(a) is not int or a%4096 or a<0x100000 or end>0x40000000 or not any(lo<=a and end<=hi for lo,hi in owned_ranges):raise ValueError('unowned DMA range')
            if any(a<hi and lo<end for lo,hi in list(forbidden_ranges)+regions):raise ValueError('DMA overlap')
            regions.append((a,end))
    def capture(self,source_id,timestamp_ns):
        self.begin();token=None
        try:
            sr=self.io.read(0x34)
            if not sr&1 or sr&0xfff0:raise RuntimeError('VDMA not clean halted')
            token=self.pool.grant()
            if token is None:return None
            address=self.addresses[token[0]]
            self.io.write(0x34,0x7000) # clear only completion/error IRQ flags
            self.io.write(0x28,self.io.read(0x28)&~0x1f00) # write park slot0
            for reg in (0xac,0xb0,0xb4):self.io.write(reg,address)
            self.io.write(0xa8,1920);self.io.write(0xa4,1920)
            self.io.write(0x30,0x10011) # run, park, frame-count-enable, count1
            self.io.write(0xa0,480) # VSIZE last starts capture
            def done():
                status=self.io.read(0x34)
                if status&0xfff0&~0x7000 or status&0x4000:raise RuntimeError('VDMA capture error')
                return status&0x1001==0x1001 # frame IRQ AND halted, not IRQ alone
            self.wait(done)
            raw=self.copy(address,self.size) # backend invalidate+barrier+immutablecopy
            self.pool.complete(token,source_id,timestamp_ns,raw)
            self.io.write(0x34,0x1000)
            return token
        except BaseException:
            self.failed=True # WRITING token retained; no reset/free/retry
            raise

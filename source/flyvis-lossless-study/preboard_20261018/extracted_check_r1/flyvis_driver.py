"""Board-local control and readback only. No neural computation or CPU fallback.

Importing this module does not import PYNQ or access hardware. Inject an MMIO
object only in an explicitly authorized board operation.
"""
import struct,time
N=45669
NE=1513231
BASE=0x43C30000
SPAN=4096
VERSION=0x00110002
class FlyVisFull:
    def init__(self,mmio):
        self.mmio=mmio
        if (self._r(0x30),self._r(0x34),self._r(0x38))!=(N,NE,VERSION):
            raise RuntimeError('Network dimensions/interface version do not match this driver')
    def _r(self,addr):return int(self.mmio.read(addr))&0xffffffff
    def _w(self,addr,value):self.mmio.write(addr,int(value)&0xffffffff)
    def status(self):
        v=self._r(0x10)
        return dict(busy=bool(v&1),selected_valid=bool(v&2),restoring=bool(v&4),state_clean=bool(v&8),phase=(v>>9)&31)
    def _idle(self,clean=False):
        s=self.status()
        if s['busy']:raise RuntimeError('Network is busy')
        if clean and not s['state_clean']:raise RuntimeError('Restore the complete neural state before starting or reading')
    def _wait_idle(self,timeout):
        end=time.monotonic()+timeout
        while self.status()['busy']:
            if self._r(0x2c):raise RuntimeError('Hardware fault flags are set')
            if time.monotonic()>=end:raise TimeoutError('Network did not complete before deadline; no automatic reset issued')
            time.sleep(0.002)
        if self._r(0x2c):raise RuntimeError('Hardware fault flags are set')
    def restore(self,timeout=5.0):
        self._idle();self._w(0,2);self._wait_idle(timeout)
        if not self.status()['state_clean'] or self._r(0x14)!=0:
            raise RuntimeError('PL restore did not establish a fresh complete state')
    def load_frame_bits(self,payload):
        self._idle()
        payload=bytes(payload)
        if len(payload)!=721*4:raise ValueError('Expected exactly 721 little-endian FP32 words')
        for i,(word,) in enumerate(struct.iter_unpack('<I',payload)):self._w(0x400+4*i,word)
    def run_steps(self,steps,timeout=None):
        if isinstance(steps,bool) or not isinstance(steps,int) or not 1<=steps<=0xffffffff:
            raise ValueError('Use a finite positive step count')
        self._idle(clean=True)
        before=self._r(0x14)
        self._w(0x0c,0);self._w(4,steps);self._w(0,1)
        self._wait_idle(timeout if timeout is not None else max(10.0,steps*2.0+5.0))
        after=self._r(0x14)
        if (after-before)&0xffffffff!=steps:raise RuntimeError('Completed-step count differs from request')
        info=dict(completed_steps=after,last_cycles=self._r(0x18),edges=self._r(0x1c),nodes=self._r(0x20),state_checksum=self._r(0x24),faults=self._r(0x2c))
        if info['edges']!=NE or info['nodes']!=N:raise RuntimeError('Whole-network edge/node count mismatch')
        return info
    def read_state_bits(self):
        self._idle(clean=True)
        saved=self._r(8);words=[]
        try:
            for node in range(N):
                self._w(8,node);words.append(self._r(0x3c))
        finally:self._w(8,saved)
        return struct.pack('<'+str(N)+'I',*words)

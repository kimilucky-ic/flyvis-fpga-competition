"""ABI2 bulk DDR controller. No board access at import, no Overlay download.
Caller must supply a separately authorized, already loaded ABI2 overlay.
All three CMA buffers remain owned until the hardware transport is idle.
"""
import time
import numpy as np

class FlyvisBBulk:
    BASE=0x43C20000
    HP0_ADDRESS_LIMIT=0x40000000
    def init__(self, overlay, edge_records):
        from pynq import MMIO, allocate
        self.overlay=overlay
        self.mmio=MMIO(self.BASE,0x20000)
        self.edges=self.inputs=self.outputs=None
        if [self.mmio.read(x) for x in (0,4,8,12,16,20)]!=[0x46564232,2,5768,16402,433880,645]:
            raise RuntimeError('Wrong B bulk hardware identity/ABI/dimensions')
        if self.mmio.read(0x1c)&9:raise RuntimeError('Existing B request is busy')
        records=np.asarray(edge_records)
        if records.shape!=(433880,) or records.dtype!=np.dtype('<u8'):
            raise ValueError('Require all frozen 433880 little-endian uint64 records')
        try:
            self.edges=allocate(shape=(433880,),dtype=np.uint64)
            self.inputs=allocate(shape=(22170,),dtype=np.int32)
            self.outputs=allocate(shape=(5768,),dtype=np.int32)
            self._addresses()
            self.edges[:]=records
            self.edges.flush()
        except Exception:
            for name in ('edges','inputs','outputs'):
                buf=getattr(self,name)
                if buf is not None:buf.freebuffer();setattr(self,name,None)
            raise

    def _addresses(self):
        ranges=[]
        for name,size in (('edges',3471040),('inputs',88680),('outputs',23072)):
            buf=getattr(self,name)
            if buf is None:raise RuntimeError('Closed/incomplete B controller')
            address=int(buf.physical_address)
            if address<0 or address&7 or address+size>self.HP0_ADDRESS_LIMIT:
                raise ValueError('Invalid physical '+name+' range')
            ranges.append((address,address+size))
        if any(a<d and c<b for i,(a,b) in enumerate(ranges) for c,d in ranges[i+1:]):
            raise ValueError('Overlapping DDR buffers')
        return [a for a,b in ranges]

    def run_once(self,sources,old_x,step_id,old_state_tag,expected_signature,timeout=5.0):
        begin=time.perf_counter()
        addresses=self._addresses()
        src=np.asarray(sources);x=np.asarray(old_x)
        if src.shape!=(16402,) or x.shape!=(5768,):raise ValueError('Full state required')
        for values in (src,x):
            if not np.issubdtype(values.dtype,np.signedinteger) or np.any(values<-(1<<30)) or np.any(values>=(1<<30)):
                raise ValueError('Signed31 integer state required without truncation')
        if not 0<=int(expected_signature)<(1<<64):raise ValueError('Signature must fit unsigned64')
        if timeout<=0:raise ValueError('Positive bounded host timeout required')
        if self.mmio.read(0x1c)&9:raise RuntimeError('B computation/DDR transport busy')
        self.inputs[:16402]=src;self.inputs[16402:]=x
        self.edges.flush();self.inputs.flush()
        # Prevent a dirty CPU output cache line being evicted over later HP0 writes.
        self.outputs.flush()
        starts_before=self.mmio.read(0x68)
        for offset,value in ((0x20,step_id),(0x24,old_state_tag),(0x28,addresses[0]),
                             (0x2c,expected_signature&0xffffffff),(0x30,expected_signature>>32),
                             (0x80,addresses[1]),(0x84,addresses[2])):
            self.mmio.write(offset,int(value)&0xffffffff)
        self.mmio.write(0x18,1)
        request_begin=time.perf_counter();self.mmio.write(0x18,2)
        while not self.mmio.read(0x1c)&2:
            if time.perf_counter()-request_begin>timeout:
                raise TimeoutError('B timeout: retain ALL DDR buffers; no candidate or COMMIT')
        flags=self.mmio.read(0x1c)
        errors=[self.mmio.read(o) for o in (0x34,0x38,0x3c,0x88,0x8c)]
        signature=self.mmio.read(0x48)|(self.mmio.read(0x4c)<<32)
        if flags&9 or not flags&4 or any(errors) or signature!=expected_signature:
            raise RuntimeError(f'B request rejected flags={flags:x} errors={errors}; no candidate/COMMIT')
        expected={0x44:433880,0x58:433880,0x64:22170,0x9c:5768,
                  0x50:step_id&0xffffffff,0x54:old_state_tag&0xffffffff,0x68:(starts_before+1)&0xffffffff}
        if any(self.mmio.read(o)!=v for o,v in expected.items()):raise RuntimeError('Result count or identity mismatch')
        # RESULT_OK proves all write responses arrived. CPU must now discard stale data.
        self.outputs.invalidate()
        candidate=np.array(self.outputs,dtype=np.int32,copy=True)
        if np.any(candidate<-(1<<30)) or np.any(candidate>=(1<<30)):raise RuntimeError('Malformed signed31 candidate')
        return dict(candidate=candidate,core_cycles=self.mmio.read(0x40),
                    input_cycles=self.mmio.read(0x90),output_cycles=self.mmio.read(0x94),
                    request_cycles=self.mmio.read(0x98),reader_stall_cycles=self.mmio.read(0x5c),
                    request_and_readback_seconds=time.perf_counter()-request_begin,
                    total_host_seconds=time.perf_counter()-begin,step_id=step_id,
                    old_state_tag=old_state_tag,signature=signature)

    def close(self):
        if any(getattr(self,n) is not None for n in ('edges','inputs','outputs')):
            if self.mmio.read(0x1c)&9:raise RuntimeError('Retain ALL buffers until DDR/computation idle')
            for name in ('edges','inputs','outputs'):
                buf=getattr(self,name)
                if buf is not None:buf.freebuffer();setattr(self,name,None)

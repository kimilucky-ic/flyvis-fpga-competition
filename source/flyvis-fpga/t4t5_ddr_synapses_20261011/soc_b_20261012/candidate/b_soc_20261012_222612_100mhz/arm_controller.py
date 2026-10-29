"""ARM-side B controller. No import-time board I/O or bitstream download.

Call only with an already-loaded, separately authorized B Overlay.
The edge CMA buffer stays alive until both core and reader are idle.
"""
import time
import numpy as np

class FlyvisB:
    BASE=0x43C20000
    HP0_ADDRESS_LIMIT=0x40000000  # Actual HWH HP0_DDR_LOWOCM aperture, exclusive.
    def init__(self,overlay,edge_records):
        from pynq import MMIO,allocate
        self.overlay=overlay
        self.mmio=MMIO(self.BASE,0x20000)
        if self.mmio.read(0)!=0x46564231 or self.mmio.read(4)!=1:
            raise RuntimeError('Wrong hardware B identity/ABI')
        if [self.mmio.read(x) for x in (8,12,16,20)]!=[5768,16402,433880,645]:
            raise RuntimeError('Wrong full-scale B dimensions')
        records=np.asarray(edge_records)
        if records.shape!=(433880,) or records.dtype!=np.dtype('uint64'):
            raise ValueError('Supply the frozen 433880 uint64 LE64 records without filtering')
        self.edges=allocate(shape=(433880,),dtype=np.uint64)
        self.edges[:]=records
        self.edges.flush()  # HP0 is not CPU-cache coherent.
        self.address=int(self.edges.physical_address)
        if self.address<0 or self.address&7 or self.address+3471040>self.HP0_ADDRESS_LIMIT:
            self.edges.freebuffer();raise RuntimeError('Invalid physical edge buffer range')
    def run_once(self,sources,old_x,step_id,old_state_tag,expected_signature,timeout=5.0):
        if self.edges is None:raise RuntimeError('Closed B controller')
        src=np.asarray(sources);x=np.asarray(old_x)
        if src.shape!=(16402,) or x.shape!=(5768,):raise ValueError('Complete source and old-x states required')
        for values in (src,x):
            if not np.issubdtype(values.dtype,np.signedinteger) or np.any(values<-(1<<30)) or np.any(values>=(1<<30)):
                raise ValueError('Signed31 integer state required; no truncation or saturation')
        if self.mmio.read(0x1c)&9:raise RuntimeError('B core/DDR reader still busy')
        self.edges.flush()
        for offset,value in ((0x20,step_id),(0x24,old_state_tag),(0x28,self.address),(0x2c,expected_signature&0xffffffff),(0x30,expected_signature>>32)):
            self.mmio.write(offset,int(value)&0xffffffff)
        self.mmio.write(0x18,1)
        for index,value in enumerate(np.concatenate((src,x))):
            self.mmio.write(0x1000+4*index,int(value)&0xffffffff)
        if self.mmio.read(0x64)!=22170:raise RuntimeError('State loading incomplete')
        starts_before=self.mmio.read(0x68)
        begin=time.perf_counter();self.mmio.write(0x18,2)
        while not self.mmio.read(0x1c)&2:
            if time.perf_counter()-begin>timeout:
                raise TimeoutError('B request not completed; preserve DDR buffer, no candidate/COMMIT')
        flags=self.mmio.read(0x1c)
        errors=[self.mmio.read(offset) for offset in (0x34,0x38,0x3c)]
        signature=self.mmio.read(0x48)|(self.mmio.read(0x4c)<<32)
        if not flags&4 or any(errors) or self.mmio.read(0x44)!=433880 or signature!=expected_signature:
            raise RuntimeError(f'B failed request: flags={flags:x}, errors={errors}; no candidate/COMMIT')
        if self.mmio.read(0x50)!=(step_id&0xffffffff) or self.mmio.read(0x54)!=(old_state_tag&0xffffffff):
            raise RuntimeError('Request/result identity mismatch')
        if self.mmio.read(0x68)!=(starts_before+1)&0xffffffff:raise RuntimeError('START count mismatch')
        output=np.empty(5768,dtype=np.int32)
        for index in range(5768):
            value=self.mmio.read(0x18000+4*index)
            output[index]=value if value<2**31 else value-2**32
        return dict(candidate=output,core_cycles=self.mmio.read(0x40),received=self.mmio.read(0x58),
                    reader_stall_cycles=self.mmio.read(0x5c),compute_and_readback_seconds=time.perf_counter()-begin,
                    step_id=step_id,old_state_tag=old_state_tag,signature=signature)
    def close(self):
        if self.edges is not None:
            if self.mmio.read(0x1c)&9:
                raise RuntimeError('Cannot free a DDR buffer while core/reader is busy; retain it')
            self.edges.freebuffer();self.edges=None

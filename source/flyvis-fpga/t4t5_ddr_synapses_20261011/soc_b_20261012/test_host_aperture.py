"""CPU-only constructor boundary tests derived from the delivered HWH aperture."""
from pathlib import Path
import json,sys,types
import numpy as np
from arm_controller import FlyvisB
P=Path(__file__).resolve().parent
class Buffer(np.ndarray):
    def flush(self): self.flushed=True
    def freebuffer(self): self.freed=True
class MMIO:
    def init__(self,*args): pass
    def read(self,offset):
        return {0:0x46564231,4:1,8:5768,12:16402,16:433880,20:645,0x1c:0}[offset]
results=[]
for address,valid in [(0x10000000,True),(0x40000000-3471040,True),
                      (0x40000000-3471040+8,False),(0x10000001,False)]:
    buf=np.zeros(433880,dtype=np.uint64).view(Buffer)
    buf.physical_address=address;buf.freed=False;buf.flushed=False
    sys.modules['pynq']=types.SimpleNamespace(MMIO=MMIO,allocate=lambda **kw:buf)
    try:
        obj=FlyvisB(object(),np.zeros(433880,dtype=np.uint64))
        assert valid and obj.address==address and buf.flushed
        obj.close();assert buf.freed
    except RuntimeError:
        assert not valid and buf.freed
    results.append(dict(address=hex(address),expected_accepted=valid,passed=True))
del sys.modules['pynq']
result=dict(status='PASS_CPU_HWH_APERTURE_BOUNDARIES',case_count=len(results),cases=results,board_IO=0)
(P/'CPU_HOST_APERTURE_TESTS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))

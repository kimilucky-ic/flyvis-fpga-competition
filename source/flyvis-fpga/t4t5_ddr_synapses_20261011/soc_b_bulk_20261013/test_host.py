"""CPU mocks only: cache ordering, bounded ownership, complete state, no board I/O."""
import unittest,json
from pathlib import Path
import numpy as np
from arm_controller import FlyvisBBulk
class Buffer(np.ndarray):
    def __new__(cls,n,address,events,name):
        obj=np.zeros(n,dtype=np.int32).view(cls);obj.physical_address=address;obj.events=events;obj.name=name;obj.freed=False;return obj
    def flush(self):self.events.append(self.name+'_flush')
    def invalidate(self):self.events.append(self.name+'_invalidate')
    def freebuffer(self):self.freed=True
class MMIO:
    def init__(self,events):self.regs={0x1c:0,0x68:0};self.events=events;self.writes=[];self.reads=[];self.error=0;self.hang=False
    def write(self,o,v):
        self.regs[o]=v;self.writes.append((o,v))
        if (o,v)==(0x18,2):
            self.events.append('START');self.regs[0x1c]=9 if self.hang else (2 if self.error else 6);self.regs[0x68]+=1
    def read(self,o):
        self.reads.append(o)
        if o in (0x34,0x38,0x3c,0x88):return 0
        if o==0x8c:return self.error
        if o in (0x48,0x4c):return self.regs[o-0x1c]
        if o in (0x50,0x54):return self.regs[o-0x30]
        return {0x44:433880,0x58:433880,0x64:22170,0x9c:5768}.get(o,self.regs.get(o,0))
def instance():
    c=FlyvisBBulk.__new__(FlyvisBBulk);e=[];c.mmio=MMIO(e)
    c.edges=Buffer(433880,0x10000000,e,'edge');c.inputs=Buffer(22170,0x11000ff8,e,'input');c.outputs=Buffer(5768,0x12000ff8,e,'output')
    c.outputs[1]=-1
    return c,e
src=np.arange(16402,dtype=np.int32)-8000;x=np.arange(5768,dtype=np.int32)-3000
class Tests(unittest.TestCase):
    def run_good(self,c):return c.run_once(src,x,17,0xe1ca6d82,0x52f17c8733341788)
    def test_bulk_exact_cache_order_and_fixed_MMIO(self):
        c,e=instance();r=self.run_good(c)
        np.testing.assert_array_equal(c.inputs,np.concatenate([src,x]));self.assertEqual(r['candidate'][1],-1)
        self.assertEqual(e,['edge_flush','input_flush','output_flush','START','output_invalidate'])
        self.assertEqual(len(c.mmio.writes),9);self.assertTrue(all(o<0xa0 for o in c.mmio.reads));self.assertEqual(c.mmio.writes.count((0x18,2)),1)
    def test_busy_no_writes(self):
        c,e=instance();c.mmio.regs[0x1c]=9
        with self.assertRaises(RuntimeError):self.run_good(c)
        self.assertEqual(c.mmio.writes,[]);self.assertEqual(e,[])
    def test_error_no_candidate_invalidate(self):
        c,e=instance();c.mmio.error=1
        with self.assertRaises(RuntimeError):self.run_good(c)
        self.assertNotIn('output_invalidate',e)
    def test_timeout_retain_all(self):
        c,e=instance();c.mmio.hang=True
        with self.assertRaises(TimeoutError):c.run_once(src,x,0,0,0,timeout=0.001)
        with self.assertRaises(RuntimeError):c.close()
        self.assertTrue(all(not getattr(c,n).freed for n in ('edges','inputs','outputs')))
        c.mmio.regs[0x1c]=2;c.close();self.assertIsNone(c.edges);self.assertIsNone(c.inputs);self.assertIsNone(c.outputs)
    def test_signed31_refused(self):
        c,e=instance();bad=src.astype(np.int64);bad[0]=1<<30
        with self.assertRaises(ValueError):c.run_once(bad,x,0,0,0)
        self.assertEqual(e,[])
    def test_overlap(self):
        c,e=instance();c.inputs.physical_address=c.edges.physical_address
        with self.assertRaises(ValueError):self.run_good(c)
        self.assertEqual(e,[])
    def test_hp0_aperture_alignment(self):
        for address in (-8,0x40000000-8,0x12000004):
            c,e=instance();c.outputs.physical_address=address
            with self.assertRaises(ValueError):self.run_good(c)
    def test_metadata_mismatch_no_invalidate(self):
        c,e=instance();original=c.mmio.read;c.mmio.read=lambda o:42 if o==0x54 else original(o)
        with self.assertRaises(RuntimeError):self.run_good(c)
        self.assertNotIn('output_invalidate',e)
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    Path(__file__).with_name('CPU_HOST_TESTS.json').write_text(json.dumps(dict(status='PASS_CPU_ONLY' if r.wasSuccessful() else 'FAIL',tests=r.testsRun,failures=len(r.failures),errors=len(r.errors),board_IO=0),indent=2))
    raise SystemExit(not r.wasSuccessful())

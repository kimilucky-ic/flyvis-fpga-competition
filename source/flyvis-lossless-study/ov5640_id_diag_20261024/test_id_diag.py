import ast, contextlib, hashlib, io, json, sys, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import id_diag as d
from bounded_io import Iic
P=Path(__file__).resolve().parent
BASELINE=P.parent/'ov5640_release_20261023/bundle'

class Bus:
    def init__(self,mode='ok'):
        self.mode=mode;self.sr=0xc0;self.irq=0;self.w=[];self.reading=False;self.reg=0;self.n=0;self.reads=[];self.now=0
    def read(self,a):
        self.reads.append(a)
        if self.mode=='exception' and a==0x104:raise OSError('injected read exception')
        if self.mode=='late' and self.reading:self.now=1
        if a==0x20:return self.irq
        if a==0x104:return 0xc4 if self.mode=='busy' else self.sr
        if a==0x10c:
            self.sr|=0x40
            return 0 if self.mode=='bad_id' else 0x40 if self.reg==0x300b else 0x56
        return 0
    def write(self,a,v):
        self.w.append((a,v))
        if a==0x20:self.irq^=v
        if a==0x108:
            if v==0x178:self.n=0;self.reg=0
            if not v&0x100 and not self.reading:
                self.reg=(self.reg<<8)|(v&255);self.n+=1
            if v&0x100 and not v&0x200:
                self.sr|=4;self.reading=bool(v&1)
                if self.reading and self.mode in ('stuck','late'):self.sr&=~4
                if self.reading and self.mode=='nack':self.irq|=2
            if v&0x200:
                self.sr=0x80 if self.reading else 0xc0;self.irq|=0x10
                if self.reading:self.irq|=2
    def clock(self):
        if self.mode=='stuck' and self.reading:self.now+=.01
        return self.now

class Tests(unittest.TestCase):
    def test_exact_protocol_and_id(self):
        b=Bus();r=d.read_id(b)
        self.assertEqual(r['status'],'PASS_OPERATOR_REPORTED_OV5640_ID_ONLY')
        self.assertEqual(r['sensor_id'],0x5640)
        ref=Bus();orig=Iic(ref);orig.read16(0x300b);orig.read16(0x300a)
        self.assertEqual(b.w,ref.w)
        self.assertEqual([v for a,v in b.w if a==0x108],[0x178,0x30,0x20b,0x179,0x201,0x178,0x30,0x20a,0x179,0x201])
        self.assertTrue(all(a in (0x20,0x100,0x108,0x120) for a,v in b.w))
    def test_busy_precheck_no_writes(self):
        b=Bus('busy');r=d.read_id(b);self.assertEqual(b.w,[]);self.assertIn('not clean',r['error'])
    def test_nack_stops_no_second_id(self):
        b=Bus('nack');r=d.read_id(b)
        self.assertIn('NACK',r['error']);self.assertEqual(r['sensor_register'],'0x300b')
        self.assertNotIn(0x201,[v for a,v in b.w if a==0x108]);self.assertNotIn(0x10c,b.reads)
    def test_stuck_preserves_wait_stage(self):
        b=Bus('stuck');r=d.read_id(b,clock=b.clock)
        self.assertIn('TimeoutError',r['error']);self.assertEqual(r['failed_stage'],'transaction:49')
        self.assertLessEqual(len(r['trace']['last_calls']),64)
        self.assertIn('0x104',r['trace']['last_reads'])
    def test_late_predicate_distinguished(self):
        b=Bus('late');r=d.read_id(b,clock=b.clock)
        self.assertIn('late MMIO return',r['error']);self.assertEqual(r['failed_stage'],'transaction:49')
    def test_bad_id_is_not_pass(self):
        r=d.read_id(Bus('bad_id'));self.assertIn('mismatch',r['error']);self.assertEqual(r['status'],'STOPPED_ID_DIAGNOSTIC')
    def test_read_exception_no_later_access(self):
        b=Bus('exception');r=d.read_id(b)
        self.assertIn('injected',r['error']);self.assertEqual(b.reads,[0x20,0x100,0x104]);self.assertFalse(b.w)
    def test_no_consuming_fifo_in_snapshot(self):
        b=Bus();d.TraceIO(b).snapshot();self.assertEqual(b.reads,[a for name,a in d.SAFE_REGS]);self.assertNotIn(0x10c,b.reads)
    def test_per_boot_reservation(self):
        base=Path(tempfile.mkdtemp(dir=P,prefix='test_marker_'))
        with self.assertRaises(RuntimeError):d.reserve(base,d.OLD_BOOT,'old')
        d.reserve(base,'fresh','one')
        with self.assertRaises(FileExistsError):d.reserve(base,'fresh','two')
    def test_clock_gate(self):
        good=dict(FPGA0_CLK_CTRL=0x200500,IO_PLL_CTRL=0x1e000,PLL_STATUS=63)
        self.assertAlmostEqual(d.check_clock(good),100,places=5)
        for k,v in [('FPGA0_CLK_CTRL',0),('IO_PLL_CTRL',0x1e010),('PLL_STATUS',0)]:
            with self.assertRaises(RuntimeError):d.check_clock(dict(good,**{k:v}))
    def test_source_unchanged_py38(self):
        self.assertEqual(d.digest(P/'bounded_io.py'),d.digest(BASELINE/'bounded_io.py'))
        for f in ('id_diag.py','bounded_io.py'):ast.parse((P/f).read_text(encoding='utf-8-sig'),feature_version=(3,8))
    def exercise_entry(self,answers,mode='ok',matched=False):
        temp=Path(tempfile.mkdtemp(dir=P,prefix='test_entry_'));(temp/'boot').write_text('new-boot')
        calls=[];bus=Bus(mode)
        reg={0xf8000000:{0x170:0x200500,0x108:0x1e000,0x10c:63,0x240:0},
             0x43c40000:{0x30:45669,0x34:1513231,0x38:0x00110004,0x3c:188416},
             0x41200000:{},0x43000000:{0x34:1}}
        if mode=='abi':reg[0x43c40000][0x30]=1
        class MM:
            def init__(self,base,size):self.base=base;calls.append(('map',base))
            def read(self,a):calls.append(('read',self.base,a));return reg[self.base].get(a,0)
        def mmio(base,size):return bus if base==0x41600000 else MM(base,size)
        class Overlay:
            def init__(self,path,download):calls.append(('overlay',download))
            def download(self):calls.append(('download',))
        fake=SimpleNamespace(__version__='2.7.0',PL=SimpleNamespace(bitfile_name=str(BASELINE/'flyvis_ov5640.bit') if matched else '',timestamp='fresh'),MMIO=mmio,Overlay=Overlay)
        def path(p):
            s=str(p)
            if s=='/proc/sys/kernel/random/boot_id':return temp/'boot'
            if s=='/home/xilinx/jupyter_notebooks/LINE11_OV5640_ID_DIAG':return temp/'output'
            return Path(p)
        ai=iter(answers)
        with patch.object(d,'Path',path),patch.object(d.platform,'machine',return_value='armv7l'),patch.dict(sys.modules,{'pynq':fake}),contextlib.redirect_stdout(io.StringIO()):
            out=d.run(BASELINE,ask=lambda p:next(ai))
        return out,calls,bus
    def test_decline_before_mmio(self):
        out,calls,bus=self.exercise_entry(['取消']);self.assertIsNone(out);self.assertFalse(calls);self.assertFalse(bus.w)
    def test_decline_load_before_mmio(self):
        out,calls,bus=self.exercise_entry(['同意只读型号','取消']);self.assertIsNone(out);self.assertFalse(calls)
    def test_fresh_entry_one_load(self):
        out,calls,bus=self.exercise_entry(['同意只读型号','加载候选并只读型号'])
        self.assertEqual(calls.count(('download',)),1)
        r=json.loads((out/'RESULT.json').read_text());self.assertEqual(r['result']['status'],'PASS_OPERATOR_REPORTED_OV5640_ID_ONLY')
        self.assertTrue(Path(str(out)+'_RESULT.zip').exists())
    def test_matching_entry_no_load(self):
        out,calls,bus=self.exercise_entry(['同意只读型号'],matched=True);self.assertNotIn(('download',),calls)
    def test_bad_abi_stops_before_iic(self):
        out,calls,bus=self.exercise_entry(['同意只读型号','加载候选并只读型号'],mode='abi')
        self.assertFalse(bus.w);self.assertFalse(bus.reads);r=json.loads((out/'RESULT.json').read_text());self.assertEqual(r['result']['phase'],'IDLE_ABI')

if __name__=='__main__':
    stream=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    r=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    (P/'CPU_TEST.log').write_text(stream.getvalue(),encoding='utf-8')
    (P/'CPU_RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_MOCK_ONLY' if r.wasSuccessful() else 'FAIL',tests=r.testsRun,failures=len(r.failures),errors=len(r.errors),board_operations=0,GPU_operations=0,Vivado_operations=0),indent=2),encoding='utf-8')
    print(stream.getvalue());sys.exit(0 if r.wasSuccessful() else 1)

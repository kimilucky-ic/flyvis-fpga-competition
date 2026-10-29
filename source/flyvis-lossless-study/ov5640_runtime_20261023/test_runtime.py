import json,sys,unittest,struct,threading,uuid
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
import numpy as np
from iic_adapter import SensorIic
from capture_binding import CapturePool,BoundSteps
P=Path(__file__).resolve().parent
OUT=P/('cpu_run_'+uuid.uuid4().hex[:8]);OUT.mkdir()
@contextmanager
def retained_case():
    root=OUT/uuid.uuid4().hex[:8];root.mkdir()
    yield root

sys.path.insert(0,str(P.parent/'ov5640_soc_20261023'))
sys.path.insert(0,str(P.parent/'ov5640_prepare_20261023'))
from sensor_init import initialize
from ps_input import PsInput

class Bus:
    def init__(self):self.events=[];self.ptr=0;self.fail=None;self.now=0.
    def send(self,a,b,n,o):
        assert a==0x3c and o==0
        self.events.append(('send',bytes(b)));self.ptr=int.from_bytes(b[:2],'big')
        if self.fail=='exception':raise OSError('NACK')
        if self.fail=='short':return n-1
        if self.fail=='late':self.now+=1
        return n
    def receive(self,a,b,n,o):
        self.events.append(('recv',n));b[0]=0x40 if self.ptr==0x300b else 0x56
        return 0 if self.fail=='receive' else n
    def wait(self):
        self.events.append(('wait',))
        if self.fail=='wait':raise TimeoutError('busy')

class Tests(unittest.TestCase):
    def test_init_through_pynq_api(self):
        b=Bus();a=SensorIic(b);self.assertEqual(initialize(a.read16,a.write16,lambda s:None),248)
        sent=[e[1] for e in b.events if e[0]=='send']
        self.assertEqual(sent[:3],[b'\x30\x0b',b'\x30\x0a',b'\x30\x08\x82'])
        self.assertEqual(len(sent),250)
    def test_iic_failures_latch_without_retry(self):
        for mode in ('short','exception','late','receive','wait'):
            b=Bus();b.fail=mode;a=SensorIic(b,clock=lambda:b.now)
            with self.assertRaises((RuntimeError,OSError,TimeoutError)):a.read16(0x300b)
            count=len(b.events)
            with self.assertRaises(RuntimeError):a.read16(0x300b)
            self.assertEqual(len(b.events),count)
    def test_invalid_iic_no_access(self):
        b=Bus();a=SensorIic(b)
        for reg,val in ((-1,0),(65536,0),(0,256),(0,True)):
            with self.assertRaises(ValueError):a.write16(reg,val)
        self.assertEqual(b.events,[])
    def test_pool_held_survives_producer(self):
        p=CapturePool(8);t=p.grant();source=bytearray(b'12345678');p.complete(t,0,0,source)
        held,frame=p.acquire_latest();source[:]=b'XXXXXXXX'
        def producer():
            for i in range(1,100):
                token=p.grant();self.assertNotEqual(token[0],held[0]);p.complete(token,i,i,bytes([i])*8)
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(producer).result(timeout=5)
        self.assertEqual(frame[2],b'12345678')
        token,latest=p.acquire_latest();self.assertEqual(latest[0],99)
        p.release(held);p.release(token)
    def test_all_held_refuses_capture(self):
        p=CapturePool(1,2)
        for i in range(2):t=p.grant();p.complete(t,i,i,b'x');p.acquire_latest()
        self.assertIsNone(p.grant())
    def test_stale_and_partial_capture_stop(self):
        for stale in (False,True):
            p=CapturePool(2);t=p.grant()
            if stale:t=(t[0],t[1]-1)
            with self.assertRaises(RuntimeError):p.complete(t,0,0,b'x')
            with self.assertRaises(RuntimeError):p.grant()
    def setup_step(self,path,capacity=3):
        return BoundSteps(path,capacity),struct.pack('<721f',*([.5]*721))
    def test_real_mapping_three_steps_and_source_skips(self):
        out=OUT/'evidence_three_steps';s=BoundSteps(out,3);p=CapturePool(480*640*3)
        mapper=PsInput(480,640,'RGB');calls=[]
        def render(raw):return mapper.render(np.frombuffer(raw,np.uint8).reshape(480,640,3)).astype('<f4').tobytes()
        def advance(bits):
            i=len(calls);d=NS(frame_id=i,sequence=i+1);calls.append(bits);return d
        def fetch(d):return NS(frame_id=d.frame_id,input_bits=calls[d.frame_id],state_bits=bytes(45669*4))
        for sid in (0,4,9):
            t=p.grant();p.complete(t,sid,sid*1000000,bytes([sid*20])*(480*640*3));s.process_latest(p,render,advance,fetch)
        self.assertEqual(len(calls),3)
        for i,sid in enumerate((0,4,9)):
            f=out/('%06d'%i);m=json.loads((f/'COMMITTED.json').read_text())
            self.assertEqual(m['source_frame_id'],sid);self.assertEqual((f/'actual_input.bin').read_bytes(),calls[i])
        with self.assertRaises(RuntimeError):s.process_latest(p,render,advance,fetch)
        self.assertEqual(len(calls),3)
    def test_disk_failure_before_step(self):
        with retained_case() as root:
            s,b=self.setup_step(Path(root)/'s');calls=[]
            with patch('capture_binding.save_new',side_effect=OSError('disk full')):
                with self.assertRaises(OSError):s.step((0,0,b'x'),lambda _:b,lambda b:calls.append(b),None)
            self.assertEqual(calls,[]);self.assertTrue(s.failed)
    def test_uncertain_step_keeps_lease_and_input(self):
        with retained_case() as root:
            s,b=self.setup_step(Path(root)/'s');p=CapturePool(1);t=p.grant();p.complete(t,0,0,b'x');calls=[]
            def fail(bits):calls.append(bits);raise TimeoutError('unknown completion')
            with self.assertRaises(TimeoutError):s.process_latest(p,lambda _:b,fail,None)
            self.assertIn('HELD',p.states);self.assertEqual((s.path/'000000/input.bin').read_bytes(),b)
            with self.assertRaises(RuntimeError):s.process_latest(p,lambda _:b,fail,None)
            self.assertEqual(len(calls),1)
    def test_published_corruption_retained(self):
        for error in ('input','state_length','sequence'):
            with retained_case() as root:
                s,b=self.setup_step(Path(root)/'s')
                d=NS(frame_id=0,sequence=2 if error=='sequence' else 1)
                r=NS(frame_id=0,input_bits=(b[:-1]+b'X') if error=='input' else b,state_bits=bytes(4 if error=='state_length' else 45669*4))
                with self.assertRaises(RuntimeError):s.step((0,0,b'x'),lambda _:b,lambda _:d,lambda _:r)
                self.assertTrue(s.failed);self.assertFalse((s.path/'000000/COMMITTED.json').exists())
    def test_disk_failure_after_hardware_preserves_uncertainty(self):
        import capture_binding as cb
        with retained_case() as root:
            s,b=self.setup_step(Path(root)/'s');calls=[];original=cb.save_json
            def fail_commit(path,data):
                if Path(path).name=='COMMITTED.json': raise OSError('disk full after STEP')
                original(path,data)
            d=NS(frame_id=0,sequence=1)
            def advance(bits):calls.append(bits);return d
            r=NS(frame_id=0,input_bits=b,state_bits=bytes(45669*4))
            with patch('capture_binding.save_json',side_effect=fail_commit):
                with self.assertRaises(OSError):s.step((0,0,b'x'),lambda _:b,advance,lambda _:r)
            self.assertEqual(len(calls),1);self.assertTrue(s.failed)
            self.assertEqual(len((s.path/'000000/actual_state.bin').read_bytes()),45669*4)
    def test_invalid_input_before_step(self):
        for bits in (b'',struct.pack('<721f',*([float('nan')]*721))):
            with retained_case() as root:
                s,b=self.setup_step(Path(root)/'s');calls=[]
                with self.assertRaises(ValueError):s.step((0,0,b'x'),lambda _:bits,lambda x:calls.append(x),None)
                self.assertEqual(calls,[])

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    (P/'CPU_RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_MOCK_ONLY' if result.wasSuccessful() else 'FAIL',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),hardware_actions=0,neural_computation_executed=False,evidence_directory=str(OUT),states_in_binding_test='zero-filled fixtures, not neural outputs'),indent=2))
    sys.exit(not result.wasSuccessful())

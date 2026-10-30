"""Focused CPU tests: real saved camera pixels + explicit fake device outputs.
Numerical oracle is used to make fixtures AND check them; this is transport,
input-binding and auditor testing, not independent verification of RTL math.
"""
import ast, hashlib, json, struct, subprocess, sys, unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'software'))
from official_bridge import OfficialBridge,start_official
from audit_bridge import audit
from capture_binding import sha,save_json
from snapshot_records import rolling
from ps_input import PsInput
OUT=ROOT/('evidence/'+(sys.argv[1] if len(sys.argv)>1 else 'cpu_r1'))
OUT.mkdir(exist_ok=False)
raw=(ROOT/'baseline/frame_raw.bin').read_bytes()
assert sha(raw)==json.loads((ROOT/'baseline/RESULT.json').read_text())['raw_sha256']
frame=np.frombuffer(raw,np.uint8).reshape(480,800,3)
frames=[frame,frame[:,::-1,:],np.zeros_like(frame)]
mapper=PsInput(height=480,width=800,channel_order='BGR')
inputs=[mapper.render(x).astype('<f4').tobytes() for x in frames]
(OUT/'oracle_inputs.bin').write_bytes(b''.join(inputs))
cmd=[str((ROOT/'software/reference.exe').resolve()),str((ROOT/'software').resolve()),str((OUT/'oracle_inputs.bin').resolve()),str((OUT/'oracle_states.bin').resolve())]
p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60);(OUT/'oracle.log').write_bytes(p.stdout);p.check_returncode()
save_json(OUT/'ORACLE_COMMAND.json',dict(command=cmd,fixture_source='CPU oracle; no DUT'))
b=(OUT/'oracle_states.bin').read_bytes();gold=[b[i*182676:(i+1)*182676] for i in range(3)]
assert len(b)==3*182676 and gold[0]!=gold[1] and gold[1]!=gold[2]


def record(k,inp,state):
    h=[0]*32
    for i,v in {0:0x5331314c,1:0x10000,2:k,4:45669,5:1513231,6:2884,7:182676,8:12345,9:1513231,10:45669,11:188416,12:rolling(inp),13:rolling(state),14:128,15:4096,16:0x00110003,17:0x3ba3d70a}.items():h[i]=v
    out=bytearray(188416);struct.pack_into('<32I',out,0,*h);out[128:3012]=inp;out[4096:186772]=state
    return bytes(out)

class Frame(np.ndarray):
    def __new__(cls,data):
        x=np.array(data,copy=True).view(cls);x.freed=False;x.fail_free=False;return x
    def freebuffer(self):
        if self.fail_free:raise RuntimeError('fake free failure')
        self.freed=True;self.fill(255) # adversarial immediate DMA reuse

class Video:
    def init__(self):self.frames=[Frame(x) for x in frames];self.reads=0;self.closes=0;self.fail_read=False
    def readframe(self):
        self.reads+=1
        if self.fail_read:raise RuntimeError('fake read failure')
        return self.frames[self.reads-1]
    def close(self):self.closes+=1

class Backend:
    def init__(self,run):self.run=run;self.calls=0;self.fetches=0;self.transform=lambda b:b;self.fail=False;self.wrong_id=False
    def advance(self,inp):
        k=self.calls;d=self.run/'bound'/('%06d'%k)
        assert (d/'PREPARED.json').exists() and (d/'input.bin').read_bytes()==inp
        assert (d/'source_frame.bin').read_bytes()==frames[k].tobytes()
        self.calls+=1
        if self.fail:raise RuntimeError('fake STEP uncertain')
        assert inp==inputs[k]
        return NS(frame_id=k+int(self.wrong_id),sequence=k+1,cycles=12345)
    def copy_record(self,d):
        self.fetches+=1
        return self.transform(record(d.frame_id,inputs[d.frame_id],gold[d.frame_id]))

class Tests(unittest.TestCase):
    def make(self,name=None,capacity=3):
        name=name or self._testMethodName
        v=Video();backend=Backend(OUT/name);s=OfficialBridge(v,backend,backend,OUT/name,capacity)
        return s,v,backend
    def assert_stopped(self,s,v,b):
        old=(v.reads,v.closes,b.calls,b.fetches)
        with self.assertRaises(RuntimeError):s.step()
        with self.assertRaises(RuntimeError):s.close_success()
        self.assertEqual(old,(v.reads,v.closes,b.calls,b.fetches))
    def test_three_steps(self):
        s,v,b=self.make()
        for k in range(3):
            s.step();self.assertTrue(v.frames[k].freed)
        old=(v.reads,b.calls)
        with self.assertRaises(RuntimeError):s.step()
        self.assertEqual(old,(v.reads,b.calls))
        s.close_success();self.assertEqual(v.closes,1)
        result=audit(s.output,OUT/'audit_good');self.assertEqual(result['state_words_compared'],137007)
    def test_read_failure(self):
        s,v,b=self.make();v.fail_read=True
        with self.assertRaises(RuntimeError):s.step()
        self.assertEqual(b.calls,0);self.assert_stopped(s,v,b)
    def test_wrong_geometry(self):
        s,v,b=self.make();v.frames[0]=Frame(np.zeros((480,640,3),np.uint8))
        with self.assertRaises(ValueError):s.step()
        self.assertFalse(v.frames[0].freed);self.assertEqual(b.calls,0);self.assert_stopped(s,v,b)
    def test_free_failure(self):
        s,v,b=self.make();v.frames[0].fail_free=True
        with self.assertRaises(RuntimeError):s.step()
        self.assertIsNotNone(s.held_frame);self.assertEqual(b.calls,0);self.assert_stopped(s,v,b)
    def test_disk_failure_before_step(self):
        s,v,b=self.make()
        with patch('capture_binding.save_new',side_effect=OSError('fake disk full')):
            with self.assertRaises(OSError):s.step()
        self.assertEqual(b.calls,0);self.assert_stopped(s,v,b)
    def test_step_uncertainty(self):
        s,v,b=self.make();b.fail=True
        with self.assertRaises(RuntimeError):s.step()
        self.assertEqual(b.calls,1);self.assertTrue((s.output/'bound/000000/IN_DOUBT.json').exists());self.assert_stopped(s,v,b)
    def test_bad_checksum(self):
        s,v,b=self.make();b.transform=lambda x:x[:4096]+bytes([x[4096]^1])+x[4097:]
        with self.assertRaises(ValueError):s.step()
        self.assert_stopped(s,v,b)
    def test_wrong_input_valid_checksum(self):
        s,v,b=self.make();b.transform=lambda x:record(0,inputs[2],gold[0])
        with self.assertRaises(RuntimeError):s.step()
        self.assert_stopped(s,v,b)
    def test_last_state_corruption_valid_checksum(self):
        s,v,b=self.make();bad=gold[0][:-4]+struct.pack('<I',struct.unpack('<I',gold[0][-4:])[0]^1)
        b.transform=lambda x:record(0,inputs[0],bad)
        s.step() # binding is not a numerical PASS; separate auditor must reject
        with self.assertRaisesRegex(ValueError,'all-state mismatch'):audit(s.output,OUT/'audit_bad_last')
    def test_stale_previous_state_rejected(self):
        s,v,b=self.make()
        s.step()
        b.transform=lambda x:record(1,inputs[1],gold[0])
        s.step()
        with self.assertRaisesRegex(ValueError,'all-state mismatch'):
            audit(s.output,OUT/'audit_stale_state')
    def test_step_identity(self):
        s,v,b=self.make();b.wrong_id=True
        with self.assertRaises(RuntimeError):s.step()
        self.assertEqual(b.fetches,0);self.assert_stopped(s,v,b)
    def test_official_start_calls(self):
        log=[]
        class Sensor:
            def init__(self,*a):log.append(('sensor',a))
            def init(self):log.append(('init',))
            def set_outsize(self,*a):log.append(('size',a))
        v=NS(configure=lambda m:log.append(('configure',m)),start=lambda:log.append(('start',)))
        start_official(NS(ip_dict={'cam_iic':'iic-description'},video=NS(video_in=v)),lambda x:('iic',x),Sensor,lambda *a:a)
        self.assertEqual(log,[('sensor',(0x3c,('iic','iic-description'))),('init',),('size',(800,480,1800,1000)),('configure',(800,480,24)),('start',)])
    def test_sensor_failure_no_video(self):
        class Sensor:
            def init__(self,*a):pass
            def init(self):raise RuntimeError('sensor failure')
        with self.assertRaises(RuntimeError):start_official(NS(ip_dict={'cam_iic':None}),lambda x:None,Sensor,None)
    def test_python38_syntax(self):
        for f in (ROOT/'software').glob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'),feature_version=(3,8))

result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
save_json(OUT/'RESULT.json',dict(status='PASS_CPU_ONLY' if result.wasSuccessful() else 'FAIL',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),
 actual_saved_camera_frame_sha256=sha(raw),input_frames=['operator saved original','CPU horizontally mirrored original','CPU zero image'],
 neural_steps_on_board=0,rtl_simulation=False,vendor_driver_execution=False,numeric_fixture='existing serial strict FP32 CPU oracle; not independent DUT',
 audit_good_state_words=137007 if (OUT/'audit_good/RESULT.json').exists() else None,
 limitation='Vendor transitive video/VDMA/cache source not fully snapshotted; DMA ownership remains hardware dependency'))
sys.exit(0 if result.wasSuccessful() else 1)

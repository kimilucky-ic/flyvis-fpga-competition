import sys,json,struct,subprocess,shutil,unittest,uuid,zipfile
from pathlib import Path
from unittest.mock import patch
import numpy as np
P=Path(__file__).resolve().parent;B=P/'bundle';sys.path.insert(0,str(B))
from offline_check import verify
from capture_binding import CapturePool,save_json,sha
from single_frame import capture_and_step
from camera_memory import CameraDdr
from ddr_memory import OwnedDdr
from ddr_control import DdrControl,STRIDE
from bounded_io import CameraControl,OneFrameVdma
from snapshot_records import rolling
from ps_input import PsInput,rgb565_to_rgb
from board_capture import run,check_conditions,nominal_clock
from verify_run import audit
from cpu_support import Buffer,MMIO,Dma,CameraBus
OUT=P/('cpu_tests_'+uuid.uuid4().hex[:8]);OUT.mkdir()
IDENTITY=verify(B)
frame=rgb565_to_rgb(np.arange(640*480,dtype=np.uint16).reshape(480,640))[:,:,::-1].copy().tobytes()
inputs=PsInput(channel_order='BGR').render(np.frombuffer(frame,dtype=np.uint8).reshape(480,640,3)).astype('<f4').tobytes()
(OUT/'input.bin').write_bytes(inputs)
cmd=[str((B/'reference.exe').resolve()),str(B.resolve()),str((OUT/'input.bin').resolve()),str((OUT/'expected.bin').resolve())]
r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60);(OUT/'oracle.log').write_bytes(r.stdout);r.check_returncode()
save_json(OUT/'ORACLE_COMMAND.json',dict(command=cmd,exit_code=r.returncode))
expected=(OUT/'expected.bin').read_bytes()
raw=bytearray((P.parent/'ddr_release_20261018/bundle_r2/cpu_fixture_ddr.bin').read_bytes()[:STRIDE])
raw[128:128+2884]=inputs;raw[4096:4096+182676]=expected
struct.pack_into('<I',raw,48,rolling(inputs));struct.pack_into('<I',raw,52,rolling(expected));raw=bytes(raw)

def path():return OUT/uuid.uuid4().hex[:10]
def fixture():
    out=path();out.mkdir()
    nb=Buffer(STRIDE);mm=MMIO(nb,raw)
    neural=OwnedDdr(lambda **k:nb,nb.barrier,1);neural.pin_before_configure()
    control=DdrControl(mm);control.restore_initial();control.configure(neural.base,neural.size,1,123)
    cb=Buffer(3*921600,0x03000000);cam=CameraDdr(lambda **k:cb,cb.barrier,[(neural.base,neural.base+neural.size)]);cam.pin()
    cb.ddr[:921600]=frame
    pool=CapturePool(921600);dma=Dma();camera=CameraControl(CameraBus())
    capture=OneFrameVdma(dma,pool,cam.addresses,[(cam.base,cam.base+cam.size)],[(neural.base,neural.base+neural.size)],cam.copy,camera,max_polls=20)
    return out,control,neural,cam,pool,mm,capture

def successful():
    out,control,neural,cam,pool,mm,capture=fixture()
    advance=control.advance
    def checked_advance(data):
        d=out/'bound/000000'
        assert (d/'PREPARED.json').is_file() and (d/'input.bin').read_bytes()==data and (d/'source_frame.bin').read_bytes()==frame
        return advance(data)
    control.advance=checked_advance
    result=capture_and_step(capture,pool,control,neural,out/'bound')
    save_json(out/'RESULT.json',result);save_json(out/'RUN_CONTEXT.json',dict(evidence='CPU_MOCK_ONLY',identity=IDENTITY))
    return out,control,neural,cam,pool,mm,capture

class Tests(unittest.TestCase):
 def test_01_default_no_authorization_no_hardware(self):
    before=set(sys.modules)
    with self.assertRaises(RuntimeError):run('unused',{})
    self.assertNotIn('pynq',set(sys.modules)-before)
    with self.assertRaises(ValueError):run('unused',json.loads((B/'conditions.json').read_text()),authorize_load_and_one_step=True)
 def test_02_clock_and_bypass(self):
    regs=dict(FPGA0_CLK_CTRL=0x200500,IO_PLL_CTRL=0x1e000,PLL_STATUS=4)
    self.assertAlmostEqual(nominal_clock(regs),100,places=5)
    for key,value in [('IO_PLL_CTRL',0x1e008),('IO_PLL_CTRL',0x1e010),('PLL_STATUS',0),('FPGA0_CLK_CTRL',0x200400)]:
      bad=dict(regs);bad[key]=value
      with self.assertRaises(RuntimeError):nominal_clock(bad)
 def test_03_full_capture_binding_and_all_state_audit(self):
    out,c,n,cam,pool,mm,cap=successful();result=audit(out,path())
    self.assertEqual(result['mismatch_words'],0);self.assertEqual(result['evidence'],'CPU_MOCK_ONLY')
    self.assertEqual(c._r(0x14),1);self.assertEqual(pool.states,['FREE']*3)
    self.assertEqual(n.buffer.free_calls+cam.buffer.free_calls,0)
    self.assertIn(('invalidate',0,921600),cam.buffer.events)
    self.assertIn(('invalidate',0,STRIDE),n.buffer.events)
 def test_04_overflow_no_step_no_free(self):
    out,c,n,cam,pool,mm,cap=fixture();old=cap.io.read
    def read(a):
      if cap.io.started:cap.camera.io.fault=1
      return old(a)
    cap.io.read=read
    with self.assertRaises(RuntimeError):capture_and_step(cap,pool,c,n,out/'bound')
    self.assertEqual(c._r(0x14),0);self.assertIn('WRITING',pool.states)
    self.assertEqual(n.buffer.free_calls+cam.buffer.free_calls,0)
 def test_05_stale_neural_cache_retains_evidence(self):
    out,c,n,cam,pool,mm,cap=fixture();n.buffer.skip_invalidate=True
    with self.assertRaises(ValueError):capture_and_step(cap,pool,c,n,out/'bound')
    self.assertEqual(c._r(0x14),1);self.assertIn('HELD',pool.states)
    self.assertTrue((out/'bound/000000/record.bin').is_file())
    self.assertTrue((out/'bound/000000/IN_DOUBT.json').is_file())
 def test_06_disk_failure_before_step(self):
    out,c,n,cam,pool,mm,cap=fixture()
    with patch('capture_binding.save_new',side_effect=OSError('disk full')):
      with self.assertRaises(OSError):capture_and_step(cap,pool,c,n,out/'bound')
    self.assertEqual(c._r(0x14),0);self.assertIn('HELD',pool.states)
 def test_07_last_neuron_corruption_even_with_checksums(self):
    out,c,n,cam,pool,mm,cap=successful();d=out/'bound/000000'
    state=bytearray((d/'actual_state.bin').read_bytes());state[-4]^=1;state=bytes(state);(d/'actual_state.bin').write_bytes(state)
    record=bytearray((d/'record.bin').read_bytes());record[4096:4096+len(state)]=state;struct.pack_into('<I',record,52,rolling(state));(d/'record.bin').write_bytes(record)
    receipt=json.loads((d/'COMMITTED.json').read_text());receipt['state_sha256']=sha(state);(d/'COMMITTED.json').write_text(json.dumps(receipt))
    a=path()
    with self.assertRaisesRegex(RuntimeError,'full-state mismatch'):audit(out,a)
    comparison=json.loads((a/'state_compare.json').read_text());self.assertEqual(comparison['mismatch_words'],1);self.assertEqual(comparison['first_mismatches'][0]['global_id'],45668)
 def test_08_actual_input_mismatch(self):
    out,*_=successful();d=out/'bound/000000';v=bytearray((d/'actual_input.bin').read_bytes());v[0]^=1;(d/'actual_input.bin').write_bytes(v)
    with self.assertRaisesRegex(ValueError,'identity'):audit(out,path())
 def test_09_descriptor_cycle_mismatch(self):
    out,c,n,cam,pool,mm,cap=fixture();mm.wrong_cycles=True
    with self.assertRaisesRegex(RuntimeError,'cycle'):capture_and_step(cap,pool,c,n,out/'bound')
    self.assertIn('HELD',pool.states);self.assertTrue((out/'bound/000000/record.bin').is_file())
 def test_10_zip_audit_and_traversal(self):
    out,*_=successful();z=Path(shutil.make_archive(str(path()),'zip',out));result=audit(z,path());self.assertEqual(result['state_words_compared'],45669)
    bad=path().with_suffix('.zip')
    with zipfile.ZipFile(bad,'w') as f:f.writestr('../escape',b'bad')
    with self.assertRaises(ValueError):audit(bad,path())
 def test_11_wrong_hwh_rejected(self):
    d=path();shutil.copytree(B,d);shutil.copyfile(P.parent/'ddr_release_20261018/bundle_r2/flyvis_ddr.hwh',d/'flyvis_ov5640.hwh')
    with self.assertRaises(ValueError):verify(d)
 def test_12_unowned_camera_copy_refused(self):
    out,c,n,cam,pool,mm,cap=fixture()
    with self.assertRaises(ValueError):cam.copy(cam.base+1,921600)
    with self.assertRaises(ValueError):cam.copy(cam.base,1)

 def test_13_previous_session_blocks_reload(self):
    import board_capture
    with patch.dict(board_capture._RETAINED,{'prior':{}},clear=True):
      with self.assertRaisesRegex(RuntimeError,'Prior session'):run('unused',{},authorize_load_and_one_step=True)
 def test_14_camera_ddr_overlap_rejected_before_arm(self):
    buf=Buffer(3*921600,0x02000000)
    with self.assertRaises(ValueError):CameraDdr(lambda **k:buf,lambda:None,[(0x02000000,0x02000000+STRIDE)])
    self.assertEqual(buf.free_calls,1)

if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 result=dict(status='PASS_CPU_MOCK_CAPTURE_BINDING_AND_OFFLINE_ACCEPTANCE' if r.wasSuccessful() else 'FAIL',tests=r.testsRun,failures=len(r.failures),errors=len(r.errors),output=str(OUT),board_operations=0,GPU_operations=0)
 (P/'CPU_RESULT.json').write_text(json.dumps(result,indent=2));sys.exit(not r.wasSuccessful())

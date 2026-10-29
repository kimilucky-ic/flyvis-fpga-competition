"""CPU only: exercise main with injected board APIs, never import PYNQ."""
import json, sys, tempfile, unittest
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import line11_live_camera_board as board

class Admission(unittest.TestCase):
    def exercise(self, failure=None, meminfo='CmaFree: 3832 kB\n', armed=False):
        events=[]; loaded=False
        class Memory:
            def init__(self, allocator, barrier, slots):
                events.append('allocate_validate')
                if not loaded:raise RuntimeError('Overlay is not downloaded')
                if failure=='allocate':raise MemoryError('injected allocation failure')
                self.base=0x100000;self.armed=False;self.released=False
            def release_unarmed(self):events.append('free_unarmed');self.released=True
        def binding(out,**kw):
            out.mkdir();(out/'identity.json').write_text(json.dumps({'library_sha256':'test'}))
            return None,None
        class Overlay:
            def init__(self,*a,**kw):events.append('overlay_create')
            def download(self):
                nonlocal loaded
                events.append('download')
                if failure=='download':raise RuntimeError('injected download failure')
                loaded=True
        def mmio(*a):
            events.append('mmio')
            if failure=='mmio':raise RuntimeError('injected MMIO failure')
            return None
        def run(control,memory,*a):
            memory.armed=armed;events.append('run')
            if failure=='run':raise RuntimeError('injected run failure')
            return {'status':'CPU_MOCK_ONLY'}
        def save(path,data):path.write_text(json.dumps(data))
        original_text=Path.read_text;original_bytes=Path.read_bytes
        def readtext(path,*a,**kw):
            return meminfo if path.as_posix()=='/proc/meminfo' else original_text(path,*a,**kw)
        def readbytes(path,*a,**kw):
            return b'xlnx,zynq-7000' if path.as_posix()=='/proc/device-tree/compatible' else original_bytes(path,*a,**kw)
        modules={'pynq':SimpleNamespace(__version__='2.7.0',Overlay=Overlay,MMIO=mmio),
                 'ddr_memory':SimpleNamespace(OwnedDdr=Memory,pynq_allocator_and_barrier=binding),
                 'ddr_control':SimpleNamespace(DdrControl=lambda x:SimpleNamespace(_r=lambda a:0)),
                 'ddr_acceptance':SimpleNamespace(save_new=save)}
        with nullcontext(tempfile.mkdtemp(dir=Path(__file__).parent)) as tmp,patch.dict(sys.modules,modules),patch.object(board,'ROOT',Path(tmp)),patch.object(board,'verify',return_value={'preparation_id':'test','total_steps':485}),patch.object(board,'PreparationClient',return_value=SimpleNamespace(http=SimpleNamespace(),post=lambda *a:None)),patch.object(board.platform,'machine',return_value='armv7l'),patch.object(board,'exclusive_inventory',return_value={}),patch.object(board,'live_context',return_value={}),patch.object(board,'run_window',side_effect=run),patch.object(Path,'read_text',readtext),patch.object(Path,'read_bytes',readbytes),patch.object(sys,'argv',['test','--execute','--exclusive-board-window']):
            if failure:
                with self.assertRaises(RuntimeError):board.main()
            else:board.main()
            report=json.loads((Path(tmp)/'live_result/MEMORY_ADMISSION.json').read_text())
        return events,report
    def test_low_free_allocates_only_after_load(self):
        e,r=self.exercise(armed=True)
        self.assertLess(e.index('download'),e.index('allocate_validate'));self.assertNotIn('free_unarmed',e)
        self.assertEqual(r['required_bytes'],91381760)
    def test_missing_free_is_diagnostic(self):
        e,r=self.exercise(meminfo='MemAvailable: 837192 kB\n',armed=True)
        self.assertIn('run',e)
    def test_allocation_failure_no_mmio_or_compute(self):
        e,r=self.exercise(failure='allocate')
        self.assertEqual(e,['overlay_create','download','allocate_validate'])
        self.assertTrue(r['overlay_loaded']);self.assertFalse(r['neural_step_started'])
        self.assertEqual(r['failed_phase'],'DDR_ALLOCATION_AND_VALIDATION')
    def test_load_failure_no_allocation_or_mmio(self):
        e,r=self.exercise(failure='download')
        self.assertEqual(e,['overlay_create','download']);self.assertFalse(r['overlay_loaded'])
        self.assertTrue(r['overlay_load_attempted']);self.assertEqual(r['failed_phase'],'OVERLAY_LOAD')
    def test_unarmed_cleanup_on_control_failure(self):
        e,r=self.exercise(failure='mmio');self.assertEqual(e[-1],'free_unarmed');self.assertNotIn('run',e)
    def test_armed_failure_retains_buffer(self):
        e,r=self.exercise(failure='run',armed=True);self.assertNotIn('free_unarmed',e)
if __name__=='__main__':unittest.main(verbosity=2)

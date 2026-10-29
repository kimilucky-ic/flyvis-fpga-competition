"""Meaningful input-mapping/time correctness checks; synthetic fixtures are never camera evidence."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import csv
import tempfile
import unittest
import numpy as np
from camera_pipeline.adapter import resample_hex,render_bgr_frames,official_components
from camera_pipeline.common import ROOT,write_json

class TimelineTests(unittest.TestCase):
    def test_irregular_delivery_and_no_future_zoh(self):
        data=np.array([np.full(721,x) for x in [0,.4,1]],dtype=np.float32)
        times=np.array([100,100.031,100.067])
        stimulus,grid,rows=resample_hex(data,times,dt_s=.005,method='zoh')
        self.assertEqual(stimulus.shape,(1,14,1,721))
        self.assertTrue(all(r['source_left_time_s']<=r['model_time_s'] and not r['uses_future_frame'] for r in rows))
        np.testing.assert_array_equal(stimulus[0,6,0],data[0])
        np.testing.assert_array_equal(stimulus[0,7,0],data[1])
        self.assertLessEqual(grid[-1],times[-1]-times[0])
    def test_interpolation_changes_values(self):
        data=np.stack([np.zeros(721),np.ones(721)]).astype(np.float32)
        zoh,t,_=resample_hex(data,[0,.05],method='zoh')
        linear,_,rows=resample_hex(data,[0,.05],method='linear')
        np.testing.assert_allclose(linear[0,:,0,0],t/.05,atol=1e-7)
        self.assertEqual(float(zoh[0,5,0,0]),0)
        self.assertAlmostEqual(float(linear[0,5,0,0]),.5)
        self.assertTrue(rows[5]['uses_future_frame'])
    def test_invalid_timestamps_rejected(self):
        data=np.zeros((2,721),dtype=np.float32)
        for t in ([0,0],[1,0],[0,np.nan]):
            with self.assertRaises(ValueError):resample_hex(data,t)

class MappingTests(unittest.TestCase):
    def test_original_gray_and_independent_box_mean(self):
        from PIL import Image
        from flyvis.datasets.sintel_utils import sample_lum
        rng=np.random.default_rng(20261010)
        frames=rng.integers(0,256,size=(1,480,640,3),dtype=np.uint8)
        rendered,coordinates,metadata=render_bgr_frames(frames,spatial_policy='native')
        with tempfile.TemporaryDirectory(dir=ROOT/'runtime') as temporary:
            path=Path(temporary)/'rgb.png';Image.fromarray(frames[0,:,:,::-1]).save(path)
            gray=sample_lum(path)
        expected=np.array([gray[c['render_row']-6:c['render_row']+7,c['render_column']-6:c['render_column']+7].mean()
                           for c in coordinates])
        # Conv2d and independent NumPy reductions have different float32 summation orders.
        # Initial 3e-7 failed at 3.5762787e-7; retain log and use explicit 1e-6 oracle tolerance.
        # This is NOT a CPU/GPU neural activity equivalence criterion.
        np.testing.assert_allclose(rendered[0],expected,atol=1e-6,rtol=0)
        torch,flyvis,BoxEye,get_hex_coords,_,_=official_components()
        u,v=get_hex_coords(15)
        golden=ROOT.parent/'artifacts/moving_edge_minimal_cpu_v1/input_hex_coordinates.csv'
        with golden.open(encoding='utf-8') as handle:reference=list(csv.DictReader(handle))
        np.testing.assert_array_equal([int(r['u']) for r in reference],u)
        np.testing.assert_array_equal([int(r['v']) for r in reference],v)
        self.assertEqual((coordinates[360]['u'],coordinates[360]['v']),(0,0))
        self.assertEqual((coordinates[360]['render_row'],coordinates[360]['render_column']),(240,320))
        self.assertEqual(metadata['resize'],'none')
    def test_native_forbids_implicit_resize(self):
        with self.assertRaises(ValueError):render_bgr_frames(np.zeros((2,64,64,3),dtype=np.uint8),spatial_policy='native')
    def test_official_chunk_and_field_transform(self):
        # Static all-white at native resolution must have no border darkening.
        frames=np.full((3,480,640,3),255,dtype=np.uint8)
        native,coords,_=render_bgr_frames(frames,spatial_policy='native',chunk_frames=1)
        self.assertTrue(np.array_equal(native,np.ones((3,721),dtype=np.float32)))
        native2,_,_=render_bgr_frames(frames,spatial_policy='native',chunk_frames=3)
        np.testing.assert_array_equal(native,native2)
        full,full_coords,meta=render_bgr_frames(frames,spatial_policy='full-field')
        self.assertEqual(full.shape,(3,721))
        self.assertTrue(np.isfinite(full).all())
        self.assertLess(full.min(),1) # declared letterbox must affect some receptor boxes
        self.assertEqual(meta['render_hw'],[417,417])

if __name__=='__main__':
    # Import official FlyVis only after CPU preprocessing selection.
    ROOT.joinpath('runtime').mkdir(exist_ok=True)
    official_components()
    suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    write_json(ROOT/'logs/unit_validation.json',{'status':'PASS' if result.wasSuccessful() else 'FAIL',
               'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
               'scope':'synthetic correctness fixtures + comparison to accepted input coordinate order; no neural/camera evidence'})
    raise SystemExit(0 if result.wasSuccessful() else 1)

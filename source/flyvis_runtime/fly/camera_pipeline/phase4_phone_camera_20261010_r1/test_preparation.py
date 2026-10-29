"""Offline contracts and localhost tests. Never call a real camera or GPU."""
from __future__ import annotations
import json
from pathlib import Path
import sys
from contextlib import contextmanager
import uuid
import threading
import unittest
from unittest.mock import patch
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from camera_pipeline.phase4_phone_camera_20261010_r1 import camera_session as camera
from camera_pipeline.phase4_phone_camera_20261010_r1.config import ROOT,DEFAULT,settings_sha,validate_settings
from camera_pipeline.phase4_phone_camera_20261010_r1.geometry import native_geometry,overlay,screen_coverage
from camera_pipeline.phase4_phone_camera_20261010_r1.serve_phone import StimulusServer
from camera_pipeline.phase4_phone_camera_20261010_r1.prepare_capture import freeze
from camera_pipeline.phase4_phone_camera_20261010_r1 import handoff
from camera_pipeline.common import cv2_module
from camera_pipeline.adapter import render_bgr_frames,resample_hex

@contextmanager
def test_folder():
    # Keep new test evidence in the assigned lane. Never delete user or temp-directory files.
    folder=ROOT/'validation'/'unit_fixtures'/uuid.uuid4().hex
    folder.mkdir(parents=True,exist_ok=False)
    yield folder

class PreparationTests(unittest.TestCase):
    def test_no_camera_without_confirmation(self):
        for command in ('preview','record'):
            with patch.object(camera.capture,'open_camera',side_effect=AssertionError('Hardware touched')) as opened:
                with self.assertRaisesRegex(ValueError,'CAMERA_NOT_OPENED'):camera.run(camera.parser().parse_args([command]))
                opened.assert_not_called()

    def test_record_requires_review_and_valid_phone_before_open(self):
        with patch.object(camera.capture,'open_camera',side_effect=AssertionError('Hardware touched')) as opened:
            with self.assertRaisesRegex(ValueError,'CAMERA_NOT_OPENED'):
                camera.run(camera.parser().parse_args(['record','--phone-ready-confirmed']))
            opened.assert_not_called()
        with test_folder() as tmp:
            file=Path(tmp)/'presentation.json';file.write_text(json.dumps({'schema':'flyvis-phone-presentation-session-v1','validation_only':True}))
            args=camera.parser().parse_args(['record','--phone-ready-confirmed','--screen-coverage-confirmed','--phone-session',str(file),
                                           '--screen-corners','100','20','540','20','540','460','100','460'])
            with patch.object(camera.capture,'open_camera',side_effect=AssertionError('Hardware touched')) as opened:
                with self.assertRaisesRegex(ValueError,'validation sessions'):camera.run(args)
                opened.assert_not_called()

    def test_settings_and_hash(self):
        for family in ('edge','dot','flicker','fade','gradient','calibration'):
            spec=validate_settings({'family':family})
            self.assertEqual(len(settings_sha(spec)),64)
        for bad in ({'speed_px_s':0},{'direction_deg':float('nan')},{'family':'unknown'},{'surprise':1},{'active_s':20,'pre_s':5,'post_s':5.1}):
            with self.assertRaises(ValueError):validate_settings(bad)
        self.assertNotEqual(settings_sha(DEFAULT),settings_sha({**DEFAULT,'direction_deg':180}))

    def test_footprints_and_screen_coverage(self):
        centers,mask,meta=native_geometry(640,480)
        self.assertEqual(len(centers),721);self.assertEqual(meta['footprint_bounds_xy_inclusive'],[119,39,521,441])
        self.assertTrue(screen_coverage(mask,[[100,20],[540,20],[540,460],[100,460]])['all_footprints_inside_active_screen'])
        self.assertFalse(screen_coverage(mask,[[200,100],[440,100],[440,380],[200,380]])['all_footprints_inside_active_screen'])
        with self.assertRaises(ValueError):screen_coverage(mask,[[100,20],[540,460],[540,20],[100,460]])
        with self.assertRaises(ValueError):native_geometry(391,391)

    def test_preview_overlay_does_not_change_raw(self):
        centers,mask,meta=native_geometry(640,480);raw=np.full((480,640,3),127,dtype=np.uint8)
        original=raw.copy();view=overlay(raw,cv2_module(),centers,mask)
        self.assertTrue(np.array_equal(raw,original));self.assertFalse(np.array_equal(view,raw))

    def test_official_geometry_and_actual_causal_values(self):
        # Clearly synthetic offline test pixels, not a phone recapture or neural response.
        frames=np.empty((3,480,640,3),dtype=np.uint8);frames[0]=0;frames[1]=255;frames[2]=127
        source,coords,transform=render_bgr_frames(frames,spatial_policy='native')
        centers,_,_=native_geometry(640,480)
        self.assertTrue(np.array_equal(centers,np.array([[r['render_column'],r['render_row']] for r in coords])))
        self.assertFalse(transform['actual_boxeye_internal_resize']);self.assertEqual(source.dtype,np.float32)
        x,t,alignment=resample_hex(source,np.array([0,.037,.083]),dt_s=.005,method='zoh')
        self.assertEqual(x.shape,(1,17,1,721));self.assertLessEqual(t[-1],.083)
        self.assertTrue(np.array_equal(x[0,7,0],source[0]));self.assertTrue(np.array_equal(x[0,8,0],source[1]))
        self.assertTrue(all(not r['uses_future_frame'] for r in alignment))

    def test_exposure_is_unknown_unless_device_verified(self):
        class CV:CAP_PROP_EXPOSURE=1;CAP_PROP_AUTO_EXPOSURE=2
        class Cap:
            def get(self,key):return 0
            def set(self,key,value):return False
        class Fake:cv2=CV();cap=Cap()
        info=camera.property_snapshot(Fake())
        self.assertEqual(info['EXPOSURE']['reported_value'],0);self.assertFalse(info['EXPOSURE']['support_confirmed'])
        args=camera.parser().parse_args(['preview']);self.assertEqual(camera.apply_requests(Fake(),args),[])
        args.exposure_value=-6;self.assertFalse(camera.apply_requests(Fake(),args)[0]['physical_mode_verified'])

    def test_new_input_requires_capture_review(self):
        with self.assertRaisesRegex(ValueError,'Review actual raw replay'):freeze(Path('missing'))

    def test_gui_rejects_backend_from_another_comparison(self):
        with test_folder() as tmp:
            file=tmp/'not_an_actual_run.json'
            file.write_text(json.dumps({'schema':'flyvis-phase4-backend-result-v1','status':'complete',
                                        'mode':'full_gpu','comparison_id':'old_animation','input_id':'old_input'}),encoding='utf-8')
            with patch.object(handoff,'load_input',return_value=({'comparison_id':'new_camera','input_id':'new_input'},None,None,None)):
                with self.assertRaisesRegex(ValueError,'comparison_id mismatch'):handoff.check_backend_identity(tmp,file)

    def test_phone_server_identity_and_atomic_logs(self):
        with test_folder() as tmp:
            server=StimulusServer(('127.0.0.1',0),tmp,validation_only=True)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();url=f'http://127.0.0.1:{server.server_port}'
            def post(path,value,token=None):
                request=Request(url+path,data=json.dumps(value).encode(),headers={'Content-Type':'application/json','X-Stimulus-Token':token or server.token})
                with urlopen(request,timeout=3) as response:return json.load(response)
            try:
                with self.assertRaises(HTTPError):urlopen(url+'/recordings/private.png',timeout=3)
                with self.assertRaises(HTTPError):post('/api/arm',{'settings':DEFAULT},'wrong')
                one=post('/api/arm',{'settings':DEFAULT});two=post('/api/arm',{'settings':DEFAULT})
                self.assertNotEqual(one['session_id'],two['session_id']);sid=one['session_id'];path=Path(tmp)/sid
                post('/api/events',{'session_id':sid,'events':[{'kind':'start','client_performance_ms':1}]})
                before=(path/'events.jsonl').read_bytes()
                with self.assertRaises(HTTPError):post('/api/events',{'session_id':sid,'events':[
                    {'kind':'frame','client_performance_ms':2},{'kind':'invalid','client_performance_ms':3}]})
                self.assertEqual(before,(path/'events.jsonl').read_bytes())
                post('/api/events',{'session_id':sid,'events':[{'kind':'complete','client_performance_ms':4}]})
                spec=json.loads((path/'presentation.json').read_text());self.assertEqual(spec['state'],'complete')
                self.assertTrue(spec['validation_only']);self.assertFalse(spec['camera_capture']);self.assertIsNone(spec['comparison_id'])
                with self.assertRaisesRegex(ValueError,'validation sessions'):camera.read_presentation(path/'presentation.json')
            finally:server.shutdown();server.server_close();thread.join(timeout=3)

if __name__=='__main__':unittest.main(verbosity=2)

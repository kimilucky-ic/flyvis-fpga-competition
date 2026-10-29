"""Assemble observed SOFTWARE preparation evidence; explicitly leave real tests pending."""
from __future__ import annotations
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import numpy as np
from camera_pipeline.common import sha256,cv2_module,utc_now
from camera_pipeline.phase4_phone_camera_20261010_r1.config import ROOT,write_new
from camera_pipeline.phase4_phone_camera_20261010_r1.geometry import native_geometry,overlay
from camera_pipeline.phase4_phone_camera_20261010_r1.validate_delivery import prior_seals,browser_checks

def main():
    unit=ROOT/'validation/unit_tests_final_r2.log';renderer=ROOT/'validation/renderer_tests_final.json'
    unit_text=unit.read_text(encoding='utf-8-sig')
    if 'Ran 10 tests' not in unit_text or '\nOK' not in unit_text:raise ValueError('Final unit tests not passed')
    rendered=json.loads(renderer.read_text(encoding='utf-8-sig'))
    if rendered['status']!='PASS' or rendered['tests']!=23:raise ValueError('Renderer tests not passed')
    browser=browser_checks()
    if {row['family'] for row in browser}!={'edge','dot','flicker','fade','gradient'}:raise ValueError('Current browser flows incomplete')
    earlier=prior_seals();centers,mask,geometry=native_geometry(640,480)
    raw=np.repeat(np.tile(np.arange(640)*255//639,(480,1)).astype(np.uint8)[:,:,None],3,axis=2)
    cv=cv2_module();view=overlay(raw,cv,centers,mask,[[100,20],[540,20],[540,460],[100,460]])
    cv.putText(view,'SYNTHETIC PLACEMENT DIAGRAM - NOT A CAMERA FRAME',(8,468),cv.FONT_HERSHEY_SIMPLEX,.43,(0,0,255),1)
    image=ROOT/'validation/synthetic_sampling_overlay.png'
    if image.exists():raise ValueError('Do not overwrite an earlier preparation diagram')
    if not cv.imwrite(str(image),view):raise ValueError('Diagram save failed')
    write_new(ROOT/'validation/geometry.json',geometry)
    report={'schema':'phase4-phone-camera-preparation-acceptance-v1','created_utc':utc_now(),
            'status':'SOFTWARE_PREPARATION_PASS_REAL_CAPTURE_PENDING','unit_tests':10,'renderer_tests':23,
            'browser_completed_sessions':browser,'browser_viewport_test_wh':[390,844],
            'browser_canvas_rect_observed':{'x':0,'y':227,'width':390,'height':390},
            'browser_exit_button_rect_observed':{'x':8,'y':8,'width':86,'height':42},
            'viewport_emulation_is_not_physical_phone_test':True,
            'evidence':{'official_boxeye_geometry_and_zoh':'actual CPU preprocessing of three synthetic test frames, not new camera input',
                        'phone_player':'actual desktop browser UI runs + renderer VM checks; validation_only sessions',
                        'camera_gates':'mock open_camera confirmed zero calls on rejected requests',
                        'source_overlay':'synthetic instructional image; raw arrays unmodified by preview overlay'},
            'prior_evidence_integrity':earlier,
            'camera_opened_this_round':False,'new_phone_capture':'NOT_RUN_WAIT_USER_PLACEMENT_CONFIRMATION',
            'new_input_freeze_e2e':'NOT_RUN_UNTIL_NEW_REAL_CAPTURE','new_full_gpu':'NOT_RUN','new_python_replacement':'NOT_RUN',
            'new_fpga':'NOT_RUN','board_used':False,'gui_source_modified':False,
            'formal_new_backend_result_e2e':'NOT_RUN; rejection of old comparison_id tested',
            'pending':['physical phone browser/Wi-Fi and brightness check','real exposure/focus/banding and footprint coverage',
                       'new real recording and exact raw timestamps','new full freeze/readback/three-clock verification',
                       'A/B actual matched Full GPU/Python computations and numerical comparison','GUI formal new schema acceptance',
                       'future C live board execution on same new input'],
            'verification_files':{str(p.relative_to(ROOT)):sha256(p) for p in (unit,renderer,image)}}
    write_new(ROOT/'acceptance.json',report)
    print(json.dumps({'status':report['status'],'unit_tests':10,'renderer_tests':23,'browser_sessions':len(browser),
                      'earlier_files_verified':sum(r['files_verified'] for r in earlier['prior_seals']),
                      'protected_golden_files':earlier['protected_golden_files_verified'],'camera_opened':False,'board_used':False},ensure_ascii=False))

if __name__=='__main__':main()

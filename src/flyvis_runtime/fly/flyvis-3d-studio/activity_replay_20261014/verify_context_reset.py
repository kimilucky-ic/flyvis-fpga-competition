"""Finite CPU regression for camera/controller cache synchronization only."""
from types import SimpleNamespace
import base64,json
import numpy as np
from bridge import Bridge,ROOT
from presentation import sha

OUT=ROOT/'evidence/competition_context_reset_r1'
OUT.mkdir(parents=True,exist_ok=True)
b=Bridge(SimpleNamespace(model=ROOT/'model.json',renderer='cpu',profile='light',width=800,height=500,tag=OUT.name))
body=dict(run_id=b.identity['run_id'],activity_sha256=b.identity['activity_sha256'],frame_index=213,
          activity_time_s=b.identity['activity_time_s'][213],profile='light')
receipts=[]
def render(name,**options):
    r=b.render({**body,'request_id':name,**options})
    meta=r['metadata'];receipts.append(meta)
    (OUT/(name+'.png')).write_bytes(base64.b64decode(r['png_base64']))
    return meta
try:
    original=render('initial',type_filter='all')
    moved=render('rotated_zoomed',type_filter='all',camera=dict(rotate=[.35,.2],zoom=1.2))
    assert moved['png_sha256']!=original['png_sha256']
    reset=render('reset',type_filter='all',camera=dict(reset='detail'))
    assert reset['png_sha256']==original['png_sha256']
    assert np.allclose(reset['camera_framing']['bbox_px'],original['camera_framing']['bbox_px'],rtol=0,atol=1e-5)
    render('T5',type_filter='T5')
    all_again=render('all_again',type_filter='all')
    assert all_again['png_sha256']==original['png_sha256']
    for r in receipts:
        assert set(r['camera_framing']['before_default_fit'])=={'bbox_px','width_fraction','height_fraction','cropped_node_count'}
    result=dict(status='PASS',adapter=b.adapter,initial_sha256=original['png_sha256'],reset_sha256=reset['png_sha256'],
                all_again_sha256=all_again['png_sha256'],reset_bbox=reset['camera_framing']['bbox_px'],
                baseline_pixels_restored_after_rotate_zoom=True,baseline_pixels_restored_after_group_roundtrip=True,
                no_recursive_framing_history=True,code_sha256={n:sha(ROOT/n) for n in ['scene.py','bridge.py']},
                no_GPU_work=True,no_neural_inference=True,PL_execution=False)
    (OUT/'acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result))
finally:
    b.scene.v.close()
    b.log(dict(event='closed',verification='bounded_cpu_camera_reset'))

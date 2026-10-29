"""One bounded CPU render: all true skeletons, source-derived ROI and actual framing."""
from pathlib import Path
from types import SimpleNamespace
import base64, hashlib, json, shutil
from bridge import Bridge, ROOT
from presentation import sha

OUT=ROOT/'evidence/competition_context_r1'
OUT.mkdir(parents=True,exist_ok=True)
args=SimpleNamespace(model=ROOT/'model.json',renderer='cpu',profile='light',width=800,height=500,
                     tag=OUT.name)
bridge=Bridge(args)
identity=bridge.identity
body=dict(run_id=identity['run_id'],activity_sha256=identity['activity_sha256'],
          frame_index=213,activity_time_s=identity['activity_time_s'][213],request_id='context-all-213',profile='light')
try:
    response=bridge.render(body)
    meta=response['metadata'];image=base64.b64decode(response['png_base64'])
    (OUT/'all_213_cpu.png').write_bytes(image)
    (OUT/'all_213_receipt.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    frame=meta['camera_framing']
    assert meta['adapter']['adapter_type']=='CPU'
    assert meta['type_filter']=='all' and len(meta['visible_types'])==len(bridge.scene.objects)
    assert all(item['visible'] for item in meta['type_states'])
    assert meta['background_style']=='simplified_mesh' and meta['rois_visible'] is True
    assert meta['background_manifest_sha256']==sha(ROOT/'roi_lod_20261015/manifest.json')
    assert sum(item['rendered_faces'] for item in meta['background_geometry'])==3600
    assert frame['cropped_node_count']==0
    assert abs(max(frame['width_fraction'],frame['height_fraction'])-.86)<1e-5
    x0,y0,x1,y1=frame['bbox_px']
    assert abs((x0+x1)/2-400)<1e-4 and abs((y0+y1)/2-250)<1e-4
    assert hashlib.sha256(image).hexdigest()==meta['png_sha256']
    result=dict(status='PASS',adapter=meta['adapter'],frame_index=213,visible_types=meta['visible_types'],
                background_style=meta['background_style'],rois_visible=True,
                source_faces=sum(i['source_faces'] for i in meta['background_geometry']),rendered_faces=3600,
                background_manifest_sha256=meta['background_manifest_sha256'],camera_framing=frame,
                render_and_png_ms=meta['render_and_png_ms'],png_sha256=meta['png_sha256'],
                original_data_identity=identity,code_sha256={n:sha(ROOT/n) for n in ['scene.py','bridge.py','presentation.py']},
                no_GPU_work=True,no_neural_inference=True,PL_execution=False)
    for name in result['code_sha256']: shutil.copyfile(ROOT/name,OUT/name)
    (OUT/'acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['status','visible_types','source_faces','rendered_faces','camera_framing','render_and_png_ms']}))
finally:
    bridge.scene.v.close()
    bridge.log(dict(event='closed',verification='bounded_cpu_context'))

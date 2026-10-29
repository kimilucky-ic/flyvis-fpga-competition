"""One bounded end-to-end export check, not a screen-FPS or inference benchmark."""
from pathlib import Path
import sys,json,io,hashlib,time,argparse
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT))
from scene import AnatomyScene,configure_renderer,research_guard
from presentation import verified_identity,sha
from fixed_camera_capture import FixedCameraCapture
import numpy as np
from PIL import Image
import psutil

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--renderer',choices=['cpu','gpu'],default='gpu')
    args=parser.parse_args()
    out=HERE/('fixed_'+args.renderer+'_delivery')
    out.mkdir(exist_ok=True)
    if (out/'result.json').exists(): raise RuntimeError('Completed evidence already exists')
    guard=research_guard()
    if args.renderer=='gpu' and (guard['busy'] or guard['markers']):
        (out/'result.json').write_text(json.dumps(dict(status='SKIPPED_RESEARCH_BUSY',guard=guard)),encoding='utf-8')
        return
    identity=verified_identity(ROOT/'model.json')
    process=psutil.Process()
    process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    if args.renderer=='cpu': process.cpu_affinity(process.cpu_affinity()[:4])
    adapter=configure_renderer(args.renderer)
    scene=AnatomyScene(offscreen=True,size=(1280,640),profile='light',max_fps=60)
    try:
        scene.set_frame(213)
        standard=np.asarray(scene.v.screenshot(None,alpha=False)).copy()
        capture=FixedCameraCapture(scene)
        payload,first=capture.capture(213)
        decoded=np.asarray(Image.open(io.BytesIO(payload)).convert('RGBA'))
        assert np.array_equal(decoded,standard)
        (out/'fixed_213.png').write_bytes(payload)
        samples=[]
        for frame in (210,211,212,213,214,215):
            payload,receipt=capture.capture(frame)
            samples.append(receipt)
        count=capture.draws
        duplicate,repeat=capture.capture(215)
        assert duplicate==payload and capture.draws==count and not repeat['draw_performed']
        rejected=False
        saved=scene.v.camera.width
        scene.v.camera.width*=1.01
        try: capture.capture(215)
        except ValueError: rejected=True
        scene.v.camera.width=saved
        assert rejected
        geometry=[]
        for item,n in zip(scene.objects,scene.neurons):
            visuals=scene.v.objects[item['name']]
            geometry.append(dict(type=item['type'],nodes=len(n.nodes),visual_types=[type(v).__name__ for v in visuals],
                                 source_swc_sha256=item['swc_sha256']))
        result=dict(status='COMPLETE',adapter=adapter,identity=identity,geometry=geometry,
                    background_geometry=scene.background_geometry,background_manifest_sha256=scene.background_manifest_sha256,
                    image_width=1280,image_height=640,camera_framing=scene.projection_info(),color_encoding=scene.color_encoding,
                    unchanged_geometry=True,baseline_screenshot_pixels_exact=True,fixed_camera_change_rejected=rejected,
                    samples=samples,median_ms={key:float(np.median([s[key] for s in samples])) for key in
                    ('color_update_ms','draw_and_readback_ms','png_encode_ms','total_capture_ms')},duplicate_receipt=repeat,
                    rss_mib=process.memory_info().rss/1024**2,cpu_affinity=process.cpu_affinity(),actual_draws=capture.draws,
                    png_sha256=sha(out/'fixed_213.png'),helper_sha256=sha(HERE/'fixed_camera_capture.py'),
                    source_code_sha256={n:sha(ROOT/n) for n in ('scene.py','bridge.py','presentation.py')},
                    scope='6 warm actual changed states; fixed-camera capture plus lossless PNG. No HTTP/WebView2 or concurrent inference timing. CPU mode limited to 4 logical processors for functional verification.',
                    owner_boundary='opt-in helper only; frozen bridge, original 485 frame pack and line 2 GUI unchanged',
                    evidence_level='OFFLINE_SOFTWARE_REPLAY',PL_execution=False,neural_compute=False)
        scene.v.close()
        result['renderer_closed']=True
        (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(dict(status='COMPLETE',median_ms=result['median_ms'],duplicate_ms=repeat['total_capture_ms'],
                              pixels_exact=True,renderer_closed=True)),flush=True)
    finally: scene.v.close()

if __name__=='__main__': main()

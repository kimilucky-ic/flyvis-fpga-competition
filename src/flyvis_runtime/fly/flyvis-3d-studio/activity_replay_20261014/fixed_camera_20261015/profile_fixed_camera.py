"""Bounded fixed-camera profiling. Mature NAVis simplification, no morphology engine."""
from pathlib import Path
import sys, io, json, time, hashlib, argparse, os
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT))
from scene import AnatomyScene, configure_renderer, research_guard
from presentation import sha, verified_identity
import numpy as np
from PIL import Image
import png
import navis
import pygfx as gfx
import psutil

def json_write(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

def encode_old(a):
    buf=io.BytesIO()
    png.Writer(a.shape[1],a.shape[0],alpha=True,greyscale=False).write(buf,a.reshape(a.shape[0],-1))
    return buf.getvalue()

def encode_fast(a):
    buf=io.BytesIO()
    Image.fromarray(a).save(buf,format='PNG',compress_level=1,optimize=False)
    return buf.getvalue()

def timed(f):
    start=time.perf_counter()
    value=f()
    return value,1000*(time.perf_counter()-start)

def project(x,camera):
    clip=np.column_stack([x,np.ones(len(x))])@camera.camera_matrix.T
    ndc=clip[:,:3]/clip[:,3,None]
    return np.column_stack([(ndc[:,0]+1)*640,(1-ndc[:,1])*320])

def check_lod(original,reduced,camera):
    source=original.nodes.set_index('node_id')
    result=reduced.nodes.set_index('node_id')
    parents=source.parent_id.to_dict()
    kept=set(int(v) for v in result.index)
    critical=set(int(v) for v in source.index[source.type!='slab'])
    assert critical<=kept
    assert np.array_equal(result[['x','y','z']].to_numpy(),source.loc[result.index,['x','y','z']].to_numpy())
    errors_um=[]
    errors_px=[]
    for node,parent in result.parent_id.items():
        old_parent=int(parents[node]);chain=[]
        while old_parent>=0 and old_parent not in kept:
            chain.append(old_parent)
            old_parent=int(parents[old_parent])
        assert old_parent==parent, 'New connection must follow the original ancestral path'
        if not chain: continue
        xyz=source.loc[[node,parent]+chain,['x','y','z']].to_numpy(dtype=float)
        for points,errors in ((xyz,errors_um),(project(xyz,camera),errors_px)):
            a,b=points[:2];p=points[2:];d=b-a
            t=np.clip(((p-a)@d)/(d@d),0,1) if d@d else np.zeros(len(p))
            errors.extend(np.linalg.norm(p-(a+t[:,None]*d),axis=1).tolist())
    # Suppressing original degree-2 nodes preserves the branch/terminal graph.
    return dict(original_nodes=len(source),derived_nodes=len(result),critical_nodes=len(critical),
                critical_ids_preserved=True,retained_coordinates_exact=True,ancestral_path_topology_preserved=True,
                skipped_node_error_um_max=max(errors_um,default=0),skipped_node_error_px_max=max(errors_px,default=0),
                skipped_node_error_px_p95=float(np.percentile(errors_px,95)) if errors_px else 0,
                measurement='Original omitted nodes to corresponding retained ancestor segment; same fixed orthographic camera',
                scope='display approximation only, not a replacement scientific morphology')

def prepare():
    model=json.loads((ROOT/'model.json').read_text(encoding='utf-8'))
    receipt=json.loads((ROOT/'framepacks/ON60_type_hue_v1_1280x640_cpu/receipts/frame_0213.json').read_text(encoding='utf-8'))
    camera=gfx.OrthographicCamera()
    camera.set_state(receipt['camera_state'])
    camera.set_view_size(1280,640)
    source_image=np.asarray(Image.open(ROOT/'framepacks/ON60_type_hue_v1_1280x640_cpu/frames/frame_0213.png').convert('RGBA'))
    encoding=[]
    for name,function in [('original_pypng',encode_old),('pillow_lossless_level1',encode_fast)]:
        samples=[]
        for _ in range(5):
            data,elapsed=timed(lambda:function(source_image))
            samples.append(elapsed)
        decoded=np.asarray(Image.open(io.BytesIO(data)).convert('RGBA'))
        assert np.array_equal(decoded,source_image)
        encoding.append(dict(encoder=name,ms=samples,median_ms=float(np.median(samples)),bytes=len(data),decoded_pixels_equal=True))
    candidates=[]
    for factor in (2,3):
        rows=[]
        for item in model['objects']:
            assert sha(Path(item['swc']))==item['swc_sha256']
            original=navis.read_swc(item['swc'],units=item['swc_units']).convert_units('um')
            reduced=navis.downsample_neuron(original,downsampling_factor=factor,inplace=False)
            row=check_lod(original,reduced,camera)
            row.update(type=item['type'],body_id=item['body_id'],source_sha256=item['swc_sha256'])
            rows.append(row)
        candidates.append(dict(factor=factor,original_nodes=sum(r['original_nodes'] for r in rows),
                               derived_nodes=sum(r['derived_nodes'] for r in rows),
                               max_screen_error_px=max(r['skipped_node_error_px_max'] for r in rows),objects=rows))
    result=dict(status='PREPARED',source_model_sha256=sha(ROOT/'model.json'),navis_version=navis.__version__,
                fixed_camera=receipt['camera_state'],encoder_comparison=encoding,candidates=candidates,
                proposed_screen_error_limit_px=1.0,dimensions=[1280,640],activity_modified=False,neural_compute=False,PL_execution=False)
    json_write(HERE/'preparation.json',result)
    print(json.dumps(dict(encoding=encoding,candidates=[{k:c[k] for k in ('factor','original_nodes','derived_nodes','max_screen_error_px')} for c in candidates])),flush=True)

def profile(renderer):
    output=HERE/renderer
    output.mkdir(exist_ok=True)
    if (output/'result.json').exists(): raise RuntimeError('Completed evidence exists')
    if renderer=='gpu':
        guard=research_guard()
        if guard['busy'] or guard['markers']:
            json_write(output/'result.json',dict(status='SKIPPED_RESEARCH_BUSY',guard=guard))
            return
    identity=verified_identity(ROOT/'model.json')
    adapter=configure_renderer(renderer)
    prep=json.loads((HERE/'preparation.json').read_text(encoding='utf-8'))
    choices=[c for c in prep['candidates'] if c['max_screen_error_px']<=prep['proposed_screen_error_limit_px']]
    lod=min(choices,key=lambda c:c['derived_nodes']) if choices else None
    scene=AnatomyScene(offscreen=True,size=(1280,640),profile='light',max_fps=60)
    results=[]
    try:
        # Fixed original camera for both variants. No camera gesture or filter change.
        scene.v.camera.set_state(prep['fixed_camera']);scene.sync_camera_controller()
        scene.set_frame(213)
        baseline=np.asarray(scene.v.screenshot(None,alpha=False)).copy()
        direct=np.asarray(scene.v.canvas.draw()).copy()
        direct_equal=bool(np.array_equal(direct,baseline))
        Image.fromarray(baseline).save(output/'original.png')
        variants=['original']+(['lod'] if lod else [])
        for variant in variants:
            if variant=='lod':
                for item,n in zip(scene.objects,scene.neurons):
                    reduced=navis.downsample_neuron(n,downsampling_factor=lod['factor'],inplace=False)
                    scene.v.remove_objects(item['name'])
                    scene.v.add_neurons(reduced,color='#a8e3ff',linewidth=3.5,radius=False,soma=False,center=False,name=item['name'])
                scene.frame=-1
                scene.set_frame(213)
                reduced_image=np.asarray(scene.v.canvas.draw()).copy()
                Image.fromarray(reduced_image).save(output/'lod.png')
            samples=[]
            for frame in (210,211,212,213,214,215):
                _,update=timed(lambda:scene.set_frame(frame))
                image,draw=timed(lambda:np.asarray(scene.v.canvas.draw()).copy())
                _,extra_snapshot=timed(lambda:scene.v.renderer.snapshot())
                png_bytes,encoding=timed(lambda:encode_fast(image))
                assert np.array_equal(np.asarray(Image.open(io.BytesIO(png_bytes)).convert('RGBA')),image)
                samples.append(dict(frame_index=frame,activity_time_s=float(scene.time[frame]),update_ms=update,
                                    draw_and_readback_ms=draw,extra_snapshot_ms=extra_snapshot,
                                    png_encode_ms=encoding,update_draw_png_ms=update+draw+encoding,png_bytes=len(png_bytes)))
            results.append(dict(variant=variant,lod_factor=lod['factor'] if variant=='lod' else None,samples=samples,
                                median={key:float(np.median([s[key] for s in samples])) for key in
                                        ('update_ms','draw_and_readback_ms','extra_snapshot_ms','png_encode_ms','update_draw_png_ms')},
                                rss_mib=psutil.Process().memory_info().rss/1024**2))
        value=dict(status='COMPLETE',identity=identity,adapter=adapter,dimensions=[1280,640],
                   original_draw_pixels_equal_screenshot=direct_equal,selected_lod=lod,results=results,
                   prior_encoder_comparison=prep['encoder_comparison'],background_faces=3600,
                   skeleton_mode='native Octarine lines, radius=False, no neuron surface mesh',
                   fixed_camera=prep['fixed_camera'],source_code_sha256={n:sha(ROOT/n) for n in ('scene.py','bridge.py','presentation.py')},
                   scope='Bounded fixed-camera draw/readback/PNG profile; excludes HTTP, WebView2 publication and concurrent inference',
                   neural_compute=False,PL_execution=False)
        scene.v.close()
        value['renderer_closed']=True
        json_write(output/'result.json',value)
        print(json.dumps(dict(status='COMPLETE',direct_pixels_equal=direct_equal,selected_lod_factor=lod['factor'] if lod else None,
                              results=[dict(variant=r['variant'],median=r['median']) for r in results])),flush=True)
    finally: scene.v.close()

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['prepare','gpu','cpu']);args=ap.parse_args()
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    prepare() if args.mode=='prepare' else profile(args.mode)

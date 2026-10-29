"""Export the user-approved C materials using the unchanged Octarine scene.

Consumer: line 2 GUI. Only local read-only scientific sources and CPU rendering.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import psutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
APPROVED=ROOT/'response_comparison_20261015'
OUT=HERE/'pack_1280x640'
sys.path.insert(0,str(ROOT))
from presentation import verified_identity, sha, describe


def dump(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')


def content_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main():
    if OUT.exists(): raise RuntimeError('Never overwrite an existing delivery')
    process=psutil.Process();process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    process.cpu_affinity(process.cpu_affinity()[:4])
    c=json.loads((APPROVED/'comparison_config.json').read_text(encoding='utf-8'))
    approved_receipt=json.loads((APPROVED/'video/video_receipt.json').read_text(encoding='utf-8'))
    assert sha(APPROVED/'comparison_config.json')==approved_receipt['comparison_config_sha256']
    approved_frames=json.loads((APPROVED/'video/frames.json').read_text(encoding='utf-8'))
    assert sha(APPROVED/'video/frames.json')==approved_receipt['frames_sha256']
    identity=verified_identity(ROOT/'model.json')
    assert identity==c['identity']
    model=json.loads((ROOT/'model.json').read_text(encoding='utf-8'))
    with np.load(ROOT/'replay.npz') as z: a,t=z['activity'],z['time']
    baseline=np.asarray(c['baseline']['values'],dtype=np.float64)
    assert np.array_equal(baseline,a[100:200].mean(0,dtype=np.float64))
    delta=a-baseline
    q=np.clip((np.abs(delta)-c['shared_display_deadband'])/(c['shared_delta_limit']-c['shared_display_deadband']),0,1)
    b=.22+.78*q**.45
    halo=.16*np.clip((q-.2)/.8,0,1)**.6
    assert np.array_equal(b,np.array([r['brightness']['C'] for r in approved_frames]))
    assert np.array_equal(a,np.array([r['raw_values'] for r in approved_frames]))
    assert np.array_equal(delta,np.array([r['signed_delta'] for r in approved_frames]))
    palette=c['palette'];types=[o['type'] for o in model['objects']]
    base=np.array([[int(palette[typ][j:j+2],16)/255 for j in (1,3,5)] for typ in types])
    encoding=dict(mode='fixed_type_hue_baseline_response_brightness_v1',palette=palette,
        approved_comparison_config_sha256=sha(APPROVED/'comparison_config.json'),
        baseline=c['baseline'],intensity_domain=[0.,c['shared_delta_limit']],
        raw_activity_domain=[-c['absolute_limit'],c['absolute_limit']],
        raw_activity_zero=0.,delta_zero=0.,display_deadband=c['shared_display_deadband'],
        gamma=.45,brightness_floor=.22,brightness_max=1.,
        formula='q=clip((abs(type_mean-baseline)-tau)/(D-tau),0,1); b=.22+.78*q^.45; core_sRGB=b*identity_sRGB',
        halo=dict(implementation='existing pygfx LineMaterial sharing original geometry buffers',
            thickness_px=7.,opacity_formula='.16*clip((q-.2)/.8,0,1)^.6',max_opacity=.16),
        meaning='Fixed hue identifies type; brightness encodes magnitude of deviation from a fixed pre-stimulus baseline.',
        sign_location='Per-skeleton signed-delta labels; receipt retains actual signed x and delta; raw zero and baseline remain separate.',
        units='original_model_units',normalization='one shared fixed delta scale and threshold, no per-frame or per-type normalization',
        quantitative_comparison='Different hue perceived luminance differs; use original signed numbers/curves for quantitative comparisons.',
        mapping='Each real SWC represents its type; activity is the FP64 mean of all 721 model nodes of that type, not a biological measurement.')
    encoding['encoding_sha256']=content_sha(encoding)
    OUT.mkdir(parents=True);(OUT/'frames').mkdir();(OUT/'receipts').mkdir()
    def offline(event,parameters):
        if event=='socket.connect': raise RuntimeError('Local-file-only export; no external connection')
    sys.addaudithook(offline)
    from scene import AnatomyScene, configure_renderer
    import pygfx as gfx
    start=time.perf_counter()
    adapter=configure_renderer('cpu')
    s=AnatomyScene(offscreen=True,size=(1280,640),max_fps=30,profile='light')
    s.v.canvas.draw()
    def camera(): return json.loads(json.dumps(s.v.camera.get_state(),default=lambda v:v.tolist()))
    camera_state=camera()
    def geometry():
        return [[id(v.geometry),id(v.geometry.positions),hashlib.sha256(np.ascontiguousarray(v.geometry.positions.data).tobytes()).hexdigest()]
                for o in s.objects for v in s.v.objects[o['name']] if hasattr(v,'geometry')]
    geometry_before=geometry()
    halos=[];anchors=[]
    for i,o in enumerate(s.objects):
        group=[]
        for v in s.v.objects[o['name']]:
            if isinstance(v,gfx.Line):
                h=gfx.Line(v.geometry,gfx.LineMaterial(thickness=7,color=tuple(base[i]),opacity=0,depth_write=False,pick_write=False))
                h.local.matrix=v.local.matrix.copy();h.visible=False;s.v.scene.add(h);group.append(h)
        halos.append(group)
        point=np.r_[s.neuron_points[i].mean(0),1.] @ s.v.camera.camera_matrix.T
        anchors.append(((point[0]/point[3]+1)*640,(1-point[1]/point[3])*320))
    ys={}
    for group in ('T4','T5'):
        for i,y in zip(sorted([i for i,typ in enumerate(types) if typ.startswith(group)],key=lambda i:anchors[i][1]),np.linspace(78,480,4)):
            ys[i]=y
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    bold=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',25)
    small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
    def annotate(im,k):
        d=ImageDraw.Draw(im)
        for i,typ in enumerate(types):
            x=205 if typ.startswith('T4') else 930;y=ys[i]
            rgb=tuple(int(palette[typ][j:j+2],16) for j in (1,3,5));dim=tuple(int(v*.45) for v in rgb)
            ax,ay=anchors[i]
            d.line((x+144 if x==205 else x,y+20,ax,ay),fill=dim,width=1)
            d.ellipse((ax-2,ay-2,ax+2,ay+2),fill=dim)
            d.rounded_rectangle((x,y,x+144,y+68),radius=9,fill='#0b1827',outline=dim)
            d.text((x+11,y+2),typ,font=bold,fill=palette[typ])
            label='+Δ 高于基线' if delta[k,i]>encoding['display_deadband'] else '−Δ 低于基线' if delta[k,i]<-encoding['display_deadband'] else '≈ 基线附近'
            d.text((x+11,y+38),label,font=font,fill='#e5edf7')
        d.text((295,610),'亮度看 |Δ|，±Δ 保留方向 · 固定基线 / 八型共用尺度 · 显示增强',font=small,fill='#a8bfd3')
        return im
    frames=[];timings=[]
    code_paths=[ROOT/'scene.py',ROOT/'presentation.py',APPROVED/'compare.py',Path(__file__)]
    code_sha={str(p):sha(p) for p in code_paths}
    try:
        for k in range(len(t)):
            begin=time.perf_counter();rgb=base*b[k,:,None]
            s.v.set_colors({o['name']:tuple(v) for o,v in zip(s.objects,rgb)})
            for i,group in enumerate(halos):
                for h in group: h.visible=halo[k,i]>0;h.material.opacity=float(halo[k,i])
            middle=time.perf_counter();s.v.canvas.request_draw()
            pixels=np.asarray(s.v.canvas.draw())
            draw_end=time.perf_counter()
            assert camera()==camera_state and all(v.visible for o in s.objects for v in s.v.objects[o['name']])
            name=f'frames/frame_{k:04d}.png';rp=f'receipts/frame_{k:04d}.json'
            annotate(Image.fromarray(pixels[:,:,:3].copy()),k).save(OUT/name,compress_level=1)
            states=[]
            for i,o in enumerate(s.objects):
                states.append(dict(type=o['type'],body_id=o['body_id'],value=float(a[k,i]),activity_signed=float(a[k,i]),
                    polarity='positive' if a[k,i]>0 else 'negative' if a[k,i]<0 else 'zero',
                    baseline=float(baseline[i]),delta_signed=float(delta[k,i]),
                    delta_polarity='positive' if delta[k,i]>0 else 'negative' if delta[k,i]<0 else 'zero',
                    response_label='above_baseline' if delta[k,i]>encoding['display_deadband'] else 'below_baseline' if delta[k,i]<-encoding['display_deadband'] else 'near_baseline',
                    identity_color=palette[o['type']],intensity_abs=float(abs(delta[k,i])),raw_intensity_abs=float(abs(a[k,i])),
                    normalized_intensity=float(q[k,i]),brightness_factor=float(b[k,i]),halo_opacity=float(halo[k,i]),
                    color='#'+''.join(f'{round(v*255):02x}' for v in rgb[i]),visible=True))
            png_sha=sha(OUT/name)
            receipt=dict(schema='line10.frame.v1',request_id=f'approved_C_{k:04d}',service_id='line10.response-c-offline-export',
                run_id=identity['run_id'],activity_sha256=identity['activity_sha256'],activity_time_sha256=identity['activity_time_sha256'],
                mapping_sha256=identity['mapping_sha256'],input_time_sha256=identity['input_time_sha256'],
                frame_index=k,activity_time_s=float(t[k]),input_time_s=identity['input_time_s'][k],
                type_filter='all',visible_types=types,selected_type=types[0],picked_type=None,
                adapter=adapter,renderer='NAVis/Octarine/pygfx',profile='light',rois_visible=s.rois_visible,
                background_style=s.background_style,background_geometry=s.background_geometry,
                background_manifest_sha256=s.background_manifest_sha256,camera_framing=s.projection_info(),camera_state=camera_state,
                color_encoding=encoding,source_code_sha256=code_sha,draw_performed=True,frame_origin='ACTUAL_RENDER_WITH_SIGNED_2D_LABELS',
                image_width=1280,image_height=640,png_sha256=png_sha,scale=s.scale,
                detail=describe(s.objects,a,t,k,0),type_states=states,
                render_and_png_ms=1000*(time.perf_counter()-begin),evidence_level='OFFLINE_SOFTWARE_REPLAY',PL_execution=False)
            dump(OUT/rp,receipt)
            frames.append(dict(frame_index=k,activity_time_s=float(t[k]),png=name,png_sha256=png_sha,receipt=rp,receipt_sha256=sha(OUT/rp)))
            timings.append(dict(step=k,color_ms=(middle-begin)*1000,draw_read_ms=(draw_end-middle)*1000,total_ms=(time.perf_counter()-begin)*1000))
            if k%80==0 or k==len(t)-1: print(json.dumps(dict(stage='export_C',step=k,total=len(t),elapsed_s=time.perf_counter()-start)),flush=True)
        assert geometry()==geometry_before
        for p,h in code_sha.items(): assert sha(p)==h
        for p,h in c['frozen_files'].items(): assert sha(p)==h
        for row in frames:
            assert sha(OUT/row['png'])==row['png_sha256'] and sha(OUT/row['receipt'])==row['receipt_sha256']
        manifest=dict(schema='line10.fixed_camera_framepack.v1',status='COMPLETE',created_utc=datetime.now(timezone.utc).isoformat(),
            run_id=identity['run_id'],activity_sha256=identity['activity_sha256'],activity_time_sha256=identity['activity_time_sha256'],
            input_time_sha256=identity['input_time_sha256'],replay_sha256=identity['replay_sha256'],mapping_sha256=identity['mapping_sha256'],identity=identity,
            color_encoding=encoding,background_manifest_sha256=s.background_manifest_sha256,image_width=1280,image_height=640,frame_count=len(frames),
            profile='light',type_filter='all',background_style=s.background_style,rois_visible=s.rois_visible,
            renderer='NAVis/Octarine/pygfx',adapter=adapter,source_code_sha256=code_sha,producer_sha256=sha(Path(__file__)),
            model_json_sha256=sha(ROOT/'model.json'),model_dt_s=identity['dt_s'],presentation_steps_per_s=485/40,nominal_duration_s=40.,
            exact_40s_mapping=dict(video_fps=30,video_frame_count=1200,formula='source_k=floor(video_frame_index*485/1200)',
                source_for_video_frame=[i*485//1200 for i in range(1200)],repeat_saved_states=True,interpolation=False),
            interpolation='none; each PNG is one exact saved state; GUI owns a single common index',
            camera_state=camera_state,camera_framing=s.projection_info(),frames=frames,
            scientific_control=dict(path=str(ROOT/'framepacks/ON60_type_hue_v1_1280x640_cpu/manifest.json'),
                sha256=c['frozen_files'][str(ROOT/'framepacks/ON60_type_hue_v1_1280x640_cpu/manifest.json')]),
            approval='Human explicitly selected C and requested line 2 final 40-second competition integration in this thread',
            approved_comparison=dict(config_sha256=sha(APPROVED/'comparison_config.json'),video_sha256=approved_receipt['video_sha256'],
                all_485_brightness_and_signed_deltas_exactly_equal=True),
            resources=dict(adapter=adapter,cpu_affinity=process.cpu_affinity(),priority='BELOW_NORMAL',elapsed_s=time.perf_counter()-start,
                timings=timings,neural_compute=False,PL_execution=False),
            geometry_buffers_ids_and_bytes_unchanged=True,neural_compute=False,evidence_level='OFFLINE_SOFTWARE_REPLAY',PL_execution=False,
            admission='Line 2 must explicitly admit this manifest SHA and C encoding SHA, retain A separately, validate all frames against same-run replay.')
        s.v.close();s=None;manifest['renderer_closed']=True
        dump(OUT/'manifest.json',manifest)
        dump(HERE/'delivery.json',dict(status='READY_FOR_LINE2',manifest=str(OUT/'manifest.json'),manifest_sha256=sha(OUT/'manifest.json'),
            color_encoding_sha256=encoding['encoding_sha256'],frame_count=len(frames),elapsed_s=time.perf_counter()-start,
            original_A_and_approved_ABC_unchanged=True,neural_compute=False,PL_execution=False))
        print(json.dumps(json.loads((HERE/'delivery.json').read_text(encoding='utf-8'))),flush=True)
    finally:
        if s is not None:s.v.close()


if __name__=='__main__': main()

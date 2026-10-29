"""Bounded ON60 display experiment. Reuses the frozen NAVis/Octarine scene.

No inference, source mutation, geometry simplification or synthetic activity.
Only material uniforms and explanatory 2-D labels are updated.
"""
from pathlib import Path
import argparse, hashlib, json, sys, time, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import psutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from presentation import verified_identity, fixed_type_palette, sha

FONT = 'C:/Windows/Fonts/msyh.ttc'
BOLD = 'C:/Windows/Fonts/msyhbd.ttc'
BG = '#091320'
FG = '#e5edf7'
MUTED = '#9baec4'
SIZE = (616, 560)
FPS = 40
KEYS = (150, 205, 213, 217, 240, 320, 360, 484)


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')


def prepare():
    model = json.loads((ROOT/'model.json').read_text(encoding='utf-8'))
    identity = verified_identity(ROOT/'model.json')
    with np.load(ROOT/model['activity_file']) as z:
        activity, times = z['activity'].copy(), z['time'].copy()
    run_file = next(Path(s['path']) for s in model['sources'] if Path(s['path']).name == 'run_identity.json')
    input_identity_file = run_file.parent/'input_identity.json'
    input_identity = json.loads(input_identity_file.read_text(encoding='utf-8'))
    condition = next(c for c in input_identity['conditions'] if c['condition_id'] == 'ON60')
    stimulus_file = run_file.parents[2]/'cpu_preparation_r1'/condition['filename']
    assert sha(stimulus_file) == condition['stimulus_sha256']
    assert input_identity['model'] == identity['model']
    stimulus = np.load(stimulus_file)[0, :, 0]
    changed = np.any(stimulus != stimulus[0], axis=1)
    onset = int(np.flatnonzero(changed)[0])
    last_change = int(np.flatnonzero(np.any(np.diff(stimulus, axis=0) != 0, axis=1))[-1]+1)
    assert onset == 200 and np.all(stimulus[:onset] == .5)
    assert np.all(stimulus[last_change:] == stimulus[last_change])
    # Fixed last 0.5 s before input onset; avoid the earlier settling transient.
    start = onset-100
    baseline = activity[start:onset].mean(axis=0, dtype=np.float64)
    delta = activity-baseline
    absolute_limit = float(np.abs(activity).max())
    delta_limit = float(np.abs(delta).max())
    pre_max = float(np.abs(delta[:onset]).max())
    # One shared threshold, chosen above ALL observed pre-onset drift.
    threshold = max(.005, 3*pre_max)
    q = np.clip((np.abs(delta)-threshold)/(delta_limit-threshold), 0, 1)
    brightness = {
        'A': .38+.62*np.clip(np.abs(activity)/absolute_limit, 0, 1),
        'B': .25+.75*np.clip(np.abs(activity)/absolute_limit, 0, 1)**.45,
        'C': .22+.78*q**.45,
    }
    # Optional low-cost halo on the same existing position buffers, never new branches.
    halo_strength = np.clip((q-.20)/.80, 0, 1)**.6
    palette = fixed_type_palette(model['objects'])
    base_colors = np.array([[int(palette[o['type']][j:j+2], 16)/255 for j in (1, 3, 5)] for o in model['objects']])
    stats = []
    for i, o in enumerate(model['objects']):
        peak_pos = onset+int(delta[onset:, i].argmax())
        peak_neg = onset+int(delta[onset:, i].argmin())
        stats.append(dict(type=o['type'], body_id=o['body_id'], model_node_count=o['count'],
            baseline=float(baseline[i]), baseline_std=float(activity[start:onset, i].std()),
            pre_onset_max_deviation=float(np.abs(delta[:onset, i]).max()),
            maximum_delta=float(delta[peak_pos, i]), maximum_delta_step=peak_pos,
            minimum_delta=float(delta[peak_neg, i]), minimum_delta_step=peak_neg,
            last_delta=float(delta[-1, i]),
            brightness={m:dict(pre_mean=float(b[:onset, i].mean()),
                post_min=float(b[onset:, i].min()), post_max=float(b[onset:, i].max()),
                peak_change_from_pre=float(b[onset:, i].max()-b[:onset, i].mean()))
                for m, b in brightness.items()}))
    frozen = [ROOT/'scene.py', ROOT/'presentation.py', ROOT/'model.json', ROOT/'replay.npz',
        ROOT/'live_raw_20261015/service.py', ROOT/'framepacks/ON60_type_hue_v1_1280x640_cpu/manifest.json']
    config = dict(schema='line10.response-comparison.v1', identity=identity,
        source_input_identity_sha256=sha(input_identity_file), source_stimulus_sha256=sha(stimulus_file),
        input_onset_step=onset, last_changing_input_step=last_change,
        held_final_input_is_pre_stimulus_background=bool(np.array_equal(stimulus[-1],stimulus[0])),
        baseline=dict(method='FP64 arithmetic mean per type', step_start_inclusive=start, step_end_exclusive=onset,
            input_time_interval_s=[float(identity['input_time_s'][start]), 0.0],
            activity_time_first_last_s=[float(times[start]),float(times[onset-1])],
            samples=100, values=baseline.tolist(), reason='Last 0.5 s of verified uniform 0.5 input; exclude earlier settling'),
        palette=palette, absolute_limit=absolute_limit, shared_delta_limit=delta_limit,
        shared_display_deadband=threshold, maximum_observed_pre_onset_drift=pre_max,
        mappings=dict(A='b = .38 + .62 * clip(abs(x)/M,0,1)',
            B='b = .25 + .75 * clip(abs(x)/M,0,1)^.45',
            C='q = clip((abs(x-baseline)-tau)/(D-tau),0,1); b = .22 + .78*q^.45',
            halo='optional same-buffer LineMaterial, thickness 7 px, opacity .16*clip((q-.2)/.8,0,1)^.6'),
        sign_display='Actual signed x, signed delta, zero and fixed baseline in plots; +delta/-delta badges beside each skeleton; near baseline means abs(delta)<=tau',
        domains_fixed_over_whole_clip=True, per_type_enhancement_scales=False,
        photometry='Same numerical scale across types; identity hues have unequal perceived luminance. Compare signed numbers/curves for quantitative comparisons.',
        units='original_model_units', base_linewidth_px=3.5, camera='frozen original AnatomyScene detail view',
        scene_size=list(SIZE), output_size=[1920,1080], fps=FPS, saved_states_per_second=FPS,
        duration_s=len(times)/FPS, source_dt_s=identity['dt_s'],
        video_frame_to_saved_step=list(range(len(times))), interpolation=False,
        statistics=stats, frozen_files={str(f):sha(f) for f in frozen},
        source_boundary='Same-type model means on real representative SWCs; not individual biological measurements or propagation.',
        evidence_level='OFFLINE_SOFTWARE_REPLAY_DISPLAY_COMPARISON', neural_compute=False, PL_execution=False)
    dump(HERE/'comparison_config.json', config)
    return model, activity, times, delta, brightness, halo_strength, base_colors, config


class Labels:
    def init__(self, scene, activity, times, delta, config):
        self.scene, self.a, self.t, self.d, self.c = scene, activity, times, delta, config
        self.fonts = {}
        self.colors = [config['palette'][o['type']] for o in scene.objects]
        self.anchors = []
        for points in scene.neuron_points:
            p = np.r_[np.mean(points, axis=0), 1.] @ scene.v.camera.camera_matrix.T
            self.anchors.append(((p[0]/p[3]+1)*SIZE[0]/2,(1-p[1]/p[3])*SIZE[1]/2))
        self.label_y = {}
        for group in ('T4','T5'):
            indices = [i for i,o in enumerate(scene.objects) if o['type'].startswith(group)]
            for i,y in zip(sorted(indices,key=lambda i:self.anchors[i][1]), np.linspace(68,450,len(indices))):
                self.label_y[i] = y
        self.base = self.background()

    def font(self, size, bold=False):
        key = (size,bold)
        if key not in self.fonts: self.fonts[key] = ImageFont.truetype(BOLD if bold else FONT,size)
        return self.fonts[key]

    def text(self, draw, xy, text, size=22, fill=FG, bold=False, **kwargs):
        draw.text(xy,text,font=self.font(size,bold),fill=fill,**kwargs)

    def background(self):
        im = Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
        self.text(d,(26,16),'一个 FlyVis 视觉网络 · 八种真实神经元骨架',35,bold=True)
        self.text(d,(28,65),'同一 ON60 记录 / 同一固定镜头 / 485 步完整回放    色相认类型，亮暗看变化',21,fill=MUTED)
        self.text(d,(1320,65),'曲线：细实线为零，虚线为刺激前基线',19,fill=MUTED)
        titles = [('A','绝对活动 · 线性','越亮 = |原始均值| 越大'),
                  ('B','绝对活动 · Gamma','增强中小绝对值，基线也会变亮'),
                  ('C','基线响应增强','越亮 = |Δ| 越大；正负由 ±Δ 标记')]
        for n,(tag,title,sub) in enumerate(titles):
            x=24+628*n
            d.rounded_rectangle((x,102,x+616,158),radius=10,fill='#14263b')
            self.text(d,(x+12,107),tag,31,bold=True)
            self.text(d,(x+58,108),title,27,bold=True)
            self.text(d,(x+4,734),sub,22,fill=MUTED)
        self.text(d,(28,1014),'C：固定刺激前 0.5 秒均值；八型共用尺度与阈值。±Δ = 高于 / 低于基线，不等同兴奋 / 抑制。',22)
        self.text(d,(28,1046),'真实 SWC 形态 + 721 节点/类型的模型均值；非个体生物测量，非 FPGA 实板结果。亮度是显示增强。',20,fill=MUTED)
        return im

    def panel_labels(self, image, k):
        im=image.copy();d=ImageDraw.Draw(im)
        tau=self.c['shared_display_deadband']
        for i,o in enumerate(self.scene.objects):
            left=o['type'].startswith('T4');x=5 if left else 508;y=self.label_y[i]
            ax,ay=self.anchors[i]
            rgb=tuple(int(self.colors[i][j:j+2],16) for j in (1,3,5))
            dim=tuple(int(c*.45) for c in rgb)
            d.line((x+100 if left else x,y+18,ax,ay),fill=dim,width=1)
            d.ellipse((ax-2,ay-2,ax+2,ay+2),fill=dim)
            d.rounded_rectangle((x,y,x+102,y+62),radius=8,fill='#0b1827',outline=dim)
            self.text(d,(x+8,y+2),o['type'],23,fill=self.colors[i],bold=True)
            badge='+Δ 高于' if self.d[k,i]>tau else '−Δ 低于' if self.d[k,i]<-tau else '≈ 基线'
            self.text(d,(x+8,y+33),badge,16,fill=FG if abs(self.d[k,i])>tau else MUTED)
        return im

    def compose(self, images, k):
        im=self.base.copy();d=ImageDraw.Draw(im)
        for n,image in enumerate(images): im.paste(self.panel_labels(image,k),(24+628*n,166))
        # Exact source input phase, not a staged response narrative.
        onset=self.c['input_onset_step'];held=self.c['last_changing_input_step']
        phase='刺激前 · 灰背景' if k<onset else '运动刺激' if k<=held else '运动后保持末帧 · 响应调整'
        self.text(d,(28,773),phase,23,bold=True)
        self.text(d,(700,773),f'保存步 {k:03d} / 484    模型活动 t = {self.t[k]:+.3f} s',22)
        self.text(d,(1410,773),'回放 40 步/秒 · 模型步长 5 ms',21,fill=MUTED)
        x0,x1,y=28,1892,816
        d.line((x0,y,x1,y),fill='#304154',width=5)
        d.line((x0+(x1-x0)*100/484,y,x0+(x1-x0)*199/484,y),fill='#8c9bae',width=7)
        for step,label in [(onset,'刺激开始'),(held,'保持末帧')]:
            x=x0+(x1-x0)*step/484
            d.line((x,y-7,x,y+7),fill='#d6dfeb',width=2)
            self.text(d,(x+8,y+3),label,12,fill=MUTED)
        px=x0+(x1-x0)*k/484
        d.ellipse((px-6,y-6,px+6,y+6),fill='#ffffff')
        # All types share the same signed raw-value axis; baseline is a separate dashed line.
        for i,o in enumerate(self.scene.objects):
            x=24+i*236;y=841
            d.rounded_rectangle((x,y,x+224,y+158),radius=9,fill='#112033')
            self.text(d,(x+8,y+4),o['type'],22,fill=self.colors[i],bold=True)
            self.text(d,(x+72,y+7),f'x {self.a[k,i]:+.4f}',19)
            self.text(d,(x+8,y+34),f'Δ {self.d[k,i]:+.4f}',19,fill=MUTED)
            plot=(x+18,y+68,x+213,y+145)
            def project(j,value): return plot[0]+(plot[2]-plot[0])*j/484,plot[3]-(value+.16)/.56*(plot[3]-plot[1])
            z=project(0,0)[1];bl=project(0,self.c['baseline']['values'][i])[1]
            d.line((plot[0],z,plot[2],z),fill='#637086',width=1)
            self.text(d,(x+2,z-8),'0',11,fill=MUTED)
            for xx in range(plot[0],plot[2],8): d.line((xx,bl,min(xx+3,plot[2]),bl),fill='#a7b3c4')
            pts=[project(j,v) for j,v in enumerate(self.a[:,i])]
            d.line(pts,fill='#35465b',width=1)
            if k: d.line(pts[:k+1],fill=self.colors[i],width=2)
            cx,cy=pts[k];d.ellipse((cx-3,cy-3,cx+3,cy+3),fill=self.colors[i])
            d.line((cx,plot[1],cx,plot[3]),fill='#65758c',width=1)
        return im


def main():
    args=argparse.ArgumentParser()
    args.add_argument('--preview',action='store_true')
    args.add_argument('--halo',action='store_true')
    args=args.parse_args()
    process=psutil.Process();process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    process.cpu_affinity(process.cpu_affinity()[:4])
    model,a,t,delta,brightness,halos,base,config=prepare()
    # CPU/WARP deliberately avoids the GPU shared by scientific lanes.
    from scene import AnatomyScene, configure_renderer
    adapter=configure_renderer('cpu')
    scene=AnatomyScene(offscreen=True,size=SIZE,max_fps=40,profile='light')
    scene.v.canvas.draw()
    def camera_signature():
        return json.dumps(scene.v.camera.get_state(),sort_keys=True,default=lambda v:v.tolist())
    original_camera=camera_signature()
    original_geometry=[(id(v.geometry),id(v.geometry.positions)) for o in scene.objects for v in scene.v.objects[o['name']] if hasattr(v,'geometry')]
    import pygfx as gfx
    halo_objects=[]
    for i,o in enumerate(scene.objects):
        hs=[]
        for v in scene.v.objects[o['name']]:
            if isinstance(v,gfx.Line):
                h=gfx.Line(v.geometry,gfx.LineMaterial(thickness=7,color=tuple(base[i]),opacity=0,
                    depth_write=False,pick_write=False))
                h.local.matrix=v.local.matrix.copy();h.visible=False
                scene.v.scene.add(h);hs.append(h)
        halo_objects.append(hs)
    labels=Labels(scene,a,t,delta,config)
    timings=[];receipts=[]
    def render(k,mode,halo=False):
        start=time.perf_counter()
        rgb=base*brightness[mode][k,:,None]
        scene.v.set_colors({o['name']:tuple(c) for o,c in zip(scene.objects,rgb)})
        for i,hs in enumerate(halo_objects):
            for h in hs:
                h.visible=halo and mode=='C' and halos[k,i]>0
                h.material.opacity=float(.16*halos[k,i]) if h.visible else 0
        mid=time.perf_counter();scene.v.canvas.request_draw()
        array=np.asarray(scene.v.canvas.draw())
        timings.append(dict(step=k,mode=mode,halo=halo,color_ms=(mid-start)*1000,draw_read_ms=(time.perf_counter()-mid)*1000))
        assert camera_signature()==original_camera
        assert all(v.visible for o in scene.objects for v in scene.v.objects[o['name']])
        return Image.fromarray(array[:,:,:3].copy())
    out=HERE/('preview' if args.preview else 'video')
    out.mkdir(exist_ok=True)
    start=time.perf_counter()
    try:
        if args.preview:
            for k in (150,205,213,217,360,484):
                imgs=[render(k,mode,args.halo) for mode in 'ABC']
                labels.compose(imgs,k).save(out/f'ABC_{k:04d}.png')
            # Small actual-render comparison of optional outline; no full extra film.
            for k in (150,213,217,360):
                off=render(k,'C',False);on=render(k,'C',True)
                paired=Image.new('RGB',(SIZE[0]*2,SIZE[1]+54),BG)
                paired.paste(labels.panel_labels(off,k),(0,54));paired.paste(labels.panel_labels(on,k),(SIZE[0],54))
                d=ImageDraw.Draw(paired);labels.text(d,(20,9),'C · 仅亮度',26);labels.text(d,(SIZE[0]+20,9),'C · 同色轻描边（候选）',26)
                paired.save(out/f'outline_{k:04d}.png')
        else:
            import imageio_ffmpeg
            target=out/'ON60_ABC_真实骨架动态对照_12秒.mp4'
            if target.exists(): raise RuntimeError('Refusing to overwrite video')
            command=[imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-f','rawvideo',
                '-pix_fmt','rgb24','-s','1920x1080','-r',str(FPS),'-i','pipe:0','-an',
                '-c:v','libx264','-threads','2','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
            with (out/'encoding.log').open('w',encoding='utf-8') as log:
                enc=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log)
                try:
                    for k in range(len(t)):
                        imgs=[render(k,mode,args.halo) for mode in 'ABC']
                        im=labels.compose(imgs,k)
                        if k in KEYS: im.save(out/f'ABC_{k:04d}.png')
                        raw=im.tobytes();enc.stdin.write(raw)
                        receipts.append(dict(video_frame=k,source_step=k,activity_time_s=float(t[k]),
                            input_time_s=config['identity']['input_time_s'][k],raw_values=a[k].tolist(),signed_delta=delta[k].tolist(),
                            brightness={mode:brightness[mode][k].tolist() for mode in 'ABC'},
                            unencoded_rgb_sha256=hashlib.sha256(raw).hexdigest()))
                        if k%40==0: print(json.dumps(dict(stage='render',step=k,total=len(t),elapsed_s=time.perf_counter()-start)),flush=True)
                    enc.stdin.close();code=enc.wait(timeout=60)
                    if code: raise RuntimeError('Encoder failed')
                finally:
                    if enc.poll() is None: enc.terminate();enc.wait(timeout=10)
            count,duration=imageio_ffmpeg.count_frames_and_secs(str(target))
            assert count==len(t) and abs(duration-len(t)/FPS)<.04
            dump(out/'frames.json',receipts)
            dump(out/'video_receipt.json',dict(status='COMPLETE',video=target.name,video_sha256=sha(target),
                frames=count,decoded_duration_s=duration,nominal_duration_s=len(t)/FPS,
                fps=FPS,dimensions=[1920,1080],all_source_states_present_once=True,
                comparison_config_sha256=sha(HERE/'comparison_config.json'),frames_sha256=sha(out/'frames.json'),
                halo_selected=args.halo,adapter=adapter,resource_scope='CPU WARP, 4 logical processors, below-normal priority; no GPU inference or board',
                original_geometry_unchanged=original_geometry==[(id(v.geometry),id(v.geometry.positions)) for o in scene.objects for v in scene.v.objects[o['name']] if hasattr(v,'geometry')],
                projection=scene.projection_info(),camera_signature=original_camera,neural_compute=False,PL_execution=False))
        for path,expected in config['frozen_files'].items(): assert sha(path)==expected,path
        dump(out/'render_measurement.json',dict(adapter=adapter,elapsed_s=time.perf_counter()-start,
            cpu_affinity=process.cpu_affinity(),halo_selected=args.halo,geometry_nodes=sum(len(n.nodes) for n in scene.neurons),
            projection=scene.projection_info(),timings=timings,frozen_files_unchanged=True))
        print(json.dumps(dict(status='COMPLETE',output=str(out),elapsed_s=time.perf_counter()-start)),flush=True)
    finally:
        scene.v.close()


if __name__=='__main__': main()

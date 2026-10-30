"""Scientific movie export: Octarine frames + labelled values and activity trace."""
from scene import ROOT, configure_cpu, AnatomyScene
import hashlib, json, time, sys
from datetime import datetime, timezone
import numpy as np
import psutil
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

def main():
    out=ROOT/'FlyVis_真实骨架活动回放_16秒.mp4'
    evidence=ROOT/'evidence'
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    # Limit this export to two available CPU cores; do not contend with lane 7.
    cpus=psutil.Process().cpu_affinity()
    psutil.Process().cpu_affinity(cpus[-2:])
    adapter=configure_cpu()
    s=AnatomyScene(offscreen=True,size=(960,640))
    font='C:/Windows/Fonts/msyh.ttc'
    fonts={size:ImageFont.truetype(font,size) for size in [12,14,16,18,22,28]}
    figure=Figure(figsize=(3.06,1.80),dpi=100,facecolor='#091320')
    canvas=FigureCanvasAgg(figure)
    ax=figure.add_subplot(111,facecolor='#091320')
    figure.subplots_adjust(left=.16,right=.96,bottom=.27,top=.86)
    ax.plot(s.time,s.activity[:,0],color='#67cfdb',linewidth=1.8)
    cursor=ax.axvline(s.time[0],color='#ffe1aa',linewidth=1)
    dot,=ax.plot([],[],'o',color='#ffe1aa',markersize=4)
    ax.set_xlim(s.time[0],s.time[-1]);ax.set_xlabel('Model time (s)',color='#94acc5',fontsize=8)
    ax.set_title('T4a / type mean',color='#d7e6f6',fontsize=10,loc='left')
    ax.tick_params(colors='#94acc5',labelsize=8)
    for spine in ax.spines.values():spine.set_color('#33495d')
    ax.grid(alpha=.1,color='#a0bed5')
    writer=imageio_ffmpeg.write_frames(str(out),(1280,800),fps=30,codec='libx264',quality=8,
                                      pix_fmt_in='rgb24',pix_fmt_out='yuv420p',macro_block_size=16,
                                      ffmpeg_log_level='warning',output_params=['-threads','2','-movflags','+faststart'])
    writer.send(None)
    started=time.perf_counter();render_times=[]
    for f in range(len(s.time)):
        start=time.perf_counter()
        s.set_frame(f)
        viewport=Image.fromarray(s.v.screenshot(None,alpha=False)).convert('RGB')
        im=Image.new('RGB',(1280,800),'#091320')
        im.paste(viewport,(0,90))
        d=ImageDraw.Draw(im)
        d.text((26,15),'真实神经元，看见模型活动',font=fonts[28],fill='#edf6ff')
        d.text((27,55),'Janelia Optic Lobe v1.1  ×  FlyVis ON60   |   NAVis / Octarine',font=fonts[14],fill='#9ab2c8')
        d.text((985,21),f'第 {f+1:03d} / {len(s.time)} 步',font=fonts[22],fill='#e5f2fc')
        d.text((985,55),f't = {s.time[f]:+.3f} s',font=fonts[18],fill='#74d5e2')
        d.line((970,100,970,706),fill='#233b51',width=1)
        d.text((992,100),'同类型模型活动均值',font=fonts[18],fill='#d9eafa')
        for i,o in enumerate(s.objects):
            y=142+i*40
            c=tuple(round(float(x)*255) for x in s.colors[i])
            d.text((992,y),o['type'],font=fonts[16],fill=c)
            d.text((1160,y),f'{s.activity[f,i]:+.4f}',font=fonts[16],fill='#e5eaf2')
            d.rounded_rectangle((1040,y+7,1148,y+14),radius=3,fill='#203647')
            if s.level[i]>.001:d.rounded_rectangle((1040,y+7,1040+108*s.level[i],y+14),radius=3,fill=c)
        cursor.set_xdata([s.time[f]]*2);dot.set_data([s.time[f]],[s.activity[f,0]])
        canvas.draw()
        im.paste(Image.fromarray(np.asarray(canvas.buffer_rgba())).convert('RGB'),(976,467))
        d.text((992,650),'暗蓝 → 青色 → 暖白',font=fonts[16],fill='#bce2ea')
        d.text((992,677),'每型固定范围；亮度不跨类型比较',font=fonts[12],fill='#91aabc')
        d.rounded_rectangle((26,716,1254,722),radius=3,fill='#22384b')
        d.rounded_rectangle((26,716,26+1228*(f+1)/len(s.time),722),radius=3,fill='#63ccdf')
        d.text((26,737),'真实形态 + 类型级活动投影；非个体对应、非生物测量、非 FPGA 实板结果',font=fonts[16],fill='#e8cfa7')
        d.text((26,768),'保存的软件结果 · 原始模型单位 · CPU 逐帧导出 / 30 fps · 模型时间较视频约慢放 6.67 倍',font=fonts[12],fill='#8ea6ba')
        writer.send(np.asarray(im).tobytes())
        if f in [0,213,370]:im.save(evidence/f'video_frame_{f:03d}.png')
        render_times.append(time.perf_counter()-start)
        if f%60==0:print(json.dumps({'frame':f,'total':len(s.time),'seconds':time.perf_counter()-started}),flush=True)
    writer.close();s.v.close()
    # The encoder is CPU libx264. Confirm exact encoded frame count and duration.
    count,duration=imageio_ffmpeg.count_frames_and_secs(str(out))
    record=dict(status='PASS',created_utc=datetime.now(timezone.utc).isoformat(),adapter=adapter,
                video=str(out),sha256=hashlib.file_digest(open(out,'rb'),'sha256').hexdigest(),bytes=out.stat().st_size,
                frames=count,duration_s=duration,fps=30,source_frames=len(s.time),skipped_source_frames=0,
                wall_seconds=time.perf_counter()-started,median_frame_render_s=float(np.median(render_times)),
                cpu_affinity=psutil.Process().cpu_affinity(),rss_bytes=psutil.Process().memory_info().rss,
                camera='fixed, same detail view as interactive program',encoder='CPU libx264, two threads; no NVENC',
                note='Movie is offline exported scientific playback, not measured live UI frame rate. All values come from replay.npz and scene.set_frame also used by player.py.')
    assert count==len(s.time) and 10<=duration<=20
    (evidence/'video_export.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(record,ensure_ascii=False),flush=True)

if __name__=='__main__':main()

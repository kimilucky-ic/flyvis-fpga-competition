"""Deterministic pixel-space candidate videos; no BoxEye or neural inference."""
from __future__ import annotations
import csv
import json
from pathlib import Path
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from camera_pipeline.common import cv2_module, sha256, utc_now, write_json

ROOT = Path(__file__).resolve().parent
FPS, SIZE, FRAMES = 60, 640, 240
CONDITIONS = [
    {'condition_id':'06_off_down','title':'暗边缘向下','family':'edge','polarity':'OFF','direction':'down'},
    {'condition_id':'07_off_up','title':'暗边缘向上','family':'edge','polarity':'OFF','direction':'up'},
    {'condition_id':'08_on_down','title':'亮边缘向下','family':'edge','polarity':'ON','direction':'down'},
    {'condition_id':'09_on_up','title':'亮边缘向上','family':'edge','polarity':'ON','direction':'up'},
    {'condition_id':'10_dark_bar_static','title':'静止黑条','family':'bar','polarity':'OFF-leading / ON-trailing when moving','direction':None},
    {'condition_id':'11_dark_bar_right','title':'黑条向右','family':'bar','polarity':'OFF-leading / ON-trailing','direction':'right'},
    {'condition_id':'12_dark_bar_left','title':'黑条向左','family':'bar','polarity':'OFF-leading / ON-trailing','direction':'left'},
]

def ideal_frame(condition, frame):
    t = frame/FPS
    progress = float(np.clip((t-1)/2,0,1))
    if condition['family'] == 'edge':
        coordinate = -1+642*progress if condition['direction']=='down' else 641-642*progress
        crossed = np.arange(SIZE)<coordinate if condition['direction']=='down' else np.arange(SIZE)>=coordinate
        low, high = (0,255) if condition['polarity']=='OFF' else (255,0)
        image = np.repeat(np.where(crossed,low,high).astype(np.uint8)[:,None],SIZE,axis=1)
    else:
        center = 320. if condition['direction'] is None else 64+512*progress if condition['direction']=='right' else 576-512*progress
        left = int(round(center-32))
        image = np.full((SIZE,SIZE),255,np.uint8); image[:,left:left+64] = 0
        coordinate = left+31.5
    return image, coordinate

def writer(cv2,path):
    out = cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*'mp4v'),FPS,(SIZE,SIZE))
    if not out.isOpened(): raise RuntimeError(f'MP4 writer failed: {path}')
    return out

def inspect(cv2,path,conditions):
    cap = cv2.VideoCapture(str(path))  # filename, never a camera device
    if not cap.isOpened(): raise RuntimeError(f'Cannot decode {path}')
    fps = cap.get(cv2.CAP_PROP_FPS)
    assert fps == FPS and int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) == SIZE and int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) == SIZE
    metrics=[]; samples={}; max_error=0; max_pts_error=0.; count=0; means=[]; position_t=[]; position=[]
    per_condition=[]
    try:
        while True:
            ok, bgr = cap.read()
            if not ok: break
            condition=conditions[count//FRAMES]; k=count%FRAMES
            reference,reference_position=ideal_frame(condition,k)
            gray=np.asarray(Image.fromarray(bgr[:,:,::-1]).convert('L'))
            error=int(np.max(np.abs(gray.astype(np.int16)-reference.astype(np.int16))))
            # This is a predeclared MP4 pixel error bound, not a neural tolerance.
            assert error <= 16,(condition['condition_id'],k,error)
            max_error=max(max_error,error)
            pts=cap.get(cv2.CAP_PROP_POS_MSEC)/1000
            max_pts_error=max(max_pts_error,abs(pts-count/FPS))
            if k==0: means=[]; position_t=[]; position=[]
            mean=float(gray.mean()); means.append(mean)
            projection=gray.mean(axis=1 if condition['family']=='edge' else 0)
            if condition['family']=='edge':
                gradient=np.abs(np.diff(projection))
                if 1<=k/FPS<3 and gradient.max()>100:
                    position_t.append(k/FPS); position.append(float(gradient.argmax()+.5))
            else:
                dark=np.flatnonzero(projection<127.5)
                assert len(dark)==64,(condition['condition_id'],k,len(dark))
                measured=float(dark.mean())
                assert measured==reference_position
                if 1<=k/FPS<3:
                    position_t.append(k/FPS); position.append(measured)
            metrics.append({'condition_id':condition['condition_id'],'frame':k,'source_time_s':k/FPS,
                            'ideal_position_px':reference_position,'decoded_mean_gray':mean,'max_pixel_error':error})
            if k in (90,150): samples[(condition['condition_id'],k)]=Image.fromarray(gray)
            if k==FRAMES-1:
                record={'condition_id':condition['condition_id'],'decoded_frames':FRAMES,'decoded_fps':fps,'decoded_mean_gray_min':min(means),
                        'decoded_mean_gray_max':max(means),'decoded_mean_gray_std':float(np.std(means))}
                if condition['direction'] is not None:
                    slope=float(np.polyfit(position_t,position,1)[0]); correlation=float(np.corrcoef(position_t,position)[0,1])
                    sign=1 if condition['direction'] in ('right','down') else -1
                    assert slope*sign>0 and correlation*sign>.999
                    record.update(measured_direction_slope_px_s=slope,position_time_correlation=correlation,visible_motion_frames=len(position))
                if condition['family']=='edge':
                    change=means[-1]-means[0]
                    assert change < -240 if condition['polarity']=='OFF' else change > 240
                    record['first_to_last_mean_change']=change
                else:
                    assert max(means)-min(means)<2,'MP4 full-frame luminance unexpectedly varies'
                    record['ideal_full_frame_mean_gray']=229.5
                    record['fixed_dark_area_pixels']=40960
                per_condition.append(record)
            count+=1
        assert count==FRAMES*len(conditions) and max_pts_error<1e-6,(count,max_pts_error)
    finally: cap.release()
    return {'status':'PASS','decoded_frames':count,'fps':fps,'max_pixel_error':max_error,
            'pixel_error_bound_predeclared':16,'decoded_pts_max_error_s':max_pts_error,'conditions':per_condition},metrics,samples

def prior_identity():
    camera=ROOT.parent
    source=camera/'controlled_video_20261010_r1'
    manifest=json.loads((source/'manifest.json').read_text())
    for item in manifest['files']:
        path=source/item['path']; assert path.stat().st_size==item['bytes'] and sha256(path)==item['sha256'],path
    phase3=camera/'phase3_input_20261010_r1'
    protected={name:sha256(source/name) for name in ['sources/01_off_right.mp4','input/stimulus.npy','gpu_full_r1/initial_state_full.npy','manifest.json']}
    protected['INPUT_SINGLE_VIDEO_IDENTITY.json']=sha256(phase3/'INPUT_SINGLE_VIDEO_IDENTITY.json')
    return {'historical_sealed_files_checked':len(manifest['files']),'identities':protected}

def preview(samples):
    font_path=Path('C:/Windows/Fonts/msyh.ttc')
    font=ImageFont.truetype(str(font_path),21)
    small=ImageFont.truetype(str(font_path),16)
    sheet=Image.new('RGB',(960,1000),'#ededed'); draw=ImageDraw.Draw(sheet)
    draw.text((18,8),'新增候选刺激：上下边缘 + 固定面积黑条',fill='black',font=font)
    for i,c in enumerate(CONDITIONS):
        x=15+(i%3)*320; y=52+(i//3)*300
        frame=samples[(c['condition_id'],90 if c['family']=='edge' else 150)].resize((280,240),Image.Resampling.NEAREST)
        sheet.paste(frame,(x,y)); draw.rectangle((x,y,x+280,y+240),outline='#777777')
        draw.text((x,y+243),c['condition_id'],fill='black',font=small)
        draw.text((x,y+265),c['title'],fill='black',font=font)
    draw.text((18,956),'预览经过缩小；正式MP4均为640×640、60FPS、4秒，无文字。',fill='black',font=small)
    sheet.save(ROOT/'conditions_preview.png')
    frames=[]
    for c in CONDITIONS:
        for k in range(0,FRAMES,6):
            gray,_=ideal_frame(c,k)
            frames.append(Image.fromarray(gray).resize((160,160),Image.Resampling.NEAREST))
    frames[0].save(ROOT/'extension_preview.gif',save_all=True,append_images=frames[1:],duration=100,loop=0,optimize=False)

def main():
    start=time.perf_counter(); before=prior_identity()
    clips=ROOT/'clips'; clips.mkdir(exist_ok=False)
    cv2=cv2_module(); all_metrics=[]; all_samples={}; audits=[]
    combined_path=ROOT/'extension_28s.mp4'; combined=writer(cv2,combined_path)
    try:
        for condition in CONDITIONS:
            path=clips/f"{condition['condition_id']}.mp4"; clip=writer(cv2,path)
            try:
                for k in range(FRAMES):
                    gray,_=ideal_frame(condition,k); bgr=np.repeat(gray[:,:,None],3,axis=2)
                    clip.write(bgr); combined.write(bgr)
            finally: clip.release()
            audit,metrics,samples=inspect(cv2,path,[condition]); audits.append(audit)
            all_metrics.extend(metrics); all_samples.update(samples)
            print(json.dumps({'condition':condition['condition_id'],'decode':'PASS','frames':audit['decoded_frames']},ensure_ascii=False),flush=True)
    finally: combined.release()
    combined_audit,_,_=inspect(cv2,combined_path,CONDITIONS)
    with (ROOT/'decoded_frame_checks.csv').open('w',newline='',encoding='utf-8') as file:
        out=csv.DictWriter(file,fieldnames=list(all_metrics[0])); out.writeheader(); out.writerows(all_metrics)
    preview(all_samples)
    after=prior_identity(); assert before==after
    write_json(ROOT/'validation.json',{'status':'PASS','created_utc':utc_now(),'clips':audits,'combined':combined_audit,
        'protected_before_after':before,'existing_P0_inputs_unchanged':True,'elapsed_s':time.perf_counter()-start,
        'new_preprocessing':False,'network_inference':False,'camera_capture':False,'RTL_simulation':False,'FPGA_execution':False})
    write_json(ROOT/'metadata.json',{'schema':'flyvis-candidate-pixel-stimuli-extension-v1','created_utc':utc_now(),
        'evidence_level':'ACTUAL_STIMULUS_GENERATION_AND_ALL_FRAME_DECODE_DIRECTION_CHECKS','condition_count':7,'conditions':CONDITIONS,
        'resolution':[SIZE,SIZE],'fps':FPS,'frames_per_condition':FRAMES,'duration_s_per_condition':4.,'motion_window_s':[1.,3.],
        'combined_duration_s':28.,'codec':'mp4v','gray_levels_ideal':[0,255],'text_in_stimulus':False,
        'edge_formula':'down b=-1+642*p; up b=641-642*p; p=clip((t-1)/2,0,1); rows increase downward',
        'bar_formula':'64px width; right center64->576, left576->64; fixed total dark area40960px; static center320',
        'bar_ideal_full_frame_mean_gray':229.5,'bar_sampled_ROI_mean_is_not_constant':True,
        'bar_semantics':'OFF leading and ON trailing boundaries; not a pure single-polarity edge',
        'new_preprocessed_stimulus_npy':False,'planned_future_input':'native official BoxEye(15,13) + causal ZOH; preprocess once and freeze if selected',
        'model_dt_s_if_selected':.005,'future_model_steps_if_selected':800,
        'not_official_angular_stimuli':True,'network_inference':False,'camera_capture':False,'FPGA_execution':False,
        'P0_scope':'independent candidate library only; existing01_off_right and closed-loop run stay frozen',
        'combined_use':'media preview only; independent neural conditions would each require the agreed common a0 and their own identities',
        'preview_gif':{'resolution':[160,160],'fps':10,'ideal_source_frames':True,'not_canonical_MP4_input':True},
        'versions':{'opencv':cv2.__version__,'numpy':np.__version__},
        'limitations':['MP4 is compressed; future network input must come from a single actual decode, not ideal-frame regeneration',
                       'No neuronal direction/contrast/speed conclusions without actual inference','No camera or display photometric calibration']})
    files=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha256(p)} for p in sorted(ROOT.rglob('*'))
           if p.is_file() and p.name!='manifest.json' and '__pycache__' not in p.parts]
    write_json(ROOT/'manifest.json',{'schema':'flyvis-candidate-animation-seal-v1','files':files,'scope':'new source clips/preview/checks only'})
    print(json.dumps({'status':'PASS','clips':7,'combined_s':28,'files':len(files),'elapsed_s':time.perf_counter()-start}),flush=True)

if __name__=='__main__': main()

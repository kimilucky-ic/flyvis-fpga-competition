"""Original BoxEye rendering and explicit host-timestamp temporal resampling."""
from __future__ import annotations
import csv
import json
import os
import platform
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from .common import ROOT, cv2_module, new_directory, sha256, utc_now, write_json

SOURCE_COMMIT = '92b3845cc426dd309a1a0e1b3890156c42e14021'

@dataclass
class StimulusBundle:
    stimulus: np.ndarray
    time: np.ndarray
    source_hex: np.ndarray
    source_time: np.ndarray
    coordinates: list[dict]
    alignment: list[dict]
    metadata: dict

def official_components():
    # Explicit CPU preprocessing avoids consuming GPU capacity owned by other experiments.
    if 'flyvis' in sys.modules and sys.modules['flyvis'].device.type != 'cpu':
        raise RuntimeError('Run CPU input preprocessing in a separate process from CUDA FlyVis inference.')
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    os.environ['FLYVIS_ROOT_DIR'] = str(ROOT/'runtime'/'flyvis_cpu_data')
    os.environ['MPLCONFIGDIR'] = str(ROOT/'runtime'/'matplotlib')
    os.environ['MPLBACKEND'] = 'Agg'
    import torch
    torch.set_num_threads(1)
    import flyvis
    from flyvis.datasets.rendering import BoxEye
    from flyvis.utils.hex_utils import get_hex_coords, hex_to_pixel
    from torchvision.transforms.functional import resize
    assert flyvis.device.type == 'cpu'
    return torch, flyvis, BoxEye, get_hex_coords, hex_to_pixel, resize

def resample_hex(source_hex, source_time, *, dt_s=0.005, method='zoh'):
    data = np.asarray(source_hex, dtype=np.float32)
    timestamps = np.asarray(source_time, dtype=np.float64)
    if data.ndim!=2 or data.shape[1]!=721 or len(data)!=len(timestamps):
        raise ValueError('Require source_hex [frame,721] and one timestamp per frame')
    if len(timestamps)<2 or not np.isfinite(timestamps).all() or (np.diff(timestamps)<=0).any():
        raise ValueError('Need >=2 finite, strictly increasing source timestamps')
    if not np.isfinite(data).all() or data.min()<0 or data.max()>1:
        raise ValueError('Source receptor intensities must be finite in [0,1]')
    if not 0<dt_s<=0.02: raise ValueError('Use integration dt in (0,0.02]')
    if method not in ('zoh','linear'): raise ValueError('method must be zoh or linear')
    relative = timestamps-timestamps[0]
    grid = np.arange(int(np.floor(relative[-1]/dt_s))+1,dtype=np.float64)*dt_s
    grid = grid[grid<=relative[-1]]  # no extrapolation beyond final measured frame
    left = np.searchsorted(relative,grid,side='right')-1
    right = np.minimum(left+1,len(data)-1)
    alpha = np.zeros_like(grid)
    if method=='linear':
        valid = right!=left
        alpha[valid] = (grid[valid]-relative[left[valid]])/(relative[right[valid]]-relative[left[valid]])
        rendered = ((1-alpha[:,None])*data[left]+alpha[:,None]*data[right]).astype(np.float32)
    else:
        rendered = data[left].copy()
        right = left.copy()
    alignment = [{'model_frame':i,'model_time_s':float(t),'source_left_frame':int(l),
                  'source_right_frame':int(r),'source_left_time_s':float(relative[l]),
                  'source_right_time_s':float(relative[r]),'right_weight':float(a),
                  'uses_future_frame':bool(a>0 and relative[r]>t)}
                 for i,(t,l,r,a) in enumerate(zip(grid,left,right,alpha))]
    return rendered[None,:,None,:], grid, alignment

def load_video_source(source, *, fps_override=None):
    source = Path(source).resolve()
    if source.is_dir():
        with (source/'recording.json').open(encoding='utf-8') as handle: metadata=json.load(handle)
        for name in ('frames.npy','frame_times.npy'):
            if sha256(source/name)!=metadata['data_sha256'][name]: raise ValueError(f'Recording checksum mismatch: {name}')
        frames = np.load(source/'frames.npy',mmap_mode='r',allow_pickle=False)
        times = np.load(source/'frame_times.npy',allow_pickle=False)
        metadata = {**metadata,'source_path':str(source),'timestamp_source':'measured_host_frame_receipt'}
    else:
        cv2 = cv2_module()
        video = cv2.VideoCapture(str(source))
        if not video.isOpened(): raise ValueError(f'Cannot decode video: {source}')
        fps = fps_override or video.get(cv2.CAP_PROP_FPS)
        if not np.isfinite(fps) or fps<=0:
            video.release();raise ValueError('Video FPS missing; supply fps_override')
        values=[]
        try:
            while True:
                ok,image=video.read()
                if not ok: break
                values.append(image)
        finally: video.release()
        if len(values)<2: raise ValueError('Video must contain at least two decodable frames')
        frames=np.stack(values)
        times=np.arange(len(frames),dtype=float)/fps
        metadata={'source_kind':'external_video','source_path':str(source),'source_sha256':sha256(source),
                  'timestamp_source':'assumed_constant_container_fps','video_nominal_fps':float(fps),
                  'measured_delivery_fps':None,'sensor_exposure_timestamps_available':False}
    if frames.dtype!=np.uint8 or frames.ndim!=4 or frames.shape[-1]!=3 or len(frames)!=len(times):
        raise ValueError('Require uint8 BGR frames [frame,height,width,3] and matching timestamps')
    return frames,times,metadata

def render_bgr_frames(frames, *, spatial_policy, chunk_frames=4):
    torch,flyvis,BoxEye,get_hex_coords,hex_to_pixel,resize = official_components()
    from PIL import Image
    import PIL
    import torchvision
    eye=BoxEye(extent=15,kernel_size=13)
    eye.conv=eye.conv.to('cpu')
    h,w=frames.shape[1:3]
    minimum=eye.min_frame_size.cpu().numpy().astype(int)
    if spatial_policy=='native':
        if h<minimum[0] or w<minimum[1]:
            raise ValueError(f'native policy prohibits implicit resize. Input {h}x{w} is below official minimum {minimum.tolist()}; choose full-field explicitly.')
        target_h,target_w=h,w
        resized_h,resized_w=h,w
        offset_y,offset_x=0,0
    elif spatial_policy=='full-field':
        # Explicit, reversible field transform, then actual official receptor rendering.
        target_h,target_w=417,417
        scale=min(target_h/h,target_w/w)
        resized_h,resized_w=max(1,round(h*scale)),max(1,round(w*scale))
        offset_y,offset_x=(target_h-resized_h)//2,(target_w-resized_w)//2
    else: raise ValueError('spatial_policy must be native or full-field; no implicit field choice')
    output=[]
    start=time.perf_counter()
    with torch.no_grad():
        for lower in range(0,len(frames),chunk_frames):
            # Exact official Sintel sample_lum policy: Pillow RGB->L, float32 /255.
            gray=np.stack([np.asarray(Image.fromarray(np.asarray(f)[:,:,::-1]).convert('L'),dtype=np.float32)/255
                           for f in frames[lower:lower+chunk_frames]])
            movie=torch.from_numpy(gray).unsqueeze(0)
            if spatial_policy=='full-field':
                resized=resize(movie,[resized_h,resized_w],antialias=True)
                movie=torch.full((1,len(gray),target_h,target_w),0.5,dtype=torch.float32)
                movie[:,:,offset_y:offset_y+resized_h,offset_x:offset_x+resized_w]=resized
            output.append(eye(movie,ftype='mean',hex_sample=True).cpu().numpy()[0,:,0])
    source_hex=np.concatenate(output,axis=0).astype(np.float32)
    u,v=get_hex_coords(15)
    x,y=hex_to_pixel(u,v)
    receptor=eye.receptor_centers.cpu().numpy()+np.array([target_h//2,target_w//2])
    coordinates=[]
    for i in range(721):
        ry,rx=receptor[i]
        inside=(offset_y<=ry<offset_y+resized_h and offset_x<=rx<offset_x+resized_w)
        sy=((ry-offset_y+.5)*h/resized_h-.5) if inside else None
        sx=((rx-offset_x+.5)*w/resized_w-.5) if inside else None
        coordinates.append({'hex_pixel':i,'u':int(u[i]),'v':int(v[i]),'plot_x':float(x[i]),'plot_y':float(y[i]),
                            'render_row':int(ry),'render_column':int(rx),'source_center_y':sy,'source_center_x':sx,
                            'center_in_camera_image':bool(inside)})
    transform={'policy':spatial_policy,'input_hw':[h,w],'render_hw':[target_h,target_w],
               'resized_hw':[resized_h,resized_w],'offset_yx':[offset_y,offset_x],
               'letterbox_value':0.5 if spatial_policy=='full-field' else None,
               'resize':'torchvision bilinear antialias=True' if spatial_policy=='full-field' else 'none',
               'boxeye_extent':15,'boxeye_kernel_size':13,'boxeye_filter':'mean',
               'boxeye_min_frame_size':minimum.tolist(),'boxeye_padding':'official constant zero convolution padding',
               'camera_fov_deg':None,'lens_calibration':None,'physical_speed_calibrated':False,
               'gray':'Pillow RGB.convert(L); float32/255, matching official sintel_utils.sample_lum',
               'gamma_linearization':False,'per_frame_contrast_normalization':False,
               'image_orientation':'raw camera row increases downward; no flip/mirror/rotation',
               'mirror_horizontal':False,'mirror_vertical':False,'rotation_degrees':0,'crop':None,
               'actual_boxeye_internal_resize':False,
               'coordinate_order':'official get_hex_coords(15): ascending u, then ascending v',
               'boxeye_center_formula':'row=int(13*(u+v/2))+H//2; column=13*v+W//2; integer cast toward zero',
               'preprocessing_elapsed_s':time.perf_counter()-start,
               'versions':{'python':sys.version,'numpy':np.__version__,'torch':torch.__version__,
                           'torchvision':torchvision.__version__,'Pillow':PIL.__version__,'flyvis':flyvis.__version__},
               'official_eye_source_sha256':sha256(Path(flyvis.__file__).parent/'datasets/rendering/eye.py')}
    return source_hex,coordinates,transform

def video_to_flyvis_stimulus(source, *, spatial_policy, method='zoh', dt_s=0.005, fps_override=None):
    frames,times,recording=load_video_source(source,fps_override=fps_override)
    source_hex,coordinates,transform=render_bgr_frames(frames,spatial_policy=spatial_policy)
    stimulus,grid,alignment=resample_hex(source_hex,times,dt_s=dt_s,method=method)
    metadata={'schema':'flyvis-camera-stimulus-v1','created_utc':utc_now(),'source':recording,
              'source_commit':SOURCE_COMMIT,'target_model':'flow/0000/000','model_weights_modified':False,
              'stimulus_shape':list(stimulus.shape),'stimulus_axes':['sample','frame','channel','hex_pixel'],
              'stimulus_dtype':'float32','spatial_transform':transform,'dt_s':dt_s,'simulation_fps':1/dt_s,
              'temporal_method':method,'causal':method=='zoh','source_frame_count':len(times),
              'source_frame_span_s':float(times[-1]-times[0]),'model_last_input_time_s':float(grid[-1]),
              'time_semantics':'time.npy indexes input grid; standard Euler neural activity is after each update, at time+dt',
              'simulation_compute_fps':None,'neural_inference_executed':False,
              'temporal_note':'resample actual 721 receptor values; linear offline blending does not reconstruct intermediate object motion',
              'evidence_level':'real camera input preprocessing' if recording.get('source_kind')=='real_windows_camera' else 'external video input preprocessing',
              'os':platform.platform()}
    return StimulusBundle(stimulus,grid,source_hex,np.asarray(times)-times[0],coordinates,alignment,metadata)

def save_stimulus(bundle, destination):
    destination=new_directory(destination)
    for name,value in [('stimulus',bundle.stimulus),('time',bundle.time),('source_hex',bundle.source_hex),('source_time',bundle.source_time)]:
        np.save(destination/f'{name}.npy',value,allow_pickle=False)
    for filename,rows in [('input_hex_coordinates.csv',bundle.coordinates),('time_alignment.csv',bundle.alignment)]:
        with (destination/filename).open('w',newline='',encoding='utf-8') as handle:
            writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    raw_timestamp_file=Path(bundle.metadata['source']['source_path'])/'frame_timestamps.csv'
    if raw_timestamp_file.is_file():
        shutil.copyfile(raw_timestamp_file,destination/'source_frame_timestamps.csv')
    metadata={**bundle.metadata,'data_sha256':{p.name:sha256(p) for p in destination.iterdir() if p.is_file()}}
    write_json(destination/'metadata.json',metadata)
    return destination

def load_stimulus(directory):
    directory=Path(directory)
    metadata=json.loads((directory/'metadata.json').read_text(encoding='utf-8'))
    for filename,digest in metadata['data_sha256'].items():
        if sha256(directory/filename)!=digest: raise ValueError(f'Stimulus checksum mismatch: {filename}')
    stimulus=np.load(directory/'stimulus.npy',allow_pickle=False,mmap_mode='r')
    grid=np.load(directory/'time.npy',allow_pickle=False)
    if list(stimulus.shape)!=metadata['stimulus_shape'] or stimulus.shape[2:]!=(1,721): raise ValueError('Stimulus shape mismatch')
    if stimulus.shape[1]!=len(grid) or not np.isfinite(stimulus).all() or stimulus.min()<0 or stimulus.max()>1: raise ValueError('Invalid stimulus')
    if not np.allclose(np.diff(grid),metadata['dt_s'],atol=1e-12,rtol=0): raise ValueError('Nonuniform simulation grid')
    with (directory/'input_hex_coordinates.csv').open(encoding='utf-8') as handle: coordinates=list(csv.DictReader(handle))
    if len(coordinates)!=721: raise ValueError('Require 721 coordinate rows')
    return stimulus,grid,coordinates,metadata

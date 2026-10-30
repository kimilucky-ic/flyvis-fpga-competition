"""Actual MP4 generation/decoding. No neuron model or target states here."""
from pathlib import Path
import cv2
import numpy as np

cv2.setNumThreads(1)
SIZE=224; FPS=100; DURATION=5.; DT=.005; PITCH=6.


def sampler(uv):
    x=np.sqrt(3)/2*uv[1]; y=-(uv[0]+uv[1]/2)
    xs=np.rint((SIZE-1)/2+PITCH*x).astype(np.int64)
    ys=np.rint((SIZE-1)/2-PITCH*y).astype(np.int64)
    assert len(xs)==721 and len(np.unique(np.stack([xs,ys],1),axis=0))==721
    assert xs.min()>=1 and ys.min()>=1 and xs.max()<SIZE-1 and ys.max()<SIZE-1
    return dict(x_pixel=xs,y_pixel=ys)


def render(path,case):
    path=Path(path); assert not path.exists()
    writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*'mp4v'),FPS,(SIZE,SIZE))
    if not writer.isOpened(): raise RuntimeError('MP4 encoder unavailable')
    yy,xx=np.mgrid[:SIZE,:SIZE]; x=(xx-(SIZE-1)/2)/PITCH; y=((SIZE-1)/2-yy)/PITCH
    rng=np.random.default_rng(case['texture_seed'])
    texture=cv2.GaussianBlur(rng.normal(size=(SIZE,SIZE)).astype(np.float32),(0,0),5)
    texture=np.tanh(texture/.05)
    if case['kind']=='motion':
        angle=np.deg2rad(case['angle']); cx,cy=case['center']
        projection=(x-cx)*np.cos(angle)+(y-cy)*np.sin(angle)
        aperture=.5*(1+np.tanh(3*(4.5-np.sqrt((x-cx)**2+(y-cy)**2)))) if case['local'] else np.ones_like(x)
    try:
        for j in range(int(FPS*DURATION)):
            t=j/FPS; elapsed=np.clip(t-1,0,3); amplitude=np.clip((t-1)/.1,0,1)
            if case['kind']=='gray': brightness=np.full_like(x,.5)
            elif case['kind']=='texture': brightness=.5+amplitude*.12*texture
            else:
                background=case['background']
                if background=='gray': bg=np.full_like(x,.5)
                elif background=='static_texture': bg=.5+.12*texture
                else:
                    ba=np.deg2rad(case['background_angle']); p=x*np.cos(ba)+y*np.sin(ba)
                    bg=.5+.08*np.sin(2*np.pi*(p-case['background_speed']*elapsed)/8)+.04*np.cos(2*np.pi*(.3*x-.7*y)/13)
                position=case['speed']*(elapsed-1.5)
                behind=.5*(1+np.tanh(6*(position-projection)))
                target=.2+.6*behind if case['polarity']=='ON' else .8-.6*behind
                picture=bg if case.get('target_absent',False) else bg+aperture*(target-bg)
                brightness=.5+amplitude*(picture-.5)
            gray=np.rint(brightness*255).clip(0,255).astype(np.uint8)
            writer.write(cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR))
    finally: writer.release()


def decode(path,sampling):
    xs,ys=sampling['x_pixel'],sampling['y_pixel']
    cap=cv2.VideoCapture(str(path))
    if not cap.isOpened(): raise ValueError('Cannot decode MP4')
    fps=float(cap.get(cv2.CAP_PROP_FPS)); shapes=set(); values=[]
    try:
        if not np.isclose(fps,FPS,atol=1e-6): raise ValueError('Expected frozen100fps')
        while True:
            okay,frame=cap.read()
            if not okay: break
            shapes.add(tuple(frame.shape[:2]))
            if frame.shape!=(SIZE,SIZE,3): raise ValueError('Frozen224x224 input required')
            gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            patch=np.stack([gray[ys+dy,xs+dx] for dy in [-1,0,1] for dx in [-1,0,1]])
            values.append(patch.mean(0,dtype=np.float64).astype(np.float32)/np.float32(255))
    finally: cap.release()
    values=np.asarray(values,np.float32)
    if len(values)!=500: raise ValueError('Exactly500 real decoded frames required; no temporal padding')
    ids=np.floor(np.arange(1000)*DT*fps+1e-9).astype(np.int64)
    assert np.array_equal(ids,np.repeat(np.arange(500),2))
    data=values[ids]
    late=values[400:]
    metadata=dict(fps=fps,decoded_frames=len(values),native_shapes=sorted(shapes),model_steps=1000,dt=DT,
        video_frame_ids=ids.tolist(),input_times=(np.arange(1000)*DT).tolist(),
        output_times=((np.arange(1000)+1)*DT).tolist(),sampling='721 original-coordinate points, 3x3 grayscale mean; pitch6px',
        temporal='causal zero-order hold; no future interpolation or temporal padding',
        late_input_temporal_RMS=float(np.sqrt(np.mean((late.astype(np.float64)-late.mean(0))**2))))
    return data,metadata

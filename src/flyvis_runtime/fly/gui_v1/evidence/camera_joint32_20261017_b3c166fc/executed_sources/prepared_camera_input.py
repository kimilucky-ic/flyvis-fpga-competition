"""Session-local official BoxEye with fixed full-field geometry prepared once.

Uses the original Pillow luminance, torchvision resize and BoxEye operations.
The frozen camera adapter remains the independent bitwise reference.
"""
import time
import numpy as np
from live_protocol import require

class PreparedCameraInput:
    def init__(self):
        from camera_pipeline.adapter import official_components
        self.torch,self.flyvis,self.BoxEye,_,_,self.resize=official_components()
        self.configs={}

    def prepare(self,h,w):
        key=(h,w)
        if key not in self.configs:
            require(len(self.configs)<2 and 1<=h<=2160 and 1<=w<=3840,'PREPARED_INPUT_SHAPE_BOUND')
            from camera_pipeline.adapter import render_bgr_frames
            _,coordinates,transform=render_bgr_frames(np.full((1,h,w,3),127,dtype=np.uint8),spatial_policy='full-field',chunk_frames=1)
            eye=self.BoxEye(extent=15,kernel_size=13);eye.conv=eye.conv.to('cpu')
            self.configs[key]=(eye,coordinates,transform)
        return self.configs[key]

    def render(self,bgr):
        from PIL import Image
        require(bgr.dtype==np.uint8 and bgr.ndim==3 and bgr.shape[2]==3,'PREPARED_INPUT_BGR')
        eye,coordinates,template=self.prepare(*bgr.shape[:2]);start=time.perf_counter();torch=self.torch
        gray=np.stack([np.asarray(Image.fromarray(np.asarray(bgr)[:,:,::-1]).convert('L'),dtype=np.float32)/255])
        movie=torch.from_numpy(gray).unsqueeze(0)
        rh,rw=template['resized_hw'];th,tw=template['render_hw'];oy,ox=template['offset_yx']
        with torch.no_grad():
            resized=self.resize(movie,[rh,rw],antialias=True)
            movie=torch.full((1,1,th,tw),0.5,dtype=torch.float32)
            movie[:,:,oy:oy+rh,ox:ox+rw]=resized
            values=eye(movie,ftype='mean',hex_sample=True).cpu().numpy()[0,:,0].astype(np.float32)
        require(values.shape==(1,721),'PREPARED_INPUT_OFFICIAL_SHAPE')
        return values,coordinates,dict(template,preprocessing_elapsed_s=time.perf_counter()-start,
            prepared_geometry=True,preprocessing_backend='original_BoxEye_CPU_session_cache')

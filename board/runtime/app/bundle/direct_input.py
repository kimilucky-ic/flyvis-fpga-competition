"""Direct grey receptor sampling; no image resize or intermediate canvas.
Changed visual-input contract, NOT equivalent to R7 13x13 area integration.
"""
import numpy as np
import step_profile as prof
from ps_input import receptor_centers, _weights

class DirectInput:
    def __init__(self,height=48,width=80,channel_order='BGR'):
        if type(height) is not int or type(width) is not int or min(height,width)<2 or max(height,width)>2048:
            raise ValueError('bounded image dimensions')
        if channel_order not in ('RGB','BGR','GBR'):raise ValueError('channel order')
        self.height,self.width=height,width
        self.channels=[channel_order.index(c) for c in 'RGB']
        scale=min(417/height,417/width)
        rh,rw=round(height*scale),round(width*scale)
        oy,ox=(417-rh)//2,(417-rw)//2
        rows,cols=receptor_centers().T
        self.valid=(rows>=oy)&(rows<oy+rh)&(cols>=ox)&(cols<ox+rw)
        y=np.clip((rows-oy+.5)*height/rh-.5,0,height-1)
        x=np.clip((cols-ox+.5)*width/rw-.5,0,width-1)
        y0=np.floor(y).astype(np.intp);x0=np.floor(x).astype(np.intp)
        y1=np.minimum(y0+1,height-1);x1=np.minimum(x0+1,width-1)
        self.indices=np.stack((y0*width+x0,y0*width+x1,y1*width+x0,y1*width+x1))
        self.wx=(x-x0).astype(np.float32);self.wy=(y-y0).astype(np.float32)
        for a in (self.valid,self.indices,self.wx,self.wy):a.flags.writeable=False
        self.contract=dict(name='direct-grey-bilinear-centres/v1',width=width,height=height,
            channel_order=channel_order,inputs=721,outside_field_value=.5,
            axis_order='same row,column ordering as R7 receptor_centers',
            threshold=False,intermediate_image=False,old_area_average=False)
    def render(self,frame):
        if not isinstance(frame,np.ndarray) or frame.dtype!=np.uint8 or frame.shape!=(self.height,self.width,3):
            raise ValueError('completed fixed-shape uint8 frame required')
        t=prof.tick()
        pixels=frame.reshape(-1,3)[self.indices]
        lum=pixels[...,self.channels[0]].astype(np.uint32)*np.uint32(19595)
        lum+=pixels[...,self.channels[1]].astype(np.uint32)*np.uint32(38470)
        lum+=pixels[...,self.channels[2]].astype(np.uint32)*np.uint32(7471)
        lum=(lum+np.uint32(32768))>>np.uint32(16)
        g=lum.astype(np.float32)/np.float32(255)
        top=g[0]*(np.float32(1)-self.wx)+g[1]*self.wx
        bottom=g[2]*(np.float32(1)-self.wx)+g[3]*self.wx
        out=top*(np.float32(1)-self.wy)+bottom*self.wy
        out[~self.valid]=np.float32(.5)
        if out.shape!=(721,) or not np.isfinite(out).all() or np.any(out<0) or np.any(out>1):
            raise ValueError('invalid receptor intensities')
        prof.add('preprocess_direct_grey_721',t)
        return out

class DirectAreaInput(DirectInput):
    """Fold resize and receptor-area coefficients once; no resized frame at runtime.
    Center square crop fills the same721 receptor coordinates without padding.
    Grey conversion only visits the crop. This changes the visual stimulus.
    """
    def __init__(self,height=48,width=80,channel_order='BGR'):
        super().__init__(height,width,channel_order)
        self.crop_size=min(height,width)
        self.crop_top=(height-self.crop_size)//2
        self.crop_left=(width-self.crop_size)//2
        rh=rw=417;oy=ox=0
        yt,xt=_weights(self.crop_size,rh),_weights(self.crop_size,rw)
        self.valid=np.ones(721,dtype=bool);self.valid.flags.writeable=False
        rows=[];bias=[]
        for cy,cx in receptor_centers():
            def combined(c,offset,target,taps):
                d={};valid=0
                for pos in range(c-6,c+7):
                    if 0<=pos-offset<target:
                        valid+=1
                        ids,weights=taps[pos-offset]
                        for i,w in zip(ids,weights):d[int(i)]=d.get(int(i),0.)+float(w)/13.
                return d,valid
            ys,ny=combined(cy,oy,rh,yt);xs,nx=combined(cx,ox,rw,xt)
            rows.append([(y*self.crop_size+x,wy*wx) for y,wy in sorted(ys.items()) for x,wx in sorted(xs.items())])
            bias.append(.5*(1-ny*nx/169.))
        taps=max(map(len,rows));self.area_indices=np.zeros((taps,721),dtype=np.intp)
        self.area_weights=np.zeros((taps,721),dtype=np.float32)
        for j,row in enumerate(rows):
            for i,(ix,w) in enumerate(row):self.area_indices[i,j]=ix;self.area_weights[i,j]=w
        self.bias=np.asarray(bias,dtype=np.float32)
        for a in (self.area_indices,self.area_weights,self.bias):a.flags.writeable=False
        if np.any(self.bias):raise RuntimeError('Square crop must cover every receptor footprint')
        self.contract.update(name='direct-grey-center-square-area/v2',old_area_average=True,
            crop=dict(top=self.crop_top,left=self.crop_left,height=self.crop_size,width=self.crop_size),
            outside_field_value=None,grey_pixels=self.crop_size*self.crop_size,aspect_preserved=True,
            input_arithmetic='folded coefficients; tolerance equivalence only',max_taps=taps)
    def render(self,frame):
        if not isinstance(frame,np.ndarray) or frame.dtype!=np.uint8 or frame.shape!=(self.height,self.width,3):
            raise ValueError('completed fixed-shape uint8 frame required')
        t=prof.tick();part=prof.tick()
        crop=frame[self.crop_top:self.crop_top+self.crop_size,self.crop_left:self.crop_left+self.crop_size]
        pixels=crop.reshape(-1,3)
        lum=pixels[...,self.channels[0]].astype(np.uint32)*np.uint32(19595)
        lum+=pixels[...,self.channels[1]].astype(np.uint32)*np.uint32(38470)
        lum+=pixels[...,self.channels[2]].astype(np.uint32)*np.uint32(7471)
        grey=((lum+np.uint32(32768))>>np.uint32(16)).astype(np.float32)/np.float32(255)
        prof.add('map_grey_once',part);part=prof.tick()
        grey=grey[self.area_indices]
        prof.add('map_gather',part);part=prof.tick()
        out=np.sum(grey*self.area_weights,axis=0,dtype=np.float32)+self.bias
        prof.add('map_weighted_sum',part);part=prof.tick()
        if not np.isfinite(out).all() or np.any(out<0) or np.any(out>np.float32(1.000001)):
            raise ValueError('invalid receptor intensities')
        out=np.clip(out,np.float32(0),np.float32(1))
        prof.add('map_range_check_clip',part)
        prof.add('preprocess_direct_grey_721',t)
        return out

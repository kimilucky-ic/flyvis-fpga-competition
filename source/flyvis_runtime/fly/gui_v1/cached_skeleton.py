"""Validated fixed SWC projection recipe; CPU reference for browser draw receipts.

This module does no neural computation and cannot create input or activity values.
"""
import hashlib
import json
import struct
import numpy as np
from live_protocol import require

MAX_CACHE=16_000_000

class CachedSkeleton:
    def init__(self,blob,health):
        require(4<len(blob)<=MAX_CACHE,'PROJECTION_CACHE_BOUND')
        n=struct.unpack_from('<I',blob)[0];require(0<n<65536 and n+4<len(blob),'PROJECTION_CACHE_HEADER')
        m=json.loads(blob[4:4+n]);data=blob[4+n:]
        require(m['schema']=='flyvis-fixed-cpu-cache/v1' and m['projection_sha256']==health['fixed_cpu_projection_sha256'],'PROJECTION_CACHE_IDENTITY')
        require(m['width']==health['viewport']['width'] and m['height']==health['viewport']['height'],'PROJECTION_CACHE_VIEW')
        require(hashlib.sha256(data).hexdigest()==m['payload_sha256'],'PROJECTION_CACHE_SHA')
        require(len(m['arrays'])==10 and len(m['boxes'])==8,'PROJECTION_CACHE_LAYERS')
        arrays={};end=0
        for a in m['arrays']:
            require(a['offset']==end and a['dtype'] in ('<f4','|u1') and a['name'] not in arrays,'PROJECTION_CACHE_ARRAY')
            length=a['length'];require(type(length) is int and 0<length<=len(data)-end,'PROJECTION_CACHE_LENGTH')
            arr=np.frombuffer(data,dtype=a['dtype'],count=length//np.dtype(a['dtype']).itemsize,offset=end).reshape(a['shape'])
            require(arr.nbytes==length and np.isfinite(arr).all(),'PROJECTION_CACHE_VALUES')
            arrays[a['name']]=arr;end+=length
        require(end==len(data),'PROJECTION_CACHE_TRAILING')
        w,h=m['width'],m['height'];self.base=arrays.pop('base');self.alpha=arrays.pop('alpha')
        require(self.base.shape==(h,w,3) and self.base.dtype==np.dtype('<f4') and np.all((self.base>=0)&(self.base<=255)),'PROJECTION_CACHE_BASE')
        require(self.alpha.shape==(h,w) and self.alpha.dtype==np.uint8,'PROJECTION_CACHE_ALPHA')
        self.layers=[]
        for i,(y0,y1,x0,x1) in enumerate(m['boxes']):
            require(all(type(v) is int for v in (y0,y1,x0,x1)) and 0<=y0<y1<=h and 0<=x0<x1<=w,'PROJECTION_CACHE_BOX')
            weight=arrays.pop('weight'+str(i));require(weight.shape==(y1-y0,x1-x0,1) and np.all((weight>=0)&(weight<=1)),'PROJECTION_CACHE_WEIGHT')
            self.layers.append(((slice(y0,y1),slice(x0,x1)),weight))
        require(not arrays,'PROJECTION_CACHE_UNKNOWN_ARRAY')
        self.blob=blob;self.metadata=m;self.sha256=hashlib.sha256(blob).hexdigest()
        # Only pixels touched by true skeleton masks can change. Precompute
        # their indexing once; keep the same float32 accumulation order.
        active=np.zeros(h*w,dtype=bool);sparse=[]
        for (ys,xs),weight in self.layers:
            yy,xx=np.nonzero(weight[:,:,0]);indices=(yy+ys.start)*w+xx+xs.start
            active[indices]=True;sparse.append((indices,weight[yy,xx,0,None]))
        self.active=np.flatnonzero(active);self.active_base=self.base.reshape(-1,3)[self.active].copy()
        self.sparse_layers=[(np.searchsorted(self.active,indices),weight) for indices,weight in sparse]
        self.static_rgba=np.empty((h*w,4),dtype=np.uint8)
        self.static_rgba[:,:3]=np.clip(self.base.reshape(-1,3)+.5,0,255).astype(np.uint8)
        self.static_rgba[:,3]=self.alpha.reshape(-1)

    def render(self,means,health):
        encoding=health['color_encoding'];values=np.asarray(means,dtype=np.float64)
        brightness=.25+.75*np.clip(np.abs(values)/encoding['intensity_domain'][1],0,1)**.45
        types=health['expected_binding']['types']
        bases=np.array([[int(encoding['palette'][t][i:i+2],16)/255 for i in (1,3,5)] for t in types])
        colors=np.asarray(bases*brightness[:,None],dtype=np.float32);out=self.active_base.copy()
        for (indices,weight),color in zip(self.sparse_layers,colors):out[indices]+=weight*(color*255)
        rgba=self.static_rgba.copy();rgba[self.active,:3]=np.clip(out+.5,0,255).astype(np.uint8)
        rgba=rgba.reshape(*self.alpha.shape,4)
        states=[dict(type=t,value=float(value),activity_signed=float(value),brightness_factor=float(b),saturated=bool(abs(value)>encoding['intensity_domain'][1])) for t,value,b in zip(types,values,brightness)]
        return rgba,states

"""Fixed mature-camera projection of original SWC edges, CPU brightness compositing.

Geometry and the source-derived ROI background are cached once. This is a flat
projection of true morphology, not a new neural model or a biological measurement.
No activity interpolation, per-frame geometry, WGPU draw, or GPU readback occurs.
"""
import hashlib
import json
from pathlib import Path
import time
import struct
import numpy as np
from PIL import Image, ImageDraw


class FixedCPU:
    def init__(self,scene,folder):
        begin=time.perf_counter();self.scene=scene
        w,h=map(int,scene.v.size);self.width=w;self.height=h
        names=[o['name'] for o in scene.objects]
        scene.v.hide_objects(names)
        try:
            scene.v.canvas.request_draw()
            background=np.asarray(scene.v.canvas.draw()).copy()
        finally:scene.v.unhide_objects(names)
        if background.shape!=(h,w,4):raise ValueError('FIXED_BACKGROUND_SHAPE')
        # Supersampling applies only to static edge masks, never neural values.
        masks=[];identity=[];depths=[];factor=2
        matrix=np.array(scene.v.camera.camera_matrix,dtype=np.float64)
        for neuron,o,points in zip(scene.neurons,scene.objects,scene.neuron_points):
            clip=np.column_stack([points,np.ones(len(points))])@matrix.T
            ndc=clip[:,:3]/clip[:,3,None]
            xy=np.column_stack([(ndc[:,0]+1)*w/2,(1-ndc[:,1])*h/2])
            if not np.isfinite(xy).all():raise ValueError('FIXED_PROJECTION_FINITE')
            nodes=neuron.nodes;lookup={int(v):i for i,v in enumerate(nodes.node_id)}
            pairs=[(i,lookup[int(parent)]) for i,parent in enumerate(nodes.parent_id) if int(parent) in lookup]
            image=Image.new('L',(w*factor,h*factor));draw=ImageDraw.Draw(image)
            for a,b in pairs:
                draw.line([tuple(xy[a]*factor),tuple(xy[b]*factor)],fill=255,width=7)
            mask=np.asarray(image.resize((w,h),Image.Resampling.LANCZOS),dtype=np.float32)/255
            masks.append(mask);depths.append(float(ndc[:,2].mean()))
            identity.append(dict(type=o['type'],body_id=o['body_id'],swc_sha256=o['swc_sha256'],
                                 nodes=len(points),edges=len(pairs),mask_sha256=hashlib.sha256(mask.tobytes()).hexdigest()))
        # A fixed painter order resolves overlaps consistently. This projected
        # display is explicitly distinct from full per-frame 3-D depth rendering.
        order=np.argsort(depths)[::-1];transmission=np.ones((h,w),dtype=np.float32)
        weights=[None]*len(masks)
        for i in reversed(order):weights[i]=masks[i]*transmission;transmission*=1-masks[i]
        self.base=background[:,:,:3].astype(np.float32)*transmission[:,:,None]
        self.layers=[]
        for weight in weights:
            yy,xx=np.nonzero(weight)
            if not len(xx):raise ValueError('FIXED_EMPTY_TYPE_MASK')
            box=(slice(yy.min(),yy.max()+1),slice(xx.min(),xx.max()+1))
            self.layers.append((box,weight[box][:,:,None]))
        self.alpha=background[:,:,3]
        self.identity=dict(schema='line10.fixed_cpu_projection.v1',width=w,height=h,types=identity,
            background_sha256=hashlib.sha256(background.tobytes()).hexdigest(),camera_matrix=matrix.tolist(),
            background_manifest_sha256=scene.background_manifest_sha256,
            occlusion_policy='fixed per-type mean-depth painter order; projected display, not full 3D depth',
            neural_values_generated=False,initialization_ms=(time.perf_counter()-begin)*1000)
        self.digest=hashlib.sha256(json.dumps(self.identity,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
        Image.fromarray(background).save(folder/'fixed_background.png')
        np.savez_compressed(folder/'fixed_masks.npz',masks=np.stack(masks))
        (folder/'fixed_projection.json').write_text(json.dumps(dict(self.identity,sha256=self.digest),indent=2),encoding='utf-8')

    def compose(self,colors):
        colors=np.asarray(colors,dtype=np.float32)
        if colors.shape!=(8,3) or not np.isfinite(colors).all():raise ValueError('FIXED_COLOR_SHAPE')
        out=self.base.copy()
        for (box,weight),color in zip(self.layers,colors):out[box]+=weight*(color*255)
        rgba=np.empty((self.height,self.width,4),dtype=np.uint8)
        rgba[:,:,:3]=np.clip(out+.5,0,255).astype(np.uint8);rgba[:,:,3]=self.alpha
        return rgba

    def cache_wire(self):
        arrays=[];payload=[];offset=0
        def add(name,value):
            nonlocal offset
            value=np.ascontiguousarray(value);raw=value.tobytes()
            arrays.append(dict(name=name,offset=offset,length=len(raw),shape=list(value.shape),dtype=value.dtype.str))
            payload.append(raw);offset+=len(raw)
        add('base',self.base.astype('<f4'));add('alpha',self.alpha)
        boxes=[]
        for i,(box,weight) in enumerate(self.layers):
            boxes.append([int(box[0].start),int(box[0].stop),int(box[1].start),int(box[1].stop)])
            add('weight'+str(i),weight.astype('<f4'))
        data=b''.join(payload)
        header=json.dumps(dict(schema='flyvis-fixed-cpu-cache/v1',projection_sha256=self.digest,
            width=self.width,height=self.height,boxes=boxes,arrays=arrays,payload_sha256=hashlib.sha256(data).hexdigest()),separators=(',',':')).encode()
        return struct.pack('<I',len(header))+header+data

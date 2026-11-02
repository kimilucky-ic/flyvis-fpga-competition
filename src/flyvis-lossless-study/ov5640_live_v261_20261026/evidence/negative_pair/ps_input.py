"""NumPy-only PS candidate; no board/camera/Torch imports. Not bitwise Torch."""
import numpy as np
import step_profile as prof


def rgb565_to_rgb(words):
    words = np.asarray(words)
    if words.dtype != np.uint16 or words.ndim != 2:
        raise ValueError('require HxW uint16 RGB565, byte order resolved upstream')
    return np.stack(((words >> 8) & 248, (words >> 3) & 252,
                     (words << 3) & 248), axis=-1).astype(np.uint8)


def rgb_luminance(rgb):
    x = rgb.astype(np.uint32)
    return ((19595*x[..., 0]+38470*x[..., 1]+7471*x[..., 2]+32768) >> 16).astype(np.uint8)


def receptor_centers():
    # Torch long truncates half-integers before adding origin.
    return np.asarray([(int(13*(u+v/2)), 13*v) for u in range(-15, 16)
                       for v in range(max(-15, -15-u), min(15, 15-u)+1)], dtype=np.int32)+208


def _weights(source, target):
    scale, taps = source/target, []
    support = max(1., scale)
    for out in range(target):
        center = (out+.5)*scale-.5
        ix = np.arange(max(0, int(np.ceil(center-support))), min(source, int(np.floor(center+support))+1))
        w = np.maximum(0., 1.-np.abs(ix-center)/support)
        taps.append((ix, (w/w.sum()).astype(np.float32)))
    return taps


class PsInput:
    """Fixed mapping; caller holds a completed immutable frame during render.

    No capture, temporal resampling or STEP. Channel order requires colour test.
    Full-field geometry follows camera_pipeline/adapter.py. Numerical tolerance
    must be recorded; neural strict FP32 verification uses actual saved inputs.
    """
    def __init__(self, height=480, width=640, channel_order='RGB'):
        if (not isinstance(height, int) or not isinstance(width, int) or
                min(height, width) < 2 or max(height, width) > 2048):
            raise ValueError('require integer dimensions 2..2048')
        if channel_order not in ('RGB', 'BGR', 'GBR'):
            raise ValueError('require explicit RGB/BGR/GBR channel order')
        self.height, self.width = height, width
        self.channels = [channel_order.index(c) for c in 'RGB']
        scale = min(417/height, 417/width)
        self.rh, self.rw = max(1, round(height*scale)), max(1, round(width*scale))
        self.oy, self.ox = (417-self.rh)//2, (417-self.rw)//2
        self.yweights, self.xweights = _weights(height, self.rh), _weights(width, self.rw)
        self.centers = receptor_centers()
        # Batch independent destinations, retaining each destination's tap order.
        def groups(taps):
            result=[]
            for k in range(max(len(ix) for ix,w in taps)):
                dst=np.asarray([j for j,(ix,w) in enumerate(taps) if k<len(ix)],dtype=np.intp)
                src=np.asarray([taps[j][0][k] for j in dst],dtype=np.intp)
                weights=np.asarray([taps[j][1][k] for j in dst],dtype=np.float32)
                result.append((dst,src,weights))
            return result
        self.xgroups,self.ygroups=groups(self.xweights),groups(self.yweights)
        rows,cols=self.centers.T
        self.window_indices=np.asarray([(rows+dy)*417+cols+dx for dy in range(-6,7) for dx in range(-6,7)])

    def render(self, frame):
        if not isinstance(frame, np.ndarray) or frame.dtype != np.uint8 or frame.shape != (self.height, self.width, 3):
            raise ValueError('require fixed HxWx3 uint8 completed captured frame')
        # Same integer luminance, avoid reordered full RGB image and three-plane uint32 copy.
        _phase=prof.tick()
        lum=frame[...,self.channels[0]].astype(np.uint32);lum*=np.uint32(19595)
        for channel,weight in ((self.channels[1],38470),(self.channels[2],7471)):
            term=frame[...,channel].astype(np.uint32);term*=np.uint32(weight);lum+=term
        lum+=np.uint32(32768);lum>>=np.uint32(16)
        gray=lum.astype(np.float32)/np.float32(255.)
        prof.add('preprocess_gray',_phase);_phase=prof.tick()
        horizontal = np.zeros((self.height,self.rw),dtype=np.float32)
        for dst,src,weights in self.xgroups:
            horizontal[:,dst] += gray[:,src]*weights[None,:]
        prof.add('preprocess_horizontal',_phase);_phase=prof.tick()
        vertical = np.zeros((self.rh,self.rw),dtype=np.float32)
        for dst,src,weights in self.ygroups:
            vertical[dst,:] += horizontal[src,:]*weights[:,None]
        prof.add('preprocess_vertical',_phase);_phase=prof.tick()
        canvas=np.full((417,417),.5,dtype=np.float32)
        canvas[self.oy:self.oy+self.rh,self.ox:self.ox+self.rw]=vertical
        # Explicit prefix0 plus ordered accumulate preserves all169 original additions.
        # This is not pairwise sum/reduce/dot/BLAS; independent receptor columns only.
        samples=np.empty((170,721),dtype=np.float32);samples[0,:]=0
        samples[1:,:]=canvas.ravel()[self.window_indices]
        np.add.accumulate(samples,axis=0,dtype=np.float32,out=samples)
        out=samples[-1,:].copy()
        out /= np.float32(169.)
        prof.add('preprocess_receptors',_phase)
        if not np.isfinite(out).all() or np.any(out < 0) or np.any(out > 1):
            raise RuntimeError('input outside intensity contract')
        return out

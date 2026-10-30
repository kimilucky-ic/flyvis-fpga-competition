"""NumPy-only PS candidate; no board/camera/Torch imports. Not bitwise Torch."""
import numpy as np


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
    def init__(self, height=480, width=640, channel_order='RGB'):
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

    def render(self, frame):
        if not isinstance(frame, np.ndarray) or frame.dtype != np.uint8 or frame.shape != (self.height, self.width, 3):
            raise ValueError('require fixed HxWx3 uint8 completed captured frame')
        gray = rgb_luminance(frame[..., self.channels]).astype(np.float32)/np.float32(255.)
        horizontal = np.empty((self.height, self.rw), dtype=np.float32)
        for j, (ix, weights) in enumerate(self.xweights):
            acc = np.zeros(self.height, dtype=np.float32)
            for k, weight in zip(ix, weights):
                acc += gray[:, k]*weight
            horizontal[:, j] = acc
        canvas = np.full((417, 417), .5, dtype=np.float32)
        for j, (ix, weights) in enumerate(self.yweights):
            acc = np.zeros(self.rw, dtype=np.float32)
            for k, weight in zip(ix, weights):
                acc += horizontal[k]*weight
            canvas[self.oy+j, self.ox:self.ox+self.rw] = acc
        # All 721 windows lie inside 417x417; accumulate each in row-major
        # order, vectorizing over independent receptors, never reducing BLAS.
        rows, cols = self.centers.T
        out = np.zeros(721, dtype=np.float32)
        for dy in range(-6, 7):
            for dx in range(-6, 7):
                out += canvas[rows+dy, cols+dx]
        out /= np.float32(169.)
        if not np.isfinite(out).all() or np.any(out < 0) or np.any(out > 1):
            raise RuntimeError('input outside intensity contract')
        return out

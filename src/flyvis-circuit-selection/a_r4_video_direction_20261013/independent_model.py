"""Induced-network continuous FlyVis equations; NumPy CPU, no external state API.

Reduced topology is a new model. No deleted neurons are computed or replayed.
Original-edge order and float32 scatter arithmetic are kept explicitly.
"""
import numpy as np


class IndependentModel:
    def init__(self, path):
        with np.load(path, allow_pickle=False) as data:
            self.p = {key: data[key].copy() for key in data.files}
        p = self.p
        self.n = len(p['bias'])
        self.n_pixels = len(p['input_hex_global_index'])
        for key in ['bias', 'time_const', 'weight']:
            if p[key].dtype != np.float32 or not np.isfinite(p[key]).all():
                raise ValueError('finite original float32 parameters required')
        for key in ['source', 'target', 'input_local_index']:
            ids = p[key]
            if ids.dtype.kind not in 'iu' or (ids < 0).any() or (ids >= self.n).any():
                raise ValueError('only retained local neuron indices are allowed')
        if len(p['source']) != len(p['weight']) or len(p['target']) != len(p['weight']):
            raise ValueError('edge schema')
        if p['time_const'].shape != (self.n,) or np.any(p['time_const'] <= 0):
            raise ValueError('time constant schema')
        self.inv_tau = np.float32(1) / np.maximum(p['time_const'], np.float32(.005))

    def step(self, old, local_pixels):
        if old.dtype != np.float32 or old.shape != (self.n,) or not np.isfinite(old).all():
            raise ValueError('finite candidate OWN old state required')
        if local_pixels.dtype != np.float32 or local_pixels.shape != (self.n_pixels,):
            raise ValueError('candidate retina shape/type')
        if not np.isfinite(local_pixels).all() or (local_pixels < 0).any() or (local_pixels > 1).any():
            raise ValueError('finite exogenous pixels in [0,1] required')
        p = self.p
        chemical = np.zeros(self.n, np.float32)
        current = p['weight'] * np.maximum(old[p['source']], np.float32(0))
        np.add.at(chemical, p['target'], current)
        stimulus = np.zeros(self.n, np.float32)
        stimulus[p['input_local_index']] = local_pixels[p['input_pixel_index']]
        # Exact operation order of PPNeuronIGRSynapses and Network._next_state.
        velocity = self.inv_tau * (((-old + p['bias']) + chemical) + stimulus)
        candidate = old + velocity * np.float32(.005)
        if not np.isfinite(candidate).all():
            raise FloatingPointError('nonfinite candidate: no commit')
        return candidate

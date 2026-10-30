"""Independent, stateless FlyVis H Euler step. NumPy only; no FlyVis calls."""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import numpy as np


class StepError(RuntimeError):
    def init__(self, code, detail):
        super().init__(f'{code}: {detail}')
        self.code = code


def array_hash(value):
    a = np.ascontiguousarray(value)
    header = json.dumps({'shape': list(a.shape), 'dtype': a.dtype.str}, sort_keys=True).encode()
    return hashlib.sha256(header + a.tobytes()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def frozen(value):
    value = np.array(value, copy=True, order='C')
    value.flags.writeable = False
    return value


def vector(value, count, name):
    if not isinstance(value, np.ndarray) or value.dtype != np.dtype('<f4'):
        raise StepError('BAD_DTYPE', name + ' must be little-endian float32')
    if value.shape != (count,) or not value.flags.c_contiguous:
        raise StepError('BAD_LENGTH', name + ' must be a contiguous ordered vector')
    if not np.isfinite(value).all():
        raise StepError('NONFINITE', name)
    return value


@dataclass(frozen=True)
class StepTag:
    run_id: str
    comparison_id: str
    condition_id: str
    epoch: int
    step_id: int
    old_full_digest: str


@dataclass(frozen=True)
class HRequest:
    tag: StepTag
    layout: str
    old_h: np.ndarray
    x_h: np.ndarray
    boundary: np.ndarray
    h_global_ids: np.ndarray
    source_global_ids: np.ndarray | None
    circuit_digest: str


@dataclass(frozen=True)
class HResult:
    tag: StepTag
    layout: str
    new_h: np.ndarray
    chemical: np.ndarray
    h_order_digest: str
    circuit_digest: str
    request_digest: str


def request_hash(request):
    values = dict(tag=request.tag.__dict__, layout=request.layout,
        old_h=array_hash(request.old_h), x_h=array_hash(request.x_h),
        boundary=array_hash(request.boundary), h_ids=array_hash(request.h_global_ids),
        source_ids=None if request.source_global_ids is None else array_hash(request.source_global_ids),
        circuit=request.circuit_digest)
    return hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()


class HUpdater:
    """One continuous activity per H node; state ownership belongs to coordinator.

    SOURCE_RAW adds HH and RH currents in original edge-index order.
    CURRENT_AGG adds a separately reduced RH vector after the HH reduction.
    All array arithmetic, including inverse_tau and dt, stays float32.
    """
    def init__(self, static_path, dt_s=0.005):
        self.static_path = Path(static_path)
        self.circuit_digest = file_hash(static_path)
        self.dt = np.float32(dt_s)
        if not np.isfinite(self.dt) or self.dt <= 0:
            raise StepError('BAD_DT', 'dt must be finite and positive')
        with np.load(static_path, allow_pickle=False) as archive:
            data = {key: frozen(archive[key]) for key in archive.files}
        self.h_ids = data['global_node_id']
        self.source_ids = data['incoming_source_global_node_id']
        self.n = len(self.h_ids)
        if not np.all(np.diff(self.h_ids) > 0) or not np.all(np.diff(self.source_ids) > 0):
            raise StepError('LAYOUT_MISMATCH', 'node IDs must be unique and ascending')
        if np.intersect1d(self.h_ids, self.source_ids).size:
            raise StepError('LAYOUT_MISMATCH', 'incoming sources must belong to R')
        self.bias = vector(data['bias'], self.n, 'bias')
        tau = vector(data['time_const_s'], self.n, 'time_const_s')
        self.inverse_tau = frozen(np.ones(self.n, dtype=np.float32) / np.maximum(tau, self.dt))
        self.hh_src = data['internal_source_local']
        self.hh_dst = data['internal_target_local']
        self.hh_weight = data['internal_weight']
        self.rh_dst = data['incoming_target_local']
        self.rh_weight = data['incoming_weight']
        self.rh_src = frozen(np.searchsorted(self.source_ids, data['incoming_source_index']))
        if not np.array_equal(self.source_ids[self.rh_src], data['incoming_source_index']):
            raise StepError('LAYOUT_MISMATCH', 'RH source map')
        if not np.array_equal(self.h_ids[self.hh_src], data['internal_source_index']):
            raise StepError('LAYOUT_MISMATCH', 'HH source map')
        for route in ['internal', 'incoming']:
            if not np.array_equal(data[route + '_weight'],
                (data[route + '_sign'] * data[route + '_syn_count']) * data[route + '_syn_strength']):
                raise StepError('MODEL_MISMATCH', 'expanded weight product')
            if not np.isfinite(data[route + '_weight']).all():
                raise StepError('NONFINITE', 'weight')
            if not np.array_equal(self.h_ids[data[route + '_target_local']], data[route + '_target_index']):
                raise StepError('LAYOUT_MISMATCH', 'target map')
        self.edge_order = frozen(np.argsort(np.concatenate([data['internal_edge_id'], data['incoming_edge_id']]), kind='stable'))
        if len(np.unique(np.concatenate([data['internal_edge_id'], data['incoming_edge_id']]))) != len(self.edge_order):
            raise StepError('LAYOUT_MISMATCH', 'duplicate original edge ID')
        self.combined_dst = frozen(np.concatenate([self.hh_dst, self.rh_dst])[self.edge_order])
        self.h_order_digest = array_hash(self.h_ids)
        self.source_order_digest = array_hash(self.source_ids)
        self.step_count = 0

    def aggregate_sources(self, source_old):
        source_old = vector(source_old, len(self.source_ids), 'incoming_source_old')
        currents = self.rh_weight * np.maximum(source_old[self.rh_src], np.float32(0))
        result = np.zeros(self.n, dtype=np.float32)
        np.add.at(result, self.rh_dst, currents)
        return frozen(result)

    def step(self, request):
        if request.circuit_digest != self.circuit_digest:
            raise StepError('MODEL_MISMATCH', 'H circuit digest')
        if not np.array_equal(request.h_global_ids, self.h_ids):
            raise StepError('LAYOUT_MISMATCH', 'old_H and x_H node order')
        if type(request.tag.step_id) is not int or request.tag.step_id < 0:
            raise StepError('OUT_OF_ORDER', 'nonnegative integer step_id required')
        old = vector(request.old_h, self.n, 'old_H')
        x = vector(request.x_h, self.n, 'x_H')
        internal = self.hh_weight * np.maximum(old[self.hh_src], np.float32(0))
        if request.layout == 'SOURCE_RAW':
            if request.source_global_ids is None or not np.array_equal(request.source_global_ids, self.source_ids):
                raise StepError('LAYOUT_MISMATCH', 'incoming source node order')
            boundary = vector(request.boundary, len(self.source_ids), 'incoming_source_old')
            incoming = self.rh_weight * np.maximum(boundary[self.rh_src], np.float32(0))
            chemical = np.zeros(self.n, dtype=np.float32)
            np.add.at(chemical, self.combined_dst, np.concatenate([internal, incoming])[self.edge_order])
        elif request.layout == 'CURRENT_AGG':
            if request.source_global_ids is not None:
                raise StepError('LAYOUT_MISMATCH', 'CURRENT_AGG boundary is indexed by H, not R sources')
            boundary = vector(request.boundary, self.n, 'J_RH')
            chemical = np.zeros(self.n, dtype=np.float32)
            np.add.at(chemical, self.hh_dst, internal)
            chemical = chemical + boundary
        else:
            raise StepError('LAYOUT_MISMATCH', 'explicit SOURCE_RAW or CURRENT_AGG required')
        velocity = self.inverse_tau * (((-old + self.bias) + chemical) + x)
        new = old + velocity * self.dt
        vector(new, self.n, 'new_H')
        self.step_count += 1
        return HResult(request.tag, request.layout, frozen(new), frozen(chemical),
            self.h_order_digest, self.circuit_digest, request_hash(request))

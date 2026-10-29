"""Frozen-CNN follow-up. All upstream and accepted results are read-only."""
from pathlib import Path
import sys, time, json, hashlib, csv, ctypes, shutil, importlib.util

HERE = Path(__file__).resolve().parent
REFINE = HERE.parent / 'cnn_t4t5_cpu_refinement_20261016'
sys.path.insert(0, str(REFINE))
import shared as ref
import numpy as np
import torch

base = ref.base
dump, load, sha, digest = ref.dump, ref.load, ref.sha, ref.digest
OriginalTargets, ClosedLoop, CNNService = ref.OriginalTargets, ref.ClosedLoop, ref.CNNService
LANE, BUNDLE, TYPES = ref.LANE, ref.BUNDLE, ref.TYPES
DT = .005
ROI_PATH = LANE / 't4t5_criticality_20261011/cpu_preparation_r1/flow_ROI_hex_indices.npy'
METRIC_PATH = LANE / 't4t5_criticality_20261011/metrics.py'
RAW = LANE / 'phase4_direction_extension_20261010/prepared_inputs/stimulus_float32.npy'
SAMPLES = RAW.parent / 'samples_source.csv'
MODEL = REFINE / 'training/ridge.pt'
MODEL_SHA = 'cd00f98ab438e743b5437e05725830dba353183ac6f2d882a195c65b1ec2c016'


def memory():
    class Status(ctypes.Structure):
        _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [
            (name, ctypes.c_ulonglong) for name in ['total', 'available', 'page_total', 'page_available',
                                                   'virtual_total', 'virtual_available', 'extended']]
    status = Status(); status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError('GlobalMemoryStatusEx failed')
    return dict(available_bytes=status.available, total_bytes=status.total)


def check(deep=False):
    registration = load(HERE / 'PREREGISTRATION.json')
    assert sha(HERE / 'PREREGISTRATION.json') == load(HERE / 'FREEZE.json')['sha256']
    assert sha(MODEL) == MODEL_SHA
    for path, record in registration['pins'].items():
        p = Path(path)
        assert p.stat().st_size == record['bytes'] and p.stat().st_mtime_ns == record['mtime_ns'], path
        if deep: assert sha(p) == record['sha256'], path
    return registration


def vector_metrics(reference, value, roi, window):
    """Original frozen arithmetic, extended ONLY from fixed485 to arbitrary T."""
    reference, value = np.asarray(reference, dtype=np.float64), np.asarray(value, dtype=np.float64)
    if reference.shape != value.shape or reference.ndim != 3 or reference.shape[1:] != (2, 721):
        raise ValueError('flow shape')
    if len(reference) < window.stop or window.start < 200 or not np.isfinite(reference).all() or not np.isfinite(value).all():
        raise ValueError('window/finite')
    baseline = reference[160:200].mean(0)
    r = (reference - baseline)[window][:, :, roi]
    v = (value - baseline)[window][:, :, roi]
    energy = float(np.sum(r*r))
    rms = float(np.sqrt(np.mean(np.sum(r*r, axis=1))))
    noise = float(np.sqrt(np.mean(np.sum((reference[160:200][:, :, roi]-baseline[:, roi])**2, axis=1))))
    eligible = bool(rms >= 1e-4 and rms >= 5*max(noise, 1e-6))
    result = dict(reference_response_rms=rms, reference_pre_window_rms=noise, reference_eligible=eligible,
                  pre_step_range=[160, 199], active_step_range=[window.start, window.stop-1], n_hexals=len(roi))
    if not eligible or energy == 0:
        return dict(result, Q=None, magnitude_ratio=None, field_error_E=None, angle_deg=None,
                    reason='REFERENCE_TOO_WEAK_OR_UNSTABLE', pass_gate=False)
    q = float(np.sum(r*v)/energy)
    mag = float(np.sqrt(np.sum(v*v)/energy))
    error = float(np.sqrt(np.sum((v-r)**2)/energy))
    angle = float(np.degrees(np.arccos(np.clip(q/mag, -1, 1)))) if mag > 1e-12 else None
    return dict(result, Q=q, magnitude_ratio=mag, field_error_E=error, angle_deg=angle,
                pass_gate=bool(error <= .2 and .8 <= mag <= 1.2 and angle is not None and angle <= 15))


def candidate_cases():
    cases = []
    for polarity, offset in [('ON', 1), ('OFF', 0)]:
        for angle in [120, 300]:
            cases.append(dict(id=f'{polarity}{angle}_base', group='short', polarity=polarity, angle=angle,
                              sample=(angle//30)*2+offset, variant='base', steps=485))
        cases.append(dict(id=f'{polarity}120_speed_new', group='short', polarity=polarity, angle=120,
                          sample=8+offset, variant='speed', speed_factor=1.5 if polarity == 'ON' else .5, steps=485))
        for position in ['upper', 'lower']:
            cases.append(dict(id=f'{polarity}120_local_{position}', group='short', polarity=polarity, angle=120,
                              sample=8+offset, variant='local_'+position, steps=485))
    for angle, speed in [(120, 12), (30, 18)]:
        cases.append(dict(id=f'GRATING{angle}_switch10s', group='long', angle=angle,
                          speed=speed, wavelength=12, contrast=.35, steps=2000))
    cases.append(dict(id='GRAY10s', group='gray', steps=2000))
    for c in cases:
        if c['group'] == 'short':
            c['windows'] = dict(primary=[200, 286], allpost=[200, 485])
        elif c['group'] == 'long':
            c['windows'] = dict(allpost=[200, 2000], forward=[240, 600], hold1=[640, 800],
                                reverse=[840, 1200], hold2=[1240, 1400], slow=[1440, 1800], hold3=[1840, 2000])
        else: c['windows'] = dict(after_adaptation=[200, 2000], late=[1000, 2000])
    assert len(cases) == 13
    return cases


def inputs(case, raw, uv):
    n = case['steps']; t = np.arange(n)*DT
    x = np.sqrt(3)/2*uv[1]; y = -(uv[0]+uv[1]/2)
    if case['group'] == 'gray': return np.full((n, 721), .5, np.float32)
    if case['group'] == 'short':
        value = np.array(raw[case['sample'], :, 0], copy=True)
        if case['variant'] == 'speed':
            indices = 200 + np.minimum(np.floor(np.arange(285)*case['speed_factor']).astype(int), 284)
            value[200:] = value[indices]
        elif case['variant'].startswith('local_'):
            cy = 5 if case['variant'] == 'local_upper' else -5
            aperture = .5*(1+np.tanh(3*(5-np.sqrt(x*x+(y-cy)**2))))
            value = .5 + aperture[None]*(value-.5)
        return value.astype(np.float32)
    velocity = np.zeros(n)
    velocity[(t >= 1) & (t < 3)] = case['speed']
    velocity[(t >= 4) & (t < 6)] = -case['speed']
    velocity[(t >= 7) & (t < 9)] = .5*case['speed']
    # phase is advanced from previous input interval, exactly constant in holds.
    phase = np.concatenate([[0.], np.cumsum(velocity[:-1])*DT])
    angle = np.deg2rad(case['angle']); projection = x*np.cos(angle)+y*np.sin(angle)
    amplitude = np.clip((t-1)/.1, 0, 1)
    return (.5+case['contrast']*amplitude[:, None]*np.sin(2*np.pi*(projection[None]-phase[:, None])/case['wavelength'])).astype(np.float32)


def epoch_scores(case, h_ref, h_value, f_ref, f_value, roi):
    scores = {}
    h_baseline = h_ref[160:200].astype(np.float64).mean(0)
    for name, (start, stop) in case['windows'].items():
        delta = h_value[start:stop].astype(np.float64)-h_ref[start:stop]
        if case['group'] == 'gray': continue
        energy = float(np.sum((h_ref[start:stop].astype(np.float64)-h_baseline)**2))
        response_rms = float(np.sqrt(energy / delta.size))
        relative = float(np.sqrt(np.sum(delta*delta)/energy)) if energy > 0 else None
        flow = vector_metrics(f_ref, f_value, roi, slice(start, stop))
        scores[name] = dict(H_response_relative_L2=relative, H_reference_response_rms=response_rms, flow=flow,
            pass_gate=bool(response_rms >= 1e-6 and relative is not None and relative <= .2 and flow['pass_gate']))
    return scores

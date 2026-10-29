"""CPU readouts of original decoder vectors; B owns scientific thresholds."""
import importlib.util
from pathlib import Path

import numpy as np
from service import HERE, host_path, load_json, sha


def stimulus_direction(angle_deg):
    """Official moving-bar positive rotation -> x right, y up."""
    theta = np.deg2rad(float(angle_deg))
    if not np.isfinite(theta):
        raise ValueError('FINITE_DIRECTION_REQUIRED')
    return np.array([np.cos(theta), np.sin(theta)], dtype=np.float64)


def official_loss_equivalents(estimate, reference):
    """Exact NumPy formulas of objectives.l2norm/epe, with CPU float64 sums.

    If reference is Full/Sham these are model differences, not ground-truth
    accuracy. No label 'Sintel EPE' without independently supplied targets.
    """
    x, y = np.asarray(estimate), np.asarray(reference)
    if x.ndim != 4 or x.shape != y.shape or x.shape[2:] != (2, 721) or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('FINITE_FLOW_B_T_2_721_REQUIRED')
    delta = x.astype(np.float64) - y.astype(np.float64)
    return dict(l2norm_difference=float(np.sqrt(np.sum(delta**2, axis=(1, 2, 3))).mean()),
                mean_endpoint_difference=float(np.sqrt(np.sum(delta**2, axis=2)).mean()),
                component_RMSE=float(np.sqrt(np.mean(delta**2))),
                reference_kind='model_reference_NOT_ground_truth')


def frozen_B_metrics(sham, mode, *, angle_deg, contract_path=HERE / 'READOUT_CONTRACT.json'):
    """Delegate to the unchanged preregistered B metric, fixed ROI/windows.

    B validates Full vs Sham separately. This does not invent new damage tests.
    """
    c = load_json(contract_path)
    pin = c['B_metric_source']
    path = host_path(pin['path'])
    if sha(path) != pin['sha256']:
        raise ValueError('B_PREREGISTERED_METRIC_CHANGED')
    roi_pin = c['fixed_ROI']
    if sha(roi_pin['path']) != roi_pin['sha256']:
        raise ValueError('B_FIXED_ROI_CHANGED')
    roi = np.load(host_path(roi_pin['path']), allow_pickle=False)
    spec = importlib.util.spec_from_file_location('frozen_B_t4t5_metrics', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    direction = stimulus_direction(angle_deg)
    return {name: module.vector_metrics(sham, mode, roi, window=slice(a, b+1), stimulus_unit_vector=direction)
            for name, (a, b) in c['windows'].items() if name != 'pre'}

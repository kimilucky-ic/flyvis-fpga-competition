"""Bounded device benchmarks using unchanged upstream FlyVis and official weights."""
from __future__ import annotations
import argparse
import gc
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument('--device', choices=['cpu', 'cuda'], required=True)
parser.add_argument('--stage', choices=['hexeye', 'flash', 'moving_edge', 'moving_edge_full'], required=True)
parser.add_argument('--threads', type=int, default=1)
parser.add_argument('--repeat', type=int, default=1)
args = parser.parse_args()
WORK = Path(__file__).resolve().parents[1]
BASE = Path('/mnt/c/Users/hzy72/Documents/ChatGPT/fly')
ROOT = Path('/opt/flyvis-gpu-data')
DEST = WORK / 'artifacts' / f'{args.stage}_{args.device}_t{args.threads}_r{args.repeat}'
DEST.mkdir(parents=True, exist_ok=True)
os.environ['CUDA_VISIBLE_DEVICES'] = '0' if args.device == 'cuda' else '-1'
os.environ['FLYVIS_ROOT_DIR'] = str(ROOT)
os.environ['MPLBACKEND'] = 'Agg'
os.environ['MPLCONFIGDIR'] = '/opt/flyvis-gpu-data/matplotlib'
os.environ['NUMBA_CACHE_DIR'] = '/opt/flyvis-gpu-data/numba'
os.environ['TIMEZONE'] = 'Asia/Shanghai'
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'

import numpy as np
import pandas as pd
import torch
torch.set_num_threads(args.threads)
torch.set_num_interop_threads(1)
torch.manual_seed(0)
np.random.seed(0)
# Separate deterministic device comparison from the timing of rendering.
torch.use_deterministic_algorithms(True)
torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False
import flyvis
from flyvis import NetworkView
from flyvis.analysis.stimulus_responses import compute_responses
from flyvis.datasets.datasets import StimulusDataset
from flyvis.datasets.moving_bar import MovingEdge
from flyvis.datasets.rendering import HexEye

assert flyvis.device.type == args.device
if args.device == 'cuda':
    assert torch.cuda.is_available()

def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding='utf-8')

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def sync():
    if args.device == 'cuda':
        torch.cuda.synchronize()

def memory():
    if args.device != 'cuda':
        return {}
    return {'peak_allocated_MiB': torch.cuda.max_memory_allocated() / 2**20,
            'peak_reserved_MiB': torch.cuda.max_memory_reserved() / 2**20}

def timed(fn):
    sync()
    if args.device == 'cuda':
        torch.cuda.reset_peak_memory_stats()
    start = time.perf_counter()
    value = fn()
    sync()
    return value, {'elapsed_s': time.perf_counter() - start, **memory()}

def compare(a, b):
    delta = a.astype(np.float64) - b.astype(np.float64)
    return {'shape_match': a.shape == b.shape, 'bitwise_equal': np.array_equal(a, b),
            'max_abs_error': float(np.max(np.abs(delta))),
            'mean_abs_error': float(np.mean(np.abs(delta))),
            'rmse': float(np.sqrt(np.mean(delta * delta))),
            'allclose_atol_1e-5_rtol_1e-5': bool(np.allclose(a, b, atol=1e-5, rtol=1e-5))}

record = {'stage': args.stage, 'device': str(flyvis.device), 'cpu_threads': args.threads,
          'repeat': args.repeat, 'python': sys.version, 'os': platform.platform(),
          'torch': torch.__version__, 'cuda_runtime': torch.version.cuda,
          'deterministic_algorithms': True, 'tf32': False,
          'flyvis_version': flyvis.__version__,
          'source_commit': subprocess.check_output(['git', '-C', str(BASE / 'upstream/flyvis'), 'rev-parse', 'HEAD'], text=True).strip(),
          'command': [sys.executable, *sys.argv], 'cache_bypassed_for_inference': True}
if args.device == 'cuda':
    record['gpu'] = torch.cuda.get_device_name()
    record['gpu_capability'] = torch.cuda.get_device_capability()
    record['gpu_total_MiB'] = torch.cuda.get_device_properties(0).total_memory / 2**20
print('START', json.dumps(record), flush=True)
def save_failure(kind, value, tb):
    write_json(DEST / 'failure.json', {**record, 'status': 'FAILED',
                                     'error_type': kind.__name__, 'error': str(value), **memory()})
    sys.__excepthook__(kind, value, tb)
sys.excepthook = save_failure

if args.stage == 'hexeye':
    eye, record['construction'] = timed(lambda: HexEye(721, 25))
    print('HEXEYE_CONSTRUCTED', json.dumps(record['construction']), flush=True)
    led_width = np.radians(2.25)
    render_args = dict(bar_width_rad=80 * led_width, bar_height_rad=80 * led_width,
                       n_bars=1, offsets=np.array([-10, 0, 10]) * led_width,
                       bar_intensity=1, bg_intensity=0.5, moving_angle=0,
                       bar_loc_horizontal=np.radians(0))
    rendered, record['render_three_offsets'] = timed(lambda: eye.render_offset_bars(**render_args))
    values = rendered.detach().cpu().numpy()
    np.save(DEST / 'rendered.npy', values)
    record['render_parameters'] = {**render_args, 'offsets': render_args['offsets'].tolist()}
    record['output_shape'] = list(values.shape)
    record['all_finite'] = bool(np.isfinite(values).all())
    for other in ['cpu', 'cuda']:
        other_path = WORK / 'artifacts' / f'hexeye_{other}_t1_r1' / 'rendered.npy'
        if other != args.device and other_path.exists():
            record[f'comparison_to_{other}'] = compare(values, np.load(other_path))
else:
    view = NetworkView(ROOT / 'results/flow/0000/000')
    checkpoint = Path(view.get_checkpoint('best'))
    expected = torch.load(checkpoint, map_location='cpu', weights_only=False)['network']
    record['checkpoint_sha256'] = sha(checkpoint)
    baseline_net = json.loads((BASE / 'artifacts/golden_reference_v1/network.json').read_text())
    assert record['checkpoint_sha256'] == baseline_net['checkpoint_sha256']
    def load_model():
        model = view.network(checkpoint='best', lazy=True)
        model.recover()
        return model
    checkpointed, record['model_initialization'] = timed(load_model)
    network = checkpointed.network
    assert set(network.state_dict()) == set(expected)
    def exact_weights():
        return all(torch.equal(network.state_dict()[key].detach().cpu(), value) for key, value in expected.items())
    assert exact_weights()
    record['weights_exact_before'] = True
    record['n_neurons'] = network.n_nodes
    record['n_connections'] = network.n_edges

    if args.stage == 'flash':
        class SavedFlash(StimulusDataset):
            """Replay the accepted CPU input through the official response API."""
            def init__(self, dt=0.005, t_pre=1.0):
                self.dt, self.t_pre = dt, t_pre
                self.data = np.load(BASE / 'artifacts/golden_reference_v1/flash/stimulus.npy')[:, :, 0]
                self.arg_df = pd.read_csv(BASE / 'artifacts/golden_reference_v1/flash/samples.csv', index_col='sample')
            def __len__(self):
                return len(self.data)
            def __getitem__(self, index):
                return torch.tensor(self.data[index], dtype=torch.float32, device=flyvis.device)
        dataset_class, config = SavedFlash, dict(dt=0.005, t_pre=1.0)
    else:
        # One original edge condition, 21 offsets, official width/height/speed/dt.
        config = dict(offsets=[-10, 11], intensities=[1], speeds=[19], height=80,
                      post_pad_mode='continue', t_pre=1.0, t_post=1.0, dt=0.005, angles=[0])
        if args.stage == 'moving_edge_full':
            config['intensities'] = [0, 1]
            config['angles'] = list(range(0, 360, 30))
        dataset, record['stimulus_first_build'] = timed(lambda: MovingEdge(**config))
        print('EDGE_STIMULUS_BUILT', json.dumps(record['stimulus_first_build']), flush=True)
        dataset_again, record['stimulus_cached_build'] = timed(lambda: MovingEdge(**config))
        del dataset_again
        record['dataset_config'] = config
        dataset_class = MovingEdge
    result, record['inference'] = timed(lambda: compute_responses(checkpointed, dataset_class, config,
                                                                  batch_size=4, t_pre=1.0, t_fade_in=0.0,
                                                                  cell_index='central'))
    activity = result.responses.values[0]
    stimulus = result.stimulus.values
    np.save(DEST / 'activity_central.npy', activity)
    np.save(DEST / 'stimulus.npy', stimulus)
    np.save(DEST / 'cell_types.npy', network.connectome.unique_cell_types[:].astype(str))
    samples = result.coords['sample'].values
    if args.stage.startswith('moving_edge'):
        pd.DataFrame({key: result.coords[key].values for key in ['angle','intensity','speed']}).to_csv(DEST / 'samples.csv',index_label='sample')
        np.save(DEST / 'time.npy', np.arange(activity.shape[1]) * config['dt'] - config['t_pre'])
    record['activity_shape'] = list(activity.shape)
    record['stimulus_shape'] = list(stimulus.shape)
    record['all_finite'] = bool(np.isfinite(activity).all() and np.isfinite(stimulus).all())
    record['weights_exact_after'] = exact_weights()
    assert record['weights_exact_after'] and record['all_finite']
    if args.stage == 'flash':
        ref = BASE / 'artifacts/golden_reference_v1/flash'
        record['activity_vs_cpu_golden'] = compare(activity, np.load(ref / 'activity_central.npy'))
        record['stimulus_vs_cpu_golden'] = compare(stimulus, np.load(ref / 'stimulus.npy'))
        # Use a predeclared numerical acceptance threshold; report exact error too.
        record['numerical_acceptance'] = record['activity_vs_cpu_golden']['allclose_atol_1e-5_rtol_1e-5']
    first = WORK / 'artifacts' / f'{args.stage}_{args.device}_t{args.threads}_r1' / 'activity_central.npy'
    if args.repeat != 1 and first.exists():
        record['activity_vs_first_device_run'] = compare(activity, np.load(first))

record['status'] = 'PASS' if record['all_finite'] and record.get('numerical_acceptance', True) else 'NUMERICAL_MISMATCH'
write_json(DEST / 'result.json', record)
print('RESULT', json.dumps(record), flush=True)
if record['status'] != 'PASS':
    raise SystemExit(2)

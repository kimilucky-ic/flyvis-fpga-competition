"""The accepted WSL model, original dynamics and an auditable runtime identity."""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from camera_pipeline.common import ROOT, sha256
from camera_pipeline.gpu_infer import CHECKPOINT_SHA, SOURCE_COMMIT


class OriginalModel:
    def init__(self):
        self.scratch = Path(tempfile.mkdtemp(prefix='flyvis-camera-phase2-'))
        model_path = self.scratch / 'results/flow/0000/000'
        shutil.copytree('/opt/flyvis-gpu-data/results/flow/0000/000', model_path,
                        ignore=shutil.ignore_patterns('__cache__'))
        os.environ.update(CUDA_VISIBLE_DEVICES='0', FLYVIS_ROOT_DIR=str(self.scratch),
                          MPLBACKEND='Agg', MPLCONFIGDIR=str(ROOT/'runtime/matplotlib_wsl'),
                          NUMBA_CACHE_DIR=str(self.scratch/'numba'), TIMEZONE='Asia/Shanghai',
                          CUBLAS_WORKSPACE_CONFIG=':4096:8')
        import numpy as np
        import torch
        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)
        torch.manual_seed(0)
        np.random.seed(0)
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        import flyvis
        from flyvis import NetworkView
        self.torch = torch
        assert flyvis.device.type == 'cuda'
        commit = subprocess.check_output(['git', '-C', str(ROOT.parent/'upstream/flyvis'),
                                          'rev-parse', 'HEAD'], text=True).strip()
        assert commit == SOURCE_COMMIT, 'Original FlyVis source identity changed'
        view = NetworkView(model_path)
        checkpoint = Path(view.get_checkpoint('best'))
        assert sha256(checkpoint) == CHECKPOINT_SHA
        self.expected = torch.load(checkpoint, map_location='cpu', weights_only=False)['network']
        start = time.perf_counter()
        self.wrapper = view.network(checkpoint='best', lazy=True)
        self.wrapper.recover()
        self.network = self.wrapper.network
        self.network.eval()
        for parameter in self.network.parameters():
            parameter.requires_grad_(False)
        self.sync()
        self.load_s = time.perf_counter()-start
        assert (self.network.n_nodes, self.network.n_edges) == (45669, 1513231)
        assert not self.network._state_hooks, 'Unexpected state observer/modifier'
        self.assert_unchanged()
        self.identity = {
            'model': 'flow/0000/000', 'checkpoint_sha256': CHECKPOINT_SHA,
            'source_commit': SOURCE_COMMIT, 'nodes': self.network.n_nodes,
            'edges': self.network.n_edges,
            'dynamics': type(self.network.dynamics).__module__+'.'+type(self.network.dynamics).__name__,
            'source_indices_sha256': self.tensor_sha(self.network._source_indices),
            'target_indices_sha256': self.tensor_sha(self.network._target_indices),
        }
        self.environment = {'device': 'cuda', 'gpu': torch.cuda.get_device_name(0),
                            'torch': torch.__version__, 'cuda': torch.version.cuda,
                            'flyvis': flyvis.__version__, 'model_load_s': self.load_s,
                            'scratch': str(self.scratch)}

    def tensor_sha(self, tensor):
        value = tensor.detach().cpu().contiguous().numpy()
        digest = hashlib.sha256()
        digest.update(str(value.dtype).encode())
        digest.update(str(value.shape).encode())
        digest.update(value.tobytes())
        return digest.hexdigest()

    def sync(self):
        self.torch.cuda.synchronize()

    def assert_unchanged(self):
        actual = self.network.state_dict()
        assert set(actual) == set(self.expected)
        assert all(self.torch.equal(actual[key].detach().cpu(), value)
                   for key, value in self.expected.items()), 'Weights or network buffers changed'

    def validate_coordinates(self, coordinates):
        import numpy as np
        u = np.array([int(row['u']) for row in coordinates])
        v = np.array([int(row['v']) for row in coordinates])
        for index in self.network.stimulus.input_index:
            np.testing.assert_array_equal(self.network.connectome.nodes.u[:][index], u)
            np.testing.assert_array_equal(self.network.connectome.nodes.v[:][index], v)

    def timed(self, function):
        self.sync()
        start = time.perf_counter()
        value = function()
        self.sync()
        return value, time.perf_counter()-start

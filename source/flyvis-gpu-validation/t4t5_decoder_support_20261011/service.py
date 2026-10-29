"""Small computation/cache adapter. AutoRunner owns scheduling and GPU leases.

Importing this file imports only NumPy, never FlyVis, Torch or CUDA. No queue,
neural rollout, retry, permission issuance, resource lock or board operation.
"""
import hashlib
import json
import os
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def host_path(value):
    s = str(value)
    if os.name != 'nt' and re.match(r'^[A-Za-z]:[/\\]', s):
        s = '/mnt/' + s[0].lower() + '/' + s[3:].replace('\\', '/')
    elif os.name == 'nt' and s.startswith('/mnt/') and len(s) > 7:
        s = s[5].upper() + ':/' + s[7:]
    return Path(s)


def load_json(path):
    return json.loads(host_path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    h = hashlib.sha256()
    with host_path(path).open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def capabilities():
    return dict(schema='flyvis-full-decoder-service/v1', scheduler=False, CUDA_on_import=False,
                methods=['AcceptedReferenceCache.open', 'OfficialDecoderService.decode',
                         'OfficialDecoderService.assert_weights_unchanged'],
                full_step=dict(module='fly/gpu_phase2/full_oracle.py', cls='FullNetworkOracle',
                               method='step(old_full, hex_frame)', owner='existing original Full core'),
                intervention_worker_status='NOT_IMPLEMENTED_IN_THIS_FIRST_DELIVERY',
                new_GPU_execution_status='NOT_RUN', board_status='NOT_CONNECTED')


class AcceptedReferenceCache:
    def init__(self, registry_path=HERE / 'REFERENCE_REGISTRY.json'):
        self.registry = load_json(registry_path)
        self.verified = {}

    def open(self, reference_id, identity, *, fresh_process=False):
        """Exact bound identity or error; read-only array, never fallback compute."""
        if fresh_process:
            raise ValueError('CACHE_CANNOT_SATISFY_FRESH_PROCESS')
        entry = self.registry['references'].get(reference_id)
        if entry is None:
            raise ValueError('CACHE_MISS')
        if identity != entry['identity']:
            raise ValueError('CACHE_IDENTITY_MISMATCH')
        if entry.get('status') != 'ACCEPTED_HISTORICAL_RESULT':
            raise ValueError('UNACCEPTED_CACHE')
        for record in entry['pins']:
            path = host_path(record['path'])
            stamp = (str(path.resolve()), path.stat().st_size, path.stat().st_mtime_ns)
            if self.verified.get(stamp) != record['sha256']:
                if sha(path) != record['sha256']:
                    raise ValueError('CACHE_FILE_CHANGED: ' + str(path))
                self.verified[stamp] = record['sha256']
        a = np.load(host_path(entry['array_path']), mmap_mode='r', allow_pickle=False)
        if list(a.shape) != entry['shape'] or str(a.dtype) != entry['dtype']:
            raise ValueError('CACHE_ARRAY_SCHEMA')
        return a, dict(execution_kind='accepted_cache_replay', actual_new_neural_computation=False,
                       actual_new_decoder_computation=False, PL_execution=False,
                       source_run_id=entry['source_run_id'], cache_identity=entry['identity'],
                       limits=entry['limits'])


def decoder_state_digest(state):
    h = hashlib.sha256()
    for key, tensor in sorted(state.items()):
        a = tensor.detach().cpu().contiguous()
        h.update(key.encode() + b'\0' + str(a.dtype).encode() + b'\0')
        h.update(json.dumps(list(a.shape)).encode() + b'\0')
        h.update(a.numpy().tobytes())
    return h.hexdigest()


class OfficialDecoderService:
    def init__(self, model_path, contract_path, *, device, check_scope):
        """Caller obtains the exclusive GPU lease, configures device, supplies gate.

        check_scope(operation) must RAISE on expiry/identity/resource mismatch.
        This adapter never issues or widens an authorization. CPU is audit-only.
        """
        if not callable(check_scope):
            raise ValueError('RUNNER_SCOPE_CALLBACK_REQUIRED')
        check_scope('decoder_load')  # before importing modules which select CUDA
        self.check_scope = check_scope
        self.contract = load_json(contract_path)
        import torch
        import flyvis
        from flyvis import NetworkView
        self.torch = torch
        self.device = torch.device(device)
        if self.device.type != flyvis.device.type:
            raise ValueError('PROCESS_DEFAULT_DEVICE_MISMATCH_NO_FALLBACK')
        if self.device.type == 'cuda' and self.device.index not in (None, 0):
            raise ValueError('THIS_ADAPTER_SUPPORTS_DEFAULT_CUDA0_ONLY')
        self.view = NetworkView(host_path(model_path))
        checkpoint = Path(self.view.get_checkpoint('best'))
        if sha(checkpoint) != self.contract['model']['checkpoint_sha256']:
            raise ValueError('DECODER_CHECKPOINT_CHANGED')
        source = Path(flyvis.__file__).parent
        for name, pin in self.contract['source_files'].items():
            if sha(source / name) != pin['sha256']:
                raise ValueError('DECODER_SOURCE_CHANGED: ' + name)
        expected = torch.load(checkpoint, map_location='cpu', weights_only=False)['decoder']['flow']
        self.decoder = self.view.init_decoder(checkpoint='best')['flow']
        self.decoder.eval()
        if any(m.training for m in self.decoder.modules()):
            raise ValueError('DECODER_RECURSIVE_EVAL_REQUIRED')
        state = self.decoder.state_dict()
        if set(state) != set(expected) or any(not torch.equal(state[k].detach().cpu(), v) for k, v in expected.items()):
            raise ValueError('DECODER_STATE_DIFFERS_FROM_CHECKPOINT')
        self.before = {k: a.detach().cpu().clone() for k, a in state.items()}
        if decoder_state_digest(state) != self.contract['decoder_state_sha256']:
            raise ValueError('DECODER_STATE_IDENTITY_MISMATCH')
        self.ids = np.asarray(self.decoder.dvs_channels.output_indices, dtype=np.int64)
        self.types = self.view.connectome.output_cell_types[:].astype(str).tolist()
        if self.types != self.contract['ordered_input_types'] or canonical(self.ids.tolist()) != self.contract['input_global_ids_canonical_sha256']:
            raise ValueError('DECODER_INPUT_MAP_MISMATCH')
        self.forward_calls = 0

    def assert_weights_unchanged(self):
        if any(m.training for m in self.decoder.modules()):
            raise ValueError('DECODER_MODE_CHANGED')
        state = self.decoder.state_dict()
        if any(not self.torch.equal(state[k].detach().cpu(), a) for k, a in self.before.items()):
            raise ValueError('DECODER_STATE_MUTATED')
        return True

    def decode(self, activity, *, chunk_frames=32, mask_types=(), mask_start_step=200):
        """[B,T,45669] float32 -> [B,T,2,721]; eval, original forward.

        Serial B=1 chunks; mask is decoder-only positive control on a private
        copy, never mutates network activity. No network H/R update occurs.
        Caller must bind the activity's full scientific identity in its scope.
        """
        if not isinstance(activity, np.ndarray) or activity.dtype != np.float32 or activity.ndim != 3 or activity.shape[-1] != 45669:
            raise ValueError('DECODER_NEEDS_FLOAT32_FULL_SPATIAL_ACTIVITY')
        if not 1 <= chunk_frames <= 32 or activity.shape[0] < 1 or activity.shape[1] < 1:
            raise ValueError('DECODER_CHUNK_SHAPE')
        if not isinstance(mask_start_step, int) or mask_start_step < 0:
            raise ValueError('MASK_TIME_RANGE')
        if len(set(mask_types)) != len(mask_types) or not set(mask_types) <= set(self.types[4:12]):
            raise ValueError('MASK_TYPES_REQUIRE_EXACT_T4_T5')
        if self.device.type != 'cuda':
            raise ValueError('CPU_AUDIT_ONLY_NO_AUTOMATIC_CPU_INFERENCE')
        torch = self.torch
        if not torch.are_deterministic_algorithms_enabled() or torch.backends.cuda.matmul.allow_tf32 or torch.backends.cudnn.allow_tf32:
            raise ValueError('FROZEN_DETERMINISTIC_FP32_PROFILE_REQUIRED')
        self.assert_weights_unchanged()
        mask_ids = self.ids[[self.types.index(t) for t in mask_types]].reshape(-1)
        result = np.empty((*activity.shape[:2], 2, 721), dtype=np.float32)
        with torch.no_grad():
            for b in range(activity.shape[0]):
                for k in range(0, activity.shape[1], chunk_frames):
                    self.check_scope('decoder_chunk')
                    stop = min(k + chunk_frames, activity.shape[1])
                    segment = np.array(activity[b:b+1, k:stop], copy=True, order='C')
                    if not np.isfinite(segment).all():
                        raise ValueError('NONFINITE_ACTIVITY')
                    if mask_ids.size and stop > mask_start_step:
                        segment[:, max(0, mask_start_step-k):, mask_ids] = 0
                    tensor = torch.as_tensor(segment, device=self.device)
                    value = self.decoder(tensor)
                    self.forward_calls += 1
                    actual = value.detach().cpu().numpy()
                    if actual.shape != (1, stop-k, 2, 721) or not np.isfinite(actual).all():
                        raise ValueError('INVALID_DECODER_OUTPUT')
                    self.check_scope('decoder_chunk_complete')
                    result[b:b+1, k:stop] = actual
        self.assert_weights_unchanged()
        return result

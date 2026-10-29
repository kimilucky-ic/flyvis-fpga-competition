"""Persist ALL independent state fields; derived edge gathers are rebuilt by FlyVis.

This adapter is explicitly pinned to the audited original PPNeuronIGRSynapses candidate.
Unknown dynamics/state schemas fail closed. Network state_dict is parameters, NOT the
simulation state; the latter lives in the returned AutoDeref state namespace.
"""
from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
import os

SCHEMA = 'flyvis-camera-complete-network-state-v1'
AUDITED_DYNAMICS = 'flyvis.network.dynamics.PPNeuronIGRSynapses'


def audit_state(state, runtime):
    torch = runtime.torch
    if runtime.identity['dynamics'] != AUDITED_DYNAMICS:
        raise ValueError('Different dynamics requires a new completeness audit')
    independent = {group: dict(state[group].items()) for group in ('nodes', 'edges')}
    if set(independent['nodes']) != {'activity'} or independent['edges']:
        raise ValueError('Unexpected independent state fields; refusing incomplete persistence')
    value = independent['nodes']['activity']
    if not torch.is_tensor(value) or value.shape != (1, 45669) or value.dtype != torch.float32:
        raise ValueError('Expected all 45669 float32 nodes, batch=1')
    if not torch.isfinite(value).all():
        raise ValueError('Nonfinite network state')
    return independent


def save_state(path, state, runtime, *, next_step, input_sha256, coordinates_sha256, dt_s=.005):
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    independent = audit_state(state, runtime)
    payload = {'schema': SCHEMA, 'identity': runtime.identity, 'dt_s': dt_s,
               'next_step': int(next_step), 'state_after_model_time_s': next_step*dt_s,
               'input_sha256': input_sha256, 'coordinates_sha256': coordinates_sha256,
               'independent': {group: {key: value.detach().cpu().clone()
                                      for key, value in fields.items()}
                               for group, fields in independent.items()},
               'derived': 'sources/targets.activity are RefTensor gathers of nodes.activity; reconstructed with original _state_api',
               'warmup_count': 1}
    temporary = path.with_suffix('.tmp')
    runtime.torch.save(payload, temporary)
    os.replace(temporary, path)
    return payload


def validate_payload(payload, runtime, *, next_step, input_sha256, coordinates_sha256, dt_s=.005):
    """Validate identity and all CPU state fields before allocating a CUDA tensor."""
    checks = {'schema': SCHEMA, 'identity': runtime.identity, 'dt_s': dt_s,
              'next_step': next_step, 'input_sha256': input_sha256,
              'coordinates_sha256': coordinates_sha256, 'warmup_count': 1,
              'state_after_model_time_s': next_step*dt_s}
    for key, expected in checks.items():
        if payload.get(key) != expected:
            raise ValueError(f'State resume contract mismatch: {key}')
    independent = payload['independent']
    if set(independent) != {'nodes', 'edges'}:
        raise ValueError('Unexpected independent state namespaces')
    audit_state(independent, runtime)
    return independent


def load_state(path, runtime, *, next_step, input_sha256, coordinates_sha256, dt_s=.005):
    # Only local files produced by this adapter. Never deserialize arbitrary downloaded PT.
    from flyvis.utils.tensor_utils import AutoDeref
    payload = runtime.torch.load(path, map_location='cpu', weights_only=True)
    independent = validate_payload(payload, runtime, next_step=next_step,
                                   input_sha256=input_sha256, coordinates_sha256=coordinates_sha256,
                                   dt_s=dt_s)
    state = AutoDeref(**{group: AutoDeref(**{key: value.to('cuda')
                                            for key, value in fields.items()})
                        for group, fields in independent.items()})
    audit_state(state, runtime)
    if runtime.network._state_hooks:
        raise ValueError('Remove observers before restoring state')
    state = runtime.network._state_api(state)
    # Both full 1,513,231-edge views must point to the restored full node state.
    torch = runtime.torch
    assert torch.equal(state.sources.activity,
                       state.nodes.activity[..., runtime.network._source_indices])
    assert torch.equal(state.targets.activity,
                       state.nodes.activity[..., runtime.network._target_indices])
    return state


@contextmanager
def observe_final_state(runtime):
    if runtime.network._state_hooks:
        raise ValueError('Cannot overlap state hooks')
    holder = {}
    def observe(state):
        audit_state(state, runtime)
        holder['state'] = state
        # Return None: original state/dynamics is never altered by this observer.
    runtime.network.register_state_hook(observe)
    try:
        yield holder
    finally:
        runtime.network.clear_state_hooks()


def simulate_block(runtime, movie, initial_state, dt_s=.005):
    with observe_final_state(runtime) as holder:
        activity = runtime.network.simulate(movie, dt=dt_s, initial_state=initial_state)
    # Official hooks see nodes/edges BEFORE _state_api adds sources/targets.
    # Rebind the derived views after removing the observer, also for in-memory carry.
    final_state = runtime.network._state_api(holder['state'])
    return activity, final_state

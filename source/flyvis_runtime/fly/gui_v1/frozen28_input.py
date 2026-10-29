"""Frozen scientific inputs for the existing joint and full-PL workers.

No camera, neural model, decoder, socket or device is opened here.
"""
import base64
import copy
import hashlib
import time
from functools import lru_cache
import numpy as np
from controlled_stimuli28 import ControlledStimuli28, PACK_SHA, MANIFEST_SHA

KIND = 'controlled_animation'
POLICY = 'FROZEN_STEP_K_TO_INPUT_K_NO_SKIP'


@lru_cache(maxsize=1)
def verified_source():
    return ControlledStimuli28(results_config=False)


class Frozen28Input:
    def init__(self, run, condition, source=None):
        self.source = source or verified_source()
        if condition not in self.source.conditions:
            raise ValueError('SCIENTIFIC_UNKNOWN_CONDITION')
        self.run, self.condition, self.step = run, condition, 0
        # Freeze one selected condition in memory once. No path resolution,
        # conversion, full hashing or disk I/O belongs on its neural STEP path.
        row=self.source.conditions[condition]
        self.source.guard(condition)
        self.values=np.array(row['input'],copy=True)
        self.values.flags.writeable=False
        self.frames=[]
        pixels={}
        for frame in row['frames']:
            name=frame['source_png']
            if name not in pixels:
                path=(self.source.root/name).resolve()
                raw=path.read_bytes()
                if hashlib.sha256(raw).hexdigest()!=self.source.entries[path]['sha256']:
                    raise ValueError('SCIENTIFIC_FROZEN_PIXELS_CHANGED')
                pixels[name]=raw
            self.frames.append(pixels[name])
        self.source.guard(condition)
        self.raw = None
        self.error = None
        self.deadline_ns = None
        self.inputs = self
        import threading
        self.ready = threading.Event()
        self.stats = dict(source_kind=KIND, camera_opened=False)

    def start(self):
        self.ready.set()

    def close(self):
        self.source.assert_unchanged()

    def for_step(self, k):
        if type(k) is not int or not 0 <= k < 485:
            raise ValueError('SCIENTIFIC_STEP_RANGE')
        self.step = k
        return self.freeze_for_step()

    def freeze_for_step(self):
        k = self.step
        row = self.source.conditions[self.condition]
        png = self.frames[k]
        x = self.values[k]
        sha = lambda b: hashlib.sha256(b).hexdigest()
        return dict(png=base64.b64encode(png).decode(), values=x.tolist(),
            source=dict(run_id=self.run, source_kind=KIND, condition_id=self.condition,
                sequence=k, relative_s=k*.005, received_monotonic_ns=time.perf_counter_ns(),
                received_utc=None, timestamp_kind='frozen_model_time_not_capture',
                png_sha256=sha(png), hex_values_sha256=sha(x.tobytes()),
                PACK_sha256=PACK_SHA, input_raw_sha256=row['source']['input_raw_sha256'],
                video_frame=k, video_pts_s=k/50),
            conversion=dict(backend='FROZEN_OFFICIAL_BOXEYE_721',
                PACK_sha256=PACK_SHA, manifest_sha256=MANIFEST_SHA,
                coordinates_sha256=self.source.pack['coordinates']['sha256']))

    def status(self):
        return dict(source_kind=KIND, condition_id=self.condition, policy=POLICY,
                    selected_step=self.step, camera_opened=False, dropped_before_conversion=0,
                    coalesced_before_selection=0, captured=0, held_steps=0)

    def binding(self, backend):
        asset = self.source.pack['initial_state_assets']['original_bias_fp32']
        return dict(PACK_sha256=PACK_SHA, manifest_sha256=MANIFEST_SHA,
            condition_id=self.condition, input_raw_sha256=self.source.conditions[self.condition]['source']['input_raw_sha256'],
            initial_raw_sha256=asset['raw_array_sha256'], steps=485, dt_s=.005,
            numerical_profile='H_A3R1_Q24_R_ORIGINAL_FP32' if backend=='GPU_FPGA' else 'FULL_PL_STRICT_FP32',
            initial_policy='ORIGINAL_BIAS_QUANTIZE_H_ONCE' if backend=='GPU_FPGA' else 'ORIGINAL_BIAS_FP32',
            cross_backend_bitwise_equivalence=False)


def bind_joint_scope(scope, condition):
    """CPU-only admission: freeze selected input/a0 before signing the scope."""
    feed=Frozen28Input(scope['run_id'],condition)
    from hybrid_full485 import Full485Contract
    c=Full485Contract()
    set_initial(c,feed)
    initial,words,_=c.initial()
    from hybrid_a3 import module
    h=module('scientific28_initial_hash',c.paths['h_step'])
    scope.update(source_kind=KIND,condition_id=condition,scientific_input=feed.binding('GPU_FPGA'),
        model=copy.deepcopy(c.registry['model']),
        input_policy=POLICY,initial_full_digest=h.array_hash(initial),initial_H_sha256=hashlib.sha256(words).hexdigest(),
        max_steps=485,run_duration_s=None,capture_duration_s=300,
        human_authorization_reference='USER_FIXED_NOTEBOOK_PREPARE_AND_GUI_START_SCIENTIFIC28')
    return scope


def set_initial(contract, feed):
    asset=feed.source.pack['initial_state_assets']['original_bias_fp32']
    a=np.load(feed.source.root/asset['path'],allow_pickle=False)
    if a.shape!=(45669,) or a.dtype!=np.dtype('<f4') or not np.isfinite(a).all():
        raise ValueError('SCIENTIFIC_INITIAL_SHAPE')
    if hashlib.sha256(a.tobytes()).hexdigest()!=asset['raw_array_sha256']:
        raise ValueError('SCIENTIFIC_INITIAL_IDENTITY')
    a.flags.writeable=False
    contract.raw=a
    # The frozen registry's default a0 is gray-adapted. This run intentionally
    # selects original bias: reflect that in the in-memory run model identity,
    # while preserving the registry file, model weights and frozen ID mapping.
    contract.registry=copy.deepcopy(contract.registry)
    contract.registry['model']['initial_state_sha256']=asset['file_sha256']


def joint_contract(scope):
    from hybrid_full485 import Full485Contract
    c=Full485Contract()
    if scope.get('scientific_input'):
        feed=Frozen28Input(scope['run_id'],scope['condition_id'])
        if scope['scientific_input']!=feed.binding('GPU_FPGA'):
            raise ValueError('SCIENTIFIC_SCOPE_BINDING_CHANGED')
        set_initial(c,feed)
    return c

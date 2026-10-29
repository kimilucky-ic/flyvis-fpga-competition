"""Read-only admission of line10 explanatory metadata for one frozen software run."""
import hashlib
import json
import math
from pathlib import Path
import threading

import numpy as np
from competition_replay import RUN, ACTIVITY_SHA
from scientific_pilot import require
from startup_cache import cached_sha256

EXPLANATION_SHA = '9b31e0902b8cc14187ad7196ebdf75101c78dba64cabf60c8d21482d857811f1'
PAYLOAD = Path(__file__).resolve().parents[1] / 'flyvis-3d-studio/activity_replay_20261014/interpretation_20261017/explanation.json'


def validate(value, replay):
    require(value['schema'] == 'line10.motion_explanation.v1' and value['version'] == '20261017.1', 'Unadmitted explanation schema')
    require(value['run_id'] == RUN and value['activity_sha256'] == ACTIVITY_SHA and
            value['condition'] == 'ON60' and value['mode'] == 'Full', 'Explanation run mismatch')
    require(value['source_steps'] == 485 and value['model_dt_s'] == .005 and value['PL_execution'] is False,
            'Explanation evidence mismatch')
    require(value['definitions']['accuracy_PASS_threshold'] is None and
            value['definitions']['accuracy_percentage'] is None, 'No recognition accuracy threshold is defined')
    roles = value['type_roles']
    require([x['type'] for x in roles] == replay.spatial.data['types'] and
            all(x['reference_is_this_model_measured_tuning'] is False for x in roles), 'Reference roles are not measured tuning')
    frames = value['frames']
    require(len(frames) == 485, 'Explanation missing steps')
    uv = replay.pilot.uv.tolist()
    center = uv.index([0, 0])
    baseline = replay.means[100:200].mean(axis=0, dtype=np.float64)
    for k, row in enumerate(frames):
        require(row['frame_index'] == k and row['input_time_s'] == float(replay.pilot.time[k]) and
                row['activity_time_s'] == float(replay.pilot.activity_time[k]), 'Explanation time mismatch')
        vector = replay.flow[k, :, center].astype(np.float64)
        require(np.array_equal(row['raw_center_vector'], vector), 'Explanation differs from actual official flow')
        moving = 200 <= k <= 284
        expected_phase = 'MOVING_EDGE' if moving else 'PRE_STIMULUS' if k < 200 else 'HELD_FINAL_INPUT'
        require(row['phase'] == expected_phase and row['known_input']['direction_deg'] == (60 if moving else None)
                and row['success_badge'] == 'NOT_DEFINED', 'Explanation phase or GT mismatch')
        raw_available = moving and np.linalg.norm(vector) >= value['definitions']['signal_floor']
        derived_available = moving and np.linalg.norm(row['derived_baseline_subtracted_ROI_mean_vector']) >= value['definitions']['signal_floor']
        require(row['direction_comparison_available'] is bool(derived_available), 'Derived ROI availability mismatch')
        if raw_available:
            angle = math.degrees(math.atan2(vector[1], vector[0])) % 360
            error = abs((angle - 60 + 180) % 360 - 180)
            require(abs(row['raw_center_bearing_deg'] - angle) < 1e-10 and
                    abs(row['raw_center_difference_from_input_deg'] - error) < 1e-10, 'Explanation angle mismatch')
        else:
            require(row['raw_center_bearing_deg'] is None and row['raw_center_difference_from_input_deg'] is None,
                    'No direction judgement outside moving input')
        require([x['type'] for x in row['type_states']] == replay.spatial.data['types'], 'Explanation type order mismatch')
        require(np.array_equal([x['raw_mean'] for x in row['type_states']], replay.means[k]), 'Explanation raw means mismatch')
        require(np.allclose([x['delta_from_fixed_C_baseline'] for x in row['type_states']],
                            replay.means[k] - baseline, rtol=0, atol=1e-12), 'Explanation baseline mismatch')


class CompetitionExplanation:
    def init__(self, replay):
        self.replay = replay
        self.raw = None
        self.checked = {}
        self.lock = threading.Lock()

    def binary(self, run):
        require(run == RUN, 'Explicit explanation run required')
        with self.lock:
            replay = self.replay.get()
            replay.unchanged()
            raw = PAYLOAD.read_bytes()
            require(hashlib.sha256(raw).hexdigest() == EXPLANATION_SHA, 'Explanation SHA256 mismatch')
            if self.raw is None:
                value = json.loads(raw)
                require(len(value['sources']) == 15, 'Explanation source list mismatch')
                for source in value['sources']:
                    path = Path(source['path'])
                    require(cached_sha256(path) == source['sha256'], 'Explanation source SHA256 mismatch')
                    stat = path.stat()
                    self.checked[path] = (stat.st_size, stat.st_mtime_ns)
                validate(value, replay)
                self.raw = raw
            for path, stamp in self.checked.items():
                stat = path.stat()
                require((stat.st_size, stat.st_mtime_ns) == stamp, 'Explanation source changed; revalidate')
            return raw

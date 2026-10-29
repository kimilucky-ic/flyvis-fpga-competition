"""Meaningful negative tests for the causal source/input/output timing contract."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
from camera_pipeline.phase2.gui_handoff import validate_alignment, load_experiment


class TimingContractTests(unittest.TestCase):
    def setUp(self):
        self.source = np.array([0., .014, .033])
        self.input = np.arange(7)*.005
        self.output = self.input+.005
        self.hex = np.stack([np.full(721, value, np.float32) for value in (.1, .7, .3)])
        indices = np.searchsorted(self.source, self.input, side='right')-1
        self.stimulus = self.hex[indices][None, :, None, :]
        self.rows = [{'model_frame': str(i), 'model_time_s': str(t),
                      'source_left_frame': str(source), 'source_right_frame': str(source),
                      'source_left_time_s': str(self.source[source]),
                      'source_right_time_s': str(self.source[source]), 'right_weight': '0.0',
                      'uses_future_frame': 'False'} for i, (t, source) in enumerate(zip(self.input, indices))]

    def validate(self, **replace):
        args = {'source_time': self.source, 'input_time': self.input, 'activity_time': self.output,
                'rows': self.rows, 'source_hex': self.hex, 'stimulus': self.stimulus, 'dt': .005}
        args.update(replace)
        return validate_alignment(**args)

    def test_measured_irregular_source_times(self):
        np.testing.assert_array_equal(self.validate(), [0, 0, 0, 1, 1, 1, 1])

    def test_one_step_early_activity_rejected(self):
        with self.assertRaisesRegex(ValueError, 'AFTER'):
            self.validate(activity_time=self.input)

    def test_legacy_minus_one_axis_rejected(self):
        with self.assertRaisesRegex(ValueError, 'start at zero'):
            self.validate(input_time=self.input-1, activity_time=self.output-1)

    def test_future_source_even_with_false_flag_rejected(self):
        rows = copy.deepcopy(self.rows)
        rows[1]['source_left_frame'] = rows[1]['source_right_frame'] = '1'
        with self.assertRaisesRegex(ValueError, 'alignment at step 1'):
            self.validate(rows=rows)

    def test_actual_values_must_match_zoh(self):
        incorrect = self.stimulus.copy()
        incorrect[0, 1, 0] = self.hex[1]
        with self.assertRaisesRegex(ValueError, 'values'):
            self.validate(stimulus=incorrect)

    def test_after_last_source_rejected(self):
        with self.assertRaisesRegex(ValueError, 'extends past'):
            self.validate(source_time=np.array([0., .014, .029]))


if __name__ == '__main__':
    unittest.main(verbosity=2)

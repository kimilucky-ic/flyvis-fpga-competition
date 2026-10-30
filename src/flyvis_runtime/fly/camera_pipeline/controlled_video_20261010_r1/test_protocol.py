"""Known-CFR endpoint and shared-input contract tests."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import unittest
import numpy as np
from camera_pipeline.controlled_video_20261010_r1.prepare import cfr_zoh


class CFRTests(unittest.TestCase):
    def setUp(self):
        self.values = np.arange(240, dtype=np.float32)[:, None]/239*np.ones((1, 721), np.float32)
        self.time = np.arange(240)/60.

    def test_actual_final_frame_is_held_until_declared_end(self):
        value, grid, rows = cfr_zoh(self.values, self.time)
        self.assertEqual(value.shape, (1, 800, 1, 721))
        self.assertEqual(grid[-1], 3.995)
        self.assertEqual(rows[-1]['source_left_frame'], 239)
        np.testing.assert_array_equal(value[0, -1, 0], self.values[-1])
        self.assertEqual(grid[-1]+.005, 4.)

    def test_every_step_is_causal_actual_zoh(self):
        value, grid, rows = cfr_zoh(self.values, self.time)
        indices = np.searchsorted(self.time, grid, side='right')-1
        np.testing.assert_array_equal(value[0, :, 0], self.values[indices])
        self.assertTrue(all(not row['uses_future_frame'] for row in rows))

    def test_unknown_duration_is_rejected(self):
        with self.assertRaises(ValueError): cfr_zoh(self.values, self.time, duration_s=5.)

    def test_irregular_camera_times_cannot_use_this_file_policy(self):
        time = self.time.copy(); time[10] += .001
        with self.assertRaises(ValueError): cfr_zoh(self.values, time)

    def test_other_dt_rejected_for_frozen_experiment(self):
        with self.assertRaises(ValueError): cfr_zoh(self.values, self.time, dt_s=.01)


if __name__ == '__main__': unittest.main(verbosity=2)

"""Saved scientific arrays only. No device, renderer or inference is started."""
import copy
import hashlib
import json
import unittest
from data_store import DataStore
from scientific_pilot import ScientificPilot
from competition_replay import LazyCompetition, RUN
from competition_explanation import CompetitionExplanation, EXPLANATION_SHA, validate


class ExplanationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = DataStore()
        cls.lazy = LazyCompetition(ScientificPilot(cls.store))
        cls.adapter = CompetitionExplanation(cls.lazy)
        cls.raw = cls.adapter.binary(RUN)
        cls.value = json.loads(cls.raw)
        cls.replay = cls.lazy.get()

    def test_all485_actual_values_clocks_and_sources(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), EXPLANATION_SHA)
        self.assertEqual(len(self.adapter.checked), 15)
        self.assertEqual(len(self.value['frames']), 485)
        self.assertEqual(self.value['frames'][217]['raw_center_bearing_deg'], 68.23349215027797)

    def test_original55_and_optional_failure_isolation(self):
        self.assertEqual(sum(len(x['conditions']) for x in self.store.catalog()['datasets']), 55)
        with self.assertRaises(ValueError):
            CompetitionExplanation(LazyCompetition(None)).binary(RUN)
        self.assertEqual(len(self.store.catalog()['datasets']), 7)

    def test_wrong_run_rejected(self):
        with self.assertRaises(ValueError):
            self.adapter.binary('a-camera-run')

    def test_wrong_clocks_and_raw_flow_rejected(self):
        for fields in ({'activity_time_s': 999}, {'input_time_s': 999}, {'raw_center_vector': [1., 2.]}):
            value = copy.deepcopy(self.value)
            value['frames'][217].update(fields)
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                validate(value, self.replay)

    def test_no_direction_judgement_before_or_after_motion(self):
        for k in (0, 150, 199, 285, 360, 484):
            row = self.value['frames'][k]
            self.assertFalse(row['direction_comparison_available'])
            self.assertIsNone(row['known_input']['direction_deg'])
            self.assertIsNone(row['raw_center_difference_from_input_deg'])
        bad = copy.deepcopy(self.value)
        bad['frames'][360]['known_input']['direction_deg'] = 60
        with self.assertRaises(ValueError):
            validate(bad, self.replay)

    def test_raw_center_and_derived_roi_availability_are_distinct(self):
        row = self.value['frames'][200]
        self.assertFalse(row['direction_comparison_available'])
        self.assertIsNotNone(row['raw_center_bearing_deg'])
        self.assertIsNone(row['derived_bearing_deg'])

    def test_no_fake_pass_or_measured_tuning(self):
        value = copy.deepcopy(self.value)
        value['definitions']['accuracy_PASS_threshold'] = .9
        with self.assertRaises(ValueError):
            validate(value, self.replay)
        value = copy.deepcopy(self.value)
        value['type_roles'][0]['reference_is_this_model_measured_tuning'] = True
        with self.assertRaises(ValueError):
            validate(value, self.replay)

    def test_signed_means_and_delta_are_real(self):
        self.assertLess(self.value['frames'][217]['type_states'][6]['delta_from_fixed_C_baseline'], 0)
        value = copy.deepcopy(self.value)
        value['frames'][217]['type_states'][6]['delta_from_fixed_C_baseline'] *= -1
        with self.assertRaises(ValueError):
            validate(value, self.replay)


if __name__ == '__main__':
    unittest.main(verbosity=2)

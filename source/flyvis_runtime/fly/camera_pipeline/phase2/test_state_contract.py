"""Reject mismatched clocks, topology and incomplete/damaged full-network states."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import torch
from camera_pipeline.common import ROOT
from camera_pipeline.phase2.network_state import validate_payload


class SavedStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = ROOT/'phase2/results/continuous_state_r2'
        cls.payload = torch.load(root/'state_after_000128.pt', map_location='cpu', weights_only=True)
        report = json.loads((root/'state_validation.json').read_text(encoding='utf-8'))
        cls.runtime = SimpleNamespace(torch=torch, identity=report['identity'])
        cls.arguments = {'next_step': 128, 'input_sha256': report['input_sha256'],
                         'coordinates_sha256': report['coordinates_sha256']}

    def check(self, payload=None, **replace):
        arguments = {**self.arguments, **replace}
        return validate_payload(self.payload if payload is None else payload, self.runtime, **arguments)

    def test_actual_saved_full_state(self):
        self.assertEqual(self.check()['nodes']['activity'].shape, (1, 45669))

    def test_wrong_step_rejected(self):
        with self.assertRaisesRegex(ValueError, 'next_step'):
            self.check(next_step=127)

    def test_wrong_input_rejected(self):
        with self.assertRaisesRegex(ValueError, 'input_sha256'):
            self.check(input_sha256='0'*64)

    def test_wrong_coordinates_rejected(self):
        with self.assertRaisesRegex(ValueError, 'coordinates_sha256'):
            self.check(coordinates_sha256='0'*64)

    def test_different_model_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload['identity']['checkpoint_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'identity'):
            self.check(payload)

    def test_wrong_dt_rejected(self):
        with self.assertRaisesRegex(ValueError, 'dt_s'):
            self.check(dt_s=.01)

    def test_missing_namespace_rejected(self):
        payload = copy.deepcopy(self.payload)
        del payload['independent']['edges']
        with self.assertRaisesRegex(ValueError, 'namespaces'):
            self.check(payload)

    def test_unpersisted_new_state_field_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload['independent']['nodes']['adaptation'] = torch.zeros(1, 45669)
        with self.assertRaisesRegex(ValueError, 'fields'):
            self.check(payload)

    def test_truncated_state_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload['independent']['nodes']['activity'] = payload['independent']['nodes']['activity'][:, :65]
        with self.assertRaisesRegex(ValueError, 'all 45669'):
            self.check(payload)

    def test_nonfinite_state_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload['independent']['nodes']['activity'][0, 0] = float('nan')
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            self.check(payload)


if __name__ == '__main__':
    unittest.main(verbosity=2)

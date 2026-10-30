"""Fail-closed checks for wrong condition, time semantics and immutable identity."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from identity import HERE, load_bundle, read_json, sha

class HandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = HERE / 'INPUT_SINGLE_VIDEO_IDENTITY.json'
        cls.reference = read_json(cls.path)

    def reject(self, mutate):
        candidate = copy.deepcopy(self.reference); mutate(candidate)
        with tempfile.TemporaryDirectory(prefix='handoff-negative-', dir=HERE) as directory:
            path = Path(directory) / 'identity.json'
            path.write_text(json.dumps(candidate), encoding='utf-8')
            with self.assertRaises(ValueError):
                load_bundle(path)

    def test_verified_read_only_views_and_endpoint(self):
        bundle = load_bundle(self.path, expected_identity_sha256=sha(self.path))
        self.assertEqual(bundle['x'].shape, (800,721)); self.assertEqual(bundle['a0'].shape, (45669,))
        self.assertFalse(bundle['x'].flags.writeable); self.assertFalse(bundle['a0'].flags.writeable)
        self.assertEqual(bundle['input_time'][-1], 3.995); self.assertEqual(bundle['activity_time'][-1], 4.)

    def test_wrong_condition_rejected(self):
        self.reject(lambda item: item.update(aggregate_sample=2))

    def test_wrong_time_contract_rejected(self):
        self.reject(lambda item: item['time'].update(dt_s=.01))

    def test_wrong_file_fingerprint_rejected(self):
        self.reject(lambda item: item['files']['single_stimulus'].update(sha256='0'*64))

    def test_wrong_actual_slice_tensor_fingerprint_rejected(self):
        self.reject(lambda item: item['input']['x_tensor'].update(c_order_payload_sha256='0'*64))

    def test_wrong_initial_tensor_shape_rejected(self):
        self.reject(lambda item: item['initial_state']['flat_tensor'].update(shape=[45602]))

    def test_wrong_pinned_descriptor_hash_rejected(self):
        with self.assertRaises(ValueError):
            load_bundle(self.path, expected_identity_sha256='0'*64)

if __name__ == '__main__':
    unittest.main(verbosity=2)

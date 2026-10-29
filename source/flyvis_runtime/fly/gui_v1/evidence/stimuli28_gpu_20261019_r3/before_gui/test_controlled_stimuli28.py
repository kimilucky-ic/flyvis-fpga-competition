"""Read-only real-package tests. Never computes neurons/decoder or opens devices."""
import copy
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
from controlled_stimuli28 import ControlledStimuli28,ROOT,PREFIX


class ControlledStimuli28Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.original=ControlledStimuli28()

    def setUp(self):
        self.p=copy.copy(self.original)
        self.p.signatures=dict(self.original.signatures)

    def test_all_conditions_key_steps_have_actual_input_and_no_outputs(self):
        for cid,item in self.p.conditions.items():
            for k in (0,200,400,484):
                with self.subTest(condition=cid,step=k):
                    row=self.p.frame(cid,k)
                    self.assertTrue(np.array_equal(np.asarray(row['input_721'],dtype='<f4'),item['input'][k]))
                    self.assertEqual(hashlib.sha256(item['input'][k].tobytes()).hexdigest(),row['input_step_sha256'])
                    self.assertIsNone(row['flow']);self.assertIsNone(row['neural_state']);self.assertIsNone(row['run_id'])
                    self.assertIsNone(row['direction_prediction']);self.assertEqual(row['all_backends_status'],'NOT_RUN')
                    self.assertEqual(row['video_pts_s'],k/50);self.assertEqual(row['state_time_s'],(k+1)*.005)

    def test_metadata_does_not_bind_an_initial_or_reference(self):
        m=self.p.metadata();self.assertEqual(len(m['conditions']),28)
        self.assertEqual(m['initial_state_binding'],'PENDING_PER_RUN')
        self.assertIsNone(m['model_comparison_id']);self.assertEqual(m['FPGA_status'],'NOT_CONNECTED')
        self.assertIsNone(m['flow']);self.assertEqual(m['preview_duration_s'],9.7)

    def test_step_bounds_and_unknown_condition(self):
        for k in (-1,485,True,'0'):
            with self.assertRaises(ValueError):self.p.frame('BAR_BRIGHT_RIGHT',k)
        with self.assertRaisesRegex(ValueError,'UNKNOWN_CONDITION'):self.p.frame('unknown',0)
        with self.assertRaises(ValueError):self.p.route(PREFIX+'/files/../../PRIVATE_CONFIG.json')

    def test_anchor_mismatch_refuses_source_without_fallback(self):
        with patch('controlled_stimuli28.PACK_SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA256 mismatch'):ControlledStimuli28()

    def test_changed_selected_file_revokes_frame(self):
        path=self.p.conditions['BAR_BRIGHT_RIGHT']['paths']['input']
        old=self.p.signatures[path];self.p.signatures[path]=(old[0]+1,old[1])
        with self.assertRaisesRegex(ValueError,'SOURCE_CHANGED'):self.p.frame('BAR_BRIGHT_RIGHT',0)

    def test_png_bytes_verified_again_before_display(self):
        original=Path.read_bytes
        def altered(path):return b'CPU_FAULT_NOT_AN_IMAGE' if path.suffix=='.png' else original(path)
        with patch.object(Path,'read_bytes',altered):
            with self.assertRaisesRegex(ValueError,'PNG_CHANGED'):self.p.image('BAR_BRIGHT_RIGHT',200)

    def test_serving_does_not_repeat_full_package_admission(self):
        with patch.object(self.p,'check',side_effect=AssertionError('NO_REHASH_PER_DISPLAY')):
            self.assertEqual(self.p.frame('DOT_CCW',200)['step_id'],200)
            self.assertEqual(self.p.metadata()['status'],'VERIFIED_STIMULUS_ONLY')


if __name__=='__main__':unittest.main()

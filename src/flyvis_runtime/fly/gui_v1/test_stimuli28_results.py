"""Actual saved-GPU data admission, isolation and error withdrawal tests."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

import numpy as np
from controlled_stimuli28 import ControlledStimuli28
from stimuli28_results import Stimuli28Results


class GPUResults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=ControlledStimuli28()
        assert cls.source.results is not None,cls.source.result_error

    def test_all28_actual_activity_flow_and_clock_bindings(self):
        m=self.source.metadata()
        self.assertEqual(m['status'],'VERIFIED_ACTUAL_GPU_OFFLINE_REPLAY')
        for cid,item in self.source.results.conditions.items():
            for k in (0,200,300,400,484):
                with self.subTest(cid=cid,k=k):
                    p=self.source.frame(cid,k);n=p['neural_state']
                    self.assertEqual(n['run_id'],item['run']['run_id'])
                    self.assertEqual(n['input_time_s'],p['input_time_s'])
                    self.assertEqual(n['activity_time_s'],p['state_time_s'])
                    self.assertEqual(len(n['spatial']),5768)
                    self.assertTrue(np.array_equal(np.asarray(p['flow'],dtype='<f4'),item['arrays']['flow'][k]))
                    self.assertEqual(hashlib.sha256(np.asarray(n['spatial'],dtype='<f4').tobytes()).hexdigest(),n['spatial_sha256'])
                    self.assertEqual(n['display_kind'],'OFFLINE_REPLAY')
                    self.assertFalse(n['PL_execution'])

    def test_original_input_only_branch_remains_available(self):
        source=copy.copy(self.source);source.results=None
        self.assertEqual(source.metadata()['status'],'VERIFIED_STIMULUS_ONLY')
        packet=source.frame('DOT_CW',300)
        self.assertIsNone(packet['neural_state']);self.assertIsNone(packet['flow'])
        self.assertIsNone(packet['run_id'])

    def test_changed_result_file_revokes_frame_without_old_data(self):
        reader=copy.copy(self.source.results);reader.signatures=dict(reader.signatures)
        path=reader.root/'conditions/EDGE_ON_RIGHT/flow.npy'
        a=reader.signatures[path];reader.signatures[path]=(a[0]+1,a[1])
        with self.assertRaisesRegex(ValueError,'RESULT_SOURCE_CHANGED'):reader.frame('EDGE_ON_RIGHT',300)

    def test_wrong_manifest_pin_cannot_admit_a_result(self):
        root=Path(__file__).parent/'evidence/stimuli28_gpu_20261019_r3'
        p=root/'BAD_CONFIG_CPU_FIXTURE.json'
        config=json.loads((Path(__file__).parent/'stimuli28_results.json').read_text())
        config['pins']['RESULT_MANIFEST.json']='0'*64
        with p.open('x',encoding='utf-8') as f:json.dump(config,f)
        with self.assertRaisesRegex(ValueError,'SHA256 mismatch'):Stimuli28Results(self.source,p)

    def test_series_actual_raw_means_and_time_match_same_run(self):
        for cid in ('BAR_BRIGHT_RIGHT','EDGE_ON_RIGHT','EDGE_OFF_RIGHT','DOT_CCW'):
            series=self.source.results.series(cid);p=self.source.frame(cid,300)
            self.assertEqual(series['run_id'],p['run_id'])
            self.assertEqual(series['means'][300],p['neural_state']['means'])
            self.assertEqual(hashlib.sha256(np.asarray(series['means'],dtype='<f8').tobytes()).hexdigest(),series['means_sha256'])
            self.assertEqual(series['activity_time_s'][300],(300+1)*.005)


if __name__=='__main__':unittest.main()

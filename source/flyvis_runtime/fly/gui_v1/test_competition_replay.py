"""Bounded data/interface checks only; no new neural or graphics computation."""
import json
from pathlib import Path
import unittest
import numpy as np
from data_store import DataStore, ROOT
from scientific_pilot import ScientificPilot
from competition_replay import CompetitionReplay, LazyCompetition, RUN, ACTIVITY_SHA
from competition_renderer import CompetitionRenderer


class CompetitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store=DataStore();cls.pilot=ScientificPilot(cls.store)
        cls.replay=CompetitionReplay(cls.pilot)

    def test_original_55_conditions(self):
        self.assertEqual(sum(len(d['conditions']) for d in self.store.catalog()['datasets']),55)

    def test_same_3d_source_and_every_mean(self):
        folder=ROOT/'flyvis-3d-studio/activity_replay_20261014'
        model=json.loads((folder/'model.json').read_text(encoding='utf-8'))
        with np.load(folder/model['activity_file']) as z:
            np.testing.assert_array_equal(z['activity'],self.replay.means)
            np.testing.assert_array_equal(z['time'],self.pilot.activity_time)
        for i,o in enumerate(model['objects']):
            self.assertEqual(o['model_node_ids'],self.replay.spatial.ids[i*721:(i+1)*721].tolist())

    def test_input_activity_flow_timing(self):
        np.testing.assert_array_equal(self.pilot.activity_time,self.pilot.time+.005)
        self.assertEqual(self.replay.activity.shape,(485,45669))
        self.assertEqual(self.replay.flow.shape,(485,2,721))
        self.assertEqual(self.replay.inputs.shape,(485,721))

    def test_spatial_global_ids_are_actual_slices(self):
        for k in (0,199,200,240,484):
            np.testing.assert_array_equal(self.replay.values[k],self.replay.activity[k,self.replay.spatial.ids])

    def test_wrong_run_cannot_fetch_array(self):
        with self.assertRaises(ValueError):self.replay.binary('flow','another-ON60')

    def test_optional_missing_package_isolated(self):
        with self.assertRaises(ValueError):LazyCompetition(None).get()
        self.assertEqual(len(self.store.catalog()['datasets']),7)

    def test_bad_render_rejected_before_process_launch(self):
        class Ready:
            def get(s):return self.replay
        renderer=CompetitionRenderer(Ready())
        body=dict(run_id=RUN,activity_sha256=ACTIVITY_SHA,frame_index=240,activity_time_s=float(self.pilot.activity_time[240]),request_id='cpu-protocol',type_filter='all',selected_type='T4a')
        for bad in ({'run_id':'wrong'},{'activity_sha256':'wrong'},{'activity_time_s':99},{'frame_index':485},{'frame_index':True},{'type_filter':'PL'},{'selected_type':'CNN'}):
            with self.assertRaises(ValueError):renderer.render(dict(body,**bad))
        self.assertIsNone(renderer.process)

    def test_explicit_offline_and_no_pl(self):
        m=self.replay.metadata()
        self.assertEqual(m['display_kind'],'OFFLINE_REPLAY')
        self.assertFalse(m['PL_execution'])
        self.assertEqual(m['FPGA_status'],'NOT_CONNECTED')
        self.assertEqual(m['spatial_metadata']['PL_proven_global_ids'],[])


if __name__=='__main__':unittest.main(verbosity=2)

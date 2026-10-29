"""CPU archive admission checks; never constructs a model or device."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from live_protocol import HERE,Registry,load
import static_connectome as cache


class StaticGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=Registry();cls.package=HERE.parent/'upstream/flyvis/flyvis'
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=HERE/'runtime');self.target=Path(self.temp.name)/'flyvis/connectome'
    def tearDown(self):
        self.assertTrue(Path(self.temp.name).resolve().is_relative_to((HERE/'runtime').resolve()));self.temp.cleanup()
    def prepare(self):return cache.prepare_static_connectome(self.registry,self.target,'CPU_TEST_GRAPH',package_root=self.package)
    def test_actual_accepted_static_graph_extracts_exactly_without_neural_state(self):
        data=load(cache.DESCRIPTOR);info=self.prepare()
        self.assertEqual(info['files'],93);self.assertFalse(info['neural_activity_reused'])
        self.assertFalse(info['model_or_checkpoint_object_reused'])
        for name,pin in data['files'].items():self.assertEqual(cache.sha(self.target/name),pin['sha256'])
        self.assertFalse(set(('torch','flyvis','cv2'))&set(sys.modules))
    def test_existing_target_cannot_be_overwritten(self):
        self.target.mkdir(parents=True);(self.target/'keep').write_text('preserve')
        with self.assertRaisesRegex(ValueError,'NOT_FRESH'):self.prepare()
        self.assertEqual((self.target/'keep').read_text(),'preserve')
    def test_modified_descriptor_cannot_be_admitted(self):
        with patch.object(cache,'DESCRIPTOR_SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'DESCRIPTOR_CHANGED'):self.prepare()
        self.assertFalse(self.target.exists())
    def test_other_model_cannot_use_graph(self):
        registry=copy.copy(self.registry);registry.data=copy.deepcopy(registry.data);registry.data['model']['checkpoint_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'CONNECTOME_MODEL'):
            cache.prepare_static_connectome(registry,self.target,'CPU_TEST_GRAPH',package_root=self.package)
    def test_changed_official_source_cannot_use_graph(self):
        original=cache.sha
        with patch.object(cache,'sha',side_effect=lambda p:'0'*64 if Path(p)==self.package/'network/network.py' else original(p)):
            with self.assertRaisesRegex(ValueError,'OFFICIAL_SOURCE'):self.prepare()
        self.assertFalse(self.target.exists())
    def test_archive_or_donor_evidence_change_is_rejected_before_extract(self):
        original=cache.sha
        for changed in ('connectome.zip','verification.json'):
            with patch.object(cache,'sha',side_effect=lambda p:'0'*64 if Path(p).name==changed else original(p)):
                with self.assertRaisesRegex(ValueError,'ARCHIVE_CHANGED|ADMISSION_CHANGED'):self.prepare()
            self.assertFalse(self.target.exists())
    def test_original_loader_must_use_current_prepared_directory(self):
        info=dict(target=str(self.target))
        oracle=SimpleNamespace(net=SimpleNamespace(connectome=SimpleNamespace(path=self.target/'connectomefromavgfilters_0000')))
        cache.confirm_static_connectome(oracle,info)
        self.assertTrue(info['official_loader_used_prepared_directory'])
    def test_other_directory_cannot_be_reported_as_cache_reuse(self):
        oracle=SimpleNamespace(net=SimpleNamespace(connectome=SimpleNamespace(path=self.target/'ConnectomeFromAvgFilters_0001')))
        with self.assertRaisesRegex(ValueError,'DID_NOT_REUSE_COPY'):cache.confirm_static_connectome(oracle,dict(target=str(self.target)))

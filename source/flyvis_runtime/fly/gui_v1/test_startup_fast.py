"""Cache invalidation and lazy lifetime tests; no devices or neural computation."""
import hashlib
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from startup_cache import DigestCache, LazyResource

HERE = Path(__file__).resolve().parent


class StartupTests(unittest.TestCase):
    def setUp(self):
        parent = HERE/'evidence/startup_fast_20261017/test_temp'
        parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root/'source.bin'
        self.path.write_bytes(b'original accepted source')
        self.db = self.root/'cache.json'

    def test_unchanged_hit_survives_process_cache_reload(self):
        a = DigestCache(self.db, True)
        wanted = hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.assertEqual(a.digest(self.path), wanted)
        a.flush()
        b = DigestCache(self.db, True)
        with patch('startup_cache.full_digest', side_effect=AssertionError('Unchanged bytes were reread')):
            self.assertEqual(b.digest(self.path), wanted)
        self.assertEqual(b.hits, 1)

    def test_modified_file_rehashed(self):
        a = DigestCache(self.db, True)
        old = a.digest(self.path)
        self.path.write_bytes(b'changed source')
        self.assertNotEqual(a.digest(self.path), old)
        self.assertEqual(a.misses, 2)

    def test_missing_file_never_uses_saved_digest(self):
        a = DigestCache(self.db, True)
        a.digest(self.path)
        self.path.unlink()
        with self.assertRaises(FileNotFoundError):
            a.digest(self.path)

    def test_replaced_file_identity_invalidates_cache(self):
        a = DigestCache(self.db, True)
        old = a.digest(self.path)
        replacement = self.root/'replacement.bin'
        replacement.write_bytes(b'different accepted bytes')
        replacement.replace(self.path)
        self.assertNotEqual(a.digest(self.path), old)
        self.assertEqual(a.misses, 2)

    def test_corrupt_cache_falls_back_to_full_bytes(self):
        self.db.write_text('{broken', encoding='utf-8')
        a = DigestCache(self.db, True)
        self.assertEqual(a.digest(self.path), hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertEqual(a.misses, 1)

    def test_full_mode_ignores_valid_cache(self):
        a = DigestCache(self.db, True)
        expected = a.digest(self.path)
        a.flush()
        b = DigestCache(self.db, False)
        self.assertEqual(b.digest(self.path), expected)
        self.assertEqual(b.digest(self.path), expected)
        self.assertEqual(b.hits, 0)
        self.assertEqual(b.misses, 2)

    def test_cache_write_error_does_not_block_reader(self):
        a = DigestCache(self.db, True)
        a.digest(self.path)
        with patch('startup_cache.os.replace', side_effect=PermissionError('cache readonly')):
            a.flush()
        self.assertTrue(a.digest(self.path))

    def test_changes_during_hash_rejected(self):
        a = DigestCache(self.db, True)
        def mutate(path):
            path.write_bytes(b'mutated while being checked')
            return '0'*64
        with patch('startup_cache.full_digest', side_effect=mutate), self.assertRaises(ValueError):
            a.digest(self.path)
        self.assertFalse(a.entries)

    def test_lazy_resource_does_not_load_until_used_and_preserves_status(self):
        class Reader:
            def status(self):
                return {'status':'VERIFIED_ORIGINAL_PAYLOAD'}
        calls = []
        value = LazyResource(lambda: calls.append(1) or Reader(), 'fixture')
        self.assertFalse(value.loaded)
        self.assertEqual(value.load_status()['state'], 'not_loaded')
        self.assertFalse(calls)
        self.assertEqual(value.status()['status'], 'VERIFIED_ORIGINAL_PAYLOAD')
        self.assertEqual(len(calls), 1)

    def test_parallel_first_requests_construct_only_once(self):
        calls = []
        resource = LazyResource(lambda: calls.append(1) or {'original':True}, 'fixture')
        results = []
        workers = [threading.Thread(target=lambda: results.append(resource.get())) for _ in range(12)]
        for worker in workers:worker.start()
        for worker in workers:worker.join(2)
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(results), 12)
        self.assertTrue(all(result is results[0] for result in results))

    def test_optional_failure_is_retained_without_retry(self):
        calls = []
        def unavailable():
            calls.append(1)
            raise ValueError('manifest mismatch')
        resource = LazyResource(unavailable, 'fixture')
        self.assertFalse(resource)
        self.assertFalse(resource)
        self.assertIn('manifest mismatch', resource.error)
        self.assertEqual(len(calls), 1)

    def test_lazy_legacy_root_access_does_not_read_datasets(self):
        from data_store import LazyDataStore
        with patch('data_store.DataStore', side_effect=ValueError('fixture data unavailable')) as factory:
            store = LazyDataStore(root=self.root)
            self.assertEqual(store.root, self.root)
            self.assertFalse(store.loaded)
            factory.assert_not_called()
            with self.assertRaises(ValueError):store.catalog()

    def test_single_reference_does_not_load_camera_or_full_library(self):
        from data_store import LazyDataStore
        cfg = self.root/'datasets.json'
        cfg.write_text(json.dumps({'datasets':[{'id':'edge24'}]}), encoding='utf-8')
        source = object()
        with patch('data_store.Dataset', return_value=source) as single, patch('data_store.DataStore', side_effect=AssertionError('Full library loaded')):
            store = LazyDataStore(self.root, config_path=cfg)
            self.assertIs(store.reference_dataset('edge24'), source)
            self.assertIs(store.reference_dataset('edge24'), source)
            self.assertFalse(store.loaded)
            single.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)

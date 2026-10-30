"""Read-only rejection and route checks; no GUI listener/GPU/board launched."""
import io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from joint_replay import JointReplay
from live_protocol import HERE,load,sha,write

class JointReplayGuard(unittest.TestCase):
    def test_missing_explicit_registration_does_not_scan(self):
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as tmp:
            with self.assertRaises(FileNotFoundError):JointReplay(Path(tmp)/'not_registered.json')
    def test_actual_three_step_cannot_be_promoted_to_485(self):
        receipt=HERE/'evidence/joint_live_20261013/JOINT_ACCEPTANCE.json'
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as tmp:
            p=Path(tmp)/'config.json';write(p,dict(acceptance_path=str(receipt),acceptance_sha256=sha(receipt)))
            with self.assertRaisesRegex(ValueError,'FULL485_NOT_ACCEPTED'):JointReplay(p)
    def test_altered_receipt_hash_rejected(self):
        receipt=HERE/'evidence/joint_live_20261013/JOINT_ACCEPTANCE.json'
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as tmp:
            p=Path(tmp)/'config.json';write(p,dict(acceptance_path=str(receipt),acceptance_sha256='0'*64))
            with self.assertRaisesRegex(ValueError,'REPLAY_SHA_CHANGED'):JointReplay(p)
    def test_stopped_worker_cannot_pass_actual_audit(self):
        from verify_hybrid_joint_run import audit
        with self.assertRaisesRegex(ValueError,'PC_NOT_COMPLETED'):
            audit(HERE/'runtime/hybrid_full485_runs/6b97fe302e34421f9c123fd991a8cf10',HERE)
    def test_unmatched_run_cannot_export_arrays(self):
        r=JointReplay.__new__(JointReplay);r.audit={'run_id':'expected'};r.unchanged=lambda:None;r.arrays={}
        with self.assertRaisesRegex(ValueError,'REPLAY_RUN_OR_ARRAY'):r.binary('spatial','other_run')
    def test_upload_without_verified_identity_cannot_write(self):
        r=JointReplay.__new__(JointReplay);r.audit={'run_id':'expected'};r.unchanged=lambda:None
        with self.assertRaisesRegex(ValueError,'WEBM_RUN_OR_FORMAT'):r.save_recording(b'not a video','expected')
    def test_optional_adapter_failure_keeps_legacy_handler(self):
        from server import handler_factory
        from data_store import DataStore
        store=DataStore();self.assertEqual(sum(len(d.conditions) for d in store.datasets.values()),55)
        handler=handler_factory(store);h=handler.__new__(handler);h.path='/api/hybrid/full485'
        observed=[];h.send=lambda data,*a,**kw:observed.append((data,kw))
        with patch('joint_replay.admitted_replay',side_effect=ValueError('TEST_MISSING_RECEIPT')):h.do_GET()
        self.assertEqual(observed[-1][0]['status'],'NOT_AVAILABLE');self.assertEqual(observed[-1][1]['status'],409)
        self.assertEqual(observed[-1][0]['PL_proven_global_ids'],[])
        h.path='/';h.do_GET();self.assertIn(b'jointExperiment',observed[-1][0]);self.assertIn(b'liveCamera',observed[-1][0])

if __name__=='__main__':unittest.main()

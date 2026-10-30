"""Scheduler/interface faults only. No neural oracle, GPU or board operations."""
import copy
import io
import json
import os
import sys
import time
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from autorunner import (Engine, HERE, RunnerError, STAGES, audit, authorize, canonical,
                        load_json, methods, own_path, sha, write_json)

SESSION = "tests_" + uuid.uuid4().hex[:10]
ARTIFACTS = own_path("tests", "artifacts", SESSION)
ARTIFACTS.mkdir(parents=True)
BASE = load_json(HERE / "configs/camera609.fast.json")


class SchedulerTests(unittest.TestCase):
    def config(self, change=None):
        cfg = copy.deepcopy(BASE)
        if change:
            change(cfg)
        path = ARTIFACTS / (self._testMethodName + ".json")
        write_json(path, cfg)
        return path

    def engine(self, change=None, mode=None):
        return Engine(self.config(change), mode)

    def execute(self, engine, **kwargs):
        return engine.execute(run_id=SESSION + "_" + self._testMethodName, **kwargs)

    def failure(self, engine, code, **kwargs):
        with self.assertRaises(RunnerError) as raised:
            self.execute(engine, **kwargs)
        self.assertEqual(raised.exception.code, code)
        failure = load_json(engine.run / "failure.json")
        self.assertEqual(failure["code"], code)
        self.assertEqual(load_json(engine.run / "job.json")["stage"], "FAILED")
        self.assertEqual(load_json(engine.run / "run_summary.json")["status"], "FAILED")
        self.assertFalse((engine.run / "seal.json").exists())
        self.assertTrue(failure["traceback"])
        return failure

    def test_preflight_does_not_import_torch_or_spawn(self):
        with patch("subprocess.Popen", side_effect=AssertionError("GPU subprocess forbidden")):
            result = self.execute(self.engine(), preflight=True)
        self.assertEqual(result["status"], "PASS_PREFLIGHT")
        self.assertEqual(set(r["execution_kind"] for r in result["results"].values()), {"accepted_cache_replay"})
        self.assertNotIn("torch", sys.modules)

    def test_dry_run_fresh_plan_cannot_start_worker(self):
        with patch("subprocess.Popen", side_effect=AssertionError("spawn forbidden")):
            result = self.execute(self.engine(lambda c: c.update(fresh_replacement=True)), dry_run=True)
        self.assertEqual(result["plan"]["PythonReplacement"], "FRESH_REQUIRED")
        self.assertFalse(result["actual_new_computation"])

    def test_real_accepted_cache_numerics_and_stop(self):
        engine = self.engine()
        with patch("subprocess.Popen", side_effect=AssertionError("cache-only spawn forbidden")):
            result = self.execute(engine, cache_only=True)
        self.assertEqual(result["status"], "PASS_FAST_CACHE_REPLAY")
        self.assertEqual(result["comparison"]["metrics"]["full"]["violations"], 0)
        self.assertTrue(result["stopped_at_acceptance"])
        stages = [json.loads(s)["stage"] for s in (engine.run / "events.jsonl").read_text().splitlines()]
        self.assertEqual([s for s in stages if s in STAGES], STAGES)
        self.assertEqual(audit(engine.run)["status"], "PASS_BOUNDED_AUDIT")

    def test_bad_pin_fails_before_cache_or_gpu(self):
        e = self.engine(lambda c: c["pins"]["bundle_manifest"].update(sha256="0" * 64))
        with patch("subprocess.Popen", side_effect=AssertionError("spawn forbidden")):
            failure = self.failure(e, "HASH_MISMATCH", preflight=True)
        self.assertIsNone(failure["last_valid_state"])

    def test_missing_bound_method_fails_at_entry(self):
        source = ARTIFACTS / "bad_bound.py"
        source.write_text("class BoundRService:\n    def step(self,old,frame,*,step_id,run_id,condition_id): pass\n")
        def change(c):
            c["sources"]["bound_r"] = str(source)
            c["pins"]["source_bound_r"] = {"path": str(source), "sha256": sha(source)}
        failure = self.failure(self.engine(change), "API_METHOD", preflight=True)
        self.assertIn("assert_weights_unchanged", failure["message"])

    def test_wrong_r_keyword_signature_fails_at_entry(self):
        source = ARTIFACTS / "bad_r.py"
        source.write_text("class RStepService:\n    def init__(self,parameter_path,identity_path,candidate_path,*,device='cpu'): pass\n    def step(self,old_full,hex_frame): pass\n")
        def change(c):
            c["sources"]["r_only"] = str(source)
            c["pins"]["source_r_only"] = {"path": str(source), "sha256": sha(source)}
        self.failure(self.engine(change), "API_SIGNATURE", preflight=True)

    def test_no_gpu_authorization_fails_with_full_cache_retained(self):
        e = self.engine(lambda c: c.update(fresh_replacement=True))
        with patch("subprocess.Popen", side_effect=AssertionError("authorization should prevent spawn")):
            failure = self.failure(e, "RUN_NOT_AUTHORIZED")
        self.assertEqual(failure["last_valid_state"], "FULL_DONE")
        self.assertIn("FullGPU", load_json(e.run / "run_summary.json")["results"])

    def test_cache_only_refuses_fresh_requirement(self):
        self.failure(self.engine(lambda c: c.update(fresh_replacement=True)), "CACHE_MISS", cache_only=True)

    def test_formal_cannot_be_satisfied_by_cache(self):
        result = self.execute(self.engine(mode="formal"), dry_run=True)
        self.assertEqual(set(result["plan"].values()), {"FRESH_REQUIRED"})
        self.assertEqual(result["results"], {})

    def test_formal_cache_only_has_no_pass(self):
        self.failure(self.engine(mode="formal"), "CACHE_MISS", cache_only=True)

    def test_out_of_scope_board_is_rejected(self):
        self.failure(self.engine(lambda c: c["scope"].update(board=True)), "UNSUPPORTED_SCOPE", preflight=True)

    def test_out_of_scope_steps_are_rejected(self):
        self.failure(self.engine(lambda c: c["scope"].update(steps=800)), "UNSUPPORTED_SCOPE", preflight=True)

    def test_ablation_is_rejected(self):
        self.failure(self.engine(lambda c: c["scope"].update(ablation="BLOCK_T4")), "UNSUPPORTED_SCOPE", preflight=True)

    def test_decoder_without_contract_is_rejected(self):
        self.failure(self.engine(lambda c: c.update(decoder={"enabled": True})), "DECODER_SCOPE", preflight=True)

    def test_write_scope_escape_is_rejected(self):
        with self.assertRaises(RunnerError) as err:
            own_path("..", "other-lane")
        self.assertEqual(err.exception.code, "WRITE_SCOPE")

    def test_no_write_scope_cannot_create_job(self):
        with self.assertRaises(RunnerError) as err:
            self.engine(lambda c: c["scope"].update(writes=False))
        self.assertEqual(err.exception.code, "WRITE_NOT_AUTHORIZED")

    def test_corrupt_cache_is_not_silently_recomputed(self):
        root = ARTIFACTS / "bad_cache"
        root.mkdir()
        baseline = Engine(HERE / "configs/camera609.fast.json")
        source = baseline.path(BASE["accepted"]["FullGPU"]["root"])
        for name in ("result.json", "run_identity.json", "artifact_manifest.json"):
            (root / name).write_bytes((source / name).read_bytes())
        (root / "activities_full.npy").write_bytes(b"CORRUPT")
        def change(c):
            c["accepted"]["FullGPU"]["root"] = str(root)
        with patch("subprocess.Popen", side_effect=AssertionError("no retry/spawn")):
            self.failure(self.engine(change), "CACHE_CORRUPT", cache_only=True)

    def test_unaccepted_result_not_cached(self):
        receipt = ARTIFACTS / "unaccepted.json"
        write_json(receipt, {"status": "PENDING"})
        def change(c):
            c["accepted"]["FullGPU"]["receipt"] = str(receipt)
        self.failure(self.engine(change), "CACHE_MISS", cache_only=True)

    def test_compare_failure_preserves_last_valid_replacement(self):
        with patch("autorunner.quick_compare", side_effect=RunnerError("NUMERICAL_MISMATCH", "scheduler injected failure")):
            failure = self.failure(self.engine(), "NUMERICAL_MISMATCH", cache_only=True)
        self.assertEqual(failure["last_valid_state"], "REPLACEMENT_DONE")

    def test_sealed_summary_tamper_is_detected(self):
        engine = self.engine()
        self.execute(engine, cache_only=True)
        path = engine.run / "run_summary.json"
        summary = load_json(path)
        summary["status"] = "PASS_INVENTED"
        write_json(path, summary)
        with self.assertRaises(RunnerError) as err:
            audit(engine.run)
        self.assertEqual(err.exception.code, "SEAL_MISMATCH")

    def test_existing_job_cannot_be_overwritten(self):
        engine = self.engine()
        self.execute(engine, dry_run=True)
        before = sha(engine.run / "job.json")
        with self.assertRaises(RunnerError) as err:
            self.execute(self.engine(), dry_run=True)
        self.assertEqual(err.exception.code, "RUN_EXISTS")
        self.assertEqual(sha(engine.run / "job.json"), before)

    def ticket(self):
        c = copy.deepcopy(BASE)
        now = datetime.now(timezone.utc)
        c["scope"]["gpu"].update(authorized=True, confirmed_by_user=True, conflict_free=True,
            authorization_reference="SYNTHETIC_UNIT_TEST_NOT_AUTHORIZATION", start=(now - timedelta(seconds=1)).isoformat(),
            end=(now + timedelta(seconds=299)).isoformat(), cache_keys={"PythonReplacement": "test-key"})
        return c, now

    def test_window_expires_at_end_no_new_step(self):
        c, now = self.ticket()
        end = datetime.fromisoformat(c["scope"]["gpu"]["end"])
        with self.assertRaises(RunnerError) as err:
            authorize(c, "PythonReplacement", "test-key", now=end)
        self.assertEqual(err.exception.code, "SLOT_EXPIRED")

    def test_wrong_cache_key_refuses_scope(self):
        c, now = self.ticket()
        with self.assertRaises(RunnerError) as err:
            authorize(c, "PythonReplacement", "different-key", now=now)
        self.assertEqual(err.exception.code, "GPU_SCOPE")

    def test_board_reservation_refuses_gpu_scope(self):
        c, now = self.ticket()
        c["scope"]["gpu"]["board_resources_reserved"] = True
        with self.assertRaises(RunnerError) as err:
            authorize(c, "PythonReplacement", "test-key", now=now)
        self.assertEqual(err.exception.code, "GPU_SCOPE")

    def test_window_over_ten_minutes_refused(self):
        c, now = self.ticket()
        c["scope"]["gpu"]["end"] = (now + timedelta(seconds=601)).isoformat()
        with self.assertRaises(RunnerError) as err:
            authorize(c, "PythonReplacement", "test-key", now=now)
        self.assertEqual(err.exception.code, "GPU_SCOPE")

    def test_valid_synthetic_scope_is_bounded(self):
        c, now = self.ticket()
        self.assertEqual(authorize(c, "PythonReplacement", "test-key", now=now)["steps"], 609)

    def test_dev_targets_only_phase1_modules(self):
        self.failure(self.engine(lambda c: c.update(affected_modules=["fpga"]), mode="dev"), "DEV_SCOPE", preflight=True)


if __name__ == "__main__":
    start = time.perf_counter()
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SchedulerTests)
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    (ARTIFACTS / "tests.log").write_text(stream.getvalue(), encoding="utf-8")
    report = {"status": "PASS" if result.wasSuccessful() else "FAIL", "tests": result.testsRun,
              "failures": len(result.failures), "errors": len(result.errors), "wall_s": time.perf_counter() - start,
              "GPU_called": False, "PL_execution": False, "torch_imported": "torch" in sys.modules,
              "artifact_directory": str(ARTIFACTS), "session": SESSION}
    write_json(ARTIFACTS / "report.json", report)
    print(stream.getvalue())
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)

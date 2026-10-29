"""CPU-only A/B scheduling and failure tests; GPU queries are always mocked."""
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
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from autorunner import HERE, RunnerError, canonical, load_json, own_path, sha, write_json
import plugin_contract as contract
import plugin_runner as scheduler
import plugin_host

SESSION = "plugins_" + uuid.uuid4().hex[:10]
ARTIFACTS = own_path("tests", "artifacts", SESSION)
ARTIFACTS.mkdir(parents=True)
A = load_json(HERE / "configs/researchA.fast.json")
B = load_json(HERE / "configs/researchB.fast.json")


def scoped(config, key):
    config = copy.deepcopy(config)
    now = datetime.now(timezone.utc)
    config["campaign_id"] = SESSION
    # CPU fault fixtures must remain reusable after real gpu_r1 evidence exists.
    config["output_dir"] = str(contract.path(config["output_dir"]).with_name("cpu_fixture_" + SESSION))
    config["scope"] = {"authorized": True, "confirmed_by_user": True, "conflict_free": True,
        "board_resources_reserved": False, "stage": config["stage"], "identity_key": key,
        "max_attempts": 1, "max_cases": 24 if config["stage"] == "A" else 14,
        "max_steps": 11640 if config["stage"] == "A" else 6790,
        "start": (now - timedelta(seconds=1)).isoformat(), "end": (now + timedelta(seconds=299)).isoformat(),
        "authorization_reference": "SYNTHETIC_CPU_TEST_NO_GPU"}
    return config


class PluginTests(unittest.TestCase):
    def setUp(self):
        self.folder = ARTIFACTS / self._testMethodName
        self.folder.mkdir()

    def error(self, code, action):
        with self.assertRaises(RunnerError) as got:
            action()
        self.assertEqual(got.exception.code, code)

    def config(self, config):
        p = self.folder / "config.json"
        write_json(p, config)
        return p

    def spec_change(self, config, mutate):
        config = copy.deepcopy(config)
        spec = load_json(contract.path(config["spec_path"]))
        mutate(spec)
        spec["identity_id"] = canonical({k: v for k, v in spec.items() if k != "identity_id"})
        p = self.folder / "spec.json"
        write_json(p, spec)
        config.update(spec_path=str(p), spec_sha256=sha(p), identity_id=spec["identity_id"])
        return config

    def test_actual_A_and_B_preflight_no_torch_or_GPU(self):
        with patch("subprocess.Popen", side_effect=AssertionError("No child allowed")):
            for config in (A, B):
                e = scheduler.PluginEngine(self.config(config))
                result = e.execute(preflight=True, run_id=SESSION + "_preflight_" + config["stage"])
                self.assertEqual(result["status"], "PASS_PREFLIGHT")
                self.assertFalse(result["actual_new_computation"])
        self.assertNotIn("torch", sys.modules)

    def test_dry_run_A_cannot_use_cache_or_spawn(self):
        e = scheduler.PluginEngine(self.config(A))
        with patch("subprocess.Popen", side_effect=AssertionError("No child")), patch.object(scheduler, "cache_read", side_effect=AssertionError("A fresh")):
            result = e.execute(dry_run=True, run_id=SESSION + "_dry")
        self.assertEqual(result["plan"], "FRESH_REQUIRED")

    def test_unauthorized_actual_attempt_preserves_failure(self):
        e = scheduler.PluginEngine(self.config(A))
        with patch("subprocess.Popen", side_effect=AssertionError("No child")):
            self.error("RUN_NOT_AUTHORIZED", lambda: e.execute(run_id=SESSION + "_refusal"))
        failure = load_json(e.run / "failure.json")
        self.assertTrue(failure["traceback"])
        self.assertEqual(failure["last_valid_state"], "PREFLIGHT_DONE")
        self.assertFalse((e.run / "plugin_seal.json").exists())

    def test_cache_only_cannot_satisfy_fresh_A(self):
        e = scheduler.PluginEngine(self.config(A))
        self.error("CACHE_MISS_OR_FRESH_REQUIRED", lambda: e.execute(cache_only=True, run_id=SESSION + "_freshcache"))

    def test_identity_tamper_rejected(self):
        config = copy.deepcopy(A)
        config["identity_id"] = "0" * 64
        self.error("IDENTITY", lambda: contract.validate(config))

    def test_preregister_file_tamper_rejected(self):
        config = copy.deepcopy(A)
        config["spec_sha256"] = "0" * 64
        self.error("SPEC_CHANGED", lambda: contract.validate(config))

    def test_extra_case_budget_rejected(self):
        config = self.spec_change(A, lambda s: s["cases"].append(s["cases"][0]))
        self.error("CASE_BUDGET", lambda: contract.validate(config))

    def test_no_third_scientific_task(self):
        config = copy.deepcopy(A)
        config["stage"] = "C"
        self.error("PLUGIN_SCHEMA", lambda: contract.validate(config))

    def test_A_fresh_false_rejected(self):
        config = copy.deepcopy(A)
        config["fresh_run"] = False
        self.error("FRESH_CONFIRMATION_REQUIRED", lambda: contract.validate(config))

    def test_B_endpoint_reordering_rejected(self):
        config = self.spec_change(B, lambda s: s["cases"].reverse())
        self.error("ENDPOINT_ORDER", lambda: contract.validate(config))

    def test_function_signature_rejected_before_import(self):
        module = self.folder / "wrong_api.py"
        module.write_text("def preflight(spec_path): pass\ndef run_experiment(spec_path, output_path): pass\n")
        def change(spec):
            spec["computational_module"] = str(module)
            spec["source_pins"][str(module)] = sha(module)
        config = self.spec_change(A, change)
        self.error("API_SIGNATURE", lambda: contract.validate(config))

    def test_source_changes_rejected(self):
        def change(spec):
            spec["source_pins"][spec["computational_module"]] = "0" * 64
        self.error("SOURCE_CHANGED", lambda: contract.validate(self.spec_change(A, change)))

    def test_old_camera_scope_cannot_authorize_science(self):
        config = copy.deepcopy(A)
        config["scope"] = load_json(HERE / "configs/camera609.after_b.authorized.json")["scope"]["gpu"]
        self.error("GPU_SCOPE", lambda: contract.authorize(config, "science_key"))

    def test_expired_scope_refuses_start(self):
        config = scoped(A, "key")
        config["scope"]["start"] = "2020-01-01T00:00:00+00:00"
        config["scope"]["end"] = "2020-01-01T00:05:00+00:00"
        self.error("SLOT_EXPIRED", lambda: contract.authorize(config, "key"))

    def test_wrong_cache_key_cannot_authorize(self):
        self.error("GPU_SCOPE", lambda: contract.authorize(scoped(A, "key"), "different"))

    def test_B_requires_A_seal(self):
        config = copy.deepcopy(B)
        config["predecessor"]["run_id"] = SESSION + "_nonexistent_A"
        self.error("A_NOT_SEALED", lambda: contract.predecessor(config))

    def test_existing_run_id_never_retries(self):
        e = scheduler.PluginEngine(self.config(A))
        run_id = SESSION + "_once"
        e.execute(preflight=True, run_id=run_id)
        self.error("RUN_ID_EXISTS", lambda: e.execute(preflight=True, run_id=run_id))

    def test_child_failure_retains_launch_stdout_stderr(self):
        key = contract.validate(A)[1]
        config = scoped(A, key)
        e = scheduler.PluginEngine(self.config(config))
        child = SimpleNamespace(poll=lambda: 7, returncode=7)
        with patch("subprocess.Popen", return_value=child) as launch:
            self.error("PLUGIN_EXIT", lambda: e.execute(run_id=SESSION + "_childfail"))
        self.assertEqual(launch.call_count, 1)
        for name in ("failure.json", "launch.json", "stdout.log", "stderr.log"):
            self.assertTrue((e.run / name).exists())

    def test_parent_timeout_requests_stop_and_quarantines_without_kill(self):
        key = contract.validate(A)[1]
        config = scoped(A, key)
        e = scheduler.PluginEngine(self.config(config))
        e.run = own_path("runs", SESSION + "_timeout")
        e.run.mkdir()
        child = SimpleNamespace(poll=lambda: None, pid=12345)
        clock = iter([0., 1000., 2000., 3000., 4000., 5000.])
        def isolated(*parts):
            return self.folder / "quarantine.json" if parts[:1] == ("runtime",) else own_path(*parts)
        with patch("subprocess.Popen", return_value=child), patch.object(scheduler, "own_path", side_effect=isolated), patch.object(e, "event"), patch.object(scheduler.time, "monotonic", side_effect=lambda: next(clock)):
            self.error("PLUGIN_TIMEOUT_UNCONFIRMED", lambda: e.launch(key))
        self.assertTrue((e.run / "STOP_REQUEST.json").exists())
        self.assertEqual(load_json(self.folder / "quarantine.json")["reason"], "OWNED_PLUGIN_COMPLETION_UNCONFIRMED")

    def test_worker_bad_result_rejected(self):
        write_json(self.folder / "result.json", {"status": "FAILED"})
        write_json(self.folder / "run_identity.json", {})
        self.error("RESULT_CONTRACT", lambda: contract.fast_check(load_json(contract.path(A["spec_path"])), self.folder))

    def test_cache_corruption_fails_without_recompute(self):
        key = SESSION + "_badcache"
        job = own_path("runs", key)
        job.mkdir()
        evidence = job / "result.json"
        write_json(evidence, {"status": "PASS"})
        write_json(job / "plugin_seal.json", {"identity_key": key, "essential_sha256": {str(evidence): "0" * 64}, "raw_file_stamps": {}})
        write_json(own_path("cache", "science", key + ".json"), {"run_id": key})
        self.error("CACHE_CORRUPT", lambda: scheduler.cache_read(key))

    def test_raw_stamp_corruption_fails(self):
        key = SESSION + "_stampcache"
        job = own_path("runs", key)
        job.mkdir()
        raw = job / "raw.bin"
        raw.write_bytes(b"abc")
        write_json(job / "plugin_seal.json", {"identity_key": key, "essential_sha256": {}, "raw_file_stamps": {str(raw): [0, 0]}})
        write_json(own_path("cache", "science", key + ".json"), {"run_id": key})
        self.error("CACHE_CORRUPT", lambda: scheduler.cache_read(key))

    def test_successful_sealed_cache_replay_without_child(self):
        config = copy.deepcopy(B)
        config["fresh_run"] = False
        spec, key = contract.validate(config)
        job = own_path("runs", SESSION + "_acceptedcache")
        job.mkdir()
        result = {"status": "PASS_FAST_ACTUAL_SCIENCE", "identity_key": key, "run_id": job.name, "output_dir": config["output_dir"]}
        write_json(job / "run_summary.json", result)
        write_json(job / "plugin_seal.json", {"identity_key": key,
            "essential_sha256": {str(job / "run_summary.json"): sha(job / "run_summary.json")}, "raw_file_stamps": {}})
        # Isolate the test cache index; never replace a real science cache.
        def isolated(*parts):
            return self.folder / "index.json" if parts[:2] == ("cache", "science") else own_path(*parts)
        write_json(self.folder / "index.json", {"run_id": job.name})
        with patch.object(scheduler, "own_path", side_effect=isolated), patch.object(scheduler, "predecessor", return_value={}), patch("subprocess.Popen", side_effect=AssertionError("No child")):
            e = scheduler.PluginEngine(self.config(config))
            value = e.execute(cache_only=True, run_id=SESSION + "_cacheconsumer")
        self.assertEqual(value["status"], "PASS_FAST_CACHE_REPLAY")
        self.assertEqual(value["new_GPU_invocations"], 0)


@unittest.skipIf(os.name == "nt", "Actual flock tested under WSL")
class ResourceTests(unittest.TestCase):
    def setUp(self):
        self.root = ARTIFACTS / self._testMethodName
        self.root.mkdir()
        self.job = own_path("runs", SESSION + "_" + self._testMethodName)
        self.job.mkdir()
        self.config = scoped(A, "key")
        self.config["queue_s"] = 0
        self.ticket = {"job_dir": str(self.job), "config": self.config, "identity_key": "key"}
        self.lease = contract.Lease(self.ticket)
        def isolated(*parts):
            p = self.root.joinpath(*parts)
            p.parent.mkdir(parents=True, exist_ok=True)
            return p
        self.isolated = isolated
        patcher = patch.object(contract, "own_path", side_effect=isolated)
        patcher.start()
        self.addCleanup(patcher.stop)

    def error(self, code, action):
        with self.assertRaises(RunnerError) as got:
            action()
        self.assertEqual(got.exception.code, code)

    def test_real_flock_is_shared_and_never_stolen(self):
        import fcntl
        with self.isolated("runtime", "gpu.lock").open("a+") as other:
            fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with patch("subprocess.run", side_effect=AssertionError("Locked GPU not probed")):
                self.error("GPU_BUSY_TIMEOUT", self.lease.acquire)

    def test_single_attempt_even_when_time_scope_is_renewed(self):
        with patch("subprocess.run", return_value=SimpleNamespace(stdout="")):
            handle, _ = self.lease.acquire()
            handle.close()
            self.config["scope"]["authorization_reference"] += "_renewed"
            self.error("INVOCATION_LIMIT", self.lease.acquire)

    def test_board_marker_blocks_probe(self):
        write_json(self.isolated("runtime", "BOARD_RESERVED.json"), {"test": True})
        with patch("subprocess.run", side_effect=AssertionError("Marker blocks probe")):
            self.error("GPU_BUSY_TIMEOUT", self.lease.acquire)

    def test_unknown_GPU_resource_fails_closed(self):
        with patch("subprocess.run", side_effect=OSError("synthetic probe failure")):
            self.error("GPU_RESOURCE_UNKNOWN", self.lease.acquire)

    def test_busy_GPU_refuses_without_termination(self):
        with patch("subprocess.run", return_value=SimpleNamespace(stdout="1234\n")):
            self.error("GPU_BUSY_TIMEOUT", self.lease.acquire)

    def test_stop_before_commit(self):
        write_json(self.job / "STOP_REQUEST.json", {"test": True})
        self.error("STOP_REQUESTED", lambda: self.lease.check("before_commit"))

    def test_quarantine_blocks_B_after_uncertain_A(self):
        write_json(self.isolated("runtime", "RESOURCE_QUARANTINE.json"), {"test": True})
        self.error("RESOURCE_QUARANTINE", self.lease.check)


if __name__ == "__main__":
    start = time.monotonic()
    log = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    (ARTIFACTS / "tests.log").write_text(log.getvalue(), encoding="utf-8")
    report = {"status": "PASS" if result.wasSuccessful() else "FAIL", "tests": result.testsRun,
              "skipped": len(result.skipped), "failures": len(result.failures), "errors": len(result.errors),
              "wall_s": time.monotonic() - start, "GPU_called": False, "GPU_queries_mocked": True,
              "torch_imported": "torch" in sys.modules, "PL_execution": False, "artifacts": str(ARTIFACTS)}
    write_json(ARTIFACTS / "report.json", report)
    print(log.getvalue())
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)

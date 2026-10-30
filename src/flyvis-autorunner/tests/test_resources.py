"""Actual local flock semantics with mocked GPU resource probe. Linux/WSL only."""
import copy
import fcntl
import io
import json
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
import worker
from autorunner import HERE, RunnerError, load_json, write_json

SESSION = "resources_" + uuid.uuid4().hex[:10]
ARTIFACTS = HERE / "tests/artifacts" / SESSION
ARTIFACTS.mkdir(parents=True)


class ResourceTests(unittest.TestCase):
    def setUp(self):
        self.root = ARTIFACTS / self._testMethodName
        self.root.mkdir()
        self.out = self.root / "job/PythonReplacement"
        self.out.mkdir(parents=True)
        self.config = copy.deepcopy(load_json(HERE / "configs/camera609.fast.json"))
        now = datetime.now(timezone.utc)
        self.config["scope"]["gpu"].update(authorized=True, confirmed_by_user=True, conflict_free=True,
                 start=(now - timedelta(seconds=1)).isoformat(), end=(now + timedelta(seconds=299)).isoformat(),
                 authorization_reference="SYNTHETIC_RESOURCE_TEST_NEVER_COMPUTE", cache_keys={"PythonReplacement": "key"})
        self.config["timeouts"]["queue_s"] = 0
        self.config["runtime"]["busy_markers"] = []
        self.spec = {"config": self.config, "cache_keys": {"PythonReplacement": "key"}}
        self.window = worker.Window(self.spec, "PythonReplacement", self.out)
        def isolated(*parts):
            result = self.root.joinpath(*parts)
            result.parent.mkdir(parents=True, exist_ok=True)
            return result
        self.isolated = isolated
        self.patcher = patch("worker.own_path", side_effect=isolated)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def error(self, code, call):
        with self.assertRaises(RunnerError) as err:
            call()
        self.assertEqual(err.exception.code, code)

    def test_real_flock_busy_is_queued_and_not_stolen(self):
        with self.isolated("runtime", "gpu.lock").open("a+") as other:
            fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with patch("worker.subprocess.run", side_effect=AssertionError("must not query locked GPU")):
                self.error("GPU_BUSY_TIMEOUT", self.window.acquire)
            self.assertEqual(load_json(self.out / "progress.json")["status"], "QUEUED_GPU_BUSY")

    def test_external_board_marker_prevents_gpu_probe(self):
        marker = self.root / "board_reserved.json"
        write_json(marker, {"owner": "synthetic board resource"})
        self.config["runtime"]["busy_markers"] = [str(marker)]
        with patch("worker.subprocess.run", side_effect=AssertionError("marker blocks query")):
            self.error("GPU_BUSY_TIMEOUT", self.window.acquire)

    def test_busy_compute_probe_does_not_interrupt_process(self):
        with patch("worker.subprocess.run", return_value=SimpleNamespace(stdout="12345\n")) as probe:
            self.error("GPU_BUSY_TIMEOUT", self.window.acquire)
        self.assertEqual(probe.call_count, 1)
        self.assertEqual(probe.call_args.args[0][0], "nvidia-smi")

    def test_unknown_gpu_resource_fails_closed(self):
        with patch("worker.subprocess.run", side_effect=OSError("synthetic missing nvidia-smi")):
            self.error("GPU_RESOURCE_UNKNOWN", self.window.acquire)

    def test_single_invocation_ledger_prevents_second_attempt(self):
        with patch("worker.subprocess.run", return_value=SimpleNamespace(stdout="")):
            handle, duration = self.window.acquire()
            self.assertGreaterEqual(duration, 0)
            fcntl.flock(handle, fcntl.LOCK_UN)
            handle.close()
            self.error("INVOCATION_LIMIT", self.window.acquire)

    def test_expired_compute_deadline_refuses_next_step(self):
        self.window.deadline = time.perf_counter() - 1
        self.error("COMPUTE_TIMEOUT", self.window.check)

    def test_cooperative_stop_refuses_next_step(self):
        write_json(self.out.parent / "STOP_REQUEST.json", {"reason": "synthetic stop"})
        self.error("STOP_REQUESTED", self.window.check)

    def test_quarantine_blocks_retry(self):
        write_json(self.isolated("runtime", "RESOURCE_QUARANTINE.json"), {"reason": "synthetic pending GPU"})
        self.error("RESOURCE_QUARANTINE", self.window.check)


if __name__ == "__main__":
    started = time.perf_counter()
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ResourceTests))
    (ARTIFACTS / "tests.log").write_text(log.getvalue())
    report = {"status": "PASS" if result.wasSuccessful() else "FAIL", "tests": result.testsRun,
              "failures": len(result.failures), "errors": len(result.errors), "wall_s": time.perf_counter() - started,
              "GPU_called": False, "GPU_probe_mocked": True, "PL_execution": False,
              "torch_imported": "torch" in sys.modules, "artifact_directory": str(ARTIFACTS)}
    write_json(ARTIFACTS / "report.json", report)
    print(log.getvalue())
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)

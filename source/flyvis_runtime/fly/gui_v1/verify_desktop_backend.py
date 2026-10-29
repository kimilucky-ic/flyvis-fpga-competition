"""Exercise owned backend lifetime and cancellation using real accepted datasets."""
import argparse
import json
from pathlib import Path
import socket
import tempfile
import threading
from urllib.request import urlopen

from data_store import DataStore, ROOT
from desktop_runtime import DesktopBackend, SessionRecord


def listening(port):
    with socket.socket() as client:
        client.settimeout(1)
        return client.connect_ex(("127.0.0.1", port)) == 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "gui_v1/evidence/desktop/backend_lifecycle.json"))
    args = parser.parse_args()
    store = DataStore()
    cases = []
    with tempfile.TemporaryDirectory(prefix="flyvis_desktop_") as temporary:
        def recorder(name):
            return SessionRecord(Path(temporary) / name)

        backend = DesktopBackend(recorder("normal"), lambda: store)
        try:
            url = backend.start()
            assert url.startswith("http://127.0.0.1:") and int(url.rsplit(":", 1)[1]) != 8771
            with urlopen(url + "/api/catalog", timeout=10) as response:
                catalog = json.load(response)
            assert len(catalog["datasets"]) == 7 and sum(len(d["conditions"]) for d in catalog["datasets"]) == 55
            with urlopen(url + "/api/adapters", timeout=10) as response:
                adapters = json.load(response)
            assert adapters["gpu"]["status"] == "not_connected"
            assert all(not mode["available"] for mode in adapters["modes"][1:])
            port = int(url.rsplit(":", 1)[1]); assert listening(port)
        finally:
            backend.close()
        assert not listening(port) and not backend.thread.is_alive()
        backend.close()
        assert backend.start() is None and backend.record.data["phase"] == "closed"
        cases += ["real_7_datasets_55_conditions", "independent_loopback_port", "closed_port_and_HTTP_thread", "repeated_close_and_late_start_safe"]

        entered, release = threading.Event(), threading.Event()
        def slow_validation():
            entered.set()
            assert release.wait(10)
            return store
        cancelled = DesktopBackend(recorder("cancelled"), slow_validation)
        outcome = []
        worker = threading.Thread(target=lambda: outcome.append(cancelled.start()))
        worker.start(); assert entered.wait(5)
        cancelled.close(); release.set(); worker.join(10)
        assert not worker.is_alive() and outcome == [None] and cancelled.url is cancelled.server is None
        assert cancelled.record.data["phase"] == "closed"
        cases.append("window_close_during_validation_cannot_start_late_backend")

        def unavailable():
            raise ValueError("Controlled startup failure for lifecycle validation")
        failed = DesktopBackend(recorder("failed"), unavailable)
        try:
            failed.start(); raise AssertionError("Expected validation failure")
        except ValueError as error:
            assert "Controlled startup failure" in str(error)
        finally:
            failed.close()
        assert failed.url is failed.server is None and failed.record.data["backend_stopped"]
        cases.append("startup_error_leaves_no_HTTP_server")

    report = {"status": "PASS", "cases": cases, "conditions": 55,
              "evidence_level": "real offline backend HTTP and lifecycle/cancellation tests; no model/device operation"}
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("PASS: 55 conditions; owned port/thread shutdown; cancellation and startup failure leave no backend.")


if __name__ == "__main__":
    main()

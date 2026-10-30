"""Independent HTTP/timing/identity acceptance for the fixed six-video import.

No inference, decoding MP4s, preprocessing source data or writing another lane.
Negative fixtures change config/objects in temporary files or test memory only.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from http.server import ThreadingHTTPServer
import io
import json
from pathlib import Path
import tempfile
from threading import Thread
from time import perf_counter
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import numpy as np
from PIL import Image

import controlled_store
from controlled_store import ControlledVideoDataset
from data_store import DataStore, ROOT, TARGETS, read_json
from server import handler_factory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8771")
    parser.add_argument("--output", default=str(ROOT / "gui_v1/evidence/controlled6/import_acceptance.json"))
    args = parser.parse_args()
    started = perf_counter()
    store = DataStore()
    assert not store.errors, store.errors
    d = store.datasets["controlled6"]

    def get(route):
        with urlopen(args.url + route, timeout=20) as response:
            return response.read(), dict(response.headers)

    catalog = json.loads(get("/api/catalog")[0])
    assert len(catalog["datasets"]) == 7 and sum(len(v["conditions"]) for v in catalog["datasets"]) == 55
    descriptor = json.loads(get("/api/datasets/controlled6")[0])
    assert descriptor["dataset_type"] == "controlled_video_flyvis" and descriptor["execution_kind"] == "offline_replay"
    assert descriptor["source_kind"] == "synthetic_controlled_video" and descriptor["source_is_camera"] is False
    video = descriptor["controlled_video"]
    assert video["received_utc"] is video["received_monotonic_ns"] is None and not video["continuous_24s_activity"]
    assert np.array_equal(descriptor["time_s"], d.time) and np.array_equal(descriptor["activity_time_s"], d.activity_time)
    assert d.time[-1] == 3.995 and d.activity_time[-1] == 4. and np.array_equal(d.stimulus[:, :, 0], d.source_hex[:, np.searchsorted(d.source_time, d.time, side="right") - 1])
    samples, frames = [], []
    for s in range(6):
        row = json.loads(get(f"/api/datasets/controlled6/samples/{s}")[0])
        inputs, headers = get(row["stimulus"]["url"])
        activity, output_headers = get(row["activity"]["url"])
        assert inputs == np.asarray(d.stimulus[s, :, 0], dtype="<f8").tobytes() and activity == d.activity[s].astype("<f4").tobytes()
        assert headers["X-Source-SHA256"] == row["source_input_sha256"] == d.hashes["stimulus.npy"]
        assert output_headers["X-Source-SHA256"] == row["source_output_sha256"] == d.hashes["activity_central.npy"]
        assert row["conditions"] == d.conditions[s]
        assert row["comparison_identity"]["common_initial_state_sha256"] == d.descriptor["frozen_common_initial_state_sha256"]
        direction = json.loads(get(f"/api/datasets/controlled6/directions?cell=T4c&sample={s}")[0])
        assert direction["official_metric"] is None and direction["official_peaks"] == []
        assert np.array_equal(direction["time_s"], d.activity_time)
        for trace in direction["traces"]:
            i = trace["sample_id"]
            assert d.conditions[i]["kind"] == d.conditions[s]["kind"] and np.array_equal(trace["activity"], d.activity[i, :, d.cells.index("T4c")])
            assert "angle_deg" not in trace and trace["label"] == d.conditions[i]["title"]
        for source in range(240):
            payload, h = get(f"/api/datasets/controlled6/samples/{s}/frames/{source}.png")
            original = d.frame_paths[s][source]
            assert hashlib.sha256(payload).hexdigest() == h["X-Source-SHA256"] == d.checked[original]
            with Image.open(io.BytesIO(payload)) as received, Image.open(original) as saved:
                assert received.size == (640, 640) and np.array_equal(np.asarray(received), np.asarray(saved))
            frames.append({"sample": s, "source_frame": source, "sha256": h["X-Source-SHA256"]})
        samples.append({"sample": s, "conditions": row["conditions"], "frames": 800, "input_sha256": row["source_input_sha256"], "activity_sha256": row["source_output_sha256"], "comparison_identity": row["comparison_identity"]})
    assert np.array_equal(np.load(d.paths["activity_T4_T5"], allow_pickle=False), d.activity[:, :, [d.cells.index(c) for c in TARGETS]])
    spec = store.integration_config["controlled_video6"]
    rejected = []
    def reject(label, action):
        try:
            action()
        except (ValueError, KeyError, OSError, AssertionError):
            rejected.append(label)
        else:
            raise AssertionError(f"Invalid controlled-video fixture accepted: {label}")
    bad = deepcopy(spec); bad["pins"][bad["descriptor"]] = "0" * 64
    reject("wrong_descriptor_pin", lambda: ControlledVideoDataset(bad, ROOT, store.datasets["edge24"]))
    bad = deepcopy(spec); bad["pins"].pop(bad["reader"])
    reject("missing_reader_pin", lambda: ControlledVideoDataset(bad, ROOT, store.datasets["edge24"]))
    original_json = controlled_store.read_json
    cases = [
        ("claims_camera", "experiment.json", "source_is_camera", True),
        ("fake_axes", "experiment.json", "axes", {}),
        ("wrong_frozen_input", "experiment.json", "frozen_comparison_input_sha256", "0" * 64),
        ("wrong_frozen_initial_state", "experiment.json", "frozen_common_initial_state_sha256", "0" * 64),
        ("failed_job", "job_status.json", "state", "failed"),
        ("continuous_24s_claim", "result.json", "combined_24s_continuous_network_inference", True),
        ("initial_state_not_shared", "result.json", "same_initial_state_for_all_conditions", False),
        ("invented_official_DSI", "analysis.json", "formal_DSI_computed", True),
        ("wrong_temporal_method", "metadata.json", "temporal_method", "linear"),
    ]
    for label, name, field, wrong in cases:
        def altered(path, name=name, field=field, wrong=wrong):
            value = original_json(path)
            if Path(path).name == name:
                value = deepcopy(value); value[field] = wrong
            return value
        with patch.object(controlled_store, "read_json", altered):
            reject(label, lambda: ControlledVideoDataset(spec, ROOT, store.datasets["edge24"]))
    original_load = np.load
    def shifted(path, *a, **kw):
        value = original_load(path, *a, **kw)
        return value + .005 if Path(path).name == "activity_time.npy" else value
    with patch.object(controlled_store.np, "load", shifted):
        reject("shifted_Euler_clock", lambda: ControlledVideoDataset(spec, ROOT, store.datasets["edge24"]))
    frame_path = d.frame_paths[4][239]; signature = d.signatures[frame_path]
    d.signatures[frame_path] = (signature[0], signature[1] - 1)
    reject("changed_verified_source", d.assert_unchanged)
    probe = ThreadingHTTPServer(("127.0.0.1", 0), handler_factory(store))
    worker = Thread(target=probe.serve_forever, daemon=True); worker.start()
    try:
        url = f"http://127.0.0.1:{probe.server_port}"
        with urlopen(url + "/api/catalog") as response:
            fallback = json.load(response)
            assert len(fallback["datasets"]) == 6 and sum(len(v["conditions"]) for v in fallback["datasets"]) == 49
        try:
            urlopen(url + "/api/datasets/controlled6/samples/4/frames/239.png")
            raise AssertionError("Changed source frame was served")
        except HTTPError as error:
            assert error.code == 409
        with urlopen(url + "/api/datasets/camera1/samples/0") as response:
            assert json.load(response)["execution_kind"] == "offline_replay"
    finally:
        probe.shutdown(); probe.server_close(); worker.join(timeout=5)
        d.signatures[frame_path] = signature
    with tempfile.TemporaryDirectory(prefix="flyvis-controlled-rejection-") as temporary:
        config = deepcopy(store.integration_config); config["controlled_video6"]["pins"][spec["descriptor"]] = "0" * 64
        path = Path(temporary) / "integrations.json"; path.write_text(json.dumps(config), encoding="utf-8")
        fallback = DataStore(integrations_path=path)
        assert "controlled6" not in fallback.datasets and len(fallback.datasets) == 6 and sum(len(v.conditions) for v in fallback.datasets.values()) == 49
    for route in ["/api/datasets/controlled6/frames/0.png", "/api/datasets/controlled6/samples/6/frames/0.png", "/api/datasets/controlled6/samples/1/frames/240.png", "/api/datasets/controlled6/files/run_full.py"]:
        try:
            get(route); raise AssertionError("Undefined route accepted")
        except HTTPError as error:
            assert error.code == 404
    try:
        urlopen(Request(args.url + "/api/inference", method="POST", data=b"{}"))
        raise AssertionError("Unavailable GPU executed")
    except HTTPError as error:
        status = json.load(error); assert error.code == 503 and status["status"] == "not_connected" and status["result"] is status["execution_kind"] is None
    report = {"status": "PASS", "checked_utc": datetime.now(timezone.utc).isoformat(), "samples": samples, "all_1440_served_PNGs_pixel_and_hash_exact": True, "source_frames": frames,
              "all_4800_input_activity_steps_bitwise_HTTP_exact": True, "input_after_state_and_file_clocks_exact": True, "shared_frozen_initial_state_identity": True, "independent_conditions_not_24s_trajectory": True,
              "negative_cases_rejected": rejected, "changed_source_409_and_previous_49_preserved": True, "invalid_optional_import_preserves_previous_49": True, "gpu_service": "not_connected", "elapsed_s": perf_counter() - started,
              "evidence_level": "source identity/time checks and GUI HTTP replay; no new GPU job, capture or board operation"}
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"PASS:6 conditions,1440 original frames,4800 exact input/activity steps,{len(rejected)} rejected cases; existing49 preserved.")


if __name__ == "__main__":
    main()

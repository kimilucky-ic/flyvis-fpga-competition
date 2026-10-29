"""Independent read-only import, synchronization, HTTP and rejection acceptance.

Negative fixtures change documents/arrays in test memory only; no camera,
experimental data, activity file or another workstream's source is written.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import io
import json
from http.server import ThreadingHTTPServer
from pathlib import Path
import tempfile
from threading import Thread
from time import perf_counter
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import numpy as np
from PIL import Image

import camera_store
from camera_store import RecordedCameraDataset
from data_store import DataStore, ROOT, TARGETS, read_json, sha256
from server import handler_factory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8771")
    parser.add_argument("--output", default=str(ROOT / "gui_v1/evidence/phase2/import_acceptance.json"))
    args = parser.parse_args()
    started = perf_counter()
    store = DataStore()
    assert not store.errors, store.errors
    d = store.datasets["camera1"]

    def get(path):
        with urlopen(args.url + path, timeout=15) as response:
            return response.read(), dict(response.headers)

    catalog = json.loads(get("/api/catalog")[0])
    assert {"edge24", "flash", "bar", "minimal", "camera1", "bar10"}.issubset({d["id"] for d in catalog["datasets"]})
    served = json.loads(get("/api/datasets/camera1")[0])
    assert served["dataset_type"] == "recorded_camera_flyvis" and served["execution_kind"] == "offline_replay"
    assert served["origin_execution_kind"] == "new_inference" and served["origin_job_id"] == d.identity["job_id"]
    assert np.array_equal(served["time_s"], d.time) and np.array_equal(served["activity_time_s"], d.activity_time)
    assert np.array_equal(served["camera"]["input_source_indices"], d.source_indices)
    sample = json.loads(get("/api/datasets/camera1/samples/0")[0])
    assert get(sample["stimulus"]["url"])[0] == np.asarray(d.stimulus[0, :, 0], dtype="<f8").tobytes()
    assert get(sample["activity"]["url"])[0] == np.asarray(d.activity[0], dtype="<f4").tobytes()
    assert sample["source_input_sha256"] == d.handoff["input_sha256"] and sample["source_output_sha256"] == d.handoff["output_sha256"]

    # Independently decode every actual served PNG and compare the authoritative BGR array.
    # Recompute only input box means for validation; never run/regenerate neural activity.
    max_input_error = 0.
    # Official BoxEye sums 169 nonnegative float32 values then divides by 169.
    # Compare independent float64 means within the forward rounding bound,
    # including gray /255 and the final division; this is not bitwise replay.
    unit_roundoff = np.finfo(np.float32).eps / 2
    box_mean_rounding_bound = float(172 * unit_roundoff / (1 - 172 * unit_roundoff))
    rows = np.array([c["render_row"] for c in d.coordinates])
    columns = np.array([c["render_column"] for c in d.coordinates])
    assert np.array_equal(rows, [int(13 * (c["u"] + c["v"] / 2)) + d.frames.shape[1] // 2 for c in d.coordinates])
    assert np.array_equal(columns, [13 * c["v"] + d.frames.shape[2] // 2 for c in d.coordinates])
    video_records = []
    for index, path in enumerate(d.frame_paths):
        raw, headers = get(f"/api/datasets/camera1/frames/{index}.png")
        assert hashlib.sha256(raw).hexdigest() == headers["X-Source-SHA256"] == d.checked[path]
        image = Image.open(io.BytesIO(raw)).convert("RGB")
        assert np.array_equal(np.asarray(image), d.frames[index, :, :, ::-1])
        gray = np.asarray(image.convert("L"), dtype=np.float64) / 255
        integral = np.pad(gray.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
        y0, y1, x0, x1 = rows - 6, rows + 7, columns - 6, columns + 7
        means = (integral[y1, x1] - integral[y0, x1] - integral[y1, x0] + integral[y0, x0]) / 169
        difference = float(np.max(np.abs(means - d.source_hex[index])))
        max_input_error = max(max_input_error, difference)
        assert difference <= box_mean_rounding_bound, (index, difference)
        video_records.append({"source_frame": index, "sha256": headers["X-Source-SHA256"], "pixels_exact": True})
    independent_indices = np.searchsorted(d.source_time, d.time, side="right") - 1
    assert np.array_equal(independent_indices, d.source_indices)
    assert np.array_equal(d.stimulus[0, :, 0], d.source_hex[independent_indices])
    assert np.array_equal(d.activity_time, d.time + .005)
    assert np.all(d.source_time[independent_indices] <= d.time)
    assert np.array_equal(np.load(d.directory / "activity_T4_T5.npy", allow_pickle=False), d.activity[:, :, [d.cells.index(c) for c in TARGETS]])
    assert [(c["u"], c["v"]) for c in d.coordinates] == [(c["u"], c["v"]) for c in store.datasets["edge24"].coordinates]
    assert json.loads(get("/api/datasets/camera1/directions?cell=T4c&intensity=1")[0])["official_metric"] is None

    bar = store.datasets["bar10"]
    bars = []
    for i in range(10):
        s = json.loads(get(f"/api/datasets/bar10/samples/{i}")[0])
        assert get(s["stimulus"]["url"])[0] == np.asarray(bar.input_array(i), dtype="<f8").tobytes()
        assert get(s["activity"]["url"])[0] == np.asarray(bar.activity[i], dtype="<f4").tobytes()
        assert np.array_equal(s["time_s"], bar.times[i]) and s["conditions"] == bar.conditions[i]
        bars.append({"sample": i, "frames": s["n_frames"], "conditions": s["conditions"], "hashes": bar.sample_hashes[i]})
    assert len(store.datasets["bar"].conditions) == 8 and len(bar.conditions) == 10

    rejected = []
    spec = store.integration_config["camera"]
    def reject(label, action):
        try:
            action()
        except (ValueError, OSError) as error:
            rejected.append({"case": label, "reason": str(error)})
        else:
            raise AssertionError(f"Invalid camera import accepted: {label}")
    bad = deepcopy(spec); bad["pins"][bad["manifest"]] = "0" * 64
    reject("unapproved_manifest_hash", lambda: RecordedCameraDataset(bad, ROOT))
    bad = deepcopy(spec); bad["pins"].pop(bad["manifest"])
    reject("missing_explicit_manifest_pin", lambda: RecordedCameraDataset(bad, ROOT))
    original_json = camera_store.read_json
    for label, filename, field, wrong in [
        ("failed_job", "gpu_status.json", "state", "failed"),
        ("wrong_job_id", "gpu_status.json", "job_id", "another_run"),
        ("wrong_output_identity", "gui_handoff.json", "output_sha256", "0" * 64),
        ("wrong_model_checkpoint", "result.json", "checkpoint_sha256", "0" * 64),
        ("wrong_activity_axes", "result.json", "activity_axes", ["frame", "sample", "cell"]),
        ("wrong_time_file_role", "gui_handoff.json", "input_time", "activity_time.npy"),
        ("missing_acceptance", "acceptance.json", "status", "NOT_RUN"),
        ("unaccepted_resampling", "metadata.json", "temporal_method", "linear"),
    ]:
        def altered_json(path, name=filename, key=field, value=wrong):
            result = original_json(path)
            if Path(path).name == name:
                result = deepcopy(result); result[key] = value
            return result
        with patch.object(camera_store, "read_json", altered_json):
            reject(label, lambda: RecordedCameraDataset(spec, ROOT))
    original_load = np.load
    def shifted_load(path, *a, **kw):
        data = original_load(path, *a, **kw)
        return data + .005 if Path(path).name == "activity_time.npy" else data
    with patch.object(camera_store.np, "load", shifted_load):
        reject("shifted_euler_time", lambda: RecordedCameraDataset(spec, ROOT))
    original_csv = camera_store.read_csv
    def altered_alignment(path):
        rows = original_csv(path)
        if Path(path).name == "time_alignment.csv":
            rows = deepcopy(rows); rows[1]["source_left_frame"] = "1"
        return rows
    with patch.object(camera_store, "read_csv", altered_alignment):
        reject("future_or_wrong_source_frame", lambda: RecordedCameraDataset(spec, ROOT))
    path = d.frame_paths[0]; signature = d.signatures[path]
    d.signatures[path] = (signature[0], signature[1] - 1)
    reject("changed_source_after_verification", d.assert_unchanged)
    degraded = store.catalog()
    assert "camera1" not in [item["id"] for item in degraded["datasets"]]
    assert all(key in [item["id"] for item in degraded["datasets"]] for key in ["edge24", "flash", "bar", "minimal"])
    # Same verified store, then a changed-source signature: the public adapter
    # cannot still advertise an accepted camera import after its data is rejected.
    probe = ThreadingHTTPServer(("127.0.0.1", 0), handler_factory(store))
    worker = Thread(target=probe.serve_forever, daemon=True)
    worker.start()
    probe_url = f"http://127.0.0.1:{probe.server_port}"
    try:
        with urlopen(probe_url + "/api/adapters", timeout=5) as response:
            assert json.load(response)["camera"]["status"] == "unavailable"
        try:
            urlopen(probe_url + "/api/datasets/camera1/samples/0", timeout=5)
            raise AssertionError("Changed camera source was served")
        except HTTPError as error:
            assert error.code == 409
        with urlopen(probe_url + "/api/datasets/edge24/samples/0", timeout=5) as response:
            assert json.load(response)["execution_kind"] == "offline_replay"
    finally:
        probe.shutdown()
        probe.server_close()
        worker.join(timeout=5)
    d.signatures[path] = signature
    with tempfile.TemporaryDirectory(prefix="flyvis-gui-v2-rejection-") as temporary:
        config = deepcopy(store.integration_config);config["camera"]["pins"][config["camera"]["handoff"]] = "0" * 64
        path = Path(temporary) / "integrations.json";path.write_text(json.dumps(config), encoding="utf-8")
        fallback = DataStore(integrations_path=path)
        assert "camera1" not in fallback.datasets and all(k in fallback.datasets for k in ["edge24", "flash", "bar", "minimal"])
        path.write_text('{invalid json', encoding="utf-8")
        fallback = DataStore(integrations_path=path)
        assert all(k in fallback.datasets for k in ["edge24", "flash", "bar", "minimal"])
    for route, method in [("/api/inference", "POST"), ("/api/inference/no_job", "GET"), ("/api/camera/record", "POST"), ("/api/comparison", "POST")]:
        try:
            urlopen(Request(args.url + route, data=b"{}" if method == "POST" else None, method=method))
            raise AssertionError("An unavailable adapter executed")
        except HTTPError as error:
            result = json.loads(error.read())
            assert error.code == 503 and result["status"] == "not_connected" and result["execution_kind"] is None and result["result"] is None
    for route in ["/api/datasets/camera1/frames/177.png", "/api/datasets/camera1/frames/-1.png", "/api/datasets/camera1/files/capture.py", "/api/datasets/bar10/samples/10"]:
        try:
            get(route); raise AssertionError("Invalid route was accepted")
        except HTTPError as error:
            assert error.code == 404
    result = {"status": "PASS", "checked_utc": datetime.now(timezone.utc).isoformat(),
              "evidence_level": "GUI read-only identity/data/timing checks and local HTTP transport; no new inference/capture/board execution",
              "camera": {"manifest_files": len(d.checked), "pins": spec["pins"], "job_id": d.identity["job_id"],
                         "source_sha256": d.handoff["source_sha256"], "input_sha256": d.handoff["input_sha256"], "output_sha256": d.handoff["output_sha256"],
                         "recorded_frames": len(d.frames), "simulation_steps": len(d.time), "all_png_pixels_equal_raw": True,
                         "all_721_source_receptor_means_independently_checked": True, "max_receptor_abs_error": max_input_error,
                         "independent_mean_rounding_bound": box_mean_rounding_bound, "bound_basis": "169 nonnegative float32 convolution sum plus gray normalization and division; float64 box means are not a bitwise FlyVis replay",
                         "all_1202_zoh_steps_exact": True, "euler_after_time_exact": True, "central_and_T4_T5_exact": True,
                         "video_frames": video_records},
              "moving_bar10": bars, "original_eight_condition_bar_preserved": True,
              "negative_cases_rejected": rejected, "camera_config_failure_preserves_offline_startup": True, "camera_source_change_preserves_offline_catalog": True,
              "changed_source_adapter_unavailable_and_data_409_offline_still_200": True,
              "gpu_service": "not_connected", "unavailable_posts_and_poll_503_null": True, "elapsed_s": perf_counter() - started}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"PASS:177 exact camera frames,1202 synchronized input/activity steps,10 independent bar conditions,{len(rejected)} negative identity/timing cases.")


if __name__ == "__main__":
    main()

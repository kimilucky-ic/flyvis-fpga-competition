"""Explicitly pinned, read-only import of accepted recorded-camera results.

Never imports the recorder, FlyVis, OpenCV or GPU code. No directory discovery.
"""
from pathlib import Path
from time import perf_counter

import numpy as np

from data_store import Dataset, TARGETS, numeric_row, read_csv, read_json, sha256


def require(ok, message):
    if not ok:
        raise ValueError(message)


def inside(root, relative):
    path = (root / relative.replace("\\", "/")).resolve()
    require(path.is_relative_to(root.resolve()), "Import path escapes approved root")
    return path


def verify_inventory(root, manifest, prefixes, pins):
    """Verify all files in chosen experiment scopes, not unrelated experiments."""
    checked = {}
    for name, expected in pins.items():
        path = inside(root, name)
        require(sha256(path) == expected, f"Pinned identity mismatch: {name}")
        checked[path] = expected
    raw = read_json(inside(root, manifest))
    entries = raw["files"] if isinstance(raw, dict) else raw
    pairs = ((name, digest, None) for name, digest in entries.items()) if isinstance(entries, dict) else (
        (item["path"], item["sha256"], item["bytes"]) for item in entries)
    for name, expected, size in pairs:
        name = name.replace("\\", "/")
        if not any(name == p or name.startswith(p.rstrip("/") + "/") for p in prefixes):
            continue
        path = inside(root, name)
        require(sha256(path) == expected, f"Manifest mismatch: {name}")
        require(size is None or path.stat().st_size == size, f"Manifest size mismatch: {name}")
        checked[path] = expected
    return checked


class RecordedCameraDataset(Dataset):
    def init__(self, config, root):
        started = perf_counter()
        self.config = config
        self.id = config["id"]
        self.camera_root = inside(root, config["root"])
        self.handoff_path = inside(self.camera_root, config["handoff"])
        self.manifest_path = inside(self.camera_root, config["manifest"])
        require(all(name in config["pins"] for name in ["API_CONTRACT.md", config["handoff"], config["manifest"], config["acceptance"]]), "Missing explicit camera document pin")
        # Pin these documents before trusting any paths or acceptance claims.
        for name, expected in config["pins"].items():
            require(sha256(inside(self.camera_root, name)) == expected, f"Pinned identity mismatch: {name}")
        self.handoff = read_json(self.handoff_path)
        require(self.handoff["schema"] == "flyvis-camera-handoff-v1", "Unknown camera handoff schema")
        require(self.handoff["input_time"] == "time.npy" and self.handoff["activity_time"] == "activity_time.npy", "Handoff time-file contract mismatch")
        require(set(self.handoff["cell_identity_files"]) >= {"cell_types.npy", "neurons.csv"}, "Handoff lacks cell identities")
        self.recording_directory = inside(self.camera_root, self.handoff["recording_directory"])
        self.input_directory = inside(self.camera_root, self.handoff["input_directory"])
        self.directory = inside(self.camera_root, self.handoff["result_directory"])
        self.acceptance_path = inside(self.camera_root, config["acceptance"])
        require(self.acceptance_path == self.handoff_path.parent / self.handoff["acceptance"], "Acceptance path mismatch")
        prefixes = [str(p.relative_to(self.camera_root)).replace("\\", "/") for p in (
            self.recording_directory, self.input_directory, self.directory)]
        self.checked = verify_inventory(self.camera_root, config["manifest"], prefixes, config["pins"])
        self.files = {}
        for path, digest in self.checked.items():
            # Only approved flat identity/data files; PNGs use the bounded frame route.
            if path.parent in [self.directory, self.input_directory, self.recording_directory, self.handoff_path.parent]:
                scope = "result" if path.parent == self.directory else "input" if path.parent == self.input_directory else "recording" if path.parent == self.recording_directory else "validation"
                self.files[f"{scope}.{path.name}"] = (path, digest)

        def covered(path):
            require(path in self.checked, f"File lacks verified manifest coverage: {path.name}")
            return self.checked[path]

        acceptance = read_json(self.acceptance_path)
        self.recording = read_json(self.recording_directory / "recording.json")
        self.metadata = read_json(self.input_directory / "metadata.json")
        self.identity = read_json(self.directory / "result.json")
        status = read_json(self.directory / "gpu_status.json")
        require(acceptance["status"] == "PASS" and self.identity["status"] == "PASS", "Camera acceptance/result is not PASS")
        require(read_json(self.recording_directory / "job_status.json")["state"] == "complete", "Recording is incomplete")
        require(status["state"] == "complete" and status["job_id"] == self.handoff["job_id"] == self.identity["job_id"], "GPU job is incomplete or ID mismatches")
        require(self.recording["source_kind"] == self.metadata["source"]["source_kind"] == "real_windows_camera", "Source is not a real camera recording")
        for key, expected in [("model", config["expected_model"]), ("source_commit", config["expected_source_commit"]), ("checkpoint_sha256", config["expected_checkpoint_sha256"])]:
            require(self.identity[key] == expected, f"Camera model identity mismatch: {key}")
            require(acceptance["GPU_record"][key] == expected, f"Acceptance model mismatch: {key}")
        require(self.identity["weights_exact_before"] and self.identity["weights_exact_after"] and not self.identity["weights_modified"], "Weights changed")
        require(self.metadata["target_model"] == self.identity["model"] and self.metadata["source_commit"] == self.identity["source_commit"] and not self.metadata["model_weights_modified"], "Input target/source identity mismatch")
        require(self.handoff["activity_axes"] == self.identity["activity_axes"] == ["sample", "frame", "central_cell_type"], "Activity axes mismatch")
        require(self.identity["target_types"] == TARGETS, "T4/T5 axis mapping mismatch")
        require(self.identity["network_mode"] == "original full continuous clip; no frame/window resets", "Unsupported camera network mode")
        require(self.identity["initialization"] == "one independent clip, 1 s grey 0.5 once before movie", "Unsupported initialization")
        for directory, inventory in [(self.recording_directory, self.recording["data_sha256"]), (self.input_directory, self.metadata["data_sha256"]), (self.directory, self.identity["data_sha256"])]:
            for name, expected in inventory.items():
                require(covered(directory / name) == expected, f"Identity inventory mismatch: {name}")
        self.hashes = {"stimulus.npy": covered(self.input_directory / "stimulus.npy"),
                       "activity_central.npy": covered(self.directory / "activity_central.npy")}
        require(self.handoff["source_sha256"] == covered(self.recording_directory / "frames.npy"), "Raw recording identity mismatch")
        require(self.handoff["input_sha256"] == self.identity["input_sha256"] == self.hashes["stimulus.npy"], "Input identity mismatch")
        require(self.handoff["output_sha256"] == self.hashes["activity_central.npy"], "Output identity mismatch")
        require(acceptance["GPU_record"]["data_sha256"] == self.identity["data_sha256"], "Accepted output inventory differs")
        require(self.metadata["source"]["data_sha256"] == self.recording["data_sha256"], "Converted input belongs to another recording")
        require(covered(self.input_directory / "source_frame_timestamps.csv") == covered(self.recording_directory / "frame_timestamps.csv"), "Capture timestamp identity mismatch")
        require(covered(self.input_directory / "time_alignment.csv") == covered(self.directory / "time_alignment.csv"), "Activity/input alignment differs")
        self.stimulus = np.load(self.input_directory / "stimulus.npy", allow_pickle=False, mmap_mode="r")
        self.activity = np.load(self.directory / "activity_central.npy", allow_pickle=False, mmap_mode="r")
        self.time = np.load(self.input_directory / "time.npy", allow_pickle=False)
        self.activity_time = np.load(self.directory / "activity_time.npy", allow_pickle=False)
        self.source_time = np.load(self.recording_directory / "frame_times.npy", allow_pickle=False)
        self.frames = np.load(self.recording_directory / "frames.npy", allow_pickle=False, mmap_mode="r")
        self.source_hex = np.load(self.input_directory / "source_hex.npy", allow_pickle=False)
        self.cells = np.load(self.directory / "cell_types.npy", allow_pickle=False).tolist()
        self.neurons = [numeric_row(r) for r in read_csv(self.directory / "neurons.csv")]
        self.coordinates = [numeric_row(r) for r in read_csv(self.input_directory / "input_hex_coordinates.csv")]
        self.receipts = read_csv(self.recording_directory / "frame_timestamps.csv")
        self.alignment = [numeric_row(r) for r in read_csv(self.input_directory / "time_alignment.csv")]
        self.dt = float(self.metadata["dt_s"])
        n = len(self.time)
        require(self.stimulus.shape == (1, n, 1, 721) and self.stimulus.dtype == np.float32, "Camera stimulus axes/dtype mismatch")
        require(self.activity.shape == (1, n, 65) and self.activity.dtype == np.float32, "Camera activity axes/dtype mismatch")
        require(len(set(self.cells)) == 65 and len(self.neurons) == 65, "Invalid central-cell identity")
        require([r["cell_type"] for r in self.neurons] == self.cells and [r["cell_type_axis"] for r in self.neurons] == list(range(65)), "Neuron axis identity mismatch")
        require(all(r["u"] == r["v"] == 0 for r in self.neurons), "Export is not central-node activity")
        require(np.array_equal(np.load(self.directory / "central_node_indices.npy", allow_pickle=False), [r["original_node_index"] for r in self.neurons]), "Original node identity mismatch")
        require(np.array_equal(np.load(self.directory / "activity_T4_T5.npy", allow_pickle=False), self.activity[:, :, [self.cells.index(c) for c in TARGETS]]), "T4/T5 activity differs from central export")
        require(self.dt == .005 and np.allclose(self.time, np.arange(n) * self.dt, atol=1e-12, rtol=0), "Invalid camera input time grid")
        require(np.array_equal(np.load(self.directory / "time.npy", allow_pickle=False), self.time), "Neural input time differs")
        require(np.array_equal(self.activity_time, self.time + self.dt), "Euler activity time is not input+dt")
        require(np.array_equal(np.load(self.input_directory / "source_time.npy", allow_pickle=False), self.source_time), "Source receipt time differs")
        require(np.isfinite(self.activity).all() and np.isfinite(self.stimulus).all() and self.stimulus.min() >= 0 and self.stimulus.max() <= 1, "Invalid camera activity/input values")
        require(self.frames.dtype == np.uint8 and self.frames.shape == tuple(self.recording["frames_shape"]) and self.frames.shape[0] == len(self.source_time) == len(self.receipts), "Recording shape mismatch")
        require(len(self.source_time) > 1 and self.source_time[0] == 0 and np.all(np.diff(self.source_time) > 0), "Invalid measured source timestamps")
        require(self.source_hex.shape == (len(self.source_time), 721) and np.isfinite(self.source_hex).all(), "Source receptor shape mismatch")
        require(self.time[-1] <= self.source_time[-1] and self.source_time[-1] - self.time[-1] < self.dt, "Input duration differs from recording")
        require(self.metadata["temporal_method"] == "zoh" and self.metadata["causal"] is True, "Only accepted causal ZOH import is enabled")
        spatial = self.metadata["spatial_transform"]
        require(spatial["policy"] == "native" and spatial["resize"] == "none" and spatial["crop"] is None and not spatial["mirror_horizontal"] and not spatial["mirror_vertical"] and spatial["rotation_degrees"] == 0, "Unaccepted spatial transform")
        require((spatial["boxeye_extent"], spatial["boxeye_kernel_size"], spatial["boxeye_filter"]) == (15, 13, "mean") and not spatial["actual_boxeye_internal_resize"], "Unaccepted official input conversion")
        require(len(self.coordinates) == 721 and [r["hex_pixel"] for r in self.coordinates] == list(range(721)), "Camera hex coordinate order mismatch")
        official_order = [(u, v) for u in range(-15, 16) for v in range(max(-15, -15-u), min(15, 15-u)+1)]
        require([(r["u"], r["v"]) for r in self.coordinates] == official_order, "Camera receptor identities differ from official order")
        require(len(self.alignment) == n, "Missing input/source correspondence")
        self.source_indices = np.searchsorted(self.source_time, self.time, side="right") - 1
        for i, row in enumerate(self.alignment):
            source = int(self.source_indices[i])
            require(row["model_frame"] == i and row["model_time_s"] == self.time[i], "Input frame/time correspondence mismatch")
            require(row["source_left_frame"] == row["source_right_frame"] == source and row["right_weight"] == 0 and str(row["uses_future_frame"]).lower() == "false", "ZOH uses wrong/future source frame")
            require(row["source_left_time_s"] == row["source_right_time_s"] == self.source_time[source], "Source frame/time correspondence mismatch")
        require(np.array_equal(self.stimulus[0, :, 0], self.source_hex[self.source_indices]), "Saved stimulus is not the mapped source receptor input")
        self.frame_paths = []
        first_ns = int(self.receipts[0]["received_monotonic_ns"])
        for i, receipt in enumerate(self.receipts):
            require(int(receipt["frame"]) == i and float(receipt["relative_time_s"]) == self.source_time[i], "Capture receipt ordering mismatch")
            require(abs((int(receipt["received_monotonic_ns"]) - first_ns) / 1e9 - self.source_time[i]) < 1e-12, "Capture monotonic time mismatch")
            path = inside(self.recording_directory, receipt["path"])
            covered(path)
            self.frame_paths.append(path)
        require(acceptance["recorded_frame_count"] == len(self.frames) and acceptance["stimulus_shape"] == list(self.stimulus.shape) and acceptance["lossless_png_equals_frames_npy"], "Acceptance data extent mismatch")
        self.conditions = [{"sample": 0, "recording_id": self.recording_directory.name, "temporal_method": "zoh", "spatial_policy": "native"}]
        self.metric_status = {"available": False, "reason": "真实录制场景没有受控12方向官方 DSI"}
        self.metric_rows, self.peak_rows, self.metric_files = [], [], {}
        self.verification_s = perf_counter() - started
        self.signatures = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in self.checked}

    def assert_unchanged(self):
        for path, signature in self.signatures.items():
            stat = path.stat()
            require((stat.st_size, stat.st_mtime_ns) == signature, f"Verified camera source changed; restart and revalidate: {path.name}")

    def file_path(self, name):
        self.assert_unchanged()
        return self.files[name][0]

    def frame_path(self, index):
        self.assert_unchanged()
        if not 0 <= index < len(self.frame_paths):
            raise IndexError("Source video frame out of range")
        return self.frame_paths[index]

    def info(self):
        self.assert_unchanged()
        result = super().info()
        result.update({"dataset_type": "recorded_camera_flyvis", "activity_time_s": self.activity_time.tolist(),
                       "time_reference": "input=time.npy; Euler after-state=activity_time.npy=input+0.005 s; capture=measured host receipt",
                       "n_neurons": self.identity["neurons"], "n_connections": self.identity["edges"],
                       "recorded_device": self.identity["device"], "recorded_gpu": self.identity["gpu"],
                       "historical_inference_s": self.identity["inference"]["elapsed_s"],
                       "processing_mode": "已录制 / native BoxEye(15,13) / 因果 ZOH / Full 连续网络 / 结果回放",
                       "origin_execution_kind": self.identity["execution_kind"], "origin_job_id": self.identity["job_id"],
                       "verification": {"status": "PASS", "manifest_files": len(self.checked), "elapsed_s": self.verification_s},
                       "files": [{"name": name, "sha256": digest, "url": f"/api/datasets/{self.id}/files/{name}"} for name, (path, digest) in self.files.items()],
                       "camera": {"source_directory": str(self.recording_directory), "input_directory": str(self.input_directory),
                                  "source_sha256": self.handoff["source_sha256"], "input_sha256": self.handoff["input_sha256"],
                                  "output_sha256": self.handoff["output_sha256"], "source_frame_count": len(self.source_time),
                                  "measured_fps": self.recording["measured_delivery_fps"], "reported_fps": self.recording["capture"]["reported_fps"],
                                  "source_time_s": self.source_time.tolist(), "input_source_indices": self.source_indices.tolist(),
                                  "received_utc": [r["received_utc"] for r in self.receipts],
                                  "received_monotonic_ns": [r["received_monotonic_ns"] for r in self.receipts],
                                  "frame_url_template": f"/api/datasets/{self.id}/frames/{{index}}.png",
                                  "timestamp_semantics": self.recording["timestamp_semantics"]}})
        return result

    def sample(self, index):
        self.assert_unchanged()
        return super().sample(index)

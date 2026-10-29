"""Explicit read-only consumer of the six independent controlled-video handoff.

Consumes the provided schema without importing its recorder/renderer/runtime.
NPY state is read with allow_pickle=False; PT checkpoints are hashed only.
"""
import hashlib
from time import perf_counter

import numpy as np

from camera_store import inside, require
from data_store import Dataset, TARGETS, numeric_row, read_csv, read_json
from startup_cache import cached_sha256 as sha256


def tensor_sha(array):
    return hashlib.sha256(str(array.dtype).encode() + str(array.shape).encode() + array.tobytes()).hexdigest()


class ControlledVideoDataset(Dataset):
    def init__(self, config, root, geometry_reference):
        started = perf_counter()
        self.config, self.id = config, config["id"]
        camera_root = inside(root, config["root"])
        self.task = inside(camera_root, config["directory"])
        self.manifest_path = inside(self.task, config["descriptor"])
        anchors = [config["descriptor"], config["acceptance"], config["reader"], "gpu_full_r1/job_status.json", "gpu_full_r2/result.json", "sources/original_manifest.json"]
        require(all(name in config["pins"] for name in anchors), "Missing explicit controlled-video pin")
        self.checked = {}
        for name, expected in config["pins"].items():
            path = inside(self.task, name)
            require(sha256(path) == expected, f"Controlled-video pinned identity mismatch: {name}")
            self.checked[path] = expected
        self.descriptor = read_json(self.manifest_path)
        descriptor = self.descriptor
        acceptance = read_json(inside(self.task, config["acceptance"]))
        require(descriptor["schema"] == "flyvis-controlled-video-experiment-v1" and descriptor["status"] == acceptance["status"] == "PASS", "Unaccepted controlled-video descriptor")
        require(acceptance["descriptor_sha256"] == self.checked[self.manifest_path], "Controlled-video acceptance/descriptor identity differs")
        require(descriptor["dataset_type"] == "controlled_video_flyvis" and descriptor["source_kind"] == "synthetic_controlled_video" and descriptor["source_is_camera"] is False, "File input cannot claim camera provenance")
        require(descriptor["processing_mode"] == "offline" and descriptor["display_kind"] == "verified_offline_replay", "Unknown controlled-video display policy")
        require(descriptor["modes"] == {"Full": "PASS", "Ablation": "unavailable", "Python Replacement": "unavailable", "FPGA Replacement": "unavailable"}, "Unaccepted replacement mode")
        self.paths, self.files = {}, {}
        for entry in descriptor["files"]:
            path = inside(camera_root, entry["path"])
            require(path.is_relative_to(self.task), "Controlled-video file escapes experiment")
            require(entry["role"] not in self.paths and path.stat().st_size == entry["bytes"] and sha256(path) == entry["sha256"], f"Controlled-video role/hash mismatch: {entry['role']}")
            self.paths[entry["role"]] = path
            self.checked[path] = entry["sha256"]
            self.files[entry["role"] + path.suffix] = (path, entry["sha256"])
        self.files["descriptor.json"] = (self.manifest_path, self.checked[self.manifest_path])
        self.files["handoff_validation.json"] = (inside(self.task, config["acceptance"]), config["pins"][config["acceptance"]])
        self.result = read_json(self.paths["result"])
        self.metadata = read_json(self.paths["input_metadata"])
        analysis = read_json(self.paths["analysis"])
        status = read_json(inside(self.task, "gpu_full_r1/job_status.json"))
        model = descriptor["model"]
        require(model == self.result["model_identity"], "Controlled-video model identity differs")
        for key in ["model", "source_commit", "checkpoint_sha256"]:
            require(model[key] == geometry_reference.identity[key], f"Controlled-video model/checkpoint mismatch: {key}")
        require(status["state"] == "complete" and status["job_id"] == self.result["job_id"] and self.result["status"] == analysis["status"] == "PASS", "Controlled-video computation incomplete")
        require(self.result["execution_kind"] == descriptor["origin_execution_kind"] == "new_inference", "Historical job execution identity differs")
        require(self.result["source_kind"] == "synthetic_controlled_video" and self.result["source_is_camera"] is False, "Result claims camera input")
        require(self.result["weights_exact_before_and_after"] and self.result["same_initial_state_for_all_conditions"] and analysis["independent_GPU_replay_bitwise_equal"], "Full/common-state/replay acceptance incomplete")
        require(self.result["network_mode"] == "six independent 4s conditions, common initial state" and descriptor["condition_execution"] == "six independent 4s clips, same frozen 45669-node initial state" and self.result["dt_s"] == .005, "Wrong independent-condition network policy")
        require(not self.result["combined_24s_continuous_network_inference"] and not analysis["formal_DSI_computed"], "Wrong continuous-network or official-metric claim")
        for folder, inventory in [(self.task / "input", self.metadata["data_sha256"]), (self.task / "gpu_full_r1", self.result["data_sha256"])]:
            for name, expected in inventory.items():
                path = inside(folder, name)
                require(sha256(path) == expected, f"Controlled-video inventory mismatch: {name}")
                self.checked[path] = expected
        load = lambda role: np.load(self.paths[role], allow_pickle=False, mmap_mode="r")
        self.stimulus, self.activity = load("stimulus"), load("activity")
        self.source_hex, self.source_time = load("source_hex"), load("source_time")
        self.time, self.activity_time = load("input_time"), load("activity_time")
        require(self.stimulus.shape == (6, 800, 1, 721) and self.activity.shape == (6, 800, 65) and self.stimulus.dtype == self.activity.dtype == np.float32, "Controlled-video arrays have wrong axes/dtype")
        require(descriptor["axes"] == {"stimulus": ["sample", "frame", "channel", "hex_pixel"], "activity": ["sample", "frame", "central_cell_type"], "stimulus_shape": [6, 800, 1, 721], "activity_shape": [6, 800, 65]}, "Descriptor axes differ from arrays")
        require(self.source_hex.shape == (6, 240, 721) and all(np.isfinite(a).all() for a in [self.stimulus, self.activity, self.source_hex]) and self.stimulus.min() >= 0 and self.stimulus.max() <= 1, "Invalid controlled-video values")
        self.dt = .005
        require(np.array_equal(self.source_time, np.arange(240) / 60.) and np.array_equal(self.time, np.arange(800) * self.dt) and np.array_equal(self.activity_time, self.time + self.dt), "Wrong controlled-video time axis")
        timing = descriptor["timing"]
        require(timing["source_clock"] == "verified_60Hz_file_presentation" and timing["sensor_or_capture_utc_available"] is False and timing["dt_s"] == self.dt and timing["legacy_offset_s"] == 0 and timing["last_frame_valid_until_s"] == timing["input_stop_exclusive_s"] == 4. and timing["last_input_s"] == self.time[-1] and timing["last_activity_s"] == self.activity_time[-1], "Wrong controlled-video clock/endpoint policy")
        self.source_indices = np.searchsorted(self.source_time, self.time, side="right") - 1
        require(np.array_equal(self.stimulus[:, :, 0], self.source_hex[:, self.source_indices]), "Controlled input is not exact causal frame hold")
        require(descriptor["frozen_comparison_input_sha256"] == self.result["input_sha256"] == analysis["input_sha256"] == self.checked[self.paths["stimulus"]], "Frozen input identity differs")
        initial = load("initial_state_full")
        require(initial.shape == (1, 45669) and np.isfinite(initial).all() and self.checked[self.paths["initial_state_full"]] == descriptor["frozen_common_initial_state_sha256"] and tensor_sha(initial) == self.result["initial_state_value_sha256"], "Frozen full initial state differs")
        require(len(self.result["condition_timings"]) == 6 and all(r["sample"] == i and r["steps"] == 800 and r["warmup_in_condition"] == 0 and r["same_initial_state_value_sha256"] == tensor_sha(initial) for i, r in enumerate(self.result["condition_timings"])), "Conditions do not share independent frozen initialization")
        self.cells = load("cell_types").tolist()
        self.neurons = [numeric_row(r) for r in read_csv(self.paths["neurons"])]
        self.coordinates = [numeric_row(r) for r in read_csv(self.paths["coordinates"])]
        require(self.cells == geometry_reference.cells and len(self.neurons) == 65 and all(r["cell_type_axis"] == i and (r["cell_type"], r["original_node_index"], r["u"], r["v"]) == (reference["cell_type"], reference["network_node_index"], reference["u"], reference["v"]) for i, (r, reference) in enumerate(zip(self.neurons, geometry_reference.neurons))), "Controlled central neuron identity mismatch")
        require([(r["u"], r["v"]) for r in self.coordinates] == [(r["u"], r["v"]) for r in geometry_reference.coordinates], "Controlled 721 ordering mismatch")
        require(np.array_equal(load("activity_T4_T5"), self.activity[:, :, [self.cells.index(c) for c in TARGETS]]), "Controlled T4/T5 identity mismatch")
        self.conditions = descriptor["samples"]
        require(self.conditions == self.metadata["samples"] and len(self.conditions) == 6 and [c["sample"] for c in self.conditions] == list(range(6)), "Controlled sample identities differ")
        samples = [numeric_row(r) for r in read_csv(self.paths["samples"])]
        require(len(samples) == 6 and all(all(row[k] == ("" if v is None else v) for k, v in condition.items()) for row, condition in zip(samples, self.conditions)), "Controlled samples CSV differs")
        require(self.metadata["temporal_method"] == "zoh", "Unaccepted controlled resampling")
        spatial = self.metadata["spatial_transform"]
        require(spatial["policy"] == "native" and spatial["boxeye_extent"] == 15 and spatial["boxeye_kernel_size"] == 13 and spatial["boxeye_filter"] == "mean" and spatial["resize"] == "none" and spatial["crop"] is None and not spatial["mirror_horizontal"] and not spatial["mirror_vertical"] and spatial["rotation_degrees"] == 0 and not spatial["actual_boxeye_internal_resize"], "Unaccepted controlled spatial policy")
        alignment = [numeric_row(r) for r in read_csv(self.paths["alignment"])]
        require(len(alignment) == 4800, "Incomplete controlled alignment")
        for sample in range(6):
            for i in range(800):
                row, source = alignment[sample * 800 + i], int(self.source_indices[i])
                require(row["sample"] == sample and row["model_frame"] == i and row["model_time_s"] == self.time[i] and row["source_left_frame"] == row["source_right_frame"] == source and row["source_left_time_s"] == row["source_right_time_s"] == self.source_time[source] and row["right_weight"] == 0 and str(row["uses_future_frame"]).lower() == "false", "Controlled frame/time mapping mismatch")
        self.frame_paths = []
        for sample in range(6):
            rows = read_csv(self.paths[f"frames_{sample}"])
            require(len(rows) == 240, "Incomplete controlled PNG sequence")
            paths = []
            for i, row in enumerate(rows):
                path = inside(self.task, row["path"])
                require(int(row["frame"]) == i and float(row["time_s"]) == self.source_time[i] and sha256(path) == row["sha256"], "Controlled PNG identity/time mismatch")
                self.checked[path] = row["sha256"]
                paths.append(path)
            self.frame_paths.append(paths)
        source_acceptance = read_json(self.paths["source_validation"])
        require(source_acceptance["status"] == "PASS" and len(source_acceptance["condition_audits"]) == 6, "Controlled video-source acceptance incomplete")
        for i, row in enumerate(source_acceptance["condition_audits"]):
            require(row["condition_id"] == self.conditions[i]["condition_id"] and row["decoded_frames"] == 240 and row["fps"] == 60. and row["source_mp4_sha256"] == self.checked[self.paths[f"source_video_{i}"]] and row["source_is_camera"] is False, "MP4/decoded source identity mismatch")
        self.directory = self.task / "gpu_full_r1"
        self.identity = dict(model, n_neurons=model["nodes"], n_connections=model["edges"])
        self.hashes = {"stimulus.npy": self.checked[self.paths["stimulus"]], "activity_central.npy": self.checked[self.paths["activity"]]}
        self.metric_status = {"available": False, "reason": "合成像素空间左右视频，不是官方12方向实验，无正式 DSI"}
        self.metric_rows, self.peak_rows, self.metric_files = [], [], {}
        self.signatures = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in self.checked}
        self.verification_s = perf_counter() - started

    def assert_unchanged(self):
        for path, signature in self.signatures.items():
            stat = path.stat()
            require((stat.st_size, stat.st_mtime_ns) == signature, "Verified controlled-video source changed; restart and revalidate")

    def file_path(self, name):
        self.assert_unchanged()
        return self.files[name][0]

    def frame_path(self, index, sample=0):
        self.assert_unchanged()
        if not 0 <= sample < 6 or not 0 <= index < 240:
            raise IndexError("Unknown controlled source frame/sample")
        return self.frame_paths[sample][index]

    def sample(self, index):
        self.assert_unchanged()
        result = super().sample(index)
        result["comparison_identity"] = {"frozen_input_sha256": self.descriptor["frozen_comparison_input_sha256"], "common_initial_state_sha256": self.descriptor["frozen_common_initial_state_sha256"], "source_video_sha256": self.checked[self.paths[f"source_video_{index}"]]}
        return result

    def info(self):
        self.assert_unchanged()
        info = super().info()
        info.update({"dataset_type": "controlled_video_flyvis", "condition_selector": True, "condition_selector_label": "六段独立条件 · 共同冻结初态", "source_kind": "synthetic_controlled_video", "source_is_camera": False,
                     "activity_time_s": self.activity_time.tolist(), "time_reference": "clip-relative input time; same-index Euler after-state=input+0.005 s; source=file presentation, not camera receipt",
                     "origin_execution_kind": self.result["execution_kind"], "origin_job_id": self.result["job_id"], "processing_mode": "合成视频文件 / native / 因果ZOH / 六条件共同初态独立执行 / Full结果回放",
                     "recorded_device": self.result["environment"]["device"], "recorded_gpu": self.result["environment"]["gpu"], "historical_inference_s": self.result["total_inference_s"],
                     "verification": {"status": "PASS", "manifest_files": len(self.checked), "elapsed_s": self.verification_s},
                     "files": [{"name": name, "sha256": digest, "url": f"/api/datasets/{self.id}/files/{name}"} for name, (path, digest) in self.files.items()],
                     "controlled_video": {"source_time_s": self.source_time.tolist(), "input_source_indices": self.source_indices.tolist(), "source_fps": 60., "received_utc": None, "received_monotonic_ns": None,
                                          "frame_url_template": f"/api/datasets/{self.id}/samples/{{sample}}/frames/{{index}}.png", "source_directory": str(self.task / "sources"), "input_directory": str(self.task / "input"),
                                          "source_video_sha256": [self.checked[self.paths[f"source_video_{i}"]] for i in range(6)], "input_sha256": self.hashes["stimulus.npy"], "output_sha256": self.hashes["activity_central.npy"],
                                          "common_initial_state_sha256": self.descriptor["frozen_common_initial_state_sha256"], "condition_execution": self.descriptor["condition_execution"], "continuous_24s_activity": False}})
        return info

    def condition_directions(self, cell, intensity, sample_id):
        require(cell in self.cells and 0 <= sample_id < 6, "Unknown controlled cell/sample")
        kind = self.conditions[sample_id]["kind"]
        traces = [{"sample_id": c["sample"], "label": c["title"], "condition_id": c["condition_id"], "activity": self.activity[c["sample"], :, self.cells.index(cell)].tolist()} for c in self.conditions if c["kind"] == kind]
        return {"dataset_id": self.id, "cell_type": cell, "time_s": self.activity_time.tolist(), "traces": traces, "official_metric": None, "official_peaks": [], "metric_status": self.metric_status}

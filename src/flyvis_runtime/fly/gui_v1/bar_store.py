"""Read accepted ten-condition MovingBar files without merging unequal time axes."""
from time import perf_counter
from pathlib import Path

import numpy as np

from camera_store import inside, require, verify_inventory
from data_store import numeric_row, read_csv, read_json


class TenConditionBar:
    def init__(self, config, root, geometry_reference):
        started = perf_counter()
        self.config, self.id = config, config["id"]
        # Trusted local configuration explicitly names the separate experiment root.
        self.root = (Path(root) / config["root"]).resolve()
        self.directory = inside(self.root, config["directory"])
        self.manifest_path = inside(self.root, config["manifest"])
        require(all(name in config["pins"] for name in [config["manifest"], config["acceptance"], config["cpu_result"], config["directory"] + "/result.json"]), "Missing explicit ten-condition document pin")
        self.checked = verify_inventory(self.root, config["manifest"], [config["directory"], config["acceptance"], config["cpu_result"]], config["pins"])
        self.identity = read_json(self.directory / "result.json")
        self.metadata = self.identity
        accepted = read_json(inside(self.root, config["acceptance"]))
        feature = next(r for r in accepted["features"] if r["function"] == "MovingBar ten finite conditions and CPU replay")
        require(feature["status"] == self.identity["status"] == "PASS" and feature["data"] == config["directory"], "Ten-condition bar acceptance differs")
        for key in ["source_commit", "checkpoint_sha256"]:
            require(self.identity[key] == geometry_reference.identity[key], f"Bar model/geometry identity mismatch: {key}")
        require(self.identity["weights_exact_before"] and self.identity["weights_exact_after"], "Bar weights changed")
        cpu = read_json(inside(self.root, config["cpu_result"]))
        require(cpu["status"] == "PASS" and cpu["checkpoint_sha256"] == self.identity["checkpoint_sha256"], "Bar CPU acceptance identity mismatch")
        require(len(cpu["conditions"]) == 10 and all(r["activity_vs_gpu"]["allclose"] for r in cpu["conditions"]), "Incomplete ten-condition CPU comparison")
        self.cells = geometry_reference.cells
        self.coordinates = geometry_reference.coordinates
        self.neurons = geometry_reference.neurons
        self.geometry_reference = geometry_reference
        self.stimulus, self.activity, self.times, self.conditions, self.sample_hashes = [], [], [], [], []
        self.files = {}
        for path, digest in self.checked.items():
            name = str(path.relative_to(self.root)).replace("\\", "/").replace("/", ".")
            self.files[name] = (path, digest)
        require(len(self.identity["conditions"]) == 10, "Bar is not a ten-condition run")
        for i, record in enumerate(self.identity["conditions"]):
            folder = self.directory / f"condition_{i:02d}"
            for name in ["stimulus.npy", "activity_central.npy", "time.npy", "cell_types.npy", "samples.csv", "result.json"]:
                require(folder / name in self.checked, f"Bar file lacks manifest coverage: {i}/{name}")
            require(record == read_json(folder / "result.json") and record["condition"] == i and record["status"] == "PASS" and record["weights_exact"], "Bar per-condition identity mismatch")
            rows = [numeric_row(r) for r in read_csv(folder / "samples.csv")]
            require(len(rows) == 1 and rows[0]["sample"] == 0 and all(rows[0][k] == v for k, v in record["parameters"].items()), "Bar sample parameters differ")
            stim = np.load(folder / "stimulus.npy", allow_pickle=False, mmap_mode="r")
            act = np.load(folder / "activity_central.npy", allow_pickle=False, mmap_mode="r")
            time = np.load(folder / "time.npy", allow_pickle=False)
            require(stim.shape == (1, len(time), 1, 721) and act.shape == (1, len(time), 65) and act.dtype == np.float32, "Invalid bar array axes")
            require(np.array_equal(np.load(folder / "cell_types.npy", allow_pickle=False), self.cells), "Bar cell order differs from matched model")
            require(np.isfinite(stim).all() and np.isfinite(act).all(), "Non-finite bar data")
            dt = record["config"]["dt"]
            require(dt == .005 and np.allclose(time, np.arange(len(time)) * dt - 1, atol=1e-12, rtol=0), "Invalid per-condition bar time")
            self.stimulus.append(stim[0]); self.activity.append(act[0]); self.times.append(time)
            self.conditions.append(dict(rows[0], sample=i, source_sample=0, source_condition=i))
            self.sample_hashes.append({"stimulus.npy": self.checked[folder / "stimulus.npy"], "activity_central.npy": self.checked[folder / "activity_central.npy"]})
        self.time, self.dt = self.times[0], .005
        self.hashes = {}
        self.metric_files = {}
        self.metric_status = {"available": False, "reason": "十条件 MovingBar 不是完整12方向实验，无正式 DSI"}
        self.verification_s = perf_counter() - started
        self.signatures = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in self.checked}

    def assert_unchanged(self):
        for path, signature in self.signatures.items():
            stat = path.stat()
            require((stat.st_size, stat.st_mtime_ns) == signature, "Verified MovingBar source changed; restart and revalidate")

    def file_path(self, name):
        self.assert_unchanged()
        return self.files[name][0]

    def info(self):
        self.assert_unchanged()
        info = self.geometry_reference.info()
        info.update({"id": self.id, "title": self.config["title"], "family": "bar", "dataset_type": "moving_bar10", "condition_selector": True,
                     "source_directory": str(self.directory), "conditions": self.conditions, "n_frames": len(self.time), "time_s": self.time.tolist(),
                     "input_shape": None, "activity_shape": None, "per_sample_frames": [len(t) for t in self.times],
                     "recorded_device": self.identity["device"], "recorded_gpu": self.identity.get("gpu"),
                     "historical_inference_s": sum(r["inference"]["elapsed_s"] for r in self.identity["conditions"]),
                     "historical_elapsed_s": None, "metadata": self.identity,
                     "official_metrics": self.metric_status,
                     "geometry_identity_source": {"dataset": self.geometry_reference.id, "checkpoint_sha256": self.identity["checkpoint_sha256"], "cell_order_exact": True},
                     "verification": {"status": "PASS", "manifest_files": len(self.checked), "elapsed_s": self.verification_s},
                     "files": [{"name": name, "sha256": digest, "url": f"/api/datasets/{self.id}/files/{name}"} for name, (path, digest) in self.files.items()],
                     "manifest_url": f"/api/datasets/{self.id}/files/manifest.json"})
        return info

    def sample(self, index):
        self.assert_unchanged()
        if not 0 <= index < 10:
            raise IndexError("Unknown MovingBar condition")
        n = len(self.times[index])
        return {"dataset_id": self.id, "sample_id": index, "conditions": self.conditions[index], "execution_kind": "offline_replay",
                "source_input_sha256": self.sample_hashes[index]["stimulus.npy"], "source_output_sha256": self.sample_hashes[index]["activity_central.npy"],
                "time_s": self.times[index].tolist(), "n_frames": n,
                "stimulus": {"url": f"/api/datasets/{self.id}/samples/{index}/stimulus.bin", "dtype": "float64_le", "shape": [n, 721]},
                "activity": {"url": f"/api/datasets/{self.id}/samples/{index}/activity.bin", "dtype": "float32_le", "shape": [n, 65]}}

    def input_array(self, index):
        return self.stimulus[index][:, 0]

    def condition_directions(self, cell, intensity, sample_id):
        require(cell in self.cells and 0 <= sample_id < 10, "Unknown cell/sample")
        row = self.conditions[sample_id]
        traces = [{"sample_id": i, "angle_deg": c["angle"], "activity": self.activity[i][:, self.cells.index(cell)].tolist()} for i, c in enumerate(self.conditions)
                  if all(c[k] == row[k] for k in ["intensity", "speed", "width"]) and len(self.times[i]) == len(self.times[sample_id])]
        return {"dataset_id": self.id, "cell_type": cell, "intensity": row["intensity"], "time_s": self.times[sample_id].tolist(),
                "traces": traces, "official_metric": None, "official_peaks": [], "metric_status": self.metric_status}

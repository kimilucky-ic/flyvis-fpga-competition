"""Read-only, manifest-verified access to existing FlyVis experiments."""
import csv
import hashlib
import json
import threading
from pathlib import Path
from time import perf_counter

import numpy as np
from startup_cache import cached_sha256, LazyResource

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [f"T{n}{s}" for n in (4, 5) for s in "abcd"]
REQUIRED = ["stimulus.npy", "activity_central.npy", "time.npy", "cell_types.npy",
            "samples.csv", "input_hex_coordinates.csv", "neurons.csv", "metadata.json"]


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def numeric_row(row):
    result = {}
    for key, value in row.items():
        try:
            number = float(value)
            result[key] = int(number) if number.is_integer() else number
        except (ValueError, TypeError):
            result[key] = value
    return result


def verify_manifest(path, directory, prefix=""):
    raw = read_json(path)
    entries = raw["files"] if isinstance(raw, dict) else raw
    hashes = {}
    for item in entries:
        relative = item["path"].replace("\\", "/")
        if prefix and not relative.startswith(prefix):
            continue
        filename = relative[len(prefix):] if prefix else relative
        target = (directory / filename).resolve()
        if not target.is_relative_to(directory.resolve()):
            raise ValueError("Manifest path escapes dataset directory")
        actual = cached_sha256(target)
        if actual != item["sha256"] or target.stat().st_size != item["bytes"]:
            raise ValueError(f"Manifest mismatch: {target.name}")
        hashes[filename] = actual
    for name in REQUIRED:
        if name not in hashes:
            raise ValueError(f"Required file is not covered by manifest: {name}")
    return hashes


class Dataset:
    def init__(self, config, root):
        started = perf_counter()
        self.config = config
        self.id = config["id"]
        self.directory = (root / config["directory"]).resolve()
        self.manifest_path = root / config["manifest"] if "manifest" in config else self.directory / "manifest.json"
        self.hashes = verify_manifest(self.manifest_path, self.directory, config.get("manifest_prefix", ""))
        self.metadata = read_json(self.directory / "metadata.json")
        self.identity = dict(self.metadata)
        if config.get("identity"):
            self.identity.update(read_json(root / config["identity"]))
        acceptance = read_json(root / config["acceptance"]) if config.get("acceptance") else self.metadata
        if acceptance.get("status") != "PASS":
            raise ValueError("Experiment acceptance is not PASS")
        self.stimulus = np.load(self.directory / "stimulus.npy", allow_pickle=False, mmap_mode="r")
        self.activity = np.load(self.directory / "activity_central.npy", allow_pickle=False, mmap_mode="r")
        self.time = np.load(self.directory / "time.npy", allow_pickle=False)
        self.cells = np.load(self.directory / "cell_types.npy", allow_pickle=False).tolist()
        self.conditions = [numeric_row(row) for row in read_csv(self.directory / "samples.csv")]
        self.neurons = [numeric_row(row) for row in read_csv(self.directory / "neurons.csv")]
        self.coordinates = [numeric_row(row) for row in read_csv(self.directory / "input_hex_coordinates.csv")]
        count, frames = config["expected_samples"], config["expected_frames"]
        if self.stimulus.shape != (count, frames, 1, 721) or self.activity.shape != (count, frames, 65):
            raise ValueError("Unexpected stimulus or activity axes")
        if len(self.cells) != 65 or len(set(self.cells)) != 65 or len(self.coordinates) != 721:
            raise ValueError("Invalid cell/coordinate identity")
        if [row["hex_pixel"] for row in self.coordinates] != list(range(721)):
            raise ValueError("Input coordinate ordering mismatch")
        if [row["sample"] for row in self.conditions] != list(range(count)):
            raise ValueError("Sample ordering mismatch")
        if [row["cell_type"] for row in self.neurons] != self.cells:
            raise ValueError("Central neuron identity ordering mismatch")
        self.dt = float(self.metadata["dt_s"])
        if self.time.shape != (frames,) or not np.allclose(self.time, np.arange(frames) * self.dt - 1, atol=1e-12, rtol=0):
            raise ValueError("Time axis is not frame*dt-1")
        if not np.isfinite(self.activity).all() or not np.isfinite(self.stimulus).all():
            raise ValueError("Non-finite activity/input")
        # Check the display payload against the exact NPY activities, without regenerating them.
        if (self.directory / "demo_payload.json").exists():
            if "demo_payload.json" not in self.hashes:
                raise ValueError("Display payload lacks manifest coverage")
            payload = read_json(self.directory / "demo_payload.json")
            indices = [self.cells.index(c) for c in payload["cell_types"]]
            for sample, saved in enumerate(payload["samples"]):
                if not np.array_equal(np.asarray(saved["activity"], dtype=self.activity.dtype), self.activity[sample][:, indices]):
                    raise ValueError("Display JSON/NPY activity mismatch")
            if not np.array_equal(np.asarray(payload["time_s"]), self.time):
                raise ValueError("Display JSON time mismatch")
        self.metric_status = {"available": False, "reason": "该实验没有匹配的正式 12 方向指标"}
        self.metric_rows = []
        self.peak_rows = []
        self.metric_files = {}
        self.verification_s = perf_counter() - started

    def info(self):
        model = self.identity
        return {
            "id": self.id, "title": self.config["title"], "family": self.config["family"],
            "execution_kind": "offline_replay", "source_directory": str(self.directory),
            "conditions": self.conditions, "n_frames": len(self.time), "time_s": self.time.tolist(),
            "dt_s": self.dt, "cell_types": self.cells, "targets": TARGETS, "neurons": self.neurons,
            "coordinates": self.coordinates, "input_shape": list(self.stimulus.shape),
            "activity_shape": list(self.activity.shape), "activity_units": "model units",
            "time_reference": "frame × dt − 1 s; activity AFTER each Euler update",
            "model": model.get("model"), "flyvis_version": model.get("flyvis", "1.2.0"),
            "source_commit": model.get("source_commit", "92b3845cc426dd309a1a0e1b3890156c42e14021"),
            "checkpoint_sha256": model.get("checkpoint_sha256"),
            "n_neurons": model.get("n_neurons"), "n_connections": model.get("n_connections"),
            "recorded_device": self.metadata.get("device", "cpu"), "recorded_gpu": self.metadata.get("gpu"),
            "historical_inference_s": self.metadata.get("inference_s"),
            "historical_elapsed_s": self.metadata.get("elapsed_s"),
            "verification": {"status": "PASS", "manifest_files": len(self.hashes), "elapsed_s": self.verification_s},
            "official_metrics": self.metric_status,
            "files": [{"name": name, "sha256": value,
                       "url": f"/api/datasets/{self.id}/files/{name}"} for name, value in self.hashes.items() if "/" not in name],
            "manifest_url": f"/api/datasets/{self.id}/files/manifest.json",
            "metadata": self.metadata,
        }

    def sample(self, index):
        if not 0 <= index < len(self.conditions):
            raise IndexError("Sample index out of range")
        return {"dataset_id": self.id, "sample_id": index, "conditions": self.conditions[index],
                "execution_kind": "offline_replay", "source_input_sha256": self.hashes["stimulus.npy"],
                "source_output_sha256": self.hashes["activity_central.npy"],
                "stimulus": {"url": f"/api/datasets/{self.id}/samples/{index}/stimulus.bin", "dtype": "float64_le",
                             "shape": [len(self.time), 721]},
                "activity": {"url": f"/api/datasets/{self.id}/samples/{index}/activity.bin", "dtype": "float32_le",
                             "shape": [len(self.time), len(self.cells)]}}

    def directions(self, cell, intensity):
        if cell not in self.cells or intensity not in (0, 1):
            raise ValueError("Unknown cell or intensity")
        index = self.cells.index(cell)
        traces = [{"sample_id": i, "angle_deg": row["angle"],
                   "activity": self.activity[i, :, index].tolist()}
                  for i, row in enumerate(self.conditions) if "angle" in row and row["intensity"] == intensity]
        metrics = next((row for row in self.metric_rows if row["cell_type"] == cell and row["intensity"] == intensity), None)
        peaks = [row for row in self.peak_rows if row["cell_type"] == cell and row["intensity"] == intensity]
        return {"dataset_id": self.id, "cell_type": cell, "intensity": intensity, "time_s": self.time.tolist(),
                "traces": traces, "official_metric": metrics, "official_peaks": peaks,
                "metric_status": self.metric_status}


class DataStore:
    def init__(self, root=ROOT, config_path=None, integrations_path=None):
        self.root = Path(root)
        self.config = read_json(config_path or ROOT / "gui_v1/datasets.json")
        self.datasets = {}
        self.errors = []
        for spec in self.config["datasets"]:
            try:
                self.datasets[spec["id"]] = Dataset(spec, self.root)
            except (OSError, ValueError, KeyError, AssertionError) as error:
                self.errors.append({"id": spec["id"], "title": spec["title"], "error": str(error)})
        if "edge24" not in self.datasets:
            raise ValueError(f"Required 24-condition data unavailable: {self.errors}")
        self.load_official_metrics()
        self.integration_config = {}
        # Optional imports/adapters are isolated from the accepted offline startup.
        try:
            self.integration_config = read_json(integrations_path or self.root / "gui_v1/integrations.json")
            spec = self.integration_config.get("camera")
            if spec:
                from camera_store import RecordedCameraDataset
                self.datasets[spec["id"]] = RecordedCameraDataset(spec, self.root)
        except (OSError, ValueError, KeyError, AssertionError, TypeError, ImportError) as error:
            self.errors.append({"id": "camera1", "title": "真实摄像头结果", "error": str(error)})
        try:
            spec = self.integration_config.get("moving_bar10")
            if spec:
                from bar_store import TenConditionBar
                self.datasets[spec["id"]] = TenConditionBar(spec, self.root, self.datasets["edge24"])
        except (OSError, ValueError, KeyError, AssertionError, TypeError, ImportError) as error:
            self.errors.append({"id": "bar10", "title": "MovingBar 新十条件", "error": str(error)})
        try:
            spec = self.integration_config.get("controlled_video6")
            if spec:
                from controlled_store import ControlledVideoDataset
                self.datasets[spec["id"]] = ControlledVideoDataset(spec, self.root, self.datasets["edge24"])
        except (OSError, ValueError, KeyError, AssertionError, TypeError, ImportError) as error:
            self.errors.append({"id": "controlled6", "title": "合成受控视频 · 六独立条件", "error": str(error)})

    def load_official_metrics(self):
        spec = self.config["official_direction_metrics"]
        dataset = self.datasets[spec["dataset"]]
        try:
            reference = (self.root / spec["reference_directory"]).resolve()
            analysis = (self.root / spec["analysis_directory"]).resolve()
            for filename, expected in spec["files"].items():
                if cached_sha256(analysis / filename) != expected:
                    raise ValueError(f"Official metric identity mismatch: {filename}")
            if cached_sha256(reference / "activity_central_gpu.npy") != dataset.hashes["activity_central.npy"]:
                raise ValueError("Official metric activity is from a different run")
            if not np.array_equal(np.load(reference / "stimulus.npy", allow_pickle=False), dataset.stimulus.astype(np.float32)):
                raise ValueError("Official metric canonical input mismatch")
            for name in ["time.npy", "cell_types.npy"]:
                if cached_sha256(reference / name) != dataset.hashes[name]:
                    raise ValueError(f"Official metric {name} identity mismatch")
            reference_conditions = [numeric_row(row) for row in read_csv(reference / "samples.csv")]
            for source, target in zip(reference_conditions, dataset.conditions, strict=True):
                if any(source[k] != target[k] for k in ["sample", "angle", "intensity", "speed"]):
                    raise ValueError("Official metric conditions mismatch")
            identity = read_json(reference / "metadata.json")
            if identity["checkpoint_sha256"] != dataset.identity["checkpoint_sha256"]:
                raise ValueError("Official metric checkpoint mismatch")
            audit = read_json(analysis / "direction_analysis.json")
            if audit["status"] != "PASS":
                raise ValueError("Official direction analysis is not PASS")
            dataset.metric_rows = [numeric_row(row) for row in read_csv(analysis / "direction_metrics_T4_T5.csv")]
            dataset.peak_rows = [numeric_row(row) for row in read_csv(analysis / "angular_peak_responses.csv")]
            dataset.metric_files = {name: analysis / name for name in spec["files"]}
            dataset.metric_status = {"available": True, "status": "PASS", "directory": str(analysis),
                                     "formula": audit["dsi_formula"], "peak_definition": audit["peak_definition"],
                                     "activity_bitwise_identity": True, "input_identity": "exact after original float32 canonical cast",
                                     "scope": "单个官方预训练模型 / MovingEdge / speed=19 / 完整12方向",
                                     "files": [{"name": name, "sha256": value, "url": f"/api/datasets/{dataset.id}/files/{name}"}
                                               for name, value in spec["files"].items()]}
        except (OSError, KeyError, ValueError) as error:
            dataset.metric_status = {"available": False, "reason": str(error)}

    def catalog(self):
        visible, unavailable = [], list(self.errors)
        for dataset in self.datasets.values():
            try:
                visible.append(dataset.info())
            except (OSError, ValueError) as error:
                if dataset.id in ["edge24", "flash", "bar", "minimal"]:
                    raise
                unavailable.append({"id": dataset.id, "title": dataset.config["title"], "error": str(error)})
        return {"schema": "flyvis-display-v1", "default_dataset": "edge24",
                "execution_kind": "offline_replay", "datasets": visible,
                "unavailable_datasets": unavailable}


class LazyDataStore:
    """The HTTP shell is ready before the user opens the legacy data library."""
    def init__(self, root=ROOT, config_path=None, integrations_path=None):
        self.root = Path(root)
        self._resource = LazyResource(lambda: DataStore(root, config_path, integrations_path), 'legacy datasets')
        self._config_path = Path(config_path or ROOT/'gui_v1/datasets.json')
        self._references = {}
        self._reference_lock = threading.RLock()

    def reference_dataset(self, name):
        """Load one explicitly configured reference without camera/library imports."""
        if self.loaded:
            return self._resource.get().datasets[name]
        with self._reference_lock:
            if name not in self._references:
                spec = next((x for x in read_json(self._config_path)['datasets'] if x['id']==name), None)
                if spec is None:
                    return self._resource.get().datasets[name]
                self._references[name] = Dataset(spec, self.root)
            return self._references[name]

    @property
    def loaded(self):
        return self._resource.loaded

    def __getattr__(self, name):
        return getattr(self._resource.get(), name)

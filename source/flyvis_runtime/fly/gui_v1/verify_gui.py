"""Verify every served real sample, provenance, official metrics and unavailable adapters."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
from time import perf_counter
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import numpy as np

from data_store import DataStore, ROOT, read_json, verify_manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8771")
    parser.add_argument("--output", default=str(ROOT / "gui_v1/evidence/data_acceptance.json"))
    args = parser.parse_args()
    started = perf_counter()
    store = DataStore()
    records = []

    def get(path):
        with urlopen(args.url + path, timeout=15) as response:
            return response.read(), dict(response.headers)

    catalog = json.loads(get("/api/catalog")[0])
    assert catalog["execution_kind"] == "offline_replay"
    legacy_ids = {"edge24", "flash", "bar", "minimal"}
    assert legacy_ids.issubset({d["id"] for d in catalog["datasets"]})
    assert not any(d["id"] in legacy_ids for d in catalog["unavailable_datasets"])
    legacy_datasets = [store.datasets[key] for key in ["edge24", "flash", "bar", "minimal"]]
    for dataset in legacy_datasets:
        samples = []
        for index in range(len(dataset.conditions)):
            sample = json.loads(get(f"/api/datasets/{dataset.id}/samples/{index}")[0])
            stim_bytes, stim_headers = get(sample["stimulus"]["url"])
            act_bytes, act_headers = get(sample["activity"]["url"])
            assert stim_bytes == np.asarray(dataset.stimulus[index, :, 0], dtype="<f8").tobytes()
            assert act_bytes == np.asarray(dataset.activity[index], dtype="<f4").tobytes()
            assert stim_headers["X-Source-SHA256"] == dataset.hashes["stimulus.npy"]
            assert act_headers["X-Source-SHA256"] == dataset.hashes["activity_central.npy"]
            assert sample["execution_kind"] == "offline_replay" and sample["conditions"] == dataset.conditions[index]
            samples.append({"sample": index, "conditions": sample["conditions"], "stimulus_transport_exact": True,
                            "activity_transport_bitwise_exact": True})
        for cell in ["T4c", "T5a"]:
            for intensity in (0, 1):
                result = json.loads(get(f"/api/datasets/{dataset.id}/directions?cell={cell}&intensity={intensity}")[0])
                for trace in result["traces"]:
                    assert np.array_equal(np.asarray(trace["activity"], dtype="float32"), dataset.activity[trace["sample_id"], :, dataset.cells.index(cell)])
                if dataset.id != "edge24":
                    assert result["official_metric"] is None
        records.append({"id": dataset.id, "status": "PASS", "source": str(dataset.directory),
                        "manifest_files": len(dataset.hashes), "source_hashes": dataset.hashes,
                        "all_samples": samples, "official_metrics": dataset.metric_status})

    metric = json.loads(get("/api/datasets/edge24/directions?cell=T4c&intensity=1")[0])
    assert metric["metric_status"]["available"] and len(metric["traces"]) == 12
    assert metric["official_metric"]["official_dsi"] == 0.627361980585308
    assert len(metric["official_peaks"]) == 12
    statuses = json.loads(get("/api/adapters")[0])
    assert statuses["gpu"]["device"] is None and statuses["fpga"]["resources"] is None
    assert statuses["fpga"]["cycles"] is None and statuses["comparison"]["time_series_error"] is None
    assert sum(m["available"] for m in statuses["modes"]) == 1
    rejected_paths = ["/.env", "/gui_v1/server.py", "/api/datasets/edge24/files/.env", "/api/datasets/edge24/samples/24",
                      "/api/datasets/edge24/files/../metadata.json", "/api/datasets/unknown"]
    for path in rejected_paths:
        try:
            get(path)
            raise AssertionError(f"Unexpected access: {path}")
        except HTTPError as error:
            assert error.code == 404
    for path in ["/api/inference", "/api/camera/record", "/api/comparison"]:
        try:
            urlopen(Request(args.url + path, data=b"{}", method="POST"), timeout=15)
            raise AssertionError("An offline adapter executed a run")
        except HTTPError as error:
            assert error.code == 503 and json.loads(error.read())["result"] is None

    # Corrupt only a temporary manifest; never touch a source experiment or fabricate activity.
    dataset = store.datasets["edge24"]
    manifest = read_json(dataset.manifest_path)
    manifest["files"][0]["sha256"] = "0" * 64
    with tempfile.TemporaryDirectory(prefix="flyvis-gui-manifest-") as temporary:
        path = Path(temporary) / "manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        try:
            verify_manifest(path, dataset.directory)
            raise AssertionError("A modified source manifest was accepted")
        except ValueError as error:
            assert "Manifest mismatch" in str(error)
        config = read_json(ROOT / "gui_v1/datasets.json")
        config["official_direction_metrics"]["files"]["direction_analysis.json"] = "0" * 64
        path = Path(temporary) / "config.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        rejected = DataStore(config_path=path)
        assert not rejected.datasets["edge24"].metric_status["available"]
        assert not rejected.datasets["edge24"].metric_rows

    output = {"status": "PASS", "checked_utc": datetime.now(timezone.utc).isoformat(),
              "evidence_level": "read-only source verification and local HTTP data transport; no new neural inference",
              "samples_checked": sum(len(d.conditions) for d in legacy_datasets),
              "datasets": records, "directions_exact": True, "unconnected_adapters_return_503": True,
              "private_and_invalid_paths_return_404": True, "corrupt_manifest_rejected": True,
              "mismatched_official_metrics_hidden": True, "elapsed_s": perf_counter() - started}
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"PASS: {output['samples_checked']} real samples, exact stimulus/activity transport, official metrics and unavailable adapters.")
    print(target)


if __name__ == "__main__":
    main()

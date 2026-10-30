"""Prepare a Phase 4 review packet. Data checks only; no neural updates/GPU calls.

Reads sealed Phase 3 inputs and the official 24-sample rendered fixture. Never
imports FlyVis, torch, HUpdater, R-only or a network runner. Existing outputs
are preserved. Run from the Windows NumPy environment, not a GPU environment.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import platform
import shutil
import numpy as np

HERE = Path(__file__).resolve().parent
FPGA = HERE.parents[1]
FLY = FPGA.parent / "fly"
P3 = FPGA / "flyvis-circuit-selection/phase3_ablation_screen_20261010"
BUNDLE = P3 / "input_bundle_r2"
SPEC = P3 / "spec_snapshot"
OLD24 = FLY / "artifacts/direction_tuning_20261010"
METRIC = FLY / "upstream/flyvis/flyvis/analysis/moving_bar_responses.py"
CANDIDATES = ["B_T5c", "C_T4T5_all_centers"]


def sha(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def dump(p, obj):
    with Path(p).open("x", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def entry(p):
    p = Path(p)
    return dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p))


def main():
    # The absence of the preparation directory is the only overwrite policy.
    dest = HERE / "prepared_inputs"
    if dest.exists():
        raise SystemExit("Existing preparation preserved; review audit before rerun")
    spec = read(SPEC / "spec_config.json")
    previous = read(P3 / "PRE_RUN_REGISTRATION.json")
    oldmeta = read(OLD24 / "metadata.json")
    oldmanifest = {e["path"]: e for e in read(OLD24 / "manifest.json")["files"]}
    audited = []
    for key, file in [
        ("initial_state_sha256", "initial_state_full.npy"),
        ("expanded_parameters_sha256", "expanded_parameters.npz"),
        ("nodes_full_sha256", "nodes_full.csv"),
    ]:
        p = BUNDLE / file
        assert sha(p) == spec["model"][key], (key, "identity mismatch")
        audited.append(entry(p))
    assert sha(BUNDLE / "stimulus.npy") == spec["fixture"]["stimulus_sha256"]
    assert sha(BUNDLE / "time.npy") == spec["fixture"]["time_sha256"]
    assert sha(SPEC / "ABLATION_SPEC_v1.md") == previous["spec_sha256"]
    assert sha(SPEC / "spec_config.json") == previous["spec_config_sha256"]
    for file in ["stimulus.npy", "time.npy", "samples.csv", "metadata.json", "activity_central.npy"]:
        p = OLD24 / file
        assert sha(p) == oldmanifest[file]["sha256"]
        audited.append(entry(p))
    assert oldmeta["source_commit"] == spec["model"]["source_commit"]
    assert oldmeta["checkpoint_sha256"] == spec["model"]["checkpoint_sha256"]
    raw = np.load(OLD24 / "stimulus.npy")
    a0 = np.load(BUNDLE / "initial_state_full.npy")
    t = np.load(OLD24 / "time.npy")
    old4 = np.load(BUNDLE / "stimulus.npy")
    assert raw.shape == (24, 485, 1, 721) and a0.shape == (45669,)
    assert np.isfinite(raw).all() and np.isfinite(a0).all()
    assert raw.min() >= 0 and raw.max() <= 1 and a0.dtype == np.float32
    assert np.array_equal(t, np.load(BUNDLE / "time.npy"))
    assert np.allclose(t, np.arange(485) * .005 - 1, atol=1e-12, rtol=0)
    stim = np.ascontiguousarray(raw, dtype=np.float32)
    assert np.array_equal(stim[[0, 1, 12, 13]], old4)
    rows = list(csv.DictReader((OLD24 / "samples.csv").open(encoding="utf-8")))
    assert len(rows) == 24
    conditions = []
    for i, row in enumerate(rows):
        assert int(row["sample"]) == int(row["fixture_sample"]) == i
        angle, intensity = int(row["angle"]), int(row["intensity"])
        assert (angle, intensity) == ((i // 2) * 30, i % 2)
        assert float(row["speed"]) == 19 and int(row["width"]) == 80
        conditions.append(dict(bundle_condition=i, original_sample=i, angle=angle,
            intensity=intensity, polarity="ON" if intensity else "OFF", width=80,
            speed=19, t_stim=float(spec["fixture"]["conditions"][0]["t_stim"])))
    all_readouts = {}
    for name, e in spec["readouts"].items():
        p = SPEC / Path(e["path"]).name
        assert sha(p) == e["sha256"]
        ids = np.load(p)
        assert len(ids) == e["n"] and len(np.unique(ids)) == len(ids)
        assert np.all(ids >= 0) and np.all(ids < 45669)
        all_readouts[name] = dict(n=len(ids), source=entry(p))
    common_r = np.load(SPEC / "common_R_ids.npy")
    v = np.load(SPEC / "common_direct_downstream_T4_T5_ids.npy")
    all_tt = np.load(SPEC / "all_T4_T5_ids.npy")
    d = np.load(SPEC / "common_direct_downstream_R_ids.npy")
    assert np.isin(v, common_r).all() and np.isin(v, d).all()
    assert np.isin(v, all_tt).all()
    z = np.load(BUNDLE / "expanded_parameters.npz")
    src, tgt = z["source_global"], z["target_global"]
    assert np.array_equal(z["original_edge_index"], np.arange(1513231))
    candidate_info = {}
    structural_secondary = {}
    for name in CANDIDATES:
        cp = BUNDLE / "candidates" / name
        mf = read(cp / "candidate_manifest.json")
        h = np.array(mf["h_global_node_indices"], dtype=np.int64)
        assert np.array_equal(h, np.load(SPEC / (name + "_H_ids.npy")))
        mask = np.zeros(45669, dtype=bool)
        mask[h] = True
        partitions = dict(HH=np.flatnonzero(mask[src] & mask[tgt]),
            RH=np.flatnonzero(~mask[src] & mask[tgt]),
            HR=np.flatnonzero(mask[src] & ~mask[tgt]),
            RR=np.flatnonzero(~mask[src] & ~mask[tgt]))
        frozen = np.load(cp / "validated_partition_ids.npz")
        for tag, ids in partitions.items():
            assert np.array_equal(ids, frozen[tag])
            assert len(ids) == mf["partition_counts"][tag]
        assert np.array_equal(partitions["HR"], np.load(SPEC / (name + "_HR_edge_ids.npy")))
        assert np.array_equal(np.sort(np.concatenate(list(partitions.values()))), np.arange(1513231))
        direct = np.unique(tgt[partitions["HR"]])
        assert np.array_equal(direct, np.load(SPEC / (name + "_direct_R_targets.npy")))
        structural_secondary[name] = np.intersect1d(direct, v)
        candidate_info[name] = dict(n_H=len(h), n_R=45669-len(h),
            partition_counts={k:len(a) for k,a in partitions.items()},
            HR_original_edge_identity=entry(SPEC / (name + "_HR_edge_ids.npy")),
            H_global_ID_identity=entry(SPEC / (name + "_H_ids.npy")),
            candidate_manifest=entry(cp / "candidate_manifest.json"),
            static_boundary=entry(cp / "static_boundary_gpu_native.npz"),
            validated_partition=entry(cp / "validated_partition_ids.npz"),
            n_incoming_source_R=len(np.unique(src[partitions["RH"]])),
            n_direct_R=len(direct), n_direct_common_visual_R=len(structural_secondary[name]),
            all_original_edges_preserved=True, partition_derived_without_activity=True,
            center_membership=spec["candidates"][name]["T4_T5_centers_membership"])
    hist = np.load(OLD24 / "activity_central.npy", mmap_mode="r")
    # All assertions above precede writing any reviewed fixture bytes.
    dest.mkdir()
    (dest / "readouts").mkdir()
    (dest / "operator_ids").mkdir()
    (dest / "metric_source").mkdir()
    np.save(dest / "stimulus_float32.npy", stim)
    shutil.copyfile(OLD24 / "time.npy", dest / "time.npy")
    shutil.copyfile(OLD24 / "samples.csv", dest / "samples_source.csv")
    config = oldmeta["source_metadata_gpu"]["fixture_provenance"]["dataset_config"].copy()
    config["widths"] = [80]
    dump(dest / "official_dataset_config.json", config)
    dump(dest / "conditions.json", conditions)
    for name, e in all_readouts.items():
        p = Path(e["source"]["path"])
        new = dest / "readouts" / p.name
        shutil.copyfile(p, new)
        e["prepared"] = entry(new)
    for name in CANDIDATES:
        for suffix in ["_H_ids.npy", "_HR_edge_ids.npy", "_direct_R_targets.npy"]:
            shutil.copyfile(SPEC / (name + suffix), dest / "operator_ids" / (name + suffix))
        path = dest / "readouts" / (name + "_direct_common_visual_R_ids.npy")
        np.save(path, structural_secondary[name])
        all_readouts[name + "_direct_common_visual_R"] = dict(
            n=len(structural_secondary[name]), prepared=entry(path),
            selection="intersection(original HR target nodes, Phase3 common visual V); structural only",
            role="secondary candidate-specific localization; not primary cross-candidate ranking")
    shutil.copyfile(METRIC, dest / "metric_source/moving_bar_responses.py")
    official_functions = ["peak_responses", "get_time_masks", "time_window", "mask_between_seconds",
                          "direction_selectivity_index", "preferred_direction"]
    audit = dict(status="PASS_PREPARATION_DATA_CHECKS_ONLY", created_utc=datetime.now(timezone.utc).isoformat(),
        python=platform.python_version(), numpy=np.__version__, preparation_code=entry(__file__),
        evidence_level="READ_ONLY_IDENTITY_AND_STATIC_PARTITION_AUDIT_PLUS_FROZEN_FIXTURE_COPY",
        new_neural_updates=0, gpu_execution=False, FPGA_execution=False,
        previous_spec=entry(SPEC / "ABLATION_SPEC_v1.md"),
        previous_registration=entry(P3 / "PRE_RUN_REGISTRATION.json"), model=spec["model"],
        audited_sources=audited, candidates=candidate_info, readouts=all_readouts,
        fixture=dict(raw=entry(OLD24 / "stimulus.npy"), raw_dtype=str(raw.dtype),
            prepared=entry(dest / "stimulus_float32.npy"), prepared_dtype=str(stim.dtype),
            shape=list(stim.shape), max_abs_cast_change=float(np.max(np.abs(raw-stim.astype(raw.dtype)))),
            time=entry(dest / "time.npy"), conditions=entry(dest / "conditions.json"),
            same_four_original_samples=[0,1,12,13], selected_four_bitwise_equal_G2=True,
            time_bitwise_equal_G2=True, stimulus_regenerated=False,
            saved_activity="activity_after[k]=a[k+1]; source time[k] labels paired with input[k]"),
        official_metrics=dict(source=entry(METRIC), snapshot=entry(dest / "metric_source/moving_bar_responses.py"),
            direct_functions=official_functions, implementation_changed=False, norm=None,
            response="raw activity, official rectification/motion mask; no baseline subtraction for official DSI/PD"),
        historical_24_Full_reuse=dict(eligible=False, inspected_artifact=entry(OLD24 / "activity_central.npy"),
            shape=list(hist.shape), reason=["only 65 centers saved, not all 45669 nodes",
            "same checkpoint is insufficient: no matching frozen full a0 or expanded parameter identity supplied"],
            required="one shared all-node Full trajectory per reference repeat under this exact stimulus/a0/native GPU profile"),
        formal_24_execution_status="NOT_RUN_PENDING_ARCH_REVIEW_AND_USER_GPU_SLOT")
    dump(HERE / "SOURCE_AUDIT.json", audit)
    print(json.dumps(dict(status=audit["status"], stimulus_sha256=audit["fixture"]["prepared"]["sha256"],
        cast_max=audit["fixture"]["max_abs_cast_change"], new_neural_updates=0,
        candidates={k:dict(n_H=v["n_H"], n_direct_common_visual_R=v["n_direct_common_visual_R"]) for k,v in candidate_info.items()}), ensure_ascii=False))


if __name__ == "__main__":
    main()

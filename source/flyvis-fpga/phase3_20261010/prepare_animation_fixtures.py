#!/usr/bin/env python3
"""Receive B's sealed actual 800-step animation data and derive integer vectors."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from numeric_profile_sweep import load_graph, qencode, run_profile, check_range
from prepare_hls_fixtures import sha256, oracle_one, write_bin, STATE_FRAC, STATE_WIDTH

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
B = REPO / "flyvis-circuit-selection/phase3_20261010"
REF = B / "c_reference"
OUT = HERE / "testdata_animation_q22"


def main() -> None:
    handoff = json.loads((REF / "C_REFERENCE_HANDOFF.json").read_text(encoding="utf-8"))
    manifest = json.loads((REF / "artifact_manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        path = REF / entry["path"]
        if path.stat().st_size != entry["bytes"] or sha256(path) != entry["sha256"]:
            raise ValueError(f"B manifest mismatch: {path}")
    static = B / "input_bundle/static_boundary_gpu_native.npz"
    vectors = REF / "SOURCE_RAW_step_io.npz"
    if sha256(static) != handoff["circuit_sha256"] or sha256(vectors) != handoff["vectors_sha256"]:
        raise ValueError("B circuit/vector identity mismatch")
    s, raw, edge_id, src, dst, weight, is_boundary = load_graph(static, vectors)
    for key, shape in (("old_H", (800, 67)), ("x_H", (800, 67)),
                       ("boundary_before", (800, 1364)), ("new_H_expected", (800, 67))):
        if raw[key].shape != shape or raw[key].dtype != np.float32 or not np.isfinite(raw[key]).all():
            raise ValueError(f"Invalid animation field {key}")
    if not np.array_equal(raw["step_id"], np.arange(800)):
        raise ValueError("Animation step order is not 0..799")
    if not np.array_equal(raw["H_global_ids"], s["global_node_id"]):
        raise ValueError("H global ordering mismatch")
    if not np.array_equal(raw["incoming_source_global_ids"], s["incoming_source_global_node_id"]):
        raise ValueError("SOURCE_RAW global ordering mismatch")
    if raw["dt_s"].view(np.uint32) != np.float32(0.005).view(np.uint32):
        raise ValueError("Animation dt mismatch")
    if not np.allclose(raw["input_time"], np.arange(800) * 0.005, rtol=0, atol=1e-12):
        raise ValueError("Animation input clock mismatch")
    if not np.allclose(raw["activity_time"], (np.arange(800) + 1) * 0.005, rtol=0, atol=1e-12):
        raise ValueError("Animation activity clock mismatch")
    with (REF / "edges_HH_RH_original_order.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 6537:
        raise ValueError("Animation edge count mismatch")
    for e, row in enumerate(rows):
        expected_array = "boundary_before" if is_boundary[e] else "old_H"
        globals_src = s["incoming_source_global_node_id"] if is_boundary[e] else s["global_node_id"]
        if (int(row["original_edge_id"]) != int(edge_id[e])
                or row["source_array"] != expected_array
                or int(row["source_local"]) != int(src[e])
                or int(row["target_H_local"]) != int(dst[e])
                or int(row["source_global"]) != int(globals_src[src[e]])
                or int(row["target_global"]) != int(s["global_node_id"][dst[e]])
                or int(row["weight_ieee754_hex"], 16) != int(weight[e].view(np.uint32))):
            raise ValueError(f"B edge export mismatch at row {e}")
    with (REF / "H_parameters.csv").open(newline="", encoding="utf-8") as f:
        hrows = list(csv.DictReader(f))
    if len(hrows) != 67:
        raise ValueError("B H parameter export row count mismatch")
    for h, row in enumerate(hrows):
        for column, key in (("bias_ieee754_hex", "bias"),
                            ("time_const_s_ieee754_hex", "time_const_s"),
                            ("inverse_tau_ieee754_hex", "inv_max_tau_dt")):
            if int(row[column], 16) != int(s[key][h].view(np.uint32)):
                raise ValueError(f"B H parameter mismatch at H={h}, {column}")
    t = {key: raw[key][None, ...] for key in ("old_H", "x_H", "boundary_before", "new_H_expected")}
    t["dt_s"] = raw["dt_s"]
    OUT.mkdir(parents=True, exist_ok=True)
    profiles = []
    oracle = None
    for frac in (22, 24):
        profile = run_profile(s, t, src, dst, weight, is_boundary, frac)
        outputs = profile.pop("oracle_outputs")[0]
        np.save(OUT / f"oracle_q{frac}.npy", outputs, allow_pickle=False)
        profiles.append(profile)
        if frac == STATE_FRAC:
            oracle = outputs
    assert oracle is not None
    bq = qencode(raw["boundary_before"], STATE_FRAC)
    oldq = qencode(raw["old_H"], STATE_FRAC)
    xq = qencode(raw["x_H"], STATE_FRAC)
    requests = np.concatenate((bq, oldq, xq), axis=1)
    check_range(requests, STATE_WIDTH, "animation requests")
    # Perturb a real active boundary source while keeping the same old_H/x_H.
    control_index = None
    control_output = None
    candidates = sorted(np.flatnonzero(is_boundary & (weight > 0)),
                        key=lambda e: float(bq[0, src[e]]) * float(weight[e]), reverse=True)
    for e in candidates:
        if bq[0, src[e]] <= 0:
            continue
        probe = bq[0].copy()
        probe[src[e]] += 1 << (STATE_FRAC - 2)
        result = oracle_one(s, src, dst, weight, is_boundary, raw["old_H"][0], raw["x_H"][0],
                            probe.astype(np.float64) / (1 << STATE_FRAC))
        if np.any(result != oracle[0]):
            control_index = int(src[e])
            control_output = result
            control_request = np.concatenate((probe, oldq[0], xq[0]))
            break
    if control_index is None:
        raise ValueError("Animation boundary perturbation had no effect")
    requests = np.vstack((requests, control_request))
    expected = np.vstack((oracle, control_output))
    write_bin(OUT / "requests_i32le.bin", requests)
    write_bin(OUT / "expected_i32le.bin", expected)
    with (OUT / "request_map.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(("request_id", "condition_id", "step_id", "purpose"))
        for k in range(800):
            w.writerow((k, "01_off_right", k, "actual B animation H request"))
        w.writerow((800, "01_off_right", 0, f"negative control +0.25 boundary[{control_index}]"))
    report = {
        "status": "PASS_B_REFERENCE_IDENTITY_AND_FIXED_POINT_VECTOR_PREPARATION",
        "evidence_level": "SOFTWARE_INTEGER_ORACLE_AND_DATA_IDENTITY_ONLY",
        "comparison_id": handoff["comparison_id"],
        "condition_id": "01_off_right", "steps": 800,
        "manifest_files_verified": len(manifest["files"]),
        "circuit_sha256": sha256(static), "vectors_sha256": sha256(vectors),
        "handoff_sha256": sha256(REF / "C_REFERENCE_HANDOFF.json"),
        "edge_rows_verified": 6537, "HH": 970, "RH": 5567,
        "source": "Actual B Python-H/GPU-R closed-loop requests; replay supplies explicit reference old_H for each step.",
        "profiles": profiles,
        "scientific_acceptance": "PENDING_ARCHITECTURE_REVIEW; absolute 1e-5 shown only as engineering screen",
        "request_sha256": sha256(OUT / "requests_i32le.bin"),
        "expected_sha256": sha256(OUT / "expected_i32le.bin"),
        "request_shape": list(requests.shape), "expected_shape": list(expected.shape),
        "boundary_perturb_index": control_index,
        "boundary_perturb_changed_H": int(np.count_nonzero(control_output != oracle[0])),
        "RTL_execution": False, "board_execution": False,
    }
    (OUT / "fixture_manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

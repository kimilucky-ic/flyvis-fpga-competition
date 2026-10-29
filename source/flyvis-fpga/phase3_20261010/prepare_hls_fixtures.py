#!/usr/bin/env python3
"""Build fixed-point constant ROMs and stateless H STEP vectors for HLS/C-RTL."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from numeric_profile_sweep import load_graph, qencode, round_shift, run_profile, check_range  # noqa: E402

STATE_FRAC = 22
STATE_WIDTH = 29
WEIGHT_FRAC = 20
WEIGHT_WIDTH = 22
INPUT_WORDS = 1364 + 67 + 67
REPLAY_STEPS_PER_CONDITION = 200


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def signed_initializer(values: np.ndarray, width: int) -> str:
    check_range(np.asarray(values, dtype=np.int64), width, "HLS ROM constant")
    return ",\n    ".join(str(int(v)) for v in values)


def unsigned_initializer(values: np.ndarray, width: int) -> str:
    array = np.asarray(values, dtype=np.int64)
    if array.size and (int(array.min()) < 0 or int(array.max()) >= (1 << width)):
        raise OverflowError(f"HLS ROM constant exceeds unsigned {width}-bit range")
    return ",\n    ".join(str(int(v)) for v in array)


def oracle_one(s, edge_src, edge_dst, edge_weight, edge_is_boundary,
               old_f, x_f, boundary_f) -> np.ndarray:
    old_q = qencode(np.asarray(old_f, dtype=np.float32), STATE_FRAC)
    x_q = qencode(np.asarray(x_f, dtype=np.float32), STATE_FRAC)
    b_q = qencode(np.asarray(boundary_f, dtype=np.float32), STATE_FRAC)
    w_q = qencode(edge_weight, WEIGHT_FRAC)
    chemical = np.zeros(67, dtype=np.int64)
    for e in range(edge_dst.size):
        src = int(b_q[edge_src[e]]) if edge_is_boundary[e] else int(old_q[edge_src[e]])
        if src < 0:
            src = 0
        chemical[int(edge_dst[e])] += round_shift(src * int(w_q[e]), WEIGHT_FRAC)
    bias_q = qencode(s["bias"], STATE_FRAC)
    inv_q = qencode(s["inv_max_tau_dt"], STATE_FRAC)
    dt_q = int(qencode(np.asarray(0.005, dtype=np.float32), STATE_FRAC))
    drive = ((-old_q + bias_q) + chemical) + x_q
    velocity = np.asarray([round_shift(int(a) * int(b), STATE_FRAC)
                           for a, b in zip(inv_q, drive)], dtype=np.int64)
    delta = np.asarray([round_shift(int(a) * dt_q, STATE_FRAC) for a in velocity], dtype=np.int64)
    result = old_q + delta
    check_range(result, STATE_WIDTH, "negative-control output")
    return result.astype(np.int64)


def write_bin(path: Path, values: np.ndarray) -> None:
    np.asarray(values, dtype="<i4").tofile(path)


def main() -> None:
    data = ROOT / "flyvis-circuit-selection/phase2_20261010/artifacts/native_gpu_step_io"
    out = HERE / "testdata_q22"
    out.mkdir(parents=True, exist_ok=True)
    s, t, edge_id, edge_src, edge_dst, edge_weight, edge_is_boundary = load_graph(
        data / "static_boundary_gpu_native.npz", data / "SOURCE_RAW_step_io.npz")
    profile = run_profile(s, t, edge_src, edge_dst, edge_weight, edge_is_boundary, STATE_FRAC)
    oracle_all = profile.pop("oracle_outputs")

    # Select 200 explicit stateless H requests from each of the four accepted G2 conditions.
    selected = [(condition, step) for condition in range(4)
                for step in range(REPLAY_STEPS_PER_CONDITION)]
    requests: list[np.ndarray] = []
    expected: list[np.ndarray] = []
    map_rows: list[dict[str, int | str]] = []
    for request_id, (condition, step) in enumerate(selected):
        b = qencode(t["boundary_before"][condition, step], STATE_FRAC)
        old = qencode(t["old_H"][condition, step], STATE_FRAC)
        x_h = qencode(t["x_H"][condition, step], STATE_FRAC)
        check_range(b, STATE_WIDTH, "source_raw input")
        check_range(old, STATE_WIDTH, "old_H input")
        check_range(x_h, STATE_WIDTH, "x_H input")
        requests.append(np.concatenate((b, old, x_h)).astype(np.int64))
        expected.append(oracle_all[condition, step])
        map_rows.append({"request_id": request_id, "condition_index": condition,
                         "original_sample": int(t["condition_original_samples"][condition]),
                         "step_id": int(t["step_id"][step]), "purpose": "G2 SOURCE_RAW replay"})

    # Boundary perturbation negative control: add +0.25 to the strongest active positive RH source.
    base_b = qencode(t["boundary_before"][0, 0], STATE_FRAC)
    base_old = qencode(t["old_H"][0, 0], STATE_FRAC)
    base_x = qencode(t["x_H"][0, 0], STATE_FRAC)
    rh_candidates = np.flatnonzero(edge_is_boundary & (edge_weight > 0))
    rh_candidates = sorted(rh_candidates,
                           key=lambda e: float(base_b[edge_src[e]]) * float(edge_weight[e]),
                           reverse=True)
    control_output = None
    control_index = None
    for e in rh_candidates:
        if base_b[edge_src[e]] <= 0:
            continue
        probe = base_b.copy()
        probe[edge_src[e]] += 1 << (STATE_FRAC - 2)
        candidate = oracle_one(s, edge_src, edge_dst, edge_weight, edge_is_boundary,
                               t["old_H"][0, 0], t["x_H"][0, 0],
                               probe.astype(np.float64) / (1 << STATE_FRAC))
        if np.any(candidate != oracle_all[0, 0]):
            control_output = candidate
            control_index = int(edge_src[e])
            base_b = probe
            break
    if control_output is None:
        raise RuntimeError("boundary perturbation did not change the fixed-point H output")
    requests.append(np.concatenate((base_b, base_old, base_x)).astype(np.int64))
    expected.append(control_output)
    map_rows.append({"request_id": len(requests) - 1, "condition_index": 0,
                     "original_sample": int(t["condition_original_samples"][0]),
                     "step_id": 0, "purpose": "negative control: +0.25 on RH boundary source index " + str(control_index)})

    request_array = np.stack(requests).astype(np.int32)
    expected_array = np.stack(expected).astype(np.int32)
    write_bin(out / "requests_i32le.bin", request_array)
    write_bin(out / "expected_i32le.bin", expected_array)
    with (out / "request_map.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(map_rows[0]))
        writer.writeheader()
        writer.writerows(map_rows)

    edge_src_encoded = np.where(edge_is_boundary, edge_src, (1 << 11) | edge_src)
    header = HERE / "hls" / "flyvis_t5c_constants_q22.hpp"
    header.parent.mkdir(parents=True, exist_ok=True)
    header.write_text(
        "#pragma once\n#include <ap_int.h>\n\n"
        "static const int FLYVIS_EDGE_COUNT = 6537;\n"
        "static const int FLYVIS_H_COUNT = 67;\n"
        "static const int FLYVIS_BOUNDARY_COUNT = 1364;\n"
        "static const int FLYVIS_STATE_FRAC = 22;\n"
        "static const int FLYVIS_WEIGHT_FRAC = 20;\n"
        "static const int FLYVIS_DT_Q22 = 20972;\n\n"
        "static const ap_uint<12> FLYVIS_EDGE_SRC[FLYVIS_EDGE_COUNT] = {\n    "
        + unsigned_initializer(edge_src_encoded, 12) + "\n};\n\n"
        "static const ap_uint<7> FLYVIS_EDGE_DST[FLYVIS_EDGE_COUNT] = {\n    "
        + unsigned_initializer(edge_dst, 7) + "\n};\n\n"
        "static const ap_int<22> FLYVIS_EDGE_WEIGHT_Q20[FLYVIS_EDGE_COUNT] = {\n    "
        + signed_initializer(qencode(edge_weight, WEIGHT_FRAC), WEIGHT_WIDTH) + "\n};\n\n"
        "static const ap_int<29> FLYVIS_BIAS_Q22[FLYVIS_H_COUNT] = {\n    "
        + signed_initializer(qencode(s["bias"], STATE_FRAC), STATE_WIDTH) + "\n};\n\n"
        "static const ap_int<29> FLYVIS_INVTau_Q22[FLYVIS_H_COUNT] = {\n    "
        + signed_initializer(qencode(s["inv_max_tau_dt"], STATE_FRAC), STATE_WIDTH) + "\n};\n",
        encoding="ascii")

    result = {
        "status": "FIXED_POINT_HLS_FIXTURES_PREPARED",
        "evidence_level": "DATA_PREPARATION_ONLY",
        "profile": {
            "name": "Q6.22 state / Q1.20 edge weight",
            "state_width": STATE_WIDTH, "state_fraction_bits": STATE_FRAC,
            "weight_width": WEIGHT_WIDTH, "weight_fraction_bits": WEIGHT_FRAC,
            "accumulator_width": 48,
            "rounding": "symmetric nearest, ties away from zero",
            "overflow": "fail-fast, no saturation",
            "screening": profile,
        },
        "fixture_identity": {
            "G2_result_sha256": "435debffde77acc753969fee8b1164bbe694401a50fe0153a87bd880edc68045",
            "static_sha256": "a915bd448e19ee6b83b7d0b8d11c913726a8dff6a5a4cebd03aa6f091154dade",
            "SOURCE_RAW_sha256": "6d2b2fa631a24929729dc827c953d02c4eee4105f6bf8507e06fdfe804b64186",
            "original_edge_order": "strict ascending global edge ID across HH and RH",
            "HH_edges": 970, "RH_edges": 5567,
        },
        "simulation_vectors": {
            "conditions": [0, 1, 12, 13],
            "requests_per_condition": REPLAY_STEPS_PER_CONDITION,
            "stateless_requests": 800,
            "negative_control_requests": 1,
            "words_per_request": INPUT_WORDS,
            "input_file_sha256": sha256(out / "requests_i32le.bin"),
            "expected_file_sha256": sha256(out / "expected_i32le.bin"),
            "request_map_sha256": sha256(out / "request_map.csv"),
            "constant_rom_header_sha256": sha256(header),
            "negative_control_boundary_index": control_index,
            "negative_control_output_changed": bool(np.any(control_output != oracle_all[0, 0])),
        },
    }
    (out / "fixture_manifest.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

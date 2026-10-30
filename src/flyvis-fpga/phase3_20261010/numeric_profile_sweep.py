#!/usr/bin/env python3
"""Independent integer oracle and exploratory Q-format sweep for FlyVis T5c."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


def round_away(x: np.ndarray | float) -> np.ndarray:
    a = np.asarray(x, dtype=np.float64)
    return np.where(a >= 0, np.floor(a + 0.5), np.ceil(a - 0.5)).astype(np.int64)


def round_shift(v: int, bits: int) -> int:
    if bits <= 0:
        return int(v) << (-bits)
    half = 1 << (bits - 1)
    if v >= 0:
        return (int(v) + half) >> bits
    return -(((-int(v)) + half) >> bits)


def qencode(values: np.ndarray, frac: int) -> np.ndarray:
    return round_away(np.asarray(values) * float(1 << frac))


def signed_bounds(width: int) -> tuple[int, int]:
    return -(1 << (width - 1)), (1 << (width - 1)) - 1


def check_range(values: np.ndarray, width: int, label: str) -> None:
    lo, hi = signed_bounds(width)
    if values.size and (int(values.min()) < lo or int(values.max()) > hi):
        raise OverflowError(f"{label} exceeds signed {width}-bit range")


def load_graph(static_path: Path, fixtures_path: Path):
    s = np.load(static_path, allow_pickle=False)
    t = np.load(fixtures_path, allow_pickle=False)
    b_ids = s["incoming_source_global_node_id"].astype(np.int64)
    b_index = {int(g): i for i, g in enumerate(b_ids)}
    if len(b_index) != 1364:
        raise ValueError("boundary source mapping is not unique")

    h_src = s["internal_source_local"].astype(np.int64)
    h_dst = s["internal_target_local"].astype(np.int64)
    h_edge = s["internal_edge_id"].astype(np.int64)
    h_weight = s["internal_weight"].astype(np.float32)
    # Map every RH edge's global source endpoint back to the unique boundary vector.
    r_src = np.asarray([b_index[int(g)] for g in s["incoming_source_index"]], dtype=np.int64)
    in_edges = s["incoming_edge_id"].astype(np.int64)
    in_dst = s["incoming_target_local"].astype(np.int64)
    in_weight = s["incoming_weight"].astype(np.float32)

    edge_id = np.concatenate((h_edge, in_edges))
    edge_src = np.concatenate((h_src, r_src))
    edge_dst = np.concatenate((h_dst, in_dst))
    edge_weight = np.concatenate((h_weight, in_weight))
    edge_is_boundary = np.concatenate((np.zeros(h_edge.size, dtype=np.bool_),
                                       np.ones(in_edges.size, dtype=np.bool_)))
    order = np.argsort(edge_id, kind="stable")
    edge_id, edge_src = edge_id[order], edge_src[order]
    edge_dst, edge_weight = edge_dst[order], edge_weight[order]
    edge_is_boundary = edge_is_boundary[order]
    if edge_id.size != 6537 or np.any(edge_id[1:] <= edge_id[:-1]):
        raise ValueError("expected 6,537 unique HH+RH edges in original edge-ID order")
    if np.any((edge_dst < 0) | (edge_dst >= 67)):
        raise ValueError("edge target outside H local range")
    return s, t, edge_id, edge_src, edge_dst, edge_weight, edge_is_boundary


def run_profile(s, t, edge_src, edge_dst, edge_weight, edge_is_boundary,
                state_frac: int, acc_width: int = 48):
    # State/boundary values use signed Q6.F; weights use signed Q1.(F-2).
    state_width = state_frac + 7
    weight_frac = state_frac - 2
    weight_width = weight_frac + 2
    old_float = t["old_H"].astype(np.float32)
    x_float = t["x_H"].astype(np.float32)
    boundary_float = t["boundary_before"].astype(np.float32)
    expected = t["new_H_expected"].astype(np.float32)

    weights_q = qencode(edge_weight, weight_frac)
    check_range(weights_q, weight_width, "edge coefficients")
    bias_q = qencode(s["bias"], state_frac)
    inv_tau_q = qencode(s["inv_max_tau_dt"], state_frac)
    dt_q = int(qencode(np.asarray(t["dt_s"], dtype=np.float32), state_frac))
    check_range(bias_q, state_width, "bias")
    check_range(inv_tau_q, state_width, "inverse tau")
    check_range(np.asarray([dt_q]), state_width, "dt")

    errors: list[np.ndarray] = []
    max_abs = 0.0
    total_sq = 0.0
    total_abs = 0.0
    total_n = 0
    edge_max_abs = 0.0
    max_chemical = 0.0
    max_state = 0.0
    replay_outputs: list[np.ndarray] = []

    for condition in range(old_float.shape[0]):
        for step in range(old_float.shape[1]):
            old_q = qencode(old_float[condition, step], state_frac)
            x_q = qencode(x_float[condition, step], state_frac)
            b_q = qencode(boundary_float[condition, step], state_frac)
            check_range(old_q, state_width, "old_H")
            check_range(x_q, state_width, "x_H")
            check_range(b_q, state_width, "source_raw")
            chemical = np.zeros(67, dtype=np.int64)
            for j in range(edge_dst.size):
                src = int(b_q[edge_src[j]]) if edge_is_boundary[j] else int(old_q[edge_src[j]])
                if src < 0:
                    src = 0
                term_q = round_shift(src * int(weights_q[j]), weight_frac)
                target = int(edge_dst[j])
                chemical[target] += term_q
                edge_max_abs = max(edge_max_abs, abs(term_q) / float(1 << state_frac))
            check_range(chemical, acc_width, "chemical accumulator")
            max_chemical = max(max_chemical, float(np.max(np.abs(chemical))) / (1 << state_frac))

            check_range(chemical, state_width, "chemical value")
            drive = ((-old_q + bias_q) + chemical) + x_q
            check_range(drive, state_width + 2, "Euler drive")
            velocity = np.asarray([round_shift(int(a) * int(b), state_frac)
                                   for a, b in zip(inv_tau_q, drive)], dtype=np.int64)
            check_range(velocity, state_width, "Euler velocity")
            delta = np.asarray([round_shift(int(a) * dt_q, state_frac)
                                for a in velocity], dtype=np.int64)
            new_q = old_q + delta
            check_range(new_q, state_width, "new_H")
            new_float = new_q.astype(np.float64) / float(1 << state_frac)
            error = np.abs(new_float - expected[condition, step].astype(np.float64))
            errors.append(error)
            max_abs = max(max_abs, float(np.max(error)))
            total_abs += float(np.sum(error))
            total_sq += float(np.sum(error * error))
            total_n += error.size
            max_state = max(max_state, float(np.max(np.abs(new_float))))
            replay_outputs.append(new_q.copy())

    all_errors = np.concatenate(errors)
    condition_errors = all_errors.reshape(old_float.shape)
    return {
        "state_width": state_width,
        "state_frac_bits": state_frac,
        "weight_width": weight_width,
        "weight_frac_bits": weight_frac,
        "accumulator_width": acc_width,
        "rounding": "symmetric round-to-nearest, ties away from zero",
        "overflow": "fail-fast; no saturation",
        "steps_checked": int(old_float.shape[0] * old_float.shape[1]),
        "H_values_checked": int(total_n),
        "max_abs_vs_float32_expected": max_abs,
        "mae_vs_float32_expected": total_abs / total_n,
        "rmse_vs_float32_expected": math.sqrt(total_sq / total_n),
        "count_over_1e-5": int(np.count_nonzero(all_errors > 1e-5)),
        "count_over_1e-5_plus_relative_1e-5": int(np.count_nonzero(
            all_errors > (1e-5 + 1e-5 * np.abs(expected.astype(np.float64).reshape(-1))))),
        "max_abs_rounded_edge_current": edge_max_abs,
        "max_abs_chemical": max_chemical,
        "max_abs_output_state": max_state,
        "oracle_outputs": np.stack(replay_outputs).reshape(old_float.shape).astype(np.int64),
        "max_abs_by_condition": [float(np.max(np.abs(condition_errors[c])))
                                 for c in range(old_float.shape[0])],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=Path(__file__).resolve().parents[2] /
        "flyvis-circuit-selection/phase2_20261010/artifacts/native_gpu_step_io")
    ap.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "artifacts")
    ap.add_argument("--frac-bits", type=int, nargs="+", default=[16, 18, 20, 22, 24])
    args = ap.parse_args()
    static_path = args.data / "static_boundary_gpu_native.npz"
    fixtures_path = args.data / "SOURCE_RAW_step_io.npz"
    s, t, edge_id, edge_src, edge_dst, edge_weight, edge_is_boundary = load_graph(
        static_path, fixtures_path)
    args.output.mkdir(parents=True, exist_ok=True)
    result = {
        "status": "EXPLORATORY_PROFILE_SWEEP",
        "evidence_level": "INDEPENDENT_FIXED_POINT_ORACLE_ON_ACCEPTED_G2_FLOAT32_STEP_FIXTURES",
        "fixture": {
            "static_sha256": "a915bd448e19ee6b83b7d0b8d11c913726a8dff6a5a4cebd03aa6f091154dade",
            "source_raw_sha256": "6d2b2fa631a24929729dc827c953d02c4eee4105f6bf8507e06fdfe804b64186",
            "original_edge_count": int(edge_id.size),
            "first_edge_id": int(edge_id[0]),
            "last_edge_id": int(edge_id[-1]),
            "conditions": [int(x) for x in t["condition_original_samples"]],
            "steps_per_condition": int(t["old_H"].shape[1]),
        },
        "profile_screening_threshold_note": "1e-5 and the existing relative rule are shown for engineering screening only; C scientific acceptance remains pending architecture review.",
        "profiles": [],
    }
    for frac in args.frac_bits:
        screened = run_profile(s, t, edge_src, edge_dst, edge_weight, edge_is_boundary, frac)
        outputs = screened.pop("oracle_outputs")
        result["profiles"].append(screened)
        if frac == max(args.frac_bits):
            np.save(args.output / f"source_raw_oracle_q{frac}.npy", outputs, allow_pickle=False)
    (args.output / "numeric_profile_sweep.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

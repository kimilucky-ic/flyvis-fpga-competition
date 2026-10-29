#!/usr/bin/env python3
"""Independent Q24/Q20 software reference for FlyVis H-subnetwork candidates.

This script reads frozen phase-3/ablation fixtures without editing them. It
reconstructs HH+RH using original global edge IDs, checks the float32 equation
against saved step I/O, then evaluates teacher-forced and internally recurrent
fixed-point updates. It is a software study, not an HLS/RTL implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
INPUT_BUNDLE = ROOT / "flyvis-circuit-selection" / "phase3_ablation_screen_20261010" / "input_bundle_r2"
SAVED_RUNS = ROOT / "flyvis-circuit-selection" / "phase3_ablation_screen_20261010" / "artifacts" / "formal_r2"
OUT = Path(__file__).resolve().parent / "artifacts" / "software_numeric_validation.json"

STATE_FRAC = 24
WEIGHT_FRAC = 20
STATE_WIDTH = 31
# T5c67's saved candidate uses 22 bits. The generalized phase-4 profile uses
# 24 bits because the preserved A/C weight tables contain values up to 4.1733.
WEIGHT_WIDTH = 24
ACC_WIDTH = 50
DRIVE_WIDTH = 33
ABS_TOL = 1e-5
REL_TOL = 1e-5


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def array_sha256(values: np.ndarray) -> str:
    array = np.ascontiguousarray(values)
    header = f"{array.dtype}{array.shape}".encode()
    return hashlib.sha256(header + array.tobytes()).hexdigest()


def round_away_float(values: np.ndarray | float, frac: int) -> np.ndarray:
    x = np.asarray(values, dtype=np.float64) * float(1 << frac)
    rounded = np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))
    return rounded.astype(np.int64)


def round_shift_scalar(value: int, shift: int) -> int:
    magnitude = abs(value)
    rounded = (magnitude + (1 << (shift - 1))) >> shift
    return -rounded if value < 0 else rounded


def round_shift_vector(values: np.ndarray, shift: int) -> np.ndarray:
    values = np.asarray(values, dtype=np.int64)
    magnitude = np.abs(values)
    rounded = (magnitude + np.int64(1 << (shift - 1))) >> shift
    return np.where(values < 0, -rounded, rounded).astype(np.int64)


def fits_signed(values: np.ndarray | int, width: int) -> bool | np.ndarray:
    lo, hi = -(1 << (width - 1)), (1 << (width - 1)) - 1
    if np.isscalar(values):
        return lo <= int(values) <= hi
    arr = np.asarray(values, dtype=np.int64)
    return (arr >= lo) & (arr <= hi)


def require_fits(values: np.ndarray, width: int, label: str) -> None:
    ok = np.asarray(fits_signed(values, width))
    if not bool(np.all(ok)):
        bad = np.asarray(values)[~ok]
        raise OverflowError(f"{label} exceeds signed {width}-bit range; count={bad.size}, sample={bad[:4].tolist()}")


def minimum_signed_width(values: np.ndarray) -> int:
    values = np.asarray(values, dtype=np.int64)
    for width in range(2, 64):
        if bool(np.all(fits_signed(values, width))):
            return width
    raise OverflowError("values do not fit signed 63-bit width")


def metric(reference: np.ndarray, candidate: np.ndarray) -> dict[str, Any]:
    ref = np.asarray(reference, dtype=np.float64)
    got = np.asarray(candidate, dtype=np.float64)
    error = np.abs(got - ref)
    threshold = ABS_TOL + REL_TOL * np.abs(ref)
    worst = int(np.argmax(error)) if error.size else 0
    return {
        "max_abs": float(np.max(error)) if error.size else 0.0,
        "rmse": float(np.sqrt(np.mean(np.square(got - ref)))) if error.size else 0.0,
        "max_relative_to_abs_plus_1e-6": float(np.max(error / (np.abs(ref) + 1e-6))) if error.size else 0.0,
        "over_initial_engineering_tolerance": int(np.count_nonzero(error > threshold)),
        "tolerance": "abs_error <= 1e-5 + 1e-5*abs(reference)",
        "flat_index_of_max_abs": worst,
    }


def float32_chemical(
    old_h: np.ndarray,
    boundary: np.ndarray,
    src_is_h: np.ndarray,
    src_local: np.ndarray,
    dst_local: np.ndarray,
    weights: np.ndarray,
) -> np.ndarray:
    source = np.empty(src_local.size, dtype=np.float32)
    source[src_is_h] = old_h[src_local[src_is_h]]
    source[~src_is_h] = boundary[src_local[~src_is_h]]
    released = np.maximum(source, np.float32(0.0))
    terms = np.multiply(weights, released, dtype=np.float32)
    chemical = np.zeros(old_h.size, dtype=np.float32)
    # np.add.at applies repeated-index updates in input order. The input edge
    # vectors have already been proven strictly ascending by original edge ID.
    np.add.at(chemical, dst_local, terms)
    return chemical


def fixed_step(
    old_h_q: np.ndarray,
    boundary_q: np.ndarray,
    x_h_q: np.ndarray,
    bias_q: np.ndarray,
    inv_tau_q: np.ndarray,
    src_is_h: np.ndarray,
    src_local: np.ndarray,
    dst_local: np.ndarray,
    weights_q: np.ndarray,
    dt_q: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    source = np.empty(src_local.size, dtype=np.int64)
    source[src_is_h] = old_h_q[src_local[src_is_h]]
    source[~src_is_h] = boundary_q[src_local[~src_is_h]]
    released = np.maximum(source, np.int64(0))
    products = released * weights_q
    terms = round_shift_vector(products, WEIGHT_FRAC)
    require_fits(terms, STATE_WIDTH, "rounded edge current")

    chemical = np.zeros(old_h_q.size, dtype=np.int64)
    np.add.at(chemical, dst_local, terms)
    require_fits(chemical, ACC_WIDTH, "chemical accumulator")
    require_fits(chemical, STATE_WIDTH, "chemical value consumed by Euler update")

    drive = -old_h_q + bias_q + chemical + x_h_q
    require_fits(drive, DRIVE_WIDTH, "Euler drive")
    velocity = round_shift_vector(inv_tau_q * drive, STATE_FRAC)
    require_fits(velocity, STATE_WIDTH, "Euler velocity")
    delta = round_shift_vector(velocity * np.int64(dt_q), STATE_FRAC)
    require_fits(delta, STATE_WIDTH, "Euler delta")
    candidate = old_h_q + delta
    require_fits(candidate, STATE_WIDTH, "new activity")
    return candidate, chemical, terms


def scalar_step_for_order_check(
    old_h_q: np.ndarray,
    boundary_q: np.ndarray,
    x_h_q: np.ndarray,
    bias_q: np.ndarray,
    inv_tau_q: np.ndarray,
    src_is_h: np.ndarray,
    src_local: np.ndarray,
    dst_local: np.ndarray,
    weights_q: np.ndarray,
    dt_q: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Slow edge-by-edge reference used to cross-check vector accumulation."""
    chemical = [0] * old_h_q.size
    for edge in range(weights_q.size):
        src = int(old_h_q[int(src_local[edge])] if src_is_h[edge] else boundary_q[int(src_local[edge])])
        term = round_shift_scalar(max(0, src) * int(weights_q[edge]), WEIGHT_FRAC)
        if not fits_signed(term, STATE_WIDTH):
            raise OverflowError(f"edge {edge} rounded current does not fit signed {STATE_WIDTH} bits")
        target = int(dst_local[edge])
        chemical[target] += term
        if not fits_signed(chemical[target], ACC_WIDTH):
            raise OverflowError(f"target {target} chemical overflow after ordered edge {edge}")

    candidate = []
    for h in range(old_h_q.size):
        chem = chemical[h]
        if not fits_signed(chem, STATE_WIDTH):
            raise OverflowError(f"target {h} chemical does not fit signed {STATE_WIDTH} bits")
        drive = -int(old_h_q[h]) + int(bias_q[h]) + chem + int(x_h_q[h])
        if not fits_signed(drive, DRIVE_WIDTH):
            raise OverflowError(f"target {h} drive does not fit signed {DRIVE_WIDTH} bits")
        velocity = round_shift_scalar(int(inv_tau_q[h]) * drive, STATE_FRAC)
        delta = round_shift_scalar(velocity * dt_q, STATE_FRAC)
        state = int(old_h_q[h]) + delta
        if not fits_signed(velocity, STATE_WIDTH) or not fits_signed(delta, STATE_WIDTH) or not fits_signed(state, STATE_WIDTH):
            raise OverflowError(f"target {h} Euler state overflow")
        candidate.append(state)
    return np.asarray(candidate, dtype=np.int64), np.asarray(chemical, dtype=np.int64)


def build_candidate(candidate: str, condition: str) -> tuple[dict[str, Any], dict[str, Any]]:
    cand_dir = INPUT_BUNDLE / "candidates" / candidate
    manifest_path = cand_dir / "candidate_manifest.json"
    partitions_path = cand_dir / "edge_partition_ids.npz"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    partition_arrays = np.load(partitions_path, allow_pickle=False)
    parameter_path = INPUT_BUNDLE / "expanded_parameters.npz"
    parameter_arrays = np.load(parameter_path, allow_pickle=False)
    io_path = SAVED_RUNS / candidate / "Sham" / condition / "SOURCE_RAW_step_io.npz"
    io_arrays = np.load(io_path, allow_pickle=False)

    h_ids = np.asarray(manifest["h_global_node_indices"], dtype=np.int64)
    boundary_ids = io_arrays["source_global_ids"].astype(np.int64, copy=False)
    if not np.all(np.diff(h_ids) > 0):
        raise ValueError(f"{candidate}: H global IDs are not strictly ascending")
    if not np.all(np.diff(boundary_ids) > 0):
        raise ValueError(f"{candidate}: boundary global IDs are not strictly ascending")
    if not np.array_equal(io_arrays["H_global_ids"], h_ids):
        raise ValueError(f"{candidate}: trajectory H ID sequence differs from frozen candidate manifest")

    hh_ids = np.asarray(partition_arrays["HH"], dtype=np.int64)
    rh_ids = np.asarray(partition_arrays["RH"], dtype=np.int64)
    if not np.array_equal(hh_ids, np.sort(hh_ids)) or not np.array_equal(rh_ids, np.sort(rh_ids)):
        raise ValueError(f"{candidate}: an edge partition is not in ascending original global edge ID order")
    if np.intersect1d(hh_ids, rh_ids).size:
        raise ValueError(f"{candidate}: HH and RH edge IDs overlap")
    edge_ids = np.sort(np.concatenate([hh_ids, rh_ids]))
    if not np.all(np.diff(edge_ids) > 0):
        raise ValueError(f"{candidate}: merged HH/RH sequence is not strictly ascending")

    params = {name: parameter_arrays[name] for name in parameter_arrays.files}
    if manifest.get("candidate_id") != candidate:
        raise ValueError(f"{candidate}: manifest candidate identity mismatch")
    if file_sha256(parameter_path) != manifest.get("expanded_parameters_sha256"):
        raise ValueError(f"{candidate}: expanded parameter bundle SHA does not match frozen manifest")
    if array_sha256(h_ids) != manifest.get("h_indices_digest"):
        raise ValueError(f"{candidate}: H global ID digest does not match frozen manifest")
    if hh_ids.size != manifest["partition_counts"]["HH"] or rh_ids.size != manifest["partition_counts"]["RH"]:
        raise ValueError(f"{candidate}: HH/RH array counts do not match frozen manifest")
    if not np.array_equal(params["original_edge_index"][edge_ids], edge_ids):
        raise ValueError(f"{candidate}: global edge indices do not index the frozen parameter bundle")
    src_global = params["source_global"][edge_ids].astype(np.int64, copy=False)
    dst_global = params["target_global"][edge_ids].astype(np.int64, copy=False)

    h_src = np.isin(src_global, h_ids)
    h_target = np.isin(dst_global, h_ids)
    if not bool(np.all(h_target)):
        raise ValueError(f"{candidate}: selected HH/RH edge has a target outside H")
    if not bool(np.all(np.where(np.isin(edge_ids, hh_ids), h_src, ~h_src))):
        raise ValueError(f"{candidate}: HH/RH partition does not match original source membership")
    if not np.array_equal(np.unique(src_global[~h_src]), boundary_ids):
        raise ValueError(f"{candidate}: saved boundary IDs do not equal the exact RH source set")

    h_local = np.searchsorted(h_ids, src_global[h_src]).astype(np.int64)
    b_local = np.searchsorted(boundary_ids, src_global[~h_src]).astype(np.int64)
    src_local = np.empty(edge_ids.size, dtype=np.int64)
    src_local[h_src] = h_local
    src_local[~h_src] = b_local
    dst_local = np.searchsorted(h_ids, dst_global).astype(np.int64)
    if np.any(dst_local >= h_ids.size) or np.any(h_ids[np.minimum(dst_local, h_ids.size - 1)] != dst_global):
        raise ValueError(f"{candidate}: target global-to-local mapping failed")

    # Hashes in the frozen manifest bind the graph to the previous all-edge audit.
    for name, ids in (("HH", hh_ids), ("RH", rh_ids)):
        expected = manifest["partition_ids_digests"][name]
        actual = array_sha256(ids)
        if actual != expected:
            raise ValueError(f"{candidate}: {name} edge-ID digest mismatch: {actual} != {expected}")

    weights = params["effective_weight"][edge_ids].astype(np.float32, copy=False)
    bias = params["bias"][h_ids].astype(np.float32, copy=False)
    tau = params["time_const"][h_ids].astype(np.float32, copy=False)
    dt = np.float32(io_arrays["dt_s"].item())
    inv_tau = np.divide(np.float32(1.0), np.maximum(tau, dt), dtype=np.float32)
    if not (np.all(np.isfinite(weights)) and np.all(np.isfinite(bias)) and np.all(np.isfinite(tau))):
        raise ValueError(f"{candidate}: non-finite parameter values")

    weights_q = round_away_float(weights, WEIGHT_FRAC)
    bias_q = round_away_float(bias, STATE_FRAC)
    inv_tau_q = round_away_float(inv_tau, STATE_FRAC)
    require_fits(weights_q, WEIGHT_WIDTH, "quantized weights")
    require_fits(bias_q, STATE_WIDTH, "quantized bias")
    require_fits(inv_tau_q, STATE_WIDTH, "quantized inverse time constants")
    dt_q = int(round_away_float(dt, STATE_FRAC))
    if dt_q != 83886:
        raise ValueError(f"{candidate}: unexpected Q24 dt encoding {dt_q}; expected 83886")

    details = {
        "candidate": candidate,
        "condition": condition,
        "n_h": int(h_ids.size),
        "n_boundary": int(boundary_ids.size),
        "n_hh": int(hh_ids.size),
        "n_rh": int(rh_ids.size),
        "n_total_h_inputs": int(edge_ids.size),
        "h_global_ids_sha256": array_sha256(h_ids),
        "boundary_global_ids_sha256": array_sha256(boundary_ids),
        "ordered_hh_edge_ids_sha256": array_sha256(hh_ids),
        "ordered_rh_edge_ids_sha256": array_sha256(rh_ids),
        "ordered_merged_edge_ids_sha256": array_sha256(edge_ids),
        "all_edge_ids_strictly_ascending": bool(np.all(np.diff(edge_ids) > 0)),
        "hh_rh_partition_disjoint": True,
        "edge_targets_all_in_h": True,
        "edge_sources_match_hh_rh_partition": True,
        "source_boundary_set_exact": True,
        "dt_s_float32": float(dt),
        "dt_q24": dt_q,
        "weight_min": float(np.min(weights)),
        "weight_max": float(np.max(weights)),
        "weight_q20_min_raw": int(np.min(weights_q)),
        "weight_q20_max_raw": int(np.max(weights_q)),
        "minimum_signed_weight_width_at_q20": minimum_signed_width(weights_q),
        "weight_values_not_fit_signed_22bit_at_q20": int(np.count_nonzero(~np.asarray(fits_signed(weights_q, 22)))),
        "weight_values_not_fit_signed_23bit_at_q20": int(np.count_nonzero(~np.asarray(fits_signed(weights_q, 23)))),
        "quantized_weight_width_bits": WEIGHT_WIDTH,
        "quantized_weight_fraction_bits": WEIGHT_FRAC,
        "quantized_weight_range": "signed 24-bit with 20 fractional bits; [-8, 8)",
        "tau_min": float(np.min(tau)),
        "tau_max": float(np.max(tau)),
        "source_files_sha256": {
            "candidate_manifest": file_sha256(manifest_path),
            "edge_partition_ids": file_sha256(partitions_path),
            "expanded_parameters": file_sha256(parameter_path),
            "step_io": file_sha256(io_path),
        },
    }
    data = {
        "h_ids": h_ids,
        "boundary_ids": boundary_ids,
        "edge_ids": edge_ids,
        "src_is_h": h_src,
        "src_local": src_local,
        "dst_local": dst_local,
        "weights": weights,
        "weights_q": weights_q,
        "bias": bias,
        "bias_q": bias_q,
        "inv_tau": inv_tau,
        "inv_tau_q": inv_tau_q,
        "dt": dt,
        "dt_q": dt_q,
        "io": io_arrays,
    }
    return details, data


def run_candidate(candidate: str, condition: str) -> dict[str, Any]:
    details, d = build_candidate(candidate, condition)
    io = d["io"]
    old_h = io["old_H"].astype(np.float32, copy=False)
    boundary = io["boundary_before"].astype(np.float32, copy=False)
    x_h = io["x_H"].astype(np.float32, copy=False)
    chemical_expected = io["chemical_expected"].astype(np.float32, copy=False)
    new_expected = io["new_H_expected"].astype(np.float32, copy=False)
    frames, n_h = old_h.shape
    if boundary.shape != (frames, details["n_boundary"]) or x_h.shape != old_h.shape or new_expected.shape != old_h.shape:
        raise ValueError(f"{candidate}/{condition}: incompatible step-I/O array shapes")
    if not np.array_equal(io["step_id"], np.arange(frames, dtype=np.int64)):
        raise ValueError(f"{candidate}/{condition}: step IDs are not a complete zero-based sequence")

    q_old_reference = round_away_float(old_h, STATE_FRAC)
    q_boundary = round_away_float(boundary, STATE_FRAC)
    q_x_h = round_away_float(x_h, STATE_FRAC)
    require_fits(q_old_reference, STATE_WIDTH, "quantized old_H inputs")
    require_fits(q_boundary, STATE_WIDTH, "quantized boundary inputs")
    require_fits(q_x_h, STATE_WIDTH, "quantized x_H inputs")

    float_chemical_all = np.empty_like(chemical_expected)
    q_teacher = np.empty_like(q_old_reference)
    q_recursive = np.empty_like(q_old_reference)
    q_teacher_chemical = np.empty_like(q_old_reference)
    q_recursive_chemical = np.empty_like(q_old_reference)
    max_term_abs = 0
    max_chemical_abs = 0
    max_q_activity_abs = 0
    order_check_done = False

    for step in range(frames):
        float_chemical_all[step] = float32_chemical(
            old_h[step], boundary[step], d["src_is_h"], d["src_local"], d["dst_local"], d["weights"]
        )
        q_candidate, q_chemical, terms = fixed_step(
            q_old_reference[step], q_boundary[step], q_x_h[step], d["bias_q"], d["inv_tau_q"],
            d["src_is_h"], d["src_local"], d["dst_local"], d["weights_q"], d["dt_q"]
        )
        q_teacher[step] = q_candidate
        q_teacher_chemical[step] = q_chemical
        max_term_abs = max(max_term_abs, int(np.max(np.abs(terms))) if terms.size else 0)
        max_chemical_abs = max(max_chemical_abs, int(np.max(np.abs(q_chemical))) if q_chemical.size else 0)
        max_q_activity_abs = max(max_q_activity_abs, int(np.max(np.abs(q_candidate))) if q_candidate.size else 0)
        if not order_check_done:
            scalar_candidate, scalar_chemical = scalar_step_for_order_check(
                q_old_reference[step], q_boundary[step], q_x_h[step], d["bias_q"], d["inv_tau_q"],
                d["src_is_h"], d["src_local"], d["dst_local"], d["weights_q"], d["dt_q"]
            )
            if not np.array_equal(q_candidate, scalar_candidate) or not np.array_equal(q_chemical, scalar_chemical):
                raise AssertionError(f"{candidate}/{condition}: vector fixed-point path differs from ordered scalar oracle")
            order_check_done = True

    # This is an independent implementation of the saved PPNeuronIGRSynapses
    # float32 operation order; stored traces are an independent comparison.
    float_drive = np.add(np.add(np.add(-old_h, d["bias"]), float_chemical_all), x_h)
    float_velocity = np.multiply(d["inv_tau"], float_drive, dtype=np.float32)
    float_new = np.add(old_h, np.multiply(float_velocity, d["dt"], dtype=np.float32))
    chemical_error = metric(chemical_expected, float_chemical_all)
    float_replay_error = metric(new_expected, float_new)

    recurrent_state = q_old_reference[0].copy()
    for step in range(frames):
        recurrent_state, q_chemical, terms = fixed_step(
            recurrent_state, q_boundary[step], q_x_h[step], d["bias_q"], d["inv_tau_q"],
            d["src_is_h"], d["src_local"], d["dst_local"], d["weights_q"], d["dt_q"]
        )
        q_recursive[step] = recurrent_state
        q_recursive_chemical[step] = q_chemical

    teacher_values = q_teacher.astype(np.float64) / float(1 << STATE_FRAC)
    recursive_values = q_recursive.astype(np.float64) / float(1 << STATE_FRAC)
    step_link_max = float(np.max(np.abs(old_h[1:].astype(np.float64) - new_expected[:-1].astype(np.float64)))) if frames > 1 else 0.0
    return {
        **details,
        "frame_count": int(frames),
        "model_semantics": {
            "dynamics": "PPNeuronIGRSynapses",
            "release": "ReLU on presynaptic old activity only",
            "edge_order": "ascending original global edge ID; full HH+RH sequence",
            "euler_order": "old + (inv_tau * (((-old + bias) + chemical) + x_H)) * dt",
            "teacher_forced": "each step consumes saved float32 old_H and external boundary_before",
            "internally_recurrent": "Q24 H state feeds its own next step; external boundary remains saved full-model trace",
            "board_or_rtl": False,
        },
        "checks": {
            "strict_scalar_vs_vector_first_step_exact": order_check_done,
            "float32_chemical_vs_saved": chemical_error,
            "float32_step_vs_saved": float_replay_error,
            "saved_old_to_new_step_link_max_abs": step_link_max,
        },
        "fixed_teacher_forced_vs_saved_float32": metric(new_expected, teacher_values),
        "fixed_internal_recurrence_vs_saved_float32": metric(new_expected, recursive_values),
        "fixed_point_peak_abs_raw": {
            "edge_term": max_term_abs,
            "chemical": max_chemical_abs,
            "activity": max_q_activity_abs,
        },
        "numeric_acceptance_status": "PASS_PRELIMINARY_ENGINEERING_SCREEN" if (
            metric(new_expected, teacher_values)["over_initial_engineering_tolerance"] == 0
            and metric(new_expected, recursive_values)["over_initial_engineering_tolerance"] == 0
        ) else "FAIL_PRELIMINARY_ENGINEERING_SCREEN",
        "scientific_numeric_acceptance": "NOT_ESTABLISHED",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", nargs="+", default=["B_T5c", "A_T4c", "C_T4T5_all_centers"])
    parser.add_argument("--conditions", nargs="+", default=["condition_00", "condition_01", "condition_02", "condition_03"])
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()

    started = time.perf_counter()
    results = []
    for candidate in args.candidates:
        for condition in args.conditions:
            results.append(run_candidate(candidate, condition))
            print(f"{candidate}/{condition}: {results[-1]['numeric_acceptance_status']}")

    output = {
        "schema": "flyvis-scalable-engine-software-validation/v1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "script_sha256": file_sha256(Path(__file__)),
        "evidence_level": "INDEPENDENT_SOFTWARE_NUMERIC_SIMULATION_AND_ORIGINAL_EDGE_ID_AUDIT",
        "fixed_point_profile": {
            "state": f"signed {STATE_WIDTH}-bit with {STATE_FRAC} fractional bits; range [-64,64)",
            "weight": f"signed {WEIGHT_WIDTH}-bit with {WEIGHT_FRAC} fractional bits; range [-8,8)",
            "accumulator_bits": ACC_WIDTH,
            "rounding": "symmetric round-to-nearest, ties away from zero",
            "overflow": "fail-fast; no saturation",
            "dt_q24": 83886,
            "screening_tolerance": "abs_error <= 1e-5 + 1e-5*abs(reference)",
        },
        "results": results,
        "elapsed_seconds": time.perf_counter() - started,
        "limits": [
            "No RTL simulation, HLS/Vivado synthesis, implementation, bitstream, or board execution was performed.",
            "The internally recurrent run uses saved full-model external boundary traces; it is not a closed-loop hybrid-network result.",
            "The tolerance is an inherited engineering screen, not scientific acceptance or model equivalence proof.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

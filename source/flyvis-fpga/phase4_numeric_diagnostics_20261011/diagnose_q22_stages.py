#!/usr/bin/env python3
"""Read-only Q22 stage attribution from the frozen Phase-4 trajectories.

The diagnostic is teacher-forced: each numerical variant receives the saved
Full-GPU a[k], fixed stimulus[k], official expanded parameters, and frozen
T5c graph. It does not write to either frozen run and is not a new comparison.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def round_away(x):
    a = np.asarray(x, dtype=np.float64)
    return np.where(a >= 0, np.floor(a + 0.5), np.ceil(a - 0.5)).astype(np.int64)


def round_shift_array(x: np.ndarray, shift: int) -> np.ndarray:
    """Signed nearest, ties-away-from-zero integer shift."""
    a = np.asarray(x, dtype=np.int64)
    mag = np.abs(a)
    return np.where(a >= 0, (mag + (1 << (shift - 1))) >> shift,
                    -((mag + (1 << (shift - 1))) >> shift)).astype(np.int64)


def signed_fit(x: np.ndarray, width: int, label: str) -> None:
    lo, hi = -(1 << (width - 1)), (1 << (width - 1)) - 1
    if np.any((x < lo) | (x > hi)):
        raise OverflowError(f"{label} outside signed {width}-bit range")


def metrics(err: np.ndarray, scale: int) -> dict:
    e = np.asarray(err, dtype=np.float64)
    return {
        "max_abs": float(np.max(np.abs(e))),
        "mae": float(np.mean(np.abs(e))),
        "rmse": float(np.sqrt(np.mean(e * e))),
        "max_abs_q22_lsb": float(np.max(np.abs(e)) * (1 << 22)),
        "rmse_q22_lsb": float(np.sqrt(np.mean(e * e)) * (1 << 22)),
        "nonzero_count": int(np.count_nonzero(e)),
        "samples": int(e.size),
        "diagnostic_state_scale": int(scale),
    }


def make_input_h(input_ids: np.ndarray, h_ids: np.ndarray, frame: np.ndarray) -> np.ndarray:
    h_map = {int(g): i for i, g in enumerate(h_ids)}
    out = np.zeros(len(h_ids), dtype=np.float64)
    for row in range(input_ids.shape[0]):
        for j, gid in enumerate(input_ids[row]):
            local = h_map.get(int(gid))
            if local is not None:
                out[local] = float(frame[j])
    return out


def build_graph(static_path: Path) -> dict:
    with np.load(static_path, allow_pickle=False) as z:
        s = {k: np.ascontiguousarray(z[k]) for k in z.files}
    h_ids = s["global_node_id"].astype(np.int64, copy=False)
    boundary_ids = s["incoming_source_global_node_id"].astype(np.int64, copy=False)
    bmap = {int(g): i for i, g in enumerate(boundary_ids)}
    h_src = s["internal_source_local"].astype(np.int64, copy=False)
    h_dst = s["internal_target_local"].astype(np.int64, copy=False)
    h_eid = s["internal_edge_id"].astype(np.int64, copy=False)
    h_w = s["internal_weight"].astype(np.float32, copy=False)
    r_src = np.asarray([bmap[int(g)] for g in s["incoming_source_index"]], dtype=np.int64)
    r_dst = s["incoming_target_local"].astype(np.int64, copy=False)
    r_eid = s["incoming_edge_id"].astype(np.int64, copy=False)
    r_w = s["incoming_weight"].astype(np.float32, copy=False)
    eids = np.concatenate((h_eid, r_eid))
    source = np.concatenate((h_src, r_src))
    target = np.concatenate((h_dst, r_dst))
    weight = np.concatenate((h_w, r_w))
    is_boundary = np.concatenate((np.zeros(len(h_eid), bool), np.ones(len(r_eid), bool)))
    order = np.argsort(eids, kind="stable")
    eids, source, target, weight, is_boundary = (x[order] for x in (eids, source, target, weight, is_boundary))
    if len(eids) != 6537 or np.any(eids[1:] <= eids[:-1]) or len(target) != len(eids):
        raise RuntimeError("frozen SOURCE_RAW edge list is malformed")
    return {"s": s, "h_ids": h_ids, "boundary_ids": boundary_ids, "src": source,
            "dst": target, "weight": weight, "is_boundary": is_boundary, "edge_id": eids}


def simulate_one(old_full: np.ndarray, frame: np.ndarray, graph: dict, input_ids: np.ndarray,
                 *, state_frac: int, state_width: int, weight_frac: int = 20,
                 accumulator: str = "rounded_per_edge", weight_mode: str = "q20",
                 inv_mode: str = "qstate", dt_frac: int | None = None,
                 euler_mode: str = "two_rounds", boundary_full: np.ndarray | None = None) -> np.ndarray:
    """One quantized H update; returns decoded float32 activity."""
    s = graph["s"]
    h_ids, b_ids = graph["h_ids"], graph["boundary_ids"]
    scale = 1 << state_frac
    src_h = round_away(old_full[h_ids].astype(np.float64) * scale)
    boundary_state = old_full if boundary_full is None else boundary_full
    src_b = round_away(boundary_state[b_ids].astype(np.float64) * scale)
    src_h = np.maximum(src_h, 0)
    src_b = np.maximum(src_b, 0)
    src = np.empty(len(graph["src"]), dtype=np.int64)
    bmask = graph["is_boundary"]
    src[bmask] = src_b[graph["src"][bmask]]
    src[~bmask] = src_h[graph["src"][~bmask]]
    wq = round_away(graph["weight"].astype(np.float64) * (1 << weight_frac))
    chem = np.zeros(len(h_ids), dtype=np.int64)
    if weight_mode == "q20":
        products = src * wq
        if accumulator == "rounded_per_edge":
            terms = round_shift_array(products, weight_frac)
            np.add.at(chem, graph["dst"], terms)
        elif accumulator == "wide_products":
            np.add.at(chem, graph["dst"], products)
            chem = round_shift_array(chem, weight_frac)
        else:
            raise ValueError(accumulator)
    elif weight_mode == "float32_weights":
        source_real = src.astype(np.float64) / scale
        terms_real = source_real * graph["weight"].astype(np.float64)
        if accumulator == "rounded_per_edge":
            np.add.at(chem, graph["dst"], round_away(terms_real * scale))
        elif accumulator == "wide_products":
            sums = np.zeros(len(h_ids), dtype=np.float64)
            np.add.at(sums, graph["dst"], terms_real)
            chem = round_away(sums * scale)
        else:
            raise ValueError(accumulator)
    else:
        raise ValueError(weight_mode)
    signed_fit(chem, state_width, "chemical")

    bias_q = round_away(s["bias"].astype(np.float64) * scale)
    old_h_q = round_away(old_full[h_ids].astype(np.float64) * scale)
    x_h = make_input_h(input_ids, h_ids, frame)
    x_q = round_away(x_h * scale)
    drive = -old_h_q + bias_q + chem + x_q
    dtf = 22 if dt_frac is None else dt_frac
    dt_q = int(round_away(np.asarray(0.005, dtype=np.float64) * (1 << dtf)))
    inv = s["inv_max_tau_dt"].astype(np.float64)

    if euler_mode == "two_rounds":
        if inv_mode == "qstate":
            inv_q = round_away(inv * scale)
            velocity = round_shift_array(inv_q * drive, state_frac)
        elif inv_mode == "float32":
            velocity = round_away((inv * (drive.astype(np.float64) / scale)) * scale)
        else:
            raise ValueError(inv_mode)
        delta = round_away((velocity.astype(np.float64) * dt_q) / (1 << dtf))
        new_codes = old_h_q + delta
    elif euler_mode == "single_round":
        if inv_mode == "qstate":
            inv_value = round_away(inv * scale).astype(np.float64) / scale
        elif inv_mode == "float32":
            inv_value = inv
        else:
            raise ValueError(inv_mode)
        dt_value = dt_q / float(1 << dtf)
        new_codes = round_away(old_h_q + inv_value * (drive.astype(np.float64) / scale) * dt_value * scale)
    else:
        raise ValueError(euler_mode)
    signed_fit(new_codes, state_width, "new H")
    return (new_codes.astype(np.float64) / scale).astype("<f4")


def summarize_by_variant(full: np.ndarray, initial: np.ndarray, graph: dict,
                         stim: np.ndarray, input_ids: np.ndarray) -> dict:
    h_ids = graph["h_ids"]
    target = full[:, h_ids]
    rows = {
        "Q22_frozen_arithmetic": dict(state_frac=22, state_width=29),
        "Q22_dt_Q30_only": dict(state_frac=22, state_width=29, dt_frac=30),
        "Q22_wide_product_accumulator": dict(state_frac=22, state_width=29, accumulator="wide_products"),
        "Q22_weight_Q24_only": dict(state_frac=22, state_width=29, weight_frac=24),
        "Q22_weight_Q24_and_dt_Q30": dict(state_frac=22, state_width=29, weight_frac=24, dt_frac=30),
        "Q22_weight_Q24_wide_products": dict(state_frac=22, state_width=29, weight_frac=24, accumulator="wide_products"),
        "Q22_float32_weights_only": dict(state_frac=22, state_width=29, weight_mode="float32_weights"),
        "Q22_float32_weights_and_wide_products": dict(state_frac=22, state_width=29, weight_mode="float32_weights", accumulator="wide_products"),
        "Q22_float32_inv_tau_only": dict(state_frac=22, state_width=29, inv_mode="float32"),
        "Q22_single_final_Euler_round": dict(state_frac=22, state_width=29, inv_mode="float32", euler_mode="single_round"),
        "Q24_state_same_per_edge_rounding": dict(state_frac=24, state_width=31, dt_frac=24),
        "Q24_state_Q30_dt_wide_products": dict(state_frac=24, state_width=31, dt_frac=30, accumulator="wide_products"),
    }
    output = {}
    for name, kwargs in rows.items():
        pred = np.empty_like(target, dtype="<f4")
        for k in range(800):
            old = initial if k == 0 else full[k - 1]
            pred[k] = simulate_one(old, stim[k], graph, input_ids, **kwargs)
        output[name] = metrics(pred.astype(np.float64) - target.astype(np.float64), kwargs["state_frac"])
        output[name]["change_vs_Q22_rmse_percent"] = None
    base = output["Q22_frozen_arithmetic"]["rmse"]
    for item in output.values():
        item["change_vs_Q22_rmse_percent"] = float((item["rmse"] / base - 1.0) * 100.0)
    return output


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--q22-root", type=Path, required=True, help="frozen artifacts/<comparison_id> directory")
    ap.add_argument("--phase3-bundle", type=Path, required=True)
    ap.add_argument("--static-path", type=Path, required=True)
    ap.add_argument("--out-root", type=Path, required=True)
    ap.add_argument("--name", default="q22_stage_attribution_r1")
    args = ap.parse_args()
    args.out_root.mkdir(parents=True, exist_ok=True)
    out = args.out_root / args.name
    out.mkdir(parents=False, exist_ok=False)
    q22_full = args.q22_root / "full_gpu_2f1de37f-59b5-47a8-a769-9b7c267fb651"
    q22_py = args.q22_root / "python_h_gpu_r_702bc7ad-c194-49f0-b2c0-123bdee26456"
    full = np.load(q22_full / "activities_full.npy", mmap_mode="r", allow_pickle=False)[0]
    py = np.load(q22_py / "activities_full.npy", mmap_mode="r", allow_pickle=False)[0]
    initial = np.load(q22_py / "initial_state_full_q22_hybrid.npy", allow_pickle=False)[0]
    stim = np.load(q22_full / "stimulus.npy", mmap_mode="r", allow_pickle=False)[0, :, 0]
    h_codes = np.load(q22_py / "H_candidate_codes_q22_i32.npy", mmap_mode="r", allow_pickle=False)
    with np.load(args.phase3_bundle / "expanded_parameters.npz", allow_pickle=False) as p:
        input_ids = np.ascontiguousarray(p["input_node_index"], dtype=np.int64)
    graph = build_graph(args.static_path)
    if full.shape != (800, 45669) or py.shape != full.shape or stim.shape != (800, 721):
        raise RuntimeError("frozen Q22 trajectory/stimulus shape mismatch")
    if not np.array_equal(np.load(q22_full / "H_global_ids.npy", allow_pickle=False), graph["h_ids"]):
        raise RuntimeError("frozen H node map differs from SOURCE_RAW graph")
    if np.any(np.isin(graph["h_ids"], input_ids)):
        raise RuntimeError("T5c input nodes are present; explicit x_H projection audit is required")

    started = time.perf_counter()
    variants = summarize_by_variant(full, initial, graph, stim, input_ids)
    elapsed = time.perf_counter() - started

    # Closed-loop H-only counterfactual: Q22 H state evolves, while every R
    # boundary sample is teacher-forced from Full a[k]. This isolates H's own
    # temporal accumulation from altered GPU-R state and R->H feedback.
    h_state = np.load(q22_py / "initial_state_H_q22_codes.npy", allow_pickle=False).astype(np.int64)
    h_loop = np.empty((800, len(graph["h_ids"])), dtype="<f4")
    for k in range(800):
        old = np.array(initial if k == 0 else full[k - 1], dtype="<f4", copy=True)
        old[graph["h_ids"]] = (h_state.astype(np.float64) / (1 << 22)).astype("<f4")
        h_loop[k] = simulate_one(old, stim[k], graph, input_ids,
                                 state_frac=22, state_width=29)
        h_state = round_away(h_loop[k].astype(np.float64) * (1 << 22))
    feedback_isolation = {}
    for n in (1, 32, 800):
        e = h_loop[:n].astype(np.float64) - full[:n, graph["h_ids"]].astype(np.float64)
        feedback_isolation[str(n)] = metrics(e, 22)

    # Recompute the production integer oracle from the Python trajectory.
    import sys
    phase4_src = Path("/mnt/c/Users/hzy72/Documents/ChatGPT/fly/gpu_phase4_q22_20261010")
    sys.path.insert(0, str(phase4_src))
    from integer_q22_h_backend import IntegerQ22HOracle, qencode
    backend = IntegerQ22HOracle(args.static_path, expected_static_sha256="a915bd448e19ee6b83b7d0b8d11c913726a8dff6a5a4cebd03aa6f091154dade")
    replay_mismatches = 0
    max_code_delta = 0
    for k in range(800):
        old = (initial if k == 0 else py[k - 1]).astype(np.float64)
        boundary = qencode(old[graph["boundary_ids"]], 22).astype("<i4")
        old_h = qencode(old[graph["h_ids"]], 22).astype("<i4")
        x_h = np.zeros(67, dtype="<i4")
        request = np.ascontiguousarray(np.concatenate((boundary, old_h, x_h)), dtype="<i4")
        got, status = backend.step_codes(request)
        if status != 0:
            raise RuntimeError(f"Q22 saved-trajectory replay returned status={status} at step {k}")
        delta = np.abs(got.astype(np.int64) - h_codes[k].astype(np.int64))
        replay_mismatches += int(np.count_nonzero(delta))
        max_code_delta = max(max_code_delta, int(np.max(delta)))
    if replay_mismatches:
        raise RuntimeError(f"frozen Q22 integer backend replay mismatched {replay_mismatches} H codes")

    report = {
        "schema": "flyvis-phase4-q22-stage-attribution/v1",
        "status": "PASS_FROZEN_INPUT_AUDIT_AND_STAGE_SENSITIVITY_COMPLETE",
        "evidence_level": "SOFTWARE_TEACHER_FORCED_NUMERICAL_SENSITIVITY_NO_NEW_COMPARISON_NO_PL",
        "frozen_comparison_id": args.q22_root.name,
        "source_hashes": {
            "full_run_manifest": sha_file(q22_full / "artifact_manifest.json"),
            "python_run_manifest": sha_file(q22_py / "artifact_manifest.json"),
            "static_candidate": sha_file(args.static_path),
            "expanded_parameters": sha_file(args.phase3_bundle / "expanded_parameters.npz"),
            "stimulus": sha_file(q22_full / "stimulus.npy"),
            "diagnostic_script": sha_file(Path(__file__)),
        },
        "frozen_integer_h_replay": {
            "steps": 800,
            "h_codes_compared": 800 * 67,
            "mismatches": replay_mismatches,
            "max_code_delta": max_code_delta,
            "meaning": "The saved Q22 H trajectory is exactly reproduced from its saved previous full state and the independent integer H backend.",
        },
        "local_full_state_teacher_forced_h_error": variants,
        "H_only_q22_closed_loop_with_full_R_boundaries": feedback_isolation,
        "elapsed_seconds_cpu": elapsed,
        "limits": {
            "not_a_closed_loop": True,
            "not_a_new_profile_or_comparison": True,
            "Q22_hardware_or_thresholds_modified": False,
            "Q24_metrics_are_reported_in_Q22_activity_LSB_equivalents": True,
            "all_variants_use_identical_saved_full_old_states_and_inputs": True,
        },
    }
    (out / "stage_attribution.json").write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    files = []
    for p in sorted(out.iterdir()):
        if p.is_file():
            files.append({"path": p.name, "bytes": p.stat().st_size, "sha256": sha_file(p)})
    (out / "artifact_manifest.json").write_text(json.dumps({"schema": "flyvis-phase4-q22-stage-attribution-manifest/v1", "files": files}, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(out), "elapsed_seconds_cpu": elapsed, "replay_mismatches": replay_mismatches, "variants": variants}, indent=2))


if __name__ == "__main__":
    main()

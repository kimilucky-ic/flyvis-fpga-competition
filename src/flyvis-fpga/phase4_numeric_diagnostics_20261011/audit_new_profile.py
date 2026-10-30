#!/usr/bin/env python3
"""Independent final identity, artifact, prefix, and drift audit for a new profile."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_hash(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def verify_manifest(root: Path) -> dict:
    manifest = json.loads((root / "artifact_manifest.json").read_text(encoding="utf-8"))
    errors = []
    for row in manifest.get("files", []):
        path = root / row["path"]
        if not path.is_file() or path.stat().st_size != row["bytes"] or sha_file(path) != row["sha256"]:
            errors.append(row["path"])
    if errors:
        raise RuntimeError(f"artifact manifest mismatch in {root}: {errors}")
    return manifest


def metric(ref: np.ndarray, out: np.ndarray) -> dict:
    e = out.astype(np.float64) - ref.astype(np.float64)
    rmse = float(np.sqrt(np.mean(e * e)))
    denominator = max(float(np.sqrt(np.mean(ref.astype(np.float64) ** 2))), 256 / (1 << 22))
    return {
        "max_abs": float(np.max(np.abs(e))), "rmse": rmse,
        "max_abs_q22_lsb": float(np.max(np.abs(e)) * (1 << 22)),
        "rmse_q22_lsb": rmse * (1 << 22), "relative_rmse": rmse / denominator,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile-dir", type=Path, required=True)
    ap.add_argument("--full-run", type=Path, required=True)
    ap.add_argument("--python-run", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    identity = json.loads((args.profile_dir / "comparison_identity.json").read_text(encoding="utf-8"))
    if canonical_hash({k: v for k, v in identity.items() if k != "comparison_id"}) != identity["comparison_id"]:
        raise RuntimeError("comparison identity canonical SHA mismatch")
    if sha_file(args.profile_dir / "numeric_profile.json") != identity["numeric_profile_sha256"]:
        raise RuntimeError("numeric profile SHA mismatch")
    for root in (args.profile_dir, args.full_run, args.python_run):
        verify_manifest(root)
    for run_dir in (args.full_run, args.python_run):
        for filename, key in (("initial_state_full.npy", "common_initial_state_sha256"), ("stimulus.npy", "stimulus_sha256"),
                              ("input_time.npy", "time_sha256"), ("activity_time.npy", "activity_time_sha256")):
            if sha_file(run_dir / filename) != identity[key]:
                raise RuntimeError(f"{run_dir.name} {filename} SHA mismatch")
        rid = json.loads((run_dir / "run_identity.json").read_text(encoding="utf-8"))
        if rid.get("comparison_id") != identity["comparison_id"] or rid.get("steps") != 800:
            raise RuntimeError(f"{run_dir.name} identity/step count mismatch")

    full = np.load(args.full_run / "activities_full.npy", mmap_mode="r", allow_pickle=False)[0]
    py = np.load(args.python_run / "activities_full.npy", mmap_mode="r", allow_pickle=False)[0]
    h_ids = np.load(args.profile_dir / "H_global_ids.npy", allow_pickle=False)
    r_ids = np.setdiff1d(np.arange(45669, dtype=np.int64), h_ids)
    if full.shape != py.shape or full.shape != (800, 45669):
        raise RuntimeError("activity trajectory shape mismatch")
    if not np.isfinite(full).all() or not np.isfinite(py).all():
        raise RuntimeError("nonfinite trajectory")
    statuses = np.load(args.python_run / "H_candidate_status_i32.npy", allow_pickle=False)
    codes = np.load(args.python_run / "H_candidate_codes_q22_i32.npy", allow_pickle=False)
    if statuses.shape != (800,) or np.any(statuses != 0) or codes.shape != (800, 67):
        raise RuntimeError("H candidate status/code trace invalid")
    decoded = (codes.astype(np.float64) / (1 << 22)).astype("<f4")
    if not np.array_equal(decoded.view("<u4"), py[:, h_ids].view("<u4")):
        raise RuntimeError("committed H activity does not decode from saved Q22 candidate codes")
    commits = [json.loads(line) for line in (args.python_run / "commit_log.jsonl").read_text(encoding="utf-8").splitlines()]
    committed = [x for x in commits if x.get("status") == "COMMITTED"]
    if len(committed) != 800 or any(x.get("native_H_update_count") != 0 for x in committed):
        raise RuntimeError("Python commit chain does not contain 800 H-zero R-only commits")

    gate_failures = []
    prefix_rows = []
    limits = identity["acceptance"]
    for n in (1, 32, 800):
        row = {"prefix_steps": n}
        for label, ids in (("H", h_ids), ("R", r_ids)):
            m = metric(full[:n, ids], py[:n, ids])
            row[label] = m
            if n == 32:
                max_lim, rmse_lim = limits[f"{label}_32_max_abs"], limits[f"{label}_32_RMSE"]
            elif n == 800:
                max_lim, rmse_lim = limits[f"{label}_800_max_abs"], limits[f"{label}_800_RMSE"]
            else:
                continue
            if m["max_abs"] > max_lim: gate_failures.append(f"{n}:{label}:max_abs")
            if m["rmse"] > rmse_lim: gate_failures.append(f"{n}:{label}:rmse")
            if m["relative_rmse"] > limits["population_relative_rmse_max"]: gate_failures.append(f"{n}:{label}:relative_rmse")
        prefix_rows.append(row)

    drift = {}
    for label, ids in (("H", h_ids), ("R", r_ids)):
        windows = []
        for start in range(0, 800, 32):
            windows.append(metric(full[start:start + 32, ids], py[start:start + 32, ids])["relative_rmse"])
        early = float(np.mean(windows[:8]))
        late = float(np.mean(windows[-8:]))
        limit = 2 * early + 2e-5
        passed = late <= limit
        drift[label] = {"window_steps": 32, "early_256_mean_relative_rmse": early,
                        "late_256_mean_relative_rmse": late, "limit": limit, "pass": passed}
        if not passed: gate_failures.append(f"drift:{label}")

    args.out_dir.mkdir(parents=True, exist_ok=False)
    result = {
        "schema": "flyvis-phase4-new-profile-final-audit/v1",
        "status": "PASS_NEW_PROFILE_SOFTWARE_FIDELITY_GATES" if not gate_failures else "FAIL_NEW_PROFILE_SOFTWARE_FIDELITY_GATES",
        "evidence_level": "INDEPENDENT_RECOMPUTATION_AND_MANIFEST_AUDIT_NO_PL",
        "comparison_id": identity["comparison_id"],
        "full_run_id": args.full_run.name.removeprefix("full_gpu_"),
        "python_run_id": args.python_run.name.removeprefix("python_q22h_q24w_dt30_gpu_r_"),
        "run_status": {"full_manifest_valid": True, "python_manifest_valid": True,
                       "exact_initial_and_input_hashes": True, "all_800_status_zero": True,
                       "H_codes_match_committed_activity": True, "commit_count": len(committed),
                       "native_H_update_count": 0, "FPGA_or_PL_execution": False, "board_io_operations": 0},
        "prefix_metrics": prefix_rows,
        "relative_rmse_drift": drift,
        "gate_failures": gate_failures,
        "thresholds_modified": False,
        "source_sha256": {"audit_script": sha_file(Path(__file__))},
    }
    (args.out_dir / "final_comparison_report.json").write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    manifest = {"schema": "flyvis-phase4-new-profile-final-audit-manifest/v1", "files": []}
    for path in sorted(args.out_dir.iterdir()):
        if path.is_file():
            manifest["files"].append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha_file(path)})
    (args.out_dir / "artifact_manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "comparison_id": result["comparison_id"],
                      "prefix_metrics": prefix_rows, "relative_rmse_drift": drift,
                      "gate_failures": gate_failures, "output": str(args.out_dir)}, indent=2))


if __name__ == "__main__":
    main()

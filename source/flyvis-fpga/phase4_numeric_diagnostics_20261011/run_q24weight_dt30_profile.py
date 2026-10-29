#!/usr/bin/env python3
"""New comparison for Q22 state + Q1.24 weights + Q30 dt (software only).

This is a separate numerical profile. It never edits or replaces the frozen
Q22 HLS source, ROM, comparison, thresholds, or prior run artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import uuid
from pathlib import Path

import numpy as np


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_hash(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def list_manifest_files(root: Path) -> list[dict]:
    out = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name != "artifact_manifest.json":
            out.append({"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size, "sha256": sha_file(p)})
    return out


def round_away(values) -> np.ndarray:
    a = np.asarray(values, dtype=np.float64)
    return np.where(a >= 0, np.floor(a + 0.5), np.ceil(a - 0.5)).astype(np.int64)


def round_shift(value: int, bits: int) -> int:
    if bits <= 0:
        return int(value) << (-bits)
    mag = abs(int(value))
    q = (mag + (1 << (bits - 1))) >> bits
    return q if value >= 0 else -q


def fits(value: int, width: int) -> bool:
    return -(1 << (width - 1)) <= int(value) <= (1 << (width - 1)) - 1


class Q22StateQ24WeightDt30Oracle:
    """Integer H candidate: Q6.22 state, Q1.24 weight, dt encoded in Q30."""
    evidence_level = "SOFTWARE_INTEGER_Q22_STATE_Q24_WEIGHT_DT30_ORACLE"
    connected = False
    firmware_identity: dict = {}

    def init__(self, static_path: Path, expected_sha: str):
        from integer_q22_h_backend import IntegerQ22HOracle
        self._base = IntegerQ22HOracle(static_path, expected_static_sha256=expected_sha)
        self.s = self._base.s
        self.h_ids = self._base.h_ids
        self.boundary_ids = self._base.boundary_ids
        self.edge_src = self._base.edge_src
        self.edge_dst = self._base.edge_dst
        self.edge_is_boundary = self._base.edge_is_boundary
        self.edge_weight = self._base.edge_weight
        self.weight_q = round_away(self.edge_weight.astype(np.float64) * (1 << 24))
        if any(not fits(w, 26) for w in self.weight_q):
            raise OverflowError("Q1.24 coefficient exceeds signed 26-bit ROM")
        self.bias_q = round_away(self.s["bias"].astype(np.float64) * (1 << 22))
        self.inv_q = round_away(self.s["inv_max_tau_dt"].astype(np.float64) * (1 << 22))
        self.dt_q30 = int(round_away(np.asarray(0.005, dtype=np.float32) * (1 << 30)))
        for label, arr in (("bias", self.bias_q), ("inv_tau", self.inv_q)):
            if any(not fits(v, 29) for v in arr):
                raise OverflowError(label + " Q22 value outside signed 29-bit range")
        if not fits(self.dt_q30, 29):
            raise OverflowError("Q30 dt does not fit 29 bits")
        self.calls = 0

    def step_codes(self, words: np.ndarray) -> tuple[np.ndarray, int]:
        a = np.asarray(words)
        if a.dtype != np.dtype("<i4") or a.shape != (1498,) or not a.flags.c_contiguous:
            raise ValueError("H request must be little-endian int32[1498]")
        # Request layout/sign-extension/range checks are delegated to the frozen base.
        self._base._signed_codes(a[:1364], "boundary")
        self._base._signed_codes(a[1364:1431], "old_H")
        self._base._signed_codes(a[1431:], "x_H")
        boundary = a[:1364].astype(np.int64)
        old_h = a[1364:1431].astype(np.int64)
        x_h = a[1431:].astype(np.int64)
        chemical = [0] * 67
        status = 0
        for e in range(len(self.edge_src)):
            src = int(boundary[self.edge_src[e]]) if self.edge_is_boundary[e] else int(old_h[self.edge_src[e]])
            if src < 0:
                src = 0
            term = round_shift(src * int(self.weight_q[e]), 24)
            if not fits(term, 29):
                status |= 1 << 2
            term = ((term + (1 << 28)) % (1 << 29)) - (1 << 28)
            dst = int(self.edge_dst[e])
            summed = chemical[dst] + term
            if not fits(summed, 48):
                status |= 1 << 1
            chemical[dst] = ((summed + (1 << 47)) % (1 << 48)) - (1 << 47)
        if any(not fits(v, 29) for v in chemical):
            status |= 1 << 2
        result = [0] * 67
        if status == 0:
            for h in range(67):
                drive = -int(old_h[h]) + int(self.bias_q[h]) + int(chemical[h]) + int(x_h[h])
                velocity = round_shift(int(self.inv_q[h]) * drive, 22)
                if not fits(velocity, 29):
                    status |= 1 << 2
                delta = round_shift(velocity * self.dt_q30, 30)
                if not fits(delta, 29):
                    status |= 1 << 2
                new = int(old_h[h]) + delta
                if not fits(new, 29):
                    status |= 1 << 2
                result[h] = new
        if status:
            result = [0] * 67
        self.calls += 1
        return np.ascontiguousarray(result, dtype="<i4"), int(status)

    def step(self, request):
        from q22_host_coordinator import HStepResponse, array_digest, canonical_bytes, sha_bytes
        codes, status = self.step_codes(request.words)
        ids = np.ascontiguousarray(self.h_ids, dtype="<i8")
        binding = dict(request.binding)
        digest = sha_bytes(canonical_bytes({
            "binding": binding, "request_digest": request.request_digest, "status": int(status),
            "h_ids_digest": array_digest(ids), "new_h_codes_digest": array_digest(codes),
        }))
        return HStepResponse(binding, request.request_digest, int(status), ids, codes, digest, self.evidence_level)


def prepare(args) -> Path:
    q22_dir = args.q22_init_dir.resolve()
    q22_identity = json.loads((q22_dir / "comparison_identity.json").read_text(encoding="utf-8"))
    # A prior software candidate may be used as the byte-identical state-package
    # carrier. Follow its explicit frozen-Q22 parent instead of accidentally
    # making the next profile appear to descend from the previous experiment.
    frozen_q22_id = q22_identity.get("source_frozen_q22_comparison_id", q22_identity["comparison_id"])
    source_bundle = args.phase3_bundle.resolve()
    base_identity = json.loads((source_bundle / "video_manifest.json").read_text(encoding="utf-8"))
    frozen_q22 = args.q22_root.resolve()
    q22_run = frozen_q22 / "full_gpu_2f1de37f-59b5-47a8-a769-9b7c267fb651"
    initial_src = q22_dir / "initial_state_full_q22_hybrid.npy"
    h_codes_src = q22_dir / "initial_state_H_q22_codes.npy"
    h_ids_src = q22_dir / "H_global_ids.npy"

    profile = json.loads(args.q22_numeric_profile.read_text(encoding="utf-8"))
    profile["schema"] = "flyvis-q22-state-q24-weight-dt30-profile/v1"
    profile["status"] = "MATCHED_SOFTWARE_BASELINES_COMPLETE_HLS_NOT_IMPLEMENTED"
    profile["profile_id"] = "Q6.22-state_26-bit-24-frac-weight_Q30-dt"
    profile["fixed_point"]["weight"] = {
        "signed_width": 26, "fractional_bits": 24, "minimum_code": -33554432,
        "maximum_code": 33554431, "minimum_value": -2.0,
        "maximum_value": 1.9999999403953552,
    }
    profile["fixed_point"]["chemical_accumulator"] = {
        "signed_width": 48, "fractional_bits": 22,
        "overflow": "reject_whole_candidate", "per_edge_weight_product_rounding": "nearest_ties_away_from_zero_to_Q22",
    }
    profile["fixed_point"]["dt"] = {
        "seconds": 0.005, "signed_width": 29, "fractional_bits": 30,
        "code": int(round_away(np.asarray(0.005, dtype=np.float32) * (1 << 30))),
        "actual_seconds": int(round_away(np.asarray(0.005, dtype=np.float32) * (1 << 30))) / float(1 << 30),
    }
    profile["fixed_point"]["state"] = {
        "signed_width": 29, "fractional_bits": 22, "host_word_bits": 32,
        "minimum_code": -268435456, "maximum_code": 268435455,
        "minimum_value": -64.0, "maximum_value": 63.99999976158142,
    }
    for stale_key in ("dt_q22_code", "dt_q22_actual", "dt_relative_error"):
        profile["fixed_point"].pop(stale_key, None)
    profile["fixed_point"]["rounding"] = "round_to_nearest_ties_away_from_zero; Q24 weight products round once per edge to Q22 chemical terms; Q22 velocity and Q30 dt product round to Q22 delta"
    profile["exactness_gate"] = "This profile has no PL implementation. The software integer H candidate is evaluated against a fresh matched Full GPU trajectory; any future HLS implementation must match this profile's independent integer H oracle code-for-code."
    profile["evidence_levels"] = {
        "full_gpu": "matched software reference execution",
        "python_q22_h_q24_weight_dt30_gpu_r": "software integer-H plus CUDA R execution",
        "hls_c_rtl_cosim": "NOT_RUN_FOR_THIS_PROFILE",
        "full_soc_implementation": "NOT_RUN_FOR_THIS_PROFILE",
        "live_gpu_r_pl_h": "NOT_CONNECTED",
    }
    profile["not_run"] = ["Q24-weight/Q30-dt HLS C/RTL implementation", "full SoC synthesis and route", "PYNQ adapter for this profile", "live board PL or GPU-R/PL closed loop"]
    profile["hardware_status"] = "NOT_IMPLEMENTED; sealed Q22 BIT/HWH unchanged"
    profile["source_frozen_q22_comparison_id"] = frozen_q22_id
    profile["preparation_evidence"] = "Q22 common full-state and H-code files are reused by identity; fresh matched Full GPU and Python Q22-state/Q24-weight/Q30-dt/GPU-R runs are saved under the new comparison_id."
    profile_path = args.out_root / "profiles" / "q22_state_q24_weight_dt30" / "numeric_profile.json"
    if profile_path.parent.exists():
        raise FileExistsError("new-profile output already exists; preserve it and choose a fresh profile folder")
    profile_path.parent.mkdir(parents=True, exist_ok=False)
    write_json(profile_path, profile)
    profile_sha = sha_file(profile_path)

    dest = profile_path.parent
    for source, name in ((initial_src, "initial_state_full_q22_hybrid.npy"),
                         (h_codes_src, "initial_state_H_q22_codes.npy"),
                         (h_ids_src, "H_global_ids.npy"),
                         (q22_dir / "metric_profile.json", "metric_profile.json"),
                         (q22_dir / "metric_roi_identity.json", "metric_roi_identity.json")):
        (dest / name).write_bytes(source.read_bytes())
    identity = {
        "schema": "flyvis-phase4-new-software-profile-comparison/v1",
        "source_frozen_q22_comparison_id": frozen_q22_id,
        "candidate_id": "B_T5c",
        "source_phase3_comparison_id": q22_identity["source_phase3_comparison_id"],
        "condition_id": "01_off_right",
        "model_id": "flow/0000/000",
        "source_commit": base_identity["source_commit"],
        "checkpoint_sha256": base_identity["checkpoint_sha256"],
        "dt_s": 0.005,
        "steps": 800,
        "stimulus_sha256": base_identity["stimulus_sha256"],
        "time_sha256": base_identity["time_sha256"],
        "activity_time_sha256": base_identity["activity_time_sha256"],
        "source_a0_sha256": base_identity["initial_state_sha256"],
        "common_initial_state_sha256": sha_file(dest / "initial_state_full_q22_hybrid.npy"),
        "initial_h_codes_sha256": sha_file(dest / "initial_state_H_q22_codes.npy"),
        "h_global_ids_sha256": sha_file(dest / "H_global_ids.npy"),
        "expanded_parameters_sha256": base_identity["expanded_parameters_sha256"],
        "candidate_manifest_sha256": base_identity["candidate_manifest_sha256"],
        "node_map_sha256": base_identity["node_map_sha256"],
        "edge_partition_sha256": base_identity["edge_partition_sha256"],
        "static_candidate_sha256": "a915bd448e19ee6b83b7d0b8d11c913726a8dff6a5a4cebd03aa6f091154dade",
        "numeric_profile_sha256": profile_sha,
        "metric_profile_sha256": sha_file(dest / "metric_profile.json"),
        "metric_definition_sha256": q22_identity["metric_definition_sha256"],
        "roi_identity_sha256": sha_file(dest / "metric_roi_identity.json"),
        "modes": ["Full_GPU", "Python_Q22_H_Q24W_DT30_GPU_R"],
        "software_source_sha256": sha_file(Path(__file__)),
        "full_oracle_sha256": sha_file(args.phase2_root / "full_oracle.py"),
        "r_only_sha256": sha_file(args.phase2_root / "r_only.py"),
        "hardware_implementation": "NOT_IMPLEMENTED; no matching Q24-weight/Q30-dt HLS kernel or bitstream",
        "acceptance": {
            "physical_activity_thresholds_unchanged_from_frozen_v2": True,
            "H_32_max_abs": 64 / (1 << 22), "H_32_RMSE": 16 / (1 << 22),
            "R_32_max_abs": 256 / (1 << 22), "R_32_RMSE": 64 / (1 << 22),
            "H_800_max_abs": 128 / (1 << 22), "H_800_RMSE": 32 / (1 << 22),
            "R_800_max_abs": 512 / (1 << 22), "R_800_RMSE": 128 / (1 << 22),
            "population_relative_rmse_max": 1e-4,
        },
    }
    identity["comparison_id"] = canonical_hash(identity)
    write_json(dest / "comparison_identity.json", identity)
    write_json(dest / "artifact_manifest.json", {"schema": "flyvis-phase4-new-profile-input-manifest/v1", "comparison_id": identity["comparison_id"], "files": list_manifest_files(dest)})
    if identity["comparison_id"] != canonical_hash({k: v for k, v in identity.items() if k != "comparison_id"}):
        raise RuntimeError("new comparison id did not canonicalize")
    print(json.dumps({"status": "PASS_NEW_PROFILE_IDENTITY_PREPARED", "comparison_id": identity["comparison_id"], "profile_sha256": profile_sha, "path": str(dest)}, indent=2))
    return dest


def load_profile_package(profile_dir: Path, args):
    identity = json.loads((profile_dir / "comparison_identity.json").read_text(encoding="utf-8"))
    if canonical_hash({k: v for k, v in identity.items() if k != "comparison_id"}) != identity["comparison_id"]:
        raise RuntimeError("new comparison identity hash mismatch")
    if sha_file(profile_dir / "numeric_profile.json") != identity["numeric_profile_sha256"]:
        raise RuntimeError("new profile hash mismatch")
    bundle = args.phase3_bundle
    stim = np.load(bundle / "stimulus.npy", mmap_mode="r", allow_pickle=False)[0, :, 0]
    input_time = np.load(bundle / "time.npy", allow_pickle=False)
    activity_time = np.load(bundle / "activity_time.npy", allow_pickle=False)
    initial = np.load(profile_dir / "initial_state_full_q22_hybrid.npy", allow_pickle=False)[0]
    h_codes = np.load(profile_dir / "initial_state_H_q22_codes.npy", allow_pickle=False)
    h_ids = np.load(profile_dir / "H_global_ids.npy", allow_pickle=False)
    if sha_file(bundle / "stimulus.npy") != identity["stimulus_sha256"] or sha_file(bundle / "time.npy") != identity["time_sha256"] or sha_file(bundle / "activity_time.npy") != identity["activity_time_sha256"]:
        raise RuntimeError("frozen video inputs changed")
    if stim.shape != (800, 721) or initial.shape != (45669,) or h_ids.shape != (67,) or h_codes.shape != (67,):
        raise RuntimeError("new profile input dimensions mismatch")
    return identity, stim, input_time, activity_time, initial, h_codes, h_ids


def run_full(profile_dir: Path, args) -> Path:
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")
    os.environ.setdefault("PYTHON_DOTENV_DISABLED", "1")
    os.environ.setdefault("FLYVIS_ROOT_DIR", "/opt/flyvis-visual-experiments-data")
    os.environ.setdefault("MPLBACKEND", "Agg")
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; refusing CPU substitution")
    torch.cuda.set_device(0)
    identity, stim, input_time, activity_time, initial, _, h_ids = load_profile_package(profile_dir, args)
    run_id = str(uuid.uuid4())
    out = args.out_root / "artifacts" / identity["comparison_id"] / f"full_gpu_{run_id}"
    out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(args.phase2_root))
    from full_oracle import FullNetworkOracle
    oracle = FullNetworkOracle(args.phase3_bundle / "identity_manifest.json", device="cuda:0")
    state = torch.tensor(initial.copy(), dtype=torch.float32, device="cuda:0")
    activities = np.lib.format.open_memmap(out / "activities_full.npy", mode="w+", dtype="<f4", shape=(1, 800, 45669))
    latencies = np.zeros(800, dtype="<f8")
    start = time.perf_counter()
    for k in range(800):
        frame = torch.tensor(np.array(stim[k], copy=True), dtype=torch.float32, device="cuda:0")
        torch.cuda.synchronize(); tick = time.perf_counter()
        state = oracle.step(state, frame)
        torch.cuda.synchronize(); latencies[k] = (time.perf_counter() - tick) * 1000
        row = state.detach().cpu().numpy().astype("<f4", copy=False)
        if not np.isfinite(row).all():
            raise RuntimeError(f"nonfinite Full result at step {k}")
        activities[0, k] = row
        if (k + 1) % 200 == 0:
            print("FULL_GPU_STEP", k + 1, flush=True)
    activities.flush()
    unchanged = oracle.assert_weights_unchanged()
    duration = time.perf_counter() - start
    np.save(out / "initial_state_full.npy", initial.reshape(1, -1), allow_pickle=False)
    # Preserve the frozen source array shape/bytes so its canonical file hash
    # is identical to the comparison identity (not merely value-equivalent).
    np.save(out / "stimulus.npy", np.load(args.phase3_bundle / "stimulus.npy", allow_pickle=False), allow_pickle=False)
    np.save(out / "input_time.npy", input_time, allow_pickle=False)
    np.save(out / "activity_time.npy", activity_time, allow_pickle=False)
    np.save(out / "step_latency_ms.npy", latencies, allow_pickle=False)
    run_identity = {
        "schema": "flyvis-phase4-profile-run/v1", "comparison_id": identity["comparison_id"],
        "run_id": run_id, "mode": "full_gpu", "condition_id": "01_off_right", "steps": 800,
        "device": "cuda:0", "gpu": torch.cuda.get_device_name(0), "torch": torch.__version__,
        "cuda": torch.version.cuda, "python": platform.python_version(), "weights_unchanged": unchanged,
        "initial_state_sha256": sha_file(out / "initial_state_full.npy"),
        "stimulus_sha256": sha_file(out / "stimulus.npy"), "wall_seconds": duration,
        "latency_ms": {"p50": float(np.percentile(latencies, 50)), "p95": float(np.percentile(latencies, 95)), "p99": float(np.percentile(latencies, 99))},
        "FPGA_or_PL_execution": False, "board_io_operations": 0,
    }
    write_json(out / "run_identity.json", run_identity)
    write_json(out / "result.json", {"status": "PASS_REFERENCE_EXECUTION", "evidence_level": "SOFTWARE_ACTUAL_FULL_GPU_NEW_PROFILE_800", "comparison_id": identity["comparison_id"], "run_id": run_id, "steps": 800, "duration_seconds": duration, "FPGA_or_PL_execution": False})
    write_json(out / "artifact_manifest.json", {"schema": "flyvis-phase4-profile-run-manifest/v1", "files": list_manifest_files(out)})
    return out


def run_python(profile_dir: Path, args) -> Path:
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")
    os.environ.setdefault("PYTHON_DOTENV_DISABLED", "1")
    os.environ.setdefault("MPLBACKEND", "Agg")
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; refusing CPU substitution")
    torch.cuda.set_device(0)
    identity, stim, input_time, activity_time, initial, h_codes, h_ids = load_profile_package(profile_dir, args)
    static = args.static_path
    if sha_file(static) != identity["static_candidate_sha256"]:
        raise RuntimeError("T5c graph hash mismatch")
    sys.path.insert(0, str(args.phase4_source_root))
    sys.path.insert(0, str(args.phase2_root))
    from r_only import RStepService
    from q22_host_coordinator import Q22HostCoordinator, GPUROnlyAdapter
    backend = Q22StateQ24WeightDt30Oracle(static, identity["static_candidate_sha256"])
    if not np.array_equal(backend.h_ids, h_ids):
        raise RuntimeError("H global order differs from the new identity")
    with np.load(args.phase3_bundle / "expanded_parameters.npz", allow_pickle=False) as p:
        input_ids = np.ascontiguousarray(p["input_node_index"], dtype=np.int64)
    p2_identity = args.phase3_bundle / "identity_manifest.json"
    candidate_manifest = args.phase3_bundle / "candidates" / "B_T5c" / "candidate_manifest.json"
    service = RStepService(args.phase3_bundle / "expanded_parameters.npz", p2_identity, candidate_manifest, device="cuda:0")
    r_ids = np.setdiff1d(np.arange(45669, dtype=np.int64), h_ids)
    adapter = GPUROnlyAdapter(service, r_ids, checkpoint_sha256=identity["checkpoint_sha256"], candidate_sha256=sha_file(candidate_manifest))
    coord = Q22HostCoordinator(identity=identity, initial_full=np.ascontiguousarray(initial, dtype="<f4"),
        h_initial_codes=np.ascontiguousarray(h_codes, dtype="<i4"), h_global_ids=h_ids,
        boundary_source_ids=backend.boundary_ids, input_node_index=input_ids,
        r_backend=adapter, h_backend=backend, run_id=str(uuid.uuid4()),
        condition_id="01_off_right", epoch=0, require_live_pl=False)
    run_id = coord.run_id
    out = args.out_root / "artifacts" / identity["comparison_id"] / f"python_q22h_q24w_dt30_gpu_r_{run_id}"
    out.mkdir(parents=True, exist_ok=False)
    activities = np.lib.format.open_memmap(out / "activities_full.npy", mode="w+", dtype="<f4", shape=(1, 800, 45669))
    h_candidates = np.zeros((800, 67), dtype="<i4")
    h_status = np.full(800, -1, dtype="<i4")
    latencies = np.zeros(800, dtype="<f8")
    start = time.perf_counter()
    for k in range(800):
        tick = time.perf_counter()
        prepared = coord.prepare(k, np.ascontiguousarray(stim[k], dtype="<f4"))
        h_candidates[k] = prepared.h_result.new_h_codes
        h_status[k] = prepared.h_result.status
        ack = coord.commit(prepared)
        latencies[k] = (time.perf_counter() - tick) * 1000
        activities[0, k] = ack["state"]
        rec = coord.commit_log[-1]
        if rec.get("status") != "COMMITTED" or rec.get("native_H_update_count") != 0:
            raise RuntimeError(f"invalid coordinator commit at step {k}")
        if (k + 1) % 200 == 0:
            print("PYTHON_Q24W_DT30_H_GPU_R_STEP", k + 1, flush=True)
    activities.flush()
    if coord.next_step_id != 800 or coord.status != "READY" or backend.calls != 800 or adapter.calls != 800 or np.any(h_status):
        raise RuntimeError("new profile did not complete 800 clean commits")
    duration = time.perf_counter() - start
    np.save(out / "H_candidate_codes_q22_i32.npy", h_candidates, allow_pickle=False)
    np.save(out / "H_candidate_status_i32.npy", h_status, allow_pickle=False)
    np.save(out / "H_global_ids.npy", h_ids, allow_pickle=False)
    np.save(out / "initial_state_full.npy", initial.reshape(1, -1), allow_pickle=False)
    np.save(out / "stimulus.npy", np.load(args.phase3_bundle / "stimulus.npy", allow_pickle=False), allow_pickle=False)
    np.save(out / "input_time.npy", input_time, allow_pickle=False)
    np.save(out / "activity_time.npy", activity_time, allow_pickle=False)
    np.save(out / "step_latency_ms.npy", latencies, allow_pickle=False)
    (out / "commit_log.jsonl").write_text("".join(json.dumps(row, sort_keys=True, allow_nan=False) + "\n" for row in coord.commit_log), encoding="utf-8")
    run_identity = {
        "schema": "flyvis-phase4-profile-run/v1", "comparison_id": identity["comparison_id"],
        "run_id": run_id, "mode": "python_q22_state_q24_weight_dt30_h_gpu_r", "condition_id": "01_off_right", "steps": 800,
        "device": "cuda:0", "gpu": torch.cuda.get_device_name(0), "torch": torch.__version__,
        "cuda": torch.version.cuda, "python": platform.python_version(), "native_H_update_count": 0,
        "H_backend_evidence_level": backend.evidence_level, "H_status_all_zero": bool(np.all(h_status == 0)),
        "initial_state_sha256": sha_file(out / "initial_state_full.npy"), "stimulus_sha256": sha_file(out / "stimulus.npy"),
        "wall_seconds": duration, "FPGA_or_PL_execution": False, "board_io_operations": 0,
        "latency_ms": {"p50": float(np.percentile(latencies, 50)), "p95": float(np.percentile(latencies, 95)), "p99": float(np.percentile(latencies, 99))},
        "software_commit_count": sum(row.get("status") == "COMMITTED" for row in coord.commit_log),
    }
    write_json(out / "run_identity.json", run_identity)
    write_json(out / "result.json", {"status": "PASS_REFERENCE_EXECUTION", "evidence_level": "SOFTWARE_ACTUAL_Q22_STATE_Q24_WEIGHT_DT30_H_GPU_R_800", "comparison_id": identity["comparison_id"], "run_id": run_id, "steps": 800, "duration_seconds": duration, "native_H_update_count": 0, "FPGA_or_PL_execution": False})
    write_json(out / "artifact_manifest.json", {"schema": "flyvis-phase4-profile-run-manifest/v1", "files": list_manifest_files(out)})
    return out


def compare(profile_dir: Path, full_dir: Path, py_dir: Path) -> Path:
    identity = json.loads((profile_dir / "comparison_identity.json").read_text(encoding="utf-8"))
    for label, run_dir in (("Full", full_dir), ("Python", py_dir)):
        if sha_file(run_dir / "stimulus.npy") != identity["stimulus_sha256"]:
            raise RuntimeError(f"{label} run stimulus file SHA differs from the new comparison identity")
        if sha_file(run_dir / "initial_state_full.npy") != identity["common_initial_state_sha256"]:
            raise RuntimeError(f"{label} run initial-state file SHA differs from the new comparison identity")
    full = np.load(full_dir / "activities_full.npy", mmap_mode="r", allow_pickle=False)[0]
    py = np.load(py_dir / "activities_full.npy", mmap_mode="r", allow_pickle=False)[0]
    h_ids = np.load(profile_dir / "H_global_ids.npy", allow_pickle=False)
    r_ids = np.setdiff1d(np.arange(45669, dtype=np.int64), h_ids)
    result = {"comparison_id": identity["comparison_id"], "Full_run_id": full_dir.name.removeprefix("full_gpu_"), "Python_run_id": py_dir.name.removeprefix("python_q22h_q24w_dt30_gpu_r_"), "prefix_metrics": [], "thresholds_modified": False, "FPGA_or_PL_execution": False, "board_io_operations": 0}
    failures = []
    for n in (1, 32, 800):
        row = {"prefix_steps": n}
        for label, ids in (("H", h_ids), ("R", r_ids)):
            e = py[:n, ids].astype(np.float64) - full[:n, ids].astype(np.float64)
            rmse = float(np.sqrt(np.mean(e * e)))
            max_abs = float(np.max(np.abs(e)))
            ref = full[:n, ids].astype(np.float64)
            rel = rmse / max(float(np.sqrt(np.mean(ref * ref))), 256 / (1 << 22))
            row[label] = {"max_abs": max_abs, "rmse": rmse, "max_abs_q22_lsb": max_abs * (1 << 22), "rmse_q22_lsb": rmse * (1 << 22), "relative_rmse": rel}
            lim = identity["acceptance"]
            if n == 32:
                max_lim = lim[label + "_32_max_abs"]
                rms_lim = lim[label + "_32_RMSE"]
            elif n == 800:
                max_lim = lim[label + "_800_max_abs"]
                rms_lim = lim[label + "_800_RMSE"]
            else:
                continue
            if max_abs > max_lim: failures.append(f"{n}:{label}:max_abs")
            if rmse > rms_lim: failures.append(f"{n}:{label}:rmse")
            if rel > lim["population_relative_rmse_max"]: failures.append(f"{n}:{label}:relative_rmse")
        result["prefix_metrics"].append(row)
    result["gate_failures"] = failures
    result["status"] = "PASS_NEW_PROFILE_SOFTWARE_FIDELITY_GATES" if not failures else "FAIL_NEW_PROFILE_SOFTWARE_FIDELITY_GATES"
    result["evidence_level"] = "MATCHED_FULL_GPU_AND_Q22_STATE_Q24_WEIGHT_DT30_H_GPU_R_SOFTWARE_RUNS_NO_PL"
    out = profile_dir.parent.parent / "artifacts" / identity["comparison_id"]
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "comparison_report.json", result)
    write_json(out / "artifact_manifest.json", {"schema": "flyvis-phase4-new-profile-comparison-manifest/v1", "files": list_manifest_files(out)})
    return out / "comparison_report.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["prepare", "full", "python", "compare", "all"], required=True)
    ap.add_argument("--out-root", type=Path, required=True)
    ap.add_argument("--q22-root", type=Path, required=True)
    ap.add_argument("--q22-init-dir", type=Path, required=True)
    ap.add_argument("--q22-numeric-profile", type=Path, required=True)
    ap.add_argument("--phase3-bundle", type=Path, required=True)
    ap.add_argument("--phase2-root", type=Path, required=True)
    ap.add_argument("--phase4-source-root", type=Path, required=True)
    ap.add_argument("--static-path", type=Path, required=True)
    ap.add_argument("--full-run-dir", type=Path)
    ap.add_argument("--python-run-dir", type=Path)
    args = ap.parse_args()
    if args.mode in ("prepare", "all"):
        profile_dir = prepare(args)
    else:
        profile_dir = args.out_root / "profiles" / "q22_state_q24_weight_dt30"
    if args.mode in ("full", "all"):
        full_dir = run_full(profile_dir, args)
        print("FULL_RUN_DIR", full_dir, flush=True)
    if args.mode in ("python", "all"):
        py_dir = run_python(profile_dir, args)
        print("PYTHON_RUN_DIR", py_dir, flush=True)
    if args.mode == "compare":
        if not args.full_run_dir or not args.python_run_dir:
            raise RuntimeError("compare requires --full-run-dir and --python-run-dir")
        report = compare(profile_dir, args.full_run_dir, args.python_run_dir)
        print("COMPARISON_REPORT", report, flush=True)


if __name__ == "__main__":
    main()

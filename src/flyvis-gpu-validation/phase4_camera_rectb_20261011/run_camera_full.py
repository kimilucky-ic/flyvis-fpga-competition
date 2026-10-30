"""Frozen 609-step real-camera input: original Full GPU, separate run identity.

No renderer, decoder, H replacement, quantization, board I/O, or new adaptation.
Bind the accepted complete native-GPU gray-adapted state at camera clip time zero.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import os
import platform
import shutil
import sys
import time
import uuid
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FPGA = HERE.parents[1]
FLY = FPGA.parent / "fly"
CAMERA = FLY / "camera_pipeline/phone_screen_rectification_20261011_r1/real_capture_review_camera_2dfba194_20261011_r1"
INPUT = CAMERA / "frozen_selected_100_190/input"
source = FLY / "gpu_phase3_fixed_video_20261010/bundle"
BUNDLE = HERE / "common_bundle"
COMPARISON = "camera_rectB_c5689ab635cc425ea672029502d0d402"
EXPECTED = {
    "stimulus.npy": "273f4bf4df0ba7591a293b36f62b1f9f3c98e0031ce8b2cc70ba13b1d49e78b9",
    "time.npy": "5ef025b2ad3f4132860ed6627f2cfd5ac5743de1cedd46a548ad7f13d943e60a",
    "activity_time.npy": "ee9628823694fe847fe3fae783d90652aab65f11bd98a015911dd39b4cca0fcd",
    "manifest.json": "35d1f43b6461439ea52222914a24eeb30997adadb01979ec07eb2518bb455800",
}


def digest(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def canonical(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def dump(p, v):
    Path(p).write_text(json.dumps(v, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def manifest(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(root.rglob("*"))
            if p.is_file() and p.name != "artifact_manifest.json"}


def read_input():
    spec = importlib.util.spec_from_file_location("frozen_camera_reader", CAMERA / "input_reader.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ident, x, t, a = mod.load_frozen_input(INPUT)
    assert ident["comparison_id"] == COMPARISON and x.shape == (1, 609, 1, 721)
    for name, expected in EXPECTED.items():
        assert digest(INPUT / name) == expected, name
    return ident, x, t, a


def verify_bundle():
    for name, expected in load(BUNDLE / "artifact_manifest.json")["files"].items():
        assert digest(BUNDLE / name) == expected, name
    return load(BUNDLE / "camera_backend_identity.json")


def prepare():
    ident, x, t, a = read_input()
    if BUNDLE.exists():
        raise RuntimeError("Existing common bundle preserved")
    BUNDLE.mkdir(parents=True)
    source_model = load(source / "identity_manifest.json")
    names = ["initial_state_full.npy", "expanded_parameters.npz", "identity_manifest.json",
             "nodes_full.csv", "input_node_indices.npy", "central_node_indices.npy", "cell_types.npy"]
    provenance = {}
    for name in names:
        shutil.copyfile(source / name, BUNDLE / name)
        provenance[name] = {"path": str(source / name), "sha256": digest(source / name)}
    candidate = "candidates/B_T5c"
    (BUNDLE / candidate).mkdir(parents=True)
    for name in ["candidate_manifest.json", "node_map.csv", "edge_partition_ids.npz"]:
        shutil.copyfile(source / candidate / name, BUNDLE / candidate / name)
        provenance[candidate + "/" + name] = {"path": str(source / candidate / name), "sha256": digest(source / candidate / name)}
    static = FPGA / "flyvis-circuit-selection/phase3_20261010/input_bundle/static_boundary_gpu_native.npz"
    shutil.copyfile(static, BUNDLE / static.name)
    assert digest(static) == "a915bd448e19ee6b83b7d0b8d11c913726a8dff6a5a4cebd03aa6f091154dade"
    provenance[static.name] = {"path": str(static), "sha256": digest(static)}
    for name in ["stimulus.npy", "time.npy", "activity_time.npy", "input_hex_coordinates.csv"]:
        shutil.copyfile(INPUT / name, BUNDLE / name)
        provenance[name] = {"path": str(INPUT / name), "sha256": digest(INPUT / name)}
    initial = np.load(BUNDLE / "initial_state_full.npy", allow_pickle=False)
    assert initial.shape == (1, 45669) and initial.dtype == np.float32 and np.isfinite(initial).all()
    assert digest(BUNDLE / "initial_state_full.npy") == source_model["initial_state_sha256"]
    independently_adapted = FLY / "gpu_phase2/artifacts/init_gpu_r1/initial_state_full.npy"
    assert np.array_equal(initial[0], np.load(independently_adapted, allow_pickle=False))
    assert digest(BUNDLE / "expanded_parameters.npz") == source_model["expanded_parameters_sha256"]
    assert digest(BUNDLE / "nodes_full.csv") == source_model["nodes_full_sha256"]
    candidate_doc = load(BUNDLE / candidate / "candidate_manifest.json")
    assert len(candidate_doc["h_global_node_indices"]) == 67
    assert candidate_doc["partition_counts"] == dict(HH=970, RH=5567, HR=8159, RR=1498535)
    with np.load(BUNDLE / "expanded_parameters.npz", allow_pickle=False) as params:
        assert not np.array_equal(initial[0], params["bias"])
        assert np.array_equal(params["input_node_index"], np.load(BUNDLE / "input_node_indices.npy"))
    profile = dict(schema="camera-float32-native-gpu/v1", state="float32",
                   parameters="OFFICIAL_NATIVE_GPU_EXPANDED", dynamics="PPNeuronIGRSynapses", activation="ReLU",
                   dt_s=.005, layout="SOURCE_RAW", state_quantization=None, weight_quantization=None,
                   no_warmup_at_block_boundaries=True, no_extra_preframes=True,
                   timestep_rule="all targets use same old complete a[k]; atomic commit after H and R validation")
    dump(BUNDLE / "numeric_profile.json", profile)
    dump(BUNDLE / "metric_profile.json", dict(schema="camera-software-metrics/v1", atol=1e-5, rtol=1e-5,
         note="Existing float32 software parity criterion; not Q22/Q24 or PL engineering acceptance"))
    binding = dict(schema="camera-backend-binding/v1", comparison_id=COMPARISON, condition_id="selected_100_190",
        input_manifest_sha256=EXPECTED["manifest.json"], stimulus_sha256=EXPECTED["stimulus.npy"],
        time_sha256=EXPECTED["time.npy"], activity_time_sha256=EXPECTED["activity_time.npy"],
        model_id=source_model["model_id"], source_commit=source_model["source_commit"],
        checkpoint_sha256=source_model["checkpoint_sha256"],
        expanded_parameters_sha256=source_model["expanded_parameters_sha256"],
        initial_state_sha256=source_model["initial_state_sha256"], nodes_full_sha256=source_model["nodes_full_sha256"],
        candidate_sha256=digest(BUNDLE / candidate / "candidate_manifest.json"),
        node_map_sha256=digest(BUNDLE / candidate / "node_map.csv"),
        edge_partition_sha256=digest(BUNDLE / candidate / "edge_partition_ids.npz"),
        static_boundary_sha256=digest(BUNDLE / static.name), numeric_profile_sha256=digest(BUNDLE / "numeric_profile.json"),
        metric_profile_sha256=digest(BUNDLE / "metric_profile.json"), steps=609, dt_s=.005,
        initial_state_shape=[1, 45669], initial_state_api="initial_state_full.npy[0] -> float32[45669]",
        time_semantics="bound gray-adapted a0 at selected clip local zero; a[k+1] after input[k], never original12s resumed state",
        parameter_profile="OFFICIAL_NATIVE_GPU_EXPANDED", n_nodes=45669, n_edges=1513231,
        layout="SOURCE_RAW", h_nodes=67, r_nodes=45602, boundary_nodes=1364,
        input_reader_sha256=digest(CAMERA / "input_reader.py"),
        a0_provenance="original GPU 200-step gray0.5 adaptation accepted video a0, values equal independent phase2 GPU adaptation",
        new_warmup_executed=False, independent_init_sha256=digest(independently_adapted),
        source_provenance=provenance, board_used=False)
    binding["backend_binding_id"] = canonical(binding)
    dump(BUNDLE / "camera_backend_identity.json", binding)
    dump(BUNDLE / "artifact_manifest.json", dict(schema="camera-common-bundle-seal/v1", files=manifest(BUNDLE)))
    verify_bundle()
    dump(HERE / "CAMERA_BACKEND_HANDOFF.json", dict(status="COMMON_BUNDLE_READY_FULL_PENDING", comparison_id=COMPARISON,
         backend_binding_id=binding["backend_binding_id"], common_bundle=str(BUNDLE), steps=609,
         full_gpu_root=None, full_gpu_finished=False, python_replacement="NOT_RUN_BY_A", fpga_replacement="NOT_CONNECTED"))
    print("COMMON_BUNDLE_READY", json.dumps({k:binding[k] for k in ["comparison_id", "backend_binding_id", "initial_state_sha256", "steps"]}), flush=True)


def configure_gpu():
    os.environ.update(CUDA_VISIBLE_DEVICES="0", FLYVIS_ROOT_DIR="/opt/flyvis-phase3-data", MPLBACKEND="Agg",
        MPLCONFIGDIR="/opt/flyvis-phase3-data/matplotlib", NUMBA_CACHE_DIR="/opt/flyvis-phase3-data/numba",
        CUBLAS_WORKSPACE_CONFIG=":4096:8", PYTHONDONTWRITEBYTECODE="1")
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(FLY / "gpu_phase2"))
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.manual_seed(0)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    assert torch.cuda.is_available()
    return torch


def run_full(name):
    binding = verify_bundle()
    _, x, t, a = read_input()
    out = HERE / "artifacts" / name
    if out.exists():
        raise RuntimeError("Existing actual run preserved")
    out.mkdir(parents=True)
    torch = configure_gpu()
    from full_oracle import FullNetworkOracle
    from r_only import array_sha
    code = {str(p):digest(p) for p in [Path(__file__), FLY / "gpu_phase2/full_oracle.py", FLY / "gpu_phase2/r_only.py"]}
    started_load = time.perf_counter()
    full = FullNetworkOracle(BUNDLE / "identity_manifest.json", device="cuda:0")
    torch.cuda.synchronize()
    load_seconds = time.perf_counter() - started_load
    assert torch.equal(torch.tensor([1.0],device="cuda")+1, torch.tensor([2.0],device="cuda"))
    run_id = str(uuid.uuid4())
    identity = dict(binding, run_id=run_id, mode="FullGPU", execution_kind="actual_new_computation",
        execution_evidence_level="SOFTWARE_ACTUAL_GPU_FULL", processing_mode="offline", no_new_warmup=True,
        no_extra_preframes=True, python=platform.python_version(), numpy=np.__version__, torch=torch.__version__,
        cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(), command=[sys.executable,*sys.argv],
        code_sha256=code, atol=1e-5, rtol=1e-5)
    dump(out / "run_identity.json", identity)
    initial = np.load(BUNDLE / "initial_state_full.npy", allow_pickle=False)[0]
    old = torch.as_tensor(initial.copy(), device="cuda:0")
    central = np.load(BUNDLE / "central_node_indices.npy", allow_pickle=False)
    states = np.lib.format.open_memmap(out / "activities_full.npy", mode="w+", dtype=np.float32, shape=(1,609,45669))
    activity = np.empty((1,609,len(central)), dtype=np.float32)
    step_times = []
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()
    started = time.perf_counter()
    before_digest = array_sha(initial)
    with (out / "step_status.jsonl").open("w", encoding="utf-8") as stream:
        for k in range(609):
            frame = torch.as_tensor(x[0,k,0].copy(), device="cuda:0")
            torch.cuda.synchronize()
            tic = time.perf_counter()
            old = full.step(old, frame)
            torch.cuda.synchronize()
            elapsed = time.perf_counter() - tic
            after = old.cpu().numpy().copy()
            assert np.isfinite(after).all()
            states[0,k] = after
            activity[0,k] = after[central]
            after_digest = array_sha(after)
            row = dict(step_id=k, run_id=run_id, comparison_id=COMPARISON, status="FULL_REFERENCE_ONLY",
                input_time_s=float(t[k]), activity_after_time_s=float(a[k]),
                before_digest=before_digest, input_digest=array_sha(x[0,k,0]), after_digest=after_digest,
                backend_step_ms=elapsed*1000)
            stream.write(json.dumps(row)+"\n")
            before_digest = after_digest
            step_times.append(elapsed*1000)
            if (k+1)%100 == 0 or k == 608:
                stream.flush()
                print("FULL_STEPS", name, k+1, flush=True)
    torch.cuda.synchronize()
    wall_seconds = time.perf_counter()-started
    states.flush()
    full.assert_weights_unchanged()
    for path, expected in code.items():
        assert digest(Path(path)) == expected
    verify_bundle()
    read_input()
    np.save(out / "activity_central.npy", activity)
    np.save(out / "final_state_full.npy", states[0,-1])
    np.save(out / "backend_step_latency_ms.npy", np.asarray(step_times))
    for name in ["time.npy", "activity_time.npy", "cell_types.npy", "central_node_indices.npy"]:
        shutil.copyfile(BUNDLE / name, out / name)
    result = dict(status="PASS_FULL_GPU_609", scope="actual original Full GPU only; no replacement or board claim",
         run_id=run_id, comparison_id=COMPARISON, backend_binding_id=binding["backend_binding_id"],
         steps=609, activities_full_shape=[1,609,45669], activity_central_shape=list(activity.shape), nonfinite_count=0,
         model_load_s=load_seconds, inference_and_recording_s=wall_seconds, kernel_total_s=sum(step_times)/1000,
         kernel_p50_ms=float(np.median(step_times)), kernel_p95_ms=float(np.percentile(step_times,95)),
         peak_torch_allocated_mib=torch.cuda.max_memory_allocated()/2**20,
         peak_torch_reserved_mib=torch.cuda.max_memory_reserved()/2**20,
         weight_state_exact_before=True, weight_state_exact_after=True, warmup_calls=0, Full_steps=609,
         gpu_r_steps=0, python_h_steps=0, pl_h_steps=0, board_used=False, actual_neural_input="frozen recorded-camera frames",
         activities_full_sha256=digest(out / "activities_full.npy"), final_state_sha256=digest(out / "final_state_full.npy"))
    dump(out / "result.json", result)
    dump(out / "artifact_manifest.json", dict(files=manifest(out)))
    print("FULL_COMPLETE", json.dumps(result), flush=True)


def audit():
    binding = verify_bundle()
    read_input()
    roots = [HERE / "artifacts/full_gpu_609_r1", HERE / "artifacts/full_gpu_609_r2"]
    for root in roots:
        for name, sha in load(root / "artifact_manifest.json")["files"].items():
            assert digest(root / name) == sha
    first, second = [load(root / "run_identity.json") for root in roots]
    assert first["backend_binding_id"] == second["backend_binding_id"] == binding["backend_binding_id"]
    assert first["run_id"] != second["run_id"]
    aa, bb = [np.load(root / "activities_full.npy", mmap_mode="r", allow_pickle=False) for root in roots]
    rows = []
    for k in range(609):
        delta = aa[0,k].astype(np.float64)-bb[0,k].astype(np.float64)
        rows.append(dict(step_id=k, max_abs=float(np.abs(delta).max()), rmse=float(np.sqrt(np.mean(delta*delta))),
                         bitwise=bool(np.array_equal(aa[0,k],bb[0,k]))))
    with (HERE / "independent_replay_errors.csv").open("w", newline="") as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result = dict(status="PASS_INDEPENDENT_FRESH_PROCESS_REPLAY", comparison_id=COMPARISON,
        backend_binding_id=binding["backend_binding_id"], steps=609, nodes=45669,
        max_abs=max(r["max_abs"] for r in rows), all_steps_bitwise=all(r["bitwise"] for r in rows),
        run_ids=[first["run_id"],second["run_id"]], board_used=False)
    assert result["all_steps_bitwise"]
    dump(HERE / "INDEPENDENT_REPLAY_ACCEPTANCE.json", result)
    handoff = dict(status="PASS_A_FULL_GPU_609_AND_INDEPENDENT_REPLAY", comparison_id=COMPARISON,
        backend_binding_id=binding["backend_binding_id"], common_bundle=str(BUNDLE),
        full_gpu_root=str(roots[0]), replay_root=str(roots[1]), activities_full=str(roots[0]/"activities_full.npy"),
        activities_full_shape=[1,609,45669], steps=609, dt_s=.005, full_gpu_finished=True,
        initial_state=str(BUNDLE/"initial_state_full.npy"), identity_manifest=str(BUNDLE/"identity_manifest.json"),
        expanded_parameters=str(BUNDLE/"expanded_parameters.npz"), native_r_only_source=str(FLY/"gpu_phase2/r_only.py"),
        input_reader=str(CAMERA/"input_reader.py"), binding=str(BUNDLE/"camera_backend_identity.json"),
        python_replacement="NOT_RUN_BY_A; B uses its own live state", fpga_replacement="NOT_CONNECTED",
        input_comparison_id_preserved=True, producer="A_original_FlyVis_GPU", board_used=False)
    dump(HERE / "CAMERA_BACKEND_HANDOFF.json", handoff)
    print("INDEPENDENT_REPLAY", json.dumps(result), flush=True)


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "full", "audit"])
    parser.add_argument("--run")
    args=parser.parse_args()
    if args.mode == "prepare": prepare()
    elif args.mode == "full":
        if not args.run: parser.error("--run required")
        run_full(args.run)
    else: audit()

"""Run CPU-only, bounded acceptance in a fresh study-owned output directory."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parent


def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fly-root", type=Path, default=ROOT.parent.parent / "fly")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--steps", type=int, choices=[1, 32, 800], default=32)
    args = parser.parse_args()
    out = args.output.resolve()
    if ROOT not in out.parents or out.exists():
        raise ValueError("Output must be a new directory strictly inside this study")
    out.mkdir(parents=True)
    import shutil
    (out / "scripts_snapshot").mkdir()
    for source in ROOT.glob("*.py"):
        shutil.copy2(source, out / "scripts_snapshot" / source.name)
    for key, value in dict(CUDA_VISIBLE_DEVICES="-1", PYTHON_DOTENV_DISABLED="1", OMP_NUM_THREADS="1",
                           MKL_NUM_THREADS="1", NUMBA_NUM_THREADS="1", MPLBACKEND="Agg", TIMEZONE="Asia/Shanghai",
                           FLYVIS_ROOT_DIR=str(out / "isolated_flyvis_root"),
                           MPLCONFIGDIR=str(out / "isolated_mpl"), NUMBA_CACHE_DIR=str(out / "isolated_numba")).items():
        os.environ[key] = value
    import numpy as np
    import torch
    import psutil
    import numba
    from reference import verify_sources, build_reference, export_shared, sha, GRAPH_SHA, CHECKPOINT_SHA
    from codec import compile_template, read_template, iter_edges
    from engine import Engine
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.set_default_device("cpu")
    torch.use_deterministic_algorithms(True)
    torch.set_flush_denormal(False)
    start = time.perf_counter()
    stages = []
    def progress(name, **data):
        row = dict(stage=name, elapsed_s=time.perf_counter() - start, rss_MiB=psutil.Process().memory_info().rss / 2**20, **data)
        stages.append(row)
        save_json(out / "progress.json", stages)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    save_json(out / "environment.json", dict(python=sys.version, executable=sys.executable, platform=platform.platform(),
              torch=torch.__version__, numpy=np.__version__, numba=numba.__version__, cpu_threads=1,
              cuda_initialized=torch.cuda.is_initialized(), deterministic_algorithms=True,
              command=sys.argv, memory_available_MiB=psutil.virtual_memory().available / 2**20,
              numerical_reference="Pinned upstream Network with in-memory connectome storage adapter"))
    try:
        if psutil.virtual_memory().available < 1800 * 2**20:
            raise RuntimeError("CPU study requires 1800 MiB available RAM; nothing else will be stopped")
        sources = verify_sources(args.fly_root)
        save_json(out / "source_inventory.json", sources)
        progress("source_identity_pass")
        net, params, spec, oracle = build_reference(args.fly_root)
        shared = export_shared(spec, oracle, out / "shared_parameters.npz")
        progress("official_cpu_reference_ready", **shared)
        layout = compile_template(spec, out / "shared_parameters.npz", out / "flyvis_template.bin", GRAPH_SHA, CHECKPOINT_SHA)
        save_json(out / "binary_layout.json", layout)
        template = read_template(out / "flyvis_template.bin")
        assert template["graph_sha256"] == GRAPH_SHA and template["checkpoint_sha256"] == CHECKPOINT_SHA
        record_dtype = np.dtype([("src", "<u2"), ("dst", "<u2"), ("weight_bits", "<u4")])
        expanded = np.empty(template["e"], dtype=record_dtype)
        for eid, src, dst, bits in iter_edges(template):
            expanded[eid] = (src, dst, bits)
        mismatches = {"source_id": int(np.count_nonzero(expanded["src"] != oracle["src"])),
                      "target_id": int(np.count_nonzero(expanded["dst"] != oracle["dst"])),
                      "weight_bits": int(np.count_nonzero(expanded["weight_bits"] != oracle["weight"].view(np.uint32)))}
        reference_records = np.empty_like(expanded)
        reference_records["src"], reference_records["dst"], reference_records["weight_bits"] = oracle["src"], oracle["dst"], oracle["weight"].view(np.uint32)
        np.save(out / "oracle_edges.npy", reference_records)
        structure = dict(status="PASS" if not any(mismatches.values()) else "FAIL", checked_edges=len(expanded),
                         mismatches=mismatches, record_format="source:uint16le,target:uint16le,weight_bits:uint32le; ordinal is eid",
                         decoded_sha256=hashlib.sha256(expanded.tobytes()).hexdigest(),
                         reference_sha256=hashlib.sha256(reference_records.tobytes()).hexdigest(),
                         all_original_nodes_equal_archived_node_table=True, all_rules_and_zero_weight_edges_retained=True,
                         **shared, **layout)
        save_json(out / "structure_acceptance.json", structure)
        assert structure["status"] == "PASS", mismatches
        progress("all_ordered_edges_and_weights_pass", binary_bytes=layout["binary_bytes"], mismatches=mismatches)
        del expanded, reference_records
        original_stimulus = np.load(args.fly_root / "artifacts/moving_edge_minimal_cpu_v1/stimulus.npy", allow_pickle=False)
        assert original_stimulus.shape == (2, 485, 1, 721) and original_stimulus.dtype in (np.float32, np.float64)
        save_json(out / "input_contract.json", dict(source_dtype=str(original_stimulus.dtype), inference_dtype="float32",
                  conversion="Explicit float32 cast, matching assignment into upstream Stimulus.zero float32 buffer",
                  sequence="200 grey 0.5 frames, saved direction-0 ON MovingEdge 485 frames, 115 grey frames",
                  steps=args.steps, initial_state="Original per-type bias, no external state feedback", dt_s=0.005))
        # Test starts at the official bias initial state: 200 grey, 485 ON-edge frames, 115 grey.
        sequence = np.concatenate([np.full((200, 721), .5, np.float32), original_stimulus[0, :, 0].astype(np.float32),
                                   np.full((115, 721), .5, np.float32)])[:args.steps].copy()
        np.save(out / "stimulus.npy", sequence)
        np.save(out / "time.npy", (np.arange(args.steps) + 1) * 0.005)
        np.save(out / "node_type_ids.npy", oracle["types"])
        save_json(out / "cell_types.json", [n["name"] for n in spec["nodes"]])
        engine = Engine(template)
        np.save(out / "initial_state.npy", engine.activity)
        assert np.array_equal(engine.activity.view(np.uint32), oracle["bias"].view(np.uint32))
        # Warm JIT on a disposable engine; accepted chain starts from a fresh initial state.
        warm = Engine(template)
        warm.advance(sequence[0]); del warm
        llvm = "\n".join(str(v) for v in __import__("engine").step.inspect_llvm().values())
        fma_found = "llvm.fma." in llvm or "llvm.fmuladd." in llvm
        save_json(out / "arithmetic_contract.json", dict(dtype="float32", fastmath=False, fma_intrinsic_found=fma_found,
                  source_order="rule, filled-offset, source-u, source-v; original IDs",
                  update="d0=RN(-a+b);d1=RN(d0+I);d2=RN(d1+x);v=RN(inv_tau*d2);delta=RN(v*dt);a_next=RN(a+delta)",
                  inv_tau="FP32 bits exported from upstream 1/max(time_const,float32(dt))",
                  edge_term="RN(weight*ReLU(old_activity))", accumulation="RN(previous_current+term) in original edge order",
                  no_expanded_edge_list_in_engine=True, vector_bytes=engine.activity.nbytes+engine.current.nbytes,
                  finite_domain_only=True, ieee_all_inputs_compliance_claim=False))
        assert not fma_found
        progress("jit_ready_two_vector_engine")
        ref_trace = np.lib.format.open_memmap(out / "reference_activity.npy", mode="w+", dtype=np.float32, shape=(args.steps, template["n"]))
        got_trace = np.lib.format.open_memmap(out / "template_activity.npy", mode="w+", dtype=np.float32, shape=(args.steps, template["n"]))
        state = net._initial_state(params, 1)
        net.stimulus.zero(1, 1)
        rows = []; ref_seconds = 0.; engine_seconds = 0.
        with torch.inference_mode():
            for t, stimulus in enumerate(sequence):
                net.stimulus.zero(1, 1)
                net.stimulus.add_input(torch.from_numpy(stimulus.copy()).reshape(1, 1, 1, 721))
                before = time.perf_counter()
                state = net._next_state(params, state, net.stimulus()[:, 0], 0.005)
                reference = state.nodes.activity[0].numpy()
                ref_seconds += time.perf_counter() - before
                before = time.perf_counter(); got = engine.advance(stimulus); engine_seconds += time.perf_counter() - before
                diff = np.abs(reference.astype(np.float64) - got.astype(np.float64))
                count = int(np.count_nonzero(reference.view(np.uint32) != got.view(np.uint32)))
                row = dict(step=t+1, bit_mismatches=count, max_abs_error=float(diff.max()), rmse=float(np.sqrt(np.mean(diff*diff))),
                           finite=bool(np.isfinite(reference).all() and np.isfinite(got).all()))
                rows.append(row); ref_trace[t], got_trace[t] = reference, got
                if count or not row["finite"]:
                    save_json(out / "numeric_first_failure.json", row)
                    raise AssertionError(f"Numerical mismatch: {row}")
                if t + 1 in {1, 32, 200, 400, 600, 800} or t + 1 == args.steps:
                    ref_trace.flush(); got_trace.flush()
                    save_json(out / "per_step_comparison.json", rows)
                    progress("numerical_checkpoint_pass", steps=t+1, compared_state_values=(t+1)*template["n"])
        ref_trace.flush(); got_trace.flush()
        del ref_trace, got_trace
        # The original CPU MovingEdge archive exports only central cells, after the same grey warmup.
        historical = {"checked": False}
        if args.steps == 800:
            central_path = args.fly_root / "artifacts/moving_edge_minimal_cpu_v1/activity_central.npy"
            if central_path.exists():
                original = np.load(central_path, allow_pickle=False)[0]
                current = np.load(out / "reference_activity.npy", mmap_mode="r")[200:685, oracle["central"]]
                historical = dict(checked=True, archived_path=str(central_path), archived_sha256=sha(central_path),
                                  shape=list(original.shape), bit_mismatches=int(np.count_nonzero(original.view(np.uint32) != current.view(np.uint32))),
                                  max_abs_error=float(np.max(np.abs(original.astype(float)-current.astype(float)))))
                save_json(out / "historical_central_comparison.json", historical)
        sources_after = verify_sources(args.fly_root)
        assert sources_after == sources, "Reference inputs changed during study"
        assert not torch.cuda.is_initialized()
        acceptance = dict(status="PASS_CPU_TEMPLATE_STRUCTURE_AND_RECURRENCE", evidence_level="software_only",
                          steps=args.steps, nodes=template["n"], edges_per_step=template["e"],
                          compared_state_values=args.steps*template["n"], bit_mismatches=0, max_abs_error=0.,
                          self_feedback_transitions=args.steps-1, graph_sha256=GRAPH_SHA, checkpoint_sha256=CHECKPOINT_SHA,
                          historical_central_comparison=historical, sources_unchanged=True, cuda_initialized=False,
                          vivado_started=False, board_operations=0, reference_compute_s=ref_seconds, template_compute_s=engine_seconds,
                          total_elapsed_s=time.perf_counter()-start, binary_bytes=layout["binary_bytes"],
                          hardware_cycle_measurement=None, synthesis=None, board_validation=None, real_time_200Hz=None)
        save_json(out / "acceptance.json", acceptance)
        progress("bounded_acceptance_complete", status=acceptance["status"])
        manifest = {str(p.relative_to(out)): {"bytes":p.stat().st_size,"sha256":sha(p)} for p in out.glob("*") if p.is_file() and p.name != "manifest.json"}
        save_json(out / "manifest.json", manifest)
        print(json.dumps(acceptance, ensure_ascii=False), flush=True)
    except Exception as exc:
        save_json(out / "failure.json", dict(status="FAIL", error=str(exc), traceback=traceback.format_exc(), elapsed_s=time.perf_counter()-start))
        raise


if __name__ == "__main__":
    main()

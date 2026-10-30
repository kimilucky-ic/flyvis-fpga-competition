"""Record this bounded A/B delivery from existing evidence; never compute neurons."""
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from autorunner import HERE, load_json, own_path, require, sha, write_json


def main():
    rows = {}
    for stage in ("A", "B"):
        run_id = "autorun_research" + stage + "_20261011_r1"
        job = own_path("runs", run_id)
        summary = load_json(job / "run_summary.json")
        require(summary["status"] == "PASS_FAST_ACTUAL_SCIENCE", "NOT_COMPLETE", run_id)
        command = load_json(own_path("verification", "phase2_" + run_id + "_command.json"))
        config = load_json(job / "config_snapshot.json")
        root = Path(summary["output_dir"])
        actual = load_json(root / "result.json")
        cases = actual["modes"]
        rows[stage] = {"run_id": run_id, "worker_uuid": actual["run_id"], "identity_id": summary["identity_id"],
            "identity_key": summary["identity_key"], "CLI_wall_s": command["CLI_wall_s"],
            "actual_start_utc": command["started_utc"], "actual_end_utc": command["ended_utc"],
            "approved_start_utc": config["scope"]["start"], "approved_end_utc": config["scope"]["end"],
            "cases": len(cases), "new_GPU_invocations": summary["new_GPU_invocations"],
            "actual_neural_steps": actual["actual_neural_steps"], "actual_decoder_frames": actual["actual_decoder_frames"],
            "reference_violations": sum(q["reference_violations"] for q in cases),
            "max_reference_state_error": max(q["max_reference_state_error"] for q in cases),
            "max_reference_flow_error": max(q["max_reference_flow_error"] or 0 for q in cases),
            "timings": summary["timings"], "orchestration_outside_scientific_worker_s": command["CLI_wall_s"] - actual["elapsed_s"],
            "peak_allocated_MiB": actual["peak_allocated_MiB"], "peak_reserved_MiB": actual["peak_reserved_MiB"],
            "raw_output_bytes": sum(p.stat().st_size for p in root.rglob("*") if p.is_file()),
            "host_exit": load_json(job / "host_exit.json"), "command": command["command"]}
    cache = load_json(own_path("verification", "phase2_researchB_cache_20261011_command.json"))
    report = {"status": "PASS_PHASE2_SERIAL_A_B_STOPPED", "evidence": "SOFTWARE_ACTUAL_CUDA_ORIGINAL_MODEL_AND_DECODER",
        "PL_execution": False, "camera609_recomputed": False, "third_research_started": False,
        "actual_GPU_invocations": 2, "auto_retries": 0, "stages": rows,
        "actual_CLI_sum_s": sum(q["CLI_wall_s"] for q in rows.values()), "B_cache_CLI_wall_s": cache["CLI_wall_s"],
        "CPU_tests": {"unique_passed_scenarios": 30, "Windows": "tests/artifacts/plugins_9f47013675/report.json",
                      "WSL": "tests/artifacts/plugins_4c9f9711e8/report.json", "GPU_called": False},
        "resource_release": "verification/phase2_resources_after_B.json",
        "cache_bulk_guard": "size+mtime; essential result, identity and COMMIT journal SHA256",
        "pure_transfer_or_GPU_kernel_time": None}
    write_json(own_path("verification", "phase2_acceptance.json"), report)
    lines = ["# AutoRunner second stage — bounded A/B delivery", "", "**PASS_PHASE2_SERIAL_A_B_STOPPED**.", "",
        "The original609 actual PASS and37.307787s record remain sealed. No609 neural computation was repeated. "
        "This delivery adapts④'s frozen public scientific module through a separate CLI host, shared exclusive GPU lock, "
        "pre-registered identities, serial A→B gate, progress, content-key cache, fixed fast checks and retained failures. "
        "The scientific owner authored and analyzed the experiments; AutoRunner does not implement neural equations.", ""]
    for stage, q in rows.items():
        lines += [f"## Research {stage}", "", f"- Scheduler ID `{q['run_id']}`; actual scientific UUID `{q['worker_uuid']}`.",
            f"- Actual {q['cases']} cases, {q['actual_neural_steps']} live neural steps and {q['actual_decoder_frames']} decoder frames; one new GPU invocation, no retry.",
            f"- CLI wall **{q['CLI_wall_s']:.6f}s**; scientific worker {q['timings']['science_worker_wall_s']:.6f}s; model load {q['timings']['model_load_s']:.6f}s.",
            f"- Neural+record wall {q['timings']['neural_and_record_wall_s']:.6f}s; decoder wall {q['timings']['decoder_wall_s']:.6f}s; fast evidence check {q['timings']['fast_check_s']:.6f}s.",
            f"- Outside-scientific-worker orchestration {q['orchestration_outside_scientific_worker_s']:.6f}s (includes entry verification, process startup/exit and sealing); pure transfer and isolated GPU kernel time are not instrumented and remain null.",
            f"- Reference violations {q['reference_violations']}; maximum compared state/flow differences {q['max_reference_state_error']}/{q['max_reference_flow_error']} at the frozen1e-5+1e-5*abs(reference) criterion. Static/middle cases have no old numeric reference; they retain finite/shape/COMMIT evidence and④'s fixed scientific metrics.",
            f"- Approved slot {q['approved_start_utc']} to {q['approved_end_utc']}; actual command {q['actual_start_utc']} to {q['actual_end_utc']}.",
            f"- Peak allocated/reserved GPU memory {q['peak_allocated_MiB']:.3f}/{q['peak_reserved_MiB']:.3f}MiB; raw output {q['raw_output_bytes']/2**30:.3f}GiB.",
            f"- Identity `{q['identity_id']}`; cache key `{q['identity_key']}`.",
            f"- Evidence: [summary](runs/{q['run_id']}/run_summary.json), [fast check](runs/{q['run_id']}/fast_check.json), [seal](runs/{q['run_id']}/plugin_seal.json), [actual command](verification/phase2_{q['run_id']}_command.json).", ""]
    lines += ["## Tests and daily commands", "", "30 unique CPU/resource scenarios passed:23 scheduler/interface/timeout scenarios on Windows,7 actual WSL flock/resource scenarios with every GPU query mocked. "
        "Windows complete suite ran1.445941s (7 WSL-only cases skipped); WSL29-case suite ran27.713502s before the final platform-independent timeout case was added. "
        "The final two child-failure/timeout cases were rerun after isolating their output paths so tests remain reusable after real data exists. All test logs and synthetic failures remain; no torch/CUDA or board operation occurred.", "",
        "Covered missing/wrong public signature, source/spec/identity mismatch, endpoint order, extra cases/third task, old camera scope, expiration, fresh-A cache refusal, occupied lock/GPU/board marker, unknown resource, renewed-slot duplicate invocation, stop/quarantine, child exit logs, parent timeout, cache corruption and accepted cache replay. "
        "These are orchestration fault injections, not intentionally damaged scientific GPU runs.", "",
        f"Actual accepted B cache replay CLI {cache['CLI_wall_s']:.6f}s, zero new GPU invocation, no neural/decoder recomputation. Bulk raw files are guarded by size+mtime in fast mode; essential identity/results/COMMITs have SHA256 seals. No claim of a second all-byte bulk audit is made.", "",
        "```powershell", "python -B .\\flyvis-autorunner\\runner.py preflight --config .\\flyvis-autorunner\\configs\\researchA.fast.json",
        "python -B .\\flyvis-autorunner\\runner.py run --config .\\flyvis-autorunner\\configs\\researchB.fast.json --dry-run",
        "python -B .\\flyvis-autorunner\\runner.py status autorun_researchB_20261011_r1",
        "python -B .\\flyvis-autorunner\\runner.py run --config .\\flyvis-autorunner\\configs\\researchB.cache-only.20261011.json --cache-only",
        "```", "", "The successful actual commands recorded above used the dated authorized A/B copies and their fixed IDs. They are consumed one-shot evidence: do not rerun them. "
        "New actual jobs require a new approved bounded scope and output directory; default reusable A/B configs have GPU authorization disabled.", "",
        "[Interface and config contract](PHASE2_INTERFACE.md). Scientific reports are④'s `t4t5_confirm_20261011/CONFIRM_REPORT.md` and `t4t5_sparse_recovery_20261011/SPARSE_REPORT.md`. "
        "Both stages use original continuous network and official decoder; they are software evidence. No GUI, LIF, FPGA/board operation, third study, new stimulus search or redundant609 calculation was performed. "
        "No automatic task/heartbeat was added. Stop at this acceptance. The reusable local CPU/CLI contract is documented; no universal hardware or cross-project Skill claim is made.", ""]
    own_path("PHASE2_ACCEPTANCE.md").write_text("\n".join(lines), encoding="utf-8")
    files = ["runner.py", "plugin_contract.py", "plugin_runner.py", "plugin_host.py", "freeze_science_config.py", "measure_science.py",
        "probe_science_resources.py", "close_science_report.py", "tests/test_plugins.py", "PHASE2_INTERFACE.md", "PHASE2_ACCEPTANCE.md",
        "configs/researchA.fast.json", "configs/researchB.fast.json", "configs/researchA.authorized.20261011.json",
        "configs/researchB.authorized.20261011.json", "configs/researchB.cache-only.20261011.json", "phase1_snapshot/runner.py"]
    write_json(own_path("phase2_release_manifest.json"), {"status": report["status"], "files": {p: sha(own_path(p)) for p in files},
        "original_phase1_manifest": "release_manifest.json", "actual_GPU_invocations": 2, "PL_execution": False})
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

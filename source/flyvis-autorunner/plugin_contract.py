"""CPU contract for the two frozen B4 science tasks; no neural implementation."""
import ast
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from autorunner import (HERE, RunnerError, canonical, host_path, load_json, methods, own_path,
                        read_clock, require, sha, utc, write_json)

SCHEMA = "flyvis-autorunner/cli-science-v2"
EXPERIMENTS = {"A": "RESEARCH_A_CONFIRM_STATIC", "B": "RESEARCH_B_SPARSE_RETAIN"}


def path(value):
    p = host_path(value)
    return (p if p.is_absolute() else HERE / p).resolve()


def validate(config):
    require(config["schema"] == SCHEMA and config["stage"] in EXPERIMENTS,
            "PLUGIN_SCHEMA", "Only assigned science A/B plugins")
    require(config.get("mode", "fast") == "fast", "PLUGIN_MODE", "Only bounded fast acceptance")
    spec_path = path(config["spec_path"])
    require(sha(spec_path) == config["spec_sha256"], "SPEC_CHANGED", str(spec_path))
    spec = load_json(spec_path)
    body = {k: v for k, v in spec.items() if k != "identity_id"}
    require(canonical(body) == spec["identity_id"] == config["identity_id"],
            "IDENTITY", "Frozen preregistration identity mismatch")
    require(spec["experiment"] == EXPERIMENTS[config["stage"]] and spec["steps"] == 485
            and spec["dt_s"] == .005 and spec["start_step"] == 200 and spec["n_nodes"] == 45669
            and spec["max_attempts"] == 1 and spec["GPU_concurrency"] == 1
            and spec["FPGA_execution"] is False and spec["training"] is False,
            "EXPERIMENT_SCOPE", "Frozen original model, one serial attempt, no PL/training")
    expected_runs = 24 if config["stage"] == "A" else 14
    require(spec["max_gpu_seconds"] == 900 and spec["storage_budget_GiB"] == (3 if config["stage"] == "A" else 2)
            and 0 <= config["queue_s"] <= 30 and 1 <= config["stop_grace_s"] <= 30,
            "RESOURCE_BUDGET", "Frozen time/storage bounds")
    require(len(spec["cases"]) == expected_runs
            and spec["actual_neural_steps_budget"] == expected_runs * 485
            and spec["actual_decoder_frames_budget"] == expected_runs * 485,
            "CASE_BUDGET", "No extra research or cases")
    if config["stage"] == "A":
        moving = [(q["condition"], q["mode"]) for q in spec["cases"] if not q["condition"].startswith("STATIC_")]
        controls = [(q["condition"], q["mode"]) for q in spec["cases"] if q["condition"].startswith("STATIC_")]
        require(set(moving) == {(c, m) for c in ("ON60", "ON240", "OFF90", "OFF270")
                for m in ("Full", "Sham", "BLOCK_T4_RELEASE", "BLOCK_T5_RELEASE", "BLOCK_T4T5_RELEASE")}
                and set(controls) == {(c, m) for c in ("STATIC_ON60", "STATIC_OFF90")
                for m in ("Sham", "BLOCK_T4T5_RELEASE")}, "CASE_SCOPE", "A main and static controls")
        require(config["fresh_run"] is True, "FRESH_CONFIRMATION_REQUIRED", "A cannot be cache-satisfied")
    else:
        expected = [(c, n) for n in (0, 5768, 488, 1016, 1736, 2648, 3752) for c in ("ON60", "OFF90")]
        require([(q["condition"], q["n_retained"]) for q in spec["cases"]] == expected,
                "ENDPOINT_ORDER", "Both endpoints precede the five middle scales")
        require(bool(config.get("predecessor")), "A_REQUIRED", "B needs the same campaign's A delivery")
    module = path(spec["computational_module"])
    # Source pin names retain the producer OS spelling; resolve them before lookup.
    pins = {path(p): digest for p, digest in spec["source_pins"].items()}
    require(module in pins and sha(module) == pins[module], "SOURCE_CHANGED", str(module))
    tree = ast.parse(module.read_text(encoding="utf-8-sig"))
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    require("run_experiment" in funcs and "preflight" in funcs, "API_METHOD", "B4 public functions")
    require([a.arg for a in funcs["run_experiment"].args.args] == ["spec_path", "output_path", "check_scope"],
            "API_SIGNATURE", "run_experiment(spec_path, output_path, check_scope)")
    require(spec["computational_function"] == "run_experiment", "API_METHOD", "Unknown callable")
    # Only bounded identity inputs and source are rehashed here; the scientific
    # worker checks its complete source/reference pins once at its own entry.
    for p, digest in pins.items():
        if p.suffix in (".py", ".json") or p == path(spec["initial_state_path"]):
            require(sha(p) == digest, "SOURCE_CHANGED", str(p))
    full_api = next((p for p in pins if p.name == "full_oracle.py"), None)
    decoder_api = next((p for p in pins if p.name == "service.py"), None)
    require(full_api is not None and decoder_api is not None, "API_CLASS", "Frozen Full/decoder source")
    methods(full_api, "FullNetworkOracle", {"step": [], "assert_weights_unchanged": []})
    methods(decoder_api, "OfficialDecoderService", {"init__": ["check_scope"], "decode": ["activity", "chunk_frames"], "assert_weights_unchanged": []})
    output = path(config["output_dir"])
    lane = HERE.parent / "flyvis-circuit-selection" / ("t4t5_confirm_20261011" if config["stage"] == "A" else "t4t5_sparse_recovery_20261011")
    require(output.is_relative_to(lane.resolve() / "artifacts"), "PLUGIN_WRITE_SCOPE", str(output))
    key = canonical({"contract": SCHEMA, "identity_id": spec["identity_id"],
                     "spec_sha256": config["spec_sha256"], "module_sha256": pins[module]})
    return spec, key


def authorize(config, key, now=None):
    ticket = config.get("scope", {})
    require(ticket.get("authorized") is True and ticket.get("confirmed_by_user") is True,
            "RUN_NOT_AUTHORIZED", "A new science lease is required; camera609 lease is closed")
    require(ticket.get("stage") == config["stage"] and ticket.get("identity_key") == key
            and ticket.get("max_attempts") == 1 and ticket.get("max_cases") == (24 if config["stage"] == "A" else 14)
            and ticket.get("max_steps") == (11640 if config["stage"] == "A" else 6790)
            and ticket.get("conflict_free") is True and ticket.get("board_resources_reserved") is False
            and bool(ticket.get("authorization_reference")) and bool(config.get("campaign_id")),
            "GPU_SCOPE", "Science identity/budget/resource scope mismatch")
    start, end = read_clock(ticket["start"]), read_clock(ticket["end"])
    require(0 < (end - start).total_seconds() <= 900, "GPU_SCOPE", "Science slot <=15 minutes")
    now = now or datetime.now(timezone.utc)
    require(start <= now < end, "SLOT_EXPIRED", "Outside science slot")
    return ticket


def predecessor(config):
    if config["stage"] != "B":
        return None
    prior = config["predecessor"]
    prior_dir = own_path("runs", prior["run_id"])
    require((prior_dir / "plugin_seal.json").exists(), "A_NOT_SEALED", "A must be sealed before B")
    job = load_json(prior_dir / "run_summary.json")
    seal = load_json(prior_dir / "plugin_seal.json")
    summary_pins = {path(p): digest for p, digest in seal["essential_sha256"].items()}
    require(summary_pins.get(prior_dir / "run_summary.json") == sha(prior_dir / "run_summary.json")
            and seal["identity_key"] == job["identity_key"], "A_SEAL_CHANGED", "A summary seal mismatch")
    require(job["status"] == "PASS_FAST_ACTUAL_SCIENCE" and job["campaign_id"] == config["campaign_id"]
            and job["identity_id"] == prior["identity_id"] and job["stage"] == "A",
            "A_NOT_COMPLETE", "Same campaign's A must finish and seal first")
    receipt = load_json(path(prior["delivery_result"]))
    require(receipt["status"] == "PASS_INDEPENDENT_CONFIRMATION_AND_STATIC_CONTROL"
            and receipt.get("identity_id", prior["identity_id"]) == prior["identity_id"],
            "A_DELIVERY_PENDING", "A's scientific short delivery is required before B")
    return {"run_id": prior["run_id"], "delivery_sha256": sha(path(prior["delivery_result"]))}


def fast_check(spec, output):
    """Validate producer's fixed numerical checks and small saved evidence once."""
    import numpy as np
    out = path(output)
    result = load_json(out / "result.json")
    identity = load_json(out / "run_identity.json")
    require(result["status"] == "PASS_ACTUAL_SCIENCE_COMPUTATION"
            and result["identity_id"] == identity["identity_id"] == spec["identity_id"]
            and result["run_id"] == identity["run_id"] and result["PL_execution"] is False
            and result["actual_neural_steps"] == spec["actual_neural_steps_budget"]
            and result["actual_decoder_frames"] == spec["actual_decoder_frames_budget"]
            and result["network_weights_unchanged"] is True and result["decoder_state_unchanged"] is True,
            "RESULT_CONTRACT", "Complete original-model/decoder result and immutable identity")
    require(len(result["modes"]) == len(spec["cases"]), "INCOMPLETE_CASES", "Every frozen case must be present")
    for case, row in zip(spec["cases"], result["modes"]):
        require((row["condition"], row["mode"]) == (case["condition"], case["mode"])
                and row["neural_steps"] == row["decoder_frames"] == 485
                and row["reference_violations"] == 0 and row["all_finite"] is True
                and row["old_state_source"] == "OWN_LIVE_COMMITTED_STATE" and row["post_commit_reference_only"] is True,
                "FAST_NUMERICAL_FAIL", "Fixed tolerance and live-state provenance failed")
        for field in ("max_reference_state_error", "max_reference_flow_error"):
            require(row[field] is None or math.isfinite(row[field]), "NONFINITE", field)
        folder = out / case["condition"] / case["mode"]
        state = np.load(folder / "activities_full.npy", mmap_mode="r", allow_pickle=False)
        flow = np.load(folder / "flow.npy", mmap_mode="r", allow_pickle=False)
        require(state.shape == (1, 485, 45669) and state.dtype == np.float32
                and flow.shape == (1, 485, 2, 721) and np.isfinite(flow).all(), "SHAPE_OR_FINITE", str(folder))
        if case["mode"].startswith("KEEP_"):
            require(row["inactive_H"] == 5768 - case["n_retained"] and row["decoder_inactive_inputs_zero"] is True,
                    "SPARSE_CONTRACT", "Inactive state and decoder inputs")
    counts = {}
    with (out / "step_status.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            row = __import__("json").loads(line)
            tag = (row["condition"], row["mode"])
            require(row["status"] == "COMMITTED" and row["step_id"] == counts.get(tag, 0)
                    and row["old_state_source"] == "OWN_LIVE_COMMITTED_STATE", "COMMIT_SEQUENCE", str(tag))
            counts[tag] = counts.get(tag, 0) + 1
    require(counts == {(q["condition"], q["mode"]): 485 for q in spec["cases"]},
            "COMMIT_SEQUENCE", "Exact cases and commits")
    return {"status": "PASS_FAST_PLUGIN_EVIDENCE", "cases": len(spec["cases"]),
            "commits": sum(counts.values()), "fixed_atol": 1e-5, "fixed_rtol": 1e-5,
            "neural_oracle_calls": 0, "reference_violations": 0, "result": result}


class Lease:
    def init__(self, ticket):
        self.ticket, self.config = ticket, ticket["config"]
        self.job = path(ticket["job_dir"])
        require(self.job.is_relative_to(HERE / "runs"), "WRITE_SCOPE", str(self.job))

    def check(self, phase="check"):
        authorize(self.config, self.ticket["identity_key"])
        require(not (self.job / "STOP_REQUEST.json").exists(), "STOP_REQUESTED", phase)
        require(not own_path("runtime", "RESOURCE_QUARANTINE.json").exists(), "RESOURCE_QUARANTINE", phase)

    def acquire(self):
        import fcntl
        import subprocess
        self.check("acquire")
        lock = own_path("runtime", "gpu.lock")
        lock.parent.mkdir(parents=True, exist_ok=True)
        handle = lock.open("a+")
        begin = time.monotonic()
        try:
            while True:
                self.check("queue")
                acquired = False
                try:
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    acquired = True
                except BlockingIOError:
                    pass
                markers = [own_path("runtime", n) for n in ("EXTERNAL_GPU_BUSY.json", "BOARD_RESERVED.json")]
                if acquired and not any(p.exists() for p in markers):
                    try:
                        probe = subprocess.run(["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader,nounits"],
                                               capture_output=True, text=True, check=True, timeout=5)
                    except (OSError, subprocess.SubprocessError) as exc:
                        raise RunnerError("GPU_RESOURCE_UNKNOWN", str(exc)) from exc
                    if not probe.stdout.strip():
                        ledger = own_path("runtime", "invocations", "cli_" + canonical({
                            "campaign": self.config["campaign_id"], "stage": self.config["stage"]}) + ".json")
                        ledger.parent.mkdir(parents=True, exist_ok=True)
                        try:
                            with ledger.open("x", encoding="utf-8") as stream:
                                __import__("json").dump({"started_utc": utc(), "pid": os.getpid(),
                                    "identity_key": self.ticket["identity_key"], "ticket": self.ticket}, stream)
                        except FileExistsError as exc:
                            raise RunnerError("INVOCATION_LIMIT", "Science stage already attempted; no retry") from exc
                        self.check("locked")
                        return handle, time.monotonic() - begin
                if acquired:
                    fcntl.flock(handle, fcntl.LOCK_UN)
                write_json(self.job / "plugin_progress.json", {"phase": "QUEUED_GPU_BUSY", "updated_utc": utc()})
                require(time.monotonic() - begin < self.config["queue_s"], "GPU_BUSY_TIMEOUT", "No other process interrupted")
                time.sleep(.2)
        except BaseException:
            handle.close()
            raise

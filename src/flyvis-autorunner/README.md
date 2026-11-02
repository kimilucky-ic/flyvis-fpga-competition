# FlyVis AutoRunner — phase one

Independent owner: ⑧. Specification: `../docs/workstreams/FLYVIS_SPRINT_20261011_AUTORUN_T4T5.md`, section ⑧. This directory owns the CLI, scheduling, cache index, progress, failure records and bounded acceptance. It calls the accepted ① Full and ④ H/R cores; those programs and data remain read-only.

Phase two adds only the assigned④ science A→B independent CLI plugin. See [PHASE2_INTERFACE.md — 历史依赖未随包提供](../../report/archive_dependencies.md#missing-001), [researchA.fast.json — 历史依赖未随包提供](../../report/archive_dependencies.md#missing-002), [researchB.fast.json — 历史依赖未随包提供](../../report/archive_dependencies.md#missing-003) and the dedicated phase-two acceptance report. The camera609 engine/worker and all first-stage actual evidence are preserved; the original CLI source with its original release hash is saved in `phase1_snapshot/runner.py`. The limitations below describe phase one; the separate science contract enables the original full-network/decoder calculations for A/B without implementing new neural equations.

## Current acceptance boundary

**Latest actual acceptance:** [ACTUAL_SMOKE_20261011.md — 历史依赖未随包提供](../../report/archive_dependencies.md#missing-004): one authorized609-step new Python Replacement completed in37.307787s total CLI wall with cached Full, zero tolerance violations, no PL. Processes exited and the heartbeat is disabled. The dated authorized config is a closed one-shot record; daily config still defaults to no GPU permission.

Supports the frozen real-camera `selected_100_190` input: `[1,609,1,721]`, dt=.005, flow/0000/000, all45,669 nodes, H=67 B_T5c, original float32 profile, no intervention. The accepted camera result packages are imported as references without copying 111MB trajectories or rerunning GPU/CPU neural calculations.

Default GPU scope is disabled. CPU preflight, accepted-cache numerical comparison, dry-run and scheduler/resource failure tests are supported. The single approved609 GPU Replacement smoke has passed; another new run requires direct user approval for a new exact short time window. Actual runs use the existing WSL Python/CUDA environment. Formal scientific campaigns and other clips/interventions/PL are deliberately rejected in this phase.

No GUI, decoder calculation, camera capture, 24-condition campaign, 5768-node design, LIF conversion or FPGA operation is included. Decoder is explicitly `NOT_USED_PHASE1`; enabling it without a separate accepted contract fails at entry, so this runner does not claim decoder eval validation.

## Actual CLI

From Windows PowerShell in the FPGA workspace (Python and NumPy already installed):

```powershell
python -B .\flyvis-autorunner\runner.py preflight --config .\flyvis-autorunner\configs\camera609.fast.json
python -B .\flyvis-autorunner\runner.py run --config .\flyvis-autorunner\configs\camera609.fast.json --dry-run
python -B .\flyvis-autorunner\runner.py run --config .\flyvis-autorunner\configs\camera609.fast.json --cache-only
python -B .\flyvis-autorunner\runner.py status <run_id>
python -B .\flyvis-autorunner\runner.py audit --run <run_id>
```

`runner.ps1` is an optional wrapper for the same commands; the Python entry point avoids PowerShell execution-policy changes. All commands may be invoked with absolute paths from another working directory. Config data paths resolve relative to this directory. `--id` is optional, new IDs are generated; an existing ID is rejected and preserved. CLI success exits0, failure exits2 with JSON and retained details. `run` performs preflight automatically. `--cache-only` refuses missing/fresh results; `--dry-run` stops at planning and never starts a CUDA worker. `--mode fast|dev|formal` overrides config.

Bounded CPU acceptance recipe:

```powershell
python -B .\flyvis-autorunner\verify_readonly.py
python -B .\flyvis-autorunner\tests\test_scheduler.py
wsl.exe -e /opt/flyvis-gpu-venv/bin/python -B /mnt/c/Users/hzy72/Documents/ChatGPT/fpga/flyvis-autorunner/tests/test_resources.py
```

The resource tests mock every GPU process query and only exercise actual Linux file locks. None of these commands imports torch or initializes CUDA. A one-time runtime file probe is also available in `worker.py --probe-checkpoint <file> --expected-sha <hash>`; it reads the checkpoint and installed package metadata without importing torch.

## Config and real smoke

Use [configs/camera609.fast.json — 历史依赖未随包提供](../../report/archive_dependencies.md#missing-005) as a reusable example; scope, filenames, source digests, accepted receipts, existing WSL environment and bounded timeouts are explicit. [configs/README.md](configs/README.md) explains the approval fields. `freeze_config.py` creates a **new** pinned baseline config only and refuses to overwrite one; do not use it to accept an unexplained changed hash.

For the first short smoke, copy the example to a new config, set `fresh_replacement=true`, retain `fresh_full=false`, and bind the user's exact window and both preflight cache keys. A normal `run --config <approved_copy>` then reuses Full and performs exactly one new609 Replacement process. The worker imports the accepted `RStepService`, `HUpdater`, `GPUAdapter` and `Coordinator`. The runner-owned `CameraBoundR` checks the frozen frame and before/after resident parameter digests; it supplies the correct R audit instead of calling a missing Full method. It does not change an equation, edge, neuron or checkpoint.

The Full path imports unchanged `FullNetworkOracle` and runs once when a fresh Full is explicitly authorized or an accepted cached Full is unavailable. It stores the resulting Full in this directory and registers it only after the complete job passes/seals. Cache corruption fails; it does not quietly recompute and erase failed evidence. Formal planning always requests new processes; phase one does not claim a full formal protocol implementation.

## Cache and identity

Keys include stimulus bytes SHA256, both clocks, complete a0, expanded parameters, checkpoint, official source commit, original input manifest/reader identities, numeric profile, global node identity, candidate/H node map/edge partitions, static boundary, backend/core source hashes and ablation definition. A video filename or comparison ID alone cannot produce a hit. Runner source hashes and launch commands are separately recorded on new actual runs; neural cache identity tracks the reused calculation cores and immutable data, allowing a new orchestration wrapper to consume an already accepted reference.

Only accepted source receipts or this runner's sealed successful jobs can seed a cache. The old manifest dictionary and list formats are both normalized. Essential trajectory/result/identity/step-log hashes are checked once per entry, along with shape and step/COMMIT sequence. Fast then makes one chunked all-node numerical comparison, finite checks and fixed1e-5 absolute/relative tolerances. This is an array comparison, not a full CPU neural oracle, independent replay, original15-fault campaign or629-file/step audit. Fast does not perform another check campaign after PASS. Cache results record `execution_kind=accepted_cache_replay` and the original run UUID; they cannot be presented as new computation.

## Progress, permissions and failure

The accepted sequence is `FROZEN_INPUT → READY_FULL → FULL_DONE → REPLACEMENT_DONE → FAST_CHECK_DONE → SEALED → COMPLETE`. A failed phase writes `FAILED`, the previous valid state, full traceback, actual worker/launch error, completed/pending step if available, and last committed state. No fallback or automatic retry exists. Partial NPY arrays are never results. Existing failed/unsealed source attempts are preserved and ineligible.

All runner writes are within this directory, enforced with resolved paths. GPU approval contains the experiment, no-ablation scope,609 steps, exact keys, start/end timezone, one invocation per backend and conflict confirmation. Before CUDA initialization the worker checks a cooperative flock, external reservation markers and existing compute processes; busy resources queue up to `queue_s`. A persistent per-scope ledger prohibits a second attempt. Expiry and cooperative stop are checked before a new step and before COMMIT. Every worker has a computation deadline; the parent requests cooperative stop on timeout, retains an unresolved-resource record if termination is unconfirmed, and does not kill the WSL launcher or infer child completion. A CUDA synchronization failure persists quarantine and prevents later starts. No board/DMA resource exists in phase one.

Resource exclusion still needs external owners to respect the confirmed slot or marker; a process that starts outside this protocol could race a read-only GPU occupancy probe. The runner never interrupts another process or changes an existing board gate.

## Read-only contract for ②

Each `runs/<id>/` provides:

- `job.json`: atomic current state, prior valid stage, elapsed, step/total609, optional ETA, mode, experiment, worker invocation list and `PL_execution=false`.
- `events.jsonl`: chronological stage/progress records.
- `plan.json`, `preflight.json`, `config_snapshot.json`: frozen plan and entry checks.
- `run_summary.json`: result paths, original/new run UUID, cache keys, new-computation flag, PL flag, failures and timings.
- `fast_check.json`, `seal.json`: bounded numerical acceptance and essential result seal; only successful actual/cached runs seal.
- Actual worker directory: raw full trajectory, final state, step/COMMIT log, launch identity, progress, result, essential hashes; complete failures retain traceback/last state. Full and Replacement launches have separate command, UUID and timestamps; independent-process evidence never assumes different WSL PIDs.

Consumers must read `status` and `actual_new_computation` together and keep FPGA **NOT_CONNECTED**. Preflight/dry-run are planning success, not scientific run PASS. `audit` is opt-in and bounded; it checks seals/essential hashes without new neural calculation.

Timings distinguish externally measured CLI wall time (including startup/seal), preflight/cache/fast-check stages, actual worker wall/load/loop, synchronized backend computation, host/device transfer plus recording/adapter time, and orchestration outside workers. Pure transfer-only time is `null` when unchanged adapter validation cannot be separated honestly; model load and per-step upload/download counts are explicit. Cache-only replay has zero new compute, loads and device transfers. No realtime or40-minute-to-real-GPU speedup claim follows from CPU/cache acceptance.

See [ACCEPTANCE.md — 历史依赖未随包提供](../../report/archive_dependencies.md#missing-006) and [verification — 历史依赖未随包提供](../../report/archive_dependencies.md#missing-007) for measured commands, results and unverified boundaries. No new cross-project Skill is claimed before actual GPU integration is independently accepted; the bounded CPU recipe above is reproduced locally.

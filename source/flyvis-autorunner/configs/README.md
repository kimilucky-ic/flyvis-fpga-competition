# Config usage

`camera609.fast.json` is the reusable phase-one config. Paths resolve relative to `flyvis-autorunner/`, on Windows or WSL. It freezes accepted source/file digests and the camera609 binding; it does not inherit either historical camera slot or the separate 90-minute/24-condition approval. GPU defaults to disabled.

- Daily cached comparison: leave `fresh_full=false`, `fresh_replacement=false`.
- Single new replacement smoke: copy this config to a new file, set `fresh_replacement=true`; keep `fresh_full=false` to reuse Full.
- New Full computation: `fresh_full=true`, only with explicit Full scope. Full is indexed only after the entire job passes and seals.
- Config `mode=fast` is default. `dev` uses the same bounded checks with `affected_modules` identifying the changed runner/adapter/comparison modules; invoke only the corresponding scheduler/resource test. It does not rerun scientific CPU or fault campaigns.
- `formal` supports planning and rejects cache as fresh-process evidence. An actual formal campaign is **unsupported in phase one** and fails closed; preregistered repeats and true-board conditions are not replaced by fast acceptance.

For an approved short GPU slot, supply the exact cache keys emitted by preflight and set the copied config's `scope.gpu` fields:

```json
{
  "authorized": true,
  "confirmed_by_user": true,
  "authorization_reference": "Exact direct user approval message for this time window",
  "start": "YYYY-MM-DDTHH:MM:SS+08:00",
  "end": "YYYY-MM-DDTHH:MM:SS+08:00",
  "experiment_id": "camera_rectB_c5689ab635cc425ea672029502d0d402",
  "steps": 609,
  "ablation": "NONE",
  "conflict_free": true,
  "board_resources_reserved": false,
  "max_invocations": {"FullGPU": 1, "PythonReplacement": 1},
  "cache_keys": {"FullGPU": "From preflight", "PythonReplacement": "From preflight"}
}
```

This fragment is documentation, **not an approval**. Both clocks require timezone and the interval must be at most ten minutes. For the first smoke request the proposed interval is five minutes. The runner cannot infer a human approval from an old slot or elapsed waiting time. Once the scope attempts a backend, its invocation ledger prevents an automatic second attempt, including after failure.

`runtime/EXTERNAL_GPU_BUSY.json` or `runtime/BOARD_RESERVED.json` may be created by the resource owner to reserve the resource (file presence blocks new CUDA work). These files belong to this runner, not an existing board gate. Before actual CUDA initialization the worker also queries existing compute processes read-only and queues if busy. An external task must participate in reservation or respect the confirmed slot; resource arbitration across nonparticipating processes cannot be guaranteed. No existing process is killed and locks are never force-cleared.

Do not refresh pins automatically after an input/core change. Prepare a separately accepted binding/config instead; phase one deliberately refuses other clips, interventions, 24-condition jobs, and PL access.
# Phase-two science configurations

`researchA.fast.json` and `researchB.fast.json` pin④'s complete frozen scientific specs and public module. Both default to `fresh_run=true` and GPU-disabled scopes. A needs24 cases/11640 steps; B needs14/6790 and a sealed A job plus matching scientific delivery receipt. The scientific A/B case sets are distinct from the old 24-condition campaign. See `../PHASE2_INTERFACE.md` for the shared lock, no-retry ledger, result contract and default fast acceptance.

Create a new config with `freeze_science_config.py --stage A|B --out configs/<new-name>.json`. `--authorize --authorization-reference <direct-human-reference>` is only for a newly authorized bounded slot, with exact identity/budget and maximum15minutes. The dated approved A/B files from20261011 are historical consumed slots; they cannot be reused. After actual completion an explicitly permitted B copy with `fresh_run=false` can be used with `--cache-only`, producing zero CUDA calls. A independent confirmation always stays fresh.


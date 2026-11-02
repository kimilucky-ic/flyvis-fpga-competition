# T4/T5 scalable engine — first decision package

2026-10-11 / ⑦ / xc7z020clg400-2. Independent directory. **No new synthesis, implementation or board execution.**

Start with [hardware feasibility report — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-060) and [decision sheet — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-061).

## Primary deliverables

- `T4T5_FULL_GRAPH_STATS.json`: exact full-graph partition, weights, fan-in/out and dynamic parameter ranges.
- `INDEPENDENT_GRAPH_AUDIT.json`: complete original topology reconstruction plus separate scalar/record audit, source/checkpoint hashes.
- `STORAGE_BANDWIDTH_BUDGET.csv`, `ARCHITECTURE_BUDGET.json`: bytes, operations, BRAM packing, explicit unmeasured cycle/bandwidth/resource assumptions.
- `NUMERIC_PROBE.json`, `data/numeric_probe_outputs.npz`: actual bounded software comparison; not live closed loop or RTL.
- `HISTORICAL_EVIDENCE_AUDIT.json`, `evidence/`: read-only authentic report copies and old olfactory COE counts; source hashes bind exact evidence scope.
- `RESOURCE_GATE.json`: live read-only host snapshot; small OOC synthesis deferred.
- `MANIFEST_SHA256.json`, `DELIVERY_CHECK.json`: output identity and bounded final consistency checks.

## Reproduction

Use the existing Windows Python with NumPy. The independent original-source constructor audit also uses installed Torch CPU, SciPy and Matplotlib; it does not import the FlyVis Network, initialize CUDA or rerun an inference baseline. Environment identities are saved in `ENVIRONMENT.json`.

```powershell
python flyvis-fpga/t4t5_scale_20261011/extract_graph.py
python flyvis-fpga/t4t5_scale_20261011/audit_graph.py
python flyvis-fpga/t4t5_scale_20261011/numeric_probe.py
python flyvis-fpga/t4t5_scale_20261011/budget_and_evidence.py
python flyvis-fpga/t4t5_scale_20261011/finalize.py
```

Inputs are read from frozen `flyvis-circuit-selection/phase3_ablation_screen_20261010/input_bundle_r2`, official FlyVis source/checkpoint under sibling `fly`, saved original Full GPU output and the archived olfactory source at `D:/FPGA_Archive_20261011/fly-olfactory-network-fpga`. Each script writes only to this new directory. Existing⑥engineering files, original sources and all previous evidence are read-only.

`budget_and_evidence.py` preserves the dated resource snapshot as data; it does **not** refresh host resource availability. A later run must explicitly obtain a new live snapshot before any EDA decision. The reference source paths are machine-local and intentionally explicit. Delivery contains graph-derived data for local research; no external publication was performed and upstream attribution/licensing still applies.

## Data format

`partition_global_ids.npz`: H/R node global IDs and HH/RH/HR/RR edge IDs, strictly original order in each partition. Source→target orientation.

`incoming_edges.npz`: unmodified f32 weight, original global IDs/source/target and local mapping. `incoming_edges_le64.bin`: one little-endian uint64 per edge; bits[20:0] gid, [35:21] source cache, [48:36] target H, [58:49] dictionary ID, [63:59]=0. Dictionary is LE float32. H and Rin mapping vectors are explicit. The first H slots in the cache correspond to old H, then ascending Rin global IDs. Hashes must travel with configuration.

The dictionary is bit-exact for the frozen GPU expanded profile. Q24/Q20 software outputs are a separately identified finite-precision execution; they are not bitwise replacement of original floating point. Reject overflow; no saturation, sign change, dropped edges or implicit model simplification.

## Execution notes

Original cached connectome files in the Windows data directories were incomplete; the graph was reconstructed directly from the original JSON/pure constructors instead. An attempted WSL inventory was sandbox-denied; no WSL/GPU execution followed. Two early independent-audit attempts were stopped after identifying repeated lazy NPZ-array decompression inside scalar loops; arrays were cached once, the corrected full audit completed in6.62s and PASS. These exploratory stops created no PASS artifacts. Numeric probe completed in3.57s; extraction in1.68s (script timings, not FPGA performance).

No new general Skill is claimed: the workflow remains tied to this checkpoint, graph builder and parameter profile; physical RAM mapping and cross-model reuse have not been reproduced. The scripts and exact validation boundaries are preserved here as a project-specific procedure.

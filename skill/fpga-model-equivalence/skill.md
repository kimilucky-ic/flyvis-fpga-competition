---
name: fpga-model-equivalence
description: Build software reference models and compare behavior across FPGA RTL, HLS, simulation, and board execution. Use when translating fixed-point or event-driven hardware behavior, checking a generated IP against its interface contract, or deciding what a verification result proves.
---

# FPGA Model Equivalence

Use this workflow to create a trustworthy reference and compare it with FPGA implementation stages. Keep functional, cycle-accurate, synthesis, bitstream, and live-board claims separate.

## 1. Identify the real design and contract

1. Trace the instantiated production module from the top-level or block design. Do not substitute a similarly named unit-test module without comparing its equations and parameters.
2. Record exact source revision, target part, clocks/resets, tool version, and the BIT/HWH or IP metadata being compared.
3. Write the observable contract before modeling: input/output fields, bit widths, signedness, fixed-point scale, saturation/wrap/truncation, initial state, reset behavior, latency, handshake, event ordering, and simultaneous-event semantics.
4. Mark any biological, numerical, or interface assumption that is not specified by RTL or a primary source as pending.

## 2. Build the reference at the right level

1. For bit-exact checks, implement the same integer widths, intermediate widths, slices, signed casts, and update ordering as the RTL. Floating-point agreement is not bit-exact evidence.
2. Keep a small equation-level model for unit vectors and a separate network-level runner for topology, scheduling, and populations.
3. If the user needs functional rather than cycle-by-cycle agreement, state which details are intentionally abstracted and which outputs remain comparable.
4. Where practical, compare against an independently written equation path or RTL simulation to avoid testing a model against itself.

## 3. Create discriminating vectors

Include deterministic cases for zero, minimum/maximum signed values, overflow and wrap boundaries, negative inputs, threshold crossings, refractory transitions, reset, back-to-back events, simultaneous events, empty/full queues, and maximum supported fan-out. Add seeded randomized vectors only after edge cases are covered.

Save the exact input vector, expected output/state, seed, source hash, and artifact path. On mismatch, report the first differing field and time/cycle; do not hide it behind a final classification score.

For long or expensive network replays, add a bounded, real-input preflight before running the full protocol:

1. Verify the source data's expected byte size and cryptographic hash; reject Git LFS pointer text and truncated files.
2. Run a short prefix through the production reference and compare it to an existing hardware trace with exact-match rate, error, correlation, and first-divergence time.
3. If the first sample diverges, stop. Check initialization, phase alignment, output scaling, event ordering, and capture origin before spending hours on the full run.
4. Keep synthetic smoke inputs labelled separately from the author's original stimulus.

For model-to-model or quantized-inference comparisons, report several levels of agreement separately:

1. Preserve the same frozen topology, input trials, initial states, train/test split, and random seeds across candidate precisions.
2. Report task-level performance twice when a readout is involved: a readout refit on each candidate model, and the reference model's frozen readout transferred directly to candidate outputs. These answer different questions.
3. Also report internal agreement such as per-neuron spike-bit match, full-population vector exact-match timesteps, analog/output feature error, and first divergent step. Good classification accuracy does not imply timestep equivalence.
4. Repeat across fixed seeds and unresolved parameter scenarios. Keep biological or sign assumptions explicit; do not select a hardware representation from the most favorable assumption alone.
5. Bound worst-case accumulator and recurrent-state ranges from graph degree/edge weights and update equations. Include signed range, rounding allowance, saturation, and recurrence; random stimuli alone do not establish overflow safety.

## 4. Compare in evidence order

1. **Reference self-check:** unit and network invariants pass.
2. **RTL simulation:** run the same vectors against the production RTL and compare fields/cycles that the model represents.
3. **HLS C simulation or co-simulation:** compare against the same contract; do not assume HLS success proves RTL or AXI integration.
4. **Synthesis/implementation:** record resource, timing, DRC, exact part, tool version, and run directory. These show build properties, not behavioral equivalence by themselves.
5. **Board execution:** verify the actual board/part, exact BIT/HWH hashes, reset/configuration, input/output transfer, status/error registers, and raw output. Compare only claims supported by the captured run.

Do not skip an evidence level in the report or promote a result from one level into the next. A successful bitstream build does not prove that the file was loaded or that the target logic ran.

## 5. Handle mismatches and unresolved interfaces

- Re-check the source hierarchy, width arithmetic, truncation points, signed casts, reset state, cycle alignment, and interface metadata before changing the model.
- If a payload does not fit its stream or register width, stop dependent integration and show the field-width calculation and affected producer/consumer files. Do not truncate fields or silently change the contract.
- If model behavior depends strongly on an unresolved assumption, report a sensitivity range and keep the conclusion conditional. Do not tune topology or labels to force agreement.
- Preserve old known-good artifacts. Use a fresh output directory for rebuilds and keep a hash or immutable copy of the comparison target.

## 6. Record the result

For each comparison, record:

- Target design, source revision, exact part, clocks, tool versions, and artifact hashes.
- Contract version and assumptions.
- Vector set or seed, raw input/output, first mismatch if any, and numerical summary.
- Evidence level reached and what was not tested.
- Next concrete validation step.

## Project examples and boundaries

- In this project, `PQN_PN.vhd` is used by the complete fly network while `DSSN_PN.vhd` is a test kernel with different update equations. The production instance must be traced before choosing a reference.
- Existing project records report 512 PN state comparisons, nine neuron-type equation checks over 32 random states each, and 11 UART decode edge values. They also report sparse PN-to-KC accumulation matching the dense RTL result for zero, low, random 18-bit, and near-wrap states; the 14.46x speedup is only that local microbenchmark, not a whole-network speed claim.
- A verified 1,030,688,757-byte ORN input matches its Git LFS SHA-256. A 100 ms prefix run against saved FPGA population traces diverged at step 0 and had only 0.67% aggregate exact matches. The correct response is to diagnose the initial-state/time-alignment contract before launching the estimated multi-hour protocol; the data hash alone does not validate the software network.
- A saved OAL raster is a cropped 20-second/100-ORN subset, not the full 1,780-ORN event input. Do not use plots or cropped exports as a substitute for the full source event table.
- The MaleCNS selected graph has 321 neurons, 7,590 directed edges, and maximum out-degree 137. A fixed 32-slot router cannot represent it without a different architecture; never prune edges just to make a comparison pass.
- MaleCNS weight sweeps across four seeds showed why task score is insufficient: under the positive-glutamate scenario, 8-bit quantization transferred the float-trained decoder at 64.4% mean accuracy, while 12-bit reached 80.8% versus an 80.1% float baseline. Yet only 32.0% of full 321-neuron timestep vectors matched exactly at 12 bits in that scenario. The polarity assumption remains unresolved. The generated RTL vectors later passed Vivado Simulator 2024.2.2: 11 directed checks and 1,200/1,200 golden vectors exact, recorded in rtl_sim/xsim.log. The 12-bit format remains a software-supported candidate; synthesis and board signoff are not established.
- For project-specific evidence and current unresolved assumptions, read `docs/workstreams/fly-experiment.md`, `docs/workstreams/snn-google.md`, `docs/fly-Zynq7020-current-status.md`, and `docs/CODEX_PROJECT_STATUS.md` as relevant.

## Exact compression, FP32 recurrence and pipeline changes

Use this branch for template-compressed graphs or strict floating-point optimization:

1. Freeze the expanded ordered source/destination/effective-weight stream, including zero-weight edges, boundary repairs, duplicate targets and ID mapping. Prove compact decoding reproduces that stream before comparing network outputs. Compressed storage does not justify pruning or changing reduction order.
2. Record the actual arithmetic contract: binary32 rounding after each operation, operation order, FMA use, signed zero, subnormal/overflow/NaN behavior and flags as required. Do not assume a vendor accumulator has the same semantics as serial FP32 adds, or that host double arithmetic supplies an FP32 oracle.
3. Compare full initial and next states, then consecutive own-feedback prefixes. Label a CPU tick model, behavioral RTL with host FP/DPI, integer FP RTL, routed implementation and physical run separately.
4. Preserve dependency interlocks and ready/valid holds through stalls. If the current natural graph has no same-target hazard, add a small duplicate-target fixture to exercise it; absence of stalls is not proof an interlock can be removed.
5. A pipeline speedup needs the same input/state and edge identities plus updated actual cycle/resource/timing reports. Source-level capacity arithmetic, cycle conversion and a changed clock label remain conditional until their own checks pass.

FlyVis source case S1 in skill/source_review_20261018.md records 1,513,231 ordered edges (including 59,352 zero-weight edges) exactly reconstructed from a compact representation and 800 CPU steps with actual self-feedback. Later RTL/routed phases have their own accepted scope; the 2026-10-18 physical first attempt stopped at clock checking before state restore/STEP, so no full-network board equivalence is inferred.

## Numerical-comparison gates

Freeze comparison identity, common initialization, all-step/prefix versus endpoint metrics and acceptance windows before evaluation. A reference successfully generating a trajectory is different from that trajectory passing its accuracy gates. If the evaluator used endpoints where prefix maxima/RMSE were specified, correct it and re-evaluate saved trajectories; retain failures and the original thresholds.

Source cases S3/S7/S9 preserve the Q22 32-step H-prefix failure separately from later integer hardware correctness and a different learned-model CPU result. Neither can silently replace the other's comparison identity.

This skill has project-specific examples but has not been freshly validated on an unrelated FPGA design or another board. Do not claim generality beyond the recorded tests.

## Competition package use and evidence

See [parameterized usage](usage.md) and [historical verification and missing evidence](validation.md). These submission appendices supplement the Codex working source; they do not certify fresh reuse.

---
name: fpga-performance-power-accounting
description: Compare GPU and FPGA performance, resources and energy using matched work counts, measured time windows and explicit power domains. Use for benchmark interpretation, routed power reports or competition cost claims, especially when mixing measured GPU data and estimated FPGA data.
---

# FPGA Performance and Power Accounting

## Prerequisites

Identify the exact source/checkpoint, graph, precision/operation semantics, batch/sample count, time steps, input, initialization and output duties. Obtain source logs/reports rather than marketing TGP or device-typical power. Analysis alone does not authorize GPU benchmarks, new EDA runs or board operations.

## Procedure

1. **Define the denominator.** A batch of B samples each running T steps is B*T model-sample steps. Record serialized versus parallel execution. Use the same work/output scope in a comparison; changing batch size may change utilization.
2. **Separate timing phases.** Report load/initialization, adaptation/warmup, steady recurrence, transfer, commit, decode/display and post-run audit. For actual GPU timing, synchronize the relevant CUDA work and retain host plus stream timing. A software substitute for PL measures only that software path.
3. **Interpret hardware cycles conditionally.** Convert cycles/frequency only with an identified clock source and divider configuration. A runtime clock API may calculate frequency from an assumed reference rather than measure it. Keep RTL cycles, routed timing and actual host/board elapsed time separate.
4. **Identify the bottleneck before changing resources.** Distinguish scarce BRAM, bandwidth, compute/DSP and host memory. A one-edge-per-cycle input limits added arithmetic lanes. Check power-of-two RAM mapping and whole-block I/O before treating low DSP use as waste.
5. **Align energy and compute windows.** Retain raw timestamped telemetry; integrate P(t) only over synchronized compute intervals. State polling rate, gaps, field semantics and device boundary. Cross-check cumulative energy where available and retain disagreements. Report total-device and baseline-subtracted energy separately.
6. **Read FPGA estimates literally.** Pin routed DCP, tool/version, clock, reset assumptions, toggle source/SAIF, confidence label, PS load and frequency, temperature/process scenario and source hashes. Vectorless estimates and a confidence category do not provide measured error bars.
7. **State the power domain.** Distinguish PL dynamic, PS dynamic, whole-chip static, off-chip DDR/PHY, regulators and whole-board input. Do not compare a PL-only number to GPU device energy as if scopes matched.
8. **Calculate transparently.** E_step=window_energy/(B*T); throughput=(B*T)/compute_time. For a conditional FPGA estimate, E_step=P_est*t_core. A break-even P=E_GPU/t_FPGA is conditional on matched work and power boundaries. Include uncertainty and overhead omissions before quoting an advantage.
9. **Stop at the supported claim.** Report actual resource stage/part, measured versus estimated results, and the narrow missing evidence. Additional FPGA+GPU hardware does not automatically lower total system cost.

## Failure and recovery

- Wrong sample denominator or mismatched window: recompute from original logs without rerunning the model.
- Missing SAIF, unknown PS defaults, clock reference ambiguity or omitted peripherals: mark conditional/unknown, preserve the original report, and state the needed measurement.
- Conflicting telemetry fields: retain both and quantify their difference rather than selecting the most favorable result.
- A simulation-model repair must remain disclosed in any associated cycle result; it is not a silicon-speed measurement.

## Demonstrated evidence

Cases S1/S3/S4/S8 in skill/source_review_20261018.md:

- GPU SUMMARY.json at gpu_power_485_20261018_r2 records 17,460 measured steps, 43.607s, 66.75W device-domain average and 166.71mJ/step; cumulative telemetry differs by about 7.52%.
- Candidate11 POWER_RESULT.json at power_analysis_20261018_r4 records only routed vectorless estimation. The running scenario gives 1.788W and a conditional 39.36mJ at 22.01418ms core time; actual board clock/energy and equal system boundaries were unverified.
- Hardware B routed BRAM changed from 85 to 69.5 tiles; its full-system simulation is explicitly not a board throughput test.

The workflow has retained source-backed accounting cases. Fresh independent reuse is observed, not yet reproduced. Neither theoretical energy nor a fixed PL cycle count establishes end-to-end real time, whole-system energy superiority or worst-case response.

## Competition package use and evidence

See [parameterized usage](usage.md) and [historical verification and missing evidence](validation.md). These submission appendices supplement the Codex working source; they do not certify fresh reuse.

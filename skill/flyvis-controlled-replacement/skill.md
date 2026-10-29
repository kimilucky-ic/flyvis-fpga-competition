---
name: flyvis-controlled-replacement
description: Design and assess controlled FlyVis ablation or learned-module replacement experiments with frozen references, explicit interventions, closed-loop feedback and preregistered metrics. Use for model-level functional comparisons and CNN or other surrogate candidates; does not establish live-neuron replacement.
---

# Controlled FlyVis Module Replacement

## Prerequisites and scope

Pin original source/checkpoint, graph/order, complete a0, stimulus, dt, intervention IDs, precision profile, decoder and comparison identity. Start from accepted original inference, including recursive decoder eval and state invariance. Keep a CPU option for small diagnostics; resource use and hardware deployment are separately authorized.

## Procedure

1. **Define the intervention precisely.** Release blocking, freezing a state at intervention time, clamping to original a0, masking decoder input and deleting edges answer different questions. Declare affected HH/RH/HR edges, onset and maintained state; do not silently renormalize or prune.
2. **Freeze controls and criteria before evaluation.** Define Full, Sham and intervention/replacement paths, common initialization, input time, ROI, metric windows, absolute/relative errors and drift limits. Quantized H with FP32 R needs a newly bound common-start identity.
3. **Check the comparator.** Endpoint error is not prefix error. If the contract requires all-step maximum or population-time RMSE, calculate that exact prefix statistic. Verify mode labels against the executed implementation; float operators with quantized stored state are not a bit-true integer oracle.
4. **Diagnose narrowly.** Start with one-step and short own-feedback windows; preserve failing conditions. Separate moving background, target position, texture and static input rather than expanding architecture immediately. Correct comparator defects using existing traces when possible.
5. **Train and freeze a candidate independently.** Record train/validation data, seeds, model size and source identity. Freeze before generating the final held-out stimuli. Keep validation disjoint; do not tune thresholds, enlarge a model or choose new training cases after seeing final-test results without starting a new identified experiment.
6. **Run real model feedback.** The replacement uses its own previous state and the currently running remainder network. Disable production updates of the replaced original module; prohibit teacher correction or future Full states in the replacement path. Use Full only as an independent comparison.
7. **Retain evidence over time.** Check complete state trajectories, feedback chains, finite values, original-module call counts, intervention identity and official decoded output. Near zero-flow controls need declared absolute metrics rather than division by a vanishing signal.
8. **Report the tested domain.** List stimulus families, durations, initial conditions, worst errors and failed conditions. A decoder amplitude ratio is not a percentage of biological visual function; low state error is not natural-scene optical-flow accuracy, speedup or hardware proof.

## Failure and recovery

On Sham/Full mismatch, mutated checkpoint/decoder buffers, leakage, incorrect mode identity or a frozen-gate failure, preserve results and stop acceptance. Repair the source/comparator or create a fresh experiment identity; do not relax the observed failing gate. Keep software, RTL and physical feedback results separate.

## Expected verification

Independent controls and all-step metrics support the chosen model-level claim. Demonstrate genuine replacement through zero native-module updates, zero teacher corrections and consecutive feedback, not only a matching one-step prediction.

## Source evidence and limits

Case S3: cnn_cpu_texture_local_refinement_20261016/SUMMARY.json and FINAL_AUDIT.json report 10/10 held-out stimulus conditions, a frozen 31,168-parameter model, 21,000 audited formal commits, no production native-H updates or teacher correction, GPU=0 and board=0.

Cases S7/S9 record a Q22 32-step H prefix failure and an evaluator that previously inspected only endpoints. The learned-model CPU success does not override that different precision candidate's failure.

See skill/source_review_20261018.md for paths, prompts and corrections. The retained experiments reproduce their declared software comparisons; newly packaged cross-model/cross-board reuse is observed, not yet reproduced. No claim about replacing living neurons, every biological function or an FPGA CNN implementation is established.

## Competition package use and evidence

See [parameterized usage](usage.md) and [historical verification and missing evidence](validation.md). These submission appendices supplement the Codex working source; they do not certify fresh reuse.

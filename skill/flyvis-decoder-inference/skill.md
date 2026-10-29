---
name: flyvis-decoder-inference
description: Validate original pretrained FlyVis optical-flow decoder inference, including recursive eval mode, state invariance and CPU/GPU replay. Use when decoding FlyVis activity or investigating unstable decoder output; this is a software workflow, not FPGA validation.
---

# Original FlyVis decoder inference

## Tested scope and prerequisites

Reproduced on 2026-10-09 in independent WSL FlyVisCPU Python processes: Python 3.12.3, PyTorch 2.5.1+cpu and 2.7.1+cu128, RTX 5060 Laptop, official FlyVis 1.2.0 commit 92b3845cc426dd309a1a0e1b3890156c42e14021, pretrained flow/0000/000. The original 45,669-node network and all 1,513,231 edges are retained. Existing interpreters and native Linux data caches are prerequisites; this Skill does not reinstall environments.

Accepted CPU/GPU arrays and restored official checkpoint identity must be available. In this project, use the isolated experiment harness (original-workspace source: `../../flyvis-visual-experiments/scripts/experiment.py`; not a bundled dependency) and report (original-workspace source: `../../flyvis-visual-experiments/docs/flyvis_experiments_report.md`; not a bundled dependency). Choose unused output repeat numbers and retain failures.

## Non-obvious failure

This version of flyvis.utils.nn_utils.simulation sets only the parent module's training flag. Child Dropout and BatchNorm modules can still be in training mode. No gradient is required for BatchNorm running-stat updates; merely disabling gradients therefore does not establish inference mode. Initial decoder CPU/GPU runs changed BatchNorm buffers and produced device-inconsistent output; they were rejected.

Original Conv2dHexSpace.forward also projects weights to hexagonal support. Audit this separately. In the tested checkpoint, projected taps were already zero and the projection caused zero changes; it was not the cause of the observed failure. Do not disable the original projection to make a weight check pass.

## Procedure

1. Select the device and separate native cache before importing FlyVis. Reload the original checkpoint in a new process, call the checkpointed network's recover(), and verify its network tensors exactly. Reuse a frozen stimulus for device comparison; independently rendered input equality is a separate question.
2. Get the original flow decoder with view.init_decoder(checkpoint='best')['flow']. Explicitly call decoder.eval() before inference. Check every entry in decoder.named_modules(): training must be False, including Dropout and BatchNorm. Keep the official model/source unchanged.
3. Snapshot the complete decoder.state_dict(), including buffers, and verify it equals the checkpoint's decoder['flow']. Check the expected original hex-mask projection if using a different checkpoint.
4. Run network.simulate on the original movie tensor shaped [sample,frame,1,721], with the declared dt and initialization. Feed the resulting full-network activity [sample,frame,45669] into the original decoder under no-gradient/evaluation context. Central T4/T5 curves alone cannot feed this decoder, which reads 34 output cell-type spatial layers.
5. Save real predictions, shape, units, input identity, module mode flags, state comparisons, and synchronized network/decoder timing separately. For the tested four edge conditions at dt=0.005, prediction shape is [4,485,2,721]. Treat components as original model output until calibration is established.
6. Repeat from a new process with freshly restored checkpoint state. Compare against another valid eval-mode output, never against the rejected training-mode output. Apply the numerical tolerance declared before the experiment; this project used atol=rtol=1e-5. Check finite outputs, network/decoder state invariance and independent device results before reporting PASS.

## Expected result and evidence

- Correct CPU eval run: decoder_cpu_r2/result.json (original-workspace source: `../../flyvis-visual-experiments/artifacts/decoder_cpu_r2/result.json`; not a bundled dependency).
- Correct independent GPU replay: decoder_cuda_r3/result.json (original-workspace source: `../../flyvis-visual-experiments/artifacts/decoder_cuda_r3/result.json`; not a bundled dependency). All child training flags are False; network and decoder state remain exact. CPU/GPU max absolute flow difference is 9.298324584960938e-6, RMSE 7.40756129838719e-7. Independent GPU eval outputs are bitwise equal.
- Rejected initial runs: decoder_cpu_r1 and decoder_cuda_r1 in the same artifact root. GPU r2 used correct eval but its old composite comparison still referenced rejected training-mode outputs, so that FAIL record is retained. The accepted comparison uses CPU r2 and GPU r3.
- Source evidence is the upstream nn_utils.simulation implementation and task/decoder.py Conv2dHexSpace.forward. The report records the initial hypothesis, correction and measured recovery as a summary, not a verbatim chat transcript.

## Recovery and untested boundaries

If state buffers change, stop accepting that result, inspect recursive training flags and reload the checkpoint before retrying. Do not continue from mutated buffers or relax tolerances. If only mask taps change, verify that every change matches the original projection before deciding the checkpoint's invariance criterion. For memory pressure, serialize this task's conditions or reduce batch size while retaining all original nodes/edges; do not terminate unrelated workers or silently truncate the graph.

This is replicated decoder inference on one original checkpoint in existing environments. Clean installation, other GPU/CPU systems, other checkpoints, Sintel endpoint-error accuracy, physical velocity calibration, live video and FPGA/board equivalence are untested. Successful synthetic-input decoding is not an optical-flow accuracy benchmark.


## Competition package use and evidence

See [parameterized usage](usage.md) and [historical verification and missing evidence](validation.md). These submission appendices supplement the Codex working source; they do not certify fresh reuse.

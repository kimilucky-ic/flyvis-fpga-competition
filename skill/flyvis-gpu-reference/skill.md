---
name: flyvis-gpu-reference
description: Validate original FlyVis GPU rendering and pretrained inference against an accepted CPU reference in WSL, with separate timing, memory and numerical evidence. Use for FlyVis device acceleration checks; this does not cover FPGA or fly/PQN models.
---

# FlyVis GPU reference validation

## Tested scope

Validated 2026-10-09 on this RTX 5060 Laptop GPU (8 GiB, compute capability 12.0), driver 596.21, WSL2 Ubuntu 24.04.5, Python 3.12.3, PyTorch 2.7.1+cu128, torchvision 0.22.1+cu128, NumPy 1.26.4 and pandas 2.2.3. Official FlyVis commit `92b3845cc426dd309a1a0e1b3890156c42e14021`, pretrained `flow/0000/000`.

The GPU flash replay was repeated from new Python processes and restored checkpoint state, producing bitwise identical GPU outputs. Installation was performed once: clean-environment installation reuse is **observed, not yet independently reproduced**. No other GPU or cloud machine has been tested.

## Prerequisites

- Accepted CPU arrays/checkpoint identity under `C:/Users/hzy72/Documents/ChatGPT/fly/artifacts/golden_reference_v1`.
- Provisioned WSL `FlyVisCPU`, GPU Python `/opt/flyvis-gpu-venv`, separate data `/opt/flyvis-gpu-data`.
- Scripts and outputs under `../../flyvis-gpu-validation/`. See its README (original-workspace source: `../../flyvis-gpu-validation/README.md`; not a bundled dependency) for exact commands and report (original-workspace source: `../../flyvis-gpu-validation/docs/flyvis_gpu_validation_report.md`; not a bundled dependency) for measured evidence.

## Procedure

1. Read the CPU manifest and weight hash. Use a new output/cache location; do not overwrite the accepted CPU evidence. Check Windows/WSL `nvidia-smi` and run an actual CUDA tensor operation. `nvidia-smi` alone does not prove the installed PyTorch can execute GPU kernels.
2. Before importing FlyVis, explicitly select CUDA and the independent data root. A CPU-only wheel or `CUDA_VISIBLE_DEVICES=-1` defeats automatic GPU selection. Preserve the CPU environment. RTX 50 hardware requires a Blackwell-compatible PyTorch CUDA build; the tested build is pinned, not an instruction to upgrade every project.
3. Run the original `HexEye(721,25)` for three original edge offsets on GPU and CPU. Measure construction separately from rendering, synchronize CUDA before and after timing, and compare the saved arrays. Keep the same software version and CPU thread count in the device comparison.
4. Replay the accepted flash input through unchanged `compute_responses`, explicitly restoring the checkpoint wrapper with `recover()`. Verify all weight tensors before and after. Do not use response caches when benchmarking inference. Record maximum/mean absolute error, RMSE and bitwise equality separately. The supplied helper declares `atol=1e-5,rtol=1e-5`; this is this benchmark's numerical criterion, not universal model equivalence.
5. Repeat the GPU flash in a new Python process with newly restored weights. Test one original moving-edge condition first. If it succeeds, the helper can run the official 12-direction x 2-intensity configuration with a 180-second cap. Preserve sample conditions, time axes and separate first-render/cache/inference timings.
6. Recheck original CPU files and tracked upstream source; save JSON, NPY, logs and report. Update only the assigned FlyVis GPU lane checkpoint. Keep complete DSI, subcircuit boundaries and FPGA claims separate until their own validation is done.

## Failure and recovery

- CUDA unavailable: inspect the wheel version, visibility environment and WSL driver exposure before changing the driver. In this setup the Windows driver already provides WSL CUDA access.
- Memory failure: record the exact failing phase and peak memory; stop the owned test, release its process and lower batch size if it is inference. In this test HexEye construction reserved about 7.4 GiB in PyTorch, so simultaneous GPU experiments can invalidate the measured memory budget. Never truncate the network to make the benchmark fit.
- CPU/GPU mismatch: preserve the actual error and inputs. Reuse fixed stimulus arrays to separate rendering differences from neural integration differences. Do not change weights or relax a declared threshold silently.
- Timeout: preserve partial logs and rendering metadata, and report that phase as incomplete. A cached dataset must not be reported as first-render performance.

## Evidence and boundaries

Raw artifacts (original-workspace source: `../../flyvis-gpu-validation/artifacts/summary.json`; not a bundled dependency), task/correction summary (original-workspace source: `../../flyvis-gpu-validation/docs/task_record.md`; not a bundled dependency), and logs (original-workspace source: `../../flyvis-gpu-validation/logs/`; not a bundled dependency). Three HexEye images matched exactly; this is not an all-stimulus CPU/GPU proof. Flash differed from CPU by at most `1.430511474609375e-6`, while repeated GPU output matched itself exactly. Complete edge inference ran once; full CPU comparison and DSI acceptance remain unverified. This workflow does not authorize publication, GPU rental, board programming, training, pruning or source-model changes.

## Competition package use and evidence

See [parameterized usage](usage.md) and [historical verification and missing evidence](validation.md). These submission appendices supplement the Codex working source; they do not certify fresh reuse.

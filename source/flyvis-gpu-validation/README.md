# FlyVis RTX 5060 GPU validation

This is the separately assigned GPU validation lane for the original FlyVis visual network. It is separate from MaleCNS/SNN, fly/PQN and the FPGA port.

The CPU baseline and official source are read from `C:/Users/hzy72/Documents/ChatGPT/fly`. The original CPU environment `/opt/flyvis-venv` and accepted Golden Reference are preserved. The independent GPU environment is `/opt/flyvis-gpu-venv`, with model/rendering data under `/opt/flyvis-gpu-data` in WSL `FlyVisCPU`.

The GPU environment pins PyTorch 2.7.1 + CUDA 12.8 and torchvision 0.22.1. NumPy and pandas match the accepted CPU environment. RTX 5060 support requires a Blackwell-compatible PyTorch build; the previous CPU-only PyTorch 2.5.1 cannot use this GPU.

Run bounded checks from this folder in PowerShell:

```powershell
.\scripts\run_benchmark.ps1 -Stage hexeye -Device cuda
.\scripts\run_benchmark.ps1 -Stage hexeye -Device cpu
.\scripts\run_benchmark.ps1 -Stage flash -Device cuda
.\scripts\run_benchmark.ps1 -Stage flash -Device cpu
.\scripts\run_benchmark.ps1 -Stage flash -Device cuda -Repeat 2
.\scripts\run_benchmark.ps1 -Stage moving_edge -Device cuda
```

Flash replays the exact accepted input array through the original `compute_responses` API, bypassing result caches. It simulates the entire original network and retains the 65 central cells. Numerical comparison reports bitwise equality, maximum/mean absolute errors and RMSE. The numerical acceptance threshold is explicitly `atol=1e-5, rtol=1e-5`; this is distinct from exact CPU replay equality.

HexEye uses the original 721-receptor, 25-pixel geometry with three offset images. Its construction and rendering times are measured separately. The edge smoke test retains the original height, width, speed, dt and 21 offsets but selects one angle/intensity. It measures first rendering, cached rendering and inference separately; it does not establish a complete direction-selectivity result.

Every CUDA timing synchronizes the device before and after measurement. GPU memory figures are PyTorch's peak allocated/reserved memory, not whole-machine VRAM use. The paired CPU check uses the same PyTorch version, one CPU thread and unchanged official weights.

No training, pruning, model replacement or FPGA/board operation is part of this validation.

#!/usr/bin/env bash
set -euo pipefail
GPU_WORK=/mnt/c/Users/hzy72/Documents/ChatGPT/fpga/flyvis-gpu-validation
CPU_WORK=/mnt/c/Users/hzy72/Documents/ChatGPT/fly
GPU_ENV=/opt/flyvis-gpu-venv
GPU_DATA=/opt/flyvis-gpu-data
mkdir -p "$GPU_WORK/logs" "$GPU_WORK/artifacts" "$GPU_DATA/results/flow/0000"
python3 -m venv "$GPU_ENV"
"$GPU_ENV/bin/python" -m pip install torch==2.7.1 torchvision==0.22.1 --index-url https://download.pytorch.org/whl/cu128
"$GPU_ENV/bin/python" -m pip install -e "$CPU_WORK/upstream/flyvis" -c "$GPU_WORK/constraints-gpu.txt"
"$GPU_ENV/bin/python" -m pip check
if [ ! -e "$GPU_DATA/results/flow/0000/000" ]; then
    cp -a /opt/flyvis-data/results/flow/0000/000 "$GPU_DATA/results/flow/0000/000"
fi
"$GPU_ENV/bin/python" -m pip freeze > "$GPU_WORK/artifacts/requirements-gpu-lock.txt"
"$GPU_ENV/bin/python" -c 'import torch; print("TORCH",torch.__version__,"CUDA",torch.version.cuda,"AVAILABLE",torch.cuda.is_available()); assert torch.cuda.is_available(); print("GPU",torch.cuda.get_device_name(0),"CAPABILITY",torch.cuda.get_device_capability(0)); x=torch.arange(1024,device="cuda"); assert int(x.sum().item())==523776; print("CUDA_KERNEL_PASS")'

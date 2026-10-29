#!/usr/bin/env bash
set -euo pipefail
work=/mnt/c/Users/hzy72/Documents/ChatGPT/fpga/flyvis-visual-experiments
stage=${1:?stage required}
device=${2:-cuda}
repeat=${3:-1}
python=/opt/flyvis-gpu-venv/bin/python
if [[ $device == cpu ]]; then python=/opt/flyvis-venv/bin/python; fi
mkdir -p "$work/logs"
timeout 240 "$python" "$work/scripts/experiment.py" "$stage" --device "$device" --repeat "$repeat" 2>&1 | tee "$work/logs/${stage}_${device}_r${repeat}.log"

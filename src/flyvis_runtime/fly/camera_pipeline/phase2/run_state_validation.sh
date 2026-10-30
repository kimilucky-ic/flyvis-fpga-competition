#!/usr/bin/env bash
set -euo pipefail
camera_work=/mnt/c/Users/hzy72/Documents/ChatGPT/fly/camera_pipeline
output=${1:?new output name required}
if [[ "$output" == *'/'* || "$output" == *'..'* ]]; then exit 2; fi
mkdir -p "$camera_work/phase2/logs"
timeout 240 /opt/flyvis-gpu-venv/bin/python "$camera_work/phase2/validate_state.py" \
  "$camera_work/results/real_camera_native_zoh_r1" "$camera_work/phase2/results/$output" \
  2>&1 | tee "$camera_work/phase2/logs/$output.log"

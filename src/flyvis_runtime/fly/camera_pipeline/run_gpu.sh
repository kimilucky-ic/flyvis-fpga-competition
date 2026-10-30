#!/usr/bin/env bash
set -euo pipefail
camera_work=/mnt/c/Users/hzy72/Documents/ChatGPT/fly/camera_pipeline
dataset=${1:?dataset subdirectory under results required}
output=${2:?new output subdirectory under results required}
if [[ "$dataset" == *'/'* || "$output" == *'/'* || "$dataset" == *'..'* || "$output" == *'..'* ]]; then
  echo 'Use simple dataset/output names within camera_pipeline/results' >&2
  exit 2
fi
mkdir -p "$camera_work/logs"
timeout 180 /opt/flyvis-gpu-venv/bin/python "$camera_work/gpu_infer.py" "$camera_work/results/$dataset" "$camera_work/results/$output" 2>&1 | tee "$camera_work/logs/$output.log"

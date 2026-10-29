#!/usr/bin/env bash
set -euo pipefail
task=/mnt/c/Users/hzy72/Documents/ChatGPT/fly/camera_pipeline/controlled_video_20261010_r1
output=${1:?new simple output name required}
if [[ "$output" == *'/'* || "$output" == *'..'* ]]; then exit 2; fi
args=()
if [[ "${2:-}" == 'replay' ]]; then args=(--initial "$task/gpu_full_r1/initial_state.pt"); fi
timeout 240 /opt/flyvis-gpu-venv/bin/python "$task/run_full.py" "$task/$output" "${args[@]}" \
  2>&1 | tee "$task/logs/$output.log"

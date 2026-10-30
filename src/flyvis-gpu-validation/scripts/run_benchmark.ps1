param(
    [ValidateSet('cpu','cuda')][string]$Device = 'cuda',
    [ValidateSet('hexeye','flash','moving_edge','moving_edge_full')][string]$Stage = 'flash',
    [int]$Threads = 1,
    [int]$Repeat = 1
)
$ErrorActionPreference = 'Stop'
$gpuWorkRoot = Split-Path $PSScriptRoot -Parent
$gpuScriptPath = '/mnt/c/Users/hzy72/Documents/ChatGPT/fpga/flyvis-gpu-validation/scripts/benchmark.py'
$gpuLogPath = Join-Path $gpuWorkRoot "logs/${Stage}_${Device}_t${Threads}_r${Repeat}.log"
& wsl -d FlyVisCPU -- timeout 180 /opt/flyvis-gpu-venv/bin/python -u $gpuScriptPath --device $Device --stage $Stage --threads $Threads --repeat $Repeat *> $gpuLogPath
if ($LASTEXITCODE -ne 0) { throw "GPU benchmark failed; see $gpuLogPath" }
Write-Output "Completed. Log: $gpuLogPath"

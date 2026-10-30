param([string]$Scope, [string]$HardwareHandoff, [switch]$Execute, [switch]$Stop, [string]$Draft, [string]$PreparedBundle, [switch]$ManualPrepare, [switch]$MinimalCompute, [switch]$Live5, [string]$ColdInit)
$ErrorActionPreference = 'Stop'
$jointPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$jointController = Join-Path $PSScriptRoot 'gui_v1\joint_camera_controller.py'
$jointArguments = @('-X','utf8','-B',$jointController)
if ($Stop) { $jointArguments += '--stop' }
elseif ($Draft) { $jointArguments += @('--draft',$Draft) }
else {
    if ($ManualPrepare) { $jointArguments += '--manual-prepare' }
    if ($MinimalCompute) { $jointArguments += '--minimal-compute' }
    if ($Live5) { $jointArguments += '--live5' }
    if ($ColdInit) { $jointArguments += @('--cold-init',$ColdInit) }
    if ($PreparedBundle) { $jointArguments += @('--prepared-bundle',$PreparedBundle) }
    if ($Scope) { $jointArguments += @('--scope',$Scope) }
    if ($HardwareHandoff) { $jointArguments += @('--hardware-handoff',$HardwareHandoff) }
    if ($Execute) { $jointArguments += '--execute' }
}
& $jointPython @jointArguments
if ($LASTEXITCODE -ne 0) { throw 'Camera joint admission or execution failed; inspect the current run logs. No automatic retry or replay fallback.' }

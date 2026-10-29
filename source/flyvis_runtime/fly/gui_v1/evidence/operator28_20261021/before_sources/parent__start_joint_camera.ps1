param([string]$Scope, [string]$HardwareHandoff, [switch]$Execute, [switch]$Stop, [string]$Draft, [string]$PreparedBundle, [switch]$ManualPrepare, [switch]$MinimalCompute, [switch]$Live5, [switch]$Workbench, [string]$ColdInit, [switch]$FixedNotebook, [int]$DurationSeconds = 60, [switch]$ShortTest)
$ErrorActionPreference = 'Stop'
$jointPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$jointController = Join-Path $PSScriptRoot 'gui_v1\joint_camera_controller.py'
$jointArguments = @('-X','utf8','-B',$jointController)
if ($Stop) { $jointArguments += '--stop' }
elseif ($Draft) { $jointArguments += @('--draft',$Draft) }
else {
    if ($Workbench) { $jointArguments += '--workbench' }
    if ($FixedNotebook) { $jointArguments += @('--fixed-notebook','--run-duration-s',"$DurationSeconds") }
    if ($ShortTest) { $jointArguments += '--short-test' }
    if ($ManualPrepare) { $jointArguments += '--manual-prepare' }
    if ($MinimalCompute) { $jointArguments += '--minimal-compute' }
    if ($Live5) { $jointArguments += '--live5' }
    if ($ColdInit) { $jointArguments += @('--cold-init',$ColdInit) }
    if ($PreparedBundle) { $jointArguments += @('--prepared-bundle',$PreparedBundle) }
    if ($Scope) { $jointArguments += @('--scope',$Scope) }
    if ($HardwareHandoff) { $jointArguments += @('--hardware-handoff',$HardwareHandoff) }
    if ($Execute) { $jointArguments += '--execute' }
}
if ($Workbench) {
    $workbenchLog = Join-Path $PSScriptRoot 'gui_v1\runtime\workbench_launch.log'
    try {
        & $jointPython @jointArguments *>&1 | Tee-Object -FilePath $workbenchLog -Append | Out-Null
        if ($LASTEXITCODE -ne 0) { throw 'FlyVis workbench stopped before normal completion. See workbench_launch.log.' }
    } catch {
        $_ | Out-String | Add-Content -LiteralPath $workbenchLog -Encoding UTF8
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.MessageBox]::Show("FlyVis could not start safely. No automatic device retry.`n$workbenchLog", 'FlyVis') | Out-Null
        exit 1
    }
    exit 0
}
& $jointPython @jointArguments
if ($LASTEXITCODE -ne 0) { throw 'Camera joint admission or execution failed; inspect the current run logs. No automatic retry or replay fallback.' }

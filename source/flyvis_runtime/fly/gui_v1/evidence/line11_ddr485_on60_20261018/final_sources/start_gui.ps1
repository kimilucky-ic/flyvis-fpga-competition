param([int]$Port = 8771, [switch]$NoOpen, [switch]$VerifyData, [string]$Line11Result,
      [switch]$Line11Stream, [string]$Line11PCAddress, [int]$Line11Steps = 32, [switch]$Line11DDR,
      [switch]$Line11Camera, [int]$CameraDevice = 0)
$ErrorActionPreference = 'Stop'
$taskPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) {
    $taskPythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $taskPythonCommand) { throw 'Python 3.10+ with NumPy is required. No GPU or FlyVis installation is needed.' }
    $taskPython = $taskPythonCommand.Source
}
& $taskPython -c 'import numpy; import sys; assert sys.version_info >= (3, 10)'
if ($LASTEXITCODE -ne 0) { throw 'The selected Python needs NumPy and Python 3.10+.' }
$taskArguments = @((Join-Path $PSScriptRoot 'gui_v1\server.py'), '--port', "$Port")
if ($Line11Camera -and -not $Line11DDR) { throw 'Line11Camera requires Line11DDR; records a NEW bounded clip, never uses an old input.' }
if ($NoOpen) { $taskArguments += '--no-open' }
if ($VerifyData) { $taskArguments += '--verify-data' }
if ($Line11Result) { $taskArguments += @('--line11-result', $Line11Result) }
if ($Line11DDR) {
    if ($Line11Stream -or $Line11Result) { throw 'Line11DDR uses its own fresh first-step admission, not an old result.' }
    if (-not $Line11PCAddress) {
        $taskAddresses = @(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -like '192.168.2.*' -and $_.AddressState -eq 'Preferred' })
        if ($taskAddresses.Count -ne 1) { throw 'Specify -Line11PCAddress with the actual board-facing PC IPv4.' }
        $Line11PCAddress = $taskAddresses[0].IPAddress
    }
    if ($Line11Camera) { $Line11Steps=485; $taskArguments+=@('--line11-camera','--line11-camera-device',"$CameraDevice") }
    $taskArguments += @('--line11-ddr','--line11-pc-address',$Line11PCAddress,'--line11-steps',"$Line11Steps")
    if (-not $NoOpen) { $taskArguments += '--no-open' } # Operator opens the GUI; no browser automation.
}
if ($Line11Stream) { $taskArguments += @('--line11-stream','--line11-pc-address',$Line11PCAddress,'--line11-steps',"$Line11Steps") }
& $taskPython @taskArguments
if ($LASTEXITCODE -ne 0) { throw "GUI exited with code $LASTEXITCODE. Check the data paths or choose another port." }

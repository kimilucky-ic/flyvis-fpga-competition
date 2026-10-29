param([int]$Port = 8771, [switch]$NoOpen)
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
if ($NoOpen) { $taskArguments += '--no-open' }
& $taskPython @taskArguments
if ($LASTEXITCODE -ne 0) { throw "GUI exited with code $LASTEXITCODE. Check the data paths or choose another port." }

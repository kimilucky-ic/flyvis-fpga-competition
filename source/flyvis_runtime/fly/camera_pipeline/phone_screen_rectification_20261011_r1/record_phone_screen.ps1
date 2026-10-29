$ErrorActionPreference = 'Stop'
$flyRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$pythonPath = Join-Path $flyRoot '.venv\Scripts\python.exe'
$recorderPath = Join-Path $PSScriptRoot 'record_selfserve.py'
Write-Host 'Prepare the existing phone player and keep the white square visible.'
Write-Host 'In the computer preview press R. When the green RECORDING cue appears, tap the phone.'
Write-Host 'Hold the phone still through playback. Q stops; recording is bounded to 12 seconds.'
& $pythonPath $recorderPath --user-authorized --duration-s 12 --preview-timeout-s 180
if ($LASTEXITCODE -ne 0) { Write-Host ('Recorder exited with code '+$LASTEXITCODE) }
Read-Host 'Press Enter to close'

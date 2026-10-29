param([string]$Stage='inspect')
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:TEMP=Join-Path $PSScriptRoot 'tmp'
$env:TMP=$env:TEMP
New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
$env:OMP_NUM_THREADS='1'
$env:PROCESSOR_ARCHITECTURE='AMD64'
& 'D:/2026.1/Vivado/bin/vivado.bat' -mode batch -notrace -source ($Stage+'.tcl') -log ($Stage+'.log') -journal ($Stage+'.jou')
exit $LASTEXITCODE

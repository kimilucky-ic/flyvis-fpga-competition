param([string]$Stage='bitgen')
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:TEMP=Join-Path $PSScriptRoot 'tmp'
$env:TMP=$env:TEMP
$env:OMP_NUM_THREADS='1'
$env:PROCESSOR_ARCHITECTURE='AMD64'
& 'C:/AMDDesignTools/2026.1.1/Vivado/bin/vivado.bat' -mode batch -notrace -source bitgen.tcl -log bitgen.log -journal bitgen.jou
exit $LASTEXITCODE

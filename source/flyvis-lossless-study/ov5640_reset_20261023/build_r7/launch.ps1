param([string]$Stage='synth')
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:TEMP=Join-Path $PSScriptRoot 'tmp'
$env:TMP=$env:TEMP
$env:OMP_NUM_THREADS='1'
$env:PROCESSOR_ARCHITECTURE='AMD64'
$script=if ($Stage -eq 'route') {'route_soc.tcl'} else {'build_soc.tcl'}
& 'C:/AMDDesignTools/2026.1.1/Vivado/bin/vivado.bat' -mode batch -notrace -source $script -log ($Stage+'.log') -journal ($Stage+'.jou')
exit $LASTEXITCODE

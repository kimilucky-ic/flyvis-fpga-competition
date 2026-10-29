param([Parameter(Mandatory=$true)][string]$RunDir)
$ErrorActionPreference='Stop'
$bResolved=[System.IO.Path]::GetFullPath($RunDir)
$bBuildRoot=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'build'))+[System.IO.Path]::DirectorySeparatorChar
if(!$bResolved.StartsWith($bBuildRoot,[System.StringComparison]::OrdinalIgnoreCase)){throw 'Not an isolated B OOC build path'}
if(!(Test-Path -LiteralPath (Join-Path $bResolved 'RUN_IDENTITY.json'))){throw 'Missing bound identity'}
. (Join-Path $PSScriptRoot '..\..\phase3_20261010\amd2026_environment.ps1') -App Vivado
$env:TEMP=Join-Path $bResolved 'tmp';$env:TMP=$env:TEMP
Push-Location $bResolved
try {
    & (Join-Path $env:XILINX_VIVADO 'bin\vivado.bat') -mode batch -source synth_fullscale.tcl -log vivado.log -journal vivado.jou
    if($LASTEXITCODE -ne 0){throw 'OOC synthesis/reporting failed; preserve all logs'}
    if(!(Select-String -LiteralPath vivado.log -Pattern 'B433880_OOC_SYNTHESIS_COMPLETE_NO_IMPLEMENTATION')){throw 'OOC completion marker absent'}
    Write-Output ('B_OOC_RUN='+$bResolved)
} finally {Pop-Location}

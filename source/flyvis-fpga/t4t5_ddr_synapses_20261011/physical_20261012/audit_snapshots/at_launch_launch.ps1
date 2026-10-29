param([Parameter(Mandatory=$true)][string]$RunDir)
$ErrorActionPreference='Stop'
$pRun=[System.IO.Path]::GetFullPath($RunDir)
$pRoot=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'build'))+[System.IO.Path]::DirectorySeparatorChar
if(!$pRun.StartsWith($pRoot,[System.StringComparison]::OrdinalIgnoreCase)){throw 'Outside own physical build root'}
. (Join-Path $PSScriptRoot '..\..\phase3_20261010\amd2026_environment.ps1') -App Vivado
$env:TEMP=Join-Path $pRun 'tmp';$env:TMP=$env:TEMP
Push-Location $pRun
try {
    & (Join-Path $env:XILINX_VIVADO 'bin\vivado.bat') -mode batch -source implement.tcl -log vivado.log -journal vivado.jou
    if($LASTEXITCODE -ne 0){throw 'Bounded physical attempt failed; retain evidence, no retry'}
    if(!(Select-String -LiteralPath vivado.log -Pattern 'B433880_SINGLE_OOC_PHYSICAL_ATTEMPT_COMPLETE')){throw 'Completion marker absent'}
} finally {Pop-Location}

param([Parameter(Mandatory=$true)][string]$RunDir)
$ErrorActionPreference='Stop'
$fullRoot=$PSScriptRoot
$fullBase=Join-Path $fullRoot 'build'
$fullResolved=[System.IO.Path]::GetFullPath($RunDir)
if(!$fullResolved.StartsWith(([System.IO.Path]::GetFullPath($fullBase)+[System.IO.Path]::DirectorySeparatorChar),[System.StringComparison]::OrdinalIgnoreCase)){throw 'Run directory is outside hardware B full-scale build root'}
if(!(Test-Path -LiteralPath (Join-Path $fullResolved 'RUN_IDENTITY.json'))){throw 'Missing gated run identity'}
. (Join-Path $fullRoot '..\..\phase3_20261010\amd2026_environment.ps1') -App Vivado
$env:TEMP=Join-Path $fullResolved 'tmp';$env:TMP=$env:TEMP
$fullBin=Join-Path $env:XILINX_VIVADO 'bin'
Push-Location $fullResolved
try {
    & (Join-Path $fullBin 'xvlog.bat') --sv -i . edge_fifo.sv axi_edge_reader.sv ddr_synapse_core.sv ddr_synapse_top.sv tb_fullscale.sv --log xvlog.log
    if($LASTEXITCODE -ne 0){throw 'Full-scale RTL compile failed'}
    & (Join-Path $fullBin 'xelab.bat') work.tb_fullscale -s fullscale_sim -debug typical --mt off -log xelab.log
    if($LASTEXITCODE -ne 0){throw 'Full-scale RTL elaboration failed'}
    & (Join-Path $fullBin 'xsim.bat') fullscale_sim -runall -log xsim.log
    if($LASTEXITCODE -ne 0){throw 'Full-scale simulation process failed'}
    if(!(Select-String -LiteralPath xsim.log -Pattern 'FULL_ALL_PASS') -or (Select-String -LiteralPath xsim.log -Pattern 'Fatal:|FATAL|Error:')){throw 'Missing clean full-scale PASS marker'}
    Write-Output ('FULL_SCALE_RUN='+$fullResolved)
} finally {Pop-Location}

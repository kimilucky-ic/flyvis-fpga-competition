param([string]$Fixture='fixtures92',[ValidateSet(1,2,4)][int]$Banks=1)
$ErrorActionPreference='Stop'
$researchRoot=$PSScriptRoot
# Read-only environment bootstrap: process-local tool/license variables only.
. (Join-Path $researchRoot '..\phase3_20261010\amd2026_environment.ps1') -App Vivado
$researchBuild=Join-Path $researchRoot ('build\s'+$Fixture.Replace('fixtures','')+'b'+$Banks+'_'+(Get-Date -Format 'HHmmss'))
New-Item -ItemType Directory -Path $researchBuild | Out-Null
New-Item -ItemType Directory -Path (Join-Path $researchBuild 'rom') | Out-Null
New-Item -ItemType Directory -Path (Join-Path $researchBuild 'tmp') | Out-Null
$env:TEMP=Join-Path $researchBuild 'tmp'; $env:TMP=$env:TEMP
Copy-Item -Path (Join-Path $researchRoot ($Fixture+'\*.mem')) -Destination (Join-Path $researchBuild 'rom')
Copy-Item -LiteralPath (Join-Path $researchRoot ($Fixture+'\fixture_config.svh')) -Destination $researchBuild
Add-Content -LiteralPath (Join-Path $researchBuild 'fixture_config.svh') -Value ('`define TEST_BANKS '+$Banks) -Encoding ascii
Copy-Item -LiteralPath (Join-Path $researchRoot 'rtl\scalable_source_raw_core.sv'),(Join-Path $researchRoot 'rtl\tb_scalable.sv') -Destination $researchBuild
Copy-Item -LiteralPath (Join-Path $researchRoot ($Fixture+'\manifest.json')) -Destination $researchBuild
$researchBin=Join-Path $env:XILINX_VIVADO 'bin'
Push-Location $researchBuild
try {
    & (Join-Path $researchBin 'xvlog.bat') --sv -i . scalable_source_raw_core.sv tb_scalable.sv --log xvlog.log
    if($LASTEXITCODE -ne 0){throw 'xvlog failed'}
    & (Join-Path $researchBin 'xelab.bat') work.tb_scalable -s scalable_sim -debug typical --mt off -log xelab.log
    if($LASTEXITCODE -ne 0){throw 'xelab failed'}
    & (Join-Path $researchBin 'xsim.bat') scalable_sim -runall -log xsim.log
    if($LASTEXITCODE -ne 0){throw 'xsim failed'}
    if(!(Select-String -LiteralPath xsim.log -Pattern 'ALL_PASS')){throw 'Simulation lacks ALL_PASS'}
    Write-Output ('SIMULATION_ARTIFACT='+$researchBuild)
} finally {Pop-Location}

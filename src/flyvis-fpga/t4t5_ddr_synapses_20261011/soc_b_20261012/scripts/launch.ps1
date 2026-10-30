param([string]$Build,[string]$Stage,[string]$StageDir,[switch]$StandaloneXsim,[switch]$RebuildSnapshot)
$ErrorActionPreference='Stop'
$bRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../work'))+[IO.Path]::DirectorySeparatorChar
$bBuild=[IO.Path]::GetFullPath($Build)
if(!$bBuild.StartsWith($bRoot,[StringComparison]::OrdinalIgnoreCase)){throw 'Outside B SoC build root'}
. (Join-Path $PSScriptRoot '../../../phase3_20261010/amd2026_environment.ps1') -App Vivado
$env:PATH=(Join-Path $env:XILINX_VIVADO 'bin')+';'+$env:PATH
$env:TEMP=Join-Path $bBuild 'tmp';$env:TMP=$env:TEMP
Push-Location $bBuild
try {
 if($StandaloneXsim){
  if($Stage -ne 'simulate'){throw 'Standalone XSim only'}
  $bSim=Join-Path $bBuild 'project/b_soc.sim/sim_1/behav/xsim'
  if(!(Test-Path -LiteralPath (Join-Path $bSim 'xsim.dir/tb_soc_behav'))){throw 'No compiled actual-BD snapshot'}
  Push-Location $bSim
  try {
   if($RebuildSnapshot){
    & .\compile.bat
    if($LASTEXITCODE -ne 0){throw 'Actual-BD compile failed'}
    & .\elaborate.bat
    if($LASTEXITCODE -ne 0){throw 'Actual-BD elaborate failed'}
   }
   if(Test-Path -LiteralPath 'system_pass.txt'){Move-Item -LiteralPath 'system_pass.txt' -Destination (Join-Path $StageDir 'preexisting_system_pass.txt')}
   & (Join-Path $env:XILINX_VIVADO 'bin/xsim.bat') tb_soc_behav -R -log simulate.log
   if($LASTEXITCODE -ne 0){throw 'Standalone XSim failed'}
   if(!(Test-Path -LiteralPath 'system_pass.txt')){throw 'No actual-BD system PASS; synthesis forbidden'}
   Copy-Item -LiteralPath 'system_pass.txt' -Destination (Join-Path $bBuild 'system_pass.txt')
  } finally {Pop-Location}
 } else {
 & (Join-Path $env:XILINX_VIVADO 'bin/vivado.bat') -mode batch -source (Join-Path $PSScriptRoot 'build_soc.tcl') -log (Join-Path $StageDir 'vivado.log') -journal (Join-Path $StageDir 'vivado.jou') -tclargs $bBuild $Stage
 if($LASTEXITCODE -ne 0){throw "B SoC stage $Stage failed; retain logs"}
 }
} finally {Pop-Location}

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
 if($Stage -eq 'unit'){
  Push-Location (Join-Path $bBuild 'source')
  try {
   & (Join-Path $env:XILINX_VIVADO 'bin/xvlog.bat') --sv source_state_ram.sv axi_edge_reader.sv ddr_state_loader.sv ddr_candidate_writer.sv tb_bulk_units.sv -log (Join-Path $StageDir 'compile.log')
   if($LASTEXITCODE -ne 0){throw 'Unit compile failed'}
   & (Join-Path $env:XILINX_VIVADO 'bin/xelab.bat') tb_bulk_units -s bulk_units -mt off -debug off -log (Join-Path $StageDir 'elaborate.log')
   if($LASTEXITCODE -ne 0){throw 'Unit elaborate failed'}
   & (Join-Path $env:XILINX_VIVADO 'bin/xsim.bat') bulk_units -R -log (Join-Path $StageDir 'simulate.log')
   if($LASTEXITCODE -ne 0 -or !(Test-Path 'unit_pass.txt')){throw 'Unit simulation did not pass'}
   Copy-Item -LiteralPath 'unit_pass.txt' -Destination (Join-Path $StageDir 'unit_pass.txt')
  } finally {Pop-Location}
 } elseif($StandaloneXsim){
  if($Stage -ne 'simulate'){throw 'Standalone XSim only'}
  $bSim=Join-Path $bBuild 'project/b_soc.sim/sim_1/behav/xsim'
  if(!(Test-Path -LiteralPath (Join-Path $bSim 'elaborate.bat'))){throw 'No compiled actual-BD snapshot'}
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

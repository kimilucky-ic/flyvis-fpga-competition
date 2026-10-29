param([ValidateSet('mini','addr15','92','298')][string]$Fixture='mini')
$ErrorActionPreference='Stop'
$bRoot=$PSScriptRoot
. (Join-Path $bRoot '..\phase3_20261010\amd2026_environment.ps1') -App Vivado
$bRun=Join-Path $bRoot ('build\'+$Fixture+'_'+(Get-Date -Format 'yyyyMMdd_HHmmss_fff'))
New-Item -ItemType Directory -Path $bRun | Out-Null
New-Item -ItemType Directory -Path (Join-Path $bRun 'rom'),(Join-Path $bRun 'tmp') | Out-Null
$env:TEMP=Join-Path $bRun 'tmp';$env:TMP=$env:TEMP
Copy-Item -Path (Join-Path $bRoot ('fixtures\'+$Fixture+'\*.mem')) -Destination (Join-Path $bRun 'rom')
Copy-Item -LiteralPath (Join-Path $bRoot ('fixtures\'+$Fixture+'\fixture_config.svh')),(Join-Path $bRoot ('fixtures\'+$Fixture+'\manifest.json')) -Destination $bRun
Copy-Item -Path (Join-Path $bRoot 'rtl\*.sv') -Destination $bRun
$bSources=Get-ChildItem -LiteralPath $bRun -Filter '*.sv' | ForEach-Object { @{name=$_.Name;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower()} }
@{tool='XSim 2026.1.1';fixture=$Fixture;created=(Get-Date -Format o);sources=$bSources;fixture_manifest_sha256=(Get-FileHash -LiteralPath (Join-Path $bRun 'manifest.json')).Hash.ToLower()} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $bRun 'RUN_IDENTITY.json') -Encoding utf8
$bBin=Join-Path $env:XILINX_VIVADO 'bin'
Push-Location $bRun
try {
    & (Join-Path $bBin 'xvlog.bat') --sv -i . edge_fifo.sv axi_edge_reader.sv ddr_synapse_core.sv ddr_synapse_top.sv tb_ddr_synapses.sv --log xvlog.log
    if($LASTEXITCODE -ne 0){throw 'RTL compile failed'}
    & (Join-Path $bBin 'xelab.bat') work.tb_ddr_synapses -s b_stream_sim -debug typical --mt off -log xelab.log
    if($LASTEXITCODE -ne 0){throw 'RTL elaboration failed'}
    & (Join-Path $bBin 'xsim.bat') b_stream_sim -runall -log xsim.log
    if($LASTEXITCODE -ne 0){throw 'RTL simulation failed'}
    if(!(Select-String -LiteralPath xsim.log -Pattern 'ALL_PASS') -or (Select-String -LiteralPath xsim.log -Pattern 'Fatal:|FATAL|Error:')){throw 'RTL simulation lacks clean ALL_PASS'}
    Write-Output ('SIMULATION_ARTIFACT='+$bRun)
} finally {Pop-Location}

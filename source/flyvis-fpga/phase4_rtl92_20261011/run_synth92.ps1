param([int]$MinimumFreeMB=4096)
$ErrorActionPreference='Stop'
$researchRoot=$PSScriptRoot
$researchOs=Get-CimInstance Win32_OperatingSystem
$researchCpu=Get-CimInstance Win32_Processor
$researchTools=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(vivado|vitis|v\+\+|xelab|xsim)\.exe$' } | Select-Object ProcessId,Name)
$researchSnapshot=[ordered]@{
    sampled_local_time=(Get-Date -Format o)
    free_physical_mb=[math]::Round($researchOs.FreePhysicalMemory/1024,2)
    total_physical_mb=[math]::Round($researchOs.TotalVisibleMemorySize/1024,2)
    cpu_load_percent=$researchCpu.LoadPercentage
    logical_processors=$researchCpu.NumberOfLogicalProcessors
    active_eda_processes=$researchTools
    conservative_gate_mb=$MinimumFreeMB
    gate_is_a_research_policy_not_a_measured_vivado_minimum=$true
    requested_stage='92_NODE_OOC_SYNTHESIS_ONLY'
}
$researchAllowed=($researchSnapshot.free_physical_mb -ge $MinimumFreeMB -and $researchSnapshot.cpu_load_percent -le 50 -and $researchTools.Count -eq 0)
$researchSnapshot['decision']=if($researchAllowed){'RUN_SINGLE_THREAD_SYNTHESIS'}else{'DEFER_SYNTHESIS_RESOURCE_GATE'}
$researchSnapshot | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $researchRoot 'artifacts\synthesis_resource_gate.json') -Encoding utf8
if(!$researchAllowed){ $researchSnapshot | ConvertTo-Json -Depth 6; exit 0 }
. (Join-Path $researchRoot '..\phase3_20261010\amd2026_environment.ps1') -App Vivado
$researchBuild=Join-Path $researchRoot ('build\syn92_'+(Get-Date -Format 'HHmmss'))
New-Item -ItemType Directory -Path $researchBuild | Out-Null
New-Item -ItemType Directory -Path (Join-Path $researchBuild 'rom'),(Join-Path $researchBuild 'tmp') | Out-Null
Copy-Item -LiteralPath (Join-Path $researchRoot 'rtl\scalable_source_raw_core.sv'),(Join-Path $researchRoot 'synth92.tcl') -Destination $researchBuild
Copy-Item -LiteralPath (Join-Path $researchRoot 'fixtures92\edges.mem'),(Join-Path $researchRoot 'fixtures92\neurons.mem') -Destination (Join-Path $researchBuild 'rom')
Copy-Item -LiteralPath (Join-Path $researchRoot 'fixtures92\manifest.json') -Destination $researchBuild
'create_clock -name core_clk -period 10 [get_ports clk]' | Set-Content -LiteralPath (Join-Path $researchBuild 'clock.xdc') -Encoding ascii
$env:TEMP=Join-Path $researchBuild 'tmp';$env:TMP=$env:TEMP
Push-Location $researchBuild
try {
    & (Join-Path $env:XILINX_VIVADO 'bin\vivado.bat') -mode batch -source synth92.tcl -log vivado.log -journal vivado.jou
    if($LASTEXITCODE -ne 0){throw 'Synthesis failed; retain failure logs'}
    Write-Output ('SYNTHESIS_ARTIFACT='+$researchBuild)
} finally {Pop-Location}

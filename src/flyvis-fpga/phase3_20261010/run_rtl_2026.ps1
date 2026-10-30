param([ValidateSet('core','axi')][string]$Design='core')
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $root 'amd2026_environment.ps1') -App Vivado
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$work = Join-Path $root ("build\rtl_${Design}_sim_2026_1_q22_$stamp")
New-Item -ItemType Directory -Path $work | Out-Null
New-Item -ItemType Directory -Path (Join-Path $work 'rom'),(Join-Path $work 'artifacts') | Out-Null
Copy-Item -LiteralPath (Join-Path $root 'rom\edges_q22.mem'),(Join-Path $root 'rom\neurons_q22.mem'),(Join-Path $root 'rom\animation_requests_q22.mem'),(Join-Path $root 'rom\animation_expected_q22.mem') -Destination (Join-Path $work 'rom')
$bin = Join-Path $env:XILINX_VIVADO 'bin'
Push-Location $work
try {
    $sources=@((Join-Path $root 'rtl\flyvis_source_raw_core.sv'))
    $top='tb_flyvis_source_raw'
    if($Design -eq 'axi') { $sources+=(Join-Path $root 'rtl\flyvis_source_raw_axil.sv'); $top='tb_flyvis_axil' }
    $sources+=(Join-Path $root ("rtl\$top.sv"))
    & (Join-Path $bin 'xvlog.bat') --sv @sources --log 'xvlog.log'
    if ($LASTEXITCODE -ne 0) { throw "RTL compile failed: $LASTEXITCODE" }
    & (Join-Path $bin 'xelab.bat') "work.$top" -s flyvis_source_raw_q22 -debug typical -log 'xelab.log'
    if ($LASTEXITCODE -ne 0) { throw "RTL elaboration failed: $LASTEXITCODE" }
    & (Join-Path $bin 'xsim.bat') flyvis_source_raw_q22 -runall -log 'xsim.log'
    if ($LASTEXITCODE -ne 0) { throw "RTL simulation failed: $LASTEXITCODE" }
    $audit='audit_rtl_results.py'
    if($Design -eq 'axi') { $audit='audit_axi_results.py' }
    & python (Join-Path $root $audit) --run-dir $work
    if ($LASTEXITCODE -ne 0) { throw "RTL result audit failed: $LASTEXITCODE" }
} finally { Pop-Location }

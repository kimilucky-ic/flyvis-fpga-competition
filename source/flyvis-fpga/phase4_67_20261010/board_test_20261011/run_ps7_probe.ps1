$ErrorActionPreference = 'Stop'
$p4root = Split-Path -Parent $PSScriptRoot
. (Join-Path $p4root '..\phase3_20261010\amd2026_environment.ps1') -App Vivado
$env:XILINX_LOCAL_USER_DATA = 'no'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$probeLog = Join-Path $PSScriptRoot "ps7_probe_$stamp.log"
$probeJournal = Join-Path $PSScriptRoot "ps7_probe_$stamp.jou"
$probeConsole = Join-Path $PSScriptRoot "ps7_probe_$stamp.console.log"
Push-Location $PSScriptRoot
try {
    & (Join-Path $env:XILINX_VIVADO 'bin\loader.bat') -exec vivado -mode batch -source (Join-Path $PSScriptRoot 'probe_ps7_bank_import.tcl') -log $probeLog -journal $probeJournal 2>&1 | Tee-Object -FilePath $probeConsole
    if ($LASTEXITCODE -ne 0) { throw "Local PS7 probe failed; see $probeLog" }
    if (!(Select-String -LiteralPath $probeLog -SimpleMatch 'PASS_LOCAL_PS7_BANK_IMPORT_REPRODUCTION' -Quiet)) { throw 'Local probe did not complete' }
} finally { Pop-Location }

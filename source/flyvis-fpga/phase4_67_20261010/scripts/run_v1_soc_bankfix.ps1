param([string]$LicenseFile = '')
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$p3 = Join-Path $root '..\phase3_20261010'
$p3 = (Resolve-Path -LiteralPath $p3).Path
. (Join-Path $p3 'amd2026_environment.ps1') -App Vivado -LicenseFile $LicenseFile

$logs = Join-Path $root 'logs'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$launchDir = Join-Path $logs "launcher_$stamp"
if (Test-Path -LiteralPath $launchDir) { throw "Refusing to overwrite $launchDir" }
New-Item -ItemType Directory -Path $launchDir | Out-Null

$log = Join-Path $logs "v1_soc_$stamp.log"
$journal = Join-Path $logs "v1_soc_$stamp.jou"
$console = Join-Path $launchDir 'console.log'
$launch = Join-Path $launchDir 'launch.cmd'
$loader = Join-Path $env:XILINX_VIVADO 'bin\loader.bat'
$source = Join-Path $PSScriptRoot 'build_v1_soc_bankfix.tcl'
$lines = @(
    '@echo off',
    'set "XILINX_LOCAL_USER_DATA=no"',
    # The vendor loader must initialize its own RDI/Tcl environment. These
    # variables are deliberately not overridden here.
    ('call "' + $loader + '" -exec vivado -mode batch -source "' + $source + '" -log "' + $log + '" -journal "' + $journal + '"'),
    'set "FLYVIS_TOOL_EXIT=%ERRORLEVEL%"',
    'exit %FLYVIS_TOOL_EXIT%'
)
Set-Content -LiteralPath $launch -Value $lines -Encoding ASCII

Push-Location $root
try {
    & $launch 2>&1 | Tee-Object -FilePath $console | Select-Object -Last 60
    if ($LASTEXITCODE -ne 0) { throw "Vivado V1 SoC build failed with exit $LASTEXITCODE; inspect $console and $log" }
    if (!(Test-Path -LiteralPath $log)) { throw "Vivado did not create its run log; inspect $console" }
    if (!(Select-String -LiteralPath $log -SimpleMatch 'FLYVIS_V1_SOC_IMPL_BIT_HWH_READY' -Quiet)) {
        throw "Vivado did not report full SoC/BIT/HWH completion; inspect $console and $log"
    }
} finally {
    Pop-Location
}

Write-Output "Vivado V1 SoC build completed. Console: $console; log: $log"

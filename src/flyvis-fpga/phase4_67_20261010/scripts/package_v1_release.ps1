param(
    [Parameter(Mandatory=$true)][string]$BuildRoot,
    [Parameter(Mandatory=$true)][string]$ReleaseDirectory,
    [string]$LicenseFile = ''
)
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$p3 = (Resolve-Path -LiteralPath (Join-Path $root '..\phase3_20261010')).Path
. (Join-Path $p3 'amd2026_environment.ps1') -App Vivado -LicenseFile $LicenseFile

$logs = Join-Path $root 'logs'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$launchDir = Join-Path $logs "package_$stamp"
if (Test-Path -LiteralPath $launchDir) { throw "Refusing to overwrite $launchDir" }
New-Item -ItemType Directory -Path $launchDir | Out-Null
$log = Join-Path $logs "package_v1_$stamp.log"
$journal = Join-Path $logs "package_v1_$stamp.jou"
$console = Join-Path $launchDir 'console.log'
$launch = Join-Path $launchDir 'launch.cmd'
$loader = Join-Path $env:XILINX_VIVADO 'bin\loader.bat'
$source = Join-Path $PSScriptRoot 'package_v1_release.tcl'
$buildPath = (Resolve-Path -LiteralPath $BuildRoot).Path
$releasePath = (Resolve-Path -LiteralPath $ReleaseDirectory).Path
$lines = @(
    '@echo off',
    'set "XILINX_LOCAL_USER_DATA=no"',
    ('set "FLYVIS_BUILD_ROOT=' + $buildPath + '"'),
    ('set "FLYVIS_RELEASE_DIR=' + $releasePath + '"'),
    ('call "' + $loader + '" -exec vivado -mode batch -source "' + $source + '" -log "' + $log + '" -journal "' + $journal + '"'),
    'set "FLYVIS_TOOL_EXIT=%ERRORLEVEL%"',
    'exit %FLYVIS_TOOL_EXIT%'
)
Set-Content -LiteralPath $launch -Value $lines -Encoding ASCII

Push-Location $root
try {
    & $launch 2>&1 | Tee-Object -FilePath $console | Select-Object -Last 35
    if ($LASTEXITCODE -ne 0) { throw "Vivado V1 packaging failed with exit $LASTEXITCODE; inspect $console and $log" }
    if (!(Select-String -LiteralPath $log -SimpleMatch 'FLYVIS_V1_SOC_IMPL_BIT_HWH_READY' -Quiet)) {
        throw "Vivado did not report a complete BIT/HWH/XSA package; inspect $console and $log"
    }
} finally {
    Pop-Location
}
Write-Output "V1 BIT/HWH/XSA package completed. Console: $console; log: $log"

param(
    [ValidateSet('csim','synth','cosim','impl','package')]
    [string]$Action = 'csim',
    [ValidateSet('g2','animation')]
    [string]$Dataset = 'g2',
    [string]$LicenseFile = '',
    [ValidatePattern('^[a-zA-Z0-9_]+$')]
    [string]$RunId = (Get-Date -Format 'yyyyMMdd_HHmmss')
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$work = Join-Path $root ("build\vitis_2026_1_q22_${Dataset}_$RunId")
$configSource = Join-Path $root 'hls\hls_config.cfg'
. (Join-Path $root 'amd2026_environment.ps1') -App Vitis -LicenseFile $LicenseFile
$vitisRun = Join-Path $env:XILINX_VITIS 'bin\vitis-run.bat'
$vpp = Join-Path $env:XILINX_VITIS 'bin\v++.bat'

if (!(Test-Path $vitisRun)) { throw "Vitis 2026.1 vitis-run not found: $vitisRun" }
New-Item -ItemType Directory -Force -Path $work | Out-Null
$logDir = Join-Path $root 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$config = Join-Path $work 'hls_config_abs.cfg'
$configLines = foreach ($line in Get-Content -LiteralPath $configSource) {
    # C simulation validates arithmetic without a target-device claim. The
    # fixed xc7z020 target remains mandatory for synthesis/RTL co-simulation.
    if ($Action -eq 'csim' -and $line -match '^part=') { continue }
    if ($line -match '^(syn\.file|tb\.file)=(.+)$') {
        $key = $Matches[1]
        $file = $Matches[2]
        if ($Dataset -eq 'animation') {
            $file = $file.Replace('hls/testbench.cpp','hls/testbench_animation.cpp').Replace('testdata_q22/','testdata_animation_q22/')
        }
        if (![System.IO.Path]::IsPathRooted($file)) { $file = Join-Path $root $file }
        "$key=$($file.Replace('\','/'))"
    } else { $line }
}
Set-Content -LiteralPath $config -Value $configLines -Encoding ASCII
if ($Action -eq 'impl') {
    # AMD UG1702: --impl defaults to synthesis only unless vivado.flow=impl.
    # This is IP OOC place/route; it does not create or program a SoC bitstream.
    Add-Content -LiteralPath $config -Value @('vivado.flow=impl','vivado.rtl=verilog') -Encoding ASCII
}
Write-Output "FLYVIS_HLS_WORK=$work"
$log = Join-Path $logDir ("hls_${Action}_${Dataset}_" + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.log')
$launcher = $vitisRun
$exe = Join-Path $env:XILINX_VITIS 'bin\unwrapped\win64.o\vitis-run.exe'
$option = '--' + $Action
if ($Action -eq 'synth') {
    $launcher = $vpp
    $exe = Join-Path $env:XILINX_VITIS 'bin\unwrapped\win64.o\v++.exe'
    $option = '-c'
}
$launch = Join-Path $work ("launch_${Action}.cmd")
# Retain the native DLL/Tcl environment and append same-version shared data.
# Tcl-visible paths use forward slashes so they cannot become escape sequences.
$launchLines = @(
    '@echo off',
    ('set "RDI_DATADIR=' + (Join-Path $flyvisInstall 'data').Replace('\','/') + ';' + (Join-Path $env:XILINX_VITIS 'data').Replace('\','/') + ';' + (Join-Path $env:XILINX_VIVADO 'data').Replace('\','/') + '"'),
    ('set "XILINX_HLS_DEVICE_DATADIR=' + (Join-Path $flyvisInstall 'data').Replace('\','/') + '"'),
    ('"' + $exe + '" --mode hls ' + $option + ' --config "' + $config + '" --work_dir "' + $work + '"'),
    'set "FLYVIS_TOOL_EXIT=%ERRORLEVEL%"',
    'exit %FLYVIS_TOOL_EXIT%'
)
Set-Content -LiteralPath $launch -Value $launchLines -Encoding ASCII
Push-Location $root
try {
    & $launcher -env $launch 2>&1 | Tee-Object -FilePath $log
    if ($LASTEXITCODE -ne 0) { throw "Vitis HLS action '$Action' failed with exit code $LASTEXITCODE" }
} finally {
    Pop-Location
}

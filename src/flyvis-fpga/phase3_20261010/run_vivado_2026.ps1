param(
    [ValidateSet('probe','ooc','hls-ooc','bridge','soc')][string]$Action='probe',
    [string]$LicenseFile=''
)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $root 'amd2026_environment.ps1') -App Vivado -LicenseFile $LicenseFile
$scripts=@{probe='license_target_probe.tcl';ooc='rtl_ooc_synth.tcl';'hls-ooc'='hls_rtl_ooc.tcl';bridge='vivado_bridge.tcl';soc='prepare_soc.tcl'}
$stamp=Get-Date -Format 'yyyyMMdd_HHmmss'
$launchDir=Join-Path $root ("build\vivado_${Action}_launcher_$stamp")
New-Item -ItemType Directory -Path $launchDir | Out-Null
$log=Join-Path $root ("logs\vivado_${Action}_$stamp.log")
$journal=Join-Path $root ("logs\vivado_${Action}_$stamp.jou")
$launch=Join-Path $launchDir 'launch.cmd'
$exe=Join-Path $env:XILINX_VIVADO 'bin\unwrapped\win64.o\vivado.exe'
$source=Join-Path $root $scripts[$Action]
$lines=@('@echo off',
    ('set "RDI_DATADIR='+ (Join-Path $flyvisInstall 'data').Replace('\','/')+';'+(Join-Path $env:XILINX_VIVADO 'data').Replace('\','/')+'"'),
    ('"'+$exe+'" -mode batch -source "'+$source+'" -log "'+$log+'" -journal "'+$journal+'"'),
    'set "FLYVIS_TOOL_EXIT=%ERRORLEVEL%"','exit %FLYVIS_TOOL_EXIT%')
Set-Content -LiteralPath $launch -Value $lines -Encoding ASCII
Push-Location $root
try {
    & (Join-Path $env:XILINX_VIVADO 'bin\vivado.bat') -env $launch 2>&1 | Tee-Object -FilePath (Join-Path $launchDir 'console.log')
    if($LASTEXITCODE -ne 0) {throw "Vivado '$Action' failed: $LASTEXITCODE; log=$log"}
} finally {Pop-Location}

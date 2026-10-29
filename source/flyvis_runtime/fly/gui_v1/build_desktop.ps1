param([switch]$Setup, [string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
$desktopGuiRoot = $PSScriptRoot
$desktopProjectRoot = Split-Path -Parent $desktopGuiRoot
$desktopEnvironment = Join-Path $desktopGuiRoot 'desktop_env'
$desktopPython = Join-Path $desktopEnvironment 'Scripts\python.exe'
if ($Setup) {
    $desktopBasePython = Join-Path $desktopProjectRoot '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $desktopPython)) {
        & $desktopBasePython -m venv $desktopEnvironment
        if ($LASTEXITCODE -ne 0) { throw 'Desktop environment creation failed.' }
    }
    & $desktopPython -m pip install --index-url https://pypi.org/simple -r (Join-Path $desktopGuiRoot 'desktop_requirements.lock')
    if ($LASTEXITCODE -ne 0) { throw 'Desktop dependency setup failed.' }
}
if (-not (Test-Path -LiteralPath $desktopPython)) { throw 'Run build_desktop.ps1 -Setup first.' }
& $desktopPython -c 'import webview, numpy; assert numpy.__version__ == "1.26.4"'
if ($LASTEXITCODE -ne 0) { throw 'Desktop dependencies are missing or incompatible.' }
$desktopCompiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
if (-not (Test-Path -LiteralPath $desktopCompiler)) { throw '.NET Framework C# compiler is missing.' }
if (-not $OutputDirectory) { $OutputDirectory = $desktopProjectRoot }
$desktopOutputFolder = [IO.Path]::GetFullPath($OutputDirectory)
if (-not $desktopOutputFolder.StartsWith($desktopProjectRoot + '\', [StringComparison]::OrdinalIgnoreCase) -and $desktopOutputFolder -ne $desktopProjectRoot) {
    throw 'Build output must stay inside this fly project.'
}
New-Item -ItemType Directory -Force -Path $desktopOutputFolder | Out-Null
$desktopOutput = Join-Path $desktopOutputFolder 'FlyVis.exe'
$desktopSource = Join-Path $desktopGuiRoot 'desktop_launcher.cs'
$desktopIcon = Join-Path $desktopGuiRoot 'desktop.ico'
& $desktopCompiler /nologo /target:winexe /codepage:65001 "/out:$desktopOutput" "/win32icon:$desktopIcon" /reference:System.Windows.Forms.dll $desktopSource
if ($LASTEXITCODE -ne 0) { throw 'Desktop launcher build failed. Close FlyVis before rebuilding.' }
Write-Output "Desktop entry: $desktopOutput"

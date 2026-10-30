param(
    [ValidateSet('Vitis','Vivado')][string]$App = 'Vitis',
    [string]$LicenseFile = ''
)

# Process-local prerequisites for AMD's native batch launchers. They populate
# RDI/Tcl/library variables themselves; do not bypass them with an unwrapped EXE.
# No installer files or system/user environment settings are changed.
$flyvisInstall = 'C:\AMDDesignTools\2026.1.1'
$flyvisVitis = Join-Path $flyvisInstall 'Vitis'
$flyvisVivado = Join-Path $flyvisInstall 'Vivado'
if (!$env:PROCESSOR_ARCHITECTURE) {
    if (![System.Environment]::Is64BitProcess) {
        throw 'The AMD 2026.1 tools require a 64-bit host process.'
    }
    $env:PROCESSOR_ARCHITECTURE = 'AMD64'
}
$env:XILINX_VIVADO = $flyvisVivado
$env:XILINX_VITIS = $flyvisVitis
$env:XILINX_HLS = $flyvisVitis
$flyvisLicenseSelection = Join-Path $PSScriptRoot 'artifacts\active_license_selection.json'
if (!$LicenseFile -and $env:FLYVIS_LICENSE_FILE) {
    $LicenseFile = $env:FLYVIS_LICENSE_FILE
}
if (!$LicenseFile -and (Test-Path -LiteralPath $flyvisLicenseSelection)) {
    $flyvisSelection = Get-Content -LiteralPath $flyvisLicenseSelection -Raw | ConvertFrom-Json
    $LicenseFile = $flyvisSelection.path
    if ((Get-FileHash -LiteralPath $LicenseFile -Algorithm SHA256).Hash -ne $flyvisSelection.sha256) {
        throw 'Selected license file changed; verify it before launching tools.'
    }
}
if (!$LicenseFile) {
    $flyvisBasicLicense = Join-Path $PSScriptRoot 'build\private_license\Xilinx_basic.lic'
    if (Test-Path -LiteralPath $flyvisBasicLicense) { $LicenseFile = $flyvisBasicLicense }
}
if ($LicenseFile) {
    $LicenseFile = (Resolve-Path -LiteralPath $LicenseFile -ErrorAction Stop).Path
    $env:XILINXD_LICENSE_FILE = $LicenseFile
    $env:LM_LICENSE_FILE = $LicenseFile
}

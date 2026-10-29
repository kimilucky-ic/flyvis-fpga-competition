$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:TEMP=Join-Path $PSScriptRoot 'tmp'
$env:TMP=$env:TEMP
$env:PROCESSOR_ARCHITECTURE='AMD64'
& 'C:/AMDDesignTools/2026.1.1/Vivado/bin/xvlog.bat' -sv ../build_r1/camera_guard.v ../build_r1/cmos_capture_data.v tb_video.sv -log compile.log
if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
& 'C:/AMDDesignTools/2026.1.1/Vivado/bin/xelab.bat' -L v_vid_in_axi4s_v5_0_8 -L xpm -L unisims_ver -debug typical -mt 1 xil_defaultlib.tb_video -s video_test -log elaborate.log
if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
& 'C:/AMDDesignTools/2026.1.1/Vivado/bin/xsim.bat' video_test -tclbatch run.tcl -log simulate.log
exit $LASTEXITCODE

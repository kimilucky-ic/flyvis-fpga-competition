$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:TEMP=Join-Path $PSScriptRoot 'tmp'
$env:TMP=$env:TEMP
$env:PROCESSOR_ARCHITECTURE='AMD64'
& 'C:/AMDDesignTools/2026.1.1/Vivado/bin/xvlog.bat' -work xil_defaultlib -sv ../build_r7/camera_guard.v ../build_r7/cmos_capture_data.v tb_video.sv C:/AMDDesignTools/2026.1.1/Vivado/data/verilog/src/glbl.v -log compile.log
if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
& 'C:/AMDDesignTools/2026.1.1/Vivado/bin/xelab.bat' -L v_vid_in_axi4s_v5_0_8 -L xpm -L unisims_ver -debug typical -mt off xil_defaultlib.tb_video xil_defaultlib.glbl -s video_test -log elaborate.log
if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
& 'C:/AMDDesignTools/2026.1.1/Vivado/bin/xsim.bat' video_test -tclbatch run.tcl -log simulate.log
exit $LASTEXITCODE

$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:TEMP=Join-Path $PSScriptRoot 'tmp'
$env:TMP=$env:TEMP
New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
$env:PROCESSOR_ARCHITECTURE='AMD64'
& 'C:/AMDDesignTools/2026.1.1/Vivado/bin/xvlog.bat' -work xil_defaultlib -sv ../vendor/ip_repo/cmos_sensor/src/cmos_capture_data.v ../imported3/base/ip/base_v_vid_in_axi4s_0_0/sim/base_v_vid_in_axi4s_0_0.v tb_official_video.sv C:/AMDDesignTools/2026.1.1/Vivado/data/verilog/src/glbl.v -log compile.log
if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
& 'C:/AMDDesignTools/2026.1.1/Vivado/bin/xelab.bat' -L v_vid_in_axi4s_v5_0_8 -L xpm -L unisims_ver -debug typical -mt off xil_defaultlib.tb_official_video xil_defaultlib.glbl -s official_test -log elaborate.log
if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
& 'C:/AMDDesignTools/2026.1.1/Vivado/bin/xsim.bat' official_test -tclbatch run.tcl -log simulate.log
exit $LASTEXITCODE



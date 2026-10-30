$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:TEMP=Join-Path $PSScriptRoot 'tmp'
$env:TMP=$env:TEMP
$env:PROCESSOR_ARCHITECTURE='AMD64'
& 'C:/AMDDesignTools/2026.1.1/Vivado/bin/xvhdl.bat' --work xil_defaultlib ../build_r3/bd/flyvis_ddr/ip/flyvis_ddr_cam_iic_0/sim/flyvis_ddr_cam_iic_0.vhd -log vhdl.log
if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
& 'C:/AMDDesignTools/2026.1.1/Vivado/bin/xvlog.bat' -work xil_defaultlib -sv tb_iic.sv C:/AMDDesignTools/2026.1.1/Vivado/data/verilog/src/glbl.v -log compile.log
if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
& 'C:/AMDDesignTools/2026.1.1/Vivado/bin/xelab.bat' -L axi_iic_v2_1_12 -L unisims_ver -debug typical -mt off xil_defaultlib.tb_iic xil_defaultlib.glbl -s iic_test -log elaborate.log
if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
& 'C:/AMDDesignTools/2026.1.1/Vivado/bin/xsim.bat' iic_test -tclbatch run.tcl -log simulate.log
exit $LASTEXITCODE

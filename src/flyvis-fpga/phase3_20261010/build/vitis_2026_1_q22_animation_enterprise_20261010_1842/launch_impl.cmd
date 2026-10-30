@echo off
set "RDI_DATADIR=C:/AMDDesignTools/2026.1.1/data;C:/AMDDesignTools/2026.1.1/Vitis/data;C:/AMDDesignTools/2026.1.1/Vivado/data"
set "XILINX_HLS_DEVICE_DATADIR=C:/AMDDesignTools/2026.1.1/data"
"C:\AMDDesignTools\2026.1.1\Vitis\bin\unwrapped\win64.o\vitis-run.exe" --mode hls --impl --config "C:\Users\hzy72\Documents\ChatGPT\fpga\flyvis-fpga\phase3_20261010\build\vitis_2026_1_q22_animation_enterprise_20261010_1842\hls_config_abs.cfg" --work_dir "C:\Users\hzy72\Documents\ChatGPT\fpga\flyvis-fpga\phase3_20261010\build\vitis_2026_1_q22_animation_enterprise_20261010_1842"
set "FLYVIS_TOOL_EXIT=%ERRORLEVEL%"
exit %FLYVIS_TOOL_EXIT%

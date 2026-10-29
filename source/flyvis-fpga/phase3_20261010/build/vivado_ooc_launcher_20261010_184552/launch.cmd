@echo off
set "RDI_DATADIR=C:/AMDDesignTools/2026.1.1/data;C:/AMDDesignTools/2026.1.1/Vivado/data"
"C:\AMDDesignTools\2026.1.1\Vivado\bin\unwrapped\win64.o\vivado.exe" -mode batch -source "C:\Users\hzy72\Documents\ChatGPT\fpga\flyvis-fpga\phase3_20261010\rtl_ooc_synth.tcl" -log "C:\Users\hzy72\Documents\ChatGPT\fpga\flyvis-fpga\phase3_20261010\logs\vivado_ooc_20261010_184552.log" -journal "C:\Users\hzy72\Documents\ChatGPT\fpga\flyvis-fpga\phase3_20261010\logs\vivado_ooc_20261010_184552.jou"
set "FLYVIS_TOOL_EXIT=%ERRORLEVEL%"
exit %FLYVIS_TOOL_EXIT%

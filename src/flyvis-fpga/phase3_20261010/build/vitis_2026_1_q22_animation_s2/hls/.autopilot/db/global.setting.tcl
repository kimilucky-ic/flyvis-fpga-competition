
set TopModule "flyvis_t5c_source_raw"
set HLSTopModule "flyvis_t5c_source_raw"
set ClockPeriod 10
set ClockList ap_clk
set AxiliteClockList {}
set HasVivadoClockPeriod 0
set CombLogicFlag 0
set PipelineFlag 0
set DataflowTaskPipelineFlag 1
set TrivialPipelineFlag 0
set noPortSwitchingFlag 0
set FloatingPointFlag 0
set FftOrFirFlag 0
set NbRWValue 0
set intNbAccess 0
set NewDSPMapping 1
set HasDSPModule 0
set ResetLevelFlag 0
set ResetStyle control
set ResetSyncFlag 1
set ResetRegisterFlag 0
set ResetVariableFlag 0
set ResetRegisterNum 0
set FsmEncStyle onehot
set MaxFanout 0
set RtlPrefix {}
set RtlSubPrefix flyvis_t5c_source_raw_
set ExtraCCFlags {}
set ExtraCLdFlags {}
set SynCheckOptions {}
set PresynOptions {}
set PreprocOptions {}
set RtlWriterOptions {}
set CbcGenFlag 0
set CasGenFlag 0
set CasMonitorFlag 0
set AutoSimOptions {}
set ExportMCPathFlag 0
set SCTraceFileName mytrace
set SCTraceFileFormat vcd
set SCTraceOption all
set TargetInfo xc7z020:-clg400:-2
set SourceFiles {sc {} c ../../../hls/flyvis_t5c_source_raw.cpp}
set SourceFlags {sc {} c {{}}}
set DirectiveFile {}
set TBFiles {verilog {C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/testdata_animation_q22/expected_i32le.bin C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/testdata_animation_q22/requests_i32le.bin C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/hls/flyvis_t5c_constants_q22.hpp C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/hls/testbench_animation.cpp} bc {C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/testdata_animation_q22/expected_i32le.bin C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/testdata_animation_q22/requests_i32le.bin C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/hls/flyvis_t5c_constants_q22.hpp C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/hls/testbench_animation.cpp} sc {C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/testdata_animation_q22/expected_i32le.bin C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/testdata_animation_q22/requests_i32le.bin C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/hls/flyvis_t5c_constants_q22.hpp C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/hls/testbench_animation.cpp} vhdl {C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/testdata_animation_q22/expected_i32le.bin C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/testdata_animation_q22/requests_i32le.bin C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/hls/flyvis_t5c_constants_q22.hpp C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/hls/testbench_animation.cpp} c {} cas {C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/testdata_animation_q22/expected_i32le.bin C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/testdata_animation_q22/requests_i32le.bin C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/hls/flyvis_t5c_constants_q22.hpp C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/hls/testbench_animation.cpp}}
set SpecLanguage C
set TVInFiles {bc {} c {} sc {} cas {} vhdl {} verilog {}}
set TVOutFiles {bc {} c {} sc {} cas {} vhdl {} verilog {}}
set TBTops {verilog {} bc {} sc {} vhdl {} c {} cas {}}
set TBInstNames {verilog {} bc {} sc {} vhdl {} c {} cas {}}
set XDCFiles {}
set ExtraGlobalOptions {"area_timing" 1 "clock_gate" 1 "impl_flow" map "power_gate" 0}
set TBTVFileNotFound {}
set AppFile {}
set ApsFile hls.aps
set AvePath ../../.
set DefaultPlatform DefaultPlatform
set multiClockList {}
set SCPortClockMap {}
set intNbAccess 0
set PlatformFiles {{DefaultPlatform {xilinx/zynq/zynq}}}
set HPFPO 0

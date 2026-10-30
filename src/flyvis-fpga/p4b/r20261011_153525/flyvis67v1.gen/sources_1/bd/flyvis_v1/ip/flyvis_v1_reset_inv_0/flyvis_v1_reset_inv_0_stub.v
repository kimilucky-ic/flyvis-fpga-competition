// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2026.1.1 (win64) Build 6605303 Fri Sep 04 12:46:29 BST 2026
// Date        : Sun Oct 11 15:39:11 2026
// Host        : hope running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode synth_stub
//               c:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/p4b/r20261011_153525/flyvis67v1.gen/sources_1/bd/flyvis_v1/ip/flyvis_v1_reset_inv_0/flyvis_v1_reset_inv_0_stub.v
// Design      : flyvis_v1_reset_inv_0
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7z020clg400-2
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* CHECK_LICENSE_TYPE = "flyvis_v1_reset_inv_0,util_vector_logic_v2_0_5_util_vector_logic,{}" *) (* CORE_GENERATION_INFO = "flyvis_v1_reset_inv_0,util_vector_logic_v2_0_5_util_vector_logic,{x_ipProduct=Vivado 2026.1.1,x_ipVendor=xilinx.com,x_ipLibrary=ip,x_ipName=util_vector_logic,x_ipVersion=2.0,x_ipCoreRevision=5,x_ipLanguage=VERILOG,x_ipSimLanguage=MIXED,C_OPERATION=not,C_SIZE=1}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) 
(* X_CORE_INFO = "util_vector_logic_v2_0_5_util_vector_logic,Vivado 2026.1.1" *) 
module flyvis_v1_reset_inv_0(Op1, Res)
/* synthesis syn_black_box black_box_pad_pin="Op1[0:0],Res[0:0]" */;
  input [0:0]Op1;
  output [0:0]Res;
endmodule

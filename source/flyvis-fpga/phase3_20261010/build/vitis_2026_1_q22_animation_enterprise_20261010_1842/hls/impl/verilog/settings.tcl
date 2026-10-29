# ==============================================================
# Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2026.1.1 (64-bit)
# Tool Version Limit: 2026.06
# Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
# Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
# 
# ==============================================================
#
# Settings for Vivado implementation flow
#
set top_module flyvis_t5c_source_raw
set language verilog
set family zynq
set device xc7z020
set package -clg400
set speed -2
set clock ap_clk
set fsm_ext "off"

# For customizing the implementation flow
set add_io_buffers false ;# true|false

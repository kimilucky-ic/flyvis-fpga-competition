# ==============================================================
# Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2026.1.1 (64-bit)
# Tool Version Limit: 2026.06
# Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
# Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
# 
# ==============================================================
source -notrace "C:/AMDDesignTools/2026.1.1/Vitis/common/scripts/ipxhls.tcl"
set ip_out_dir "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/build/vitis_2026_1_q22_animation_enterprise_20261010_1842/hls/impl/ip"
set data_file "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-fpga/phase3_20261010/build/vitis_2026_1_q22_animation_enterprise_20261010_1842/hls/hls_data.json"
set src_dir [file dir $data_file]
set ip_types {vitis sysgen}
set ippack_opts_dict {}
if { [catch {::ipx::utils::package_hls_ip $ip_out_dir $data_file $ip_types $src_dir $ippack_opts_dict} res] } {
  puts "Caught error:\n$::errorInfo"
  error $res
}

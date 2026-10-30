# Isolated camera extension with explicit capture reset and sticky overflow status.
set_property -dict [list CONFIG.PCW_USE_S_AXI_HP1 {1} CONFIG.PCW_S_AXI_HP1_DATA_WIDTH {64}] $ps
set_property CONFIG.NUM_MI {4} $ic
create_bd_cell -type module -reference cmos_capture_data capture
create_bd_cell -type module -reference camera_guard camera_guard
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 camera_control
set_property -dict [list CONFIG.C_IS_DUAL {1} CONFIG.C_GPIO_WIDTH {1} CONFIG.C_ALL_OUTPUTS {1} CONFIG.C_DOUT_DEFAULT {0} CONFIG.C_GPIO2_WIDTH {3} CONFIG.C_ALL_INPUTS_2 {1}] [get_bd_cells camera_control]
connect_bd_intf_net [get_bd_intf_pins control_bus/M03_AXI] [get_bd_intf_pins camera_control/S_AXI]
connect_bd_net [get_bd_pins camera_control/gpio_io_o] [get_bd_pins camera_guard/run]
connect_bd_net [get_bd_pins camera_guard/status] [get_bd_pins camera_control/gpio2_io_i]
create_bd_cell -type ip -vlnv xilinx.com:ip:v_vid_in_axi4s:5.0 camera_stream
set_property -dict [list CONFIG.C_HAS_ASYNC_CLK {1} CONFIG.C_ADDR_WIDTH {10}] [get_bd_cells camera_stream]
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_vdma:6.3 camera_dma
set_property -dict [list CONFIG.c_include_mm2s {0} CONFIG.c_include_s2mm {1} CONFIG.c_m_axi_s2mm_data_width {64} CONFIG.c_num_fstores {3} CONFIG.c_s2mm_linebuffer_depth {4096} CONFIG.c_s2mm_max_burst_length {32}] [get_bd_cells camera_dma]
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_iic:2.1 cam_iic
set_property CONFIG.IIC_FREQ_KHZ {100} [get_bd_cells cam_iic]
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 camera_memory
set_property -dict [list CONFIG.NUM_SI {1} CONFIG.NUM_MI {1}] [get_bd_cells camera_memory]
connect_bd_intf_net [get_bd_intf_pins control_bus/M01_AXI] [get_bd_intf_pins camera_dma/S_AXI_LITE]
connect_bd_intf_net [get_bd_intf_pins control_bus/M02_AXI] [get_bd_intf_pins cam_iic/S_AXI]
connect_bd_intf_net [get_bd_intf_pins camera_stream/video_out] [get_bd_intf_pins camera_dma/S_AXIS_S2MM]
connect_bd_intf_net [get_bd_intf_pins camera_dma/M_AXI_S2MM] [get_bd_intf_pins camera_memory/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins camera_memory/M00_AXI] [get_bd_intf_pins ps7/S_AXI_HP1]
create_bd_intf_port -mode Master -vlnv xilinx.com:interface:iic_rtl:1.0 cam_iic
connect_bd_intf_net [get_bd_intf_ports cam_iic] [get_bd_intf_pins cam_iic/IIC]
foreach pin {control_bus/M03_ACLK camera_control/s_axi_aclk camera_guard/aclk control_bus/M01_ACLK control_bus/M02_ACLK camera_dma/s_axi_lite_aclk camera_dma/m_axi_s2mm_aclk camera_dma/s_axis_s2mm_aclk cam_iic/s_axi_aclk camera_stream/aclk camera_memory/ACLK camera_memory/S00_ACLK camera_memory/M00_ACLK ps7/S_AXI_HP1_ACLK} {
 connect_bd_net [get_bd_pins ps7/FCLK_CLK0] [get_bd_pins $pin]
}
foreach pin {control_bus/M03_ARESETN control_bus/M01_ARESETN control_bus/M02_ARESETN camera_memory/ARESETN camera_memory/S00_ARESETN camera_memory/M00_ARESETN} {
 connect_bd_net [get_bd_pins reset/interconnect_aresetn] [get_bd_pins $pin]
}
foreach pin {camera_dma/axi_resetn cam_iic/s_axi_aresetn camera_control/s_axi_aresetn camera_guard/aresetn} {
 connect_bd_net [get_bd_pins reset/peripheral_aresetn] [get_bd_pins $pin]
}
connect_bd_net [get_bd_pins one/dout] [get_bd_pins camera_stream/aclken] [get_bd_pins camera_stream/axis_enable]
# Both stream/FIFO reset domains owned by camera_guard; default held in reset.
connect_bd_net [get_bd_pins capture/cmos_frame_clk] [get_bd_pins camera_guard/pclk] [get_bd_pins camera_stream/vid_io_in_clk]
connect_bd_net [get_bd_pins camera_guard/stream_aresetn] [get_bd_pins camera_stream/aresetn]
connect_bd_net [get_bd_pins camera_guard/capture_resetn] [get_bd_pins capture/rst_n]
connect_bd_net [get_bd_pins camera_guard/video_reset] [get_bd_pins camera_stream/vid_io_in_reset]
connect_bd_net [get_bd_pins camera_stream/overflow] [get_bd_pins camera_guard/overflow]
foreach {src dst} {cmos_frame_ce vid_io_in_ce cmos_frame_vsync vid_vsync cmos_frame_href vid_hsync cmos_active_video vid_active_video cmos_frame_data vid_data} {
 connect_bd_net [get_bd_pins capture/$src] [get_bd_pins camera_stream/$dst]
}
connect_bd_net [get_bd_pins zero/dout] [get_bd_pins camera_stream/vid_field_id]
foreach name {cam_pclk cam_href cam_vsync} {
 if {$name eq "cam_pclk"} {create_bd_port -dir I -type clk -freq_hz 72000000 $name} else {create_bd_port -dir I $name}
 connect_bd_net [get_bd_ports $name] [get_bd_pins capture/$name]
}
create_bd_port -dir I -from 7 -to 0 cam_data
connect_bd_net [get_bd_ports cam_data] [get_bd_pins capture/cam_data]
foreach name {cam_rst_n cam_pwdn} {
 create_bd_port -dir O $name
 connect_bd_net [get_bd_ports $name] [get_bd_pins capture/$name]
}
# Interrupts not yet bound to runtime; first preparation uses bounded polling.
# PCLK period/input delays MUST be supplied from verified sensor mode before implementation.

connect_bd_net [get_bd_pins zero/dout] [get_bd_pins camera_stream/vid_hblank] [get_bd_pins camera_stream/vid_vblank]

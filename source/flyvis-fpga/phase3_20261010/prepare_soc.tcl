# Prepared PS7 + AXI4-Lite shell. Exact Leader PS preset must be reviewed first.
# Creates a fresh isolated project only; no launch_runs/write_bitstream/hardware.
set root [file normalize [file dirname [info script]]]
set target xc7z020clg400-2
if {[llength [get_parts -quiet $target]] != 1} { error "FLYVIS_TARGET_UNAVAILABLE: $target" }
if {![info exists ::env(FLYVIS_PS7_PRESET_TCL)] || ![file isfile $::env(FLYVIS_PS7_PRESET_TCL)]} {
    error "FLYVIS_BOARD_PRESET_REQUIRED: reviewed exact Leader Zynq-7020 PS/DDR preset; no guessed DDR settings"
}
set output [file join $root build soc_prepare_2026_1_[clock format [clock seconds] -format %Y%m%d_%H%M%S]]
if {[file exists $output]} { error "Output already exists: $output" }
create_project flyvis_source_raw_soc $output -part $target
add_files [list [file join $root rtl flyvis_source_raw_core.sv] [file join $root rtl flyvis_source_raw_axil.sv]]
add_files [list [file join $root rom edges_q22.mem] [file join $root rom neurons_q22.mem]]
create_bd_design flyvis_soc
set flyvis_ps7 [create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 ps7]
source $::env(FLYVIS_PS7_PRESET_TCL)
set_property -dict [list CONFIG.PCW_USE_M_AXI_GP0 {1} CONFIG.PCW_EN_CLK0_PORT {1} CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ {100}] $flyvis_ps7
set acc [create_bd_cell -type module -reference flyvis_source_raw_axil flyvis]
set axi [create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 axi]
set_property CONFIG.NUM_MI 1 $axi
set reset [create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:5.0 reset]
set_property CONFIG.C_EXT_RESET_HIGH 0 $reset
set zero [create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 zero]
set_property CONFIG.CONST_VAL 0 $zero
set one [create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 one]
set_property CONFIG.CONST_VAL 1 $one
connect_bd_intf_net [get_bd_intf_pins ps7/M_AXI_GP0] [get_bd_intf_pins axi/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins axi/M00_AXI] [get_bd_intf_pins flyvis/s_axi]
connect_bd_net [get_bd_pins ps7/FCLK_CLK0] [get_bd_pins ps7/M_AXI_GP0_ACLK] [get_bd_pins axi/ACLK] [get_bd_pins axi/S00_ACLK] [get_bd_pins axi/M00_ACLK] [get_bd_pins flyvis/s_axi_aclk] [get_bd_pins reset/slowest_sync_clk]
connect_bd_net [get_bd_pins ps7/FCLK_RESET0_N] [get_bd_pins reset/ext_reset_in]
connect_bd_net [get_bd_pins zero/dout] [get_bd_pins reset/aux_reset_in] [get_bd_pins reset/mb_debug_sys_rst]
connect_bd_net [get_bd_pins one/dout] [get_bd_pins reset/dcm_locked]
connect_bd_net [get_bd_pins reset/interconnect_aresetn] [get_bd_pins axi/ARESETN] [get_bd_pins axi/S00_ARESETN] [get_bd_pins axi/M00_ARESETN]
connect_bd_net [get_bd_pins reset/peripheral_aresetn] [get_bd_pins flyvis/s_axi_aresetn]
make_bd_intf_pins_external [get_bd_intf_pins ps7/DDR]
make_bd_intf_pins_external [get_bd_intf_pins ps7/FIXED_IO]
set seg [get_bd_addr_segs flyvis/s_axi/*]
if {[llength $seg]!=1} { error "Expected one FlyVis AXI register segment; check interface inference" }
assign_bd_address -offset 0x43C00000 -range 64K -target_address_space [get_bd_addr_spaces ps7/Data] $seg
validate_bd_design
save_bd_design
generate_target all [get_files flyvis_soc.bd]
add_files [make_wrapper -files [get_files flyvis_soc.bd] -top]
set_property top flyvis_soc_wrapper [current_fileset]
puts "FLYVIS_SOC_PREPARED=$output; synthesis/implementation/board execution remain separate stages"

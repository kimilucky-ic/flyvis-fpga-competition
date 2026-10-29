# PREPARATION ONLY, never modifies baseline or launches synthesis/implementation.
set here [file dirname [file normalize [info script]]]
if {[version -short] ne "2020.2"} {
    error "Official camera is 2020.2; a separately audited IP migration is required for other tools"
}
if {$argc != 1} {error "Pass a NEW isolated output directory"}
set out [file normalize [lindex $argv 0]]
if {[file exists $out]} {error "Output must not exist"}
file mkdir $out
cd $out
create_project official_flyvis $out -part xc7z020clg400-2
set_property target_language Verilog [current_project]
set_property source_mgmt_mode All [current_project]
set_property ip_repo_paths [file join $here vendor ip_repo] [current_project]
update_ip_catalog
file copy [file join $here vendor base.bd] [file join $out base.bd]
add_files -norecurse [file join $out base.bd]
open_bd_design [get_files base.bd]
foreach name {fp32_rne.sv banked_state_mem.sv sync_mem.sv compact_edge_gen.sv flyvis_lane.sv snapshot_axi_writer.sv flyvis_ddr_snapshot_top.sv flyvis_ddr_soc_ip.sv} {
    add_files -norecurse [file join $here neural $name]
}
foreach name [glob [file join $here neural *.hex]] {
    file copy $name [file join $out [file tail $name]]
    add_files -norecurse [file join $out [file tail $name]]
}
update_compile_order -fileset sources_1
set ps [get_bd_cells ps7_0]
if {[get_property CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ $ps] != 100 ||
    [get_property CONFIG.PCW_USE_S_AXI_HP1 $ps] != 0 ||
    [get_property CONFIG.NUM_MI [get_bd_cells ps7_0_axi_periph]] != 3} {
    error "Unexpected official clock/HP/control baseline"
}
# Official video stays on HP0; all video hierarchy/IRQs/addresses retained.
set_property -dict [list CONFIG.PCW_USE_S_AXI_HP1 {1} CONFIG.PCW_S_AXI_HP1_DATA_WIDTH {64}] $ps
set_property CONFIG.NUM_MI 4 [get_bd_cells ps7_0_axi_periph]
create_bd_cell -type module -reference flyvis_ddr_soc_ip network
set mem [create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 neural_memory]
set_property -dict [list CONFIG.NUM_SI {1} CONFIG.NUM_MI {1}] $mem
connect_bd_intf_net [get_bd_intf_pins ps7_0_axi_periph/M03_AXI] [get_bd_intf_pins network/S_AXI]
connect_bd_intf_net [get_bd_intf_pins network/M_AXI] [get_bd_intf_pins neural_memory/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins neural_memory/M00_AXI] [get_bd_intf_pins ps7_0/S_AXI_HP1]
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] [get_bd_pins network/aclk] [get_bd_pins ps7_0_axi_periph/M03_ACLK] [get_bd_pins ps7_0/S_AXI_HP1_ACLK] [get_bd_pins neural_memory/ACLK] [get_bd_pins neural_memory/S00_ACLK] [get_bd_pins neural_memory/M00_ACLK]
connect_bd_net [get_bd_pins rst_ps7_0_fclk0/peripheral_aresetn] [get_bd_pins network/aresetn] [get_bd_pins ps7_0_axi_periph/M03_ARESETN] [get_bd_pins neural_memory/S00_ARESETN] [get_bd_pins neural_memory/M00_ARESETN]
connect_bd_net [get_bd_pins rst_ps7_0_fclk0/interconnect_aresetn] [get_bd_pins neural_memory/ARESETN]
set ns [get_bd_addr_segs -of_objects [get_bd_intf_pins network/S_AXI]]
set ma [get_bd_addr_spaces -of_objects [get_bd_intf_pins network/M_AXI]]
if {[llength $ns] != 1 || [llength $ma] != 1} {error "Unknown network address interfaces"}
assign_bd_address -offset 0x43C40000 -range 4K -target_address_space [get_bd_addr_spaces ps7_0/Data] $ns
assign_bd_address -offset 0 -range 1G -target_address_space $ma [get_bd_addr_segs ps7_0/S_AXI_HP1/HP1_DDR_LOWOCM]
validate_bd_design
save_bd_design
write_bd_tcl [file join $out combined_bd.tcl]
report_ip_status -file [file join $out ip_status.rpt]
add_files -fileset constrs_1 -norecurse [file join $here vendor base.xdc]
# Camera external timing is not certified by original pin-only XDC.
puts "BD_PREPARED_ONLY_NOT_SYNTHESIZED_NOT_BOARD_VALIDATED"

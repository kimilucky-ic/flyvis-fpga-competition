# Whole FlyVis network + native Zynq PS7. Local implementation and artifacts only.
set_param general.maxThreads 1
set here [file dirname [file normalize [info script]]]
cd $here
set release [file join $here release]
file mkdir $release
set vf [open tool_version.txt w];puts $vf [version];close $vf
create_project -in_memory -part xc7z020clg400-2
set_property target_language Verilog [current_project]
# Required by UG994 for module references in an in-memory/non-project flow.
set_property source_mgmt_mode All [current_project]
foreach name {cmos_capture_data.v fp32_rne.sv banked_state_mem.sv sync_mem.sv compact_edge_gen.sv flyvis_lane.sv snapshot_axi_writer.sv flyvis_ddr_snapshot_top.sv flyvis_ddr_soc_ip.sv} {
    add_files -norecurse [file join $here $name]
}
set_property top flyvis_ddr_soc_ip [current_fileset]
update_compile_order -fileset sources_1

# Installed 2026.1.1 BD rules occasionally use source utils.tcl relative to
# a vendor script. Resolve only existing local vendor includes, without edits.
rename ::source ::flyvis_soc_original_source
proc ::source {args} {
    set script [lindex $args end]
    if {[file pathtype $script] eq "relative"} {
        set caller [string map {\\ /} [info script]]
        if {[string first "/Vivado/data/" $caller]>=0} {
            set candidate [file join [file dirname $caller] $script]
            if {[file isfile $candidate]} {set args [lreplace $args end end $candidate]}
        }
    }
    return [uplevel 1 [list ::flyvis_soc_original_source {*}$args]]
}
source [file join $here ps7_vendor_params.tcl]
set psprops {}
foreach {name value} $flyvis_vendor_ps7_user_params {
    if {[string match "PCW_UIPARAM_DDR_*" $name] || [string match "PCW_DDR_*" $name] ||
        [string match "PCW_DQS_*" $name] || [string match "PCW_DQ_*" $name] ||
        [string match "PCW_DM_*" $name] || [string match "PCW_MIO_*" $name] ||
        [string match "PCW_QSPI_*" $name] || [string match "PCW_SD0_*" $name] ||
        [string match "PCW_UART0_*" $name] || [string match "PCW_ENET0_*" $name] ||
        [string match "PCW_USB0_*" $name] || [string match "PCW_GPIO_MIO_*" $name] ||
        [string match "PCW_PRESET_BANK*_VOLTAGE" $name] ||
        $name eq "PCW_CRYSTAL_PERIPHERAL_FREQMHZ" ||
        $name eq "PCW_DDR_RAM_BASEADDR" || $name eq "PCW_DDR_RAM_HIGHADDR"} {
        lappend psprops CONFIG.$name $value
    }
}
create_bd_design -dir [file join $here bd] flyvis_ddr
set ps [create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 ps7]
set_property -dict $psprops $ps
set_property -dict [list CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ {100} CONFIG.PCW_EN_CLK0_PORT {1} CONFIG.PCW_USE_M_AXI_GP0 {1} CONFIG.PCW_USE_S_AXI_HP0 {1} CONFIG.PCW_S_AXI_HP0_DATA_WIDTH {64}] $ps
foreach {name expected} {PCW_PRESET_BANK0_VOLTAGE {LVCMOS 3.3V} PCW_PRESET_BANK1_VOLTAGE {LVCMOS 1.8V} PCW_MIO_16_IOTYPE {LVCMOS 1.8V} PCW_MIO_27_IOTYPE {LVCMOS 1.8V}} {
    if {[get_property CONFIG.$name $ps] ne $expected} {error "PS7 voltage mismatch $name"}
}
set core [create_bd_cell -type module -reference flyvis_ddr_soc_ip network]
set ic [create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 control_bus]
set_property -dict [list CONFIG.NUM_SI {1} CONFIG.NUM_MI {1}] $ic
set hp [create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 memory_bus]
set_property -dict [list CONFIG.NUM_SI {1} CONFIG.NUM_MI {1}] $hp
set rst [create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:5.0 reset]
# External polarity is read-only and propagated from the active-low PS7 pin.
set_property CONFIG.C_AUX_RESET_HIGH {1} $rst
set zero [create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 zero]
set_property CONFIG.CONST_VAL 0 $zero
set one [create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 one]
set_property CONFIG.CONST_VAL 1 $one
create_bd_intf_port -mode Master -vlnv xilinx.com:interface:ddrx_rtl:1.0 DDR
connect_bd_intf_net [get_bd_intf_pins ps7/DDR] [get_bd_intf_ports DDR]
create_bd_intf_port -mode Master -vlnv xilinx.com:display_processing_system7:fixedio_rtl:1.0 FIXED_IO
connect_bd_intf_net [get_bd_intf_pins ps7/FIXED_IO] [get_bd_intf_ports FIXED_IO]
connect_bd_intf_net [get_bd_intf_pins ps7/M_AXI_GP0] [get_bd_intf_pins control_bus/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins control_bus/M00_AXI] [get_bd_intf_pins network/S_AXI]
connect_bd_intf_net [get_bd_intf_pins network/M_AXI] [get_bd_intf_pins memory_bus/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins memory_bus/M00_AXI] [get_bd_intf_pins ps7/S_AXI_HP0]
connect_bd_net [get_bd_pins ps7/FCLK_CLK0] [get_bd_pins ps7/M_AXI_GP0_ACLK] [get_bd_pins control_bus/ACLK] [get_bd_pins control_bus/S00_ACLK] [get_bd_pins control_bus/M00_ACLK] [get_bd_pins network/aclk] [get_bd_pins reset/slowest_sync_clk] [get_bd_pins ps7/S_AXI_HP0_ACLK] [get_bd_pins memory_bus/ACLK] [get_bd_pins memory_bus/S00_ACLK] [get_bd_pins memory_bus/M00_ACLK]
connect_bd_net [get_bd_pins ps7/FCLK_RESET0_N] [get_bd_pins reset/ext_reset_in]
connect_bd_net [get_bd_pins zero/dout] [get_bd_pins reset/aux_reset_in] [get_bd_pins reset/mb_debug_sys_rst]
connect_bd_net [get_bd_pins one/dout] [get_bd_pins reset/dcm_locked]
connect_bd_net [get_bd_pins reset/interconnect_aresetn] [get_bd_pins control_bus/ARESETN] [get_bd_pins control_bus/S00_ARESETN] [get_bd_pins control_bus/M00_ARESETN] [get_bd_pins memory_bus/ARESETN] [get_bd_pins memory_bus/S00_ARESETN] [get_bd_pins memory_bus/M00_ARESETN]
connect_bd_net [get_bd_pins reset/peripheral_aresetn] [get_bd_pins network/aresetn]
source [file join $here camera_extension.tcl]
assign_bd_address
set assigned 0
foreach seg [get_bd_addr_segs -of_objects [get_bd_addr_spaces ps7/Data]] {
    if {[string match "*network*" $seg]} {
        set_property offset 0x43C40000 $seg
        set_property range 4K $seg
        incr assigned
    }
}
if {$assigned!=1} {error "Expected one whole-network AXI segment; got $assigned"}
validate_bd_design
save_bd_design
write_bd_tcl [file join $release validated_bd.tcl]
set pf [open [file join $release platform_properties.txt] w]
foreach name {PCW_FPGA0_PERIPHERAL_FREQMHZ PCW_ACT_FPGA0_PERIPHERAL_FREQMHZ PCW_PRESET_BANK0_VOLTAGE PCW_PRESET_BANK1_VOLTAGE PCW_UIPARAM_DDR_PARTNO PCW_USE_M_AXI_GP0 PCW_USE_S_AXI_HP0 PCW_S_AXI_HP0_DATA_WIDTH PCW_CRYSTAL_PERIPHERAL_FREQMHZ} {puts $pf "$name=[get_property CONFIG.$name $ps]"}
close $pf
set af [open [file join $release address_map.txt] w]
foreach space [get_bd_addr_spaces] {
    puts $af "SPACE $space"
    foreach seg [get_bd_addr_segs -of_objects $space] {puts $af "$seg [get_property OFFSET $seg] [get_property RANGE $seg]"}
}
close $af
set hf [open [file join $release interface_properties.txt] w]
foreach pin {network/M_AXI memory_bus/S00_AXI memory_bus/M00_AXI ps7/S_AXI_HP0} {
    puts $hf "INTERFACE $pin"
    report_property -all [get_bd_intf_pins $pin]
    foreach key {CONFIG.PROTOCOL CONFIG.DATA_WIDTH CONFIG.ID_WIDTH CONFIG.READ_WRITE_MODE CONFIG.FREQ_HZ} {
        catch {puts $hf "$key=[get_property $key [get_bd_intf_pins $pin]]"}
    }
}
close $hf
set_property synth_checkpoint_mode None [get_files flyvis_ddr.bd]
generate_target all [get_files flyvis_ddr.bd]
set wrapper [make_wrapper -files [get_files flyvis_ddr.bd] -top]
add_files -norecurse $wrapper
set_property top flyvis_ddr_wrapper [current_fileset]
update_compile_order -fileset sources_1
save_bd_design

read_xdc [file join $here camera_candidate.xdc]
synth_design -top flyvis_ddr_wrapper -part xc7z020clg400-2
report_utilization -file [file join $release utilization_synth.rpt]
write_checkpoint [file join $release ddr_soc_synth.dcp]
set f [open synth_completed.txt w];puts $f "synth complete";close $f
exit

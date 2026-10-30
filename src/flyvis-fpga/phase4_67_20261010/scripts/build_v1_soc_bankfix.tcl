# Independent Phase 4 V1 board shell. Creates local BIT/HWH/XSA only.
set root [file normalize [file join [file dirname [info script]] ..]]
set p3 [file normalize [file join $root .. phase3_20261010]]
set ip_repo [file join $p3 build vitis_2026_1_q22_animation_enterprise_20261010_1842 hls impl ip]
set ps_params_file [file join $root artifacts leader_ps7_user_params.tcl]
set stamp [clock format [clock seconds] -format %Y%m%d_%H%M%S]
set build_root [file normalize [file join $root .. p4b r$stamp]]
set release_dir [file join $root build V1_bankfix_$stamp]
if {[file exists $build_root] || [file exists $release_dir]} { error "Refusing to overwrite existing build/release: $build_root / $release_dir" }
if {![file exists [file join $ip_repo component.xml]]} { error "Validated HLS IP is missing at $ip_repo" }
if {![file isfile $ps_params_file]} { error "Run inspect_leader_platform.py first" }
file mkdir [file dirname $build_root]
file mkdir $release_dir

create_project flyvis67v1 $build_root -part xc7z020clg400-2
set_property target_language Verilog [current_project]
set_property ip_repo_paths [list $ip_repo] [current_project]
update_ip_catalog

# Vivado 2026.1.1 loads installed BD rule scripts that call `source utils.tcl`
# relative to their own file, while the rule loader leaves the project
# directory as the process CWD. Resolve only that local include without
# changing CWD or modifying the Vivado installation.
rename ::source ::flyvis_original_source
proc ::source {args} {
    set script [lindex $args end]
    if {[file pathtype $script] eq "relative"} {
        set caller_script [string map {\\ /} [info script]]
        if {[string first "/Vivado/data/" $caller_script] >= 0} {
            set local_script [file join [file dirname $caller_script] $script]
            if {[file isfile $local_script]} {
                set args [lreplace $args end end $local_script]
            }
        }
    }
    return [uplevel 1 [list ::flyvis_original_source {*}$args]]
}

# Start with the vendor PYNQ resizer's PS7 DDR/MIO/network settings and keep
# its GP0, 64-bit HP0, and 100 MHz FCLK values for the FlyVis IP.
source $ps_params_file
set ps7props {}
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
        lappend ps7props CONFIG.$name $value
    }
}

create_bd_design flyvis_v1
set ps [create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 ps7]
if {[llength $ps7props]} { set_property -dict $ps7props $ps }
set_property -dict [list \
    CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ {100} \
    CONFIG.PCW_EN_CLK0_PORT {1} \
    CONFIG.PCW_USE_M_AXI_GP0 {1} \
    CONFIG.PCW_USE_S_AXI_HP0 {1} \
    CONFIG.PCW_S_AXI_HP0_DATA_WIDTH {64} \
] $ps

foreach {name expected} {PCW_PRESET_BANK0_VOLTAGE {LVCMOS 3.3V} PCW_PRESET_BANK1_VOLTAGE {LVCMOS 1.8V} PCW_MIO_16_IOTYPE {LVCMOS 1.8V} PCW_MIO_27_IOTYPE {LVCMOS 1.8V}} {
    if {[get_property CONFIG.$name $ps] ne $expected} {error "Vendor PS7 voltage mismatch: $name"}
}

create_bd_cell -type ip -vlnv xilinx.com:hls:flyvis_t5c_source_raw:1.0 flyvis_h
set cfg_ic [create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 cfg_ic]
set_property CONFIG.NUM_MI {1} $cfg_ic
set mem_ic [create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 mem_ic]
set_property -dict [list CONFIG.NUM_SI {1} CONFIG.NUM_MI {1}] $mem_ic
set reset_inv [create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 reset_inv]
set_property -dict [list CONFIG.C_OPERATION {not} CONFIG.C_SIZE {1}] $reset_inv
set reset [create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:5.0 reset]
set zero [create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 zero]
set_property CONFIG.CONST_VAL 0 $zero
set one [create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 one]
set_property CONFIG.CONST_VAL 1 $one

create_bd_intf_port -mode Master -vlnv xilinx.com:interface:ddrx_rtl:1.0 DDR
connect_bd_intf_net [get_bd_intf_pins ps7/DDR] [get_bd_intf_ports DDR]
create_bd_intf_port -mode Master -vlnv xilinx.com:display_processing_system7:fixedio_rtl:1.0 FIXED_IO
connect_bd_intf_net [get_bd_intf_pins ps7/FIXED_IO] [get_bd_intf_ports FIXED_IO]

# GP0 controls the HLS registers; HLS m_axi_gmem0 sends requests/results to DDR
# through a width-converting interconnect and HP0. No host-side chemical input.
connect_bd_intf_net [get_bd_intf_pins ps7/M_AXI_GP0] [get_bd_intf_pins cfg_ic/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins cfg_ic/M00_AXI] [get_bd_intf_pins flyvis_h/s_axi_control]
connect_bd_intf_net [get_bd_intf_pins flyvis_h/m_axi_gmem0] [get_bd_intf_pins mem_ic/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins mem_ic/M00_AXI] [get_bd_intf_pins ps7/S_AXI_HP0]

connect_bd_net [get_bd_pins ps7/FCLK_CLK0] \
    [get_bd_pins ps7/M_AXI_GP0_ACLK] [get_bd_pins ps7/S_AXI_HP0_ACLK] \
    [get_bd_pins cfg_ic/ACLK] [get_bd_pins cfg_ic/S00_ACLK] [get_bd_pins cfg_ic/M00_ACLK] \
    [get_bd_pins mem_ic/ACLK] [get_bd_pins mem_ic/S00_ACLK] [get_bd_pins mem_ic/M00_ACLK] \
    [get_bd_pins flyvis_h/ap_clk] [get_bd_pins reset/slowest_sync_clk]
connect_bd_net [get_bd_pins ps7/FCLK_RESET0_N] [get_bd_pins reset_inv/Op1]
connect_bd_net [get_bd_pins reset_inv/Res] [get_bd_pins reset/ext_reset_in]
connect_bd_net [get_bd_pins zero/dout] [get_bd_pins reset/aux_reset_in] [get_bd_pins reset/mb_debug_sys_rst]
connect_bd_net [get_bd_pins one/dout] [get_bd_pins reset/dcm_locked]
connect_bd_net [get_bd_pins reset/interconnect_aresetn] \
    [get_bd_pins cfg_ic/ARESETN] [get_bd_pins cfg_ic/S00_ARESETN] [get_bd_pins cfg_ic/M00_ARESETN] \
    [get_bd_pins mem_ic/ARESETN] [get_bd_pins mem_ic/S00_ARESETN] [get_bd_pins mem_ic/M00_ARESETN]
connect_bd_net [get_bd_pins reset/peripheral_aresetn] [get_bd_pins flyvis_h/ap_rst_n]

assign_bd_address
set assigned 0
set ps_data_space [get_bd_addr_spaces ps7/Data]
set ps_data_segs [get_bd_addr_segs -of_objects $ps_data_space]
foreach seg $ps_data_segs {
    if {[get_property NAME $seg] eq "SEG_flyvis_h_Reg"} {
        set_property offset 0x43C00000 $seg
        set_property range 64K $seg
        set assigned 1
    }
}
if {!$assigned} { error "HLS control segment was not assigned in the PS address space" }

validate_bd_design
save_bd_design
generate_target all [get_files flyvis_v1.bd]
set bd [get_files flyvis_v1.bd]
set wrapper [make_wrapper -files $bd -top]
add_files -norecurse $wrapper
set_property top flyvis_v1_wrapper [current_fileset]
update_compile_order -fileset sources_1
validate_bd_design
save_bd_design
puts "FLYVIS_V1_SOC_VALIDATED build=$build_root part=xc7z020clg400-2 control=0x43C00000 HP0=64 FCLK=100MHz"

launch_runs synth_1 -jobs 4
wait_on_run synth_1
if {[get_property PROGRESS [get_runs synth_1]] ne "100%"} { error "Synthesis did not complete" }
open_run synth_1
report_utilization -file [file join $release_dir synth_utilization.rpt]
report_timing_summary -file [file join $release_dir synth_timing_summary.rpt]

launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1
if {[get_property PROGRESS [get_runs impl_1]] ne "100%"} { error "Full SoC implementation/bit generation did not complete" }
open_run impl_1
report_utilization -file [file join $release_dir implementation_utilization.rpt]
report_timing_summary -delay_type min_max -file [file join $release_dir implementation_timing_summary.rpt]
report_drc -file [file join $release_dir implementation_drc.rpt]
report_io -file [file join $release_dir implementation_io.rpt]

set bit_candidates [glob -nocomplain -types f [file join $build_root flyvis67v1.runs impl_1 *.bit]]
if {[llength $bit_candidates] != 1} { error "Expected one implementation bitstream; got $bit_candidates" }
set bit_file [lindex $bit_candidates 0]
set hwh_candidates [glob -nocomplain -types f [file join $build_root *.gen sources_1 bd flyvis_v1 hw_handoff flyvis_v1.hwh]]
if {[llength $hwh_candidates] != 1} { error "Expected one flyvis_v1.hwh; got $hwh_candidates" }
file copy $bit_file [file join $release_dir flyvis_t5c_source_raw_v1.bit]
file copy [lindex $hwh_candidates 0] [file join $release_dir flyvis_t5c_source_raw_v1.hwh]
write_hw_platform -fixed -include_bit -file [file join $release_dir flyvis_t5c_source_raw_v1.xsa]
puts "FLYVIS_V1_SOC_IMPL_BIT_HWH_READY release=$release_dir board_programming=NOT_PERFORMED"
exit

# Independent B production BD, then system simulation, then gated implementation.
set_param general.maxThreads 1
set build [file normalize [lindex $argv 0]]
set action [lindex $argv 1]
set project_file [file join $build project b_soc.xpr]
if {$action eq "prepare"} {
 create_project b_soc [file join $build project] -part xc7z020clg400-2
 set_property target_language Verilog [current_project]
 foreach f [glob [file join $build source *.sv]] {if {[file tail $f] ne "tb_soc.sv"} {add_files $f}}
 add_files [list [file join $build rom weights.mem] [file join $build rom neurons.mem]]
 # Work around installed BD rule relative source calls without changing installation.
 rename ::source ::b_original_source
 proc ::source {args} {
  set path [lindex $args end]
  if {[file pathtype $path] eq "relative"} {
   set caller [string map {\\ /} [info script]]
   if {[string first "/Vivado/data/" $caller]>=0 && [file isfile [file join [file dirname $caller] $path]]} {set args [lreplace $args end end [file join [file dirname $caller] $path]]}
  }
  return [uplevel 1 [list ::b_original_source {*}$args]]
 }
 source [file join $build source leader_ps7_user_params.tcl]
 set props {}
 foreach {name value} $flyvis_vendor_ps7_user_params {
  if {[regexp {^PCW_(UIPARAM_DDR_|DDR_|DQS_|DQ_|DM_|MIO_|QSPI_|SD0_|UART0_|ENET0_|USB0_|GPIO_MIO_|PRESET_BANK)} $name] || $name eq "PCW_CRYSTAL_PERIPHERAL_FREQMHZ"} {lappend props CONFIG.$name $value}
 }
 create_bd_design b_soc
 set ps [create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 ps7]
 set_property -dict $props $ps
 set_property -dict [list CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ 100 CONFIG.PCW_EN_CLK0_PORT 1 CONFIG.PCW_USE_M_AXI_GP0 1 CONFIG.PCW_USE_S_AXI_HP0 1 CONFIG.PCW_S_AXI_HP0_DATA_WIDTH 64] $ps
 set engine [create_bd_cell -type module -reference b_soc_engine engine]
 set cfg [create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 cfg]
 set_property CONFIG.NUM_MI 1 $cfg
 set reset [create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:5.0 reset]
 # PS FCLK_RESET0_N connects directly: external active-low, unused auxiliary active-high.
 # C_EXT_RESET_HIGH is derived read-only from the actual connected reset polarity.
 set_property CONFIG.C_AUX_RESET_HIGH 1 $reset
 set zero [create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 zero]
 set_property CONFIG.CONST_VAL 0 $zero
 set one [create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 one]
 set_property CONFIG.CONST_VAL 1 $one
 make_bd_intf_pins_external [get_bd_intf_pins ps7/DDR] [get_bd_intf_pins ps7/FIXED_IO]
 connect_bd_intf_net [get_bd_intf_pins ps7/M_AXI_GP0] [get_bd_intf_pins cfg/S00_AXI]
 connect_bd_intf_net [get_bd_intf_pins cfg/M00_AXI] [get_bd_intf_pins engine/s_axi]
 connect_bd_intf_net [get_bd_intf_pins engine/m_axi] [get_bd_intf_pins ps7/S_AXI_HP0]
 set clocks [list ps7/M_AXI_GP0_ACLK ps7/S_AXI_HP0_ACLK engine/clk reset/slowest_sync_clk]
 foreach pin [get_bd_pins cfg/*CLK] {lappend clocks $pin}
 set clock_pins {};foreach name $clocks {lappend clock_pins [get_bd_pins $name]}
 connect_bd_net [get_bd_pins ps7/FCLK_CLK0] {*}$clock_pins
 connect_bd_net [get_bd_pins ps7/FCLK_RESET0_N] [get_bd_pins reset/ext_reset_in]
 connect_bd_net [get_bd_pins zero/dout] [get_bd_pins reset/aux_reset_in] [get_bd_pins reset/mb_debug_sys_rst]
 connect_bd_net [get_bd_pins one/dout] [get_bd_pins reset/dcm_locked]
 foreach pin [get_bd_pins cfg/*RESETN] {connect_bd_net [get_bd_pins reset/interconnect_aresetn] [get_bd_pins $pin]}
 connect_bd_net [get_bd_pins reset/peripheral_aresetn] [get_bd_pins engine/rst_n]
 assign_bd_address
 set found 0
 foreach seg [get_bd_addr_segs -of_objects [get_bd_addr_spaces ps7/Data]] {
  if {[string match *engine* [get_property NAME $seg]]} {set_property offset 0x43C20000 $seg;set_property range 128K $seg;set found 1}
 }
 if {!$found} {error "B GP0 control address not assigned"}
 validate_bd_design
 if {[get_property CONFIG.C_EXT_RESET_HIGH $reset]!=0 || [get_property CONFIG.C_AUX_RESET_HIGH $reset]!=1} {error "Actual proc_sys_reset polarity wrong"}
 validate_bd_design
 save_bd_design
 set bd [get_files b_soc.bd]
 set_property synth_checkpoint_mode None $bd
 generate_target all $bd
 add_files -norecurse [make_wrapper -files $bd -top]
 set_property top b_soc_wrapper [current_fileset]
 add_files -fileset sim_1 [file join $build source tb_soc.sv]
 set_property top tb_soc [get_filesets sim_1]
 update_compile_order -fileset sources_1
 update_compile_order -fileset sim_1
 write_bd_tcl -force [file join $build validated_bd.tcl]
 set f [open [file join $build reset_contract.txt] w]
 puts $f "C_EXT_RESET_HIGH=[get_property CONFIG.C_EXT_RESET_HIGH $reset]"
 puts $f "C_AUX_RESET_HIGH=[get_property CONFIG.C_AUX_RESET_HIGH $reset]"
 puts $f "FCLK0_MHz=[get_property CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ $ps]"
 puts $f "control_base=0x43C20000 range=128K HP0_width=64"
 close $f
 puts "B_SOC_PRODUCTION_BD_GENERATED_NO_SYNTHESIS"
} elseif {$action eq "simulate"} {
 open_project $project_file
 set simdir [file join $build project b_soc.sim sim_1 behav xsim]
 file mkdir [file join $simdir rom]
 foreach name {weights.mem neurons.mem requests.mem edges.mem expected.mem} {file copy -force [file join $build rom $name] [file join $simdir rom $name]}
 set_property -name xsim.elaborate.xelab.more_options -value {} -objects [get_filesets sim_1]
 set_property xsim.elaborate.mt_level off [get_filesets sim_1]
 launch_simulation -mode behavioral
 run all
 close_sim
 if {![file isfile [file join $simdir system_pass.txt]]} {error "System simulation did not produce PASS; synthesis forbidden"}
 file copy -force [file join $simdir system_pass.txt] [file join $build system_pass.txt]
 puts "B_ACTUAL_BD_SYSTEM_SIMULATION_PASS"
} elseif {$action eq "implement"} {
 if {![file isfile [file join $build system_pass.txt]]} {error "Actual-BD simulation gate not passed"}
 open_project $project_file
 foreach name {synth_1 impl_1} {
  file mkdir [file join $build project b_soc.runs $name rom]
  foreach mem {weights.mem neurons.mem} {file copy -force [file join $build rom $mem] [file join $build project b_soc.runs $name rom $mem]}
 }
 set hook [file join $build single_thread.tcl]
 set f [open $hook w];puts $f {set_param general.maxThreads 1};close $f
 set_property STEPS.SYNTH_DESIGN.TCL.PRE $hook [get_runs synth_1]
 set_property STEPS.OPT_DESIGN.TCL.PRE $hook [get_runs impl_1]
 launch_runs synth_1 -jobs 1
 wait_on_run synth_1
 if {[get_property PROGRESS [get_runs synth_1]] ne "100%"} {error "B SoC synthesis incomplete"}
 open_run synth_1
 report_utilization -file [file join $build synth_utilization.rpt]
 report_timing_summary -delay_type min_max -report_unconstrained -file [file join $build synth_timing.rpt]
 launch_runs impl_1 -to_step route_design -jobs 1
 wait_on_run impl_1
 if {[get_property STATUS [get_runs impl_1]] ne "route_design Complete!"} {error "B SoC route incomplete"}
 open_run impl_1
 report_utilization -file [file join $build routed_utilization.rpt]
 report_timing_summary -delay_type min_max -report_unconstrained -file [file join $build routed_timing.rpt]
 check_timing -verbose -file [file join $build check_timing.rpt]
 report_drc -file [file join $build routed_drc.rpt]
 report_route_status -file [file join $build route_status.rpt]
 report_clocks -file [file join $build routed_clocks.rpt]
 report_methodology -file [file join $build routed_methodology.rpt]
 report_timing -delay_type min -max_paths 20 -file [file join $build routed_hold_paths.rpt]
 report_timing -delay_type max -max_paths 20 -file [file join $build routed_setup_paths.rpt]
 write_xdc -force [file join $build routed_constraints.xdc]
 write_checkpoint [file join $build b_soc_routed.dcp]
 set wns [get_property SLACK [get_timing_paths -delay_type max -max_paths 1]]
 set whs [get_property SLACK [get_timing_paths -delay_type min -max_paths 1]]
 if {$wns<0 || $whs<0} {error "B complete SoC timing FAIL; no bit release"}
 # Independently gate pulse width and all failing endpoint totals as well.
 set f [open [file join $build routed_timing.rpt] r];set timing [read $f];close $f
 set summary_pattern {(?m)^\s+([-0-9.]+)\s+([-0-9.]+)\s+(\d+)\s+(\d+)\s+([-0-9.]+)\s+([-0-9.]+)\s+(\d+)\s+(\d+)\s+([-0-9.]+)\s+([-0-9.]+)\s+(\d+)\s+(\d+)\s*$}
 if {![regexp $summary_pattern $timing row setup tns setup_fail setup_total hold ths hold_fail hold_total pulse tpws pulse_fail pulse_total]} {error "Timing summary not parsed; no bit release"}
 if {$setup<0 || $hold<0 || $pulse<0 || $setup_fail!=0 || $hold_fail!=0 || $pulse_fail!=0} {error "Timing or pulse failure; no bit release"}
 set f [open [file join $build check_timing.rpt] r];set checking [read $f];close $f
 set checks [regexp -all -inline {checking ([a-z_]+) \(([0-9]+)\)} $checking]
 if {[llength $checks]<36} {error "Incomplete constraint coverage; no bit release"}
 foreach {whole name count} $checks {if {$count!=0} {error "Constraint check $name=$count; no bit release"}}
 if {[llength [get_cells -hierarchical -filter {IS_BLACKBOX == 1}]]!=0} {error "Black box present; no bit release"}
 foreach violation [get_drc_violations] {if {[get_property SEVERITY $violation] in {Error {Critical Warning}}} {error "B critical DRC $violation"}}
 write_bitstream [file join $build flyvis_b.bit]
 set hwh [glob [file join $build project *.gen sources_1 bd b_soc hw_handoff b_soc.hwh]]
 if {[llength $hwh]!=1} {error "Expected one B HWH"}
 file copy [lindex $hwh 0] [file join $build flyvis_b.hwh]
 puts "B_COMPLETE_SOC_BIT_HWH_READY_BOARD_NOT_RUN"
} else {error "Unknown B stage"}
exit 0

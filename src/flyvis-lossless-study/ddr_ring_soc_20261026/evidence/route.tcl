set_param general.maxThreads 1
set here [file dirname [file normalize [info script]]]
cd $here
file mkdir release_routed
open_checkpoint release/combined_synth.dcp
if {[get_property PART [current_design]] ne "xc7z020clg400-2"} {error "Wrong device"}
set bb [get_cells -quiet -hier -filter {IS_BLACKBOX == 1}]
if {[llength $bb]} {error "Unresolved blackboxes: $bb"}
# Official pin exception needs the synthesized IBUF net, not RTL elaboration.
set n [get_nets -quiet cam_pclk_IBUF]
if {[llength $n]!=1} {error "Camera clock net not unique"}
set_property CLOCK_DEDICATED_ROUTE FALSE $n
report_drc -file release_routed/drc_before_route.rpt
opt_design
place_design
phys_opt_design
route_design
report_utilization -file release_routed/utilization_routed.rpt
report_utilization -hierarchical -file release_routed/utilization_routed_hier.rpt
report_timing_summary -delay_type min_max -report_unconstrained -file release_routed/timing_routed.rpt
report_timing -delay_type max -max_paths 10 -path_type full_clock_expanded -file release_routed/paths_setup.rpt
report_timing -delay_type min -max_paths 10 -path_type full_clock_expanded -file release_routed/paths_hold.rpt
check_timing -verbose -file release_routed/check_timing.rpt
report_route_status -file release_routed/route_status.rpt
report_drc -file release_routed/drc.rpt
report_bus_skew -file release_routed/bus_skew.rpt
report_cdc -details -file release_routed/cdc.rpt
report_io -file release_routed/io.rpt
report_clock_utilization -file release_routed/clocks.rpt
write_xdc release_routed/effective_constraints.xdc
write_checkpoint release_routed/combined_routed.dcp
report_clock_interaction -file release_routed/clock_interaction.rpt
report_exceptions -file release_routed/exceptions.rpt
set neurons [get_cells -hier -filter {IS_SEQUENTIAL == 1 && NAME =~ */network/*}]
if {[llength $neurons]<100} {error "Missing neural state logic"}
report_timing -from [get_clocks clk_fpga_0] -to $neurons -max_paths 10 -file release_routed/neural_setup.rpt
report_timing -delay_type min -from [get_clocks clk_fpga_0] -to $neurons -max_paths 10 -file release_routed/neural_hold.rpt
source audit_routed.tcl
set f [open ROUTE_COMPLETED_REVIEW_REQUIRED.txt w]
puts $f "Route completed; inspect timing/DRC/CDC reports. Camera72MHz external budget conditional; no bitstream or board operations."
close $f
exit

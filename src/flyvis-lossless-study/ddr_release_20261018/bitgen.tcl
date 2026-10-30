# Exact accepted route -> BIT only. No synthesis, route, XSA or hardware action.
set_param general.maxThreads 1
set here [file dirname [file normalize [info script]]]
cd $here
set f [open tool_version.txt w];puts $f [version];close $f
open_checkpoint source_routed.dcp
if {[get_property PART [current_design]] ne "xc7z020clg400-2"} {error "Wrong part"}
if {[llength [get_cells -quiet flyvis_ddr_i]]!=1} {error "Wrong complete SoC root"}
if {[llength [get_cells -quiet -hier -filter {IS_BLACKBOX == 1}]]} {error "Unresolved IP"}
set clocks [get_clocks clk_fpga_0]
if {[llength $clocks]!=1||abs([get_property PERIOD $clocks]-10.0)>0.00001} {error "Wrong clock"}
report_timing_summary -delay_type min_max -report_unconstrained -file timing.rpt
report_route_status -file route_status.rpt
check_timing -verbose -file check_timing.rpt
report_drc -file drc.rpt
foreach mode {max min} {
    if {[llength [get_timing_paths -quiet -delay_type $mode -slack_lesser_than 0 -max_paths 1]]} {error "Timing failed"}
}
foreach item [get_drc_violations -quiet] {
    if {[get_property SEVERITY $item] in {Error {Critical Warning}}} {error "DRC failed"}
}
write_bitstream flyvis_ddr.bit
set f [open completed.txt w];puts $f "BIT generated from exact accepted route; no board operations";close $f
exit 0

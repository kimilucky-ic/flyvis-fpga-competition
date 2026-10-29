# Full SoC, all resolved IPs and constraints loaded from the accepted synthesis
# checkpoint. One Vivado process avoids keeping a parent project process resident.
set_param general.maxThreads 1
set here [file dirname [file normalize [info script]]]
cd $here
set release [file join $here release]
set f [open tool_version.txt w];puts $f [version];close $f
open_checkpoint [file join $release ddr_soc_synth.dcp]
if {[current_design] eq ""} {error "No checkpoint design opened"}
puts "Opened checkpoint design handle: [current_design]"
report_property -all -file design_properties.txt [current_design]
if {[llength [get_cells -quiet flyvis_ddr_i]]!=1} {error "Missing full SoC root cell"}
if {[get_property PART [current_design]] ne "xc7z020clg400-2"} {error "Unexpected checkpoint part"}
set blackboxes [get_cells -quiet -hier -filter {IS_BLACKBOX == 1}]
if {[llength $blackboxes]} {error "Unresolved black boxes in synthesized SoC: $blackboxes"}
# Apply vendor PCLK placement exception after actual IBUF net exists.
set camera_net [get_nets -quiet cam_pclk_IBUF]
if {[llength $camera_net]!=1} {error "Expected one post-synthesis camera IBUF net"}
puts "Camera non-dedicated clock network: $camera_net"
set_property CLOCK_DEDICATED_ROUTE FALSE $camera_net
opt_design
place_design
phys_opt_design
route_design
report_utilization -file [file join $release utilization_routed.rpt]
report_utilization -hierarchical -file [file join $release utilization_routed_hier.rpt]
report_timing_summary -delay_type min_max -report_unconstrained -file [file join $release timing_routed.rpt]
report_timing -delay_type max -max_paths 10 -path_type full_clock_expanded -file [file join $release paths_setup.rpt]
report_timing -delay_type min -max_paths 10 -path_type full_clock_expanded -file [file join $release paths_hold.rpt]
check_timing -verbose -file [file join $release check_timing.rpt]
report_route_status -file [file join $release route_status.rpt]
report_drc -file [file join $release drc.rpt]
report_cdc -file [file join $release cdc.rpt]
report_io -file [file join $release io.rpt]
report_clock_utilization -file [file join $release clocks.rpt]
write_checkpoint [file join $release ddr_soc_routed.dcp]
set setup_bad [get_timing_paths -quiet -delay_type max -slack_lesser_than 0 -max_paths 1]
set hold_bad [get_timing_paths -quiet -delay_type min -slack_lesser_than 0 -max_paths 1]
if {[llength $setup_bad]||[llength $hold_bad]} {error "Full SoC timing fails; no bitstream"}
foreach item [get_drc_violations -quiet] {
    if {[get_property SEVERITY $item] in {Error {Critical Warning}}} {error "DRC error; no bitstream"}
}
set f [open completed.txt w]
puts $f "Full DDR SoC route/timing/DRC passed. Reports and DCP only; no bitstream, board or GPU operation."
close $f
exit 0

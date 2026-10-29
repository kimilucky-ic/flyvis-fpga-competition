# Exactly one physical attempt, from accepted pipeline synthesis DCP. No synthesis.
set_param general.maxThreads 1
open_checkpoint input_synthesis.dcp
if {[get_property PART [current_design]] ne "xc7z020clg400-2"} {error "Wrong accepted device"}
if {[llength [get_clocks]] != 1 || [get_property PERIOD [get_clocks b_clk]] != 10.000} {error "Clock identity drift"}
if {[llength [get_sites -quiet BUFGCTRL_X0Y16]] != 1} {error "Reference clock site unavailable"}
read_xdc context.xdc
if {[get_property HD.CLK_SRC [get_ports clk]] ne "BUFGCTRL_X0Y16"} {error "Clock context absent"}
write_xdc context_resolved.xdc
report_clocks -file clocks_context.rpt
report_exceptions -file exceptions_context.rpt
check_timing -verbose -file check_context.rpt

proc violation_paths {stage} {
    set f [open "${stage}_violations.tsv" w]
    puts $f "kind\tslack_ns\tstartpoint\tendpoint\tstartpoint_class\tendpoint_class"
    foreach type {max min} {
        foreach p [get_timing_paths -quiet -delay_type $type -max_paths 10000 -nworst 1 -slack_lesser_than 0] {
            set a [get_property STARTPOINT_PIN $p];set b [get_property ENDPOINT_PIN $p]
            puts $f "$type\t[get_property SLACK $p]\t$a\t$b\t[get_property CLASS $a]\t[get_property CLASS $b]"
        }
    }
    close $f
}
report_timing_summary -delay_type min_max -report_unconstrained -max_paths 10 -file timing_context.rpt
violation_paths context
set started [clock milliseconds]
opt_design
place_design
write_checkpoint b_placed.dcp
report_timing_summary -delay_type min_max -report_unconstrained -max_paths 10 -file timing_placed.rpt
violation_paths placed
# Single timing-driven route. No retry/second clock target/constraint rewrite.
route_design
set route_ms [expr {[clock milliseconds]-$started}]
write_checkpoint b_routed.dcp
write_xdc routed_constraints.xdc
report_route_status -file route_status.rpt
report_utilization -file utilization_routed.rpt
report_utilization -hierarchical -hierarchical_depth 6 -file utilization_hierarchical.rpt
foreach scope {core reader fifo} {report_utilization -cells [get_cells $scope] -file utilization_${scope}.rpt}
report_timing_summary -delay_type min_max -report_unconstrained -max_paths 10 -file timing_routed.rpt
report_timing -delay_type max -max_paths 10 -input_pins -file setup_routed.rpt
report_timing -delay_type min -max_paths 10 -input_pins -file hold_routed.rpt
check_timing -verbose -file check_routed.rpt
report_clocks -file clocks_routed.rpt
report_clock_networks -file clock_networks.rpt
report_exceptions -file exceptions_routed.rpt
report_drc -file drc_routed.rpt
report_methodology -file methodology_routed.rpt
violation_paths routed
set f [open primitive_cells.tsv w]
puts $f "cell\tref_name\tprimitive_group\tprimitive_subgroup"
foreach c [get_cells -hierarchical -filter {IS_PRIMITIVE == 1}] {
    puts $f "$c\t[get_property REF_NAME $c]\t[get_property PRIMITIVE_GROUP $c]\t[get_property PRIMITIVE_SUBGROUP $c]"
}
close $f
set f [open stage_identity.txt w]
puts $f "tool=[version -short]"
puts $f "part=[get_property PART [current_design]]"
puts $f "stage=OOC_PLACED_ROUTED_NO_SOC_NO_BIT"
puts $f "clock_period_ns=[get_property PERIOD [get_clocks b_clk]]"
puts $f "HD.CLK_SRC=[get_property HD.CLK_SRC [get_ports clk]]"
puts $f "general.maxThreads=[get_param general.maxThreads]"
puts $f "opt_place_route_ms=$route_ms"
puts $f "black_boxes=[llength [get_cells -quiet -hierarchical -filter {IS_BLACKBOX == 1}]]"
close $f
puts "B433880_SINGLE_OOC_PHYSICAL_ATTEMPT_COMPLETE"
exit 0

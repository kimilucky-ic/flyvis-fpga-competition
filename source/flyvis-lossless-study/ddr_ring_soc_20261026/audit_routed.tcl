# Structural checks in the routed full SoC; not numerical/board validation.
if {[get_property PART [current_design]] ne "xc7z020clg400-2"} {error "Part mismatch"}
if {[llength [get_clocks -quiet clk_fpga_0]] != 1} {error "Neural clock absent"}
if {abs([get_property PERIOD [get_clocks clk_fpga_0]] - 10.0) > 0.000001} {error "Neural clock not100MHz"}
set f [open release_routed/ring_structure.txt w]
puts $f "clock_period_ns [get_property PERIOD [get_clocks clk_fpga_0]]"
foreach pattern {*/network/*/released_count_reg* */network/*/committed_count_reg* */network/*/release_sequence_reg* */network/*/release_cookie_reg* */network/*/write_slot_reg* */network/*/session_cookie_reg*} {
    set cells [get_cells -quiet -hier -filter "IS_SEQUENTIAL == 1 && NAME =~ $pattern"]
    if {[llength $cells]==0} {error "Missing ring register group $pattern"}
    puts $f "$pattern [llength $cells]"
    foreach c $cells {puts $f "  $c [get_property REF_NAME $c]"}
}
close $f
report_timing -to [get_cells -hier -filter {IS_SEQUENTIAL == 1 && NAME =~ */network/*/released_count_reg*}] -max_paths 5 -file release_routed/release_ack_setup.rpt
report_timing -delay_type min -to [get_cells -hier -filter {IS_SEQUENTIAL == 1 && NAME =~ */network/*/released_count_reg*}] -max_paths 5 -file release_routed/release_ack_hold.rpt

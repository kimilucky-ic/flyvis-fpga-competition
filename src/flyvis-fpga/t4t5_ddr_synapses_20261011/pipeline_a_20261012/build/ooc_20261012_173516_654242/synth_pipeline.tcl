# User-selected A: one-lane II=1, four outstanding reads, FIFO 128. OOC synthesis only.
set_param general.maxThreads 1
set target xc7z020clg400-2
if {[llength [get_parts -quiet $target]] != 1} {error "Exact target unavailable"}
set sources {edge_fifo.sv axi_edge_reader.sv ddr_synapse_core.sv ddr_synapse_top.sv}
foreach source $sources {read_verilog -sv $source}
read_xdc clock.xdc
set b_start [clock milliseconds]
synth_design -top ddr_synapse_top -part $target -mode out_of_context -flatten_hierarchy none -generic {
    H_COUNT=5768 SOURCE_COUNT=16402 EDGE_COUNT=433880 WEIGHT_COUNT=645
    FIFO_DEPTH=128 AXI_TIMEOUT=64 STEP_TIMEOUT=8000000
}
set b_synth_ms [expr {[clock milliseconds]-$b_start}]
# Save checkpoint before optional detailed reporting so failures retain netlist.
write_checkpoint b_fullscale_synthesis.dcp
write_xdc resolved_constraints.xdc
report_utilization -file utilization_top.rpt
report_utilization -hierarchical -hierarchical_depth 6 -file utilization_hierarchical.rpt
foreach scope {core reader fifo} {
    set cell [get_cells -quiet $scope]
    if {[llength $cell] != 1} {error "Missing preserved hierarchy: $scope"}
    report_utilization -cells $cell -file utilization_${scope}.rpt
}
report_timing_summary -delay_type min_max -report_unconstrained -max_paths 10 -file timing_synth.rpt
report_timing -delay_type max -max_paths 10 -input_pins -file worst_setup_paths.rpt
report_timing -delay_type min -max_paths 10 -input_pins -file worst_hold_paths.rpt
check_timing -verbose -file check_timing.rpt
report_clocks -file clocks.rpt
report_exceptions -file exceptions.rpt
report_methodology -file methodology.rpt

set f [open primitive_cells.tsv w]
puts $f "cell\tref_name\tprimitive_group\tprimitive_subgroup"
foreach cell [get_cells -hierarchical -filter {IS_PRIMITIVE == 1}] {
    puts $f "$cell\t[get_property REF_NAME $cell]\t[get_property PRIMITIVE_GROUP $cell]\t[get_property PRIMITIVE_SUBGROUP $cell]"
}
close $f
set f [open ram_cells.tsv w]
puts $f "cell\tref_name\tread_width_a\tread_width_b\twrite_width_a\twrite_width_b\tdoa_reg\tdob_reg\tram_mode"
set rams [get_cells -hierarchical -filter {REF_NAME =~ RAMB*}]
foreach cell $rams {
    set values [list $cell [get_property REF_NAME $cell]]
    foreach prop {READ_WIDTH_A READ_WIDTH_B WRITE_WIDTH_A WRITE_WIDTH_B DOA_REG DOB_REG RAM_MODE} {
        if {[lsearch -exact [list_property $cell] $prop] >= 0} {lappend values [get_property $prop $cell]} else {lappend values ""}
    }
    puts $f [join $values "\t"]
}
close $f
set f [open ram_properties.tsv w]
puts $f "cell\tproperty\tvalue"
foreach cell $rams {
    # Keep BRAM configuration and all INIT/INITP contents. Generic list_property
    # also exposes unrelated AIE properties on 2026.1.1: do not query those.
    foreach prop [lsort [list_property $cell]] {
        if {[regexp {^(REF_NAME|NAME|INIT.*|SRVAL.*|READ_WIDTH.*|WRITE_WIDTH.*|WRITE_MODE.*|RAM_MODE|DO[AB]_REG|EN_ECC.*|RDADDR.*|SIM_.*)$} $prop]} {
            puts $f "$cell\t$prop\t[get_property $prop $cell]"
        }
    }
}
close $f
set f [open black_boxes.txt w]
set boxes [get_cells -quiet -hierarchical -filter {IS_BLACKBOX == 1}]
puts $f "count=[llength $boxes]"
foreach cell $boxes {puts $f $cell}
close $f
set f [open stage_identity.txt w]
puts $f "tool=[version -short]"
puts $f "part=[get_property PART [current_design]]"
puts $f "design=[current_design]"
puts $f "stage=OOC_SYNTHESIS_ONLY"
puts $f "flatten_hierarchy=none"
puts $f "general.maxThreads=[get_param general.maxThreads]"
puts $f "synthesis_elapsed_ms=$b_synth_ms"
puts $f "H_COUNT=5768 SOURCE_COUNT=16402 EDGE_COUNT=433880 WEIGHT_COUNT=645 FIFO_DEPTH=128 AXI_TIMEOUT=64 STEP_TIMEOUT=8000000"
puts $f "clock_period_ns=[get_property PERIOD [get_clocks b_clk]]"
puts $f "HD.CLK_SRC=[get_property HD.CLK_SRC [get_ports clk]]"
puts $f "black_box_count=[llength $boxes]"
close $f
puts "B433880_OOC_SYNTHESIS_COMPLETE_NO_IMPLEMENTATION"
exit 0

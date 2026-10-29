# Isolated 92-node OOC synthesis ONLY. No opt/place/route/bitstream/board.
set_param general.maxThreads 1
set target xc7z020clg400-2
set probe [open target_probe.txt w]
puts $probe "tool=[version -short] part=$target stage=OOC_SYNTHESIS_ONLY"
close $probe
if {[llength [get_parts -quiet $target]] != 1} {error "Exact device unavailable"}
read_verilog -sv scalable_source_raw_core.sv
read_xdc clock.xdc
synth_design -top scalable_source_raw_core -part $target -mode out_of_context
report_utilization -file utilization.rpt
report_utilization -hierarchical -file utilization_hierarchical.rpt
report_timing_summary -delay_type min_max -report_unconstrained -max_paths 10 -file timing_synth.rpt
check_timing -verbose -file check_timing.rpt
set fd [open memory_cells.txt w]
foreach cell [get_cells -hierarchical -filter {REF_NAME =~ RAMB* || REF_NAME =~ DSP*}] {
    puts $fd "$cell [get_property REF_NAME $cell]"
}
close $fd
write_checkpoint core_synthesis.dcp
puts "RESEARCH92_SYNTHESIS_COMPLETE_NO_IMPLEMENTATION"
exit 0

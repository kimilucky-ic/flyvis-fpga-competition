# Independent RTL OOC resource/implementation run. No bitstream or hardware APIs.
set root [file normalize [file dirname [info script]]]
set output [file join $root build rtl_ooc_2026_1_[clock format [clock seconds] -format %Y%m%d_%H%M%S]]
file mkdir $output
set target xc7z020clg400-2
set diag [open [file join $output target_probe.txt] w]
puts $diag "Vivado=[version -short] tier=[get_vivado_tier] target=$target parts_count=[llength [get_parts -quiet *]]"
if {[llength [get_parts -quiet $target]] != 1} {
    puts $diag "BLOCKED: exact target not available. No synthesis/resource PASS."
    close $diag
    error "FLYVIS_TARGET_UNAVAILABLE: $target; evidence=$output"
}
close $diag
file mkdir [file join $output rtl]
file mkdir [file join $output rom]
foreach leaf {flyvis_source_raw_core.sv flyvis_source_raw_axil.sv} {
    file copy [file join $root rtl $leaf] [file join $output rtl $leaf]
}
foreach leaf {edges_q22.mem neurons_q22.mem manifest.json} {
    file copy [file join $root rom $leaf] [file join $output rom $leaf]
}
file copy [info script] [file join $output rtl_ooc_synth.tcl]
cd $output
read_verilog -sv [file join $output rtl flyvis_source_raw_core.sv]
read_verilog -sv [file join $output rtl flyvis_source_raw_axil.sv]
synth_design -top flyvis_source_raw_axil -part $target -mode out_of_context
create_clock -name axi_clk -period 10 [get_ports s_axi_aclk]
report_utilization -file [file join $output rtl_ooc_synthesis_utilization.rpt]
write_checkpoint [file join $output rtl_ooc_synthesis.dcp]
opt_design
place_design
route_design
report_utilization -file [file join $output rtl_ooc_route_utilization.rpt]
report_timing_summary -file [file join $output rtl_ooc_route_timing.rpt]
report_timing_summary -delay_type min_max -max_paths 10 -report_unconstrained -file [file join $output rtl_ooc_route_timing_full.rpt]
check_timing -verbose -file [file join $output rtl_ooc_check_timing.rpt]
report_drc -file [file join $output rtl_ooc_route_drc.rpt]
write_checkpoint [file join $output rtl_ooc_route.dcp]
puts "FLYVIS_RTL_OOC_REPORTS=$output (not a full SoC or board result)"
exit 0

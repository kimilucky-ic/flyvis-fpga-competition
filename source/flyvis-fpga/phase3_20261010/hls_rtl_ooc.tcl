# Implement the exact, already co-simulated generated HLS RTL in a short fresh
# directory. This avoids relocating HLS's private compiler database and avoids
# IP-integrator's 267-character generated path. No bitstream or hardware APIs.
set root [file normalize [file dirname [info script]]]
set source [file join $root build vitis_2026_1_q22_animation_enterprise_20261010_1842 hls syn verilog]
set output [file join $root build hoc_[clock format [clock seconds] -format %Y%m%d_%H%M%S]]
set target xc7z020clg400-2
if {[llength [get_parts -quiet $target]] != 1} { error "FLYVIS_TARGET_UNAVAILABLE: $target" }
if {[file exists $output]} { error "Fresh output required: $output" }
file mkdir [file join $output hdl]
set files [glob -directory $source *.v *.dat]
foreach original $files {
    file copy $original [file join $output hdl [file tail $original]]
}
file copy [info script] [file join $output hls_rtl_ooc.tcl]
set f [open [file join $output target_probe.txt] w]
puts $f "Vivado=[version -short] tier=[get_vivado_tier] target=$target generated_RTL_source=$source"
close $f
cd [file join $output hdl]
read_verilog [glob *.v]
synth_design -top flyvis_t5c_source_raw -part $target -mode out_of_context
create_clock -name ap_clk -period 10 [get_ports ap_clk]
report_utilization -file [file join $output hls_ooc_synthesis_utilization.rpt]
write_checkpoint [file join $output hls_ooc_synthesis.dcp]
opt_design
place_design
route_design
report_utilization -file [file join $output hls_ooc_route_utilization.rpt]
report_timing_summary -file [file join $output hls_ooc_route_timing.rpt]
report_timing_summary -delay_type min_max -max_paths 10 -report_unconstrained -file [file join $output hls_ooc_route_timing_full.rpt]
check_timing -verbose -file [file join $output hls_ooc_check_timing.rpt]
report_drc -file [file join $output hls_ooc_route_drc.rpt]
write_checkpoint [file join $output hls_ooc_route.dcp]
puts "FLYVIS_HLS_RTL_OOC_REPORTS=$output; IP scope only, not full SoC or board execution"
exit 0

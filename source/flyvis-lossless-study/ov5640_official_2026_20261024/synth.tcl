set_param general.maxThreads 1
set here [file dirname [file normalize [info script]]]
cd $here
if {![file exists COMBINED_GENERATED.txt]} {error "Combined BD output products missing"}
file mkdir release
open_project [file join $here project3 migrated3.xpr]
set_property top base_wrapper [current_fileset]
read_xdc [file join $here camera_budget.xdc]
synth_design -top base_wrapper -part xc7z020clg400-2
report_utilization -file release/utilization_synth.rpt
report_utilization -hierarchical -file release/utilization_synth_hier.rpt
write_checkpoint release/combined_synth.dcp
set f [open synth_completed.txt w];puts $f "full official-video and strict-FP32 network synthesized only";close $f
exit

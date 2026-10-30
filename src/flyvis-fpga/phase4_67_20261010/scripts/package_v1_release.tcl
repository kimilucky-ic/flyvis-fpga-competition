# Package an already completed Phase 4 V1 implementation without rerunning it.
if {![info exists ::env(FLYVIS_BUILD_ROOT)] || ![info exists ::env(FLYVIS_RELEASE_DIR)]} {
    error "Set FLYVIS_BUILD_ROOT and FLYVIS_RELEASE_DIR before launching Vivado"
}
set build_root [file normalize $::env(FLYVIS_BUILD_ROOT)]
set release_dir [file normalize $::env(FLYVIS_RELEASE_DIR)]
set project_file [file join $build_root flyvis67v1.xpr]
if {![file isfile $project_file]} { error "Missing isolated V1 project: $project_file" }
foreach name {flyvis_t5c_source_raw_v1.bit flyvis_t5c_source_raw_v1.hwh flyvis_t5c_source_raw_v1.xsa} {
    if {[file exists [file join $release_dir $name]]} { error "Refusing to overwrite package file: $name" }
}
foreach name {implementation_timing_summary.rpt implementation_utilization.rpt implementation_drc.rpt implementation_io.rpt} {
    if {![file isfile [file join $release_dir $name]]} { error "Missing completed implementation report: $name" }
}
set bit_candidates [glob -nocomplain -types f [file join $build_root flyvis67v1.runs impl_1 *.bit]]
if {[llength $bit_candidates] != 1} { error "Expected one implementation bitstream; got $bit_candidates" }
set hwh_candidates [glob -nocomplain -types f [file join $build_root flyvis67v1.gen sources_1 bd flyvis_v1 hw_handoff flyvis_v1.hwh]]
if {[llength $hwh_candidates] != 1} { error "Expected one generated HWH; got $hwh_candidates" }

open_project $project_file
if {[get_property PROGRESS [get_runs impl_1]] ne "100%"} { error "Implementation run is not complete" }
open_run impl_1
file copy [lindex $bit_candidates 0] [file join $release_dir flyvis_t5c_source_raw_v1.bit]
file copy [lindex $hwh_candidates 0] [file join $release_dir flyvis_t5c_source_raw_v1.hwh]
write_hw_platform -fixed -include_bit -file [file join $release_dir flyvis_t5c_source_raw_v1.xsa]
foreach name {flyvis_t5c_source_raw_v1.bit flyvis_t5c_source_raw_v1.hwh flyvis_t5c_source_raw_v1.xsa} {
    set path [file join $release_dir $name]
    if {![file isfile $path] || [file size $path] == 0} { error "Package output missing or empty: $path" }
}
puts "FLYVIS_V1_SOC_IMPL_BIT_HWH_READY release=$release_dir board_programming=NOT_PERFORMED"
exit

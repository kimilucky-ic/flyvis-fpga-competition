set root [file normalize [file dirname [info script]]]
set target xc7z020clg400-2
set report [dict create version [version -short] active_tier [get_vivado_tier] all_parts_count [llength [get_parts -quiet *]] target [get_parts -quiet $target]]
dict set report create_project_code [catch {create_project -in_memory flyvis_license_probe -part $target} message]
dict set report create_project_message $message
if {[llength [get_projects -quiet]]} { close_project }
set output [file join $root artifacts license_target_probe_[clock format [clock seconds] -format %Y%m%d_%H%M%S].txt]
set f [open $output w]; puts $f $report; close $f
puts "FLYVIS_LICENSE_TARGET_PROBE=$report"
puts "FLYVIS_PROBE_EVIDENCE=$output"
if {[dict get $report create_project_code] != 0} { exit 3 }
exit 0

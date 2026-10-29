set_param general.maxThreads 1
set here [file dirname [file normalize [info script]]]
cd $here
# Installed vendor include path workaround; source RTL is never changed.
rename ::source ::original_source
proc ::source {args} {
    set script [lindex $args end]
    if {[file pathtype $script] eq "relative"} {
        set caller [string map {\\ /} [info script]]
        if {[string first "/Vivado/data/" $caller]>=0} {
            set candidate [file join [file dirname $caller] $script]
            if {[file isfile $candidate]} {set args [lreplace $args end end $candidate]}
        }
    }
    return [uplevel 1 [list ::original_source {*}$args]]
}
create_project migrated3 [file join $here project3] -part xc7z020clg400-2
set_property target_language Verilog [current_project]
set_property ip_repo_paths [file join $here vendor ip_repo] [current_project]
update_ip_catalog
file mkdir [file join $here imported3 base]
file copy [file join $here base_2026.bd] [file join $here imported3 base base.bd]
add_files -norecurse [file join $here imported3 base base.bd]
open_bd_design [get_files base.bd]
report_ip_status -file migrated_ip_status.rpt
set f [open migrated_cells.txt w]
foreach c [get_bd_cells -hier -filter {TYPE == ip}] {puts $f "$c [get_property VLNV $c]"}
close $f
validate_bd_design
save_bd_design
write_bd_tcl -force migrated_camera.tcl
puts "MIGRATED_CAMERA_BD_VALIDATED_NO_GENERATION"
exit

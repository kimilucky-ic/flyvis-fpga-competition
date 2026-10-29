set_param general.maxThreads 1
set here [file dirname [file normalize [info script]]]
cd $here
create_project migrated2 [file join $here project2] -part xc7z020clg400-2
set_property target_language Verilog [current_project]
set_property ip_repo_paths [file join $here vendor ip_repo] [current_project]
update_ip_catalog
file mkdir [file join $here imported2 base]
file copy [file join $here vendor base.bd] [file join $here imported2 base base.bd]
file copy [file join $here vendor bd_xci ip] [file join $here imported2 base ip]
add_files -norecurse [glob [file join $here imported2 base ip * *.xci]]
add_files -norecurse [file join $here imported2 base base.bd]
open_bd_design [get_files base.bd]
report_ip_status -file before_ip_status2.rpt
set f [open before_cells2.txt w]
foreach c [get_bd_cells -hier -filter {TYPE == ip}] {puts $f "$c [get_property VLNV $c]"}
close $f
help upgrade_bd_cells
help upgrade_ip
puts "INSPECT_DONE_NO_UPGRADE"
exit

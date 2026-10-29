set_param general.maxThreads 1
set here [file dirname [file normalize [info script]]]
cd $here
open_checkpoint combined_routed.dcp
if {[get_property PART [current_design]] ne "xc7z020clg400-2"} {error "Wrong device"}
report_drc -file bitgen_drc.rpt
write_bitstream flyvis_official.bit
exit

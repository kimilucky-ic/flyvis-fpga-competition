set_param general.maxThreads 1
set here [file dirname [file normalize [info script]]]
cd $here
open_checkpoint release_routed/combined_routed.dcp
report_drc -file bitgen_drc.rpt
write_bitstream flyvis_official.bit
close_design
exit

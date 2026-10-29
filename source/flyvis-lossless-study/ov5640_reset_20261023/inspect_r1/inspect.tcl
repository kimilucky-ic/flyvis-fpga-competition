set_param general.maxThreads 1
set here [file dirname [file normalize [info script]]]
cd $here
open_checkpoint ../build_r6/release/ddr_soc_routed.dcp
report_cdc -details -file cdc_details.rpt
foreach c [get_cells -hier -filter {NAME =~ */camera_guard/* && IS_SEQUENTIAL == 1}] {puts "GUARD $c ASYNC_REG=[get_property ASYNC_REG $c]"}
exit 0

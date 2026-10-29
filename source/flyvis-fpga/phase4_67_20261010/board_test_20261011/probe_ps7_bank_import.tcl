# Local configuration reproduction only. No hardware manager or board commands.
set p4 [file normalize [file join [file dirname [info script]] ..]]
set output [file dirname [info script]]
# Match the already validated launcher workaround; installation stays intact.
rename ::source ::flyvis_original_source
proc ::source {args} {
    set script [lindex $args end]
    if {[file pathtype $script] eq "relative"} {
        set caller_script [string map {\\ /} [info script]]
        if {[string first "/Vivado/data/" $caller_script] >= 0} {
            set local_script [file join [file dirname $caller_script] $script]
            if {[file isfile $local_script]} {set args [lreplace $args end end $local_script]}
        }
    }
    return [uplevel 1 [list ::flyvis_original_source {*}$args]]
}
source [file join $p4 artifacts leader_ps7_user_params.tcl]
set stamp [clock format [clock seconds] -format %Y%m%d_%H%M%S]
set probe_root [file normalize [file join $p4 .. p4b psprobe_$stamp]]
if {[file exists $probe_root]} {error "Refusing to overwrite $probe_root"}
file mkdir $probe_root
set report [open [file join $output PS7_BANK_IMPORT_PROBE_$stamp.tsv] {WRONLY CREAT EXCL}]
puts $report "variant\tparameter\tvalue"
puts "PROBE_TOOL [version -short] BOARD_IO=0"
foreach variant {original_filter with_bank_voltage} {
    create_project psprobe [file join $probe_root $variant] -part xc7z020clg400-2
    create_bd_design psprobe
    set ps [create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 ps7]
    set props {}
    foreach {name value} $flyvis_vendor_ps7_user_params {
        if {[string match "PCW_UIPARAM_DDR_*" $name] || [string match "PCW_DDR_*" $name] ||
            [string match "PCW_DQS_*" $name] || [string match "PCW_DQ_*" $name] ||
            [string match "PCW_DM_*" $name] || [string match "PCW_MIO_*" $name] ||
            [string match "PCW_QSPI_*" $name] || [string match "PCW_SD0_*" $name] ||
            [string match "PCW_UART0_*" $name] || [string match "PCW_ENET0_*" $name] ||
            [string match "PCW_USB0_*" $name] || [string match "PCW_GPIO_MIO_*" $name] ||
            $name eq "PCW_CRYSTAL_PERIPHERAL_FREQMHZ" ||
            $name eq "PCW_DDR_RAM_BASEADDR" || $name eq "PCW_DDR_RAM_HIGHADDR" ||
            ($variant eq "with_bank_voltage" && [string match "PCW_PRESET_BANK*_VOLTAGE" $name])} {
            lappend props CONFIG.$name $value
        }
    }
    set_property -dict $props $ps
    save_bd_design
    foreach name {PCW_PRESET_BANK0_VOLTAGE PCW_PRESET_BANK1_VOLTAGE PCW_MIO_16_IOTYPE PCW_MIO_27_IOTYPE PCW_UIPARAM_DDR_PARTNO} {
        puts $report "$variant\t$name\t[get_property CONFIG.$name $ps]"
        puts "PROBE $variant $name=[get_property CONFIG.$name $ps]"
    }
    if {$variant eq "with_bank_voltage" && [get_property CONFIG.PCW_PRESET_BANK1_VOLTAGE $ps] ne "LVCMOS 1.8V"} {
        error "Explicit vendor bank voltage was not preserved"
    }
    if {$variant eq "with_bank_voltage" && [get_property CONFIG.PCW_MIO_16_IOTYPE $ps] ne "LVCMOS 1.8V"} {
        error "RGMII MIO voltage was not regenerated correctly"
    }
    close_project
}
close $report
puts "PASS_LOCAL_PS7_BANK_IMPORT_REPRODUCTION BOARD_IO=0 BUILD=$probe_root"
exit

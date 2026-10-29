set_property -dict {PACKAGE_PIN T12 IOSTANDARD LVCMOS33} [get_ports cam_href]
set_property -dict {PACKAGE_PIN W14 IOSTANDARD LVCMOS33} [get_ports cam_pclk]
set_property -dict {PACKAGE_PIN U12 IOSTANDARD LVCMOS33} [get_ports cam_vsync]
set_property -dict {PACKAGE_PIN P14 IOSTANDARD LVCMOS33} [get_ports cam_rst_n]
set_property -dict {PACKAGE_PIN V15 IOSTANDARD LVCMOS33} [get_ports cam_pwdn]
set_property -dict {PACKAGE_PIN R14 IOSTANDARD LVCMOS33} [get_ports {cam_data[0]}]
set_property -dict {PACKAGE_PIN U13 IOSTANDARD LVCMOS33} [get_ports {cam_data[1]}]
set_property -dict {PACKAGE_PIN V13 IOSTANDARD LVCMOS33} [get_ports {cam_data[2]}]
set_property -dict {PACKAGE_PIN U15 IOSTANDARD LVCMOS33} [get_ports {cam_data[3]}]
set_property -dict {PACKAGE_PIN U14 IOSTANDARD LVCMOS33} [get_ports {cam_data[4]}]
set_property -dict {PACKAGE_PIN W13 IOSTANDARD LVCMOS33} [get_ports {cam_data[5]}]
set_property -dict {PACKAGE_PIN V12 IOSTANDARD LVCMOS33} [get_ports {cam_data[6]}]
set_property -dict {PACKAGE_PIN Y14 IOSTANDARD LVCMOS33} [get_ports {cam_data[7]}]
set_property -dict {PACKAGE_PIN T10 IOSTANDARD LVCMOS33} [get_ports {cam_iic_scl_io}]
set_property -dict {PACKAGE_PIN T11 IOSTANDARD LVCMOS33} [get_ports {cam_iic_sda_io}] 
# Reference only: not automatically imported; physical revision/PCLK timing pending.

# Conditional implementation budget; not measured camera input timing.
create_clock -name camera_pclk -period 13.888889 [get_ports cam_pclk]
# Original board routes PCLK W14; preserve explicit vendor non-dedicated route.
# Applied after synthesis when the exact IBUF net exists.
set_false_path -to [get_ports {cam_pwdn cam_rst_n}]

# SCCB is an asynchronous, clock-stretching open-drain bus, sampled at FCLK.
# Engineering pad/logic propagation budget, NOT sensor setup/hold certification.
# Protocol constraints: local OV5640 datasheet p165: <=400kHz, tAA 100..900ns,
# input setup>=100ns, hold>=0, rise/fall<=300ns. Core configured 100kHz.
# Default 0x4740=0x20; application guide R2.13C p27 specifies falling-edge data.
# CONDITIONAL acceptance envelope, not a characterized sensor tCO or board skew.
# Budget combines sensor clock-to-output and relative board trace skew.
set_input_delay -clock camera_pclk -clock_fall -min -0.500 [get_ports {cam_data[*] cam_href cam_vsync}]
set_input_delay -clock camera_pclk -clock_fall -max 2.000 [get_ports {cam_data[*] cam_href cam_vsync}]
set_clock_uncertainty -setup 0.250 [get_clocks camera_pclk]
set_clock_uncertainty -hold 0.100 [get_clocks camera_pclk]
# Async SCCB: bound actual pad-to-synchronizer and register-to-pad propagation,
# do not invent a synchronous SCL relationship to 100MHz FCLK.
# Vendor CDC first-stage false paths take precedence on input. Keep those;
# report input propagation separately and audit <=20ns, do not fake setup/hold.
set_max_delay -datapath_only 20.000 -from [get_cells -hier -filter {IS_SEQUENTIAL == 1 && NAME =~ */cam_iic/*}] -to [get_ports {cam_iic_scl_io cam_iic_sda_io}]

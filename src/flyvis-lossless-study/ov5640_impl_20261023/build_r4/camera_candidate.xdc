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
set_input_delay -clock camera_pclk -min 0.0 [get_ports {cam_data[*] cam_href cam_vsync}]
set_input_delay -clock camera_pclk -max 6.944444 [get_ports {cam_data[*] cam_href cam_vsync}]
# Original board routes PCLK W14; preserve explicit vendor non-dedicated route.
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets cam_pclk_IBUF]
set_false_path -to [get_ports {cam_pwdn cam_rst_n}]

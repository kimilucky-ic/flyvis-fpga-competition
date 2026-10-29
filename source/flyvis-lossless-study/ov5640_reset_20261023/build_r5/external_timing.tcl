# Default 0x4740=0x20; application guide R2.13C p27 specifies falling-edge data.
# CONDITIONAL acceptance envelope, not a characterized sensor tCO or board skew.
# Budget combines sensor clock-to-output and relative board trace skew.
set_input_delay -clock camera_pclk -clock_fall -min -0.500 [get_ports {cam_data[*] cam_href cam_vsync}]
set_input_delay -clock camera_pclk -clock_fall -max 2.000 [get_ports {cam_data[*] cam_href cam_vsync}]
set_clock_uncertainty -setup 0.250 [get_clocks camera_pclk]
set_clock_uncertainty -hold 0.100 [get_clocks camera_pclk]
# Async SCCB: bound actual pad-to-synchronizer and register-to-pad propagation,
# do not invent a synchronous SCL relationship to 100MHz FCLK.
set_max_delay -datapath_only 20.000 -from [get_ports {cam_iic_scl_io cam_iic_sda_io}]
set_max_delay -datapath_only 20.000 -from [all_registers -output_pins] -to [get_ports {cam_iic_scl_io cam_iic_sda_io}]

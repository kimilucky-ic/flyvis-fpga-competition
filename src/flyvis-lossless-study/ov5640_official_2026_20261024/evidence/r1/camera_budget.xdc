# Conditional external budget only; sensor PCLK/tCO/skew are NOT measured.
# Same 72MHz envelope used in prior R7 offline camera analysis.
create_clock -name camera_pclk -period 13.888889 [get_ports cam_pclk]
set_input_delay -clock camera_pclk -clock_fall -min -0.500 [get_ports {cam_data[*] cam_href cam_vsync}]
set_input_delay -clock camera_pclk -clock_fall -max 2.000 [get_ports {cam_data[*] cam_href cam_vsync}]
set_clock_uncertainty -setup 0.250 [get_clocks camera_pclk]
set_clock_uncertainty -hold 0.100 [get_clocks camera_pclk]

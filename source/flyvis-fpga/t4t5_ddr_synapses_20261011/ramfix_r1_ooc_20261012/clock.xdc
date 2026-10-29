# Single synchronous OOC domain. Abstract input clock; no package pin, BUFG
# location, PS FCLK or HD.CLK_SRC is established by this synthesis-only run.
create_clock -name b_clk -period 10.000 [get_ports clk]
set b_inputs [get_ports -filter {DIRECTION == IN && NAME != clk}]
set b_outputs [get_ports -filter {DIRECTION == OUT}]
set_input_delay -clock b_clk -max 2.000 $b_inputs
set_input_delay -clock b_clk -min 0.000 $b_inputs
set_output_delay -clock b_clk -max 2.000 $b_outputs
set_output_delay -clock b_clk -min 0.000 $b_outputs
# rst_n is treated as a synchronous timed input. No false-path exception.
# No invented external jitter/clock-source property or board pin constraint.

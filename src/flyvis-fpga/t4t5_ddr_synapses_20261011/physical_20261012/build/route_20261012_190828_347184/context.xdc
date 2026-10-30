# B OOC context only. Reference: phase4 bankfix routed FCLK0 BUFG, not B SoC.
# Clock/IO delay values already in the accepted synthesis DCP stay unchanged:
# b_clk=10ns; all non-clock inputs max=2/min=0; outputs max=2/min=0.
# No false/multicycle path, clock-group cut, clock latency override or IO relaxation.
set_property HD.CLK_SRC BUFGCTRL_X0Y16 [get_ports clk]

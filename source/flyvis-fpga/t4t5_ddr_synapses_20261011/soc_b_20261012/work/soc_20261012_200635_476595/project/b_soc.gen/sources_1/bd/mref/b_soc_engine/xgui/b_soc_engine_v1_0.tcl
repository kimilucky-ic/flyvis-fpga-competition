# Definitional proc to organize widgets for parameters.
proc init_gui { IPINST } {
  ipgui::add_param $IPINST -name "Component_Name"
  #Adding Page
  set Page_0 [ipgui::add_page $IPINST -name "Page 0"]
  ipgui::add_param $IPINST -name "AXI_TIMEOUT" -parent ${Page_0}
  ipgui::add_param $IPINST -name "EDGE_COUNT" -parent ${Page_0}
  ipgui::add_param $IPINST -name "H_COUNT" -parent ${Page_0}
  ipgui::add_param $IPINST -name "SOURCE_COUNT" -parent ${Page_0}
  ipgui::add_param $IPINST -name "STEP_TIMEOUT" -parent ${Page_0}
  ipgui::add_param $IPINST -name "WEIGHT_COUNT" -parent ${Page_0}


}

proc update_PARAM_VALUE.AXI_TIMEOUT { PARAM_VALUE.AXI_TIMEOUT } {
	# Procedure called to update AXI_TIMEOUT when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.AXI_TIMEOUT { PARAM_VALUE.AXI_TIMEOUT } {
	# Procedure called to validate AXI_TIMEOUT
	return true
}

proc update_PARAM_VALUE.EDGE_COUNT { PARAM_VALUE.EDGE_COUNT } {
	# Procedure called to update EDGE_COUNT when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.EDGE_COUNT { PARAM_VALUE.EDGE_COUNT } {
	# Procedure called to validate EDGE_COUNT
	return true
}

proc update_PARAM_VALUE.H_COUNT { PARAM_VALUE.H_COUNT } {
	# Procedure called to update H_COUNT when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.H_COUNT { PARAM_VALUE.H_COUNT } {
	# Procedure called to validate H_COUNT
	return true
}

proc update_PARAM_VALUE.SOURCE_COUNT { PARAM_VALUE.SOURCE_COUNT } {
	# Procedure called to update SOURCE_COUNT when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.SOURCE_COUNT { PARAM_VALUE.SOURCE_COUNT } {
	# Procedure called to validate SOURCE_COUNT
	return true
}

proc update_PARAM_VALUE.STEP_TIMEOUT { PARAM_VALUE.STEP_TIMEOUT } {
	# Procedure called to update STEP_TIMEOUT when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.STEP_TIMEOUT { PARAM_VALUE.STEP_TIMEOUT } {
	# Procedure called to validate STEP_TIMEOUT
	return true
}

proc update_PARAM_VALUE.WEIGHT_COUNT { PARAM_VALUE.WEIGHT_COUNT } {
	# Procedure called to update WEIGHT_COUNT when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.WEIGHT_COUNT { PARAM_VALUE.WEIGHT_COUNT } {
	# Procedure called to validate WEIGHT_COUNT
	return true
}


proc update_MODELPARAM_VALUE.H_COUNT { MODELPARAM_VALUE.H_COUNT PARAM_VALUE.H_COUNT } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.H_COUNT}] ${MODELPARAM_VALUE.H_COUNT}
}

proc update_MODELPARAM_VALUE.SOURCE_COUNT { MODELPARAM_VALUE.SOURCE_COUNT PARAM_VALUE.SOURCE_COUNT } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.SOURCE_COUNT}] ${MODELPARAM_VALUE.SOURCE_COUNT}
}

proc update_MODELPARAM_VALUE.EDGE_COUNT { MODELPARAM_VALUE.EDGE_COUNT PARAM_VALUE.EDGE_COUNT } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.EDGE_COUNT}] ${MODELPARAM_VALUE.EDGE_COUNT}
}

proc update_MODELPARAM_VALUE.WEIGHT_COUNT { MODELPARAM_VALUE.WEIGHT_COUNT PARAM_VALUE.WEIGHT_COUNT } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.WEIGHT_COUNT}] ${MODELPARAM_VALUE.WEIGHT_COUNT}
}

proc update_MODELPARAM_VALUE.AXI_TIMEOUT { MODELPARAM_VALUE.AXI_TIMEOUT PARAM_VALUE.AXI_TIMEOUT } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.AXI_TIMEOUT}] ${MODELPARAM_VALUE.AXI_TIMEOUT}
}

proc update_MODELPARAM_VALUE.STEP_TIMEOUT { MODELPARAM_VALUE.STEP_TIMEOUT PARAM_VALUE.STEP_TIMEOUT } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.STEP_TIMEOUT}] ${MODELPARAM_VALUE.STEP_TIMEOUT}
}


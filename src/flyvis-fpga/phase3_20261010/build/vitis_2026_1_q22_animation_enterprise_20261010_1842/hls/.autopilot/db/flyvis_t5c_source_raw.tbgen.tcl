set moduleName flyvis_t5c_source_raw
set isTopModule 1
set isCombinational 0
set isDatapathOnly 0
set isPipelined 0
set isPipelined_legacy 0
set pipeline_type none
set FunctionProtocol ap_ctrl_hs
set restart_counter_num 0
set isOneStateSeq 0
set ProfileFlag 0
set StallSigGenFlag 0
set isEnableWaveformDebug 1
set hasInterrupt 0
set DLRegFirstOffset 0
set DLRegItemOffset 0
set svuvm_can_support 1
set cdfgNum 8
set C_modelName {flyvis_t5c_source_raw}
set C_modelType { int 32 }
set ap_memory_interface_dict [dict create]
set C_modelArgList {
	{ gmem0 int 32 regular {axi_master 2}  }
	{ request int 64 regular {axi_slave 0}  }
	{ result int 64 regular {axi_slave 0}  }
}
set hasAXIMCache 0
set l_AXIML2Cache [list]
set AXIMCacheInstDict [dict create]
set C_modelArgMapList {[ 
	{ "Name" : "gmem0", "interface" : "axi_master", "bitwidth" : 32, "direction" : "READWRITE", "id_num" : 1, "bitSlice":[ {"cElement": [{"cName": "request","offset": { "type": "dynamic","port_name": "request","bundle": "control"},"direction": "READONLY"},{"cName": "result","offset": { "type": "dynamic","port_name": "result","bundle": "control"},"direction": "WRITEONLY"}]}]} , 
 	{ "Name" : "request", "interface" : "axi_slave", "bundle":"control","type":"ap_none","bitwidth" : 64, "direction" : "READONLY", "offset" : {"in":24}, "offset_end" : {"in":35}} , 
 	{ "Name" : "result", "interface" : "axi_slave", "bundle":"control","type":"ap_none","bitwidth" : 64, "direction" : "READONLY", "offset" : {"in":36}, "offset_end" : {"in":47}} , 
 	{ "Name" : "ap_return", "interface" : "axi_slave", "bundle":"control","type":"ap_none","bitwidth" : 32, "offset" : {"out":16}} ]}
# RTL Port declarations: 
set portNum 65
set portList { 
	{ ap_clk sc_in sc_logic 1 clock -1 } 
	{ ap_rst_n sc_in sc_logic 1 reset -1 active_low_sync } 
	{ m_axi_gmem0_AWVALID sc_out sc_logic 1 signal 0 } 
	{ m_axi_gmem0_AWREADY sc_in sc_logic 1 signal 0 } 
	{ m_axi_gmem0_AWADDR sc_out sc_lv 64 signal 0 } 
	{ m_axi_gmem0_AWID sc_out sc_lv 1 signal 0 } 
	{ m_axi_gmem0_AWLEN sc_out sc_lv 8 signal 0 } 
	{ m_axi_gmem0_AWSIZE sc_out sc_lv 3 signal 0 } 
	{ m_axi_gmem0_AWBURST sc_out sc_lv 2 signal 0 } 
	{ m_axi_gmem0_AWLOCK sc_out sc_lv 2 signal 0 } 
	{ m_axi_gmem0_AWCACHE sc_out sc_lv 4 signal 0 } 
	{ m_axi_gmem0_AWPROT sc_out sc_lv 3 signal 0 } 
	{ m_axi_gmem0_AWQOS sc_out sc_lv 4 signal 0 } 
	{ m_axi_gmem0_AWREGION sc_out sc_lv 4 signal 0 } 
	{ m_axi_gmem0_AWUSER sc_out sc_lv 1 signal 0 } 
	{ m_axi_gmem0_WVALID sc_out sc_logic 1 signal 0 } 
	{ m_axi_gmem0_WREADY sc_in sc_logic 1 signal 0 } 
	{ m_axi_gmem0_WDATA sc_out sc_lv 32 signal 0 } 
	{ m_axi_gmem0_WSTRB sc_out sc_lv 4 signal 0 } 
	{ m_axi_gmem0_WLAST sc_out sc_logic 1 signal 0 } 
	{ m_axi_gmem0_WID sc_out sc_lv 1 signal 0 } 
	{ m_axi_gmem0_WUSER sc_out sc_lv 1 signal 0 } 
	{ m_axi_gmem0_ARVALID sc_out sc_logic 1 signal 0 } 
	{ m_axi_gmem0_ARREADY sc_in sc_logic 1 signal 0 } 
	{ m_axi_gmem0_ARADDR sc_out sc_lv 64 signal 0 } 
	{ m_axi_gmem0_ARID sc_out sc_lv 1 signal 0 } 
	{ m_axi_gmem0_ARLEN sc_out sc_lv 8 signal 0 } 
	{ m_axi_gmem0_ARSIZE sc_out sc_lv 3 signal 0 } 
	{ m_axi_gmem0_ARBURST sc_out sc_lv 2 signal 0 } 
	{ m_axi_gmem0_ARLOCK sc_out sc_lv 2 signal 0 } 
	{ m_axi_gmem0_ARCACHE sc_out sc_lv 4 signal 0 } 
	{ m_axi_gmem0_ARPROT sc_out sc_lv 3 signal 0 } 
	{ m_axi_gmem0_ARQOS sc_out sc_lv 4 signal 0 } 
	{ m_axi_gmem0_ARREGION sc_out sc_lv 4 signal 0 } 
	{ m_axi_gmem0_ARUSER sc_out sc_lv 1 signal 0 } 
	{ m_axi_gmem0_RVALID sc_in sc_logic 1 signal 0 } 
	{ m_axi_gmem0_RREADY sc_out sc_logic 1 signal 0 } 
	{ m_axi_gmem0_RDATA sc_in sc_lv 32 signal 0 } 
	{ m_axi_gmem0_RLAST sc_in sc_logic 1 signal 0 } 
	{ m_axi_gmem0_RID sc_in sc_lv 1 signal 0 } 
	{ m_axi_gmem0_RUSER sc_in sc_lv 1 signal 0 } 
	{ m_axi_gmem0_RRESP sc_in sc_lv 2 signal 0 } 
	{ m_axi_gmem0_BVALID sc_in sc_logic 1 signal 0 } 
	{ m_axi_gmem0_BREADY sc_out sc_logic 1 signal 0 } 
	{ m_axi_gmem0_BRESP sc_in sc_lv 2 signal 0 } 
	{ m_axi_gmem0_BID sc_in sc_lv 1 signal 0 } 
	{ m_axi_gmem0_BUSER sc_in sc_lv 1 signal 0 } 
	{ s_axi_control_AWVALID sc_in sc_logic 1 signal -1 } 
	{ s_axi_control_AWREADY sc_out sc_logic 1 signal -1 } 
	{ s_axi_control_AWADDR sc_in sc_lv 6 signal -1 } 
	{ s_axi_control_WVALID sc_in sc_logic 1 signal -1 } 
	{ s_axi_control_WREADY sc_out sc_logic 1 signal -1 } 
	{ s_axi_control_WDATA sc_in sc_lv 32 signal -1 } 
	{ s_axi_control_WSTRB sc_in sc_lv 4 signal -1 } 
	{ s_axi_control_ARVALID sc_in sc_logic 1 signal -1 } 
	{ s_axi_control_ARREADY sc_out sc_logic 1 signal -1 } 
	{ s_axi_control_ARADDR sc_in sc_lv 6 signal -1 } 
	{ s_axi_control_RVALID sc_out sc_logic 1 signal -1 } 
	{ s_axi_control_RREADY sc_in sc_logic 1 signal -1 } 
	{ s_axi_control_RDATA sc_out sc_lv 32 signal -1 } 
	{ s_axi_control_RRESP sc_out sc_lv 2 signal -1 } 
	{ s_axi_control_BVALID sc_out sc_logic 1 signal -1 } 
	{ s_axi_control_BREADY sc_in sc_logic 1 signal -1 } 
	{ s_axi_control_BRESP sc_out sc_lv 2 signal -1 } 
	{ interrupt sc_out sc_logic 1 signal -1 } 
}
set NewPortList {[ 
	{ "name": "s_axi_control_AWADDR", "direction": "in", "datatype": "sc_lv", "bitwidth":6, "type": "signal", "bundle":{"name": "control", "role": "AWADDR" },"address":[{"name":"flyvis_t5c_source_raw","role":"start","value":"0","valid_bit":"0"},{"name":"flyvis_t5c_source_raw","role":"continue","value":"0","valid_bit":"4"},{"name":"flyvis_t5c_source_raw","role":"auto_start","value":"0","valid_bit":"7"},{"name":"request","role":"data","value":"24"},{"name":"result","role":"data","value":"36"}] },
	{ "name": "s_axi_control_AWVALID", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "control", "role": "AWVALID" } },
	{ "name": "s_axi_control_AWREADY", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "control", "role": "AWREADY" } },
	{ "name": "s_axi_control_WVALID", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "control", "role": "WVALID" } },
	{ "name": "s_axi_control_WREADY", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "control", "role": "WREADY" } },
	{ "name": "s_axi_control_WDATA", "direction": "in", "datatype": "sc_lv", "bitwidth":32, "type": "signal", "bundle":{"name": "control", "role": "WDATA" } },
	{ "name": "s_axi_control_WSTRB", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "control", "role": "WSTRB" } },
	{ "name": "s_axi_control_ARADDR", "direction": "in", "datatype": "sc_lv", "bitwidth":6, "type": "signal", "bundle":{"name": "control", "role": "ARADDR" },"address":[{"name":"flyvis_t5c_source_raw","role":"start","value":"0","valid_bit":"0"},{"name":"flyvis_t5c_source_raw","role":"done","value":"0","valid_bit":"1"},{"name":"flyvis_t5c_source_raw","role":"idle","value":"0","valid_bit":"2"},{"name":"flyvis_t5c_source_raw","role":"ready","value":"0","valid_bit":"3"},{"name":"flyvis_t5c_source_raw","role":"auto_start","value":"0","valid_bit":"7"},{"name":"return","role":"data","value":"16"}] },
	{ "name": "s_axi_control_ARVALID", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "control", "role": "ARVALID" } },
	{ "name": "s_axi_control_ARREADY", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "control", "role": "ARREADY" } },
	{ "name": "s_axi_control_RVALID", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "control", "role": "RVALID" } },
	{ "name": "s_axi_control_RREADY", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "control", "role": "RREADY" } },
	{ "name": "s_axi_control_RDATA", "direction": "out", "datatype": "sc_lv", "bitwidth":32, "type": "signal", "bundle":{"name": "control", "role": "RDATA" } },
	{ "name": "s_axi_control_RRESP", "direction": "out", "datatype": "sc_lv", "bitwidth":2, "type": "signal", "bundle":{"name": "control", "role": "RRESP" } },
	{ "name": "s_axi_control_BVALID", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "control", "role": "BVALID" } },
	{ "name": "s_axi_control_BREADY", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "control", "role": "BREADY" } },
	{ "name": "s_axi_control_BRESP", "direction": "out", "datatype": "sc_lv", "bitwidth":2, "type": "signal", "bundle":{"name": "control", "role": "BRESP" } },
	{ "name": "interrupt", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "control", "role": "interrupt" } }, 
 	{ "name": "ap_clk", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "clock", "bundle":{"name": "ap_clk", "role": "default" }} , 
 	{ "name": "ap_rst_n", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "reset", "bundle":{"name": "ap_rst_n", "role": "default" }} , 
 	{ "name": "m_axi_gmem0_AWVALID", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "AWVALID" }} , 
 	{ "name": "m_axi_gmem0_AWREADY", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "AWREADY" }} , 
 	{ "name": "m_axi_gmem0_AWADDR", "direction": "out", "datatype": "sc_lv", "bitwidth":64, "type": "signal", "bundle":{"name": "gmem0", "role": "AWADDR" }} , 
 	{ "name": "m_axi_gmem0_AWID", "direction": "out", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "AWID" }} , 
 	{ "name": "m_axi_gmem0_AWLEN", "direction": "out", "datatype": "sc_lv", "bitwidth":8, "type": "signal", "bundle":{"name": "gmem0", "role": "AWLEN" }} , 
 	{ "name": "m_axi_gmem0_AWSIZE", "direction": "out", "datatype": "sc_lv", "bitwidth":3, "type": "signal", "bundle":{"name": "gmem0", "role": "AWSIZE" }} , 
 	{ "name": "m_axi_gmem0_AWBURST", "direction": "out", "datatype": "sc_lv", "bitwidth":2, "type": "signal", "bundle":{"name": "gmem0", "role": "AWBURST" }} , 
 	{ "name": "m_axi_gmem0_AWLOCK", "direction": "out", "datatype": "sc_lv", "bitwidth":2, "type": "signal", "bundle":{"name": "gmem0", "role": "AWLOCK" }} , 
 	{ "name": "m_axi_gmem0_AWCACHE", "direction": "out", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "gmem0", "role": "AWCACHE" }} , 
 	{ "name": "m_axi_gmem0_AWPROT", "direction": "out", "datatype": "sc_lv", "bitwidth":3, "type": "signal", "bundle":{"name": "gmem0", "role": "AWPROT" }} , 
 	{ "name": "m_axi_gmem0_AWQOS", "direction": "out", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "gmem0", "role": "AWQOS" }} , 
 	{ "name": "m_axi_gmem0_AWREGION", "direction": "out", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "gmem0", "role": "AWREGION" }} , 
 	{ "name": "m_axi_gmem0_AWUSER", "direction": "out", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "AWUSER" }} , 
 	{ "name": "m_axi_gmem0_WVALID", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "WVALID" }} , 
 	{ "name": "m_axi_gmem0_WREADY", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "WREADY" }} , 
 	{ "name": "m_axi_gmem0_WDATA", "direction": "out", "datatype": "sc_lv", "bitwidth":32, "type": "signal", "bundle":{"name": "gmem0", "role": "WDATA" }} , 
 	{ "name": "m_axi_gmem0_WSTRB", "direction": "out", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "gmem0", "role": "WSTRB" }} , 
 	{ "name": "m_axi_gmem0_WLAST", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "WLAST" }} , 
 	{ "name": "m_axi_gmem0_WID", "direction": "out", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "WID" }} , 
 	{ "name": "m_axi_gmem0_WUSER", "direction": "out", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "WUSER" }} , 
 	{ "name": "m_axi_gmem0_ARVALID", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "ARVALID" }} , 
 	{ "name": "m_axi_gmem0_ARREADY", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "ARREADY" }} , 
 	{ "name": "m_axi_gmem0_ARADDR", "direction": "out", "datatype": "sc_lv", "bitwidth":64, "type": "signal", "bundle":{"name": "gmem0", "role": "ARADDR" }} , 
 	{ "name": "m_axi_gmem0_ARID", "direction": "out", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "ARID" }} , 
 	{ "name": "m_axi_gmem0_ARLEN", "direction": "out", "datatype": "sc_lv", "bitwidth":8, "type": "signal", "bundle":{"name": "gmem0", "role": "ARLEN" }} , 
 	{ "name": "m_axi_gmem0_ARSIZE", "direction": "out", "datatype": "sc_lv", "bitwidth":3, "type": "signal", "bundle":{"name": "gmem0", "role": "ARSIZE" }} , 
 	{ "name": "m_axi_gmem0_ARBURST", "direction": "out", "datatype": "sc_lv", "bitwidth":2, "type": "signal", "bundle":{"name": "gmem0", "role": "ARBURST" }} , 
 	{ "name": "m_axi_gmem0_ARLOCK", "direction": "out", "datatype": "sc_lv", "bitwidth":2, "type": "signal", "bundle":{"name": "gmem0", "role": "ARLOCK" }} , 
 	{ "name": "m_axi_gmem0_ARCACHE", "direction": "out", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "gmem0", "role": "ARCACHE" }} , 
 	{ "name": "m_axi_gmem0_ARPROT", "direction": "out", "datatype": "sc_lv", "bitwidth":3, "type": "signal", "bundle":{"name": "gmem0", "role": "ARPROT" }} , 
 	{ "name": "m_axi_gmem0_ARQOS", "direction": "out", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "gmem0", "role": "ARQOS" }} , 
 	{ "name": "m_axi_gmem0_ARREGION", "direction": "out", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "gmem0", "role": "ARREGION" }} , 
 	{ "name": "m_axi_gmem0_ARUSER", "direction": "out", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "ARUSER" }} , 
 	{ "name": "m_axi_gmem0_RVALID", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "RVALID" }} , 
 	{ "name": "m_axi_gmem0_RREADY", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "RREADY" }} , 
 	{ "name": "m_axi_gmem0_RDATA", "direction": "in", "datatype": "sc_lv", "bitwidth":32, "type": "signal", "bundle":{"name": "gmem0", "role": "RDATA" }} , 
 	{ "name": "m_axi_gmem0_RLAST", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "RLAST" }} , 
 	{ "name": "m_axi_gmem0_RID", "direction": "in", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "RID" }} , 
 	{ "name": "m_axi_gmem0_RUSER", "direction": "in", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "RUSER" }} , 
 	{ "name": "m_axi_gmem0_RRESP", "direction": "in", "datatype": "sc_lv", "bitwidth":2, "type": "signal", "bundle":{"name": "gmem0", "role": "RRESP" }} , 
 	{ "name": "m_axi_gmem0_BVALID", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "BVALID" }} , 
 	{ "name": "m_axi_gmem0_BREADY", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "BREADY" }} , 
 	{ "name": "m_axi_gmem0_BRESP", "direction": "in", "datatype": "sc_lv", "bitwidth":2, "type": "signal", "bundle":{"name": "gmem0", "role": "BRESP" }} , 
 	{ "name": "m_axi_gmem0_BID", "direction": "in", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "BID" }} , 
 	{ "name": "m_axi_gmem0_BUSER", "direction": "in", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "BUSER" }}  ]}

set ArgLastReadFirstWriteLatency {
	flyvis_t5c_source_raw {
		gmem0 {Type IO LastRead 18 FirstWrite -1}
		request {Type I LastRead 0 FirstWrite -1}
		result {Type I LastRead 0 FirstWrite -1}
		FLYVIS_EDGE_SRC {Type I LastRead -1 FirstWrite -1}
		FLYVIS_EDGE_WEIGHT_Q20 {Type I LastRead -1 FirstWrite -1}
		FLYVIS_EDGE_DST {Type I LastRead -1 FirstWrite -1}
		FLYVIS_BIAS_Q22 {Type I LastRead -1 FirstWrite -1}
		FLYVIS_INVTau_Q22 {Type I LastRead -1 FirstWrite -1}}
	flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_67_1 {
		gmem0 {Type I LastRead 1 FirstWrite -1}
		boundary {Type O LastRead -1 FirstWrite 2}
		sext_ln67 {Type I LastRead 0 FirstWrite -1}
		x_h_66_out {Type O LastRead -1 FirstWrite 1}
		x_h_65_out {Type O LastRead -1 FirstWrite 1}
		x_h_64_out {Type O LastRead -1 FirstWrite 1}
		x_h_63_out {Type O LastRead -1 FirstWrite 1}
		x_h_62_out {Type O LastRead -1 FirstWrite 1}
		x_h_61_out {Type O LastRead -1 FirstWrite 1}
		x_h_60_out {Type O LastRead -1 FirstWrite 1}
		x_h_59_out {Type O LastRead -1 FirstWrite 1}
		x_h_58_out {Type O LastRead -1 FirstWrite 1}
		x_h_57_out {Type O LastRead -1 FirstWrite 1}
		x_h_56_out {Type O LastRead -1 FirstWrite 1}
		x_h_55_out {Type O LastRead -1 FirstWrite 1}
		x_h_54_out {Type O LastRead -1 FirstWrite 1}
		x_h_53_out {Type O LastRead -1 FirstWrite 1}
		x_h_52_out {Type O LastRead -1 FirstWrite 1}
		x_h_51_out {Type O LastRead -1 FirstWrite 1}
		x_h_50_out {Type O LastRead -1 FirstWrite 1}
		x_h_49_out {Type O LastRead -1 FirstWrite 1}
		x_h_48_out {Type O LastRead -1 FirstWrite 1}
		x_h_47_out {Type O LastRead -1 FirstWrite 1}
		x_h_46_out {Type O LastRead -1 FirstWrite 1}
		x_h_45_out {Type O LastRead -1 FirstWrite 1}
		x_h_44_out {Type O LastRead -1 FirstWrite 1}
		x_h_43_out {Type O LastRead -1 FirstWrite 1}
		x_h_42_out {Type O LastRead -1 FirstWrite 1}
		x_h_41_out {Type O LastRead -1 FirstWrite 1}
		x_h_40_out {Type O LastRead -1 FirstWrite 1}
		x_h_39_out {Type O LastRead -1 FirstWrite 1}
		x_h_38_out {Type O LastRead -1 FirstWrite 1}
		x_h_37_out {Type O LastRead -1 FirstWrite 1}
		x_h_36_out {Type O LastRead -1 FirstWrite 1}
		x_h_35_out {Type O LastRead -1 FirstWrite 1}
		x_h_34_out {Type O LastRead -1 FirstWrite 1}
		x_h_33_out {Type O LastRead -1 FirstWrite 1}
		x_h_32_out {Type O LastRead -1 FirstWrite 1}
		x_h_31_out {Type O LastRead -1 FirstWrite 1}
		x_h_30_out {Type O LastRead -1 FirstWrite 1}
		x_h_29_out {Type O LastRead -1 FirstWrite 1}
		x_h_28_out {Type O LastRead -1 FirstWrite 1}
		x_h_27_out {Type O LastRead -1 FirstWrite 1}
		x_h_26_out {Type O LastRead -1 FirstWrite 1}
		x_h_25_out {Type O LastRead -1 FirstWrite 1}
		x_h_24_out {Type O LastRead -1 FirstWrite 1}
		x_h_23_out {Type O LastRead -1 FirstWrite 1}
		x_h_22_out {Type O LastRead -1 FirstWrite 1}
		x_h_21_out {Type O LastRead -1 FirstWrite 1}
		x_h_20_out {Type O LastRead -1 FirstWrite 1}
		x_h_19_out {Type O LastRead -1 FirstWrite 1}
		x_h_18_out {Type O LastRead -1 FirstWrite 1}
		x_h_17_out {Type O LastRead -1 FirstWrite 1}
		x_h_16_out {Type O LastRead -1 FirstWrite 1}
		x_h_15_out {Type O LastRead -1 FirstWrite 1}
		x_h_14_out {Type O LastRead -1 FirstWrite 1}
		x_h_13_out {Type O LastRead -1 FirstWrite 1}
		x_h_12_out {Type O LastRead -1 FirstWrite 1}
		x_h_11_out {Type O LastRead -1 FirstWrite 1}
		x_h_10_out {Type O LastRead -1 FirstWrite 1}
		x_h_9_out {Type O LastRead -1 FirstWrite 1}
		x_h_8_out {Type O LastRead -1 FirstWrite 1}
		x_h_7_out {Type O LastRead -1 FirstWrite 1}
		x_h_6_out {Type O LastRead -1 FirstWrite 1}
		x_h_5_out {Type O LastRead -1 FirstWrite 1}
		x_h_4_out {Type O LastRead -1 FirstWrite 1}
		x_h_3_out {Type O LastRead -1 FirstWrite 1}
		x_h_2_out {Type O LastRead -1 FirstWrite 1}
		x_h_1_out {Type O LastRead -1 FirstWrite 1}
		x_h_out {Type O LastRead -1 FirstWrite 1}
		old_h_66_out {Type O LastRead -1 FirstWrite 1}
		old_h_65_out {Type O LastRead -1 FirstWrite 1}
		old_h_64_out {Type O LastRead -1 FirstWrite 1}
		old_h_63_out {Type O LastRead -1 FirstWrite 1}
		old_h_62_out {Type O LastRead -1 FirstWrite 1}
		old_h_61_out {Type O LastRead -1 FirstWrite 1}
		old_h_60_out {Type O LastRead -1 FirstWrite 1}
		old_h_59_out {Type O LastRead -1 FirstWrite 1}
		old_h_58_out {Type O LastRead -1 FirstWrite 1}
		old_h_57_out {Type O LastRead -1 FirstWrite 1}
		old_h_56_out {Type O LastRead -1 FirstWrite 1}
		old_h_55_out {Type O LastRead -1 FirstWrite 1}
		old_h_54_out {Type O LastRead -1 FirstWrite 1}
		old_h_53_out {Type O LastRead -1 FirstWrite 1}
		old_h_52_out {Type O LastRead -1 FirstWrite 1}
		old_h_51_out {Type O LastRead -1 FirstWrite 1}
		old_h_50_out {Type O LastRead -1 FirstWrite 1}
		old_h_49_out {Type O LastRead -1 FirstWrite 1}
		old_h_48_out {Type O LastRead -1 FirstWrite 1}
		old_h_47_out {Type O LastRead -1 FirstWrite 1}
		old_h_46_out {Type O LastRead -1 FirstWrite 1}
		old_h_45_out {Type O LastRead -1 FirstWrite 1}
		old_h_44_out {Type O LastRead -1 FirstWrite 1}
		old_h_43_out {Type O LastRead -1 FirstWrite 1}
		old_h_42_out {Type O LastRead -1 FirstWrite 1}
		old_h_41_out {Type O LastRead -1 FirstWrite 1}
		old_h_40_out {Type O LastRead -1 FirstWrite 1}
		old_h_39_out {Type O LastRead -1 FirstWrite 1}
		old_h_38_out {Type O LastRead -1 FirstWrite 1}
		old_h_37_out {Type O LastRead -1 FirstWrite 1}
		old_h_36_out {Type O LastRead -1 FirstWrite 1}
		old_h_35_out {Type O LastRead -1 FirstWrite 1}
		old_h_34_out {Type O LastRead -1 FirstWrite 1}
		old_h_33_out {Type O LastRead -1 FirstWrite 1}
		old_h_32_out {Type O LastRead -1 FirstWrite 1}
		old_h_31_out {Type O LastRead -1 FirstWrite 1}
		old_h_30_out {Type O LastRead -1 FirstWrite 1}
		old_h_29_out {Type O LastRead -1 FirstWrite 1}
		old_h_28_out {Type O LastRead -1 FirstWrite 1}
		old_h_27_out {Type O LastRead -1 FirstWrite 1}
		old_h_26_out {Type O LastRead -1 FirstWrite 1}
		old_h_25_out {Type O LastRead -1 FirstWrite 1}
		old_h_24_out {Type O LastRead -1 FirstWrite 1}
		old_h_23_out {Type O LastRead -1 FirstWrite 1}
		old_h_22_out {Type O LastRead -1 FirstWrite 1}
		old_h_21_out {Type O LastRead -1 FirstWrite 1}
		old_h_20_out {Type O LastRead -1 FirstWrite 1}
		old_h_19_out {Type O LastRead -1 FirstWrite 1}
		old_h_18_out {Type O LastRead -1 FirstWrite 1}
		old_h_17_out {Type O LastRead -1 FirstWrite 1}
		old_h_16_out {Type O LastRead -1 FirstWrite 1}
		old_h_15_out {Type O LastRead -1 FirstWrite 1}
		old_h_14_out {Type O LastRead -1 FirstWrite 1}
		old_h_13_out {Type O LastRead -1 FirstWrite 1}
		old_h_12_out {Type O LastRead -1 FirstWrite 1}
		old_h_11_out {Type O LastRead -1 FirstWrite 1}
		old_h_10_out {Type O LastRead -1 FirstWrite 1}
		old_h_9_out {Type O LastRead -1 FirstWrite 1}
		old_h_8_out {Type O LastRead -1 FirstWrite 1}
		old_h_7_out {Type O LastRead -1 FirstWrite 1}
		old_h_6_out {Type O LastRead -1 FirstWrite 1}
		old_h_5_out {Type O LastRead -1 FirstWrite 1}
		old_h_4_out {Type O LastRead -1 FirstWrite 1}
		old_h_3_out {Type O LastRead -1 FirstWrite 1}
		old_h_2_out {Type O LastRead -1 FirstWrite 1}
		old_h_1_out {Type O LastRead -1 FirstWrite 1}
		old_h_out {Type O LastRead -1 FirstWrite 1}
		status_out {Type O LastRead -1 FirstWrite 1}}
	flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_85_2 {
		candidate_66_out {Type O LastRead -1 FirstWrite 0}
		candidate_65_out {Type O LastRead -1 FirstWrite 0}
		candidate_64_out {Type O LastRead -1 FirstWrite 0}
		candidate_63_out {Type O LastRead -1 FirstWrite 0}
		candidate_62_out {Type O LastRead -1 FirstWrite 0}
		candidate_61_out {Type O LastRead -1 FirstWrite 0}
		candidate_60_out {Type O LastRead -1 FirstWrite 0}
		candidate_59_out {Type O LastRead -1 FirstWrite 0}
		candidate_58_out {Type O LastRead -1 FirstWrite 0}
		candidate_57_out {Type O LastRead -1 FirstWrite 0}
		candidate_56_out {Type O LastRead -1 FirstWrite 0}
		candidate_55_out {Type O LastRead -1 FirstWrite 0}
		candidate_54_out {Type O LastRead -1 FirstWrite 0}
		candidate_53_out {Type O LastRead -1 FirstWrite 0}
		candidate_52_out {Type O LastRead -1 FirstWrite 0}
		candidate_51_out {Type O LastRead -1 FirstWrite 0}
		candidate_50_out {Type O LastRead -1 FirstWrite 0}
		candidate_49_out {Type O LastRead -1 FirstWrite 0}
		candidate_48_out {Type O LastRead -1 FirstWrite 0}
		candidate_47_out {Type O LastRead -1 FirstWrite 0}
		candidate_46_out {Type O LastRead -1 FirstWrite 0}
		candidate_45_out {Type O LastRead -1 FirstWrite 0}
		candidate_44_out {Type O LastRead -1 FirstWrite 0}
		candidate_43_out {Type O LastRead -1 FirstWrite 0}
		candidate_42_out {Type O LastRead -1 FirstWrite 0}
		candidate_41_out {Type O LastRead -1 FirstWrite 0}
		candidate_40_out {Type O LastRead -1 FirstWrite 0}
		candidate_39_out {Type O LastRead -1 FirstWrite 0}
		candidate_38_out {Type O LastRead -1 FirstWrite 0}
		candidate_37_out {Type O LastRead -1 FirstWrite 0}
		candidate_36_out {Type O LastRead -1 FirstWrite 0}
		candidate_35_out {Type O LastRead -1 FirstWrite 0}
		candidate_34_out {Type O LastRead -1 FirstWrite 0}
		candidate_33_out {Type O LastRead -1 FirstWrite 0}
		candidate_32_out {Type O LastRead -1 FirstWrite 0}
		candidate_31_out {Type O LastRead -1 FirstWrite 0}
		candidate_30_out {Type O LastRead -1 FirstWrite 0}
		candidate_29_out {Type O LastRead -1 FirstWrite 0}
		candidate_28_out {Type O LastRead -1 FirstWrite 0}
		candidate_27_out {Type O LastRead -1 FirstWrite 0}
		candidate_26_out {Type O LastRead -1 FirstWrite 0}
		candidate_25_out {Type O LastRead -1 FirstWrite 0}
		candidate_24_out {Type O LastRead -1 FirstWrite 0}
		candidate_23_out {Type O LastRead -1 FirstWrite 0}
		candidate_22_out {Type O LastRead -1 FirstWrite 0}
		candidate_21_out {Type O LastRead -1 FirstWrite 0}
		candidate_20_out {Type O LastRead -1 FirstWrite 0}
		candidate_19_out {Type O LastRead -1 FirstWrite 0}
		candidate_18_out {Type O LastRead -1 FirstWrite 0}
		candidate_17_out {Type O LastRead -1 FirstWrite 0}
		candidate_16_out {Type O LastRead -1 FirstWrite 0}
		candidate_15_out {Type O LastRead -1 FirstWrite 0}
		candidate_14_out {Type O LastRead -1 FirstWrite 0}
		candidate_13_out {Type O LastRead -1 FirstWrite 0}
		candidate_12_out {Type O LastRead -1 FirstWrite 0}
		candidate_11_out {Type O LastRead -1 FirstWrite 0}
		candidate_10_out {Type O LastRead -1 FirstWrite 0}
		candidate_9_out {Type O LastRead -1 FirstWrite 0}
		candidate_8_out {Type O LastRead -1 FirstWrite 0}
		candidate_7_out {Type O LastRead -1 FirstWrite 0}
		candidate_6_out {Type O LastRead -1 FirstWrite 0}
		candidate_5_out {Type O LastRead -1 FirstWrite 0}
		candidate_4_out {Type O LastRead -1 FirstWrite 0}
		candidate_3_out {Type O LastRead -1 FirstWrite 0}
		candidate_2_out {Type O LastRead -1 FirstWrite 0}
		candidate_1_out {Type O LastRead -1 FirstWrite 0}
		candidate_out {Type O LastRead -1 FirstWrite 0}
		chemical_66_out {Type O LastRead -1 FirstWrite 0}
		chemical_65_out {Type O LastRead -1 FirstWrite 0}
		chemical_64_out {Type O LastRead -1 FirstWrite 0}
		chemical_63_out {Type O LastRead -1 FirstWrite 0}
		chemical_62_out {Type O LastRead -1 FirstWrite 0}
		chemical_61_out {Type O LastRead -1 FirstWrite 0}
		chemical_60_out {Type O LastRead -1 FirstWrite 0}
		chemical_59_out {Type O LastRead -1 FirstWrite 0}
		chemical_58_out {Type O LastRead -1 FirstWrite 0}
		chemical_57_out {Type O LastRead -1 FirstWrite 0}
		chemical_56_out {Type O LastRead -1 FirstWrite 0}
		chemical_55_out {Type O LastRead -1 FirstWrite 0}
		chemical_54_out {Type O LastRead -1 FirstWrite 0}
		chemical_53_out {Type O LastRead -1 FirstWrite 0}
		chemical_52_out {Type O LastRead -1 FirstWrite 0}
		chemical_51_out {Type O LastRead -1 FirstWrite 0}
		chemical_50_out {Type O LastRead -1 FirstWrite 0}
		chemical_49_out {Type O LastRead -1 FirstWrite 0}
		chemical_48_out {Type O LastRead -1 FirstWrite 0}
		chemical_47_out {Type O LastRead -1 FirstWrite 0}
		chemical_46_out {Type O LastRead -1 FirstWrite 0}
		chemical_45_out {Type O LastRead -1 FirstWrite 0}
		chemical_44_out {Type O LastRead -1 FirstWrite 0}
		chemical_43_out {Type O LastRead -1 FirstWrite 0}
		chemical_42_out {Type O LastRead -1 FirstWrite 0}
		chemical_41_out {Type O LastRead -1 FirstWrite 0}
		chemical_40_out {Type O LastRead -1 FirstWrite 0}
		chemical_39_out {Type O LastRead -1 FirstWrite 0}
		chemical_38_out {Type O LastRead -1 FirstWrite 0}
		chemical_37_out {Type O LastRead -1 FirstWrite 0}
		chemical_36_out {Type O LastRead -1 FirstWrite 0}
		chemical_35_out {Type O LastRead -1 FirstWrite 0}
		chemical_34_out {Type O LastRead -1 FirstWrite 0}
		chemical_33_out {Type O LastRead -1 FirstWrite 0}
		chemical_32_out {Type O LastRead -1 FirstWrite 0}
		chemical_31_out {Type O LastRead -1 FirstWrite 0}
		chemical_30_out {Type O LastRead -1 FirstWrite 0}
		chemical_29_out {Type O LastRead -1 FirstWrite 0}
		chemical_28_out {Type O LastRead -1 FirstWrite 0}
		chemical_27_out {Type O LastRead -1 FirstWrite 0}
		chemical_26_out {Type O LastRead -1 FirstWrite 0}
		chemical_25_out {Type O LastRead -1 FirstWrite 0}
		chemical_24_out {Type O LastRead -1 FirstWrite 0}
		chemical_23_out {Type O LastRead -1 FirstWrite 0}
		chemical_22_out {Type O LastRead -1 FirstWrite 0}
		chemical_21_out {Type O LastRead -1 FirstWrite 0}
		chemical_20_out {Type O LastRead -1 FirstWrite 0}
		chemical_19_out {Type O LastRead -1 FirstWrite 0}
		chemical_18_out {Type O LastRead -1 FirstWrite 0}
		chemical_17_out {Type O LastRead -1 FirstWrite 0}
		chemical_16_out {Type O LastRead -1 FirstWrite 0}
		chemical_15_out {Type O LastRead -1 FirstWrite 0}
		chemical_14_out {Type O LastRead -1 FirstWrite 0}
		chemical_13_out {Type O LastRead -1 FirstWrite 0}
		chemical_12_out {Type O LastRead -1 FirstWrite 0}
		chemical_11_out {Type O LastRead -1 FirstWrite 0}
		chemical_10_out {Type O LastRead -1 FirstWrite 0}
		chemical_9_out {Type O LastRead -1 FirstWrite 0}
		chemical_8_out {Type O LastRead -1 FirstWrite 0}
		chemical_7_out {Type O LastRead -1 FirstWrite 0}
		chemical_6_out {Type O LastRead -1 FirstWrite 0}
		chemical_5_out {Type O LastRead -1 FirstWrite 0}
		chemical_4_out {Type O LastRead -1 FirstWrite 0}
		chemical_3_out {Type O LastRead -1 FirstWrite 0}
		chemical_2_out {Type O LastRead -1 FirstWrite 0}
		chemical_1_out {Type O LastRead -1 FirstWrite 0}
		chemical_out {Type O LastRead -1 FirstWrite 0}}
	flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_93_3 {
		chemical_66_reload {Type I LastRead 0 FirstWrite -1}
		chemical_65_reload {Type I LastRead 0 FirstWrite -1}
		chemical_64_reload {Type I LastRead 0 FirstWrite -1}
		chemical_63_reload {Type I LastRead 0 FirstWrite -1}
		chemical_62_reload {Type I LastRead 0 FirstWrite -1}
		chemical_61_reload {Type I LastRead 0 FirstWrite -1}
		chemical_60_reload {Type I LastRead 0 FirstWrite -1}
		chemical_59_reload {Type I LastRead 0 FirstWrite -1}
		chemical_58_reload {Type I LastRead 0 FirstWrite -1}
		chemical_57_reload {Type I LastRead 0 FirstWrite -1}
		chemical_56_reload {Type I LastRead 0 FirstWrite -1}
		chemical_55_reload {Type I LastRead 0 FirstWrite -1}
		chemical_54_reload {Type I LastRead 0 FirstWrite -1}
		chemical_53_reload {Type I LastRead 0 FirstWrite -1}
		chemical_52_reload {Type I LastRead 0 FirstWrite -1}
		chemical_51_reload {Type I LastRead 0 FirstWrite -1}
		chemical_50_reload {Type I LastRead 0 FirstWrite -1}
		chemical_49_reload {Type I LastRead 0 FirstWrite -1}
		chemical_48_reload {Type I LastRead 0 FirstWrite -1}
		chemical_47_reload {Type I LastRead 0 FirstWrite -1}
		chemical_46_reload {Type I LastRead 0 FirstWrite -1}
		chemical_45_reload {Type I LastRead 0 FirstWrite -1}
		chemical_44_reload {Type I LastRead 0 FirstWrite -1}
		chemical_43_reload {Type I LastRead 0 FirstWrite -1}
		chemical_42_reload {Type I LastRead 0 FirstWrite -1}
		chemical_41_reload {Type I LastRead 0 FirstWrite -1}
		chemical_40_reload {Type I LastRead 0 FirstWrite -1}
		chemical_39_reload {Type I LastRead 0 FirstWrite -1}
		chemical_38_reload {Type I LastRead 0 FirstWrite -1}
		chemical_37_reload {Type I LastRead 0 FirstWrite -1}
		chemical_36_reload {Type I LastRead 0 FirstWrite -1}
		chemical_35_reload {Type I LastRead 0 FirstWrite -1}
		chemical_34_reload {Type I LastRead 0 FirstWrite -1}
		chemical_33_reload {Type I LastRead 0 FirstWrite -1}
		chemical_32_reload {Type I LastRead 0 FirstWrite -1}
		chemical_31_reload {Type I LastRead 0 FirstWrite -1}
		chemical_30_reload {Type I LastRead 0 FirstWrite -1}
		chemical_29_reload {Type I LastRead 0 FirstWrite -1}
		chemical_28_reload {Type I LastRead 0 FirstWrite -1}
		chemical_27_reload {Type I LastRead 0 FirstWrite -1}
		chemical_26_reload {Type I LastRead 0 FirstWrite -1}
		chemical_25_reload {Type I LastRead 0 FirstWrite -1}
		chemical_24_reload {Type I LastRead 0 FirstWrite -1}
		chemical_23_reload {Type I LastRead 0 FirstWrite -1}
		chemical_22_reload {Type I LastRead 0 FirstWrite -1}
		chemical_21_reload {Type I LastRead 0 FirstWrite -1}
		chemical_20_reload {Type I LastRead 0 FirstWrite -1}
		chemical_19_reload {Type I LastRead 0 FirstWrite -1}
		chemical_18_reload {Type I LastRead 0 FirstWrite -1}
		chemical_17_reload {Type I LastRead 0 FirstWrite -1}
		chemical_16_reload {Type I LastRead 0 FirstWrite -1}
		chemical_15_reload {Type I LastRead 0 FirstWrite -1}
		chemical_14_reload {Type I LastRead 0 FirstWrite -1}
		chemical_13_reload {Type I LastRead 0 FirstWrite -1}
		chemical_12_reload {Type I LastRead 0 FirstWrite -1}
		chemical_11_reload {Type I LastRead 0 FirstWrite -1}
		chemical_10_reload {Type I LastRead 0 FirstWrite -1}
		chemical_9_reload {Type I LastRead 0 FirstWrite -1}
		chemical_8_reload {Type I LastRead 0 FirstWrite -1}
		chemical_7_reload {Type I LastRead 0 FirstWrite -1}
		chemical_6_reload {Type I LastRead 0 FirstWrite -1}
		chemical_5_reload {Type I LastRead 0 FirstWrite -1}
		chemical_4_reload {Type I LastRead 0 FirstWrite -1}
		chemical_3_reload {Type I LastRead 0 FirstWrite -1}
		chemical_2_reload {Type I LastRead 0 FirstWrite -1}
		chemical_1_reload {Type I LastRead 0 FirstWrite -1}
		chemical_reload {Type I LastRead 0 FirstWrite -1}
		old_h_reload {Type I LastRead 0 FirstWrite -1}
		old_h_1_reload {Type I LastRead 0 FirstWrite -1}
		old_h_2_reload {Type I LastRead 0 FirstWrite -1}
		old_h_3_reload {Type I LastRead 0 FirstWrite -1}
		old_h_4_reload {Type I LastRead 0 FirstWrite -1}
		old_h_5_reload {Type I LastRead 0 FirstWrite -1}
		old_h_6_reload {Type I LastRead 0 FirstWrite -1}
		old_h_7_reload {Type I LastRead 0 FirstWrite -1}
		old_h_8_reload {Type I LastRead 0 FirstWrite -1}
		old_h_9_reload {Type I LastRead 0 FirstWrite -1}
		old_h_10_reload {Type I LastRead 0 FirstWrite -1}
		old_h_11_reload {Type I LastRead 0 FirstWrite -1}
		old_h_12_reload {Type I LastRead 0 FirstWrite -1}
		old_h_13_reload {Type I LastRead 0 FirstWrite -1}
		old_h_14_reload {Type I LastRead 0 FirstWrite -1}
		old_h_15_reload {Type I LastRead 0 FirstWrite -1}
		old_h_16_reload {Type I LastRead 0 FirstWrite -1}
		old_h_17_reload {Type I LastRead 0 FirstWrite -1}
		old_h_18_reload {Type I LastRead 0 FirstWrite -1}
		old_h_19_reload {Type I LastRead 0 FirstWrite -1}
		old_h_20_reload {Type I LastRead 0 FirstWrite -1}
		old_h_21_reload {Type I LastRead 0 FirstWrite -1}
		old_h_22_reload {Type I LastRead 0 FirstWrite -1}
		old_h_23_reload {Type I LastRead 0 FirstWrite -1}
		old_h_24_reload {Type I LastRead 0 FirstWrite -1}
		old_h_25_reload {Type I LastRead 0 FirstWrite -1}
		old_h_26_reload {Type I LastRead 0 FirstWrite -1}
		old_h_27_reload {Type I LastRead 0 FirstWrite -1}
		old_h_28_reload {Type I LastRead 0 FirstWrite -1}
		old_h_29_reload {Type I LastRead 0 FirstWrite -1}
		old_h_30_reload {Type I LastRead 0 FirstWrite -1}
		old_h_31_reload {Type I LastRead 0 FirstWrite -1}
		old_h_32_reload {Type I LastRead 0 FirstWrite -1}
		old_h_33_reload {Type I LastRead 0 FirstWrite -1}
		old_h_34_reload {Type I LastRead 0 FirstWrite -1}
		old_h_35_reload {Type I LastRead 0 FirstWrite -1}
		old_h_36_reload {Type I LastRead 0 FirstWrite -1}
		old_h_37_reload {Type I LastRead 0 FirstWrite -1}
		old_h_38_reload {Type I LastRead 0 FirstWrite -1}
		old_h_39_reload {Type I LastRead 0 FirstWrite -1}
		old_h_40_reload {Type I LastRead 0 FirstWrite -1}
		old_h_41_reload {Type I LastRead 0 FirstWrite -1}
		old_h_42_reload {Type I LastRead 0 FirstWrite -1}
		old_h_43_reload {Type I LastRead 0 FirstWrite -1}
		old_h_44_reload {Type I LastRead 0 FirstWrite -1}
		old_h_45_reload {Type I LastRead 0 FirstWrite -1}
		old_h_46_reload {Type I LastRead 0 FirstWrite -1}
		old_h_47_reload {Type I LastRead 0 FirstWrite -1}
		old_h_48_reload {Type I LastRead 0 FirstWrite -1}
		old_h_49_reload {Type I LastRead 0 FirstWrite -1}
		old_h_50_reload {Type I LastRead 0 FirstWrite -1}
		old_h_51_reload {Type I LastRead 0 FirstWrite -1}
		old_h_52_reload {Type I LastRead 0 FirstWrite -1}
		old_h_53_reload {Type I LastRead 0 FirstWrite -1}
		old_h_54_reload {Type I LastRead 0 FirstWrite -1}
		old_h_55_reload {Type I LastRead 0 FirstWrite -1}
		old_h_56_reload {Type I LastRead 0 FirstWrite -1}
		old_h_57_reload {Type I LastRead 0 FirstWrite -1}
		old_h_58_reload {Type I LastRead 0 FirstWrite -1}
		old_h_59_reload {Type I LastRead 0 FirstWrite -1}
		old_h_60_reload {Type I LastRead 0 FirstWrite -1}
		old_h_61_reload {Type I LastRead 0 FirstWrite -1}
		old_h_62_reload {Type I LastRead 0 FirstWrite -1}
		old_h_63_reload {Type I LastRead 0 FirstWrite -1}
		old_h_64_reload {Type I LastRead 0 FirstWrite -1}
		old_h_65_reload {Type I LastRead 0 FirstWrite -1}
		old_h_66_reload {Type I LastRead 0 FirstWrite -1}
		boundary {Type I LastRead 1 FirstWrite -1}
		chemical_200_out {Type O LastRead -1 FirstWrite 5}
		chemical_199_out {Type O LastRead -1 FirstWrite 5}
		chemical_198_out {Type O LastRead -1 FirstWrite 5}
		chemical_197_out {Type O LastRead -1 FirstWrite 5}
		chemical_196_out {Type O LastRead -1 FirstWrite 5}
		chemical_195_out {Type O LastRead -1 FirstWrite 5}
		chemical_194_out {Type O LastRead -1 FirstWrite 5}
		chemical_193_out {Type O LastRead -1 FirstWrite 5}
		chemical_192_out {Type O LastRead -1 FirstWrite 5}
		chemical_191_out {Type O LastRead -1 FirstWrite 5}
		chemical_190_out {Type O LastRead -1 FirstWrite 5}
		chemical_189_out {Type O LastRead -1 FirstWrite 5}
		chemical_188_out {Type O LastRead -1 FirstWrite 5}
		chemical_187_out {Type O LastRead -1 FirstWrite 5}
		chemical_186_out {Type O LastRead -1 FirstWrite 5}
		chemical_185_out {Type O LastRead -1 FirstWrite 5}
		chemical_184_out {Type O LastRead -1 FirstWrite 5}
		chemical_183_out {Type O LastRead -1 FirstWrite 5}
		chemical_182_out {Type O LastRead -1 FirstWrite 5}
		chemical_181_out {Type O LastRead -1 FirstWrite 5}
		chemical_180_out {Type O LastRead -1 FirstWrite 5}
		chemical_179_out {Type O LastRead -1 FirstWrite 5}
		chemical_178_out {Type O LastRead -1 FirstWrite 5}
		chemical_177_out {Type O LastRead -1 FirstWrite 5}
		chemical_176_out {Type O LastRead -1 FirstWrite 5}
		chemical_175_out {Type O LastRead -1 FirstWrite 5}
		chemical_174_out {Type O LastRead -1 FirstWrite 5}
		chemical_173_out {Type O LastRead -1 FirstWrite 5}
		chemical_172_out {Type O LastRead -1 FirstWrite 5}
		chemical_171_out {Type O LastRead -1 FirstWrite 5}
		chemical_170_out {Type O LastRead -1 FirstWrite 5}
		chemical_169_out {Type O LastRead -1 FirstWrite 5}
		chemical_168_out {Type O LastRead -1 FirstWrite 5}
		chemical_167_out {Type O LastRead -1 FirstWrite 5}
		chemical_166_out {Type O LastRead -1 FirstWrite 5}
		chemical_165_out {Type O LastRead -1 FirstWrite 5}
		chemical_164_out {Type O LastRead -1 FirstWrite 5}
		chemical_163_out {Type O LastRead -1 FirstWrite 5}
		chemical_162_out {Type O LastRead -1 FirstWrite 5}
		chemical_161_out {Type O LastRead -1 FirstWrite 5}
		chemical_160_out {Type O LastRead -1 FirstWrite 5}
		chemical_159_out {Type O LastRead -1 FirstWrite 5}
		chemical_158_out {Type O LastRead -1 FirstWrite 5}
		chemical_157_out {Type O LastRead -1 FirstWrite 5}
		chemical_156_out {Type O LastRead -1 FirstWrite 5}
		chemical_155_out {Type O LastRead -1 FirstWrite 5}
		chemical_154_out {Type O LastRead -1 FirstWrite 5}
		chemical_153_out {Type O LastRead -1 FirstWrite 5}
		chemical_152_out {Type O LastRead -1 FirstWrite 5}
		chemical_151_out {Type O LastRead -1 FirstWrite 5}
		chemical_150_out {Type O LastRead -1 FirstWrite 5}
		chemical_149_out {Type O LastRead -1 FirstWrite 5}
		chemical_148_out {Type O LastRead -1 FirstWrite 5}
		chemical_147_out {Type O LastRead -1 FirstWrite 5}
		chemical_146_out {Type O LastRead -1 FirstWrite 5}
		chemical_145_out {Type O LastRead -1 FirstWrite 5}
		chemical_144_out {Type O LastRead -1 FirstWrite 5}
		chemical_143_out {Type O LastRead -1 FirstWrite 5}
		chemical_142_out {Type O LastRead -1 FirstWrite 5}
		chemical_141_out {Type O LastRead -1 FirstWrite 5}
		chemical_140_out {Type O LastRead -1 FirstWrite 5}
		chemical_139_out {Type O LastRead -1 FirstWrite 5}
		chemical_138_out {Type O LastRead -1 FirstWrite 5}
		chemical_137_out {Type O LastRead -1 FirstWrite 5}
		chemical_136_out {Type O LastRead -1 FirstWrite 5}
		chemical_135_out {Type O LastRead -1 FirstWrite 5}
		chemical_134_out {Type O LastRead -1 FirstWrite 5}
		status_3_out {Type O LastRead -1 FirstWrite 5}
		FLYVIS_EDGE_SRC {Type I LastRead -1 FirstWrite -1}
		FLYVIS_EDGE_WEIGHT_Q20 {Type I LastRead -1 FirstWrite -1}
		FLYVIS_EDGE_DST {Type I LastRead -1 FirstWrite -1}}
	flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_124_4 {
		candidate_66_reload {Type I LastRead 0 FirstWrite -1}
		candidate_65_reload {Type I LastRead 0 FirstWrite -1}
		candidate_64_reload {Type I LastRead 0 FirstWrite -1}
		candidate_63_reload {Type I LastRead 0 FirstWrite -1}
		candidate_62_reload {Type I LastRead 0 FirstWrite -1}
		candidate_61_reload {Type I LastRead 0 FirstWrite -1}
		candidate_60_reload {Type I LastRead 0 FirstWrite -1}
		candidate_59_reload {Type I LastRead 0 FirstWrite -1}
		candidate_58_reload {Type I LastRead 0 FirstWrite -1}
		candidate_57_reload {Type I LastRead 0 FirstWrite -1}
		candidate_56_reload {Type I LastRead 0 FirstWrite -1}
		candidate_55_reload {Type I LastRead 0 FirstWrite -1}
		candidate_54_reload {Type I LastRead 0 FirstWrite -1}
		candidate_53_reload {Type I LastRead 0 FirstWrite -1}
		candidate_52_reload {Type I LastRead 0 FirstWrite -1}
		candidate_51_reload {Type I LastRead 0 FirstWrite -1}
		candidate_50_reload {Type I LastRead 0 FirstWrite -1}
		candidate_49_reload {Type I LastRead 0 FirstWrite -1}
		candidate_48_reload {Type I LastRead 0 FirstWrite -1}
		candidate_47_reload {Type I LastRead 0 FirstWrite -1}
		candidate_46_reload {Type I LastRead 0 FirstWrite -1}
		candidate_45_reload {Type I LastRead 0 FirstWrite -1}
		candidate_44_reload {Type I LastRead 0 FirstWrite -1}
		candidate_43_reload {Type I LastRead 0 FirstWrite -1}
		candidate_42_reload {Type I LastRead 0 FirstWrite -1}
		candidate_41_reload {Type I LastRead 0 FirstWrite -1}
		candidate_40_reload {Type I LastRead 0 FirstWrite -1}
		candidate_39_reload {Type I LastRead 0 FirstWrite -1}
		candidate_38_reload {Type I LastRead 0 FirstWrite -1}
		candidate_37_reload {Type I LastRead 0 FirstWrite -1}
		candidate_36_reload {Type I LastRead 0 FirstWrite -1}
		candidate_35_reload {Type I LastRead 0 FirstWrite -1}
		candidate_34_reload {Type I LastRead 0 FirstWrite -1}
		candidate_33_reload {Type I LastRead 0 FirstWrite -1}
		candidate_32_reload {Type I LastRead 0 FirstWrite -1}
		candidate_31_reload {Type I LastRead 0 FirstWrite -1}
		candidate_30_reload {Type I LastRead 0 FirstWrite -1}
		candidate_29_reload {Type I LastRead 0 FirstWrite -1}
		candidate_28_reload {Type I LastRead 0 FirstWrite -1}
		candidate_27_reload {Type I LastRead 0 FirstWrite -1}
		candidate_26_reload {Type I LastRead 0 FirstWrite -1}
		candidate_25_reload {Type I LastRead 0 FirstWrite -1}
		candidate_24_reload {Type I LastRead 0 FirstWrite -1}
		candidate_23_reload {Type I LastRead 0 FirstWrite -1}
		candidate_22_reload {Type I LastRead 0 FirstWrite -1}
		candidate_21_reload {Type I LastRead 0 FirstWrite -1}
		candidate_20_reload {Type I LastRead 0 FirstWrite -1}
		candidate_19_reload {Type I LastRead 0 FirstWrite -1}
		candidate_18_reload {Type I LastRead 0 FirstWrite -1}
		candidate_17_reload {Type I LastRead 0 FirstWrite -1}
		candidate_16_reload {Type I LastRead 0 FirstWrite -1}
		candidate_15_reload {Type I LastRead 0 FirstWrite -1}
		candidate_14_reload {Type I LastRead 0 FirstWrite -1}
		candidate_13_reload {Type I LastRead 0 FirstWrite -1}
		candidate_12_reload {Type I LastRead 0 FirstWrite -1}
		candidate_11_reload {Type I LastRead 0 FirstWrite -1}
		candidate_10_reload {Type I LastRead 0 FirstWrite -1}
		candidate_9_reload {Type I LastRead 0 FirstWrite -1}
		candidate_8_reload {Type I LastRead 0 FirstWrite -1}
		candidate_7_reload {Type I LastRead 0 FirstWrite -1}
		candidate_6_reload {Type I LastRead 0 FirstWrite -1}
		candidate_5_reload {Type I LastRead 0 FirstWrite -1}
		candidate_4_reload {Type I LastRead 0 FirstWrite -1}
		candidate_3_reload {Type I LastRead 0 FirstWrite -1}
		candidate_2_reload {Type I LastRead 0 FirstWrite -1}
		candidate_1_reload {Type I LastRead 0 FirstWrite -1}
		candidate_reload {Type I LastRead 0 FirstWrite -1}
		chemical_134_reload {Type I LastRead 0 FirstWrite -1}
		chemical_135_reload {Type I LastRead 0 FirstWrite -1}
		chemical_136_reload {Type I LastRead 0 FirstWrite -1}
		chemical_137_reload {Type I LastRead 0 FirstWrite -1}
		chemical_138_reload {Type I LastRead 0 FirstWrite -1}
		chemical_139_reload {Type I LastRead 0 FirstWrite -1}
		chemical_140_reload {Type I LastRead 0 FirstWrite -1}
		chemical_141_reload {Type I LastRead 0 FirstWrite -1}
		chemical_142_reload {Type I LastRead 0 FirstWrite -1}
		chemical_143_reload {Type I LastRead 0 FirstWrite -1}
		chemical_144_reload {Type I LastRead 0 FirstWrite -1}
		chemical_145_reload {Type I LastRead 0 FirstWrite -1}
		chemical_146_reload {Type I LastRead 0 FirstWrite -1}
		chemical_147_reload {Type I LastRead 0 FirstWrite -1}
		chemical_148_reload {Type I LastRead 0 FirstWrite -1}
		chemical_149_reload {Type I LastRead 0 FirstWrite -1}
		chemical_150_reload {Type I LastRead 0 FirstWrite -1}
		chemical_151_reload {Type I LastRead 0 FirstWrite -1}
		chemical_152_reload {Type I LastRead 0 FirstWrite -1}
		chemical_153_reload {Type I LastRead 0 FirstWrite -1}
		chemical_154_reload {Type I LastRead 0 FirstWrite -1}
		chemical_155_reload {Type I LastRead 0 FirstWrite -1}
		chemical_156_reload {Type I LastRead 0 FirstWrite -1}
		chemical_157_reload {Type I LastRead 0 FirstWrite -1}
		chemical_158_reload {Type I LastRead 0 FirstWrite -1}
		chemical_159_reload {Type I LastRead 0 FirstWrite -1}
		chemical_160_reload {Type I LastRead 0 FirstWrite -1}
		chemical_161_reload {Type I LastRead 0 FirstWrite -1}
		chemical_162_reload {Type I LastRead 0 FirstWrite -1}
		chemical_163_reload {Type I LastRead 0 FirstWrite -1}
		chemical_164_reload {Type I LastRead 0 FirstWrite -1}
		chemical_165_reload {Type I LastRead 0 FirstWrite -1}
		chemical_166_reload {Type I LastRead 0 FirstWrite -1}
		chemical_167_reload {Type I LastRead 0 FirstWrite -1}
		chemical_168_reload {Type I LastRead 0 FirstWrite -1}
		chemical_169_reload {Type I LastRead 0 FirstWrite -1}
		chemical_170_reload {Type I LastRead 0 FirstWrite -1}
		chemical_171_reload {Type I LastRead 0 FirstWrite -1}
		chemical_172_reload {Type I LastRead 0 FirstWrite -1}
		chemical_173_reload {Type I LastRead 0 FirstWrite -1}
		chemical_174_reload {Type I LastRead 0 FirstWrite -1}
		chemical_175_reload {Type I LastRead 0 FirstWrite -1}
		chemical_176_reload {Type I LastRead 0 FirstWrite -1}
		chemical_177_reload {Type I LastRead 0 FirstWrite -1}
		chemical_178_reload {Type I LastRead 0 FirstWrite -1}
		chemical_179_reload {Type I LastRead 0 FirstWrite -1}
		chemical_180_reload {Type I LastRead 0 FirstWrite -1}
		chemical_181_reload {Type I LastRead 0 FirstWrite -1}
		chemical_182_reload {Type I LastRead 0 FirstWrite -1}
		chemical_183_reload {Type I LastRead 0 FirstWrite -1}
		chemical_184_reload {Type I LastRead 0 FirstWrite -1}
		chemical_185_reload {Type I LastRead 0 FirstWrite -1}
		chemical_186_reload {Type I LastRead 0 FirstWrite -1}
		chemical_187_reload {Type I LastRead 0 FirstWrite -1}
		chemical_188_reload {Type I LastRead 0 FirstWrite -1}
		chemical_189_reload {Type I LastRead 0 FirstWrite -1}
		chemical_190_reload {Type I LastRead 0 FirstWrite -1}
		chemical_191_reload {Type I LastRead 0 FirstWrite -1}
		chemical_192_reload {Type I LastRead 0 FirstWrite -1}
		chemical_193_reload {Type I LastRead 0 FirstWrite -1}
		chemical_194_reload {Type I LastRead 0 FirstWrite -1}
		chemical_195_reload {Type I LastRead 0 FirstWrite -1}
		chemical_196_reload {Type I LastRead 0 FirstWrite -1}
		chemical_197_reload {Type I LastRead 0 FirstWrite -1}
		chemical_198_reload {Type I LastRead 0 FirstWrite -1}
		chemical_199_reload {Type I LastRead 0 FirstWrite -1}
		chemical_200_reload {Type I LastRead 0 FirstWrite -1}
		old_h_reload {Type I LastRead 0 FirstWrite -1}
		old_h_1_reload {Type I LastRead 0 FirstWrite -1}
		old_h_2_reload {Type I LastRead 0 FirstWrite -1}
		old_h_3_reload {Type I LastRead 0 FirstWrite -1}
		old_h_4_reload {Type I LastRead 0 FirstWrite -1}
		old_h_5_reload {Type I LastRead 0 FirstWrite -1}
		old_h_6_reload {Type I LastRead 0 FirstWrite -1}
		old_h_7_reload {Type I LastRead 0 FirstWrite -1}
		old_h_8_reload {Type I LastRead 0 FirstWrite -1}
		old_h_9_reload {Type I LastRead 0 FirstWrite -1}
		old_h_10_reload {Type I LastRead 0 FirstWrite -1}
		old_h_11_reload {Type I LastRead 0 FirstWrite -1}
		old_h_12_reload {Type I LastRead 0 FirstWrite -1}
		old_h_13_reload {Type I LastRead 0 FirstWrite -1}
		old_h_14_reload {Type I LastRead 0 FirstWrite -1}
		old_h_15_reload {Type I LastRead 0 FirstWrite -1}
		old_h_16_reload {Type I LastRead 0 FirstWrite -1}
		old_h_17_reload {Type I LastRead 0 FirstWrite -1}
		old_h_18_reload {Type I LastRead 0 FirstWrite -1}
		old_h_19_reload {Type I LastRead 0 FirstWrite -1}
		old_h_20_reload {Type I LastRead 0 FirstWrite -1}
		old_h_21_reload {Type I LastRead 0 FirstWrite -1}
		old_h_22_reload {Type I LastRead 0 FirstWrite -1}
		old_h_23_reload {Type I LastRead 0 FirstWrite -1}
		old_h_24_reload {Type I LastRead 0 FirstWrite -1}
		old_h_25_reload {Type I LastRead 0 FirstWrite -1}
		old_h_26_reload {Type I LastRead 0 FirstWrite -1}
		old_h_27_reload {Type I LastRead 0 FirstWrite -1}
		old_h_28_reload {Type I LastRead 0 FirstWrite -1}
		old_h_29_reload {Type I LastRead 0 FirstWrite -1}
		old_h_30_reload {Type I LastRead 0 FirstWrite -1}
		old_h_31_reload {Type I LastRead 0 FirstWrite -1}
		old_h_32_reload {Type I LastRead 0 FirstWrite -1}
		old_h_33_reload {Type I LastRead 0 FirstWrite -1}
		old_h_34_reload {Type I LastRead 0 FirstWrite -1}
		old_h_35_reload {Type I LastRead 0 FirstWrite -1}
		old_h_36_reload {Type I LastRead 0 FirstWrite -1}
		old_h_37_reload {Type I LastRead 0 FirstWrite -1}
		old_h_38_reload {Type I LastRead 0 FirstWrite -1}
		old_h_39_reload {Type I LastRead 0 FirstWrite -1}
		old_h_40_reload {Type I LastRead 0 FirstWrite -1}
		old_h_41_reload {Type I LastRead 0 FirstWrite -1}
		old_h_42_reload {Type I LastRead 0 FirstWrite -1}
		old_h_43_reload {Type I LastRead 0 FirstWrite -1}
		old_h_44_reload {Type I LastRead 0 FirstWrite -1}
		old_h_45_reload {Type I LastRead 0 FirstWrite -1}
		old_h_46_reload {Type I LastRead 0 FirstWrite -1}
		old_h_47_reload {Type I LastRead 0 FirstWrite -1}
		old_h_48_reload {Type I LastRead 0 FirstWrite -1}
		old_h_49_reload {Type I LastRead 0 FirstWrite -1}
		old_h_50_reload {Type I LastRead 0 FirstWrite -1}
		old_h_51_reload {Type I LastRead 0 FirstWrite -1}
		old_h_52_reload {Type I LastRead 0 FirstWrite -1}
		old_h_53_reload {Type I LastRead 0 FirstWrite -1}
		old_h_54_reload {Type I LastRead 0 FirstWrite -1}
		old_h_55_reload {Type I LastRead 0 FirstWrite -1}
		old_h_56_reload {Type I LastRead 0 FirstWrite -1}
		old_h_57_reload {Type I LastRead 0 FirstWrite -1}
		old_h_58_reload {Type I LastRead 0 FirstWrite -1}
		old_h_59_reload {Type I LastRead 0 FirstWrite -1}
		old_h_60_reload {Type I LastRead 0 FirstWrite -1}
		old_h_61_reload {Type I LastRead 0 FirstWrite -1}
		old_h_62_reload {Type I LastRead 0 FirstWrite -1}
		old_h_63_reload {Type I LastRead 0 FirstWrite -1}
		old_h_64_reload {Type I LastRead 0 FirstWrite -1}
		old_h_65_reload {Type I LastRead 0 FirstWrite -1}
		old_h_66_reload {Type I LastRead 0 FirstWrite -1}
		x_h_reload {Type I LastRead 0 FirstWrite -1}
		x_h_1_reload {Type I LastRead 0 FirstWrite -1}
		x_h_2_reload {Type I LastRead 0 FirstWrite -1}
		x_h_3_reload {Type I LastRead 0 FirstWrite -1}
		x_h_4_reload {Type I LastRead 0 FirstWrite -1}
		x_h_5_reload {Type I LastRead 0 FirstWrite -1}
		x_h_6_reload {Type I LastRead 0 FirstWrite -1}
		x_h_7_reload {Type I LastRead 0 FirstWrite -1}
		x_h_8_reload {Type I LastRead 0 FirstWrite -1}
		x_h_9_reload {Type I LastRead 0 FirstWrite -1}
		x_h_10_reload {Type I LastRead 0 FirstWrite -1}
		x_h_11_reload {Type I LastRead 0 FirstWrite -1}
		x_h_12_reload {Type I LastRead 0 FirstWrite -1}
		x_h_13_reload {Type I LastRead 0 FirstWrite -1}
		x_h_14_reload {Type I LastRead 0 FirstWrite -1}
		x_h_15_reload {Type I LastRead 0 FirstWrite -1}
		x_h_16_reload {Type I LastRead 0 FirstWrite -1}
		x_h_17_reload {Type I LastRead 0 FirstWrite -1}
		x_h_18_reload {Type I LastRead 0 FirstWrite -1}
		x_h_19_reload {Type I LastRead 0 FirstWrite -1}
		x_h_20_reload {Type I LastRead 0 FirstWrite -1}
		x_h_21_reload {Type I LastRead 0 FirstWrite -1}
		x_h_22_reload {Type I LastRead 0 FirstWrite -1}
		x_h_23_reload {Type I LastRead 0 FirstWrite -1}
		x_h_24_reload {Type I LastRead 0 FirstWrite -1}
		x_h_25_reload {Type I LastRead 0 FirstWrite -1}
		x_h_26_reload {Type I LastRead 0 FirstWrite -1}
		x_h_27_reload {Type I LastRead 0 FirstWrite -1}
		x_h_28_reload {Type I LastRead 0 FirstWrite -1}
		x_h_29_reload {Type I LastRead 0 FirstWrite -1}
		x_h_30_reload {Type I LastRead 0 FirstWrite -1}
		x_h_31_reload {Type I LastRead 0 FirstWrite -1}
		x_h_32_reload {Type I LastRead 0 FirstWrite -1}
		x_h_33_reload {Type I LastRead 0 FirstWrite -1}
		x_h_34_reload {Type I LastRead 0 FirstWrite -1}
		x_h_35_reload {Type I LastRead 0 FirstWrite -1}
		x_h_36_reload {Type I LastRead 0 FirstWrite -1}
		x_h_37_reload {Type I LastRead 0 FirstWrite -1}
		x_h_38_reload {Type I LastRead 0 FirstWrite -1}
		x_h_39_reload {Type I LastRead 0 FirstWrite -1}
		x_h_40_reload {Type I LastRead 0 FirstWrite -1}
		x_h_41_reload {Type I LastRead 0 FirstWrite -1}
		x_h_42_reload {Type I LastRead 0 FirstWrite -1}
		x_h_43_reload {Type I LastRead 0 FirstWrite -1}
		x_h_44_reload {Type I LastRead 0 FirstWrite -1}
		x_h_45_reload {Type I LastRead 0 FirstWrite -1}
		x_h_46_reload {Type I LastRead 0 FirstWrite -1}
		x_h_47_reload {Type I LastRead 0 FirstWrite -1}
		x_h_48_reload {Type I LastRead 0 FirstWrite -1}
		x_h_49_reload {Type I LastRead 0 FirstWrite -1}
		x_h_50_reload {Type I LastRead 0 FirstWrite -1}
		x_h_51_reload {Type I LastRead 0 FirstWrite -1}
		x_h_52_reload {Type I LastRead 0 FirstWrite -1}
		x_h_53_reload {Type I LastRead 0 FirstWrite -1}
		x_h_54_reload {Type I LastRead 0 FirstWrite -1}
		x_h_55_reload {Type I LastRead 0 FirstWrite -1}
		x_h_56_reload {Type I LastRead 0 FirstWrite -1}
		x_h_57_reload {Type I LastRead 0 FirstWrite -1}
		x_h_58_reload {Type I LastRead 0 FirstWrite -1}
		x_h_59_reload {Type I LastRead 0 FirstWrite -1}
		x_h_60_reload {Type I LastRead 0 FirstWrite -1}
		x_h_61_reload {Type I LastRead 0 FirstWrite -1}
		x_h_62_reload {Type I LastRead 0 FirstWrite -1}
		x_h_63_reload {Type I LastRead 0 FirstWrite -1}
		x_h_64_reload {Type I LastRead 0 FirstWrite -1}
		x_h_65_reload {Type I LastRead 0 FirstWrite -1}
		x_h_66_reload {Type I LastRead 0 FirstWrite -1}
		candidate_200_out {Type O LastRead -1 FirstWrite 6}
		candidate_199_out {Type O LastRead -1 FirstWrite 6}
		candidate_198_out {Type O LastRead -1 FirstWrite 6}
		candidate_197_out {Type O LastRead -1 FirstWrite 6}
		candidate_196_out {Type O LastRead -1 FirstWrite 6}
		candidate_195_out {Type O LastRead -1 FirstWrite 6}
		candidate_194_out {Type O LastRead -1 FirstWrite 6}
		candidate_193_out {Type O LastRead -1 FirstWrite 6}
		candidate_192_out {Type O LastRead -1 FirstWrite 6}
		candidate_191_out {Type O LastRead -1 FirstWrite 6}
		candidate_190_out {Type O LastRead -1 FirstWrite 6}
		candidate_189_out {Type O LastRead -1 FirstWrite 6}
		candidate_188_out {Type O LastRead -1 FirstWrite 6}
		candidate_187_out {Type O LastRead -1 FirstWrite 6}
		candidate_186_out {Type O LastRead -1 FirstWrite 6}
		candidate_185_out {Type O LastRead -1 FirstWrite 6}
		candidate_184_out {Type O LastRead -1 FirstWrite 6}
		candidate_183_out {Type O LastRead -1 FirstWrite 6}
		candidate_182_out {Type O LastRead -1 FirstWrite 6}
		candidate_181_out {Type O LastRead -1 FirstWrite 6}
		candidate_180_out {Type O LastRead -1 FirstWrite 6}
		candidate_179_out {Type O LastRead -1 FirstWrite 6}
		candidate_178_out {Type O LastRead -1 FirstWrite 6}
		candidate_177_out {Type O LastRead -1 FirstWrite 6}
		candidate_176_out {Type O LastRead -1 FirstWrite 6}
		candidate_175_out {Type O LastRead -1 FirstWrite 6}
		candidate_174_out {Type O LastRead -1 FirstWrite 6}
		candidate_173_out {Type O LastRead -1 FirstWrite 6}
		candidate_172_out {Type O LastRead -1 FirstWrite 6}
		candidate_171_out {Type O LastRead -1 FirstWrite 6}
		candidate_170_out {Type O LastRead -1 FirstWrite 6}
		candidate_169_out {Type O LastRead -1 FirstWrite 6}
		candidate_168_out {Type O LastRead -1 FirstWrite 6}
		candidate_167_out {Type O LastRead -1 FirstWrite 6}
		candidate_166_out {Type O LastRead -1 FirstWrite 6}
		candidate_165_out {Type O LastRead -1 FirstWrite 6}
		candidate_164_out {Type O LastRead -1 FirstWrite 6}
		candidate_163_out {Type O LastRead -1 FirstWrite 6}
		candidate_162_out {Type O LastRead -1 FirstWrite 6}
		candidate_161_out {Type O LastRead -1 FirstWrite 6}
		candidate_160_out {Type O LastRead -1 FirstWrite 6}
		candidate_159_out {Type O LastRead -1 FirstWrite 6}
		candidate_158_out {Type O LastRead -1 FirstWrite 6}
		candidate_157_out {Type O LastRead -1 FirstWrite 6}
		candidate_156_out {Type O LastRead -1 FirstWrite 6}
		candidate_155_out {Type O LastRead -1 FirstWrite 6}
		candidate_154_out {Type O LastRead -1 FirstWrite 6}
		candidate_153_out {Type O LastRead -1 FirstWrite 6}
		candidate_152_out {Type O LastRead -1 FirstWrite 6}
		candidate_151_out {Type O LastRead -1 FirstWrite 6}
		candidate_150_out {Type O LastRead -1 FirstWrite 6}
		candidate_149_out {Type O LastRead -1 FirstWrite 6}
		candidate_148_out {Type O LastRead -1 FirstWrite 6}
		candidate_147_out {Type O LastRead -1 FirstWrite 6}
		candidate_146_out {Type O LastRead -1 FirstWrite 6}
		candidate_145_out {Type O LastRead -1 FirstWrite 6}
		candidate_144_out {Type O LastRead -1 FirstWrite 6}
		candidate_143_out {Type O LastRead -1 FirstWrite 6}
		candidate_142_out {Type O LastRead -1 FirstWrite 6}
		candidate_141_out {Type O LastRead -1 FirstWrite 6}
		candidate_140_out {Type O LastRead -1 FirstWrite 6}
		candidate_139_out {Type O LastRead -1 FirstWrite 6}
		candidate_138_out {Type O LastRead -1 FirstWrite 6}
		candidate_137_out {Type O LastRead -1 FirstWrite 6}
		candidate_136_out {Type O LastRead -1 FirstWrite 6}
		candidate_135_out {Type O LastRead -1 FirstWrite 6}
		candidate_134_out {Type O LastRead -1 FirstWrite 6}
		status_4_out {Type O LastRead -1 FirstWrite 6}
		FLYVIS_BIAS_Q22 {Type I LastRead -1 FirstWrite -1}
		FLYVIS_INVTau_Q22 {Type I LastRead -1 FirstWrite -1}}
	flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_161_5 {
		gmem0 {Type O LastRead -1 FirstWrite 1}
		status_6 {Type I LastRead 0 FirstWrite -1}
		sext_ln161 {Type I LastRead 0 FirstWrite -1}
		candidate_201 {Type I LastRead 0 FirstWrite -1}
		candidate_202 {Type I LastRead 0 FirstWrite -1}
		candidate_203 {Type I LastRead 0 FirstWrite -1}
		candidate_204 {Type I LastRead 0 FirstWrite -1}
		candidate_205 {Type I LastRead 0 FirstWrite -1}
		candidate_206 {Type I LastRead 0 FirstWrite -1}
		candidate_207 {Type I LastRead 0 FirstWrite -1}
		candidate_208 {Type I LastRead 0 FirstWrite -1}
		candidate_209 {Type I LastRead 0 FirstWrite -1}
		candidate_210 {Type I LastRead 0 FirstWrite -1}
		candidate_211 {Type I LastRead 0 FirstWrite -1}
		candidate_212 {Type I LastRead 0 FirstWrite -1}
		candidate_213 {Type I LastRead 0 FirstWrite -1}
		candidate_214 {Type I LastRead 0 FirstWrite -1}
		candidate_215 {Type I LastRead 0 FirstWrite -1}
		candidate_216 {Type I LastRead 0 FirstWrite -1}
		candidate_217 {Type I LastRead 0 FirstWrite -1}
		candidate_218 {Type I LastRead 0 FirstWrite -1}
		candidate_219 {Type I LastRead 0 FirstWrite -1}
		candidate_220 {Type I LastRead 0 FirstWrite -1}
		candidate_221 {Type I LastRead 0 FirstWrite -1}
		candidate_222 {Type I LastRead 0 FirstWrite -1}
		candidate_223 {Type I LastRead 0 FirstWrite -1}
		candidate_224 {Type I LastRead 0 FirstWrite -1}
		candidate_225 {Type I LastRead 0 FirstWrite -1}
		candidate_226 {Type I LastRead 0 FirstWrite -1}
		candidate_227 {Type I LastRead 0 FirstWrite -1}
		candidate_228 {Type I LastRead 0 FirstWrite -1}
		candidate_229 {Type I LastRead 0 FirstWrite -1}
		candidate_230 {Type I LastRead 0 FirstWrite -1}
		candidate_231 {Type I LastRead 0 FirstWrite -1}
		candidate_232 {Type I LastRead 0 FirstWrite -1}
		candidate_233 {Type I LastRead 0 FirstWrite -1}
		candidate_234 {Type I LastRead 0 FirstWrite -1}
		candidate_235 {Type I LastRead 0 FirstWrite -1}
		candidate_236 {Type I LastRead 0 FirstWrite -1}
		candidate_237 {Type I LastRead 0 FirstWrite -1}
		candidate_238 {Type I LastRead 0 FirstWrite -1}
		candidate_239 {Type I LastRead 0 FirstWrite -1}
		candidate_240 {Type I LastRead 0 FirstWrite -1}
		candidate_241 {Type I LastRead 0 FirstWrite -1}
		candidate_242 {Type I LastRead 0 FirstWrite -1}
		candidate_243 {Type I LastRead 0 FirstWrite -1}
		candidate_244 {Type I LastRead 0 FirstWrite -1}
		candidate_245 {Type I LastRead 0 FirstWrite -1}
		candidate_246 {Type I LastRead 0 FirstWrite -1}
		candidate_247 {Type I LastRead 0 FirstWrite -1}
		candidate_248 {Type I LastRead 0 FirstWrite -1}
		candidate_249 {Type I LastRead 0 FirstWrite -1}
		candidate_250 {Type I LastRead 0 FirstWrite -1}
		candidate_251 {Type I LastRead 0 FirstWrite -1}
		candidate_252 {Type I LastRead 0 FirstWrite -1}
		candidate_253 {Type I LastRead 0 FirstWrite -1}
		candidate_254 {Type I LastRead 0 FirstWrite -1}
		candidate_255 {Type I LastRead 0 FirstWrite -1}
		candidate_256 {Type I LastRead 0 FirstWrite -1}
		candidate_257 {Type I LastRead 0 FirstWrite -1}
		candidate_258 {Type I LastRead 0 FirstWrite -1}
		candidate_259 {Type I LastRead 0 FirstWrite -1}
		candidate_260 {Type I LastRead 0 FirstWrite -1}
		candidate_261 {Type I LastRead 0 FirstWrite -1}
		candidate_262 {Type I LastRead 0 FirstWrite -1}
		candidate_263 {Type I LastRead 0 FirstWrite -1}
		candidate_264 {Type I LastRead 0 FirstWrite -1}
		candidate_265 {Type I LastRead 0 FirstWrite -1}
		candidate_266 {Type I LastRead 0 FirstWrite -1}
		candidate_267 {Type I LastRead 0 FirstWrite -1}}}

set hasDtUnsupportedChannel 0

set PerformanceInfo {[
	{"Name" : "Latency", "Min" : "1589", "Max" : "8211"}
	, {"Name" : "Interval", "Min" : "1590", "Max" : "8212"}
]}

set PipelineEnableSignalInfo {[
]}

set Spec2ImplPortList { 
	gmem0 { m_axi {  { m_axi_gmem0_AWVALID VALID 1 1 }  { m_axi_gmem0_AWREADY READY 0 1 }  { m_axi_gmem0_AWADDR ADDR 1 64 }  { m_axi_gmem0_AWID ID 1 1 }  { m_axi_gmem0_AWLEN SIZE 1 8 }  { m_axi_gmem0_AWSIZE BURST 1 3 }  { m_axi_gmem0_AWBURST LOCK 1 2 }  { m_axi_gmem0_AWLOCK CACHE 1 2 }  { m_axi_gmem0_AWCACHE PROT 1 4 }  { m_axi_gmem0_AWPROT QOS 1 3 }  { m_axi_gmem0_AWQOS REGION 1 4 }  { m_axi_gmem0_AWREGION USER 1 4 }  { m_axi_gmem0_AWUSER DATA 1 1 }  { m_axi_gmem0_WVALID VALID 1 1 }  { m_axi_gmem0_WREADY READY 0 1 }  { m_axi_gmem0_WDATA FIFONUM 1 32 }  { m_axi_gmem0_WSTRB STRB 1 4 }  { m_axi_gmem0_WLAST LAST 1 1 }  { m_axi_gmem0_WID ID 1 1 }  { m_axi_gmem0_WUSER DATA 1 1 }  { m_axi_gmem0_ARVALID VALID 1 1 }  { m_axi_gmem0_ARREADY READY 0 1 }  { m_axi_gmem0_ARADDR ADDR 1 64 }  { m_axi_gmem0_ARID ID 1 1 }  { m_axi_gmem0_ARLEN SIZE 1 8 }  { m_axi_gmem0_ARSIZE BURST 1 3 }  { m_axi_gmem0_ARBURST LOCK 1 2 }  { m_axi_gmem0_ARLOCK CACHE 1 2 }  { m_axi_gmem0_ARCACHE PROT 1 4 }  { m_axi_gmem0_ARPROT QOS 1 3 }  { m_axi_gmem0_ARQOS REGION 1 4 }  { m_axi_gmem0_ARREGION USER 1 4 }  { m_axi_gmem0_ARUSER DATA 1 1 }  { m_axi_gmem0_RVALID VALID 0 1 }  { m_axi_gmem0_RREADY READY 1 1 }  { m_axi_gmem0_RDATA FIFONUM 0 32 }  { m_axi_gmem0_RLAST LAST 0 1 }  { m_axi_gmem0_RID ID 0 1 }  { m_axi_gmem0_RUSER DATA 0 1 }  { m_axi_gmem0_RRESP RESP 0 2 }  { m_axi_gmem0_BVALID VALID 0 1 }  { m_axi_gmem0_BREADY READY 1 1 }  { m_axi_gmem0_BRESP RESP 0 2 }  { m_axi_gmem0_BID ID 0 1 }  { m_axi_gmem0_BUSER DATA 0 1 } } }
}

set maxi_interface_dict [dict create]
dict set maxi_interface_dict gmem0 { CHANNEL_NUM 0 BUNDLE gmem0 NUM_READ_OUTSTANDING 16 NUM_WRITE_OUTSTANDING 16 MAX_READ_BURST_LENGTH 64 MAX_WRITE_BURST_LENGTH 64 READ_WRITE_MODE READ_WRITE}

# RTL port scheduling information:
set fifoSchedulingInfoList { 
}

# RTL bus port read request latency information:
set busReadReqLatencyList { 
	{ gmem0 1 }
}

# RTL bus port write response latency information:
set busWriteResLatencyList { 
	{ gmem0 1 }
}

# RTL array port load latency information:
set memoryLoadLatencyList { 
}

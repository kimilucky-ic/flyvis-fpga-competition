set moduleName flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_161_5
set isTopModule 0
set isCombinational 0
set isDatapathOnly 0
set isPipelined 1
set isPipelined_legacy 1
set pipeline_type loop_auto_rewind
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
set C_modelName {flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_161_5}
set C_modelType { void 0 }
set ap_memory_interface_dict [dict create]
set C_modelArgList {
	{ gmem0 int 32 regular {axi_master 1}  }
	{ status_6 int 32 regular  }
	{ sext_ln161 int 62 regular  }
	{ candidate_201 int 29 regular  }
	{ candidate_202 int 29 regular  }
	{ candidate_203 int 29 regular  }
	{ candidate_204 int 29 regular  }
	{ candidate_205 int 29 regular  }
	{ candidate_206 int 29 regular  }
	{ candidate_207 int 29 regular  }
	{ candidate_208 int 29 regular  }
	{ candidate_209 int 29 regular  }
	{ candidate_210 int 29 regular  }
	{ candidate_211 int 29 regular  }
	{ candidate_212 int 29 regular  }
	{ candidate_213 int 29 regular  }
	{ candidate_214 int 29 regular  }
	{ candidate_215 int 29 regular  }
	{ candidate_216 int 29 regular  }
	{ candidate_217 int 29 regular  }
	{ candidate_218 int 29 regular  }
	{ candidate_219 int 29 regular  }
	{ candidate_220 int 29 regular  }
	{ candidate_221 int 29 regular  }
	{ candidate_222 int 29 regular  }
	{ candidate_223 int 29 regular  }
	{ candidate_224 int 29 regular  }
	{ candidate_225 int 29 regular  }
	{ candidate_226 int 29 regular  }
	{ candidate_227 int 29 regular  }
	{ candidate_228 int 29 regular  }
	{ candidate_229 int 29 regular  }
	{ candidate_230 int 29 regular  }
	{ candidate_231 int 29 regular  }
	{ candidate_232 int 29 regular  }
	{ candidate_233 int 29 regular  }
	{ candidate_234 int 29 regular  }
	{ candidate_235 int 29 regular  }
	{ candidate_236 int 29 regular  }
	{ candidate_237 int 29 regular  }
	{ candidate_238 int 29 regular  }
	{ candidate_239 int 29 regular  }
	{ candidate_240 int 29 regular  }
	{ candidate_241 int 29 regular  }
	{ candidate_242 int 29 regular  }
	{ candidate_243 int 29 regular  }
	{ candidate_244 int 29 regular  }
	{ candidate_245 int 29 regular  }
	{ candidate_246 int 29 regular  }
	{ candidate_247 int 29 regular  }
	{ candidate_248 int 29 regular  }
	{ candidate_249 int 29 regular  }
	{ candidate_250 int 29 regular  }
	{ candidate_251 int 29 regular  }
	{ candidate_252 int 29 regular  }
	{ candidate_253 int 29 regular  }
	{ candidate_254 int 29 regular  }
	{ candidate_255 int 29 regular  }
	{ candidate_256 int 29 regular  }
	{ candidate_257 int 29 regular  }
	{ candidate_258 int 29 regular  }
	{ candidate_259 int 29 regular  }
	{ candidate_260 int 29 regular  }
	{ candidate_261 int 29 regular  }
	{ candidate_262 int 29 regular  }
	{ candidate_263 int 29 regular  }
	{ candidate_264 int 29 regular  }
	{ candidate_265 int 29 regular  }
	{ candidate_266 int 29 regular  }
	{ candidate_267 int 29 regular  }
}
set hasAXIMCache 0
set l_AXIML2Cache [list]
set AXIMCacheInstDict [dict create]
set C_modelArgMapList {[ 
	{ "Name" : "gmem0", "interface" : "axi_master", "bitwidth" : 32, "direction" : "WRITEONLY", "id_num" : 0, "bitSlice":[ {"cElement": [{"cName": "request","offset": { "type": "dynamic","port_name": "request","bundle": "control"},"direction": "READONLY"},{"cName": "result","offset": { "type": "dynamic","port_name": "result","bundle": "control"},"direction": "WRITEONLY"}]}]} , 
 	{ "Name" : "status_6", "interface" : "wire", "bitwidth" : 32, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln161", "interface" : "wire", "bitwidth" : 62, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_201", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_202", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_203", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_204", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_205", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_206", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_207", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_208", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_209", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_210", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_211", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_212", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_213", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_214", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_215", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_216", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_217", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_218", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_219", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_220", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_221", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_222", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_223", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_224", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_225", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_226", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_227", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_228", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_229", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_230", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_231", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_232", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_233", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_234", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_235", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_236", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_237", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_238", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_239", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_240", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_241", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_242", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_243", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_244", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_245", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_246", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_247", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_248", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_249", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_250", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_251", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_252", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_253", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_254", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_255", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_256", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_257", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_258", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_259", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_260", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_261", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_262", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_263", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_264", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_265", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_266", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} , 
 	{ "Name" : "candidate_267", "interface" : "wire", "bitwidth" : 29, "direction" : "READONLY"} ]}
# RTL Port declarations: 
set portNum 121
set portList { 
	{ ap_clk sc_in sc_logic 1 clock -1 } 
	{ ap_rst sc_in sc_logic 1 reset -1 active_high_sync } 
	{ ap_start sc_in sc_logic 1 start -1 } 
	{ ap_done sc_out sc_logic 1 predone -1 } 
	{ ap_idle sc_out sc_logic 1 done -1 } 
	{ ap_ready sc_out sc_logic 1 ready -1 } 
	{ m_axi_gmem0_0_AWVALID sc_out sc_logic 1 signal 0 } 
	{ m_axi_gmem0_0_AWREADY sc_in sc_logic 1 signal 0 } 
	{ m_axi_gmem0_0_AWADDR sc_out sc_lv 64 signal 0 } 
	{ m_axi_gmem0_0_AWID sc_out sc_lv 1 signal 0 } 
	{ m_axi_gmem0_0_AWLEN sc_out sc_lv 32 signal 0 } 
	{ m_axi_gmem0_0_AWSIZE sc_out sc_lv 3 signal 0 } 
	{ m_axi_gmem0_0_AWBURST sc_out sc_lv 2 signal 0 } 
	{ m_axi_gmem0_0_AWLOCK sc_out sc_lv 2 signal 0 } 
	{ m_axi_gmem0_0_AWCACHE sc_out sc_lv 4 signal 0 } 
	{ m_axi_gmem0_0_AWPROT sc_out sc_lv 3 signal 0 } 
	{ m_axi_gmem0_0_AWQOS sc_out sc_lv 4 signal 0 } 
	{ m_axi_gmem0_0_AWREGION sc_out sc_lv 4 signal 0 } 
	{ m_axi_gmem0_0_AWUSER sc_out sc_lv 1 signal 0 } 
	{ m_axi_gmem0_0_WVALID sc_out sc_logic 1 signal 0 } 
	{ m_axi_gmem0_0_WREADY sc_in sc_logic 1 signal 0 } 
	{ m_axi_gmem0_0_WDATA sc_out sc_lv 32 signal 0 } 
	{ m_axi_gmem0_0_WSTRB sc_out sc_lv 4 signal 0 } 
	{ m_axi_gmem0_0_WLAST sc_out sc_logic 1 signal 0 } 
	{ m_axi_gmem0_0_WID sc_out sc_lv 1 signal 0 } 
	{ m_axi_gmem0_0_WUSER sc_out sc_lv 1 signal 0 } 
	{ m_axi_gmem0_0_ARVALID sc_out sc_logic 1 signal 0 } 
	{ m_axi_gmem0_0_ARREADY sc_in sc_logic 1 signal 0 } 
	{ m_axi_gmem0_0_ARADDR sc_out sc_lv 64 signal 0 } 
	{ m_axi_gmem0_0_ARID sc_out sc_lv 1 signal 0 } 
	{ m_axi_gmem0_0_ARLEN sc_out sc_lv 32 signal 0 } 
	{ m_axi_gmem0_0_ARSIZE sc_out sc_lv 3 signal 0 } 
	{ m_axi_gmem0_0_ARBURST sc_out sc_lv 2 signal 0 } 
	{ m_axi_gmem0_0_ARLOCK sc_out sc_lv 2 signal 0 } 
	{ m_axi_gmem0_0_ARCACHE sc_out sc_lv 4 signal 0 } 
	{ m_axi_gmem0_0_ARPROT sc_out sc_lv 3 signal 0 } 
	{ m_axi_gmem0_0_ARQOS sc_out sc_lv 4 signal 0 } 
	{ m_axi_gmem0_0_ARREGION sc_out sc_lv 4 signal 0 } 
	{ m_axi_gmem0_0_ARUSER sc_out sc_lv 1 signal 0 } 
	{ m_axi_gmem0_0_RVALID sc_in sc_logic 1 signal 0 } 
	{ m_axi_gmem0_0_RREADY sc_out sc_logic 1 signal 0 } 
	{ m_axi_gmem0_0_RDATA sc_in sc_lv 32 signal 0 } 
	{ m_axi_gmem0_0_RLAST sc_in sc_logic 1 signal 0 } 
	{ m_axi_gmem0_0_RID sc_in sc_lv 1 signal 0 } 
	{ m_axi_gmem0_0_RFIFONUM sc_in sc_lv 11 signal 0 } 
	{ m_axi_gmem0_0_RUSER sc_in sc_lv 1 signal 0 } 
	{ m_axi_gmem0_0_RRESP sc_in sc_lv 2 signal 0 } 
	{ m_axi_gmem0_0_BVALID sc_in sc_logic 1 signal 0 } 
	{ m_axi_gmem0_0_BREADY sc_out sc_logic 1 signal 0 } 
	{ m_axi_gmem0_0_BRESP sc_in sc_lv 2 signal 0 } 
	{ m_axi_gmem0_0_BID sc_in sc_lv 1 signal 0 } 
	{ m_axi_gmem0_0_BUSER sc_in sc_lv 1 signal 0 } 
	{ status_6 sc_in sc_lv 32 signal 1 } 
	{ sext_ln161 sc_in sc_lv 62 signal 2 } 
	{ candidate_201 sc_in sc_lv 29 signal 3 } 
	{ candidate_202 sc_in sc_lv 29 signal 4 } 
	{ candidate_203 sc_in sc_lv 29 signal 5 } 
	{ candidate_204 sc_in sc_lv 29 signal 6 } 
	{ candidate_205 sc_in sc_lv 29 signal 7 } 
	{ candidate_206 sc_in sc_lv 29 signal 8 } 
	{ candidate_207 sc_in sc_lv 29 signal 9 } 
	{ candidate_208 sc_in sc_lv 29 signal 10 } 
	{ candidate_209 sc_in sc_lv 29 signal 11 } 
	{ candidate_210 sc_in sc_lv 29 signal 12 } 
	{ candidate_211 sc_in sc_lv 29 signal 13 } 
	{ candidate_212 sc_in sc_lv 29 signal 14 } 
	{ candidate_213 sc_in sc_lv 29 signal 15 } 
	{ candidate_214 sc_in sc_lv 29 signal 16 } 
	{ candidate_215 sc_in sc_lv 29 signal 17 } 
	{ candidate_216 sc_in sc_lv 29 signal 18 } 
	{ candidate_217 sc_in sc_lv 29 signal 19 } 
	{ candidate_218 sc_in sc_lv 29 signal 20 } 
	{ candidate_219 sc_in sc_lv 29 signal 21 } 
	{ candidate_220 sc_in sc_lv 29 signal 22 } 
	{ candidate_221 sc_in sc_lv 29 signal 23 } 
	{ candidate_222 sc_in sc_lv 29 signal 24 } 
	{ candidate_223 sc_in sc_lv 29 signal 25 } 
	{ candidate_224 sc_in sc_lv 29 signal 26 } 
	{ candidate_225 sc_in sc_lv 29 signal 27 } 
	{ candidate_226 sc_in sc_lv 29 signal 28 } 
	{ candidate_227 sc_in sc_lv 29 signal 29 } 
	{ candidate_228 sc_in sc_lv 29 signal 30 } 
	{ candidate_229 sc_in sc_lv 29 signal 31 } 
	{ candidate_230 sc_in sc_lv 29 signal 32 } 
	{ candidate_231 sc_in sc_lv 29 signal 33 } 
	{ candidate_232 sc_in sc_lv 29 signal 34 } 
	{ candidate_233 sc_in sc_lv 29 signal 35 } 
	{ candidate_234 sc_in sc_lv 29 signal 36 } 
	{ candidate_235 sc_in sc_lv 29 signal 37 } 
	{ candidate_236 sc_in sc_lv 29 signal 38 } 
	{ candidate_237 sc_in sc_lv 29 signal 39 } 
	{ candidate_238 sc_in sc_lv 29 signal 40 } 
	{ candidate_239 sc_in sc_lv 29 signal 41 } 
	{ candidate_240 sc_in sc_lv 29 signal 42 } 
	{ candidate_241 sc_in sc_lv 29 signal 43 } 
	{ candidate_242 sc_in sc_lv 29 signal 44 } 
	{ candidate_243 sc_in sc_lv 29 signal 45 } 
	{ candidate_244 sc_in sc_lv 29 signal 46 } 
	{ candidate_245 sc_in sc_lv 29 signal 47 } 
	{ candidate_246 sc_in sc_lv 29 signal 48 } 
	{ candidate_247 sc_in sc_lv 29 signal 49 } 
	{ candidate_248 sc_in sc_lv 29 signal 50 } 
	{ candidate_249 sc_in sc_lv 29 signal 51 } 
	{ candidate_250 sc_in sc_lv 29 signal 52 } 
	{ candidate_251 sc_in sc_lv 29 signal 53 } 
	{ candidate_252 sc_in sc_lv 29 signal 54 } 
	{ candidate_253 sc_in sc_lv 29 signal 55 } 
	{ candidate_254 sc_in sc_lv 29 signal 56 } 
	{ candidate_255 sc_in sc_lv 29 signal 57 } 
	{ candidate_256 sc_in sc_lv 29 signal 58 } 
	{ candidate_257 sc_in sc_lv 29 signal 59 } 
	{ candidate_258 sc_in sc_lv 29 signal 60 } 
	{ candidate_259 sc_in sc_lv 29 signal 61 } 
	{ candidate_260 sc_in sc_lv 29 signal 62 } 
	{ candidate_261 sc_in sc_lv 29 signal 63 } 
	{ candidate_262 sc_in sc_lv 29 signal 64 } 
	{ candidate_263 sc_in sc_lv 29 signal 65 } 
	{ candidate_264 sc_in sc_lv 29 signal 66 } 
	{ candidate_265 sc_in sc_lv 29 signal 67 } 
	{ candidate_266 sc_in sc_lv 29 signal 68 } 
	{ candidate_267 sc_in sc_lv 29 signal 69 } 
}
set NewPortList {[ 
	{ "name": "ap_clk", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "clock", "bundle":{"name": "ap_clk", "role": "default" }} , 
 	{ "name": "ap_rst", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "reset", "bundle":{"name": "ap_rst", "role": "default" }} , 
 	{ "name": "ap_start", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "start", "bundle":{"name": "ap_start", "role": "default" }} , 
 	{ "name": "ap_done", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "predone", "bundle":{"name": "ap_done", "role": "default" }} , 
 	{ "name": "ap_idle", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "done", "bundle":{"name": "ap_idle", "role": "default" }} , 
 	{ "name": "ap_ready", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "ready", "bundle":{"name": "ap_ready", "role": "default" }} , 
 	{ "name": "m_axi_gmem0_0_AWVALID", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_AWVALID" }} , 
 	{ "name": "m_axi_gmem0_0_AWREADY", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_AWREADY" }} , 
 	{ "name": "m_axi_gmem0_0_AWADDR", "direction": "out", "datatype": "sc_lv", "bitwidth":64, "type": "signal", "bundle":{"name": "gmem0", "role": "0_AWADDR" }} , 
 	{ "name": "m_axi_gmem0_0_AWID", "direction": "out", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_AWID" }} , 
 	{ "name": "m_axi_gmem0_0_AWLEN", "direction": "out", "datatype": "sc_lv", "bitwidth":32, "type": "signal", "bundle":{"name": "gmem0", "role": "0_AWLEN" }} , 
 	{ "name": "m_axi_gmem0_0_AWSIZE", "direction": "out", "datatype": "sc_lv", "bitwidth":3, "type": "signal", "bundle":{"name": "gmem0", "role": "0_AWSIZE" }} , 
 	{ "name": "m_axi_gmem0_0_AWBURST", "direction": "out", "datatype": "sc_lv", "bitwidth":2, "type": "signal", "bundle":{"name": "gmem0", "role": "0_AWBURST" }} , 
 	{ "name": "m_axi_gmem0_0_AWLOCK", "direction": "out", "datatype": "sc_lv", "bitwidth":2, "type": "signal", "bundle":{"name": "gmem0", "role": "0_AWLOCK" }} , 
 	{ "name": "m_axi_gmem0_0_AWCACHE", "direction": "out", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "gmem0", "role": "0_AWCACHE" }} , 
 	{ "name": "m_axi_gmem0_0_AWPROT", "direction": "out", "datatype": "sc_lv", "bitwidth":3, "type": "signal", "bundle":{"name": "gmem0", "role": "0_AWPROT" }} , 
 	{ "name": "m_axi_gmem0_0_AWQOS", "direction": "out", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "gmem0", "role": "0_AWQOS" }} , 
 	{ "name": "m_axi_gmem0_0_AWREGION", "direction": "out", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "gmem0", "role": "0_AWREGION" }} , 
 	{ "name": "m_axi_gmem0_0_AWUSER", "direction": "out", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_AWUSER" }} , 
 	{ "name": "m_axi_gmem0_0_WVALID", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_WVALID" }} , 
 	{ "name": "m_axi_gmem0_0_WREADY", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_WREADY" }} , 
 	{ "name": "m_axi_gmem0_0_WDATA", "direction": "out", "datatype": "sc_lv", "bitwidth":32, "type": "signal", "bundle":{"name": "gmem0", "role": "0_WDATA" }} , 
 	{ "name": "m_axi_gmem0_0_WSTRB", "direction": "out", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "gmem0", "role": "0_WSTRB" }} , 
 	{ "name": "m_axi_gmem0_0_WLAST", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_WLAST" }} , 
 	{ "name": "m_axi_gmem0_0_WID", "direction": "out", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_WID" }} , 
 	{ "name": "m_axi_gmem0_0_WUSER", "direction": "out", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_WUSER" }} , 
 	{ "name": "m_axi_gmem0_0_ARVALID", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_ARVALID" }} , 
 	{ "name": "m_axi_gmem0_0_ARREADY", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_ARREADY" }} , 
 	{ "name": "m_axi_gmem0_0_ARADDR", "direction": "out", "datatype": "sc_lv", "bitwidth":64, "type": "signal", "bundle":{"name": "gmem0", "role": "0_ARADDR" }} , 
 	{ "name": "m_axi_gmem0_0_ARID", "direction": "out", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_ARID" }} , 
 	{ "name": "m_axi_gmem0_0_ARLEN", "direction": "out", "datatype": "sc_lv", "bitwidth":32, "type": "signal", "bundle":{"name": "gmem0", "role": "0_ARLEN" }} , 
 	{ "name": "m_axi_gmem0_0_ARSIZE", "direction": "out", "datatype": "sc_lv", "bitwidth":3, "type": "signal", "bundle":{"name": "gmem0", "role": "0_ARSIZE" }} , 
 	{ "name": "m_axi_gmem0_0_ARBURST", "direction": "out", "datatype": "sc_lv", "bitwidth":2, "type": "signal", "bundle":{"name": "gmem0", "role": "0_ARBURST" }} , 
 	{ "name": "m_axi_gmem0_0_ARLOCK", "direction": "out", "datatype": "sc_lv", "bitwidth":2, "type": "signal", "bundle":{"name": "gmem0", "role": "0_ARLOCK" }} , 
 	{ "name": "m_axi_gmem0_0_ARCACHE", "direction": "out", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "gmem0", "role": "0_ARCACHE" }} , 
 	{ "name": "m_axi_gmem0_0_ARPROT", "direction": "out", "datatype": "sc_lv", "bitwidth":3, "type": "signal", "bundle":{"name": "gmem0", "role": "0_ARPROT" }} , 
 	{ "name": "m_axi_gmem0_0_ARQOS", "direction": "out", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "gmem0", "role": "0_ARQOS" }} , 
 	{ "name": "m_axi_gmem0_0_ARREGION", "direction": "out", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "gmem0", "role": "0_ARREGION" }} , 
 	{ "name": "m_axi_gmem0_0_ARUSER", "direction": "out", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_ARUSER" }} , 
 	{ "name": "m_axi_gmem0_0_RVALID", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_RVALID" }} , 
 	{ "name": "m_axi_gmem0_0_RREADY", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_RREADY" }} , 
 	{ "name": "m_axi_gmem0_0_RDATA", "direction": "in", "datatype": "sc_lv", "bitwidth":32, "type": "signal", "bundle":{"name": "gmem0", "role": "0_RDATA" }} , 
 	{ "name": "m_axi_gmem0_0_RLAST", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_RLAST" }} , 
 	{ "name": "m_axi_gmem0_0_RID", "direction": "in", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_RID" }} , 
 	{ "name": "m_axi_gmem0_0_RFIFONUM", "direction": "in", "datatype": "sc_lv", "bitwidth":11, "type": "signal", "bundle":{"name": "gmem0", "role": "0_RFIFONUM" }} , 
 	{ "name": "m_axi_gmem0_0_RUSER", "direction": "in", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_RUSER" }} , 
 	{ "name": "m_axi_gmem0_0_RRESP", "direction": "in", "datatype": "sc_lv", "bitwidth":2, "type": "signal", "bundle":{"name": "gmem0", "role": "0_RRESP" }} , 
 	{ "name": "m_axi_gmem0_0_BVALID", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_BVALID" }} , 
 	{ "name": "m_axi_gmem0_0_BREADY", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_BREADY" }} , 
 	{ "name": "m_axi_gmem0_0_BRESP", "direction": "in", "datatype": "sc_lv", "bitwidth":2, "type": "signal", "bundle":{"name": "gmem0", "role": "0_BRESP" }} , 
 	{ "name": "m_axi_gmem0_0_BID", "direction": "in", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_BID" }} , 
 	{ "name": "m_axi_gmem0_0_BUSER", "direction": "in", "datatype": "sc_lv", "bitwidth":1, "type": "signal", "bundle":{"name": "gmem0", "role": "0_BUSER" }} , 
 	{ "name": "status_6", "direction": "in", "datatype": "sc_lv", "bitwidth":32, "type": "signal", "bundle":{"name": "status_6", "role": "default" }} , 
 	{ "name": "sext_ln161", "direction": "in", "datatype": "sc_lv", "bitwidth":62, "type": "signal", "bundle":{"name": "sext_ln161", "role": "default" }} , 
 	{ "name": "candidate_201", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_201", "role": "default" }} , 
 	{ "name": "candidate_202", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_202", "role": "default" }} , 
 	{ "name": "candidate_203", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_203", "role": "default" }} , 
 	{ "name": "candidate_204", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_204", "role": "default" }} , 
 	{ "name": "candidate_205", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_205", "role": "default" }} , 
 	{ "name": "candidate_206", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_206", "role": "default" }} , 
 	{ "name": "candidate_207", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_207", "role": "default" }} , 
 	{ "name": "candidate_208", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_208", "role": "default" }} , 
 	{ "name": "candidate_209", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_209", "role": "default" }} , 
 	{ "name": "candidate_210", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_210", "role": "default" }} , 
 	{ "name": "candidate_211", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_211", "role": "default" }} , 
 	{ "name": "candidate_212", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_212", "role": "default" }} , 
 	{ "name": "candidate_213", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_213", "role": "default" }} , 
 	{ "name": "candidate_214", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_214", "role": "default" }} , 
 	{ "name": "candidate_215", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_215", "role": "default" }} , 
 	{ "name": "candidate_216", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_216", "role": "default" }} , 
 	{ "name": "candidate_217", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_217", "role": "default" }} , 
 	{ "name": "candidate_218", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_218", "role": "default" }} , 
 	{ "name": "candidate_219", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_219", "role": "default" }} , 
 	{ "name": "candidate_220", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_220", "role": "default" }} , 
 	{ "name": "candidate_221", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_221", "role": "default" }} , 
 	{ "name": "candidate_222", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_222", "role": "default" }} , 
 	{ "name": "candidate_223", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_223", "role": "default" }} , 
 	{ "name": "candidate_224", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_224", "role": "default" }} , 
 	{ "name": "candidate_225", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_225", "role": "default" }} , 
 	{ "name": "candidate_226", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_226", "role": "default" }} , 
 	{ "name": "candidate_227", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_227", "role": "default" }} , 
 	{ "name": "candidate_228", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_228", "role": "default" }} , 
 	{ "name": "candidate_229", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_229", "role": "default" }} , 
 	{ "name": "candidate_230", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_230", "role": "default" }} , 
 	{ "name": "candidate_231", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_231", "role": "default" }} , 
 	{ "name": "candidate_232", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_232", "role": "default" }} , 
 	{ "name": "candidate_233", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_233", "role": "default" }} , 
 	{ "name": "candidate_234", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_234", "role": "default" }} , 
 	{ "name": "candidate_235", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_235", "role": "default" }} , 
 	{ "name": "candidate_236", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_236", "role": "default" }} , 
 	{ "name": "candidate_237", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_237", "role": "default" }} , 
 	{ "name": "candidate_238", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_238", "role": "default" }} , 
 	{ "name": "candidate_239", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_239", "role": "default" }} , 
 	{ "name": "candidate_240", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_240", "role": "default" }} , 
 	{ "name": "candidate_241", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_241", "role": "default" }} , 
 	{ "name": "candidate_242", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_242", "role": "default" }} , 
 	{ "name": "candidate_243", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_243", "role": "default" }} , 
 	{ "name": "candidate_244", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_244", "role": "default" }} , 
 	{ "name": "candidate_245", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_245", "role": "default" }} , 
 	{ "name": "candidate_246", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_246", "role": "default" }} , 
 	{ "name": "candidate_247", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_247", "role": "default" }} , 
 	{ "name": "candidate_248", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_248", "role": "default" }} , 
 	{ "name": "candidate_249", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_249", "role": "default" }} , 
 	{ "name": "candidate_250", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_250", "role": "default" }} , 
 	{ "name": "candidate_251", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_251", "role": "default" }} , 
 	{ "name": "candidate_252", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_252", "role": "default" }} , 
 	{ "name": "candidate_253", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_253", "role": "default" }} , 
 	{ "name": "candidate_254", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_254", "role": "default" }} , 
 	{ "name": "candidate_255", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_255", "role": "default" }} , 
 	{ "name": "candidate_256", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_256", "role": "default" }} , 
 	{ "name": "candidate_257", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_257", "role": "default" }} , 
 	{ "name": "candidate_258", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_258", "role": "default" }} , 
 	{ "name": "candidate_259", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_259", "role": "default" }} , 
 	{ "name": "candidate_260", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_260", "role": "default" }} , 
 	{ "name": "candidate_261", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_261", "role": "default" }} , 
 	{ "name": "candidate_262", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_262", "role": "default" }} , 
 	{ "name": "candidate_263", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_263", "role": "default" }} , 
 	{ "name": "candidate_264", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_264", "role": "default" }} , 
 	{ "name": "candidate_265", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_265", "role": "default" }} , 
 	{ "name": "candidate_266", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_266", "role": "default" }} , 
 	{ "name": "candidate_267", "direction": "in", "datatype": "sc_lv", "bitwidth":29, "type": "signal", "bundle":{"name": "candidate_267", "role": "default" }}  ]}

set ArgLastReadFirstWriteLatency {
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
	{"Name" : "Latency", "Min" : "69", "Max" : "69"}
	, {"Name" : "Interval", "Min" : "68", "Max" : "68"}
]}

set PipelineEnableSignalInfo {[
	{"Pipeline" : "0", "EnableSignal" : "ap_enable_pp0"}
]}

set Spec2ImplPortList { 
	 { m_axi {  { m_axi_gmem0_0_AWVALID VALID 1 1 }  { m_axi_gmem0_0_AWREADY READY 0 1 }  { m_axi_gmem0_0_AWADDR ADDR 1 64 }  { m_axi_gmem0_0_AWID ID 1 1 }  { m_axi_gmem0_0_AWLEN SIZE 1 32 }  { m_axi_gmem0_0_AWSIZE BURST 1 3 }  { m_axi_gmem0_0_AWBURST LOCK 1 2 }  { m_axi_gmem0_0_AWLOCK CACHE 1 2 }  { m_axi_gmem0_0_AWCACHE PROT 1 4 }  { m_axi_gmem0_0_AWPROT QOS 1 3 }  { m_axi_gmem0_0_AWQOS REGION 1 4 }  { m_axi_gmem0_0_AWREGION USER 1 4 }  { m_axi_gmem0_0_AWUSER DATA 1 1 }  { m_axi_gmem0_0_WVALID VALID 1 1 }  { m_axi_gmem0_0_WREADY READY 0 1 }  { m_axi_gmem0_0_WDATA FIFONUM 1 32 }  { m_axi_gmem0_0_WSTRB STRB 1 4 }  { m_axi_gmem0_0_WLAST LAST 1 1 }  { m_axi_gmem0_0_WID ID 1 1 }  { m_axi_gmem0_0_WUSER DATA 1 1 }  { m_axi_gmem0_0_ARVALID VALID 1 1 }  { m_axi_gmem0_0_ARREADY READY 0 1 }  { m_axi_gmem0_0_ARADDR ADDR 1 64 }  { m_axi_gmem0_0_ARID ID 1 1 }  { m_axi_gmem0_0_ARLEN SIZE 1 32 }  { m_axi_gmem0_0_ARSIZE BURST 1 3 }  { m_axi_gmem0_0_ARBURST LOCK 1 2 }  { m_axi_gmem0_0_ARLOCK CACHE 1 2 }  { m_axi_gmem0_0_ARCACHE PROT 1 4 }  { m_axi_gmem0_0_ARPROT QOS 1 3 }  { m_axi_gmem0_0_ARQOS REGION 1 4 }  { m_axi_gmem0_0_ARREGION USER 1 4 }  { m_axi_gmem0_0_ARUSER DATA 1 1 }  { m_axi_gmem0_0_RVALID VALID 0 1 }  { m_axi_gmem0_0_RREADY READY 1 1 }  { m_axi_gmem0_0_RDATA FIFONUM 0 32 }  { m_axi_gmem0_0_RLAST LAST 0 1 }  { m_axi_gmem0_0_RID ID 0 1 }  { m_axi_gmem0_0_RFIFONUM LEN 0 11 }  { m_axi_gmem0_0_RUSER DATA 0 1 }  { m_axi_gmem0_0_RRESP RESP 0 2 }  { m_axi_gmem0_0_BVALID VALID 0 1 }  { m_axi_gmem0_0_BREADY READY 1 1 }  { m_axi_gmem0_0_BRESP RESP 0 2 }  { m_axi_gmem0_0_BID ID 0 1 }  { m_axi_gmem0_0_BUSER DATA 0 1 } } }
	status_6 { ap_none {  { status_6 in_data 0 32 } } }
	sext_ln161 { ap_none {  { sext_ln161 in_data 0 62 } } }
	candidate_201 { ap_none {  { candidate_201 in_data 0 29 } } }
	candidate_202 { ap_none {  { candidate_202 in_data 0 29 } } }
	candidate_203 { ap_none {  { candidate_203 in_data 0 29 } } }
	candidate_204 { ap_none {  { candidate_204 in_data 0 29 } } }
	candidate_205 { ap_none {  { candidate_205 in_data 0 29 } } }
	candidate_206 { ap_none {  { candidate_206 in_data 0 29 } } }
	candidate_207 { ap_none {  { candidate_207 in_data 0 29 } } }
	candidate_208 { ap_none {  { candidate_208 in_data 0 29 } } }
	candidate_209 { ap_none {  { candidate_209 in_data 0 29 } } }
	candidate_210 { ap_none {  { candidate_210 in_data 0 29 } } }
	candidate_211 { ap_none {  { candidate_211 in_data 0 29 } } }
	candidate_212 { ap_none {  { candidate_212 in_data 0 29 } } }
	candidate_213 { ap_none {  { candidate_213 in_data 0 29 } } }
	candidate_214 { ap_none {  { candidate_214 in_data 0 29 } } }
	candidate_215 { ap_none {  { candidate_215 in_data 0 29 } } }
	candidate_216 { ap_none {  { candidate_216 in_data 0 29 } } }
	candidate_217 { ap_none {  { candidate_217 in_data 0 29 } } }
	candidate_218 { ap_none {  { candidate_218 in_data 0 29 } } }
	candidate_219 { ap_none {  { candidate_219 in_data 0 29 } } }
	candidate_220 { ap_none {  { candidate_220 in_data 0 29 } } }
	candidate_221 { ap_none {  { candidate_221 in_data 0 29 } } }
	candidate_222 { ap_none {  { candidate_222 in_data 0 29 } } }
	candidate_223 { ap_none {  { candidate_223 in_data 0 29 } } }
	candidate_224 { ap_none {  { candidate_224 in_data 0 29 } } }
	candidate_225 { ap_none {  { candidate_225 in_data 0 29 } } }
	candidate_226 { ap_none {  { candidate_226 in_data 0 29 } } }
	candidate_227 { ap_none {  { candidate_227 in_data 0 29 } } }
	candidate_228 { ap_none {  { candidate_228 in_data 0 29 } } }
	candidate_229 { ap_none {  { candidate_229 in_data 0 29 } } }
	candidate_230 { ap_none {  { candidate_230 in_data 0 29 } } }
	candidate_231 { ap_none {  { candidate_231 in_data 0 29 } } }
	candidate_232 { ap_none {  { candidate_232 in_data 0 29 } } }
	candidate_233 { ap_none {  { candidate_233 in_data 0 29 } } }
	candidate_234 { ap_none {  { candidate_234 in_data 0 29 } } }
	candidate_235 { ap_none {  { candidate_235 in_data 0 29 } } }
	candidate_236 { ap_none {  { candidate_236 in_data 0 29 } } }
	candidate_237 { ap_none {  { candidate_237 in_data 0 29 } } }
	candidate_238 { ap_none {  { candidate_238 in_data 0 29 } } }
	candidate_239 { ap_none {  { candidate_239 in_data 0 29 } } }
	candidate_240 { ap_none {  { candidate_240 in_data 0 29 } } }
	candidate_241 { ap_none {  { candidate_241 in_data 0 29 } } }
	candidate_242 { ap_none {  { candidate_242 in_data 0 29 } } }
	candidate_243 { ap_none {  { candidate_243 in_data 0 29 } } }
	candidate_244 { ap_none {  { candidate_244 in_data 0 29 } } }
	candidate_245 { ap_none {  { candidate_245 in_data 0 29 } } }
	candidate_246 { ap_none {  { candidate_246 in_data 0 29 } } }
	candidate_247 { ap_none {  { candidate_247 in_data 0 29 } } }
	candidate_248 { ap_none {  { candidate_248 in_data 0 29 } } }
	candidate_249 { ap_none {  { candidate_249 in_data 0 29 } } }
	candidate_250 { ap_none {  { candidate_250 in_data 0 29 } } }
	candidate_251 { ap_none {  { candidate_251 in_data 0 29 } } }
	candidate_252 { ap_none {  { candidate_252 in_data 0 29 } } }
	candidate_253 { ap_none {  { candidate_253 in_data 0 29 } } }
	candidate_254 { ap_none {  { candidate_254 in_data 0 29 } } }
	candidate_255 { ap_none {  { candidate_255 in_data 0 29 } } }
	candidate_256 { ap_none {  { candidate_256 in_data 0 29 } } }
	candidate_257 { ap_none {  { candidate_257 in_data 0 29 } } }
	candidate_258 { ap_none {  { candidate_258 in_data 0 29 } } }
	candidate_259 { ap_none {  { candidate_259 in_data 0 29 } } }
	candidate_260 { ap_none {  { candidate_260 in_data 0 29 } } }
	candidate_261 { ap_none {  { candidate_261 in_data 0 29 } } }
	candidate_262 { ap_none {  { candidate_262 in_data 0 29 } } }
	candidate_263 { ap_none {  { candidate_263 in_data 0 29 } } }
	candidate_264 { ap_none {  { candidate_264 in_data 0 29 } } }
	candidate_265 { ap_none {  { candidate_265 in_data 0 29 } } }
	candidate_266 { ap_none {  { candidate_266 in_data 0 29 } } }
	candidate_267 { ap_none {  { candidate_267 in_data 0 29 } } }
}

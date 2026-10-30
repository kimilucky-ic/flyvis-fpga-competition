set SynModuleInfo {
  {SRCNAME flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_67_1 MODELNAME flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_67_1 RTLNAME flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_67_1
    SUBMODULES {
      {MODELNAME flyvis_t5c_source_raw_flow_control_loop_pipe_sequential_init RTLNAME flyvis_t5c_source_raw_flow_control_loop_pipe_sequential_init BINDTYPE interface TYPE internal_upc_flow_control INSTNAME flyvis_t5c_source_raw_flow_control_loop_pipe_sequential_init_U}
    }
  }
  {SRCNAME flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_85_2 MODELNAME flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_85_2 RTLNAME flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_85_2}
  {SRCNAME flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_93_3 MODELNAME flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_93_3 RTLNAME flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_93_3
    SUBMODULES {
      {MODELNAME flyvis_t5c_source_raw_mul_28ns_22s_50_1_1 RTLNAME flyvis_t5c_source_raw_mul_28ns_22s_50_1_1 BINDTYPE op TYPE mul IMPL auto LATENCY 0 ALLOW_PRAGMA 1}
      {MODELNAME flyvis_t5c_source_raw_sparsemux_135_7_29_1_1 RTLNAME flyvis_t5c_source_raw_sparsemux_135_7_29_1_1 BINDTYPE op TYPE sparsemux IMPL compactencoding_dontcare}
      {MODELNAME flyvis_t5c_source_raw_sparsemux_135_7_48_1_1 RTLNAME flyvis_t5c_source_raw_sparsemux_135_7_48_1_1 BINDTYPE op TYPE sparsemux IMPL compactencoding_dontcare}
      {MODELNAME flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_93_3_FLYVIS_EDGE_SRC_ROM_AUTO_1R RTLNAME flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_93_3_FLYVIS_EDGE_SRC_ROM_AUTO_1R BINDTYPE storage TYPE rom IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_93_3_FLYVIS_EDGE_WEIGHT_Q20_ROM_AUTbkb RTLNAME flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_93_3_FLYVIS_EDGE_WEIGHT_Q20_ROM_AUTbkb BINDTYPE storage TYPE rom IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_93_3_FLYVIS_EDGE_DST_ROM_AUTO_1R RTLNAME flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_93_3_FLYVIS_EDGE_DST_ROM_AUTO_1R BINDTYPE storage TYPE rom IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
    }
  }
  {SRCNAME flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_124_4 MODELNAME flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_124_4 RTLNAME flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_124_4
    SUBMODULES {
      {MODELNAME flyvis_t5c_source_raw_mul_29s_16ns_45_1_1 RTLNAME flyvis_t5c_source_raw_mul_29s_16ns_45_1_1 BINDTYPE op TYPE mul IMPL auto LATENCY 0 ALLOW_PRAGMA 1}
      {MODELNAME flyvis_t5c_source_raw_mul_31s_28ns_59_1_1 RTLNAME flyvis_t5c_source_raw_mul_31s_28ns_59_1_1 BINDTYPE op TYPE mul IMPL auto LATENCY 0 ALLOW_PRAGMA 1}
      {MODELNAME flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_124_4_FLYVIS_BIAS_Q22_ROM_AUTO_1R RTLNAME flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_124_4_FLYVIS_BIAS_Q22_ROM_AUTO_1R BINDTYPE storage TYPE rom IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_124_4_FLYVIS_INVTau_Q22_ROM_AUTO_1R RTLNAME flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_124_4_FLYVIS_INVTau_Q22_ROM_AUTO_1R BINDTYPE storage TYPE rom IMPL auto LATENCY 2 ALLOW_PRAGMA 1}
    }
  }
  {SRCNAME flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_161_5 MODELNAME flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_161_5 RTLNAME flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_161_5}
  {SRCNAME flyvis_t5c_source_raw MODELNAME flyvis_t5c_source_raw RTLNAME flyvis_t5c_source_raw IS_TOP 1
    SUBMODULES {
      {MODELNAME flyvis_t5c_source_raw_boundary_RAM_1P_BRAM_1R1W RTLNAME flyvis_t5c_source_raw_boundary_RAM_1P_BRAM_1R1W BINDTYPE storage TYPE ram_1p IMPL bram LATENCY 2 ALLOW_PRAGMA 1}
      {MODELNAME flyvis_t5c_source_raw_gmem0_m_axi RTLNAME flyvis_t5c_source_raw_gmem0_m_axi BINDTYPE interface TYPE adapter IMPL m_axi}
      {MODELNAME flyvis_t5c_source_raw_control_s_axi RTLNAME flyvis_t5c_source_raw_control_s_axi BINDTYPE interface TYPE interface_s_axilite}
    }
  }
}

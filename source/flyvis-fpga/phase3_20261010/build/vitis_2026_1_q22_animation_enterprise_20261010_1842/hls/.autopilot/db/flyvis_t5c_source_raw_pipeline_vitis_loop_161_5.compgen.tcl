# This script segment is generated automatically by AutoPilot

# clear list
if {${::AESL::PGuard_autoexp_gen}} {
    cg_default_interface_gen_dc_begin
    cg_default_interface_gen_bundle_begin
    AESL_LIB_XILADAPTER::native_axis_begin
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 831 \
    name gmem0 \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_gmem0 \
    op interface \
    ports { m_axi_gmem0_0_AWVALID { O 1 bit } m_axi_gmem0_0_AWREADY { I 1 bit } m_axi_gmem0_0_AWADDR { O 64 vector } m_axi_gmem0_0_AWID { O 1 vector } m_axi_gmem0_0_AWLEN { O 32 vector } m_axi_gmem0_0_AWSIZE { O 3 vector } m_axi_gmem0_0_AWBURST { O 2 vector } m_axi_gmem0_0_AWLOCK { O 2 vector } m_axi_gmem0_0_AWCACHE { O 4 vector } m_axi_gmem0_0_AWPROT { O 3 vector } m_axi_gmem0_0_AWQOS { O 4 vector } m_axi_gmem0_0_AWREGION { O 4 vector } m_axi_gmem0_0_AWUSER { O 1 vector } m_axi_gmem0_0_WVALID { O 1 bit } m_axi_gmem0_0_WREADY { I 1 bit } m_axi_gmem0_0_WDATA { O 32 vector } m_axi_gmem0_0_WSTRB { O 4 vector } m_axi_gmem0_0_WLAST { O 1 bit } m_axi_gmem0_0_WID { O 1 vector } m_axi_gmem0_0_WUSER { O 1 vector } m_axi_gmem0_0_ARVALID { O 1 bit } m_axi_gmem0_0_ARREADY { I 1 bit } m_axi_gmem0_0_ARADDR { O 64 vector } m_axi_gmem0_0_ARID { O 1 vector } m_axi_gmem0_0_ARLEN { O 32 vector } m_axi_gmem0_0_ARSIZE { O 3 vector } m_axi_gmem0_0_ARBURST { O 2 vector } m_axi_gmem0_0_ARLOCK { O 2 vector } m_axi_gmem0_0_ARCACHE { O 4 vector } m_axi_gmem0_0_ARPROT { O 3 vector } m_axi_gmem0_0_ARQOS { O 4 vector } m_axi_gmem0_0_ARREGION { O 4 vector } m_axi_gmem0_0_ARUSER { O 1 vector } m_axi_gmem0_0_RVALID { I 1 bit } m_axi_gmem0_0_RREADY { O 1 bit } m_axi_gmem0_0_RDATA { I 32 vector } m_axi_gmem0_0_RLAST { I 1 bit } m_axi_gmem0_0_RID { I 1 vector } m_axi_gmem0_0_RFIFONUM { I 11 vector } m_axi_gmem0_0_RUSER { I 1 vector } m_axi_gmem0_0_RRESP { I 2 vector } m_axi_gmem0_0_BVALID { I 1 bit } m_axi_gmem0_0_BREADY { O 1 bit } m_axi_gmem0_0_BRESP { I 2 vector } m_axi_gmem0_0_BID { I 1 vector } m_axi_gmem0_0_BUSER { I 1 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 832 \
    name status_6 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_status_6 \
    op interface \
    ports { status_6 { I 32 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 833 \
    name sext_ln161 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_sext_ln161 \
    op interface \
    ports { sext_ln161 { I 62 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 834 \
    name candidate_201 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_201 \
    op interface \
    ports { candidate_201 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 835 \
    name candidate_202 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_202 \
    op interface \
    ports { candidate_202 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 836 \
    name candidate_203 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_203 \
    op interface \
    ports { candidate_203 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 837 \
    name candidate_204 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_204 \
    op interface \
    ports { candidate_204 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 838 \
    name candidate_205 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_205 \
    op interface \
    ports { candidate_205 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 839 \
    name candidate_206 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_206 \
    op interface \
    ports { candidate_206 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 840 \
    name candidate_207 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_207 \
    op interface \
    ports { candidate_207 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 841 \
    name candidate_208 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_208 \
    op interface \
    ports { candidate_208 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 842 \
    name candidate_209 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_209 \
    op interface \
    ports { candidate_209 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 843 \
    name candidate_210 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_210 \
    op interface \
    ports { candidate_210 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 844 \
    name candidate_211 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_211 \
    op interface \
    ports { candidate_211 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 845 \
    name candidate_212 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_212 \
    op interface \
    ports { candidate_212 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 846 \
    name candidate_213 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_213 \
    op interface \
    ports { candidate_213 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 847 \
    name candidate_214 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_214 \
    op interface \
    ports { candidate_214 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 848 \
    name candidate_215 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_215 \
    op interface \
    ports { candidate_215 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 849 \
    name candidate_216 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_216 \
    op interface \
    ports { candidate_216 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 850 \
    name candidate_217 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_217 \
    op interface \
    ports { candidate_217 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 851 \
    name candidate_218 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_218 \
    op interface \
    ports { candidate_218 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 852 \
    name candidate_219 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_219 \
    op interface \
    ports { candidate_219 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 853 \
    name candidate_220 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_220 \
    op interface \
    ports { candidate_220 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 854 \
    name candidate_221 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_221 \
    op interface \
    ports { candidate_221 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 855 \
    name candidate_222 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_222 \
    op interface \
    ports { candidate_222 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 856 \
    name candidate_223 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_223 \
    op interface \
    ports { candidate_223 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 857 \
    name candidate_224 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_224 \
    op interface \
    ports { candidate_224 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 858 \
    name candidate_225 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_225 \
    op interface \
    ports { candidate_225 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 859 \
    name candidate_226 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_226 \
    op interface \
    ports { candidate_226 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 860 \
    name candidate_227 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_227 \
    op interface \
    ports { candidate_227 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 861 \
    name candidate_228 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_228 \
    op interface \
    ports { candidate_228 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 862 \
    name candidate_229 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_229 \
    op interface \
    ports { candidate_229 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 863 \
    name candidate_230 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_230 \
    op interface \
    ports { candidate_230 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 864 \
    name candidate_231 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_231 \
    op interface \
    ports { candidate_231 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 865 \
    name candidate_232 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_232 \
    op interface \
    ports { candidate_232 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 866 \
    name candidate_233 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_233 \
    op interface \
    ports { candidate_233 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 867 \
    name candidate_234 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_234 \
    op interface \
    ports { candidate_234 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 868 \
    name candidate_235 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_235 \
    op interface \
    ports { candidate_235 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 869 \
    name candidate_236 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_236 \
    op interface \
    ports { candidate_236 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 870 \
    name candidate_237 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_237 \
    op interface \
    ports { candidate_237 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 871 \
    name candidate_238 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_238 \
    op interface \
    ports { candidate_238 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 872 \
    name candidate_239 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_239 \
    op interface \
    ports { candidate_239 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 873 \
    name candidate_240 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_240 \
    op interface \
    ports { candidate_240 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 874 \
    name candidate_241 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_241 \
    op interface \
    ports { candidate_241 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 875 \
    name candidate_242 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_242 \
    op interface \
    ports { candidate_242 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 876 \
    name candidate_243 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_243 \
    op interface \
    ports { candidate_243 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 877 \
    name candidate_244 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_244 \
    op interface \
    ports { candidate_244 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 878 \
    name candidate_245 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_245 \
    op interface \
    ports { candidate_245 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 879 \
    name candidate_246 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_246 \
    op interface \
    ports { candidate_246 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 880 \
    name candidate_247 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_247 \
    op interface \
    ports { candidate_247 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 881 \
    name candidate_248 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_248 \
    op interface \
    ports { candidate_248 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 882 \
    name candidate_249 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_249 \
    op interface \
    ports { candidate_249 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 883 \
    name candidate_250 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_250 \
    op interface \
    ports { candidate_250 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 884 \
    name candidate_251 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_251 \
    op interface \
    ports { candidate_251 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 885 \
    name candidate_252 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_252 \
    op interface \
    ports { candidate_252 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 886 \
    name candidate_253 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_253 \
    op interface \
    ports { candidate_253 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 887 \
    name candidate_254 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_254 \
    op interface \
    ports { candidate_254 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 888 \
    name candidate_255 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_255 \
    op interface \
    ports { candidate_255 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 889 \
    name candidate_256 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_256 \
    op interface \
    ports { candidate_256 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 890 \
    name candidate_257 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_257 \
    op interface \
    ports { candidate_257 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 891 \
    name candidate_258 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_258 \
    op interface \
    ports { candidate_258 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 892 \
    name candidate_259 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_259 \
    op interface \
    ports { candidate_259 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 893 \
    name candidate_260 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_260 \
    op interface \
    ports { candidate_260 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 894 \
    name candidate_261 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_261 \
    op interface \
    ports { candidate_261 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 895 \
    name candidate_262 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_262 \
    op interface \
    ports { candidate_262 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 896 \
    name candidate_263 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_263 \
    op interface \
    ports { candidate_263 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 897 \
    name candidate_264 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_264 \
    op interface \
    ports { candidate_264 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 898 \
    name candidate_265 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_265 \
    op interface \
    ports { candidate_265 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 899 \
    name candidate_266 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_266 \
    op interface \
    ports { candidate_266 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 900 \
    name candidate_267 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_267 \
    op interface \
    ports { candidate_267 { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id -1 \
    name ap_ctrl \
    type ap_ctrl \
    reset_level 1 \
    sync_rst true \
    corename ap_ctrl \
    op interface \
    ports { ap_start { I 1 bit } ap_ready { O 1 bit } ap_done { O 1 bit } ap_idle { O 1 bit } } \
} "
}


# Adapter definition:
set PortName ap_clk
set DataWd 1 
if {${::AESL::PGuard_autoexp_gen}} {
if {[info proc cg_default_interface_gen_clock] == "cg_default_interface_gen_clock"} {
eval "cg_default_interface_gen_clock { \
    id -2 \
    name ${PortName} \
    reset_level 1 \
    sync_rst true \
    corename apif_ap_clk \
    data_wd ${DataWd} \
    op interface \
}"
} else {
puts "@W \[IMPL-113\] Cannot find bus interface model in the library. Ignored generation of bus interface for '${PortName}'"
}
}


# Adapter definition:
set PortName ap_rst
set DataWd 1 
if {${::AESL::PGuard_autoexp_gen}} {
if {[info proc cg_default_interface_gen_reset] == "cg_default_interface_gen_reset"} {
eval "cg_default_interface_gen_reset { \
    id -3 \
    name ${PortName} \
    reset_level 1 \
    sync_rst true \
    corename apif_ap_rst \
    data_wd ${DataWd} \
    op interface \
}"
} else {
puts "@W \[IMPL-114\] Cannot find bus interface model in the library. Ignored generation of bus interface for '${PortName}'"
}
}



# merge
if {${::AESL::PGuard_autoexp_gen}} {
    cg_default_interface_gen_dc_end
    cg_default_interface_gen_bundle_end
    AESL_LIB_XILADAPTER::native_axis_end
}


# flow_control definition:
set InstName flyvis_t5c_source_raw_flow_control_loop_pipe_sequential_init_U
set CompName flyvis_t5c_source_raw_flow_control_loop_pipe_sequential_init
set name flow_control_loop_pipe_sequential_init
if {${::AESL::PGuard_autocg_gen} && ${::AESL::PGuard_autocg_ipmgen}} {
if {[info proc ::AESL_LIB_VIRTEX::xil_gen_UPC_flow_control] == "::AESL_LIB_VIRTEX::xil_gen_UPC_flow_control"} {
eval "::AESL_LIB_VIRTEX::xil_gen_UPC_flow_control { \
    name ${name} \
    prefix flyvis_t5c_source_raw_ \
}"
} else {
puts "@W \[IMPL-107\] Cannot find ::AESL_LIB_VIRTEX::xil_gen_UPC_flow_control, check your platform lib"
}
}


if {${::AESL::PGuard_rtl_comp_handler}} {
	::AP::rtl_comp_handler $CompName BINDTYPE interface TYPE internal_upc_flow_control INSTNAME $InstName
}



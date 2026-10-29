# This script segment is generated automatically by AutoPilot

# clear list
if {${::AESL::PGuard_autoexp_gen}} {
    cg_default_interface_gen_dc_begin
    cg_default_interface_gen_bundle_begin
    AESL_LIB_XILADAPTER::native_axis_begin
}

# XIL_BRAM:
if {${::AESL::PGuard_autoexp_gen}} {
if {[info proc ::AESL_LIB_XILADAPTER::xil_bram_gen] == "::AESL_LIB_XILADAPTER::xil_bram_gen"} {
eval "::AESL_LIB_XILADAPTER::xil_bram_gen { \
    id 2 \
    name boundary \
    reset_level 1 \
    sync_rst true \
    dir O \
    corename boundary \
    op interface \
    ports { boundary_address0 { O 11 vector } boundary_ce0 { O 1 bit } boundary_we0 { O 1 bit } boundary_d0 { O 29 vector } } \
} "
} else {
puts "@W \[IMPL-110\] Cannot find bus interface model in the library. Ignored generation of bus interface for 'boundary'"
}
}


# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 1 \
    name gmem0 \
    type other \
    dir I \
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
    id 3 \
    name sext_ln67 \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_sext_ln67 \
    op interface \
    ports { sext_ln67 { I 62 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 4 \
    name x_h_66_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_66_out \
    op interface \
    ports { x_h_66_out { O 29 vector } x_h_66_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 5 \
    name x_h_65_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_65_out \
    op interface \
    ports { x_h_65_out { O 29 vector } x_h_65_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 6 \
    name x_h_64_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_64_out \
    op interface \
    ports { x_h_64_out { O 29 vector } x_h_64_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 7 \
    name x_h_63_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_63_out \
    op interface \
    ports { x_h_63_out { O 29 vector } x_h_63_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 8 \
    name x_h_62_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_62_out \
    op interface \
    ports { x_h_62_out { O 29 vector } x_h_62_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 9 \
    name x_h_61_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_61_out \
    op interface \
    ports { x_h_61_out { O 29 vector } x_h_61_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 10 \
    name x_h_60_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_60_out \
    op interface \
    ports { x_h_60_out { O 29 vector } x_h_60_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 11 \
    name x_h_59_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_59_out \
    op interface \
    ports { x_h_59_out { O 29 vector } x_h_59_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 12 \
    name x_h_58_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_58_out \
    op interface \
    ports { x_h_58_out { O 29 vector } x_h_58_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 13 \
    name x_h_57_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_57_out \
    op interface \
    ports { x_h_57_out { O 29 vector } x_h_57_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 14 \
    name x_h_56_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_56_out \
    op interface \
    ports { x_h_56_out { O 29 vector } x_h_56_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 15 \
    name x_h_55_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_55_out \
    op interface \
    ports { x_h_55_out { O 29 vector } x_h_55_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 16 \
    name x_h_54_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_54_out \
    op interface \
    ports { x_h_54_out { O 29 vector } x_h_54_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 17 \
    name x_h_53_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_53_out \
    op interface \
    ports { x_h_53_out { O 29 vector } x_h_53_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 18 \
    name x_h_52_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_52_out \
    op interface \
    ports { x_h_52_out { O 29 vector } x_h_52_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 19 \
    name x_h_51_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_51_out \
    op interface \
    ports { x_h_51_out { O 29 vector } x_h_51_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 20 \
    name x_h_50_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_50_out \
    op interface \
    ports { x_h_50_out { O 29 vector } x_h_50_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 21 \
    name x_h_49_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_49_out \
    op interface \
    ports { x_h_49_out { O 29 vector } x_h_49_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 22 \
    name x_h_48_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_48_out \
    op interface \
    ports { x_h_48_out { O 29 vector } x_h_48_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 23 \
    name x_h_47_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_47_out \
    op interface \
    ports { x_h_47_out { O 29 vector } x_h_47_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 24 \
    name x_h_46_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_46_out \
    op interface \
    ports { x_h_46_out { O 29 vector } x_h_46_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 25 \
    name x_h_45_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_45_out \
    op interface \
    ports { x_h_45_out { O 29 vector } x_h_45_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 26 \
    name x_h_44_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_44_out \
    op interface \
    ports { x_h_44_out { O 29 vector } x_h_44_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 27 \
    name x_h_43_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_43_out \
    op interface \
    ports { x_h_43_out { O 29 vector } x_h_43_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 28 \
    name x_h_42_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_42_out \
    op interface \
    ports { x_h_42_out { O 29 vector } x_h_42_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 29 \
    name x_h_41_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_41_out \
    op interface \
    ports { x_h_41_out { O 29 vector } x_h_41_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 30 \
    name x_h_40_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_40_out \
    op interface \
    ports { x_h_40_out { O 29 vector } x_h_40_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 31 \
    name x_h_39_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_39_out \
    op interface \
    ports { x_h_39_out { O 29 vector } x_h_39_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 32 \
    name x_h_38_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_38_out \
    op interface \
    ports { x_h_38_out { O 29 vector } x_h_38_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 33 \
    name x_h_37_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_37_out \
    op interface \
    ports { x_h_37_out { O 29 vector } x_h_37_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 34 \
    name x_h_36_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_36_out \
    op interface \
    ports { x_h_36_out { O 29 vector } x_h_36_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 35 \
    name x_h_35_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_35_out \
    op interface \
    ports { x_h_35_out { O 29 vector } x_h_35_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 36 \
    name x_h_34_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_34_out \
    op interface \
    ports { x_h_34_out { O 29 vector } x_h_34_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 37 \
    name x_h_33_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_33_out \
    op interface \
    ports { x_h_33_out { O 29 vector } x_h_33_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 38 \
    name x_h_32_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_32_out \
    op interface \
    ports { x_h_32_out { O 29 vector } x_h_32_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 39 \
    name x_h_31_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_31_out \
    op interface \
    ports { x_h_31_out { O 29 vector } x_h_31_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 40 \
    name x_h_30_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_30_out \
    op interface \
    ports { x_h_30_out { O 29 vector } x_h_30_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 41 \
    name x_h_29_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_29_out \
    op interface \
    ports { x_h_29_out { O 29 vector } x_h_29_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 42 \
    name x_h_28_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_28_out \
    op interface \
    ports { x_h_28_out { O 29 vector } x_h_28_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 43 \
    name x_h_27_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_27_out \
    op interface \
    ports { x_h_27_out { O 29 vector } x_h_27_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 44 \
    name x_h_26_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_26_out \
    op interface \
    ports { x_h_26_out { O 29 vector } x_h_26_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 45 \
    name x_h_25_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_25_out \
    op interface \
    ports { x_h_25_out { O 29 vector } x_h_25_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 46 \
    name x_h_24_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_24_out \
    op interface \
    ports { x_h_24_out { O 29 vector } x_h_24_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 47 \
    name x_h_23_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_23_out \
    op interface \
    ports { x_h_23_out { O 29 vector } x_h_23_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 48 \
    name x_h_22_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_22_out \
    op interface \
    ports { x_h_22_out { O 29 vector } x_h_22_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 49 \
    name x_h_21_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_21_out \
    op interface \
    ports { x_h_21_out { O 29 vector } x_h_21_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 50 \
    name x_h_20_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_20_out \
    op interface \
    ports { x_h_20_out { O 29 vector } x_h_20_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 51 \
    name x_h_19_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_19_out \
    op interface \
    ports { x_h_19_out { O 29 vector } x_h_19_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 52 \
    name x_h_18_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_18_out \
    op interface \
    ports { x_h_18_out { O 29 vector } x_h_18_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 53 \
    name x_h_17_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_17_out \
    op interface \
    ports { x_h_17_out { O 29 vector } x_h_17_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 54 \
    name x_h_16_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_16_out \
    op interface \
    ports { x_h_16_out { O 29 vector } x_h_16_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 55 \
    name x_h_15_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_15_out \
    op interface \
    ports { x_h_15_out { O 29 vector } x_h_15_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 56 \
    name x_h_14_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_14_out \
    op interface \
    ports { x_h_14_out { O 29 vector } x_h_14_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 57 \
    name x_h_13_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_13_out \
    op interface \
    ports { x_h_13_out { O 29 vector } x_h_13_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 58 \
    name x_h_12_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_12_out \
    op interface \
    ports { x_h_12_out { O 29 vector } x_h_12_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 59 \
    name x_h_11_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_11_out \
    op interface \
    ports { x_h_11_out { O 29 vector } x_h_11_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 60 \
    name x_h_10_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_10_out \
    op interface \
    ports { x_h_10_out { O 29 vector } x_h_10_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 61 \
    name x_h_9_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_9_out \
    op interface \
    ports { x_h_9_out { O 29 vector } x_h_9_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 62 \
    name x_h_8_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_8_out \
    op interface \
    ports { x_h_8_out { O 29 vector } x_h_8_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 63 \
    name x_h_7_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_7_out \
    op interface \
    ports { x_h_7_out { O 29 vector } x_h_7_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 64 \
    name x_h_6_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_6_out \
    op interface \
    ports { x_h_6_out { O 29 vector } x_h_6_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 65 \
    name x_h_5_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_5_out \
    op interface \
    ports { x_h_5_out { O 29 vector } x_h_5_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 66 \
    name x_h_4_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_4_out \
    op interface \
    ports { x_h_4_out { O 29 vector } x_h_4_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 67 \
    name x_h_3_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_3_out \
    op interface \
    ports { x_h_3_out { O 29 vector } x_h_3_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 68 \
    name x_h_2_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_2_out \
    op interface \
    ports { x_h_2_out { O 29 vector } x_h_2_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 69 \
    name x_h_1_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_1_out \
    op interface \
    ports { x_h_1_out { O 29 vector } x_h_1_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 70 \
    name x_h_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_out \
    op interface \
    ports { x_h_out { O 29 vector } x_h_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 71 \
    name old_h_66_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_66_out \
    op interface \
    ports { old_h_66_out { O 29 vector } old_h_66_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 72 \
    name old_h_65_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_65_out \
    op interface \
    ports { old_h_65_out { O 29 vector } old_h_65_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 73 \
    name old_h_64_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_64_out \
    op interface \
    ports { old_h_64_out { O 29 vector } old_h_64_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 74 \
    name old_h_63_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_63_out \
    op interface \
    ports { old_h_63_out { O 29 vector } old_h_63_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 75 \
    name old_h_62_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_62_out \
    op interface \
    ports { old_h_62_out { O 29 vector } old_h_62_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 76 \
    name old_h_61_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_61_out \
    op interface \
    ports { old_h_61_out { O 29 vector } old_h_61_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 77 \
    name old_h_60_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_60_out \
    op interface \
    ports { old_h_60_out { O 29 vector } old_h_60_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 78 \
    name old_h_59_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_59_out \
    op interface \
    ports { old_h_59_out { O 29 vector } old_h_59_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 79 \
    name old_h_58_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_58_out \
    op interface \
    ports { old_h_58_out { O 29 vector } old_h_58_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 80 \
    name old_h_57_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_57_out \
    op interface \
    ports { old_h_57_out { O 29 vector } old_h_57_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 81 \
    name old_h_56_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_56_out \
    op interface \
    ports { old_h_56_out { O 29 vector } old_h_56_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 82 \
    name old_h_55_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_55_out \
    op interface \
    ports { old_h_55_out { O 29 vector } old_h_55_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 83 \
    name old_h_54_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_54_out \
    op interface \
    ports { old_h_54_out { O 29 vector } old_h_54_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 84 \
    name old_h_53_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_53_out \
    op interface \
    ports { old_h_53_out { O 29 vector } old_h_53_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 85 \
    name old_h_52_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_52_out \
    op interface \
    ports { old_h_52_out { O 29 vector } old_h_52_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 86 \
    name old_h_51_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_51_out \
    op interface \
    ports { old_h_51_out { O 29 vector } old_h_51_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 87 \
    name old_h_50_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_50_out \
    op interface \
    ports { old_h_50_out { O 29 vector } old_h_50_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 88 \
    name old_h_49_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_49_out \
    op interface \
    ports { old_h_49_out { O 29 vector } old_h_49_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 89 \
    name old_h_48_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_48_out \
    op interface \
    ports { old_h_48_out { O 29 vector } old_h_48_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 90 \
    name old_h_47_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_47_out \
    op interface \
    ports { old_h_47_out { O 29 vector } old_h_47_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 91 \
    name old_h_46_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_46_out \
    op interface \
    ports { old_h_46_out { O 29 vector } old_h_46_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 92 \
    name old_h_45_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_45_out \
    op interface \
    ports { old_h_45_out { O 29 vector } old_h_45_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 93 \
    name old_h_44_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_44_out \
    op interface \
    ports { old_h_44_out { O 29 vector } old_h_44_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 94 \
    name old_h_43_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_43_out \
    op interface \
    ports { old_h_43_out { O 29 vector } old_h_43_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 95 \
    name old_h_42_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_42_out \
    op interface \
    ports { old_h_42_out { O 29 vector } old_h_42_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 96 \
    name old_h_41_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_41_out \
    op interface \
    ports { old_h_41_out { O 29 vector } old_h_41_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 97 \
    name old_h_40_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_40_out \
    op interface \
    ports { old_h_40_out { O 29 vector } old_h_40_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 98 \
    name old_h_39_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_39_out \
    op interface \
    ports { old_h_39_out { O 29 vector } old_h_39_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 99 \
    name old_h_38_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_38_out \
    op interface \
    ports { old_h_38_out { O 29 vector } old_h_38_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 100 \
    name old_h_37_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_37_out \
    op interface \
    ports { old_h_37_out { O 29 vector } old_h_37_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 101 \
    name old_h_36_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_36_out \
    op interface \
    ports { old_h_36_out { O 29 vector } old_h_36_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 102 \
    name old_h_35_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_35_out \
    op interface \
    ports { old_h_35_out { O 29 vector } old_h_35_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 103 \
    name old_h_34_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_34_out \
    op interface \
    ports { old_h_34_out { O 29 vector } old_h_34_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 104 \
    name old_h_33_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_33_out \
    op interface \
    ports { old_h_33_out { O 29 vector } old_h_33_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 105 \
    name old_h_32_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_32_out \
    op interface \
    ports { old_h_32_out { O 29 vector } old_h_32_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 106 \
    name old_h_31_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_31_out \
    op interface \
    ports { old_h_31_out { O 29 vector } old_h_31_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 107 \
    name old_h_30_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_30_out \
    op interface \
    ports { old_h_30_out { O 29 vector } old_h_30_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 108 \
    name old_h_29_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_29_out \
    op interface \
    ports { old_h_29_out { O 29 vector } old_h_29_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 109 \
    name old_h_28_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_28_out \
    op interface \
    ports { old_h_28_out { O 29 vector } old_h_28_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 110 \
    name old_h_27_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_27_out \
    op interface \
    ports { old_h_27_out { O 29 vector } old_h_27_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 111 \
    name old_h_26_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_26_out \
    op interface \
    ports { old_h_26_out { O 29 vector } old_h_26_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 112 \
    name old_h_25_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_25_out \
    op interface \
    ports { old_h_25_out { O 29 vector } old_h_25_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 113 \
    name old_h_24_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_24_out \
    op interface \
    ports { old_h_24_out { O 29 vector } old_h_24_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 114 \
    name old_h_23_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_23_out \
    op interface \
    ports { old_h_23_out { O 29 vector } old_h_23_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 115 \
    name old_h_22_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_22_out \
    op interface \
    ports { old_h_22_out { O 29 vector } old_h_22_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 116 \
    name old_h_21_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_21_out \
    op interface \
    ports { old_h_21_out { O 29 vector } old_h_21_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 117 \
    name old_h_20_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_20_out \
    op interface \
    ports { old_h_20_out { O 29 vector } old_h_20_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 118 \
    name old_h_19_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_19_out \
    op interface \
    ports { old_h_19_out { O 29 vector } old_h_19_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 119 \
    name old_h_18_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_18_out \
    op interface \
    ports { old_h_18_out { O 29 vector } old_h_18_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 120 \
    name old_h_17_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_17_out \
    op interface \
    ports { old_h_17_out { O 29 vector } old_h_17_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 121 \
    name old_h_16_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_16_out \
    op interface \
    ports { old_h_16_out { O 29 vector } old_h_16_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 122 \
    name old_h_15_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_15_out \
    op interface \
    ports { old_h_15_out { O 29 vector } old_h_15_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 123 \
    name old_h_14_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_14_out \
    op interface \
    ports { old_h_14_out { O 29 vector } old_h_14_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 124 \
    name old_h_13_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_13_out \
    op interface \
    ports { old_h_13_out { O 29 vector } old_h_13_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 125 \
    name old_h_12_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_12_out \
    op interface \
    ports { old_h_12_out { O 29 vector } old_h_12_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 126 \
    name old_h_11_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_11_out \
    op interface \
    ports { old_h_11_out { O 29 vector } old_h_11_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 127 \
    name old_h_10_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_10_out \
    op interface \
    ports { old_h_10_out { O 29 vector } old_h_10_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 128 \
    name old_h_9_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_9_out \
    op interface \
    ports { old_h_9_out { O 29 vector } old_h_9_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 129 \
    name old_h_8_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_8_out \
    op interface \
    ports { old_h_8_out { O 29 vector } old_h_8_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 130 \
    name old_h_7_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_7_out \
    op interface \
    ports { old_h_7_out { O 29 vector } old_h_7_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 131 \
    name old_h_6_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_6_out \
    op interface \
    ports { old_h_6_out { O 29 vector } old_h_6_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 132 \
    name old_h_5_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_5_out \
    op interface \
    ports { old_h_5_out { O 29 vector } old_h_5_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 133 \
    name old_h_4_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_4_out \
    op interface \
    ports { old_h_4_out { O 29 vector } old_h_4_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 134 \
    name old_h_3_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_3_out \
    op interface \
    ports { old_h_3_out { O 29 vector } old_h_3_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 135 \
    name old_h_2_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_2_out \
    op interface \
    ports { old_h_2_out { O 29 vector } old_h_2_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 136 \
    name old_h_1_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_1_out \
    op interface \
    ports { old_h_1_out { O 29 vector } old_h_1_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 137 \
    name old_h_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_out \
    op interface \
    ports { old_h_out { O 29 vector } old_h_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 138 \
    name status_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_status_out \
    op interface \
    ports { status_out { O 32 vector } status_out_ap_vld { O 1 bit } } \
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



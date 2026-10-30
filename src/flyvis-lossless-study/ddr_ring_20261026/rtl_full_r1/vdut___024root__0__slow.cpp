// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See vdut.h for the primary calling header

#include "vdut__pch.h"

VL_ATTR_COLD void Vdut___024root___eval_static(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_static\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__Vtrigprevexpr___TOP__aclk__0 = vlSelfRef.aclk;
}

VL_ATTR_COLD void Vdut___024root___eval_initial__TOP(Vdut___024root* vlSelf);

VL_ATTR_COLD void Vdut___024root___eval_initial(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_initial\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vdut___024root___eval_initial__TOP(vlSelf);
}

VL_ATTR_COLD void Vdut___024root___eval_initial__TOP(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_initial__TOP\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__metadata__DOT____VlemExpr_0;
    IData/*31:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__maps__DOT____VlemExpr_0;
    IData/*31:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rows__DOT____VlemExpr_0;
    IData/*31:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_rows__DOT____VlemExpr_0;
    // Body
    vlSelfRef.m_axi_awid = 0U;
    vlSelfRef.m_axi_awlock = 0U;
    vlSelfRef.m_axi_awcache = 3U;
    vlSelfRef.m_axi_awprot = 0U;
    vlSelfRef.m_axi_awqos = 0U;
    VL_READMEM_N(true, 32, 7663, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/meta.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__metadata__DOT__ordinary__DOT__mem)
                 , 0, ~0ULL);
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__metadata__DOT____VlemExpr_0 
        = VL_VALUEPLUSARGS_INN(64, "META=%s"s, vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__metadata__DOT__ordinary__DOT__path);
    if (VL_UNLIKELY(((! flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__metadata__DOT____VlemExpr_0)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: sync_mem.sv:24: Assertion failed in %m: missing memory image META\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.metadata.ordinary", 'T',-12
                     , '#',64,VL_TIME_UNITED_Q(1));
        VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\sync_mem.sv", 24, "", false);
    }
    VL_READMEM_N(true, 32, 7663, 0, vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__metadata__DOT__ordinary__DOT__path
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__metadata__DOT__ordinary__DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_00.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_01.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_02.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_03.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_04.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_05.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_06.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_07.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_08.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_09.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_10.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_11.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_12.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_13.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_14.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_15.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_16.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_17.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_18.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_19.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_20.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_21.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_22.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_23.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_24.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_25.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_26.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_27.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_28.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_29.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_30.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_31.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_32.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_33.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_34.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_35.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_36.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_37.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_38.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_39.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_40.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_41.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_42.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_43.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 1024, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/state_bank_44.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 16, 1922, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/map.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__maps__DOT__ordinary__DOT__mem)
                 , 0, ~0ULL);
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__maps__DOT____VlemExpr_0 
        = VL_VALUEPLUSARGS_INN(64, "MAP=%s"s, vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__maps__DOT__ordinary__DOT__path);
    if (VL_UNLIKELY(((! flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__maps__DOT____VlemExpr_0)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: sync_mem.sv:24: Assertion failed in %m: missing memory image MAP\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen.maps.ordinary", 'T',-12
                     , '#',64,VL_TIME_UNITED_Q(1));
        VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\sync_mem.sv", 24, "", false);
    }
    VL_READMEM_N(true, 16, 1922, 0, vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__maps__DOT__ordinary__DOT__path
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__maps__DOT__ordinary__DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 62, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/rows.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rows__DOT__ordinary__DOT__mem)
                 , 0, ~0ULL);
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rows__DOT____VlemExpr_0 
        = VL_VALUEPLUSARGS_INN(64, "ROWS=%s"s, vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rows__DOT__ordinary__DOT__path);
    if (VL_UNLIKELY(((! flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rows__DOT____VlemExpr_0)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: sync_mem.sv:24: Assertion failed in %m: missing memory image ROWS\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen.rows.ordinary", 'T',-12
                     , '#',64,VL_TIME_UNITED_Q(1));
        VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\sync_mem.sv", 24, "", false);
    }
    VL_READMEM_N(true, 32, 62, 0, vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rows__DOT__ordinary__DOT__path
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rows__DOT__ordinary__DOT__mem)
                 , 0, ~0ULL);
    VL_READMEM_N(true, 32, 62, 0, "C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/rows.hex"s
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_rows__DOT__ordinary__DOT__mem)
                 , 0, ~0ULL);
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_rows__DOT____VlemExpr_0 
        = VL_VALUEPLUSARGS_INN(64, "ROWS=%s"s, vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_rows__DOT__ordinary__DOT__path);
    if (VL_UNLIKELY(((! flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_rows__DOT____VlemExpr_0)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: sync_mem.sv:24: Assertion failed in %m: missing memory image ROWS\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen.target_rows.ordinary", 'T',-12
                     , '#',64,VL_TIME_UNITED_Q(1));
        VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\sync_mem.sv", 24, "", false);
    }
    VL_READMEM_N(true, 32, 62, 0, vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_rows__DOT__ordinary__DOT__path
                 ,  &(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_rows__DOT__ordinary__DOT__mem)
                 , 0, ~0ULL);
    vlSelfRef.m_axi_awsize = 3U;
    vlSelfRef.m_axi_awburst = 1U;
}

VL_ATTR_COLD void Vdut___024root___eval_final(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_final\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vdut___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vdut___024root___eval_phase__stl(Vdut___024root* vlSelf);

VL_ATTR_COLD void Vdut___024root___eval_settle(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_settle\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VstlIterCount;
    // Body
    __VstlIterCount = 0U;
    vlSelfRef.__VstlFirstIteration = 1U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VstlIterCount)))) {
#ifdef VL_DEBUG
            Vdut___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
#endif
            VL_FATAL_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_ddr_soc_ip.sv", 3, "", "DIDNOTCONVERGE: Settle region did not converge after '--converge-limit' of 10000 tries");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        vlSelfRef.__VstlPhaseResult = Vdut___024root___eval_phase__stl(vlSelf);
        vlSelfRef.__VstlFirstIteration = 0U;
    } while (vlSelfRef.__VstlPhaseResult);
}

VL_ATTR_COLD void Vdut___024root___eval_triggers_vec__stl(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_triggers_vec__stl\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VstlTriggered[0U] = ((0xfffffffffffffffeULL 
                                      & vlSelfRef.__VstlTriggered[0U]) 
                                     | (IData)((IData)(vlSelfRef.__VstlFirstIteration)));
}

VL_ATTR_COLD bool Vdut___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vdut___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___dump_triggers__stl\n"); );
    // Body
    if ((1U & (~ (IData)(Vdut___024root___trigger_anySet__stl(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD bool Vdut___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___trigger_anySet__stl\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        if (in[n]) {
            return (1U);
        }
        n = ((IData)(1U) + n);
    } while ((1U > n));
    return (0U);
}

VL_ATTR_COLD void Vdut___024root___stl_sequent__TOP__0(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___stl_sequent__TOP__0\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT____Vlvbound_h3910bbff__0;
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT____Vlvbound_h3910bbff__0 = 0;
    SData/*8:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__final_exp;
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__final_exp = 0;
    SData/*10:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__final_exp;
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__final_exp = 0;
    // Body
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__a_ge_b 
        = (1U & (((((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[3U][31U] 
                     >> 0x00000015U) | ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[3U][31U] 
                                         >> 0x00000011U) 
                                        & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[3U][31U] 
                                           >> 0x00000014U))) 
                   | ((3U == (3U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[3U][31U] 
                                    >> 0x00000010U))) 
                      & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[3U][31U] 
                         >> 0x00000013U))) | ((7U == 
                                               (7U 
                                                & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[3U][31U] 
                                                   >> 0x0000000fU))) 
                                              & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[3U][31U] 
                                                 >> 0x00000012U))) 
                 | (0x0000000fU == (0x0000000fU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[3U][31U] 
                                                   >> 0x0000000eU)))));
    vlSelfRef.m_axi_awvalid = (1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus));
    vlSelfRef.m_axi_bready = (3U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus));
    vlSelfRef.s_axi_arready = (1U & (~ (IData)(vlSelfRef.s_axi_rvalid)));
    vlSelfRef.m_axi_awlen = (0x000000ffU & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__burst_beats) 
                                            - (IData)(1U)));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__operand_a 
        = ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[0U][8U] 
            << 0x0000000dU) | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[0U][7U] 
                               >> 0x00000013U));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__operand_b 
        = ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[0U][7U] 
            << 0x0000000dU) | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[0U][6U] 
                               >> 0x00000013U));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__ai 
        = ((~ (0U != (0x007fffffU & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[0U][8U] 
                                      << 0x0000000dU) 
                                     | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[0U][7U] 
                                        >> 0x00000013U))))) 
           & (0x000000ffU == (0x000000ffU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[0U][8U] 
                                             >> 0x0000000aU))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__bn 
        = ((0x000000ffU == (0x000000ffU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[0U][7U] 
                                           >> 0x0000000aU))) 
           & (0U != (0x007fffffU & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[0U][7U] 
                                     << 0x0000000dU) 
                                    | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[0U][6U] 
                                       >> 0x00000013U)))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__an 
        = ((0x000000ffU == (0x000000ffU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[0U][8U] 
                                           >> 0x0000000aU))) 
           & (0U != (0x007fffffU & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[0U][8U] 
                                     << 0x0000000dU) 
                                    | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[0U][7U] 
                                       >> 0x00000013U)))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__bi 
        = ((~ (0U != (0x007fffffU & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[0U][7U] 
                                      << 0x0000000dU) 
                                     | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[0U][6U] 
                                        >> 0x00000013U))))) 
           & (0x000000ffU == (0x000000ffU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[0U][7U] 
                                             >> 0x0000000aU))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr = 0U;
    if ((((3U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)) 
          | (4U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) 
         & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv)) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar = 1U;
    } else {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar = 0U;
    }
    if ((7U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar = 1U;
    }
    if ((0x0bU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar = 1U;
    }
    vlSelfRef.s_axi_awready = (1U & (~ ((IData)(vlSelfRef.s_axi_bvalid) 
                                        | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__aw_pending))));
    vlSelfRef.s_axi_wready = (1U & (~ ((IData)(vlSelfRef.s_axi_bvalid) 
                                       | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__w_pending))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vcellinp__stimulus_ram__re 
        = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_input) 
           & (7U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)));
    vlSelfRef.m_axi_wlast = (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__burst_beats) 
                              - (IData)(1U)) == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__beat));
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__final_exp 
        = (0x000001ffU & (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[11U][10U] 
                            << 3U) | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[11U][9U] 
                                      >> 0x0000001dU)) 
                          + (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[11U][0U] 
                                   >> 0x00000019U))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__packed_result 
        = ((0x00004000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[11U][10U])
            ? ((QData)((IData)((1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[11U][67U] 
                                      >> 7U)))) << 0x0000001fU)
            : ((0x00ffU <= (IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__final_exp))
                ? (0x0000000500000000ULL | (QData)((IData)(
                                                           (0x7f800000U 
                                                            | (0x80000000U 
                                                               & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[11U][67U] 
                                                                  << 0x00000018U))))))
                : (((QData)((IData)((1U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[11U][0U]))) 
                    << 0x00000020U) | (QData)((IData)(
                                                      ((0x80000000U 
                                                        & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[11U][67U] 
                                                           << 0x00000018U)) 
                                                       | ((0x7f800000U 
                                                           & ((IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__final_exp) 
                                                              << 0x00000017U)) 
                                                          | (0x007fffffU 
                                                             & ((0x02000000U 
                                                                 & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[11U][0U])
                                                                 ? 
                                                                ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[11U][0U] 
                                                                  << 0x0000001eU) 
                                                                 | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[11U][0U] 
                                                                    >> 2U))
                                                                 : 
                                                                ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[11U][0U] 
                                                                  << 0x0000001fU) 
                                                                 | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[11U][0U] 
                                                                    >> 1U)))))))))));
    if ((0x00008000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[11U][68U])) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__packed_result 
            = (0x0000001fffffffffULL & (((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[11U][68U])) 
                                         << 0x00000016U) 
                                        | ((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[11U][67U])) 
                                           >> 0x0000000aU)));
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__carry = 0U;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__carry 
        = ((0x1eU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__carry)) 
           | (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][67U] 
                    >> 6U)));
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT____Vlvbound_h3910bbff__0 
        = (1U & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][24U] 
                  >> 0x00000018U) | ((0xffffffffU == 
                                      ((((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][23U] 
                                          << 0x0000000eU) 
                                         | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][22U] 
                                            >> 0x00000012U)) 
                                        & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][24U] 
                                            << 0x0000000eU) 
                                           | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][23U] 
                                              >> 0x00000012U))) 
                                       & (0xffffffc0U 
                                          | (0x0000003fU 
                                             & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][24U] 
                                                >> 0x00000012U))))) 
                                     & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__carry))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__carry 
        = ((0x1dU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__carry)) 
           | ((IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT____Vlvbound_h3910bbff__0) 
              << 1U));
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT____Vlvbound_h3910bbff__0 
        = (1U & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][26U] 
                  >> 0x0000001fU) | ((0xffffffffU == 
                                      ((((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][25U] 
                                          << 7U) | 
                                         (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][24U] 
                                          >> 0x00000019U)) 
                                        & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][26U] 
                                            << 7U) 
                                           | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][25U] 
                                              >> 0x00000019U))) 
                                       & (0xffffffc0U 
                                          | (0x0000003fU 
                                             & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][26U] 
                                                >> 0x00000019U))))) 
                                     & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__carry) 
                                        >> 1U))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__carry 
        = ((0x1bU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__carry)) 
           | ((IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT____Vlvbound_h3910bbff__0) 
              << 2U));
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT____Vlvbound_h3910bbff__0 
        = (1U & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][29U] 
                  >> 6U) | ((0xffffffffU == ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][27U] 
                                              & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][28U]) 
                                             & (0xffffffc0U 
                                                | (0x0000003fU 
                                                   & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][29U])))) 
                            & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__carry) 
                               >> 2U))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__carry 
        = ((0x17U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__carry)) 
           | ((IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT____Vlvbound_h3910bbff__0) 
              << 3U));
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT____Vlvbound_h3910bbff__0 
        = (1U & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][31U] 
                  >> 0x0000000dU) | ((0xffffffffU == 
                                      ((((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][30U] 
                                          << 0x00000019U) 
                                         | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][29U] 
                                            >> 7U)) 
                                        & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][31U] 
                                            << 0x00000019U) 
                                           | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][30U] 
                                              >> 7U))) 
                                       & (0xffffffc0U 
                                          | (0x0000003fU 
                                             & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[5U][31U] 
                                                >> 7U))))) 
                                     & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__carry) 
                                        >> 3U))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__carry 
        = ((0x0fU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__carry)) 
           | ((IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT____Vlvbound_h3910bbff__0) 
              << 4U));
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__final_exp 
        = (0x000007ffU & (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][3U] 
                            << 3U) | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][2U] 
                                      >> 0x0000001dU)) 
                          + (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][0U] 
                                   >> 0x00000018U))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__packed_result 
        = ((0x00200000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][8U])
            ? ((QData)((IData)((1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][8U] 
                                      >> 0x00000016U)))) 
               << 0x0000001fU) : (VL_GTS_III(32, 0xffffff82U, 
                                             VL_EXTENDS_II(32,11, 
                                                           (0x000007ffU 
                                                            & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][3U] 
                                                                << 3U) 
                                                               | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][2U] 
                                                                  >> 0x0000001dU)))))
                                   ? (((QData)((IData)(
                                                       ((2U 
                                                         & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][8U] 
                                                             >> 0x00000013U) 
                                                            & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][8U] 
                                                               >> 0x00000012U))) 
                                                        | (1U 
                                                           & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][8U] 
                                                              >> 0x00000013U))))) 
                                       << 0x00000020U) 
                                      | (QData)((IData)(
                                                        ((0x80000000U 
                                                          & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][8U] 
                                                             << 9U)) 
                                                         | (0x00ffffffU 
                                                            & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][0U])))))
                                   : (VL_LTS_III(32, 0x0000007fU, 
                                                 VL_EXTENDS_II(32,11, (IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__final_exp)))
                                       ? (0x0000000500000000ULL 
                                          | (QData)((IData)(
                                                            (0x7f800000U 
                                                             | (0x80000000U 
                                                                & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][8U] 
                                                                   << 9U))))))
                                       : (((QData)((IData)(
                                                           (1U 
                                                            & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][8U] 
                                                               >> 0x00000013U)))) 
                                           << 0x00000020U) 
                                          | (QData)((IData)(
                                                            ((0x80000000U 
                                                              & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][8U] 
                                                                 << 9U)) 
                                                             | ((0x7f800000U 
                                                                 & (((IData)(0x7fU) 
                                                                     + 
                                                                     VL_EXTENDS_II(8,11, (IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__final_exp))) 
                                                                    << 0x00000017U)) 
                                                                | (0x007fffffU 
                                                                   & ((0x01000000U 
                                                                       & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][0U])
                                                                       ? 
                                                                      ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][0U] 
                                                                        << 0x0000001fU) 
                                                                       | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][0U] 
                                                                          >> 1U))
                                                                       : vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][0U]))))))))));
}

VL_ATTR_COLD void Vdut___024root___stl_sequent__TOP__1(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___stl_sequent__TOP__1\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlWide<10>/*319:0*/ __Vtemp_3;
    VlWide<10>/*319:0*/ __Vtemp_6;
    VlWide<10>/*319:0*/ __Vtemp_9;
    VlWide<10>/*319:0*/ __Vtemp_12;
    VlWide<10>/*319:0*/ __Vtemp_16;
    VlWide<10>/*319:0*/ __Vtemp_19;
    VlWide<10>/*319:0*/ __Vtemp_22;
    VlWide<10>/*319:0*/ __Vtemp_25;
    // Body
    if ((0x10000000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][9U])) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__packed_result 
            = (0x0000001fffffffffULL & (((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][9U])) 
                                         << 9U) | ((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][8U])) 
                                                   >> 0x00000017U)));
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__exponent 
        = (0x000007ffU & ((0x0000003fU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[2U][2U] 
                                          >> 0x0000000cU)) 
                          + ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[2U][3U] 
                              << 0x00000018U) | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[2U][3U] 
                                                 >> 8U))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__amount 
        = (0x000007ffU & (VL_GTS_III(32, 0xffffff82U, 
                                     VL_EXTENDS_II(32,11, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__exponent)))
                           ? ((IData)(0x076bU) - ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[2U][3U] 
                                                   << 0x00000018U) 
                                                  | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[2U][3U] 
                                                     >> 8U)))
                           : ((0x0000003fU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[2U][2U] 
                                              >> 0x0000000cU)) 
                              - (IData)(0x0017U))));
    vlSelfRef.m_axi_awaddr = (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__record_base 
                              + (((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))
                                   ? 0x00000080U : 
                                  (0x00001000U & (- (IData)(
                                                            (4U 
                                                             != (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase)))))) 
                                 + VL_SHIFTL_III(32,32,32, vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__acked_beats, 3U)));
    vlSelfRef.m_axi_wstrb = (0x000000ffU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__fifo_strb
                                            [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__rp] 
                                            | (- (IData)(
                                                         (4U 
                                                          == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))))));
    if ((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__word_bits 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__frame_q;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__last_word 
            = (0x000002d0U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_count);
    } else {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__word_bits 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__old_a;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__last_word 
            = (0x0000b264U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count);
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_b 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[1U];
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_valid 
        = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                 >> 1U));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_valid 
        = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                 >> 9U));
    if ((9U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
        if ((0U != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
            if ((1U != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
                if ((2U != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
                    if ((3U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
                        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_b 
                            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result
                            [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot];
                    } else if ((4U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
                        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_b = 0x3ba3d70aU;
                    }
                }
            }
        }
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_valid 
            = ((3U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id) 
               | (4U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_valid 
            = (1U & (~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_valid)));
    }
    vlSelfRef.m_axi_wvalid = (2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[0U] 
        = ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][1U] 
            << 6U) | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][0U] 
                      >> 0x0000001aU));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[1U] 
        = ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][2U] 
            << 6U) | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][1U] 
                      >> 0x0000001aU));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[2U] 
        = ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][3U] 
            << 6U) | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][2U] 
                      >> 0x0000001aU));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[3U] 
        = ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][4U] 
            << 6U) | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][3U] 
                      >> 0x0000001aU));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[4U] 
        = ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][5U] 
            << 6U) | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][4U] 
                      >> 0x0000001aU));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[5U] 
        = ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][6U] 
            << 6U) | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][5U] 
                      >> 0x0000001aU));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[6U] 
        = ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][7U] 
            << 6U) | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][6U] 
                      >> 0x0000001aU));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[7U] 
        = ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][8U] 
            << 6U) | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][7U] 
                      >> 0x0000001aU));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[8U] 
        = ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][9U] 
            << 6U) | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][8U] 
                      >> 0x0000001aU));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[9U] 
        = (7U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][9U] 
                 >> 0x0000001aU));
    if ((0x00000400U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][10U])) {
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[0U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[0U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[1U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[2U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[3U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[4U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[5U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[6U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[7U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[8U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[9U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[9U];
        VL_SHIFTR_WWI(291,291,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x, 0x00000010U);
        VL_SHIFTL_WWI(291,291,32, __Vtemp_3, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x, 0x00000113U);
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U] 
            = ((0xfffffffeU & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U]) 
               | (1U & (vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U] 
                        | (0U != (((((((((__Vtemp_3[0U] 
                                          | __Vtemp_3[1U]) 
                                         | __Vtemp_3[2U]) 
                                        | __Vtemp_3[3U]) 
                                       | __Vtemp_3[4U]) 
                                      | __Vtemp_3[5U]) 
                                     | __Vtemp_3[6U]) 
                                    | __Vtemp_3[7U]) 
                                   | __Vtemp_3[8U]) 
                                  | (7U & __Vtemp_3[9U]))))));
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[9U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[9U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[0U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[1U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[2U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[3U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[4U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[5U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[6U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[7U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[8U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[9U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[9U];
    }
    if ((0x00000800U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][10U])) {
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[0U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[0U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[1U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[2U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[3U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[4U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[5U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[6U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[7U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[8U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[9U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[9U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[9U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[9U] = 0U;
        VL_SHIFTL_WWI(291,291,32, __Vtemp_6, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x, 0x00000103U);
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U] 
            = ((0xfffffffeU & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U]) 
               | (1U & (vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U] 
                        | (0U != (((((((((__Vtemp_6[0U] 
                                          | __Vtemp_6[1U]) 
                                         | __Vtemp_6[2U]) 
                                        | __Vtemp_6[3U]) 
                                       | __Vtemp_6[4U]) 
                                      | __Vtemp_6[5U]) 
                                     | __Vtemp_6[6U]) 
                                    | __Vtemp_6[7U]) 
                                   | __Vtemp_6[8U]) 
                                  | (7U & __Vtemp_6[9U]))))));
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[9U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[9U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[0U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[1U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[2U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[3U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[4U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[5U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[6U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[7U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[8U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[9U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[9U];
    }
    if ((0x00001000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][10U])) {
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[0U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[0U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[1U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[2U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[3U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[4U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[5U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[6U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[7U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[8U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[9U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[9U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[9U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[8U] = 0U;
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[9U] = 0U;
        VL_SHIFTL_WWI(291,291,32, __Vtemp_9, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x, 0x000000e3U);
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U] 
            = ((0xfffffffeU & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U]) 
               | (1U & (vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U] 
                        | (0U != (((((((((__Vtemp_9[0U] 
                                          | __Vtemp_9[1U]) 
                                         | __Vtemp_9[2U]) 
                                        | __Vtemp_9[3U]) 
                                       | __Vtemp_9[4U]) 
                                      | __Vtemp_9[5U]) 
                                     | __Vtemp_9[6U]) 
                                    | __Vtemp_9[7U]) 
                                   | __Vtemp_9[8U]) 
                                  | (7U & __Vtemp_9[9U]))))));
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[9U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[9U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[0U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[1U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[2U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[3U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[4U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[5U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[6U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[7U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[8U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[9U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[9U];
    }
    if ((0x00002000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[9U][10U])) {
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[0U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[0U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[1U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[2U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[3U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[4U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[5U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[6U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[7U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[8U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[9U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[9U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x[9U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[6U] = 0U;
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[7U] = 0U;
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[8U] = 0U;
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[9U] = 0U;
        VL_SHIFTL_WWI(291,291,32, __Vtemp_12, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x, 0x000000a3U);
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U] 
            = ((0xfffffffeU & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U]) 
               | (1U & (vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U] 
                        | (0U != (((((((((__Vtemp_12[0U] 
                                          | __Vtemp_12[1U]) 
                                         | __Vtemp_12[2U]) 
                                        | __Vtemp_12[3U]) 
                                       | __Vtemp_12[4U]) 
                                      | __Vtemp_12[5U]) 
                                     | __Vtemp_12[6U]) 
                                    | __Vtemp_12[7U]) 
                                   | __Vtemp_12[8U]) 
                                  | (7U & __Vtemp_12[9U]))))));
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[9U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[9U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[0U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[1U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[2U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[3U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[4U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[5U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[6U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[7U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[8U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high[9U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout[9U];
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_addr = 0U;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr_addr = 0U;
    if ((((3U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)) 
          | (4U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) 
         & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv)) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_addr 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__request_src;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr_addr 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[0U];
    }
    if ((7U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_addr 
            = (0x0000ffffU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_base 
                              + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr_addr 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_addr;
    }
    if ((0x0bU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_addr 
            = (0x0000ffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index);
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__amount 
        = ((0x0017U < (0x000001ffU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][10U] 
                                      >> 0x0000000fU)))
            ? (0x000000ffU & ((0x000001ffU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][10U] 
                                              >> 0x0000000fU)) 
                              - (IData)(0x17U))) : 0U);
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[0U] 
        = ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][14U] 
            << 0x00000011U) | (0x0001fff8U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][13U] 
                                              >> 0x0000000fU)));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[1U] 
        = ((7U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][14U] 
                  >> 0x0000000fU)) | ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][15U] 
                                       << 0x00000011U) 
                                      | (0x0001fff8U 
                                         & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][14U] 
                                            >> 0x0000000fU))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[2U] 
        = ((7U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][15U] 
                  >> 0x0000000fU)) | ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][16U] 
                                       << 0x00000011U) 
                                      | (0x0001fff8U 
                                         & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][15U] 
                                            >> 0x0000000fU))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[3U] 
        = ((7U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][16U] 
                  >> 0x0000000fU)) | ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][17U] 
                                       << 0x00000011U) 
                                      | (0x0001fff8U 
                                         & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][16U] 
                                            >> 0x0000000fU))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[4U] 
        = ((7U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][17U] 
                  >> 0x0000000fU)) | ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][18U] 
                                       << 0x00000011U) 
                                      | (0x0001fff8U 
                                         & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][17U] 
                                            >> 0x0000000fU))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[5U] 
        = ((7U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][18U] 
                  >> 0x0000000fU)) | ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][19U] 
                                       << 0x00000011U) 
                                      | (0x0001fff8U 
                                         & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][18U] 
                                            >> 0x0000000fU))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[6U] 
        = ((7U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][19U] 
                  >> 0x0000000fU)) | ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][20U] 
                                       << 0x00000011U) 
                                      | (0x0001fff8U 
                                         & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][19U] 
                                            >> 0x0000000fU))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[7U] 
        = ((7U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][20U] 
                  >> 0x0000000fU)) | ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][21U] 
                                       << 0x00000011U) 
                                      | (0x0001fff8U 
                                         & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][20U] 
                                            >> 0x0000000fU))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[8U] 
        = ((7U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][21U] 
                  >> 0x0000000fU)) | ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][22U] 
                                       << 0x00000011U) 
                                      | (0x0001fff8U 
                                         & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][21U] 
                                            >> 0x0000000fU))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[9U] 
        = (7U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[8U][22U] 
                 >> 0x0000000fU));
    if ((1U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__amount))) {
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[0U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[0U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[1U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[2U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[3U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[4U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[5U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[6U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[7U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[8U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[9U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[9U];
        VL_SHIFTR_WWI(291,291,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x, 1U);
        VL_SHIFTL_WWI(291,291,32, __Vtemp_16, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x, 0x00000122U);
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U] 
            = ((0xfffffffeU & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U]) 
               | (1U & (vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U] 
                        | (0U != (((((((((__Vtemp_16[0U] 
                                          | __Vtemp_16[1U]) 
                                         | __Vtemp_16[2U]) 
                                        | __Vtemp_16[3U]) 
                                       | __Vtemp_16[4U]) 
                                      | __Vtemp_16[5U]) 
                                     | __Vtemp_16[6U]) 
                                    | __Vtemp_16[7U]) 
                                   | __Vtemp_16[8U]) 
                                  | (7U & __Vtemp_16[9U]))))));
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[9U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[9U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[0U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[1U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[2U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[3U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[4U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[5U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[6U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[7U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[8U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[9U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[9U];
    }
    if ((2U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__amount))) {
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[0U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[0U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[1U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[2U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[3U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[4U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[5U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[6U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[7U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[8U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[9U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[9U];
        VL_SHIFTR_WWI(291,291,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x, 2U);
        VL_SHIFTL_WWI(291,291,32, __Vtemp_19, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x, 0x00000121U);
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U] 
            = ((0xfffffffeU & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U]) 
               | (1U & (vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U] 
                        | (0U != (((((((((__Vtemp_19[0U] 
                                          | __Vtemp_19[1U]) 
                                         | __Vtemp_19[2U]) 
                                        | __Vtemp_19[3U]) 
                                       | __Vtemp_19[4U]) 
                                      | __Vtemp_19[5U]) 
                                     | __Vtemp_19[6U]) 
                                    | __Vtemp_19[7U]) 
                                   | __Vtemp_19[8U]) 
                                  | (7U & __Vtemp_19[9U]))))));
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[9U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[9U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[0U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[1U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[2U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[3U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[4U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[5U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[6U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[7U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[8U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[9U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[9U];
    }
    if ((4U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__amount))) {
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[0U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[0U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[1U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[2U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[3U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[4U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[5U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[6U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[7U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[8U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[9U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[9U];
        VL_SHIFTR_WWI(291,291,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x, 4U);
        VL_SHIFTL_WWI(291,291,32, __Vtemp_22, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x, 0x0000011fU);
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U] 
            = ((0xfffffffeU & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U]) 
               | (1U & (vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U] 
                        | (0U != (((((((((__Vtemp_22[0U] 
                                          | __Vtemp_22[1U]) 
                                         | __Vtemp_22[2U]) 
                                        | __Vtemp_22[3U]) 
                                       | __Vtemp_22[4U]) 
                                      | __Vtemp_22[5U]) 
                                     | __Vtemp_22[6U]) 
                                    | __Vtemp_22[7U]) 
                                   | __Vtemp_22[8U]) 
                                  | (7U & __Vtemp_22[9U]))))));
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[9U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[9U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[0U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[1U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[2U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[3U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[4U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[5U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[6U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[7U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[8U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[9U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[9U];
    }
    if ((8U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__amount))) {
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[0U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[0U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[1U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[2U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[3U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[4U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[5U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[6U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[7U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[8U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x[9U] 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[9U];
        VL_SHIFTR_WWI(291,291,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x, 8U);
        VL_SHIFTL_WWI(291,291,32, __Vtemp_25, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x, 0x0000011bU);
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U] 
            = ((0xfffffffeU & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U]) 
               | (1U & (vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U] 
                        | (0U != (((((((((__Vtemp_25[0U] 
                                          | __Vtemp_25[1U]) 
                                         | __Vtemp_25[2U]) 
                                        | __Vtemp_25[3U]) 
                                       | __Vtemp_25[4U]) 
                                      | __Vtemp_25[5U]) 
                                     | __Vtemp_25[6U]) 
                                    | __Vtemp_25[7U]) 
                                   | __Vtemp_25[8U]) 
                                  | (7U & __Vtemp_25[9U]))))));
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[1U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[2U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[3U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[4U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[5U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[6U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[7U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[8U];
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[9U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[9U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[0U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[0U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[1U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[1U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[2U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[2U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[3U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[3U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[4U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[4U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[5U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[5U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[6U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[6U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[7U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[7U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[8U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[8U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low[9U] 
            = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout[9U];
    }
}

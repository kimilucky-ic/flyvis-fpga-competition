// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See vdut.h for the primary calling header

#include "vdut__pch.h"

VL_ATTR_COLD void Vdut___024root___eval_static(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_static\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.cmos_capture_data__DOT__rst_n_d0 = 1U;
    vlSelfRef.cmos_capture_data__DOT__rst_n_syn = 1U;
    vlSelfRef.__Vtrigprevexpr___TOP__cam_pclk__0 = vlSelfRef.cam_pclk;
    vlSelfRef.__Vtrigprevexpr___TOP__rst_n__0 = vlSelfRef.rst_n;
    vlSelfRef.__Vtrigprevexpr___TOP__cmos_capture_data__DOT__rst_n_syn__0 = 1U;
}

VL_ATTR_COLD void Vdut___024root___eval_static__TOP(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_static__TOP\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.cmos_capture_data__DOT__rst_n_d0 = 1U;
    vlSelfRef.cmos_capture_data__DOT__rst_n_syn = 1U;
}

VL_ATTR_COLD void Vdut___024root___eval_initial(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_initial\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.cam_rst_n = 1U;
    vlSelfRef.cam_pwdn = 0U;
}

VL_ATTR_COLD void Vdut___024root___eval_initial__TOP(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_initial__TOP\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.cam_rst_n = 1U;
    vlSelfRef.cam_pwdn = 0U;
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
            VL_FATAL_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ov5640_soc_20261023\\rtl\\cmos_capture_data.v", 22, "", "DIDNOTCONVERGE: Settle region did not converge after '--converge-limit' of 10000 tries");
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
    // Body
    vlSelfRef.cmos_frame_clk = vlSelfRef.cam_pclk;
    vlSelfRef.cmos_frame_vsync = ((IData)(vlSelfRef.cmos_capture_data__DOT__cam_vsync_d1) 
                                  & (IData)(vlSelfRef.cmos_capture_data__DOT__wait_done));
    vlSelfRef.cmos_frame_data = (((0x00f80000U & ((IData)(vlSelfRef.cmos_capture_data__DOT__cmos_data_16b) 
                                                  << 8U)) 
                                  | ((0x0000fc00U & 
                                      ((IData)(vlSelfRef.cmos_capture_data__DOT__cmos_data_16b) 
                                       << 5U)) | (0x000000f8U 
                                                  & ((IData)(vlSelfRef.cmos_capture_data__DOT__cmos_data_16b) 
                                                     << 3U)))) 
                                 & (- (IData)((IData)(vlSelfRef.cmos_capture_data__DOT__wait_done))));
    vlSelfRef.cmos_capture_data__DOT__pos_vsync = (
                                                   (~ (IData)(vlSelfRef.cmos_capture_data__DOT__cam_vsync_d1)) 
                                                   & (IData)(vlSelfRef.cmos_capture_data__DOT__cam_vsync_d0));
    vlSelfRef.cmos_frame_href = ((IData)(vlSelfRef.cmos_capture_data__DOT__wait_done) 
                                 & (IData)(vlSelfRef.cmos_capture_data__DOT__cam_href_d1));
    vlSelfRef.cmos_active_video = vlSelfRef.cmos_frame_href;
    vlSelfRef.cmos_frame_ce = ((IData)(vlSelfRef.cmos_capture_data__DOT__wait_done) 
                               & ((~ (IData)(vlSelfRef.cmos_frame_href)) 
                                  | ((IData)(vlSelfRef.cmos_capture_data__DOT__byte_flag_d0) 
                                     & (IData)(vlSelfRef.cmos_frame_href))));
}

VL_ATTR_COLD void Vdut___024root___eval_stl(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_stl\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VstlTriggered[0U])) {
        vlSelfRef.cmos_frame_clk = vlSelfRef.cam_pclk;
        vlSelfRef.cmos_frame_vsync = ((IData)(vlSelfRef.cmos_capture_data__DOT__cam_vsync_d1) 
                                      & (IData)(vlSelfRef.cmos_capture_data__DOT__wait_done));
        vlSelfRef.cmos_frame_data = (((0x00f80000U 
                                       & ((IData)(vlSelfRef.cmos_capture_data__DOT__cmos_data_16b) 
                                          << 8U)) | 
                                      ((0x0000fc00U 
                                        & ((IData)(vlSelfRef.cmos_capture_data__DOT__cmos_data_16b) 
                                           << 5U)) 
                                       | (0x000000f8U 
                                          & ((IData)(vlSelfRef.cmos_capture_data__DOT__cmos_data_16b) 
                                             << 3U)))) 
                                     & (- (IData)((IData)(vlSelfRef.cmos_capture_data__DOT__wait_done))));
        vlSelfRef.cmos_capture_data__DOT__pos_vsync 
            = ((~ (IData)(vlSelfRef.cmos_capture_data__DOT__cam_vsync_d1)) 
               & (IData)(vlSelfRef.cmos_capture_data__DOT__cam_vsync_d0));
        vlSelfRef.cmos_frame_href = ((IData)(vlSelfRef.cmos_capture_data__DOT__wait_done) 
                                     & (IData)(vlSelfRef.cmos_capture_data__DOT__cam_href_d1));
        vlSelfRef.cmos_active_video = vlSelfRef.cmos_frame_href;
        vlSelfRef.cmos_frame_ce = ((IData)(vlSelfRef.cmos_capture_data__DOT__wait_done) 
                                   & ((~ (IData)(vlSelfRef.cmos_frame_href)) 
                                      | ((IData)(vlSelfRef.cmos_capture_data__DOT__byte_flag_d0) 
                                         & (IData)(vlSelfRef.cmos_frame_href))));
    }
}

VL_ATTR_COLD bool Vdut___024root___eval_phase__stl(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_phase__stl\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VstlExecute;
    // Body
    Vdut___024root___eval_triggers_vec__stl(vlSelf);
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vdut___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
    }
#endif
    __VstlExecute = Vdut___024root___trigger_anySet__stl(vlSelfRef.__VstlTriggered);
    if (__VstlExecute) {
        Vdut___024root___eval_stl(vlSelf);
    }
    return (__VstlExecute);
}

bool Vdut___024root___trigger_anySet__ico(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vdut___024root___dump_triggers__ico(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___dump_triggers__ico\n"); );
    // Body
    if ((1U & (~ (IData)(Vdut___024root___trigger_anySet__ico(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: Internal 'ico' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

bool Vdut___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vdut___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(Vdut___024root___trigger_anySet__act(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @(posedge cam_pclk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 1U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 1 is active: @(negedge rst_n)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 2U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 2 is active: @(negedge cmos_capture_data.rst_n_syn)\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vdut___024root___ctor_var_reset(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___ctor_var_reset\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->rst_n = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1638864771569018232ull);
    vlSelf->cam_pclk = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12636236934795309076ull);
    vlSelf->cam_vsync = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16997869351925223859ull);
    vlSelf->cam_href = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7391894802380392527ull);
    vlSelf->cam_data = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 14362943484164509060ull);
    vlSelf->cam_rst_n = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12886948426289703630ull);
    vlSelf->cam_pwdn = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9172520836941670697ull);
    vlSelf->cmos_frame_clk = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 742140529072965067ull);
    vlSelf->cmos_frame_ce = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12846065931662535845ull);
    vlSelf->cmos_frame_vsync = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7576500532563688940ull);
    vlSelf->cmos_frame_href = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13679804702850732279ull);
    vlSelf->cmos_active_video = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15911308966249695942ull);
    vlSelf->cmos_frame_data = VL_SCOPED_RAND_RESET_I(24, __VscopeHash, 14737558553335829199ull);
    vlSelf->cmos_capture_data__DOT__cam_vsync_d0 = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4239333054108980874ull);
    vlSelf->cmos_capture_data__DOT__cam_vsync_d1 = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3395547641751643431ull);
    vlSelf->cmos_capture_data__DOT__cam_href_d0 = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13569383219472952981ull);
    vlSelf->cmos_capture_data__DOT__cam_href_d1 = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 88653702510242852ull);
    vlSelf->cmos_capture_data__DOT__cmos_ps_cnt = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 6091683549146101852ull);
    vlSelf->cmos_capture_data__DOT__wait_done = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13732348406458091631ull);
    vlSelf->cmos_capture_data__DOT__byte_flag = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12330256205184120898ull);
    vlSelf->cmos_capture_data__DOT__cam_data_d0 = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5966495591766491460ull);
    vlSelf->cmos_capture_data__DOT__cmos_data_16b = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 4177329501538717869ull);
    vlSelf->cmos_capture_data__DOT__byte_flag_d0 = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8651809702862228670ull);
    vlSelf->cmos_capture_data__DOT__pos_vsync = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15806294379181229072ull);
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VstlTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VicoTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggered[__Vi0] = 0;
    }
    vlSelf->__Vtrigprevexpr___TOP__cam_pclk__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__rst_n__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__cmos_capture_data__DOT__rst_n_syn__0 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VnbaTriggered[__Vi0] = 0;
    }
}

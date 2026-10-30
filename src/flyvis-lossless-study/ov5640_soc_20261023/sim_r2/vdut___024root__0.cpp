// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See vdut.h for the primary calling header

#include "vdut__pch.h"

void Vdut___024root___eval_triggers_vec__ico(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_triggers_vec__ico\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VicoTriggered[0U] = ((0xfffffffffffffffeULL 
                                      & vlSelfRef.__VicoTriggered[0U]) 
                                     | (IData)((IData)(vlSelfRef.__VicoFirstIteration)));
}

bool Vdut___024root___trigger_anySet__ico(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___trigger_anySet__ico\n"); );
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

void Vdut___024root___ico_sequent__TOP__0(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___ico_sequent__TOP__0\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.cmos_frame_clk = vlSelfRef.cam_pclk;
}

void Vdut___024root___eval_ico(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_ico\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VicoTriggered[0U])) {
        vlSelfRef.cmos_frame_clk = vlSelfRef.cam_pclk;
    }
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vdut___024root___dump_triggers__ico(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG

bool Vdut___024root___eval_phase__ico(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_phase__ico\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VicoExecute;
    // Body
    Vdut___024root___eval_triggers_vec__ico(vlSelf);
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vdut___024root___dump_triggers__ico(vlSelfRef.__VicoTriggered, "ico"s);
    }
#endif
    __VicoExecute = Vdut___024root___trigger_anySet__ico(vlSelfRef.__VicoTriggered);
    if (__VicoExecute) {
        Vdut___024root___eval_ico(vlSelf);
    }
    return (__VicoExecute);
}

void Vdut___024root___eval_triggers_vec__act(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_triggers_vec__act\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VactTriggered[0U] = (QData)((IData)(
                                                    ((((~ (IData)(vlSelfRef.cmos_capture_data__DOT__rst_n_syn)) 
                                                       & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__cmos_capture_data__DOT__rst_n_syn__0)) 
                                                      << 2U) 
                                                     | ((((~ (IData)(vlSelfRef.rst_n)) 
                                                          & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__rst_n__0)) 
                                                         << 1U) 
                                                        | ((IData)(vlSelfRef.cam_pclk) 
                                                           & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__cam_pclk__0)))))));
    vlSelfRef.__Vtrigprevexpr___TOP__cam_pclk__0 = vlSelfRef.cam_pclk;
    vlSelfRef.__Vtrigprevexpr___TOP__rst_n__0 = vlSelfRef.rst_n;
    vlSelfRef.__Vtrigprevexpr___TOP__cmos_capture_data__DOT__rst_n_syn__0 
        = vlSelfRef.cmos_capture_data__DOT__rst_n_syn;
}

bool Vdut___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___trigger_anySet__act\n"); );
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

void Vdut___024root___nba_sequent__TOP__0(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__0\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*3:0*/ __Vdly__cmos_capture_data__DOT__cmos_ps_cnt;
    __Vdly__cmos_capture_data__DOT__cmos_ps_cnt = 0;
    CData/*0:0*/ __Vdly__cmos_capture_data__DOT__byte_flag;
    __Vdly__cmos_capture_data__DOT__byte_flag = 0;
    // Body
    __Vdly__cmos_capture_data__DOT__cmos_ps_cnt = vlSelfRef.cmos_capture_data__DOT__cmos_ps_cnt;
    __Vdly__cmos_capture_data__DOT__byte_flag = vlSelfRef.cmos_capture_data__DOT__byte_flag;
    if (vlSelfRef.cmos_capture_data__DOT__rst_n_syn) {
        if (((IData)(vlSelfRef.cmos_capture_data__DOT__pos_vsync) 
             & (0x0aU > (IData)(vlSelfRef.cmos_capture_data__DOT__cmos_ps_cnt)))) {
            __Vdly__cmos_capture_data__DOT__cmos_ps_cnt 
                = (0x0000000fU & ((IData)(1U) + (IData)(vlSelfRef.cmos_capture_data__DOT__cmos_ps_cnt)));
        }
        if (((0x0aU == (IData)(vlSelfRef.cmos_capture_data__DOT__cmos_ps_cnt)) 
             & (IData)(vlSelfRef.cmos_capture_data__DOT__pos_vsync))) {
            vlSelfRef.cmos_capture_data__DOT__wait_done = 1U;
        }
        if (vlSelfRef.cam_href) {
            __Vdly__cmos_capture_data__DOT__byte_flag 
                = (1U & (~ (IData)(vlSelfRef.cmos_capture_data__DOT__byte_flag)));
            if (vlSelfRef.cmos_capture_data__DOT__byte_flag) {
                vlSelfRef.cmos_capture_data__DOT__cmos_data_16b 
                    = (((IData)(vlSelfRef.cmos_capture_data__DOT__cam_data_d0) 
                        << 8U) | (IData)(vlSelfRef.cam_data));
                vlSelfRef.cmos_capture_data__DOT__cam_data_d0 
                    = vlSelfRef.cam_data;
                vlSelfRef.cmos_capture_data__DOT__byte_flag_d0 = 1U;
            } else {
                vlSelfRef.cmos_capture_data__DOT__cam_data_d0 
                    = vlSelfRef.cam_data;
                vlSelfRef.cmos_capture_data__DOT__byte_flag_d0 = 0U;
            }
        } else {
            __Vdly__cmos_capture_data__DOT__byte_flag = 0U;
            vlSelfRef.cmos_capture_data__DOT__cam_data_d0 = 0U;
            vlSelfRef.cmos_capture_data__DOT__byte_flag_d0 = 0U;
        }
    } else {
        __Vdly__cmos_capture_data__DOT__cmos_ps_cnt = 0U;
        vlSelfRef.cmos_capture_data__DOT__wait_done = 0U;
        vlSelfRef.cmos_capture_data__DOT__cmos_data_16b = 0U;
        __Vdly__cmos_capture_data__DOT__byte_flag = 0U;
        vlSelfRef.cmos_capture_data__DOT__cam_data_d0 = 0U;
        vlSelfRef.cmos_capture_data__DOT__byte_flag_d0 = 0U;
    }
    vlSelfRef.cmos_capture_data__DOT__cam_vsync_d1 
        = ((IData)(vlSelfRef.cmos_capture_data__DOT__rst_n_syn) 
           && (IData)(vlSelfRef.cmos_capture_data__DOT__cam_vsync_d0));
    vlSelfRef.cmos_capture_data__DOT__cam_href_d1 = 
        ((IData)(vlSelfRef.cmos_capture_data__DOT__rst_n_syn) 
         && (IData)(vlSelfRef.cmos_capture_data__DOT__cam_href_d0));
    vlSelfRef.cmos_capture_data__DOT__cmos_ps_cnt = __Vdly__cmos_capture_data__DOT__cmos_ps_cnt;
    vlSelfRef.cmos_capture_data__DOT__byte_flag = __Vdly__cmos_capture_data__DOT__byte_flag;
    vlSelfRef.cmos_frame_vsync = ((IData)(vlSelfRef.cmos_capture_data__DOT__cam_vsync_d1) 
                                  & (IData)(vlSelfRef.cmos_capture_data__DOT__wait_done));
    vlSelfRef.cmos_capture_data__DOT__cam_vsync_d0 
        = ((IData)(vlSelfRef.cmos_capture_data__DOT__rst_n_syn) 
           && (IData)(vlSelfRef.cam_vsync));
    vlSelfRef.cmos_frame_href = ((IData)(vlSelfRef.cmos_capture_data__DOT__wait_done) 
                                 & (IData)(vlSelfRef.cmos_capture_data__DOT__cam_href_d1));
    vlSelfRef.cmos_capture_data__DOT__cam_href_d0 = 
        ((IData)(vlSelfRef.cmos_capture_data__DOT__rst_n_syn) 
         && (IData)(vlSelfRef.cam_href));
    vlSelfRef.cmos_frame_data = (((0x00f80000U & ((IData)(vlSelfRef.cmos_capture_data__DOT__cmos_data_16b) 
                                                  << 8U)) 
                                  | ((0x0000fc00U & 
                                      ((IData)(vlSelfRef.cmos_capture_data__DOT__cmos_data_16b) 
                                       << 5U)) | (0x000000f8U 
                                                  & ((IData)(vlSelfRef.cmos_capture_data__DOT__cmos_data_16b) 
                                                     << 3U)))) 
                                 & (- (IData)((IData)(vlSelfRef.cmos_capture_data__DOT__wait_done))));
    vlSelfRef.cmos_active_video = vlSelfRef.cmos_frame_href;
    vlSelfRef.cmos_frame_ce = ((IData)(vlSelfRef.cmos_capture_data__DOT__wait_done) 
                               & ((~ (IData)(vlSelfRef.cmos_frame_href)) 
                                  | ((IData)(vlSelfRef.cmos_capture_data__DOT__byte_flag_d0) 
                                     & (IData)(vlSelfRef.cmos_frame_href))));
    vlSelfRef.cmos_capture_data__DOT__pos_vsync = (
                                                   (~ (IData)(vlSelfRef.cmos_capture_data__DOT__cam_vsync_d1)) 
                                                   & (IData)(vlSelfRef.cmos_capture_data__DOT__cam_vsync_d0));
}

void Vdut___024root___nba_sequent__TOP__1(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__1\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.cmos_capture_data__DOT__rst_n_syn = ((IData)(vlSelfRef.rst_n) 
                                                   && (IData)(vlSelfRef.cmos_capture_data__DOT__rst_n_d0));
    vlSelfRef.cmos_capture_data__DOT__rst_n_d0 = vlSelfRef.rst_n;
}

void Vdut___024root___eval_nba(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_nba\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*3:0*/ __Vinline__nba_sequent__TOP__0___Vdly__cmos_capture_data__DOT__cmos_ps_cnt;
    __Vinline__nba_sequent__TOP__0___Vdly__cmos_capture_data__DOT__cmos_ps_cnt = 0;
    CData/*0:0*/ __Vinline__nba_sequent__TOP__0___Vdly__cmos_capture_data__DOT__byte_flag;
    __Vinline__nba_sequent__TOP__0___Vdly__cmos_capture_data__DOT__byte_flag = 0;
    // Body
    if ((5ULL & vlSelfRef.__VnbaTriggered[0U])) {
        __Vinline__nba_sequent__TOP__0___Vdly__cmos_capture_data__DOT__cmos_ps_cnt 
            = vlSelfRef.cmos_capture_data__DOT__cmos_ps_cnt;
        __Vinline__nba_sequent__TOP__0___Vdly__cmos_capture_data__DOT__byte_flag 
            = vlSelfRef.cmos_capture_data__DOT__byte_flag;
        if (vlSelfRef.cmos_capture_data__DOT__rst_n_syn) {
            if (((IData)(vlSelfRef.cmos_capture_data__DOT__pos_vsync) 
                 & (0x0aU > (IData)(vlSelfRef.cmos_capture_data__DOT__cmos_ps_cnt)))) {
                __Vinline__nba_sequent__TOP__0___Vdly__cmos_capture_data__DOT__cmos_ps_cnt 
                    = (0x0000000fU & ((IData)(1U) + (IData)(vlSelfRef.cmos_capture_data__DOT__cmos_ps_cnt)));
            }
            if (((0x0aU == (IData)(vlSelfRef.cmos_capture_data__DOT__cmos_ps_cnt)) 
                 & (IData)(vlSelfRef.cmos_capture_data__DOT__pos_vsync))) {
                vlSelfRef.cmos_capture_data__DOT__wait_done = 1U;
            }
            if (vlSelfRef.cam_href) {
                __Vinline__nba_sequent__TOP__0___Vdly__cmos_capture_data__DOT__byte_flag 
                    = (1U & (~ (IData)(vlSelfRef.cmos_capture_data__DOT__byte_flag)));
                if (vlSelfRef.cmos_capture_data__DOT__byte_flag) {
                    vlSelfRef.cmos_capture_data__DOT__cmos_data_16b 
                        = (((IData)(vlSelfRef.cmos_capture_data__DOT__cam_data_d0) 
                            << 8U) | (IData)(vlSelfRef.cam_data));
                    vlSelfRef.cmos_capture_data__DOT__cam_data_d0 
                        = vlSelfRef.cam_data;
                    vlSelfRef.cmos_capture_data__DOT__byte_flag_d0 = 1U;
                } else {
                    vlSelfRef.cmos_capture_data__DOT__cam_data_d0 
                        = vlSelfRef.cam_data;
                    vlSelfRef.cmos_capture_data__DOT__byte_flag_d0 = 0U;
                }
            } else {
                __Vinline__nba_sequent__TOP__0___Vdly__cmos_capture_data__DOT__byte_flag = 0U;
                vlSelfRef.cmos_capture_data__DOT__cam_data_d0 = 0U;
                vlSelfRef.cmos_capture_data__DOT__byte_flag_d0 = 0U;
            }
        } else {
            __Vinline__nba_sequent__TOP__0___Vdly__cmos_capture_data__DOT__cmos_ps_cnt = 0U;
            vlSelfRef.cmos_capture_data__DOT__wait_done = 0U;
            vlSelfRef.cmos_capture_data__DOT__cmos_data_16b = 0U;
            __Vinline__nba_sequent__TOP__0___Vdly__cmos_capture_data__DOT__byte_flag = 0U;
            vlSelfRef.cmos_capture_data__DOT__cam_data_d0 = 0U;
            vlSelfRef.cmos_capture_data__DOT__byte_flag_d0 = 0U;
        }
        vlSelfRef.cmos_capture_data__DOT__cam_vsync_d1 
            = ((IData)(vlSelfRef.cmos_capture_data__DOT__rst_n_syn) 
               && (IData)(vlSelfRef.cmos_capture_data__DOT__cam_vsync_d0));
        vlSelfRef.cmos_capture_data__DOT__cam_href_d1 
            = ((IData)(vlSelfRef.cmos_capture_data__DOT__rst_n_syn) 
               && (IData)(vlSelfRef.cmos_capture_data__DOT__cam_href_d0));
        vlSelfRef.cmos_capture_data__DOT__cmos_ps_cnt 
            = __Vinline__nba_sequent__TOP__0___Vdly__cmos_capture_data__DOT__cmos_ps_cnt;
        vlSelfRef.cmos_capture_data__DOT__byte_flag 
            = __Vinline__nba_sequent__TOP__0___Vdly__cmos_capture_data__DOT__byte_flag;
        vlSelfRef.cmos_frame_vsync = ((IData)(vlSelfRef.cmos_capture_data__DOT__cam_vsync_d1) 
                                      & (IData)(vlSelfRef.cmos_capture_data__DOT__wait_done));
        vlSelfRef.cmos_capture_data__DOT__cam_vsync_d0 
            = ((IData)(vlSelfRef.cmos_capture_data__DOT__rst_n_syn) 
               && (IData)(vlSelfRef.cam_vsync));
        vlSelfRef.cmos_frame_href = ((IData)(vlSelfRef.cmos_capture_data__DOT__wait_done) 
                                     & (IData)(vlSelfRef.cmos_capture_data__DOT__cam_href_d1));
        vlSelfRef.cmos_capture_data__DOT__cam_href_d0 
            = ((IData)(vlSelfRef.cmos_capture_data__DOT__rst_n_syn) 
               && (IData)(vlSelfRef.cam_href));
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
        vlSelfRef.cmos_active_video = vlSelfRef.cmos_frame_href;
        vlSelfRef.cmos_frame_ce = ((IData)(vlSelfRef.cmos_capture_data__DOT__wait_done) 
                                   & ((~ (IData)(vlSelfRef.cmos_frame_href)) 
                                      | ((IData)(vlSelfRef.cmos_capture_data__DOT__byte_flag_d0) 
                                         & (IData)(vlSelfRef.cmos_frame_href))));
        vlSelfRef.cmos_capture_data__DOT__pos_vsync 
            = ((~ (IData)(vlSelfRef.cmos_capture_data__DOT__cam_vsync_d1)) 
               & (IData)(vlSelfRef.cmos_capture_data__DOT__cam_vsync_d0));
    }
    if ((3ULL & vlSelfRef.__VnbaTriggered[0U])) {
        vlSelfRef.cmos_capture_data__DOT__rst_n_syn 
            = ((IData)(vlSelfRef.rst_n) && (IData)(vlSelfRef.cmos_capture_data__DOT__rst_n_d0));
        vlSelfRef.cmos_capture_data__DOT__rst_n_d0 
            = vlSelfRef.rst_n;
    }
}

void Vdut___024root___trigger_orInto__act_vec_vec(VlUnpacked<QData/*63:0*/, 1> &out, const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___trigger_orInto__act_vec_vec\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = (out[n] | in[n]);
        n = ((IData)(1U) + n);
    } while ((0U >= n));
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vdut___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG

bool Vdut___024root___eval_phase__act(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_phase__act\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vdut___024root___eval_triggers_vec__act(vlSelf);
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vdut___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
    }
#endif
    Vdut___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VnbaTriggered, vlSelfRef.__VactTriggered);
    return (0U);
}

void Vdut___024root___trigger_clear__act(VlUnpacked<QData/*63:0*/, 1> &out) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___trigger_clear__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = 0ULL;
        n = ((IData)(1U) + n);
    } while ((1U > n));
}

bool Vdut___024root___eval_phase__nba(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_phase__nba\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = Vdut___024root___trigger_anySet__act(vlSelfRef.__VnbaTriggered);
    if (__VnbaExecute) {
        Vdut___024root___eval_nba(vlSelf);
        Vdut___024root___trigger_clear__act(vlSelfRef.__VnbaTriggered);
    }
    return (__VnbaExecute);
}

void Vdut___024root___eval(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VicoIterCount;
    IData/*31:0*/ __VnbaIterCount;
    // Body
    __VicoIterCount = 0U;
    vlSelfRef.__VicoFirstIteration = 1U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VicoIterCount)))) {
#ifdef VL_DEBUG
            Vdut___024root___dump_triggers__ico(vlSelfRef.__VicoTriggered, "ico"s);
#endif
            VL_FATAL_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ov5640_soc_20261023\\rtl\\cmos_capture_data.v", 22, "", "DIDNOTCONVERGE: Input combinational region did not converge after '--converge-limit' of 10000 tries");
        }
        __VicoIterCount = ((IData)(1U) + __VicoIterCount);
        vlSelfRef.__VicoPhaseResult = Vdut___024root___eval_phase__ico(vlSelf);
        vlSelfRef.__VicoFirstIteration = 0U;
    } while (vlSelfRef.__VicoPhaseResult);
    __VnbaIterCount = 0U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vdut___024root___dump_triggers__act(vlSelfRef.__VnbaTriggered, "nba"s);
#endif
            VL_FATAL_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ov5640_soc_20261023\\rtl\\cmos_capture_data.v", 22, "", "DIDNOTCONVERGE: NBA region did not converge after '--converge-limit' of 10000 tries");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        vlSelfRef.__VactIterCount = 0U;
        do {
            if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                Vdut___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
#endif
                VL_FATAL_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ov5640_soc_20261023\\rtl\\cmos_capture_data.v", 22, "", "DIDNOTCONVERGE: Active region did not converge after '--converge-limit' of 10000 tries");
            }
            vlSelfRef.__VactIterCount = ((IData)(1U) 
                                         + vlSelfRef.__VactIterCount);
            vlSelfRef.__VactPhaseResult = Vdut___024root___eval_phase__act(vlSelf);
        } while (vlSelfRef.__VactPhaseResult);
        vlSelfRef.__VnbaPhaseResult = Vdut___024root___eval_phase__nba(vlSelf);
    } while (vlSelfRef.__VnbaPhaseResult);
}

#ifdef VL_DEBUG
void Vdut___024root___eval_debug_assertions(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_debug_assertions\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (VL_UNLIKELY(((vlSelfRef.rst_n & 0xfeU)))) {
        Verilated::overWidthError("rst_n");
    }
    if (VL_UNLIKELY(((vlSelfRef.cam_pclk & 0xfeU)))) {
        Verilated::overWidthError("cam_pclk");
    }
    if (VL_UNLIKELY(((vlSelfRef.cam_vsync & 0xfeU)))) {
        Verilated::overWidthError("cam_vsync");
    }
    if (VL_UNLIKELY(((vlSelfRef.cam_href & 0xfeU)))) {
        Verilated::overWidthError("cam_href");
    }
}
#endif  // VL_DEBUG

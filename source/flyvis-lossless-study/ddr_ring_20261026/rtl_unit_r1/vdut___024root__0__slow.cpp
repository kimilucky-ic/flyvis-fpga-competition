// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See vdut.h for the primary calling header

#include "vdut__pch.h"

VL_ATTR_COLD void Vdut___024root___eval_static(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_static\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__Vtrigprevexpr___TOP__clk__0 = vlSelfRef.clk;
}

VL_ATTR_COLD void Vdut___024root___eval_initial(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_initial\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.m_axi_awsize = 3U;
    vlSelfRef.m_axi_awburst = 1U;
}

VL_ATTR_COLD void Vdut___024root___eval_initial__TOP(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_initial__TOP\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
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
            VL_FATAL_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\snapshot_axi_writer.sv", 5, "", "DIDNOTCONVERGE: Settle region did not converge after '--converge-limit' of 10000 tries");
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
    vlSelfRef.m_axi_awvalid = (1U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__bus));
    vlSelfRef.m_axi_bready = (3U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__bus));
    vlSelfRef.m_axi_awlen = (0x000000ffU & ((IData)(vlSelfRef.snapshot_axi_writer__DOT__burst_beats) 
                                            - (IData)(1U)));
    vlSelfRef.m_axi_wlast = (((IData)(vlSelfRef.snapshot_axi_writer__DOT__burst_beats) 
                              - (IData)(1U)) == (IData)(vlSelfRef.snapshot_axi_writer__DOT__beat));
    vlSelfRef.cfg_ready = ((~ (IData)(vlSelfRef.active)) 
                           & ((~ (IData)(vlSelfRef.configured)) 
                              & (0U == (IData)(vlSelfRef.error_flags))));
    vlSelfRef.m_axi_awaddr = (vlSelfRef.snapshot_axi_writer__DOT__record_base 
                              + (((1U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))
                                   ? 0x00000080U : 
                                  (0x00001000U & (- (IData)(
                                                            (4U 
                                                             != (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase)))))) 
                                 + VL_SHIFTL_III(32,32,32, vlSelfRef.snapshot_axi_writer__DOT__acked_beats, 3U)));
    vlSelfRef.m_axi_wstrb = (0x000000ffU & (vlSelfRef.snapshot_axi_writer__DOT__fifo_strb
                                            [vlSelfRef.snapshot_axi_writer__DOT__rp] 
                                            | (- (IData)(
                                                         (4U 
                                                          == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))))));
    if ((1U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))) {
        vlSelfRef.snapshot_axi_writer__DOT__word_bits 
            = vlSelfRef.input_bits;
        vlSelfRef.snapshot_axi_writer__DOT__last_word 
            = (6U == vlSelfRef.snapshot_axi_writer__DOT__input_count);
    } else {
        vlSelfRef.snapshot_axi_writer__DOT__word_bits 
            = vlSelfRef.state_bits;
        vlSelfRef.snapshot_axi_writer__DOT__last_word 
            = (0x00000100U == vlSelfRef.snapshot_axi_writer__DOT__state_count);
    }
    vlSelfRef.m_axi_wvalid = (2U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__bus));
    vlSelfRef.release_ready = ((IData)(vlSelfRef.configured) 
                               & ((0U == (IData)(vlSelfRef.error_flags)) 
                                  & ((vlSelfRef.release_cookie 
                                      == vlSelfRef.snapshot_axi_writer__DOT__session_cookie) 
                                     & ((vlSelfRef.release_sequence 
                                         >= vlSelfRef.released_count) 
                                        & (vlSelfRef.release_sequence 
                                           <= vlSelfRef.committed_count)))));
    vlSelfRef.input_ready = ((IData)(vlSelfRef.active) 
                             & ((1U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase)) 
                                & ((0x40U > (IData)(vlSelfRef.snapshot_axi_writer__DOT__count)) 
                                   & ((0U == (IData)(vlSelfRef.error_flags)) 
                                      & (7U > vlSelfRef.snapshot_axi_writer__DOT__input_count)))));
    vlSelfRef.state_ready = ((IData)(vlSelfRef.active) 
                             & ((0x40U > (IData)(vlSelfRef.snapshot_axi_writer__DOT__count)) 
                                & ((0U == (IData)(vlSelfRef.error_flags)) 
                                   & ((2U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase)) 
                                      & (0x00000101U 
                                         > vlSelfRef.snapshot_axi_writer__DOT__state_count)))));
    if ((4U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))) {
        vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index 
            = vlSelfRef.snapshot_axi_writer__DOT__beat;
        vlSelfRef.snapshot_axi_writer__DOT____VlemCall_0__header_word 
            = (((((((((0U == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index)) 
                      | (1U == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index))) 
                     | (2U == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index))) 
                    | (3U == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index))) 
                   | (4U == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index))) 
                  | (5U == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index))) 
                 | (6U == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index))) 
                | (7U == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index)))
                ? ((0U == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index))
                    ? 0x000100005331314cULL : ((1U 
                                                == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index))
                                                ? (QData)((IData)(vlSelfRef.snapshot_axi_writer__DOT__frame_id))
                                                : (
                                                   (2U 
                                                    == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index))
                                                    ? 0x0000001100000101ULL
                                                    : 
                                                   ((3U 
                                                     == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index))
                                                     ? 0x000004040000001cULL
                                                     : 
                                                    ((4U 
                                                      == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index))
                                                      ? 
                                                     (((QData)((IData)(vlSelfRef.snapshot_axi_writer__DOT__saved_edges)) 
                                                       << 0x00000020U) 
                                                      | (QData)((IData)(vlSelfRef.snapshot_axi_writer__DOT__saved_cycles)))
                                                      : 
                                                     ((5U 
                                                       == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index))
                                                       ? 
                                                      (0x0000200000000000ULL 
                                                       | (QData)((IData)(vlSelfRef.snapshot_axi_writer__DOT__saved_states)))
                                                       : 
                                                      ((6U 
                                                        == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index))
                                                        ? 
                                                       (((QData)((IData)(vlSelfRef.snapshot_axi_writer__DOT__state_hash)) 
                                                         << 0x00000020U) 
                                                        | (QData)((IData)(vlSelfRef.snapshot_axi_writer__DOT__input_hash)))
                                                        : 0x0000100000000080ULL)))))))
                : ((8U == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index))
                    ? 0x3ba3d70a00110005ULL : ((9U 
                                                == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index))
                                                ? (QData)((IData)(vlSelfRef.snapshot_axi_writer__DOT__saved_faults))
                                                : (
                                                   (0x0aU 
                                                    == (IData)(vlSelfRef.__Vfunc_snapshot_axi_writer__DOT__header_word__0__index))
                                                    ? 
                                                   (((QData)((IData)(vlSelfRef.snapshot_axi_writer__DOT__session_cookie)) 
                                                     << 0x00000020U) 
                                                    | (QData)((IData)(
                                                                      ((IData)(1U) 
                                                                       + vlSelfRef.committed_count))))
                                                    : 0ULL))));
    } else {
        vlSelfRef.snapshot_axi_writer__DOT____VlemCall_0__header_word 
            = vlSelfRef.snapshot_axi_writer__DOT__fifo_data
            [vlSelfRef.snapshot_axi_writer__DOT__rp];
    }
    vlSelfRef.m_axi_wdata = vlSelfRef.snapshot_axi_writer__DOT____VlemCall_0__header_word;
    vlSelfRef.__VdfgRegularize_h52e72c00_0_1 = ((~ (IData)(vlSelfRef.active)) 
                                                & (IData)(vlSelfRef.configured));
    vlSelfRef.snapshot_axi_writer__DOT__pop = ((IData)(vlSelfRef.m_axi_wvalid) 
                                               & ((IData)(vlSelfRef.m_axi_wready) 
                                                  & (4U 
                                                     != (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))));
    vlSelfRef.snapshot_axi_writer__DOT__accept_word 
        = (((IData)(vlSelfRef.input_valid) & (IData)(vlSelfRef.input_ready)) 
           | ((IData)(vlSelfRef.state_valid) & (IData)(vlSelfRef.state_ready)));
    vlSelfRef.capacity_exhausted = ((((vlSelfRef.committed_count 
                                       - vlSelfRef.released_count) 
                                      >= (IData)(vlSelfRef.snapshot_axi_writer__DOT__slots)) 
                                     | ((IData)(vlSelfRef.snapshot_axi_writer__DOT__sequence_exhausted) 
                                        | ((0xffffffffU 
                                            == vlSelfRef.committed_count) 
                                           | ((IData)(
                                                      (1ULL 
                                                       & ((0x0000000000002000ULL 
                                                           + (QData)((IData)(vlSelfRef.snapshot_axi_writer__DOT__record_base))) 
                                                          >> 0x00000020U))) 
                                              | ((0x00000001ffffffffULL 
                                                  & (0x0000000000002000ULL 
                                                     + (QData)((IData)(vlSelfRef.snapshot_axi_writer__DOT__record_base)))) 
                                                 > (QData)((IData)(vlSelfRef.snapshot_axi_writer__DOT__end_address))))))) 
                                    & (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_1));
    vlSelfRef.snapshot_axi_writer__DOT__push = ((IData)(vlSelfRef.snapshot_axi_writer__DOT__accept_word) 
                                                & ((IData)(vlSelfRef.snapshot_axi_writer__DOT__half) 
                                                   | (IData)(vlSelfRef.snapshot_axi_writer__DOT__last_word)));
    vlSelfRef.begin_ready = ((IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_1) 
                             & ((~ (IData)(vlSelfRef.capacity_exhausted)) 
                                & (0U == (IData)(vlSelfRef.error_flags))));
}

VL_ATTR_COLD void Vdut___024root___eval_stl(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_stl\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VstlTriggered[0U])) {
        Vdut___024root___stl_sequent__TOP__0(vlSelf);
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
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @(posedge clk)\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vdut___024root___ctor_var_reset(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___ctor_var_reset\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->clk = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16707436170211756652ull);
    vlSelf->reset = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9928399931838511862ull);
    vlSelf->cfg_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6248242304995844936ull);
    vlSelf->cfg_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3984417237715664170ull);
    vlSelf->cfg_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5314371911542424974ull);
    vlSelf->cfg_end = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14285423868348168024ull);
    vlSelf->cfg_first_frame = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3613201675892191759ull);
    vlSelf->cfg_slots = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 17246983616710363210ull);
    vlSelf->cfg_cookie = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16286991198690016146ull);
    vlSelf->release_sequence = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 268715236352076113ull);
    vlSelf->release_cookie = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8590455011974996725ull);
    vlSelf->release_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11524967974582733144ull);
    vlSelf->release_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11795450719872017728ull);
    vlSelf->released_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6778211003619489094ull);
    vlSelf->begin_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16506624435180496128ull);
    vlSelf->begin_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9482934434659335177ull);
    vlSelf->configured = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8438889958579756013ull);
    vlSelf->active = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12797771265061833892ull);
    vlSelf->capacity_exhausted = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8496005861256398201ull);
    vlSelf->input_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4270309033785105452ull);
    vlSelf->input_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5031374033172706937ull);
    vlSelf->input_bits = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9177295728181537852ull);
    vlSelf->state_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8151811770426067351ull);
    vlSelf->state_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4559697342327645542ull);
    vlSelf->state_id = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 7534972940745705553ull);
    vlSelf->state_bits = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11872404314182647930ull);
    vlSelf->state_last = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14654066745272030000ull);
    vlSelf->info_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7526746080845702260ull);
    vlSelf->info_cycles = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 349765087241088275ull);
    vlSelf->info_edges = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10025330969795865921ull);
    vlSelf->info_states = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16912426576256643770ull);
    vlSelf->info_faults = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18108527953951892124ull);
    vlSelf->publish = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15362266082144979547ull);
    vlSelf->published_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3208562451885681960ull);
    vlSelf->published_frame = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15816029982436648846ull);
    vlSelf->committed_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6602422443527026371ull);
    vlSelf->error_flags = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6518861505241357035ull);
    vlSelf->m_axi_awaddr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13558266821849222593ull);
    vlSelf->m_axi_awlen = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 15527027863330074270ull);
    vlSelf->m_axi_awsize = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 17768164634708584365ull);
    vlSelf->m_axi_awburst = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 16027732775651784324ull);
    vlSelf->m_axi_awvalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17994771565963626208ull);
    vlSelf->m_axi_awready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16573481163850279297ull);
    vlSelf->m_axi_wdata = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 1286380785785437420ull);
    vlSelf->m_axi_wstrb = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 15721383833457952779ull);
    vlSelf->m_axi_wlast = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2914646395814725164ull);
    vlSelf->m_axi_wvalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17462522629772039856ull);
    vlSelf->m_axi_wready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10076110868751280388ull);
    vlSelf->m_axi_bresp = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 3179402000051064225ull);
    vlSelf->m_axi_bvalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17532096651654485089ull);
    vlSelf->m_axi_bready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 919615779156835605ull);
    vlSelf->snapshot_axi_writer__DOT__phase = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 2926372828977295575ull);
    vlSelf->snapshot_axi_writer__DOT__bus = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 11250315841842607581ull);
    vlSelf->snapshot_axi_writer__DOT__record_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18320112971194910577ull);
    vlSelf->snapshot_axi_writer__DOT__end_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13967257201543609731ull);
    vlSelf->snapshot_axi_writer__DOT__frame_id = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7163588050744834149ull);
    vlSelf->snapshot_axi_writer__DOT__acked_beats = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8854569252056001731ull);
    vlSelf->snapshot_axi_writer__DOT__slots = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 8912765887954287147ull);
    vlSelf->snapshot_axi_writer__DOT__write_slot = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 8265543843963850696ull);
    vlSelf->snapshot_axi_writer__DOT__ring_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9141763233896742048ull);
    vlSelf->snapshot_axi_writer__DOT__session_cookie = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9141829193584277345ull);
    vlSelf->snapshot_axi_writer__DOT__sequence_exhausted = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 610404171620972060ull);
    vlSelf->snapshot_axi_writer__DOT__wp = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 1820681668369137099ull);
    vlSelf->snapshot_axi_writer__DOT__rp = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 15749529467739223924ull);
    vlSelf->snapshot_axi_writer__DOT__count = VL_SCOPED_RAND_RESET_I(7, __VscopeHash, 10420488501752592711ull);
    for (int __Vi0 = 0; __Vi0 < 64; ++__Vi0) {
        vlSelf->snapshot_axi_writer__DOT__fifo_data[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15663610420323622068ull);
    }
    for (int __Vi0 = 0; __Vi0 < 64; ++__Vi0) {
        vlSelf->snapshot_axi_writer__DOT__fifo_strb[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 17447256382189884606ull);
    }
    vlSelf->snapshot_axi_writer__DOT__half = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3036520389406379022ull);
    vlSelf->snapshot_axi_writer__DOT__low_word = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15766867644981651556ull);
    vlSelf->snapshot_axi_writer__DOT__input_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2956661461980805831ull);
    vlSelf->snapshot_axi_writer__DOT__state_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7632393851331633352ull);
    vlSelf->snapshot_axi_writer__DOT__input_hash = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2430339693421146812ull);
    vlSelf->snapshot_axi_writer__DOT__state_hash = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9376217778213348428ull);
    vlSelf->snapshot_axi_writer__DOT__saved_cycles = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2151692704970859476ull);
    vlSelf->snapshot_axi_writer__DOT__saved_edges = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5269111716708060633ull);
    vlSelf->snapshot_axi_writer__DOT__saved_states = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13475846246440859411ull);
    vlSelf->snapshot_axi_writer__DOT__saved_faults = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1517741439387378168ull);
    vlSelf->snapshot_axi_writer__DOT__got_info = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2169864322587979351ull);
    vlSelf->snapshot_axi_writer__DOT__burst_beats = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 12189255401756647647ull);
    vlSelf->snapshot_axi_writer__DOT__beat = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 10500365784266458943ull);
    vlSelf->snapshot_axi_writer__DOT__timeout_count = VL_SCOPED_RAND_RESET_I(7, __VscopeHash, 12358288181459288310ull);
    vlSelf->snapshot_axi_writer__DOT__push = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9394721942619099816ull);
    vlSelf->snapshot_axi_writer__DOT__pop = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2142886763826404986ull);
    vlSelf->snapshot_axi_writer__DOT__accept_word = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4250153160908460437ull);
    vlSelf->snapshot_axi_writer__DOT__last_word = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4685956314023997811ull);
    vlSelf->snapshot_axi_writer__DOT__word_bits = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1226122848724390998ull);
    vlSelf->__Vfunc_snapshot_axi_writer__DOT__header_word__0__index = 0;
    vlSelf->__VdfgRegularize_h52e72c00_0_1 = 0;
    vlSelf->__Vdly__active = 0;
    vlSelf->__Vdly__snapshot_axi_writer__DOT__phase = 0;
    vlSelf->__Vdly__snapshot_axi_writer__DOT__bus = 0;
    vlSelf->__Vdly__snapshot_axi_writer__DOT__record_base = 0;
    vlSelf->__Vdly__snapshot_axi_writer__DOT__frame_id = 0;
    vlSelf->__Vdly__committed_count = 0;
    vlSelf->__Vdly__snapshot_axi_writer__DOT__write_slot = 0;
    vlSelf->__Vdly__snapshot_axi_writer__DOT__count = 0;
    vlSelf->__Vdly__snapshot_axi_writer__DOT__half = 0;
    vlSelf->__Vdly__snapshot_axi_writer__DOT__acked_beats = 0;
    vlSelf->__Vdly__snapshot_axi_writer__DOT__input_count = 0;
    vlSelf->__Vdly__snapshot_axi_writer__DOT__state_count = 0;
    vlSelf->__Vdly__snapshot_axi_writer__DOT__input_hash = 0;
    vlSelf->__Vdly__snapshot_axi_writer__DOT__state_hash = 0;
    vlSelf->__Vdly__snapshot_axi_writer__DOT__got_info = 0;
    vlSelf->__Vdly__error_flags = 0;
    vlSelf->__Vdly__snapshot_axi_writer__DOT__burst_beats = 0;
    vlSelf->__Vdly__snapshot_axi_writer__DOT__beat = 0;
    vlSelf->__Vdly__snapshot_axi_writer__DOT__timeout_count = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VstlTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VicoTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggered[__Vi0] = 0;
    }
    vlSelf->__Vtrigprevexpr___TOP__clk__0 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VnbaTriggered[__Vi0] = 0;
    }
}

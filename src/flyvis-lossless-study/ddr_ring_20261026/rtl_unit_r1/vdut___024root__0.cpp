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
    vlSelfRef.snapshot_axi_writer__DOT__word_bits = 
        ((1U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))
          ? vlSelfRef.input_bits : vlSelfRef.state_bits);
    vlSelfRef.snapshot_axi_writer__DOT__pop = ((IData)(vlSelfRef.m_axi_wvalid) 
                                               & ((IData)(vlSelfRef.m_axi_wready) 
                                                  & (4U 
                                                     != (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))));
    vlSelfRef.release_ready = ((IData)(vlSelfRef.configured) 
                               & ((0U == (IData)(vlSelfRef.error_flags)) 
                                  & ((vlSelfRef.release_cookie 
                                      == vlSelfRef.snapshot_axi_writer__DOT__session_cookie) 
                                     & ((vlSelfRef.release_sequence 
                                         >= vlSelfRef.released_count) 
                                        & (vlSelfRef.release_sequence 
                                           <= vlSelfRef.committed_count)))));
    vlSelfRef.snapshot_axi_writer__DOT__accept_word 
        = (((IData)(vlSelfRef.input_valid) & (IData)(vlSelfRef.input_ready)) 
           | ((IData)(vlSelfRef.state_valid) & (IData)(vlSelfRef.state_ready)));
    vlSelfRef.snapshot_axi_writer__DOT__push = ((IData)(vlSelfRef.snapshot_axi_writer__DOT__accept_word) 
                                                & ((IData)(vlSelfRef.snapshot_axi_writer__DOT__half) 
                                                   | (IData)(vlSelfRef.snapshot_axi_writer__DOT__last_word)));
}

void Vdut___024root___eval_ico(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_ico\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VicoTriggered[0U])) {
        vlSelfRef.snapshot_axi_writer__DOT__word_bits 
            = ((1U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))
                ? vlSelfRef.input_bits : vlSelfRef.state_bits);
        vlSelfRef.snapshot_axi_writer__DOT__pop = ((IData)(vlSelfRef.m_axi_wvalid) 
                                                   & ((IData)(vlSelfRef.m_axi_wready) 
                                                      & (4U 
                                                         != (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))));
        vlSelfRef.release_ready = ((IData)(vlSelfRef.configured) 
                                   & ((0U == (IData)(vlSelfRef.error_flags)) 
                                      & ((vlSelfRef.release_cookie 
                                          == vlSelfRef.snapshot_axi_writer__DOT__session_cookie) 
                                         & ((vlSelfRef.release_sequence 
                                             >= vlSelfRef.released_count) 
                                            & (vlSelfRef.release_sequence 
                                               <= vlSelfRef.committed_count)))));
        vlSelfRef.snapshot_axi_writer__DOT__accept_word 
            = (((IData)(vlSelfRef.input_valid) & (IData)(vlSelfRef.input_ready)) 
               | ((IData)(vlSelfRef.state_valid) & (IData)(vlSelfRef.state_ready)));
        vlSelfRef.snapshot_axi_writer__DOT__push = 
            ((IData)(vlSelfRef.snapshot_axi_writer__DOT__accept_word) 
             & ((IData)(vlSelfRef.snapshot_axi_writer__DOT__half) 
                | (IData)(vlSelfRef.snapshot_axi_writer__DOT__last_word)));
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
                                                    ((IData)(vlSelfRef.clk) 
                                                     & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__clk__0)))));
    vlSelfRef.__Vtrigprevexpr___TOP__clk__0 = vlSelfRef.clk;
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
    CData/*5:0*/ __Vdly__snapshot_axi_writer__DOT__rp;
    __Vdly__snapshot_axi_writer__DOT__rp = 0;
    CData/*5:0*/ __Vdly__snapshot_axi_writer__DOT__wp;
    __Vdly__snapshot_axi_writer__DOT__wp = 0;
    QData/*63:0*/ __VdlyVal__snapshot_axi_writer__DOT__fifo_data__v0;
    __VdlyVal__snapshot_axi_writer__DOT__fifo_data__v0 = 0;
    CData/*5:0*/ __VdlyDim0__snapshot_axi_writer__DOT__fifo_data__v0;
    __VdlyDim0__snapshot_axi_writer__DOT__fifo_data__v0 = 0;
    CData/*0:0*/ __VdlySet__snapshot_axi_writer__DOT__fifo_data__v0;
    __VdlySet__snapshot_axi_writer__DOT__fifo_data__v0 = 0;
    CData/*7:0*/ __VdlyVal__snapshot_axi_writer__DOT__fifo_strb__v0;
    __VdlyVal__snapshot_axi_writer__DOT__fifo_strb__v0 = 0;
    CData/*5:0*/ __VdlyDim0__snapshot_axi_writer__DOT__fifo_strb__v0;
    __VdlyDim0__snapshot_axi_writer__DOT__fifo_strb__v0 = 0;
    // Body
    __Vdly__snapshot_axi_writer__DOT__rp = vlSelfRef.snapshot_axi_writer__DOT__rp;
    if ((1U & (~ (IData)(vlSelfRef.reset)))) {
        if (VL_UNLIKELY((((vlSelfRef.released_count 
                           > vlSelfRef.committed_count) 
                          | ((vlSelfRef.committed_count 
                              - vlSelfRef.released_count) 
                             > (IData)(vlSelfRef.snapshot_axi_writer__DOT__slots)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: snapshot_axi_writer.sv:213: Assertion failed in %m: Ring ownership invariant\n",3, 'M',vlSymsp->name(),"snapshot_axi_writer", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\snapshot_axi_writer.sv", 213, "", false);
        }
        if (VL_UNLIKELY(((0x40U < (IData)(vlSelfRef.snapshot_axi_writer__DOT__count))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: snapshot_axi_writer.sv:214: Assertion failed in %m: FIFO overflow\n",3, 'M',vlSymsp->name(),"snapshot_axi_writer", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\snapshot_axi_writer.sv", 214, "", false);
        }
        if (VL_UNLIKELY((((IData)(vlSelfRef.snapshot_axi_writer__DOT__pop) 
                          & (0U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__count)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: snapshot_axi_writer.sv:215: Assertion failed in %m: FIFO underflow\n",3, 'M',vlSymsp->name(),"snapshot_axi_writer", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\snapshot_axi_writer.sv", 215, "", false);
        }
        if (VL_UNLIKELY(((((IData)(vlSelfRef.m_axi_awvalid) 
                           & (IData)(vlSelfRef.m_axi_awready)) 
                          & (0x00001000U < ((0x00000fffU 
                                             & vlSelfRef.m_axi_awaddr) 
                                            + VL_SHIFTL_III(32,32,32, 
                                                            ((IData)(1U) 
                                                             + (IData)(vlSelfRef.m_axi_awlen)), 3U))))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: snapshot_axi_writer.sv:216: Assertion failed in %m: AXI4KiB boundary\n",3, 'M',vlSymsp->name(),"snapshot_axi_writer", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\snapshot_axi_writer.sv", 216, "", false);
        }
    }
    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__write_slot 
        = vlSelfRef.snapshot_axi_writer__DOT__write_slot;
    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__got_info 
        = vlSelfRef.snapshot_axi_writer__DOT__got_info;
    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__timeout_count 
        = vlSelfRef.snapshot_axi_writer__DOT__timeout_count;
    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__half 
        = vlSelfRef.snapshot_axi_writer__DOT__half;
    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__acked_beats 
        = vlSelfRef.snapshot_axi_writer__DOT__acked_beats;
    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__burst_beats 
        = vlSelfRef.snapshot_axi_writer__DOT__burst_beats;
    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__bus 
        = vlSelfRef.snapshot_axi_writer__DOT__bus;
    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__record_base 
        = vlSelfRef.snapshot_axi_writer__DOT__record_base;
    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__frame_id 
        = vlSelfRef.snapshot_axi_writer__DOT__frame_id;
    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__input_hash 
        = vlSelfRef.snapshot_axi_writer__DOT__input_hash;
    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__state_hash 
        = vlSelfRef.snapshot_axi_writer__DOT__state_hash;
    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__beat 
        = vlSelfRef.snapshot_axi_writer__DOT__beat;
    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__input_count 
        = vlSelfRef.snapshot_axi_writer__DOT__input_count;
    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__state_count 
        = vlSelfRef.snapshot_axi_writer__DOT__state_count;
    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__count 
        = vlSelfRef.snapshot_axi_writer__DOT__count;
    vlSelfRef.__Vdly__committed_count = vlSelfRef.committed_count;
    vlSelfRef.__Vdly__error_flags = vlSelfRef.error_flags;
    vlSelfRef.__Vdly__active = vlSelfRef.active;
    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__phase 
        = vlSelfRef.snapshot_axi_writer__DOT__phase;
    __Vdly__snapshot_axi_writer__DOT__wp = vlSelfRef.snapshot_axi_writer__DOT__wp;
    __VdlySet__snapshot_axi_writer__DOT__fifo_data__v0 = 0U;
    if (vlSelfRef.reset) {
        __Vdly__snapshot_axi_writer__DOT__rp = 0U;
        __Vdly__snapshot_axi_writer__DOT__wp = 0U;
        vlSelfRef.snapshot_axi_writer__DOT__end_address = 0U;
        vlSelfRef.snapshot_axi_writer__DOT__session_cookie = 0U;
        vlSelfRef.configured = 0U;
        vlSelfRef.released_count = 0U;
        vlSelfRef.__Vdly__active = 0U;
        vlSelfRef.__Vdly__snapshot_axi_writer__DOT__phase = 0U;
        vlSelfRef.__Vdly__snapshot_axi_writer__DOT__bus = 0U;
        vlSelfRef.__Vdly__snapshot_axi_writer__DOT__record_base = 0U;
        vlSelfRef.__Vdly__snapshot_axi_writer__DOT__frame_id = 0U;
        vlSelfRef.__Vdly__committed_count = 0U;
        vlSelfRef.__Vdly__snapshot_axi_writer__DOT__write_slot = 0U;
        vlSelfRef.snapshot_axi_writer__DOT__sequence_exhausted = 0U;
        vlSelfRef.__Vdly__snapshot_axi_writer__DOT__count = 0U;
        vlSelfRef.__Vdly__snapshot_axi_writer__DOT__half = 0U;
        vlSelfRef.snapshot_axi_writer__DOT__low_word = 0U;
        vlSelfRef.__Vdly__snapshot_axi_writer__DOT__acked_beats = 0U;
        vlSelfRef.__Vdly__snapshot_axi_writer__DOT__input_count = 0U;
        vlSelfRef.__Vdly__snapshot_axi_writer__DOT__state_count = 0U;
        vlSelfRef.__Vdly__snapshot_axi_writer__DOT__input_hash = 0U;
        vlSelfRef.__Vdly__snapshot_axi_writer__DOT__state_hash = 0U;
        vlSelfRef.__Vdly__snapshot_axi_writer__DOT__got_info = 0U;
        vlSelfRef.snapshot_axi_writer__DOT__saved_cycles = 0U;
        vlSelfRef.snapshot_axi_writer__DOT__saved_edges = 0U;
        vlSelfRef.snapshot_axi_writer__DOT__saved_states = 0U;
        vlSelfRef.snapshot_axi_writer__DOT__saved_faults = 0U;
        vlSelfRef.__Vdly__error_flags = 0U;
        vlSelfRef.publish = 0U;
        vlSelfRef.published_base = 0U;
        vlSelfRef.published_frame = 0U;
        vlSelfRef.__Vdly__snapshot_axi_writer__DOT__burst_beats = 0U;
        vlSelfRef.__Vdly__snapshot_axi_writer__DOT__beat = 0U;
        vlSelfRef.__Vdly__snapshot_axi_writer__DOT__timeout_count = 0U;
    } else {
        if (vlSelfRef.snapshot_axi_writer__DOT__pop) {
            __Vdly__snapshot_axi_writer__DOT__rp = 
                (0x0000003fU & ((IData)(1U) + (IData)(vlSelfRef.snapshot_axi_writer__DOT__rp)));
        }
        if (vlSelfRef.snapshot_axi_writer__DOT__push) {
            __VdlyVal__snapshot_axi_writer__DOT__fifo_data__v0 
                = ((IData)(vlSelfRef.snapshot_axi_writer__DOT__half)
                    ? (((QData)((IData)(vlSelfRef.snapshot_axi_writer__DOT__word_bits)) 
                        << 0x00000020U) | (QData)((IData)(vlSelfRef.snapshot_axi_writer__DOT__low_word)))
                    : (QData)((IData)(vlSelfRef.snapshot_axi_writer__DOT__word_bits)));
            __VdlyDim0__snapshot_axi_writer__DOT__fifo_data__v0 
                = vlSelfRef.snapshot_axi_writer__DOT__wp;
            __VdlySet__snapshot_axi_writer__DOT__fifo_data__v0 = 1U;
            __VdlyVal__snapshot_axi_writer__DOT__fifo_strb__v0 
                = (0x000000ffU & (0x0fU | (- (IData)((IData)(vlSelfRef.snapshot_axi_writer__DOT__half)))));
            __VdlyDim0__snapshot_axi_writer__DOT__fifo_strb__v0 
                = vlSelfRef.snapshot_axi_writer__DOT__wp;
            __Vdly__snapshot_axi_writer__DOT__wp = 
                (0x0000003fU & ((IData)(1U) + (IData)(vlSelfRef.snapshot_axi_writer__DOT__wp)));
        }
        if (vlSelfRef.release_valid) {
            if (vlSelfRef.release_ready) {
                vlSelfRef.released_count = vlSelfRef.release_sequence;
            }
            if ((1U & (~ (IData)(vlSelfRef.release_ready)))) {
                vlSelfRef.__Vdly__error_flags = (0x00000020U 
                                                 | (IData)(vlSelfRef.__Vdly__error_flags));
            }
        }
        if (((IData)(vlSelfRef.cfg_valid) & (IData)(vlSelfRef.cfg_ready))) {
            if ((1U & (~ (((((0U != (0x00000fffU & vlSelfRef.cfg_base)) 
                             | (vlSelfRef.cfg_end <= vlSelfRef.cfg_base)) 
                            | (0U == (IData)(vlSelfRef.cfg_slots))) 
                           | (((QData)((IData)(vlSelfRef.cfg_base)) 
                               + VL_SHIFTL_QQI(64,64,32, (QData)((IData)(vlSelfRef.cfg_slots)), 0x0000000dU)) 
                              > (QData)((IData)(vlSelfRef.cfg_end)))) 
                          | (0x0000000100000000ULL 
                             < (0x00000001ffffffffULL 
                                & ((QData)((IData)(vlSelfRef.cfg_first_frame)) 
                                   + (QData)((IData)(vlSelfRef.cfg_slots))))))))) {
                vlSelfRef.snapshot_axi_writer__DOT__end_address 
                    = vlSelfRef.cfg_end;
                vlSelfRef.snapshot_axi_writer__DOT__session_cookie 
                    = vlSelfRef.cfg_cookie;
                vlSelfRef.configured = 1U;
            }
            if ((((((0U != (0x00000fffU & vlSelfRef.cfg_base)) 
                    | (vlSelfRef.cfg_end <= vlSelfRef.cfg_base)) 
                   | (0U == (IData)(vlSelfRef.cfg_slots))) 
                  | (((QData)((IData)(vlSelfRef.cfg_base)) 
                      + VL_SHIFTL_QQI(64,64,32, (QData)((IData)(vlSelfRef.cfg_slots)), 0x0000000dU)) 
                     > (QData)((IData)(vlSelfRef.cfg_end)))) 
                 | (0x0000000100000000ULL < (0x00000001ffffffffULL 
                                             & ((QData)((IData)(vlSelfRef.cfg_first_frame)) 
                                                + (QData)((IData)(vlSelfRef.cfg_slots))))))) {
                vlSelfRef.__Vdly__error_flags = (8U 
                                                 | (IData)(vlSelfRef.__Vdly__error_flags));
            } else {
                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__record_base 
                    = vlSelfRef.cfg_base;
                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__write_slot = 0U;
                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__frame_id 
                    = vlSelfRef.cfg_first_frame;
            }
        }
        vlSelfRef.publish = 0U;
        if (((IData)(vlSelfRef.begin_valid) & (IData)(vlSelfRef.begin_ready))) {
            vlSelfRef.__Vdly__active = 1U;
            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__phase = 1U;
            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__input_count = 0U;
            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__state_count = 0U;
            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__half = 0U;
            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__input_hash = 0U;
            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__state_hash = 0U;
            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__acked_beats = 0U;
            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__got_info = 0U;
        }
        if (vlSelfRef.snapshot_axi_writer__DOT__accept_word) {
            if (((IData)(vlSelfRef.snapshot_axi_writer__DOT__half) 
                 | (IData)(vlSelfRef.snapshot_axi_writer__DOT__last_word))) {
                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__half = 0U;
            } else {
                vlSelfRef.snapshot_axi_writer__DOT__low_word 
                    = vlSelfRef.snapshot_axi_writer__DOT__word_bits;
                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__half = 1U;
            }
            if ((1U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))) {
                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__input_count 
                    = ((IData)(1U) + vlSelfRef.snapshot_axi_writer__DOT__input_count);
                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__input_hash 
                    = ((((vlSelfRef.snapshot_axi_writer__DOT__input_hash 
                          << 1U) | (vlSelfRef.snapshot_axi_writer__DOT__input_hash 
                                    >> 0x1fU)) ^ vlSelfRef.input_bits) 
                       ^ vlSelfRef.snapshot_axi_writer__DOT__input_count);
            } else {
                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__state_count 
                    = ((IData)(1U) + vlSelfRef.snapshot_axi_writer__DOT__state_count);
                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__state_hash 
                    = ((((vlSelfRef.snapshot_axi_writer__DOT__state_hash 
                          << 1U) | (vlSelfRef.snapshot_axi_writer__DOT__state_hash 
                                    >> 0x1fU)) ^ vlSelfRef.state_bits) 
                       ^ vlSelfRef.snapshot_axi_writer__DOT__state_count);
                if ((((IData)(vlSelfRef.state_id) != vlSelfRef.snapshot_axi_writer__DOT__state_count) 
                     | ((IData)(vlSelfRef.state_last) 
                        != (IData)(vlSelfRef.snapshot_axi_writer__DOT__last_word)))) {
                    vlSelfRef.__Vdly__error_flags = 
                        (1U | (IData)(vlSelfRef.__Vdly__error_flags));
                }
            }
        }
        if ((2U == (((IData)(vlSelfRef.snapshot_axi_writer__DOT__push) 
                     << 1U) | (IData)(vlSelfRef.snapshot_axi_writer__DOT__pop)))) {
            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__count 
                = (0x0000007fU & ((IData)(1U) + (IData)(vlSelfRef.snapshot_axi_writer__DOT__count)));
        } else if ((1U == (((IData)(vlSelfRef.snapshot_axi_writer__DOT__push) 
                            << 1U) | (IData)(vlSelfRef.snapshot_axi_writer__DOT__pop)))) {
            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__count 
                = (0x0000007fU & ((IData)(vlSelfRef.snapshot_axi_writer__DOT__count) 
                                  - (IData)(1U)));
        }
        if (((IData)(vlSelfRef.info_valid) & (IData)(vlSelfRef.active))) {
            vlSelfRef.snapshot_axi_writer__DOT__saved_cycles 
                = vlSelfRef.info_cycles;
            vlSelfRef.snapshot_axi_writer__DOT__saved_edges 
                = vlSelfRef.info_edges;
            vlSelfRef.snapshot_axi_writer__DOT__saved_states 
                = vlSelfRef.info_states;
            vlSelfRef.snapshot_axi_writer__DOT__saved_faults 
                = vlSelfRef.info_faults;
            if (((((((0x00000011U != vlSelfRef.info_edges) 
                     | (0x00000101U != vlSelfRef.info_states)) 
                    | (0U != vlSelfRef.info_faults)) 
                   | (IData)(vlSelfRef.snapshot_axi_writer__DOT__got_info)) 
                  | (0x00000101U != vlSelfRef.snapshot_axi_writer__DOT__state_count)) 
                 | (7U != vlSelfRef.snapshot_axi_writer__DOT__input_count))) {
                vlSelfRef.__Vdly__error_flags = (0x00000010U 
                                                 | (IData)(vlSelfRef.__Vdly__error_flags));
            }
            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__got_info = 1U;
        }
        if ((((3U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase)) 
              & (IData)(vlSelfRef.snapshot_axi_writer__DOT__got_info)) 
             & (0U == (IData)(vlSelfRef.error_flags)))) {
            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__phase = 4U;
            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__acked_beats = 0U;
        }
        if (((((0U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__bus)) 
               | ((1U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__bus)) 
                  & (IData)(vlSelfRef.m_axi_awready))) 
              | ((2U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__bus)) 
                 & (IData)(vlSelfRef.m_axi_wready))) 
             | ((3U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__bus)) 
                & (IData)(vlSelfRef.m_axi_bvalid)))) {
            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__timeout_count = 0U;
        } else if ((0x60U > (IData)(vlSelfRef.snapshot_axi_writer__DOT__timeout_count))) {
            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__timeout_count 
                = (0x0000007fU & ((IData)(1U) + (IData)(vlSelfRef.snapshot_axi_writer__DOT__timeout_count)));
            if ((0x5fU == (IData)(vlSelfRef.snapshot_axi_writer__DOT__timeout_count))) {
                vlSelfRef.__Vdly__error_flags = (4U 
                                                 | (IData)(vlSelfRef.__Vdly__error_flags));
            }
        }
        if ((2U & (IData)(vlSelfRef.snapshot_axi_writer__DOT__bus))) {
            if ((1U & (IData)(vlSelfRef.snapshot_axi_writer__DOT__bus))) {
                if (vlSelfRef.m_axi_bvalid) {
                    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__bus = 0U;
                    if ((0U != (IData)(vlSelfRef.m_axi_bresp))) {
                        vlSelfRef.__Vdly__error_flags 
                            = (2U | (IData)(vlSelfRef.__Vdly__error_flags));
                    } else if ((0U == (IData)(vlSelfRef.error_flags))) {
                        if ((4U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))) {
                            vlSelfRef.__Vdly__committed_count 
                                = ((IData)(1U) + vlSelfRef.committed_count);
                            vlSelfRef.publish = 1U;
                            vlSelfRef.published_base 
                                = vlSelfRef.snapshot_axi_writer__DOT__record_base;
                            vlSelfRef.published_frame 
                                = vlSelfRef.snapshot_axi_writer__DOT__frame_id;
                            vlSelfRef.__Vdly__active = 0U;
                            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__phase = 0U;
                            if (((IData)(vlSelfRef.snapshot_axi_writer__DOT__write_slot) 
                                 == ((IData)(vlSelfRef.snapshot_axi_writer__DOT__slots) 
                                     - (IData)(1U)))) {
                                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__record_base 
                                    = vlSelfRef.snapshot_axi_writer__DOT__ring_base;
                                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__write_slot = 0U;
                            } else {
                                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__record_base 
                                    = ((IData)(0x00002000U) 
                                       + vlSelfRef.snapshot_axi_writer__DOT__record_base);
                                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__write_slot 
                                    = (0x0000ffffU 
                                       & ((IData)(1U) 
                                          + (IData)(vlSelfRef.snapshot_axi_writer__DOT__write_slot)));
                            }
                            if ((0xffffffffU == vlSelfRef.snapshot_axi_writer__DOT__frame_id)) {
                                vlSelfRef.snapshot_axi_writer__DOT__sequence_exhausted = 1U;
                            }
                            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__frame_id 
                                = ((IData)(1U) + vlSelfRef.snapshot_axi_writer__DOT__frame_id);
                        } else if (((vlSelfRef.snapshot_axi_writer__DOT__acked_beats 
                                     + (IData)(vlSelfRef.snapshot_axi_writer__DOT__burst_beats)) 
                                    == ((1U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))
                                         ? 4U : 0x00000081U))) {
                            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__phase 
                                = ((1U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))
                                    ? 2U : 3U);
                            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__acked_beats = 0U;
                            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__half = 0U;
                        } else {
                            vlSelfRef.__Vdly__snapshot_axi_writer__DOT__acked_beats 
                                = (vlSelfRef.snapshot_axi_writer__DOT__acked_beats 
                                   + (IData)(vlSelfRef.snapshot_axi_writer__DOT__burst_beats));
                        }
                    }
                }
            } else if (vlSelfRef.m_axi_wready) {
                if (((IData)(vlSelfRef.snapshot_axi_writer__DOT__beat) 
                     == ((IData)(vlSelfRef.snapshot_axi_writer__DOT__burst_beats) 
                         - (IData)(1U)))) {
                    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__bus = 3U;
                } else {
                    vlSelfRef.__Vdly__snapshot_axi_writer__DOT__beat 
                        = (0x0000001fU & ((IData)(1U) 
                                          + (IData)(vlSelfRef.snapshot_axi_writer__DOT__beat)));
                }
            }
        } else if ((1U & (IData)(vlSelfRef.snapshot_axi_writer__DOT__bus))) {
            if (vlSelfRef.m_axi_awready) {
                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__bus = 2U;
            }
        } else if (((IData)(vlSelfRef.active) & (0U 
                                                 == (IData)(vlSelfRef.error_flags)))) {
            if ((4U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))) {
                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__burst_beats = 0x10U;
                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__beat = 0U;
                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__bus = 1U;
            } else if (((((1U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase)) 
                          | (2U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))) 
                         & (0U != (IData)(vlSelfRef.snapshot_axi_writer__DOT__count))) 
                        & ((0x10U <= (IData)(vlSelfRef.snapshot_axi_writer__DOT__count)) 
                           | ((1U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))
                               ? (7U == vlSelfRef.snapshot_axi_writer__DOT__input_count)
                               : (0x00000101U == vlSelfRef.snapshot_axi_writer__DOT__state_count))))) {
                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__burst_beats 
                    = ((0x10U <= (IData)(vlSelfRef.snapshot_axi_writer__DOT__count))
                        ? 0x00000010U : (0x0000001fU 
                                         & (IData)(vlSelfRef.snapshot_axi_writer__DOT__count)));
                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__beat = 0U;
                vlSelfRef.__Vdly__snapshot_axi_writer__DOT__bus = 1U;
            }
        }
    }
    vlSelfRef.snapshot_axi_writer__DOT__rp = __Vdly__snapshot_axi_writer__DOT__rp;
    vlSelfRef.snapshot_axi_writer__DOT__wp = __Vdly__snapshot_axi_writer__DOT__wp;
    if (__VdlySet__snapshot_axi_writer__DOT__fifo_data__v0) {
        vlSelfRef.snapshot_axi_writer__DOT__fifo_strb[__VdlyDim0__snapshot_axi_writer__DOT__fifo_strb__v0] 
            = __VdlyVal__snapshot_axi_writer__DOT__fifo_strb__v0;
        vlSelfRef.snapshot_axi_writer__DOT__fifo_data[__VdlyDim0__snapshot_axi_writer__DOT__fifo_data__v0] 
            = __VdlyVal__snapshot_axi_writer__DOT__fifo_data__v0;
    }
}

void Vdut___024root___nba_sequent__TOP__1(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__1\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.snapshot_axi_writer__DOT__write_slot 
        = vlSelfRef.__Vdly__snapshot_axi_writer__DOT__write_slot;
    vlSelfRef.snapshot_axi_writer__DOT__got_info = vlSelfRef.__Vdly__snapshot_axi_writer__DOT__got_info;
    vlSelfRef.snapshot_axi_writer__DOT__timeout_count 
        = vlSelfRef.__Vdly__snapshot_axi_writer__DOT__timeout_count;
    vlSelfRef.snapshot_axi_writer__DOT__acked_beats 
        = vlSelfRef.__Vdly__snapshot_axi_writer__DOT__acked_beats;
    vlSelfRef.snapshot_axi_writer__DOT__half = vlSelfRef.__Vdly__snapshot_axi_writer__DOT__half;
    vlSelfRef.snapshot_axi_writer__DOT__burst_beats 
        = vlSelfRef.__Vdly__snapshot_axi_writer__DOT__burst_beats;
    vlSelfRef.snapshot_axi_writer__DOT__bus = vlSelfRef.__Vdly__snapshot_axi_writer__DOT__bus;
    vlSelfRef.snapshot_axi_writer__DOT__record_base 
        = vlSelfRef.__Vdly__snapshot_axi_writer__DOT__record_base;
    vlSelfRef.snapshot_axi_writer__DOT__frame_id = vlSelfRef.__Vdly__snapshot_axi_writer__DOT__frame_id;
    vlSelfRef.snapshot_axi_writer__DOT__input_hash 
        = vlSelfRef.__Vdly__snapshot_axi_writer__DOT__input_hash;
    vlSelfRef.snapshot_axi_writer__DOT__state_hash 
        = vlSelfRef.__Vdly__snapshot_axi_writer__DOT__state_hash;
    vlSelfRef.snapshot_axi_writer__DOT__beat = vlSelfRef.__Vdly__snapshot_axi_writer__DOT__beat;
    vlSelfRef.snapshot_axi_writer__DOT__input_count 
        = vlSelfRef.__Vdly__snapshot_axi_writer__DOT__input_count;
    vlSelfRef.snapshot_axi_writer__DOT__state_count 
        = vlSelfRef.__Vdly__snapshot_axi_writer__DOT__state_count;
    vlSelfRef.snapshot_axi_writer__DOT__count = vlSelfRef.__Vdly__snapshot_axi_writer__DOT__count;
    vlSelfRef.committed_count = vlSelfRef.__Vdly__committed_count;
    vlSelfRef.error_flags = vlSelfRef.__Vdly__error_flags;
    vlSelfRef.active = vlSelfRef.__Vdly__active;
    vlSelfRef.snapshot_axi_writer__DOT__phase = vlSelfRef.__Vdly__snapshot_axi_writer__DOT__phase;
    vlSelfRef.m_axi_awlen = (0x000000ffU & ((IData)(vlSelfRef.snapshot_axi_writer__DOT__burst_beats) 
                                            - (IData)(1U)));
    vlSelfRef.m_axi_awvalid = (1U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__bus));
    vlSelfRef.m_axi_bready = (3U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__bus));
    vlSelfRef.m_axi_wvalid = (2U == (IData)(vlSelfRef.snapshot_axi_writer__DOT__bus));
    vlSelfRef.m_axi_wlast = (((IData)(vlSelfRef.snapshot_axi_writer__DOT__burst_beats) 
                              - (IData)(1U)) == (IData)(vlSelfRef.snapshot_axi_writer__DOT__beat));
    vlSelfRef.release_ready = ((IData)(vlSelfRef.configured) 
                               & ((0U == (IData)(vlSelfRef.error_flags)) 
                                  & ((vlSelfRef.release_cookie 
                                      == vlSelfRef.snapshot_axi_writer__DOT__session_cookie) 
                                     & ((vlSelfRef.release_sequence 
                                         >= vlSelfRef.released_count) 
                                        & (vlSelfRef.release_sequence 
                                           <= vlSelfRef.committed_count)))));
    vlSelfRef.__VdfgRegularize_h52e72c00_0_1 = ((~ (IData)(vlSelfRef.active)) 
                                                & (IData)(vlSelfRef.configured));
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
    if (vlSelfRef.reset) {
        vlSelfRef.snapshot_axi_writer__DOT__ring_base = 0U;
        vlSelfRef.snapshot_axi_writer__DOT__slots = 0U;
    } else if (((IData)(vlSelfRef.cfg_valid) & (IData)(vlSelfRef.cfg_ready))) {
        if ((1U & (~ (((((0U != (0x00000fffU & vlSelfRef.cfg_base)) 
                         | (vlSelfRef.cfg_end <= vlSelfRef.cfg_base)) 
                        | (0U == (IData)(vlSelfRef.cfg_slots))) 
                       | (((QData)((IData)(vlSelfRef.cfg_base)) 
                           + VL_SHIFTL_QQI(64,64,32, (QData)((IData)(vlSelfRef.cfg_slots)), 0x0000000dU)) 
                          > (QData)((IData)(vlSelfRef.cfg_end)))) 
                      | (0x0000000100000000ULL < (0x00000001ffffffffULL 
                                                  & ((QData)((IData)(vlSelfRef.cfg_first_frame)) 
                                                     + (QData)((IData)(vlSelfRef.cfg_slots))))))))) {
            vlSelfRef.snapshot_axi_writer__DOT__ring_base 
                = vlSelfRef.cfg_base;
            vlSelfRef.snapshot_axi_writer__DOT__slots 
                = vlSelfRef.cfg_slots;
        }
    }
    vlSelfRef.snapshot_axi_writer__DOT__pop = ((IData)(vlSelfRef.m_axi_wvalid) 
                                               & ((IData)(vlSelfRef.m_axi_wready) 
                                                  & (4U 
                                                     != (IData)(vlSelfRef.snapshot_axi_writer__DOT__phase))));
    vlSelfRef.snapshot_axi_writer__DOT__accept_word 
        = (((IData)(vlSelfRef.input_valid) & (IData)(vlSelfRef.input_ready)) 
           | ((IData)(vlSelfRef.state_valid) & (IData)(vlSelfRef.state_ready)));
    vlSelfRef.cfg_ready = ((~ (IData)(vlSelfRef.active)) 
                           & ((~ (IData)(vlSelfRef.configured)) 
                              & (0U == (IData)(vlSelfRef.error_flags))));
    vlSelfRef.snapshot_axi_writer__DOT__push = ((IData)(vlSelfRef.snapshot_axi_writer__DOT__accept_word) 
                                                & ((IData)(vlSelfRef.snapshot_axi_writer__DOT__half) 
                                                   | (IData)(vlSelfRef.snapshot_axi_writer__DOT__last_word)));
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
}

void Vdut___024root___nba_sequent__TOP__2(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__2\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.begin_ready = ((IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_1) 
                             & ((~ (IData)(vlSelfRef.capacity_exhausted)) 
                                & (0U == (IData)(vlSelfRef.error_flags))));
}

void Vdut___024root___eval_nba(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_nba\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VnbaTriggered[0U])) {
        Vdut___024root___nba_sequent__TOP__0(vlSelf);
        Vdut___024root___nba_sequent__TOP__1(vlSelf);
        vlSelfRef.begin_ready = ((IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_1) 
                                 & ((~ (IData)(vlSelfRef.capacity_exhausted)) 
                                    & (0U == (IData)(vlSelfRef.error_flags))));
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
            VL_FATAL_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\snapshot_axi_writer.sv", 5, "", "DIDNOTCONVERGE: Input combinational region did not converge after '--converge-limit' of 10000 tries");
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
            VL_FATAL_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\snapshot_axi_writer.sv", 5, "", "DIDNOTCONVERGE: NBA region did not converge after '--converge-limit' of 10000 tries");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        vlSelfRef.__VactIterCount = 0U;
        do {
            if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                Vdut___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
#endif
                VL_FATAL_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\snapshot_axi_writer.sv", 5, "", "DIDNOTCONVERGE: Active region did not converge after '--converge-limit' of 10000 tries");
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
    if (VL_UNLIKELY(((vlSelfRef.clk & 0xfeU)))) {
        Verilated::overWidthError("clk");
    }
    if (VL_UNLIKELY(((vlSelfRef.reset & 0xfeU)))) {
        Verilated::overWidthError("reset");
    }
    if (VL_UNLIKELY(((vlSelfRef.cfg_valid & 0xfeU)))) {
        Verilated::overWidthError("cfg_valid");
    }
    if (VL_UNLIKELY(((vlSelfRef.release_valid & 0xfeU)))) {
        Verilated::overWidthError("release_valid");
    }
    if (VL_UNLIKELY(((vlSelfRef.begin_valid & 0xfeU)))) {
        Verilated::overWidthError("begin_valid");
    }
    if (VL_UNLIKELY(((vlSelfRef.input_valid & 0xfeU)))) {
        Verilated::overWidthError("input_valid");
    }
    if (VL_UNLIKELY(((vlSelfRef.state_valid & 0xfeU)))) {
        Verilated::overWidthError("state_valid");
    }
    if (VL_UNLIKELY(((vlSelfRef.state_last & 0xfeU)))) {
        Verilated::overWidthError("state_last");
    }
    if (VL_UNLIKELY(((vlSelfRef.info_valid & 0xfeU)))) {
        Verilated::overWidthError("info_valid");
    }
    if (VL_UNLIKELY(((vlSelfRef.m_axi_awready & 0xfeU)))) {
        Verilated::overWidthError("m_axi_awready");
    }
    if (VL_UNLIKELY(((vlSelfRef.m_axi_wready & 0xfeU)))) {
        Verilated::overWidthError("m_axi_wready");
    }
    if (VL_UNLIKELY(((vlSelfRef.m_axi_bresp & 0xfcU)))) {
        Verilated::overWidthError("m_axi_bresp");
    }
    if (VL_UNLIKELY(((vlSelfRef.m_axi_bvalid & 0xfeU)))) {
        Verilated::overWidthError("m_axi_bvalid");
    }
}
#endif  // VL_DEBUG

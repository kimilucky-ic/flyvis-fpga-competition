// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See vdut.h for the primary calling header

#include "vdut__pch.h"

void Vdut___024root___nba_sequent__TOP__19(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__19\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__write_slot 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__write_slot;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__got_info 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__got_info;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__timeout_count 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__timeout_count;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__cycles 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__cycles;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__acked_beats 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__acked_beats;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__half 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__half;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__frame_id 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__frame_id;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_hash 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_hash;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_hash 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_hash;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_count 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_count;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__record_base 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__record_base;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__active 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__active;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors;
    vlSelfRef.m_axi_awlen = (0x000000ffU & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__burst_beats) 
                                            - (IData)(1U)));
    vlSelfRef.m_axi_awvalid = (1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus));
    vlSelfRef.m_axi_bready = (3U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus));
    vlSelfRef.m_axi_wvalid = (2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus));
    vlSelfRef.m_axi_wlast = (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__burst_beats) 
                              - (IData)(1U)) == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__beat));
    vlSelfRef.m_axi_wstrb = (0x000000ffU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__fifo_strb
                                            [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__rp] 
                                            | (- (IData)(
                                                         (4U 
                                                          == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__last_word 
        = ((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))
            ? (0x000002d0U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_count)
            : (0x0000b264U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count));
    vlSelfRef.m_axi_awaddr = (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__record_base 
                              + (((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))
                                   ? 0x00000080U : 
                                  (0x00001000U & (- (IData)(
                                                            (4U 
                                                             != (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase)))))) 
                                 + VL_SHIFTL_III(32,32,32, vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__acked_beats, 3U)));
    if ((4U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))) {
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__beat;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT____VlemCall_0__header_word 
            = (((((((((0U == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index)) 
                      | (1U == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index))) 
                     | (2U == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index))) 
                    | (3U == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index))) 
                   | (4U == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index))) 
                  | (5U == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index))) 
                 | (6U == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index))) 
                | (7U == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index)))
                ? ((0U == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index))
                    ? 0x000100005331314cULL : ((1U 
                                                == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index))
                                                ? (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__frame_id))
                                                : (
                                                   (2U 
                                                    == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index))
                                                    ? 0x0017170f0000b265ULL
                                                    : 
                                                   ((3U 
                                                     == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index))
                                                     ? 0x0002c99400000b44ULL
                                                     : 
                                                    ((4U 
                                                      == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index))
                                                      ? 
                                                     (((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__saved_edges)) 
                                                       << 0x00000020U) 
                                                      | (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__saved_cycles)))
                                                      : 
                                                     ((5U 
                                                       == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index))
                                                       ? 
                                                      (0x0002e00000000000ULL 
                                                       | (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__saved_states)))
                                                       : 
                                                      ((6U 
                                                        == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index))
                                                        ? 
                                                       (((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_hash)) 
                                                         << 0x00000020U) 
                                                        | (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_hash)))
                                                        : 0x0000100000000080ULL)))))))
                : ((8U == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index))
                    ? 0x3ba3d70a00110005ULL : ((9U 
                                                == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index))
                                                ? (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__saved_faults))
                                                : (
                                                   (0x0aU 
                                                    == (IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index))
                                                    ? 
                                                   (((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__session_cookie)) 
                                                     << 0x00000020U) 
                                                    | (QData)((IData)(
                                                                      ((IData)(1U) 
                                                                       + vlSelfRef.flyvis_ddr_soc_ip__DOT__committed))))
                                                    : 0ULL))));
    } else {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT____VlemCall_0__header_word 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__fifo_data
            [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__rp];
    }
    vlSelfRef.m_axi_wdata = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT____VlemCall_0__header_word;
    vlSelfRef.__VdfgRegularize_h52e72c00_0_3 = ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__active)) 
                                                & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__configured));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__release_ready 
        = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__configured) 
           & ((0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors)) 
              & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__release_cookie 
                  == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__session_cookie) 
                 & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__release_sequence 
                     >= vlSelfRef.flyvis_ddr_soc_ip__DOT__released) 
                    & (vlSelfRef.flyvis_ddr_soc_ip__DOT__release_sequence 
                       <= vlSelfRef.flyvis_ddr_soc_ip__DOT__committed)))));
    if (vlSelfRef.aresetn) {
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT____Vcellinp__journal__cfg_valid) 
             & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_cfg_ready))) {
            if ((1U & (~ (((((0U != (0x00000fffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_base)) 
                             | (vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_end 
                                <= vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_base)) 
                            | (0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_slots))) 
                           | (((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_base)) 
                               + (0x000000000002e000ULL 
                                  * (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_slots)))) 
                              > (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_end)))) 
                          | (0x0000000100000000ULL 
                             < (0x00000001ffffffffULL 
                                & ((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_first)) 
                                   + (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_slots))))))))) {
                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__ring_base 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_base;
                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__slots 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_slots;
            }
        }
        if ((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__feed))) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__frame_q 
                = ((0x02d0U >= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__feed_index))
                    ? vlSelfRef.flyvis_ddr_soc_ip__DOT__frame
                   [vlSelfRef.flyvis_ddr_soc_ip__DOT__feed_index]
                    : 0U);
        }
        if (vlSelfRef.flyvis_ddr_soc_ip__DOT__start_cmd) {
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__feed_index = 0U;
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__feed = 1U;
        }
        if ((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__feed))) {
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__feed = 2U;
        } else if ((2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__feed))) {
            if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__inflight) 
                 & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__lane_input_ready) 
                    & (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_5)))) {
                if ((0x02d0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__feed_index))) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__feed = 0U;
                } else {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__feed_index 
                        = (0x000003ffU & ((IData)(1U) 
                                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__feed_index)));
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__feed = 1U;
                }
            }
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__start_cmd) 
             & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__begin_ready))) {
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__edges = 0U;
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__states = 0U;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__core_faults = 0U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edge_valid) 
             & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edge_ready))) {
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__edges 
                = ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edges);
            if ((((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_eid 
                   != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edges) 
                  | (0xb265U <= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_src))) 
                 | (0xb265U <= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__core_faults 
                    = (1U | vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__core_faults);
            }
        }
        if (((0x0dU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)) 
             & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_state_ready))) {
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__states 
                = ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__states);
            if (((0x0000ffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index) 
                 != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__states)) {
                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__core_faults 
                    = (2U | vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__core_faults);
            }
        }
        if (((0x0eU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)) 
             & ((0x0017170fU != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edges) 
                | (0x0000b265U != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__states)))) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__core_faults 
                = (4U | vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__core_faults);
        }
    } else {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__ring_base = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__slots = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__feed_index = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__feed = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__edges = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__states = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__core_faults = 0U;
    }
}

void Vdut___024root___nba_sequent__TOP__20(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__20\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.aresetn) {
        if (VL_UNLIKELY(((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar) 
                           & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw)) 
                          & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_addr) 
                             == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: flyvis_lane.sv:140: Assertion failed in %m: A same-address collision\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_lane.sv", 140, "", false);
        }
        if (VL_UNLIKELY(((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr) 
                           & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw)) 
                          & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr_addr) 
                             == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: flyvis_lane.sv:141: Assertion failed in %m: C same-address collision\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_lane.sv", 141, "", false);
        }
        if (VL_UNLIKELY(((((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar) 
                             & VL_LTES_III(32, 0x0000b265U, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_addr))) 
                            | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr) 
                               & VL_LTES_III(32, 0x0000b265U, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr_addr)))) 
                           | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
                              & VL_LTES_III(32, 0x0000b265U, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr)))) 
                          | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
                             & VL_LTES_III(32, 0x0000b265U, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: flyvis_lane.sv:142: Assertion failed in %m: RAM bounds\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_lane.sv", 142, "", false);
        }
        if (VL_UNLIKELY((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
                          & ((3U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)) 
                             | (4U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: flyvis_lane.sv:143: Assertion failed in %m: early update\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_lane.sv", 143, "", false);
        }
        if (VL_UNLIKELY((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pipe_valid) 
                          & (~ ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__v) 
                                >> 0x0000000cU)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: flyvis_lane.sv:144: Assertion failed in %m: adder/tag mismatch\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_lane.sv", 144, "", false);
        }
        if (VL_UNLIKELY(((1U & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                                 >> 9U) & (~ ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__v) 
                                              >> 7U))))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: flyvis_lane.sv:145: Assertion failed in %m: multiplier/tag mismatch\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_lane.sv", 145, "", false);
        }
        if (VL_UNLIKELY(((1U & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                                 >> 1U) & ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__av)) 
                                           | (~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cv)))))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: flyvis_lane.sv:146: Assertion failed in %m: missing synchronous response\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_lane.sv", 146, "", false);
        }
        if (VL_UNLIKELY((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_return) 
                          & (~ (((3U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id) 
                                 | (4U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id))
                                 ? ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__v) 
                                    >> 7U) : ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__v) 
                                              >> 0x0000000cU))))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: flyvis_lane.sv:147: Assertion failed in %m: missing Euler result\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_lane.sv", 147, "", false);
        }
        if (VL_UNLIKELY((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_return) 
                          & (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__return_slot) 
                              != (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__received)) 
                             | VL_GTES_III(32, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__return_slot), (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__batch_count))))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: flyvis_lane.sv:148: Assertion failed in %m: Euler return order\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_lane.sv", 148, "", false);
        }
        if (VL_UNLIKELY((((9U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)) 
                          & (VL_GTES_III(32, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot), (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__batch_count)) 
                             | (0U != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: flyvis_lane.sv:149: Assertion failed in %m: Euler issue bounds/barrier\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_lane.sv", 149, "", false);
        }
        if (VL_UNLIKELY((((5U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)) 
                          & (0U != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: flyvis_lane.sv:150: Assertion failed in %m: undrained pipeline\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_lane.sv", 150, "", false);
        }
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0 
            = (1U & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid) 
                     >> 0x0bU));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[21U];
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid 
            = ((0x0fffU & (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid)) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0) 
                  << 0x0000000cU));
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v0 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[11U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[20U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v1 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v1 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[19U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v0 = 1U;
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v2 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0 
            = (1U & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid) 
                     >> 0x0aU));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[18U];
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid 
            = ((0x17ffU & (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid)) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0) 
                  << 0x0000000bU));
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v3 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v3 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[10U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[17U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v1 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v1 = 1U;
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v4 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0 
            = (1U & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid) 
                     >> 9U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[16U];
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid 
            = ((0x1bffU & (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid)) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0) 
                  << 0x0000000aU));
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v5 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v5 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[9U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[15U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v2 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v2 = 1U;
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v6 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0 
            = (1U & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid) 
                     >> 8U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[14U];
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid 
            = ((0x1dffU & (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid)) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0) 
                  << 9U));
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v7 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v7 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[8U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[13U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v3 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v3 = 1U;
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v8 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0 
            = (1U & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid) 
                     >> 7U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[12U];
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid 
            = ((0x1effU & (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid)) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0) 
                  << 8U));
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v9 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v9 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[7U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[11U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v4 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v4 = 1U;
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v10 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0 
            = (1U & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid) 
                     >> 6U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[10U];
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid 
            = ((0x1f7fU & (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid)) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0) 
                  << 7U));
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v11 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v11 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[6U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[9U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v5 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v5 = 1U;
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v12 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0 
            = (1U & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid) 
                     >> 5U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[8U];
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid 
            = ((0x1fbfU & (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid)) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0) 
                  << 6U));
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v13 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v13 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[5U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[7U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v6 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v6 = 1U;
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v14 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0 
            = (1U & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid) 
                     >> 4U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[6U];
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid 
            = ((0x1fdfU & (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid)) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0) 
                  << 5U));
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v15 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v15 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[4U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[5U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v7 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v7 = 1U;
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v16 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0 
            = (1U & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid) 
                     >> 3U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[4U];
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid 
            = ((0x1fefU & (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid)) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0) 
                  << 4U));
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v17 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v17 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[3U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[3U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v8 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v8 = 1U;
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v18 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0 
            = (1U & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid) 
                     >> 2U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[2U];
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid 
            = ((0x1ff7U & (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid)) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0) 
                  << 3U));
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v19 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v19 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[2U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[1U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v9 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v9 = 1U;
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v20 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0 
            = (1U & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid) 
                     >> 1U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__1 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr_data;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid 
            = ((0x1ffbU & (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid)) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0) 
                  << 2U));
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v21 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__1;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v21 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[1U];
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[0U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v10 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v10 = 1U;
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v22 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0 
            = (1U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid 
            = ((0x1ffdU & (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid)) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0) 
                  << 1U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[0U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v11 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v11 = 1U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid 
            = ((0x1ffeU & (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid)) 
               | (9U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)));
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v12 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v12 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 0x15U));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x003fffffU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 0x00000016U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[21U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v0 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[21U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v0 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[21U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v0 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[21U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v0 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 0x14U));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x005fffffU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 0x00000015U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[20U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v1 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v1 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[20U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v1 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v1 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[20U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v1 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v1 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[20U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v1 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v1 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 0x13U));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x006fffffU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 0x00000014U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[19U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v2 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v2 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[19U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v2 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v2 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[19U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v2 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v2 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[19U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v2 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v2 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 0x12U));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x0077ffffU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 0x00000013U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[18U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v3 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v3 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[18U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v3 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v3 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[18U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v3 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v3 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[18U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v3 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v3 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 0x11U));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007bffffU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 0x00000012U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[17U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v4 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v4 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[17U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v4 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v4 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[17U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v4 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v4 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[17U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v4 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v4 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 0x10U));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007dffffU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 0x00000011U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[16U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v5 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v5 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[16U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v5 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v5 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[16U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v5 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v5 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[16U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v5 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v5 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 0x0fU));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007effffU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 0x00000010U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[15U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v6 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v6 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[15U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v6 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v6 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[15U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v6 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v6 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[15U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v6 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v6 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 0x0eU));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007f7fffU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 0x0000000fU));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[14U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v7 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v7 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[14U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v7 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v7 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[14U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v7 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v7 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[14U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v7 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v7 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 0x0dU));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007fbfffU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 0x0000000eU));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[13U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v8 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v8 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[13U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v8 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v8 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[13U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v8 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v8 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[13U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v8 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v8 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 0x0cU));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007fdfffU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 0x0000000dU));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[12U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v9 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v9 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[12U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v9 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v9 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[12U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v9 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v9 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[12U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v9 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v9 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 0x0bU));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007fefffU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 0x0000000cU));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[11U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v10 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v10 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[11U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v10 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v10 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[11U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v10 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v10 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[11U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v10 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v10 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 0x0aU));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007ff7ffU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 0x0000000bU));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[10U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v11 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v11 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[10U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v11 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v11 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[10U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v11 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v11 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[10U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v11 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v11 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 9U));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007ffbffU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 0x0000000aU));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[9U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v12 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v12 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[9U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v12 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v12 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[9U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v12 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v12 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[9U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v12 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v12 = 1U;
        if ((0x00000200U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv)) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__1 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_out;
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v13 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__1;
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v13 = 1U;
        }
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 8U));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007ffdffU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 9U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[8U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v13 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v13 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[8U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v13 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v13 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[8U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v13 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v13 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[8U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v14 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v14 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 7U));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007ffeffU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 8U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[7U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v14 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v14 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[7U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v14 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v14 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[7U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v14 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v14 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[7U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v15 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v15 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 6U));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007fff7fU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 7U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[6U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v15 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v15 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[6U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v15 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v15 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[6U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v15 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v15 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[6U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v16 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v16 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 5U));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007fffbfU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 6U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[5U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v16 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v16 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[5U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v16 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v16 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[5U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v16 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v16 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[5U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v17 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v17 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 4U));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007fffdfU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 5U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[4U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v17 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v17 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[4U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v17 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v17 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[4U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v17 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v17 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[4U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v18 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v18 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 3U));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007fffefU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 4U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[3U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v18 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v18 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[3U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v18 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v18 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[3U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v18 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v18 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[3U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v19 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v19 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 2U));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007ffff7U & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 3U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[2U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v19 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v19 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[2U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v19 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v19 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[2U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v19 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v19 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[2U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v20 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v20 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                     >> 1U));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007ffffbU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 2U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[1U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v20 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v20 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[1U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v20 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v20 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[1U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v20 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v20 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[1U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v21 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v21 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 
            = (1U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv);
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007ffffdU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0) 
                  << 1U));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[0U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v21 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v21 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[0U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v21 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v21 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[0U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v21 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v21 = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[0U];
        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v22 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v22 = 1U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
            = ((0x007ffffeU & vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv) 
               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edge_valid) 
                  & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edge_ready)));
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edge_valid) 
             & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edge_ready))) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__request_src 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_src;
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v22 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_weight;
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v22 = 1U;
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v22 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst;
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v22 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_eid;
        }
        if ((0x00000010U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
            if (VL_UNLIKELY(((8U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: flyvis_lane.sv:223: Assertion failed in %m: controller phase\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network", 'T',-12
                             , '#',64,VL_TIME_UNITED_Q(1));
                VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_lane.sv", 223, "", false);
            } else if ((4U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
                if (VL_UNLIKELY(((2U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: flyvis_lane.sv:223: Assertion failed in %m: controller phase\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network", 'T',-12
                                 , '#',64,VL_TIME_UNITED_Q(1));
                    VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_lane.sv", 223, "", false);
                } else if (VL_UNLIKELY(((1U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: flyvis_lane.sv:223: Assertion failed in %m: controller phase\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network", 'T',-12
                                 , '#',64,VL_TIME_UNITED_Q(1));
                    VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_lane.sv", 223, "", false);
                } else {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0U;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__input_index = 0U;
                }
            } else if ((2U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
                if ((1U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
                    if (VL_LTS_III(32, ((IData)(1U) 
                                        + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index), vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_count)) {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index 
                            = ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index);
                    } else if (VL_GTS_III(32, 0x00000041U, 
                                          ((IData)(1U) 
                                           + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id))) {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id 
                            = ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id);
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0x0fU;
                    } else {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0x14U;
                    }
                } else {
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__bias 
                        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_q;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index = 0U;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0x13U;
                }
            } else if ((1U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0x12U;
            } else {
                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_base 
                    = (0x0000ffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_q);
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_count 
                    = (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_q 
                       >> 0x10U);
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0x11U;
            }
        } else if ((8U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
            if ((4U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
                if ((2U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
                    if ((1U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0x10U;
                    } else {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0U;
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__input_index = 0U;
                    }
                } else if ((1U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
                    if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_state_ready) {
                        if ((0x0000b264U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index)) {
                            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0x0eU;
                        } else {
                            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index 
                                = ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index);
                            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0x0bU;
                        }
                    }
                } else {
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__old_a 
                        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_data;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0x0dU;
                }
            } else if ((2U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
                if ((1U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0x0cU;
                }
            } else if ((1U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
                if ((((IData)(1U) + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot)) 
                     < (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__batch_count))) {
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot 
                        = (0x0000001fU & ((IData)(1U) 
                                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot)));
                } else {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0x0aU;
                }
            } else {
                vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_old__v0 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_data;
                vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_old__v0 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__load_slot;
                vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_old__v0 = 1U;
                vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_current__v0 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr_data;
                vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_current__v0 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__load_slot;
                vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_input__v0 
                    = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_input)
                        ? vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__stim_q
                        : 0U);
                vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_input__v0 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__load_slot;
                if ((VL_GTS_III(32, 0x00000020U, ((IData)(1U) 
                                                  + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__load_slot))) 
                     & VL_LTS_III(32, ((IData)(1U) 
                                       + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index), vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_count))) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index 
                        = ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index);
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__load_slot 
                        = (0x0000001fU & ((IData)(1U) 
                                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__load_slot)));
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 7U;
                } else {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__batch_count 
                        = (0x0000003fU & ((IData)(1U) 
                                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__load_slot)));
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot = 0U;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__received = 0U;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id = 0U;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 9U;
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__batch_first 
                        = (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index 
                           - (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__load_slot));
                }
            }
        } else if ((4U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
            if ((2U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
                if ((1U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 8U;
                } else {
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h5e55ba7f__0 
                        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_q;
                    if ((6U >= (7U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__word_id))) {
                        vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__desc__v0 
                            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h5e55ba7f__0;
                        vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__desc__v0 
                            = (7U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__word_id);
                        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__desc__v0 = 1U;
                    }
                    if ((6U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__word_id)) {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__load_slot = 0U;
                        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_base 
                            = (0x0000ffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__desc[0U]);
                        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__inv 
                            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_q;
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index = 0U;
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 7U;
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_count 
                            = (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__desc[0U] 
                               >> 0x10U);
                        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_input 
                            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__desc[1U] 
                                     >> 0x18U));
                        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__bias 
                            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__desc[4U];
                    } else {
                        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__word_id 
                            = ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__word_id);
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 5U;
                    }
                }
            } else if ((1U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 6U;
            } else if ((0U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv)) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id = 0U;
                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__word_id = 0U;
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 5U;
            }
        } else if ((2U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
            if ((1U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
                if (((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edge_valid)) 
                     & (0x0dU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state)))) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 4U;
                }
            } else {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 3U;
            }
        } else if ((1U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
            if ((0x0000b264U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index)) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 2U;
            } else {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index 
                    = ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index);
            }
        } else if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__restore_fire) {
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id = 0U;
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0x0fU;
        } else if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT____Vcellinp__network__input_valid) 
                    & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__lane_input_ready))) {
            if ((0x000002d0U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__input_index)) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index = 0U;
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 1U;
            } else {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__input_index 
                    = ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__input_index);
            }
        }
        if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_return) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_result;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__return_slot;
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result__v0 = 1U;
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__received 
                = (0x0000003fU & ((IData)(1U) + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__received)));
            if ((((IData)(1U) + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__received)) 
                 == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__batch_count))) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid = 0U;
                if (VL_GTS_III(32, 5U, vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id 
                        = ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id);
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot = 0U;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__received = 0U;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 9U;
                } else if (VL_LTS_III(32, ((IData)(1U) 
                                           + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index), vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_count)) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index 
                        = ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index);
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__load_slot = 0U;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 7U;
                } else if (VL_GTS_III(32, 0x00000041U, 
                                      ((IData)(1U) 
                                       + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id))) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id 
                        = ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id);
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__word_id = 0U;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 5U;
                } else {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index = 0U;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0x0bU;
                }
            }
        }
    } else {
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__input_index = 0U;
    }
}

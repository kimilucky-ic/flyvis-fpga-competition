// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See vdut.h for the primary calling header

#include "vdut__pch.h"

void Vdut___024root___nba_sequent__TOP__26(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__26\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 7U) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[7U] 
                    == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 8U) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[8U] 
                    == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 9U) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[9U] 
                    == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 0x0aU) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[10U] 
                       == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 0x0bU) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[11U] 
                       == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 0x0cU) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[12U] 
                       == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 0x0dU) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[13U] 
                       == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 0x0eU) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[14U] 
                       == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 0x0fU) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[15U] 
                       == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 0x10U) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[16U] 
                       == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 0x11U) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[17U] 
                       == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 0x12U) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[18U] 
                       == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 0x13U) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[19U] 
                       == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 0x14U) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[20U] 
                       == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 0x15U) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[21U] 
                       == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 0x16U) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[22U] 
                       == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edge_ready 
        = ((3U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)) 
           & (~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard)));
    if (vlSelfRef.aresetn) {
        if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_read) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_q 
                = ((0x1deeU >= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_address))
                    ? vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__metadata__DOT__ordinary__DOT__mem
                   [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_address]
                    : 0U);
        }
        if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__advance) {
            if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__map_read) {
                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__map_q 
                    = ((0x0781U >= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__map_address))
                        ? vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__maps__DOT__ordinary__DOT__mem
                       [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__map_address]
                        : 0U);
            }
            if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_read) {
                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_q 
                    = ((0x3dU >= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rows_addr))
                        ? vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rows__DOT__ordinary__DOT__mem
                       [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rows_addr]
                        : 0U);
            }
        }
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__control_busy 
        = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__running) 
           | (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_7));
    vlSelfRef.__VdfgRegularize_h52e72c00_0_9 = ((~ (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_7)) 
                                                & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__clean));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__restore_ready 
        = ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__configured)) 
           & ((~ (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_7)) 
              & (0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__ai 
        = (IData)(((0x7f800000U == (0x7f800000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_a)) 
                   & (~ (0U != (0x007fffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_a)))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__an 
        = (IData)(((0x7f800000U == (0x7f800000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_a)) 
                   & (0U != (0x007fffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_a))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__bn 
        = (IData)(((0x7f800000U == (0x7f800000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_b)) 
                   & (0U != (0x007fffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_b))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__bi 
        = (IData)(((0x7f800000U == (0x7f800000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_b)) 
                   & (~ (0U != (0x007fffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_b)))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_address 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen_rom_addr;
    if ((5U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_address 
            = (0x00001fffU & (VL_GTS_III(32, 4U, vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__word_id)
                               ? ((IData)(0x0020U) 
                                  + (VL_MULS_III(32, (IData)(4U), vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id) 
                                     + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__word_id))
                               : ((IData)(0x1d28U) 
                                  + (VL_MULS_III(32, (IData)(3U), vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id) 
                                     + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__word_id))));
    }
    if ((0x0fU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_address 
            = (0x00001fffU & ((IData)(0x0020U) + VL_MULS_III(32, (IData)(4U), vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id)));
    }
    if ((0x11U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_address 
            = (0x00001fffU & ((IData)(0x1d2cU) + VL_MULS_III(32, (IData)(3U), vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id)));
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__prefetch_u 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u;
    if ((0x0aU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__prefetch_u 
            = (0x0000003fU & ((IData)(1U) + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u)));
    }
    if ((0x0cU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__prefetch_u 
            = (0x0000003fU & ((IData)(2U) + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u)));
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rows_addr 
        = (0x0000003fU & (((IData)(0x0000001fU) * (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sl)) 
                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__prefetch_u)));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_read_u 
        = (0x000000ffU & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__prefetch_u) 
                          + ((0x000000f0U & ((- (IData)(
                                                        (1U 
                                                         & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__du) 
                                                            >> 3U)))) 
                                             << 4U)) 
                             | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__du))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_rows_addr 
        = (0x0000003fU & (((IData)(0x0000001fU) * (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tl)) 
                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_read_u)));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen_rom_en = 0U;
    if ((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen_rom_en = 1U;
    } else if ((3U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen_rom_en = 1U;
    } else if ((5U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen_rom_en = 1U;
    } else if ((7U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen_rom_en = 1U;
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__advance 
        = (1U & ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edge_valid)) 
                 | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edge_ready)));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__last_candidate 
        = ((0x0000003fU & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j) 
                           + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j_step))) 
           >= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_count));
}

void Vdut___024root___nba_sequent__TOP__27(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__27\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*4:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__query_j;
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__query_j = 0;
    CData/*6:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__ut;
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__ut = 0;
    CData/*7:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__vt;
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__vt = 0;
    CData/*4:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__descriptor_u;
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__descriptor_u = 0;
    CData/*5:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__upper_j;
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__upper_j = 0;
    CData/*7:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__lower_delta;
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__lower_delta = 0;
    CData/*7:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_last_v;
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_last_v = 0;
    // Body
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_read 
        = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__advance) 
           & (((9U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state)) 
               | ((0x0aU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state)) 
                  & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u) 
                     < (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u_last)))) 
              | ((((0x0cU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state)) 
                   & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__last_candidate)) 
                  & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_ready)) 
                 & (((IData)(1U) + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u)) 
                    < (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u_last)))));
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__descriptor_u 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_tag;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__descriptor_query 
        = ((0x0aU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state)) 
           | ((((0x0cU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state)) 
                & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__last_candidate)) 
               & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u) 
                  < (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u_last))) 
              & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_ready)));
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__query_j 
        = (0x0000001fU & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j) 
                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j_step)));
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__ut 
        = (0x0000007fU & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u) 
                          + ((0x00000070U & ((- (IData)(
                                                        (1U 
                                                         & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__du) 
                                                            >> 3U)))) 
                                             << 4U)) 
                             | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__du))));
    if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__descriptor_query) {
        flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__query_j 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_first;
        flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__ut 
            = (0x0000007fU & ((IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__descriptor_u) 
                              + ((0x00000070U & ((- (IData)(
                                                            (1U 
                                                             & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__du) 
                                                                >> 3U)))) 
                                                 << 4U)) 
                                 | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__du))));
    }
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__vt 
        = (0x000000ffU & (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__vfirst) 
                           + ((IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__query_j) 
                              * (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sv))) 
                          + ((0x000000f0U & ((- (IData)(
                                                        (1U 
                                                         & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__dv) 
                                                            >> 3U)))) 
                                             << 4U)) 
                             | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__dv))));
    if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__descriptor_query) {
        flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__vt 
            = (0x000000ffU & (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_vfirst) 
                               + ((IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__query_j) 
                                  * (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sv))) 
                              + ((0x000000f0U & ((- (IData)(
                                                            (1U 
                                                             & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__dv) 
                                                                >> 3U)))) 
                                                 << 4U)) 
                                 | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__dv))));
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__in_bounds 
        = ((((VL_LTES_III(32, 0U, VL_EXTENDS_II(32,7, (IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__ut))) 
              & VL_GTS_III(32, 0x0000001fU, VL_EXTENDS_II(32,7, (IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__ut)))) 
             & VL_LTES_III(32, 0U, VL_EXTENDS_II(32,8, (IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__vt)))) 
            & VL_GTS_III(32, 0x0000001fU, VL_EXTENDS_II(32,8, (IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__vt)))) 
           & ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__descriptor_query)) 
              | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_nonempty)));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen_rom_en 
        = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen_rom_en) 
           & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__advance));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__map_read 
        = ((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__descriptor_query) 
             | ((0x0cU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state)) 
                & (~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__last_candidate)))) 
            & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__in_bounds)) 
           & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__advance));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__map_address 
        = (0x000007ffU & ((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tl)
                             ? 0x03c1U : 0U) + VL_MULS_III(32, (IData)(0x0000001fU), 
                                                           VL_EXTENDS_II(32,7, (IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__ut)))) 
                          + VL_EXTENDS_II(11,8, (IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__vt))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__begin_ready = 
        ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_begin_ready) 
         & (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_9));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__base_v 
        = (0x000000ffU & ((0x0000000fU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_q) 
                          + ((0x000000f0U & ((- (IData)(
                                                        (1U 
                                                         & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__dv) 
                                                            >> 3U)))) 
                                             << 4U)) 
                             | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__dv))));
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_last_v 
        = (0x0000000fU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_row_q);
    if ((0U != (0x0000001fU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_row_q 
                               >> 8U)))) {
        flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_last_v 
            = (0x000000ffU & ((IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_last_v) 
                              + ((0x000000ffU & ((0x0000001fU 
                                                  & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_row_q 
                                                     >> 8U)) 
                                                 - (IData)(1U))) 
                                 * (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tv))));
    }
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__lower_delta 
        = (0x000000ffU & ((0x0000000fU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_row_q) 
                          - (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__base_v)));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__upper_delta 
        = (0x000000ffU & ((IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_last_v) 
                          - (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__base_v)));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__lower_j = 0U;
    if (VL_LTS_III(32, 0U, VL_EXTENDS_II(32,8, (IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__lower_delta)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__lower_j 
            = (0x0000003fU & ((2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sv))
                               ? (0x0000003fU & (((IData)(1U) 
                                                  + (IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__lower_delta)) 
                                                 >> 1U))
                               : (IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__lower_delta)));
    }
    if ((((2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tv)) 
          & (1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sv))) 
         & (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__base_v) 
             ^ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__lower_j)) 
            ^ vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_row_q))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__lower_j 
            = (0x0000003fU & ((IData)(1U) + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__lower_j)));
    }
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__upper_j = 0U;
    if (VL_LTES_III(32, 0U, VL_EXTENDS_II(32,8, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__upper_delta)))) {
        flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__upper_j 
            = (0x0000003fU & ((2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sv))
                               ? ((IData)(1U) + ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__upper_delta) 
                                                 >> 1U))
                               : ((IData)(1U) + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__upper_delta))));
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__first_j 
        = (0x0000001fU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__lower_j));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__end_j 
        = (0x0000001fU & (((IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__upper_j) 
                           < (0x0000001fU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_q 
                                             >> 8U)))
                           ? (IData)(flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__upper_j)
                           : (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_q 
                              >> 8U)));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__descriptor_valid 
        = (((0U != (0x0000001fU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_row_q 
                                   >> 8U))) & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__first_j) 
                                               < (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__end_j))) 
           & (~ (((2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tv)) 
                  & (2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sv))) 
                 & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__base_v) 
                    ^ vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_row_q))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_read 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen_rom_en;
    if ((5U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_read = 1U;
    }
    if ((0x0fU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_read = 1U;
    }
    if ((0x11U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_read = 1U;
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__wr_ok = 0U;
    if (((0x0fU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__wstrb)) 
         & (0U == (3U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr))))) {
        if (((0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr)) 
             & (8U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata))) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__wr_ok 
                = (0U != vlSelfRef.flyvis_ddr_soc_ip__DOT__live_seq);
        } else if (((0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr)) 
                    & (0x00000010U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata))) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__wr_ok 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__release_ready;
        } else if (((0x0044U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr)) 
                    | (0x0048U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr)))) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__wr_ok 
                = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__configured) 
                   & (0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors)));
        } else if ((1U & (~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__control_busy)))) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__wr_ok 
                = (1U & ((0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr))
                          ? ((1U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata)
                              ? (((0x02d1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__loaded)) 
                                  & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__begin_ready)) 
                                 & (0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors)))
                              : ((2U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata)
                                  ? (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__restore_ready)
                                  : ((4U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata) 
                                     && ((((((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_cfg_ready) 
                                               & (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_4)) 
                                              & (0U 
                                                 != (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_slots))) 
                                             & (0U 
                                                == 
                                                (0x00000fffU 
                                                 & vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_base))) 
                                            & (0x00100000U 
                                               <= vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_base)) 
                                           & (0x40000000U 
                                              >= vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_end)) 
                                          & (((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_base)) 
                                              + (0x000000000002e000ULL 
                                                 * (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_slots)))) 
                                             <= (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_end)))) 
                                         & (0x0000000100000000ULL 
                                            >= (0x00000001ffffffffULL 
                                                & ((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_first)) 
                                                   + (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_slots)))))))))
                          : (((((4U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr)) 
                                || (8U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr))) 
                               || (0x001cU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr))) 
                              || (0x002cU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr)))
                              ? (~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__configured))
                              : ((0x000cU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr))
                                  ? (((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__configured)) 
                                      & (0U < vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata)) 
                                     & (0x0000ffffU 
                                        >= vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata))
                                  : ((((0x0400U <= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr)) 
                                       & (0x0f40U >= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr))) 
                                      & (0x02d1U > (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__loaded))) 
                                     & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr) 
                                        == (0x00000fffU 
                                            & ((IData)(0x0400U) 
                                               + VL_SHIFTL_III(12,32,32, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__loaded), 2U)))))))));
        }
    }
}

void Vdut___024root___nba_sequent__TOP__28(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__28\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VdfgRegularize_h52e72c00_0_0;
    __VdfgRegularize_h52e72c00_0_0 = 0;
    CData/*0:0*/ __VdfgRegularize_h52e72c00_0_6;
    __VdfgRegularize_h52e72c00_0_6 = 0;
    // Body
    __VdfgRegularize_h52e72c00_0_6 = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__wr_ok) 
                                      & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__wr_fire));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__input_write = 
        ((0x0400U <= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr)) 
         & (IData)(__VdfgRegularize_h52e72c00_0_6));
    __VdfgRegularize_h52e72c00_0_0 = ((0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr)) 
                                      & (IData)(__VdfgRegularize_h52e72c00_0_6));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__release_cmd = 
        ((0x00000010U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata) 
         & (IData)(__VdfgRegularize_h52e72c00_0_0));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__start_cmd = (
                                                   (1U 
                                                    == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata) 
                                                   & (IData)(__VdfgRegularize_h52e72c00_0_0));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__latch_cmd = (
                                                   (8U 
                                                    == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata) 
                                                   & (IData)(__VdfgRegularize_h52e72c00_0_0));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT____Vcellinp__journal__cfg_valid 
        = ((IData)(__VdfgRegularize_h52e72c00_0_0) 
           & ((4U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata) 
              & (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_4)));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__restore_cmd = 
        ((2U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata) 
         & (IData)(__VdfgRegularize_h52e72c00_0_0));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__restore_fire 
        = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__restore_cmd) 
           & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__restore_ready));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__lane_input_ready 
        = ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__restore_fire)) 
           & (0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vcellinp__stimulus_ram__we 
        = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT____Vcellinp__network__input_valid) 
           & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__lane_input_ready));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__accept_word 
        = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vcellinp__stimulus_ram__we) 
           | ((0x0dU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)) 
              & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_state_ready)));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__push 
        = (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__half) 
            | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__last_word)) 
           & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__accept_word));
}

void Vdut___024root___nba_sequent__TOP__0(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__1(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__3(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__4(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__5(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__6(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__7(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__8(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__9(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__10(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__11(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__12(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__13(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__14(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__15(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__16(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__17(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__18(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__19(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__20(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__21(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__22(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__23(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__24(Vdut___024root* vlSelf);
void Vdut___024root___nba_sequent__TOP__25(Vdut___024root* vlSelf);

void Vdut___024root___eval_nba(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_nba\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_0;
    __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_0 = 0;
    CData/*0:0*/ __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_6;
    __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_6 = 0;
    // Body
    if ((1ULL & vlSelfRef.__VnbaTriggered[0U])) {
        Vdut___024root___nba_sequent__TOP__0(vlSelf);
        Vdut___024root___nba_sequent__TOP__1(vlSelf);
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v0 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v1 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v2 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v3 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v4 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v5 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v6 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v7 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v8 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v9 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v10 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v0 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v1 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v2 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v3 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v4 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v5 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v6 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v7 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v8 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v9 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v10 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v11 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v12 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v13 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v14 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v15 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v16 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v17 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v18 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v19 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v20 = 0U;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v21 = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v22 = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__publish 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__publish;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__write_slot 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__write_slot;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__got_info 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__got_info;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__timeout_count 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__timeout_count;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__half 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__half;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__acked_beats 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__acked_beats;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__frame_id 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__frame_id;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_hash 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_hash;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_hash 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_hash;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_count 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_count;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__record_base 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__record_base;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__active 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__active;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__fifo_data__v0 = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__cfg_cookie 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_cookie;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__rejected 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__rejected;
        vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__frame__v0 = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__cfg_base 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_base;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__cfg_end 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_end;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__cfg_slots 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_slots;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__cfg_first 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_first;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__release_sequence 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__release_sequence;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__release_cookie 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__release_cookie;
        Vdut___024root___nba_sequent__TOP__3(vlSelf);
        Vdut___024root___nba_sequent__TOP__4(vlSelf);
        Vdut___024root___nba_sequent__TOP__5(vlSelf);
        Vdut___024root___nba_sequent__TOP__6(vlSelf);
        Vdut___024root___nba_sequent__TOP__7(vlSelf);
        Vdut___024root___nba_sequent__TOP__8(vlSelf);
        Vdut___024root___nba_sequent__TOP__9(vlSelf);
        Vdut___024root___nba_sequent__TOP__10(vlSelf);
        Vdut___024root___nba_sequent__TOP__11(vlSelf);
        Vdut___024root___nba_sequent__TOP__12(vlSelf);
        Vdut___024root___nba_sequent__TOP__13(vlSelf);
        Vdut___024root___nba_sequent__TOP__14(vlSelf);
        Vdut___024root___nba_sequent__TOP__15(vlSelf);
        Vdut___024root___nba_sequent__TOP__16(vlSelf);
        Vdut___024root___nba_sequent__TOP__17(vlSelf);
        Vdut___024root___nba_sequent__TOP__18(vlSelf);
        Vdut___024root___nba_sequent__TOP__19(vlSelf);
        Vdut___024root___nba_sequent__TOP__20(vlSelf);
        Vdut___024root___nba_sequent__TOP__21(vlSelf);
        Vdut___024root___nba_sequent__TOP__22(vlSelf);
        Vdut___024root___nba_sequent__TOP__23(vlSelf);
        Vdut___024root___nba_sequent__TOP__24(vlSelf);
        Vdut___024root___nba_sequent__TOP__25(vlSelf);
        Vdut___024root___nba_sequent__TOP__26(vlSelf);
        Vdut___024root___nba_sequent__TOP__27(vlSelf);
        __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_6 
            = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__wr_ok) 
               & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__wr_fire));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__input_write 
            = ((0x0400U <= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr)) 
               & __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_6);
        __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_0 
            = ((0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr)) 
               & __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_6);
        vlSelfRef.flyvis_ddr_soc_ip__DOT__release_cmd 
            = ((0x00000010U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata) 
               & __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_0);
        vlSelfRef.flyvis_ddr_soc_ip__DOT__start_cmd 
            = ((1U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata) 
               & __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_0);
        vlSelfRef.flyvis_ddr_soc_ip__DOT__latch_cmd 
            = ((8U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata) 
               & __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_0);
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT____Vcellinp__journal__cfg_valid 
            = (__Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_0 
               & ((4U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata) 
                  & (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_4)));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__restore_cmd 
            = ((2U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata) 
               & __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_0);
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__restore_fire 
            = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__restore_cmd) 
               & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__restore_ready));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__lane_input_ready 
            = ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__restore_fire)) 
               & (0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vcellinp__stimulus_ram__we 
            = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT____Vcellinp__network__input_valid) 
               & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__lane_input_ready));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__accept_word 
            = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vcellinp__stimulus_ram__we) 
               | ((0x0dU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)) 
                  & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_state_ready)));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__push 
            = (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__half) 
                | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__last_word)) 
               & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__accept_word));
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

void Vdut___024root___eval_triggers_vec__act(Vdut___024root* vlSelf);
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

bool Vdut___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);

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

#ifdef VL_DEBUG
VL_ATTR_COLD void Vdut___024root___dump_triggers__ico(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
bool Vdut___024root___eval_phase__ico(Vdut___024root* vlSelf);

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
            VL_FATAL_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_ddr_soc_ip.sv", 3, "", "DIDNOTCONVERGE: Input combinational region did not converge after '--converge-limit' of 10000 tries");
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
            VL_FATAL_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_ddr_soc_ip.sv", 3, "", "DIDNOTCONVERGE: NBA region did not converge after '--converge-limit' of 10000 tries");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        vlSelfRef.__VactIterCount = 0U;
        do {
            if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                Vdut___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
#endif
                VL_FATAL_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\flyvis_ddr_soc_ip.sv", 3, "", "DIDNOTCONVERGE: Active region did not converge after '--converge-limit' of 10000 tries");
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
    if (VL_UNLIKELY(((vlSelfRef.aclk & 0xfeU)))) {
        Verilated::overWidthError("aclk");
    }
    if (VL_UNLIKELY(((vlSelfRef.aresetn & 0xfeU)))) {
        Verilated::overWidthError("aresetn");
    }
    if (VL_UNLIKELY(((vlSelfRef.s_axi_awaddr & 0xf000U)))) {
        Verilated::overWidthError("s_axi_awaddr");
    }
    if (VL_UNLIKELY(((vlSelfRef.s_axi_awprot & 0xf8U)))) {
        Verilated::overWidthError("s_axi_awprot");
    }
    if (VL_UNLIKELY(((vlSelfRef.s_axi_awvalid & 0xfeU)))) {
        Verilated::overWidthError("s_axi_awvalid");
    }
    if (VL_UNLIKELY(((vlSelfRef.s_axi_wstrb & 0xf0U)))) {
        Verilated::overWidthError("s_axi_wstrb");
    }
    if (VL_UNLIKELY(((vlSelfRef.s_axi_wvalid & 0xfeU)))) {
        Verilated::overWidthError("s_axi_wvalid");
    }
    if (VL_UNLIKELY(((vlSelfRef.s_axi_bready & 0xfeU)))) {
        Verilated::overWidthError("s_axi_bready");
    }
    if (VL_UNLIKELY(((vlSelfRef.s_axi_araddr & 0xf000U)))) {
        Verilated::overWidthError("s_axi_araddr");
    }
    if (VL_UNLIKELY(((vlSelfRef.s_axi_arprot & 0xf8U)))) {
        Verilated::overWidthError("s_axi_arprot");
    }
    if (VL_UNLIKELY(((vlSelfRef.s_axi_arvalid & 0xfeU)))) {
        Verilated::overWidthError("s_axi_arvalid");
    }
    if (VL_UNLIKELY(((vlSelfRef.s_axi_rready & 0xfeU)))) {
        Verilated::overWidthError("s_axi_rready");
    }
    if (VL_UNLIKELY(((vlSelfRef.m_axi_awready & 0xfeU)))) {
        Verilated::overWidthError("m_axi_awready");
    }
    if (VL_UNLIKELY(((vlSelfRef.m_axi_wready & 0xfeU)))) {
        Verilated::overWidthError("m_axi_wready");
    }
    if (VL_UNLIKELY(((vlSelfRef.m_axi_bid & 0xf0U)))) {
        Verilated::overWidthError("m_axi_bid");
    }
    if (VL_UNLIKELY(((vlSelfRef.m_axi_bresp & 0xfcU)))) {
        Verilated::overWidthError("m_axi_bresp");
    }
    if (VL_UNLIKELY(((vlSelfRef.m_axi_bvalid & 0xfeU)))) {
        Verilated::overWidthError("m_axi_bvalid");
    }
}
#endif  // VL_DEBUG

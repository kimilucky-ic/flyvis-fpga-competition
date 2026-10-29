// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See vdut.h for the primary calling header

#include "vdut__pch.h"

void Vdut___024root___nba_sequent__TOP__21(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__21\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__pop 
        = ((IData)(vlSelfRef.m_axi_wvalid) & ((IData)(vlSelfRef.m_axi_wready) 
                                              & (4U 
                                                 != (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_base = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__cfg_base;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_end = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__cfg_end;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_slots = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__cfg_slots;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_first = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__cfg_first;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_cfg_ready 
        = ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__configured)) 
           & ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__active)) 
              & (0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__feed_index = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__feed_index;
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__frame__v0) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__frame[vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__frame__v0] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__frame__v0;
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__feed = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__feed;
    vlSelfRef.__VdfgRegularize_h52e72c00_0_5 = (IData)(
                                                       ((((0U 
                                                           == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors)) 
                                                          & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__active)) 
                                                         & (1U 
                                                            == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))) 
                                                        & ((0x40U 
                                                            > (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count)) 
                                                           & (0x000002d1U 
                                                              > vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_count))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edges 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__edges;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__states 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__states;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__v 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__v;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__v 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__v;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr_data 
        = (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q
           [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__selected] 
           & (- (IData)((0x2cU >= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__selected)))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_count 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_count;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__load_slot 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__load_slot;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__batch_count 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__batch_count;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__received 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__received;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__input_index 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__input_index;
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__desc__v0) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__desc[vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__desc__v0] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__desc__v0;
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_data 
        = (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q
           [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__selected] 
           & (- (IData)((0x2cU >= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__selected)))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_state_ready 
        = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__active) 
           & ((0x40U > (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count)) 
              & ((0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors)) 
                 & ((2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase)) 
                    & (0x0000b265U > vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count)))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index;
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result__v0) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result[vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result__v0] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result__v0;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_old__v0) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_old[vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_old__v0] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_old__v0;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_current[vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_current__v0] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_current__v0;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_input[vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_input__v0] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_input__v0;
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv;
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v0) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[12U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v0;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v1) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[11U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v1;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v2) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[10U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v2;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v3) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[9U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v3;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v4) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[8U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v4;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v5) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[7U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v5;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v6) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[6U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v6;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v7) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[5U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v7;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v8) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[4U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v8;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v9) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[3U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v9;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v10) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[2U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v10;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v11) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[1U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v11;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v12) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[0U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v12;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v0) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[22U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v0;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v1) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[21U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v1;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v0) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[20U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v2;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v3) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[19U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v3;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v1) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[18U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v4;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v5) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[17U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v5;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v2) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[16U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v6;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v7) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[15U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v7;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v3) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[14U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v8;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v9) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[13U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v9;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v4) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[12U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v10;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v11) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[11U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v11;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v5) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[10U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v12;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v13) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[9U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v13;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v6) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[8U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v14;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v15) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[7U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v15;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v7) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[6U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v16;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v17) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[5U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v17;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v8) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[4U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v18;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v19) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[3U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v19;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v9) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[2U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v20;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v21) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[2U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v21;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v10) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[1U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v22;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v0) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[22U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v0;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v1) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[21U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v1;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v2) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[20U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v2;
    }
}

void Vdut___024root___nba_sequent__TOP__22(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__22\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v3) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[19U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v3;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v4) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[18U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v4;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v5) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[17U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v5;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v6) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[16U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v6;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v7) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[15U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v7;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v8) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[14U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v8;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v9) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[13U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v9;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v10) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[12U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v10;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v11) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[11U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v11;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v12) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[10U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v12;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v13) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[9U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v13;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v14) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[8U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v14;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v15) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[7U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v15;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v16) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[6U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v16;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v17) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[5U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v17;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v18) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[4U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v18;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v19) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[3U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v19;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v20) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[2U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v20;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v21) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[1U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v21;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v0) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[22U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v0;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v1) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[21U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v1;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v2) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[20U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v2;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v3) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[19U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v3;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v4) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[18U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v4;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v5) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[17U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v5;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v6) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[16U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v6;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v7) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[15U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v7;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v8) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[14U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v8;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v9) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[13U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v9;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v10) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[12U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v10;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v11) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[11U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v11;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v12) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[10U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v12;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v13) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[10U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v13;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v14) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[9U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v14;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v15) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[8U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v15;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v16) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[7U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v16;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v17) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[6U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v17;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v18) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[5U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v18;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v19) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[4U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v19;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v20) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[3U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v20;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v21) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[2U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v21;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v22) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[1U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v22;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v0) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[22U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v0;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v1) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[21U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v1;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v2) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[20U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v2;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v3) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[19U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v3;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v4) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[18U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v4;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v5) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[17U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v5;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v6) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[16U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v6;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v7) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[15U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v7;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v8) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[14U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v8;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v9) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[13U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v9;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v10) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[12U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v10;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v11) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[11U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v11;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v12) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[10U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v12;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v13) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[9U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v13;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v14) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[8U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v14;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v15) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[7U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v15;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v16) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[6U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v16;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v17) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[5U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v17;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v18) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[4U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v18;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v19) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[3U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v19;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v20) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[2U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v20;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v21) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[1U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v21;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v22) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[0U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v22;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[0U] = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[0U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v22;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v0) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[22U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v0;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v1) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[21U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v1;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v2) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[20U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v2;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v3) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[19U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v3;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v4) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[18U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v4;
    }
}

void Vdut___024root___nba_sequent__TOP__23(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__23\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v5) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[17U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v5;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v6) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[16U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v6;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v7) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[15U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v7;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v8) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[14U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v8;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v9) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[13U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v9;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v10) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[12U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v10;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v11) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[11U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v11;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v12) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[10U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v12;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v13) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[9U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v13;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v14) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[8U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v14;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v15) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[7U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v15;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v16) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[6U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v16;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v17) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[5U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v17;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v18) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[4U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v18;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v19) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[3U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v19;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v20) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[2U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v20;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v21) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[1U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v21;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v22) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[0U] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v22;
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__full = ((((vlSelfRef.flyvis_ddr_soc_ip__DOT__committed 
                                                 - vlSelfRef.flyvis_ddr_soc_ip__DOT__released) 
                                                >= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__slots)) 
                                               | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__sequence_exhausted) 
                                                  | ((0xffffffffU 
                                                      == vlSelfRef.flyvis_ddr_soc_ip__DOT__committed) 
                                                     | ((IData)(
                                                                (1ULL 
                                                                 & ((0x000000000002e000ULL 
                                                                     + (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__record_base))) 
                                                                    >> 0x00000020U))) 
                                                        | ((0x00000001ffffffffULL 
                                                            & (0x000000000002e000ULL 
                                                               + (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__record_base)))) 
                                                           > (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__end_address))))))) 
                                              & (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_3));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__word_bits 
        = ((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))
            ? vlSelfRef.flyvis_ddr_soc_ip__DOT__frame_q
            : vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__old_a);
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__av 
        = ((IData)(vlSelfRef.aresetn) && (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cv 
        = ((IData)(vlSelfRef.aresetn) && (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr));
    if (VL_UNLIKELY(((((IData)(vlSelfRef.aresetn) & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_read)) 
                      & ((((0x3eU <= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rows_addr)) 
                           | (0x3eU <= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_rows_addr))) 
                          | VL_GTS_III(32, 0U, VL_EXTENDS_II(32,8, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_read_u)))) 
                         | VL_LTS_III(32, 0x0000001eU, 
                                      VL_EXTENDS_II(32,8, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_read_u)))))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: compact_edge_gen.sv:118: Assertion failed in %m: prefetched source/target row address out of range\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen", 'T',-12
                     , '#',64,VL_TIME_UNITED_Q(1));
        VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\compact_edge_gen.sv", 118, "", false);
    }
    if (vlSelfRef.aresetn) {
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__start_cmd) 
             & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__begin_ready))) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__inflight = 1U;
        }
        if (vlSelfRef.flyvis_ddr_soc_ip__DOT__publish) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__inflight = 0U;
        }
        if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vcellinp__stimulus_ram__re) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__stim_q 
                = ((0x02d0U >= (0x000003ffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index))
                    ? vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__stimulus_ram__DOT__ordinary__DOT__mem
                   [(0x000003ffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index)]
                    : 0U);
        }
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_out 
            = (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__packed_result);
        if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__advance) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edge_valid = 0U;
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_pending 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_read;
            if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_pending) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_first 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__first_j;
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_end 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__end_j;
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_step 
                    = (((2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tv)) 
                        & (1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sv)))
                        ? 2U : 1U);
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_vfirst 
                    = (0x0000000fU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_q);
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_rank 
                    = (0x000003ffU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_q 
                                      >> 0x10U));
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_nonempty 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__descriptor_valid;
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_tag 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_tag;
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_ready = 1U;
            }
            if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__descriptor_query) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_ready = 0U;
            }
            if (VL_UNLIKELY((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__descriptor_query) 
                              & ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_ready)) 
                                 | ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_tag) 
                                    != (0x0000001fU 
                                        & ((0x0cU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))
                                            ? ((IData)(1U) 
                                               + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u))
                                            : (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u))))))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: compact_edge_gen.sv:136: Assertion failed in %m: clipped row descriptor tag/not-ready mismatch\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen", 'T',-12
                             , '#',64,VL_TIME_UNITED_Q(1));
                VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\compact_edge_gen.sv", 136, "", false);
            }
            if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_read) {
                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_tag 
                    = (0x0000001fU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__prefetch_u));
            }
            if ((((((((((0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state)) 
                        || (0x0dU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) 
                       | (1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) 
                      | (2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) 
                     | (3U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) 
                    | (4U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) 
                   | (5U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) 
                  | (6U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) 
                 | (7U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state)))) {
                if (((0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state)) 
                     || (0x0dU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state)))) {
                    if ((2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 1U;
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id = 0U;
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id = 0U;
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__next_eid = 0U;
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_pending = 0U;
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_ready = 0U;
                    }
                } else if ((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 2U;
                } else if ((2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
                    vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r__v0 
                        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_q;
                    vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r__v0 
                        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id;
                    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r__v0 = 1U;
                    if ((3U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id))) {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id = 0U;
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 3U;
                    } else {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id 
                            = (3U & ((IData)(1U) + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id)));
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 1U;
                    }
                } else if ((3U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 4U;
                } else if ((4U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
                    vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sn__v0 
                        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_q;
                    vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sn__v0 
                        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id;
                    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sn__v0 = 1U;
                    if ((3U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id))) {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id = 0U;
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 5U;
                    } else {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id 
                            = (3U & ((IData)(1U) + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id)));
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 3U;
                    }
                } else if ((5U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 6U;
                } else if ((6U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
                    vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tn__v0 
                        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_q;
                    vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tn__v0 
                        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id;
                    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tn__v0 = 1U;
                    if ((3U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id))) {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id = 0U;
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 7U;
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id 
                            = (0x00000fffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r[1U]);
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_end 
                            = (0x00000fffU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r[1U] 
                                              + (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r[0U] 
                                                 >> 0x10U)));
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sbase 
                            = (0x0000ffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sn[0U]);
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tbase 
                            = (0x0000ffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tn[0U]);
                        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sl 
                            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sn[1U] 
                                     >> 0x10U));
                        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tl 
                            = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tn[1U] 
                                     >> 0x10U));
                        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sv 
                            = (3U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sn[1U] 
                                     >> 8U));
                        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tv 
                            = (3U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tn[1U] 
                                     >> 8U));
                        if (VL_UNLIKELY(((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__next_eid 
                                          != (0x001fffffU 
                                              & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r[2U]))))) {
                            VL_WRITEF_NX("[%0t] %%Fatal: compact_edge_gen.sv:161: Assertion failed in %m: rule first eid mismatch\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen", 'T',-12
                                         , '#',64,VL_TIME_UNITED_Q(1));
                            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\compact_edge_gen.sv", 161, "", false);
                        }
                        if (VL_UNLIKELY(((((((0x00000fffU 
                                              < (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r[1U] 
                                                 + 
                                                 (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r[0U] 
                                                  >> 0x10U))) 
                                             | (1U 
                                                < (0x000000ffU 
                                                   & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sn[1U] 
                                                      >> 0x10U)))) 
                                            | (1U < 
                                               (0x000000ffU 
                                                & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tn[1U] 
                                                   >> 0x10U)))) 
                                           | ((1U > 
                                               (0x000000ffU 
                                                & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sn[1U] 
                                                   >> 8U))) 
                                              | (2U 
                                                 < 
                                                 (0x000000ffU 
                                                  & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sn[1U] 
                                                     >> 8U))))) 
                                          | ((1U > 
                                              (0x000000ffU 
                                               & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tn[1U] 
                                                  >> 8U))) 
                                             | (2U 
                                                < (0x000000ffU 
                                                   & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tn[1U] 
                                                      >> 8U)))))))) {
                            VL_WRITEF_NX("[%0t] %%Fatal: compact_edge_gen.sv:164: Assertion failed in %m: template exceeds checked address widths\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen", 'T',-12
                                         , '#',64,VL_TIME_UNITED_Q(1));
                            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\compact_edge_gen.sv", 164, "", false);
                        }
                    } else {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id 
                            = (3U & ((IData)(1U) + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id)));
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 5U;
                    }
                } else {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 8U;
                }
            } else if ((8U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
                if ((0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id))) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom 
                        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_q;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id = 1U;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 7U;
                } else {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_weight 
                        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_q;
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__du 
                        = (0x0000000fU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom);
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id = 0U;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 9U;
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__dv 
                        = (0x0000000fU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom 
                                          >> 8U));
                    if (VL_UNLIKELY(((((VL_GTS_III(32, 0xfffffff8U, 
                                                   VL_EXTENDS_II(32,8, 
                                                                 (0x000000ffU 
                                                                  & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom))) 
                                        | VL_LTS_III(32, 7U, 
                                                     VL_EXTENDS_II(32,8, 
                                                                   (0x000000ffU 
                                                                    & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom)))) 
                                       | VL_GTS_III(32, 0xfffffff8U, 
                                                    VL_EXTENDS_II(32,8, 
                                                                  (0x000000ffU 
                                                                   & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom 
                                                                      >> 8U))))) 
                                      | VL_LTS_III(32, 7U, 
                                                   VL_EXTENDS_II(32,8, 
                                                                 (0x000000ffU 
                                                                  & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom 
                                                                     >> 8U)))))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: compact_edge_gen.sv:176: Assertion failed in %m: offset exceeds checked signed width\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen", 'T',-12
                                     , '#',64,VL_TIME_UNITED_Q(1));
                        VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\compact_edge_gen.sv", 176, "", false);
                    }
                    if ((8U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom)) {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u 
                            = (0x0000001fU & (- ((0x00000070U 
                                                  & ((- (IData)(
                                                                (1U 
                                                                 & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom 
                                                                    >> 3U)))) 
                                                     << 4U)) 
                                                 | (0x0000000fU 
                                                    & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom))));
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u_last = 0x0000001eU;
                    } else {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u = 0U;
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u_last 
                            = (0x0000001fU & ((IData)(0x1eU) 
                                              - (0x0000000fU 
                                                 & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom)));
                    }
                }
            } else if ((9U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 0x0eU;
            } else if ((0x0eU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 0x0aU;
            } else if ((0x0aU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
                if (VL_UNLIKELY(((((0x0fU < (0x000000ffU 
                                             & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_q)) 
                                   | (0x1fU < (0x000000ffU 
                                               & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_q 
                                                  >> 8U)))) 
                                  | (0x03ffU < (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_q 
                                                >> 0x10U)))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: compact_edge_gen.sv:191: Assertion failed in %m: row descriptor exceeds checked widths\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen", 'T',-12
                                 , '#',64,VL_TIME_UNITED_Q(1));
                    VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\compact_edge_gen.sv", 191, "", false);
                }
                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__vfirst 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_vfirst;
                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_count 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_end;
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rank_first 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_rank;
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_first;
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j_step 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_step;
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__bounds_q 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__in_bounds;
                if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_nonempty) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 0x0cU;
                } else if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u) 
                            < (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u_last))) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u 
                        = (0x0000001fU & ((IData)(1U) 
                                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u)));
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 0x0eU;
                } else if ((((IData)(1U) + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id)) 
                            < (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_end))) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id 
                        = (0x00000fffU & ((IData)(1U) 
                                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id)));
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 7U;
                } else if ((0x0000025dU > ((IData)(1U) 
                                           + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id)))) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id 
                        = (0x000003ffU & ((IData)(1U) 
                                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id)));
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 1U;
                } else {
                    if (VL_UNLIKELY(((0x0017170fU != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__next_eid)))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: compact_edge_gen.sv:199: Assertion failed in %m: edge total mismatch\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen", 'T',-12
                                     , '#',64,VL_TIME_UNITED_Q(1));
                        VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\compact_edge_gen.sv", 199, "", false);
                    }
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 0x0dU;
                }
            } else if (VL_LIKELY(((0x0cU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))))) {
                if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__bounds_q) 
                     & (0xffffU != (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__map_q)))) {
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edge_valid = 1U;
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_src 
                        = (0x0000ffffU & (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sbase) 
                                           + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rank_first)) 
                                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j)));
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst 
                        = (0x0000ffffU & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tbase) 
                                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__map_q)));
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_weight 
                        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_weight;
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_eid 
                        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__next_eid;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__next_eid 
                        = (0x001fffffU & ((IData)(1U) 
                                          + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__next_eid));
                }
                if (VL_UNLIKELY(((1U & ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__bounds_q)) 
                                        | (0xffffU 
                                           == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__map_q))))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: compact_edge_gen.sv:214: Assertion failed in %m: hole survived occupied-row intersection\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen", 'T',-12
                                 , '#',64,VL_TIME_UNITED_Q(1));
                    VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\compact_edge_gen.sv", 214, "", false);
                }
                if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__last_candidate) {
                    if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u) 
                         < (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u_last))) {
                        if (VL_UNLIKELY(((((0x0fU < 
                                            (0x000000ffU 
                                             & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_q)) 
                                           | (0x1fU 
                                              < (0x000000ffU 
                                                 & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_q 
                                                    >> 8U)))) 
                                          | (0x03ffU 
                                             < (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_q 
                                                >> 0x10U)))))) {
                            VL_WRITEF_NX("[%0t] %%Fatal: compact_edge_gen.sv:222: Assertion failed in %m: prefetched row descriptor exceeds checked widths\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen", 'T',-12
                                         , '#',64,VL_TIME_UNITED_Q(1));
                            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\compact_edge_gen.sv", 222, "", false);
                        }
                        if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_ready) {
                            if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_nonempty) {
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u 
                                    = (0x0000001fU 
                                       & ((IData)(1U) 
                                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u)));
                                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__vfirst 
                                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_vfirst;
                                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_count 
                                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_end;
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rank_first 
                                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_rank;
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j 
                                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_first;
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j_step 
                                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_step;
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__bounds_q 
                                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__in_bounds;
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 0x0cU;
                            } else if ((((IData)(1U) 
                                         + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u)) 
                                        < (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u_last))) {
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u 
                                    = (0x0000001fU 
                                       & ((IData)(2U) 
                                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u)));
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 0x0eU;
                            } else if ((((IData)(1U) 
                                         + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id)) 
                                        < (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_end))) {
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id 
                                    = (0x00000fffU 
                                       & ((IData)(1U) 
                                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id)));
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 7U;
                            } else if ((0x0000025dU 
                                        > ((IData)(1U) 
                                           + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id)))) {
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id 
                                    = (0x000003ffU 
                                       & ((IData)(1U) 
                                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id)));
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 1U;
                            } else {
                                if (VL_UNLIKELY(((0x0017170fU 
                                                  != 
                                                  (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__next_eid 
                                                   + 
                                                   ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__bounds_q) 
                                                    & (0xffffU 
                                                       != (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__map_q)))))))) {
                                    VL_WRITEF_NX("[%0t] %%Fatal: compact_edge_gen.sv:233: Assertion failed in %m: edge total mismatch\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen", 'T',-12
                                                 , '#',64,VL_TIME_UNITED_Q(1));
                                    VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\compact_edge_gen.sv", 233, "", false);
                                }
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 0x0dU;
                            }
                        } else {
                            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u 
                                = (0x0000001fU & ((IData)(1U) 
                                                  + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u)));
                            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 0x0aU;
                        }
                    } else if ((((IData)(1U) + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id)) 
                                < (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_end))) {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id 
                            = (0x00000fffU & ((IData)(1U) 
                                              + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id)));
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 7U;
                    } else if ((0x0000025dU > ((IData)(1U) 
                                               + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id)))) {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id 
                            = (0x000003ffU & ((IData)(1U) 
                                              + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id)));
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 1U;
                    } else {
                        if (VL_UNLIKELY(((0x0017170fU 
                                          != (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__next_eid 
                                              + ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__bounds_q) 
                                                 & (0xffffU 
                                                    != (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__map_q)))))))) {
                            VL_WRITEF_NX("[%0t] %%Fatal: compact_edge_gen.sv:241: Assertion failed in %m: edge total mismatch\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen", 'T',-12
                                         , '#',64,VL_TIME_UNITED_Q(1));
                            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\compact_edge_gen.sv", 241, "", false);
                        }
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 0x0dU;
                    }
                } else {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j 
                        = (0x0000001fU & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j) 
                                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j_step)));
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__bounds_q 
                        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__in_bounds;
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 0x0cU;
                }
            } else {
                VL_WRITEF_NX("[%0t] %%Fatal: compact_edge_gen.sv:247: Assertion failed in %m: generator state\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen", 'T',-12
                             , '#',64,VL_TIME_UNITED_Q(1));
                VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\compact_edge_gen.sv", 247, "", false);
            }
        }
    } else {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__inflight = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_pending = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_eid = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__next_eid = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edge_valid = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_weight = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_ready = 0U;
    }
}

void Vdut___024root___nba_sequent__TOP__24(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__24\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    SData/*10:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__final_exp;
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__final_exp = 0;
    // Body
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_begin_ready 
        = ((IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_3) 
           & ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__full)) 
              & (0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__publish = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__publish;
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__stimulus_ram__DOT__ordinary__DOT__mem__v0) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__stimulus_ram__DOT__ordinary__DOT__mem[vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__stimulus_ram__DOT__ordinary__DOT__mem__v0] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__stimulus_ram__DOT__ordinary__DOT__mem__v0;
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index;
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
    if ((0x10000000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][9U])) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__packed_result 
            = (0x0000001fffffffffULL & (((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][9U])) 
                                         << 9U) | ((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[6U][8U])) 
                                                   >> 0x00000017U)));
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_pending 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_pending;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_end 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_end;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_step 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_step;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_rank 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_rank;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__next_eid 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__next_eid;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_end 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_end;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sbase 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sbase;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tbase 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tbase;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_weight 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_weight;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rank_first 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rank_first;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__bounds_q 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__bounds_q;
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sn__v0) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sn[vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sn__v0] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sn__v0;
    }
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tn__v0) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tn[vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tn__v0] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tn__v0;
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id;
    if (vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r__v0) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r[vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r__v0] 
            = vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r__v0;
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_first 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_first;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_vfirst 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_vfirst;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_nonempty 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_nonempty;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_tag 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_tag;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_ready 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_ready;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u_last 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u_last;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j_step 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j_step;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT____Vcellinp__network__input_valid 
        = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__inflight) 
           & ((2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__feed)) 
              & (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_5)));
    vlSelfRef.__VdfgRegularize_h52e72c00_0_7 = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__inflight) 
                                                | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__restoring));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen_rom_addr = 0U;
    if ((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen_rom_addr 
            = (0x00001fffU & ((IData)(0x0124U) + (VL_SHIFTL_III(13,32,32, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id), 2U) 
                                                  + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id))));
    } else if ((3U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen_rom_addr 
            = (0x00001fffU & ((IData)(0x0020U) + (VL_SHIFTL_III(13,32,32, 
                                                                (0x000000ffU 
                                                                 & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r[0U]), 2U) 
                                                  + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id))));
    } else if ((5U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen_rom_addr 
            = (0x00001fffU & ((IData)(0x0020U) + (VL_SHIFTL_III(13,32,32, 
                                                                (0x000000ffU 
                                                                 & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r[0U] 
                                                                    >> 8U)), 2U) 
                                                  + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id))));
    } else if ((7U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen_rom_addr 
            = (0x00001fffU & ((IData)(0x0a98U) + (VL_SHIFTL_III(13,32,32, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id), 1U) 
                                                  + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id))));
    }
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
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vcellinp__stimulus_ram__re 
        = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_input) 
           & (7U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_b 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[1U];
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
    }
}

void Vdut___024root___nba_sequent__TOP__25(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__25\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    SData/*15:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pipe_dst;
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pipe_dst = 0;
    // Body
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_valid 
        = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                 >> 1U));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_valid 
        = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                 >> 9U));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_a 
        = (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_data 
             >> 0x0000001fU) | (0U == (0x7fffffffU 
                                       & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_data)))
            ? 0U : vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_data);
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
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_a 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[9U];
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pipe_valid 
        = (1U & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
                 >> 0x16U));
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pipe_dst 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[22U];
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw = 0U;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr = 0U;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data = 0U;
    if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pipe_valid) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr 
            = flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pipe_dst;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_out;
    }
    if ((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr 
            = (0x0000ffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index);
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data = 0U;
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_b 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_out;
    if ((9U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_valid 
            = ((3U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id) 
               | (4U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_valid 
            = (1U & (~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_valid)));
        if ((0U != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
            if ((1U != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
                if ((2U != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
                    if ((3U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
                        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_a 
                            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__inv;
                    } else if ((4U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
                        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_a 
                            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result
                            [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot];
                    }
                }
            }
        }
        if ((0U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_a 
                = (0x80000000U ^ vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_old
                   [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot]);
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_b 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__bias;
        } else if ((1U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_a 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result
                [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot];
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_b 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_current
                [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot];
        } else if ((2U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_a 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result
                [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot];
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_b 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_input
                [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot];
        } else if ((3U != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
            if ((4U != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
                if ((5U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id)) {
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_a 
                        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_old
                        [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot];
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_b 
                        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result
                        [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot];
                }
            }
        }
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_result 
        = (((3U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id) 
            | (4U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id))
            ? vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_out
            : vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_out);
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_return 
        = (((9U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)) 
            | (0x0aU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) 
           & ((0x0cU >= (((3U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id) 
                          | (4U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id))
                          ? 7U : 0x0000000cU)) && (1U 
                                                   & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid) 
                                                      >> 
                                                      (((3U 
                                                         == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id) 
                                                        | (4U 
                                                           == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id))
                                                        ? 7U
                                                        : 0x0000000cU)))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__return_slot 
        = ((0x0cU >= (((3U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id) 
                       | (4U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id))
                       ? 7U : 0x0000000cU)) ? vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag
           [(((3U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id) 
              | (4U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id))
              ? 7U : 0x0000000cU)] : 0U);
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw = 0U;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr = 0U;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data = 0U;
    if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_return) 
         & (5U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr 
            = (0x0000ffffU & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_base 
                               + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__batch_first) 
                              + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__return_slot)));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_result;
    }
    if ((0x13U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw = 1U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr 
            = (0x0000ffffU & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_base 
                              + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data 
            = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__bias;
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 0U;
    if ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
         & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[0U] 
            == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 1U) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[1U] 
                    == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 2U) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[2U] 
                    == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 3U) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[3U] 
                    == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 4U) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[4U] 
                    == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 5U) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[5U] 
                    == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
    if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
          >> 6U) & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[6U] 
                    == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst)))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = 1U;
    }
}

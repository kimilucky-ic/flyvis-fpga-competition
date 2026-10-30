// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See vdut.h for the primary calling header

#include "vdut__pch.h"

void Vdut___024root___nba_sequent__TOP__17(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__17\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*4:0*/ __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__Vfuncout;
    __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__Vfuncout = 0;
    IData/*17:0*/ __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__x;
    __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__x = 0;
    IData/*17:0*/ __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__q;
    __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__q = 0;
    CData/*4:0*/ __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__n;
    __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__n = 0;
    VlWide<10>/*319:0*/ __Vtemp_2;
    VlWide<10>/*319:0*/ __Vtemp_6;
    VlWide<10>/*319:0*/ __Vtemp_9;
    VlWide<10>/*319:0*/ __Vtemp_12;
    VlWide<10>/*319:0*/ __Vtemp_15;
    // Body
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
        VL_SHIFTL_WWI(291,291,32, __Vtemp_2, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x, 0x000000a3U);
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U] 
            = ((0xfffffffeU & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U]) 
               | (1U & (vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q[0U] 
                        | (0U != (((((((((__Vtemp_2[0U] 
                                          | __Vtemp_2[1U]) 
                                         | __Vtemp_2[2U]) 
                                        | __Vtemp_2[3U]) 
                                       | __Vtemp_2[4U]) 
                                      | __Vtemp_2[5U]) 
                                     | __Vtemp_2[6U]) 
                                    | __Vtemp_2[7U]) 
                                   | __Vtemp_2[8U]) 
                                  | (7U & __Vtemp_2[9U]))))));
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
        VL_SHIFTL_WWI(291,291,32, __Vtemp_6, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x, 0x00000122U);
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U] 
            = ((0xfffffffeU & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U]) 
               | (1U & (vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U] 
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
        VL_SHIFTL_WWI(291,291,32, __Vtemp_9, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x, 0x00000121U);
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U] 
            = ((0xfffffffeU & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U]) 
               | (1U & (vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U] 
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
        VL_SHIFTL_WWI(291,291,32, __Vtemp_12, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x, 0x0000011fU);
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U] 
            = ((0xfffffffeU & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U]) 
               | (1U & (vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U] 
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
        VL_SHIFTL_WWI(291,291,32, __Vtemp_15, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x, 0x0000011bU);
        vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U] 
            = ((0xfffffffeU & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U]) 
               | (1U & (vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q[0U] 
                        | (0U != (((((((((__Vtemp_15[0U] 
                                          | __Vtemp_15[1U]) 
                                         | __Vtemp_15[2U]) 
                                        | __Vtemp_15[3U]) 
                                       | __Vtemp_15[4U]) 
                                      | __Vtemp_15[5U]) 
                                     | __Vtemp_15[6U]) 
                                    | __Vtemp_15[7U]) 
                                   | __Vtemp_15[8U]) 
                                  | (7U & __Vtemp_15[9U]))))));
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
    __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__x 
        = (0x0003ffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[7U][13U]);
    __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__q 
        = __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__x;
    __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__n = 0U;
    if ((0U != (3U & (__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__q 
                      >> 0x10U)))) {
        __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__q 
            = VL_SHIFTR_III(18,18,32, __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__q, 0x00000010U);
        __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__n 
            = (0x0000001fU & ((IData)(0x10U) + (IData)(__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__n)));
    }
    if ((0U != (0x000000ffU & (__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__q 
                               >> 8U)))) {
        __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__q 
            = VL_SHIFTR_III(18,18,32, __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__q, 8U);
        __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__n 
            = (0x0000001fU & ((IData)(8U) + (IData)(__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__n)));
    }
    if ((0U != (0x0000000fU & (__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__q 
                               >> 4U)))) {
        __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__q 
            = VL_SHIFTR_III(18,18,32, __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__q, 4U);
        __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__n 
            = (0x0000001fU & ((IData)(4U) + (IData)(__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__n)));
    }
    if ((0U != (3U & (__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__q 
                      >> 2U)))) {
        __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__q 
            = VL_SHIFTR_III(18,18,32, __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__q, 2U);
        __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__n 
            = (0x0000001fU & ((IData)(2U) + (IData)(__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__n)));
    }
    if ((2U & __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__q)) {
        __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__n 
            = (0x0000001fU & ((IData)(1U) + (IData)(__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__n)));
    }
    __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__Vfuncout 
        = __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__n;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__group_index 
        = __Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__msb18__2__Vfuncout;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__wr_fire = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__aw_pending) 
                                                 & ((~ (IData)(vlSelfRef.s_axi_bvalid)) 
                                                    & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__w_pending)));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[0U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[1U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[2U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[3U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[4U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[5U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[6U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[7U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[8U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[9U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[10U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[11U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[12U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[13U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[14U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[15U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[16U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[17U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[18U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[19U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[20U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[21U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[22U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[23U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[24U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[25U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[26U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[27U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[28U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[29U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[30U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[31U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[32U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[33U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[34U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[35U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[36U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[37U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[38U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[39U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[40U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[41U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[42U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[43U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[44U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__data;
}

void Vdut___024root___nba_sequent__TOP__18(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__18\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[0U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[1U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[2U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[3U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[4U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[5U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[6U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[7U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[8U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[9U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[10U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[11U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[12U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[13U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[14U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[15U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[16U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[17U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[18U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[19U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[20U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[21U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[22U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[23U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[24U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[25U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[26U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[27U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[28U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[29U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[30U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[31U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[32U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[33U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[34U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[35U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[36U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[37U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[38U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[39U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[40U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[41U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[42U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[43U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__data;
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[44U] 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__data;
    if (vlSelfRef.aresetn) {
        if (((IData)(vlSelfRef.s_axi_wvalid) & (IData)(vlSelfRef.s_axi_wready))) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata 
                = vlSelfRef.s_axi_wdata;
        }
        if (((IData)(vlSelfRef.s_axi_awvalid) & (IData)(vlSelfRef.s_axi_awready))) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr 
                = vlSelfRef.s_axi_awaddr;
        }
        if (vlSelfRef.flyvis_ddr_soc_ip__DOT__latch_cmd) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__snap_errors 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__snap_frame 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__live_frame;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__snap_base 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__live_base;
        }
        if (vlSelfRef.flyvis_ddr_soc_ip__DOT__publish) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__live_cycles 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__cycles;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__live_seq 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__committed;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__live_frame 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__published_frame;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__live_base 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__published_base;
        }
        if (vlSelfRef.flyvis_ddr_soc_ip__DOT__release_cmd) {
            if (vlSelfRef.flyvis_ddr_soc_ip__DOT__release_ready) {
                vlSelfRef.flyvis_ddr_soc_ip__DOT__released 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__release_sequence;
            }
            if ((1U & (~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__release_ready)))) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors 
                    = (0x00000020U | (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors));
            }
        }
        if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__restore_fire) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__clean = 0U;
        }
        if ((0x14U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__clean = 1U;
        }
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
                vlSelfRef.flyvis_ddr_soc_ip__DOT__configured = 1U;
            }
            if ((((((0U != (0x00000fffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_base)) 
                    | (vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_end 
                       <= vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_base)) 
                   | (0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_slots))) 
                  | (((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_base)) 
                      + (0x000000000002e000ULL * (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_slots)))) 
                     > (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_end)))) 
                 | (0x0000000100000000ULL < (0x00000001ffffffffULL 
                                             & ((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_first)) 
                                                + (QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_slots))))))) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors 
                    = (8U | (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors));
            } else {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__record_base 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_base;
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__write_slot = 0U;
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__frame_id 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__cfg_first;
            }
        }
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__publish = 0U;
        if ((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__start_cmd) 
              & (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_9)) 
             & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_begin_ready))) {
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__active = 1U;
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase = 1U;
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_count = 0U;
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count = 0U;
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__half = 0U;
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_hash = 0U;
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_hash = 0U;
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__acked_beats = 0U;
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__got_info = 0U;
        }
        if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__accept_word) {
            if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__half) 
                 | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__last_word))) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__half = 0U;
            } else {
                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__low_word 
                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__word_bits;
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__half = 1U;
            }
            if ((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_count 
                    = ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_count);
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_hash 
                    = ((((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_hash 
                          << 1U) | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_hash 
                                    >> 0x1fU)) ^ vlSelfRef.flyvis_ddr_soc_ip__DOT__frame_q) 
                       ^ vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_count);
            } else {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count 
                    = ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count);
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_hash 
                    = ((((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_hash 
                          << 1U) | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_hash 
                                    >> 0x1fU)) ^ vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__old_a) 
                       ^ vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count);
                if ((((0x0000ffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index) 
                      != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count) 
                     | ((0xb264U == (0x0000ffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index)) 
                        != (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__last_word)))) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors 
                        = (1U | (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors));
                }
            }
        }
        if ((2U == (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__push) 
                     << 1U) | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__pop)))) {
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count 
                = (0x0000007fU & ((IData)(1U) + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count)));
        } else if ((1U == (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__push) 
                            << 1U) | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__pop)))) {
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count 
                = (0x0000007fU & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count) 
                                  - (IData)(1U)));
        }
        if (((0x0eU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)) 
             & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__active))) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__saved_cycles 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__cycles;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__saved_edges 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edges;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__saved_states 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__states;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__saved_faults 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__core_faults;
            if (((((((0x0017170fU != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edges) 
                     | (0x0000b265U != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__states)) 
                    | (0U != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__core_faults)) 
                   | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__got_info)) 
                  | (0x0000b265U != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count)) 
                 | (0x000002d1U != vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_count))) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors 
                    = (0x00000010U | (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors));
            }
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__got_info = 1U;
        }
        if ((((3U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase)) 
              & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__got_info)) 
             & (0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors)))) {
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase = 4U;
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__acked_beats = 0U;
        }
        if (((((0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus)) 
               | ((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus)) 
                  & (IData)(vlSelfRef.m_axi_awready))) 
              | ((2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus)) 
                 & (IData)(vlSelfRef.m_axi_wready))) 
             | ((3U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus)) 
                & (IData)(vlSelfRef.m_axi_bvalid)))) {
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__timeout_count = 0U;
        } else if ((0x00010000U > vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__timeout_count)) {
            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__timeout_count 
                = (0x0001ffffU & ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__timeout_count));
            if ((0x0000ffffU == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__timeout_count)) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors 
                    = (4U | (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors));
            }
        }
        if ((2U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus))) {
            if ((1U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus))) {
                if (vlSelfRef.m_axi_bvalid) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus = 0U;
                    if ((0U != ((0U == (IData)(vlSelfRef.m_axi_bid))
                                 ? (IData)(vlSelfRef.m_axi_bresp)
                                 : 2U))) {
                        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors 
                            = (2U | (IData)(vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors));
                    } else if ((0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors))) {
                        if ((4U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))) {
                            vlSelfRef.flyvis_ddr_soc_ip__DOT__committed 
                                = ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__committed);
                            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__publish = 1U;
                            vlSelfRef.flyvis_ddr_soc_ip__DOT__published_base 
                                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__record_base;
                            vlSelfRef.flyvis_ddr_soc_ip__DOT__published_frame 
                                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__frame_id;
                            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__active = 0U;
                            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase = 0U;
                            if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__write_slot) 
                                 == ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__slots) 
                                     - (IData)(1U)))) {
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__record_base 
                                    = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__ring_base;
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__write_slot = 0U;
                            } else {
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__record_base 
                                    = ((IData)(0x0002e000U) 
                                       + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__record_base);
                                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__write_slot 
                                    = (0x0000ffffU 
                                       & ((IData)(1U) 
                                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__write_slot)));
                            }
                            if ((0xffffffffU == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__frame_id)) {
                                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__sequence_exhausted = 1U;
                            }
                            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__frame_id 
                                = ((IData)(1U) + vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__frame_id);
                        } else if (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__acked_beats 
                                     + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__burst_beats)) 
                                    == ((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))
                                         ? 0x00000169U
                                         : 0x00005933U))) {
                            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase 
                                = ((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))
                                    ? 2U : 3U);
                            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__acked_beats = 0U;
                            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__half = 0U;
                        } else {
                            vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__acked_beats 
                                = (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__acked_beats 
                                   + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__burst_beats));
                        }
                    }
                }
            } else if (vlSelfRef.m_axi_wready) {
                if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__beat) 
                     == ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__burst_beats) 
                         - (IData)(1U)))) {
                    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus = 3U;
                } else {
                    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__beat 
                        = (0x0000001fU & ((IData)(1U) 
                                          + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__beat)));
                }
            }
        } else if ((1U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus))) {
            if (vlSelfRef.m_axi_awready) {
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus = 2U;
            }
        } else if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__active) 
                    & (0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors)))) {
            if ((4U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))) {
                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__burst_beats = 0x10U;
                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__beat = 0U;
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus = 1U;
            } else if (((((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase)) 
                          | (2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))) 
                         & (0U != (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count))) 
                        & ((0x10U <= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count)) 
                           | ((1U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))
                               ? (0x000002d1U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_count)
                               : (0x0000b265U == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count))))) {
                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__burst_beats 
                    = ((0x10U <= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count))
                        ? 0x00000010U : (0x0000001fU 
                                         & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count)));
                vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__beat = 0U;
                vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus = 1U;
            }
        }
    } else {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__live_cycles = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__live_seq = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__snap_errors = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__released = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__clean = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__configured = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__snap_frame = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__snap_base = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__live_frame = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__live_base = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__record_base = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__frame_id = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__committed = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__write_slot = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__half = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__acked_beats = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_hash = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_hash = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__active = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__sequence_exhausted = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__low_word = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_count = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__got_info = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__saved_cycles = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__saved_edges = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__saved_states = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__saved_faults = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__publish = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__published_base = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__published_frame = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__burst_beats = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__beat = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__timeout_count = 0U;
    }
    vlSelfRef.s_axi_wready = (1U & (~ ((IData)(vlSelfRef.s_axi_bvalid) 
                                       | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__w_pending))));
    vlSelfRef.s_axi_awready = (1U & (~ ((IData)(vlSelfRef.s_axi_bvalid) 
                                        | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__aw_pending))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__release_sequence 
        = vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__release_sequence;
    vlSelfRef.__VdfgRegularize_h52e72c00_0_4 = ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__restoring)) 
                                                & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__clean));
}

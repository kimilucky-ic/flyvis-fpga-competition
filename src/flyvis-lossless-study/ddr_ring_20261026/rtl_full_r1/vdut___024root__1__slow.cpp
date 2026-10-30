// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See vdut.h for the primary calling header

#include "vdut__pch.h"

VL_ATTR_COLD void Vdut___024root___stl_sequent__TOP__2(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___stl_sequent__TOP__2\n"); );
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
    // Body
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
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_high 
        = (0x0007ffffffffffffULL & (((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[4U][2U])) 
                                     << 0x00000027U) 
                                    | (((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[4U][1U])) 
                                        << 7U) | ((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[4U][0U])) 
                                                  >> 0x00000019U))));
    if (VL_LTES_III(32, 0U, VL_EXTENDS_II(32,11, (0x000007ffU 
                                                  & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[4U][2U] 
                                                     >> 0x00000012U))))) {
        if ((0x00400000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[4U][2U])) {
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__x 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_high;
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__q 
                = VL_SHIFTR_QQI(51,51,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__x, 0x00000010U);
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__q 
                = ((0x0007fffffffffffeULL & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__q) 
                   | (IData)((IData)((1U & ((IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__q) 
                                            | (0U != 
                                               (0x0007ffffffffffffULL 
                                                & VL_SHIFTL_QQI(51,51,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__x, 0x00000023U))))))));
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__Vfuncout 
                = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__q;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_high 
                = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__Vfuncout;
        }
        if ((0x00800000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[4U][2U])) {
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__x 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_high;
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__q 
                = VL_SHIFTR_QQI(51,51,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__x, 0x00000020U);
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__q 
                = ((0x0007fffffffffffeULL & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__q) 
                   | (IData)((IData)((1U & ((IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__q) 
                                            | (0U != 
                                               (0x0007ffffffffffffULL 
                                                & VL_SHIFTL_QQI(51,51,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__x, 0x00000013U))))))));
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__Vfuncout 
                = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__q;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_high 
                = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__Vfuncout;
        }
        if ((0x01000000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[4U][2U])) {
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__x 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_high;
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__q 
                = (QData)((IData)((0U != vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__x)));
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__Vfuncout 
                = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__q;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_high 
                = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__Vfuncout;
        }
        if ((0x02000000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[4U][2U])) {
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__x 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_high;
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__q 
                = (QData)((IData)((0U != vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__x)));
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__Vfuncout 
                = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__q;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_high 
                = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__Vfuncout;
        }
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_low 
        = (0x0007fffffffffff8ULL & (((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[3U][5U])) 
                                     << 0x00000030U) 
                                    | (((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[3U][4U])) 
                                        << 0x00000010U) 
                                       | (0x0000fffffffffff8ULL 
                                          & ((QData)((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[3U][3U])) 
                                             >> 0x00000010U)))));
    if (VL_GTS_III(32, 0U, VL_EXTENDS_II(32,11, (0x000007ffU 
                                                 & (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[3U][2U] 
                                                    >> 0x00000012U))))) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_low 
            = (0x0007ffffffffffffULL & VL_SHIFTL_QQI(51,51,11, vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_low, 
                                                     (0x000007ffU 
                                                      & (- 
                                                         ((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[3U][2U] 
                                                           << 0x0000000eU) 
                                                          | (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[3U][2U] 
                                                             >> 0x00000012U))))));
    } else {
        if ((0x00040000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[3U][2U])) {
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__x 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_low;
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q 
                = VL_SHIFTR_QQI(51,51,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__x, 1U);
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q 
                = ((0x0007fffffffffffeULL & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q) 
                   | (IData)((IData)((1U & ((IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q) 
                                            | (0U != 
                                               (0x0007ffffffffffffULL 
                                                & VL_SHIFTL_QQI(51,51,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__x, 0x00000032U))))))));
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__Vfuncout 
                = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_low 
                = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__Vfuncout;
        }
        if ((0x00080000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[3U][2U])) {
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__x 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_low;
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q 
                = VL_SHIFTR_QQI(51,51,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__x, 2U);
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q 
                = ((0x0007fffffffffffeULL & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q) 
                   | (IData)((IData)((1U & ((IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q) 
                                            | (0U != 
                                               (0x0007ffffffffffffULL 
                                                & VL_SHIFTL_QQI(51,51,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__x, 0x00000031U))))))));
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__Vfuncout 
                = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_low 
                = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__Vfuncout;
        }
        if ((0x00100000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[3U][2U])) {
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__x 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_low;
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q 
                = VL_SHIFTR_QQI(51,51,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__x, 4U);
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q 
                = ((0x0007fffffffffffeULL & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q) 
                   | (IData)((IData)((1U & ((IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q) 
                                            | (0U != 
                                               (0x0007ffffffffffffULL 
                                                & VL_SHIFTL_QQI(51,51,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__x, 0x0000002fU))))))));
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__Vfuncout 
                = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_low 
                = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__Vfuncout;
        }
        if ((0x00200000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[3U][2U])) {
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__x 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_low;
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q 
                = VL_SHIFTR_QQI(51,51,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__x, 8U);
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q 
                = ((0x0007fffffffffffeULL & vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q) 
                   | (IData)((IData)((1U & ((IData)(vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q) 
                                            | (0U != 
                                               (0x0007ffffffffffffULL 
                                                & VL_SHIFTL_QQI(51,51,32, vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__x, 0x0000002bU))))))));
            vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__Vfuncout 
                = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q;
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_low 
                = vlSelfRef.__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__Vfuncout;
        }
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
}

VL_ATTR_COLD void Vdut___024root___stl_sequent__TOP__3(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___stl_sequent__TOP__3\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    SData/*15:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pipe_dst;
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pipe_dst = 0;
    CData/*7:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__lower_delta;
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__lower_delta = 0;
    CData/*7:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_last_v;
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_last_v = 0;
    // Body
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
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_state_ready 
        = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__active) 
           & ((0x40U > (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count)) 
              & ((0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors)) 
                 & ((2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase)) 
                    & (0x0000b265U > vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count)))));
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
}

VL_ATTR_COLD void Vdut___024root___stl_sequent__TOP__4(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___stl_sequent__TOP__4\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*5:0*/ flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__upper_j;
    flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__upper_j = 0;
    // Body
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
}

VL_ATTR_COLD void Vdut___024root___stl_sequent__TOP__5(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___stl_sequent__TOP__5\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
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
    vlSelfRef.flyvis_ddr_soc_ip__DOT__wr_fire = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__aw_pending) 
                                                 & ((~ (IData)(vlSelfRef.s_axi_bvalid)) 
                                                    & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__w_pending)));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_cfg_ready 
        = ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__configured)) 
           & ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__active)) 
              & (0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__release_ready 
        = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__configured) 
           & ((0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors)) 
              & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__release_cookie 
                  == vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__session_cookie) 
                 & ((vlSelfRef.flyvis_ddr_soc_ip__DOT__release_sequence 
                     >= vlSelfRef.flyvis_ddr_soc_ip__DOT__released) 
                    & (vlSelfRef.flyvis_ddr_soc_ip__DOT__release_sequence 
                       <= vlSelfRef.flyvis_ddr_soc_ip__DOT__committed)))));
    vlSelfRef.__VdfgRegularize_h52e72c00_0_4 = ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__restoring)) 
                                                & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__clean));
    vlSelfRef.__VdfgRegularize_h52e72c00_0_3 = ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__active)) 
                                                & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__configured));
    vlSelfRef.__VdfgRegularize_h52e72c00_0_7 = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__inflight) 
                                                | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__restoring));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__pop 
        = ((IData)(vlSelfRef.m_axi_wvalid) & ((IData)(vlSelfRef.m_axi_wready) 
                                              & (4U 
                                                 != (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))));
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
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__ai 
        = (IData)(((0x7f800000U == (0x7f800000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_a)) 
                   & (~ (0U != (0x007fffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_a)))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__an 
        = (IData)(((0x7f800000U == (0x7f800000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_a)) 
                   & (0U != (0x007fffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_a))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__bn 
        = (IData)(((0x7f800000U == (0x7f800000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_b)) 
                   & (0U != (0x007fffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_b))));
}

VL_ATTR_COLD void Vdut___024root___stl_sequent__TOP__6(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___stl_sequent__TOP__6\n"); );
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
    // Body
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__bi 
        = (IData)(((0x7f800000U == (0x7f800000U & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_b)) 
                   & (~ (0U != (0x007fffffU & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_b)))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT____Vcellinp__network__input_valid 
        = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__inflight) 
           & ((2U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__feed)) 
              & (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_5)));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr_data 
        = (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q
           [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__selected] 
           & (- (IData)((0x2cU >= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__selected)))));
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
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_data 
        = (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q
           [vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__selected] 
           & (- (IData)((0x2cU >= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__selected)))));
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
    vlSelfRef.flyvis_ddr_soc_ip__DOT__control_busy 
        = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__running) 
           | (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_7));
    vlSelfRef.__VdfgRegularize_h52e72c00_0_9 = ((~ (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_7)) 
                                                & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__clean));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__restore_ready 
        = ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__configured)) 
           & ((~ (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_7)) 
              & (0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors))));
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
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_a 
        = (((vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_data 
             >> 0x0000001fU) | (0U == (0x7fffffffU 
                                       & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_data)))
            ? 0U : vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_data);
    if ((9U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase))) {
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
    }
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_begin_ready 
        = ((IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_3) 
           & ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__full)) 
              & (0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors))));
    vlSelfRef.flyvis_ddr_soc_ip__DOT__begin_ready = 
        ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_begin_ready) 
         & (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_9));
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

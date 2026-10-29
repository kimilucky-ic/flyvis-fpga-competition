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
    vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__pop 
        = ((IData)(vlSelfRef.m_axi_wvalid) & ((IData)(vlSelfRef.m_axi_wready) 
                                              & (4U 
                                                 != (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))));
}

void Vdut___024root___eval_ico(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_ico\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VicoTriggered[0U])) {
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__pop 
            = ((IData)(vlSelfRef.m_axi_wvalid) & ((IData)(vlSelfRef.m_axi_wready) 
                                                  & (4U 
                                                     != (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase))));
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
                                                    ((IData)(vlSelfRef.aclk) 
                                                     & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__aclk__0)))));
    vlSelfRef.__Vtrigprevexpr___TOP__aclk__0 = vlSelfRef.aclk;
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
    // Body
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__v 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__v;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__v 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__v;
    if (vlSelfRef.aresetn) {
        if (VL_UNLIKELY((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_read) 
                          & VL_LTES_III(32, 0x00001defU, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_address)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: sync_mem.sv:28: Assertion failed in %m: sync read bounds\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.metadata.ordinary", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\sync_mem.sv", 28, "", false);
        }
        if (VL_UNLIKELY((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vcellinp__stimulus_ram__re) 
                          & VL_LTES_III(32, 0x000002d1U, 
                                        (0x000003ffU 
                                         & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: sync_mem.sv:28: Assertion failed in %m: sync read bounds\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.stimulus_ram.ordinary", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\sync_mem.sv", 28, "", false);
        }
        if (VL_UNLIKELY((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vcellinp__stimulus_ram__we) 
                          & VL_LTES_III(32, 0x000002d1U, 
                                        (0x000003ffU 
                                         & vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__input_index)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: sync_mem.sv:29: Assertion failed in %m: sync write bounds\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.stimulus_ram.ordinary", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\sync_mem.sv", 29, "", false);
        }
    }
    if (((IData)(vlSelfRef.aresetn) & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__advance))) {
        if (VL_UNLIKELY((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_read) 
                          & VL_LTES_III(32, 0x0000003eU, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rows_addr)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: sync_mem.sv:28: Assertion failed in %m: sync read bounds\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen.rows.ordinary", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\sync_mem.sv", 28, "", false);
        }
        if (VL_UNLIKELY((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_read) 
                          & VL_LTES_III(32, 0x0000003eU, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_rows_addr)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: sync_mem.sv:28: Assertion failed in %m: sync read bounds\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen.target_rows.ordinary", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\sync_mem.sv", 28, "", false);
        }
        if (VL_UNLIKELY((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__map_read) 
                          & VL_LTES_III(32, 0x00000782U, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__map_address)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: sync_mem.sv:28: Assertion failed in %m: sync read bounds\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.gen.maps.ordinary", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\sync_mem.sv", 28, "", false);
        }
    }
    if (vlSelfRef.aresetn) {
        if (VL_UNLIKELY((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr) 
                          & VL_LTES_III(32, 0x0000b265U, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr_addr)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: sync_mem.sv:13: Assertion failed in %m: banked read bounds\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.current_ram.wide_banked", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\sync_mem.sv", 13, "", false);
        }
        if (VL_UNLIKELY((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
                          & VL_LTES_III(32, 0x0000b265U, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: sync_mem.sv:14: Assertion failed in %m: banked write bounds\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.current_ram.wide_banked", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\sync_mem.sv", 14, "", false);
        }
        if (VL_UNLIKELY((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar) 
                          & VL_LTES_III(32, 0x0000b265U, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_addr)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: sync_mem.sv:13: Assertion failed in %m: banked read bounds\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.state_ram.wide_banked", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\sync_mem.sv", 13, "", false);
        }
        if (VL_UNLIKELY((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
                          & VL_LTES_III(32, 0x0000b265U, (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: sync_mem.sv:14: Assertion failed in %m: banked write bounds\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.network.state_ram.wide_banked", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\sync_mem.sv", 14, "", false);
        }
        if (VL_UNLIKELY((((vlSelfRef.flyvis_ddr_soc_ip__DOT__released 
                           > vlSelfRef.flyvis_ddr_soc_ip__DOT__committed) 
                          | ((vlSelfRef.flyvis_ddr_soc_ip__DOT__committed 
                              - vlSelfRef.flyvis_ddr_soc_ip__DOT__released) 
                             > (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__slots)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: snapshot_axi_writer.sv:213: Assertion failed in %m: Ring ownership invariant\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.journal", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\snapshot_axi_writer.sv", 213, "", false);
        }
        if (VL_UNLIKELY(((0x40U < (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: snapshot_axi_writer.sv:214: Assertion failed in %m: FIFO overflow\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.journal", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\snapshot_axi_writer.sv", 214, "", false);
        }
        if (VL_UNLIKELY((((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__pop) 
                          & (0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: snapshot_axi_writer.sv:215: Assertion failed in %m: FIFO underflow\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.journal", 'T',-12
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
            VL_WRITEF_NX("[%0t] %%Fatal: snapshot_axi_writer.sv:216: Assertion failed in %m: AXI4KiB boundary\n",3, 'M',vlSymsp->name(),"flyvis_ddr_soc_ip.engine.journal", 'T',-12
                         , '#',64,VL_TIME_UNITED_Q(1));
            VL_STOP_MT("C:\\Users\\hzy72\\Documents\\ChatGPT\\fpga\\flyvis_runtime\\fpga\\flyvis-lossless-study\\ddr_ring_20261026\\rtl\\snapshot_axi_writer.sv", 216, "", false);
        }
    }
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__mem__v0 = 0U;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__feed_index 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__feed_index;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__feed 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__feed;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__cycles 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__cycles;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__stimulus_ram__DOT__ordinary__DOT__mem__v0 = 0U;
}

void Vdut___024root___nba_sequent__TOP__1(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__1\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d__v1 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d__v2 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d__v3 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d__v4 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d__v5 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d__v16 = 0U;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_pending 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_pending;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_end 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_end;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_step 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_step;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_rank 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_rank;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__next_eid 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__next_eid;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_end 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_end;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sbase 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sbase;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tbase 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tbase;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_weight 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_weight;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rank_first 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rank_first;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__bounds_q 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__bounds_q;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sn__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tn__v0 = 0U;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r__v0 = 0U;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_first 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_first;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_vfirst 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_vfirst;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_nonempty 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_nonempty;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_tag 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_tag;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_ready 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_ready;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u_last 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u_last;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j_step 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j_step;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v1 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v2 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v3 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v4 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v5 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v6 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v7 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v8 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v9 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v10 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v46 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v48 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v50 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v52 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v54 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v56 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v58 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v60 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v62 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v64 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v66 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v68 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v70 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v72 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v74 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v76 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v78 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d__v80 = 0U;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__edges 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__edges;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__states 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__states;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__input_index 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__input_index;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_count 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_count;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__load_slot 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__load_slot;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__batch_count 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__batch_count;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__received 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__received;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__desc__v0 = 0U;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v1 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v2 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v3 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v4 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v5 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v6 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v7 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v8 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v9 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v10 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v11 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v12 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v13 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v14 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v15 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v16 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v17 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v18 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v19 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v20 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v21 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v1 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v2 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v3 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v4 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v5 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v6 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v7 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v8 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v9 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v10 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v11 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v12 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v13 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v14 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v15 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v16 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v17 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v18 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v19 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v20 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v21 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v22 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v11 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v12 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v1 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v2 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v3 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v4 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v5 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v6 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v7 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v8 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v9 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v10 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v11 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v12 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v13 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v14 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v15 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v16 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v17 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v18 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v19 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v20 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v21 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_old__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v0 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v1 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v3 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v5 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v7 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v9 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v11 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v13 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v15 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v17 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v19 = 0U;
    vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v21 = 0U;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id;
    vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv 
        = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv;
}

void Vdut___024root___nba_sequent__TOP__2(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__2\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
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
}

void Vdut___024root___nba_sequent__TOP__3(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__3\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.aresetn) {
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__v 
            = ((0x00001ffeU & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__v) 
                               << 1U)) | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_valid));
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__v 
            = ((0x000000feU & ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__v) 
                               << 1U)) | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_valid));
        if (((IData)(vlSelfRef.s_axi_rvalid) & (IData)(vlSelfRef.s_axi_rready))) {
            vlSelfRef.s_axi_rvalid = 0U;
        }
        if (((IData)(vlSelfRef.s_axi_arvalid) & (IData)(vlSelfRef.s_axi_arready))) {
            vlSelfRef.s_axi_rvalid = 1U;
        }
        if (vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__pop) {
            vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__rp 
                = (0x0000003fU & ((IData)(1U) + (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__rp)));
        }
        if (((IData)(vlSelfRef.s_axi_bvalid) & (IData)(vlSelfRef.s_axi_bready))) {
            vlSelfRef.s_axi_bvalid = 0U;
        }
        if (vlSelfRef.flyvis_ddr_soc_ip__DOT__wr_fire) {
            vlSelfRef.s_axi_bvalid = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x0400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x0800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x0c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x1000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x1400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x1800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x1c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x2000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x2400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x2800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x2c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x3000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x3400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x3800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x3c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x4000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x4400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__mem__v0 = 1U;
        }
    } else {
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__v = 0U;
        vlSelfRef.__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__v = 0U;
        vlSelfRef.s_axi_rvalid = 0U;
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__rp = 0U;
        vlSelfRef.s_axi_bvalid = 0U;
    }
}

void Vdut___024root___nba_sequent__TOP__4(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__4\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.aresetn) {
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x4800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x4c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x5000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x5400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x5800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x5c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x6000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x6400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x6800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x6c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x7000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x7400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x7800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x7c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x8000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x8400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x8800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x8c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x9000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x9400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x9800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0x9c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0xa000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0xa400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__mem__v0 = 1U;
        }
    }
}

void Vdut___024root___nba_sequent__TOP__5(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__5\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.aresetn) {
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0xa800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0xac00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw) 
             & (0xb000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x0400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x0800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x0c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x1000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x1400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x1800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x1c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x2000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x2400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x2800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x2c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x3000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x3400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x3800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x3c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x4000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x4400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x4800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x4c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x5000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__mem__v0 = 1U;
        }
    }
}

void Vdut___024root___nba_sequent__TOP__6(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___nba_sequent__TOP__6\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.aresetn) {
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x5400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x5800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x5c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x6000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x6400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x6800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x6c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x7000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x7400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x7800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x7c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x8000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x8400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x8800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x8c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x9000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x9400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x9800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0x9c00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0xa000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0xa400U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0xa800U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0xac00U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__mem__v0 = 1U;
        }
        if (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw) 
             & (0xb000U == (0xfc00U & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr))))) {
            vlSelfRef.__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__mem__v0 
                = vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data;
            vlSelfRef.__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__mem__v0 
                = (0x000003ffU & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr));
            vlSelfRef.__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__mem__v0 = 1U;
        }
    }
}

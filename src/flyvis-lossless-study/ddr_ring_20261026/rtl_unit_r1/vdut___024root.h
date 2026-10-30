// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See vdut.h for the primary calling header

#ifndef VERILATED_VDUT___024ROOT_H_
#define VERILATED_VDUT___024ROOT_H_  // guard

#include "verilated.h"


class Vdut__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vdut___024root final {
  public:

    // DESIGN SPECIFIC STATE
    // Anonymous structures to workaround compiler member-count bugs
    struct {
        VL_IN8(clk,0,0);
        VL_IN8(reset,0,0);
        VL_IN8(cfg_valid,0,0);
        VL_OUT8(cfg_ready,0,0);
        VL_IN8(release_valid,0,0);
        VL_OUT8(release_ready,0,0);
        VL_IN8(begin_valid,0,0);
        VL_OUT8(begin_ready,0,0);
        VL_OUT8(configured,0,0);
        VL_OUT8(active,0,0);
        VL_OUT8(capacity_exhausted,0,0);
        VL_IN8(input_valid,0,0);
        VL_OUT8(input_ready,0,0);
        VL_IN8(state_valid,0,0);
        VL_OUT8(state_ready,0,0);
        VL_IN8(state_last,0,0);
        VL_IN8(info_valid,0,0);
        VL_OUT8(publish,0,0);
        VL_OUT8(error_flags,7,0);
        VL_OUT8(m_axi_awlen,7,0);
        VL_OUT8(m_axi_awsize,2,0);
        VL_OUT8(m_axi_awburst,1,0);
        VL_OUT8(m_axi_awvalid,0,0);
        VL_IN8(m_axi_awready,0,0);
        VL_OUT8(m_axi_wstrb,7,0);
        VL_OUT8(m_axi_wlast,0,0);
        VL_OUT8(m_axi_wvalid,0,0);
        VL_IN8(m_axi_wready,0,0);
        VL_IN8(m_axi_bresp,1,0);
        VL_IN8(m_axi_bvalid,0,0);
        VL_OUT8(m_axi_bready,0,0);
        CData/*2:0*/ snapshot_axi_writer__DOT__phase;
        CData/*1:0*/ snapshot_axi_writer__DOT__bus;
        CData/*0:0*/ snapshot_axi_writer__DOT__sequence_exhausted;
        CData/*5:0*/ snapshot_axi_writer__DOT__wp;
        CData/*5:0*/ snapshot_axi_writer__DOT__rp;
        CData/*6:0*/ snapshot_axi_writer__DOT__count;
        CData/*0:0*/ snapshot_axi_writer__DOT__half;
        CData/*0:0*/ snapshot_axi_writer__DOT__got_info;
        CData/*4:0*/ snapshot_axi_writer__DOT__burst_beats;
        CData/*4:0*/ snapshot_axi_writer__DOT__beat;
        CData/*6:0*/ snapshot_axi_writer__DOT__timeout_count;
        CData/*0:0*/ snapshot_axi_writer__DOT__push;
        CData/*0:0*/ snapshot_axi_writer__DOT__pop;
        CData/*0:0*/ snapshot_axi_writer__DOT__accept_word;
        CData/*0:0*/ snapshot_axi_writer__DOT__last_word;
        CData/*4:0*/ __Vfunc_snapshot_axi_writer__DOT__header_word__0__index;
        CData/*0:0*/ __VdfgRegularize_h52e72c00_0_1;
        CData/*0:0*/ __Vdly__active;
        CData/*2:0*/ __Vdly__snapshot_axi_writer__DOT__phase;
        CData/*1:0*/ __Vdly__snapshot_axi_writer__DOT__bus;
        CData/*6:0*/ __Vdly__snapshot_axi_writer__DOT__count;
        CData/*0:0*/ __Vdly__snapshot_axi_writer__DOT__half;
        CData/*0:0*/ __Vdly__snapshot_axi_writer__DOT__got_info;
        CData/*7:0*/ __Vdly__error_flags;
        CData/*4:0*/ __Vdly__snapshot_axi_writer__DOT__burst_beats;
        CData/*4:0*/ __Vdly__snapshot_axi_writer__DOT__beat;
        CData/*6:0*/ __Vdly__snapshot_axi_writer__DOT__timeout_count;
        CData/*0:0*/ __VstlFirstIteration;
        CData/*0:0*/ __VstlPhaseResult;
        CData/*0:0*/ __VicoFirstIteration;
        CData/*0:0*/ __VicoPhaseResult;
        CData/*0:0*/ __Vtrigprevexpr___TOP__clk__0;
        CData/*0:0*/ __VactPhaseResult;
    };
    struct {
        CData/*0:0*/ __VnbaPhaseResult;
        VL_IN16(cfg_slots,15,0);
        VL_IN16(state_id,15,0);
        SData/*15:0*/ snapshot_axi_writer__DOT__slots;
        SData/*15:0*/ snapshot_axi_writer__DOT__write_slot;
        SData/*15:0*/ __Vdly__snapshot_axi_writer__DOT__write_slot;
        VL_IN(cfg_base,31,0);
        VL_IN(cfg_end,31,0);
        VL_IN(cfg_first_frame,31,0);
        VL_IN(cfg_cookie,31,0);
        VL_IN(release_sequence,31,0);
        VL_IN(release_cookie,31,0);
        VL_OUT(released_count,31,0);
        VL_IN(input_bits,31,0);
        VL_IN(state_bits,31,0);
        VL_IN(info_cycles,31,0);
        VL_IN(info_edges,31,0);
        VL_IN(info_states,31,0);
        VL_IN(info_faults,31,0);
        VL_OUT(published_base,31,0);
        VL_OUT(published_frame,31,0);
        VL_OUT(committed_count,31,0);
        VL_OUT(m_axi_awaddr,31,0);
        IData/*31:0*/ snapshot_axi_writer__DOT__record_base;
        IData/*31:0*/ snapshot_axi_writer__DOT__end_address;
        IData/*31:0*/ snapshot_axi_writer__DOT__frame_id;
        IData/*31:0*/ snapshot_axi_writer__DOT__acked_beats;
        IData/*31:0*/ snapshot_axi_writer__DOT__ring_base;
        IData/*31:0*/ snapshot_axi_writer__DOT__session_cookie;
        IData/*31:0*/ snapshot_axi_writer__DOT__low_word;
        IData/*31:0*/ snapshot_axi_writer__DOT__input_count;
        IData/*31:0*/ snapshot_axi_writer__DOT__state_count;
        IData/*31:0*/ snapshot_axi_writer__DOT__input_hash;
        IData/*31:0*/ snapshot_axi_writer__DOT__state_hash;
        IData/*31:0*/ snapshot_axi_writer__DOT__saved_cycles;
        IData/*31:0*/ snapshot_axi_writer__DOT__saved_edges;
        IData/*31:0*/ snapshot_axi_writer__DOT__saved_states;
        IData/*31:0*/ snapshot_axi_writer__DOT__saved_faults;
        IData/*31:0*/ snapshot_axi_writer__DOT__word_bits;
        IData/*31:0*/ __Vdly__snapshot_axi_writer__DOT__record_base;
        IData/*31:0*/ __Vdly__snapshot_axi_writer__DOT__frame_id;
        IData/*31:0*/ __Vdly__committed_count;
        IData/*31:0*/ __Vdly__snapshot_axi_writer__DOT__acked_beats;
        IData/*31:0*/ __Vdly__snapshot_axi_writer__DOT__input_count;
        IData/*31:0*/ __Vdly__snapshot_axi_writer__DOT__state_count;
        IData/*31:0*/ __Vdly__snapshot_axi_writer__DOT__input_hash;
        IData/*31:0*/ __Vdly__snapshot_axi_writer__DOT__state_hash;
        IData/*31:0*/ __VactIterCount;
        VL_OUT64(m_axi_wdata,63,0);
        QData/*63:0*/ snapshot_axi_writer__DOT____VlemCall_0__header_word;
        VlUnpacked<QData/*63:0*/, 64> snapshot_axi_writer__DOT__fifo_data;
        VlUnpacked<CData/*7:0*/, 64> snapshot_axi_writer__DOT__fifo_strb;
        VlUnpacked<QData/*63:0*/, 1> __VstlTriggered;
        VlUnpacked<QData/*63:0*/, 1> __VicoTriggered;
        VlUnpacked<QData/*63:0*/, 1> __VactTriggered;
        VlUnpacked<QData/*63:0*/, 1> __VnbaTriggered;
    };

    // INTERNAL VARIABLES
    Vdut__Syms* vlSymsp;
    const char* vlNamep;

    // CONSTRUCTORS
    Vdut___024root(Vdut__Syms* symsp, const char* namep);
    ~Vdut___024root();
    VL_UNCOPYABLE(Vdut___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard

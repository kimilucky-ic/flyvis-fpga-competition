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
    VL_IN8(rst_n,0,0);
    VL_IN8(cam_pclk,0,0);
    VL_IN8(cam_vsync,0,0);
    VL_IN8(cam_href,0,0);
    VL_IN8(cam_data,7,0);
    VL_OUT8(cam_rst_n,0,0);
    VL_OUT8(cam_pwdn,0,0);
    VL_OUT8(cmos_frame_clk,0,0);
    VL_OUT8(cmos_frame_ce,0,0);
    VL_OUT8(cmos_frame_vsync,0,0);
    VL_OUT8(cmos_frame_href,0,0);
    VL_OUT8(cmos_active_video,0,0);
    CData/*0:0*/ cmos_capture_data__DOT__rst_n_d0;
    CData/*0:0*/ cmos_capture_data__DOT__rst_n_syn;
    CData/*0:0*/ cmos_capture_data__DOT__cam_vsync_d0;
    CData/*0:0*/ cmos_capture_data__DOT__cam_vsync_d1;
    CData/*0:0*/ cmos_capture_data__DOT__cam_href_d0;
    CData/*0:0*/ cmos_capture_data__DOT__cam_href_d1;
    CData/*3:0*/ cmos_capture_data__DOT__cmos_ps_cnt;
    CData/*0:0*/ cmos_capture_data__DOT__wait_done;
    CData/*0:0*/ cmos_capture_data__DOT__byte_flag;
    CData/*7:0*/ cmos_capture_data__DOT__cam_data_d0;
    CData/*0:0*/ cmos_capture_data__DOT__byte_flag_d0;
    CData/*0:0*/ cmos_capture_data__DOT__pos_vsync;
    CData/*0:0*/ __VstlFirstIteration;
    CData/*0:0*/ __VstlPhaseResult;
    CData/*0:0*/ __VicoFirstIteration;
    CData/*0:0*/ __VicoPhaseResult;
    CData/*0:0*/ __Vtrigprevexpr___TOP__cam_pclk__0;
    CData/*0:0*/ __Vtrigprevexpr___TOP__rst_n__0;
    CData/*0:0*/ __Vtrigprevexpr___TOP__cmos_capture_data__DOT__rst_n_syn__0;
    CData/*0:0*/ __VactPhaseResult;
    CData/*0:0*/ __VnbaPhaseResult;
    SData/*15:0*/ cmos_capture_data__DOT__cmos_data_16b;
    VL_OUT(cmos_frame_data,23,0);
    IData/*31:0*/ __VactIterCount;
    VlUnpacked<QData/*63:0*/, 1> __VstlTriggered;
    VlUnpacked<QData/*63:0*/, 1> __VicoTriggered;
    VlUnpacked<QData/*63:0*/, 1> __VactTriggered;
    VlUnpacked<QData/*63:0*/, 1> __VnbaTriggered;

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

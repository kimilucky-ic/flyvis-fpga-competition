// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Model implementation (design independent parts)

#include "vdut__pch.h"

//============================================================
// Constructors

Vdut::Vdut(VerilatedContext* _vcontextp__, const char* _vcname__)
    : VerilatedModel{*_vcontextp__}
    , vlSymsp{new Vdut__Syms(contextp(), _vcname__, this)}
    , rst_n{vlSymsp->TOP.rst_n}
    , cam_pclk{vlSymsp->TOP.cam_pclk}
    , cam_vsync{vlSymsp->TOP.cam_vsync}
    , cam_href{vlSymsp->TOP.cam_href}
    , cam_data{vlSymsp->TOP.cam_data}
    , cam_rst_n{vlSymsp->TOP.cam_rst_n}
    , cam_pwdn{vlSymsp->TOP.cam_pwdn}
    , cmos_frame_clk{vlSymsp->TOP.cmos_frame_clk}
    , cmos_frame_ce{vlSymsp->TOP.cmos_frame_ce}
    , cmos_frame_vsync{vlSymsp->TOP.cmos_frame_vsync}
    , cmos_frame_href{vlSymsp->TOP.cmos_frame_href}
    , cmos_active_video{vlSymsp->TOP.cmos_active_video}
    , cmos_frame_data{vlSymsp->TOP.cmos_frame_data}
    , rootp{&(vlSymsp->TOP)}
{
    // Register model with the context
    contextp()->addModel(this);
}

Vdut::Vdut(const char* _vcname__)
    : Vdut(Verilated::threadContextp(), _vcname__)
{
}

//============================================================
// Destructor

Vdut::~Vdut() {
    delete vlSymsp;
}

//============================================================
// Evaluation function

#ifdef VL_DEBUG
void Vdut___024root___eval_debug_assertions(Vdut___024root* vlSelf);
#endif  // VL_DEBUG
void Vdut___024root___eval_static(Vdut___024root* vlSelf);
void Vdut___024root___eval_initial(Vdut___024root* vlSelf);
void Vdut___024root___eval_settle(Vdut___024root* vlSelf);
void Vdut___024root___eval(Vdut___024root* vlSelf);

void Vdut::eval_step() {
    VL_DEBUG_IF(VL_DBG_MSGF("+++++TOP Evaluate Vdut::eval_step\n"); );
#ifdef VL_DEBUG
    // Debug assertions
    Vdut___024root___eval_debug_assertions(&(vlSymsp->TOP));
#endif  // VL_DEBUG
    vlSymsp->__Vm_deleter.deleteAll();
    if (VL_UNLIKELY(!vlSymsp->__Vm_didInit)) {
        VL_DEBUG_IF(VL_DBG_MSGF("+ Initial\n"););
        Vdut___024root___eval_static(&(vlSymsp->TOP));
        Vdut___024root___eval_initial(&(vlSymsp->TOP));
        Vdut___024root___eval_settle(&(vlSymsp->TOP));
        vlSymsp->__Vm_didInit = true;
    }
    VL_DEBUG_IF(VL_DBG_MSGF("+ Eval\n"););
    Vdut___024root___eval(&(vlSymsp->TOP));
    // Evaluate cleanup
    Verilated::endOfEval(vlSymsp->__Vm_evalMsgQp);
}

//============================================================
// Events and timing
bool Vdut::eventsPending() { return false; }

uint64_t Vdut::nextTimeSlot() {
    VL_FATAL_MT(__FILE__, __LINE__, "", "No delays in the design");
    return 0;
}

//============================================================
// Utilities

const char* Vdut::name() const {
    return vlSymsp->name();
}

//============================================================
// Invoke final blocks

void Vdut___024root___eval_final(Vdut___024root* vlSelf);

VL_ATTR_COLD void Vdut::final() {
    contextp()->executingFinal(true);
    Vdut___024root___eval_final(&(vlSymsp->TOP));
    contextp()->executingFinal(false);
}

//============================================================
// Implementations of abstract methods from VerilatedModel

const char* Vdut::hierName() const { return vlSymsp->name(); }
const char* Vdut::modelName() const { return "Vdut"; }
unsigned Vdut::threads() const { return 1; }
void Vdut::prepareClone() const { contextp()->prepareClone(); }
void Vdut::atClone() const {
    contextp()->threadPoolpOnClone();
}

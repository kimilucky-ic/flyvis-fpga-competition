// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Model implementation (design independent parts)

#include "vdut__pch.h"

//============================================================
// Constructors

Vdut::Vdut(VerilatedContext* _vcontextp__, const char* _vcname__)
    : VerilatedModel{*_vcontextp__}
    , vlSymsp{new Vdut__Syms(contextp(), _vcname__, this)}
    , aclk{vlSymsp->TOP.aclk}
    , aresetn{vlSymsp->TOP.aresetn}
    , s_axi_awprot{vlSymsp->TOP.s_axi_awprot}
    , s_axi_awvalid{vlSymsp->TOP.s_axi_awvalid}
    , s_axi_awready{vlSymsp->TOP.s_axi_awready}
    , s_axi_wstrb{vlSymsp->TOP.s_axi_wstrb}
    , s_axi_wvalid{vlSymsp->TOP.s_axi_wvalid}
    , s_axi_wready{vlSymsp->TOP.s_axi_wready}
    , s_axi_bresp{vlSymsp->TOP.s_axi_bresp}
    , s_axi_bvalid{vlSymsp->TOP.s_axi_bvalid}
    , s_axi_bready{vlSymsp->TOP.s_axi_bready}
    , s_axi_arprot{vlSymsp->TOP.s_axi_arprot}
    , s_axi_arvalid{vlSymsp->TOP.s_axi_arvalid}
    , s_axi_arready{vlSymsp->TOP.s_axi_arready}
    , s_axi_rresp{vlSymsp->TOP.s_axi_rresp}
    , s_axi_rvalid{vlSymsp->TOP.s_axi_rvalid}
    , s_axi_rready{vlSymsp->TOP.s_axi_rready}
    , m_axi_awid{vlSymsp->TOP.m_axi_awid}
    , m_axi_awlen{vlSymsp->TOP.m_axi_awlen}
    , m_axi_awsize{vlSymsp->TOP.m_axi_awsize}
    , m_axi_awburst{vlSymsp->TOP.m_axi_awburst}
    , m_axi_awlock{vlSymsp->TOP.m_axi_awlock}
    , m_axi_awcache{vlSymsp->TOP.m_axi_awcache}
    , m_axi_awprot{vlSymsp->TOP.m_axi_awprot}
    , m_axi_awqos{vlSymsp->TOP.m_axi_awqos}
    , m_axi_awvalid{vlSymsp->TOP.m_axi_awvalid}
    , m_axi_awready{vlSymsp->TOP.m_axi_awready}
    , m_axi_wstrb{vlSymsp->TOP.m_axi_wstrb}
    , m_axi_wlast{vlSymsp->TOP.m_axi_wlast}
    , m_axi_wvalid{vlSymsp->TOP.m_axi_wvalid}
    , m_axi_wready{vlSymsp->TOP.m_axi_wready}
    , m_axi_bid{vlSymsp->TOP.m_axi_bid}
    , m_axi_bresp{vlSymsp->TOP.m_axi_bresp}
    , m_axi_bvalid{vlSymsp->TOP.m_axi_bvalid}
    , m_axi_bready{vlSymsp->TOP.m_axi_bready}
    , s_axi_awaddr{vlSymsp->TOP.s_axi_awaddr}
    , s_axi_araddr{vlSymsp->TOP.s_axi_araddr}
    , s_axi_wdata{vlSymsp->TOP.s_axi_wdata}
    , s_axi_rdata{vlSymsp->TOP.s_axi_rdata}
    , m_axi_awaddr{vlSymsp->TOP.m_axi_awaddr}
    , m_axi_wdata{vlSymsp->TOP.m_axi_wdata}
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

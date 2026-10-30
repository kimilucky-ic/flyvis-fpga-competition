// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See vdut.h for the primary calling header

#include "vdut__pch.h"

void Vdut___024root___ctor_var_reset(Vdut___024root* vlSelf);

Vdut___024root::Vdut___024root(Vdut__Syms* symsp, const char* namep)
 {
    vlSymsp = symsp;
    vlNamep = strdup(namep);
    // Reset structure values
    Vdut___024root___ctor_var_reset(this);
}

void Vdut___024root::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

Vdut___024root::~Vdut___024root() {
    VL_DO_DANGLING(std::free(const_cast<char*>(vlNamep)), vlNamep);
}

// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table internal header
//
// Internal details; most calling programs do not need this header,
// unless using verilator public meta comments.

#ifndef VERILATED_VDUT__SYMS_H_
#define VERILATED_VDUT__SYMS_H_  // guard

#include "verilated.h"

// INCLUDE MODEL CLASS

#include "vdut.h"

// INCLUDE MODULE CLASSES
#include "vdut___024root.h"

// SYMS CLASS (contains all model state)
class alignas(VL_CACHE_LINE_BYTES) Vdut__Syms final : public VerilatedSyms {
  public:
    // INTERNAL STATE
    Vdut* const __Vm_modelp;
    VlDeleter __Vm_deleter;
    bool __Vm_didInit = false;

    // MODULE INSTANCE STATE
    Vdut___024root                 TOP;

    // CONSTRUCTORS
    Vdut__Syms(VerilatedContext* contextp, const char* namep, Vdut* modelp);
    ~Vdut__Syms();

    // METHODS
    const char* name() const { return TOP.vlNamep; }
};

#endif  // guard

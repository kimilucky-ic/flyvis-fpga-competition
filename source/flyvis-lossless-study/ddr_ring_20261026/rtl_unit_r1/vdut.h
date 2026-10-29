// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Primary model header
//
// This header should be included by all source files instantiating the design.
// The class here is then constructed to instantiate the design.
// See the Verilator manual for examples.

#ifndef VERILATED_VDUT_H_
#define VERILATED_VDUT_H_  // guard

#include "verilated.h"

class Vdut__Syms;
class Vdut___024root;

// This class is the main interface to the Verilated model
class alignas(VL_CACHE_LINE_BYTES) Vdut VL_NOT_FINAL : public VerilatedModel {
  private:
    // Symbol table holding complete model state (owned by this class)
    Vdut__Syms* const vlSymsp;

  public:

    // CONSTEXPR CAPABILITIES
    // Verilated with --trace?
    static constexpr bool traceCapable = false;

    // PORTS
    // The application code writes and reads these signals to
    // propagate new values into/out from the Verilated model.
    VL_IN8(&clk,0,0);
    VL_IN8(&reset,0,0);
    VL_IN8(&cfg_valid,0,0);
    VL_OUT8(&cfg_ready,0,0);
    VL_IN8(&release_valid,0,0);
    VL_OUT8(&release_ready,0,0);
    VL_IN8(&begin_valid,0,0);
    VL_OUT8(&begin_ready,0,0);
    VL_OUT8(&configured,0,0);
    VL_OUT8(&active,0,0);
    VL_OUT8(&capacity_exhausted,0,0);
    VL_IN8(&input_valid,0,0);
    VL_OUT8(&input_ready,0,0);
    VL_IN8(&state_valid,0,0);
    VL_OUT8(&state_ready,0,0);
    VL_IN8(&state_last,0,0);
    VL_IN8(&info_valid,0,0);
    VL_OUT8(&publish,0,0);
    VL_OUT8(&error_flags,7,0);
    VL_OUT8(&m_axi_awlen,7,0);
    VL_OUT8(&m_axi_awsize,2,0);
    VL_OUT8(&m_axi_awburst,1,0);
    VL_OUT8(&m_axi_awvalid,0,0);
    VL_IN8(&m_axi_awready,0,0);
    VL_OUT8(&m_axi_wstrb,7,0);
    VL_OUT8(&m_axi_wlast,0,0);
    VL_OUT8(&m_axi_wvalid,0,0);
    VL_IN8(&m_axi_wready,0,0);
    VL_IN8(&m_axi_bresp,1,0);
    VL_IN8(&m_axi_bvalid,0,0);
    VL_OUT8(&m_axi_bready,0,0);
    VL_IN16(&cfg_slots,15,0);
    VL_IN16(&state_id,15,0);
    VL_IN(&cfg_base,31,0);
    VL_IN(&cfg_end,31,0);
    VL_IN(&cfg_first_frame,31,0);
    VL_IN(&cfg_cookie,31,0);
    VL_IN(&release_sequence,31,0);
    VL_IN(&release_cookie,31,0);
    VL_OUT(&released_count,31,0);
    VL_IN(&input_bits,31,0);
    VL_IN(&state_bits,31,0);
    VL_IN(&info_cycles,31,0);
    VL_IN(&info_edges,31,0);
    VL_IN(&info_states,31,0);
    VL_IN(&info_faults,31,0);
    VL_OUT(&published_base,31,0);
    VL_OUT(&published_frame,31,0);
    VL_OUT(&committed_count,31,0);
    VL_OUT(&m_axi_awaddr,31,0);
    VL_OUT64(&m_axi_wdata,63,0);

    // CELLS
    // Public to allow access to /* verilator public */ items.
    // Otherwise the application code can consider these internals.

    // Root instance pointer to allow access to model internals,
    // including inlined /* verilator public_flat_* */ items.
    Vdut___024root* const rootp;

    // CONSTRUCTORS
    /// Construct the model; called by application code
    /// If contextp is null, then the model will use the default global context
    /// If name is "", then makes a wrapper with a
    /// single model invisible with respect to DPI scope names.
    explicit Vdut(VerilatedContext* contextp, const char* name = "TOP");
    explicit Vdut(const char* name = "TOP");
    /// Destroy the model; called (often implicitly) by application code
    virtual ~Vdut();
  private:
    VL_UNCOPYABLE(Vdut);  ///< Copying not allowed

  public:
    // API METHODS
    /// Evaluate the model.  Application must call when inputs change.
    void eval() { eval_step(); }
    /// Evaluate when calling multiple units/models per time step.
    void eval_step();
    /// Evaluate at end of a timestep for tracing, when using eval_step().
    /// Application must call after all eval() and before time changes.
    void eval_end_step() {}
    /// Simulation complete, run final blocks.  Application must call on completion.
    void final();
    /// Are there scheduled events to handle?
    bool eventsPending();
    /// Returns time at next time slot. Aborts if !eventsPending()
    uint64_t nextTimeSlot();
    /// Trace signals in the model; called by application code
    void trace(VerilatedTraceBaseC* tfp, int levels, int options = 0) { contextp()->trace(tfp, levels, options); }
    /// Retrieve name of this model instance (as passed to constructor).
    const char* name() const;

    // Abstract methods from VerilatedModel
    const char* hierName() const override final;
    const char* modelName() const override final;
    unsigned threads() const override final;
    /// Prepare for cloning the model at the process level (e.g. fork in Linux)
    /// Release necessary resources. Called before cloning.
    void prepareClone() const;
    /// Re-init after cloning the model at the process level (e.g. fork in Linux)
    /// Re-allocate necessary resources. Called after cloning.
    void atClone() const;
  private:
    // Internal functions - trace registration
    void traceBaseModel(VerilatedTraceBaseC* tfp, int levels, int options);
};

#endif  // guard

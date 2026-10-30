// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See vdut.h for the primary calling header

#include "vdut__pch.h"

VL_ATTR_COLD void Vdut___024root___stl_sequent__TOP__0(Vdut___024root* vlSelf);
VL_ATTR_COLD void Vdut___024root___stl_sequent__TOP__1(Vdut___024root* vlSelf);
VL_ATTR_COLD void Vdut___024root___stl_sequent__TOP__2(Vdut___024root* vlSelf);
VL_ATTR_COLD void Vdut___024root___stl_sequent__TOP__3(Vdut___024root* vlSelf);
VL_ATTR_COLD void Vdut___024root___stl_sequent__TOP__4(Vdut___024root* vlSelf);
VL_ATTR_COLD void Vdut___024root___stl_sequent__TOP__5(Vdut___024root* vlSelf);
VL_ATTR_COLD void Vdut___024root___stl_sequent__TOP__6(Vdut___024root* vlSelf);

VL_ATTR_COLD void Vdut___024root___eval_stl(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_stl\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_0;
    __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_0 = 0;
    CData/*0:0*/ __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_6;
    __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_6 = 0;
    // Body
    if ((1ULL & vlSelfRef.__VstlTriggered[0U])) {
        Vdut___024root___stl_sequent__TOP__0(vlSelf);
        Vdut___024root___stl_sequent__TOP__1(vlSelf);
        Vdut___024root___stl_sequent__TOP__2(vlSelf);
        Vdut___024root___stl_sequent__TOP__3(vlSelf);
        Vdut___024root___stl_sequent__TOP__4(vlSelf);
        Vdut___024root___stl_sequent__TOP__5(vlSelf);
        Vdut___024root___stl_sequent__TOP__6(vlSelf);
        __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_6 
            = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__wr_ok) 
               & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__wr_fire));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__input_write 
            = ((0x0400U <= (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr)) 
               & __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_6);
        __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_0 
            = ((0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__awaddr)) 
               & __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_6);
        vlSelfRef.flyvis_ddr_soc_ip__DOT__release_cmd 
            = ((0x00000010U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata) 
               & __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_0);
        vlSelfRef.flyvis_ddr_soc_ip__DOT__start_cmd 
            = ((1U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata) 
               & __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_0);
        vlSelfRef.flyvis_ddr_soc_ip__DOT__latch_cmd 
            = ((8U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata) 
               & __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_0);
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT____Vcellinp__journal__cfg_valid 
            = (__Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_0 
               & ((4U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata) 
                  & (IData)(vlSelfRef.__VdfgRegularize_h52e72c00_0_4)));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__restore_cmd 
            = ((2U == vlSelfRef.flyvis_ddr_soc_ip__DOT__wdata) 
               & __Vinline__nba_sequent__TOP__28___VdfgRegularize_h52e72c00_0_0);
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__restore_fire 
            = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__restore_cmd) 
               & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__restore_ready));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__lane_input_ready 
            = ((~ (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__restore_fire)) 
               & (0U == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vcellinp__stimulus_ram__we 
            = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT____Vcellinp__network__input_valid) 
               & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__lane_input_ready));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__accept_word 
            = ((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vcellinp__stimulus_ram__we) 
               | ((0x0dU == (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__phase)) 
                  & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal_state_ready)));
        vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__push 
            = (((IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__half) 
                | (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__last_word)) 
               & (IData)(vlSelfRef.flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__accept_word));
    }
}

VL_ATTR_COLD void Vdut___024root___eval_triggers_vec__stl(Vdut___024root* vlSelf);
#ifdef VL_DEBUG
VL_ATTR_COLD void Vdut___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vdut___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in);

VL_ATTR_COLD bool Vdut___024root___eval_phase__stl(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___eval_phase__stl\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VstlExecute;
    // Body
    Vdut___024root___eval_triggers_vec__stl(vlSelf);
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vdut___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
    }
#endif
    __VstlExecute = Vdut___024root___trigger_anySet__stl(vlSelfRef.__VstlTriggered);
    if (__VstlExecute) {
        Vdut___024root___eval_stl(vlSelf);
    }
    return (__VstlExecute);
}

bool Vdut___024root___trigger_anySet__ico(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vdut___024root___dump_triggers__ico(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___dump_triggers__ico\n"); );
    // Body
    if ((1U & (~ (IData)(Vdut___024root___trigger_anySet__ico(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: Internal 'ico' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

bool Vdut___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vdut___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(Vdut___024root___trigger_anySet__act(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @(posedge aclk)\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vdut___024root___ctor_var_reset_0(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___ctor_var_reset_0\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->aclk = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10553736683680568397ull);
    vlSelf->aresetn = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8123012239402083478ull);
    vlSelf->s_axi_awaddr = VL_SCOPED_RAND_RESET_I(12, __VscopeHash, 7303631981020876172ull);
    vlSelf->s_axi_awprot = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 15115230546005115681ull);
    vlSelf->s_axi_awvalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13986037914296269070ull);
    vlSelf->s_axi_awready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14099717354022636468ull);
    vlSelf->s_axi_wdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11311253403970331505ull);
    vlSelf->s_axi_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 18112015138521062007ull);
    vlSelf->s_axi_wvalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12168530306759773544ull);
    vlSelf->s_axi_wready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17608475915581965368ull);
    vlSelf->s_axi_bresp = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 15162762900795686431ull);
    vlSelf->s_axi_bvalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9334582144896637853ull);
    vlSelf->s_axi_bready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15653039750784194130ull);
    vlSelf->s_axi_araddr = VL_SCOPED_RAND_RESET_I(12, __VscopeHash, 8722301305194254610ull);
    vlSelf->s_axi_arprot = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 375973211984234811ull);
    vlSelf->s_axi_arvalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17746383479076595557ull);
    vlSelf->s_axi_arready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17791137924766170856ull);
    vlSelf->s_axi_rdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12866136205313389248ull);
    vlSelf->s_axi_rresp = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 14929039895447920609ull);
    vlSelf->s_axi_rvalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15026938065200214434ull);
    vlSelf->s_axi_rready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1794163653381394343ull);
    vlSelf->m_axi_awaddr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13558266821849222593ull);
    vlSelf->m_axi_awid = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 1024821634766282054ull);
    vlSelf->m_axi_awlen = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 15527027863330074270ull);
    vlSelf->m_axi_awsize = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 17768164634708584365ull);
    vlSelf->m_axi_awburst = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 16027732775651784324ull);
    vlSelf->m_axi_awlock = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8893572666646070633ull);
    vlSelf->m_axi_awcache = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 3753142715102392777ull);
    vlSelf->m_axi_awprot = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 6216549597533674627ull);
    vlSelf->m_axi_awqos = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 10786130570056985181ull);
    vlSelf->m_axi_awvalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17994771565963626208ull);
    vlSelf->m_axi_awready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16573481163850279297ull);
    vlSelf->m_axi_wdata = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 1286380785785437420ull);
    vlSelf->m_axi_wstrb = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 15721383833457952779ull);
    vlSelf->m_axi_wlast = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2914646395814725164ull);
    vlSelf->m_axi_wvalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17462522629772039856ull);
    vlSelf->m_axi_wready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10076110868751280388ull);
    vlSelf->m_axi_bid = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 11115145799783860064ull);
    vlSelf->m_axi_bresp = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 3179402000051064225ull);
    vlSelf->m_axi_bvalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17532096651654485089ull);
    vlSelf->m_axi_bready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 919615779156835605ull);
    vlSelf->flyvis_ddr_soc_ip__DOT____Vlvbound_h38bd5078__0 = 0;
    vlSelf->flyvis_ddr_soc_ip__DOT__aw_pending = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4349184481099862307ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__w_pending = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12742005950009412579ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__awaddr = VL_SCOPED_RAND_RESET_I(12, __VscopeHash, 10834332365442383729ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__wdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17725259573411165147ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 5699028468877347570ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__cfg_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11605239426568738573ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__cfg_end = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2039602674953005401ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__cfg_first = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11047641597956649060ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__cfg_cookie = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9757850246288898792ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__cfg_slots = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 15639260944479126324ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__loaded = VL_SCOPED_RAND_RESET_I(10, __VscopeHash, 16442377500519328286ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__feed_index = VL_SCOPED_RAND_RESET_I(10, __VscopeHash, 11550545374574098400ull);
    for (int __Vi0 = 0; __Vi0 < 721; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__frame[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9792208247088983173ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__frame_q = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9250628730351376225ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__feed = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 16150081352136521529ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__running = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3949485673919720218ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__clean = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1941708493944996870ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__configured = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13505755485859184129ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__full = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3159732307665574942ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__begin_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2238167850145127444ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__restore_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10631848184137989490ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__publish = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 664982413799502748ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__published_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16765601803712321302ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__published_frame = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7082739301727964806ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__committed = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15156350720294720400ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__released = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8301187722758033445ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__release_sequence = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6229982710339681131ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__release_cookie = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15728161448456767419ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__release_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6101913439667611030ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__rejected = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12904218285076279785ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__live_seq = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10099685063455611528ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__live_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5047503770502914483ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__live_frame = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2753348180213660715ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__live_cycles = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16344829187718060927ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__snap_seq = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5626131631563765737ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__snap_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12964238591143189974ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__snap_frame = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8205737593398467607ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__snap_cycles = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11339635852928176434ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__snap_cookie = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8126087811617924980ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__snap_errors = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3671565396309207849ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__control_busy = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4472010087779238534ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__wr_fire = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6889527852503877120ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__wr_ok = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14456362961814153282ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__restore_cmd = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3315293194433743528ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__start_cmd = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11829425522275875292ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__latch_cmd = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5380006167668881199ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__release_cmd = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10492367001775832883ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__input_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6035071927900138418ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__trace_eid = VL_SCOPED_RAND_RESET_I(21, __VscopeHash, 2197247811725918500ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__trace_src = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 1086162677532438251ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__trace_dst = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 7267689284806893605ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__trace_weight = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7216263523465228571ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__inflight = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8608448041611649234ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__restoring = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11700548381380057046ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__restore_fire = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8149991774643838529ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__lane_input_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12951118793577353898ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal_state_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6557558933979769279ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal_begin_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12196257790930747093ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal_cfg_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8030023625767754882ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__active = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10056097096674262451ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__edge_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15372310664316779886ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__edge_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14853261791182207798ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__cycles = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9550099008962822503ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__edges = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1871569686735756169ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__states = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18146033211746788946ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__core_faults = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 122337644919794368ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 11468551307466514987ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__phase = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 14940129657870399310ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT____Vcellinp__network__input_valid = 0;
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT____Vcellinp__journal__cfg_valid = 0;
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h5e55ba7f__0 = 0;
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__1 = 0;
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__1 = 0;
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h74bfb57c__0 = 0;
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hcdd07836__0 = 0;
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h47fa1709__0 = 0;
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_ha5127405__0 = 0;
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h25151c11__0 = 0;
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h8505b61a__0 = 0;
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_h7a6e951d__0 = 0;
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vlvbound_hb2d1acac__0 = 0;
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pipe_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4818438155128207559ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6142778232689016744ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 627359425413819012ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14697335690705591820ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11709011823656952906ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_addr = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 18148878335308638113ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_addr = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 14542640586276397591ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr_addr = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 7591598293602944530ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_addr = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 11743201818833315203ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__ar_data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4900965819007922315ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__aw_data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14001975351369342557ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cr_data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9486455072198326808ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cw_data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2198547989946821155ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_read = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15784548329500291235ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__map_read = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14652790115812401611ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_address = VL_SCOPED_RAND_RESET_I(13, __VscopeHash, 14512972539174334473ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__map_address = VL_SCOPED_RAND_RESET_I(11, __VscopeHash, 12361364250244067155ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__stim_q = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4020037780704600319ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__av = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15955660508482690389ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cv = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10191449804269217006ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6667427895479774610ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10844931979442010786ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_a = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7252326285343043851ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_b = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10172484391376950309ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_a = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3124877422100458108ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_b = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16108110226637071855ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__add_out = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17742365873357288048ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__mul_out = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16682074073130992209ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__rom_q = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11267158915935946395ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen_rom_en = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12446404283457538868ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen_rom_addr = VL_SCOPED_RAND_RESET_I(13, __VscopeHash, 6488480669958388159ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv = VL_SCOPED_RAND_RESET_I(23, __VscopeHash, 443424414058392663ull);
    for (int __Vi0 = 0; __Vi0 < 23; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15093128079473820737ull);
    }
    for (int __Vi0 = 0; __Vi0 < 23; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15320063618031799162ull);
    }
    for (int __Vi0 = 0; __Vi0 < 23; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4966009813673335936ull);
    }
    for (int __Vi0 = 0; __Vi0 < 23; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 2902960929397344968ull);
    }
    for (int __Vi0 = 0; __Vi0 < 23; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid[__Vi0] = VL_SCOPED_RAND_RESET_I(21, __VscopeHash, 13942786040115153438ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__request_src = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 6105502207938149473ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__hazard = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7668198378760774915ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__input_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14760047866368096355ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 730822148384538130ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 811293634670716169ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__word_id = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2891330060994783056ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12116022017303049632ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13226321307701257333ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11911830576493278463ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2580567110748908381ull);
    for (int __Vi0 = 0; __Vi0 < 7; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__desc[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18270065691856163193ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__old_a = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15800234482645683927ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__bias = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11487113451795257609ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__inv = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4664709655580524444ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_result = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8058325186600676323ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__load_slot = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 15006575718516068308ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__issue_slot = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 13842287963311040377ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__batch_count = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 3840844614596651075ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__received = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 17909245500951062818ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__batch_first = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6456681366826146440ull);
    for (int __Vi0 = 0; __Vi0 < 32; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_old[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2302136592036532099ull);
    }
    for (int __Vi0 = 0; __Vi0 < 32; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_current[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1991892803474652543ull);
    }
    for (int __Vi0 = 0; __Vi0 < 32; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_input[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2707612367583884111ull);
    }
    for (int __Vi0 = 0; __Vi0 < 32; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5488758717970309265ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid = VL_SCOPED_RAND_RESET_I(13, __VscopeHash, 16693633890290998898ull);
    for (int __Vi0 = 0; __Vi0 < 13; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag[__Vi0] = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 4097713653564695779ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_return = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18415844472243612996ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__return_slot = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 13057899429355633529ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_input = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3812297257325584760ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vcellinp__stimulus_ram__we = 0;
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT____Vcellinp__stimulus_ram__re = 0;
    for (int __Vi0 = 0; __Vi0 < 7663; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__metadata__DOT__ordinary__DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16849429004041054346ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__selected = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 10147916766837263332ull);
    for (int __Vi0 = 0; __Vi0 < 45; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13755533048117127485ull);
    }
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 113124747949633252ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 495617875778848651ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14437343386925142906ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7085700422707347173ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5442617800289338012ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10109753778499189182ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10179507098408938358ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10240771275524469953ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13641004309280277208ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3119499556533766763ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11081773274415303108ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2488418993374162060ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14301395254838252554ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16470088380996999443ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9745576262572206435ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8581770224675122384ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10338295158229357844ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15054377956263453125ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12070400468277429655ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2822740698068909791ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8079629690718140666ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4394606494480808858ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6797922348422756397ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5393183576213089330ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13137167075907832701ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5712959434338706901ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2665694870700614591ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11780735398580043363ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8793608349131419850ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15406144453772734894ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8501046608500174798ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2509942235548638986ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10813661836657073324ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 627208939741760258ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14475049023307468146ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14157906748936198735ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12464192653348543250ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13426662467533475395ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1605776655858449219ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 192513565479122652ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18033870523606236768ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5515836000553855292ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11658068470960120099ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 193816606905650943ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 216684951420977005ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3702652085312920761ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16734412905787022253ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12419695238796673279ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17014700323494861188ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15600357266479336089ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5037004582875397860ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3302755137650085852ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6771564439336338800ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1956471771623280921ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16950429846866501140ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16139234060530760884ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14086172642825902873ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6906673994948368009ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5633490463815424038ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13178704036264839764ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11154067883231153149ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5653331678616572327ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9061679880794612455ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2653120745882374711ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14557083209649235346ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18287262944577803616ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10437299280156062021ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7984472530312987760ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3374519645753308797ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4044635504507924861ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11350459318389916698ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4357123465837759639ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4611139085040030846ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12862376771191534630ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15641796188499934653ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18378399497207174737ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17819270791318174697ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5935512518656605171ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6869564684989488032ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16088310974105026895ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13557222301296960937ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7939548687938191647ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16518382274776108444ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7770956384981495713ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1870947772457441628ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2549333737844857174ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9571436761892221104ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9599189587128936101ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16620099705883354461ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11975839591625938875ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__selected = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 7271147835191986861ull);
    for (int __Vi0 = 0; __Vi0 < 45; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__bank_q[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11473422805323886234ull);
    }
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15585718141604812775ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7277527228976922119ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9833612500996147571ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4713912546673338088ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18394338011532465752ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8915982946555588035ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2065251934254525157ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9723688946214978097ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12454566140811639712ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12638973058873857103ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4015700842869447035ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13307969360997545860ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11417105701946717648ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5036161182580856360ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3489801773695520430ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14945782017561808498ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14638992309289445729ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9958626307448911727ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8571743870946378100ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11188611693316922874ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5424754686981537402ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5859541192597409735ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12218425269063711985ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10070850197836955518ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12377601187631617187ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6125122327334106151ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13649009534805871131ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8137322431070487009ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9204379903967709152ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13760922778666742833ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6117292270891174906ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17567028590797745809ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4562147337688498892ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11143751723807422725ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14347415796519431872ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17808366721708094999ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 132818293935648466ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8860238692265033117ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1700513257262092093ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6124183280916807995ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1414282127847117646ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12131074780473446413ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6511760801552035533ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15951104383810983708ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14124681497308282359ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5140565229182612796ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8793957414186348294ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12926927846549737517ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14835911558614574343ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 605499397868420529ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17458633139903359671ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17383018028730897441ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15925398668942672863ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2206208323732436824ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12355042853201839383ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12091845601917521725ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10718034124946945264ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4539311093559967111ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12541446046499537944ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18424535836068210740ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8132626598910391599ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12097292082655630049ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14836464001552543854ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9960524537644193107ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13303794943537080347ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5991225126718401452ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1936229492955288523ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11354815187450711250ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5529471838087121146ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9517602811797095338ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 900131513767925787ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 514893156770073102ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8416363184938870054ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6100450633798412623ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5666768128689250053ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7338361595486172465ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8775965364654710844ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1217643902841199488ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10796925326909801160ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3873023687202275454ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17234601265946683795ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14701260698653833131ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6471129975982489064ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2881954442589783399ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4190464330608969652ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14129365378621387849ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 97754812196723495ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8047044455932641319ull);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9181948442348736628ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7021369292386708805ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__stimulus_ram__DOT____Vlvbound_hf157a2a8__0 = 0;
    for (int __Vi0 = 0; __Vi0 < 721; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__stimulus_ram__DOT__ordinary__DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17087781730707358432ull);
    }
    VL_ZERO_RESET_W(2192, vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT____Vlvbound_h6fa177e9__0);
    for (int __Vi0 = 0; __Vi0 < 12; ++__Vi0) {
        VL_SCOPED_RAND_RESET_W(2192, vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__d[__Vi0], __VscopeHash, 1069719459926445111ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__v = VL_SCOPED_RAND_RESET_I(13, __VscopeHash, 15660399976974816940ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__packed_result = VL_SCOPED_RAND_RESET_Q(37, __VscopeHash, 8020482202842830385ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__an = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7875271873088446401ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__bn = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2541584615517139075ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__ai = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15256518265102047747ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__bi = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7782739427215933736ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__a_ge_b = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8957260792255347610ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__carry = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 10982111890163467138ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__group_index = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 6658757570680263635ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__amount = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 17661369486297721182ull);
    VL_SCOPED_RAND_RESET_W(291, vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_low, __VscopeHash, 6149439235765371187ull);
    VL_SCOPED_RAND_RESET_W(291, vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__shift_high, __VscopeHash, 18264596932283974870ull);
    VL_ZERO_RESET_W(317, vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT____Vlvbound_hac29fb3c__0);
    for (int __Vi0 = 0; __Vi0 < 7; ++__Vi0) {
        VL_SCOPED_RAND_RESET_W(317, vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__d[__Vi0], __VscopeHash, 11083883676236032423ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__v = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8823645562109214991ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__operand_a = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15694037923528378091ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__operand_b = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17292208415254502426ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__an = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12761170918341967988ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__bn = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4754740568631797586ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__ai = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6811995434541279589ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__bi = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17196613993714122105ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__exponent = VL_SCOPED_RAND_RESET_I(11, __VscopeHash, 6152964992431810219ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__amount = VL_SCOPED_RAND_RESET_I(11, __VscopeHash, 5771762350450482175ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_low = VL_SCOPED_RAND_RESET_Q(51, __VscopeHash, 14117319780929173810ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__shift_high = VL_SCOPED_RAND_RESET_Q(51, __VscopeHash, 12432720149166154077ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__packed_result = VL_SCOPED_RAND_RESET_Q(37, __VscopeHash, 6314247360178948690ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 16706188023476320512ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id = VL_SCOPED_RAND_RESET_I(10, __VscopeHash, 14131334557671147628ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rank_first = VL_SCOPED_RAND_RESET_I(10, __VscopeHash, 2810160351802277015ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 10621717501112305546ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sv = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 12107576481524952809ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tv = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 7447619533667221197ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j_step = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 10096333247545838855ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id = VL_SCOPED_RAND_RESET_I(12, __VscopeHash, 11457190229301041914ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_end = VL_SCOPED_RAND_RESET_I(12, __VscopeHash, 12946822524335583651ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 9037915505529688167ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u_last = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 10581694166443244901ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 17540833525336111814ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_count = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 3387024847712692563ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__vfirst = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 6475577132196074462ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sl = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13184453418107333001ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tl = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2489916754570208020ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sbase = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 9819148916014737103ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tbase = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 15755942843024706504ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__du = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 11151345851213356529ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__dv = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 11935296027413605445ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__next_eid = VL_SCOPED_RAND_RESET_I(21, __VscopeHash, 15196238996820316753ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_weight = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7225727551808206724ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__advance = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14030792039168535723ull);
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__r[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7812290119813571514ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sn[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13747085197201157146ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tn[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15795844715011949895ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5815343027051529803ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_q = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7911183477627400501ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__map_q = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 16113916172041240125ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16626821746156128261ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__bounds_q = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17267879000439253750ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_read = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9326436513972390923ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__last_candidate = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18092628380883047218ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__descriptor_query = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6430474727442416548ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__descriptor_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11998916126883350977ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__first_j = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 8608945666762835802ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__end_j = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 6556854812067320932ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__lower_j = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 9803524216649841267ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rows_addr = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 3335737241303872870ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_rows_addr = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 14031751478018005822ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__prefetch_u = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 9228047031795114745ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__base_v = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 686964438970120387ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__upper_delta = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5691257962325424121ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_read_u = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8851404915350982851ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_row_q = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3034810867676691590ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_pending = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3928123807658445299ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4145172635921696801ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_nonempty = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8696880363428786321ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_tag = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 17707955720594883331ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_tag = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 483587257567751784ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_first = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 2795442398717742172ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_end = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 18431471855841365695ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_step = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 1002782195580685412ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_vfirst = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 13733218847369592398ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_rank = VL_SCOPED_RAND_RESET_I(10, __VscopeHash, 1747004126796537271ull);
    for (int __Vi0 = 0; __Vi0 < 1922; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__maps__DOT__ordinary__DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 7765379945570969549ull);
    }
    for (int __Vi0 = 0; __Vi0 < 62; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rows__DOT__ordinary__DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8920448916181311175ull);
    }
    for (int __Vi0 = 0; __Vi0 < 62; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__target_rows__DOT__ordinary__DOT__mem[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12231888949619406020ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 14575782273478762561ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 1674503174050759850ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__record_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17478418954896853694ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__end_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 175775356333895652ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__frame_id = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11818713804301278621ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__acked_beats = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3729652101286457936ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__slots = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 4074242842566100741ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__write_slot = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 8142159737731110327ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__ring_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9108005251654537434ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__session_cookie = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1868616769532143728ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__sequence_exhausted = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16540882421009827024ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__wp = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 14827441864051918393ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__rp = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 8052749738024865046ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count = VL_SCOPED_RAND_RESET_I(7, __VscopeHash, 162973730014366964ull);
    for (int __Vi0 = 0; __Vi0 < 64; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__fifo_data[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 7158778505208818869ull);
    }
    for (int __Vi0 = 0; __Vi0 < 64; ++__Vi0) {
        vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__fifo_strb[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 11573581345125932360ull);
    }
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__half = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9903273662347172894ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__low_word = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17538786876736204862ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18404670959878533728ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9522198926474809506ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_hash = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10563470787058717112ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_hash = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2046647474907565804ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__saved_cycles = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1425574807266610659ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__saved_edges = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6210146022122102750ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__saved_states = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7581799829717434504ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__saved_faults = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6821736695714204902ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__got_info = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13630074396988096337ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__burst_beats = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 3244904681807353639ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__beat = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 2896722778901702600ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__timeout_count = VL_SCOPED_RAND_RESET_I(17, __VscopeHash, 9247963532589991637ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__push = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6560034405231134105ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__pop = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8699052393997518087ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__accept_word = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11530036391818970181ull);
}

VL_ATTR_COLD void Vdut___024root___ctor_var_reset_1(Vdut___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vdut___024root___ctor_var_reset_1\n"); );
    Vdut__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__last_word = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11363595372980120816ull);
    vlSelf->flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__word_bits = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1298053255260189965ull);
    VL_ZERO_RESET_W(291, vlSelf->__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__Vfuncout);
    VL_ZERO_RESET_W(291, vlSelf->__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__x);
    VL_ZERO_RESET_W(291, vlSelf->__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__3__q);
    VL_ZERO_RESET_W(291, vlSelf->__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__Vfuncout);
    VL_ZERO_RESET_W(291, vlSelf->__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__x);
    VL_ZERO_RESET_W(291, vlSelf->__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__jam__4__q);
    vlSelf->__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__Vfuncout = 0;
    vlSelf->__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__x = 0;
    vlSelf->__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__6__q = 0;
    vlSelf->__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__Vfuncout = 0;
    vlSelf->__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__x = 0;
    vlSelf->__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__jam__7__q = 0;
    vlSelf->__Vfunc_flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__header_word__9__index = 0;
    vlSelf->__VdfgRegularize_h52e72c00_0_3 = 0;
    vlSelf->__VdfgRegularize_h52e72c00_0_4 = 0;
    vlSelf->__VdfgRegularize_h52e72c00_0_5 = 0;
    vlSelf->__VdfgRegularize_h52e72c00_0_7 = 0;
    vlSelf->__VdfgRegularize_h52e72c00_0_9 = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__cfg_base = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__cfg_end = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__cfg_slots = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__cfg_first = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__cfg_cookie = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__release_sequence = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__release_cookie = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__rejected = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__feed_index = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__feed = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__edges = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__states = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__cycles = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_valid = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pv = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__phase = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__input_index = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__local_index = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__type_id = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__node_count = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__index = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__load_slot = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__batch_count = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__received = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__op_id = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__adder__DOT__genblk1__DOT__impl__DOT__v = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__multiplier__DOT__genblk1__DOT__impl__DOT__v = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__row_pending = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_first = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_end = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_step = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_vfirst = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_rank = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_nonempty = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_tag = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__desc_ready = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__state = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rule_id = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__word_id = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__next_eid = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_id = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_end = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__sbase = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__tbase = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__geom = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__offset_weight = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__u_last = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__rank_first = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__j_step = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__gen__DOT__bounds_q = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__publish = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal_errors = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__record_base = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__write_slot = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__frame_id = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__active = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__phase = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_count = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_count = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__half = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__input_hash = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__state_hash = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__acked_beats = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__got_info = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__count = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__timeout_count = 0;
    vlSelf->__Vdly__flyvis_ddr_soc_ip__DOT__engine__DOT__journal__DOT__bus = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__frame__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__frame__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__frame__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v1 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v1 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v2 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v3 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v3 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v1 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v1 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v4 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v5 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v5 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v2 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v2 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v6 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v7 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v7 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v3 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v3 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v8 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v9 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v9 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v4 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v4 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v10 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v11 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v11 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v5 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v5 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v12 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v13 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v13 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v6 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v6 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v14 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v15 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v15 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v7 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v7 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v16 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v17 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v17 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v8 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v8 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v18 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v19 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v19 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v9 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v9 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v20 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v21 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v21 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v10 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v10 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__cap__v22 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v11 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v11 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v12 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_tag__v12 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v1 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v1 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v1 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v1 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v1 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v1 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v1 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v1 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v2 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v2 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v2 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v2 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v2 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v2 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v2 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v2 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v3 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v3 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v3 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v3 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v3 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v3 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v3 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v3 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v4 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v4 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v4 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v4 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v4 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v4 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v4 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v4 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v5 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v5 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v5 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v5 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v5 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v5 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v5 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v5 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v6 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v6 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v6 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v6 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v6 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v6 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v6 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v6 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v7 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v7 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v7 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v7 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v7 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v7 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v7 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v7 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v8 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v8 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v8 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v8 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v8 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v8 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v8 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v8 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v9 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v9 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v9 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v9 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v9 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v9 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v9 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v9 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v10 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v10 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v10 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v10 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v10 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v10 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v10 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v10 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v11 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v11 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v11 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v11 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v11 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v11 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v11 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v11 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v12 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v12 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v12 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v12 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v12 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v12 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v12 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v12 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v13 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v13 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v13 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v13 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v13 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v13 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v13 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v13 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v14 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v14 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v14 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v14 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v14 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v14 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v14 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v14 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v15 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v15 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v15 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v15 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v15 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v15 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v15 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v15 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v16 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v16 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v16 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v16 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v16 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v16 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v16 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v16 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v17 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v17 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v17 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v17 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v17 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v17 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v17 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v17 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v18 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v18 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v18 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v18 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v18 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v18 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v18 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v18 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v19 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v19 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v19 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v19 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v19 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v19 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v19 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v19 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v20 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v20 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v20 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v20 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v20 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v20 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v20 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v20 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v21 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v21 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v21 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v21 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v21 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v21 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v21 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v21 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v22 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__prod__v22 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v22 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__wt__v22 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pdst__v22 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__pid__v22 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_old__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_old__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_old__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_current__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_current__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_input__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_input__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__desc__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__desc__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__desc__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__eu_result__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__6__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__7__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__8__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__9__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__10__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__11__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__12__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__13__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__14__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__15__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__16__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__17__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__18__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__19__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__20__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__21__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__22__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__23__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__24__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__25__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__26__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__27__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__28__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__29__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__30__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__31__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__32__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__33__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__34__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__35__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__36__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__37__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__38__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__39__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__40__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__41__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__42__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__43__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__state_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__44__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__0__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__1__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__2__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__3__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__4__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyVal__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlyDim0__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem__v0 = 0;
    vlSelf->__VdlySet__flyvis_ddr_soc_ip__DOT__engine__DOT__network__DOT__current_ram__DOT__wide_banked__DOT__storage__DOT__banks__BRA__5__KET____DOT__mem__v0 = 0;
}

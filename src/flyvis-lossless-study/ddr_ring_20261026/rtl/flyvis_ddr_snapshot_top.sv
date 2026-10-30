// CPU/RTL integration candidate, not yet PS7/HP0 or an implemented SoC.
// All neural arithmetic, graph generation and neural memories are frozen copies.
// Reserve an unreleased ring slot BEFORE accepting input; arithmetic unchanged.
module flyvis_ddr_snapshot_top #(
    parameter integer N=45669,NT=65,NR=605,NE=1513231,INPUT_WORDS=721,
    parameter META_FILE="",MAP_FILE="",ROWS_FILE="",STATE_FILE="",
    parameter integer BUS_TIMEOUT=65536
)(
    input logic clk,reset,restore_req, output logic restore_ready,state_clean,
    input logic cfg_valid, output logic cfg_ready,
    input logic [31:0] cfg_base,cfg_end,cfg_first_frame,input logic [15:0] cfg_slots,
    input logic [31:0] cfg_cookie,release_sequence,release_cookie,
    input logic release_valid, output logic release_ready,
    output logic [31:0] released_count,
    input logic begin_valid, output logic begin_ready,
    input logic input_valid,output logic input_ready,input logic [31:0] input_bits,
    output logic busy,capacity_exhausted,configured,
    output logic publish,output logic [31:0] published_base,published_frame,
    output logic [31:0] committed_count, output logic [7:0] error_flags,
    output logic trace_edge,output logic [20:0] trace_eid,
    output logic [15:0] trace_src,trace_dst,output logic [31:0] trace_weight,
    output logic neural_done,output logic [31:0] neural_cycles,
    output logic [31:0] m_axi_awaddr,output logic [7:0] m_axi_awlen,
    output logic [2:0] m_axi_awsize,output logic [1:0] m_axi_awburst,
    output logic m_axi_awvalid,input logic m_axi_awready,
    output logic [63:0] m_axi_wdata,output logic [7:0] m_axi_wstrb,
    output logic m_axi_wlast,m_axi_wvalid,input logic m_axi_wready,
    input logic [1:0] m_axi_bresp,input logic m_axi_bvalid,output logic m_axi_bready
);
    logic inflight,restoring,restore_busy,restore_done,restore_fire;
    logic lane_input_ready,journal_input_ready,lane_state_valid,journal_state_ready;
    logic [15:0] lane_state_id;
    logic [31:0] lane_state_bits;
    logic journal_begin_ready,journal_cfg_ready,active,edge_valid,edge_ready;
    logic [31:0] cycles,edges,states,core_faults;
    logic [7:0] journal_errors;
    logic [4:0] phase;
    assign restore_ready=!configured&&!inflight&&!restoring&&journal_errors==0;
    assign restore_fire=restore_req&&restore_ready;
    assign cfg_ready=journal_cfg_ready&&state_clean&&!restoring;
    assign begin_ready=journal_begin_ready&&state_clean&&!inflight&&!restoring;
    assign input_ready=inflight&&lane_input_ready&&journal_input_ready&&journal_errors==0;
    assign busy=inflight||restoring;
    assign trace_edge=edge_valid&&edge_ready;
    assign neural_cycles=cycles;
    assign error_flags=journal_errors;

    flyvis_lane #(.N(N),.NT(NT),.NR(NR),.NE(NE),.META_FILE(META_FILE),
        .MAP_FILE(MAP_FILE),.ROWS_FILE(ROWS_FILE),.STATE_FILE(STATE_FILE)) network(
        .clk,.reset,.restore_req(restore_fire),.restore_busy,.restore_done,
        .inspect_valid(1'b0),.inspect_addr(16'b0),.inspect_ready(),.inspect_rsp_valid(),.inspect_bits(),
        .input_valid(input_valid&&inflight&&journal_input_ready&&journal_errors==0),
        .input_ready(lane_input_ready),.input_bits,
        .accept_enable(1'b1),.write_enable(1'b1),
        .state_valid(lane_state_valid),.state_ready(journal_state_ready),
        .state_id(lane_state_id),.state_bits(lane_state_bits),.step_done(neural_done),.phase,
        .edge_valid,.edge_ready,.edge_src(trace_src),.edge_dst(trace_dst),.edge_weight(trace_weight),.edge_id(trace_eid),
        .pipe_valid(),.pipe_ready(),.pipe_dst(),.pipe_id(),.pipe_old(),.pipe_product(),
        .ar(),.aw(),.cr(),.cw(),.ar_addr(),.aw_addr(),.cr_addr(),.cw_addr(),
        .ar_data(),.aw_data(),.cr_data(),.cw_data(),.rom_read(),.map_read(),.rom_address(),.map_address(),.hazard_wait());

    snapshot_axi_writer #(.N(N),.NE(NE),.INPUT_WORDS(INPUT_WORDS),.BUS_TIMEOUT(BUS_TIMEOUT)) journal(
        .clk,.reset,.cfg_valid(cfg_valid&&state_clean&&!restoring),.cfg_ready(journal_cfg_ready),
        .cfg_base,.cfg_end,.cfg_first_frame,.cfg_slots,
        .cfg_cookie,.release_valid,.release_ready,.release_sequence,.release_cookie,.released_count,
        .begin_valid(begin_valid&&state_clean&&!inflight&&!restoring),.begin_ready(journal_begin_ready),
        .configured,.active,.capacity_exhausted,
        .input_valid(input_valid&&inflight&&lane_input_ready&&journal_errors==0),
        .input_ready(journal_input_ready),.input_bits,
        .state_valid(lane_state_valid),.state_ready(journal_state_ready),
        .state_id(lane_state_id),.state_bits(lane_state_bits),.state_last(32'(lane_state_id)==N-1),
        .info_valid(neural_done),.info_cycles(cycles),.info_edges(edges),.info_states(states),.info_faults(core_faults),
        .publish,.published_base,.published_frame,.committed_count,.error_flags(journal_errors),
        .m_axi_awaddr,.m_axi_awlen,.m_axi_awsize,.m_axi_awburst,.m_axi_awvalid,.m_axi_awready,
        .m_axi_wdata,.m_axi_wstrb,.m_axi_wlast,.m_axi_wvalid,.m_axi_wready,
        .m_axi_bresp,.m_axi_bvalid,.m_axi_bready);
    always_ff @(posedge clk) begin
        if(reset) begin
            inflight<=0;restoring<=0;state_clean<=0;
            cycles<=0;edges<=0;states<=0;core_faults<=0;
        end else begin
            if(restore_fire) begin restoring<=1;state_clean<=0;end
            if(restore_done) begin restoring<=0;state_clean<=1;end
            if(begin_valid&&begin_ready) begin
                inflight<=1;cycles<=0;edges<=0;states<=0;core_faults<=0;
            end else if(inflight&&!neural_done&&phase!=0) cycles<=cycles+1;
            if(trace_edge) begin
                edges<=edges+1;
                if(32'(trace_eid)!=edges||32'(trace_src)>=N||32'(trace_dst)>=N) core_faults[0]<=1;
            end
            if(lane_state_valid&&journal_state_ready) begin
                states<=states+1;
                if(32'(lane_state_id)!=states) core_faults[1]<=1;
            end
            if(neural_done&&(edges!=NE||states!=N)) core_faults[2]<=1;
            if(publish) inflight<=0;
        end
    end
endmodule

`timescale 1ns/1ps
module ddr_synapse_top #(
    parameter integer H_COUNT=4,SOURCE_COUNT=12,EDGE_COUNT=12,WEIGHT_COUNT=8,
    parameter integer FIFO_DEPTH=4,AXI_TIMEOUT=256,STEP_TIMEOUT=2000000
)(
    input wire clk,rst_n,req_begin,in_we,start,
    input wire [15:0] in_addr,input wire signed [31:0] in_data,
    input wire [31:0] step_id,old_state_tag,base_addr,input wire [63:0] expected_signature,
    output wire busy,done,out_valid,output wire [31:0] status,cycles,
    output wire [31:0] result_step_id,result_old_state_tag,edges_applied,
    output wire [63:0] signature,
    input wire [12:0] out_addr,output wire signed [31:0] out_data,
    output wire trace_valid,output wire [20:0] trace_gid,output wire [12:0] trace_target,
    output wire signed [30:0] trace_term,output wire signed [49:0] trace_sum,
    output wire [31:0] araddr,output wire [3:0] arlen,output wire [2:0] arsize,
    output wire [1:0] arburst,output wire [5:0] arid,output wire arvalid,input wire arready,
    input wire [63:0] rdata,input wire [1:0] rresp,input wire [5:0] rid,
    input wire rlast,rvalid,output wire rready,
    output wire reader_busy,reader_poisoned,output wire [31:0] reader_error,
    output wire [31:0] received,stall_cycles,fifo_occupancy
);
    wire core_busy,reader_done;reg interface_fault;
    wire [63:0] fifo_in,fifo_out;wire fifo_in_valid,fifo_in_ready,fifo_out_valid,fifo_out_ready;
    wire transport_start=start&&core_busy&&!reader_busy&&!interface_fault;
    always @(posedge clk) begin
        if(!rst_n) interface_fault<=0;
        else if(req_begin) interface_fault<=reader_busy;
    end
    assign busy=core_busy||reader_busy;
    axi_edge_reader #(.EDGE_COUNT(EDGE_COUNT),.TIMEOUT_CYCLES(AXI_TIMEOUT)) reader(
        .clk(clk),.rst_n(rst_n),.start(transport_start),.abort(status!=0||interface_fault),.base_addr(base_addr),
        .busy(reader_busy),.done(reader_done),.error(reader_error),.poisoned(reader_poisoned),
        .araddr(araddr),.arlen(arlen),.arsize(arsize),.arburst(arburst),.arid(arid),.arvalid(arvalid),.arready(arready),
        .rdata(rdata),.rresp(rresp),.rid(rid),.rlast(rlast),.rvalid(rvalid),.rready(rready),
        .stream_data(fifo_in),.stream_valid(fifo_in_valid),.stream_ready(fifo_in_ready),.received(received),.stall_cycles(stall_cycles));
    edge_fifo #(.DEPTH(FIFO_DEPTH)) fifo(.clk(clk),.rst_n(rst_n),.clear(req_begin||status!=0),
        .in_data(fifo_in),.in_valid(fifo_in_valid),.in_ready(fifo_in_ready),
        .out_data(fifo_out),.out_valid(fifo_out_valid),.out_ready(fifo_out_ready),.occupancy(fifo_occupancy));
    ddr_synapse_core #(.H_COUNT(H_COUNT),.SOURCE_COUNT(SOURCE_COUNT),.EDGE_COUNT(EDGE_COUNT),
        .WEIGHT_COUNT(WEIGHT_COUNT),.STEP_TIMEOUT(STEP_TIMEOUT)) core(
        .clk(clk),.rst_n(rst_n),.req_begin(req_begin),.in_we(in_we),.start(start),.in_addr(in_addr),.in_data(in_data),
        .step_id(step_id),.old_state_tag(old_state_tag),.expected_signature(expected_signature),
        .edge_data(fifo_out),.edge_valid(fifo_out_valid),.edge_ready(fifo_out_ready),
        .transport_done(reader_done),.transport_error(reader_error|(interface_fault?32'h100:0)),
        .busy(core_busy),.done(done),.out_valid(out_valid),.status(status),.cycles(cycles),
        .result_step_id(result_step_id),.result_old_state_tag(result_old_state_tag),.edges_applied(edges_applied),.signature(signature),
        .out_addr(out_addr),.out_data(out_data),.trace_valid(trace_valid),.trace_gid(trace_gid),
        .trace_target(trace_target),.trace_term(trace_term),.trace_sum(trace_sum));
endmodule

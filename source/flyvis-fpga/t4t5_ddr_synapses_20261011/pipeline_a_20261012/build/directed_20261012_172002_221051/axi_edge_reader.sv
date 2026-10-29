`timescale 1ns/1ps
// Bounded in-order AXI3 read queue. All ARID=0; responses must remain ordered.
// Pending ARVALID remains stable on poison/abort; drain every accepted burst.
module axi_edge_reader #(
    parameter integer EDGE_COUNT=12,BURST_BEATS=16,TIMEOUT_CYCLES=256,OUTSTANDING=4
)(
    input wire clk,rst_n,start,abort,input wire [31:0] base_addr,
    output wire busy,output reg done,output reg [31:0] error,output reg poisoned,
    output reg [31:0] araddr,output reg [3:0] arlen,output wire [2:0] arsize,
    output wire [1:0] arburst,output wire [5:0] arid,output reg arvalid,input wire arready,
    input wire [63:0] rdata,input wire [1:0] rresp,input wire [5:0] rid,
    input wire rlast,rvalid,output wire rready,
    output wire [63:0] stream_data,output wire stream_valid,input wire stream_ready,
    output reg [31:0] received,stall_cycles
);
    localparam AW=$clog2(OUTSTANDING);
    reg running;
    reg [31:0] next_addr,remaining,ar_wait,wait_count;
    reg [AW:0] queued;
    reg [AW-1:0] wp,rp;
    reg [4:0] lengths[0:OUTSTANDING-1];
    reg [4:0] beat;
    integer planned,page_beats;
    wire has_response=running&&(queued!=0);
    wire bad_beat=(rresp!=0)||(rid!=0)||(rlast!=(beat==lengths[rp]-1));
    wire ar_take=running&&arvalid&&arready;
    wire r_take=has_response&&rvalid&&rready;
    wire burst_pop=r_take&&(beat==lengths[rp]-1);
    assign busy=running;
    assign arsize=3'd3;assign arburst=2'b01;assign arid=0;
    assign stream_data=rdata;
    assign stream_valid=has_response&&rvalid&&!poisoned&&!abort&&!bad_beat;
    assign rready=has_response&&(poisoned||abort||bad_beat||stream_ready);
    always @* begin
        page_beats=(4096-{1'b0,next_addr[11:0]})>>3;
        planned=(remaining<BURST_BEATS)?remaining:BURST_BEATS;
        if(planned>page_beats) planned=page_beats;
    end
    always @(posedge clk) begin
        if(!rst_n) begin
            running<=0;done<=0;error<=0;poisoned<=0;arvalid<=0;araddr<=0;arlen<=0;
            next_addr<=0;remaining<=0;ar_wait<=0;wait_count<=0;received<=0;stall_cycles<=0;
            queued<=0;wp<=0;rp<=0;beat<=0;
        end else begin
            done<=0;
            if(start&&!running) begin
                error<=0;poisoned<=0;received<=0;stall_cycles<=0;ar_wait<=0;wait_count<=0;
                queued<=0;wp<=0;rp<=0;beat<=0;arvalid<=0;
                if(base_addr[2:0]!=0||({1'b0,base_addr}+33'd8*EDGE_COUNT)>33'h100000000) begin error<=32'h1;poisoned<=1;done<=1;end
                else begin running<=1;next_addr<=base_addr;remaining<=EDGE_COUNT;end
            end else if(running) begin
                if(abort) begin poisoned<=1;error[5]<=1;end
                if(!arvalid&&remaining!=0&&queued<OUTSTANDING&&!poisoned&&!abort) begin
                    araddr<=next_addr;arlen<=planned-1;arvalid<=1;ar_wait<=0;
                end
                if(ar_take) begin
                    lengths[wp]<={1'b0,arlen}+1'b1;wp<=(wp==OUTSTANDING-1)?0:wp+1'b1;
                    next_addr<=next_addr+8*({1'b0,arlen}+1);remaining<=remaining-({1'b0,arlen}+1);
                    arvalid<=0;ar_wait<=0;
                end else if(arvalid&&!poisoned) begin
                    if(ar_wait==TIMEOUT_CYCLES-1) begin poisoned<=1;error[4]<=1;end else ar_wait<=ar_wait+1;
                end
                if(has_response&&rvalid&&!rready) stall_cycles<=stall_cycles+1;
                if(r_take) begin
                    wait_count<=0;
                    if(rresp!=0) begin error[1]<=1;poisoned<=1;end
                    if(rid!=0) begin error[2]<=1;poisoned<=1;end
                    if(rlast!=(beat==lengths[rp]-1)) begin error[3]<=1;poisoned<=1;end
                    if(!poisoned&&!abort&&!bad_beat) received<=received+1;
                    if(burst_pop) begin beat<=0;rp<=(rp==OUTSTANDING-1)?0:rp+1'b1;end else beat<=beat+1;
                end else if(has_response&&!poisoned&&!rvalid) begin
                    if(wait_count==TIMEOUT_CYCLES-1) begin poisoned<=1;error[4]<=1;end else wait_count<=wait_count+1;
                end else if(!has_response||rvalid) wait_count<=0;
                case({ar_take,burst_pop})
                    2'b10:queued<=queued+1'b1;
                    2'b01:queued<=queued-1'b1;
                    default:begin end
                endcase
                if(queued==0&&!arvalid&&(remaining==0||poisoned||abort)) begin running<=0;done<=1;end
            end
        end
    end
endmodule

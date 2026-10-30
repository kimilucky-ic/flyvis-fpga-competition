`timescale 1ns/1ps
// AXI3-compatible 64-bit read master for HP0, one outstanding burst, ID=0.
// On a fault/abort, keep a pending ARVALID stable and drain the accepted
// burst. A stuck slave leaves busy/poisoned asserted: reset is then required.
module axi_edge_reader #(
    parameter integer EDGE_COUNT=12, BURST_BEATS=16, TIMEOUT_CYCLES=256
)(
    input wire clk,rst_n,start,abort,
    input wire [31:0] base_addr,
    output wire busy, output reg done, output reg [31:0] error,
    output reg poisoned,
    output reg [31:0] araddr, output reg [3:0] arlen,
    output wire [2:0] arsize, output wire [1:0] arburst,
    output wire [5:0] arid, output reg arvalid, input wire arready,
    input wire [63:0] rdata,input wire [1:0] rresp,
    input wire [5:0] rid,input wire rlast,rvalid,output wire rready,
    output wire [63:0] stream_data,output wire stream_valid,input wire stream_ready,
    output reg [31:0] received,output reg [31:0] stall_cycles
);
    localparam IDLE=0,PREP=1,ADDR=2,DATA=3;
    reg [1:0] state;
    reg [31:0] next_addr,remaining,wait_count;
    reg [4:0] burst_count,beat;
    integer planned,page_beats;
    wire bad_beat=(rresp!=0)||(rid!=0)||(rlast!=(beat==burst_count-1));
    assign busy=(state!=IDLE);
    assign arsize=3'd3;assign arburst=2'b01;assign arid=0;
    assign stream_data=rdata;
    assign stream_valid=(state==DATA)&&rvalid&&!poisoned&&!abort&&!bad_beat;
    assign rready=(state==DATA)&&(poisoned||abort||bad_beat||stream_ready);
    always @* begin
        page_beats=(4096-{1'b0,next_addr[11:0]})>>3;
        planned=(remaining<BURST_BEATS)?remaining:BURST_BEATS;
        if(planned>page_beats) planned=page_beats;
    end
    always @(posedge clk) begin
        if(!rst_n) begin
            state<=IDLE;done<=0;error<=0;poisoned<=0;arvalid<=0;
            araddr<=0;arlen<=0;next_addr<=0;remaining<=0;
            burst_count<=0;beat<=0;wait_count<=0;received<=0;stall_cycles<=0;
        end else begin
            done<=0;
            if(start && state==IDLE) begin
                error<=0;poisoned<=0;received<=0;stall_cycles<=0;wait_count<=0;
                if(base_addr[2:0]!=0 || ({1'b0,base_addr}+33'd8*EDGE_COUNT)>33'h100000000) begin
                    error<=32'h1;poisoned<=1;done<=1;
                end else begin next_addr<=base_addr;remaining<=EDGE_COUNT;state<=PREP;end
            end
            if(state!=IDLE && abort) begin poisoned<=1;error[5]<=1;end
            case(state)
                IDLE: begin end
                PREP: begin
                    wait_count<=0;
                    if(poisoned||abort) begin state<=IDLE;done<=1;end
                    else if(remaining==0) begin state<=IDLE;done<=1;end
                    else begin
                        araddr<=next_addr;arlen<=planned-1;burst_count<=planned;
                        beat<=0;arvalid<=1;state<=ADDR;
                    end
                end
                ADDR: begin
                    if(arvalid&&arready) begin arvalid<=0;wait_count<=0;state<=DATA;end
                    else if(!poisoned) begin
                        if(wait_count==TIMEOUT_CYCLES-1) begin poisoned<=1;error[4]<=1;end
                        else wait_count<=wait_count+1;
                    end
                end
                DATA: begin
                    if(rvalid&&!rready) stall_cycles<=stall_cycles+1;
                    if(rvalid&&rready) begin
                        wait_count<=0;
                        if(rresp!=0) begin error[1]<=1;poisoned<=1;end
                        if(rid!=0) begin error[2]<=1;poisoned<=1;end
                        if(rlast!=(beat==burst_count-1)) begin error[3]<=1;poisoned<=1;end
                        if(!poisoned&&!abort&&!bad_beat) received<=received+1;
                        // Count the advertised beats, not an illegal early RLAST.
                        if(beat==burst_count-1) begin
                            next_addr<=next_addr+burst_count*8;
                            remaining<=remaining-burst_count;state<=PREP;
                        end else beat<=beat+1;
                    end else if(!poisoned && !rvalid) begin
                        // Local FIFO backpressure with RVALID present is not
                        // a slave timeout. The core has a separate step watchdog.
                        if(wait_count==TIMEOUT_CYCLES-1) begin poisoned<=1;error[4]<=1;end
                        else wait_count<=wait_count+1;
                    end
                end
            endcase
        end
    end
endmodule

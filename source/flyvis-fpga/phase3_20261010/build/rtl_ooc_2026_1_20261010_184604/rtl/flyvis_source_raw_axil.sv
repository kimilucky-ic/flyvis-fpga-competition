`timescale 1ns/1ps
// AXI4-Lite transport for the independently verified serial FlyVis arithmetic.
// AW/W are buffered separately; B/R remain stable until accepted.
module flyvis_source_raw_axil #(
    parameter EDGE_FILE="rom/edges_q22.mem",
    parameter NEURON_FILE="rom/neurons_q22.mem"
) (
    (* X_INTERFACE_PARAMETER="ASSOCIATED_BUSIF s_axi, ASSOCIATED_RESET s_axi_aresetn" *)
    input wire s_axi_aclk,
    (* X_INTERFACE_PARAMETER="POLARITY ACTIVE_LOW" *) input wire s_axi_aresetn,
    input wire [15:0] s_axi_awaddr, input wire [2:0] s_axi_awprot,
    input wire s_axi_awvalid, output wire s_axi_awready,
    input wire [31:0] s_axi_wdata, input wire [3:0] s_axi_wstrb,
    input wire s_axi_wvalid, output wire s_axi_wready,
    output reg [1:0] s_axi_bresp, output reg s_axi_bvalid, input wire s_axi_bready,
    input wire [15:0] s_axi_araddr, input wire [2:0] s_axi_arprot,
    input wire s_axi_arvalid, output wire s_axi_arready,
    output reg [31:0] s_axi_rdata, output reg [1:0] s_axi_rresp,
    output reg s_axi_rvalid, input wire s_axi_rready
);
    reg aw_pending, w_pending;
    reg [15:0] aw_address;
    reg [31:0] w_data;
    reg [3:0] w_strobe;
    reg req_begin, in_we, start;
    reg [10:0] in_addr;
    reg signed [31:0] in_data;
    wire busy, done, out_valid;
    wire [31:0] status, compute_cycles;
    wire [6:0] out_addr = (s_axi_araddr - 16'h4000) >> 2;
    wire signed [31:0] out_data;
    reg done_sticky;
    assign s_axi_awready = !aw_pending && !s_axi_bvalid;
    assign s_axi_wready = !w_pending && !s_axi_bvalid;
    assign s_axi_arready = !s_axi_rvalid;
    flyvis_source_raw_core #(.EDGE_FILE(EDGE_FILE),.NEURON_FILE(NEURON_FILE)) core(
        .clk(s_axi_aclk),.rst_n(s_axi_aresetn),.req_begin(req_begin),
        .in_we(in_we),.in_addr(in_addr),.in_data(in_data),.start(start),
        .busy(busy),.done(done),.out_valid(out_valid),.status(status),
        .compute_cycles(compute_cycles),.out_addr(out_addr),.out_data(out_data));
    always @(posedge s_axi_aclk) begin
        if (!s_axi_aresetn) begin
            aw_pending<=0; w_pending<=0; s_axi_bvalid<=0; s_axi_bresp<=0;
            s_axi_rvalid<=0; s_axi_rresp<=0; s_axi_rdata<=0;
            req_begin<=0; in_we<=0; start<=0; in_addr<=0; in_data<=0; done_sticky<=0;
        end else begin
            req_begin<=0; in_we<=0; start<=0;
            if(done) done_sticky<=1;
            if(s_axi_bvalid && s_axi_bready) s_axi_bvalid<=0;
            if(s_axi_awvalid && s_axi_awready) begin aw_address<=s_axi_awaddr; aw_pending<=1; end
            if(s_axi_wvalid && s_axi_wready) begin w_data<=s_axi_wdata; w_strobe<=s_axi_wstrb; w_pending<=1; end
            if(aw_pending && w_pending && !s_axi_bvalid) begin
                aw_pending<=0; w_pending<=0; s_axi_bvalid<=1; s_axi_bresp<=2'b00;
                if(w_strobe!=4'hf || aw_address[1:0]!=0) s_axi_bresp<=2'b10;
                else if(aw_address==16'h0020) begin
                    if(w_data==1) begin req_begin<=1; done_sticky<=0; end
                    else if(w_data==2) begin start<=1; done_sticky<=0; end
                    else s_axi_bresp<=2'b10;
                end else if(aw_address>=16'h1000 && aw_address<16'h2768) begin
                    in_we<=1; in_addr<=(aw_address-16'h1000)>>2; in_data<=w_data;
                end else s_axi_bresp<=2'b10;
            end
            if(s_axi_rvalid && s_axi_rready) s_axi_rvalid<=0;
            if(s_axi_arvalid && s_axi_arready) begin
                s_axi_rvalid<=1; s_axi_rresp<=2'b00; s_axi_rdata<=0;
                if(s_axi_araddr[1:0]!=0) s_axi_rresp<=2'b10;
                else if(s_axi_araddr>=16'h4000 && s_axi_araddr<16'h410c) begin
                    if(out_valid && status==0) s_axi_rdata<=out_data;
                    else s_axi_rresp<=2'b10;
                end else case(s_axi_araddr)
                    16'h0000: s_axi_rdata<=32'h46565333; // FVS3
                    16'h0004: s_axi_rdata<=32'h0616141d; // I6,F22,WF20,W29
                    16'h0008: s_axi_rdata<=67;
                    16'h000c: s_axi_rdata<=1364;
                    16'h0010: s_axi_rdata<=6537;
                    16'h0014: s_axi_rdata<=1498;
                    16'h0018: s_axi_rdata<=compute_cycles;
                    16'h001c: s_axi_rdata<=status;
                    16'h0024: s_axi_rdata<={29'd0,out_valid,done_sticky,busy};
                    16'h0028: s_axi_rdata<=32'h04cc0571; // edge-ROM SHA prefix, full SHA checked by host manifest
                    16'h002c: s_axi_rdata<=1; // ABI version
                    default: s_axi_rresp<=2'b10;
                endcase
            end
        end
    end
endmodule

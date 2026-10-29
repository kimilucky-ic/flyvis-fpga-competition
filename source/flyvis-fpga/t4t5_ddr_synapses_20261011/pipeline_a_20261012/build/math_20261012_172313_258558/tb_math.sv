`timescale 1ns/1ps
module tb_math;
    reg clk=0;always #5 clk=~clk;
    reg signed [32:0] a=0;reg signed [30:0] b=0;wire signed [63:0] product;
    reg [32:0] av[0:1023];reg [30:0] bv[0:1023];reg [63:0] pv[0:1023];
    reg [63:0] rv[0:1023];reg [44:0] r20[0:1023];reg [40:0] r24[0:1023];
    reg signed [63:0] injected;
    pipe_mul33x31 m(.clk(clk),.a(a),.b(b),.product(product));
    ddr_synapse_core #(.H_COUNT(8),.SOURCE_COUNT(20),.EDGE_COUNT(256),.WEIGHT_COUNT(8)) d(
        .clk(clk),.rst_n(1'b0),.req_begin(1'b0),.in_we(1'b0),.start(1'b0),.in_addr(16'd0),.in_data(32'd0),
        .step_id(32'd0),.old_state_tag(32'd0),.expected_signature(64'd0),.edge_data(64'd0),.edge_valid(1'b0),
        .transport_done(1'b0),.transport_error(32'd0),.out_addr(13'd0));
    integer i;
    initial begin
        $readmemh("rom/mul_a.mem",av);$readmemh("rom/mul_b.mem",bv);$readmemh("rom/mul_expected.mem",pv);
        $readmemh("rom/round_input.mem",rv);$readmemh("rom/round20_expected.mem",r20);$readmemh("rom/round24_expected.mem",r24);
        for(i=0;i<1026;i=i+1) begin
            @(negedge clk);a=(i<1024)?av[i]:0;b=(i<1024)?bv[i]:0;
            @(posedge clk);#1;
            if(i>=2&&product!==pv[i-2]) $fatal(1,"multiply case=%0d got=%h expected=%h",i-2,product,pv[i-2]);
        end
        force d.product=injected;
        for(i=0;i<1024;i=i+1) begin
            injected=rv[i];#1;
            if(d.round20!==r20[i]||d.round24!==r24[i]) $fatal(1,"round case=%0d",i);
        end
        release d.product;
        $display("MATH_ALL_PASS multiply=1024 rounding20=1024 rounding24=1024");$finish;
    end
endmodule

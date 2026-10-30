`timescale 1ns/1ps
// Synchronous single-clock FIFO. A registered output stage is additional to
// DEPTH RAM slots. No combinational RAM read, no read of an empty slot.
module edge_fifo #(parameter integer DEPTH=16)(
    input wire clk, rst_n, clear,
    input wire [63:0] in_data, input wire in_valid, output wire in_ready,
    output reg [63:0] out_data, output reg out_valid, input wire out_ready,
    output wire [31:0] occupancy
);
    localparam AW=(DEPTH>1)?$clog2(DEPTH):1;
    (* ram_style="block" *) reg [63:0] mem[0:DEPTH-1];
    reg [AW-1:0] wp,rp;
    reg [AW:0] used;
    wire push=in_valid && in_ready;
    wire read_slot=(used!=0) && (!out_valid || out_ready) && !clear;
    assign in_ready=(used<DEPTH) && !clear;
    assign occupancy=used+out_valid;
    always @(posedge clk) begin
        if(!rst_n || clear) begin wp<=0;rp<=0;used<=0;out_valid<=0;out_data<=0;end
        else begin
            if(push) begin mem[wp]<=in_data;wp<=(wp==DEPTH-1)?0:wp+1'b1;end
            if(read_slot) begin
                out_data<=mem[rp];out_valid<=1;
                rp<=(rp==DEPTH-1)?0:rp+1'b1;
            end else if(out_valid && out_ready) out_valid<=0;
            case({push,read_slot})
                2'b10:used<=used+1'b1;
                2'b01:used<=used-1'b1;
                default:begin end
            endcase
        end
    end
endmodule

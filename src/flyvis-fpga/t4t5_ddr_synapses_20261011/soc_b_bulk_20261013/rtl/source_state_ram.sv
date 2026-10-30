`timescale 1ns/1ps
// Preserve one-clock synchronous reads. Avoid rounding 16402 deep storage to 32768.
module source_state_ram #(parameter integer COUNT=16402)(
 input wire clk,we,re,input wire [14:0] waddr,raddr,
 input wire signed [30:0] wdata,output wire signed [30:0] rdata);
 localparam MAIN=(COUNT>16384)?16384:COUNT;
 localparam TAIL=(COUNT>16384)?COUNT-16384:1;
 (* ram_style="block" *) reg signed [30:0] main_mem[0:MAIN-1];
 (* ram_style="distributed" *) reg signed [30:0] tail_mem[0:TAIL-1];
 reg signed [30:0] main_q,tail_q;reg select_tail;
 always @(posedge clk)begin
  if(we&&waddr<COUNT)begin
   if(waddr<MAIN)main_mem[waddr[13:0]]<=wdata;
   else tail_mem[waddr-MAIN]<=wdata;
  end
  if(re)begin
   select_tail<=raddr>=MAIN;
   if(raddr<MAIN)main_q<=main_mem[raddr[13:0]];
   else if(raddr<COUNT)tail_q<=tail_mem[raddr-MAIN];
  end
 end
 assign rdata=select_tail?tail_q:main_q;
endmodule

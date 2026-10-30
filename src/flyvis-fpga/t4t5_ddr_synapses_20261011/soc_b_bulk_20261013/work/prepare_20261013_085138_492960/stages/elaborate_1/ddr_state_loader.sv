`timescale 1ns/1ps
// Each 64-bit beat contains two signed32 words, low word first.
module ddr_state_loader #(parameter integer WORDS=22170,TIMEOUT=65536)(
 input wire clk,rst_n,start,abort,input wire [31:0] base_addr,
 output reg done,output wire busy,output wire [31:0] error,
 output reg [31:0] words_written,output wire in_we,output wire [15:0] in_addr,output wire [31:0] in_data,
 output wire [31:0] araddr,output wire [3:0] arlen,output wire [2:0] arsize,
 output wire [1:0] arburst,output wire [5:0] arid,output wire arvalid,input wire arready,
 input wire [63:0] rdata,input wire [1:0] rresp,input wire [5:0] rid,input wire rlast,rvalid,output wire rready);
 wire [63:0] data;wire valid,ready,reader_busy,reader_done,poisoned;
 wire [31:0] reader_error,received,stalls;
 reg active,finished,high_pending,format_error;
 reg [31:0] high_word;
 wire bad_pair=data[31]!=data[30]||data[63]!=data[62];
 assign error=reader_error|(format_error?32'h100:0);
 assign busy=active||reader_busy;
 assign ready=active&&!high_pending;
 assign in_we=active&&!abort&&error==0&&(high_pending||(valid&&ready&&!bad_pair));
 assign in_addr=words_written[15:0];assign in_data=high_pending?high_word:data[31:0];
 axi_edge_reader #(.EDGE_COUNT((WORDS+1)/2),.TIMEOUT_CYCLES(TIMEOUT)) reader(
  .clk(clk),.rst_n(rst_n),.start(start),.abort(abort||format_error),.base_addr(base_addr),
  .busy(reader_busy),.done(reader_done),.error(reader_error),.poisoned(poisoned),
  .araddr(araddr),.arlen(arlen),.arsize(arsize),.arburst(arburst),.arid(arid),.arvalid(arvalid),.arready(arready),
  .rdata(rdata),.rresp(rresp),.rid(rid),.rlast(rlast),.rvalid(rvalid),.rready(rready),
  .stream_data(data),.stream_valid(valid),.stream_ready(ready),.received(received),.stall_cycles(stalls));
 always @(posedge clk)begin
  if(!rst_n)begin active<=0;finished<=0;high_pending<=0;format_error<=0;words_written<=0;done<=0;high_word<=0;end
  else begin
   done<=0;
   if(start&&!busy)begin active<=1;finished<=0;high_pending<=0;format_error<=0;words_written<=0;end
   else if(active)begin
    if(reader_done)finished<=1;
    if(in_we)words_written<=words_written+1;
    if(high_pending)high_pending<=0;
    if(valid&&ready)begin
     if(bad_pair)format_error<=1;
     else begin high_word<=data[63:32];high_pending<=words_written+1<WORDS;end
    end
    if(abort||error!=0)high_pending<=0;
    if((finished||reader_done)&&!reader_busy&&!high_pending)begin active<=0;done<=1;end
   end
  end
 end
endmodule

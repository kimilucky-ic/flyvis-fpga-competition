`timescale 1ns/1ps
// One buffered AXI3 burst at a time; retain AW/W and drain B on error/timeout.
module ddr_candidate_writer #(parameter integer WORDS=5768,TIMEOUT=65536)(
 input wire clk,rst_n,start,abort,input wire [31:0] base_addr,
 output wire busy,output reg done,output reg [31:0] error,words_acked,
 output reg [12:0] out_addr,input wire [31:0] out_data,
 output wire [31:0] awaddr,output wire [3:0] awlen,output wire awvalid,input wire awready,
 output wire [63:0] wdata,output wire [7:0] wstrb,output wire wlast,wvalid,input wire wready,
 input wire [5:0] bid,input wire [1:0] bresp,input wire bvalid,output wire bready);
 localparam IDLE=0,PRIME=1,FILL=2,ADDR=3,DATA=4,RESP=5;
 reg [2:0] state;
 (* ram_style="distributed" *) reg [63:0] buffer_mem[0:15];
 reg [31:0] address,cursor,remaining,wait_count,low_word;
 reg [5:0] fill_words;reg [4:0] burst_beats,beat;
 initial begin if(WORDS%2!=0)$fatal(1,"Bulk candidate writer requires an even word count");end
 integer planned,page_beats;
 always @*begin
  page_beats=(4096-{1'b0,address[11:0]})>>3;
  planned=((remaining+1)/2<16)?(remaining+1)/2:16;
  if(planned>page_beats)planned=page_beats;
  // Bound the tail to a power-of-two burst; all remaining words follow next.
  if(planned>=16)planned=16;else if(planned>=8)planned=8;
  else if(planned>=4)planned=4;else if(planned>=2)planned=2;else planned=1;
 end
 assign busy=state!=IDLE;assign awaddr=address;assign awlen=burst_beats-1;
 assign awvalid=state==ADDR;assign wvalid=state==DATA;assign wdata=buffer_mem[beat[3:0]];
 assign wstrb=(remaining==1&&beat==0)?8'h0f:8'hff;
 assign wlast=beat==burst_beats-1;assign bready=state==RESP;
 always @(posedge clk)begin
  if(!rst_n)begin state<=IDLE;done<=0;error<=0;words_acked<=0;out_addr<=0;
   address<=0;cursor<=0;remaining<=0;wait_count<=0;low_word<=0;fill_words<=0;burst_beats<=0;beat<=0;end
  else begin
   done<=0;
   if(start&&!busy)begin
    error<=0;words_acked<=0;out_addr<=0;address<=base_addr;cursor<=0;remaining<=WORDS;
    fill_words<=0;beat<=0;wait_count<=0;state<=PRIME;
    if(base_addr[2:0]!=0||({1'b0,base_addr}+33'd4*WORDS)>33'h40000000)begin error<=4;done<=1;state<=IDLE;end
   end else if(busy)begin
    if(abort)error[3]<=1;
    if(state>=ADDR)begin
     if((state==ADDR&&awready)||(state==DATA&&wready)||(state==RESP&&bvalid))wait_count<=0;
     else if(wait_count==TIMEOUT-1)error[1]<=1;
     else wait_count<=wait_count+1;
    end
    case(state)
     PRIME:begin
      if(abort||error!=0)begin state<=IDLE;done<=1;end
      else begin burst_beats<=planned;out_addr<=out_addr+1;state<=FILL;end
     end
     FILL:begin
      if(abort||error!=0)begin state<=IDLE;done<=1;end
      else begin
       if(!fill_words[0])low_word<=out_data;
       else buffer_mem[fill_words[4:1]]<={out_data,low_word};
       cursor<=cursor+1;out_addr<=out_addr+1;
       if(fill_words==2*burst_beats-1)begin state<=ADDR;fill_words<=0;end
       else fill_words<=fill_words+1;
      end
     end
     ADDR:if(awready)begin state<=DATA;beat<=0;end
     DATA:if(wready)begin if(wlast)state<=RESP;else beat<=beat+1;end
     RESP:if(bvalid)begin
      if(bresp!=0||bid!=0)error[0]<=1;
      if(bresp==0&&bid==0)words_acked<=words_acked+2*burst_beats;
      if(bresp!=0||bid!=0||abort||error!=0||remaining<=2*burst_beats)begin state<=IDLE;done<=1;end
      else begin
       remaining<=remaining-2*burst_beats;address<=address+8*burst_beats;
       out_addr<=cursor[12:0];fill_words<=0;state<=PRIME;
      end
     end
    endcase
   end
  end
 end
endmodule

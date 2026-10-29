`timescale 1ns/1ps
module tb_official_video;
 reg ac=0,pc=0,rst=1,vs=0,href=0,pc_run=1;
 reg [2:0] saved_controls;
 reg [7:0] data=0;
 always #5 ac=~ac;
 always #6.944444 if(pc_run) pc=~pc;
 wire ce,ovs,oh,active,overflow,valid,sof,eol;
 wire [23:0] rgb,pixel;
 reg ready=1,checking=0,stall=0,hold_sink=0;
 integer seen=0,width=0,height=0,seed=0,ticks=0;
 cmos_capture_data cap(.rst_n(rst),.cam_pclk(pc),.cam_vsync(vs),.cam_href(href),.cam_data(data),.cmos_frame_ce(ce),.cmos_frame_vsync(ovs),.cmos_frame_href(oh),.cmos_active_video(active),.cmos_frame_data(rgb));
 // Exact generated IP wrapper and original BD tie-offs, no guard replacement.
 base_v_vid_in_axi4s_0_0 video(.aclk(ac),.aclken(1'b1),.aresetn(1'b1),.axis_enable(1'b1),
 .m_axis_video_tdata(pixel),.m_axis_video_tlast(eol),.m_axis_video_tready(ready),.m_axis_video_tuser(sof),.m_axis_video_tvalid(valid),
 .vid_active_video(active),.vid_data(rgb),.vid_field_id(1'b0),.vid_hblank(1'b0),.vid_hsync(oh),.vid_io_in_ce(ce),.vid_io_in_clk(pc),.vid_io_in_reset(!rst),.vid_vblank(1'b0),.vid_vsync(ovs),.overflow(overflow));
 function [23:0] expand(input [15:0] w);expand={w[15:11],3'b0,w[10:5],2'b0,w[4:0],3'b0};endfunction
 always @(negedge ac) begin ticks=ticks+1;if(hold_sink)ready=0;else if(stall)ready=(ticks%17>5);else ready=1;end
 always @(posedge ac) if(checking && valid && ready) begin
   if(seen>=width*height)$fatal(1,"extra pixel");
   if(pixel!==expand(16'(seed+seen)))$fatal(1,"pixel %d got %h",seen,pixel);
   if(sof!==(seen==0))$fatal(1,"SOF %d",seen);
   if(eol!==((seen%width)==width-1))$fatal(1,"EOL %d",seen);
   seen=seen+1;
 end
 task clocks(input integer n);repeat(n)@(negedge pc);endtask
 task pulse_vs;vs=1;clocks(32);vs=0;clocks(40);endtask
 task frame(input integer w,h,s);
   seen=0;width=w;height=h;seed=s;checking=1;pulse_vs();
   for(integer y=0;y<h;y=y+1)begin
    for(integer x=0;x<w;x=x+1)begin
      href=1;data=8'((s+y*w+x)>>8);clocks(1);data=8'(s+y*w+x);clocks(1);
    end
    href=0;clocks(40);
   end
   clocks(100);
   if(seen!=w*h || overflow)$fatal(1,"frame/overflow %d %b",seen,overflow);
   checking=0;
 endtask
 task restart;
  href=0;vs=0;data=0;clocks(40);rst=1;clocks(40);
  repeat(11)pulse_vs();
  if(overflow)$fatal(1,"overflow persists after reset");
 endtask
 task partial_pixel;
  checking=0;pulse_vs();href=1;data=8'hab;clocks(1);
 endtask
 initial begin
  #3;rst=0;clocks(40);rst=1;clocks(40);repeat(11)pulse_vs();
  stall=1;frame(64,8,16'h1234);$display("PASS_RESET_R2_CAPTURE_VIDEO5_BACKPRESSURE_512");
  frame(800,480,16'h3456);$display("PASS_OFFICIAL_GEOMETRY_384000_PIXELS_ALL_BITS_SOF_EOL");
  frame(64,8,16'h789a);$display("PASS_CONTINUOUS_NEXT_FRAME_512");
  partial_pixel();
  // Assert between PCLK edges while a high byte is pending.
  #1;saved_controls={ce,active,ovs};rst=0;#1;
  if({ce,active,ovs}!==saved_controls)$fatal(1,"asynchronous capture control change");
  restart();frame(64,8,16'h92a1);
  $display("PASS_MIDBYTE_RESET_RESTART_ALL_512_PIXELS");
  // Stopped PCLK: reset may assert, capture outputs must wait for clock.
  partial_pixel();pc_run=0;saved_controls={ce,active,ovs};#1;rst=0;#100;
  if({ce,active,ovs}!==saved_controls)$fatal(1,"stopped-clock control change");
  pc_run=1;restart();frame(64,8,16'hb3c2);
  $display("PASS_STOPPED_PCLK_RESET_RESTART_ALL_512_PIXELS");
  checking=0;hold_sink=1;pulse_vs();
  for(integer k=0;k<32;k=k+1)begin
    href=1;data=8'hcc;clocks(1);data=8'(k);clocks(1);
  end
  // A valid old-frame prefix is queued with the AXIS consumer stalled.
  clocks(20);if(!valid)$fatal(1,"reset test did not fill FIFO");
  #1;rst=0;clocks(40);hold_sink=0;
  restart();frame(64,8,16'hd4e3);
  $display("PASS_NONEMPTY_FIFO_MIDFRAME_RESET_RESTART_ALL_512_PIXELS");
  $display("PASS_RESET_R2_STREAM_386560_PIXELS_NOT_VDMA_OR_BOARD");$finish;
 end
 initial begin #25000000;$fatal(1,"bounded timeout");end
endmodule

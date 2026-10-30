`timescale 1ns/1ps
module tb_video;
 reg ac=0,pc=0,clock_enable=1,rst=0,run=0,vs=0,href=0;
 reg [7:0] data=0;
 always #5 ac=~ac;
 always #6.944444 if(clock_enable) pc=~pc; else pc=0;
 wire an,cn,vr,ce,ovs,oh,active,overflow,valid,sof,eol;
 wire [23:0] rgb,axis_data; wire [2:0] status;
 reg ready=1,checking=0,stall=0; integer ticks=0,seen=0,width=0,height=0,seed=0;
 camera_guard guard(.aclk(ac),.aresetn(rst),.run(run),.pclk(pc),.overflow(overflow),.stream_aresetn(an),.capture_resetn(cn),.video_reset(vr),.status(status));
 cmos_capture_data cap(.rst_n(cn),.cam_pclk(pc),.cam_vsync(vs),.cam_href(href),.cam_data(data),.cmos_frame_ce(ce),.cmos_frame_vsync(ovs),.cmos_frame_href(oh),.cmos_active_video(active),.cmos_frame_data(rgb));
 v_vid_in_axi4s_v5_0_8 #(.C_FAMILY("zynq"),.C_HAS_ASYNC_CLK(1),.C_ADDR_WIDTH(10)) video(
 .vid_io_in_clk(pc),.vid_io_in_ce(ce),.vid_io_in_reset(vr),.vid_active_video(active),.vid_vblank(1'b0),.vid_hblank(1'b0),.vid_vsync(ovs),.vid_hsync(oh),.vid_field_id(1'b0),.vid_data(rgb),
 .vid_de_arb(1'b0),.vid_vsync_arb(1'b0),.vid_hsync_arb(1'b0),.vid_field_id_arb(1'b0),.vid_data_arb(24'd0),.vid_format(2'd0),
 .aclk(ac),.aclken(1'b1),.aresetn(an),.m_axis_video_tdata(axis_data),.m_axis_video_tvalid(valid),.m_axis_video_tready(ready),.m_axis_video_tuser(sof),.m_axis_video_tlast(eol),.overflow(overflow),.axis_enable(1'b1),.drop_en(1'b0),.remap_420_en(1'b0));
 function [23:0] expand(input [15:0] w); expand={w[15:11],3'b0,w[10:5],2'b0,w[4:0],3'b0};endfunction
 always @(negedge ac) begin ticks=ticks+1;if(stall) ready=(ticks%17>5);end
 always @(posedge ac) if(an && checking && valid && ready) begin
   if(seen>=width*height) $fatal(1,"extra pixel %d",seen);
   if(axis_data!==expand(16'(seed+seen))) $fatal(1,"pixel %d got %h expected %h",seen,axis_data,expand(16'(seed+seen)));
   if(sof!==(seen==0)) $fatal(1,"SOF index %d",seen);
   if(eol!==((seen%width)==width-1)) $fatal(1,"EOL index %d",seen);
   seen=seen+1;
 end
 task clocks(input integer n);repeat(n) @(negedge pc);endtask
 task pulse_vs;vs=1;clocks(32);vs=0;clocks(40);endtask
 task warm;run=1;clocks(60);repeat(10) pulse_vs();endtask
 task reset_all;
   checking=0;stall=0;ready=1;run=0;rst=0;href=0;vs=0;clocks(40);rst=1;clocks(40);
   if(status!==0) $fatal(1,"global reset status %b",status);
 endtask
 task put(input [7:0] b);href=1;data=b;clocks(1);endtask
 task line_blank;href=0;clocks(24);endtask
 task full_frame(input integer w,h,s);
  width=w;height=h;seed=s;seen=0;checking=1;pulse_vs();
  for(integer y=0;y<h;y=y+1) begin
   for(integer x=0;x<w;x=x+1) begin put(8'((s+y*w+x)>>8));put(8'(s+y*w+x));end
   line_blank();
  end
  clocks(100);
  if(seen!=w*h) $fatal(1,"frame short %d/%d",seen,w*h);
  if(status[0]) $fatal(1,"unexpected overflow");
  checking=0;
 endtask
 reg old_ce;
 initial begin
  reset_all();warm();stall=1;full_frame(64,8,16'h1234);
  $display("PASS_FRAME_AND_BACKPRESSURE 512 pixels");
  // Reset while bytes and real video FIFO data are in flight.
  stall=0;ready=0;pulse_vs();for(integer i=0;i<200;i=i+1) put(8'(i));
  @(posedge pc);#1;old_ce=ce;run=0;#1;
  if(ce!==old_ce) $fatal(1,"capture output changed asynchronously on reset");
  clocks(40);href=0;ready=1;clocks(40);
  if(valid) $fatal(1,"FIFO stale data while reset");
  warm();full_frame(64,8,16'h4567);
  $display("PASS_MIDFRAME_FIFO_RESET_RESTART_NO_STALE_PIXELS");
  // Stop PCLK during reset, then resume mid-line; warmup discards that fragment.
  checking=0;href=1;put(8'hfe);@(negedge pc);clock_enable=0;#3;run=0;#200;
  if(an!==0 || vr!==1) $fatal(1,"stopped-PCLK reset not asserted");
  clock_enable=1;clocks(40);run=1;clocks(40);put(8'haa);line_blank();
  repeat(10) pulse_vs();full_frame(64,8,16'h6789);
  $display("PASS_STOPPED_PCLK_AND_MIDBYTE_RESTART");
  // Overflow actual 1024-entry XPM FIFO under unbounded consumer stall.
  ready=0;pulse_vs();for(integer i=0;i<6000;i=i+1) put(8'(i));line_blank();clocks(40);
  if(status[0]!==1) $fatal(1,"overflow not sticky");
  run=0;clocks(40);if(status[0]!==1) $fatal(1,"normal stop erased fault");
  $display("PASS_ACTUAL_VIDEO_FIFO_OVERFLOW_STICKY_ACROSS_STOP");
  reset_all();warm();stall=1;full_frame(640,480,16'h89ab);
  $display("PASS_VGA_RESTART 307200 pixels all RGB bits SOF/EOL checked");
  $display("PASS_VENDOR_VIDEO5_XPM_FIFO_RESET_OVERFLOW_RESTART");$finish;
 end
 initial begin #30000000;$fatal(1,"bounded simulation timeout");end
endmodule

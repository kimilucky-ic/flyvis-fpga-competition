`timescale 1ns/1ps
module tb_iic;
reg clk=0,rst=0;always #5 clk=~clk;
reg [8:0] aw=0;reg av=0,wv=0;reg[31:0] wd=0;
wire ardy,wrdy,bv;wire[1:0] br;wire si,so,st,di,dout,dt;
reg slave_low=0,active=0;integer bitno=0,bytes_seen=0,stops=0;
reg[7:0] shift=0;reg[7:0] expected[0:3];
// Conditional digital line model: max 300ns rise and 20ns fall, not RC measurement.
assign #(300,20) si=st?1'b1:so;
assign #(300,20) di=(slave_low || (!dt && !dout))?1'b0:1'b1;
flyvis_ddr_cam_iic_0 dut(.s_axi_aclk(clk),.s_axi_aresetn(rst),
.s_axi_awaddr(aw),.s_axi_awvalid(av),.s_axi_awready(ardy),
.s_axi_wdata(wd),.s_axi_wstrb(4'hf),.s_axi_wvalid(wv),.s_axi_wready(wrdy),
.s_axi_bresp(br),.s_axi_bvalid(bv),.s_axi_bready(1'b1),
.s_axi_araddr(9'd0),.s_axi_arvalid(1'b0),.s_axi_rready(1'b1),
.sda_i(di),.sda_o(dout),.sda_t(dt),.scl_i(si),.scl_o(so),.scl_t(st));
realtime last_rise=0,last_fall=0,last_change=0,min_low=1e9,min_high=1e9,min_setup=1e9,min_period=1e9;
always @(di) last_change=$realtime;
always @(negedge di) if(si===1 && rst) begin active=1;bitno=0;end
always @(posedge di) if(si===1 && active) begin active=0;stops=stops+1;end
always @(negedge si) begin
 if(active && last_rise>0) begin
  if($realtime-last_rise<min_high)min_high=$realtime-last_rise;
  if($realtime-last_rise<640) $fatal(1,"SCCB high time too short");
 end
 last_fall=$realtime;
 if(active) slave_low=(bitno%9==8); else slave_low=0;
end
always @(posedge si) begin
 if(active && last_fall>0) begin
  if($realtime-last_fall<min_low)min_low=$realtime-last_fall;
  if($realtime-last_fall<1340)$fatal(1,"SCCB low time too short");
  if($realtime-last_change<min_setup)min_setup=$realtime-last_change;
  if($realtime-last_change<140)$fatal(1,"SCCB setup too short");
  if(last_rise>0 && $realtime-last_rise<min_period)min_period=$realtime-last_rise;
  if(bitno%9<8) begin
   shift={shift[6:0],di};
   if(bitno%9==7) begin
    if(bytes_seen>3 || shift!==expected[bytes_seen]) $fatal(1,"SCCB byte mismatch %d %h",bytes_seen,shift);
    bytes_seen=bytes_seen+1;
   end
  end else if(di!==0) $fatal(1,"ACK was not low");
  bitno=bitno+1;
 end
 last_rise=$realtime;
end
 task write_reg(input[8:0] a,input[31:0] d);
  @(negedge clk);aw=a;wd=d;av=1;wv=1;
  fork
   begin do @(posedge clk);while(!ardy);@(negedge clk);av=0;end
   begin do @(posedge clk);while(!wrdy);@(negedge clk);wv=0;end
  join
  wait(bv);if(br!==0)$fatal(1,"AXI response");@(negedge clk);
 endtask
initial begin
 expected[0]=8'h78;expected[1]=8'h30;expected[2]=8'h08;expected[3]=8'h82;
 #1000;rst=1;#1000;
 write_reg(9'h120,15);write_reg(9'h100,1);
 write_reg(9'h108,32'h178);write_reg(9'h108,32'h30);write_reg(9'h108,32'h08);write_reg(9'h108,32'h282);
 wait(stops==1);#1000;
 if(bytes_seen!=4)$fatal(1,"incomplete write");
 if(min_period<2540)$fatal(1,"SCCB frequency exceeds limit");
 $display("PASS_ACTUAL_AXI_IIC_WRITE_100KHZ_WITH_300NS_LINE_MODEL low_ns=%0.3f high_ns=%0.3f setup_ns=%0.3f period_ns=%0.3f",min_low,min_high,min_setup,min_period);
 $finish;
end
initial begin #2000000;$fatal(1,"bounded IIC simulation timeout");end
endmodule

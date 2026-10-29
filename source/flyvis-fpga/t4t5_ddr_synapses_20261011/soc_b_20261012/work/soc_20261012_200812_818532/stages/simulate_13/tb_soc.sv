`timescale 1ns/1ps
`define PS dut.b_soc_i.ps7.inst
`define ENG dut.b_soc_i.engine.inst
module tb_soc;
 import axi_vip_pkg::*;
 reg ps_clk_drive=0,por_drive=0,srst_drive=0;
 wire ps_clk=ps_clk_drive,por_n=por_drive,srst_n=srst_drive;
 always #15 ps_clk_drive=~ps_clk_drive;
 b_soc_wrapper dut(.FIXED_IO_0_ps_clk(ps_clk),.FIXED_IO_0_ps_porb(por_n),.FIXED_IO_0_ps_srstb(srst_n));
 // Only the native PS simulation memory latency changes for the timeout case.
 defparam dut.b_soc_i.ps7.inst.S_AXI_HP0.afi_rd_max=100000;
 localparam H=5768,S=16402,E=433880,WORDS=S+H;
 localparam BASE=32'h43c20000,DDR=32'h10000000;
 reg [31:0] requests[0:WORDS-1];reg [30:0] expected[0:H-1];reg [63:0] edges[0:E-1];
 reg [1023:0] packed_data,read_data;
 reg [63:0] retired_record[0:E-1];
 reg signed [30:0] retired_term[0:E-1];
 reg signed [49:0] retired_sum[0:E-1];
 axi_monitor_transaction observed_gp,observed_hp;
 integer gp_transactions=0,hp_transactions=0;
 reg [1:0] response;
 reg [31:0] value;
 integer i,j,n,checks=0,hp_beats=0,trace_edges=0,ar_bursts=0,control_stalls=0,DDR_stalls=0;
 integer reset_edges=0,summary,candidates_log,edges_log,timeout_wait;
 reg audit_full=0;
 reg [31:0] compute_cycles,reader_stalls;
 integer ticks=0,test_phase=0,progress_log;
 reg gp_hold=0,hp_hold=0,ar_hold=0;
 reg [31:0] held_gp;reg [63:0] held_hp;reg [31:0] held_ar;reg [3:0] held_arlen;
 axi_ready_gen gp_rready;
 wire clk=`ENG.clk;
 always @(posedge clk) begin
  ticks=ticks+1;
  if(ticks%10000==0)begin
   $fwrite(progress_log,"time=%0t test_phase=%0d flags=%h load=%0d received=%0d retired=%0d fifo=%0d AR=%b%b R=%b%b\n",$time,test_phase,`ENG.flags,`ENG.load_count,`ENG.received,trace_edges,`ENG.fifo_occupancy,`ENG.m_axi_arvalid,`ENG.m_axi_arready,`ENG.m_axi_rvalid,`ENG.m_axi_rready);
   $fflush(progress_log);
  end
  if(`ENG.rst_n)begin
   if(gp_hold&&(!`ENG.s_axi_rvalid||`ENG.s_axi_rdata!==held_gp))$fatal(1,"GP0 R instability");
   if(hp_hold&&(!`ENG.m_axi_rvalid||`ENG.m_axi_rdata!==held_hp))$fatal(1,"HP0 R instability");
   if(ar_hold&&(!`ENG.m_axi_arvalid||`ENG.m_axi_araddr!==held_ar||`ENG.m_axi_arlen!==held_arlen))$fatal(1,"HP0 AR instability");
   gp_hold=`ENG.s_axi_rvalid&&!`ENG.s_axi_rready;held_gp=`ENG.s_axi_rdata;
   hp_hold=`ENG.m_axi_rvalid&&!`ENG.m_axi_rready;held_hp=`ENG.m_axi_rdata;
   ar_hold=`ENG.m_axi_arvalid&&!`ENG.m_axi_arready;held_ar=`ENG.m_axi_araddr;held_arlen=`ENG.m_axi_arlen;
   if(gp_hold)control_stalls=control_stalls+1;
   if(hp_hold)DDR_stalls=DDR_stalls+1;
   if(`ENG.m_axi_arvalid&&`ENG.m_axi_arready)begin
    if(`ENG.m_axi_arid!=0||`ENG.m_axi_arsize!=3||`ENG.m_axi_arburst!=1||`ENG.m_axi_arlock!=0||`ENG.m_axi_arprot!=2)$fatal(1,"HP0 attributes");
    if({1'b0,`ENG.m_axi_araddr[11:0]}+8*(`ENG.m_axi_arlen+1)>4096)$fatal(1,"HP0 4K boundary");
    ar_bursts=ar_bursts+1;
    if(ar_bursts<=4)$display("B_SYSTEM_HP0_AR count=%0d address=%h time=%0t",ar_bursts,`ENG.m_axi_araddr,$time);
   end
   if(`ENG.m_axi_rvalid&&`ENG.m_axi_rready)begin
    if(audit_full&&(hp_beats>=E||`ENG.m_axi_rdata!==edges[hp_beats]||`ENG.m_axi_rresp!==0||`ENG.m_axi_rid!==0))$fatal(1,"HP0 ordered record mismatch %0d",hp_beats);
    hp_beats=hp_beats+1;
    if(hp_beats==1)$display("B_SYSTEM_HP0_FIRST_R time=%0t",$time);
   end
   if(`ENG.compute.trace_valid)begin
    if(audit_full)begin
     if(trace_edges>=E||`ENG.compute.core.trace_record!==edges[trace_edges])$fatal(1,"Retired edge order mismatch %0d",trace_edges);
     retired_record[trace_edges]=`ENG.compute.core.trace_record;
     retired_term[trace_edges]=`ENG.compute.trace_term;
     retired_sum[trace_edges]=`ENG.compute.trace_sum;
     if(trace_edges%65536==0)$display("B_SYSTEM_EDGE_PROGRESS retired=%0d time=%0t",trace_edges,$time);
    end
    trace_edges=trace_edges+1;
   end
  end else begin gp_hold=0;hp_hold=0;ar_hold=0;end
 end
 task automatic write_word(input [31:0] offset,input [31:0] data,input [1:0] want);
  reg [1:0] resp;
  begin `PS.write_data(BASE+offset,4,data,resp);if(resp!==want)$fatal(1,"GP0 WRITE %h response %b expected %b",offset,resp,want);checks=checks+1;end
 endtask
 task automatic read_word(input [31:0] offset,output [31:0] data,input [1:0] want);
  reg [1023:0] wide;reg [1:0] resp;
  begin `PS.read_data(BASE+offset,4,wide,resp);data=wide[31:0];if(resp!==want)$fatal(1,"GP0 READ %h response %b expected %b",offset,resp,want);checks=checks+1;end
 endtask
 task automatic read_burst_backpressured(input [31:0] offset,input integer count,output [1023:0] data,output [1:0] resp);
  axi_transaction transaction;
  axi_monitor_transaction observed;
  xil_axi_data_beat beat;
  integer k;
  begin
   // Use the same native GP0 VIP as PS.read_data, with one monitor consumer.
   // The convenience wrapper creates its own RREADY policy, so bypass only
   // that wrapper when deliberately testing control-channel backpressure.
   gp_rready=`PS.M_AXI_GP0.mst.rd_driver.create_ready("B_explicit_backpressure");
   gp_rready.set_ready_policy(XIL_AXI_READY_GEN_OSC);
   gp_rready.clr_use_variable_ranges();gp_rready.set_low_time(64);gp_rready.set_high_time(1);
   `PS.M_AXI_GP0.mst.rd_driver.send_rready(gp_rready);
   transaction=`PS.M_AXI_GP0.mst.rd_driver.create_transaction("B_explicit_GP0_read");
   transaction.set_read_cmd(BASE+offset,XIL_AXI_BURST_TYPE_INCR,12'hb00,count-1,XIL_AXI_SIZE_4BYTE);
   transaction.set_cache(0);transaction.set_prot(0);transaction.set_lock(XIL_AXI_ALOCK_NOLOCK);
   `PS.M_AXI_GP0.mst.rd_driver.send(transaction);
   `PS.M_AXI_GP0.mst.monitor.item_collected_port.get(observed);
   data=0;resp=0;
   for(k=0;k<count;k=k+1)begin beat=observed.get_data_beat(k);data[k*32+:32]=beat[31:0];resp=resp|observed.rresp[k];end
  end
 endtask
 task automatic reset_fabric;
  integer limit;
  begin
   // Native VIP implements each output reset_n as !reset_ctrl[bit].
   // Assert FCLK0 only; leave GP0/HP0 private reset bits deasserted.
   `PS.gen_rst.fpga_soft_reset(32'h00000001);
   repeat(80)@(posedge clk);
   if(`ENG.rst_n!==0||dut.b_soc_i.reset.peripheral_aresetn!==0)$fatal(1,"Actual BD reset not asserted");
   `PS.gen_rst.fpga_soft_reset(32'h00000000);
   limit=0;while(`ENG.rst_n!==1&&limit<1000)begin @(posedge clk);limit=limit+1;end
   if(`ENG.rst_n!==1)$fatal(1,"Actual BD reset polarity/release failed");
   reset_edges=reset_edges+limit;
   repeat(8)@(posedge clk);
  end
 endtask
 task automatic configure_and_load;
  integer index,k,count;reg [1023:0] payload;reg [1:0] resp;reg [31:0] loaded;
  begin
   write_word('h20,32'd17,0);write_word('h24,32'he1ca6d82,0);
   write_word('h28,DDR,0);write_word('h2c,32'h33341788,0);write_word('h30,32'h52f17c87,0);
   write_word('h18,1,0);
   for(index=0;index<WORDS;index=index+16)begin
    count=(WORDS-index<16)?WORDS-index:16;payload=0;
    for(k=0;k<count;k=k+1)payload[k*32+:32]=requests[index+k];
    `PS.write_data(BASE+'h1000+index*4,count*4,payload,resp);
    if(resp!==0)$fatal(1,"GP0 state load at %0d",index);
   end
   read_word('h64,loaded,0);if(loaded!=WORDS)$fatal(1,"Full state load count");
  end
 endtask
 initial begin
  progress_log=$fopen("system_progress.log","w");
  #300000000;$fatal(1,"System bounded simulation timeout");
 end
 initial begin
  $readmemh("rom/requests.mem",requests);$readmemh("rom/expected.mem",expected);$readmemh("rom/edges.mem",edges);
  #1000;por_drive=1;srst_drive=1;
  #1000;`PS.set_debug_level_info(0);`PS.set_stop_on_error(0);
  `PS.M_AXI_GP0.set_verbosity(0);`PS.S_AXI_HP0.set_verbosity(0);
  // Vendor analysis ports are enabled and use unbounded transaction queues.
  // Consume their observations; all native protocol assertions stay enabled.
  fork
   // GP0 convenience APIs consume their own monitor queue. Do not compete.
   begin forever begin `PS.S_AXI_HP0.slv.monitor.item_collected_port.get(observed_hp);hp_transactions=hp_transactions+1;observed_hp=null;end end
  join_none
  `PS.S_AXI_HP0.set_latency_type(0);
  reset_fabric();
  test_phase=1;
  $display("B_SYSTEM_RESET_RELEASE_PASS time=%0t",$time);
  read_word(0,value,0);if(value!==32'h46564231)$fatal(1,"GP0 ID response");
  read_word(8,value,0);if(value!=H)$fatal(1,"Actual production BD H_COUNT");
  read_word('hc,value,0);if(value!=S)$fatal(1,"Production source count");
  read_word('h10,value,0);if(value!=E)$fatal(1,"Production edge count");
  read_word('h18000,value,2);
  write_word('h18,2,2);read_word('h68,value,0);if(value!=0)$fatal(1,"Invalid START executed");
  reset_fabric();
  test_phase=2;
  read_burst_backpressured(0,16,read_data,response);
  if(response!==0||read_data[31:0]!==32'h46564231||read_data[95:64]!==H||control_stalls==0)$fatal(1,"Control backpressure probe failed: stalls=%0d",control_stalls);
  $display("B_SYSTEM_CONTROL_BACKPRESSURE_PASS stalls=%0d time=%0t",control_stalls,$time);
  // PS DDR model preload is stimulus only; all compute reads traverse real BD HP0.
  for(i=0;i<E;i=i+16)begin
   n=(E-i<16)?E-i:16;packed_data=0;
   for(j=0;j<n;j=j+1)packed_data[j*64+:64]=edges[i+j];
   `PS.write_mem(packed_data,DDR+8*i,n*8);
  end
  $display("B_SYSTEM_DDR_PRELOAD_COMPLETE records=%0d time=%0t",E,$time);
  test_phase=3;
  gp_rready=`PS.M_AXI_GP0.mst.rd_driver.create_ready("B_control_backpressure");
  gp_rready.set_ready_policy(XIL_AXI_READY_GEN_OSC);gp_rready.set_low_time(64);gp_rready.set_high_time(1);
  fork `PS.M_AXI_GP0.mst.rd_driver.send_rready(gp_rready);join_none
  configure_and_load();
  $display("B_SYSTEM_GP0_FULL_LOAD_COMPLETE words=%0d time=%0t",WORDS,$time);
  audit_full=1;
  test_phase=4;$display("B_SYSTEM_START_WRITE_BEGIN time=%0t",$time);
  write_word('h18,2,0);
  test_phase=5;$display("B_SYSTEM_START_WRITE_RESPONDED time=%0t",$time);
  value=0;timeout_wait=0;
  while(!value[1]&&timeout_wait<100000)begin repeat(1024)@(posedge clk);read_word('h1c,value,0);timeout_wait=timeout_wait+1;end
  if(!value[1]||!value[2])$fatal(1,"START/DONE/result valid not completed");
  read_word('h34,value,0);if(value!=0)$fatal(1,"Core error %h",value);
  read_word('h38,value,0);if(value!=0)$fatal(1,"Adapter error");
  read_word('h3c,value,0);if(value!=0)$fatal(1,"DDR transport error");
  read_word('h44,value,0);if(value!=E||trace_edges!=E||hp_beats!=E)$fatal(1,"Edge/DDR retirement count %0d %0d %0d",value,trace_edges,hp_beats);
  read_word('h48,value,0);if(value!=32'h33341788)$fatal(1,"Signature low");
  read_word('h4c,value,0);if(value!=32'h52f17c87)$fatal(1,"Signature high");
  read_word('h50,value,0);if(value!=17)$fatal(1,"Step identity");
  read_word('h54,value,0);if(value!=32'he1ca6d82)$fatal(1,"Old state identity");
  read_word('h68,value,0);if(value!=1)$fatal(1,"START duplicate");
  read_word('h40,compute_cycles,0);read_word('h5c,reader_stalls,0);
  audit_full=0;edges_log=$fopen("system_edges.csv","w");
  if(edges_log==0)$fatal(1,"Edge evidence file open failed");
  for(i=0;i<E;i=i+1)$fwrite(edges_log,"%0d,%016h,%0d,%0d,%0d,%0d\n",i,retired_record[i],retired_record[i][20:0],retired_record[i][48:36],$signed(retired_term[i]),$signed(retired_sum[i]));
  $fclose(edges_log);
  candidates_log=$fopen("system_candidates.csv","w");
  test_phase=6;
  for(i=0;i<H;i=i+16)begin
   n=(H-i<16)?H-i:16;
   if(i==0)read_burst_backpressured('h18000+4*i,n,read_data,response);
   else `PS.read_data(BASE+'h18000+4*i,n*4,read_data,response);
   if(response!==0)$fatal(1,"Candidate read response");
   for(j=0;j<n;j=j+1)begin
    if(read_data[j*32+:32]!=={expected[i+j][30],expected[i+j]})$fatal(1,"Candidate mismatch %0d",i+j);
    $fwrite(candidates_log,"%0d,%08h\n",i+j,read_data[j*32+:32]);
   end
  end
  $fclose(candidates_log);
  if(DDR_stalls==0||control_stalls==0)$fatal(1,"System backpressure not exercised: control=%0d DDR=%0d",control_stalls,DDR_stalls);
  $display("B_SYSTEM_FULL_REQUEST_PASS edges=%0d candidates=%0d control_stalls=%0d DDR_stalls=%0d",E,H,control_stalls,DDR_stalls);
  // Native PS model worst response latency exceeds the finite reader timeout.
  configure_and_load();`PS.S_AXI_HP0.set_latency_type(2);write_word('h18,2,0);
  test_phase=7;
  value=0;timeout_wait=0;
  while(!value[1]&&timeout_wait<20000)begin repeat(1024)@(posedge clk);read_word('h1c,value,0);timeout_wait=timeout_wait+1;end
  if(!value[1]||value[2])$fatal(1,"Timed out DDR request published result");
  read_word('h3c,value,0);if((value&32'h10)==0)$fatal(1,"DDR timeout not detected");
  read_word('h18000,value,2);
  // Do not end the test with accepted HP0 requests still outstanding.
  timeout_wait=0;value=8;
  while(value[3]&&timeout_wait<100000)begin repeat(1024)@(posedge clk);read_word('h1c,value,0);timeout_wait=timeout_wait+1;end
  if(value[3]||value[2]||trace_edges!=E)$fatal(1,"Timeout drain/invalid candidate failure");
  summary=$fopen("system_pass.txt","w");
  $fwrite(summary,"B_ACTUAL_BD_SYSTEM_SIMULATION_PASS\nH=%0d S=%0d E=%0d\nGP0_checks=%0d\nreset_release_edges=%0d\ncontrol_stalls=%0d DDR_stalls=%0d\ncompute_cycles=%0d reader_stalls=%0d\nordered_HP0_records=%0d ordered_retired_edges=%0d candidate_comparisons=%0d\ncandidate_mismatches=0\nvalid_REQUESTS=1 invalid_START_rejected=1 DDR_timeout_rejected=1\n",H,S,E,checks,reset_edges,control_stalls,DDR_stalls,compute_cycles,reader_stalls,E,E,H);
  $fclose(summary);
  $display("B_ACTUAL_BD_SYSTEM_SIMULATION_PASS");$finish;
 end
endmodule

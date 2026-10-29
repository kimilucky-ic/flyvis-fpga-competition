`timescale 1ns/1ps
// Independent B control/HP0 adapter; accepted compute RTL is unchanged.
module b_soc_engine #(parameter integer H_COUNT=5768,SOURCE_COUNT=16402,EDGE_COUNT=433880,WEIGHT_COUNT=645,AXI_TIMEOUT=65536,STEP_TIMEOUT=50000000)(
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, ASSOCIATED_BUSIF s_axi:m_axi, ASSOCIATED_RESET rst_n, FREQ_HZ 100000000" *)
    (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *)
    input wire clk,
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME rst_n, POLARITY ACTIVE_LOW" *)
    (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 rst_n RST" *)
    input wire rst_n,
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME s_axi, PROTOCOL AXI4LITE, DATA_WIDTH 32, ADDR_WIDTH 17, FREQ_HZ 100000000" *)
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi AWADDR" *)
    input wire [16:0] s_axi_awaddr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi AWPROT" *)
    input wire [2:0] s_axi_awprot,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi AWVALID" *)
    input wire s_axi_awvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi AWREADY" *)
    output wire s_axi_awready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi WDATA" *)
    input wire [31:0] s_axi_wdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi WSTRB" *)
    input wire [3:0] s_axi_wstrb,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi WVALID" *)
    input wire s_axi_wvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi WREADY" *)
    output wire s_axi_wready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi BRESP" *)
    output wire [1:0] s_axi_bresp,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi BVALID" *)
    output wire s_axi_bvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi BREADY" *)
    input wire s_axi_bready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi ARADDR" *)
    input wire [16:0] s_axi_araddr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi ARPROT" *)
    input wire [2:0] s_axi_arprot,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi ARVALID" *)
    input wire s_axi_arvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi ARREADY" *)
    output wire s_axi_arready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi RDATA" *)
    output wire [31:0] s_axi_rdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi RRESP" *)
    output wire [1:0] s_axi_rresp,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi RVALID" *)
    output wire s_axi_rvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 s_axi RREADY" *)
    input wire s_axi_rready,
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME m_axi, PROTOCOL AXI3, DATA_WIDTH 64, ADDR_WIDTH 32, ID_WIDTH 6, MAX_BURST_LENGTH 16, NUM_READ_OUTSTANDING 4, NUM_WRITE_OUTSTANDING 1, FREQ_HZ 100000000" *)
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi ARADDR" *)
    output wire [31:0] m_axi_araddr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi ARID" *)
    output wire [5:0] m_axi_arid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi ARLEN" *)
    output wire [3:0] m_axi_arlen,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi ARSIZE" *)
    output wire [2:0] m_axi_arsize,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi ARBURST" *)
    output wire [1:0] m_axi_arburst,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi ARLOCK" *)
    output wire [1:0] m_axi_arlock,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi ARCACHE" *)
    output wire [3:0] m_axi_arcache,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi ARPROT" *)
    output wire [2:0] m_axi_arprot,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi ARQOS" *)
    output wire [3:0] m_axi_arqos,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi ARVALID" *)
    output wire m_axi_arvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi ARREADY" *)
    input wire m_axi_arready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi RDATA" *)
    input wire [63:0] m_axi_rdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi RID" *)
    input wire [5:0] m_axi_rid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi RRESP" *)
    input wire [1:0] m_axi_rresp,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi RLAST" *)
    input wire m_axi_rlast,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi RVALID" *)
    input wire m_axi_rvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi RREADY" *)
    output wire m_axi_rready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi AWADDR" *)
    output wire [31:0] m_axi_awaddr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi AWID" *)
    output wire [5:0] m_axi_awid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi AWLEN" *)
    output wire [3:0] m_axi_awlen,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi AWSIZE" *)
    output wire [2:0] m_axi_awsize,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi AWBURST" *)
    output wire [1:0] m_axi_awburst,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi AWLOCK" *)
    output wire [1:0] m_axi_awlock,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi AWCACHE" *)
    output wire [3:0] m_axi_awcache,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi AWPROT" *)
    output wire [2:0] m_axi_awprot,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi AWQOS" *)
    output wire [3:0] m_axi_awqos,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi AWVALID" *)
    output wire m_axi_awvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi AWREADY" *)
    input wire m_axi_awready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi WDATA" *)
    output wire [63:0] m_axi_wdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi WSTRB" *)
    output wire [7:0] m_axi_wstrb,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi WID" *)
    output wire [5:0] m_axi_wid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi WLAST" *)
    output wire m_axi_wlast,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi WVALID" *)
    output wire m_axi_wvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi WREADY" *)
    input wire m_axi_wready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi BID" *)
    input wire [5:0] m_axi_bid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi BRESP" *)
    input wire [1:0] m_axi_bresp,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi BVALID" *)
    input wire m_axi_bvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 m_axi BREADY" *)
    output wire m_axi_bready
);

 localparam IDLE=0,ARMED=1,INPUT_DMA=2,RUN=3,OUTPUT_DMA=4,RESULT=5,FAILED=6;
 reg [3:0] phase;
 reg aw_pending,w_pending,read_pending,bvalid,rvalid;
 reg [16:0] aw_addr,rd_addr;reg [31:0] w_data,rdata;reg [3:0] w_strb;
 reg [1:0] bresp,rresp;
 reg req_begin,start,load_start,store_start,done_sticky;
 reg [31:0] step_id,old_state_tag,base_addr,input_base,output_base,adapter_error,starts,finishes;
 reg [31:0] load_cycles,store_cycles,total_cycles;
 reg [63:0] expected_signature;
 wire core_busy,done,out_valid,reader_busy,reader_poisoned;
 wire [31:0] status,cycles,result_step_id,result_old_state_tag,edges_applied;
 wire [31:0] reader_error,received,stall_cycles,fifo_occupancy;
 wire [63:0] signature;
 wire load_busy,load_done,store_busy,store_done,in_we;
 wire [31:0] load_error,store_error,load_count,output_count,in_data;
 wire [15:0] in_addr;wire [12:0] out_addr;wire signed [31:0] out_data;
 wire active=(phase==INPUT_DMA||phase==RUN||phase==OUTPUT_DMA);
 wire transport_busy=load_busy||reader_busy||store_busy;
 wire busy=active||transport_busy;
 wire result_ok=phase==RESULT&&out_valid&&status==0&&reader_error==0&&adapter_error==0&&load_error==0&&store_error==0;
 wire [31:0] flags={24'd0,phase,transport_busy,result_ok,done_sticky,busy};
 wire can_config=!busy&&phase!=ARMED;
 wire abort_dma=adapter_error!=0;
 wire [31:0] c_araddr,l_araddr;wire [3:0] c_arlen,l_arlen;
 wire [2:0] c_arsize,l_arsize;wire [1:0] c_arburst,l_arburst;
 wire [5:0] c_arid,l_arid;wire c_arvalid,l_arvalid,c_rready,l_rready;
 // A load remains selected until all accepted read requests drain, even on error.
 wire select_load=load_busy||load_start||phase==INPUT_DMA;
 assign m_axi_araddr=select_load?l_araddr:c_araddr;assign m_axi_arlen=select_load?l_arlen:c_arlen;
 assign m_axi_arsize=3;assign m_axi_arburst=1;assign m_axi_arid=0;
 assign m_axi_arvalid=select_load?l_arvalid:c_arvalid;assign m_axi_rready=select_load?l_rready:c_rready;
 assign m_axi_arlock=0;assign m_axi_arcache=4'b0011;assign m_axi_arprot=2;assign m_axi_arqos=0;
 assign m_axi_awid=0;assign m_axi_awsize=3;assign m_axi_awburst=1;assign m_axi_awlock=0;
 assign m_axi_awcache=4'b0011;assign m_axi_awprot=2;assign m_axi_awqos=0;assign m_axi_wid=0;
 assign s_axi_awready=rst_n&&!aw_pending&&!bvalid;assign s_axi_wready=rst_n&&!w_pending&&!bvalid;
 assign s_axi_bvalid=bvalid;assign s_axi_bresp=bresp;
 assign s_axi_arready=rst_n&&!read_pending&&!rvalid;assign s_axi_rvalid=rvalid;
 assign s_axi_rdata=rdata;assign s_axi_rresp=rresp;
 ddr_state_loader #(.WORDS(SOURCE_COUNT+H_COUNT),.TIMEOUT(AXI_TIMEOUT)) loader(
  .clk(clk),.rst_n(rst_n),.start(load_start),.abort(abort_dma),.base_addr(input_base),
  .busy(load_busy),.done(load_done),.error(load_error),.words_written(load_count),.in_we(in_we),.in_addr(in_addr),.in_data(in_data),
  .araddr(l_araddr),.arlen(l_arlen),.arsize(l_arsize),.arburst(l_arburst),.arid(l_arid),
  .arvalid(l_arvalid),.arready(m_axi_arready&&select_load),.rdata(m_axi_rdata),.rresp(m_axi_rresp),.rid(m_axi_rid),
  .rlast(m_axi_rlast),.rvalid(m_axi_rvalid&&select_load),.rready(l_rready));
 ddr_synapse_top #(.H_COUNT(H_COUNT),.SOURCE_COUNT(SOURCE_COUNT),.EDGE_COUNT(EDGE_COUNT),
  .WEIGHT_COUNT(WEIGHT_COUNT),.FIFO_DEPTH(128),.AXI_TIMEOUT(AXI_TIMEOUT),.STEP_TIMEOUT(STEP_TIMEOUT)) compute(
  .clk(clk),.rst_n(rst_n),.req_begin(req_begin),.in_we(in_we),.start(start),.in_addr(in_addr),.in_data(in_data),
  .step_id(step_id),.old_state_tag(old_state_tag),.base_addr(base_addr),.expected_signature(expected_signature),
  .busy(core_busy),.done(done),.out_valid(out_valid),.status(status),.cycles(cycles),
  .result_step_id(result_step_id),.result_old_state_tag(result_old_state_tag),.edges_applied(edges_applied),.signature(signature),
  .out_addr(out_addr),.out_data(out_data),.trace_valid(),.trace_gid(),.trace_target(),.trace_term(),.trace_sum(),
  .araddr(c_araddr),.arlen(c_arlen),.arsize(c_arsize),.arburst(c_arburst),.arid(c_arid),
  .arvalid(c_arvalid),.arready(m_axi_arready&&!select_load),.rdata(m_axi_rdata),.rresp(m_axi_rresp),.rid(m_axi_rid),
  .rlast(m_axi_rlast),.rvalid(m_axi_rvalid&&!select_load),.rready(c_rready),.reader_busy(reader_busy),
  .reader_poisoned(reader_poisoned),.reader_error(reader_error),.received(received),.stall_cycles(stall_cycles),.fifo_occupancy(fifo_occupancy));
 ddr_candidate_writer #(.WORDS(H_COUNT),.TIMEOUT(AXI_TIMEOUT)) writer(
  .clk(clk),.rst_n(rst_n),.start(store_start),.abort(abort_dma),.base_addr(output_base),
  .busy(store_busy),.done(store_done),.error(store_error),.words_acked(output_count),.out_addr(out_addr),.out_data(out_data),
  .awaddr(m_axi_awaddr),.awlen(m_axi_awlen),.awvalid(m_axi_awvalid),.awready(m_axi_awready),
  .wdata(m_axi_wdata),.wstrb(m_axi_wstrb),.wlast(m_axi_wlast),.wvalid(m_axi_wvalid),.wready(m_axi_wready),
  .bid(m_axi_bid),.bresp(m_axi_bresp),.bvalid(m_axi_bvalid),.bready(m_axi_bready));
 function automatic valid_range(input [31:0] base,input integer bytes);
  valid_range=base[2:0]==0&&({1'b0,base}+bytes)<=33'h40000000;
 endfunction
 function automatic overlap(input [31:0] a,input integer asize,input [31:0] b,input integer bsize);
  overlap=({1'b0,a}<{1'b0,b}+bsize)&&({1'b0,b}<{1'b0,a}+asize);
 endfunction
 wire addresses_ok=valid_range(base_addr,8*EDGE_COUNT)&&valid_range(input_base,4*(SOURCE_COUNT+H_COUNT))&&valid_range(output_base,4*H_COUNT)&&
  !overlap(base_addr,8*EDGE_COUNT,input_base,4*(SOURCE_COUNT+H_COUNT))&&
  !overlap(base_addr,8*EDGE_COUNT,output_base,4*H_COUNT)&&!overlap(input_base,4*(SOURCE_COUNT+H_COUNT),output_base,4*H_COUNT);
 function automatic [31:0] register_data(input [16:0] addr);
  case(addr)
   'h00:register_data=32'h46564232; 'h04:register_data=2;
   'h08:register_data=H_COUNT;'h0c:register_data=SOURCE_COUNT;'h10:register_data=EDGE_COUNT;'h14:register_data=WEIGHT_COUNT;
   'h1c:register_data=flags;'h20:register_data=step_id;'h24:register_data=old_state_tag;'h28:register_data=base_addr;
   'h2c:register_data=expected_signature[31:0];'h30:register_data=expected_signature[63:32];
   'h34:register_data=status;'h38:register_data=adapter_error;'h3c:register_data=reader_error;
   'h40:register_data=cycles;'h44:register_data=edges_applied;'h48:register_data=signature[31:0];'h4c:register_data=signature[63:32];
   'h50:register_data=result_step_id;'h54:register_data=result_old_state_tag;'h58:register_data=received;
   'h5c:register_data=stall_cycles;'h60:register_data=fifo_occupancy;'h64:register_data=load_count;
   'h68:register_data=starts;'h6c:register_data=finishes;'h70:register_data=AXI_TIMEOUT;'h74:register_data=STEP_TIMEOUT;
   'h78:register_data={31'd0,reader_poisoned};'h80:register_data=input_base;'h84:register_data=output_base;
   'h88:register_data=load_error;'h8c:register_data=store_error;'h90:register_data=load_cycles;
   'h94:register_data=store_cycles;'h98:register_data=total_cycles;'h9c:register_data=output_count;
   default:register_data=0;
  endcase
 endfunction
 always @(posedge clk)begin
  if(!rst_n)begin
   phase<=IDLE;aw_pending<=0;w_pending<=0;read_pending<=0;bvalid<=0;rvalid<=0;
   aw_addr<=0;rd_addr<=0;w_data<=0;rdata<=0;w_strb<=0;bresp<=0;rresp<=0;
   req_begin<=0;start<=0;load_start<=0;store_start<=0;done_sticky<=0;
   step_id<=0;old_state_tag<=0;base_addr<=0;input_base<=0;output_base<=0;expected_signature<=0;
   adapter_error<=0;starts<=0;finishes<=0;load_cycles<=0;store_cycles<=0;total_cycles<=0;
  end else begin
   req_begin<=0;start<=0;load_start<=0;store_start<=0;
   if(active)total_cycles<=total_cycles+1;
   if(phase==INPUT_DMA)load_cycles<=load_cycles+1;
   if(phase==OUTPUT_DMA)store_cycles<=store_cycles+1;
   if(bvalid&&s_axi_bready)bvalid<=0;if(rvalid&&s_axi_rready)rvalid<=0;
   if(s_axi_awvalid&&s_axi_awready)begin aw_pending<=1;aw_addr<=s_axi_awaddr;end
   if(s_axi_wvalid&&s_axi_wready)begin w_pending<=1;w_data<=s_axi_wdata;w_strb<=s_axi_wstrb;end
   if(phase==INPUT_DMA&&!load_start)begin
    if(load_error!=0||adapter_error!=0)begin phase<=FAILED;done_sticky<=1;finishes<=finishes+1;end
    else if(load_done)begin
     if(load_count!=SOURCE_COUNT+H_COUNT)begin adapter_error[4]<=1;phase<=FAILED;done_sticky<=1;finishes<=finishes+1;end
     else begin start<=1;phase<=RUN;end
    end
   end
   if(phase==RUN&&done)begin
    if(status!=0||reader_error!=0||adapter_error!=0||!out_valid)begin phase<=FAILED;done_sticky<=1;finishes<=finishes+1;end
    else begin store_start<=1;phase<=OUTPUT_DMA;end
   end
   if(phase==OUTPUT_DMA&&!store_start)begin
    if(store_error!=0||adapter_error!=0)begin phase<=FAILED;done_sticky<=1;finishes<=finishes+1;end
    else if(store_done)begin
     done_sticky<=1;finishes<=finishes+1;
     if(output_count==H_COUNT)phase<=RESULT;else begin phase<=FAILED;adapter_error[5]<=1;end
    end
   end
   if(aw_pending&&w_pending&&!bvalid)begin
    aw_pending<=0;w_pending<=0;bvalid<=1;bresp<=0;
    if(aw_addr[1:0]!=0||w_strb!=15)begin bresp<=2;adapter_error[0]<=1;end
    else if(aw_addr=='h18)begin
     if(w_data==1&&!busy)begin
      req_begin<=1;phase<=ARMED;done_sticky<=0;adapter_error<=0;
      load_cycles<=0;store_cycles<=0;total_cycles<=0;
     end else if(w_data==2&&phase==ARMED&&adapter_error==0&&addresses_ok)begin
      load_start<=1;phase<=INPUT_DMA;done_sticky<=0;starts<=starts+1;
     end else if(w_data==4&&!busy)done_sticky<=0;
     else begin bresp<=2;adapter_error[1]<=1;end
    end else if(can_config&&((aw_addr>='h20&&aw_addr<='h30)||aw_addr=='h80||aw_addr=='h84))begin
     case(aw_addr)
      'h20:step_id<=w_data;'h24:old_state_tag<=w_data;'h28:base_addr<=w_data;
      'h2c:expected_signature[31:0]<=w_data;'h30:expected_signature[63:32]<=w_data;
      'h80:input_base<=w_data;'h84:output_base<=w_data;
     endcase
    end else begin bresp<=2;adapter_error[2]<=1;end
   end
   if(s_axi_arvalid&&s_axi_arready)begin read_pending<=1;rd_addr<=s_axi_araddr;end
   if(read_pending)begin
    read_pending<=0;rvalid<=1;rresp<=0;rdata<=0;
    if(rd_addr[1:0]!=0||rd_addr>='ha0)rresp<=2;else rdata<=register_data(rd_addr);
   end
  end
 end
endmodule


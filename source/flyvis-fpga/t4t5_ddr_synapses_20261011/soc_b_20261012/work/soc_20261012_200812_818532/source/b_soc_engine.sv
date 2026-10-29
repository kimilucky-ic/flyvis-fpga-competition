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

    localparam IDLE=0,LOAD=1,RUN=2,RESULT=3,FAILED=4;
    reg [3:0] phase;
    reg aw_pending,w_pending,read_pending;
    reg [16:0] aw_addr,rd_addr;
    reg [31:0] w_data;
    reg [3:0] w_strb;
    reg [1:0] read_wait;
    reg bvalid,rvalid;
    reg [1:0] bresp,rresp;
    reg [31:0] rdata,adapter_error,load_count,starts,finishes;
    reg req_begin,start,in_we,done_sticky;
    reg [15:0] in_addr;
    reg [31:0] in_data,step_id,old_state_tag,base_addr;
    reg [63:0] expected_signature;
    wire busy,done,out_valid,reader_busy,reader_poisoned;
    wire [31:0] status,cycles,result_step_id,result_old_state_tag,edges_applied;
    wire [31:0] reader_error,received,stall_cycles,fifo_occupancy;
    wire [63:0] signature;
    wire signed [31:0] out_data;
    wire [12:0] out_addr=(rd_addr-17'h18000)>>2;
    wire result_ok=phase==RESULT&&out_valid&&status==0&&reader_error==0&&adapter_error==0;
    wire [31:0] flags={24'd0,phase,reader_busy,result_ok,done_sticky,busy};
    assign s_axi_awready=rst_n&&!aw_pending&&!bvalid;
    assign s_axi_wready=rst_n&&!w_pending&&!bvalid;
    assign s_axi_bvalid=bvalid;assign s_axi_bresp=bresp;
    assign s_axi_arready=rst_n&&!read_pending&&!rvalid;
    assign s_axi_rvalid=rvalid;assign s_axi_rresp=rresp;assign s_axi_rdata=rdata;
    assign m_axi_arlock=0;assign m_axi_arcache=4'b0011;
    assign m_axi_arprot=3'b010;assign m_axi_arqos=0;
    // Read-only HP0 master. Unused write channels remain inactive.
    assign m_axi_awaddr=0;assign m_axi_awid=0;assign m_axi_awlen=0;
    assign m_axi_awsize=3'd3;assign m_axi_awburst=2'b01;assign m_axi_awlock=0;
    assign m_axi_awcache=0;assign m_axi_awprot=3'b010;assign m_axi_awqos=0;
    assign m_axi_awvalid=0;assign m_axi_wdata=0;assign m_axi_wstrb=0;
    assign m_axi_wid=0;assign m_axi_wlast=0;assign m_axi_wvalid=0;assign m_axi_bready=1;
    ddr_synapse_top #(.H_COUNT(H_COUNT),.SOURCE_COUNT(SOURCE_COUNT),.EDGE_COUNT(EDGE_COUNT),
        .WEIGHT_COUNT(WEIGHT_COUNT),.FIFO_DEPTH(128),.AXI_TIMEOUT(AXI_TIMEOUT),.STEP_TIMEOUT(STEP_TIMEOUT)) compute(
        .clk(clk),.rst_n(rst_n),.req_begin(req_begin),.in_we(in_we),.start(start),.in_addr(in_addr),.in_data(in_data),
        .step_id(step_id),.old_state_tag(old_state_tag),.base_addr(base_addr),.expected_signature(expected_signature),
        .busy(busy),.done(done),.out_valid(out_valid),.status(status),.cycles(cycles),
        .result_step_id(result_step_id),.result_old_state_tag(result_old_state_tag),.edges_applied(edges_applied),.signature(signature),
        .out_addr(out_addr),.out_data(out_data),.trace_valid(),.trace_gid(),.trace_target(),.trace_term(),.trace_sum(),
        .araddr(m_axi_araddr),.arlen(m_axi_arlen),.arsize(m_axi_arsize),.arburst(m_axi_arburst),.arid(m_axi_arid),
        .arvalid(m_axi_arvalid),.arready(m_axi_arready),.rdata(m_axi_rdata),.rresp(m_axi_rresp),.rid(m_axi_rid),
        .rlast(m_axi_rlast),.rvalid(m_axi_rvalid),.rready(m_axi_rready),.reader_busy(reader_busy),
        .reader_poisoned(reader_poisoned),.reader_error(reader_error),.received(received),.stall_cycles(stall_cycles),.fifo_occupancy(fifo_occupancy));
    function automatic [31:0] register_data(input [16:0] addr);
        case(addr)
            17'h00000:register_data=32'h46564231;
            17'h00004:register_data=1;
            17'h00008:register_data=H_COUNT;
            17'h0000c:register_data=SOURCE_COUNT;
            17'h00010:register_data=EDGE_COUNT;
            17'h00014:register_data=WEIGHT_COUNT;
            17'h0001c:register_data=flags;
            17'h00020:register_data=step_id;
            17'h00024:register_data=old_state_tag;
            17'h00028:register_data=base_addr;
            17'h0002c:register_data=expected_signature[31:0];
            17'h00030:register_data=expected_signature[63:32];
            17'h00034:register_data=status;
            17'h00038:register_data=adapter_error;
            17'h0003c:register_data=reader_error;
            17'h00040:register_data=cycles;
            17'h00044:register_data=edges_applied;
            17'h00048:register_data=signature[31:0];
            17'h0004c:register_data=signature[63:32];
            17'h00050:register_data=result_step_id;
            17'h00054:register_data=result_old_state_tag;
            17'h00058:register_data=received;
            17'h0005c:register_data=stall_cycles;
            17'h00060:register_data=fifo_occupancy;
            17'h00064:register_data=load_count;
            17'h00068:register_data=starts;
            17'h0006c:register_data=finishes;
            17'h00070:register_data=AXI_TIMEOUT;
            17'h00074:register_data=STEP_TIMEOUT;
            17'h00078:register_data={31'd0,reader_poisoned};
            default:register_data=0;
        endcase
    endfunction
    always @(posedge clk) begin
        if(!rst_n) begin
            phase<=IDLE;aw_pending<=0;w_pending<=0;read_pending<=0;
            aw_addr<=0;rd_addr<=0;w_data<=0;w_strb<=0;read_wait<=0;
            bvalid<=0;bresp<=0;rvalid<=0;rresp<=0;rdata<=0;
            req_begin<=0;start<=0;in_we<=0;done_sticky<=0;adapter_error<=0;
            in_addr<=0;in_data<=0;load_count<=0;starts<=0;finishes<=0;
            step_id<=0;old_state_tag<=0;base_addr<=0;expected_signature<=0;
        end else begin
            req_begin<=0;start<=0;in_we<=0;
            if(bvalid&&s_axi_bready)bvalid<=0;
            if(rvalid&&s_axi_rready)rvalid<=0;
            if(s_axi_awvalid&&s_axi_awready)begin aw_pending<=1;aw_addr<=s_axi_awaddr;end
            if(s_axi_wvalid&&s_axi_wready)begin w_pending<=1;w_data<=s_axi_wdata;w_strb<=s_axi_wstrb;end
            if(done)begin done_sticky<=1;finishes<=finishes+1;phase<=status!=0||reader_error!=0||adapter_error!=0?FAILED:RESULT;end
            if(aw_pending&&w_pending&&!bvalid) begin
                aw_pending<=0;w_pending<=0;bvalid<=1;bresp<=0;
                if(aw_addr[1:0]!=0||w_strb!=4'hf) begin bresp<=2;adapter_error<=adapter_error|1;end
                else if(aw_addr==17'h18) begin
                    if(w_data==1&&!busy&&!reader_busy) begin
                        req_begin<=1;phase<=LOAD;load_count<=0;done_sticky<=0;adapter_error<=0;
                    end else if(w_data==2&&phase==LOAD&&load_count==SOURCE_COUNT+H_COUNT&&adapter_error==0&&status==0&&base_addr[2:0]==0) begin
                        start<=1;phase<=RUN;done_sticky<=0;starts<=starts+1;
                    end else if(w_data==4)done_sticky<=0;
                    else begin bresp<=2;adapter_error<=adapter_error|2;end
                end else if(aw_addr>=17'h1000&&aw_addr<17'h1000+4*(SOURCE_COUNT+H_COUNT)) begin
                    if(phase!=LOAD||adapter_error!=0||((aw_addr-17'h1000)>>2)!=load_count||w_data[31]!=w_data[30])begin bresp<=2;adapter_error<=adapter_error|4;end
                    else begin in_we<=1;in_addr<=load_count[15:0];in_data<=w_data;load_count<=load_count+1;end
                end else if(aw_addr>=17'h20&&aw_addr<=17'h30&&phase!=LOAD&&phase!=RUN&&!busy&&!reader_busy) begin
                    case(aw_addr)
                        17'h20:step_id<=w_data;
                        17'h24:old_state_tag<=w_data;
                        17'h28:base_addr<=w_data;
                        17'h2c:expected_signature[31:0]<=w_data;
                        17'h30:expected_signature[63:32]<=w_data;
                    endcase
                end else begin bresp<=2;adapter_error<=adapter_error|8;end
            end
            if(s_axi_arvalid&&s_axi_arready)begin read_pending<=1;rd_addr<=s_axi_araddr;read_wait<=2;end
            if(read_pending)begin
                if(read_wait!=0)read_wait<=read_wait-1;
                else begin
                    read_pending<=0;rvalid<=1;rresp<=0;rdata<=0;
                    if(rd_addr[1:0]!=0)rresp<=2;
                    else if(rd_addr>=17'h18000&&rd_addr<17'h18000+4*H_COUNT) begin
                        if(result_ok)rdata<=out_data;else rresp<=2;
                    end else if(rd_addr<17'h80)rdata<=register_data(rd_addr);
                    else rresp<=2;
                end
            end
        end
    end
endmodule

// Independent candidate. GP0 controls/input; HP0 writes immutable audit records.
// No display ACK gates computation. No software/GPU neural fallback.
module flyvis_ddr_soc_ip(
    (* X_INTERFACE_INFO="xilinx.com:signal:clock:1.0 aclk CLK" *)
    (* X_INTERFACE_PARAMETER="XIL_INTERFACENAME aclk, ASSOCIATED_BUSIF S_AXI:M_AXI, ASSOCIATED_RESET aresetn, FREQ_HZ 100000000" *) input wire aclk,
    (* X_INTERFACE_INFO="xilinx.com:signal:reset:1.0 aresetn RST" *)
    (* X_INTERFACE_PARAMETER="XIL_INTERFACENAME aresetn, POLARITY ACTIVE_LOW" *) input wire aresetn,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI AWADDR" *)
    (* X_INTERFACE_PARAMETER="XIL_INTERFACENAME S_AXI, PROTOCOL AXI4LITE, DATA_WIDTH 32, ADDR_WIDTH 12, READ_WRITE_MODE READ_WRITE, HAS_BURST 0, NUM_READ_OUTSTANDING 1, NUM_WRITE_OUTSTANDING 1, FREQ_HZ 100000000" *) input wire [11:0] s_axi_awaddr,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI AWPROT" *) input wire [2:0] s_axi_awprot,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI AWVALID" *) input wire s_axi_awvalid,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI AWREADY" *) output wire s_axi_awready,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI WDATA" *) input wire [31:0] s_axi_wdata,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI WSTRB" *) input wire [3:0] s_axi_wstrb,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI WVALID" *) input wire s_axi_wvalid,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI WREADY" *) output wire s_axi_wready,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI BRESP" *) output logic [1:0] s_axi_bresp,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI BVALID" *) output logic s_axi_bvalid,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI BREADY" *) input wire s_axi_bready,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI ARADDR" *) input wire [11:0] s_axi_araddr,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI ARPROT" *) input wire [2:0] s_axi_arprot,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI ARVALID" *) input wire s_axi_arvalid,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI ARREADY" *) output wire s_axi_arready,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI RDATA" *) output logic [31:0] s_axi_rdata,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI RRESP" *) output logic [1:0] s_axi_rresp,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI RVALID" *) output logic s_axi_rvalid,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 S_AXI RREADY" *) input wire s_axi_rready,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI AWADDR" *)
    (* X_INTERFACE_PARAMETER="XIL_INTERFACENAME M_AXI, PROTOCOL AXI4, DATA_WIDTH 64, ADDR_WIDTH 32, ID_WIDTH 4, READ_WRITE_MODE WRITE_ONLY, MAX_BURST_LENGTH 16, NUM_READ_OUTSTANDING 1, NUM_WRITE_OUTSTANDING 1, FREQ_HZ 100000000" *) output wire [31:0] m_axi_awaddr,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI AWID" *) output wire [3:0] m_axi_awid,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI AWLEN" *) output wire [7:0] m_axi_awlen,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI AWSIZE" *) output wire [2:0] m_axi_awsize,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI AWBURST" *) output wire [1:0] m_axi_awburst,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI AWLOCK" *) output wire m_axi_awlock,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI AWCACHE" *) output wire [3:0] m_axi_awcache,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI AWPROT" *) output wire [2:0] m_axi_awprot,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI AWQOS" *) output wire [3:0] m_axi_awqos,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI AWVALID" *) output wire m_axi_awvalid,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI AWREADY" *) input wire m_axi_awready,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI WDATA" *) output wire [63:0] m_axi_wdata,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI WSTRB" *) output wire [7:0] m_axi_wstrb,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI WLAST" *) output wire m_axi_wlast,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI WVALID" *) output wire m_axi_wvalid,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI WREADY" *) input wire m_axi_wready,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI BID" *) input wire [3:0] m_axi_bid,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI BRESP" *) input wire [1:0] m_axi_bresp,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI BVALID" *) input wire m_axi_bvalid,
    (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 M_AXI BREADY" *) output wire m_axi_bready
);
    localparam integer N=45669,NE=1513231,STRIDE=188416;
    wire reset=!aresetn;
    logic aw_pending,w_pending;
    logic [11:0] awaddr;
    logic [31:0] wdata;
    logic [3:0] wstrb;
    logic [31:0] cfg_base,cfg_end,cfg_first,cfg_cookie;
    logic [15:0] cfg_slots;
    logic [9:0] loaded,feed_index;
    (* ram_style="block" *) logic [31:0] frame[0:720];
    logic [31:0] frame_q;
    logic [1:0] feed;
    localparam logic [1:0] F_IDLE=0,F_READ=1,F_SEND=2;
    logic running;
    wire busy,clean,configured,full,engine_cfg_ready,begin_ready,restore_ready,input_ready;
    wire publish,neural_done;
    wire [31:0] published_base,published_frame,neural_cycles;
    wire [15:0] committed;
    wire [7:0] errors;
    logic [31:0] rejected;
    logic [31:0] live_seq,live_base,live_frame,live_cycles;
    logic [31:0] snap_seq,snap_base,snap_frame,snap_cycles,snap_cookie,snap_errors;
    wire control_busy=busy||running;
    wire wr_fire=aw_pending&&w_pending&&!s_axi_bvalid;
    logic wr_ok;
    wire restore_cmd=wr_fire&&wr_ok&&awaddr==0&&wdata==2;
    wire configure_cmd=wr_fire&&wr_ok&&awaddr==0&&wdata==4;
    wire start_cmd=wr_fire&&wr_ok&&awaddr==0&&wdata==1;
    wire latch_cmd=wr_fire&&wr_ok&&awaddr==0&&wdata==8;
    wire input_write=wr_fire&&wr_ok&&awaddr>=12'h400;
    assign s_axi_awready=!aw_pending&&!s_axi_bvalid;
    assign s_axi_wready=!w_pending&&!s_axi_bvalid;
    assign s_axi_arready=!s_axi_rvalid;
    assign m_axi_awid=0;assign m_axi_awlock=0;assign m_axi_awcache=4'b0011;
    assign m_axi_awprot=0;assign m_axi_awqos=0;

    always_comb begin
        wr_ok=0;
        if(wstrb==15&&awaddr[1:0]==0) begin
            if(awaddr==0&&wdata==8) wr_ok=live_seq!=0;
            else if(!control_busy) case(awaddr)
                0:case(wdata)
                    1:wr_ok=loaded==721&&begin_ready&&errors==0;
                    2:wr_ok=restore_ready;
                    4:wr_ok=engine_cfg_ready&&cfg_slots!=0&&cfg_base[11:0]==0&&
                        cfg_base>=32'h00100000&&cfg_end<=32'h40000000&&
                        {1'b0,cfg_base}+STRIDE<={1'b0,cfg_end}&&
                        {1'b0,cfg_first}+33'(cfg_slots)<=33'h100000000;
                    default:wr_ok=0;
                endcase
                12'h004,12'h008,12'h01c,12'h02c:wr_ok=!configured;
                12'h00c:wr_ok=!configured&&wdata>0&&wdata<=65535;
                default:wr_ok=awaddr>=12'h400&&awaddr<=12'hf40&&loaded<721&&
                    awaddr==12'h400+12'(loaded*4);
            endcase
        end
    end
    function automatic logic readable(input logic [11:0] addr);
        case(addr)
            12'h004,12'h008,12'h00c,12'h010,12'h014,12'h018,12'h01c,
            12'h020,12'h024,12'h028,12'h02c,12'h030,12'h034,12'h038,
            12'h03c,12'h040,12'h080,12'h084,12'h088,12'h08c,12'h090,
            12'h094,12'h098,12'h09c,12'h0a0:readable=1;
            default:readable=0;
        endcase
    endfunction
    function automatic logic [31:0] value(input logic [11:0] addr);
        case(addr)
            12'h004:value=cfg_base;12'h008:value=cfg_end;12'h00c:value={16'b0,cfg_slots};
            12'h010:value={25'b0,(errors!=0),(live_seq!=0),(loaded==721),full,configured,clean,control_busy};
            12'h014:value={16'b0,committed};12'h018:value={22'b0,loaded};12'h01c:value=cfg_first;
            12'h020:value=live_cycles;12'h024:value={24'b0,errors};12'h028:value=rejected;
            12'h02c:value=cfg_cookie;12'h030:value=N;12'h034:value=NE;12'h038:value=32'h00110004;
            12'h03c:value=STRIDE;12'h040:value=cfg_first+{16'b0,committed};
            12'h080:value=snap_seq;12'h084:value=snap_base;12'h088:value=snap_frame;
            12'h08c:value=snap_cycles;12'h090:value=snap_seq;12'h094:value=snap_cookie;
            12'h098:value=snap_errors;12'h09c:value=N;12'h0a0:value=NE;
            default:value=0;
        endcase
    endfunction
    always_ff @(posedge aclk) begin
        if(!reset) begin
            if(input_write) frame[loaded]<=wdata;
            if(feed==F_READ) frame_q<=frame[feed_index];
        end
        if(reset) begin
            aw_pending<=0;w_pending<=0;awaddr<=0;wdata<=0;wstrb<=0;
            s_axi_bvalid<=0;s_axi_bresp<=0;s_axi_rvalid<=0;s_axi_rdata<=0;s_axi_rresp<=0;
            cfg_base<=0;cfg_end<=0;cfg_first<=0;cfg_cookie<=0;cfg_slots<=0;
            loaded<=0;feed_index<=0;feed<=F_IDLE;running<=0;rejected<=0;
            live_seq<=0;live_base<=0;live_frame<=0;live_cycles<=0;
            snap_seq<=0;snap_base<=0;snap_frame<=0;snap_cycles<=0;snap_cookie<=0;snap_errors<=0;
        end else begin
            if(s_axi_awvalid&&s_axi_awready) begin aw_pending<=1;awaddr<=s_axi_awaddr;end
            if(s_axi_wvalid&&s_axi_wready) begin w_pending<=1;wdata<=s_axi_wdata;wstrb<=s_axi_wstrb;end
            if(s_axi_bvalid&&s_axi_bready) s_axi_bvalid<=0;
            if(wr_fire) begin
                aw_pending<=0;w_pending<=0;s_axi_bvalid<=1;s_axi_bresp<=wr_ok?0:2;
                if(!wr_ok) rejected<=rejected+1;
                else case(awaddr)
                    12'h004:cfg_base<=wdata;12'h008:cfg_end<=wdata;12'h00c:cfg_slots<=wdata[15:0];
                    12'h01c:cfg_first<=wdata;12'h02c:cfg_cookie<=wdata;
                    default:begin end
                endcase
            end
            if(s_axi_rvalid&&s_axi_rready) s_axi_rvalid<=0;
            if(s_axi_arvalid&&s_axi_arready) begin
                s_axi_rvalid<=1;s_axi_rdata<=value(s_axi_araddr);s_axi_rresp<=readable(s_axi_araddr)?0:2;
            end
            if(input_write) loaded<=loaded+1'b1;
            if(restore_cmd) loaded<=0;
            if(start_cmd) begin running<=1;loaded<=0;feed_index<=0;feed<=F_READ;end
            case(feed)
                F_READ:feed<=F_SEND;
                F_SEND:if(input_ready) begin
                    if(feed_index==720) feed<=F_IDLE;
                    else begin feed_index<=feed_index+1'b1;feed<=F_READ;end
                end
                default:begin end
            endcase
            if(publish) begin
                running<=0;live_seq<={16'b0,committed};live_base<=published_base;
                live_frame<=published_frame;live_cycles<=neural_cycles;
            end
            // Nonblocking assignments intentionally capture ONE old live epoch
            // even if a new publication occurs on this same clock edge.
            if(latch_cmd) begin
                snap_seq<=live_seq;snap_base<=live_base;snap_frame<=live_frame;snap_cycles<=live_cycles;
                snap_cookie<=cfg_cookie;snap_errors<={24'b0,errors};
            end
        end
    end
    flyvis_ddr_snapshot_top #(
        .META_FILE("C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/meta.hex"),
        .MAP_FILE("C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/map.hex"),
        .ROWS_FILE("C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/rows.hex"),
        .STATE_FILE("C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/initial.hex")) engine(
        .clk(aclk),.reset,.restore_req(restore_cmd),.restore_ready,.state_clean(clean),
        .cfg_valid(configure_cmd),.cfg_ready(engine_cfg_ready),.cfg_base,.cfg_end,.cfg_first_frame(cfg_first),.cfg_slots,
        .begin_valid(start_cmd),.begin_ready,.input_valid(feed==F_SEND),.input_ready,.input_bits(frame_q),
        .busy,.capacity_exhausted(full),.configured,.publish,.published_base,.published_frame,.committed_count(committed),
        .error_flags(errors),.trace_edge(),.trace_eid(),.trace_src(),.trace_dst(),.trace_weight(),
        .neural_done,.neural_cycles,.m_axi_awaddr,.m_axi_awlen,.m_axi_awsize,.m_axi_awburst,.m_axi_awvalid,.m_axi_awready,
        .m_axi_wdata,.m_axi_wstrb,.m_axi_wlast,.m_axi_wvalid,.m_axi_wready,
        .m_axi_bresp(m_axi_bid==0?m_axi_bresp:2'b10),.m_axi_bvalid,.m_axi_bready);
endmodule

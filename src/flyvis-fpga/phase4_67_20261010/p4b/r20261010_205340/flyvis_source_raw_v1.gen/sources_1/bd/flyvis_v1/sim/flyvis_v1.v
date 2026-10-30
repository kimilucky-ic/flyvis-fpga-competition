//Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
//Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
//--------------------------------------------------------------------------------
//Tool Version: Vivado v.2026.1.1 (win64) Build 6605303 Fri Sep 04 12:46:29 BST 2026
//Date        : Sat Oct 10 20:54:15 2026
//Host        : hope running 64-bit major release  (build 9200)
//Command     : generate_target flyvis_v1.bd
//Design      : flyvis_v1
//Purpose     : IP block netlist
//--------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CORE_GENERATION_INFO = "flyvis_v1,IP_Integrator,{x_ipVendor=xilinx.com,x_ipLibrary=BlockDiagram,x_ipName=flyvis_v1,x_ipVersion=1.00.a,x_ipLanguage=VERILOG}" *) (* HW_HANDOFF = "flyvis_v1.hwdef" *) 
module flyvis_v1
   (DDR_addr,
    DDR_ba,
    DDR_cas_n,
    DDR_ck_n,
    DDR_ck_p,
    DDR_cke,
    DDR_cs_n,
    DDR_dm,
    DDR_dq,
    DDR_dqs_n,
    DDR_dqs_p,
    DDR_odt,
    DDR_ras_n,
    DDR_reset_n,
    DDR_we_n,
    FIXED_IO_ddr_vrn,
    FIXED_IO_ddr_vrp,
    FIXED_IO_mio,
    FIXED_IO_ps_clk,
    FIXED_IO_ps_porb,
    FIXED_IO_ps_srstb);
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR ADDR" *) (* X_INTERFACE_MODE = "Master" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME DDR, AXI_ARBITRATION_SCHEME TDM, BURST_LENGTH 8, CAN_DEBUG false, CAS_LATENCY 11, CAS_WRITE_LATENCY 11, CS_ENABLED true, DATA_MASK_ENABLED true, DATA_WIDTH 8, MEMORY_TYPE COMPONENTS, MEM_ADDR_MAP ROW_COLUMN_BANK, SLOT Single, TIMEPERIOD_PS 1250" *) inout [14:0]DDR_addr;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR BA" *) inout [2:0]DDR_ba;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR CAS_N" *) inout DDR_cas_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR CK_N" *) inout DDR_ck_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR CK_P" *) inout DDR_ck_p;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR CKE" *) inout DDR_cke;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR CS_N" *) inout DDR_cs_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR DM" *) inout [3:0]DDR_dm;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR DQ" *) inout [31:0]DDR_dq;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR DQS_N" *) inout [3:0]DDR_dqs_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR DQS_P" *) inout [3:0]DDR_dqs_p;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR ODT" *) inout DDR_odt;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR RAS_N" *) inout DDR_ras_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR RESET_N" *) inout DDR_reset_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR WE_N" *) inout DDR_we_n;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO DDR_VRN" *) (* X_INTERFACE_MODE = "Master" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME FIXED_IO, CAN_DEBUG false" *) inout FIXED_IO_ddr_vrn;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO DDR_VRP" *) inout FIXED_IO_ddr_vrp;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO MIO" *) inout [53:0]FIXED_IO_mio;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO PS_CLK" *) inout FIXED_IO_ps_clk;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO PS_PORB" *) inout FIXED_IO_ps_porb;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO PS_SRSTB" *) inout FIXED_IO_ps_srstb;

  wire [14:0]DDR_addr;
  wire [2:0]DDR_ba;
  wire DDR_cas_n;
  wire DDR_ck_n;
  wire DDR_ck_p;
  wire DDR_cke;
  wire DDR_cs_n;
  wire [3:0]DDR_dm;
  wire [31:0]DDR_dq;
  wire [3:0]DDR_dqs_n;
  wire [3:0]DDR_dqs_p;
  wire DDR_odt;
  wire DDR_ras_n;
  wire DDR_reset_n;
  wire DDR_we_n;
  wire FIXED_IO_ddr_vrn;
  wire FIXED_IO_ddr_vrp;
  wire [53:0]FIXED_IO_mio;
  wire FIXED_IO_ps_clk;
  wire FIXED_IO_ps_porb;
  wire FIXED_IO_ps_srstb;
  wire [31:0]cfg_ic_M00_AXI_ARADDR;
  wire cfg_ic_M00_AXI_ARREADY;
  wire cfg_ic_M00_AXI_ARVALID;
  wire [31:0]cfg_ic_M00_AXI_AWADDR;
  wire cfg_ic_M00_AXI_AWREADY;
  wire cfg_ic_M00_AXI_AWVALID;
  wire cfg_ic_M00_AXI_BREADY;
  wire [1:0]cfg_ic_M00_AXI_BRESP;
  wire cfg_ic_M00_AXI_BVALID;
  wire [31:0]cfg_ic_M00_AXI_RDATA;
  wire cfg_ic_M00_AXI_RREADY;
  wire [1:0]cfg_ic_M00_AXI_RRESP;
  wire cfg_ic_M00_AXI_RVALID;
  wire [31:0]cfg_ic_M00_AXI_WDATA;
  wire cfg_ic_M00_AXI_WREADY;
  wire [3:0]cfg_ic_M00_AXI_WSTRB;
  wire cfg_ic_M00_AXI_WVALID;
  wire [63:0]flyvis_h_m_axi_gmem0_ARADDR;
  wire [1:0]flyvis_h_m_axi_gmem0_ARBURST;
  wire [3:0]flyvis_h_m_axi_gmem0_ARCACHE;
  wire [0:0]flyvis_h_m_axi_gmem0_ARID;
  wire [7:0]flyvis_h_m_axi_gmem0_ARLEN;
  wire [1:0]flyvis_h_m_axi_gmem0_ARLOCK;
  wire [2:0]flyvis_h_m_axi_gmem0_ARPROT;
  wire [3:0]flyvis_h_m_axi_gmem0_ARQOS;
  wire flyvis_h_m_axi_gmem0_ARREADY;
  wire [3:0]flyvis_h_m_axi_gmem0_ARREGION;
  wire [2:0]flyvis_h_m_axi_gmem0_ARSIZE;
  wire flyvis_h_m_axi_gmem0_ARVALID;
  wire [63:0]flyvis_h_m_axi_gmem0_AWADDR;
  wire [1:0]flyvis_h_m_axi_gmem0_AWBURST;
  wire [3:0]flyvis_h_m_axi_gmem0_AWCACHE;
  wire [0:0]flyvis_h_m_axi_gmem0_AWID;
  wire [7:0]flyvis_h_m_axi_gmem0_AWLEN;
  wire [1:0]flyvis_h_m_axi_gmem0_AWLOCK;
  wire [2:0]flyvis_h_m_axi_gmem0_AWPROT;
  wire [3:0]flyvis_h_m_axi_gmem0_AWQOS;
  wire flyvis_h_m_axi_gmem0_AWREADY;
  wire [3:0]flyvis_h_m_axi_gmem0_AWREGION;
  wire [2:0]flyvis_h_m_axi_gmem0_AWSIZE;
  wire flyvis_h_m_axi_gmem0_AWVALID;
  wire [0:0]flyvis_h_m_axi_gmem0_BID;
  wire flyvis_h_m_axi_gmem0_BREADY;
  wire [1:0]flyvis_h_m_axi_gmem0_BRESP;
  wire flyvis_h_m_axi_gmem0_BVALID;
  wire [31:0]flyvis_h_m_axi_gmem0_RDATA;
  wire [0:0]flyvis_h_m_axi_gmem0_RID;
  wire flyvis_h_m_axi_gmem0_RLAST;
  wire flyvis_h_m_axi_gmem0_RREADY;
  wire [1:0]flyvis_h_m_axi_gmem0_RRESP;
  wire flyvis_h_m_axi_gmem0_RVALID;
  wire [31:0]flyvis_h_m_axi_gmem0_WDATA;
  wire flyvis_h_m_axi_gmem0_WLAST;
  wire flyvis_h_m_axi_gmem0_WREADY;
  wire [3:0]flyvis_h_m_axi_gmem0_WSTRB;
  wire flyvis_h_m_axi_gmem0_WVALID;
  wire [63:0]mem_ic_M00_AXI_ARADDR;
  wire [1:0]mem_ic_M00_AXI_ARBURST;
  wire [3:0]mem_ic_M00_AXI_ARCACHE;
  wire [3:0]mem_ic_M00_AXI_ARLEN;
  wire [1:0]mem_ic_M00_AXI_ARLOCK;
  wire [2:0]mem_ic_M00_AXI_ARPROT;
  wire [3:0]mem_ic_M00_AXI_ARQOS;
  wire mem_ic_M00_AXI_ARREADY;
  wire [2:0]mem_ic_M00_AXI_ARSIZE;
  wire mem_ic_M00_AXI_ARVALID;
  wire [63:0]mem_ic_M00_AXI_AWADDR;
  wire [1:0]mem_ic_M00_AXI_AWBURST;
  wire [3:0]mem_ic_M00_AXI_AWCACHE;
  wire [3:0]mem_ic_M00_AXI_AWLEN;
  wire [1:0]mem_ic_M00_AXI_AWLOCK;
  wire [2:0]mem_ic_M00_AXI_AWPROT;
  wire [3:0]mem_ic_M00_AXI_AWQOS;
  wire mem_ic_M00_AXI_AWREADY;
  wire [2:0]mem_ic_M00_AXI_AWSIZE;
  wire mem_ic_M00_AXI_AWVALID;
  wire mem_ic_M00_AXI_BREADY;
  wire [1:0]mem_ic_M00_AXI_BRESP;
  wire mem_ic_M00_AXI_BVALID;
  wire [63:0]mem_ic_M00_AXI_RDATA;
  wire mem_ic_M00_AXI_RLAST;
  wire mem_ic_M00_AXI_RREADY;
  wire [1:0]mem_ic_M00_AXI_RRESP;
  wire mem_ic_M00_AXI_RVALID;
  wire [63:0]mem_ic_M00_AXI_WDATA;
  wire mem_ic_M00_AXI_WLAST;
  wire mem_ic_M00_AXI_WREADY;
  wire [7:0]mem_ic_M00_AXI_WSTRB;
  wire mem_ic_M00_AXI_WVALID;
  wire ps7_FCLK_CLK0;
  wire ps7_FCLK_RESET0_N;
  wire [31:0]ps7_M_AXI_GP0_ARADDR;
  wire [1:0]ps7_M_AXI_GP0_ARBURST;
  wire [3:0]ps7_M_AXI_GP0_ARCACHE;
  wire [11:0]ps7_M_AXI_GP0_ARID;
  wire [3:0]ps7_M_AXI_GP0_ARLEN;
  wire [1:0]ps7_M_AXI_GP0_ARLOCK;
  wire [2:0]ps7_M_AXI_GP0_ARPROT;
  wire [3:0]ps7_M_AXI_GP0_ARQOS;
  wire ps7_M_AXI_GP0_ARREADY;
  wire [2:0]ps7_M_AXI_GP0_ARSIZE;
  wire ps7_M_AXI_GP0_ARVALID;
  wire [31:0]ps7_M_AXI_GP0_AWADDR;
  wire [1:0]ps7_M_AXI_GP0_AWBURST;
  wire [3:0]ps7_M_AXI_GP0_AWCACHE;
  wire [11:0]ps7_M_AXI_GP0_AWID;
  wire [3:0]ps7_M_AXI_GP0_AWLEN;
  wire [1:0]ps7_M_AXI_GP0_AWLOCK;
  wire [2:0]ps7_M_AXI_GP0_AWPROT;
  wire [3:0]ps7_M_AXI_GP0_AWQOS;
  wire ps7_M_AXI_GP0_AWREADY;
  wire [2:0]ps7_M_AXI_GP0_AWSIZE;
  wire ps7_M_AXI_GP0_AWVALID;
  wire [11:0]ps7_M_AXI_GP0_BID;
  wire ps7_M_AXI_GP0_BREADY;
  wire [1:0]ps7_M_AXI_GP0_BRESP;
  wire ps7_M_AXI_GP0_BVALID;
  wire [31:0]ps7_M_AXI_GP0_RDATA;
  wire [11:0]ps7_M_AXI_GP0_RID;
  wire ps7_M_AXI_GP0_RLAST;
  wire ps7_M_AXI_GP0_RREADY;
  wire [1:0]ps7_M_AXI_GP0_RRESP;
  wire ps7_M_AXI_GP0_RVALID;
  wire [31:0]ps7_M_AXI_GP0_WDATA;
  wire [11:0]ps7_M_AXI_GP0_WID;
  wire ps7_M_AXI_GP0_WLAST;
  wire ps7_M_AXI_GP0_WREADY;
  wire [3:0]ps7_M_AXI_GP0_WSTRB;
  wire ps7_M_AXI_GP0_WVALID;

  flyvis_v1_cfg_ic_0 cfg_ic
       (.ACLK(ps7_FCLK_CLK0),
        .ARESETN(ps7_FCLK_RESET0_N),
        .M00_ACLK(ps7_FCLK_CLK0),
        .M00_ARESETN(ps7_FCLK_RESET0_N),
        .M00_AXI_araddr(cfg_ic_M00_AXI_ARADDR),
        .M00_AXI_arready(cfg_ic_M00_AXI_ARREADY),
        .M00_AXI_arvalid(cfg_ic_M00_AXI_ARVALID),
        .M00_AXI_awaddr(cfg_ic_M00_AXI_AWADDR),
        .M00_AXI_awready(cfg_ic_M00_AXI_AWREADY),
        .M00_AXI_awvalid(cfg_ic_M00_AXI_AWVALID),
        .M00_AXI_bready(cfg_ic_M00_AXI_BREADY),
        .M00_AXI_bresp(cfg_ic_M00_AXI_BRESP),
        .M00_AXI_bvalid(cfg_ic_M00_AXI_BVALID),
        .M00_AXI_rdata(cfg_ic_M00_AXI_RDATA),
        .M00_AXI_rready(cfg_ic_M00_AXI_RREADY),
        .M00_AXI_rresp(cfg_ic_M00_AXI_RRESP),
        .M00_AXI_rvalid(cfg_ic_M00_AXI_RVALID),
        .M00_AXI_wdata(cfg_ic_M00_AXI_WDATA),
        .M00_AXI_wready(cfg_ic_M00_AXI_WREADY),
        .M00_AXI_wstrb(cfg_ic_M00_AXI_WSTRB),
        .M00_AXI_wvalid(cfg_ic_M00_AXI_WVALID),
        .S00_ACLK(ps7_FCLK_CLK0),
        .S00_ARESETN(ps7_FCLK_RESET0_N),
        .S00_AXI_araddr(ps7_M_AXI_GP0_ARADDR),
        .S00_AXI_arburst(ps7_M_AXI_GP0_ARBURST),
        .S00_AXI_arcache(ps7_M_AXI_GP0_ARCACHE),
        .S00_AXI_arid(ps7_M_AXI_GP0_ARID),
        .S00_AXI_arlen(ps7_M_AXI_GP0_ARLEN),
        .S00_AXI_arlock(ps7_M_AXI_GP0_ARLOCK),
        .S00_AXI_arprot(ps7_M_AXI_GP0_ARPROT),
        .S00_AXI_arqos(ps7_M_AXI_GP0_ARQOS),
        .S00_AXI_arready(ps7_M_AXI_GP0_ARREADY),
        .S00_AXI_arsize(ps7_M_AXI_GP0_ARSIZE),
        .S00_AXI_arvalid(ps7_M_AXI_GP0_ARVALID),
        .S00_AXI_awaddr(ps7_M_AXI_GP0_AWADDR),
        .S00_AXI_awburst(ps7_M_AXI_GP0_AWBURST),
        .S00_AXI_awcache(ps7_M_AXI_GP0_AWCACHE),
        .S00_AXI_awid(ps7_M_AXI_GP0_AWID),
        .S00_AXI_awlen(ps7_M_AXI_GP0_AWLEN),
        .S00_AXI_awlock(ps7_M_AXI_GP0_AWLOCK),
        .S00_AXI_awprot(ps7_M_AXI_GP0_AWPROT),
        .S00_AXI_awqos(ps7_M_AXI_GP0_AWQOS),
        .S00_AXI_awready(ps7_M_AXI_GP0_AWREADY),
        .S00_AXI_awsize(ps7_M_AXI_GP0_AWSIZE),
        .S00_AXI_awvalid(ps7_M_AXI_GP0_AWVALID),
        .S00_AXI_bid(ps7_M_AXI_GP0_BID),
        .S00_AXI_bready(ps7_M_AXI_GP0_BREADY),
        .S00_AXI_bresp(ps7_M_AXI_GP0_BRESP),
        .S00_AXI_bvalid(ps7_M_AXI_GP0_BVALID),
        .S00_AXI_rdata(ps7_M_AXI_GP0_RDATA),
        .S00_AXI_rid(ps7_M_AXI_GP0_RID),
        .S00_AXI_rlast(ps7_M_AXI_GP0_RLAST),
        .S00_AXI_rready(ps7_M_AXI_GP0_RREADY),
        .S00_AXI_rresp(ps7_M_AXI_GP0_RRESP),
        .S00_AXI_rvalid(ps7_M_AXI_GP0_RVALID),
        .S00_AXI_wdata(ps7_M_AXI_GP0_WDATA),
        .S00_AXI_wid(ps7_M_AXI_GP0_WID),
        .S00_AXI_wlast(ps7_M_AXI_GP0_WLAST),
        .S00_AXI_wready(ps7_M_AXI_GP0_WREADY),
        .S00_AXI_wstrb(ps7_M_AXI_GP0_WSTRB),
        .S00_AXI_wvalid(ps7_M_AXI_GP0_WVALID));
  flyvis_v1_flyvis_h_0 flyvis_h
       (.ap_clk(ps7_FCLK_CLK0),
        .ap_rst_n(ps7_FCLK_RESET0_N),
        .m_axi_gmem0_ARADDR(flyvis_h_m_axi_gmem0_ARADDR),
        .m_axi_gmem0_ARBURST(flyvis_h_m_axi_gmem0_ARBURST),
        .m_axi_gmem0_ARCACHE(flyvis_h_m_axi_gmem0_ARCACHE),
        .m_axi_gmem0_ARID(flyvis_h_m_axi_gmem0_ARID),
        .m_axi_gmem0_ARLEN(flyvis_h_m_axi_gmem0_ARLEN),
        .m_axi_gmem0_ARLOCK(flyvis_h_m_axi_gmem0_ARLOCK),
        .m_axi_gmem0_ARPROT(flyvis_h_m_axi_gmem0_ARPROT),
        .m_axi_gmem0_ARQOS(flyvis_h_m_axi_gmem0_ARQOS),
        .m_axi_gmem0_ARREADY(flyvis_h_m_axi_gmem0_ARREADY),
        .m_axi_gmem0_ARREGION(flyvis_h_m_axi_gmem0_ARREGION),
        .m_axi_gmem0_ARSIZE(flyvis_h_m_axi_gmem0_ARSIZE),
        .m_axi_gmem0_ARVALID(flyvis_h_m_axi_gmem0_ARVALID),
        .m_axi_gmem0_AWADDR(flyvis_h_m_axi_gmem0_AWADDR),
        .m_axi_gmem0_AWBURST(flyvis_h_m_axi_gmem0_AWBURST),
        .m_axi_gmem0_AWCACHE(flyvis_h_m_axi_gmem0_AWCACHE),
        .m_axi_gmem0_AWID(flyvis_h_m_axi_gmem0_AWID),
        .m_axi_gmem0_AWLEN(flyvis_h_m_axi_gmem0_AWLEN),
        .m_axi_gmem0_AWLOCK(flyvis_h_m_axi_gmem0_AWLOCK),
        .m_axi_gmem0_AWPROT(flyvis_h_m_axi_gmem0_AWPROT),
        .m_axi_gmem0_AWQOS(flyvis_h_m_axi_gmem0_AWQOS),
        .m_axi_gmem0_AWREADY(flyvis_h_m_axi_gmem0_AWREADY),
        .m_axi_gmem0_AWREGION(flyvis_h_m_axi_gmem0_AWREGION),
        .m_axi_gmem0_AWSIZE(flyvis_h_m_axi_gmem0_AWSIZE),
        .m_axi_gmem0_AWVALID(flyvis_h_m_axi_gmem0_AWVALID),
        .m_axi_gmem0_BID(flyvis_h_m_axi_gmem0_BID),
        .m_axi_gmem0_BREADY(flyvis_h_m_axi_gmem0_BREADY),
        .m_axi_gmem0_BRESP(flyvis_h_m_axi_gmem0_BRESP),
        .m_axi_gmem0_BVALID(flyvis_h_m_axi_gmem0_BVALID),
        .m_axi_gmem0_RDATA(flyvis_h_m_axi_gmem0_RDATA),
        .m_axi_gmem0_RID(flyvis_h_m_axi_gmem0_RID),
        .m_axi_gmem0_RLAST(flyvis_h_m_axi_gmem0_RLAST),
        .m_axi_gmem0_RREADY(flyvis_h_m_axi_gmem0_RREADY),
        .m_axi_gmem0_RRESP(flyvis_h_m_axi_gmem0_RRESP),
        .m_axi_gmem0_RVALID(flyvis_h_m_axi_gmem0_RVALID),
        .m_axi_gmem0_WDATA(flyvis_h_m_axi_gmem0_WDATA),
        .m_axi_gmem0_WLAST(flyvis_h_m_axi_gmem0_WLAST),
        .m_axi_gmem0_WREADY(flyvis_h_m_axi_gmem0_WREADY),
        .m_axi_gmem0_WSTRB(flyvis_h_m_axi_gmem0_WSTRB),
        .m_axi_gmem0_WVALID(flyvis_h_m_axi_gmem0_WVALID),
        .s_axi_control_ARADDR(cfg_ic_M00_AXI_ARADDR[5:0]),
        .s_axi_control_ARREADY(cfg_ic_M00_AXI_ARREADY),
        .s_axi_control_ARVALID(cfg_ic_M00_AXI_ARVALID),
        .s_axi_control_AWADDR(cfg_ic_M00_AXI_AWADDR[5:0]),
        .s_axi_control_AWREADY(cfg_ic_M00_AXI_AWREADY),
        .s_axi_control_AWVALID(cfg_ic_M00_AXI_AWVALID),
        .s_axi_control_BREADY(cfg_ic_M00_AXI_BREADY),
        .s_axi_control_BRESP(cfg_ic_M00_AXI_BRESP),
        .s_axi_control_BVALID(cfg_ic_M00_AXI_BVALID),
        .s_axi_control_RDATA(cfg_ic_M00_AXI_RDATA),
        .s_axi_control_RREADY(cfg_ic_M00_AXI_RREADY),
        .s_axi_control_RRESP(cfg_ic_M00_AXI_RRESP),
        .s_axi_control_RVALID(cfg_ic_M00_AXI_RVALID),
        .s_axi_control_WDATA(cfg_ic_M00_AXI_WDATA),
        .s_axi_control_WREADY(cfg_ic_M00_AXI_WREADY),
        .s_axi_control_WSTRB(cfg_ic_M00_AXI_WSTRB),
        .s_axi_control_WVALID(cfg_ic_M00_AXI_WVALID));
  flyvis_v1_mem_ic_0 mem_ic
       (.ACLK(ps7_FCLK_CLK0),
        .ARESETN(ps7_FCLK_RESET0_N),
        .M00_ACLK(ps7_FCLK_CLK0),
        .M00_ARESETN(ps7_FCLK_RESET0_N),
        .M00_AXI_araddr(mem_ic_M00_AXI_ARADDR),
        .M00_AXI_arburst(mem_ic_M00_AXI_ARBURST),
        .M00_AXI_arcache(mem_ic_M00_AXI_ARCACHE),
        .M00_AXI_arlen(mem_ic_M00_AXI_ARLEN),
        .M00_AXI_arlock(mem_ic_M00_AXI_ARLOCK),
        .M00_AXI_arprot(mem_ic_M00_AXI_ARPROT),
        .M00_AXI_arqos(mem_ic_M00_AXI_ARQOS),
        .M00_AXI_arready(mem_ic_M00_AXI_ARREADY),
        .M00_AXI_arsize(mem_ic_M00_AXI_ARSIZE),
        .M00_AXI_arvalid(mem_ic_M00_AXI_ARVALID),
        .M00_AXI_awaddr(mem_ic_M00_AXI_AWADDR),
        .M00_AXI_awburst(mem_ic_M00_AXI_AWBURST),
        .M00_AXI_awcache(mem_ic_M00_AXI_AWCACHE),
        .M00_AXI_awlen(mem_ic_M00_AXI_AWLEN),
        .M00_AXI_awlock(mem_ic_M00_AXI_AWLOCK),
        .M00_AXI_awprot(mem_ic_M00_AXI_AWPROT),
        .M00_AXI_awqos(mem_ic_M00_AXI_AWQOS),
        .M00_AXI_awready(mem_ic_M00_AXI_AWREADY),
        .M00_AXI_awsize(mem_ic_M00_AXI_AWSIZE),
        .M00_AXI_awvalid(mem_ic_M00_AXI_AWVALID),
        .M00_AXI_bready(mem_ic_M00_AXI_BREADY),
        .M00_AXI_bresp(mem_ic_M00_AXI_BRESP),
        .M00_AXI_bvalid(mem_ic_M00_AXI_BVALID),
        .M00_AXI_rdata(mem_ic_M00_AXI_RDATA),
        .M00_AXI_rlast(mem_ic_M00_AXI_RLAST),
        .M00_AXI_rready(mem_ic_M00_AXI_RREADY),
        .M00_AXI_rresp(mem_ic_M00_AXI_RRESP),
        .M00_AXI_rvalid(mem_ic_M00_AXI_RVALID),
        .M00_AXI_wdata(mem_ic_M00_AXI_WDATA),
        .M00_AXI_wlast(mem_ic_M00_AXI_WLAST),
        .M00_AXI_wready(mem_ic_M00_AXI_WREADY),
        .M00_AXI_wstrb(mem_ic_M00_AXI_WSTRB),
        .M00_AXI_wvalid(mem_ic_M00_AXI_WVALID),
        .S00_ACLK(ps7_FCLK_CLK0),
        .S00_ARESETN(ps7_FCLK_RESET0_N),
        .S00_AXI_araddr(flyvis_h_m_axi_gmem0_ARADDR),
        .S00_AXI_arburst(flyvis_h_m_axi_gmem0_ARBURST),
        .S00_AXI_arcache(flyvis_h_m_axi_gmem0_ARCACHE),
        .S00_AXI_arid(flyvis_h_m_axi_gmem0_ARID),
        .S00_AXI_arlen(flyvis_h_m_axi_gmem0_ARLEN),
        .S00_AXI_arlock(flyvis_h_m_axi_gmem0_ARLOCK),
        .S00_AXI_arprot(flyvis_h_m_axi_gmem0_ARPROT),
        .S00_AXI_arqos(flyvis_h_m_axi_gmem0_ARQOS),
        .S00_AXI_arready(flyvis_h_m_axi_gmem0_ARREADY),
        .S00_AXI_arregion(flyvis_h_m_axi_gmem0_ARREGION),
        .S00_AXI_arsize(flyvis_h_m_axi_gmem0_ARSIZE),
        .S00_AXI_arvalid(flyvis_h_m_axi_gmem0_ARVALID),
        .S00_AXI_awaddr(flyvis_h_m_axi_gmem0_AWADDR),
        .S00_AXI_awburst(flyvis_h_m_axi_gmem0_AWBURST),
        .S00_AXI_awcache(flyvis_h_m_axi_gmem0_AWCACHE),
        .S00_AXI_awid(flyvis_h_m_axi_gmem0_AWID),
        .S00_AXI_awlen(flyvis_h_m_axi_gmem0_AWLEN),
        .S00_AXI_awlock(flyvis_h_m_axi_gmem0_AWLOCK),
        .S00_AXI_awprot(flyvis_h_m_axi_gmem0_AWPROT),
        .S00_AXI_awqos(flyvis_h_m_axi_gmem0_AWQOS),
        .S00_AXI_awready(flyvis_h_m_axi_gmem0_AWREADY),
        .S00_AXI_awregion(flyvis_h_m_axi_gmem0_AWREGION),
        .S00_AXI_awsize(flyvis_h_m_axi_gmem0_AWSIZE),
        .S00_AXI_awvalid(flyvis_h_m_axi_gmem0_AWVALID),
        .S00_AXI_bid(flyvis_h_m_axi_gmem0_BID),
        .S00_AXI_bready(flyvis_h_m_axi_gmem0_BREADY),
        .S00_AXI_bresp(flyvis_h_m_axi_gmem0_BRESP),
        .S00_AXI_bvalid(flyvis_h_m_axi_gmem0_BVALID),
        .S00_AXI_rdata(flyvis_h_m_axi_gmem0_RDATA),
        .S00_AXI_rid(flyvis_h_m_axi_gmem0_RID),
        .S00_AXI_rlast(flyvis_h_m_axi_gmem0_RLAST),
        .S00_AXI_rready(flyvis_h_m_axi_gmem0_RREADY),
        .S00_AXI_rresp(flyvis_h_m_axi_gmem0_RRESP),
        .S00_AXI_rvalid(flyvis_h_m_axi_gmem0_RVALID),
        .S00_AXI_wdata(flyvis_h_m_axi_gmem0_WDATA),
        .S00_AXI_wlast(flyvis_h_m_axi_gmem0_WLAST),
        .S00_AXI_wready(flyvis_h_m_axi_gmem0_WREADY),
        .S00_AXI_wstrb(flyvis_h_m_axi_gmem0_WSTRB),
        .S00_AXI_wvalid(flyvis_h_m_axi_gmem0_WVALID));
  flyvis_v1_ps7_0 ps7
       (.DDR_Addr(DDR_addr),
        .DDR_BankAddr(DDR_ba),
        .DDR_CAS_n(DDR_cas_n),
        .DDR_CKE(DDR_cke),
        .DDR_CS_n(DDR_cs_n),
        .DDR_Clk(DDR_ck_p),
        .DDR_Clk_n(DDR_ck_n),
        .DDR_DM(DDR_dm),
        .DDR_DQ(DDR_dq),
        .DDR_DQS(DDR_dqs_p),
        .DDR_DQS_n(DDR_dqs_n),
        .DDR_DRSTB(DDR_reset_n),
        .DDR_ODT(DDR_odt),
        .DDR_RAS_n(DDR_ras_n),
        .DDR_VRN(FIXED_IO_ddr_vrn),
        .DDR_VRP(FIXED_IO_ddr_vrp),
        .DDR_WEB(DDR_we_n),
        .FCLK_CLK0(ps7_FCLK_CLK0),
        .FCLK_RESET0_N(ps7_FCLK_RESET0_N),
        .MIO(FIXED_IO_mio),
        .M_AXI_GP0_ACLK(ps7_FCLK_CLK0),
        .M_AXI_GP0_ARADDR(ps7_M_AXI_GP0_ARADDR),
        .M_AXI_GP0_ARBURST(ps7_M_AXI_GP0_ARBURST),
        .M_AXI_GP0_ARCACHE(ps7_M_AXI_GP0_ARCACHE),
        .M_AXI_GP0_ARID(ps7_M_AXI_GP0_ARID),
        .M_AXI_GP0_ARLEN(ps7_M_AXI_GP0_ARLEN),
        .M_AXI_GP0_ARLOCK(ps7_M_AXI_GP0_ARLOCK),
        .M_AXI_GP0_ARPROT(ps7_M_AXI_GP0_ARPROT),
        .M_AXI_GP0_ARQOS(ps7_M_AXI_GP0_ARQOS),
        .M_AXI_GP0_ARREADY(ps7_M_AXI_GP0_ARREADY),
        .M_AXI_GP0_ARSIZE(ps7_M_AXI_GP0_ARSIZE),
        .M_AXI_GP0_ARVALID(ps7_M_AXI_GP0_ARVALID),
        .M_AXI_GP0_AWADDR(ps7_M_AXI_GP0_AWADDR),
        .M_AXI_GP0_AWBURST(ps7_M_AXI_GP0_AWBURST),
        .M_AXI_GP0_AWCACHE(ps7_M_AXI_GP0_AWCACHE),
        .M_AXI_GP0_AWID(ps7_M_AXI_GP0_AWID),
        .M_AXI_GP0_AWLEN(ps7_M_AXI_GP0_AWLEN),
        .M_AXI_GP0_AWLOCK(ps7_M_AXI_GP0_AWLOCK),
        .M_AXI_GP0_AWPROT(ps7_M_AXI_GP0_AWPROT),
        .M_AXI_GP0_AWQOS(ps7_M_AXI_GP0_AWQOS),
        .M_AXI_GP0_AWREADY(ps7_M_AXI_GP0_AWREADY),
        .M_AXI_GP0_AWSIZE(ps7_M_AXI_GP0_AWSIZE),
        .M_AXI_GP0_AWVALID(ps7_M_AXI_GP0_AWVALID),
        .M_AXI_GP0_BID(ps7_M_AXI_GP0_BID),
        .M_AXI_GP0_BREADY(ps7_M_AXI_GP0_BREADY),
        .M_AXI_GP0_BRESP(ps7_M_AXI_GP0_BRESP),
        .M_AXI_GP0_BVALID(ps7_M_AXI_GP0_BVALID),
        .M_AXI_GP0_RDATA(ps7_M_AXI_GP0_RDATA),
        .M_AXI_GP0_RID(ps7_M_AXI_GP0_RID),
        .M_AXI_GP0_RLAST(ps7_M_AXI_GP0_RLAST),
        .M_AXI_GP0_RREADY(ps7_M_AXI_GP0_RREADY),
        .M_AXI_GP0_RRESP(ps7_M_AXI_GP0_RRESP),
        .M_AXI_GP0_RVALID(ps7_M_AXI_GP0_RVALID),
        .M_AXI_GP0_WDATA(ps7_M_AXI_GP0_WDATA),
        .M_AXI_GP0_WID(ps7_M_AXI_GP0_WID),
        .M_AXI_GP0_WLAST(ps7_M_AXI_GP0_WLAST),
        .M_AXI_GP0_WREADY(ps7_M_AXI_GP0_WREADY),
        .M_AXI_GP0_WSTRB(ps7_M_AXI_GP0_WSTRB),
        .M_AXI_GP0_WVALID(ps7_M_AXI_GP0_WVALID),
        .PS_CLK(FIXED_IO_ps_clk),
        .PS_PORB(FIXED_IO_ps_porb),
        .PS_SRSTB(FIXED_IO_ps_srstb),
        .S_AXI_HP0_ACLK(ps7_FCLK_CLK0),
        .S_AXI_HP0_ARADDR(mem_ic_M00_AXI_ARADDR[31:0]),
        .S_AXI_HP0_ARBURST(mem_ic_M00_AXI_ARBURST),
        .S_AXI_HP0_ARCACHE(mem_ic_M00_AXI_ARCACHE),
        .S_AXI_HP0_ARID({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .S_AXI_HP0_ARLEN(mem_ic_M00_AXI_ARLEN),
        .S_AXI_HP0_ARLOCK(mem_ic_M00_AXI_ARLOCK),
        .S_AXI_HP0_ARPROT(mem_ic_M00_AXI_ARPROT),
        .S_AXI_HP0_ARQOS(mem_ic_M00_AXI_ARQOS),
        .S_AXI_HP0_ARREADY(mem_ic_M00_AXI_ARREADY),
        .S_AXI_HP0_ARSIZE(mem_ic_M00_AXI_ARSIZE),
        .S_AXI_HP0_ARVALID(mem_ic_M00_AXI_ARVALID),
        .S_AXI_HP0_AWADDR(mem_ic_M00_AXI_AWADDR[31:0]),
        .S_AXI_HP0_AWBURST(mem_ic_M00_AXI_AWBURST),
        .S_AXI_HP0_AWCACHE(mem_ic_M00_AXI_AWCACHE),
        .S_AXI_HP0_AWID({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .S_AXI_HP0_AWLEN(mem_ic_M00_AXI_AWLEN),
        .S_AXI_HP0_AWLOCK(mem_ic_M00_AXI_AWLOCK),
        .S_AXI_HP0_AWPROT(mem_ic_M00_AXI_AWPROT),
        .S_AXI_HP0_AWQOS(mem_ic_M00_AXI_AWQOS),
        .S_AXI_HP0_AWREADY(mem_ic_M00_AXI_AWREADY),
        .S_AXI_HP0_AWSIZE(mem_ic_M00_AXI_AWSIZE),
        .S_AXI_HP0_AWVALID(mem_ic_M00_AXI_AWVALID),
        .S_AXI_HP0_BREADY(mem_ic_M00_AXI_BREADY),
        .S_AXI_HP0_BRESP(mem_ic_M00_AXI_BRESP),
        .S_AXI_HP0_BVALID(mem_ic_M00_AXI_BVALID),
        .S_AXI_HP0_RDATA(mem_ic_M00_AXI_RDATA),
        .S_AXI_HP0_RDISSUECAP1_EN(1'b0),
        .S_AXI_HP0_RLAST(mem_ic_M00_AXI_RLAST),
        .S_AXI_HP0_RREADY(mem_ic_M00_AXI_RREADY),
        .S_AXI_HP0_RRESP(mem_ic_M00_AXI_RRESP),
        .S_AXI_HP0_RVALID(mem_ic_M00_AXI_RVALID),
        .S_AXI_HP0_WDATA(mem_ic_M00_AXI_WDATA),
        .S_AXI_HP0_WID({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .S_AXI_HP0_WLAST(mem_ic_M00_AXI_WLAST),
        .S_AXI_HP0_WREADY(mem_ic_M00_AXI_WREADY),
        .S_AXI_HP0_WRISSUECAP1_EN(1'b0),
        .S_AXI_HP0_WSTRB(mem_ic_M00_AXI_WSTRB),
        .S_AXI_HP0_WVALID(mem_ic_M00_AXI_WVALID),
        .USB0_VBUS_PWRFAULT(1'b0));
endmodule

module flyvis_v1_cfg_ic_0
   (ACLK,
    ARESETN,
    M00_ACLK,
    M00_ARESETN,
    M00_AXI_araddr,
    M00_AXI_arready,
    M00_AXI_arvalid,
    M00_AXI_awaddr,
    M00_AXI_awready,
    M00_AXI_awvalid,
    M00_AXI_bready,
    M00_AXI_bresp,
    M00_AXI_bvalid,
    M00_AXI_rdata,
    M00_AXI_rready,
    M00_AXI_rresp,
    M00_AXI_rvalid,
    M00_AXI_wdata,
    M00_AXI_wready,
    M00_AXI_wstrb,
    M00_AXI_wvalid,
    S00_ACLK,
    S00_ARESETN,
    S00_AXI_araddr,
    S00_AXI_arburst,
    S00_AXI_arcache,
    S00_AXI_arid,
    S00_AXI_arlen,
    S00_AXI_arlock,
    S00_AXI_arprot,
    S00_AXI_arqos,
    S00_AXI_arready,
    S00_AXI_arsize,
    S00_AXI_arvalid,
    S00_AXI_awaddr,
    S00_AXI_awburst,
    S00_AXI_awcache,
    S00_AXI_awid,
    S00_AXI_awlen,
    S00_AXI_awlock,
    S00_AXI_awprot,
    S00_AXI_awqos,
    S00_AXI_awready,
    S00_AXI_awsize,
    S00_AXI_awvalid,
    S00_AXI_bid,
    S00_AXI_bready,
    S00_AXI_bresp,
    S00_AXI_bvalid,
    S00_AXI_rdata,
    S00_AXI_rid,
    S00_AXI_rlast,
    S00_AXI_rready,
    S00_AXI_rresp,
    S00_AXI_rvalid,
    S00_AXI_wdata,
    S00_AXI_wid,
    S00_AXI_wlast,
    S00_AXI_wready,
    S00_AXI_wstrb,
    S00_AXI_wvalid);
  input ACLK;
  input ARESETN;
  input M00_ACLK;
  input M00_ARESETN;
  output [31:0]M00_AXI_araddr;
  input M00_AXI_arready;
  output M00_AXI_arvalid;
  output [31:0]M00_AXI_awaddr;
  input M00_AXI_awready;
  output M00_AXI_awvalid;
  output M00_AXI_bready;
  input [1:0]M00_AXI_bresp;
  input M00_AXI_bvalid;
  input [31:0]M00_AXI_rdata;
  output M00_AXI_rready;
  input [1:0]M00_AXI_rresp;
  input M00_AXI_rvalid;
  output [31:0]M00_AXI_wdata;
  input M00_AXI_wready;
  output [3:0]M00_AXI_wstrb;
  output M00_AXI_wvalid;
  input S00_ACLK;
  input S00_ARESETN;
  input [31:0]S00_AXI_araddr;
  input [1:0]S00_AXI_arburst;
  input [3:0]S00_AXI_arcache;
  input [11:0]S00_AXI_arid;
  input [3:0]S00_AXI_arlen;
  input [1:0]S00_AXI_arlock;
  input [2:0]S00_AXI_arprot;
  input [3:0]S00_AXI_arqos;
  output S00_AXI_arready;
  input [2:0]S00_AXI_arsize;
  input S00_AXI_arvalid;
  input [31:0]S00_AXI_awaddr;
  input [1:0]S00_AXI_awburst;
  input [3:0]S00_AXI_awcache;
  input [11:0]S00_AXI_awid;
  input [3:0]S00_AXI_awlen;
  input [1:0]S00_AXI_awlock;
  input [2:0]S00_AXI_awprot;
  input [3:0]S00_AXI_awqos;
  output S00_AXI_awready;
  input [2:0]S00_AXI_awsize;
  input S00_AXI_awvalid;
  output [11:0]S00_AXI_bid;
  input S00_AXI_bready;
  output [1:0]S00_AXI_bresp;
  output S00_AXI_bvalid;
  output [31:0]S00_AXI_rdata;
  output [11:0]S00_AXI_rid;
  output S00_AXI_rlast;
  input S00_AXI_rready;
  output [1:0]S00_AXI_rresp;
  output S00_AXI_rvalid;
  input [31:0]S00_AXI_wdata;
  input [11:0]S00_AXI_wid;
  input S00_AXI_wlast;
  output S00_AXI_wready;
  input [3:0]S00_AXI_wstrb;
  input S00_AXI_wvalid;

  wire M00_ACLK;
  wire M00_ARESETN;
  wire [31:0]M00_AXI_araddr;
  wire M00_AXI_arready;
  wire M00_AXI_arvalid;
  wire [31:0]M00_AXI_awaddr;
  wire M00_AXI_awready;
  wire M00_AXI_awvalid;
  wire M00_AXI_bready;
  wire [1:0]M00_AXI_bresp;
  wire M00_AXI_bvalid;
  wire [31:0]M00_AXI_rdata;
  wire M00_AXI_rready;
  wire [1:0]M00_AXI_rresp;
  wire M00_AXI_rvalid;
  wire [31:0]M00_AXI_wdata;
  wire M00_AXI_wready;
  wire [3:0]M00_AXI_wstrb;
  wire M00_AXI_wvalid;
  wire S00_ACLK;
  wire S00_ARESETN;
  wire [31:0]S00_AXI_araddr;
  wire [1:0]S00_AXI_arburst;
  wire [3:0]S00_AXI_arcache;
  wire [11:0]S00_AXI_arid;
  wire [3:0]S00_AXI_arlen;
  wire [1:0]S00_AXI_arlock;
  wire [2:0]S00_AXI_arprot;
  wire [3:0]S00_AXI_arqos;
  wire S00_AXI_arready;
  wire [2:0]S00_AXI_arsize;
  wire S00_AXI_arvalid;
  wire [31:0]S00_AXI_awaddr;
  wire [1:0]S00_AXI_awburst;
  wire [3:0]S00_AXI_awcache;
  wire [11:0]S00_AXI_awid;
  wire [3:0]S00_AXI_awlen;
  wire [1:0]S00_AXI_awlock;
  wire [2:0]S00_AXI_awprot;
  wire [3:0]S00_AXI_awqos;
  wire S00_AXI_awready;
  wire [2:0]S00_AXI_awsize;
  wire S00_AXI_awvalid;
  wire [11:0]S00_AXI_bid;
  wire S00_AXI_bready;
  wire [1:0]S00_AXI_bresp;
  wire S00_AXI_bvalid;
  wire [31:0]S00_AXI_rdata;
  wire [11:0]S00_AXI_rid;
  wire S00_AXI_rlast;
  wire S00_AXI_rready;
  wire [1:0]S00_AXI_rresp;
  wire S00_AXI_rvalid;
  wire [31:0]S00_AXI_wdata;
  wire [11:0]S00_AXI_wid;
  wire S00_AXI_wlast;
  wire S00_AXI_wready;
  wire [3:0]S00_AXI_wstrb;
  wire S00_AXI_wvalid;

  s00_couplers_imp_1HPG0HT s00_couplers
       (.M_ACLK(M00_ACLK),
        .M_ARESETN(M00_ARESETN),
        .M_AXI_araddr(M00_AXI_araddr),
        .M_AXI_arready(M00_AXI_arready),
        .M_AXI_arvalid(M00_AXI_arvalid),
        .M_AXI_awaddr(M00_AXI_awaddr),
        .M_AXI_awready(M00_AXI_awready),
        .M_AXI_awvalid(M00_AXI_awvalid),
        .M_AXI_bready(M00_AXI_bready),
        .M_AXI_bresp(M00_AXI_bresp),
        .M_AXI_bvalid(M00_AXI_bvalid),
        .M_AXI_rdata(M00_AXI_rdata),
        .M_AXI_rready(M00_AXI_rready),
        .M_AXI_rresp(M00_AXI_rresp),
        .M_AXI_rvalid(M00_AXI_rvalid),
        .M_AXI_wdata(M00_AXI_wdata),
        .M_AXI_wready(M00_AXI_wready),
        .M_AXI_wstrb(M00_AXI_wstrb),
        .M_AXI_wvalid(M00_AXI_wvalid),
        .S_ACLK(S00_ACLK),
        .S_ARESETN(S00_ARESETN),
        .S_AXI_araddr(S00_AXI_araddr),
        .S_AXI_arburst(S00_AXI_arburst),
        .S_AXI_arcache(S00_AXI_arcache),
        .S_AXI_arid(S00_AXI_arid),
        .S_AXI_arlen(S00_AXI_arlen),
        .S_AXI_arlock(S00_AXI_arlock),
        .S_AXI_arprot(S00_AXI_arprot),
        .S_AXI_arqos(S00_AXI_arqos),
        .S_AXI_arready(S00_AXI_arready),
        .S_AXI_arsize(S00_AXI_arsize),
        .S_AXI_arvalid(S00_AXI_arvalid),
        .S_AXI_awaddr(S00_AXI_awaddr),
        .S_AXI_awburst(S00_AXI_awburst),
        .S_AXI_awcache(S00_AXI_awcache),
        .S_AXI_awid(S00_AXI_awid),
        .S_AXI_awlen(S00_AXI_awlen),
        .S_AXI_awlock(S00_AXI_awlock),
        .S_AXI_awprot(S00_AXI_awprot),
        .S_AXI_awqos(S00_AXI_awqos),
        .S_AXI_awready(S00_AXI_awready),
        .S_AXI_awsize(S00_AXI_awsize),
        .S_AXI_awvalid(S00_AXI_awvalid),
        .S_AXI_bid(S00_AXI_bid),
        .S_AXI_bready(S00_AXI_bready),
        .S_AXI_bresp(S00_AXI_bresp),
        .S_AXI_bvalid(S00_AXI_bvalid),
        .S_AXI_rdata(S00_AXI_rdata),
        .S_AXI_rid(S00_AXI_rid),
        .S_AXI_rlast(S00_AXI_rlast),
        .S_AXI_rready(S00_AXI_rready),
        .S_AXI_rresp(S00_AXI_rresp),
        .S_AXI_rvalid(S00_AXI_rvalid),
        .S_AXI_wdata(S00_AXI_wdata),
        .S_AXI_wid(S00_AXI_wid),
        .S_AXI_wlast(S00_AXI_wlast),
        .S_AXI_wready(S00_AXI_wready),
        .S_AXI_wstrb(S00_AXI_wstrb),
        .S_AXI_wvalid(S00_AXI_wvalid));
endmodule

module flyvis_v1_mem_ic_0
   (ACLK,
    ARESETN,
    M00_ACLK,
    M00_ARESETN,
    M00_AXI_araddr,
    M00_AXI_arburst,
    M00_AXI_arcache,
    M00_AXI_arlen,
    M00_AXI_arlock,
    M00_AXI_arprot,
    M00_AXI_arqos,
    M00_AXI_arready,
    M00_AXI_arsize,
    M00_AXI_arvalid,
    M00_AXI_awaddr,
    M00_AXI_awburst,
    M00_AXI_awcache,
    M00_AXI_awlen,
    M00_AXI_awlock,
    M00_AXI_awprot,
    M00_AXI_awqos,
    M00_AXI_awready,
    M00_AXI_awsize,
    M00_AXI_awvalid,
    M00_AXI_bready,
    M00_AXI_bresp,
    M00_AXI_bvalid,
    M00_AXI_rdata,
    M00_AXI_rlast,
    M00_AXI_rready,
    M00_AXI_rresp,
    M00_AXI_rvalid,
    M00_AXI_wdata,
    M00_AXI_wlast,
    M00_AXI_wready,
    M00_AXI_wstrb,
    M00_AXI_wvalid,
    S00_ACLK,
    S00_ARESETN,
    S00_AXI_araddr,
    S00_AXI_arburst,
    S00_AXI_arcache,
    S00_AXI_arid,
    S00_AXI_arlen,
    S00_AXI_arlock,
    S00_AXI_arprot,
    S00_AXI_arqos,
    S00_AXI_arready,
    S00_AXI_arregion,
    S00_AXI_arsize,
    S00_AXI_arvalid,
    S00_AXI_awaddr,
    S00_AXI_awburst,
    S00_AXI_awcache,
    S00_AXI_awid,
    S00_AXI_awlen,
    S00_AXI_awlock,
    S00_AXI_awprot,
    S00_AXI_awqos,
    S00_AXI_awready,
    S00_AXI_awregion,
    S00_AXI_awsize,
    S00_AXI_awvalid,
    S00_AXI_bid,
    S00_AXI_bready,
    S00_AXI_bresp,
    S00_AXI_bvalid,
    S00_AXI_rdata,
    S00_AXI_rid,
    S00_AXI_rlast,
    S00_AXI_rready,
    S00_AXI_rresp,
    S00_AXI_rvalid,
    S00_AXI_wdata,
    S00_AXI_wlast,
    S00_AXI_wready,
    S00_AXI_wstrb,
    S00_AXI_wvalid);
  input ACLK;
  input ARESETN;
  input M00_ACLK;
  input M00_ARESETN;
  output [63:0]M00_AXI_araddr;
  output [1:0]M00_AXI_arburst;
  output [3:0]M00_AXI_arcache;
  output [3:0]M00_AXI_arlen;
  output [1:0]M00_AXI_arlock;
  output [2:0]M00_AXI_arprot;
  output [3:0]M00_AXI_arqos;
  input M00_AXI_arready;
  output [2:0]M00_AXI_arsize;
  output M00_AXI_arvalid;
  output [63:0]M00_AXI_awaddr;
  output [1:0]M00_AXI_awburst;
  output [3:0]M00_AXI_awcache;
  output [3:0]M00_AXI_awlen;
  output [1:0]M00_AXI_awlock;
  output [2:0]M00_AXI_awprot;
  output [3:0]M00_AXI_awqos;
  input M00_AXI_awready;
  output [2:0]M00_AXI_awsize;
  output M00_AXI_awvalid;
  output M00_AXI_bready;
  input [1:0]M00_AXI_bresp;
  input M00_AXI_bvalid;
  input [63:0]M00_AXI_rdata;
  input M00_AXI_rlast;
  output M00_AXI_rready;
  input [1:0]M00_AXI_rresp;
  input M00_AXI_rvalid;
  output [63:0]M00_AXI_wdata;
  output M00_AXI_wlast;
  input M00_AXI_wready;
  output [7:0]M00_AXI_wstrb;
  output M00_AXI_wvalid;
  input S00_ACLK;
  input S00_ARESETN;
  input [63:0]S00_AXI_araddr;
  input [1:0]S00_AXI_arburst;
  input [3:0]S00_AXI_arcache;
  input [0:0]S00_AXI_arid;
  input [7:0]S00_AXI_arlen;
  input [1:0]S00_AXI_arlock;
  input [2:0]S00_AXI_arprot;
  input [3:0]S00_AXI_arqos;
  output S00_AXI_arready;
  input [3:0]S00_AXI_arregion;
  input [2:0]S00_AXI_arsize;
  input S00_AXI_arvalid;
  input [63:0]S00_AXI_awaddr;
  input [1:0]S00_AXI_awburst;
  input [3:0]S00_AXI_awcache;
  input [0:0]S00_AXI_awid;
  input [7:0]S00_AXI_awlen;
  input [1:0]S00_AXI_awlock;
  input [2:0]S00_AXI_awprot;
  input [3:0]S00_AXI_awqos;
  output S00_AXI_awready;
  input [3:0]S00_AXI_awregion;
  input [2:0]S00_AXI_awsize;
  input S00_AXI_awvalid;
  output [0:0]S00_AXI_bid;
  input S00_AXI_bready;
  output [1:0]S00_AXI_bresp;
  output S00_AXI_bvalid;
  output [31:0]S00_AXI_rdata;
  output [0:0]S00_AXI_rid;
  output S00_AXI_rlast;
  input S00_AXI_rready;
  output [1:0]S00_AXI_rresp;
  output S00_AXI_rvalid;
  input [31:0]S00_AXI_wdata;
  input S00_AXI_wlast;
  output S00_AXI_wready;
  input [3:0]S00_AXI_wstrb;
  input S00_AXI_wvalid;

  wire M00_ACLK;
  wire M00_ARESETN;
  wire [63:0]M00_AXI_araddr;
  wire [1:0]M00_AXI_arburst;
  wire [3:0]M00_AXI_arcache;
  wire [3:0]M00_AXI_arlen;
  wire [1:0]M00_AXI_arlock;
  wire [2:0]M00_AXI_arprot;
  wire [3:0]M00_AXI_arqos;
  wire M00_AXI_arready;
  wire [2:0]M00_AXI_arsize;
  wire M00_AXI_arvalid;
  wire [63:0]M00_AXI_awaddr;
  wire [1:0]M00_AXI_awburst;
  wire [3:0]M00_AXI_awcache;
  wire [3:0]M00_AXI_awlen;
  wire [1:0]M00_AXI_awlock;
  wire [2:0]M00_AXI_awprot;
  wire [3:0]M00_AXI_awqos;
  wire M00_AXI_awready;
  wire [2:0]M00_AXI_awsize;
  wire M00_AXI_awvalid;
  wire M00_AXI_bready;
  wire [1:0]M00_AXI_bresp;
  wire M00_AXI_bvalid;
  wire [63:0]M00_AXI_rdata;
  wire M00_AXI_rlast;
  wire M00_AXI_rready;
  wire [1:0]M00_AXI_rresp;
  wire M00_AXI_rvalid;
  wire [63:0]M00_AXI_wdata;
  wire M00_AXI_wlast;
  wire M00_AXI_wready;
  wire [7:0]M00_AXI_wstrb;
  wire M00_AXI_wvalid;
  wire S00_ACLK;
  wire S00_ARESETN;
  wire [63:0]S00_AXI_araddr;
  wire [1:0]S00_AXI_arburst;
  wire [3:0]S00_AXI_arcache;
  wire [0:0]S00_AXI_arid;
  wire [7:0]S00_AXI_arlen;
  wire [1:0]S00_AXI_arlock;
  wire [2:0]S00_AXI_arprot;
  wire [3:0]S00_AXI_arqos;
  wire S00_AXI_arready;
  wire [3:0]S00_AXI_arregion;
  wire [2:0]S00_AXI_arsize;
  wire S00_AXI_arvalid;
  wire [63:0]S00_AXI_awaddr;
  wire [1:0]S00_AXI_awburst;
  wire [3:0]S00_AXI_awcache;
  wire [0:0]S00_AXI_awid;
  wire [7:0]S00_AXI_awlen;
  wire [1:0]S00_AXI_awlock;
  wire [2:0]S00_AXI_awprot;
  wire [3:0]S00_AXI_awqos;
  wire S00_AXI_awready;
  wire [3:0]S00_AXI_awregion;
  wire [2:0]S00_AXI_awsize;
  wire S00_AXI_awvalid;
  wire [0:0]S00_AXI_bid;
  wire S00_AXI_bready;
  wire [1:0]S00_AXI_bresp;
  wire S00_AXI_bvalid;
  wire [31:0]S00_AXI_rdata;
  wire [0:0]S00_AXI_rid;
  wire S00_AXI_rlast;
  wire S00_AXI_rready;
  wire [1:0]S00_AXI_rresp;
  wire S00_AXI_rvalid;
  wire [31:0]S00_AXI_wdata;
  wire S00_AXI_wlast;
  wire S00_AXI_wready;
  wire [3:0]S00_AXI_wstrb;
  wire S00_AXI_wvalid;

  s00_couplers_imp_G7WFNB s00_couplers
       (.M_ACLK(M00_ACLK),
        .M_ARESETN(M00_ARESETN),
        .M_AXI_araddr(M00_AXI_araddr),
        .M_AXI_arburst(M00_AXI_arburst),
        .M_AXI_arcache(M00_AXI_arcache),
        .M_AXI_arlen(M00_AXI_arlen),
        .M_AXI_arlock(M00_AXI_arlock),
        .M_AXI_arprot(M00_AXI_arprot),
        .M_AXI_arqos(M00_AXI_arqos),
        .M_AXI_arready(M00_AXI_arready),
        .M_AXI_arsize(M00_AXI_arsize),
        .M_AXI_arvalid(M00_AXI_arvalid),
        .M_AXI_awaddr(M00_AXI_awaddr),
        .M_AXI_awburst(M00_AXI_awburst),
        .M_AXI_awcache(M00_AXI_awcache),
        .M_AXI_awlen(M00_AXI_awlen),
        .M_AXI_awlock(M00_AXI_awlock),
        .M_AXI_awprot(M00_AXI_awprot),
        .M_AXI_awqos(M00_AXI_awqos),
        .M_AXI_awready(M00_AXI_awready),
        .M_AXI_awsize(M00_AXI_awsize),
        .M_AXI_awvalid(M00_AXI_awvalid),
        .M_AXI_bready(M00_AXI_bready),
        .M_AXI_bresp(M00_AXI_bresp),
        .M_AXI_bvalid(M00_AXI_bvalid),
        .M_AXI_rdata(M00_AXI_rdata),
        .M_AXI_rlast(M00_AXI_rlast),
        .M_AXI_rready(M00_AXI_rready),
        .M_AXI_rresp(M00_AXI_rresp),
        .M_AXI_rvalid(M00_AXI_rvalid),
        .M_AXI_wdata(M00_AXI_wdata),
        .M_AXI_wlast(M00_AXI_wlast),
        .M_AXI_wready(M00_AXI_wready),
        .M_AXI_wstrb(M00_AXI_wstrb),
        .M_AXI_wvalid(M00_AXI_wvalid),
        .S_ACLK(S00_ACLK),
        .S_ARESETN(S00_ARESETN),
        .S_AXI_araddr(S00_AXI_araddr),
        .S_AXI_arburst(S00_AXI_arburst),
        .S_AXI_arcache(S00_AXI_arcache),
        .S_AXI_arid(S00_AXI_arid),
        .S_AXI_arlen(S00_AXI_arlen),
        .S_AXI_arlock(S00_AXI_arlock),
        .S_AXI_arprot(S00_AXI_arprot),
        .S_AXI_arqos(S00_AXI_arqos),
        .S_AXI_arready(S00_AXI_arready),
        .S_AXI_arregion(S00_AXI_arregion),
        .S_AXI_arsize(S00_AXI_arsize),
        .S_AXI_arvalid(S00_AXI_arvalid),
        .S_AXI_awaddr(S00_AXI_awaddr),
        .S_AXI_awburst(S00_AXI_awburst),
        .S_AXI_awcache(S00_AXI_awcache),
        .S_AXI_awid(S00_AXI_awid),
        .S_AXI_awlen(S00_AXI_awlen),
        .S_AXI_awlock(S00_AXI_awlock),
        .S_AXI_awprot(S00_AXI_awprot),
        .S_AXI_awqos(S00_AXI_awqos),
        .S_AXI_awready(S00_AXI_awready),
        .S_AXI_awregion(S00_AXI_awregion),
        .S_AXI_awsize(S00_AXI_awsize),
        .S_AXI_awvalid(S00_AXI_awvalid),
        .S_AXI_bid(S00_AXI_bid),
        .S_AXI_bready(S00_AXI_bready),
        .S_AXI_bresp(S00_AXI_bresp),
        .S_AXI_bvalid(S00_AXI_bvalid),
        .S_AXI_rdata(S00_AXI_rdata),
        .S_AXI_rid(S00_AXI_rid),
        .S_AXI_rlast(S00_AXI_rlast),
        .S_AXI_rready(S00_AXI_rready),
        .S_AXI_rresp(S00_AXI_rresp),
        .S_AXI_rvalid(S00_AXI_rvalid),
        .S_AXI_wdata(S00_AXI_wdata),
        .S_AXI_wlast(S00_AXI_wlast),
        .S_AXI_wready(S00_AXI_wready),
        .S_AXI_wstrb(S00_AXI_wstrb),
        .S_AXI_wvalid(S00_AXI_wvalid));
endmodule

module s00_couplers_imp_1HPG0HT
   (M_ACLK,
    M_ARESETN,
    M_AXI_araddr,
    M_AXI_arready,
    M_AXI_arvalid,
    M_AXI_awaddr,
    M_AXI_awready,
    M_AXI_awvalid,
    M_AXI_bready,
    M_AXI_bresp,
    M_AXI_bvalid,
    M_AXI_rdata,
    M_AXI_rready,
    M_AXI_rresp,
    M_AXI_rvalid,
    M_AXI_wdata,
    M_AXI_wready,
    M_AXI_wstrb,
    M_AXI_wvalid,
    S_ACLK,
    S_ARESETN,
    S_AXI_araddr,
    S_AXI_arburst,
    S_AXI_arcache,
    S_AXI_arid,
    S_AXI_arlen,
    S_AXI_arlock,
    S_AXI_arprot,
    S_AXI_arqos,
    S_AXI_arready,
    S_AXI_arsize,
    S_AXI_arvalid,
    S_AXI_awaddr,
    S_AXI_awburst,
    S_AXI_awcache,
    S_AXI_awid,
    S_AXI_awlen,
    S_AXI_awlock,
    S_AXI_awprot,
    S_AXI_awqos,
    S_AXI_awready,
    S_AXI_awsize,
    S_AXI_awvalid,
    S_AXI_bid,
    S_AXI_bready,
    S_AXI_bresp,
    S_AXI_bvalid,
    S_AXI_rdata,
    S_AXI_rid,
    S_AXI_rlast,
    S_AXI_rready,
    S_AXI_rresp,
    S_AXI_rvalid,
    S_AXI_wdata,
    S_AXI_wid,
    S_AXI_wlast,
    S_AXI_wready,
    S_AXI_wstrb,
    S_AXI_wvalid);
  input M_ACLK;
  input M_ARESETN;
  output [31:0]M_AXI_araddr;
  input M_AXI_arready;
  output M_AXI_arvalid;
  output [31:0]M_AXI_awaddr;
  input M_AXI_awready;
  output M_AXI_awvalid;
  output M_AXI_bready;
  input [1:0]M_AXI_bresp;
  input M_AXI_bvalid;
  input [31:0]M_AXI_rdata;
  output M_AXI_rready;
  input [1:0]M_AXI_rresp;
  input M_AXI_rvalid;
  output [31:0]M_AXI_wdata;
  input M_AXI_wready;
  output [3:0]M_AXI_wstrb;
  output M_AXI_wvalid;
  input S_ACLK;
  input S_ARESETN;
  input [31:0]S_AXI_araddr;
  input [1:0]S_AXI_arburst;
  input [3:0]S_AXI_arcache;
  input [11:0]S_AXI_arid;
  input [3:0]S_AXI_arlen;
  input [1:0]S_AXI_arlock;
  input [2:0]S_AXI_arprot;
  input [3:0]S_AXI_arqos;
  output S_AXI_arready;
  input [2:0]S_AXI_arsize;
  input S_AXI_arvalid;
  input [31:0]S_AXI_awaddr;
  input [1:0]S_AXI_awburst;
  input [3:0]S_AXI_awcache;
  input [11:0]S_AXI_awid;
  input [3:0]S_AXI_awlen;
  input [1:0]S_AXI_awlock;
  input [2:0]S_AXI_awprot;
  input [3:0]S_AXI_awqos;
  output S_AXI_awready;
  input [2:0]S_AXI_awsize;
  input S_AXI_awvalid;
  output [11:0]S_AXI_bid;
  input S_AXI_bready;
  output [1:0]S_AXI_bresp;
  output S_AXI_bvalid;
  output [31:0]S_AXI_rdata;
  output [11:0]S_AXI_rid;
  output S_AXI_rlast;
  input S_AXI_rready;
  output [1:0]S_AXI_rresp;
  output S_AXI_rvalid;
  input [31:0]S_AXI_wdata;
  input [11:0]S_AXI_wid;
  input S_AXI_wlast;
  output S_AXI_wready;
  input [3:0]S_AXI_wstrb;
  input S_AXI_wvalid;

  wire [31:0]M_AXI_araddr;
  wire M_AXI_arready;
  wire M_AXI_arvalid;
  wire [31:0]M_AXI_awaddr;
  wire M_AXI_awready;
  wire M_AXI_awvalid;
  wire M_AXI_bready;
  wire [1:0]M_AXI_bresp;
  wire M_AXI_bvalid;
  wire [31:0]M_AXI_rdata;
  wire M_AXI_rready;
  wire [1:0]M_AXI_rresp;
  wire M_AXI_rvalid;
  wire [31:0]M_AXI_wdata;
  wire M_AXI_wready;
  wire [3:0]M_AXI_wstrb;
  wire M_AXI_wvalid;
  wire S_ACLK;
  wire S_ARESETN;
  wire [31:0]S_AXI_araddr;
  wire [1:0]S_AXI_arburst;
  wire [3:0]S_AXI_arcache;
  wire [11:0]S_AXI_arid;
  wire [3:0]S_AXI_arlen;
  wire [1:0]S_AXI_arlock;
  wire [2:0]S_AXI_arprot;
  wire [3:0]S_AXI_arqos;
  wire S_AXI_arready;
  wire [2:0]S_AXI_arsize;
  wire S_AXI_arvalid;
  wire [31:0]S_AXI_awaddr;
  wire [1:0]S_AXI_awburst;
  wire [3:0]S_AXI_awcache;
  wire [11:0]S_AXI_awid;
  wire [3:0]S_AXI_awlen;
  wire [1:0]S_AXI_awlock;
  wire [2:0]S_AXI_awprot;
  wire [3:0]S_AXI_awqos;
  wire S_AXI_awready;
  wire [2:0]S_AXI_awsize;
  wire S_AXI_awvalid;
  wire [11:0]S_AXI_bid;
  wire S_AXI_bready;
  wire [1:0]S_AXI_bresp;
  wire S_AXI_bvalid;
  wire [31:0]S_AXI_rdata;
  wire [11:0]S_AXI_rid;
  wire S_AXI_rlast;
  wire S_AXI_rready;
  wire [1:0]S_AXI_rresp;
  wire S_AXI_rvalid;
  wire [31:0]S_AXI_wdata;
  wire [11:0]S_AXI_wid;
  wire S_AXI_wlast;
  wire S_AXI_wready;
  wire [3:0]S_AXI_wstrb;
  wire S_AXI_wvalid;

  flyvis_v1_cfg_ic_imp_auto_pc_0 auto_pc
       (.aclk(S_ACLK),
        .aresetn(S_ARESETN),
        .m_axi_araddr(M_AXI_araddr),
        .m_axi_arready(M_AXI_arready),
        .m_axi_arvalid(M_AXI_arvalid),
        .m_axi_awaddr(M_AXI_awaddr),
        .m_axi_awready(M_AXI_awready),
        .m_axi_awvalid(M_AXI_awvalid),
        .m_axi_bready(M_AXI_bready),
        .m_axi_bresp(M_AXI_bresp),
        .m_axi_bvalid(M_AXI_bvalid),
        .m_axi_rdata(M_AXI_rdata),
        .m_axi_rready(M_AXI_rready),
        .m_axi_rresp(M_AXI_rresp),
        .m_axi_rvalid(M_AXI_rvalid),
        .m_axi_wdata(M_AXI_wdata),
        .m_axi_wready(M_AXI_wready),
        .m_axi_wstrb(M_AXI_wstrb),
        .m_axi_wvalid(M_AXI_wvalid),
        .s_axi_araddr(S_AXI_araddr),
        .s_axi_arburst(S_AXI_arburst),
        .s_axi_arcache(S_AXI_arcache),
        .s_axi_arid(S_AXI_arid),
        .s_axi_arlen(S_AXI_arlen),
        .s_axi_arlock(S_AXI_arlock),
        .s_axi_arprot(S_AXI_arprot),
        .s_axi_arqos(S_AXI_arqos),
        .s_axi_arready(S_AXI_arready),
        .s_axi_arsize(S_AXI_arsize),
        .s_axi_arvalid(S_AXI_arvalid),
        .s_axi_awaddr(S_AXI_awaddr),
        .s_axi_awburst(S_AXI_awburst),
        .s_axi_awcache(S_AXI_awcache),
        .s_axi_awid(S_AXI_awid),
        .s_axi_awlen(S_AXI_awlen),
        .s_axi_awlock(S_AXI_awlock),
        .s_axi_awprot(S_AXI_awprot),
        .s_axi_awqos(S_AXI_awqos),
        .s_axi_awready(S_AXI_awready),
        .s_axi_awsize(S_AXI_awsize),
        .s_axi_awvalid(S_AXI_awvalid),
        .s_axi_bid(S_AXI_bid),
        .s_axi_bready(S_AXI_bready),
        .s_axi_bresp(S_AXI_bresp),
        .s_axi_bvalid(S_AXI_bvalid),
        .s_axi_rdata(S_AXI_rdata),
        .s_axi_rid(S_AXI_rid),
        .s_axi_rlast(S_AXI_rlast),
        .s_axi_rready(S_AXI_rready),
        .s_axi_rresp(S_AXI_rresp),
        .s_axi_rvalid(S_AXI_rvalid),
        .s_axi_wdata(S_AXI_wdata),
        .s_axi_wid(S_AXI_wid),
        .s_axi_wlast(S_AXI_wlast),
        .s_axi_wready(S_AXI_wready),
        .s_axi_wstrb(S_AXI_wstrb),
        .s_axi_wvalid(S_AXI_wvalid));
endmodule

module s00_couplers_imp_G7WFNB
   (M_ACLK,
    M_ARESETN,
    M_AXI_araddr,
    M_AXI_arburst,
    M_AXI_arcache,
    M_AXI_arlen,
    M_AXI_arlock,
    M_AXI_arprot,
    M_AXI_arqos,
    M_AXI_arready,
    M_AXI_arsize,
    M_AXI_arvalid,
    M_AXI_awaddr,
    M_AXI_awburst,
    M_AXI_awcache,
    M_AXI_awlen,
    M_AXI_awlock,
    M_AXI_awprot,
    M_AXI_awqos,
    M_AXI_awready,
    M_AXI_awsize,
    M_AXI_awvalid,
    M_AXI_bready,
    M_AXI_bresp,
    M_AXI_bvalid,
    M_AXI_rdata,
    M_AXI_rlast,
    M_AXI_rready,
    M_AXI_rresp,
    M_AXI_rvalid,
    M_AXI_wdata,
    M_AXI_wlast,
    M_AXI_wready,
    M_AXI_wstrb,
    M_AXI_wvalid,
    S_ACLK,
    S_ARESETN,
    S_AXI_araddr,
    S_AXI_arburst,
    S_AXI_arcache,
    S_AXI_arid,
    S_AXI_arlen,
    S_AXI_arlock,
    S_AXI_arprot,
    S_AXI_arqos,
    S_AXI_arready,
    S_AXI_arregion,
    S_AXI_arsize,
    S_AXI_arvalid,
    S_AXI_awaddr,
    S_AXI_awburst,
    S_AXI_awcache,
    S_AXI_awid,
    S_AXI_awlen,
    S_AXI_awlock,
    S_AXI_awprot,
    S_AXI_awqos,
    S_AXI_awready,
    S_AXI_awregion,
    S_AXI_awsize,
    S_AXI_awvalid,
    S_AXI_bid,
    S_AXI_bready,
    S_AXI_bresp,
    S_AXI_bvalid,
    S_AXI_rdata,
    S_AXI_rid,
    S_AXI_rlast,
    S_AXI_rready,
    S_AXI_rresp,
    S_AXI_rvalid,
    S_AXI_wdata,
    S_AXI_wlast,
    S_AXI_wready,
    S_AXI_wstrb,
    S_AXI_wvalid);
  input M_ACLK;
  input M_ARESETN;
  output [63:0]M_AXI_araddr;
  output [1:0]M_AXI_arburst;
  output [3:0]M_AXI_arcache;
  output [3:0]M_AXI_arlen;
  output [1:0]M_AXI_arlock;
  output [2:0]M_AXI_arprot;
  output [3:0]M_AXI_arqos;
  input M_AXI_arready;
  output [2:0]M_AXI_arsize;
  output M_AXI_arvalid;
  output [63:0]M_AXI_awaddr;
  output [1:0]M_AXI_awburst;
  output [3:0]M_AXI_awcache;
  output [3:0]M_AXI_awlen;
  output [1:0]M_AXI_awlock;
  output [2:0]M_AXI_awprot;
  output [3:0]M_AXI_awqos;
  input M_AXI_awready;
  output [2:0]M_AXI_awsize;
  output M_AXI_awvalid;
  output M_AXI_bready;
  input [1:0]M_AXI_bresp;
  input M_AXI_bvalid;
  input [63:0]M_AXI_rdata;
  input M_AXI_rlast;
  output M_AXI_rready;
  input [1:0]M_AXI_rresp;
  input M_AXI_rvalid;
  output [63:0]M_AXI_wdata;
  output M_AXI_wlast;
  input M_AXI_wready;
  output [7:0]M_AXI_wstrb;
  output M_AXI_wvalid;
  input S_ACLK;
  input S_ARESETN;
  input [63:0]S_AXI_araddr;
  input [1:0]S_AXI_arburst;
  input [3:0]S_AXI_arcache;
  input [0:0]S_AXI_arid;
  input [7:0]S_AXI_arlen;
  input [1:0]S_AXI_arlock;
  input [2:0]S_AXI_arprot;
  input [3:0]S_AXI_arqos;
  output S_AXI_arready;
  input [3:0]S_AXI_arregion;
  input [2:0]S_AXI_arsize;
  input S_AXI_arvalid;
  input [63:0]S_AXI_awaddr;
  input [1:0]S_AXI_awburst;
  input [3:0]S_AXI_awcache;
  input [0:0]S_AXI_awid;
  input [7:0]S_AXI_awlen;
  input [1:0]S_AXI_awlock;
  input [2:0]S_AXI_awprot;
  input [3:0]S_AXI_awqos;
  output S_AXI_awready;
  input [3:0]S_AXI_awregion;
  input [2:0]S_AXI_awsize;
  input S_AXI_awvalid;
  output [0:0]S_AXI_bid;
  input S_AXI_bready;
  output [1:0]S_AXI_bresp;
  output S_AXI_bvalid;
  output [31:0]S_AXI_rdata;
  output [0:0]S_AXI_rid;
  output S_AXI_rlast;
  input S_AXI_rready;
  output [1:0]S_AXI_rresp;
  output S_AXI_rvalid;
  input [31:0]S_AXI_wdata;
  input S_AXI_wlast;
  output S_AXI_wready;
  input [3:0]S_AXI_wstrb;
  input S_AXI_wvalid;

  wire [63:0]M_AXI_araddr;
  wire [1:0]M_AXI_arburst;
  wire [3:0]M_AXI_arcache;
  wire [3:0]M_AXI_arlen;
  wire [1:0]M_AXI_arlock;
  wire [2:0]M_AXI_arprot;
  wire [3:0]M_AXI_arqos;
  wire M_AXI_arready;
  wire [2:0]M_AXI_arsize;
  wire M_AXI_arvalid;
  wire [63:0]M_AXI_awaddr;
  wire [1:0]M_AXI_awburst;
  wire [3:0]M_AXI_awcache;
  wire [3:0]M_AXI_awlen;
  wire [1:0]M_AXI_awlock;
  wire [2:0]M_AXI_awprot;
  wire [3:0]M_AXI_awqos;
  wire M_AXI_awready;
  wire [2:0]M_AXI_awsize;
  wire M_AXI_awvalid;
  wire M_AXI_bready;
  wire [1:0]M_AXI_bresp;
  wire M_AXI_bvalid;
  wire [63:0]M_AXI_rdata;
  wire M_AXI_rlast;
  wire M_AXI_rready;
  wire [1:0]M_AXI_rresp;
  wire M_AXI_rvalid;
  wire [63:0]M_AXI_wdata;
  wire M_AXI_wlast;
  wire M_AXI_wready;
  wire [7:0]M_AXI_wstrb;
  wire M_AXI_wvalid;
  wire S_ACLK;
  wire S_ARESETN;
  wire [63:0]S_AXI_araddr;
  wire [1:0]S_AXI_arburst;
  wire [3:0]S_AXI_arcache;
  wire [0:0]S_AXI_arid;
  wire [7:0]S_AXI_arlen;
  wire [1:0]S_AXI_arlock;
  wire [2:0]S_AXI_arprot;
  wire [3:0]S_AXI_arqos;
  wire S_AXI_arready;
  wire [3:0]S_AXI_arregion;
  wire [2:0]S_AXI_arsize;
  wire S_AXI_arvalid;
  wire [63:0]S_AXI_awaddr;
  wire [1:0]S_AXI_awburst;
  wire [3:0]S_AXI_awcache;
  wire [0:0]S_AXI_awid;
  wire [7:0]S_AXI_awlen;
  wire [1:0]S_AXI_awlock;
  wire [2:0]S_AXI_awprot;
  wire [3:0]S_AXI_awqos;
  wire S_AXI_awready;
  wire [3:0]S_AXI_awregion;
  wire [2:0]S_AXI_awsize;
  wire S_AXI_awvalid;
  wire [0:0]S_AXI_bid;
  wire S_AXI_bready;
  wire [1:0]S_AXI_bresp;
  wire S_AXI_bvalid;
  wire [31:0]S_AXI_rdata;
  wire [0:0]S_AXI_rid;
  wire S_AXI_rlast;
  wire S_AXI_rready;
  wire [1:0]S_AXI_rresp;
  wire S_AXI_rvalid;
  wire [31:0]S_AXI_wdata;
  wire S_AXI_wlast;
  wire S_AXI_wready;
  wire [3:0]S_AXI_wstrb;
  wire S_AXI_wvalid;
  wire [63:0]auto_pc_to_auto_us_ARADDR;
  wire [1:0]auto_pc_to_auto_us_ARBURST;
  wire [3:0]auto_pc_to_auto_us_ARCACHE;
  wire [0:0]auto_pc_to_auto_us_ARID;
  wire [3:0]auto_pc_to_auto_us_ARLEN;
  wire [1:0]auto_pc_to_auto_us_ARLOCK;
  wire [2:0]auto_pc_to_auto_us_ARPROT;
  wire [3:0]auto_pc_to_auto_us_ARQOS;
  wire auto_pc_to_auto_us_ARREADY;
  wire [2:0]auto_pc_to_auto_us_ARSIZE;
  wire auto_pc_to_auto_us_ARVALID;
  wire [63:0]auto_pc_to_auto_us_AWADDR;
  wire [1:0]auto_pc_to_auto_us_AWBURST;
  wire [3:0]auto_pc_to_auto_us_AWCACHE;
  wire [0:0]auto_pc_to_auto_us_AWID;
  wire [3:0]auto_pc_to_auto_us_AWLEN;
  wire [1:0]auto_pc_to_auto_us_AWLOCK;
  wire [2:0]auto_pc_to_auto_us_AWPROT;
  wire [3:0]auto_pc_to_auto_us_AWQOS;
  wire auto_pc_to_auto_us_AWREADY;
  wire [2:0]auto_pc_to_auto_us_AWSIZE;
  wire auto_pc_to_auto_us_AWVALID;
  wire [0:0]auto_pc_to_auto_us_BID;
  wire auto_pc_to_auto_us_BREADY;
  wire [1:0]auto_pc_to_auto_us_BRESP;
  wire auto_pc_to_auto_us_BVALID;
  wire [31:0]auto_pc_to_auto_us_RDATA;
  wire [0:0]auto_pc_to_auto_us_RID;
  wire auto_pc_to_auto_us_RLAST;
  wire auto_pc_to_auto_us_RREADY;
  wire [1:0]auto_pc_to_auto_us_RRESP;
  wire auto_pc_to_auto_us_RVALID;
  wire [31:0]auto_pc_to_auto_us_WDATA;
  wire auto_pc_to_auto_us_WLAST;
  wire auto_pc_to_auto_us_WREADY;
  wire [3:0]auto_pc_to_auto_us_WSTRB;
  wire auto_pc_to_auto_us_WVALID;

  flyvis_v1_mem_ic_imp_auto_pc_0 auto_pc
       (.aclk(S_ACLK),
        .aresetn(S_ARESETN),
        .m_axi_araddr(auto_pc_to_auto_us_ARADDR),
        .m_axi_arburst(auto_pc_to_auto_us_ARBURST),
        .m_axi_arcache(auto_pc_to_auto_us_ARCACHE),
        .m_axi_arid(auto_pc_to_auto_us_ARID),
        .m_axi_arlen(auto_pc_to_auto_us_ARLEN),
        .m_axi_arlock(auto_pc_to_auto_us_ARLOCK),
        .m_axi_arprot(auto_pc_to_auto_us_ARPROT),
        .m_axi_arqos(auto_pc_to_auto_us_ARQOS),
        .m_axi_arready(auto_pc_to_auto_us_ARREADY),
        .m_axi_arsize(auto_pc_to_auto_us_ARSIZE),
        .m_axi_arvalid(auto_pc_to_auto_us_ARVALID),
        .m_axi_awaddr(auto_pc_to_auto_us_AWADDR),
        .m_axi_awburst(auto_pc_to_auto_us_AWBURST),
        .m_axi_awcache(auto_pc_to_auto_us_AWCACHE),
        .m_axi_awid(auto_pc_to_auto_us_AWID),
        .m_axi_awlen(auto_pc_to_auto_us_AWLEN),
        .m_axi_awlock(auto_pc_to_auto_us_AWLOCK),
        .m_axi_awprot(auto_pc_to_auto_us_AWPROT),
        .m_axi_awqos(auto_pc_to_auto_us_AWQOS),
        .m_axi_awready(auto_pc_to_auto_us_AWREADY),
        .m_axi_awsize(auto_pc_to_auto_us_AWSIZE),
        .m_axi_awvalid(auto_pc_to_auto_us_AWVALID),
        .m_axi_bid(auto_pc_to_auto_us_BID),
        .m_axi_bready(auto_pc_to_auto_us_BREADY),
        .m_axi_bresp(auto_pc_to_auto_us_BRESP),
        .m_axi_bvalid(auto_pc_to_auto_us_BVALID),
        .m_axi_rdata(auto_pc_to_auto_us_RDATA),
        .m_axi_rid(auto_pc_to_auto_us_RID),
        .m_axi_rlast(auto_pc_to_auto_us_RLAST),
        .m_axi_rready(auto_pc_to_auto_us_RREADY),
        .m_axi_rresp(auto_pc_to_auto_us_RRESP),
        .m_axi_rvalid(auto_pc_to_auto_us_RVALID),
        .m_axi_wdata(auto_pc_to_auto_us_WDATA),
        .m_axi_wlast(auto_pc_to_auto_us_WLAST),
        .m_axi_wready(auto_pc_to_auto_us_WREADY),
        .m_axi_wstrb(auto_pc_to_auto_us_WSTRB),
        .m_axi_wvalid(auto_pc_to_auto_us_WVALID),
        .s_axi_araddr(S_AXI_araddr),
        .s_axi_arburst(S_AXI_arburst),
        .s_axi_arcache(S_AXI_arcache),
        .s_axi_arid(S_AXI_arid),
        .s_axi_arlen(S_AXI_arlen),
        .s_axi_arlock(S_AXI_arlock[0]),
        .s_axi_arprot(S_AXI_arprot),
        .s_axi_arqos(S_AXI_arqos),
        .s_axi_arready(S_AXI_arready),
        .s_axi_arregion(S_AXI_arregion),
        .s_axi_arsize(S_AXI_arsize),
        .s_axi_arvalid(S_AXI_arvalid),
        .s_axi_awaddr(S_AXI_awaddr),
        .s_axi_awburst(S_AXI_awburst),
        .s_axi_awcache(S_AXI_awcache),
        .s_axi_awid(S_AXI_awid),
        .s_axi_awlen(S_AXI_awlen),
        .s_axi_awlock(S_AXI_awlock[0]),
        .s_axi_awprot(S_AXI_awprot),
        .s_axi_awqos(S_AXI_awqos),
        .s_axi_awready(S_AXI_awready),
        .s_axi_awregion(S_AXI_awregion),
        .s_axi_awsize(S_AXI_awsize),
        .s_axi_awvalid(S_AXI_awvalid),
        .s_axi_bid(S_AXI_bid),
        .s_axi_bready(S_AXI_bready),
        .s_axi_bresp(S_AXI_bresp),
        .s_axi_bvalid(S_AXI_bvalid),
        .s_axi_rdata(S_AXI_rdata),
        .s_axi_rid(S_AXI_rid),
        .s_axi_rlast(S_AXI_rlast),
        .s_axi_rready(S_AXI_rready),
        .s_axi_rresp(S_AXI_rresp),
        .s_axi_rvalid(S_AXI_rvalid),
        .s_axi_wdata(S_AXI_wdata),
        .s_axi_wlast(S_AXI_wlast),
        .s_axi_wready(S_AXI_wready),
        .s_axi_wstrb(S_AXI_wstrb),
        .s_axi_wvalid(S_AXI_wvalid));
  flyvis_v1_mem_ic_imp_auto_us_0 auto_us
       (.m_axi_araddr(M_AXI_araddr),
        .m_axi_arburst(M_AXI_arburst),
        .m_axi_arcache(M_AXI_arcache),
        .m_axi_arlen(M_AXI_arlen),
        .m_axi_arlock(M_AXI_arlock),
        .m_axi_arprot(M_AXI_arprot),
        .m_axi_arqos(M_AXI_arqos),
        .m_axi_arready(M_AXI_arready),
        .m_axi_arsize(M_AXI_arsize),
        .m_axi_arvalid(M_AXI_arvalid),
        .m_axi_awaddr(M_AXI_awaddr),
        .m_axi_awburst(M_AXI_awburst),
        .m_axi_awcache(M_AXI_awcache),
        .m_axi_awlen(M_AXI_awlen),
        .m_axi_awlock(M_AXI_awlock),
        .m_axi_awprot(M_AXI_awprot),
        .m_axi_awqos(M_AXI_awqos),
        .m_axi_awready(M_AXI_awready),
        .m_axi_awsize(M_AXI_awsize),
        .m_axi_awvalid(M_AXI_awvalid),
        .m_axi_bready(M_AXI_bready),
        .m_axi_bresp(M_AXI_bresp),
        .m_axi_bvalid(M_AXI_bvalid),
        .m_axi_rdata(M_AXI_rdata),
        .m_axi_rlast(M_AXI_rlast),
        .m_axi_rready(M_AXI_rready),
        .m_axi_rresp(M_AXI_rresp),
        .m_axi_rvalid(M_AXI_rvalid),
        .m_axi_wdata(M_AXI_wdata),
        .m_axi_wlast(M_AXI_wlast),
        .m_axi_wready(M_AXI_wready),
        .m_axi_wstrb(M_AXI_wstrb),
        .m_axi_wvalid(M_AXI_wvalid),
        .s_axi_aclk(S_ACLK),
        .s_axi_araddr(auto_pc_to_auto_us_ARADDR),
        .s_axi_arburst(auto_pc_to_auto_us_ARBURST),
        .s_axi_arcache(auto_pc_to_auto_us_ARCACHE),
        .s_axi_aresetn(S_ARESETN),
        .s_axi_arid(auto_pc_to_auto_us_ARID),
        .s_axi_arlen(auto_pc_to_auto_us_ARLEN),
        .s_axi_arlock(auto_pc_to_auto_us_ARLOCK),
        .s_axi_arprot(auto_pc_to_auto_us_ARPROT),
        .s_axi_arqos(auto_pc_to_auto_us_ARQOS),
        .s_axi_arready(auto_pc_to_auto_us_ARREADY),
        .s_axi_arsize(auto_pc_to_auto_us_ARSIZE),
        .s_axi_arvalid(auto_pc_to_auto_us_ARVALID),
        .s_axi_awaddr(auto_pc_to_auto_us_AWADDR),
        .s_axi_awburst(auto_pc_to_auto_us_AWBURST),
        .s_axi_awcache(auto_pc_to_auto_us_AWCACHE),
        .s_axi_awid(auto_pc_to_auto_us_AWID),
        .s_axi_awlen(auto_pc_to_auto_us_AWLEN),
        .s_axi_awlock(auto_pc_to_auto_us_AWLOCK),
        .s_axi_awprot(auto_pc_to_auto_us_AWPROT),
        .s_axi_awqos(auto_pc_to_auto_us_AWQOS),
        .s_axi_awready(auto_pc_to_auto_us_AWREADY),
        .s_axi_awsize(auto_pc_to_auto_us_AWSIZE),
        .s_axi_awvalid(auto_pc_to_auto_us_AWVALID),
        .s_axi_bid(auto_pc_to_auto_us_BID),
        .s_axi_bready(auto_pc_to_auto_us_BREADY),
        .s_axi_bresp(auto_pc_to_auto_us_BRESP),
        .s_axi_bvalid(auto_pc_to_auto_us_BVALID),
        .s_axi_rdata(auto_pc_to_auto_us_RDATA),
        .s_axi_rid(auto_pc_to_auto_us_RID),
        .s_axi_rlast(auto_pc_to_auto_us_RLAST),
        .s_axi_rready(auto_pc_to_auto_us_RREADY),
        .s_axi_rresp(auto_pc_to_auto_us_RRESP),
        .s_axi_rvalid(auto_pc_to_auto_us_RVALID),
        .s_axi_wdata(auto_pc_to_auto_us_WDATA),
        .s_axi_wlast(auto_pc_to_auto_us_WLAST),
        .s_axi_wready(auto_pc_to_auto_us_WREADY),
        .s_axi_wstrb(auto_pc_to_auto_us_WSTRB),
        .s_axi_wvalid(auto_pc_to_auto_us_WVALID));
endmodule

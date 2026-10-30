`timescale 1ns/1ps
// One ordered edge/cycle; shared pipelined multiplier for edges and two Euler
// sweeps. Q24/Q20, nearest ties away, fail closed. No old-state writes in RUN.
module ddr_synapse_core #(
    parameter integer H_COUNT=4,SOURCE_COUNT=12,EDGE_COUNT=12,WEIGHT_COUNT=8,
    parameter integer STEP_TIMEOUT=8000000,
    parameter WEIGHT_FILE="rom/weights.mem",NEURON_FILE="rom/neurons.mem"
)(
    input wire clk,rst_n,req_begin,in_we,start,
    input wire [15:0] in_addr,input wire signed [31:0] in_data,
    input wire [31:0] step_id,old_state_tag,input wire [63:0] expected_signature,
    input wire [63:0] edge_data,input wire edge_valid,output wire edge_ready,
    input wire transport_done,input wire [31:0] transport_error,
    output wire busy,output reg done,out_valid,output reg [31:0] status,cycles,
    output reg [31:0] result_step_id,result_old_state_tag,edges_applied,
    output reg [63:0] signature,
    input wire [12:0] out_addr,output wire signed [31:0] out_data,
    output reg trace_valid,output reg [20:0] trace_gid,
    output reg [12:0] trace_target,output reg signed [30:0] trace_term,
    output reg signed [49:0] trace_sum
);
    localparam IDLE=0,LOAD=1,CLEAR=2,EDGES=3,V_PASS=4,D_PASS=5,WAIT_END=6,FINISH=7,ERROR=8;
    reg [3:0] state;
    reg [31:0] loaded,issued,retired;
    reg [12:0] h_index;
    reg [20:0] previous_gid;
    reg previous_valid,ingress_blocked,transport_seen;
    reg [63:0] expected_sig;
    (* ram_style="block" *) reg signed [30:0] source_mem[0:SOURCE_COUNT-1];
    (* ram_style="block" *) reg signed [30:0] x_mem[0:H_COUNT-1];
    (* ram_style="block" *) reg signed [49:0] chemical_mem[0:H_COUNT-1];
    (* ram_style="block" *) reg signed [30:0] velocity_mem[0:H_COUNT-1];
    (* ram_style="block" *) reg signed [30:0] candidate_mem[0:H_COUNT-1];
    (* rom_style="block" *) reg signed [23:0] weight_rom[0:WEIGHT_COUNT-1];
    (* rom_style="block" *) reg [61:0] neuron_rom[0:H_COUNT-1];
    initial begin $readmemh(WEIGHT_FILE,weight_rom);$readmemh(NEURON_FILE,neuron_rom);end
    reg signed [30:0] source_q,x_q,velocity_q,candidate_q;
    reg signed [49:0] chemical_q;
    reg signed [23:0] weight_q;
    reg [61:0] neuron_q;
    reg candidate_addr_valid;
    reg [6:0] valid_pipe;
    reg [63:0] meta_pipe[0:6];
    reg [3:0] mode_pipe[0:6];
    reg [31:0] error_pipe[0:6];
    reg signed [30:0] old_pipe[1:6];
    reg signed [32:0] mul_a;
    reg signed [30:0] mul_b;
    wire signed [63:0] product;
    reg signed [44:0] rounded_q;
    reg signed [30:0] term_q,new_q;
    reg last_write_valid;
    reg [12:0] last_write_target;
    reg signed [49:0] last_write_sum;
    // Full trace identity is retained in RTL simulation; unused debug fields
    // may be removed by synthesis. Public trace pins remain unchanged.
    reg [63:0] trace_record;
    reg signed [30:0] trace_source_value;
    wire active_phase=(state==EDGES)||(state==V_PASS)||(state==D_PASS);
    wire protocol_fault=req_begin||in_we||start;
    wire step_error=(transport_error!=0)||(cycles>=STEP_TIMEOUT);
    wire [14:0] incoming_src=edge_data[35:21];
    wire [12:0] incoming_target=edge_data[48:36];
    wire [9:0] incoming_weight=edge_data[58:49];
    wire incoming_bad=(edge_data[63:59]!=0)||(incoming_src>=SOURCE_COUNT)||
        (incoming_target>=H_COUNT)||(incoming_weight>=WEIGHT_COUNT)||
        (previous_valid&&edge_data[20:0]<=previous_gid);
    assign edge_ready=(state==EDGES)&&(issued<EDGE_COUNT)&&!ingress_blocked&&!step_error&&!protocol_fault;
    wire issue_edge=edge_ready&&edge_valid;
    wire issue_node=((state==V_PASS)||(state==D_PASS))&&(issued<H_COUNT)&&!step_error&&!protocol_fault;
    wire issue=issue_edge||issue_node;
    wire source_re=issue&&(!issue_edge||!incoming_bad);
    wire [14:0] source_raddr=issue_edge?incoming_src:issued[14:0];
    wire chemical_re=(issue_node&&state==V_PASS)||(valid_pipe[5]&&mode_pipe[5]==EDGES&&error_pipe[5]==0);
    wire [12:0] chemical_raddr=(state==V_PASS)?issued[12:0]:meta_pipe[5][48:36];
    wire load_ok=(state==LOAD)&&in_we&&(loaded<SOURCE_COUNT+H_COUNT)&&
        (in_addr==loaded)&&(in_data[31]==in_data[30])&&!req_begin;
    wire signed [32:0] drive_sum=-$signed({{2{source_q[30]}},source_q})+
        $signed({{2{neuron_q[30]}},neuron_q[30:0]})+
        $signed({{2{chemical_q[30]}},chemical_q[30:0]})+
        $signed({{2{x_q[30]}},x_q});
    // Equivalent to abs/add-half/restore-sign, with only one narrow carry chain.
    // For negative exact halves keep floor; otherwise round up past half.
    wire inc20=product[19]&&(!product[63]||(|product[18:0]));
    wire inc24=product[23]&&(!product[63]||(|product[22:0]));
    wire signed [44:0] round20=$signed({product[63],product[63:20]})+$signed({44'b0,inc20});
    wire signed [40:0] round24=$signed({product[63],product[63:24]})+$signed({40'b0,inc24});
    wire rounded_fits=(rounded_q[44:31]=={14{rounded_q[30]}});
    wire signed [31:0] candidate_sum=$signed({old_pipe[5][30],old_pipe[5]})+
        $signed({rounded_q[30],rounded_q[30:0]});
    wire [12:0] retire_target=meta_pipe[6][48:36];
    wire signed [49:0] chemical_base=(last_write_valid&&last_write_target==retire_target)?last_write_sum:chemical_q;
    wire signed [50:0] chemical_sum=$signed({chemical_base[49],chemical_base})+
        $signed({{20{term_q[30]}},term_q});
    wire retire=active_phase&&valid_pipe[6]&&!protocol_fault&&!step_error;
    wire [31:0] retire_error=error_pipe[6]|
        ((mode_pipe[6]==EDGES&&chemical_sum[50]!=chemical_sum[49])?32'h2:32'h0);
    wire edge_write=retire&&(mode_pipe[6]==EDGES)&&(retire_error==0);
    wire velocity_write=retire&&(mode_pipe[6]==V_PASS)&&(retire_error==0);
    wire candidate_write=retire&&(mode_pipe[6]==D_PASS)&&(retire_error==0);
    wire chemical_we=(state==CLEAR)||edge_write;
    wire [12:0] chemical_waddr=(state==CLEAR)?h_index:retire_target;
    wire signed [49:0] chemical_wdata=(state==CLEAR)?50'sd0:chemical_sum[49:0];
    assign busy=(state!=IDLE);
    assign out_data=(out_valid&&status==0&&candidate_addr_valid)?{candidate_q[30],candidate_q}:32'sd0;
    pipe_mul33x31 multiplier(.clk(clk),.a(mul_a),.b(mul_b),.product(product));
    integer k;
    always @(posedge clk) begin
        if(load_ok) begin
            if(in_addr<SOURCE_COUNT) source_mem[in_addr]<=in_data[30:0];
            else x_mem[in_addr-SOURCE_COUNT]<=in_data[30:0];
        end
        if(source_re) source_q<=source_mem[source_raddr];
        if(issue_edge&&!incoming_bad) weight_q<=weight_rom[incoming_weight];
        if(issue_node&&state==V_PASS) begin x_q<=x_mem[issued[12:0]];neuron_q<=neuron_rom[issued[12:0]];end
        if(issue_node&&state==D_PASS) velocity_q<=velocity_mem[issued[12:0]];
        if(chemical_re) chemical_q<=chemical_mem[chemical_raddr];
        if(chemical_we) chemical_mem[chemical_waddr]<=chemical_wdata;
        if(velocity_write) velocity_mem[retire_target]<=term_q;
        if(candidate_write) candidate_mem[retire_target]<=new_q;
        candidate_addr_valid<=out_addr<H_COUNT;
        if(out_addr<H_COUNT) candidate_q<=candidate_mem[out_addr];
        if(!rst_n||req_begin||!active_phase) valid_pipe<=0;
        else valid_pipe<={valid_pipe[5:0],issue};
        if(issue) begin
            meta_pipe[0]<=issue_edge?edge_data:{15'b0,issued[12:0],36'b0};
            mode_pipe[0]<=state;error_pipe[0]<=(issue_edge&&incoming_bad)?32'h10:0;
        end
        for(k=1;k<=6;k=k+1) if(valid_pipe[k-1]) begin
            meta_pipe[k]<=meta_pipe[k-1];mode_pipe[k]<=mode_pipe[k-1];
            error_pipe[k]<=error_pipe[k-1];
            if(k>1) old_pipe[k]<=old_pipe[k-1];
        end
        if(valid_pipe[0]) begin
            old_pipe[1]<=source_q;
            if(mode_pipe[0]==EDGES) begin mul_a<=source_q[30]?33'sd0:$signed({{2{source_q[30]}},source_q});mul_b<=$signed({{7{weight_q[23]}},weight_q});end
            else if(mode_pipe[0]==V_PASS) begin
                mul_a<=drive_sum;mul_b<=neuron_q[61:31];
                if(chemical_q[49:31]!={19{chemical_q[30]}}) error_pipe[1]<=error_pipe[0]|32'h4;
            end else begin mul_a<=$signed({{2{velocity_q[30]}},velocity_q});mul_b<=31'sd83886;end
        end
        if(valid_pipe[4]) rounded_q<=(mode_pipe[4]==EDGES)?round20:{{4{round24[40]}},round24};
        if(valid_pipe[5]) begin
            term_q<=rounded_q[30:0];new_q<=candidate_sum[30:0];
            if(!rounded_fits||(mode_pipe[5]==D_PASS&&candidate_sum[31]!=candidate_sum[30]))
                error_pipe[6]<=error_pipe[5]|32'h4;
        end
        if(!rst_n||req_begin||state==CLEAR) last_write_valid<=0;
        else if(edge_write) begin last_write_valid<=1;last_write_target<=retire_target;last_write_sum<=chemical_sum[49:0];end
    end
    always @(posedge clk) begin
        if(!rst_n) begin
            state<=IDLE;loaded<=0;issued<=0;retired<=0;h_index<=0;done<=0;out_valid<=0;status<=0;cycles<=0;
            previous_gid<=0;previous_valid<=0;ingress_blocked<=0;edges_applied<=0;signature<=0;
            transport_seen<=0;expected_sig<=0;trace_valid<=0;trace_gid<=0;trace_target<=0;trace_term<=0;trace_sum<=0;
            trace_record<=0;trace_source_value<=0;result_step_id<=0;result_old_state_tag<=0;
        end else begin
            done<=0;trace_valid<=0;
            if(state!=IDLE&&state!=LOAD) begin cycles<=cycles+1;if(transport_done) transport_seen<=1;end
            if(req_begin) begin
                if(state==IDLE) begin
                    state<=LOAD;loaded<=0;issued<=0;retired<=0;status<=0;out_valid<=0;cycles<=0;
                    edges_applied<=0;signature<=0;previous_valid<=0;ingress_blocked<=0;transport_seen<=0;
                    expected_sig<=expected_signature;result_step_id<=step_id;result_old_state_tag<=old_state_tag;
                end else begin status<=32'h8;out_valid<=0;state<=ERROR;end
            end else if((in_we&&state!=LOAD)||(start&&state!=LOAD)) begin status<=32'h8;out_valid<=0;state<=ERROR;end
            else if(state!=IDLE&&state!=LOAD&&state!=ERROR&&step_error) begin status<=transport_error!=0?32'h40:32'h80;out_valid<=0;state<=ERROR;end
            else if(retire&&retire_error!=0) begin status<=retire_error;out_valid<=0;state<=ERROR;end
            else case(state)
                IDLE:begin end
                LOAD:begin
                    if(in_we) begin
                        if(!load_ok) status<=status|32'h8|((in_data[31]!=in_data[30])?32'h1:0);
                        else loaded<=loaded+1;
                    end
                    if(start) begin
                        if(loaded==SOURCE_COUNT+H_COUNT&&status==0&&!in_we) begin h_index<=0;state<=CLEAR;end
                        else begin status<=status|32'h8;state<=ERROR;end
                    end
                end
                CLEAR:if(h_index==H_COUNT-1) state<=EDGES;else h_index<=h_index+1;
                EDGES:begin
                    if(issue_edge) begin
                        issued<=issued+1;previous_gid<=edge_data[20:0];previous_valid<=1;
                        if(incoming_bad) ingress_blocked<=1;
                    end
                    if(edge_write) begin
                        edges_applied<=edges_applied+1;signature<={signature[62:0],signature[63]}^meta_pipe[6];
                        trace_valid<=1;trace_gid<=meta_pipe[6][20:0];trace_target<=retire_target;
                        trace_term<=term_q;trace_sum<=chemical_sum[49:0];trace_record<=meta_pipe[6];trace_source_value<=old_pipe[6];
                        if(edges_applied==EDGE_COUNT-1) state<=WAIT_END;
                    end
                end
                WAIT_END:begin
                    if(edge_valid||edges_applied!=EDGE_COUNT) begin status<=32'h20;state<=ERROR;end
                    else if(transport_seen||transport_done) begin
                        if(signature!=expected_sig) begin status<=32'h20;state<=ERROR;end
                        else begin issued<=0;retired<=0;state<=V_PASS;end
                    end
                end
                V_PASS,D_PASS:begin
                    if(issue_node) issued<=issued+1;
                    if(velocity_write||candidate_write) begin
                        retired<=retired+1;
                        if(retired==H_COUNT-1) begin
                            issued<=0;retired<=0;state<=(state==V_PASS)?D_PASS:FINISH;
                        end
                    end
                end
                FINISH:begin done<=1;out_valid<=1;state<=IDLE;end
                ERROR:begin done<=1;out_valid<=0;state<=IDLE;end
                default:begin status<=32'h8;out_valid<=0;state<=ERROR;end
            endcase
        end
    end
endmodule

// Four partial products, then two registered adder levels. All three phases
// use this one multiplier at initiation interval 1. Exact signed 33x31->64.
module pipe_mul33x31(input wire clk,input wire signed [32:0] a,input wire signed [30:0] b,
    output reg signed [63:0] product);
    (* use_dsp="yes" *) reg signed [35:0] ll;
    (* use_dsp="yes" *) reg signed [33:0] hl;
    (* use_dsp="yes" *) reg signed [31:0] lh;
    (* use_dsp="yes" *) reg signed [29:0] hh;
    reg signed [63:0] lower,upper;
    always @(posedge clk) begin
        ll<=$signed({1'b0,a[16:0]})*$signed({1'b0,b[16:0]});
        hl<=$signed(a[32:17])*$signed({1'b0,b[16:0]});
        lh<=$signed({1'b0,a[16:0]})*$signed(b[30:17]);
        hh<=$signed(a[32:17])*$signed(b[30:17]);
        lower<=$signed({{28{ll[35]}},ll})+($signed({{30{hl[33]}},hl})<<<17);
        upper<=$signed({{32{lh[31]}},lh})+($signed({{34{hh[29]}},hh})<<<17);
        product<=lower+(upper<<<17);
    end
endmodule

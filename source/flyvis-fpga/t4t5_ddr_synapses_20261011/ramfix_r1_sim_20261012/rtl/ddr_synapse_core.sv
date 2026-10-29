`timescale 1ns/1ps
// B candidate: source cache is old_H followed by old_Rin; separate x and
// candidate banks. Q24 state/Q20 weight, nearest ties away, reject overflow.
// Sequential edges serialize chemical RMW, even for consecutive same target.
module ddr_synapse_core #(
    parameter integer H_COUNT=4,SOURCE_COUNT=12,EDGE_COUNT=12,WEIGHT_COUNT=8,
    parameter integer STEP_TIMEOUT=2000000,
    parameter WEIGHT_FILE="rom/weights.mem",NEURON_FILE="rom/neurons.mem"
)(
    input wire clk,rst_n,req_begin,in_we,start,
    input wire [15:0] in_addr,input wire signed [31:0] in_data,
    input wire [31:0] step_id,old_state_tag,
    input wire [63:0] expected_signature,
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
    localparam IDLE=0,LOAD=1,CLEAR=2,FETCH=3,CHECK=4,READ=5,MUL=6,
        ROUND=7,SUM=8,WAIT_END=9,N_READ=10,N_DRIVE=11,N_VMUL=12,
        N_VROUND=13,N_DMUL=14,N_NEW=15,FINISH=16,ERROR=17;
    reg [4:0] state;
    reg [31:0] loaded;
    reg [12:0] h_index;
    reg [63:0] meta,expected_sig;
    reg [20:0] previous_gid;
    reg previous_valid,transport_seen;
    (* ram_style="block" *) reg signed [30:0] source_mem[0:SOURCE_COUNT-1];
    (* ram_style="block" *) reg signed [30:0] x_mem[0:H_COUNT-1];
    (* ram_style="block" *) reg signed [49:0] chemical_mem[0:H_COUNT-1];
    (* ram_style="block" *) reg signed [30:0] candidate_mem[0:H_COUNT-1];
    (* rom_style="block" *) reg signed [23:0] weight_rom[0:WEIGHT_COUNT-1];
    (* rom_style="block" *) reg [61:0] neuron_rom[0:H_COUNT-1];
    initial begin $readmemh(WEIGHT_FILE,weight_rom);$readmemh(NEURON_FILE,neuron_rom);end
    reg signed [30:0] source_q,x_q,candidate_q;
    reg signed [49:0] chemical_q;
    reg signed [23:0] weight_q;
    reg [61:0] neuron_q;
    reg candidate_addr_valid;
    wire [20:0] gid=meta[20:0];wire [14:0] src=meta[35:21];
    wire [12:0] target=meta[48:36];wire [9:0] weight_index=meta[58:49];
    reg signed [30:0] old_h,inv_tau,velocity,edge_term;
    reg signed [32:0] drive,mul_a;reg signed [30:0] mul_b;
    reg signed [63:0] product;
    function automatic signed [63:0] rounded(input signed [63:0] val,input integer shift);
        reg signed [64:0] ext,mag,q;
        begin ext={val[63],val};mag=(ext<0)?-ext:ext;
            q=(mag+(65'sd1<<<(shift-1)))>>>shift;rounded=(ext<0)?-q:q;end
    endfunction
    function automatic fits31(input signed [63:0] val);
        begin fits31=(val[63:31]=={33{val[30]}});end
    endfunction
    wire signed [63:0] re=rounded(product,20),rn=rounded(product,24);
    wire signed [50:0] sum=$signed({chemical_q[49],chemical_q})+$signed({{20{edge_term[30]}},edge_term});
    wire signed [31:0] new_sum=$signed({old_h[30],old_h})+$signed({rn[30],rn[30:0]});
    wire neuron_ok=fits31(rn)&&(new_sum[31]==new_sum[30]);
    wire signed [32:0] drive_sum=-$signed({{2{source_q[30]}},source_q})
        +$signed({{2{neuron_q[30]}},neuron_q[30:0]})
        +$signed({{2{chemical_q[30]}},chemical_q[30:0]})
        +$signed({{2{x_q[30]}},x_q});
    wire load_ok=(state==LOAD)&&in_we&&(loaded<SOURCE_COUNT+H_COUNT)
        &&(in_addr==loaded)&&(in_data[31]==in_data[30])&&!req_begin;
    wire step_error=(transport_error!=0)||(cycles>=STEP_TIMEOUT);
    wire edge_write=(state==SUM)&&(sum[50]==sum[49])&&!step_error&&!req_begin&&!in_we&&!start;
    // CLEAR and SUM are mutually exclusive: one physical RAM write port.
    wire chemical_we=(state==CLEAR)||edge_write;
    wire [12:0] chemical_waddr=(state==CLEAR)?h_index:target;
    wire signed [49:0] chemical_wdata=(state==CLEAR)?50'sd0:sum[49:0];
    wire cand_write=(state==N_NEW)&&neuron_ok&&!step_error&&!req_begin&&!in_we&&!start;
    assign edge_ready=(state==FETCH)&&!step_error&&!req_begin&&!in_we&&!start;
    assign busy=(state!=IDLE);
    assign out_data=(out_valid&&status==0&&candidate_addr_valid)?{candidate_q[30],candidate_q}:32'sd0;
    always @* begin
        mul_a=0;mul_b=0;
        case(state)
            MUL:begin mul_a=source_q[30]?33'sd0:$signed({{2{source_q[30]}},source_q});
                mul_b=$signed({{7{weight_q[23]}},weight_q});end
            N_VMUL:begin mul_a=drive;mul_b=inv_tau;end
            N_DMUL:begin mul_a=$signed({{2{velocity[30]}},velocity});mul_b=31'sd83886;end
            default:begin end
        endcase
    end
    always @(posedge clk) begin
        if(load_ok) begin
            if(in_addr<SOURCE_COUNT) source_mem[in_addr]<=in_data[30:0];
            else x_mem[in_addr-SOURCE_COUNT]<=in_data[30:0];
        end
        if(chemical_we) chemical_mem[chemical_waddr]<=chemical_wdata;
        if(state==READ) begin
            source_q<=source_mem[src];weight_q<=weight_rom[weight_index];chemical_q<=chemical_mem[target];
        end
        if(state==N_READ) begin
            source_q<=source_mem[h_index];x_q<=x_mem[h_index];
            chemical_q<=chemical_mem[h_index];neuron_q<=neuron_rom[h_index];
        end
        if(state==MUL||state==N_VMUL||state==N_DMUL) product<=mul_a*mul_b;
        if(cand_write) candidate_mem[h_index]<=new_sum[30:0];
        candidate_addr_valid<=out_addr<H_COUNT;
        if(out_addr<H_COUNT) candidate_q<=candidate_mem[out_addr];
    end
    always @(posedge clk) begin
        if(!rst_n) begin
            state<=IDLE;loaded<=0;h_index<=0;done<=0;out_valid<=0;status<=0;cycles<=0;
            previous_gid<=0;previous_valid<=0;edges_applied<=0;signature<=0;
            transport_seen<=0;trace_valid<=0;trace_gid<=0;trace_target<=0;trace_term<=0;trace_sum<=0;
            result_step_id<=0;result_old_state_tag<=0;expected_sig<=0;meta<=0;
        end else begin
            done<=0;trace_valid<=0;
            if(state!=IDLE&&state!=LOAD) begin
                cycles<=cycles+1;
                if(transport_done) transport_seen<=1;
            end
            if(req_begin) begin
                if(state==IDLE) begin
                    state<=LOAD;loaded<=0;status<=0;out_valid<=0;cycles<=0;edges_applied<=0;signature<=0;
                    previous_valid<=0;transport_seen<=0;
                    result_step_id<=step_id;result_old_state_tag<=old_state_tag;expected_sig<=expected_signature;
                end else begin status<=32'h8;out_valid<=0;state<=ERROR;end
            end else if((in_we&&state!=LOAD)||(start&&state!=LOAD)) begin status<=32'h8;out_valid<=0;state<=ERROR;end
            else if(state!=IDLE&&state!=LOAD&&state!=ERROR&&step_error) begin
                status<=transport_error!=0?32'h40:32'h80;out_valid<=0;state<=ERROR;
            end else case(state)
                IDLE:begin end
                LOAD:begin
                    if(in_we) begin
                        if(!load_ok) status<=status|32'h8 | ((in_data[31]!=in_data[30])?32'h1:0);
                        else loaded<=loaded+1;
                    end
                    if(start) begin
                        if(loaded==SOURCE_COUNT+H_COUNT&&status==0&&!in_we) begin h_index<=0;state<=CLEAR;end
                        else begin status<=status|32'h8;state<=ERROR;end
                    end
                end
                CLEAR:begin
                    if(h_index==H_COUNT-1) begin h_index<=0;state<=FETCH;end else h_index<=h_index+1;
                end
                FETCH:if(edge_valid) begin meta<=edge_data;state<=CHECK;end
                CHECK:begin
                    if(meta[63:59]!=0||src>=SOURCE_COUNT||target>=H_COUNT||weight_index>=WEIGHT_COUNT
                        ||(previous_valid&&gid<=previous_gid)) begin status<=32'h10;state<=ERROR;end
                    else state<=READ;
                end
                READ:state<=MUL;
                MUL:state<=ROUND;
                ROUND:begin
                    if(!fits31(re)) begin status<=32'h4;state<=ERROR;end
                    else begin edge_term<=re[30:0];state<=SUM;end
                end
                SUM:begin
                    if(sum[50]!=sum[49]) begin status<=32'h2;state<=ERROR;end
                    else begin
                        trace_valid<=1;trace_gid<=gid;trace_target<=target;trace_term<=edge_term;trace_sum<=sum[49:0];
                        edges_applied<=edges_applied+1;signature<={signature[62:0],signature[63]}^meta;
                        previous_gid<=gid;previous_valid<=1;
                        state<=(edges_applied==EDGE_COUNT-1)?WAIT_END:FETCH;
                    end
                end
                WAIT_END:begin
                    if(edge_valid||edges_applied!=EDGE_COUNT) begin status<=32'h20;state<=ERROR;end
                    else if(transport_seen||transport_done) begin
                        if(signature!=expected_sig) begin status<=32'h20;state<=ERROR;end
                        else begin h_index<=0;state<=N_READ;end
                    end
                end
                N_READ:state<=N_DRIVE;
                N_DRIVE:begin
                    if(chemical_q[49:31]!={19{chemical_q[30]}}) begin status<=32'h4;state<=ERROR;end
                    else begin old_h<=source_q;inv_tau<=neuron_q[61:31];drive<=drive_sum;state<=N_VMUL;end
                end
                N_VMUL:state<=N_VROUND;
                N_VROUND:begin
                    if(!fits31(rn)) begin status<=32'h4;state<=ERROR;end
                    else begin velocity<=rn[30:0];state<=N_DMUL;end
                end
                N_DMUL:state<=N_NEW;
                N_NEW:begin
                    if(!neuron_ok) begin status<=32'h4;state<=ERROR;end
                    else if(h_index==H_COUNT-1) state<=FINISH;
                    else begin h_index<=h_index+1;state<=N_READ;end
                end
                FINISH:begin done<=1;out_valid<=1;state<=IDLE;end
                ERROR:begin done<=1;out_valid<=0;state<=IDLE;end
                default:begin status<=32'h8;state<=ERROR;end
            endcase
        end
    end
endmodule

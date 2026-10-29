`timescale 1ns/1ps
// Research-only SOURCE_RAW core. No AXI/PS/board interface. Q24/Q20 profile.
// A complete edge read/modify/write finishes before another edge can issue.
module scalable_source_raw_core #(
    parameter integer H_COUNT=92, B_COUNT=1900, EDGE_COUNT=9207,
    parameter integer BANKS=1,
    parameter EDGE_FILE="rom/edges.mem", NEURON_FILE="rom/neurons.mem"
) (
    input wire clk, rst_n, req_begin, in_we, start,
    input wire [$clog2(B_COUNT+2*H_COUNT)-1:0] in_addr,
    input wire signed [31:0] in_data,
    output wire busy,
    output reg done, out_valid,
    output reg [31:0] status, compute_cycles,
    input wire [$clog2(H_COUNT)-1:0] out_addr,
    output wire signed [31:0] out_data,
    output reg trace_valid,
    output reg [20:0] trace_gid,
    output reg [$clog2(H_COUNT)-1:0] trace_target,
    output reg signed [30:0] trace_term,
    output reg signed [49:0] trace_sum
);
    localparam integer WORDS=B_COUNT+2*H_COUNT, AW=$clog2(WORDS);
    localparam integer HW=$clog2(H_COUNT), EW=$clog2(EDGE_COUNT);
    localparam integer SW=$clog2((B_COUNT>H_COUNT)?B_COUNT:H_COUNT);
    localparam integer MW=21+1+SW+HW+24;
    localparam integer ROWS=(H_COUNT+BANKS-1)/BANKS;
    localparam integer RW=(ROWS>1)?$clog2(ROWS):1;
    localparam integer BW=(BANKS>1)?$clog2(BANKS):1;
    localparam [4:0] IDLE=0, LOAD=1, CLEAR=2, E_FETCH=3, E_CHECK=4,
        E_READ=5, E_MUL=6, E_ROUND=7, E_SUM=8, N_READ=9, N_DRIVE=10,
        N_VMUL=11, N_VROUND=12, N_DMUL=13, N_NEW=14, FINISH=15, ERROR=16;
    reg [4:0] state;
    reg [AW:0] loaded;
    reg [HW-1:0] h_index;
    reg [EW-1:0] e_index;
    reg [20:0] previous_gid;
    reg previous_valid;

    // True dual read request BRAM: one write port while idle/loading, two
    // synchronous read ports during compute (old_H and x_H in N_READ).
    (* ram_style="block" *) reg signed [30:0] request_mem [0:WORDS-1];
    reg signed [30:0] req_q_a, req_q_b;
    wire load_write=(state==LOAD && in_we && loaded<WORDS && in_addr==loaded
        && in_data[31]==in_data[30] && !req_begin);
    wire request_read=(state==E_READ || state==N_READ);
    reg [AW-1:0] req_addr_a, req_addr_b;

    (* rom_style="block" *) reg [MW-1:0] edge_rom [0:EDGE_COUNT-1];
    (* rom_style="block" *) reg [61:0] neuron_rom [0:H_COUNT-1];
    reg [MW-1:0] meta;
    reg [61:0] neuron_q;
    initial begin
        if(BANKS!=1 && BANKS!=2 && BANKS!=4) $error("BANKS must be 1/2/4");
        $readmemh(EDGE_FILE,edge_rom); $readmemh(NEURON_FILE,neuron_rom);
    end
    always @(posedge clk) begin
        if(state==E_FETCH) meta<=edge_rom[e_index];
        if(state==N_READ) neuron_q<=neuron_rom[h_index];
    end
    wire signed [23:0] weight=meta[23:0];
    wire [HW-1:0] target=meta[24+:HW];
    wire [SW-1:0] source_index=meta[24+HW+:SW];
    wire source_is_h=meta[24+HW+SW];
    wire [20:0] global_edge_id=meta[MW-1-:21];

    // Separate synchronous chemical banks. No asynchronous array reads and
    // no same-clock read/write collision. BANKS changes placement, not order.
    wire edge_ok;
    wire signed [50:0] edge_sum;
    wire chem_read=(state==E_READ || state==N_READ);
    wire chem_write=(state==CLEAR || (state==E_SUM && edge_ok));
    wire [HW-1:0] chem_target=(state==E_READ || state==E_SUM)?target:h_index;
    wire [BW-1:0] chem_bank=chem_target % BANKS;
    wire [RW-1:0] chem_row=chem_target / BANKS;
    wire signed [49:0] chem_wr_data=(state==CLEAR)?50'sd0:edge_sum[49:0];
    wire signed [49:0] chem_q [0:BANKS-1];
    wire signed [49:0] chemical_read=chem_q[chem_bank];

    (* ram_style="block" *) reg signed [30:0] candidate_mem [0:H_COUNT-1];
    reg signed [30:0] candidate_q;
    // Output read latency is one rising clock; invalid candidates are hidden.
    assign out_data=(out_valid && status==0)?{candidate_q[30],candidate_q}:32'sd0;
    assign busy=(state!=IDLE);

    reg signed [30:0] old_h, inv_tau, velocity, edge_term;
    reg signed [32:0] drive;
    reg signed [63:0] product;
    reg signed [32:0] mul_a;
    reg signed [30:0] mul_b;
    // Exactly one multiply expression shared across edge, velocity and dt.
    always @* begin
        mul_a=0; mul_b=0;
        case(state)
            E_MUL: begin
                mul_a=req_q_a[30]?33'sd0:$signed({{2{req_q_a[30]}},req_q_a});
                mul_b=$signed({{7{weight[23]}},weight});
            end
            N_VMUL: begin mul_a=drive; mul_b=inv_tau; end
            N_DMUL: begin mul_a=$signed({{2{velocity[30]}},velocity}); mul_b=31'sd83886; end
            default: begin end
        endcase
    end
    // 65-bit magnitude prevents negation/half-add overflow at signed64 min.
    function automatic signed [63:0] rounded;
        input signed [63:0] value;
        input integer shift;
        reg signed [64:0] extended, magnitude, result;
        begin
            extended={value[63],value};
            magnitude=(extended<0)?-extended:extended;
            result=(magnitude+(65'sd1<<<(shift-1)))>>>shift;
            rounded=(extended<0)?-result:result;
        end
    endfunction
    function automatic fits31;
        input signed [63:0] value;
        begin fits31=(value[63:31]=={33{value[30]}}); end
    endfunction
    wire signed [63:0] rounded_edge=rounded(product,20);
    wire signed [63:0] rounded_state=rounded(product,24);
    assign edge_sum=$signed({chemical_read[49],chemical_read})
        +$signed({{20{edge_term[30]}},edge_term});
    assign edge_ok=(edge_sum[50]==edge_sum[49]);
    wire signed [31:0] new_sum=$signed({old_h[30],old_h})
        +$signed({rounded_state[30],rounded_state[30:0]});
    wire neuron_ok=fits31(rounded_state) && new_sum[31]==new_sum[30];
    wire signed [32:0] drive_sum=-$signed({{2{req_q_a[30]}},req_q_a})
        +$signed({{2{neuron_q[30]}},neuron_q[30:0]})
        +$signed({{2{chemical_read[30]}},chemical_read[30:0]})
        +$signed({{2{req_q_b[30]}},req_q_b});

    always @* begin
        req_addr_a=0; req_addr_b=0;
        if(state==E_READ) req_addr_a=source_is_h ? B_COUNT+source_index : source_index;
        if(state==N_READ) begin
            req_addr_a=B_COUNT+h_index; req_addr_b=B_COUNT+H_COUNT+h_index;
        end
    end
    always @(posedge clk) begin
        if(load_write) request_mem[in_addr]<=in_data[30:0];
        if(request_read) begin
            req_q_a<=request_mem[req_addr_a]; req_q_b<=request_mem[req_addr_b];
        end
        if(state==N_NEW && neuron_ok) candidate_mem[h_index]<=new_sum[30:0];
        if(out_addr<H_COUNT) candidate_q<=candidate_mem[out_addr];
    end
    genvar bank;
    generate for(bank=0;bank<BANKS;bank=bank+1) begin: chemical_banks
        (* ram_style="block" *) reg signed [49:0] mem [0:ROWS-1];
        reg signed [49:0] q;
        always @(posedge clk) begin
            if(chem_write && chem_bank==bank) mem[chem_row]<=chem_wr_data;
            if(chem_read && chem_bank==bank) q<=mem[chem_row];
        end
        assign chem_q[bank]=q;
    end endgenerate

    always @(posedge clk) begin
        if(!rst_n) begin
            state<=IDLE; loaded<=0; h_index<=0; e_index<=0;
            previous_gid<=0; previous_valid<=0;
            done<=0; out_valid<=0; status<=0; compute_cycles<=0; trace_valid<=0;
            trace_gid<=0; trace_target<=0; trace_term<=0; trace_sum<=0;
        end else begin
            done<=0; trace_valid<=0;
            if(state!=IDLE && state!=LOAD) compute_cycles<=compute_cycles+1;
            if(req_begin) begin
                if(state==IDLE) begin
                    state<=LOAD; loaded<=0; status<=0; out_valid<=0;
                    compute_cycles<=0; previous_valid<=0;
                end else begin status[3]<=1; out_valid<=0; state<=ERROR; end
            end else if((in_we && state!=LOAD)||(start && state!=LOAD)) begin
                status[3]<=1; out_valid<=0; state<=ERROR;
            end else case(state)
                IDLE: begin end
                LOAD: begin
                    if(in_we) begin
                        if(loaded>=WORDS || in_addr!=loaded) status[3]<=1;
                        else begin
                            loaded<=loaded+1;
                            if(in_data[31]!=in_data[30]) status[0]<=1;
                        end
                    end
                    if(start) begin
                        if(loaded==WORDS && status==0 && !in_we) begin
                            h_index<=0; e_index<=0; state<=CLEAR; compute_cycles<=0;
                        end else begin status[3]<=1; state<=ERROR; end
                    end
                end
                CLEAR: begin
                    if(h_index==H_COUNT-1) begin h_index<=0; state<=E_FETCH; end
                    else h_index<=h_index+1;
                end
                E_FETCH: state<=E_CHECK;
                E_CHECK: begin
                    if(target>=H_COUNT || (source_is_h && source_index>=H_COUNT)
                        ||(!source_is_h && source_index>=B_COUNT)
                        ||(previous_valid && global_edge_id<=previous_gid)) begin
                        status[4]<=1; state<=ERROR;
                    end else state<=E_READ;
                end
                E_READ: state<=E_MUL;
                E_MUL: begin product<=mul_a*mul_b; state<=E_ROUND; end
                E_ROUND: begin
                    if(!fits31(rounded_edge)) begin status[2]<=1; state<=ERROR; end
                    else begin edge_term<=rounded_edge[30:0]; state<=E_SUM; end
                end
                E_SUM: begin
                    if(!edge_ok) begin status[1]<=1; state<=ERROR; end
                    else begin
                        trace_valid<=1; trace_gid<=global_edge_id; trace_target<=target;
                        trace_term<=edge_term; trace_sum<=edge_sum[49:0];
                        previous_gid<=global_edge_id; previous_valid<=1;
                        if(e_index==EDGE_COUNT-1) begin h_index<=0; state<=N_READ; end
                        else begin e_index<=e_index+1; state<=E_FETCH; end
                    end
                end
                N_READ: state<=N_DRIVE;
                N_DRIVE: begin
                    if(chemical_read[49:31]!={19{chemical_read[30]}}) begin status[2]<=1; state<=ERROR; end
                    else begin
                        old_h<=req_q_a; inv_tau<=neuron_q[61:31];
                        drive<=drive_sum; state<=N_VMUL;
                    end
                end
                N_VMUL: begin product<=mul_a*mul_b; state<=N_VROUND; end
                N_VROUND: begin
                    if(!fits31(rounded_state)) begin status[2]<=1; state<=ERROR; end
                    else begin velocity<=rounded_state[30:0]; state<=N_DMUL; end
                end
                N_DMUL: begin product<=mul_a*mul_b; state<=N_NEW; end
                N_NEW: begin
                    if(!neuron_ok) begin status[2]<=1; state<=ERROR; end
                    else if(h_index==H_COUNT-1) state<=FINISH;
                    else begin h_index<=h_index+1; state<=N_READ; end
                end
                FINISH: begin done<=1; out_valid<=1; state<=IDLE; end
                ERROR: begin done<=1; out_valid<=0; state<=IDLE; end
                default: begin status[3]<=1; state<=ERROR; end
            endcase
        end
    end
endmodule

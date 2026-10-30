// Integer-only FP32 lane with synchronous memories. No DPI in DUT.
// LM/LA match the true internal pipelines; timing must still be implemented.
module flyvis_lane #(
    parameter integer N=45669, NT=65, NR=605, NE=1513231,
    parameter integer LM=8, LA=13, EU_CONTEXTS=32,
    parameter META_FILE="", MAP_FILE="", ROWS_FILE="", STATE_FILE=""
)(
    input logic clk,reset,
    input logic restore_req,output logic restore_busy,restore_done,
    input logic inspect_valid,input logic [15:0] inspect_addr,
    output logic inspect_ready,inspect_rsp_valid,output logic [31:0] inspect_bits,
    input logic input_valid, output logic input_ready, input logic [31:0] input_bits,
    input logic accept_enable,write_enable,
    output logic state_valid,input logic state_ready,
    output logic [15:0] state_id,output logic [31:0] state_bits,
    output logic step_done,output logic [4:0] phase,
    output logic edge_valid,edge_ready,output logic [15:0] edge_src,edge_dst,
    output logic [31:0] edge_weight,output logic [20:0] edge_id,
    output logic pipe_valid,pipe_ready,output logic [15:0] pipe_dst,
    output logic [20:0] pipe_id,output logic [31:0] pipe_old,pipe_product,
    output logic ar,aw,cr,cw,output logic [15:0] ar_addr,aw_addr,cr_addr,cw_addr,
    output logic [31:0] ar_data,aw_data,cr_data,cw_data,
    output logic rom_read,map_read,output logic [12:0] rom_address,output logic [10:0] map_address,
    output logic hazard_wait
);
    localparam integer D=2+LM+LA;
    localparam logic [4:0] INPUTS=0,CLEAR=1,START=2,SYN=3,DRAIN=4,
        UPQ=5,UPG=6,UREAD=7,UWAIT=8,OP=9,OWAIT=10,
        OUTQ=11,OUTG=12,OUTH=13,DONE=14,
        RPQ=15,RPG=16,RBQ=17,RBG=18,RFILL=19,RDONE=20;
    logic [31:0] stim_q;
    logic av,cv,mem_ce,add_valid,mul_valid,add_out_valid,mul_out_valid;
    logic [31:0] add_a,add_b,mul_a,mul_b,add_out,mul_out;
    logic [4:0] add_flags,mul_flags;
    logic [31:0] rom_q;
    logic gen_rom_en,gen_done,gen_start;
    logic [12:0] gen_rom_addr;
    logic [D-1:0] pv;
    logic [31:0] cap[0:D-1],wt[0:D-1],prod[0:D-1];
    logic [15:0] pdst[0:D-1];logic [20:0] pid[0:D-1];
    logic [15:0] request_src;
    logic pipe_ce,hazard;
    integer input_index,index,type_id,word_id,local_index,node_base,node_count,op_id,wait_count;
    logic [31:0] desc[0:6],old_a,bias,inv,op_result;
    // One arithmetic lane, several independent Euler contexts. A wave issues
    // one operation per clock in node order, then drains before the next wave.
    // No reassociation: -a+bias, +c, +x, *inv, *dt, +old_a remains six FP32 ops.
    localparam integer EW=(EU_CONTEXTS>1)?$clog2(EU_CONTEXTS):1, EV=(LA>LM)?LA:LM;
    logic [EW-1:0] load_slot,issue_slot;
    logic [EW:0] batch_count,received;
    integer batch_first;
    (* ram_style="distributed" *) logic [31:0] eu_old[0:EU_CONTEXTS-1];
    (* ram_style="distributed" *) logic [31:0] eu_current[0:EU_CONTEXTS-1];
    (* ram_style="distributed" *) logic [31:0] eu_input[0:EU_CONTEXTS-1];
    (* ram_style="distributed" *) logic [31:0] eu_result[0:EU_CONTEXTS-1];
    logic [EV-1:0] eu_valid;
    logic [EW-1:0] eu_tag[0:EV-1];
    logic eu_return;
    logic [EW-1:0] return_slot;
    logic node_input;
    sync_mem #(.DEPTH(7663),.AW(13),.INIT_FILE(META_FILE),.SIM_KEY("META")) metadata(
        .clk,.reset,.ce(1'b1),.re(rom_read),.ra(rom_address),.we(1'b0),.wa(13'b0),.wd(32'b0),.q(rom_q),.qvalid());
    sync_mem #(.DEPTH(N),.INIT_FILE(STATE_FILE),.SIM_KEY("INIT")) state_ram(
        .clk,.reset,.ce(mem_ce),.re(ar),.ra(ar_addr),.we(aw),.wa(aw_addr),.wd(aw_data),.q(ar_data),.qvalid(av));
    sync_mem #(.DEPTH(N)) current_ram(
        .clk,.reset,.ce(mem_ce),.re(cr),.ra(cr_addr),.we(cw),.wa(cw_addr),.wd(cw_data),.q(cr_data),.qvalid(cv));
    sync_mem #(.DEPTH(721),.AW(10)) stimulus_ram(
        .clk,.reset,.ce(1'b1),.re(phase==UREAD&&node_input),.ra(10'(local_index)),
        .we(input_valid&&input_ready),.wa(10'(input_index)),.wd(input_bits),.q(stim_q),.qvalid());
    fp32_pipe #(.LATENCY(LA)) adder(.clk,.reset,.ce(pipe_ce),.valid_in(add_valid),
        .a(add_a),.b(add_b),.valid_out(add_out_valid),.result(add_out),.flags(add_flags));
    fp32_pipe #(.LATENCY(LM),.MULTIPLY(1)) multiplier(.clk,.reset,.ce(pipe_ce),.valid_in(mul_valid),
        .a(mul_a),.b(mul_b),.valid_out(mul_out_valid),.result(mul_out),.flags(mul_flags));
    compact_edge_gen #(.NR(NR),.NE(NE),.MAP_FILE(MAP_FILE),.ROWS_FILE(ROWS_FILE)) gen(.clk,.reset,.start(gen_start),
        .rom_en(gen_rom_en),.rom_addr(gen_rom_addr),.rom_q,
        .valid(edge_valid),.ready(edge_ready),.src(edge_src),.dst(edge_dst),
        .weight(edge_weight),.eid(edge_id),.done(gen_done),.map_read,.map_address);

    always_comb begin
        pipe_valid=pv[D-1];pipe_ready=write_enable;pipe_dst=pdst[D-1];pipe_id=pid[D-1];
        pipe_old=cap[D-1];pipe_product=prod[D-1];
        pipe_ce=!pipe_valid||write_enable;
        mem_ce=(phase==SYN||phase==DRAIN)?pipe_ce:1'b1;
        mul_valid=pv[1];mul_a=(ar_data[31]||ar_data[30:0]==0)?32'b0:ar_data;mul_b=wt[1];
        add_valid=pv[1+LM];add_a=cap[1+LM];add_b=mul_out;
        if(phase==OP) begin
            mul_valid=(op_id==3||op_id==4);add_valid=!mul_valid;
            case(op_id)
                0:begin add_a=eu_old[issue_slot]^32'h80000000;add_b=bias;end
                1:begin add_a=eu_result[issue_slot];add_b=eu_current[issue_slot];end
                2:begin add_a=eu_result[issue_slot];add_b=eu_input[issue_slot];end
                3:begin mul_a=inv;mul_b=eu_result[issue_slot];end
                4:begin mul_a=eu_result[issue_slot];mul_b=32'h3ba3d70a;end
                5:begin add_a=eu_old[issue_slot];add_b=eu_result[issue_slot];end
                default:begin end
            endcase
        end
        op_result=(op_id==3||op_id==4)?mul_out:add_out;
        eu_return=(phase==OP||phase==OWAIT)&&eu_valid[(op_id==3||op_id==4)?LM-1:LA-1];
        return_slot=eu_tag[(op_id==3||op_id==4)?LM-1:LA-1];
        hazard=0;
        for(integer k=0;k<D;k=k+1) if(pv[k]&&pdst[k]==edge_dst) hazard=1;
        hazard_wait=(phase==SYN)&&edge_valid&&hazard;
        edge_ready=(phase==SYN)&&accept_enable&&pipe_ce&&!hazard;
        input_ready=(phase==INPUTS)&&!restore_req&&!inspect_valid;
        restore_busy=(phase>=RPQ&&phase<=RDONE);restore_done=(phase==RDONE);
        inspect_ready=(phase==INPUTS)&&!restore_req&&!input_valid;
        inspect_bits=ar_data;
        gen_start=(phase==START);
        rom_read=gen_rom_en;rom_address=gen_rom_addr;
        if(phase==UPQ) begin
            rom_read=1;
            if(word_id<4) rom_address=13'(32+4*type_id+word_id);
            else rom_address=13'(7468+3*type_id+word_id-4);
        end
        if(phase==RPQ) begin rom_read=1;rom_address=13'(32+4*type_id);end
        if(phase==RBQ) begin rom_read=1;rom_address=13'(7468+3*type_id);end
        ar=0;aw=0;cr=0;cw=0;
        ar_addr=0;aw_addr=0;cr_addr=0;cw_addr=0;aw_data=0;cw_data=0;
        // Register accepted source/target before driving the 45-bank RAMs.
        // Pending-target protection includes this request slot. Global CE holds
        // both the slot and memories, so a stopped pipeline cannot reread it.
        if((phase==SYN||phase==DRAIN)&&pv[0]&&pipe_ce) begin
            ar=1;cr=1;ar_addr=request_src;cr_addr=pdst[0];
        end
        if(pipe_valid&&write_enable) begin cw=1;cw_addr=pipe_dst;cw_data=add_out;end
        if(phase==CLEAR) begin cw=1;cw_addr=16'(index);cw_data=0;end
        if(phase==UREAD) begin ar=1;cr=1;ar_addr=16'(node_base+local_index);cr_addr=ar_addr;end
        if(eu_return&&op_id==5) begin aw=1;aw_addr=16'(node_base+batch_first+int'(return_slot));aw_data=op_result;end
        if(phase==OUTQ) begin ar=1;ar_addr=16'(index);end
        if(inspect_valid&&inspect_ready) begin ar=1;ar_addr=inspect_addr;end
        if(phase==RFILL) begin aw=1;aw_addr=16'(node_base+local_index);aw_data=bias;end
        state_valid=(phase==OUTH);state_id=16'(index);state_bits=old_a;
        step_done=(phase==DONE);
    end

    always_ff @(posedge clk) begin
        // synthesis translate_off
        if(!reset) begin
            if(ar&&aw&&ar_addr==aw_addr) $fatal(1,"A same-address collision");
            if(cr&&cw&&cr_addr==cw_addr) $fatal(1,"C same-address collision");
            if(ar&&int'(ar_addr)>=N || cr&&int'(cr_addr)>=N || aw&&int'(aw_addr)>=N || cw&&int'(cw_addr)>=N) $fatal(1,"RAM bounds");
            if(aw&&(phase==SYN||phase==DRAIN)) $fatal(1,"early update");
            if(pipe_valid&&!add_out_valid) $fatal(1,"adder/tag mismatch");
            if(pv[1+LM]&&!mul_out_valid) $fatal(1,"multiplier/tag mismatch");
            if(pv[1]&&(!av||!cv)) $fatal(1,"missing synchronous response");
            if(eu_return&&!(op_id==3||op_id==4?mul_out_valid:add_out_valid)) $fatal(1,"missing Euler result");
            if(eu_return&&(int'(return_slot)!=int'(received)||int'(return_slot)>=int'(batch_count))) $fatal(1,"Euler return order");
            if(phase==OP&&(int'(issue_slot)>=int'(batch_count)||pv!=0)) $fatal(1,"Euler issue bounds/barrier");
            if(phase==UPQ&&pv!=0) $fatal(1,"undrained pipeline");
        end
        // synthesis translate_on
        if(reset) begin pv<='0;eu_valid<='0;phase<=INPUTS;input_index<=0;index<=0;inspect_rsp_valid<=0;end
        else begin
            inspect_rsp_valid<=inspect_valid&&inspect_ready;
            if(pipe_ce) begin
                for(integer k=EV-1;k>0;k=k-1) begin eu_valid[k]<=eu_valid[k-1];eu_tag[k]<=eu_tag[k-1];end
                eu_valid[0]<=(phase==OP);
                eu_tag[0]<=issue_slot;
                for(integer k=D-1;k>0;k=k-1) begin
                    pv[k]<=pv[k-1];cap[k]<=cap[k-1];wt[k]<=wt[k-1];
                    pdst[k]<=pdst[k-1];pid[k]<=pid[k-1];prod[k]<=prod[k-1];
                    if(k==2) cap[k]<=cr_data;
                    if(k==2+LM && pv[k-1]) prod[k]<=mul_out;
                end
                pv[0]<=edge_valid&&edge_ready;
                if(edge_valid&&edge_ready) begin
                    request_src<=edge_src;wt[0]<=edge_weight;pdst[0]<=edge_dst;pid[0]<=edge_id;prod[0]<=0;
                end
            end
            case(phase)
                INPUTS:if(restore_req) begin type_id<=0;phase<=RPQ;end
                else if(input_valid&&input_ready) begin
                    if(input_index==720) begin index<=0;phase<=CLEAR;end
                    else input_index<=input_index+1;
                end
                CLEAR:if(index==N-1) phase<=START;else index<=index+1;
                START:phase<=SYN;
                SYN:if(gen_done) phase<=DRAIN;
                DRAIN:if(pv==0) begin type_id<=0;word_id<=0;phase<=UPQ;end
                UPQ:phase<=UPG;
                UPG:begin
                    desc[word_id]<=rom_q;
                    if(word_id==6) begin
                        node_base<=int'(desc[0][15:0]);node_count<=int'(desc[0][31:16]);
                        node_input<=desc[1][24];bias<=desc[4];inv<=rom_q;
                        local_index<=0;load_slot<=0;phase<=UREAD;
                    end else begin word_id<=word_id+1;phase<=UPQ;end
                end
                UREAD:phase<=UWAIT;
                UWAIT:begin
                    eu_old[load_slot]<=ar_data;eu_current[load_slot]<=cr_data;
                    eu_input[load_slot]<=node_input?stim_q:32'b0;
                    if(int'(load_slot)+1<EU_CONTEXTS&&local_index+1<node_count) begin
                        load_slot<=load_slot+1;local_index<=local_index+1;phase<=UREAD;
                    end else begin
                        batch_count<={1'b0,load_slot}+1;batch_first<=local_index-int'(load_slot);
                        issue_slot<=0;received<=0;op_id<=0;phase<=OP;
                    end
                end
                OP:begin
                    if({1'b0,issue_slot}+1<batch_count) issue_slot<=issue_slot+1;
                    else phase<=OWAIT;
                end
                OWAIT:begin end
                OUTQ:phase<=OUTG;
                OUTG:begin old_a<=ar_data;phase<=OUTH;end
                OUTH:if(state_ready) begin
                    if(index==N-1) phase<=DONE;
                    else begin index<=index+1;phase<=OUTQ;end
                end
                DONE:begin phase<=INPUTS;input_index<=0;end
                RPQ:phase<=RPG;
                RPG:begin node_base<=int'(rom_q[15:0]);node_count<=int'(rom_q[31:16]);phase<=RBQ;end
                RBQ:phase<=RBG;
                RBG:begin bias<=rom_q;local_index<=0;phase<=RFILL;end
                RFILL:if(local_index+1<node_count) local_index<=local_index+1;
                else if(type_id+1<NT) begin type_id<=type_id+1;phase<=RPQ;end
                else phase<=RDONE;
                RDONE:begin phase<=INPUTS;input_index<=0;end
                default:begin
                    // synthesis translate_off
                    $fatal(1,"controller phase");
                    // synthesis translate_on
                end
            endcase
            if(eu_return) begin
                eu_result[return_slot]<=op_result;received<=received+1;
                if(received+1==batch_count) begin
                    // The shorter multiplier wave may leave older tags above
                    // LM. They must not be reinterpreted as adder returns.
                    eu_valid<='0;
                    if(op_id<5) begin op_id<=op_id+1;issue_slot<=0;received<=0;phase<=OP;end
                    else if(local_index+1<node_count) begin local_index<=local_index+1;load_slot<=0;phase<=UREAD;end
                    else if(type_id+1<NT) begin type_id<=type_id+1;word_id<=0;phase<=UPQ;end
                    else begin index<=0;phase<=OUTQ;end
                end
            end
        end
    end
endmodule

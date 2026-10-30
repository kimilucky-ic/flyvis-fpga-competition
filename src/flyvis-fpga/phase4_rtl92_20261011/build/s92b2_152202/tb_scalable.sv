`timescale 1ns/1ps
`include "fixture_config.svh"
`ifndef TEST_BANKS
`define TEST_BANKS 1
`endif
module tb_scalable;
    localparam H=`TEST_H, B=`TEST_B, E=`TEST_E, STEPS=`TEST_STEPS;
    localparam BANKS=`TEST_BANKS, HW=$clog2(H), AW=$clog2(B+2*H), WORDS=B+2*H;
    reg clk=0; always #5 clk=~clk;
    reg rst_n=0, req_begin=0,in_we=0,start=0;
    reg [AW-1:0] in_addr=0; reg signed [31:0] in_data=0;
    wire busy,done,out_valid; wire [31:0] status,cycles;
    reg [HW-1:0] out_addr=0; wire signed [31:0] out_data;
    wire trace_valid; wire [20:0] trace_gid; wire [HW-1:0] trace_target;
    wire signed [30:0] trace_term; wire signed [49:0] trace_sum;
    scalable_source_raw_core #(.H_COUNT(H),.B_COUNT(B),.EDGE_COUNT(E),.BANKS(BANKS)) dut(
        .clk(clk),.rst_n(rst_n),.req_begin(req_begin),.in_we(in_we),.start(start),
        .in_addr(in_addr),.in_data(in_data),.busy(busy),.done(done),.out_valid(out_valid),
        .status(status),.compute_cycles(cycles),.out_addr(out_addr),.out_data(out_data),
        .trace_valid(trace_valid),.trace_gid(trace_gid),.trace_target(trace_target),
        .trace_term(trace_term),.trace_sum(trace_sum));
    reg [31:0] requests[0:STEPS*WORDS-1];
    reg [30:0] expected[0:STEPS*H-1];
    reg [80:0] edge_traces[0:STEPS*E-1];
    reg [20+HW:0] edge_ids[0:E-1];
    reg recurrent[0:STEPS-1]; reg signed [31:0] last_output[0:H-1];
    integer s=0,edge_seen=0,j,watchdog,f,summary,clock_count=0;
    integer chem_reads=0,request_reads=0,min_write_read_gap=100000,last_write=-100000;
    integer aborted=0;
    integer min_edge_write_read_gap=100000;
    reg request_check=0,chemical_check=0;
    reg signed [30:0] expected_qa,expected_qb;
    reg signed [49:0] expected_cq;
    reg [HW-1:0] previous_target;
    integer target_repeats=0;

    // Independently monitor synchronous BRAM latency using pre-clock array
    // contents, then compare registered values after the active clock.
    always @(posedge clk) begin
        clock_count=clock_count+1;
        request_check=dut.request_read;
        if(request_check) begin
            expected_qa=dut.request_mem[dut.req_addr_a];
            expected_qb=dut.request_mem[dut.req_addr_b];
            request_reads=request_reads+1;
        end
        chemical_check=dut.chem_read;
        if(dut.chem_read && dut.chem_write) $fatal(1,"chemical read/write collision");
        if(dut.chem_write) last_write=clock_count;
        if(chemical_check) begin
            if(clock_count-last_write<min_write_read_gap) min_write_read_gap=clock_count-last_write;
            if(dut.state==dut.E_READ && clock_count-last_write<min_edge_write_read_gap)
                min_edge_write_read_gap=clock_count-last_write;
            case(dut.chem_bank)
                0: expected_cq=dut.chemical_banks[0].mem[dut.chem_row];
                // Other bank memory checks are covered by the ordered sums;
                // direct hierarchy is generated below for each bank.
                default: expected_cq=0;
            endcase
            chem_reads=chem_reads+1;
        end
    end
    genvar bk;
    generate for(bk=0;bk<BANKS;bk=bk+1) begin: monitor_bank
        reg checked; reg signed [49:0] before_value;
        always @(posedge clk) begin
            checked=dut.chem_read && dut.chem_bank==bk;
            if(checked) before_value=dut.chemical_banks[bk].mem[dut.chem_row];
        end
        always @(negedge clk) if(rst_n && checked)
            if(dut.chem_q[bk]!==before_value) $fatal(1,"synchronous chemical read bank %0d",bk);
    end endgenerate
    always @(negedge clk) begin
        if(rst_n && request_check)
            if(dut.req_q_a!==expected_qa || dut.req_q_b!==expected_qb) $fatal(1,"synchronous request read");
        if(rst_n && trace_valid && !aborted) begin
            if(edge_seen>=E) $fatal(1,"extra edge");
            if(trace_gid!==edge_ids[edge_seen][20+HW:HW] || trace_target!==edge_ids[edge_seen][HW-1:0])
                $fatal(1,"ID/order mismatch step %0d edge %0d",s,edge_seen);
            if({trace_term,trace_sum}!==edge_traces[s*E+edge_seen])
                $fatal(1,"edge arithmetic mismatch step %0d edge %0d got %h expected %h",s,edge_seen,{trace_term,trace_sum},edge_traces[s*E+edge_seen]);
            if(edge_seen>0 && trace_target==previous_target) target_repeats=target_repeats+1;
            previous_target=trace_target; edge_seen=edge_seen+1;
        end
    end
    task begin_load;
        begin
            @(negedge clk); req_begin=1;
            @(negedge clk); req_begin=0;
        end
    endtask
    task await_done;
        begin
            watchdog=0;
            while(!done && watchdog<6*E+8*H+100) begin @(negedge clk); watchdog=watchdog+1; end
            if(!done) $fatal(1,"timeout");
        end
    endtask
    initial begin
        $readmemh("rom/requests.mem",requests); $readmemh("rom/expected.mem",expected);
        $readmemh("rom/edge_traces.mem",edge_traces); $readmemh("rom/edge_identity.mem",edge_ids);
        $readmemh("rom/recurrent.mem",recurrent);
        if(dut.rounded(64'sd524288,20)!==64'sd1 || dut.rounded(-64'sd524288,20)!==-64'sd1
            || dut.rounded(64'sh8000000000000000,24)!==-64'sd549755813888)
            $fatal(1,"rounding corner failure");
        f=$fopen("outputs.csv","w"); summary=$fopen("simulation_summary.csv","w");
        $fdisplay(f,"step,neuron,raw_q24"); $fdisplay(summary,"step,status,cycles,edges");
        repeat(4) @(negedge clk); rst_n=1;
        for(s=0;s<STEPS;s=s+1) begin
            edge_seen=0; begin_load;
            for(j=0;j<WORDS;j=j+1) begin
                in_we=1; in_addr=j; in_data=requests[s*WORDS+j];
                if(recurrent[s] && j>=B && j<B+H) begin
                    in_data=last_output[j-B];
                    if(in_data!==requests[s*WORDS+j]) $fatal(1,"RTL recurrent feedback mismatch");
                end
                @(negedge clk);
            end
            in_we=0; start=1; @(negedge clk); start=0; await_done;
            if(status!==0 || !out_valid || edge_seen!=E) $fatal(1,"bad success status step %0d status=%h edges=%0d",s,status,edge_seen);
            if(cycles!==6*E+7*H+1) $fatal(1,"cycle count mismatch %0d",cycles);
            for(j=0;j<H;j=j+1) begin
                out_addr=j; @(negedge clk);
                if(out_data!==$signed({expected[s*H+j][30],expected[s*H+j]}))
                    $fatal(1,"state mismatch step %0d neuron %0d got %0d expected %0d",s,j,out_data,$signed(expected[s*H+j]));
                $fdisplay(f,"%0d,%0d,%0d",s,j,out_data);
                last_output[j]=out_data;
            end
            if((1<<HW)>H) begin
                out_addr=H; @(negedge clk);
                if(out_data!==0) $fatal(1,"out-of-range candidate read not zeroed");
            end
            $fdisplay(summary,"%0d,%0d,%0d,%0d",s,status,cycles,edge_seen);
            $display("STEP_PASS s=%0d cycles=%0d edges=%0d banks=%0d",s,cycles,edge_seen,BANKS);
        end
        // Protocol and numeric fail-closed cases, with no accepted output.
        aborted=1; begin_load;
        in_we=1; in_addr=0; in_data=32'h40000000; @(negedge clk);
        in_we=0; start=1; @(negedge clk); start=0; await_done;
        if(status==0 || out_valid || out_data!==0) $fatal(1,"malformed sign extension accepted");
        $display("ERROR_PASS malformed_sign status=%h",status);
        begin_load; in_we=1; in_addr=1; in_data=0; @(negedge clk);
        in_we=0; start=1; @(negedge clk); start=0; await_done;
        if(status==0 || out_valid || out_data!==0) $fatal(1,"missing/out-of-order input accepted");
        $display("ERROR_PASS missing_input status=%h",status);
        begin_load;
        for(j=0;j<WORDS;j=j+1) begin
            in_we=1; in_addr=j; in_data=32'h3fffffff; @(negedge clk);
        end
        in_we=0; start=1; @(negedge clk); start=0; await_done;
        if(!status[2] || out_valid || out_data!==0) $fatal(1,"numeric overflow accepted status=%h",status);
        $display("ERROR_PASS numeric_overflow status=%h",status);
        $display("ALL_PASS requests=%0d nodes=%0d edges=%0d banks=%0d chemical_reads=%0d request_reads=%0d same_target_pairs=%0d min_write_read_gap=%0d min_edge_write_read_gap=%0d",STEPS,H,E,BANKS,chem_reads,request_reads,target_repeats,min_write_read_gap,min_edge_write_read_gap);
        $fclose(f); $fclose(summary); $finish;
    end
endmodule

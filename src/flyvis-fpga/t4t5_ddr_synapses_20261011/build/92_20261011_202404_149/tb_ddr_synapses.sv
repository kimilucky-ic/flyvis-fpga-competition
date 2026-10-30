`timescale 1ns/1ps
`include "fixture_config.svh"
module tb_ddr_synapses;
    localparam H=`TEST_H,S=`TEST_S,E=`TEST_E,W=`TEST_W,STEPS=`TEST_STEPS,MINI=`TEST_MINI;
    localparam WORDS=S+H,FIFO_DEPTH=4,STEP_LIMIT=MINI?512:500000;
    localparam BASE=32'h00000ff0;
    reg clk=0;always #5 clk=~clk;
    reg rst_n=0,req_begin=0,in_we=0,start=0;
    reg [15:0] in_addr=0;reg signed [31:0] in_data=0;
    reg [31:0] step_id=0,old_tag=32'h1234a567,base_addr=BASE;
    reg [63:0] expected_signature=`TEST_SIGNATURE;
    reg [12:0] out_addr=0;
    wire busy,done,out_valid,trace_valid,reader_busy,poisoned;
    wire [31:0] status,cycles,result_step_id,result_tag,applied,reader_error,received,stalls,occupancy;
    wire [63:0] signature;wire signed [31:0] out_data;
    wire [20:0] trace_gid;wire [12:0] trace_target;
    wire signed [30:0] trace_term;wire signed [49:0] trace_sum;
    wire [31:0] araddr;wire [3:0] arlen;wire [2:0] arsize;wire [1:0] arburst;wire [5:0] arid;
    wire arvalid,rready;reg arready=0;
    reg [63:0] rdata=0;reg [1:0] rresp=0;reg [5:0] rid=0;reg rlast=0,rvalid=0;
    ddr_synapse_top #(.H_COUNT(H),.SOURCE_COUNT(S),.EDGE_COUNT(E),.WEIGHT_COUNT(W),
        .FIFO_DEPTH(FIFO_DEPTH),.AXI_TIMEOUT(64),.STEP_TIMEOUT(STEP_LIMIT)) dut(
        .clk(clk),.rst_n(rst_n),.req_begin(req_begin),.in_we(in_we),.start(start),.in_addr(in_addr),.in_data(in_data),
        .step_id(step_id),.old_state_tag(old_tag),.base_addr(base_addr),.expected_signature(expected_signature),
        .busy(busy),.done(done),.out_valid(out_valid),.status(status),.cycles(cycles),
        .result_step_id(result_step_id),.result_old_state_tag(result_tag),.edges_applied(applied),.signature(signature),
        .out_addr(out_addr),.out_data(out_data),.trace_valid(trace_valid),.trace_gid(trace_gid),.trace_target(trace_target),
        .trace_term(trace_term),.trace_sum(trace_sum),.araddr(araddr),.arlen(arlen),.arsize(arsize),.arburst(arburst),
        .arid(arid),.arvalid(arvalid),.arready(arready),.rdata(rdata),.rresp(rresp),.rid(rid),.rlast(rlast),.rvalid(rvalid),.rready(rready),
        .reader_busy(reader_busy),.reader_poisoned(poisoned),.reader_error(reader_error),.received(received),.stall_cycles(stalls),.fifo_occupancy(occupancy));
    reg [63:0] edges[0:E-1];reg [31:0] requests[0:STEPS*WORDS-1];
    reg [30:0] expected[0:STEPS*H-1];reg [80:0] traces[0:STEPS*E-1];
    reg [23:0] weights[0:W-1];reg [61:0] neurons[0:H-1];
    integer current=0,fault=0,mode=0,clock_count=0,edge_seen=0,stream_seen=0;
    integer burst_seen=0,max_fifo=0,ar_stalls=0,r_bubbles=0,watchdog,j,k,summary,raw,state_raw;
    integer total_edges=0,total_states=0,faults_passed=0,same_target=0,read_checks=0,saved_fault=0;
    integer active=0,bstart=0,blen=0,bbeat=0,delay_left=0,expected_addr=BASE;
    integer last_chem_write=-1000,min_rmw_gap=1000;
    reg [31:0] prng=32'h31415926;
    reg arheld=0,rheld=0,fheld=0;
    reg [31:0] heldaddr;reg [3:0] heldlen;
    reg [63:0] helddata,heldfifo;reg [1:0] heldresp;reg [5:0] heldrid;reg heldlast;
    reg source_check=0,chem_check=0,weight_check=0;
    reg signed [30:0] before_source;reg signed [49:0] before_chem;reg signed [23:0] before_weight;
    reg [12:0] prev_target=0;

    function automatic [63:0] injected(input integer index);
        reg [63:0] x;
        begin
            x=edges[index];
            if(index==1) case(fault)
                1:x[35:21]=S;
                2:x[48:36]=H;
                3:x[58:49]=W;
                4:x[63]=1;
                5:x[20:0]=edges[0][20:0];
                6:x[20:0]=edges[0][20:0]-1;
                default:begin end
            endcase
            if(fault==7&&index>=1) x[20:0]=x[20:0]+1;
            injected=x;
        end
    endfunction
    // Protocol-conforming mock DDR except the explicitly selected fault.
    // Drive data once and hold it across every RREADY stall.
    always @(posedge clk) begin
        if(!rst_n) begin
            active<=0;rvalid<=0;arready<=0;rdata<=0;rresp<=0;rid<=0;rlast<=0;
            bstart<=0;blen<=0;bbeat<=0;delay_left<=0;prng<=32'h31415926;
        end else begin
            prng<={prng[30:0],prng[31]^prng[21]^prng[1]^prng[0]};
            arready<=(fault!=13)&&((mode==0)||prng[2:0]!=0);
            if(arvalid&&arready) begin
                if(active) $fatal(1,"multiple outstanding bursts");
                if(arid!=0||arsize!=3||arburst!=1||araddr[2:0]!=0) $fatal(1,"AXI read attributes");
                if({1'b0,araddr[11:0]}+8*(arlen+1)>4096) $fatal(1,"4KiB crossing");
                if(araddr!=expected_addr) $fatal(1,"DDR address gap or repeat");
                expected_addr=expected_addr+8*(arlen+1);
                if(burst_seen==0&&arlen!=1) $fatal(1,"first page-split burst must have two beats");
                burst_seen=burst_seen+1;
                active<=1;bstart<=(araddr-BASE)/8;blen<=arlen+1;bbeat<=0;delay_left<=(fault==25)?50:0;
            end
            if(rvalid&&rready) begin
                rvalid<=0;bbeat<=bbeat+1;
                if(bbeat==blen-1) active<=0;
                if(fault==25) delay_left<=50;
            end
            if(active&&!rvalid&&fault!=14) begin
                if(delay_left!=0) delay_left<=delay_left-1;
                else if(mode==0||prng[3:0]<((mode==1)?12:4)) begin
                    rvalid<=1;rdata<=injected(bstart+bbeat);
                    rresp<=(fault==9&&bstart+bbeat==1)?2'b10:0;
                    rid<=(fault==10&&bstart+bbeat==1)?6'd1:0;
                    rlast<=(fault==11&&bbeat==0)?1:((fault==12&&bbeat==blen-1)?0:(bbeat==blen-1));
                end else r_bubbles=r_bubbles+1;
            end
        end
    end
    // Check valid/data stability, FIFO bounds, and synchronous RAM values.
    always @(posedge clk) begin
        clock_count=clock_count+1;
        if(!rst_n) begin arheld=0;rheld=0;fheld=0;source_check=0;chem_check=0;weight_check=0;end
        else begin
            if(arheld&&(!arvalid||araddr!==heldaddr||arlen!==heldlen)) $fatal(1,"AR unstable while stalled");
            if(rheld&&(!rvalid||rdata!==helddata||rresp!==heldresp||rid!==heldrid||rlast!==heldlast)) $fatal(1,"mock DDR data unstable");
            if(fheld&&fault==0&&(!dut.fifo_out_valid||dut.fifo_out!==heldfifo)) $fatal(1,"FIFO output unstable");
            arheld=arvalid&&!arready;heldaddr=araddr;heldlen=arlen;
            rheld=rvalid&&!rready;helddata=rdata;heldresp=rresp;heldrid=rid;heldlast=rlast;
            fheld=dut.fifo_out_valid&&!dut.fifo_out_ready;heldfifo=dut.fifo_out;
            if(occupancy>FIFO_DEPTH+1) $fatal(1,"FIFO overflow");
            if(occupancy>max_fifo) max_fifo=occupancy;
            if(arvalid&&!arready) ar_stalls=ar_stalls+1;
            if(dut.fifo_out_valid&&dut.fifo_out_ready&&fault==0) begin
                if(stream_seen>=E||dut.fifo_out!==edges[stream_seen]) $fatal(1,"FIFO loss/repeat/reorder");
                stream_seen=stream_seen+1;
            end
            source_check=(dut.core.state==dut.core.READ||dut.core.state==dut.core.N_READ);
            weight_check=dut.core.state==dut.core.READ;
            if(source_check) begin
                before_source=dut.core.source_mem[(dut.core.state==dut.core.READ)?dut.core.src:dut.core.h_index];
                before_chem=dut.core.chemical_mem[(dut.core.state==dut.core.READ)?dut.core.target:dut.core.h_index];
                read_checks=read_checks+1;
            end
            if(weight_check) before_weight=dut.core.weight_rom[dut.core.weight_index];
            chem_check=source_check;
            if(source_check&&(dut.core.edge_write||dut.core.state==dut.core.CLEAR)) $fatal(1,"chemical read/write collision");
            if(dut.core.edge_write) last_chem_write=clock_count;
            if(weight_check&&clock_count-last_chem_write<min_rmw_gap) min_rmw_gap=clock_count-last_chem_write;
        end
    end
    always @(negedge clk) begin
        if(rst_n&&source_check&&dut.core.source_q!==before_source) $fatal(1,"source RAM latency");
        if(rst_n&&chem_check&&dut.core.chemical_q!==before_chem) $fatal(1,"chemical RAM latency");
        if(rst_n&&weight_check&&dut.core.weight_q!==before_weight) $fatal(1,"weight ROM latency");
        if(rst_n&&trace_valid&&fault==0) begin
            if(edge_seen>=E||trace_gid!==edges[edge_seen][20:0]||trace_target!==edges[edge_seen][48:36]) $fatal(1,"edge ID/target mismatch");
            if({trace_term,trace_sum}!==traces[current*E+edge_seen]) $fatal(1,"edge arithmetic mismatch request %0d edge %0d",current,edge_seen);
            if(edge_seen!=0&&prev_target==trace_target) same_target=same_target+1;
            prev_target=trace_target;
            $fwrite(raw,"%0d,%0d,%0d,%0d,%0d,%0d,%0d\n",current,edge_seen,trace_gid,trace_target,trace_term,trace_sum,cycles);
            edge_seen=edge_seen+1;total_edges=total_edges+1;
        end
    end
    task reset_dut;
        begin
            @(negedge clk);rst_n=0;req_begin=0;start=0;in_we=0;
            repeat(4) @(negedge clk);
            rst_n=1;repeat(2) @(negedge clk);
            for(k=0;k<W;k=k+1) dut.core.weight_rom[k]=weights[k];
            for(k=0;k<H;k=k+1) dut.core.neuron_rom[k]=neurons[k];
        end
    endtask
    task load_request(input integer idx);
        begin
            current=idx;edge_seen=0;stream_seen=0;burst_seen=0;max_fifo=0;ar_stalls=0;r_bubbles=0;expected_addr=BASE;
            base_addr=(fault==15)?BASE+1:BASE;
            expected_signature=(fault==8)?(`TEST_SIGNATURE^64'h1):`TEST_SIGNATURE;
            step_id=32'h1000+idx;old_tag=32'h1234a567+idx;
            @(negedge clk);req_begin=1;
            @(negedge clk);req_begin=0;
            for(j=0;j<WORDS-((fault==22)?1:0);j=j+1) begin
                in_we=1;in_addr=(fault==23&&j==0)?1:j;in_data=$signed(requests[idx*WORDS+j]);
                if(fault==21&&j==0) in_data=32'h40000000;
                if((fault==16||fault==20)&&j==0) in_data=32'h3fffffff;
                if(fault==19&&j==0) in_data=0;
                if((fault==19||fault==20)&&j==S) in_data=32'h3fffffff;
                @(negedge clk);
            end
            in_we=0;
            if(fault==16) dut.core.weight_rom[0]=24'h200000;
            if(fault==19) dut.core.neuron_rom[0][61:31]=31'h3fffffff;
            if(fault==20) dut.core.neuron_rom[0][30:0]=31'h3fffffff;
            start=1;@(negedge clk);start=0;
        end
    endtask
    task await_result;
        begin
            watchdog=0;
            while(!done&&watchdog<STEP_LIMIT+1000) begin
                @(negedge clk);watchdog=watchdog+1;
                if(fault==17&&dut.core.state==dut.core.READ&&applied==0)
                    dut.core.chemical_mem[0]=50'h1ffffffffffff;
                if(fault==18&&dut.core.state==dut.core.N_READ&&dut.core.h_index==0)
                    dut.core.chemical_mem[0]=50'h40000000;
                if(fault==24&&watchdog==10) req_begin=1;
                else if(fault==24) req_begin=0;
            end
            if(!done) $fatal(1,"testbench watchdog fault %0d",fault);
        end
    endtask
    task verify_success;
        begin
            if(status!=0||!out_valid||reader_busy||poisoned||reader_error!=0) $fatal(1,"valid step rejected %h",status);
            if(applied!=E||received!=E||edge_seen!=E||stream_seen!=E||signature!==`TEST_SIGNATURE) $fatal(1,"edge count/signature mismatch");
            if(result_step_id!=step_id||result_tag!=old_tag) $fatal(1,"request identity changed");
            for(j=0;j<H;j=j+1) begin
                out_addr=j;@(negedge clk);
                if(out_data!==$signed({expected[current*H+j][30],expected[current*H+j]})) $fatal(1,"state mismatch request %0d index %0d",current,j);
                $fwrite(state_raw,"%0d,%0d,%0d\n",current,j,out_data);total_states=total_states+1;
            end
            for(j=0;j<S;j=j+1)
                if(dut.core.source_mem[j]!==requests[current*WORDS+j][30:0]) $fatal(1,"old source state was changed");
            out_addr=H;@(negedge clk);if(out_data!==0) $fatal(1,"out-of-range candidate visible");
            $fwrite(summary,"PASS,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d\n",current,cycles,applied,received,stalls,max_fifo,burst_seen,ar_stalls,r_bubbles);
            $display("REQUEST_PASS index=%0d cycles=%0d edges=%0d fifo_stalls=%0d max_fifo=%0d",current,cycles,applied,stalls,max_fifo);
        end
    endtask
    task verify_failure(input integer want);
        begin
            if(out_valid||status!=want) $fatal(1,"fault %0d expected %h got %h valid %b",fault,want,status,out_valid);
            for(j=0;j<H;j=j+1) begin out_addr=j;@(negedge clk);if(out_data!==0) $fatal(1,"failed candidate visible");end
            if((fault==13||fault==14)&&(!reader_busy||!poisoned)) $fatal(1,"stuck transport must stay poisoned and busy");
            if(fault!=13&&fault!=14) begin
                watchdog=0;while(reader_busy&&watchdog<1200) begin @(negedge clk);watchdog=watchdog+1;end
                if(reader_busy) $fatal(1,"finite fault failed to drain");
            end
            $fwrite(summary,"FAULT_PASS,%0d,%0d,%0d,%0d,%0d,%0d\n",fault,status,cycles,applied,reader_error,reader_busy);
            $display("FAULT_PASS code=%0d status=%h reader_error=%h busy=%b",fault,status,reader_error,reader_busy);
            faults_passed=faults_passed+1;
        end
    endtask
    initial begin
        $readmemh("rom/edges.mem",edges);$readmemh("rom/requests.mem",requests);$readmemh("rom/expected.mem",expected);
        $readmemh("rom/edge_traces.mem",traces);$readmemh("rom/weights.mem",weights);$readmemh("rom/neurons.mem",neurons);
        summary=$fopen("summary.csv","w");raw=$fopen("edge_trace.csv","w");state_raw=$fopen("states.csv","w");
        $fwrite(raw,"request,edge_index,global_edge_id,target,term,partial_sum,cycle\n");
        $fwrite(state_raw,"request,index,candidate_q24\n");
        reset_dut();
        for(current=0;current<STEPS;current=current+1) begin
            mode=current%3;fault=0;load_request(current);await_result();verify_success();
        end
        if(same_target==0||read_checks==0||min_rmw_gap<2) $fatal(1,"missing RAM hazard coverage");
        // Capture the real-input run coverage before resets/negative tests.
        $fwrite(summary,"COVERAGE,%0d,%0d,%0d,%0d,%0d\n",total_edges,total_states,same_target,read_checks,min_rmw_gap);
        if(MINI) begin
            for(fault=1;fault<=25;fault=fault+1) begin
                mode=0;reset_dut();load_request(0);await_result();
                if(fault<=6) verify_failure(32'h10);
                else if(fault<=8) verify_failure(32'h20);
                else if(fault<=15) verify_failure(32'h40);
                else if(fault==17) verify_failure(32'h2);
                else if(fault==21) verify_failure(32'h9);
                else if(fault>=22&&fault<=24) verify_failure(32'h8);
                else if(fault==25) verify_failure(32'h80);
                else verify_failure(32'h4);
                if(fault==13||fault==14) begin
                    // Release the mock DDR after timeout: the still asserted
                    // ARVALID or outstanding R burst must drain, without reset.
                    saved_fault=fault;fault=0;watchdog=0;
                    while(reader_busy&&watchdog<300) begin @(negedge clk);watchdog=watchdog+1;end
                    if(reader_busy||out_valid) $fatal(1,"timeout recovery/drain failed");
                    $fwrite(summary,"DRAIN_PASS,%0d\n",watchdog);
                    fault=saved_fault;
                end
            end
            // Prove normal recovery after the drained step-timeout, no reset.
            fault=0;mode=2;load_request(0);await_result();verify_success();
        end
        $display("ALL_PASS H=%0d source=%0d edges=%0d requests=%0d total_edges=%0d states=%0d fault_checks=%0d",H,S,E,STEPS,total_edges,total_states,faults_passed);
        $fclose(summary);$fclose(raw);$fclose(state_raw);$finish;
    end
endmodule

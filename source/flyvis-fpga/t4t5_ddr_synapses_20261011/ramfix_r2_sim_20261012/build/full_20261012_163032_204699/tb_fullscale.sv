`timescale 1ns/1ps
`include "full_config.svh"
// Exactly one complete original-graph request. No synthetic graph mutations,
// repeated small-graph acceptance or second full request in this testbench.
module tb_fullscale;
    localparam H=5768,S=16402,E=433880,W=645,WORDS=S+H,FIFO_DEPTH=4;
    localparam STEP_LIMIT=`FULL_STEP_LIMIT,BASE=32'h00000ff0;
    reg clk=0;always #5 clk=~clk;
    reg rst_n=0,req_begin=0,in_we=0,start=0;
    reg [15:0] in_addr=0;reg signed [31:0] in_data=0;
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
        .step_id(32'd0),.old_state_tag(`OLD_STATE_TAG),.base_addr(BASE),.expected_signature(`FULL_SIGNATURE),
        .busy(busy),.done(done),.out_valid(out_valid),.status(status),.cycles(cycles),
        .result_step_id(result_step_id),.result_old_state_tag(result_tag),.edges_applied(applied),.signature(signature),
        .out_addr(out_addr),.out_data(out_data),.trace_valid(trace_valid),.trace_gid(trace_gid),.trace_target(trace_target),
        .trace_term(trace_term),.trace_sum(trace_sum),.araddr(araddr),.arlen(arlen),.arsize(arsize),.arburst(arburst),
        .arid(arid),.arvalid(arvalid),.arready(arready),.rdata(rdata),.rresp(rresp),.rid(rid),.rlast(rlast),.rvalid(rvalid),.rready(rready),
        .reader_busy(reader_busy),.reader_poisoned(poisoned),.reader_error(reader_error),.received(received),.stall_cycles(stalls),.fifo_occupancy(occupancy));
    reg [63:0] edges[0:E-1];reg [31:0] requests[0:WORDS-1];
    reg [30:0] expected[0:H-1];reg [80:0] expected_trace[0:E-1];
    integer source_reads[0:S-1],target_edges[0:H-1],dictionary_edges[0:W-1];
    integer clock_count=0,edge_seen=0,stream_seen=0,burst_seen=0,bus_beats=0;
    integer max_fifo=0,ar_stalls=0,r_bubbles=0,watchdog=0,j;
    integer raw,state_raw,summary,burst_log,coverage_log;
    integer active=0,bstart=0,blen=0,bbeat=0,delay_left=0,expected_addr=BASE;
    integer page_ends=0,same_target=0,high_source_reads=0,zero_weight_edges=0;
    integer negative_source_edges=0,zero_terms=0,negative_terms=0;
    integer last_write_cycle[0:H-1],min_target_rmw_gap=2147483647;
    integer sync_checks=0,max_reader_wait=0,max_r_stall=0,current_r_stall=0,compute_cycles=0;
    reg [12:0] previous_target=0;
    reg arheld=0,rheld=0,fheld=0,source_check=0,weight_check=0;
    reg [31:0] heldaddr;reg [3:0] heldlen;
    reg [63:0] helddata,heldfifo;reg [1:0] heldresp;reg [5:0] heldrid;reg heldlast;
    reg signed [30:0] before_source;reg signed [49:0] before_chem;reg signed [23:0] before_weight;
    function automatic integer response_gap(input integer index);
        begin response_gap=(index%1024==1023)?7:((index%64>=48)?3:0);end
    endfunction
    always @(posedge clk) begin
        if(!rst_n) begin
            active<=0;rvalid<=0;arready<=0;rdata<=0;rresp<=0;rid<=0;rlast<=0;
            bstart<=0;blen<=0;bbeat<=0;delay_left<=0;
        end else begin
            // Uses simulation time, avoiding races with the monitor counter.
            arready<=((($time/10)%5)!=0);
            if(arvalid&&arready) begin
                if(active) $fatal(1,"more than one outstanding AR");
                if(arid!=0||arsize!=3||arburst!=1||araddr[2:0]!=0) $fatal(1,"AXI attributes");
                if({1'b0,araddr[11:0]}+8*(arlen+1)>4096) $fatal(1,"burst crosses 4KiB");
                if(araddr!=expected_addr) $fatal(1,"DDR address gap/repeat");
                if(burst_seen==0&&arlen!=1) $fatal(1,"missing initial page split");
                if((araddr-BASE)/8+arlen+1>E) $fatal(1,"read beyond full edge stream");
                $fwrite(burst_log,"%0d,%08h,%0d,%0d\n",burst_seen,araddr,arlen+1,cycles);
                expected_addr=expected_addr+8*(arlen+1);burst_seen=burst_seen+1;
                if((expected_addr&4095)==0) page_ends=page_ends+1;
                active<=1;bstart<=(araddr-BASE)/8;blen<=arlen+1;bbeat<=0;
                delay_left<=response_gap((araddr-BASE)/8);
            end
            if(rvalid&&rready) begin
                rvalid<=0;bbeat<=bbeat+1;bus_beats=bus_beats+1;
                if(bbeat==blen-1) active<=0;
                else delay_left<=response_gap(bstart+bbeat+1);
            end
            if(active&&!rvalid) begin
                if(delay_left!=0) begin delay_left<=delay_left-1;r_bubbles=r_bubbles+1;end
                else begin
                    if(bstart+bbeat>=E) $fatal(1,"mock DDR array out of range");
                    rvalid<=1;rdata<=edges[bstart+bbeat];rresp<=0;rid<=0;rlast<=(bbeat==blen-1);
                end
            end
        end
    end
    always @(posedge clk) begin
        clock_count=clock_count+1;
        if(!rst_n) begin arheld=0;rheld=0;fheld=0;source_check=0;weight_check=0;end
        else begin
            if(arheld&&(!arvalid||araddr!==heldaddr||arlen!==heldlen)) $fatal(1,"AR unstable during stall");
            if(rheld&&(!rvalid||rdata!==helddata||rresp!==heldresp||rid!==heldrid||rlast!==heldlast)) $fatal(1,"DDR unstable during stall");
            if(fheld&&(!dut.fifo_out_valid||dut.fifo_out!==heldfifo)) $fatal(1,"FIFO unstable during stall");
            arheld=arvalid&&!arready;heldaddr=araddr;heldlen=arlen;
            rheld=rvalid&&!rready;helddata=rdata;heldresp=rresp;heldrid=rid;heldlast=rlast;
            fheld=dut.fifo_out_valid&&!dut.fifo_out_ready;heldfifo=dut.fifo_out;
            if(occupancy>FIFO_DEPTH+1) $fatal(1,"FIFO overflow");
            if(occupancy>max_fifo) max_fifo=occupancy;
            if(arvalid&&!arready) ar_stalls=ar_stalls+1;
            if(rvalid&&!rready) begin
                current_r_stall=current_r_stall+1;
                if(current_r_stall>max_r_stall) max_r_stall=current_r_stall;
            end else current_r_stall=0;
            if(dut.reader.wait_count>max_reader_wait) max_reader_wait=dut.reader.wait_count;
            if(dut.fifo_out_valid&&dut.fifo_out_ready) begin
                if(stream_seen>=E||dut.fifo_out!==edges[stream_seen]) $fatal(1,"FIFO loss/repeat/reorder at %0d",stream_seen);
                stream_seen=stream_seen+1;
            end
            source_check=(dut.core.state==dut.core.READ||dut.core.state==dut.core.N_READ);
            weight_check=(dut.core.state==dut.core.READ);
            if(source_check) begin
                before_source=dut.core.source_mem[weight_check?dut.core.src:dut.core.h_index];
                before_chem=dut.core.chemical_mem[weight_check?dut.core.target:dut.core.h_index];
                sync_checks=sync_checks+1;
                if(dut.core.edge_write||dut.core.state==dut.core.CLEAR) $fatal(1,"chemical read/write collision");
            end
            if(weight_check) begin
                if(dut.core.src>=S||dut.core.target>=H||dut.core.weight_index>=W) $fatal(1,"decoded index out of range");
                before_weight=dut.core.weight_rom[dut.core.weight_index];
                source_reads[dut.core.src]=source_reads[dut.core.src]+1;
                if(dut.core.src>=16384) high_source_reads=high_source_reads+1;
                if(clock_count-last_write_cycle[dut.core.target]<min_target_rmw_gap)
                    min_target_rmw_gap=clock_count-last_write_cycle[dut.core.target];
            end
            if(dut.core.edge_write) last_write_cycle[dut.core.target]=clock_count;
        end
    end
    always @(negedge clk) begin
        if(rst_n&&source_check&&(dut.core.source_q!==before_source||dut.core.chemical_q!==before_chem)) $fatal(1,"synchronous state/chemical read");
        if(rst_n&&weight_check&&dut.core.weight_q!==before_weight) $fatal(1,"synchronous dictionary read");
        if(rst_n&&trace_valid) begin
            if(edge_seen>=E||trace_gid!==edges[edge_seen][20:0]||trace_target!==edges[edge_seen][48:36]) $fatal(1,"edge ID/target mismatch at %0d",edge_seen);
            if({trace_term,trace_sum}!==expected_trace[edge_seen]) $fatal(1,"integer edge mismatch at %0d",edge_seen);
            if(dut.core.meta!==edges[edge_seen]) $fatal(1,"raw record mismatch");
            if(edge_seen>0&&trace_target==previous_target) same_target=same_target+1;
            previous_target=trace_target;target_edges[trace_target]=target_edges[trace_target]+1;
            dictionary_edges[dut.core.weight_index]=dictionary_edges[dut.core.weight_index]+1;
            if(dut.core.weight_q==0) zero_weight_edges=zero_weight_edges+1;
            if(dut.core.source_q<0) negative_source_edges=negative_source_edges+1;
            if(trace_term==0) zero_terms=zero_terms+1;
            if(trace_term<0) negative_terms=negative_terms+1;
            $fwrite(raw,"%0d,%016h,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d\n",edge_seen,dut.core.meta,trace_gid,
                dut.core.src,trace_target,dut.core.weight_index,dut.core.source_q,trace_term,trace_sum,cycles);
            edge_seen=edge_seen+1;
            if(edge_seen%100000==0) $display("FULL_PROGRESS edges=%0d cycles=%0d",edge_seen,cycles);
        end
    end
    initial begin
        $readmemh("rom/edges.mem",edges);$readmemh("rom/requests.mem",requests);
        $readmemh("rom/expected.mem",expected);$readmemh("rom/edge_traces.mem",expected_trace);
        raw=$fopen("edge_trace.csv","w");state_raw=$fopen("candidates.csv","w");summary=$fopen("summary.csv","w");
        burst_log=$fopen("axi_bursts.csv","w");coverage_log=$fopen("coverage.csv","w");
        if(!raw||!state_raw||!summary||!burst_log||!coverage_log) $fatal(1,"cannot open complete raw output logs");
        $fwrite(raw,"edge_index,record_hex,global_edge_id,source_index,target,dict_index,source_q24,term_q24,partial_sum_q24,cycle\n");
        $fwrite(state_raw,"index,candidate_q24\n");$fwrite(summary,"metric,value\n");
        $fwrite(burst_log,"burst_index,address_hex,beats,cycle\n");$fwrite(coverage_log,"kind,index,count\n");
        for(j=0;j<S;j=j+1) source_reads[j]=0;
        for(j=0;j<H;j=j+1) begin target_edges[j]=0;last_write_cycle[j]=-1000000;end
        for(j=0;j<W;j=j+1) dictionary_edges[j]=0;
        repeat(4) @(negedge clk);rst_n=1;repeat(2) @(negedge clk);
        req_begin=1;@(negedge clk);req_begin=0;
        for(j=0;j<WORDS;j=j+1) begin
            in_we=1;in_addr=j;in_data=$signed(requests[j]);@(negedge clk);
        end
        in_we=0;start=1;@(negedge clk);start=0;
        while(!done&&watchdog<STEP_LIMIT+4) begin @(negedge clk);watchdog=watchdog+1;end
        if(!done) $fatal(1,"full request watchdog: edge_count=%0d status=%h",applied,status);
        compute_cycles=cycles;
        $fwrite(summary,"status,%0d\nreader_error,%0d\ncycles,%0d\n",status,reader_error,cycles);
        if(status!=0||!out_valid||reader_busy||poisoned||reader_error!=0) $fatal(1,"full request rejected status=%h reader=%h",status,reader_error);
        if(edge_seen!=E||stream_seen!=E||applied!=E||received!=E||bus_beats!=E) $fatal(1,"edge count mismatch");
        if(signature!==`FULL_SIGNATURE||result_step_id!=0||result_tag!==`OLD_STATE_TAG) $fatal(1,"signature/identity mismatch");
        if(cycles<=2000000||cycles>=STEP_LIMIT) $fatal(1,"unexpected full cycle range");
        if(burst_seen!=`FULL_BURSTS||page_ends!=`FULL_BOUNDARIES) $fatal(1,"burst/page boundary coverage");
        if(max_fifo!=5||stalls==0||ar_stalls==0||r_bubbles==0||max_reader_wait>=64) $fatal(1,"backpressure/stall coverage");
        if(high_source_reads!=2067||source_reads[S-1]!=92||same_target!=0||zero_weight_edges!=8790) $fatal(1,"graph coverage changed");
        if(min_target_rmw_gap<3) $fatal(1,"unsafe same-target RMW distance");
        for(j=0;j<H;j=j+1) begin
            out_addr=j;@(negedge clk);
            if(out_data!==$signed({expected[j][30],expected[j]})) $fatal(1,"candidate mismatch at %0d",j);
            $fwrite(state_raw,"%0d,%0d\n",j,out_data);
            if(target_edges[j]<26||target_edges[j]>119) $fatal(1,"target missing or extra fanin");
            $fwrite(coverage_log,"target,%0d,%0d\n",j,target_edges[j]);
        end
        for(j=0;j<S;j=j+1) begin
            if(dut.core.source_mem[j]!==requests[j][30:0]||source_reads[j]==0) $fatal(1,"old source modified or unread %0d",j);
            $fwrite(coverage_log,"source,%0d,%0d\n",j,source_reads[j]);
        end
        for(j=0;j<W;j=j+1) begin
            if(dictionary_edges[j]==0) $fatal(1,"unused dictionary entry %0d",j);
            $fwrite(coverage_log,"dictionary,%0d,%0d\n",j,dictionary_edges[j]);
        end
        out_addr=H;@(negedge clk);if(out_data!==0) $fatal(1,"out-of-range candidate visible");
        $fwrite(summary,"requests,1\nedges,%0d\ncandidates,%0d\nbursts,%0d\npage_boundary_ends,%0d\n",E,H,burst_seen,page_ends);
        $fwrite(summary,"fifo_stall_cycles,%0d\nmax_fifo_occupancy,%0d\nar_stall_cycles,%0d\nr_bubble_cycles,%0d\n",stalls,max_fifo,ar_stalls,r_bubbles);
        $fwrite(summary,"max_reader_wait,%0d\nmax_r_backpressure_run,%0d\nsource_reads_ge_16384,%0d\nlast_source_reads,%0d\n",max_reader_wait,max_r_stall,high_source_reads,source_reads[S-1]);
        $fwrite(summary,"same_target_adjacent,%0d\nmin_same_target_write_read_gap,%0d\nsynchronous_read_checks,%0d\n",same_target,min_target_rmw_gap,sync_checks);
        $fwrite(summary,"zero_weight_edges,%0d\nnegative_source_edges,%0d\nzero_terms,%0d\nnegative_terms,%0d\n",zero_weight_edges,negative_source_edges,zero_terms,negative_terms);
        $fwrite(summary,"signature_hex,%016h\nstep_timeout,%0d\naxi_timeout,64\ntimeout_events,0\nreject_events,0\n",signature,STEP_LIMIT);
        $display("FULL_ALL_PASS requests=1 H=%0d sources=%0d edges=%0d cycles=%0d zero_edges=%0d bursts=%0d fifo_stalls=%0d",H,S,E,compute_cycles,zero_weight_edges,burst_seen,stalls);
        $fclose(raw);$fclose(state_raw);$fclose(summary);$fclose(burst_log);$fclose(coverage_log);$finish;
    end
endmodule

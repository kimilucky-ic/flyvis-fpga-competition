from pathlib import Path
P=Path(__file__).resolve().parent
old=(P.parent/'ramfix_r2_sim_20261012/tb_fullscale.sv').read_text(encoding='utf-8')
prefix=old[:old.index('    reg [63:0] edges[0:E-1]')]
prefix=prefix.replace('module tb_fullscale;','module tb_pipeline_full;').replace('FIFO_DEPTH=4;','FIFO_DEPTH=128;')
tail=r'''
    reg [63:0] edges[0:E-1];reg [31:0] requests[0:WORDS-1];reg [30:0] expected[0:H-1];reg [80:0] expected_trace[0:E-1];
    integer source_reads[0:S-1],target_edges[0:H-1],dictionary_edges[0:W-1];
    integer q_start[0:15],q_length[0:15];
    integer qp=0,qw=0,qn=0,qbeat=0,delay_left=0,stress=0;
    integer clock_count=0,edge_seen=0,stream_seen=0,burst_seen=0,bus_beats=0;
    integer max_fifo=0,ar_stalls=0,r_bubbles=0,watchdog=0,j,expected_addr=BASE,page_ends=0;
    integer max_queued=0,max_reader_wait=0,source_sync=0,chemical_sync=0,consecutive=0,previous_cycle=-10;
    integer raw,state_raw,summary,burst_log,coverage_log,zero_weight_edges=0,negative_source_edges=0,zero_terms=0,negative_terms=0;
    integer source_index,dict_index,compute_cycles;
    reg consumed=0,arheld=0,rheld=0,fheld=0,scheck=0,ccheck=0;
    reg [31:0] heldaddr;reg [3:0] heldlen;reg [63:0] helddata,heldfifo;reg heldlast;
    reg signed [30:0] expected_source;reg signed [49:0] expected_chemical;
    function automatic integer response_gap(input integer index);
        begin response_gap=(index%1024==1023)?7:((index%64>=48)?3:0);end
    endfunction
    always @(posedge clk) begin
        clock_count=clock_count+1;consumed=0;scheck=0;ccheck=0;
        if(rst_n) begin
            if(arheld&&(!arvalid||araddr!==heldaddr||arlen!==heldlen)) $fatal(1,"AR stability");
            if(rheld&&(!rvalid||rdata!==helddata||rlast!==heldlast)) $fatal(1,"R stability");
            if(fheld&&(!dut.fifo_out_valid||dut.fifo_out!==heldfifo)) $fatal(1,"FIFO stability");
            arheld=arvalid&&!arready;heldaddr=araddr;heldlen=arlen;
            rheld=rvalid&&!rready;helddata=rdata;heldlast=rlast;
            fheld=dut.fifo_out_valid&&!dut.fifo_out_ready;heldfifo=dut.fifo_out;
            if(occupancy>FIFO_DEPTH+1||dut.reader.queued>4||qn>4) $fatal(1,"bounded queue overflow");
            if(occupancy>max_fifo) max_fifo=occupancy;
            if(dut.reader.queued>max_queued) max_queued=dut.reader.queued;
            if(dut.reader.wait_count>max_reader_wait) max_reader_wait=dut.reader.wait_count;
            if(dut.reader.ar_wait>max_reader_wait) max_reader_wait=dut.reader.ar_wait;
            if(arvalid&&!arready) ar_stalls=ar_stalls+1;
            if(rvalid&&rready) begin
                if(qn==0||rdata!==edges[bus_beats]||rlast!==(qbeat==q_length[qp]-1)) $fatal(1,"DDR beat bookkeeping");
                bus_beats=bus_beats+1;consumed=1;
                if(qbeat==q_length[qp]-1) begin qp=(qp+1)%16;qn=qn-1;qbeat=0;end else qbeat=qbeat+1;
                delay_left=stress?(1+response_gap(bus_beats)):0;
            end
            if(arvalid&&arready) begin
                if(arid!=0||arsize!=3||arburst!=1||araddr!==expected_addr||araddr[2:0]!=0) $fatal(1,"AXI address/attributes/order");
                if({1'b0,araddr[11:0]}+8*(arlen+1)>4096||(araddr-BASE)/8+arlen+1>E) $fatal(1,"AXI boundary/length");
                $fwrite(burst_log,"%0d,%08h,%0d,%0d\n",burst_seen,araddr,arlen+1,cycles);
                q_start[qw]=(araddr-BASE)/8;q_length[qw]=arlen+1;qw=(qw+1)%16;qn=qn+1;
                if(burst_seen==0) delay_left=stress?response_gap(0):0;
                burst_seen=burst_seen+1;expected_addr=expected_addr+8*(arlen+1);
                if((expected_addr&4095)==0) page_ends=page_ends+1;
            end
            if(dut.fifo_out_valid&&dut.fifo_out_ready) begin
                if(stream_seen>=E||dut.fifo_out!==edges[stream_seen]) $fatal(1,"FIFO sequence at %0d",stream_seen);
                stream_seen=stream_seen+1;
            end
            if(dut.core.source_re) begin
                scheck=1;expected_source=dut.core.source_mem[dut.core.source_raddr];source_sync=source_sync+1;
                if(dut.core.issue_edge) source_reads[dut.core.incoming_src]=source_reads[dut.core.incoming_src]+1;
            end
            if(dut.core.chemical_re) begin ccheck=1;expected_chemical=dut.core.chemical_mem[dut.core.chemical_raddr];chemical_sync=chemical_sync+1;end
        end
    end
    always @(negedge clk) begin
        if(!rst_n) begin arready=0;rvalid=0;rdata=0;rlast=0;end
        else begin
            arready=stress?((clock_count%5)!=0):1;
            if(!rvalid||consumed) begin
                if(qn!=0&&delay_left==0) begin
                    rvalid=1;rdata=edges[q_start[qp]+qbeat];rlast=(qbeat==q_length[qp]-1);rresp=0;rid=0;
                end else begin
                    rvalid=0;
                    if(qn!=0&&delay_left>0) begin delay_left=delay_left-1;r_bubbles=r_bubbles+1;end
                end
            end
            if(scheck&&dut.core.source_q!==expected_source) $fatal(1,"source sync read");
            if(ccheck&&dut.core.chemical_q!==expected_chemical) $fatal(1,"chemical sync read");
            if(trace_valid) begin
                if(edge_seen>=E||dut.core.trace_record!==edges[edge_seen]||trace_gid!==edges[edge_seen][20:0]||trace_target!==edges[edge_seen][48:36]) $fatal(1,"trace identity edge=%0d",edge_seen);
                if({trace_term,trace_sum}!==expected_trace[edge_seen]) $fatal(1,"exact integer edge=%0d got=%0d,%0d expected=%h",edge_seen,trace_term,trace_sum,expected_trace[edge_seen]);
                source_index=edges[edge_seen][35:21];dict_index=edges[edge_seen][58:49];
                if(dut.core.trace_source_value!==requests[source_index][30:0]) $fatal(1,"trace source identity");
                target_edges[trace_target]=target_edges[trace_target]+1;dictionary_edges[dict_index]=dictionary_edges[dict_index]+1;
                if(dut.core.weight_rom[dict_index]==0) zero_weight_edges=zero_weight_edges+1;
                if(dut.core.trace_source_value<0) negative_source_edges=negative_source_edges+1;
                if(trace_term==0) zero_terms=zero_terms+1;
                if(trace_term<0) negative_terms=negative_terms+1;
                if(cycles==previous_cycle+1) consecutive=consecutive+1;previous_cycle=cycles;
                $fwrite(raw,"%0d,%016h,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d\n",edge_seen,dut.core.trace_record,trace_gid,source_index,trace_target,dict_index,dut.core.trace_source_value,trace_term,trace_sum,cycles);
                edge_seen=edge_seen+1;
                if(edge_seen%100000==0) $display("PIPE_PROGRESS stress=%0d edges=%0d cycles=%0d",stress,edge_seen,cycles);
            end
        end
    end
    initial begin
        if($value$plusargs("STRESS=%d",stress)) begin end
        $readmemh("rom/edges.mem",edges);$readmemh("rom/requests.mem",requests);$readmemh("rom/expected.mem",expected);$readmemh("rom/edge_traces.mem",expected_trace);
        raw=$fopen("edge_trace.csv","w");state_raw=$fopen("candidates.csv","w");summary=$fopen("summary.csv","w");burst_log=$fopen("axi_bursts.csv","w");coverage_log=$fopen("coverage.csv","w");
        $fwrite(raw,"edge_index,record_hex,global_edge_id,source_index,target,dict_index,source_q24,term_q24,partial_sum_q24,cycle\n");
        $fwrite(state_raw,"index,candidate_q24\n");$fwrite(summary,"metric,value\n");$fwrite(burst_log,"burst_index,address_hex,beats,cycle\n");$fwrite(coverage_log,"kind,index,count\n");
        for(j=0;j<S;j=j+1) source_reads[j]=0;
        for(j=0;j<H;j=j+1) target_edges[j]=0;
        for(j=0;j<W;j=j+1) dictionary_edges[j]=0;
        repeat(4) @(negedge clk);rst_n=1;repeat(2) @(negedge clk);
        req_begin=1;@(negedge clk);req_begin=0;
        for(j=0;j<WORDS;j=j+1) begin in_we=1;in_addr=j;in_data=$signed(requests[j]);@(negedge clk);end
        in_we=0;start=1;@(negedge clk);start=0;
        while(!done&&watchdog<STEP_LIMIT+4) begin @(negedge clk);watchdog=watchdog+1;end
        if(!done||status!=0||!out_valid||reader_busy||poisoned||reader_error!=0) $fatal(1,"request failed status=%h reader=%h",status,reader_error);
        compute_cycles=cycles;
        if(edge_seen!=E||stream_seen!=E||applied!=E||received!=E||bus_beats!=E) $fatal(1,"full edge count");
        if(signature!==`FULL_SIGNATURE||result_step_id!=0||result_tag!==`OLD_STATE_TAG) $fatal(1,"identity/signature");
        if(burst_seen!=`FULL_BURSTS||page_ends!=`FULL_BOUNDARIES||max_queued!=4) $fatal(1,"burst coverage");
        if(max_fifo!=FIFO_DEPTH+1||stalls==0||max_reader_wait>=64) $fatal(1,"backpressure coverage");
        if(!stress&&(cycles>=600000||consecutive<E-32)) $fatal(1,"peak initiation interval/cycles %0d consecutive=%0d",cycles,consecutive);
        if(stress&&(cycles>=2000000||ar_stalls==0||r_bubbles==0)) $fatal(1,"stress timing/coverage");
        for(j=0;j<H;j=j+1) begin
            out_addr=j;@(negedge clk);
            if(out_data!==$signed({expected[j][30],expected[j]})) $fatal(1,"candidate %0d got=%0d expected=%0d",j,out_data,$signed(expected[j]));
            $fwrite(state_raw,"%0d,%0d\n",j,out_data);
            if(target_edges[j]<26||target_edges[j]>119) $fatal(1,"target coverage");
            $fwrite(coverage_log,"target,%0d,%0d\n",j,target_edges[j]);
        end
        for(j=0;j<S;j=j+1) begin
            if(dut.core.source_mem[j]!==requests[j][30:0]||source_reads[j]==0) $fatal(1,"old source changed/unused");
            $fwrite(coverage_log,"source,%0d,%0d\n",j,source_reads[j]);
        end
        for(j=0;j<W;j=j+1) begin if(dictionary_edges[j]==0) $fatal(1,"dictionary coverage");$fwrite(coverage_log,"dictionary,%0d,%0d\n",j,dictionary_edges[j]);end
        out_addr=H;@(negedge clk);if(out_data!==0) $fatal(1,"invalid output address");
        if(source_sync!=E+2*H||chemical_sync!=E+H||zero_weight_edges!=8790) $fatal(1,"sync/zero counts");
        $fwrite(summary,"stress,%0d\ncycles,%0d\nstatus,%0d\nreader_error,%0d\nedges,%0d\ncandidates,%0d\nbursts,%0d\npage_boundary_ends,%0d\n",stress,compute_cycles,status,reader_error,E,H,burst_seen,page_ends);
        $fwrite(summary,"max_fifo_occupancy,%0d\nfifo_stall_cycles,%0d\nmax_outstanding,%0d\nar_stall_cycles,%0d\nr_bubble_cycles,%0d\nmax_reader_wait,%0d\n",max_fifo,stalls,max_queued,ar_stalls,r_bubbles,max_reader_wait);
        $fwrite(summary,"source_sync_checks,%0d\nchemical_sync_checks,%0d\nconsecutive_edge_retirements,%0d\nzero_weight_edges,%0d\nnegative_source_edges,%0d\nzero_terms,%0d\nnegative_terms,%0d\n",source_sync,chemical_sync,consecutive,zero_weight_edges,negative_source_edges,zero_terms,negative_terms);
        $fwrite(summary,"signature_hex,%016h\n",signature);
        $display("PIPELINE_FULL_ALL_PASS stress=%0d edges=%0d candidates=%0d cycles=%0d consecutive=%0d",stress,E,H,compute_cycles,consecutive);
        $fclose(raw);$fclose(state_raw);$fclose(summary);$fclose(burst_log);$fclose(coverage_log);$finish;
    end
endmodule
'''
(P/'tb_pipeline_full.sv').write_text(prefix+tail,encoding='utf-8')

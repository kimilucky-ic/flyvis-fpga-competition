`timescale 1ns/1ps
`include "test_config.svh"
module tb_directed;
    localparam H=8,S=20,E=256,W=8;
    reg clk=0;always #5 clk=~clk;
    reg rst=0,req=0,we=0,start=0,ev=0,tdone=0;
    reg [15:0] ia=0;reg signed [31:0] din=0;reg [12:0] oa=0;
    reg [63:0] edata=0,expected_sig=`TEST_SIG;
    reg [31:0] terr=0;
    wire ready,busy,done,ov,tv;wire [31:0] status,cycles,applied;
    wire [63:0] sig;wire signed [31:0] dout;wire [20:0] gid;wire [12:0] target;
    wire signed [30:0] term;wire signed [49:0] sum;
    ddr_synapse_core #(.H_COUNT(H),.SOURCE_COUNT(S),.EDGE_COUNT(E),.WEIGHT_COUNT(W),.STEP_TIMEOUT(4096)) dut(
        .clk(clk),.rst_n(rst),.req_begin(req),.in_we(we),.start(start),.in_addr(ia),.in_data(din),
        .step_id(32'd123),.old_state_tag(32'h12345678),.expected_signature(expected_sig),
        .edge_data(edata),.edge_valid(ev),.edge_ready(ready),.transport_done(tdone),.transport_error(terr),
        .busy(busy),.done(done),.out_valid(ov),.status(status),.cycles(cycles),.edges_applied(applied),.signature(sig),
        .result_step_id(),.result_old_state_tag(),.out_addr(oa),.out_data(dout),.trace_valid(tv),.trace_gid(gid),.trace_target(target),.trace_term(term),.trace_sum(sum));
    reg [63:0] edges[0:E-1];reg [31:0] requests[0:S+H-1];reg [30:0] expected[0:H-1];reg [80:0] traces[0:E-1];
    integer case_id=-1,sent=0,seen=0,ticks=0,j,watchdog,passes=0,trace_file,previous_cycle=-10,consecutive=0;
    reg feeding=0,checked_hold=0;reg [63:0] held;
    always @(posedge clk) begin
        if(rst) begin
            if(ev&&ready) sent=sent+1;
            if(checked_hold&&status==0&&busy&&(edata!==held||!ev)) $fatal(1,"directed source changed while held");
            checked_hold=ev&&!ready&&status==0;held=edata;
        end else checked_hold=0;
    end
    always @(negedge clk) begin
        if(rst&&tv) begin
            if(seen>=E||gid!==edges[seen][20:0]||target!==edges[seen][48:36]||{term,sum}!==traces[seen])
                $fatal(1,"directed exact trace mismatch case=%0d edge=%0d gotterm=%0d gotsum=%0d expected=%h",case_id,seen,term,sum,traces[seen]);
            if(cycles==previous_cycle+1) consecutive=consecutive+1;
            previous_cycle=cycles;
            $fwrite(trace_file,"%0d,%0d,%0d,%0d,%0d\n",case_id,seen,gid,term,sum);seen=seen+1;
        end
    end
    task run_case(input integer id,input [31:0] expected_status);
        integer local_clock;
        begin
            @(negedge clk);rst=0;req=0;we=0;start=0;ev=0;tdone=0;terr=0;
            repeat(3) @(negedge clk);
            case_id=id;sent=0;seen=0;consecutive=0;previous_cycle=-10;expected_sig=(id==7)?(`TEST_SIG^64'h1):`TEST_SIG;
            $readmemh("rom/weights.mem",dut.weight_rom);$readmemh("rom/neurons.mem",dut.neuron_rom);
            rst=1;@(negedge clk);req=1;@(negedge clk);req=0;
            for(j=0;j<S+H;j=j+1) begin
                we=1;ia=(id==15&&j==3)?4:j;din=requests[j];
                if(id==8&&j==0) din=32'h3fffffff;
                if(id==16&&j==2) din=32'h40000000;
                @(negedge clk);
            end
            we=0;
            if(id==8) dut.weight_rom[1]=24'h7fffff;
            if(id==11) dut.neuron_rom[0]={31'h3fffffff,31'h3fffffff};
            start=1;@(negedge clk);start=0;
            watchdog=0;local_clock=0;
            while(!done&&watchdog<8200) begin
                req=0;we=0;start=0;
                ev=(sent<E)&&(id!=18)&&!(id==1&&local_clock%7<3);
                edata=edges[(sent<E)?sent:0];
                if(sent==7) case(id)
                    2:edata[35:21]=S;
                    3:edata[48:36]=H;
                    4:edata[58:49]=W;
                    5:edata[63]=1;
                    6:edata[20:0]=0;
                endcase
                if(id==9&&dut.state==dut.EDGES&&sent==0) dut.chemical_mem[0]=50'h1ffffffffffff;
                tdone=(sent==E);
                if(id==10&&dut.state==dut.WAIT_END) dut.chemical_mem[0]=50'd1073741824;
                if(id==20&&dut.state==dut.D_PASS&&dut.issued==0) begin dut.source_mem[0]=31'h3fffffff;dut.velocity_mem[0]=31'h3fffffff;end
                if(dut.state==dut.EDGES&&sent==3) begin
                    if(id==12) req=1;
                    if(id==13) start=1;
                    if(id==14) we=1;
                    if(id==19) terr=32'h2;
                end
                @(negedge clk);watchdog=watchdog+1;local_clock=local_clock+1;
            end
            ev=0;req=0;we=0;start=0;terr=0;
            if(!done||status!==expected_status) $fatal(1,"case %0d status got=%h expected=%h",id,status,expected_status);
            if(expected_status==0) begin
                if(!ov||seen!=E||applied!=E||sig!==`TEST_SIG) $fatal(1,"success count/signature");
                if(id==0&&consecutive<E-2) $fatal(1,"pipeline not one edge/cycle %0d",consecutive);
                for(j=0;j<H;j=j+1) begin oa=j;@(negedge clk);if(dout!==$signed({expected[j][30],expected[j]})) $fatal(1,"candidate case=%0d index=%0d got=%0d expected=%0d",id,j,dout,$signed(expected[j]));end
                for(j=0;j<S;j=j+1) if(dut.source_mem[j]!==requests[j][30:0]) $fatal(1,"old state overwritten");
                oa=H;@(negedge clk);if(dout!==0) $fatal(1,"invalid candidate address");
            end else if(ov||dout!==0) $fatal(1,"rejected candidate visible");
            repeat(12) begin @(negedge clk);if(tv) $fatal(1,"trace leaked after completion/reject");end
            $display("DIRECTED_PASS case=%0d status=%h traces=%0d cycles=%0d",id,status,seen,cycles);passes=passes+1;
        end
    endtask
    initial begin
        $readmemh("rom/edges.mem",edges);$readmemh("rom/requests.mem",requests);$readmemh("rom/expected.mem",expected);$readmemh("rom/edge_traces.mem",traces);
        trace_file=$fopen("directed_trace.csv","w");$fwrite(trace_file,"case,edge,gid,term,sum\n");
        run_case(0,0);run_case(1,0);
        for(integer n=2;n<=6;n=n+1) run_case(n,32'h10);
        run_case(7,32'h20);run_case(8,32'h4);run_case(9,32'h2);run_case(10,32'h4);run_case(11,32'h4);
        run_case(12,32'h8);run_case(13,32'h8);run_case(14,32'h8);run_case(15,32'h8);run_case(16,32'h9);
        run_case(18,32'h80);run_case(19,32'h40);run_case(20,32'h4);
        $fclose(trace_file);$display("DIRECTED_ALL_PASS cases=%0d",passes);$finish;
    end
endmodule

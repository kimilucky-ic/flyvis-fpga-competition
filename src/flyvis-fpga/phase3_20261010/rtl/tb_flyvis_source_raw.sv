`timescale 1ns/1ps
module tb_flyvis_source_raw;
    localparam integer WORDS=1498, H=67, REQUESTS=801;
    reg clk=0;
    always #5 clk=~clk;
    reg rst_n=0, req_begin=0, in_we=0, start=0;
    reg [10:0] in_addr=0;
    reg signed [31:0] in_data=0;
    reg [6:0] out_addr=0;
    wire busy, done, out_valid;
    wire [31:0] status, compute_cycles;
    wire signed [31:0] out_data;
    reg signed [31:0] requests [0:REQUESTS*WORDS-1];
    reg signed [31:0] expected [0:REQUESTS*H-1];
    reg signed [31:0] baseline [0:H-1];
    integer audit, dump, i, h, k, timeout, echo_bad=0, zero_bad=0, changed=0;
    flyvis_source_raw_core dut(.*);

    task automatic launch(input integer request_id, input integer mode);
        integer a;
        begin
            @(negedge clk); req_begin=1;
            @(negedge clk); req_begin=0;
            for(a=0; a<((mode==3)?1:WORDS); a=a+1) begin
                in_we=1; in_addr=a; in_data=requests[request_id*WORDS+a];
                if(mode==1 && a==0) in_data=32'h40000000;
                if(mode==2 && a==1431) in_data=32'h0fffffff;
                @(negedge clk);
            end
            in_we=0; start=1;
            @(negedge clk); start=0;
            timeout=0;
            while(!done) begin
                @(posedge clk); #1; timeout=timeout+1;
                if(timeout>100000) $fatal(1,"TIMEOUT request=%0d mode=%0d",request_id,mode);
            end
        end
    endtask

    task automatic check_failed(input integer mode, input integer required_status);
        integer n;
        begin
            launch(0,mode);
            if(status!==required_status || out_valid!==0) $fatal(1,"FAIL-CLOSED mode=%0d status=%h valid=%b",mode,status,out_valid);
            for(n=0;n<H;n=n+1) begin
                out_addr=n; #1;
                if(out_data!==0) $fatal(1,"STALE OUTPUT on failed request H=%0d",n);
            end
            $fwrite(audit,"negative_%0d,%08x,%0d,FAIL_CLOSED\n",mode,status,compute_cycles);
            $display("PASS RTL fail-closed control mode=%0d status=%h",mode,status);
        end
    endtask

    initial begin
        $readmemh("rom/animation_requests_q22.mem",requests);
        $readmemh("rom/animation_expected_q22.mem",expected);
        audit=$fopen("artifacts/rtl_animation_q22_request_trace.csv","w");
        dump=$fopen("artifacts/rtl_animation_q22_output.mem","w");
        if(!audit || !dump) $fatal(1,"Cannot open RTL evidence files");
        $fwrite(audit,"request_id,status,compute_cycles,comparison\n");
        repeat(5) @(negedge clk);
        rst_n=1;
        for(k=0;k<REQUESTS;k=k+1) begin
            launch(k,0);
            if(status!==0 || out_valid!==1) $fatal(1,"RTL STATUS request=%0d status=%h",k,status);
            for(h=0;h<H;h=h+1) begin
                out_addr=h; #1;
                if(out_data!==expected[k*H+h]) $fatal(1,"RTL MISMATCH request=%0d H=%0d expected=%0d actual=%0d",k,h,expected[k*H+h],out_data);
                $fwrite(dump,"%08x\n",out_data);
                if(k==0) begin
                    baseline[h]=out_data;
                    if(out_data!=requests[1364+h]) echo_bad=echo_bad+1;
                    if(out_data!=0) zero_bad=zero_bad+1;
                end
                if(k==800 && out_data!=baseline[h]) changed=changed+1;
            end
            $fwrite(audit,"%0d,%08x,%0d,EXACT_INTEGER_ORACLE\n",k,status,compute_cycles);
            if(k==0 || k==31 || k==799) begin
                $display("PASS RTL %0d actual 01_off_right stateless SOURCE_RAW requests; cycles=%0d",k+1,compute_cycles);
                $fflush(audit); $fflush(dump);
            end
        end
        if(echo_bad==0 || zero_bad==0 || changed==0) $fatal(1,"NEGATIVE CONTROL DID NOT DISCRIMINATE");
        $display("PASS RTL echo/zero controls rejected; boundary perturb changed %0d H outputs",changed);
        check_failed(1,1);
        check_failed(2,4);
        check_failed(3,8);
        $fclose(audit); $fclose(dump);
        $display("PASS RTL total 801 valid requests plus malformed/overflow/incomplete controls");
        $finish;
    end
    initial begin
        #1000000000;
        $fatal(1,"GLOBAL RTL WATCHDOG");
    end
endmodule

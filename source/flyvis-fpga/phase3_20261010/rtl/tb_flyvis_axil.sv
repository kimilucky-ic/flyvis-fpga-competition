`timescale 1ns/1ps
module tb_flyvis_axil;
    reg s_axi_aclk=0; always #5 s_axi_aclk=~s_axi_aclk;
    reg s_axi_aresetn=0;
    reg [15:0] s_axi_awaddr=0,s_axi_araddr=0;
    reg [2:0] s_axi_awprot=0,s_axi_arprot=0;
    reg s_axi_awvalid=0,s_axi_wvalid=0,s_axi_bready=0,s_axi_arvalid=0,s_axi_rready=0;
    wire s_axi_awready,s_axi_wready,s_axi_bvalid,s_axi_arready,s_axi_rvalid;
    reg [31:0] s_axi_wdata=0; reg [3:0] s_axi_wstrb=15;
    wire [1:0] s_axi_bresp,s_axi_rresp; wire [31:0] s_axi_rdata;
    reg signed [31:0] requests[0:801*1498-1],expected[0:801*67-1];
    integer k,a,h,polls,trace,dump; reg [31:0] flags,value,fault;
    flyvis_source_raw_axil dut(.*);
    task automatic aw(input [15:0] address,input integer delay_cycles);
        begin
            repeat(delay_cycles) @(negedge s_axi_aclk);
            s_axi_awaddr=address; s_axi_awvalid=1;
            @(posedge s_axi_aclk); while(!s_axi_awready) @(posedge s_axi_aclk);
            @(negedge s_axi_aclk); s_axi_awvalid=0;
        end
    endtask
    task automatic wd(input [31:0] data,input integer delay_cycles);
        begin
            repeat(delay_cycles) @(negedge s_axi_aclk);
            s_axi_wdata=data; s_axi_wvalid=1;
            @(posedge s_axi_aclk); while(!s_axi_wready) @(posedge s_axi_aclk);
            @(negedge s_axi_aclk); s_axi_wvalid=0;
        end
    endtask
    task automatic write_reg(input [15:0] address,input [31:0] data,input integer skew,input [1:0] response);
        reg [1:0] saved_response;
        begin
            @(negedge s_axi_aclk);
            fork aw(address,(skew<0)?-skew:0); wd(data,(skew>0)?skew:0); join
            while(!s_axi_bvalid) begin @(posedge s_axi_aclk); #1; end
            saved_response=s_axi_bresp;
            repeat(2) begin @(posedge s_axi_aclk); #1; if(!s_axi_bvalid || s_axi_bresp!==saved_response) $fatal(1,"B backpressure stability"); end
            if(saved_response!==response) $fatal(1,"AXI B response at %h: %h",address,saved_response);
            @(negedge s_axi_aclk); s_axi_bready=1;
            @(negedge s_axi_aclk); s_axi_bready=0;
        end
    endtask
    task automatic read_reg(input [15:0] address,output [31:0] data,input [1:0] response);
        reg [31:0] saved_data; reg [1:0] saved_response;
        begin
            @(negedge s_axi_aclk); s_axi_araddr=address; s_axi_arvalid=1;
            @(posedge s_axi_aclk); while(!s_axi_arready) @(posedge s_axi_aclk);
            @(negedge s_axi_aclk); s_axi_arvalid=0;
            while(!s_axi_rvalid) begin @(posedge s_axi_aclk); #1; end
            saved_data=s_axi_rdata; saved_response=s_axi_rresp;
            repeat(2) begin @(posedge s_axi_aclk); #1; if(!s_axi_rvalid || s_axi_rdata!==saved_data || s_axi_rresp!==saved_response) $fatal(1,"R backpressure stability"); end
            if(saved_response!==response) $fatal(1,"AXI R response at %h: %h",address,saved_response);
            data=saved_data;
            @(negedge s_axi_aclk); s_axi_rready=1;
            @(negedge s_axi_aclk); s_axi_rready=0;
        end
    endtask
    initial begin
        $readmemh("rom/animation_requests_q22.mem",requests); $readmemh("rom/animation_expected_q22.mem",expected);
        trace=$fopen("artifacts/axi_animation_trace.csv","w"); dump=$fopen("artifacts/axi_animation_output.mem","w");
        if(!trace || !dump) $fatal(1,"Evidence file open");
        $fwrite(trace,"request_id,status,compute_cycles,comparison\n");
        repeat(5) @(negedge s_axi_aclk); s_axi_aresetn=1;
        read_reg(0,value,0); if(value!==32'h46565333) $fatal(1,"IP identity");
        read_reg(4,value,0); if(value!==32'h0616141d) $fatal(1,"Numeric profile");
        read_reg(16'h4000,value,2); // no stale candidate after reset
        write_reg(16'h0020,3,2,2); // invalid combined control
        write_reg(16'h0000,0,-2,2); // read-only register
        read_reg(16'h0030,value,2); // unmapped register
        for(k=0;k<801;k=k+1) begin
            write_reg(16'h0020,1,0,0);
            for(a=0;a<1498;a=a+1) write_reg(16'h1000+a*4,requests[k*1498+a],(a%3)-1,0);
            write_reg(16'h0020,2,1,0); polls=0; flags=0;
            while(!flags[1]) begin
                read_reg(16'h0024,flags,0); polls=polls+1;
                if(polls>10000) $fatal(1,"AXI compute timeout");
            end
            read_reg(16'h001c,fault,0); if(fault!==0 || flags[2]!==1) $fatal(1,"AXI failed valid request");
            for(h=0;h<67;h=h+1) begin
                read_reg(16'h4000+h*4,value,0);
                if(value!==expected[k*67+h]) $fatal(1,"AXI H mismatch k=%0d H=%0d",k,h);
                $fwrite(dump,"%08x\n",value);
            end
            read_reg(16'h0018,value,0); $fwrite(trace,"%0d,%08x,%0d,EXACT_INTEGER_ORACLE\n",k,fault,value);
            if(k==0 || k==31 || k==799) begin $display("PASS AXI %0d actual animation requests with AW/W skew and B/R backpressure; cycles=%0d",k+1,value); $fflush(trace); $fflush(dump); end
        end
        write_reg(16'h0020,1,0,0); write_reg(16'h1000,requests[0],-2,0); write_reg(16'h0020,2,2,0);
        flags=0; while(!flags[1]) read_reg(16'h0024,flags,0);
        read_reg(16'h001c,fault,0); if(fault!==8 || flags[2]!==0) $fatal(1,"Incomplete request was not rejected");
        read_reg(16'h4000,value,2); if(value!==0) $fatal(1,"Failed candidate exposed");
        $fwrite(trace,"incomplete,%08x,0,FAIL_CLOSED\n",fault);
        $fclose(trace); $fclose(dump);
        $display("PASS AXI total 801 valid requests; invalid address/control and incomplete request rejected"); $finish;
    end
    initial begin #1000000000; $fatal(1,"AXI global watchdog"); end
endmodule

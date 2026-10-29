`timescale 1ns/1ps
module tb_reader;
    localparam E=96;
    reg clk=0;always #5 clk=~clk;
    reg rst=0,start=0,abort=0;reg [31:0] base=32'hff0;
    wire busy,done,poisoned;wire [31:0] error,araddr,received,stalls;wire [3:0] arlen;
    wire [2:0] arsize;wire [1:0] arburst;wire [5:0] arid;wire arvalid,rready,sv;
    reg arready=0,rv=0,rlast=0,sready=1;reg [63:0] rd=0;reg [1:0] resp=0;reg [5:0] rid=0;
    wire [63:0] sd;
    axi_edge_reader #(.EDGE_COUNT(E),.TIMEOUT_CYCLES(16),.OUTSTANDING(4)) dut(
        .clk(clk),.rst_n(rst),.start(start),.abort(abort),.base_addr(base),.busy(busy),.done(done),.error(error),.poisoned(poisoned),
        .araddr(araddr),.arlen(arlen),.arsize(arsize),.arburst(arburst),.arid(arid),.arvalid(arvalid),.arready(arready),
        .rdata(rd),.rresp(resp),.rid(rid),.rlast(rlast),.rvalid(rv),.rready(rready),.stream_data(sd),.stream_valid(sv),.stream_ready(sready),.received(received),.stall_cycles(stalls));
    integer qs[0:15],ql[0:15],wp=0,rp=0,qn=0,beat=0,sent=0,accepted=0,stream=0,arcount=0,cycle=0;
    integer id=-1,passes=0,maxq=0,watchdog,logfile;reg consumed=0,arheld=0,rheld=0;
    reg [31:0] ha,nextaddr;reg [3:0] hl;reg [63:0] hr;reg hlast;reg [1:0] hresp;reg [5:0] hid;
    always @(posedge clk) begin
        consumed=0;
        if(rst) begin
            cycle=cycle+1;
            if(arheld&&(!arvalid||araddr!==ha||arlen!==hl)) $fatal(1,"pending AR changed case=%0d",id);
            if(rheld&&(!rv||rd!==hr||rlast!==hlast||resp!==hresp||rid!==hid)) $fatal(1,"R test source held");
            arheld=arvalid&&!arready;ha=araddr;hl=arlen;
            rheld=rv&&!rready;hr=rd;hlast=rlast;hresp=resp;hid=rid;
            if(sv&&sready) begin if(sd!==stream||poisoned||abort||resp!=0||rid!=0) $fatal(1,"stream corrupt/poisoned");stream=stream+1;end
            if(rv&&rready) begin
                if(qn==0) $fatal(1,"unsolicited R accepted");
                consumed=1;sent=sent+1;
                if(beat==ql[rp]-1) begin rp=(rp+1)%16;qn=qn-1;beat=0;end else beat=beat+1;
            end
            if(arvalid&&arready) begin
                if(araddr!==nextaddr||arid!=0||arsize!=3||arburst!=1) $fatal(1,"AR sequence/fields");
                if({1'b0,araddr[11:0]}+8*(arlen+1)>4096||accepted+arlen+1>E) $fatal(1,"AR bounds");
                qs[wp]=accepted;ql[wp]=arlen+1;wp=(wp+1)%16;qn=qn+1;
                nextaddr=nextaddr+8*(arlen+1);accepted=accepted+arlen+1;arcount=arcount+1;
            end
            if(dut.queued>4||qn>4) $fatal(1,"too many outstanding");
            if(qn>maxq) maxq=qn;
            if((id==8||id==9||id==11)&&cycle==35&&(!busy||!poisoned||done)) $fatal(1,"timeout must stay busy for undrained transaction");
        end else begin arheld=0;rheld=0;end
    end
    always @(negedge clk) begin
        if(!rst) begin arready=0;rv=0;end
        else begin
            arready=1;sready=1;abort=0;
            if(id==1) begin arready=(cycle%5!=0);sready=(cycle%9<6);end
            if(id==6&&sent>=7) abort=1;
            if(id==7) begin arready=cycle>=12;abort=cycle>=4;end
            if(id==8) arready=cycle>=40;
            if(id==10) sready=cycle>=45;
            if(!rv||consumed) begin
                rv=0;
                if(qn!=0&&!(id==1&&cycle%7<2)&&!((id==9||id==11)&&cycle<40)&&id!=11) begin
                    rv=1;rd=qs[rp]+beat;rlast=(beat==ql[rp]-1);resp=0;rid=0;
                    if(sent==7) begin
                        if(id==2) resp=2;
                        if(id==3) rid=1;
                        if(id==4) rlast=1;
                    end
                    if(id==5&&sent==17) rlast=0;
                end
            end
        end
    end
    task test(input integer case_num,input [31:0] expected_error);
        begin
            @(negedge clk);#1;rst=0;start=0;
            repeat(3) @(negedge clk);#1;
            id=case_num;wp=0;rp=0;qn=0;beat=0;sent=0;accepted=0;stream=0;arcount=0;cycle=0;maxq=0;
            base=(id==12)?32'hff1:((id==13)?32'hffffffe0:32'hff0);nextaddr=base;rst=1;
            @(negedge clk);#1;start=1;@(negedge clk);#1;start=0;watchdog=0;
            while(!done&&watchdog<500&&(id!=11||cycle<90)) begin @(negedge clk);#1;watchdog=watchdog+1;end
            if(id==11) begin if(done||!busy||!poisoned||error!==32'h10||stream!=0) $fatal(1,"wedged timeout semantics");end
            else begin
                if(!done||busy||error!==expected_error||qn!=0||sent!=accepted||arvalid) $fatal(1,"reader case=%0d error=%h expect=%h accepted=%0d sent=%0d",id,error,expected_error,accepted,sent);
                if(expected_error==0) begin
                    if(poisoned||stream!=E||received!=E||accepted!=E||maxq!=4) $fatal(1,"reader successful coverage");
                    if(id==10&&stalls<16) $fatal(1,"missing long local backpressure");
                end else if(!poisoned) $fatal(1,"missing poison");
                if(id==7&&(arcount!=1||stream!=0)) $fatal(1,"pending AR abort must drain exactly pending burst");
                if((id==8||id==9)&&stream!=0) $fatal(1,"timeout leaked data");
                if((id==12||id==13)&&arcount!=0) $fatal(1,"bad base issued AR");
            end
            $fwrite(logfile,"%0d,%h,%0d,%0d,%0d,%0d,%0d\n",id,error,accepted,sent,stream,maxq,stalls);
            $display("READER_PASS case=%0d error=%h accepted=%0d drained=%0d delivered=%0d maxq=%0d",id,error,accepted,sent,stream,maxq);passes=passes+1;
        end
    endtask
    initial begin
        logfile=$fopen("reader_cases.csv","w");$fwrite(logfile,"case,error,accepted_beats,drained_beats,streamed_beats,max_outstanding,stalls\n");
        test(0,0);test(1,0);test(2,32'h2);test(3,32'h4);test(4,32'h8);test(5,32'h8);
        test(6,32'h20);test(7,32'h20);test(8,32'h10);test(9,32'h10);test(10,0);test(11,32'h10);test(12,32'h1);test(13,32'h1);
        $fclose(logfile);$display("READER_ALL_PASS cases=%0d",passes);$finish;
    end
endmodule

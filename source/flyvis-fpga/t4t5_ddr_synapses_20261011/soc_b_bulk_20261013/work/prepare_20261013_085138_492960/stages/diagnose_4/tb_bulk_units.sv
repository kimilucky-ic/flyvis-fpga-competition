`timescale 1ns/1ps
module tb_bulk_units;
 reg clk=0,rst_n=0;always #5 clk=~clk;
 integer checks=0,i,limit,fd;
 function automatic [31:0] value(input integer index);value=index*373-100000;endfunction
 reg ram_we=0,ram_re=0;reg [14:0] ram_wa=0,ram_ra=0;reg [30:0] ram_wd=0;wire [30:0] ram_rd;
 source_state_ram ram(.clk(clk),.we(ram_we),.re(ram_re),.waddr(ram_wa),.raddr(ram_ra),.wdata(ram_wd),.rdata(ram_rd));
 reg ls=0,la=0,ws=0,wa=0;integer lmode=0,wmode=0,ticks=0;
 wire lb,ld,lwe,larv,lrr;wire [31:0] le,lcount,laddr,lidat;wire [15:0] liaddr;
 wire [3:0] llen;wire [2:0] lsize;wire [1:0] lburst;wire [5:0] lid;
 reg larready=0,lrv=0,lrl=0;reg [63:0] lrd=0;reg [1:0] lresp=0;
 ddr_state_loader #(.WORDS(36),.TIMEOUT(32)) loader(.clk(clk),.rst_n(rst_n),.start(ls),.abort(la),.base_addr(32'h10000ff8),
  .busy(lb),.done(ld),.error(le),.words_written(lcount),.in_we(lwe),.in_addr(liaddr),.in_data(lidat),
  .araddr(laddr),.arlen(llen),.arsize(lsize),.arburst(lburst),.arid(lid),.arvalid(larv),.arready(larready),
  .rdata(lrd),.rresp(lresp),.rid(6'd0),.rlast(lrl),.rvalid(lrv),.rready(lrr));
 integer qaddr[0:63],qlen[0:63],qwp=0,qrp=0,qbeat=0,lwrites=0,lreceived=0;
 integer index_word;
 always @(posedge clk)begin
  if(!rst_n)begin ticks<=0;larready<=0;lrv<=0;qwp<=0;qrp<=0;qbeat<=0;lwrites<=0;lreceived<=0;end
  else begin
   ticks<=ticks+1;larready<=ticks%3!=0;
   if(larv&&larready)begin
    if(lid!=0||lsize!=3||lburst!=1||laddr[11:0]+8*(llen+1)>4096)$fatal(1,"Loader AXI geometry");
    qaddr[qwp]<=(laddr-32'h10000ff8)/4;qlen[qwp]<=llen+1;qwp<=qwp+1;
   end
   if(lrv&&lrr)begin
    lrv<=0;lreceived<=lreceived+1;
    if(qbeat==qlen[qrp]-1)begin qrp<=qrp+1;qbeat<=0;end else qbeat<=qbeat+1;
   end
   if(!lrv&&qrp<qwp&&(lmode!=3||ticks>120)&&ticks%4!=0)begin
    index_word=qaddr[qrp]+2*qbeat;
    lrd<={value(index_word+1),value(index_word)};
    if(lmode==1&&index_word==4)lrd<=64'h0000000040000000;
    lresp<=(lmode==2&&index_word==0)?2:0;
    lrl<=qbeat==qlen[qrp]-1;lrv<=1;
   end
   if(lwe)begin
    if(liaddr!=lwrites||lidat!==value(lwrites))$fatal(1,"Loader word order/value %0d",lwrites);
    lwrites<=lwrites+1;
   end
  end
 end
 wire wb,wd,wav,wv,wl,br;wire [31:0] we,wcount,waddr;wire [12:0] oa;reg [31:0] od=0;
 wire [3:0] wlen;wire [63:0] wdata;wire [7:0] wstrb;
 reg awready=0,wready=0,bvalid=0;reg [1:0] bresp=0;reg [5:0] bid=0;
 ddr_candidate_writer #(.WORDS(36),.TIMEOUT(32)) writer(.clk(clk),.rst_n(rst_n),.start(ws),.abort(wa),.base_addr(32'h20000ff8),
  .busy(wb),.done(wd),.error(we),.words_acked(wcount),.out_addr(oa),.out_data(od),
  .awaddr(waddr),.awlen(wlen),.awvalid(wav),.awready(awready),.wdata(wdata),.wstrb(wstrb),.wlast(wl),.wvalid(wv),.wready(wready),
  .bid(bid),.bresp(bresp),.bvalid(bvalid),.bready(br));
 integer wleft=0,windex=0,wwords=0,aw_count=0,b_count=0,bwait=0;
 reg awhold=0,whold=0;reg [35:0] held_aw;reg [72:0] held_w;
 always @(posedge clk)begin
  od<=value(oa);
  if(!rst_n)begin awready<=0;wready<=0;bvalid<=0;wleft<=0;windex<=0;wwords<=0;aw_count<=0;b_count<=0;bwait<=0;awhold<=0;whold<=0;end
  else begin
   awready<=ticks%5!=0&&(wmode!=3||ticks>80);
   wready<=ticks%4!=0&&(wmode!=4||ticks>100);
   if(awhold&&(!wav||{waddr,wlen}!==held_aw))$fatal(1,"AW changed under backpressure/timeout");
   if(whold&&(!wv||{wdata,wstrb,wl}!==held_w))$fatal(1,"W changed under backpressure/timeout");
   awhold=wav&&!awready;held_aw={waddr,wlen};whold=wv&&!wready;held_w={wdata,wstrb,wl};
   if(wav&&awready)begin
    if(wleft!=0||waddr!==32'h20000ff8+wwords*4||waddr[11:0]+8*(wlen+1)>4096)$fatal(1,"Writer address/4K");
    aw_count<=aw_count+1;wleft<=wlen+1;windex<=0;
   end
   if(wv&&wready)begin
    if(wleft==0||wdata!=={value(wwords+1),value(wwords)}||wstrb!=255||wl!==(wleft==1))$fatal(1,"Writer payload/order/last %0d",wwords);
    wleft<=wleft-1;wwords<=wwords+2;windex<=windex+1;
    if(wleft==1)bwait<=(wmode==2)?80:7;
   end
   if(bwait>0)begin
    bwait<=bwait-1;
    if(bwait==1)begin bvalid<=1;bresp<=(wmode==1)?2:0;bid<=(wmode==5)?1:0;end
   end
   if(bvalid&&br)begin bvalid<=0;b_count<=b_count+1;end
  end
 end
 task automatic reset;
  begin @(negedge clk);rst_n=0;ls=0;la=0;ws=0;wa=0;repeat(5)@(negedge clk);rst_n=1;repeat(2)@(negedge clk);end
 endtask
 initial begin #5000000;$fatal(1,"Bounded unit timeout");end
 initial begin
  reset();
  for(i=0;i<16402;i=i+1)begin @(negedge clk);ram_we=1;ram_wa=i;ram_wd=value(i);end
  @(negedge clk);ram_we=0;
  for(i=0;i<16402;i=i+1)begin
   @(negedge clk);ram_re=1;ram_ra=i;
   @(posedge clk);#1;if({ram_rd[30],ram_rd}!==value(i))$fatal(1,"Source RAM split read %0d",i);
  end
  @(negedge clk);ram_re=0;repeat(3)@(posedge clk);checks=checks+1;
  $display("B_BULK_RAM_ALL_16402_PASS");
  for(lmode=0;lmode<4;lmode=lmode+1)begin
   reset();@(negedge clk);ls=1;@(negedge clk);ls=0;limit=0;
   while(!ld&&limit<2000)begin @(posedge clk);#1;limit=limit+1;end
   if(!ld||lb||qrp!=qwp)$fatal(1,"Loader failed to drain mode%0d",lmode);
   if(lmode==0)begin if(le!=0||lcount!=36||lwrites!=36||lreceived!=18||qwp!=3)$fatal(1,"Loader positive counts");end
   else if(le==0)$fatal(1,"Loader failure not detected %0d",lmode);
   if(lmode==3&&lwrites!=0)$fatal(1,"Timeout loader wrote state");
   checks=checks+1;
  end
  for(wmode=0;wmode<7;wmode=wmode+1)begin
   reset();@(negedge clk);ws=1;@(negedge clk);ws=0;limit=0;
   while(!wd&&limit<3000)begin
    @(negedge clk);if(wmode==6&&wwords>=6)wa=1;
    @(posedge clk);#1;limit=limit+1;
   end
   if(!wd||wb||wleft!=0||bvalid||aw_count!=b_count)$fatal(1,"Writer failed drain mode%0d",wmode);
   if(wmode==0)begin if(we!=0||wcount!=36||wwords!=36||aw_count!=3)$fatal(1,"Writer positive count");end
   else if(we==0)$fatal(1,"Writer failure not detected mode%0d",wmode);
   checks=checks+1;
  end
  fd=$fopen("unit_pass.txt","w");$fwrite(fd,"B_BULK_UNITS_PASS cases=%0d source_addresses=16402\n",checks);$fclose(fd);
  $display("B_BULK_UNITS_PASS cases=%0d",checks);$finish;
 end
endmodule

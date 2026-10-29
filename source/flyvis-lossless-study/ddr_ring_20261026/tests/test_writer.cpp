#include "vdut.h"
#include "verilated.h"
#include "ddr_model.hpp"
#include <memory>
#include <iostream>
struct Dut:Vdut { unsigned m_axi_bid=0; using Vdut::Vdut; };
struct Test {
 std::unique_ptr<VerilatedContext> ctx=std::make_unique<VerilatedContext>();
 std::unique_ptr<Dut> ptr; DdrModel mem{8192,2};uint64_t cyc=0;unsigned pubs=0;
 Test(){ctx->threads(1);ptr=std::make_unique<Dut>(ctx.get());auto&d=*ptr;
 d.reset=1;d.cfg_valid=0;d.begin_valid=0;d.release_valid=0;d.input_valid=0;d.state_valid=0;d.info_valid=0;
 for(int i=0;i<4;i++)tick();d.reset=0;tick();}
 void tick(){auto&d=*ptr;ck(++cyc<200000,"unit watchdog");d.clk=0;mem.drive(d,cyc);d.eval();if(!d.reset)mem.sample(d,cyc);d.clk=1;d.eval();if(d.publish)pubs++;}
 void cfg(uint32_t first=0,bool short_end=false){auto&d=*ptr;d.cfg_base=DdrModel::BASE;d.cfg_end=DdrModel::BASE+(short_end?8192:16384);d.cfg_slots=2;d.cfg_first_frame=first;d.cfg_cookie=0x11a0cafe;d.cfg_valid=1;tick();d.cfg_valid=0;tick();}
 void ack(unsigned seq,unsigned cookie=0x11a0cafe){auto&d=*ptr;d.release_sequence=seq;d.release_cookie=cookie;d.release_valid=1;tick();d.release_valid=0;tick();}
 void start(){auto&d=*ptr;ck(d.begin_ready,"no credit");d.begin_valid=1;tick();d.begin_valid=0;}
 void payload(unsigned k){auto&d=*ptr;for(unsigned i=0;i<7;i++){while(!d.input_ready)tick();d.input_valid=1;d.input_bits=0x3f000000+k*256+i;tick();d.input_valid=0;}
 for(unsigned i=0;i<257;i++){while(!d.state_ready)tick();d.state_valid=1;d.state_id=i;d.state_bits=0x3e000000+k*512+i;d.state_last=i==256;tick();d.state_valid=0;}
 d.info_cycles=2199975;d.info_edges=17;d.info_states=257;d.info_faults=0;d.info_valid=1;tick();d.info_valid=0;}
 void finish(unsigned n){while(ptr->committed_count<n){ck(!ptr->error_flags,"unexpected writer error");tick();}tick();}
};
int main(int argc,char**argv)try{
 ck(argc>1,"out");unsigned cases=0;
 {Test t;t.cfg();auto&d=*t.ptr;
 for(unsigned k=0;k<8;k++){
 t.start();if(k==0)t.mem.hold_header_b=true;t.payload(k);
 if(k==0){while(!(t.mem.pending&&t.mem.header))t.tick();for(int i=0;i<20;i++){t.tick();ck(d.committed_count==0&&t.pubs==0,"published before final B");}t.mem.hold_header_b=false;}
 t.finish(k+1);std::vector<uint32_t> a,b;for(unsigned i=0;i<7;i++)a.push_back(0x3f000000+k*256+i);for(unsigned i=0;i<257;i++)b.push_back(0x3e000000+k*512+i);
 t.mem.verify(k%2,k,257,17,a,b);
 if(k%2){ck(d.capacity_exhausted&&!d.begin_ready,"full credit");auto saved=t.mem.mem;d.begin_valid=1;for(int j=0;j<20;j++)t.tick();d.begin_valid=0;ck(t.mem.mem==saved&&d.committed_count==k+1,"full overwrote");t.ack(k+1);t.ack(k+1);ck(d.released_count==k+1&&d.begin_ready,"ACK credit/idempotence");}
 }ck(t.pubs==8,"publication count");cases++;}
 {Test t;t.cfg(0,false);auto&d=*t.ptr;t.start();t.payload(0);t.finish(1);auto before=t.mem.mem;t.ack(2);ck(d.error_flags&32,"future ACK not rejected");ck(d.released_count==0&&!d.begin_ready&&t.mem.mem==before,"bad ACK freed record");cases++;}
 {Test t;t.cfg();auto&d=*t.ptr;t.ack(0,123);ck(d.error_flags&32,"cookie reject");cases++;}
 {Test t;t.cfg(0,true);ck(t.ptr->error_flags&8,"full ring allocation bounds");ck(!t.ptr->configured,"short allocation admitted");cases++;}
 {Test t;t.cfg();auto&d=*t.ptr;t.start();t.mem.inject_error=true;for(unsigned i=0;i<7;i++){d.input_valid=1;d.input_bits=i;t.tick();}d.input_valid=0;while(!d.error_flags)t.tick();ck(d.error_flags&2,"BRESP error");ck(!d.committed_count&&!t.pubs&&!d.begin_ready,"published failed burst");cases++;}
 {Test t;t.cfg();auto&d=*t.ptr;t.start();t.mem.hold_aw=true;for(unsigned i=0;i<7;i++){d.input_valid=1;d.input_bits=i;t.tick();}d.input_valid=0;while(!d.error_flags)t.tick();ck((d.error_flags&4)&&d.m_axi_awvalid,"timeout withdrew AW");for(int i=0;i<10;i++)t.tick();t.mem.hold_aw=false;for(int i=0;i<100;i++)t.tick();ck(!d.committed_count&&!t.pubs&&!d.begin_ready,"timeout published");cases++;}
 {Test t;t.cfg(0xfffffffe);auto&d=*t.ptr;for(unsigned k=0;k<2;k++){t.start();t.payload(k);t.finish(k+1);}t.ack(2);ck(!d.begin_ready&&d.capacity_exhausted,"frame counter wrapped and reused identity");cases++;}
 std::ofstream f(std::string(argv[1])+"/summary.json");f<<"{\"status\":\"PASS_RING_WRITER_DIRECTED_RTL_CPU_ONLY\",\"cases\":"<<cases<<",\"wrap_records\":8,\"board_operations\":0}\n";std::cout<<"PASS writer cases="<<cases<<std::endl;
}catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}

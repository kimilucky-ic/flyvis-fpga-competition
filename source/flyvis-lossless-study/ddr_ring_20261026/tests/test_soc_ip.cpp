#include "vdut.h"
#include "verilated.h"
#include "ddr_model.hpp"
#include <iostream>
#include <memory>
extern "C" void fp32_environment();
extern "C" uint32_t fp32_add(uint32_t,uint32_t);
extern "C" uint32_t fp32_mul(uint32_t,uint32_t);
struct Edge{uint16_t s,t;uint32_t w;};static_assert(sizeof(Edge)==8,"edge layout");
int main(int argc,char**argv)try{
    ck(argc>1,"output directory");std::string out=argv[1];fp32_environment();
    const std::string vectors="../rtl_behavior_20261013/vectors/initial32/";
    auto edges=load<Edge>(vectors+"edges.bin");auto a=load<uint32_t>(vectors+"initial.bin");
    auto stim=load<uint32_t>(vectors+"stimulus.bin");
    auto frozen=load<uint32_t>("../preboard_20261018/bundle_r1/expected_state1.bin");
    std::ifstream file("../hole_pipeline_20261016/images/meta.hex");std::vector<uint32_t> meta;uint32_t q;
    while(file>>std::hex>>q)meta.push_back(q);
    ck(a.size()==45669&&edges.size()==1513231&&meta.size()==7663&&stim.size()>=1442,"full frozen dimensions");
    std::vector<std::vector<uint32_t>> gold,inputs;
    for(unsigned step=0;step<5;++step){
        unsigned offset=step==1?721:0;inputs.emplace_back(stim.begin()+offset,stim.begin()+offset+721);
        std::vector<uint32_t> c(a.size(),0);
        for(auto e:edges){uint32_t rel=(a[e.s]&0x80000000)?0:a[e.s];c[e.t]=fp32_add(c[e.t],fp32_mul(rel,e.w));}
        for(unsigned t=0;t<65;++t){
            unsigned base=meta[32+4*t]&65535,n=meta[32+4*t]>>16;bool input=(meta[33+4*t]>>24)&1;
            for(unsigned j=0;j<n;++j){unsigned id=base+j;uint32_t r=fp32_add(a[id]^0x80000000,meta[7468+3*t]);
                r=fp32_add(r,c[id]);r=fp32_add(r,input?inputs.back()[j]:0);
                r=fp32_mul(meta[7470+3*t],r);r=fp32_mul(r,0x3ba3d70a);a[id]=fp32_add(a[id],r);}
        }gold.push_back(a);
    }
    ck(gold[0]==frozen,"first oracle state differs from accepted original");
    auto ctx=std::make_unique<VerilatedContext>();ctx->threads(1);ctx->commandArgs(argc,argv);
    auto model=std::make_unique<Vdut>(ctx.get());auto& d=*model;
    constexpr unsigned STRIDE=188416;DdrModel mem(STRIDE,2);mem.w_period=2;
    uint64_t cycle=0,axi_reads=0,axi_writes=0,rejections=0,held_read_cycles=0;
    bool hold_read=false;uint32_t held_read_value=0;
    auto tick=[&](){
        ck(cycle<16000000,"SoC-IP watchdog");d.aclk=0;mem.drive(d,cycle);d.eval();
        if(d.aresetn){
            if(hold_read){ck(d.s_axi_rvalid&&d.s_axi_rdata==held_read_value&&d.s_axi_rresp==0,"R changed while reader stalled");++held_read_cycles;}
            mem.sample(d,cycle);
        }
        d.aclk=1;d.eval();++cycle;
    };
    d.aresetn=0;d.s_axi_awvalid=0;d.s_axi_wvalid=0;d.s_axi_bready=0;d.s_axi_arvalid=0;d.s_axi_rready=0;
    d.s_axi_awprot=0;d.s_axi_arprot=0;
    for(int j=0;j<4;++j)tick();d.aresetn=1;tick();
    auto write=[&](uint32_t addr,uint32_t data,unsigned order=2,unsigned expected=0,unsigned strb=15){
        d.s_axi_awaddr=addr;d.s_axi_wdata=data;d.s_axi_wstrb=strb;
        if(order==0){d.s_axi_awvalid=1;tick();d.s_axi_awvalid=0;tick();d.s_axi_wvalid=1;tick();d.s_axi_wvalid=0;}
        else if(order==1){d.s_axi_wvalid=1;tick();d.s_axi_wvalid=0;tick();d.s_axi_awvalid=1;tick();d.s_axi_awvalid=0;}
        else{d.s_axi_awvalid=1;d.s_axi_wvalid=1;tick();d.s_axi_awvalid=0;d.s_axi_wvalid=0;}
        unsigned t=0;while(!d.s_axi_bvalid){tick();ck(++t<30,"GP0 B timeout");}
        ck(d.s_axi_bresp==expected,"GP0 BRESP");
        for(int j=0;j<2;++j){tick();ck(d.s_axi_bvalid&&d.s_axi_bresp==expected,"GP0 B hold");}
        d.s_axi_bready=1;tick();d.s_axi_bready=0;++axi_writes;if(expected)++rejections;
    };
    auto read=[&](uint32_t addr,unsigned expected=0){
        d.s_axi_araddr=addr;d.s_axi_arvalid=1;tick();d.s_axi_arvalid=0;
        unsigned t=0;while(!d.s_axi_rvalid){tick();ck(++t<30,"GP0 R timeout");}
        auto data=d.s_axi_rdata;ck(d.s_axi_rresp==expected,"GP0 RRESP");
        for(int j=0;j<2;++j){tick();ck(d.s_axi_rvalid&&d.s_axi_rdata==data&&d.s_axi_rresp==expected,"GP0 R hold");}
        d.s_axi_rready=1;tick();d.s_axi_rready=0;++axi_reads;return data;
    };
    ck(read(0x30)==45669&&read(0x34)==1513231&&read(0x38)==0x00110005&&read(0x3c)==STRIDE,"independent ABI/scope");
    write(0,1,0,2);write(0,4,1,2);write(0,8,2,2);read(0x3fc,2);
    write(0,2);while(read(0x10)&1){}ck(read(0x10)&2,"restored initial state");
    write(4,DdrModel::BASE);write(8,DdrModel::BASE+2*STRIDE);write(12,2);
    write(0x1c,0);write(0x2c,0x11a0cafe);write(0,4);ck(read(0x10)&4,"configured");
    write(4,DdrModel::BASE,0,2); // frozen session configuration
    for(unsigned k=0;k<5;++k){
        unsigned first=0;
        if(k==0){
            write(0x400,inputs[k][0]);first=1;write(0,1,0,2); // partial frame
            write(0x400,inputs[k][0],0,2); // duplicate index
            write(0x404,inputs[k][1],1,2,1); // partial WSTRB
            ck(read(0x18)==1&&read(0x14)==0,"rejected input changed admission");
        }
        for(unsigned j=first;j<721;++j)write(0x400+4*j,inputs[k][j],j%3);
        ck(read(0x18)==721&&read(0x40)==k,"fresh complete input / expected next frame");
        write(0,1);ck(read(0x10)&1,"start did not establish busy");
        write(0x400,0x7f800000,0,2);write(0,1,1,2);write(0,2,2,2);
        if(k==1){
            // A slow PS reader holds the old coherent descriptor response
            // through a complete neural/DDR publication; no RREADY feedback.
            d.s_axi_araddr=0x088;d.s_axi_arvalid=1;tick();d.s_axi_arvalid=0;
            while(!d.s_axi_rvalid)tick();ck(d.s_axi_rdata==0,"prior latched frame");
            held_read_value=d.s_axi_rdata;hold_read=true;
            while(mem.header_ok<2)tick();for(int j=0;j<6;++j)tick();
            hold_read=false;d.s_axi_rready=1;tick();d.s_axi_rready=0;++axi_reads;
        }
        while(read(0x14)<k+1){}while(read(0x10)&1){}
        if(k)ck(read(0x80)==k,"latched publication changed without LATCH command");
        write(0,8);ck(read(0x80)==k+1&&read(0x84)==DdrModel::BASE+(k%2)*STRIDE&&read(0x88)==k,"atomic publication descriptor");
        ck(read(0x90)==k+1&&read(0x94)==0x11a0cafe&&read(0x98)==0,"descriptor count/cookie/faults");
        ck(read(0x9c)==45669&&read(0xa0)==1513231,"descriptor network scope");
        mem.verify(k%2,k,45669,1513231,inputs[k],gold[k]);
        ck(read(0x8c)==mem.u32((k%2)*STRIDE+32),"latched compute cycle binding");
        if(k)mem.verify((k-1)%2,k-1,45669,1513231,inputs[k-1],gold[k-1]);
        if(k>=1 && k<4){
            ck(read(0x10)&8,"full before durable ACK");auto saved=mem.mem;
            write(0,1,0,2);for(int j=0;j<40;++j)tick();
            ck(mem.mem==saved&&read(0x14)==k+1,"full cannot advance/overwrite");
            write(0x44,k);write(0x48,0x11a0cafe);write(0,16);
            ck(read(0x4c)==k&&read(0x50)==1&&!(read(0x10)&8),"durable prefix releases exactly one credit");
            write(0,16);ck(read(0x4c)==k,"duplicate ACK idempotent");
        }
        ck(read(0x24)==0,"engine error");
        std::cout<<"PASS step="<<k<<" complete states=45669 input=721 descriptor_seq="<<k+1<<std::endl;
    }
    ck(read(0x10)&8,"journal full");auto preserved=mem.mem;
    for(unsigned j=0;j<721;++j)write(0x400+4*j,inputs[0][j]);
    write(0,1,0,2);for(int j=0;j<100;++j)tick();
    ck(read(0x14)==5&&mem.mem==preserved,"capacity overwrite or sixth neural step");
    write(0x44,6);write(0,16,0,2); // future ACK
    write(0x44,2);write(0,16,0,2); // regressed ACK
    write(0x44,5);write(0x48,0xdeadbeef);write(0,16,0,2); // foreign session
    ck(read(0x4c)==3&&mem.mem==preserved,"invalid ACK released/changed record");
    write(0x48,0x11a0cafe);write(0,16);ck(read(0x4c)==5&&read(0x50)==0,"final release");
    ck(read(0x28)==rejections,"rejected write counter");ck(held_read_cycles>2000000,"long reader stall was not exercised");
    std::ofstream bytes(out+"/ddr_records.bin",std::ios::binary);bytes.write((char*)mem.mem.data(),mem.mem.size());bytes.close();
    std::ofstream summary(out+"/summary.json");
    summary<<"{\"status\":\"PASS_RING_FULL_NETWORK_FIVE_STEPS_CPU_RTL_ONLY\",\"completed_steps\":5,\"nodes\":45669,\"edges_per_step\":1513231,\"state_words_checked\":228345,\"input_words_checked\":3605,\"state_mismatches\":0,\"self_feedback_transitions\":4,\"AXI_reads\":"<<axi_reads<<",\"AXI_writes\":"<<axi_writes<<",\"rejected_writes\":"<<rejections<<",\"reader_stall_cycles\":"<<held_read_cycles<<",\"DDR_bursts\":"<<mem.aw_count<<",\"simulated_cycles\":"<<cycle<<",\"board_operations\":0}\n";
    std::cout<<"PASS SoC-IP full network steps=5 held_reader_cycles="<<held_read_cycles<<std::endl;d.final();return 0;
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<std::endl;return 1;}

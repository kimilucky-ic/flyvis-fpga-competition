#pragma once
#include <cstdint>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>
inline void ck(bool ok,const std::string& msg){if(!ok)throw std::runtime_error(msg);}
template<class T> std::vector<T> load(const std::string& path){
    std::ifstream f(path,std::ios::binary|std::ios::ate);ck(bool(f),"open "+path);
    auto size=f.tellg();ck(size>=0&&size%sizeof(T)==0,"binary shape");std::vector<T> v(size/sizeof(T));
    f.seekg(0);f.read((char*)v.data(),size);ck(bool(f),"binary read");return v;
}
inline uint32_t rolling(const std::vector<uint32_t>& v){uint32_t h=0;for(unsigned i=0;i<v.size();++i)h=((h<<1)|(h>>31))^v[i]^i;return h;}
struct DdrModel{
    static constexpr uint32_t BASE=0x10000000;
    unsigned stride;std::vector<uint8_t> mem;
    bool active=false,pending=false,hold_aw=false,hold_w=false,hold_b=false,hold_header_b=false;
    bool inject_error=false;unsigned w_period=5;uint64_t response_at=0,aw_count=0,w_count=0,b_count=0,header_ok=0;
    uint32_t address=0;unsigned length=0,index=0;bool header=false;
    bool held_aw=false,held_w=false;uint32_t held_address=0;unsigned held_len=0;
    uint64_t held_data=0;unsigned held_strb=0;bool held_last=false;
    explicit DdrModel(unsigned stride_,unsigned slots):stride(stride_),mem(stride_*slots,0xa5){}
    template<class D>void drive(D& d,uint64_t cycle){
        d.m_axi_awready=!active&&!pending&&!hold_aw&&(cycle%7!=0);
        d.m_axi_wready=active&&!hold_w&&(w_period==1||cycle%w_period==1);
        d.m_axi_bvalid=pending&&!hold_b&&!(header&&hold_header_b)&&cycle>=response_at;
        d.m_axi_bresp=inject_error?2:0;d.m_axi_bid=0;
    }
    template<class D>void sample(D& d,uint64_t cycle){
        if(held_aw)ck(d.m_axi_awvalid&&d.m_axi_awaddr==held_address&&d.m_axi_awlen==held_len,"AW changed/withdrawn under stall");
        if(held_w)ck(d.m_axi_wvalid&&d.m_axi_wdata==held_data&&d.m_axi_wstrb==held_strb&&bool(d.m_axi_wlast)==held_last,"W changed/withdrawn under stall");
        held_aw=d.m_axi_awvalid&&!d.m_axi_awready;held_address=d.m_axi_awaddr;held_len=d.m_axi_awlen;
        held_w=d.m_axi_wvalid&&!d.m_axi_wready;held_data=d.m_axi_wdata;held_strb=d.m_axi_wstrb;held_last=d.m_axi_wlast;
        if(d.m_axi_awvalid&&d.m_axi_awready){
            ck(!active&&!pending,"one outstanding transaction");address=d.m_axi_awaddr;length=d.m_axi_awlen+1;index=0;
            ck(length<=16&&d.m_axi_awsize==3&&d.m_axi_awburst==1,"AXI burst profile");
            ck((address&4095)+8*length<=4096,"4KiB crossing");
            ck(address>=BASE&&uint64_t(address-BASE)+8*length<=mem.size(),"write outside reserved DDR");
            active=true;header=((address-BASE)%stride)==0;++aw_count;
        }
        if(d.m_axi_wvalid&&d.m_axi_wready){
            ck(active,"W without AW");ck(bool(d.m_axi_wlast)==(index+1==length),"WLAST count");
            unsigned offset=address-BASE+index*8;
            for(unsigned b=0;b<8;++b)if(d.m_axi_wstrb&(1u<<b))mem[offset+b]=d.m_axi_wdata>>(8*b);
            ++index;++w_count;
            if(index==length){active=false;pending=true;response_at=cycle+3+(cycle%5);}
        }
        if(d.m_axi_bvalid&&d.m_axi_bready){
            ck(pending,"B without outstanding write");pending=false;++b_count;
            if(header&&!inject_error)++header_ok;
        }
    }
    uint32_t u32(unsigned offset)const{
        ck(offset+4<=mem.size(),"DDR read bounds");uint32_t v=0;for(unsigned b=0;b<4;++b)v|=uint32_t(mem[offset+b])<<(8*b);return v;
    }
    void verify(unsigned slot,unsigned fid,unsigned n,unsigned ne,const std::vector<uint32_t>& input,const std::vector<uint32_t>& state){
        unsigned p=slot*stride;
        ck(u32(p)==0x5331314c&&u32(p+4)==0x10000&&u32(p+8)==fid&&u32(p+12)==0,"committed header identity");
        ck(u32(p+16)==n&&u32(p+20)==ne&&u32(p+24)==input.size()*4&&u32(p+28)==n*4,"record scope");
        ck(u32(p+36)==ne&&u32(p+40)==n&&u32(p+44)==stride,"record counts/stride");
        ck(u32(p+48)==rolling(input)&&u32(p+52)==rolling(state),"record rolling checksums");
        ck(u32(p+56)==128&&u32(p+60)==4096&&u32(p+64)==0x00110005&&u32(p+68)==0x3ba3d70a,"record profile");
        ck(u32(p+80)==fid+1&&u32(p+84)==0x11a0cafe,"ring sequence/cookie");
        for(unsigned j=0;j<input.size();++j)ck(u32(p+128+4*j)==input[j],"all DDR input words");
        for(unsigned j=0;j<n;++j)ck(u32(p+4096+4*j)==state[j],"all DDR state words");
        if(n%2)ck(u32(p+4096+4*n)==0xa5a5a5a5,"state odd tail strobe overwrote padding");
        if(input.size()%2)ck(u32(p+128+4*input.size())==0xa5a5a5a5,"input odd tail strobe overwrote padding");
    }
};

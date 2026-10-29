// Serial ordered-edge strict-FP32 oracle; no RTL, GPU or board dependency.
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>
extern "C" void fp32_environment();
extern "C" uint32_t fp32_add(uint32_t,uint32_t);
extern "C" uint32_t fp32_mul(uint32_t,uint32_t);
struct Edge{uint16_t s,t;uint32_t w;};static_assert(sizeof(Edge)==8,"frozen layout");
template<class T>std::vector<T> read(const std::string&p){
    std::ifstream f(p,std::ios::binary|std::ios::ate);if(!f)throw std::runtime_error(p);
    auto n=f.tellg();if(n%sizeof(T))throw std::runtime_error("size");std::vector<T> v(n/sizeof(T));
    f.seekg(0);f.read(reinterpret_cast<char*>(v.data()),n);if(!f)throw std::runtime_error("read");return v;
}
void save(std::ofstream&f,const std::vector<uint32_t>&v){f.write(reinterpret_cast<const char*>(v.data()),v.size()*4);if(!f)throw std::runtime_error("write");}
int main(int argc,char**argv)try{
    if(argc!=4)throw std::runtime_error("bundle input.bin output.bin");std::string r=argv[1];fp32_environment();
    auto e=read<Edge>(r+"/edges.bin");
    auto a=read<uint32_t>(r+"/initial_state.bin");
    auto x=read<uint32_t>(argv[2]);
    std::ifstream mf(r+"/meta.hex");std::vector<uint32_t> m;uint32_t z;
    while(mf>>std::hex>>z)m.push_back(z);
    if(e.size()!=1513231||a.size()!=45669||m.size()!=7663||x.empty()||x.size()%721||x.size()>3*721)throw std::runtime_error("full dimensions");
    std::ofstream gold(argv[3],std::ios::binary);
    for(unsigned k=0;k<x.size()/721;++k){
        unsigned off=k*721;std::vector<uint32_t> input(x.begin()+off,x.begin()+off+721),c(45669,0);
        for(auto edge:e){auto rel=(a[edge.s]&0x80000000)?0:a[edge.s];c[edge.t]=fp32_add(c[edge.t],fp32_mul(rel,edge.w));}
        for(unsigned t=0;t<65;++t){
            unsigned base=m[32+4*t]&65535,n=m[32+4*t]>>16;bool sensory=(m[33+4*t]>>24)&1;
            for(unsigned j=0;j<n;++j){unsigned id=base+j;
                auto v=fp32_add(a[id]^0x80000000,m[7468+3*t]);v=fp32_add(v,c[id]);
                v=fp32_add(v,sensory?input[j]:0);v=fp32_mul(m[7470+3*t],v);v=fp32_mul(v,0x3ba3d70a);a[id]=fp32_add(a[id],v);
            }
        }
        save(gold,a);std::cout<<"oracle step="<<k<<" nodes=45669 edges=1513231 strict_fp32=1\n";
    }return 0;
}catch(const std::exception&ex){std::cerr<<ex.what()<<'\n';return 1;}

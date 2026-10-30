// Host-only independent scoreboard reference. Never linked via DPI to the DUT.
#include <cstdint>
#include <cstring>
#include <cfenv>
#include <limits>
#include <xmmintrin.h>
static_assert(sizeof(float)==4 && std::numeric_limits<float>::is_iec559,"IEEE binary32 host required");
extern "C" void fp32_environment() {
    std::fesetround(FE_TONEAREST);
    _mm_setcsr(_mm_getcsr() & ~((1u<<15)|(1u<<6))); // no FTZ, no DAZ
}
extern "C" uint32_t fp32_add(uint32_t x,uint32_t y) {
    float a,b;std::memcpy(&a,&x,4);std::memcpy(&b,&y,4);
    volatile float r=a+b;float v=r;uint32_t out;std::memcpy(&out,&v,4);return out;
}
extern "C" uint32_t fp32_mul(uint32_t x,uint32_t y) {
    float a,b;std::memcpy(&a,&x,4);std::memcpy(&b,&y,4);
    volatile float r=a*b;float v=r;uint32_t out;std::memcpy(&out,&v,4);return out;
}

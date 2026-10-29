/* Fixed complete-network payload validation; integer only, no neural math. */
#include <stddef.h>
#include <stdint.h>
#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif
API uint32_t line11_payload_abi(void) { return UINT32_C(0x12110001); }
static uint32_t check(const unsigned char *p, size_t count, uint32_t *bad) {
    uint32_t h=0;
    for (size_t i=0; i<count; ++i,p+=4) {
        uint32_t w=(uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
        h=((h<<1)|(h>>31)) ^ w ^ (uint32_t)i;
        *bad |= ((w & UINT32_C(0x7f800000)) == UINT32_C(0x7f800000));
    }
    return h;
}
API int line11_payload_check(const unsigned char *raw,size_t length,uint32_t *out) {
    if (!raw || !out || length!=188416) return -1;
    uint32_t bad=0;
    out[0]=check(raw+128,721,&bad);
    out[1]=check(raw+4096,45669,&bad);
    out[2]=bad;
    return 0;
}

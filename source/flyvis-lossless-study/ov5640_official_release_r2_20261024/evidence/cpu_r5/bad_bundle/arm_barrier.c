/* Future PYNQ/Zynq-7000 CPU helper. Not compiled or executed on a board here. */
#if !defined(__arm__) || !defined(__ARM_ARCH) || __ARM_ARCH < 7
#error This helper requires the ARMv7 target compiler
#endif
void line11_dsb(void) { __asm__ volatile("dsb sy" ::: "memory"); }

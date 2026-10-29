#include "vdut.h"
#include "verilated.h"
#include <vector>
#include <stdexcept>
#include <iostream>
Vdut d;
std::vector<unsigned> pixels;
void check(bool ok,const char* s){if(!ok)throw std::runtime_error(s);}
void tick(){d.cam_pclk=0;d.eval();if(d.cmos_frame_ce&&d.cmos_active_video)pixels.push_back(d.cmos_frame_data);d.cam_pclk=1;d.eval();}
void clocks(int n){while(n--)tick();}
void reset(){d.rst_n=1;clocks(3);d.rst_n=0;d.cam_pclk=0;d.eval();check(!d.cmos_frame_ce,"async reset failed");clocks(3);d.rst_n=1;clocks(4);check(!d.cmos_frame_ce,"warmup missing");}
void vs(){d.cam_vsync=1;clocks(4);d.cam_vsync=0;clocks(4);}
void byte(unsigned b){d.cam_href=1;d.cam_data=b;tick();}
void blank(){d.cam_href=0;clocks(5);}
int main(){try{
 d.rst_n=1;d.cam_href=0;d.cam_vsync=0;d.cam_data=0;reset();
 for(int i=0;i<10;i++){vs();check(!d.cmos_frame_ce,"early warmup");}vs();
 pixels.clear();byte(0xf8);byte(0x00);byte(0x07);byte(0xe0);blank();
 check(pixels==std::vector<unsigned>({0xf80000,0x00fc00}),"RGB565 or first/last pixel mismatch");
 pixels.clear();byte(0xff);blank();byte(0x00);byte(0x1f);blank();
 check(pixels==std::vector<unsigned>({0x0000f8}),"odd byte crossed line boundary");
 byte(0xff);reset();d.cam_href=0;clocks(4);for(int i=0;i<11;i++)vs();pixels.clear();
 byte(0xff);byte(0xff);blank();check(pixels==std::vector<unsigned>({0xf8fcf8}),"reset recovery");
 std::cout<<"PASS_DVP_RTL_RESET_WARMUP_RGB565_LINE_BOUNDARY_RECOVERY\n";return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}

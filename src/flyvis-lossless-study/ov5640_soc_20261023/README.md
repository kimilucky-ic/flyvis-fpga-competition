# OV5640独立采集及SoC接入候选 — 2026-10-23

当前状态：初始化CPU验证和独立DVP RTL仿真通过；SoC源码接入完成但未由Vivado验证、综合或实现。未上板，未启动GPU或摄像头。旧版目录未修改。

## 初始化来源及移植

在用户官方资料`4_Source_Code/2_Embedded_Vitis/ZYNQ_Vitis_7020.rar`中定位`27_ov5640_lcd/vitis/ov5640_lcd/src/ov5640/ov5640_init.c`及SCCB源码，只提取4个文件共19,889字节。原始文件、版权及SHA保留在vendor/与SOURCE_IDENTITY.json，供内部工程参考，不视为公开再发布许可。

sensor_init.py使用注入的读写接口，先延时20ms，按原顺序读取0x300b/0x300a并检查0x5640；保留原软件复位及1ms等待，再完成248次写入。没有自动连接或设备导入。实际AXI IIC驱动必须处理7位地址0x3c、16位寄存器地址、写/读长度检查、NACK及超时；其硬件绑定尚未完成，不能直接把本函数视作可执行板端驱动。

test_init.py把原C初始化函数单独编译并注入记录接口，与Python移植逐事件比较：640×480、总周期1800×1000的252项读/写/延时事件完全一致。错误ID零写入，首笔写入失败立即停止且不重试。INIT_RESULT.json、init_trace.txt为证据。源码注释写24MHz输入、72MHz PCLK，但该模式的实际频率、物理模块时钟、输出方向/色序仍待核验；不据此宣称摄像头帧率。原驱动含自动曝光、白平衡、Gamma等设置，实验必须记录，不可当成无图像处理的传感器原始数据。

## DVP最小修复及仿真

rtl/cmos_capture_data.v保留官方接口和原始编码，只有两处功能修改：

- 重复的第二条rst_n_d0清零改为rst_n_syn清零。
- byte_flag_d0有效条件改为cam_href && byte_flag，只有收到完整两字节才发布像素。原实现遇到奇数长度行会发布旧像素。

sim_r1/保留奇数字节测试失败；sim_r2/通过复位、11次VSYNC预热门控、RGB565红绿蓝白、首尾像素、奇数长度行丢弃未成对字节、下行重新对齐、半像素中途复位及恢复。使用现成Windows Verilator和单进程g++，编译22.719秒、仿真0.375秒。未启动Vivado。没有重新跑不变的全网神经回归；其证据按源码身份复用。

该模块仍只是字节/视频前端，不是完整帧完整性监控器。不应让不完整帧进入STEP：后续必须验证VDMA完成/错误状态、分辨率/行长度及缓冲所有权。未测试真实PCLK、I/O延迟、亚稳态或厂商异步桥。

## SoC源码接入

prepare_soc.tcl基于已通过DDR SoC构建脚本；camera_extension.tcl新增DVP前端、异步video-in、仅S2MM的24位流/64位存储VDMA、AXI IIC及HP1。原神经HP0路径及GP0神经接口保持。所有9个原RTL/参考文件身份见NEURAL_SOURCE_IDENTITY.json。FP32和完整网络不变，神经/AXI目标仍100MHz。

脚本仅准备BD和生成包装源，不含综合、布局布线或BIT生成；本轮没有执行该脚本。新增IP端口/参数、自动地址分配、复位极性、未用端口/中断及跨时钟连接需要Vivado校验，当前不能宣称可综合或时序通过。相机使用独立HP口仍共享DDR，不能宣称零竞争。

camera_pins_reference.xdc来自官方示例，只保留camera引脚，不自动载入、不复制CLOCK_DEDICATED_ROUTE FALSE豁免。实物底板版本、PCLK约束和输入延迟未确认，不允许凭当前源脚本生成可上板交付。神经BRAM初始化文件在旧hole_pipeline_20261016/images，后续构建需按原流程冻结并放到构建目录。

PS预处理复用ov5640_prepare_20261023的已验证NumPy原型；它与Torch在容差内但不逐位一致。所有神经全状态验收必须使用实际保存的721项输入位串。PC只显示；记录满、相机/DDR/初始化故障应停止，不重试或重置。

下一步：完成AXI IIC实际API适配和采集缓冲所有权接口的CPU模拟，再在获准的Vivado窗口内运行新BD校验、综合及100MHz实现。需要实物底板/摄像头时钟参数才能完成物理约束；当前没有新BIT/HWH，也没有ARM、真实采集或实板性能证据。

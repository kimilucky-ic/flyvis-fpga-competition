# 候选⑪ OV5640 单帧离线发布包（2026-10-23）

本包是离线准备结果，EXECUTION_AUTHORITY=NONE。当前任务没有上板；不要因为收到ZIP就直接执行加载。完整45669节点/1513231连接、连续值严格FP32与100MHz未变。相机版来自 ov5640_reset_20261023/build_r7 的同一已通过布线DCP和同构建HWH；未重综合/重布线。原始来源与哈希见release_info.json、original_model_provenance.json和release_manifest.json。

## 当前可安全运行的默认入口

在有Python和NumPy的电脑解压后运行 `python -B offline_check.py`，检查文件、BIT容器、同名HWH、芯片、100MHz、HP0/HP1、VDMA和地址映射。`python -B board_capture.py`同样只做离线检查。默认入口不会导入PYNQ、分配板端DDR或访问硬件。Windows x86-64的reference.exe仅用于电脑CPU事后验收；不在ARM板端运行它。

## 日后获准上板时的一次准备与一次运行

1. 由用户确认独占板卡、当前加载工程及其他任务都可中断，并逐项核对下方实物条件。将conditions.json复制到包目录外，填入实物底板版本及真实确认结果；不要修改封存模板，不要把未知项批量设为true。第一次缺少时序测量时，只能由用户明确接受文件所列条件预算，不能写成测量通过。
2. 由用户把完整包解压到板端Jupyter目录，在同一Notebook内导入board_capture，读取外部已确认条件JSON，然后仅调用一次：

```python
import json
from board_capture import run
conditions = json.load(open('/home/xilinx/jupyter_notebooks/conditions_confirmed.json'))
result_dir = run('/home/xilinx/jupyter_notebooks', conditions,
                 authorize_load_and_one_step=True)
```

此调用属于真实硬件操作，必须另行获得当次授权。本轮没有运行它。它会编译ARM内存屏障帮助函数、加载一次本包BIT、检查时钟和新鲜ABI、初始化OV5640、分配并保留互不重叠的DDR、采集一帧、保存实际721项输入后执行一次PL STEP、保存完整DDR记录及45669状态，并生成_RESULT.zip。传感器初始化包含官方一次软件复位；它不是失败后的恢复重试。最终只打印“已保存、待CPU参考验收”，不会提前报全状态PASS。

3. 把_RESULT.zip交回电脑，在本包目录执行 `python -B verify_run.py RESULT.zip NEW_AUDIT_DIRECTORY`，或交给当前任务验收。它用此次实际input.bin进行独立串行严格FP32推导，比对全部45669个32位状态、721输入、记录帧号/步号/周期和帧来源哈希。成功产生ACCEPTANCE.json；失败保留FAILED.json及实际记录。基准输入不是旧录像或旧刺激。

任何异常后保持Notebook内核与DDR分配存活；不要重复运行、关闭内核、重载、复位或释放缓冲。程序不自动重试/复位/回退。即使保存成功，当前实现也保留两块分配，等待CPU验收及明确的后续处置。不是持续运行服务，也不提供自动回滚旧BIT；旧版始终独立保留。

## 上板前必须核实的时钟和接口条件

- **实物与接线**：正点原子领航者ZYNQ-7020，芯片应为XC7Z020-2CLG400；记录真实底板版本。当前引脚来自官方V3.9资料，只有确认实物引脚一致才可用。排线方向、接口3.3V及共地必须正确。完整引脚在camera_pins_and_budget.xdc；PCLK=W14、HREF=T12、VSYNC=U12、RST_N=P14、PWDN=V15、SCL=T10、SDA=T11；D[0..7]=R14/U13/V13/U15/U14/W13/V12/Y14。
- **相机时钟来源**：本候选不输出XCLK；需要确认模块自带24MHz晶振并实际工作。不能仅凭“OV5640”芯片名称推定晶振存在。官方初始化以该时钟为基础，目标PCLK72MHz。每次启动仍有11次VSYNC预热，2秒有界等待不是实时帧率保证。
- **相机外部时序**：按0x4740=0x20的下降沿更新数据、PL上升沿采样，条件预算输入延迟-0.5..2ns、建立/保持不确定度0.25/0.10ns。实际PCLK频率/占空比/抖动、传感器tCO、排线与板级偏斜仍需验证。W14非专用时钟引脚的CLOCK_DEDICATED_ROUTE例外保留；“实现通过”不等于该电气接口实测通过。
- **PS参考和FCLK**：物理PS参考33.333333MHz。加载后保存IO_PLL_CTRL、PLL_STATUS、FPGA0_CLK_CTRL；要求IO PLL锁定、不在复位/掉电/旁路，FDIV=30、两级分频5和2，名义FCLK=33.333333×30÷5÷2≈100MHz。PYNQ若误用50MHz参考可能显示150MHz，因此同时保存PYNQ读数与原始寄存器，绝不盲改时钟。寄存器推导不叫频率测量。
- **SCCB/IIC**：7位地址0x3C，AXI IIC100kHz，传感器ID0x5640；SCL/SDA有正确电压的上拉，核实实际并联上拉和总线负载。现有V3.9资料为4.7kΩ/3.3V，但实物必须核对；传感器要求的上升/下降时间不应超过300ns。保留异步输入同步器与两项no_input_delay标记；内部输出20ns预算不替代外部SCCB波形验证。逐次MMIO调用本身必须返回，软件超时不能终止AXI总线挂死。
- **像素模式与顺序**：RGB565、640×480；readback检查PLL/分频、0x4300=0x61、0x501f=1、0x4740和尺寸。视频IP扩展为24位RGB，DDR流按低字节优先预计为BGR；conditions中显式记录选择。要用色条核实色序、行列方向及图像质量；未做色条时只可宣称数学状态比对，不能宣称相机视觉语义已确认。
- **PS/PL/DDR**：PYNQ2.7、ARMv7、NumPy及本机cc/gcc。HP0和HP1实际PS配置必须为64位；HWH为64位不自动证明当前启动镜像正确配置。神经控制0x43C40000/4KiB，采集GPIO0x41200000、IIC0x41600000、VDMA0x43000000。加载后必须新鲜空闲、计数/错误为0。程序不修改PS DDR初始化和HP宽度，不使用硬编码DDR缓冲地址。
- **缓存与存储**：PYNQ allocate实际分配神经188416B、相机3×921600B，共约2.82MiB，页对齐且物理范围不重叠。CPU先清零flush+ARM dsb，PL持有后CPU只读；完成后invalidate+dsb再复制。至少32MiB结果空间；不允许环形覆盖未验收神经记录。ARM帮助函数编译、CMA和cache行为尚未在该候选实板验证。

## 验收数据与证据级别

bound/000000包含原始source_frame.bin、实际input.bin、PREPARED.json（先于STEP落盘）、DDR record.bin、actual_input.bin、actual_state.bin和绑定收据。RUN_CONTEXT记录包身份、boot_id、条件；另存时钟寄存器、传感器读回、DDR分配与失败阶段。时间戳是PS发起采集时刻，不是曝光时间。显示不参与此次一步验收；不丢神经步或输入记录。

PS预处理为NumPy固定417视场与721感受野映射，与原Torch不是逐位等价。电脑复算映射允许原先验证的3e-6绝对误差；神经参考始终使用实际保存输入bits，所有状态要求逐位完全一致。严格参考保留边序、有效权重bits、每次binary32 RNE加/乘、无FMA/FTZ/DAZ与原Euler顺序。ABI没有独立初态读回：只能检查restore-clean标记与全部更新后状态，不假称实测初态比较。

reference.exe是从已验证的参考代码小改输入接口后生成，并重新与既有3步137007状态逐位核对；它独立于RTL，不调用GPU。新相机画面的CPU模拟流程是软件证据，不等于PL在板上算过。本包没有光流decoder、训练或PC神经推理主循环。

## 来源与保留边界

本地私有工程包，未公开发布。FlyVis来源与版本见original_model_provenance.json。OV5640寄存器表来自正点原子官方Vitis相机示例；vendor_ov5640_init.c/h保留原署名，解析结果为init_actions.json。AMD IP模型/实现结果仅作当前器件工程交付，不附带整套工具或模拟器库。

PLL核对依据AMD UG585：
https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Register-PLL_STATUS-Details
https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Enable-PLL-Mode-when-PLL-Bypass-Mode-Pin-is-Tied-High

本候选保持旧版独立，回退需用户另行授权选择旧版，不能自动恢复板卡。未新增通用Skill：ARM/实物流程尚未复现。

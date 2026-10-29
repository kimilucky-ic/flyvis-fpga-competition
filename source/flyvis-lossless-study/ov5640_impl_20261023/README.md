# OV5640完整网络SoC：有界IIC、单帧VDMA与实现核验

日期2026-10-23。用户授权CPU验证后运行独立Vivado设计校验、综合、布局布线；不操作实体板卡。完整45669节点/1513231边、严格FP32、神经100MHz要求保持。原神经SV逐文件SHA核验见NEURAL_IDENTITY.json；旧候选未编辑。最终实现结果由FINAL_RESULT.json及build_r4/release报告决定，不能以本说明或CPU PASS代替。

## 有界接口

bounded_io.py新增直接MMIO的IIC动态主机事务：7位0x3c地址、START/STOP、16位寄存器地址、FIFO就绪、NACK/仲裁丢失、总线完成检查。所有软件轮询同时受单事务deadline与max_polls限制，不再调用PYNQ可能无限等待的C发送/接收函数。单次MMIO本身必须能返回；如果PS总线访问本身硬挂起，Python无法中断，这不是相机NACK/clock-stretch超时。失败锁定、不重试、不复位。接口要求一个调用者独占；尚未连接实物。

OneFrameVdma采用固定640x480 RGB888、1920字节行跨度、每帧921600字节。每次只从已有CapturePool获得一个可写租约；三个VDMA帧地址槽均指向这一租约，park模式、frame-count=1，最后写VSIZE启动。必须同时观察帧完成状态和HALTED后，才调用显式cache invalidate/barrier/不可变拷贝后端并发布到CapturePool。正在被PS持有的缓冲不会再次授予。所给物理范围必须来自真实分配，排除神经日志范围、相互重叠和越界。超时/错误保留WRITING租约，不自动释放或重置。

这是首版按需单帧采集，未宣称连续无间隙摄像；停采期间的帧可能被前端跳过或积压。真实视频前端溢出、VDMA重启帧对齐、相机字节顺序、cache行为和帧时间戳需后续独立实板验收。现有输入绑定实现仍负责保存每个已选帧及721项实际输入，PC显示不参与采集租约。

CPU_RESULT.json/CPU.log：6项CPU寄存器模型测试通过，覆盖动态读写协议、NACK/仲裁丢失/忙总线/事务停滞、截止时间和轮询预算、DMA完成但未HALTED时不可读、持有缓冲排除、错误/超时保留租约、范围重叠拒绝。没有神经计算或实体MMIO。上阶段12项输入绑定测试按源码身份复用。

## Vivado版本及边界

实际Vivado2026.1.1 SW6605303，完整flyvis_ddr_wrapper，xc7z020clg400-2。适配本机Video In5.0和AXI IIC2.1，VDMA6.3；旧示例4.0/2.0不可直接实例化。build_r1为脚本策略启动失败；r2保留旧视频IP缺失；r3保留旧端口名和只读参数错误；r4为修正后的独立候选。沙箱安装脚本访问失败后按已有用户授权提升工具执行，未改变系统策略；仅子进程使用ExecutionPolicy Bypass。

BD实际地址：神经0x43C40000/4KiB、相机VDMA0x43000000/64KiB、IIC0x41600000/64KiB。神经HP0和相机HP1都64位100MHz，仍共享PS DDR，并非无竞争。HWH审计见IP_PARAMETER_AUDIT.json：24位视频流、3帧槽、S2MM-only、帧计数器启用、IIC100kHz。

相机约束是**条件性工程预算**：依据官方初始化源码注释取PCLK72MHz，数据/同步输入延迟预算0至6.944444ns；不是实测板级时序。保留官方W14非专用时钟路由例外，在综合检查点中的实际cam_pclk_IBUF网上重新施加并检查对象唯一性。早期综合解析时曾找不到该网络的警告保留，不能删除日志掩盖。外部IIC时序、传感器PCLK实测及底板版本必须单独落实。即使内部100MHz通过也不代表相机端到端时序/实时运行通过。

脚本有单线程、时间和内存保护；原始日志、工具版本、参数、地址图、检查点及报告保留。没有生成新BIT或上板。SOURCES.json保存寄存器参考来源和复现命令。物理运行前还须验证完整状态oracle、缓存顺序、相机帧完整性及错误恢复边界；当前不提供自动板端入口。

## 最终核验结果

build_r4综合、build_r5从同一综合DCP重新布局布线。首轮r4布线失败仅两条复位同步器CLR恢复路径，WNS-2.643ns；保留失败报告。r5只为两级相机复位同步器设置ASYNC_REG并对两只CLR设置精确false-path，不切数据路径、不改神经RTL。最终内部100MHz WNS+0.202ns/WHS+0.064ns/WPWS+3.870ns；建立/保持/脉宽违规均0；21043/21043网络布线，0路由错误；CDC5个端点Safe、0Unsafe/Unknown/缺ASYNC_REG；FIFO总线偏斜裕量9.324/9.056ns。

最终资源9963LUT、10632FF、109BRAM36等效、2DSP，相对旧DDR SoC7531/7092/102/2增加2432LUT、3540FF、7BRAM、0DSP。完整神经源保持字节身份，不重新宣称全网数值仿真通过。

**最终状态ROUTED_INTERNAL_100MHZ_PASS_CAMERA_SIGNOFF_INCOMPLETE。** DRC0Error/0CriticalWarning，但14Warning+2Advisory；特别保留PLCK-12非专用PCLK路由、3项REQP-1839（capture byte_flag_d0/cam_href_d1/wait_done异步复位控制驱动视频FIFO BRAM使能）待处理。check_timing另有IIC两输入/两输出缺延迟约束；其余检查项0。不把“所有已指定约束满足”写成“所有接口签核完成”。复位同步例外仅解决异步跨域恢复检查，未消除上述BRAM异步控制警告。

综合210.953秒/峰值3306.96MiB，最终实现228.422秒/峰值2198.21MiB，无资源保护停止，进程已结束。BASELINE_AFTER记录1689旧封存成员全部一致。MANIFEST封存本候选输入/日志/报告/检查点，不包括可再生成IP缓存。

下一具体动作：独立修复采集输出控制的复位方式并补充视频FIFO复位/溢出/重启帧完整性RTL验证，再按实物时钟与IIC总线参数完成外部约束。当前不生成BIT、不提供上板入口；需要这些缺口关闭后再推进上板准备。

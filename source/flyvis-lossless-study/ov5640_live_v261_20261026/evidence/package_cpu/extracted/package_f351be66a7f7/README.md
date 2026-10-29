# 官方 OV5640 + 完整 FlyVis：周期检查修正版 R2

此包目标为领航者 ZYNQ-7020 / xc7z020clg400-2、PYNQ2.7，保留完整45669节点/1513231连接、严格FP32及100MHz设计。仅适用于此前跑通官方摄像头的同一板卡和接口。官方采集模式800x480，神经计算完全由PL完成，PS仅负责采集管理、721项输入映射和状态保存。

板端上传单文件 LINE11_OFFICIAL_FULL_R2_20261024.ipynb，在独立新内核运行唯一代码格。先确保之前的官方摄像头已正常关闭、没有其他程序使用板卡、接口和供电未变。无需先运行旧测试或手动装载BIT。提示时输入“运行官方完整网络”，一次授权加载新固件、采一帧、算一步和正常关闭相机。下载打印的 RUN_*_RESULT.zip 交回电脑核查。

完成提示只表示原始记录保存，不表示数值PASS。保留Notebook内核及神经DDR缓冲区；不重复运行、不手动删attempt标记、不复位或加载其他工程。出错后也不做自动清理。若官方同步驱动阻塞，保留最后阶段输出，不以反复运行尝试恢复。

完整状态验收：在Windows电脑进入本包，运行 `python verify_result.py RESULT.zip NEW_AUDIT_DIRECTORY`。独立顺序边FP32参考程序使用本次真实721项输入与冻结初态，逐uint32比较全部45669状态。程序不会执行ZIP中的代码，不连接板卡。对操作者交回的记录验收通过仍不等于独立观察了硬件运行。

文件检查：`python offline_check.py`，只检查本地文件，不访问硬件。Notebook已嵌入整个包，不需要另外上传ZIP/BIT/HWH。

限制：PS图像映射不是Torch逐位一致性声明；神经数值验收以保存的实际输入为准。BGR顺序未经色条实测；FCLK来自PS寄存器及33.333333MHz名义参考推导，PYNQ显示150MHz可能源于50MHz参考假设。DVP72MHz外部预算、W14非专用时钟引脚例外、IIC/LCD外部约束与普通DRC/CDC告警尚未形成电气签核。新固件ARM驱动/VDMA/cache/HP1须由此次独立实板验收确认；当前无新实板PASS、无实时帧率或功耗结论。

来源：官方正点原子OV5640/PYNQ视频采集路径和驱动；IIC2.1登记适配，Video In5.0，以及独立候选中的最小采集复位修复。原官方源码版权说明保留；FlyVis来源见 original_model_provenance.json 和 upstream_flyvis_license.txt。路由来源和BIT/HWH哈希见release_info.json；成功旧版不被覆盖。

R2修复：DDR核心阶段预期为2199975周期；原2201418为旧MMIO计数。CYCLE_CHECK.json保存实际值/预期值/口径，失败也保留PUBLICATION.json。旧会话收尾使用单独close_current_session.py，勿在旧内核重跑本入口。

# 果蝇生物视觉神经回路的 FPGA 硬件模拟

本仓库主分支只保留最新完整系统：45,669个模型神经元、1,513,231条连接、721项视觉输入，FP32/Euler状态递推。PL执行完整神经计算，PS负责摄像头输入与DDR记录，电脑展示神经活动与官方光流读出。

## 从这里开始

- **运行实验：**[board/runtime](board/runtime/README.md)。Windows x64、Python3.12、原有Zynq-7020/PYNQ2.7板端环境。先安装requirements，再运行 `python run.py --check-only`；实际实验按说明生成并运行固定Notebook。
- **查看硬件：**[src/neural](src/neural/README.md) 是最终8个神经计算RTL模块及50个初始化/映射数据文件。[src/vendor](src/vendor/README.md) 保留匹配构建要求的56项摄像头与平台依赖，原版权声明保留。
- **构建固件：**[build/portable](build/portable/README.md)，使用Vivado2026.1。已有BIT/HWH直接随运行包提供。
- **报告和海报：**[设计报告](report/design_report.pdf)、[海报PDF](report/poster_en_a4.pdf)、[可编辑海报](report/poster_en.pptx)、[技术说明](report/technical_report.md)。
- **研发过程：**[协作案例](report/ai_engineering_cases.md)包含两组真实短原文与两组明确标记的工程摘要；[14个Skill](skill/README.md)连同经验和验证依据保留。

![Competition poster](report/poster_preview.png)

## 目录

`src/` 最新RTL、参数与必需平台源文件；`board/` 当前运行程序、固件、软件参考和保存样例；`build/` 构建脚本与资源时序报告；`sim/` 验证记录；`data/` 参考样例；`report/` 报告、海报与协作材料；`skill/` 全部14项技能及案例。

当前运行代码、固件和参考样例在精简中保持原字节。神经RTL仅从build/portable/neural集中到src/neural，构建准备脚本相应调整查找路径。摄像头平台依赖逐项匹配vendor_requirements.json。清单见public_manifest.json；整理映射见[保留范围](report/current_delivery_inventory.json)。

## 验证范围

保留的1090步操作者实验记录对应49,779,210个保存状态值、零失配；它是既有实板证据。软件自检重新计算保存的721项输入与45,669个状态值。模型5ms时间步与实测运行速度分别说明。FPGA功耗为Vivado估算，GPU为设备域遥测，原获取方法与范围保留。

本次目录精简不启动GPU、摄像头、Vivado或板卡。构建文件准备与软件参考检查可独立验证；新机器从源文件到BIT的完整Vivado重建仍需实际执行。

## 完整研发历史

[完整研发归档分支](https://github.com/kimilucky-ic/flyvis-fpga-competition/tree/archive/full-development-before-slim)保留精简前全部文件，包括67节点、A/B路线、旧GUI和实验版本。历史证据中的旧路径从归档分支查看。主分支不再混入这些旧实现、工具缓存或重复网表。旧提交与本地实验未删除，Git历史未重写。需要只下载当前内容可用GitHub的Code → Download ZIP。

许可与第三方范围见[声明](third_party_notices.md)及[平台依赖说明](build/vendor_dependency_review.md)。保留原声明不等于将第三方代码改为本项目许可证。

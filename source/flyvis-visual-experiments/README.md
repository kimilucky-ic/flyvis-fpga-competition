# FlyVis 原始模型追加实验

本目录是 2026-10-09 的独立实验交付，使用已经安装的 WSL CPU/GPU 环境。没有修改队友打包目录、原始 FlyVis 源码、官方 checkpoint 或此前验收数据；所有活动均来自原完整视觉网络的软件仿真。

- [技术报告](docs/flyvis_experiments_report.md)：结果、数值容差、耗时、内存、纠错记录和未解决项。
- [交接清单](handoff.json)：提供给另一边打包工作只读引用。
- [Golden Reference v2](artifacts/golden_reference_v2/)：24 条件固定输入的 CPU/GPU 活动、T4/T5 CSV/NPY、方向指标、元数据与哈希。
- [功能验收](artifacts/functional_acceptance.json)：逐项 PASS / FAIL / NOT_RUN，光流整体 PARTIAL。
- [展示素材](artifacts/analysis/)：方向、ON/OFF、速度、热力图、实际解码矢量和预录制 GIF。
- [边界数据](artifacts/boundary_cuda_r1/)：T4c/T5c 各四组原始完整网络轨迹，连接参数、初态与跨界输入。
- [本任务检查点](../docs/workstreams/flyvis-visual-experiments.md)。

## 环境和运行

现有 WSL 发行版是 `FlyVisCPU`；CPU Python `/opt/flyvis-venv/bin/python`，GPU Python `/opt/flyvis-gpu-venv/bin/python`。新缓存为 `/opt/flyvis-visual-experiments-data`，必须保留 Linux 原生文件系统位置。没有安装步骤。

在 PowerShell 调用下列脚本，依次传阶段、设备、未使用的重复编号。已有 `result.json` 的目录会拒绝覆盖；新的重复编号才执行新的进程复算。

```powershell
wsl -d FlyVisCPU -- bash /mnt/c/Users/hzy72/Documents/ChatGPT/fpga/flyvis-visual-experiments/scripts/run_phase.sh minimal cuda 2
wsl -d FlyVisCPU -- bash /mnt/c/Users/hzy72/Documents/ChatGPT/fpga/flyvis-visual-experiments/scripts/run_phase.sh flash cuda 2
wsl -d FlyVisCPU -- bash /mnt/c/Users/hzy72/Documents/ChatGPT/fpga/flyvis-visual-experiments/scripts/run_phase.sh bar cuda 2
wsl -d FlyVisCPU -- bash /mnt/c/Users/hzy72/Documents/ChatGPT/fpga/flyvis-visual-experiments/scripts/run_phase.sh decoder cuda 4
```

每个阶段 240 秒上限，日志与条件结果单独保存。不要同时启动两个重型渲染或仿真；CPU 渲染和 GPU 推理都会占用主机资源。MovingBar 中断时已完成的条件保留，尚未完成的条件可以在同一尚无最终 `result.json` 的目录续跑。完整中断恢复不是本轮独立测试项。

`cross_cpu` / `cross_gpu` 包含固定输入推理对照和历史独立 CPU 渲染输入对照。后者已经确认失败，因此复合阶段会保留 FAIL 并退出 2；其同输入推理对照本身通过，正式拆分验收见 `artifacts/fixed_input_acceptance.json`。不要把失败记录改成 PASS，也不要将独立渲染等价视为已经证明。

`bar_replay cpu` 对 `bar_cuda_r1` 的十组保存输入复算；`boundary cuda` 从完整网络提取边界数据。解码器必须递归 `eval()`，不能只依赖本版官方 `simulation()` 的父模块标志。

## 展示和证据范围

已接受的解码结果来自 `decoder_cpu_r2` 和 `decoder_cuda_r3`。`decoder_cpu_r1`、`decoder_cuda_r1` 是未递归关闭 Dropout/BatchNorm 的失败结果；`decoder_cuda_r2` 虽然使用正确 eval，但旧脚本仍拿失败的训练模式输出作比较，所以其复合 FAIL 记录也保留，不能当作交接验收入口。

GIF 是预录制原始软件仿真回放；图和 CSV 不代表实时视频分析、真实生物测量、FPGA 仿真或板上执行。光流仅验证原预训练解码器在合成刺激上的功能及复算，尚无真实标注数据 EPE 验收。

新增的解码器工作流记录在 [项目 Skill](../.agents/skills/flyvis-decoder-inference/SKILL.md)。本目录没有创建或修改队友运行包。

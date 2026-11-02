# FlyVis CPU 软件基准

当前已通过的阶段：官方预训练单模型的 **flash demo + Golden Reference v1**。四组刺激的活动经过重新加载权重、绕过缓存重算，逐位一致，最大误差为 0。

2026-10-09 已追加通过 **最小 Moving Edge CPU 实验（方案 A）**：0°/180° 两个方向、ON 单种亮度、每组 485 帧，保存全部 65 类中心细胞和 T4/T5 八类活动。独立进程绕过响应缓存复算，输入和活动逐位一致，最大误差为 0。

- 最小实验报告：[docs/flyvis_moving_edge_minimal_report.md — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-078)。
- 展示用 JSON：[demo_payload.json — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-079)。
- 数据与验收：[artifacts/moving_edge_minimal_cpu_v1](artifacts/moving_edge_minimal_cpu_v1)。
- 本工作线检查点：[docs/workstreams/flyvis-baseline.md — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-080)。

重现最小实验：`./scripts/run_minimal_moving_edge.ps1`；独立复算：`./scripts/run_minimal_moving_edge.ps1 -ReplayOnly`。冷刺激构建需串行安排，避免与同一 WSL 中其他重型渲染同时运行。该实验只验证两个 ON 条件，不计算完整 DSI，也没有导出 FPGA 子回路内部和边界状态。

完整验收报告：[docs/flyvis_baseline_report.md — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-081)。

- 数据：[artifacts/golden_reference_v1/flash — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-082)。
- 验收边界：[milestone.json — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-083)。
- 原始网络和权重身份：[network.json — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-084)。
- 候选区域只读分析：[candidate_circuits.json — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-085)。

运行环境为 WSL2 的 `FlyVisCPU`，Python 环境 `/opt/flyvis-venv`，原模型和 HDF5 缓存 `/opt/flyvis-data`。虚拟磁盘保存在本项目 `.wsl/ubuntu/ext4.vhdx`，无需重新下载即可重跑。Windows 原生和 Windows 共享盘的 HDF5 缓存均未通过验收。

在本项目 PowerShell 中重现已验收实验：

```powershell
.\scripts\run_baseline.ps1 -Experiment flash -Verify
```

默认也只运行 flash。完整 24 条件的移动边缘 CPU 扫描此前停止并留存日志；新增最小实验的验收仅覆盖两个 ON 条件。完整方向扫描、OFF 条件、moving-bar/motion 和 Sintel 光流不属于本方案 A 的验收范围。当前软件基准工作没有 FPGA 设计、RTL 修改、训练、剪枝或 LIF 替换。

官方源码：[TuragaLab/flyvis](https://github.com/TuragaLab/flyvis)，固定 commit `92b3845cc426dd309a1a0e1b3890156c42e14021`，跟踪源码未修改。

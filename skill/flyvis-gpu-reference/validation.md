# 冻结官方FlyVis参考与CPU/GPU比较：证据与适用边界

核对日期：2026-10-21。这里审核历史文件，不表示今天重跑了工程。

## 已验证效果／观察

既有RTX5060Laptop/torch2.7.1cu128案例：三张渲染逐位一致；flash最大误差1.4305e-6，独立GPU重复一致。

证据类型：HISTORICAL_CASE_RECORD_NOT_FRESH_SKILL_REUSE。
适用范围、前提和失效条件见 [操作正文](skill.md)；下面的输入模板可换成本队契约和合法数据使用。

## 随包材料

- [gpu](../evidence/originals/gpu.json): byte_exact_original, source SHA-256 `af098fe8482fe972430bbff673baf053d0c7f746f718efd93de875d9009d7b0c`.
- [gpu_report](../evidence/originals/gpu_report.txt): byte_exact_original, source SHA-256 `bca068eed073ab01de40fcfa027d2b9b34dccf6a8d9fb6c189ed852bc55e3aa9`.
- [gpu_corrections](../evidence/originals/gpu_corrections.txt): byte_exact_original, source SHA-256 `29664b0ccacf0a388be0665b7c8a127f2db9c2cff32c54b5b97018f949a7bf97`.

原始位置、字节数、原始hash与包内hash见 [来源清单](../evidence/source_manifest.json)。.txt/.log保存原报告字节；报告中的旧路径、旧“待办”和链接属于当时记录，并非本包执行入口或当前状态。大报告摘要明确标注派生，不冒充完整原证据。

## 缺少的验证材料

缺干净安装复现及不同GPU/所有刺激覆盖；checkpoint、输入和大数组不随包。不能把特定算子快照作为完整端到端速度。

所有14项都没有在本次文档修订中完成陌生队伍从零复用；格式/文件hash检查不代替这种效果验证。

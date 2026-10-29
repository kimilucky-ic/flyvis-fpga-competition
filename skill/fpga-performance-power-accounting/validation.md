# 同工作量分母、计时边界、功耗域与积分：证据与适用边界

核对日期：2026-10-21。这里审核历史文件，不表示今天重跑了工程。

## 已验证效果／观察

GPU17460步、43.607秒、域平均66.749W、166.709mJ/步；计数器低7.52%。FPGA报告明确vectorless估算，无实板能耗。

证据类型：HISTORICAL_CASE_RECORD_NOT_FRESH_SKILL_REUSE。
适用范围、前提和失效条件见 [操作正文](skill.md)；下面的输入模板可换成本队契约和合法数据使用。

## 随包材料

- [power_gpu](../evidence/originals/power_gpu.json): byte_exact_original, source SHA-256 `f6ee3dcf814d006ce80afcf5c17ea42a32e41c41e23b7cfeca5dac499291f75f`.
- [power_fpga](../evidence/originals/power_fpga.json): byte_exact_original, source SHA-256 `60be688a1fd14e69a62ece9034a9ca7967cfcfc8414b7a552fa5910888eaee98`.

原始位置、字节数、原始hash与包内hash见 [来源清单](../evidence/source_manifest.json)。.txt/.log保存原报告字节；报告中的旧路径、旧“待办”和链接属于当时记录，并非本包执行入口或当前状态。大报告摘要明确标注派生，不冒充完整原证据。

## 缺少的验证材料

缺同任务同边界的板级能耗/时延测量及外部校准；因此比较性节能结论未验证。现有GPU遥测原CSV未随包。

所有14项都没有在本次文档修订中完成陌生队伍从零复用；格式/文件hash检查不代替这种效果验证。

# PYNQ网页、kernel、overlay、AXI/DMA逐层判断：证据与适用边界

核对日期：2026-10-21。这里审核历史文件，不表示今天重跑了工程。

## 已验证效果／观察

历史两神经元256→0→1级联，ID/weight及计数吻合；原记录保留首次重载偏离约束及之后未重载复测。

证据类型：HISTORICAL_CASE_RECORD_NOT_FRESH_SKILL_REUSE。
适用范围、前提和失效条件见 [操作正文](skill.md)；下面的输入模板可换成本队契约和合法数据使用。

## 随包材料

- [board](../evidence/originals/board.txt): byte_exact_original, source SHA-256 `29773185893b2639b6e93ec0a8be8b065c96de3a5b7825c579415b1dd1475d0e`.

原始位置、字节数、原始hash与包内hash见 [来源清单](../evidence/source_manifest.json)。.txt/.log保存原报告字节；报告中的旧路径、旧“待办”和链接属于当时记录，并非本包执行入口或当前状态。大报告摘要明确标注派生，不冒充完整原证据。

## 缺少的验证材料

缺独立陌生使用者复用记录；原Notebook完整输出未随包保存。跨题/跨板通用性未验证。

所有14项都没有在本次文档修订中完成陌生队伍从零复用；格式/文件hash检查不代替这种效果验证。

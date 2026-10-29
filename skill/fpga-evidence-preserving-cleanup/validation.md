# 依赖审计、生成物可恢复性与保留证据：证据与适用边界

核对日期：2026-10-21。这里审核历史文件，不表示今天重跑了工程。

## 已验证效果／观察

历史五项派生物清理后8164保留文件、84旧数组检查通过；恢复结果all_exact=true，无神经推理。

证据类型：HISTORICAL_CASE_RECORD_NOT_FRESH_SKILL_REUSE。
适用范围、前提和失效条件见 [操作正文](skill.md)；下面的输入模板可换成本队契约和合法数据使用。

## 随包材料

- [cleanup](../evidence/originals/cleanup.json): byte_exact_original, source SHA-256 `172db89148cba53692c50360abaf14a1bb93817657edd03f3846e1f1f6ddd429`.
- [cleanup_recovery](../evidence/originals/cleanup_recovery.json): byte_exact_original, source SHA-256 `4406d9da2d7fb6f61316ea0a7e4ebcc18bc386de9a6ff5f95d0b781a0edf9cd7`.

原始位置、字节数、原始hash与包内hash见 [来源清单](../evidence/source_manifest.json)。.txt/.log保存原报告字节；报告中的旧路径、旧“待办”和链接属于当时记录，并非本包执行入口或当前状态。大报告摘要明确标注派生，不冒充完整原证据。

## 缺少的验证材料

包内附最终/恢复结果，未附完整恢复源片段与逐文件前后hash清单；不可据此删除陌生项目。独立恢复演练未做。

所有14项都没有在本次文档修订中完成陌生队伍从零复用；格式/文件hash检查不代替这种效果验证。

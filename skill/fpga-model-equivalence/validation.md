# 生产RTL契约、首个差异与证据等级：证据与适用边界

核对日期：2026-10-21。这里审核历史文件，不表示今天重跑了工程。

## 已验证效果／观察

保留生产PQN与测试DSSN区别的历史记录；所附MaleCNS XSim原日志记录11定向检查及1200步golden一致。

证据类型：HISTORICAL_CASE_RECORD_NOT_FRESH_SKILL_REUSE。
适用范围、前提和失效条件见 [操作正文](skill.md)；下面的输入模板可换成本队契约和合法数据使用。

## 随包材料

- [model_report](../evidence/originals/model_report.txt): byte_exact_original, source SHA-256 `5157ee003f4dba12506fd6226f73e261e0229708fad1f63625e38405644c54dc`.
- [quant_xsim](../evidence/originals/quant_xsim.log): byte_exact_original, source SHA-256 `c5bd81d7807096b473973157ac7e8d3edbbeefb143e51a5331a1e7fea9356f58`.

原始位置、字节数、原始hash与包内hash见 [来源清单](../evidence/source_manifest.json)。.txt/.log保存原报告字节；报告中的旧路径、旧“待办”和链接属于当时记录，并非本包执行入口或当前状态。大报告摘要明确标注派生，不冒充完整原证据。

## 缺少的验证材料

包内未包含整个fly数值比较程序、原始长输入和全状态轨迹；不构成fly原网络或所有IEEE输入等价证明。独立套用未做。

所有14项都没有在本次文档修订中完成陌生队伍从零复用；格式/文件hash检查不代替这种效果验证。

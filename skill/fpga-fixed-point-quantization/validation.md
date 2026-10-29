# 定点扫宽、冻结读出、范围界与RTL向量：证据与适用边界

核对日期：2026-10-21。这里审核历史文件，不表示今天重跑了工程。

## 已验证效果／观察

321节点7590边四种子扫宽报告；12bit正号场景迁移80.8%对浮点80.1%，完整向量仅约32%；另有11/1200项RTL仿真原日志。

证据类型：HISTORICAL_CASE_RECORD_NOT_FRESH_SKILL_REUSE。
适用范围、前提和失效条件见 [操作正文](skill.md)；下面的输入模板可换成本队契约和合法数据使用。

## 随包材料

- [quantization](../evidence/originals/quantization.txt): byte_exact_original, source SHA-256 `1a5064a35e84e7db5187858872c5ee28a93b7e064c3c7b38ebd350551815c2ba`.
- [quant_vectors](../evidence/originals/quant_vectors.txt): byte_exact_original, source SHA-256 `667e68fd7e94f985bd450bf4a902df5586f1d29b9a7d6bf076cac89f76331f02`.
- [quant_xsim](../evidence/originals/quant_xsim.log): byte_exact_original, source SHA-256 `c5bd81d7807096b473973157ac7e8d3edbbeefb143e51a5331a1e7fea9356f58`.

原始位置、字节数、原始hash与包内hash见 [来源清单](../evidence/source_manifest.json)。.txt/.log保存原报告字节；报告中的旧路径、旧“待办”和链接属于当时记录，并非本包执行入口或当前状态。大报告摘要明确标注派生，不冒充完整原证据。

## 缺少的验证材料

缺量化候选的综合/实板证据；递质极性未定。完整图/生成器/向量未打入轻量Skill包，须在具体工程取得合法输入。

所有14项都没有在本次文档修订中完成陌生队伍从零复用；格式/文件hash检查不代替这种效果验证。

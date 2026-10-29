# 原始解码器递归eval与参数/buffer不变性：证据与适用边界

核对日期：2026-10-21。这里审核历史文件，不表示今天重跑了工程。

## 已验证效果／观察

纠正父模块false但Dropout等仍training的问题；修正后CPU/GPU最大差9.2983e-6、GPU重复逐位一致、状态不变。

证据类型：HISTORICAL_CASE_RECORD_NOT_FRESH_SKILL_REUSE。
适用范围、前提和失效条件见 [操作正文](skill.md)；下面的输入模板可换成本队契约和合法数据使用。

## 随包材料

- [decoder_cpu](../evidence/originals/decoder_cpu.json): byte_exact_original, source SHA-256 `773af2c39cc8d00d6c98cd6b42248da9bc1beccc97d45aeea5e518d5c0a22512`.
- [decoder_gpu](../evidence/originals/decoder_gpu.json): byte_exact_original, source SHA-256 `3d4be11cfe223b11051e743b087933f906fc462ca257e781c6d2e9fbe06349fa`.
- [decoder_report](../evidence/originals/decoder_report.txt): byte_exact_original, source SHA-256 `65816a5d9adde90bc49313979a552eef5120e7751a46bf73f9254e6123c79542`.

原始位置、字节数、原始hash与包内hash见 [来源清单](../evidence/source_manifest.json)。.txt/.log保存原报告字节；报告中的旧路径、旧“待办”和链接属于当时记录，并非本包执行入口或当前状态。大报告摘要明确标注派生，不冒充完整原证据。

## 缺少的验证材料

缺陌生checkpoint/decoder独立复用及自然视频校准；原脚本/模型权重/输出数组不随包，绝对速度单位和生物行为未验证。

所有14项都没有在本次文档修订中完成陌生队伍从零复用；格式/文件hash检查不代替这种效果验证。

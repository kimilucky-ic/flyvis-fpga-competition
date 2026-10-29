# 冻结对照、Sham和模型替换评价：证据与适用边界

核对日期：2026-10-21。这里审核历史文件，不表示今天重跑了工程。

## 已验证效果／观察

CPU CNN案例10/10预注册条件通过，21000正式commits审计；冻结模型31168参数，测试训练更新0、teacher纠正0。

证据类型：HISTORICAL_CASE_RECORD_NOT_FRESH_SKILL_REUSE。
适用范围、前提和失效条件见 [操作正文](skill.md)；下面的输入模板可换成本队契约和合法数据使用。

## 随包材料

- [controls](../evidence/originals/controls.json): byte_exact_original, source SHA-256 `07797bd16e3962fc28ef636f9fac947dd76f4696f5a6e9d029ee7a18be2e101c`.
- [controls_summary](../evidence/originals/controls_summary.json): byte_exact_original, source SHA-256 `6e357d8011501b52326cf3f3287a90f1b4c67f23a7902ee73e5894e294f0b671`.

原始位置、字节数、原始hash与包内hash见 [来源清单](../evidence/source_manifest.json)。.txt/.log保存原报告字节；报告中的旧路径、旧“待办”和链接属于当时记录，并非本包执行入口或当前状态。大报告摘要明确标注派生，不冒充完整原证据。

## 缺少的验证材料

完整训练/测试数据和逐步轨迹未随包；不构成生物恢复、自然视频真值或CNN上FPGA证据。独立任务复用未完成。

所有14项都没有在本次文档修订中完成陌生队伍从零复用；格式/文件hash检查不代替这种效果验证。

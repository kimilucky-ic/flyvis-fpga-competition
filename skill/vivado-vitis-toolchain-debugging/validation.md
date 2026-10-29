# Vivado/Vitis首个错误及生成网表/复位契约定位：证据与适用边界

核对日期：2026-10-21。这里审核历史文件，不表示今天重跑了工程。

## 已验证效果／观察

静态识别aux_reset低有效接零；独立2026.1.1生成物纠正极性，后续同一BIT/HWH的800请求板测通过。不是证明所有整机死机仅此一因。

证据类型：HISTORICAL_CASE_RECORD_NOT_FRESH_SKILL_REUSE。
适用范围、前提和失效条件见 [操作正文](skill.md)；下面的输入模板可换成本队契约和合法数据使用。

## 随包材料

- [reset](../evidence/originals/reset.txt): byte_exact_original, source SHA-256 `0005281bc341118a7b720e888dc644068d8fbdbbde6070042e9990a3ce35d38e`.
- [build](../evidence/originals/build.txt): byte_exact_original, source SHA-256 `5ca4d69fb24fb9e3aedb25aeaf234b80bc2db72bbc2e803317b3744dd4e70a9d`.
- [replay](../evidence/originals/replay.txt): byte_exact_original, source SHA-256 `2546fc463b6bbf3ddcb66ceae50d8c9f76a095a09898fdfba1179c7e3c91114b`.

原始位置、字节数、原始hash与包内hash见 [来源清单](../evidence/source_manifest.json)。.txt/.log保存原报告字节；报告中的旧路径、旧“待办”和链接属于当时记录，并非本包执行入口或当前状态。大报告摘要明确标注派生，不冒充完整原证据。

## 缺少的验证材料

缺另一工程独立套用该流程的记录；未覆盖全部Vivado/Vitis版本。2024.2.2案例须在总报告说明版本与重建脚本。

所有14项都没有在本次文档修订中完成陌生队伍从零复用；格式/文件hash检查不代替这种效果验证。

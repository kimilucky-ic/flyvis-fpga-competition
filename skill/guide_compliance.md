# 原指南逐项核对

核对时间：2026-10-21；范围为本地skill/的14项与一个单列UART候选，不代表比赛整仓库审计通过。

## 原文依据

原文件：`C:\Users\hzy72\Documents\xwechat_files\wxid_khlrd7p7q6j422_642a\msg\file\2026-09\全国大学生嵌入式芯片与系统设计竞赛'2026FPGA赛道选题指南-AMD.pdf`；SHA-256 `c6ad82acd4f7bdcd13bd412e232ed85d05f2a87dd5e2cdd04f9d219f88b569fc`，28页。提取文字并渲染核看PDF第24页（印刷第21页）。指南为来源材料，不把其中示例当作本工程已完成事实。

- 3.3.5.2：放在skill/；README.md逐项说明适用范围、使用方法、失效条件；每项说明已验证效果与失败/观察来源。允许提示词流程、案例模板、校验脚本、结构化踩坑清单任一或多种，并非每项都必须有程序。
- 3.3.5.2：评价核心是陌生队伍能否直接用于自己的题目。历史成功案例支持方法，但本次补写模板未经陌生使用者执行，不能称为新验证通过。
- 3.3.5.4：目录/文件名限定小写英文、数字、下划线/连字符，正文可中文。3.3.5.2及目录示例又明确点名README.md。本包保留这一指定名称，其余名字小写ASCII；扩展名点号按原指南.md示例理解。
- 3.3.3.1：推荐2026.1或2025.2；其他版本允许但要解释且有可复现脚本。需要提示词、回答、自我纠错记录。
- 3.3.2及3.3.5.2：通用PYNQ为额外加分；必须说明题目之外适用场景并有相应复用依据，不能把单板成功当跨板证明。
- 3.3.3.2的具体器件和实板输出要求属于整体参赛作品；不把每个纯软件Skill都强行要求上板。
- 3.3.3.3的开源仓库/许可，以及3.3.5.1完整工程、3.3.5.3完整设计报告，属于总交付另行核验；这次不公开仓库、不迁移活跃工程。

## 已改格式与内容

1. 14项及UART候选的提交入口改为skill.md；source_review_20261018.md改小写；更新独立比赛包内索引，原工作快照因有占用文件保留。
2. 14项各补usage.md和validation.md：给出适用输入、可改写提示词、判断与记录方法、历史效果/来源及具体缺口。新提示词明确尚未独立验证稳定性。
3. 复制可得的小型历史报告/JSON/日志，保存原字节和来源hash。大型真实反馈报告仅提取指定字段并标注摘要；不声称包含全部原始数据。
4. 外部本机Markdown链接改作来源文字，包内使用入口与材料相对链接可独立解析。旧报告快照中的原工程路径仍是历史定位，不是便携运行依赖。
5. 修正定点Skill“RTL已通过”与结尾“RTL未验证”的矛盾；板操作恢复条款加上当前授权与已知状态前提。
6. 修正UART旧摘要“尚无HEX”的过时表述：已有用户粘贴RX与TX记录，缺刺激前后时间对齐和原始终端文件，仍作为候选。
7. 隐私修订：原始消息摘录、来源路径及行号元数据已撤回；仅保留明确标为摘要的工程经验，不声称它替代原始协作记录。
8. Windows路径项降为待验证观察；历史XSim日志含中文工程路径但成功，记录这个反例，避免把路径相关性误写成必然原因。

## 14项结果

### 1. zynq-7000-board-operations

格式与必填说明已补；来源等级：historical_case_record。详见 [逐项证据](zynq-7000-board-operations/validation.md) 和 [使用示例](zynq-7000-board-operations/usage.md)。

仍缺：缺独立陌生使用者复用记录；原Notebook完整输出未随包保存。跨题/跨板通用性未验证。

### 2. vivado-vitis-toolchain-debugging

格式与必填说明已补；来源等级：historical_case_record。详见 [逐项证据](vivado-vitis-toolchain-debugging/validation.md) 和 [使用示例](vivado-vitis-toolchain-debugging/usage.md)。

仍缺：缺另一工程独立套用该流程的记录；未覆盖全部Vivado/Vitis版本。2024.2.2案例须在总报告说明版本与重建脚本。

### 3. fpga-board-reference-research

格式与必填说明已补；来源等级：historical_case_record。详见 [逐项证据](fpga-board-reference-research/validation.md) 和 [使用示例](fpga-board-reference-research/usage.md)。

仍缺：包内有历史核对报告，但缺原厂手册/原理图对应页与版本的可分发摘录或精确公开获取定位；缺第二硬件修订复核。

### 4. fpga-model-equivalence

格式与必填说明已补；来源等级：historical_case_record。详见 [逐项证据](fpga-model-equivalence/validation.md) 和 [使用示例](fpga-model-equivalence/usage.md)。

仍缺：包内未包含整个fly数值比较程序、原始长输入和全状态轨迹；不构成fly原网络或所有IEEE输入等价证明。独立套用未做。

### 5. fpga-fixed-point-quantization

格式与必填说明已补；来源等级：historical_case_record。详见 [逐项证据](fpga-fixed-point-quantization/validation.md) 和 [使用示例](fpga-fixed-point-quantization/usage.md)。

仍缺：缺量化候选的综合/实板证据；递质极性未定。完整图/生成器/向量未打入轻量Skill包，须在具体工程取得合法输入。

### 6. windows-fpga-path-diagnostics

格式与必填说明已补；来源等级：user_observation_only。详见 [逐项证据](windows-fpga-path-diagnostics/validation.md) 和 [使用示例](windows-fpga-path-diagnostics/usage.md)。

仍缺：关键缺口：原失败命令/版本/错误日志、保持输入不变的路径对照、可重复成功。按待验证诊断观察列入，不能充当已验证稳定工作流。

### 7. pynq-bounded-replay-evidence

格式与必填说明已补；来源等级：historical_case_record。详见 [逐项证据](pynq-bounded-replay-evidence/validation.md) 和 [使用示例](pynq-bounded-replay-evidence/usage.md)。

仍缺：包内附验收报告，不含原数千项ZIP、全部输入oracle或未剪辑现场视频。陌生任务/第二板卡复用及通用PYNQ加分未证明。

### 8. gpu-fpga-feedback-transactions

格式与必填说明已补；来源等级：historical_case_record。详见 [逐项证据](gpu-fpga-feedback-transactions/validation.md) 和 [使用示例](gpu-fpga-feedback-transactions/usage.md)。

仍缺：附大型FINAL_RESULT的来源绑定摘要，不含完整1.37MB原报告及逐步原始事务/故障注入证据。另一后端/独立部署及全部负向路径未在本次复验。

### 9. flyvis-demo-data-integration

格式与必填说明已补；来源等级：historical_case_record。详见 [逐项证据](flyvis-demo-data-integration/validation.md) 和 [使用示例](flyvis-demo-data-integration/usage.md)。

仍缺：包内没有完整GUI和真实模型数据，也未重新启动GUI或接相机；陌生GUI适配和完整负向场景复用未完成。

### 10. flyvis-controlled-replacement

格式与必填说明已补；来源等级：historical_case_record。详见 [逐项证据](flyvis-controlled-replacement/validation.md) 和 [使用示例](flyvis-controlled-replacement/usage.md)。

仍缺：完整训练/测试数据和逐步轨迹未随包；不构成生物恢复、自然视频真值或CNN上FPGA证据。独立任务复用未完成。

### 11. fpga-performance-power-accounting

格式与必填说明已补；来源等级：historical_case_record。详见 [逐项证据](fpga-performance-power-accounting/validation.md) 和 [使用示例](fpga-performance-power-accounting/usage.md)。

仍缺：缺同任务同边界的板级能耗/时延测量及外部校准；因此比较性节能结论未验证。现有GPU遥测原CSV未随包。

### 12. fpga-evidence-preserving-cleanup

格式与必填说明已补；来源等级：historical_case_record。详见 [逐项证据](fpga-evidence-preserving-cleanup/validation.md) 和 [使用示例](fpga-evidence-preserving-cleanup/usage.md)。

仍缺：包内附最终/恢复结果，未附完整恢复源片段与逐文件前后hash清单；不可据此删除陌生项目。独立恢复演练未做。

### 13. flyvis-gpu-reference

格式与必填说明已补；来源等级：historical_case_record。详见 [逐项证据](flyvis-gpu-reference/validation.md) 和 [使用示例](flyvis-gpu-reference/usage.md)。

仍缺：缺干净安装复现及不同GPU/所有刺激覆盖；checkpoint、输入和大数组不随包。不能把特定算子快照作为完整端到端速度。

### 14. flyvis-decoder-inference

格式与必填说明已补；来源等级：historical_case_record。详见 [逐项证据](flyvis-decoder-inference/validation.md) 和 [使用示例](flyvis-decoder-inference/usage.md)。

仍缺：缺陌生checkpoint/decoder独立复用及自然视频校准；原脚本/模型权重/输出数组不随包，绝对速度单位和生物行为未验证。

## 判定边界

本次可确认提交结构及来源材料已整理，不能宣布全部14项都满足“经过验证、稳定复用”的实质要求。13项有历史案例记录，Windows路径仅有观察；所有14项的新参数化提示词和陌生使用者独立复用尚未执行。待验证列表见validation_gaps.md；静态验收结果另记audit_validation.json。

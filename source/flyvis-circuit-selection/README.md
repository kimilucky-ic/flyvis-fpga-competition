# FlyVis 回路选择与独立参考工作线

负责人范围：官方 FlyVis 神经回路提取、网络分割、独立 Python 参考及未来 FPGA 测试向量。与 MaleCNS/SNN、fly/PQN、fly Port、GPU 实验、GUI、打包分开。

第一轮：[候选比较与源码审计](round1_20261010/REPORT.md)，[静态导出说明](round1_20261010/BOUNDARY_CONTRACT_DRAFT.md)，[实际统计](round1_20261010/artifacts/summary.json)，[验证](round1_20261010/artifacts/verification.json)。后续已读取总控 v0.1：[三 profile 对齐补充](alignment_v01_20261010/ALIGNMENT_REPORT.md)、[集中待决清单](alignment_v01_20261010/DECISION_REQUESTS.md)、[最新交接](alignment_v01_20261010/handoff.json)。通信量以显式包含 x_H 的补充为准。

截至 2026-10-10：用户已确认 T5c 67 节点用于本轮软件闭环。第二阶段 **PASS_SOFTWARE_CLOSED_LOOP**：[报告](phase2_20261010/REPORT.md)、[交接](phase2_20261010/handoff.json)、[独立 H.step 接口](phase2_20261010/H_STEP_INTERFACE.md)、[主验收](phase2_20261010/artifacts/final_native_audit/result.json)。官方 GPU 原生参数下，真实 GPU R-only + 独立 NumPy H 的 SOURCE_RAW/CURRENT_AGG 四条件×485步均通过；全部45,669节点逐步核验、双向 live 反馈、15负测试与统一提交通过。CPU-canonical 参数基线单独保存，不混入 GPU-native comparison。

第三阶段首个硬件原型已由用户确认 **T5c67 + SOURCE_RAW**。动画01_off_right的FullGPU与实际Python H+GPU R连续800步 **Gate S1 PASS**：[报告](phase3_20261010/REPORT.md)、[机器交接](phase3_20261010/B_ANIMATION_SOURCE_RAW_800.json)、[C动画向量](phase3_20261010/c_reference/C_REFERENCE_HANDOFF.json)、[GUI只读包](phase3_20261010/gui_bundle/GUI_READONLY_HANDOFF.json)。全网逐步最大9.5367e-7，800 PREPARED+800 COMMITTED链、真实H→R→H、15负测试通过。完整硬件闭环仍未完成。

新增三候选四条件正式消融 **PASS_SOFTWARE_ABLATION_IMPLEMENTATION**：[报告](phase3_ablation_screen_20261010/REPORT.md)、[机器交接](phase3_ablation_screen_20261010/B_ABLATION_SCREEN_4CONDITIONS.json)、[三候选功能影响对照CSV](phase3_ablation_screen_20261010/artifacts/formal_analysis/three_candidate_function_comparison.csv)、[全状态/原边/两进程审计](phase3_ablation_screen_20261010/artifacts/formal_audit/result.json)。遵循③v1 BLOCK_HR_RELEASE，k200起仅阻断原HR电流，H继续真实更新；两个新进程共48个condition-runs/23,280步，两份全部状态逐位复现。298的固定共同下游V方向差结构变化最大；92 ON/298两极性达到扩展门槛，67未达到但保留覆盖理由。24条件待③/用户评审，⑥原67工作独立；软件消融不证明FPGA功能恢复。

数值位宽、PS–PL及报头由总架构/C另评；早期[消融提案](phase2_20261010/ABLATION_PROPOSALS.md)保留为历史。本线没有定点量化、RTL修改、综合或板级操作。

本工作线的新增实现和实验结果只存于此目录。上游、已有 Golden、其他工作线只读；本线检查点单独存于 `docs/workstreams/flyvis-circuit-selection.md`。

# FlyVis B：第二阶段独立 H / 真实闭环

**PASS_SOFTWARE_CLOSED_LOOP**（T5c67、四条件×485步、5ms、float32），最终 FPGA 方案未冻结。

- [完整报告 — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-028)、[机器交接 — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-029)、[原生GPU主验收 — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-030)。
- [H.step语义接口 — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-031)、[独立实现](h_step.py)、[统一提交](coordinator.py)、[A服务对接](gpu_adapter.py)。
- [逐条件误差 — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-032)、[中心T4/T5逐节点指标 — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-033)、[逐步误差图 — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-034)。
- [浮点软件输入输出 — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-035)、[实际GPU负测试/反馈 — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-036)、[新进程32步复现 — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-037)。
- [CPU-canonical独立基线 — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-038)、[消融提案待评审 — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-039)、[执行/复建记录 — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-040)。

Full比较目录只是独立官方参考；生产R从本运行完整已提交状态计算。SOURCE_RAW与CURRENT_AGG各自单独验收；后者使用主机NumPy RH归约，尚未接受GPU RH/PL归约。所有关键数据/代码SHA在run_identity及manifest，历史失败输出保留。

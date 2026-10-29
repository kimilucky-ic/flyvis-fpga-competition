# FlyVis B：第二阶段独立 H / 真实闭环

**PASS_SOFTWARE_CLOSED_LOOP**（T5c67、四条件×485步、5ms、float32），最终 FPGA 方案未冻结。

- [完整报告](REPORT.md)、[机器交接](handoff.json)、[原生GPU主验收](artifacts/final_native_audit/result.json)。
- [H.step语义接口](H_STEP_INTERFACE.md)、[独立实现](h_step.py)、[统一提交](coordinator.py)、[A服务对接](gpu_adapter.py)。
- [逐条件误差](artifacts/final_native_audit/condition_error_summary.csv)、[中心T4/T5逐节点指标](artifacts/final_native_audit/central_T4T5_error_summary.csv)、[逐步误差图](artifacts/final_native_audit/step_error_comparison.png)。
- [浮点软件输入输出](artifacts/native_gpu_step_io/result.json)、[实际GPU负测试/反馈](artifacts/live_feedback_native_r1/result.json)、[新进程32步复现](artifacts/reproduce_native_prefix_r1/result.json)。
- [CPU-canonical独立基线](artifacts/final_audit/result.json)、[消融提案待评审](ABLATION_PROPOSALS.md)、[执行/复建记录](EXECUTION_RECORD.md)。

Full比较目录只是独立官方参考；生产R从本运行完整已提交状态计算。SOURCE_RAW与CURRENT_AGG各自单独验收；后者使用主机NumPy RH归约，尚未接受GPU RH/PL归约。所有关键数据/代码SHA在run_identity及manifest，历史失败输出保留。

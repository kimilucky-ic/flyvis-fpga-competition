# 第三阶段 B P0

**Gate S1软件动画800闭环 PASS，完整软硬件第三阶段尚未完成。** 机器总入口[B_ANIMATION_SOURCE_RAW_800.json](B_ANIMATION_SOURCE_RAW_800.json)，[报告](REPORT.md)。所有数据原始来源/参数保持不变；没有RTL或板级操作。

- [真实Python替换](artifacts/python_source_raw_800_r2/result.json)：独立H800 + 实际GPU R800，同旧态一次提交。
- [独立链/向量/误差验收](artifacts/audit_800_r1/result.json)、[15负测试与实际反馈](artifacts/live_feedback_r1/result.json)。
- [A新Full验收收据](A_FULL_800_RECEIPT.json)：引用A同身份新全网800参考，未重复Full。
- [C动画数值交接](c_reference/C_REFERENCE_HANDOFF.json)、[格式说明](C_REFERENCE_README.md)、[共享H.step语义](H_STEP_INTERFACE.md)。
- [GUI只读交接](gui_bundle/GUI_READONLY_HANDOFF.json)：真实软件结果的离线展示包，FPGA不可用；浏览器由GUI线验证。

WSL FlyVisCPU `/opt/flyvis-gpu-venv/bin/python` 运行run_video.py；确认A后端/冻结包SHA仍一致，用新的--run保存，禁止复用已有结果目录：

```text
run_video.py --mode PythonReplacement --run <new_name> --reference /mnt/c/Users/hzy72/Documents/ChatGPT/fly/gpu_phase3_fixed_video_20261010/artifacts/full_gpu_800_r1
```

本目录dependencies/b_core三份核心实现按原字节复用G2；a_video_adapter只绑定真实A callable。Full轨迹仅在提交后比较。审计/export是离线证据检查，不是生产R驱动器。FPGAReplacement当前NOT_READY且无回退。

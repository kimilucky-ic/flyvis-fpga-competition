# FlyVis T4/T5 DDR流式硬件B

独立首批交付，2026-10-11。入口：[DDR_STREAM_MINI_RTL.md — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-054)、[机器验收 — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-055)、[资源风险 — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-056)、[数值profile — 历史依赖未随包提供](../../../report/archive_dependencies.md#missing-057)。仅RTL_SIM，完整433880边/5768H尚未仿真、综合、路由或上板。

复现依赖：Windows x64 / PowerShell / Python3.14+NumPy2.4.6 / Vivado XSim2026.1.1、⑦冻结92/298夹具与t4t5_scale数据。每次创建新B build，单线程依次执行。无需安装或改全局设置；借用⑦既有AMD环境脚本仅设置当前进程变量，不修改它或许可证文件。

在仓库根执行：

```powershell
python flyvis-fpga/t4t5_ddr_synapses_20261011/prepare_vectors.py
./flyvis-fpga/t4t5_ddr_synapses_20261011/run_sim.ps1 -Fixture mini
./flyvis-fpga/t4t5_ddr_synapses_20261011/run_sim.ps1 -Fixture addr15
./flyvis-fpga/t4t5_ddr_synapses_20261011/run_sim.ps1 -Fixture 92
./flyvis-fpga/t4t5_ddr_synapses_20261011/run_sim.ps1 -Fixture 298
python flyvis-fpga/t4t5_ddr_synapses_20261011/audit_results.py
```

普通桌面权限XSim已实际复现；受限环境generated-C编译曾失败，原因未进一步定位。不要因此重装工具或改⑥/⑦工程。FAIL日志保留，当前源码/夹具SHA不一致、少CSV、fatal或缺ALL_PASS的run不会验收。

`prepare_vectors.py`不会重新推断原模型或重建原图；读取已冻结source mapping/request/expected/trace，独立整数oracle交叉核对，转换为B的LE64原序记录。`audit_results.py`再次用另一舍入实现核对raw CSV，并复核所有继承SHA。

本批到第一里程碑停止。无综合脚本、板端脚本、bitstream或自动后续campaign。后续全图与OOC分批推进并遵守EDA错峰及板卡专门授权。

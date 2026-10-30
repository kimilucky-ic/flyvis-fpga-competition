# 独立 FlyVis RTL 研究包

入口：[REPORT.md](REPORT.md)、[最终仿真审计](artifacts/simulation_audit.json)、[综合资源检查](artifacts/synthesis_resource_gate.json)。

只在本目录生成新输出，不运行⑥的 build/board/driver 脚本。依赖冻结的 input_bundle_r2、formal_r2 SOURCE_RAW 轨迹、此前整数参考、Python/NumPy，以及本机 Vivado/XSim 2026.1.1。`amd2026_environment.ps1` 仅只读设定进程内工具和已验证许可证选择，不修改其文件或全局环境。

## 软件夹具和 oracle

从仓库根在普通 PowerShell 中运行：

```powershell
python flyvis-fpga/phase4_rtl92_20261011/prepare_fixtures.py
python flyvis-fpga/phase4_rtl92_20261011/prepare_fixtures.py --candidate hazard --out flyvis-fpga/phase4_rtl92_20261011/fixtures_hazard
python flyvis-fpga/phase4_rtl92_20261011/prepare_fixtures.py --candidate C_T4T5_all_centers --window-steps 4 --out flyvis-fpga/phase4_rtl92_20261011/fixtures298
```

现有 fixture manifest 保存其生成时 oracle SHA；每次实验前重新生成，修改源期间不要运行同一夹具。保护 before 快照仅在一次新实验开始时生成，不覆盖已封存的基线。

## 单线程行为仿真

```powershell
./flyvis-fpga/phase4_rtl92_20261011/run_sim.ps1 -Fixture fixtures92 -Banks 1
./flyvis-fpga/phase4_rtl92_20261011/run_sim.ps1 -Fixture fixtures92 -Banks 2
./flyvis-fpga/phase4_rtl92_20261011/run_sim.ps1 -Fixture fixtures92 -Banks 4
./flyvis-fpga/phase4_rtl92_20261011/run_sim.ps1 -Fixture fixtures_hazard -Banks 1
./flyvis-fpga/phase4_rtl92_20261011/run_sim.ps1 -Fixture fixtures_hazard -Banks 2
./flyvis-fpga/phase4_rtl92_20261011/run_sim.ps1 -Fixture fixtures_hazard -Banks 4
./flyvis-fpga/phase4_rtl92_20261011/run_sim.ps1 -Fixture fixtures298 -Banks 1
python flyvis-fpga/phase4_rtl92_20261011/audit_simulations.py
```

逐个运行，避免并发。每次在 build 中创建新目录，复制源、ROM和 manifest；临时目录也限定在该次构建。PASS 必须具有完整 ALL_PASS、每步状态/边数/周期、fault markers，并通过独立CSV/SHA审计。Fatal、少输出、缺日志、当前源SHA不匹配不能纳入当前版本验收。审计中保留旧版本通过列表，原失败日志不删除。

受限执行环境中的 generated C 编译可能失败；本次已在普通桌面权限下以同一源/工具/独立目录成功。不要因此改⑥或安装新工具。具体限制原因未定位。

## 92 OOC 小综合（资源许可后）

```powershell
./flyvis-fpga/phase4_rtl92_20261011/run_synth92.ps1
```

默认先检查≥4GiB可用内存、CPU≤50%及无活动EDA任务；不通过即保存 DEFER 证据，不启动 Vivado。此阈值为本线保守调度策略。本轮只验证了 DEFER 分支，实际综合分支未运行。允许后也仅综合92 bank1独立核心，不做布线、SoC或板卡。

动态加载、AXI包装、网络身份/step tag协议、GPU-R/PL闭环、298 bank2/4硬件测试、门级仿真、综合/实现资源及科学功能验收均未完成。

# 2026-10-18 九个对话的 Skill 来源与纠错记录

这是按用户截图整理的协作记录摘要，不是逐字聊天导出，也不是一次新的设备验收。九个会话的完整本地 JSONL 已作用户／最终答复全文检索，检索快照包含704条用户消息项、405条最终答复；逐项阅读了各会话近期6轮和历史高信号纠错段，并核对下列源文件。消息项数不等于独立实验数。没有把全部工具输出重新作为现场证据逐项审计。

⑪和带“(2)”的②在阅读时仍工作中。下面记录的是本轮读到的源快照；以后执行前须读对应 owner 的最新状态。原始 JSONL、模型、代码、BIT/HWH、实验数组均不纳入此文档包。

## S1 — ⑪ FlyVis｜无损压缩研究

- 对话ID：01a1342c-a407-7373-9125-7b1442fa7b94。
- 用户任务摘要：完整原图和连续值动力学保持，研究无损结构压缩、FP32硬件、资源及能耗；最后由用户亲自上板。
- 关键纠错：连接数不等于必须逐条存储的字节数；结构压缩仍须保持全部有序边、有效FP32权重及零权边。行为RTL、整数FP32、周期模型、实际布线各有自己的证据。运算单元名称不保证舍入／subnormal／累加顺序相同。
- 已有经验：先证明紧凑格式完整解码，再验证全状态和自己的递推反馈；用重复目标小夹具检查依赖互锁，用背压检查ready/valid保持；每次优化绑定源、周期及布线报告。
- 当前边界：2026-10-18人工首测下载调用返回后，在时钟检查停止；未恢复初态、未STEP、未得到完整网络实板正确性PASS。PYNQ参考频率50与工程33.333333MHz导致显示差异的解释仅有源码／静态计算支持，真实PLL／分频和原始结果包仍待返回；不能盲写时钟或放宽门禁。
- 来源：完整工作线 (original-workspace source: `../docs/workstreams/flyvis-lossless-study.md`; not a bundled dependency)、软件无损结构报告 (original-workspace source: `../flyvis-lossless-study/REPORT.md`; not a bundled dependency)、首测停止记录 (original-workspace source: `../flyvis-lossless-study/clock_diagnosis_20261018/USER_REPORTED_STOP.json`; not a bundled dependency)、片上功耗估算 (original-workspace source: `../flyvis-lossless-study/power_analysis_20261018_r4/POWER_RESULT.json`; not a bundled dependency)。
- 整理到：模型等价、工具链／板端时钟排查、性能功耗统计。时钟解释保留待验证。

## S2 — ② FlyVis · GUI与演示集成 (2)

- 对话ID：01a134ff-b93a-7c50-a3eb-f7b22a07010d。
- 用户任务摘要：摄像头与真实联合流程接原GUI；流程要简单，准备一次、一个启动入口，最终按分段实测查慢。
- 关键纠错：同步落盘、逐步深度核验、解码和绘制曾拖住递推；软件“准备成功”回执的格式问题发生在STEP前，不能直接归因于GPU／FPGA算错。COMMIT前持久化及ACK前持久化，和后来的异步性能分支不是同一掉电保证。
- 已有经验：明确计算／提交／落盘三个计数；非阻塞记录用不可变快照，记录失败标不完整。保留必需的身份、ACK和停止逻辑，深度审计在约定阶段进行。无板时可用真实GPU＋软件Q24测电脑路径，并明确不计为PL结果。
- 已核对结果：32步软件候选用原冻结摄像头输入，compute_wall_s=1.166027849；状态为PASS_ACTUAL_GPU32_SOFTWARE_Q24_ONLY，不能当作真实联合速度。
- 新接口边界：⑪完整PL网络不沿用⑦分区的COMMIT/ACK，不再开第二套GPU神经更新；当前接入仅准备／读取器工作，须先验完整初态与首步状态。没有官方Decoder结果时显示不可用。
- 来源：32步原始结果 (original-workspace source: `../../fly/gui_v1/evidence/minimal_gpu_software32_20261018/RESULT.json`; not a bundled dependency)、最小路径软件核验 (original-workspace source: `../../fly/gui_v1/evidence/minimal_compute_20261017/VERIFICATION.json`; not a bundled dependency)、持久化合并记录 (original-workspace source: `../../fly/gui_v1/evidence/ps_commit_journal_20261017/REPORT.md`; not a bundled dependency)、运行契约 (original-workspace source: `../../fly/gui_v1/JOINT_STREAM_RUNTIME_CONTRACT.md`; not a bundled dependency)、⑪接入清单 (original-workspace source: `../../fly/gui_v1/evidence/line11_board_readiness_20261018/READINESS.json`; not a bundled dependency)。
- 整理到：反馈事务、演示数据接入、性能统计和新版PYNQ流程。

## S3 — ④ FlyVis · T4/T5功能与规模研究

- 对话ID：01a12435-4dbc-7212-8b4b-af1a91add91e。
- 用户任务摘要：原模型功能／消融与规模对照，后来研究CPU人工模块替代；另获准实测GPU能耗。
- 关键纠错：释放阻断、状态钳制、读出屏蔽不可互称；读出幅度比不是生物功能百分比。移动背景失败通过冻结背景、灰背景和局部位置对照定位，不能未经诊断就换大模型。新正式刺激必须在模型冻结后生成。
- 已有经验：Full/Sham、初态、ROI／时窗和阈值先冻结；替代者读自己的旧状态并进入余网反馈，统计原模块调用和teacher correction；保留静止与局部目标失败和后续新实验身份。
- 已核对结果：同规模31,168参数CNN，10/10新条件通过原门槛，21,000正式提交状态链审计，native H生产更新和teacher correction均为0，GPU=0、board=0。这是受控软件模型替代，不是生物组织或FPGA CNN验证。
- 能耗纠错：历史485步有24样本，必须按11,640模型样本步作分母。新实测正式17,460步，GPU设备域平均66.75W、166.71mJ/步；累计能量字段相差约7.52%，未隐藏差异。
- 来源：CNN摘要 (original-workspace source: `../flyvis-circuit-selection/cnn_cpu_texture_local_refinement_20261016/SUMMARY.json`; not a bundled dependency)、正式状态链审计 (original-workspace source: `../flyvis-circuit-selection/cnn_cpu_texture_local_refinement_20261016/FINAL_AUDIT.json`; not a bundled dependency)、冻结模型 (original-workspace source: `../flyvis-circuit-selection/cnn_cpu_texture_local_refinement_20261016/MODEL_FREEZE.json`; not a bundled dependency)、GPU功耗实测 (original-workspace source: `../flyvis-circuit-selection/gpu_power_485_20261018_r2/SUMMARY.json`; not a bundled dependency)。
- 整理到：受控替代、原GPU／Decoder已有Skill和性能功耗统计。

## S4 — ⑦ FlyVis · FPGA A｜5768神经元核

- 对话ID：01a125a8-a4ac-7702-bdcb-f17a475a2c44。
- 用户任务摘要：共享神经元核、实际PL计算和GPU反馈，随后按比赛交付解释资源、成本和价值。
- 关键纠错：各侧用同一旧态，禁用原GPU-H更新，PL原始整数进入下一步；COMMIT／RELEASE／ACK必须匹配，未知状态不能自动继续。PS旧UTC、旧服务句柄、时钟API显示值均需解释来源。
- 已核对结果：run c708f1c9bac14c07ac8f56d59678b95a为PASS_ACTUAL_485_STEP_GPU_FPGA_CLOSED_LOOP，检查2,797,480个PL候选及2,791,712反馈字，native_H_GPU_updates=0。
- 边界：其结果是已结束会话、实际联合结果的离线展示，不证明当前板态。固定57,681周期不等于固定端到端延迟；历史软件时钟频率报告不能冒充物理实测。该分区的突触仍在GPU，与⑨和⑪职责不同。
- 来源：485步结果 (original-workspace source: `../flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/joint_latency485_20261016/runs/c708f1c9bac14c07ac8f56d59678b95a/FINAL_RESULT.json`; not a bundled dependency)、本线工作记录 (original-workspace source: `../docs/workstreams/flyvis-scalable-engine.md`; not a bundled dependency)。
- 整理到：反馈事务、PYNQ流程、性能功耗／成本表述。

## S5 — ② FlyVis · GUI与演示集成

- 对话ID：01a12436-3886-7623-948d-8bd1a7d8c33b。
- 用户任务摘要：保留旧实验，解释T4/T5，界面集中成输入、光流、神经元、解释四区，并解决慢启动。
- 关键纠错：分散说明和重复文字增加理解成本；亮度增强不等于正向激活，模型估计方向不能写成输入预设。首页等待全实验初始化、重复全量hash成为启动瓶颈。
- 已核对经验：选中实验按需加载，首次hash后依文件身份规则复用并按变化失效；服务准备12.41→0.47秒，首帧数据准备14.71→2.49秒，属于同一真实数据的有界离线优化，不是完整桌面启动或新神经计算速度。
- 来源：启动核验 (original-workspace source: `../../fly/gui_v1/evidence/startup_fast_20261017/VERIFICATION.json`; not a bundled dependency)、四区界面验收 (original-workspace source: `../../fly/gui_v1/evidence/competition_four_panels_20261017/REPORT.md`; not a bundled dependency)。
- 整理到：演示接入和性能分段统计。

## S6 — ⑩ FlyVis｜3D神经网络可视化

- 对话ID：01a13462-749a-79b3-8a62-63642c82b6da。
- 用户任务摘要：八类真实骨架同屏，同一次ON60活动同步，固定身份色，清楚展示正负响应。
- 关键纠错：六角计算坐标不是电镜解剖坐标；同类型SWC没有证明与global ID个体一一对应。旧65中心读数接口不能充当5,768节点接口。按wsl.exe进程名一刀切也会误判资源占用。
- 已有经验：固定刺激前基线及全片尺度，保留signed原值和±Δ；验证原几何、时间和八类同屏。PID须连创建时间与命令／所属会话一起判断；缺少原始进程证据时不反推唯一故障原因。
- 边界：已验收的C方案是原实验活动的离线形态展示；资源分类软件修复不等于后续60秒现场稳定性已验收。
- 来源：渲染与时间验收 (original-workspace source: `../../fly/flyvis-3d-studio/activity_replay_20261014/response_comparison_20261015/acceptance.json`; not a bundled dependency)、资源规则修复核验 (original-workspace source: `../../fly/flyvis-3d-studio/activity_replay_20261014/live_raw_guard_20261015/evidence/verification.json`; not a bundled dependency)、②接入回执 (original-workspace source: `../../fly/flyvis-3d-studio/activity_replay_20261014/live_raw_guard_20261015/integration_ack.json`; not a bundled dependency)。
- 整理到：演示数据接入；未证实的跨个体解剖映射保留边界。

## S7 — ③ FlyVis · 总架构与决策

- 对话ID：01a12436-f9f8-7560-ad78-8b929711ef41。
- 用户任务摘要：比较状态所有权、精度／接口与验收；后来按明确范围整理存储。
- 关键纠错：候选生成成功不是数值验收；32步终点不能代替整段前缀max/RMSE。Q22状态上的float运算不能标成bit-true Q22 oracle。不同A/B实现及已有软件／实板结果不能互借。
- 可复用清理经验：先区分原始轨迹、可恢复派生数组和缓存；记录逻辑大小及实际分配。授权五文件退役后，用保留原始数据和约2.82MiB必要片段重建完整字节流，删除前后SHA均相同；8,164保留文件和84旧轨迹数组保持。
- 来源：精度／oracle纠错 (original-workspace source: `../docs/flyvis_visual_hybrid/architect_phase4_20261010/PREPARATION_CORRECTION.md`; not a bundled dependency)、恢复说明 (original-workspace source: `../docs/flyvis_visual_hybrid/architect_cleanup_20261016/DERIVED_RETIREMENT_AND_RECOVERY.md`; not a bundled dependency)、退役后恢复检查 (original-workspace source: `../docs/flyvis_visual_hybrid/architect_cleanup_20261016/DERIVED_RECOVERY_CHECK_AFTER_DELETION.json`; not a bundled dependency)、保留项核验 (original-workspace source: `../docs/flyvis_visual_hybrid/architect_cleanup_20261016/DERIVED_RETIREMENT_FINAL_VERIFICATION.json`; not a bundled dependency)。
- 整理到：模型等价、反馈事务、保留证据的清理流程。

## S8 — ⑨ FlyVis · FPGA B｜DDR突触引擎

- 对话ID：01a12adf-a39e-7cd0-a45b-f2a635bc8213。
- 用户任务摘要：全部433,880输入边的有序DDR计算；明确优先BRAM布局与整块传输，保留旧固件，暂不上板。
- 关键纠错：空闲DSP不等于加lane就能变快；单拍一边供数已经接近核心吞吐上限。源项仅比16,384多18项，却触发额外BRAM映射，拆小尾区后再看真实报告。
- 已核对结果：16,402源项完整保留，GP0数据逐字搬运换为DDR整块传输；完整SoC布线69.5 BRAM tile，旧版85；4DSP。仿真490,790周期是100MHz条件下4.90790ms，不是实板吞吐。
- 重要限制：PS7 VIP在active/#0调度中先采到旧地址／数据，正确AXI输出与DDR最后六项缺失同时出现。只在本工程、固定厂商SHA的仿真副本延后1ps采样并独立复现；厂商安装和DUT不变。该修复模型条件必须随系统仿真PASS披露。
- 来源：机读结果 (original-workspace source: `../flyvis-fpga/t4t5_ddr_synapses_20261011/soc_b_bulk_20261013/RESULT.json`; not a bundled dependency)、仿真模型修复 (original-workspace source: `../flyvis-fpga/t4t5_ddr_synapses_20261011/soc_b_bulk_20261013/PS7_SIMULATION_MODEL_REPAIR.md`; not a bundled dependency)、里程碑 (original-workspace source: `../flyvis-fpga/t4t5_ddr_synapses_20261011/soc_b_bulk_20261013/MILESTONE_RESULT.md`; not a bundled dependency)。
- 整理到：工具链、模型等价和性能统计；保持BOARD_NOT_RUN。

## S9 — ③辅 FlyVis · 架构答疑与审查

- 对话ID：01a12462-8260-7791-b0f6-7c01175bd9f8。
- 用户任务摘要：查清项目与真实依赖，降低接手／提交成本；先方案，不批量搬迁或删除。
- 关键纠错：XPR数量不是独立设计数量，文件相同不等于无调用，根Git无提交不能提供整体回滚。重复fly/PQN源仍有导入者；探针日志被封存SHA引用，不能当垃圾。
- 已有经验：按owner、入口、源→工程→制品→manifest建立依赖；发布用白名单，比赛期冻结活跃路径，模型／权重／证据各归自己的项目。迁移要分lane并保留回滚，Git嵌套和许可一起核对。
- 来源：入口与依赖 (original-workspace source: `../docs/architecture_cleanup_20261011/ENTRYPOINTS_AND_DEPENDENCIES.md`; not a bundled dependency)、退役候选 (original-workspace source: `../docs/architecture_cleanup_20261011/DEPRECATED_PROJECT_CANDIDATES.csv`; not a bundled dependency)、迁移与回滚方案 (original-workspace source: `../docs/architecture_cleanup_20261011/MIGRATION_SEQUENCE_AND_ROLLBACK.md`; not a bundled dependency)。
- 整理到：清理／交接流程和反馈状态契约。旧清理授权不继承给本轮新目标。

## 本次产物及验证范围

新增五个工作流：反馈事务、演示数据接入、受控替代、性能功耗统计、保留证据的清理。更新PYNQ重放、模型等价、Vivado工具链。已有GPU参考／官方解码器Skill纳入比赛包，保留原验证范围和失败记录。

Skill本体均包含作用／触发、前置条件、过程、预期核验、失败处理、来源和未验证边界。新工作流有上述历史案例支持，但本次仅作静态文档与来源核验；作为新打包Skill的独立跨任务／跨板复用仍为observed, not yet reproduced。软件／模拟／仿真模型修复／完整实现／现场结果／现场结果离线回放各保留自己的证据等级。

这是文档整理；没有新跑GPU、相机、EDA或板卡操作，没有删除／迁移项目数据、修改其他lane检查点或发布GitHub。完整逐字聊天导出及跨环境复用仍不是本次已交付证据。
